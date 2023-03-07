"""
Simple copyright checker.
"""
from __future__ import annotations

import argparse
import datetime
import re
import typing

import git


def write_file(filename: str, content: str) -> None:
    """
    Write content to file.
    """
    with open(filename, "w") as f:
        f.write(content)


def check_copyright(
    filename: str, owner: str, update: bool, repo: git.Repo, year: str
) -> int:
    """
    Check the copyright of a file. Compose a basic copyright regex with
    'owner'.
    If copyright does not exist fail.
    If file has been modified and copyright doesn't include current year fail.
    """
    copyright_rgx = re.compile(
        rf"Copyright \(c\) ([0-9]{{4}})(, [0-9]{{4}})? by {owner}"
    )
    content = ""
    with open(filename) as f:
        content = f.read()
    m = copyright_rgx.search(content)
    if m:
        changes = repo.git.diff(["@{upstream}", "@", filename])
        first = m.group(1)
        if changes and year != first:
            second = m.group(2)
            if second is not None:
                if not second.endswith(year):
                    if update:
                        new_copyright = m.group(0).replace(second, f", {year}")
                        content = copyright_rgx.sub(new_copyright, content)
                        write_file(filename, content)
                    else:
                        print(f"Copyright is out-of-date for {filename}")
                    return 1
            else:
                if update:
                    new_copyright = m.group(0).replace(first, f"{first}, {year}")
                    content = copyright_rgx.sub(new_copyright, content)
                    write_file(filename, content)
                else:
                    print(f"Copyright is out-of-date for {filename}")
                return 1
        return 0
    else:
        print(f"Copyright missing for file {filename}")
        return 1


def copyright_checker(filenames: list[str], owner: str, update: bool) -> int:
    """
    Run copyright check on each file.
    """
    result = 0
    repo = git.Repo(".")
    year = str(datetime.date.today().year)
    for filename in filenames:
        result = check_copyright(filename, owner, update, repo, year) or result
    return result


def main(argv: typing.Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames pre-commit believes are changed.",
    )
    parser.add_argument(
        "-o",
        "--owner",
        help="Owner of the license.",
    )
    parser.add_argument(
        "-u",
        "--update",
        default=True,
        action="store_true",
        help="Whether to update license.",
    )
    args = parser.parse_args(argv)
    return copyright_checker(args.filenames, args.owner, args.update)


if __name__ == "__main__":
    raise SystemExit(main())
