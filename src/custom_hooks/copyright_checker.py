"""
Simple copyright checker.
"""
from __future__ import annotations

import argparse
import datetime
import os
import re
import typing

import git

COPYRIGHT = "Copyright (c) {year} by {owner}. All rights reserved."

HASH_ENDINGS = {"cfg", "conf", "py", "sh", "tf", "yaml", "yml"}

PLAIN_ENDINGS = {"md"}

STAR_ENDINGS = {"gradle", "groovy", "java", "properties"}


def write_file(filename: str, content: str) -> None:
    """
    Write content to file.
    """
    if os.access(filename, os.W_OK):
        with open(filename, "w") as f:
            f.write(content)
    else:
        print(f"Cannot write {filename}. Skipping.")


def wrap_copyright(filename: str, new_copyright: str) -> str:
    """
    Wrap copyright into ending specific comments.
    """
    wrapped = ""
    ending = filename.split(".")[-1]
    if ending in HASH_ENDINGS:
        wrapped = f"#\n# {new_copyright}\n#\n\n"
    elif ending in PLAIN_ENDINGS:
        wrapped = new_copyright
    elif ending in STAR_ENDINGS:
        wrapped = f"/*\n * {new_copyright}\n */\n\n"
    # TODO: Add other cases here
    return wrapped


def insert_missing_copyright(
    filename: str, content: str, year: str, owner: str
) -> None:
    """
    Insert missing copyright.
    """
    new_copyright = COPYRIGHT.format(year=year, owner=owner)
    wrapped = wrap_copyright(filename, new_copyright)
    if wrapped:
        print(f"Adding copyright to {filename}")
        if content.startswith("#!"):
            # Preserve shebang
            index = content.find("\n") + 1
            content = content[:index] + wrapped + content[index:]
        else:
            content = wrapped + content
        write_file(filename, content)
    else:
        print(f"Missing copyright for file {filename}")


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
    if os.access(filename, os.R_OK):
        with open(filename, encoding="utf-8") as f:
            content = f.read()
    else:
        print(f"Cannot read {filename}. Skipping.")
        return 0
    m = copyright_rgx.search(content)
    if m:
        changes = repo.git.diff(["@{upstream}", "@", filename])
        first = m.group(1)
        if changes and year != first:
            second = m.group(2)
            if second is not None:
                if not second.endswith(year):
                    if update:
                        print(f"Updating copyright: {filename}")
                        new_copyright = m.group(0).replace(second, f", {year}")
                        content = copyright_rgx.sub(new_copyright, content)
                        write_file(filename, content)
                    else:
                        print(f"Copyright is out-of-date: {filename}")
                    return 1
            else:
                if update:
                    print(f"Updating copyright: {filename}")
                    new_copyright = m.group(0).replace(first, f"{first}, {year}")
                    content = copyright_rgx.sub(new_copyright, content)
                    write_file(filename, content)
                else:
                    print(f"Copyright is out-of-date: {filename}")
                return 1
        return 0
    else:
        if update:
            insert_missing_copyright(filename, content, year, owner)
        else:
            print(f"Missing copyright for file {filename}")
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
        required=True,
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
