"""
Hook to verify only modules are imported.

This is adapted from https://stackoverflow.com/a/45390670
"""
from __future__ import annotations

import argparse
import typing

import astroid


def _check_only_modules_imported(filename: str, skip_modules: set[str]) -> int:
    """
    Parse the content of the filename and inspect the ImportFrom nodes.
    If we fail to import, we check if name imported is capitalized going
    against the module naming convention. Otherwise, we continue.

    Note: This is a best-effort approach. If libraries used in module are not
    available in environment where hook is run, then we will always fail to
    import and would only check based on module name heuristic.
    """
    result = 0
    with open(filename) as f:
        content = f.read()
    tree = astroid.parse(content)
    for node in tree.body:
        if isinstance(node, astroid.ImportFrom):
            # Skip user's configured modules
            if node.modname in skip_modules:
                continue
            try:
                imported_module = node.do_import_module(node.modname)
            except astroid.AstroidBuildingException:
                # If we fail to import, we use the convention
                # that modules are all lowercase to catch some
                # other cases of object imports
                for name, _alias in node.names:
                    if name[0].isupper():
                        print(
                            f"Found non-module import: '{node.as_string()}' "
                            f"in '{filename}:{node.end_lineno}'"
                        )
                        result = 1
                continue

            for name, _alias in node.names:
                # Skip wildcard imports
                if name == "*":
                    continue

                try:
                    imported_module.import_module(name, True)
                except astroid.AstroidImportError:
                    # If we fail to import, this means 'name' is not a module.
                    print(
                        f"Found non-module import: '{node.as_string()}' "
                        f"in '{filename}:{node.end_lineno}'"
                    )
                    result = 1
                except astroid.AstroidBuildingException:
                    pass
    return result


def check_only_modules_imported(filenames: list[str], skip_modules: set[str]) -> int:
    """
    Check if only modules are imported on each file.
    """
    result = 0
    for filename in filenames:
        result = _check_only_modules_imported(filename, skip_modules) or result
    return result


def main(argv: typing.Sequence[str] | None = None) -> int:
    """
    Best effort hook for checking only module imports.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames pre-commit believes are changed.",
    )
    parser.add_argument(
        "-s",
        "--skip-modules",
        default=[],
        type=lambda x: x.split(","),
        help="Comma-separated list of modules to skip.",
    )
    args = parser.parse_args(argv)
    return check_only_modules_imported(args.filenames, set(args.skip_modules))


if __name__ == "__main__":
    raise SystemExit(main())
