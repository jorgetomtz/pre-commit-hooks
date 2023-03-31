from __future__ import annotations

from custom_hooks import check_version_bumped


def test_no_bump(tmpdir, fake_git_no_changes):
    d = tmpdir / "d"
    d.mkdir()
    f = d / "setup.cfg"
    f.write("version = 0.1.0")
    f1 = d / "a.py"
    f1.write("hello")
    assert check_version_bumped.main([f"{f1}"]) == 0


def test_no_bump_and_required(capsys, tmpdir):
    d = tmpdir / "d"
    d.mkdir()
    f = d / "pyproject.toml"
    f.write("version = 0.1.0")
    f1 = d / "a.py"
    f1.write("hello")
    check_version_bumped.main([f"{f1}"])
    cap = capsys.readouterr()
    assert f"Version bumped required in {f}" in cap.out


def test_bump_and_required(capsys, tmpdir, fake_git_version_changes):
    d = tmpdir / "d"
    d.mkdir()
    f = d / "pyproject.toml"
    f.write("version = 0.1.0")
    f1 = d / "a.py"
    f1.write("hello")
    assert check_version_bumped.main([f"{f1}"]) == 0
