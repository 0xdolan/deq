from __future__ import annotations

import math

import pytest

from deq_spec import SpecError
from deq_spec import geometry as g


def close(p: tuple[float, float], q: tuple[float, float]) -> bool:
    return math.isclose(p[0], q[0], abs_tol=1e-9) and math.isclose(p[1], q[1], abs_tol=1e-9)


def test_transforms_compose() -> None:
    t = g.rotate(90, (12, 12)).then(g.translate(1, 0))
    assert close(t.apply((22, 12)), (13, 22))
    s = g.scale(2, (12, 12))
    assert close(s.apply((13, 12)), (14, 12))
    assert s.scale == 2
    assert close(g.IDENTITY.apply((3, 4)), (3, 4))


def test_parse_path_and_errors() -> None:
    segs = g.parse_path("M 0 0 L 1 1 H 3 V 4 Q 1 1 2 2 C 0 0 1 1 2 2 Z")
    assert [s[0] for s in segs] == ["M", "L", "L", "L", "Q", "C", "Z"]
    assert segs[2][1] == (3.0, 1.0)
    assert segs[3][1] == (3.0, 4.0)
    for bad in ["M 0 0 a 1 1", "0 0", "M 0", "M 0 0 L 1 1 x"]:
        with pytest.raises(SpecError):
            g.parse_path(bad)


def test_star_points() -> None:
    pts = g.star_points(0, 0, 5, 10, 5, -90)
    assert len(pts) == 10
    assert close(pts[0], (0, -10))


def test_bbox_and_extremes() -> None:
    items: list[g.Flat] = [
        g.Poly(((2, 2), (4, 6)), False, "a"),
        g.Circle(10, 10, 1, "a", "fill", dot=True),
    ]
    assert g.bbox(items, 2) == (1, 1, 10, 10)
    arc = g.Arc(0, 0, 1, 180, 360, "a")
    x, y, w, h = g.bbox([arc])
    assert (round(x, 9), round(y, 9), round(w, 9), round(h, 9)) == (-1, -1, 2, 1)
    ell = g.Ellipse(0, 0, 2, 1, 0, "a")
    assert g.bbox([ell]) == (-2, -1, 4, 2)
    path = g.Path(g.parse_path("M 0 0 Q 1 2 2 0 C 2 -2 4 -2 4 0 Z"), "a")
    _bx, by, bw, bh = g.bbox([path])
    assert math.isclose(by + bh, 1.0)
    assert math.isclose(by, -1.5)
    assert bw == 4
    with pytest.raises(SpecError):
        g.bbox([])


def test_transform_flat_each_kind() -> None:
    t = g.translate(1, 1).then(g.scale(2))
    items: list[g.Flat] = [
        g.Poly(((0, 0), (1, 0)), False, "a"),
        g.Circle(0, 0, 1, "a"),
        g.Circle(0, 0, 1, "a", "fill", dot=True),
        g.Arc(0, 0, 1, 0, 90, "a"),
        g.Ellipse(0, 0, 1, 2, 0, "a"),
        g.Path(g.parse_path("M 0 0 L 1 0"), "a"),
    ]
    out = [g.transform_flat(i, t) for i in items]
    assert out[0].points[1] == (4, 2)  # type: ignore[union-attr]
    assert out[1].r == 2  # type: ignore[union-attr]
    assert out[2].r == 1  # type: ignore[union-attr]
    assert out[3].r == 2  # type: ignore[union-attr]
    assert out[4].rx == 2  # type: ignore[union-attr]
    assert out[5].segments[1][1] == (4, 2)  # type: ignore[union-attr]
    rot = g.transform_flat(g.Arc(0, 0, 1, 0, 90, "a"), g.rotate(90))
    assert math.isclose(rot.start, 90)  # type: ignore[union-attr]


def test_samples_and_centroid() -> None:
    items: list[g.Flat] = [
        g.Poly(((0, 0), (2, 0), (2, 2)), True, "a"),
        g.Circle(5, 5, 1, "a"),
        g.Circle(8, 8, 1, "a", "fill", dot=True),
        g.Arc(0, 0, 1, 0, 90, "a"),
        g.Ellipse(0, 0, 1, 2, 0, "a"),
        g.Path(g.parse_path("M 0 0 Q 1 1 2 0 C 3 1 4 1 5 0 Z"), "a"),
    ]
    assert len(g.samples(items, 0.5)) > 20
    cx, cy = g.ink_centroid([g.Poly(((0, 0), (4, 0)), False, "a")])
    assert math.isclose(cx, 2)
    assert math.isclose(cy, 0)
    fill = g.Poly(((0, 0), (2, 0), (2, 2), (0, 2)), True, "a", "fill")
    assert close(g.ink_centroid([fill]), (1, 1))
    with pytest.raises(SpecError):
        g.ink_centroid([g.Poly(((1, 1), (1, 1)), False, "a")])
