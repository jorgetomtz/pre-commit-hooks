import argparse
import os
import re
import typing

import git

VERSION_FILES = ["pyproject.toml", "setup.cfg", "setup.py"]


def check_version_file(version_file: str):
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
        print(f"Version bumped required for {version_file}")
        return 1
    else:
        return 0


def check_version_bump(filenames: list[str]) -> int:
    seen: set[str] = set()
    result = 0
    for filename in filenames:
        dirname = os.path.dirname(filename)
        if dirname not in seen:
            for version_file in VERSION_FILES:
                version_file_path = os.path.join(dirname, version_file)
                if os.path.exists(version_file_path):
                    result &= check_version_file(version_file_path)
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
