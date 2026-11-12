#!/usr/bin/env python3
"""Generate Markdown and optional Sphinx documentation without running tools."""

import argparse
import ast
import os
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


def discover_tools(source_dir, excludes):
    """Find tool parsers without importing or executing the source files."""
    source_dir = Path(source_dir).resolve()
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
        tool_parser = load_parser(filename)
        if tool_parser is None:
            print("Skipping {}: no argparse parser found".format(filename.name))
        else:
            tools.append((filename, tool_parser))
    if not tools:
        raise ValueError("No argparse tools found after exclusions")
    return tools


def markdown_text(value):
    """Escape a value for inclusion in a Markdown table cell."""
    return str(value).replace("|", r"\|").replace("\n", "<br>")


def format_metavar(action):
    if action.metavar is not None:
        if isinstance(action.metavar, tuple):
            return " ".join(str(item) for item in action.metavar)
        return str(action.metavar)
    if action.option_strings:
        return action.dest.upper()
    return action.dest


def format_default(value):
    if isinstance(value, Path):
        return "current working directory"
    return repr(value)


def render_argument(action):
    names = ", ".join(action.option_strings) or format_metavar(action)
    if action.option_strings and action.nargs != 0:
        names += " " + format_metavar(action)
    details = []
    if action.required:
        details.append("Required")
    if action.choices is not None:
        details.append("Choices: `{}`".format(
            markdown_text(", ".join(str(choice) for choice in action.choices))
        ))
    if action.default is not argparse.SUPPRESS:
        details.append(
            "Default: `{}`".format(markdown_text(format_default(action.default)))
        )
    if action.nargs not in (None, 0):
        details.append("Arguments: `{}`".format(markdown_text(action.nargs)))
    if action.type is not None:
        type_name = getattr(action.type, "__name__", str(action.type))
        details.append("Type: `{}`".format(markdown_text(type_name)))
    return (
        "| `{}` | {} | {} |".format(
            markdown_text(names),
            markdown_text(action.help or ""),
            "; ".join(details),
        )
    )


def render_parser(parser, depth=3):
    """Render one parser, including nested subcommands, as Markdown."""
    sections = []
    if parser.description:
        sections.extend([markdown_text(parser.description), ""])
    sections.extend([
        "```text",
        parser.format_usage().strip(),
        "```",
        "",
    ])
    subparser_actions = []
    for group in parser._action_groups:
        actions = [
            action for action in group._group_actions
            if action.dest != "help" and action.help != argparse.SUPPRESS
        ]
        if not actions:
            continue
        visible_actions = [
            action for action in actions
            if not isinstance(action, argparse._SubParsersAction)
        ]
        if visible_actions:
            sections.extend([
                "{} {}".format("#" * depth, group.title),
                "",
                "| Option | Description | Details |",
                "| --- | --- | --- |",
            ])
            sections.extend(render_argument(action) for action in visible_actions)
            sections.append("")
        subparser_actions.extend(
            action for action in actions
            if isinstance(action, argparse._SubParsersAction)
        )
    for subparsers in subparser_actions:
        sections.extend([
            "{} Subcommands".format("#" * depth),
            "",
        ])
        for name, child_parser in subparsers.choices.items():
            description = subparsers._choices_actions
            help_text = next(
                (choice.help for choice in description if choice.dest == name),
                "",
            )
            sections.extend([
                "{} `{}`".format("#" * (depth + 1), name),
            ])
            if help_text:
                sections.extend(["", markdown_text(help_text)])
            sections.extend(["", *render_parser(child_parser, depth + 2)])
    return sections


def write_markdown(tools, destination):
    """Write the generated tool reference to a Markdown file."""
    destination = Path(destination).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# pyviyatools Tool Reference",
        "",
        "This reference is generated from the tools' `argparse` definitions. "
        "Regenerate it after changing a tool's arguments.",
        "",
    ]
    for filename, parser in tools:
        source_link = Path(os.path.relpath(filename, destination.parent)).as_posix()
        lines.extend([
            "## {}".format(filename.name),
            "",
            "[Source]({})".format(source_link),
            "",
        ])
        lines.extend(render_parser(parser))
    destination.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return destination


def write_sphinx_source(tools, output_dir):
    """Write the Sphinx source tree used for the optional HTML reference."""
    output_dir = Path(output_dir).resolve()
    sphinx_source = output_dir / "source"
    sphinx_source.mkdir(parents=True, exist_ok=True)
    (sphinx_source / "conf.py").write_text(
        "import sys\n"
        "from pathlib import Path\n"
        "sys.path.insert(0, str(Path(__file__).parent))\n"
        "sys.path.insert(0, {!r})\n"
        "project = 'pyviyatools Tool Reference'\n"
        "extensions = ['sphinxarg.ext']\n"
        "master_doc = 'index'\n"
        "html_theme = 'alabaster'\n".format(str(Path(__file__).resolve().parent)),
        encoding="utf-8",
    )
    adapters = ["from generate_tool_docs import load_parser\n"]
    title = "pyviyatools Tool Reference"
    pages = [title, "=" * len(title), "", "Generated from argparse definitions.", ""]
    for index, (filename, _) in enumerate(tools):
        function = "parser_{}".format(index)
        adapters.append(
            "\ndef {}():\n    return load_parser({!r})\n".format(function, str(filename))
        )
        pages.extend([
            filename.name, "-" * len(filename.name), "",
            ".. argparse::",
            "   :module: _tool_parsers",
            "   :func: " + function,
            "   :prog: " + filename.name,
            "",
        ])
    (sphinx_source / "_tool_parsers.py").write_text("".join(adapters), encoding="utf-8")
    (sphinx_source / "index.rst").write_text("\n".join(pages), encoding="utf-8")
    return sphinx_source, len(tools)


def generate_docs(source_dir, markdown_file, excludes, html_output_dir=None):
    """Generate the committed Markdown reference and optional Sphinx sources."""
    tools = discover_tools(source_dir, excludes)
    markdown_path = write_markdown(tools, markdown_file)
    sphinx_source = None
    if html_output_dir is not None:
        sphinx_source, _ = write_sphinx_source(tools, html_output_dir)
    return markdown_path, sphinx_source, len(tools)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir", type=Path, default=Path(__file__).resolve().parents[1],
        help="Directory containing tools (non-recursive; default: repository root)",
    )
    parser.add_argument(
        "--markdown-file", type=Path, default=Path("docs/TOOLS.md"),
        help="Generated Markdown tool reference (default: docs/TOOLS.md)",
    )
    parser.add_argument(
        "--html", action="store_true",
        help="Also generate the optional Sphinx HTML reference",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("docs/tools"),
        help="Generated Sphinx source and HTML directory when --html is used "
             "(default: docs/tools)",
    )
    parser.add_argument(
        "--exclude", nargs="+", action="append", default=[], metavar="FILE.py",
        help="Exact filenames to exclude; accepts multiple names and can be repeated",
    )
    args = parser.parse_args(argv)
    try:
        markdown_path, source, count = generate_docs(
            args.source_dir, args.markdown_file,
            {name for group in args.exclude for name in group},
            args.output_dir if args.html else None,
        )
    except (OSError, SyntaxError, ValueError, TypeError, argparse.ArgumentError) as error:
        parser.exit(1, "Documentation generation failed: {}\n".format(error))
    if args.html:
        result = subprocess.run([
            sys.executable, "-m", "sphinx", "-W", "--keep-going", "-E", "-a",
            "-b", "html", str(source), str(Path(args.output_dir).resolve() / "html"),
        ])
        if result.returncode:
            parser.exit(
                result.returncode,
                "Sphinx build failed. Install optional HTML documentation "
                "dependencies with 'python3 -m pip install -r requirements-docs.txt'.\n",
            )
        print("Generated HTML tool reference: {}".format(
            Path(args.output_dir).resolve() / "html" / "index.html"
        ))
    print("Documented {} tools in {}".format(count, markdown_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
