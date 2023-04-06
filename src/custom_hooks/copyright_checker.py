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

from custom_hooks import utils

COPYRIGHT = "Copyright (c) {year} by {owner}. All rights reserved."

HASH_ENDINGS = {
    "cfg",
    "conf",
    "Dockerfile",
    "hcl",
    "ini",
    "Makefile",
    "properties",
    "ps1",
    "py",
    "sh",
    "txt",
    "tf",
    "toml",
    "yaml",
    "yml",
}

MD_ENDINGS = {"md"}

STAR_ENDINGS = {"gradle", "groovy", "java", "js", "ts"}


def read_file(filename: str) -> str | None:
    """
    Read file and return content.
    """
    content = None
    if os.access(filename, os.R_OK):
        with open(filename, encoding="utf-8") as f:
            try:
                content = f.read()
            except UnicodeDecodeError:
                print(f"Cannot decode {filename} with 'utf-8'. Skipping.")
    else:
        print(f"Cannot read {filename}. Skipping.")
    return content


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
        wrapped = f"#\n# {new_copyright}\n#\n"
    elif ending in MD_ENDINGS:
        escaped_copyright = new_copyright.replace("(", r"\(").replace(")", r"\)")
        wrapped = f"[//]: # ({escaped_copyright})\n"
    elif ending in STAR_ENDINGS:
        wrapped = f"/*\n * {new_copyright}\n */\n"
    # TODO: Add other cases here
    return wrapped


def get_index_after_special_lines(content: str) -> int:
    """
    Get index after special lines. Used to preserve shebang
    and/or encoding lines.

    TODO: Extend this function to handle other special first lines.
    """
    index = 0
    first_line_index = content.find("\n") + 1
    first_line = content[:first_line_index]
    # Encoding regex used by https://peps.python.org/pep-0263/
    encoding_rgx = re.compile(r"^[ \t\f]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)")
    if first_line.startswith("#!") or encoding_rgx.match(first_line):
        # Preserve shebang or coding in first line
        index = first_line_index
        second_line_index = content[first_line_index:].find("\n") + first_line_index + 1
        second_line = content[first_line_index:second_line_index]
        if encoding_rgx.match(second_line):
            # Preserve coding in second line
            index = second_line_index
    return index


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
        index = get_index_after_special_lines(content)
        if index != 0:
            content = content[:index] + wrapped + content[index:]
        else:
            new_line = "\n" if content else ""
            content = wrapped + new_line + content
        write_file(filename, content)
    else:
        print(f"Missing copyright for file {filename}")


def content_head(content: str) -> str:
    """
    Return the head of the content where the copyright should be.
    """
    head = []
    for line in content.splitlines():
        head.append(line)
        if line and re.match("[A-Za-z]{1}", line[0]):
            # We consider the first line of "code" to be the first line
            # with a leading character in the alphabet. We are loose
            # about this definition to ensure "head" is broad enough
            # without having to actually determine if a line is code or not
            # with full certainty.
            break
    return "\n".join(head)


def check_copyright(
    filename: str, owner: str, update: bool, repo: git.Repo, curr_year: str
) -> int:
    """
    Check the copyright of a file. Compose a basic copyright regex with
    'owner'.
    If copyright does not exist fail.
    If file has been modified and copyright doesn't include current year fail.
    """
    content = read_file(filename)
    if content is None:
        return 0

    copyright_rgx = re.compile(
        rf"Copyright \\?\(c\\?\) ([0-9]{{4}})(, [0-9]{{4}})? by {owner}"
    )
    # Search the head of the content for copyright
    if m := copyright_rgx.search(content_head(content)):
        full_match = m.group(0)
        first_year, second_year = m.groups()
        if utils.get_changes(repo, filename) and curr_year != first_year:
            if second_year is None:
                # Copyright only has one year and is out-of-date
                new_copyright = full_match.replace(
                    first_year, f"{first_year}, {curr_year}"
                )
            elif not second_year.endswith(curr_year):
                # Copyright has a year range and is out-of-date
                new_copyright = full_match.replace(second_year, f", {curr_year}")
            else:
                # Copyright is up-to-date
                return 0
            if update:
                print(f"Updating copyright: {filename}")
                content = copyright_rgx.sub(new_copyright, content, 1)
                write_file(filename, content)
            else:
                print(f"Copyright is out-of-date: {filename}")
            return 1
        else:
            # Copyright is up-to-date or no changes found
            return 0
    else:
        # No copyright found on head of file
        if update:
            insert_missing_copyright(filename, content, curr_year, owner)
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
        "-n",
        "--no-update",
        default=False,
        action="store_true",
        help="Whether to skip copyright update.",
    )
    args = parser.parse_args(argv)
    update = not args.no_update
    return copyright_checker(args.filenames, args.owner, update)


if __name__ == "__main__":
    raise SystemExit(main())
