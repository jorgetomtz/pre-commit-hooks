from __future__ import annotations

import datetime

import pytest

from custom_hooks import copyright_checker


def test_no_args(capsys):
    with pytest.raises(SystemExit):
        copyright_checker.main()
    cap = capsys.readouterr()
    assert " error: the following arguments are required: -o/--owner" in cap.err


def test_no_copyright_py(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write("hello world")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert f"#\n# Copyright (c) {year} by fake. All rights reserved.\n#\n\n" in out
    cap = capsys.readouterr()
    assert f"Adding copyright to {f}" in cap.out


def test_no_copyright_empty_py(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write("")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert f"#\n# Copyright (c) {year} by fake. All rights reserved.\n#\n" in out
    cap = capsys.readouterr()
    assert f"Adding copyright to {f}" in cap.out


def test_current_copyright_py(capsys, tmpdir):
    f = tmpdir / "a.py"
    year = str(datetime.date.today().year)
    f.write(f"#\n# Copyright (c) {year} by fake. All rights reserved.\n#\n")
    assert copyright_checker.main(["-o", "fake", f"{f}"]) == 0


def test_old_copyright_py(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write("#\n# Copyright (c) 2000 by fake. All rights reserved.\n#\n")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert f"#\n# Copyright (c) 2000, {year} by fake. All rights reserved.\n#\n" in out
    cap = capsys.readouterr()
    assert f"Updating copyright: {f}" in cap.out


def test_old_range_copyright_py(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write("#\n# Copyright (c) 2000, 2022 by fake. All rights reserved.\n#\n")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert f"#\n# Copyright (c) 2000, {year} by fake. All rights reserved.\n#\n" in out
    cap = capsys.readouterr()
    assert f"Updating copyright: {f}" in cap.out


def test_old_copyright_py_no_changes(tmpdir, fake_git_no_changes):
    f = tmpdir / "a.py"
    t = "#\n# Copyright (c) 2000 by fake. All rights reserved.\n#\n"
    f.write(t)
    assert copyright_checker.main(["-o", "fake", f"{f}"]) == 0
    out = f.read()
    assert t == out


def test_old_copyright_py_no_update(capsys, tmpdir):
    f = tmpdir / "a.py"
    t = "#\n# Copyright (c) 2000 by fake. All rights reserved.\n#\n"
    f.write(t)
    assert copyright_checker.main(["-o", "fake", "-n", f"{f}"]) == 1
    out = f.read()
    assert t == out
    cap = capsys.readouterr()
    assert f"Copyright is out-of-date: {f}" in cap.out


def test_no_copyright_py_with_shebang_and_encoding(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write("#! /usr/bin/env python3\n# coding: utf-8\n\nhello world")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert (
        "#! /usr/bin/env python3\n# coding: utf-8\n#\n"
        f"# Copyright (c) {year} by fake. All rights reserved.\n#\n\nhello world" in out
    )
    cap = capsys.readouterr()
    assert f"Adding copyright to {f}" in cap.out


def test_no_copyright_py_with_encoding(capsys, tmpdir):
    f = tmpdir / "a.py"
    f.write("# -*- coding: iso-8859-15 -*-\n\nhello world")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert (
        "# -*- coding: iso-8859-15 -*-\n#\n"
        f"# Copyright (c) {year} by fake. All rights reserved.\n#\n\nhello world" in out
    )
    cap = capsys.readouterr()
    assert f"Adding copyright to {f}" in cap.out


def test_no_copyright_sh_with_shebang(capsys, tmpdir):
    f = tmpdir / "a.sh"
    f.write("#! /usr/bin/env bash\n\nhello world")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert (
        "#! /usr/bin/env bash\n#\n"
        f"# Copyright (c) {year} by fake. All rights reserved.\n#\n\nhello world" in out
    )
    cap = capsys.readouterr()
    assert f"Adding copyright to {f}" in cap.out


def test_no_copyright_md(capsys, tmpdir):
    f = tmpdir / "a.md"
    f.write("hello world")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert (
        f"[//]: # (Copyright \\(c\\) {year} by fake. All rights reserved.)\n\n"
        "hello world" in out
    )
    cap = capsys.readouterr()
    assert f"Adding copyright to {f}" in cap.out


def test_old_copyright_md(capsys, tmpdir):
    f = tmpdir / "a.md"
    f.write(
        "[//]: # (Copyright \\(c\\) 2000 by fake. All rights reserved.)\n\nhello world"
    )
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert (
        f"[//]: # (Copyright \\(c\\) 2000, {year} by fake. All rights reserved.)"
        "\n\nhello world" in out
    )
    cap = capsys.readouterr()
    assert f"Updating copyright: {f}" in cap.out


def test_no_copyright_groovy(capsys, tmpdir):
    f = tmpdir / "a.groovy"
    f.write("hello world")
    copyright_checker.main(["-o", "fake", f"{f}"])
    out = f.read()
    year = str(datetime.date.today().year)
    assert f"/*\n * Copyright (c) {year} by fake. All rights reserved.\n */\n\n" in out
    cap = capsys.readouterr()
    assert f"Adding copyright to {f}" in cap.out


def test_no_copyright_fake_ending(capsys, tmpdir):
    f = tmpdir / "a.fake"
    f.write("hello world")
    copyright_checker.main(["-o", "fake", f"{f}"])
    cap = capsys.readouterr()
    assert f"Missing copyright for file {f}" in cap.out
