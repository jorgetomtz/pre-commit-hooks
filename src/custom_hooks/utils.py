"""
Common hook utilities.
"""
from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import git


def get_changes(repo: git.Repo, filename: str) -> str:
    """
    Get the changes committed for a file.
    """
    changes = ""
    try:
        changes = repo.git.diff(["@{upstream}", "@", filename])
    except git.exc.GitCommandError:
        # Upstream is not set or running on detached HEAD
        # Fall back to comparing against previous commit
        changes = repo.git.diff(["HEAD~", filename])
    return changes
