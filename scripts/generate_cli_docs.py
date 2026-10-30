#!/usr/bin/env python3
"""Build Sphinx argparse documentation without importing or running Viya tools."""

import argparse
import ast
from pathlib import Path
import subprocess
import sys
import tokenize


class ParserExtractionError(ValueError):
    """A parser cannot be reconstructed safely from its source."""


PARSER_METHODS = {
    "add_argument",
    "add_argument_group",
    "add_mutually_exclusive_group",
    "add_subparsers",
    "add_parser",
    "set_defaults",
}
ARGPARSE_VALUES = {
    name: getattr(argparse, name)
    for name in (
        "SUPPRESS",
        "REMAINDER",
        "RawDescriptionHelpFormatter",
        "RawTextHelpFormatter",
        "ArgumentDefaultsHelpFormatter",
        "MetavarTypeHelpFormatter",
    )
}


def load_parser(filename):
    """Reconstruct literal argparse declarations; never execute source code."""
    filename = Path(filename)
    with tokenize.open(str(filename)) as source:
        tree = ast.parse(source.read(), filename=str(filename))
    values = {"int": int, "str": str, "float": float, "version": sys.version_info[0]}
    parser_objects = set()
    roots = []

    def fail(node, message):
        raise ParserExtractionError(
            "{}:{}: {}".format(filename, node.lineno, message)
        )

    def is_constructor(node):
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "argparse"
            and node.func.attr == "ArgumentParser"
        )

    def is_parser_call(node):
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in values
            and id(values[node.func.value.id]) in parser_objects
            and node.func.attr in PARSER_METHODS
        )

    def contains_declarations(node):
        return any(
            is_constructor(child) or is_parser_call(child)
            for child in ast.walk(node)
        )

    def value(node):
        if isinstance(node, ast.Name) and node.id in values:
            return values[node.id]
        if isinstance(node, (ast.List, ast.Tuple)):
            items = [value(item) for item in node.elts]
            return tuple(items) if isinstance(node, ast.Tuple) else items
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "argparse"
            and node.attr in ARGPARSE_VALUES
        ):
            return ARGPARSE_VALUES[node.attr]
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
        ):
            owner, method = node.func.value.id, node.func.attr
            if (owner, method) in (("Path", "cwd"), ("os", "getcwd")):
                if not node.args and not node.keywords:
                    return Path.cwd() if owner == "Path" else str(Path.cwd())
            if (owner, method) == ("argparse", "FileType"):
                args, kwargs = arguments(node)
                return argparse.FileType(*args, **kwargs)
        try:
            return ast.literal_eval(node)
        except (ValueError, TypeError):
            fail(node, "unsupported dynamic argparse value")

    def arguments(node):
        if any(isinstance(item, ast.Starred) for item in node.args) or any(
            item.arg is None for item in node.keywords
        ):
            fail(node, "expanded argparse arguments are not supported")
        return (
            [value(item) for item in node.args],
            {item.arg: value(item.value) for item in node.keywords},
        )

    def declaration(node):
        args, kwargs = arguments(node)
        if is_constructor(node):
            kwargs.setdefault("prog", filename.name)
            result = argparse.ArgumentParser(*args, **kwargs)
            roots.append(result)
        else:
            result = getattr(values[node.func.value.id], node.func.attr)(*args, **kwargs)
        parser_objects.add(id(result))
        return result

    def visit(statements):
        for statement in statements:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if contains_declarations(statement):
                    visit(statement.body)
            elif isinstance(statement, ast.If) and contains_declarations(statement):
                test = statement.test
                if (
                    isinstance(test, ast.Compare)
                    and isinstance(test.left, ast.Name)
                    and test.left.id == "version"
                    and len(test.ops) == 1
                    and isinstance(test.ops[0], ast.Eq)
                    and len(test.comparators) == 1
                ):
                    is_current_version = (
                        value(test.comparators[0]) == sys.version_info[0]
                    )
                    branch = statement.body if is_current_version else statement.orelse
                    visit(branch)
                else:
                    fail(statement, "unsupported conditional parser declaration")
            elif isinstance(statement, ast.Try) and contains_declarations(statement):
                branches = [
                    block for block in [statement.body, *(h.body for h in statement.handlers)]
                    if any(contains_declarations(item) for item in block)
                ]
                if len(branches) != 1 or statement.orelse or statement.finalbody:
                    fail(statement, "ambiguous parser declarations in try statement")
                visit(branches[0])
            elif isinstance(statement, ast.Assign) and len(statement.targets) == 1:
                target = statement.targets[0]
                if not isinstance(target, ast.Name):
                    continue
                expression = statement.value
                if is_constructor(expression) or is_parser_call(expression):
                    values[target.id] = declaration(expression)
                else:
                    try:
                        constant = ast.literal_eval(expression)
                    except (ValueError, TypeError):
                        if target.id == "cwd":
                            values[target.id] = value(expression)
                    else:
                        values[target.id] = constant
            elif isinstance(statement, ast.Expr) and is_parser_call(statement.value):
                declaration(statement.value)
            elif contains_declarations(statement):
                fail(statement, "unsupported parser declaration")

    visit(tree.body)
    if not roots:
        return None
    root = values.get("parser")
    if root not in roots:
        if len(roots) != 1:
            raise ParserExtractionError("{}: ambiguous root parser".format(filename))
        root = roots[0]
    return root


def generate_docs(source_dir, output_dir, excludes):
    """Write a Sphinx project and return its source directory and tool count."""
    source_dir = Path(source_dir).resolve()
    output_dir = Path(output_dir).resolve()
    if not source_dir.is_dir():
        raise ValueError("Source directory does not exist: {}".format(source_dir))
    candidates = sorted(source_dir.glob("*.py"))
    unknown = set(excludes) - {path.name for path in candidates}
    if unknown:
        raise ValueError("Excluded files not found: {}".format(", ".join(sorted(unknown))))

    tools = []
    for filename in candidates:
        if filename.name in excludes:
            continue
        if load_parser(filename) is None:
            print("Skipping {}: no argparse parser found".format(filename.name))
        else:
            tools.append(filename)
    if not tools:
        raise ValueError("No argparse tools found after exclusions")

    sphinx_source = output_dir / "source"
    sphinx_source.mkdir(parents=True, exist_ok=True)
    (sphinx_source / "conf.py").write_text(
        "import sys\n"
        "from pathlib import Path\n"
        "sys.path.insert(0, str(Path(__file__).parent))\n"
        "sys.path.insert(0, {!r})\n"
        "project = 'pyviyatools CLI reference'\n"
        "extensions = ['sphinxarg.ext']\n"
        "master_doc = 'index'\n"
        "html_theme = 'alabaster'\n".format(str(Path(__file__).resolve().parent)),
        encoding="utf-8",
    )
    adapters = ["from generate_cli_docs import load_parser\n"]
    title = "pyviyatools CLI reference"
    pages = [title, "=" * len(title), "", "Generated from argparse definitions.", ""]
    for index, filename in enumerate(tools):
        function = "parser_{}".format(index)
        adapters.append(
            "\ndef {}():\n    return load_parser({!r})\n".format(function, str(filename))
        )
        pages.extend([
            filename.name, "-" * len(filename.name), "",
            ".. argparse::",
            "   :module: _cli_parsers",
            "   :func: " + function,
            "   :prog: " + filename.name,
            "",
        ])
    (sphinx_source / "_cli_parsers.py").write_text("".join(adapters), encoding="utf-8")
    (sphinx_source / "index.rst").write_text("\n".join(pages), encoding="utf-8")
    return sphinx_source, len(tools)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir", type=Path, default=Path(__file__).resolve().parents[1],
        help="Directory containing tools (non-recursive; default: repository root)",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("docs/cli"),
        help="Generated Sphinx source and HTML directory (default: docs/cli)",
    )
    parser.add_argument(
        "--exclude", nargs="+", action="append", default=[], metavar="FILE.py",
        help="Exact filenames to exclude; accepts multiple names and can be repeated",
    )
    args = parser.parse_args(argv)
    try:
        source, count = generate_docs(
            args.source_dir, args.output_dir,
            {name for group in args.exclude for name in group},
        )
    except (OSError, SyntaxError, ValueError, TypeError, argparse.ArgumentError) as error:
        parser.exit(1, "Documentation generation failed: {}\n".format(error))
    result = subprocess.run([
        sys.executable, "-m", "sphinx", "-W", "--keep-going", "-E", "-a",
        "-b", "html", str(source), str(source.parent / "html"),
    ])
    if result.returncode:
        parser.exit(
            result.returncode,
            "Sphinx build failed. Install documentation dependencies with "
            "'python3 -m pip install -r requirements-docs.txt' if needed.\n",
        )
    print("Documented {} tools: {}".format(count, source.parent / "html" / "index.html"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
