import argparse
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.generate_cli_docs import (
    ParserExtractionError,
    generate_docs,
    load_parser,
    main,
)


class GenerateCliDocsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def script(self, name, text):
        filename = self.directory / name
        filename.write_text(text, encoding="utf-8")
        return filename

    def test_extracts_without_imports_parsing_or_runtime_side_effects(self):
        marker = self.directory / "must-not-exist"
        filename = self.script("tool.py", '''
import missing_viya_dependency
from pathlib import Path
import argparse
Path({!r}).touch()
parser = argparse.ArgumentParser(description="Test tool")
parser.add_argument("-o", "--output", choices=["csv", "json"], default="csv")
parser.add_argument("--count", type=int, default=10)
parser.add_argument("--write", action="store_true")
args = parser.parse_args()
raise RuntimeError("Must not execute")
'''.format(str(marker)))
        parser = load_parser(filename)
        self.assertEqual(parser.prog, "tool.py")
        self.assertEqual(parser.description, "Test tool")
        self.assertEqual(
            vars(parser.parse_args([])),
            {"output": "csv", "count": 10, "write": False},
        )
        self.assertIn("-o {csv,json}, --output {csv,json}", parser.format_help())
        self.assertFalse(marker.exists())

    def test_parents_subcommands_and_mutually_exclusive_groups(self):
        filename = self.script("tool.py", '''
import argparse
parent = argparse.ArgumentParser(add_help=False)
parent.add_argument("--name", required=True)
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command")
child = subparsers.add_parser("create", parents=[parent])
group = child.add_mutually_exclusive_group(required=True)
group.add_argument("--id")
group.add_argument("--path")
''')
        parser = load_parser(filename)
        parsed = parser.parse_args(["create", "--name", "example", "--id", "123"])
        self.assertEqual(parsed.command, "create")
        self.assertEqual(parsed.name, "example")
        self.assertIn("create", parser.format_help())
        child = next(
            action for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)
        ).choices["create"]
        self.assertTrue(child._mutually_exclusive_groups[0].required)

    def test_function_and_python_version_branch(self):
        filename = self.script("tool.py", '''
import argparse
def main():
    parser = argparse.ArgumentParser()
    if version == 2:
        parser.add_argument("--encoding", default="ascii")
    else:
        parser.add_argument("--encoding", default="utf-8")
    return parser.parse_args()
''')
        self.assertEqual(load_parser(filename).parse_args([]).encoding, "utf-8")

    def test_literal_defaults_and_file_type_do_not_open_files(self):
        filename = self.script("tool.py", '''
import argparse
from pathlib import Path
cwd = Path.cwd()
permissions = ["read", "update"]
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--permissions", default=permissions)
parser.add_argument("--directory", default=cwd)
parser.add_argument("--file", type=argparse.FileType("r"))
''')
        parser = load_parser(filename)
        defaults = parser.parse_args([])
        self.assertEqual(defaults.permissions, ["read", "update"])
        self.assertEqual(defaults.directory, Path.cwd())
        self.assertIsNone(defaults.file)

    def test_dynamic_values_fail_without_execution(self):
        filename = self.script("tool.py", '''
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--value", default=dangerous_function())
''')
        with self.assertRaisesRegex(ParserExtractionError, "tool.py:4: unsupported"):
            load_parser(filename)

    def test_unknown_conditional_fails(self):
        filename = self.script("tool.py", '''
import argparse
parser = argparse.ArgumentParser()
if some_runtime_condition:
    parser.add_argument("--value")
''')
        with self.assertRaisesRegex(ParserExtractionError, "unsupported conditional"):
            load_parser(filename)

    def test_excluded_files_are_not_read_and_rerun_removes_their_directives(self):
        self.script("tool.py", "import argparse\nparser = argparse.ArgumentParser()\n")
        self.script("other.py", "import argparse\nparser = argparse.ArgumentParser()\n")
        self.script("support.py", "raise RuntimeError('must not run')\n")
        output = self.directory / "output"
        source, count = generate_docs(self.directory, output, set())
        self.assertEqual(count, 2)
        self.assertIn("other.py", (source / "index.rst").read_text())
        self.script("other.py", "invalid Python !")
        source, count = generate_docs(self.directory, output, {"other.py"})
        self.assertEqual(count, 1)
        self.assertNotIn("other.py", (source / "index.rst").read_text())
        self.assertNotIn("other.py", (source / "_cli_parsers.py").read_text())
        self.assertIn("sphinxarg.ext", (source / "conf.py").read_text())

    def test_unknown_exclusion_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "Excluded files not found"):
            generate_docs(self.directory, self.directory / "out", {"typo.py"})

    def test_no_parsers_is_an_error(self):
        self.script("support.py", "import argparse\n")
        with self.assertRaisesRegex(ValueError, "No argparse tools"):
            generate_docs(self.directory, self.directory / "out", set())

    def test_cli_accepts_multiple_and_repeated_exclusions(self):
        with patch("scripts.generate_cli_docs.generate_docs") as generate:
            generate.return_value = (self.directory / "source", 1)
            with patch("scripts.generate_cli_docs.subprocess.run") as run:
                run.return_value.returncode = 0
                self.assertEqual(main([
                    "--exclude", "a.py", "b.py", "--exclude", "c.py",
                ]), 0)
        self.assertEqual(generate.call_args.args[2], {"a.py", "b.py", "c.py"})
        self.assertIn("-W", run.call_args.args[0])

    def test_sphinx_failure_is_propagated(self):
        with patch("scripts.generate_cli_docs.generate_docs") as generate:
            generate.return_value = (self.directory / "source", 1)
            with patch("scripts.generate_cli_docs.subprocess.run") as run:
                run.return_value.returncode = 2
                with self.assertRaises(SystemExit) as failure:
                    main([])
        self.assertEqual(failure.exception.code, 2)

    def test_all_current_tools_can_be_extracted(self):
        root = Path(__file__).resolve().parents[1]
        for filename in sorted(root.glob("*.py")):
            with self.subTest(filename=filename.name):
                parser = load_parser(filename)
                if parser is not None:
                    self.assertIsInstance(parser, argparse.ArgumentParser)
                    self.assertTrue(parser.format_help())


if __name__ == "__main__":
    unittest.main()
