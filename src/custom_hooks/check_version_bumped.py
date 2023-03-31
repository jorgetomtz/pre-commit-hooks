from __future__ import annotations

import argparse
import os
import re
import typing

import git

from custom_hooks import utils

VERSION_FILES = ["pyproject.toml", "setup.cfg"]


def check_version_file(repo: git.Repo, version_file: str):
    """
    Check if version entry in version_file has been modified.

    :param version_file: The file that includes the package version.
    """
    version_rgx = re.compile(
        'version = "?(([0-9]+)\\.?([0-9+])?\\.?([0-9+])?\\.?([0-9+])?)"?'
    )
    with open(version_file) as f:
        content = f.read()
    if version_rgx.search(content):
        changes = utils.get_changes(repo, version_file)
        if version_rgx.search(changes):
            # If version in changes then it has been changed
            return 0
        else:
            # This is the file with the version but no bump
            print(f"Version bumped required in {version_file}")
            return 1
    else:
        # File doesn't have a version entry
        return 0


def check_version_bump(filenames: list[str]) -> int:
    """
    Check whether the version was appropriately bumped for a change.
    """
    result = 0
    paths_to_check: set[str] = set()
    repo = git.Repo(".")
    for filename in filenames:
        if utils.get_changes(repo, filename):
            # We only care about filenames that have actual changes
            # compared to upstream or previous commit if in detached head
            path = os.path.dirname(filename)
            # Bubble up from each file to all pattern directories
            while path and path not in paths_to_check:
                paths_to_check.add(path)
                path = os.path.dirname(path)

    # For each unique directory with at least one file changed, construct
    # possible version file paths and check if version has been bumped
    for dirname in paths_to_check:
        for version_file in VERSION_FILES:
            version_file_path = os.path.join(dirname, version_file)
            if os.path.exists(version_file_path):
                result = check_version_file(repo, version_file_path) or result
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
