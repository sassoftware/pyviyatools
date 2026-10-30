import argparse
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.generate_tool_docs import (
    ParserExtractionError,
    generate_docs,
    load_parser,
    main,
    write_markdown,
)


class GenerateToolDocsTests(unittest.TestCase):
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

    def test_generates_markdown_and_excludes_files(self):
        self.script("tool.py", "import argparse\nparser = argparse.ArgumentParser()\n")
        self.script("other.py", "import argparse\nparser = argparse.ArgumentParser()\n")
        self.script("support.py", "raise RuntimeError('must not run')\n")
        output = self.directory / "TOOLS.md"
        markdown, source, count = generate_docs(self.directory, output, set())
        self.assertEqual(markdown, output.resolve())
        self.assertEqual(count, 2)
        self.assertIsNone(source)
        content = output.read_text()
        self.assertIn("# pyviyatools Tool Reference", content)
        self.assertIn("## tool.py", content)
        self.assertIn("[Source](tool.py)", content)
        self.assertIn("## other.py", content)
        self.script("other.py", "invalid Python !")
        markdown, source, count = generate_docs(
            self.directory, output, {"other.py"}
        )
        self.assertEqual(count, 1)
        self.assertIsNone(source)
        self.assertNotIn("other.py", markdown.read_text())

    def test_markdown_documents_arguments_and_subcommands(self):
        filename = self.script("tool.py", '''
import argparse
from pathlib import Path
cwd = Path.cwd()
parser = argparse.ArgumentParser(description="Manage sample tools.")
parser.add_argument("--format", choices=["json", "csv"], default="json")
parser.add_argument("--directory", default=cwd)
subparsers = parser.add_subparsers(dest="action")
create_parser = subparsers.add_parser(
    "create", help="Create an item", description="Create an item with its required name."
)
create_parser.add_argument("--name", required=True, help="Item name")
''')
        parser = load_parser(filename)
        output = write_markdown([(filename, parser)], self.directory / "TOOLS.md")
        content = output.read_text()
        self.assertIn("Manage sample tools.", content)
        self.assertIn("Choices: `json, csv`", content)
        self.assertIn("Default: `'json'`", content)
        self.assertIn("Default: `current working directory`", content)
        self.assertNotIn(str(Path.cwd()), content)
        self.assertIn("### `create`", content)
        self.assertIn("Create an item with its required name.", content)
        self.assertIn("Item name", content)
        self.assertIn("Required", content)

    def test_unknown_exclusion_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "Excluded files not found"):
            generate_docs(self.directory, self.directory / "TOOLS.md", {"typo.py"})

    def test_no_parsers_is_an_error(self):
        self.script("support.py", "import argparse\n")
        with self.assertRaisesRegex(ValueError, "No argparse tools"):
            generate_docs(self.directory, self.directory / "TOOLS.md", set())

    def test_tool_name_and_exclusions_in_command_line(self):
        markdown = self.directory / "TOOLS.md"
        with patch("scripts.generate_tool_docs.generate_docs") as generate:
            generate.return_value = (markdown, None, 1)
            self.assertEqual(main([
                "--markdown-file", str(markdown),
                "--exclude", "a.py", "b.py", "--exclude", "c.py",
            ]), 0)
        self.assertEqual(generate.call_args.args[2], {"a.py", "b.py", "c.py"})
        self.assertEqual(generate.call_args.args[1], markdown)

    def test_sphinx_failure_is_propagated(self):
        with patch("scripts.generate_tool_docs.generate_docs") as generate:
            generate.return_value = (
                self.directory / "TOOLS.md",
                self.directory / "source",
                1,
            )
            with patch("scripts.generate_tool_docs.subprocess.run") as run:
                run.return_value.returncode = 2
                with self.assertRaises(SystemExit) as failure:
                    main(["--html"])
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
