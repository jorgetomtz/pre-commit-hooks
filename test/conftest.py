from __future__ import annotations

import pytest

CHANGES = """
+Changes Found
"""


class FakeGit:
    def __init__(self, changes):
        self.changes = changes

    def diff(self, args):
        return self.changes


class FakeGitRepo:
    def __init__(self, changes):
        self.git = FakeGit(changes)


@pytest.fixture(autouse=True)
def fake_git(mocker):
    mocker.patch("git.Repo", return_value=FakeGitRepo(CHANGES))


@pytest.fixture
def fake_git_no_changes(mocker):
    mocker.patch("git.Repo", return_value=FakeGitRepo(""))
