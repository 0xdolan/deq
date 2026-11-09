from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from deq_spec import flag

from .conftest import Editor

FLAG = "spec/flag.json"


def check(repo: Path) -> list[str]:
    return flag.check(json.loads((repo / FLAG).read_text(encoding="utf-8")), repo)


def test_reference_matches(repo: Path) -> None:
    assert check(repo) == []


def test_parse_polygon() -> None:
    assert flag.parse_polygon("M0 0h10v5H0z") == [(0, 0), (10, 0), (10, 5), (0, 5)]
    assert flag.parse_polygon("m1 1 l2 0 2 2 V9z")[-1] == (5, 9)
    with pytest.raises(ValueError, match="command"):
        flag.parse_polygon("0 0")


def test_derived_values(repo: Path, edit: Editor) -> None:
    def mutate(d: dict[str, Any]) -> None:
        d["source"]["sha1"] = "0" * 40
        d["viewBox"] = [900, 601]
        d["aspectRatio"]["width"] = 4
        d["colors"][0]["hsl"] = [0, 0, 0]
        d["colors"][1]["hex"] = "#FFFFFE"
        d["bands"][0]["height"] = 199
        d["bands"][1]["y"] = 500
        d["sun"]["innerToOuter"] = 0.4
        d["sun"]["heightToFlagHeight"] = 0.6
        d["sun"]["center"] = [451, 300.842]
        d["contrast"][0]["ratio"] = 1
        d["variants"].append(dict(d["variants"][0]))
        d["sizes"][0]["variant"] = "nope"
        d["sizes"][3]["pixels"] = [1, 1]

    edit(FLAG, mutate)
    errs = "\n".join(check(repo))
    for needle in [
        "sha1 does not match",
        "viewBox",
        "aspectRatio",
        "color red: hsl",
        "color white #FFFFFE is not used",
        "band red",
        "band white",
        "bands do not cover",
        "innerToOuter",
        "heightToFlagHeight",
        "sun vertices differ",
        "contrast",
        "variant ids must be unique",
        "unknown variant 'nope'",
        "pixels should be",
    ]:
        assert needle in errs


def test_band_without_polygon_and_sun_count(repo: Path, edit: Editor) -> None:
    def mutate(d: dict[str, Any]) -> None:
        d["colors"][2]["hex"] = "#000000"
        d["sun"]["rays"] = 20

    edit(FLAG, mutate)
    errs = "\n".join(check(repo))
    assert "band green" in errs
    assert "vertices in the reference" in errs


def test_reference_file_guards(repo: Path, edit: Editor) -> None:
    ref = repo / "spec/reference/Flag_of_Kurdistan.svg"
    ref.write_bytes(ref.read_bytes() + b" ")
    assert check(repo) == [
        "reference file spec/reference/Flag_of_Kurdistan.svg: sha256 does not match"
    ]
    ref.write_bytes(b" " * (flag.MAX_SVG_BYTES + 1))
    assert "larger than" in check(repo)[0]
    ref.unlink()
    assert "missing or a symlink" in check(repo)[0]
