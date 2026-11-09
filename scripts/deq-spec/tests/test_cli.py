from __future__ import annotations

import argparse
import os
from pathlib import Path

import pytest

from deq_spec import cli


def run(repo: Path, *args: str) -> int:
    return cli.main(["--root", str(repo), *args])


def test_lint_ok_and_stale_sheet(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(repo, "lint") == 0
    assert "97 shapes OK" in capsys.readouterr().out
    (repo / "docs/design/logo-concepts.svg").write_text("x", encoding="utf-8")
    assert run(repo, "lint") == 1
    assert "stale or missing" in capsys.readouterr().err


def test_fmt(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(repo, "fmt", "--check") == 0
    path = repo / "spec/shapes/dot.json"
    path.write_text(
        path.read_text(encoding="utf-8").replace('"metrics": {', '"metrics": {"x": 1, ', 1)
    )
    assert run(repo, "fmt", "--check") == 1
    assert "spec/shapes/dot.json" in capsys.readouterr().out
    assert run(repo, "fmt") == 0
    assert run(repo, "fmt", "--check") == 0
    path.write_text(path.read_text(encoding="utf-8").replace('"type": "dot"', '"type": "zz"'))
    assert run(repo, "fmt") == 2
    assert "cannot compute metrics" in capsys.readouterr().err


def test_render(repo: Path, capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    assert run(repo, "render", "cross-dotted", "--param", "dots=ends") == 0
    assert "<title>cross-dotted</title>" in capsys.readouterr().out
    assert run(repo, "render", "comb", "--param", "teeth=3") == 0
    assert run(repo, "render", "fork", "--param", "nope=true") == 2
    out = tmp_path / "out.svg"
    assert run(repo, "render", "dot", "--out", str(out)) == 0
    assert run(repo, "render", "dot", "--out", str(out)) == 2
    assert run(repo, "render", "dot", "--out", str(out), "--force") == 0
    link = tmp_path / "link.svg"
    os.symlink(out, link)
    assert run(repo, "render", "dot", "--out", str(link), "--force") == 2


def test_sheet(repo: Path, tmp_path: Path) -> None:
    assert run(repo, "sheet", "--set", "concepts", "--force") == 0
    out = tmp_path / "s" / "shapes.svg"
    assert run(repo, "sheet", "--out", str(out)) == 0
    assert out.read_text(encoding="utf-8").startswith("<!-- Generated")


def test_param_parsing() -> None:
    assert cli._param("a=true") == ("a", True)
    assert cli._param("a=-3") == ("a", -3)
    assert cli._param("a=x") == ("a", "x")
    with pytest.raises(argparse.ArgumentTypeError):
        cli._param("novalue")
