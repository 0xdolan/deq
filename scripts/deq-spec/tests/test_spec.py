from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

from deq_spec import SpecError, colors, jsonfmt, metrics, render
from deq_spec import geometry as g
from deq_spec.spec import MAX_FILE_BYTES, ParamValue, Registry, expand, read_json, round3


def shape(prims: list[Any], params: dict[str, Any] | None = None, sid: str = "t") -> dict[str, Any]:
    return {"id": sid, "primitives": prims, "parameters": params or {}}


def line(**kw: object) -> dict[str, object]:
    return {"type": "line", "x1": 2, "y1": 12, "x2": 22, "y2": 12, **kw}


def test_read_json(tmp_path: Path) -> None:
    ok = tmp_path / "a.json"
    ok.write_text('{"a": 1}')
    assert read_json(ok) == {"a": 1}
    bad = tmp_path / "b.json"
    bad.write_text("{")
    big = tmp_path / "c.json"
    big.write_text(" " * (MAX_FILE_BYTES + 1))
    link = tmp_path / "d.json"
    os.symlink(ok, link)
    for p in (bad, big, link, tmp_path / "missing.json"):
        with pytest.raises(SpecError):
            read_json(p)


def test_every_primitive_kind() -> None:
    reg = Registry()
    prims = [
        line(layer="a"),
        {"type": "polyline", "points": [[1, 1], [2, 2]], "layer": "a"},
        {"type": "polygon", "points": [[1, 1], [2, 2], [3, 1]], "layer": "a"},
        {"type": "path", "d": "M 1 1 L 2 2", "layer": "a"},
        {"type": "circle", "cx": 12, "cy": 12, "r": 3, "layer": "a"},
        {"type": "dot", "cx": 12, "cy": 12, "layer": "a"},
        {"type": "arc", "cx": 12, "cy": 12, "r": 3, "start": 0, "end": 90, "layer": "a"},
        {"type": "ellipse", "cx": 12, "cy": 12, "rx": 3, "ry": 2, "layer": "a"},
        {"type": "rect", "x": 2, "y": 2, "width": 4, "height": 4, "layer": "a"},
        {
            "type": "star",
            "cx": 12,
            "cy": 12,
            "points": 5,
            "outerRadius": 4,
            "innerRadius": 2,
            "rotation": 0,
            "layer": "a",
        },
        {
            "type": "repeat",
            "count": 3,
            "step": [2, 0],
            "align": "start",
            "element": line(),
            "layer": "a",
        },
        {"type": "repeat", "count": 1, "spread": [8, 0], "element": line(), "layer": "a"},
        {
            "type": "radial",
            "count": 4,
            "center": [12, 12],
            "start": 0,
            "sweep": 90,
            "element": line(),
            "layer": "a",
        },
        {
            "type": "radial",
            "count": 1,
            "center": [12, 12],
            "start": 0,
            "sweep": 90,
            "element": line(),
            "layer": "a",
        },
        {
            "type": "concentric",
            "count": 2,
            "center": [12, 12],
            "scaleStep": 0.5,
            "element": line(),
            "layer": "a",
        },
    ]
    items = expand(shape(prims), reg)
    assert len(items) == 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 3 + 1 + 4 + 1 + 2
    svg = render.svg(items, title="t", layer_colors={"a": "#ff0000"})
    assert svg.startswith("<svg")
    assert "<title>t</title>" in svg
    assert "<ellipse" in svg


def test_params_when_and_use() -> None:
    base = shape(
        [
            {
                "type": "repeat",
                "count": {"param": "n"},
                "step": [1, 0],
                "element": line(),
                "layer": "a",
            },
            {"type": "dot", "cx": 12, "cy": 12, "layer": "b", "when": {"on": True}},
            {"type": "dot", "cx": 12, "cy": 14, "layer": "b", "when": {"kind": ["x", "y"]}},
        ],
        {
            "n": {"type": "integer", "min": 0, "max": 4, "default": 2},
            "on": {"type": "boolean", "default": False},
            "kind": {"type": "enum", "values": ["x", "y", "z"], "default": "z"},
        },
        "base",
    )
    reg = Registry(shapes={"base": base})
    assert len(expand(base, reg)) == 2
    assert len(expand(base, reg, {"n": 0, "on": True, "kind": "x"})) == 2
    user = shape(
        [
            {
                "type": "use",
                "shape": "base",
                "params": {"n": 1},
                "transform": {"translate": [1, 0], "scale": 0.5, "rotate": 90},
                "layer": "u",
            }
        ]
    )
    items = expand(user, reg)
    assert {i.layer for i in items} == {"u"}
    bad_values: list[dict[str, ParamValue]] = [
        {"x": 1},
        {"n": "a"},
        {"n": 9},
        {"on": 1},
        {"kind": "w"},
    ]
    for bad in bad_values:
        with pytest.raises(SpecError):
            expand(base, reg, bad)


@pytest.mark.parametrize(
    "prim",
    [
        {"type": "dot", "cx": 1, "cy": 1},
        {"type": "nope", "layer": "a"},
        {"type": "arc", "cx": 1, "cy": 1, "r": 1, "start": 90, "end": 0, "layer": "a"},
        {
            "type": "star",
            "cx": 1,
            "cy": 1,
            "points": 1,
            "outerRadius": 1,
            "innerRadius": 1,
            "rotation": 0,
            "layer": "a",
        },
        {
            "type": "concentric",
            "count": 3,
            "center": [12, 12],
            "scaleStep": 0.5,
            "element": line(),
            "layer": "a",
        },
        {
            "type": "repeat",
            "count": {"param": "zz"},
            "step": [1, 0],
            "element": line(),
            "layer": "a",
        },
        {"type": "repeat", "count": 1.5, "step": [1, 0], "element": line(), "layer": "a"},
        {"type": "repeat", "count": -1, "step": [1, 0], "element": line(), "layer": "a"},
        {"type": "repeat", "count": 3000, "step": [0, 0], "element": line(), "layer": "a"},
        {"type": "dot", "cx": 1, "cy": 1, "layer": "a", "when": {"zz": True}},
        {"type": "use", "shape": "missing", "layer": "a"},
        {"type": "use", "shape": "t", "layer": "a"},
    ],
)
def test_expand_errors(prim: dict[str, Any]) -> None:
    s = shape([prim])
    with pytest.raises(SpecError):
        expand(s, Registry(shapes={"t": s}))


def test_depth_limit() -> None:
    el: dict[str, Any] = line()
    for _ in range(8):
        el = {"type": "repeat", "count": 1, "step": [0, 0], "element": el}
    el["layer"] = "a"
    with pytest.raises(SpecError):
        expand(shape([el]), Registry())


def test_round3_and_jsonfmt() -> None:
    assert round3(2.0000001) == 2
    assert isinstance(round3(2.0000001), int)
    assert round3(1.23456) == 1.235
    text = jsonfmt.dumps(
        {"a": [1.0, 2.5], "b": {}, "c": [], "long": ["x" * 60, "y" * 60], "d": {"e": "é"}}
    )
    assert '"a": [1, 2.5]' in text
    assert '"é"' in text
    assert text.endswith("}\n")
    assert '"long": [\n' in text


def test_colors() -> None:
    red = colors.hex_to_rgb("#ED2024")
    assert red == (237, 32, 36)
    assert colors.rgb_to_hsl((128, 128, 128))[1] == 0
    assert colors.rgb_to_cmyk((0, 0, 0)) == [0, 0, 0, 100]
    assert colors.contrast((0, 0, 0), (255, 255, 255)) == 21
    assert len(colors.rgb_to_oklch(red)) == 3
    with pytest.raises(ValueError, match="RRGGBB"):
        colors.hex_to_rgb("red")


def test_metrics_and_symmetry() -> None:
    items: list[g.Flat] = [g.Poly(((4, 12), (20, 12)), False, "a")]
    m = metrics.compute(items)
    assert m["primitiveCount"] == 1
    for sym in ["none", "mirror-x", "mirror-y", "mirror-xy", "rotational-2"]:
        assert metrics.symmetry_errors(items, sym, (12, 12)) == []
    assert metrics.symmetry_errors(items, "rotational-4", (12, 12))
    lopsided: list[g.Flat] = [g.Poly(((4, 12), (12, 12)), False, "a")]
    assert metrics.symmetry_errors(lopsided, "mirror-x", (12, 12))
    many = {f"p{i}": {"type": "integer", "min": 0, "max": 2, "default": 1} for i in range(6)}
    combos = list(metrics.combos(many))
    assert combos[0] == {}
    assert len(combos) == 1 + 6 * 3
    assert (
        len(list(metrics.combos({"e": {"type": "enum", "values": ["a", "b"], "default": "a"}})))
        == 2
    )
