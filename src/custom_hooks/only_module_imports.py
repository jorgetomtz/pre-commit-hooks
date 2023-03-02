"""
Hook to verify only modules are imported.

This is adapted from https://stackoverflow.com/a/45390670
"""
from __future__ import annotations

import argparse
import typing

import astroid


def _check_only_modules_imported(filename: str) -> int:
    result = 0
    with open(filename) as f:
        content = f.read()
    tree = astroid.parse(content)
    for node in tree.body:
        if isinstance(node, astroid.ImportFrom):
            # Skip __future__ imports
            if node.modname == "__future__":
                continue
            try:
                imported_module = node.do_import_module(node.modname)
            except astroid.AstroidBuildingException:
                continue

            for name, _alias in node.names:
                # Skip wildcard imports
                if name == "*":
                    continue

                try:
                    imported_module.import_module(name, True)
                except astroid.AstroidImportError:
                    print(
                        f"Found non-module import: '{node.as_string()}' "
                        f"in '{filename}:{node.end_lineno}'"
                    )
                    result = 1
                except astroid.AstroidBuildingException:
                    pass
    return result


def check_only_modules_imported(filenames: list[str]) -> int:
    result = 0
    for filename in filenames:
        result = _check_only_modules_imported(filename) or result
    return result


def main(argv: typing.Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames pre-commit believes are changed.",
    )
    args = parser.parse_args(argv)
    return check_only_modules_imported(args.filenames)


if __name__ == "__main__":
    raise SystemExit(main())
