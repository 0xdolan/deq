from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

from deq_spec import SpecError, lint

from .conftest import Editor

CHIN = "spec/shapes/chevron.json"


def errors(root: Path) -> list[str]:
    return lint.lint(root).errors


def test_repository_is_clean(repo: Path) -> None:
    report = lint.lint(repo)
    assert report.errors == []
    assert report.checked == 49


def test_shape_rules(repo: Path, edit: Editor) -> None:
    def mutate(d: dict[str, Any]) -> None:
        d["aliases"] = ["cross"]
        d["layers"] = ["chevron", "unused"]
        d["primitives"][0]["points"][0] = [5.0001, 16]
        d["sources"] = ["natgeo-2015", "nope"]
        d["references"]["images"] = ["no-such-image"]
        d["references"]["files"] = ["../outside.txt"]

    edit(CHIN, mutate)
    errs = "\n".join(errors(repo))
    for needle in [
        "alias 'cross' is also a shape id",
        "layer 'unused' is declared but not used",
        "has more than 3 decimals",
        "source 'mee-2022' is cited but not listed",
        "unknown source 'nope'",
        "unknown image 'no-such-image'",
        "referenced file '../outside.txt'",
    ]:
        assert needle in errs


def test_missing_layer(repo: Path, edit: Editor) -> None:
    edit(CHIN, lambda d: d["primitives"][0].pop("layer") and None)
    errs = "\n".join(errors(repo))
    assert "primitives[0] needs a layer" in errs
    assert "no layer" in errs


def test_layers_bounds_and_symmetry(repo: Path, edit: Editor) -> None:
    def mutate(d: dict[str, Any]) -> None:
        d["primitives"][0]["layer"] = "other"
        d["primitives"].append({"type": "dot", "cx": 22.5, "cy": 12, "layer": "other"})

    edit(CHIN, mutate)
    errs = "\n".join(errors(repo))
    assert "layer 'other' is used but not declared" in errs
    assert "leaves the live area" in errs
    assert "not mirror-x" in errs


def test_stale_metrics(repo: Path, edit: Editor) -> None:
    edit(CHIN, lambda d: d["metrics"].update(primitiveCount=9) or None)
    assert any("metrics are stale" in e for e in errors(repo))


def test_schema_and_filename(repo: Path, edit: Editor) -> None:
    edit(CHIN, lambda d: d.update(id="chevron-2") or None)
    assert any("file name must be chevron-2.json" in e for e in errors(repo))
    edit(CHIN, lambda d: d.update(version="one") or None)
    assert any("schema: version" in e for e in errors(repo))


def test_parameter_defaults_and_expansion(repo: Path, edit: Editor) -> None:
    def mutate(d: dict[str, Any]) -> None:
        d["parameters"]["count"]["default"] = 9
        d["parameters"]["count"]["max"] = 4

    edit("spec/shapes/chevron-stack.json", mutate)
    edit(
        "spec/shapes/triangle-dotted.json",
        lambda d: d["parameters"]["style"].update(default="nope") or None,
    )
    errs = "\n".join(errors(repo))
    assert "parameter count: default outside min..max" in errs
    assert "parameter style: default is not one of its values" in errs


def test_empty_and_broken_expansion(repo: Path, edit: Editor) -> None:
    edit(CHIN, lambda d: d["primitives"][0].update(when={"x": True}) or None)
    assert any("unknown parameter 'x'" in e for e in errors(repo))
    edit(
        CHIN,
        lambda d: (d["primitives"][0].pop("when") and d["primitives"][0].update(when={})) or None,
    )

    def nothing(d: dict[str, Any]) -> None:
        d["parameters"] = {"on": {"type": "boolean", "default": True, "description": "x"}}
        d["primitives"][0]["when"] = {"on": True}

    edit(CHIN, nothing)
    assert any("expands to nothing" in e for e in errors(repo))


def test_formatting_and_duplicates(repo: Path) -> None:
    path = repo / CHIN
    path.write_text(path.read_text(encoding="utf-8").replace("\n", "\n\n", 1), encoding="utf-8")
    (repo / "spec/grid.json").write_text(
        (repo / "spec/grid.json").read_text(encoding="utf-8") + "\n", encoding="utf-8"
    )
    dup = repo / "spec/shapes/zz-dup.json"
    dup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    (repo / "spec/shapes/zz-noid.json").write_text("[]", encoding="utf-8")
    errs = "\n".join(errors(repo))
    assert "spec/shapes/chevron.json: not canonically formatted" in errs
    assert "spec/grid.json: not canonically formatted" in errs
    assert "duplicate id 'chevron'" in errs
    assert "no string `id`" in errs


def test_symlinked_shape_is_refused(repo: Path) -> None:
    os.symlink(repo / CHIN, repo / "spec/shapes/link.json")
    with pytest.raises(SpecError):
        lint.lint(repo)


def test_catalog_rules(repo: Path, edit: Editor) -> None:
    def mutate(d: dict[str, Any]) -> None:
        cats = d["categories"]
        cats[0]["shapes"].remove("sterk-star")
        cats[0]["shapes"] += ["cross", "ghost"]
        cats[2]["shapes"].append("ring-stem")
        d["deferred"].append({"id": "dot", "reason": "x"})
        d["deferred"].append({"id": "zz", "reason": "x", "drawnAs": "ghost"})

    edit("spec/catalog.json", mutate)
    errs = "\n".join(errors(repo))
    for needle in [
        "shape sterk-star is not listed",
        "cross is listed under celestial but its category differs",
        "listed shape ghost does not exist",
        "shape ring-stem is listed 2 times",
        "deferred motif dot is also a shape",
        "drawnAs 'ghost' is not a shape",
    ]:
        assert needle in errs


def test_catalog_missing_or_invalid(repo: Path, edit: Editor) -> None:
    edit("spec/catalog.json", lambda d: d.update(version="x") or None)
    assert any("spec/catalog.json: schema" in e for e in errors(repo))
    (repo / "spec/catalog.json").unlink()
    assert "spec/catalog.json: missing" in errors(repo)


def test_no_shapes(repo: Path) -> None:
    for f in (repo / "spec/shapes").glob("*.json"):
        f.unlink()
    for f in (repo / "assets/brand/concepts").glob("*.json"):
        f.unlink()
    errs = errors(repo)
    assert "spec/shapes: no shapes found" in errs
    assert "spec/shapes: kurdish-sun is missing" in errs


def test_sun_ratio(repo: Path, edit: Editor) -> None:
    edit("spec/shapes/kurdish-sun.json", lambda d: d["primitives"][0].update(innerRadius=4) or None)
    assert any("flag innerToOuter" in e for e in errors(repo))
