from __future__ import annotations

import pytest


class FakeDiff:
    def __init__(self, a_path):
        self.a_path = a_path


class FakeIndex:
    def __init__(self, diffs):
        self.diffs = diffs

    def diff(self, *args, **kwargs):
        return self.diffs


class FakeGit:
    def __init__(self, changes, date):
        self.changes = changes
        self.date = date

    def diff(self, *args, **kwargs):
        return self.changes

    def log(self, *args, **kwargs):
        return self.date


class FakeGitRepo:
    def __init__(self, changes, date, working_dir, files):
        self.git = FakeGit(changes, date)
        self.index = FakeIndex([FakeDiff(f) for f in files])
        self.working_dir = working_dir


@pytest.fixture()
def date():
    return "1704321349"


@pytest.fixture()
def changes():
    return "\n+Changes Found\n"


@pytest.fixture()
def files():
    return ["CHANGELOG.md"]


@pytest.fixture(autouse=True)
def fake_git(mocker, date, changes, files, tmpdir):
    mocker.patch("git.Repo", return_value=FakeGitRepo(changes, date, tmpdir, files))
