from __future__ import annotations

import argparse
import os
import re
import typing

import git

VERSION_FILES = ["pyproject.toml", "setup.cfg"]


def check_version_file(version_file: str):
    """
    Check if version entry in version_file has been modified.

    :param version_file: The file that includes the package version.
    """
    version_rgx = re.compile(
        'version = "?(([0-9]+)\\.?([0-9+])?\\.?([0-9+])?\\.?([0-9+])?)"?'
    )
    content = ""
    with open(version_file) as f:
        content = f.read()
    m = version_rgx.search(content)
    if m:
        repo = git.Repo(".")
        changes = repo.git.diff(["@{upstream}", "@", version_file])
        if changes:
            m = version_rgx.search(content)
            if m:
                return 0
        print(f"Version bumped required in {version_file}")
        return 1
    else:
        return 0


def check_version_bump(filenames: list[str]) -> int:
    """
    Check whether the version was appropriately bumped for a change.
    """
    result = 0
    paths_to_check: set[str] = set()
    for filename in filenames:
        path = os.path.dirname(filename)
        # Bubble up from each file to all pattern directories
        while path and path not in paths_to_check:
            paths_to_check.add(path)
            path = os.path.dirname(path)

    seen: set[str] = set()
    for dirname in paths_to_check:
        if dirname not in seen:
            for version_file in VERSION_FILES:
                version_file_path = os.path.join(dirname, version_file)
                if os.path.exists(version_file_path):
                    result = check_version_file(version_file_path) or result
            seen.add(dirname)
    return result


def main(argv: typing.Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames pre-commit believes are changed.",
    )
    args = parser.parse_args(argv)
    return check_version_bump(args.filenames)


if __name__ == "__main__":
    raise SystemExit(main())
