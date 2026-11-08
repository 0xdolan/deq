"""Computed metrics and symmetry checks for expanded shapes."""

from __future__ import annotations

import math
from collections.abc import Iterator, Mapping
from itertools import product
from typing import Any

from deq_spec import geometry as g
from deq_spec.spec import ParamValue, round3

#: Above this many parameter combinations, vary one parameter at a time instead.
MAX_COMBOS = 256
STROKE = 2.0


def compute(items: list[g.Flat]) -> dict[str, Any]:
    """The ``metrics`` block for a shape expanded at its defaults."""
    bx = g.bbox(items)
    vb = g.bbox(items, STROKE)
    cx, cy = g.ink_centroid(items, STROKE)
    size = max(vb[2], vb[3])
    return {
        "bbox": [round3(v) for v in bx],
        "visualBox": [round3(v) for v in vb],
        "opticalCenter": [round3(cx), round3(cy)],
        "strokeToSize": round3(STROKE / size) if size else 0,
        "primitiveCount": len(items),
    }


def _values(decl: Mapping[str, Any]) -> list[ParamValue]:
    if decl["type"] == "integer":
        return list(dict.fromkeys([decl["min"], decl["default"], decl["max"]]))
    if decl["type"] == "boolean":
        return [decl["default"], not decl["default"]]
    return list(decl["values"])


def combos(parameters: Mapping[str, Mapping[str, Any]]) -> Iterator[dict[str, ParamValue]]:
    """Parameter settings to test: every combination, or one parameter at a time if too many."""
    names = list(parameters)
    choices = [_values(parameters[n]) for n in names]
    if math.prod(len(c) for c in choices) <= MAX_COMBOS:
        for values in product(*choices):
            yield dict(zip(names, values, strict=True))
        return
    yield {}
    for name, options in zip(names, choices, strict=True):
        for v in options:
            yield {name: v}


def _mapper(symmetry: str, center: g.Point) -> list[g.Transform]:
    cx, cy = center
    mx = g.Transform(a=-1, e=2 * cx)
    my = g.Transform(d=-1, f=2 * cy)
    if symmetry == "mirror-x":
        return [mx]
    if symmetry == "mirror-y":
        return [my]
    if symmetry == "mirror-xy":
        return [mx, my]
    if symmetry.startswith("rotational-"):
        n = int(symmetry.removeprefix("rotational-"))
        return [g.rotate(360 / n, center)]
    return []


def symmetry_errors(
    items: list[g.Flat], symmetry: str, center: g.Point, tol: float = 0.12
) -> list[str]:
    """Sample the centre lines and check each mapped sample lands near another sample."""
    pts = g.samples(items, 0.05)
    cell = 0.1
    grid: dict[tuple[int, int], list[g.Point]] = {}
    for p in pts:
        grid.setdefault((round(p[0] / cell), round(p[1] / cell)), []).append(p)
    errors = []
    for t in _mapper(symmetry, center):
        worst = 0.0
        for p in pts:
            q = t.apply(p)
            ix, iy = round(q[0] / cell), round(q[1] / cell)
            near = min(
                (
                    math.dist(q, r)
                    for dx in (-2, -1, 0, 1, 2)
                    for dy in (-2, -1, 0, 1, 2)
                    for r in grid.get((ix + dx, iy + dy), ())
                ),
                default=math.inf,
            )
            worst = max(worst, near)
        if worst > tol:
            off = "more than 0.2" if math.isinf(worst) else f"{worst:.3f}"
            errors.append(f"not {symmetry} about {list(center)}: a sample is off by {off}")
            break
    return errors
