from __future__ import annotations

from custom_hooks import only_module_imports


def test_failure_with_system_module(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write("from datetime import datetime")
    only_module_imports.main([f"{f}"])
    cap = capsys.readouterr()
    assert "Found non-module import: 'from datetime import datetime" in cap.out


def test_pass_with_system_module(tmpdir):
    f = tmpdir / "a.py"
    f.write("import os")
    assert only_module_imports.main([f"{f}"]) == 0


def test_failure_with_system_module_after_pass(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write("from os import path\nimport sys\nfrom datetime import datetime")
    only_module_imports.main([f"{f}"])
    cap = capsys.readouterr()
    assert "Found non-module import: 'from datetime import datetime" in cap.out


def test_failure_with_non_importable_module_capitalized(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write("from jorgetomtz import Jorge")
    only_module_imports.main([f"{f}"])
    cap = capsys.readouterr()
    assert "Found non-module import: 'from jorgetomtz import Jorge" in cap.out


def test_pass_with_non_importable_module_unknown(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write("from jorgetomtz import jorgito")
    assert only_module_imports.main([f"{f}"]) == 0


def test_skipped_with_importable_module(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write("from __future__ import annotations")
    assert only_module_imports.main(["-s", "__future__", f"{f}"]) == 0
