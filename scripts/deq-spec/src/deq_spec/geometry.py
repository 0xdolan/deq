"""Flat geometry: the result of expanding a shape, plus transforms, bounds and sampling.

Every shape expands to a list of :class:`Flat` items in canvas units. Transforms are
similarities (uniform scale, rotation, translation); stroke widths and dot radii are never
scaled, so a composition keeps the 2-unit stroke of its parts.
"""

from __future__ import annotations

import itertools
import math
import re
from dataclasses import dataclass, replace
from typing import Any, Literal

from deq_spec import SpecError

type Point = tuple[float, float]
type Paint = Literal["stroke", "fill"]

#: Path commands accepted in ``path.d`` (absolute only).
PATH_TOKEN = re.compile(r"[MLHVCQZ]|-?(?:\d+\.?\d*|\.\d+)")


@dataclass(frozen=True)
class Transform:
    """``p' = M p`` for the 2 x 3 matrix ``[a c e; b d f]``, with its scale and angle."""

    a: float = 1.0
    b: float = 0.0
    c: float = 0.0
    d: float = 1.0
    e: float = 0.0
    f: float = 0.0
    scale: float = 1.0
    angle: float = 0.0

    def apply(self, p: Point) -> Point:
        x, y = p
        return (self.a * x + self.c * y + self.e, self.b * x + self.d * y + self.f)

    def then(self, outer: Transform) -> Transform:
        """The transform that applies ``self`` first, then ``outer``."""
        o = outer
        return Transform(
            a=o.a * self.a + o.c * self.b,
            b=o.b * self.a + o.d * self.b,
            c=o.a * self.c + o.c * self.d,
            d=o.b * self.c + o.d * self.d,
            e=o.a * self.e + o.c * self.f + o.e,
            f=o.b * self.e + o.d * self.f + o.f,
            scale=self.scale * o.scale,
            angle=self.angle + o.angle,
        )


IDENTITY = Transform()


def translate(dx: float, dy: float) -> Transform:
    return Transform(e=dx, f=dy)


def rotate(deg: float, center: Point = (0.0, 0.0)) -> Transform:
    """Rotate clockwise on screen (y points down) by ``deg`` about ``center``."""
    t = math.radians(deg)
    cos, sin = math.cos(t), math.sin(t)
    cx, cy = center
    return Transform(
        a=cos,
        b=sin,
        c=-sin,
        d=cos,
        e=cx - cos * cx + sin * cy,
        f=cy - sin * cx - cos * cy,
        angle=deg,
    )


def scale(s: float, center: Point = (0.0, 0.0)) -> Transform:
    cx, cy = center
    return Transform(a=s, d=s, e=cx - s * cx, f=cy - s * cy, scale=s)


@dataclass(frozen=True)
class Poly:
    points: tuple[Point, ...]
    closed: bool
    layer: str
    paint: Paint = "stroke"


@dataclass(frozen=True)
class Circle:
    cx: float
    cy: float
    r: float
    layer: str
    paint: Paint = "stroke"
    dot: bool = False


@dataclass(frozen=True)
class Arc:
    cx: float
    cy: float
    r: float
    start: float
    end: float
    layer: str
    paint: Paint = "stroke"


@dataclass(frozen=True)
class Ellipse:
    cx: float
    cy: float
    rx: float
    ry: float
    rotation: float
    layer: str
    paint: Paint = "stroke"


#: A path segment: ("M", p) / ("L", p) / ("Q", c, p) / ("C", c1, c2, p) / ("Z",).
#: Typed loosely: the command letter decides how many points follow.
type Segment = tuple[Any, ...]


@dataclass(frozen=True)
class Path:
    segments: tuple[Segment, ...]
    layer: str
    paint: Paint = "stroke"


type Flat = Poly | Circle | Arc | Ellipse | Path


def parse_path(d: str) -> tuple[Segment, ...]:
    """Parse absolute ``M L H V C Q Z`` path data into segments with explicit points."""
    tokens = PATH_TOKEN.findall(d)
    if "".join(tokens) != re.sub(r"\s+", "", d) or not tokens or tokens[0] != "M":
        raise SpecError(f"unsupported path data: {d!r}")
    arity = {"M": 2, "L": 2, "H": 1, "V": 1, "Q": 4, "C": 6, "Z": 0}
    segments: list[Segment] = []
    cur: Point = (0.0, 0.0)
    start: Point = cur
    i = 0
    while i < len(tokens):
        cmd = tokens[i]
        if cmd not in arity:
            raise SpecError(f"expected a path command at token {i} in {d!r}")
        n = arity[cmd]
        try:
            nums = [float(t) for t in tokens[i + 1 : i + 1 + n]]
        except ValueError as exc:
            raise SpecError(f"bad number after {cmd} in {d!r}") from exc
        if len(nums) != n:
            raise SpecError(f"{cmd} needs {n} numbers in {d!r}")
        i += 1 + n
        if cmd == "M":
            cur = start = (nums[0], nums[1])
            segments.append(("M", cur))
        elif cmd in {"L", "H", "V"}:
            if cmd == "L":
                cur = (nums[0], nums[1])
            elif cmd == "H":
                cur = (nums[0], cur[1])
            else:
                cur = (cur[0], nums[0])
            segments.append(("L", cur))
        elif cmd == "Q":
            ctrl = (nums[0], nums[1])
            cur = (nums[2], nums[3])
            segments.append(("Q", ctrl, cur))
        elif cmd == "C":
            c1, c2 = (nums[0], nums[1]), (nums[2], nums[3])
            cur = (nums[4], nums[5])
            segments.append(("C", c1, c2, cur))
        else:
            segments.append(("Z",))
            cur = start
    return tuple(segments)


def transform_flat(item: Flat, t: Transform) -> Flat:
    """Apply a similarity transform; dot radii and stroke widths stay unscaled."""
    if t == IDENTITY:
        return item
    if isinstance(item, Poly):
        return replace(item, points=tuple(t.apply(p) for p in item.points))
    if isinstance(item, Circle):
        cx, cy = t.apply((item.cx, item.cy))
        return replace(item, cx=cx, cy=cy, r=item.r if item.dot else item.r * t.scale)
    if isinstance(item, Arc):
        cx, cy = t.apply((item.cx, item.cy))
        return replace(
            item,
            cx=cx,
            cy=cy,
            r=item.r * t.scale,
            start=item.start + t.angle,
            end=item.end + t.angle,
        )
    if isinstance(item, Ellipse):
        cx, cy = t.apply((item.cx, item.cy))
        return replace(
            item,
            cx=cx,
            cy=cy,
            rx=item.rx * t.scale,
            ry=item.ry * t.scale,
            rotation=item.rotation + t.angle,
        )
    segments = tuple((seg[0], *(t.apply(p) for p in seg[1:])) for seg in item.segments)
    return replace(item, segments=segments)


def star_points(
    cx: float, cy: float, points: int, outer: float, inner: float, rotation: float
) -> tuple[Point, ...]:
    """Vertices of a star polygon, outer vertex first at ``rotation`` degrees."""
    out: list[Point] = []
    for k in range(points * 2):
        r = outer if k % 2 == 0 else inner
        a = math.radians(rotation + k * 180.0 / points)
        out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return tuple(out)


# --- bounds -----------------------------------------------------------------------------


def _arc_point(cx: float, cy: float, r: float, deg: float) -> Point:
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def _quad_extrema(p0: float, p1: float, p2: float) -> list[float]:
    den = p0 - 2 * p1 + p2
    if abs(den) < 1e-12:
        return []
    t = (p0 - p1) / den
    return [t] if 0 < t < 1 else []


def _cubic_extrema(p0: float, p1: float, p2: float, p3: float) -> list[float]:
    a = -p0 + 3 * p1 - 3 * p2 + p3
    b = 2 * (p0 - 2 * p1 + p2)
    c = p1 - p0
    roots: list[float] = []
    if abs(a) < 1e-12:
        if abs(b) > 1e-12:
            roots.append(-c / b)
    else:
        disc = b * b - 4 * a * c
        if disc >= 0:
            sq = math.sqrt(disc)
            roots += [(-b + sq) / (2 * a), (-b - sq) / (2 * a)]
    return [t for t in roots if 0 < t < 1]


def _quad(p0: Point, p1: Point, p2: Point, t: float) -> Point:
    u = 1 - t
    return (
        u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
        u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
    )


def _cubic(p0: Point, p1: Point, p2: Point, p3: Point, t: float) -> Point:
    u = 1 - t
    return (
        u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
        u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1],
    )


def extreme_points(item: Flat) -> list[Point]:
    """Points whose bounding box equals the item's exact geometric bounding box."""
    if isinstance(item, Poly):
        return list(item.points)
    if isinstance(item, Circle):
        return [(item.cx - item.r, item.cy - item.r), (item.cx + item.r, item.cy + item.r)]
    if isinstance(item, Arc):
        pts = [
            _arc_point(item.cx, item.cy, item.r, item.start),
            _arc_point(item.cx, item.cy, item.r, item.end),
        ]
        k = math.ceil(item.start / 90.0)
        while k * 90.0 < item.end:
            pts.append(_arc_point(item.cx, item.cy, item.r, k * 90.0))
            k += 1
        return pts
    if isinstance(item, Ellipse):
        t = math.radians(item.rotation)
        hw = math.hypot(item.rx * math.cos(t), item.ry * math.sin(t))
        hh = math.hypot(item.rx * math.sin(t), item.ry * math.cos(t))
        return [(item.cx - hw, item.cy - hh), (item.cx + hw, item.cy + hh)]
    pts = []
    cur: Point = (0.0, 0.0)
    for seg in item.segments:
        if seg[0] in {"M", "L"}:
            cur = seg[1]
            pts.append(cur)
        elif seg[0] == "Q":
            c, end = seg[1], seg[2]
            ts = _quad_extrema(cur[0], c[0], end[0]) + _quad_extrema(cur[1], c[1], end[1])
            pts += [_quad(cur, c, end, t) for t in ts] + [end]
            cur = end
        elif seg[0] == "C":
            c1, c2, end = seg[1], seg[2], seg[3]
            ts = _cubic_extrema(cur[0], c1[0], c2[0], end[0]) + _cubic_extrema(
                cur[1], c1[1], c2[1], end[1]
            )
            pts += [_cubic(cur, c1, c2, end, t) for t in ts] + [end]
            cur = end
    return pts


def bbox(items: list[Flat], stroke_width: float = 0.0) -> tuple[float, float, float, float]:
    """``(x, y, width, height)``. With ``stroke_width`` > 0, the visual box (stroke edges)."""
    if not items:
        raise SpecError("nothing to measure: the shape expands to no primitives")
    xs: list[float] = []
    ys: list[float] = []
    for item in items:
        grow = stroke_width / 2 if item.paint == "stroke" and not _is_dot(item) else 0.0
        for x, y in extreme_points(item):
            xs += [x - grow, x + grow]
            ys += [y - grow, y + grow]
    return (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))


def _is_dot(item: Flat) -> bool:
    return isinstance(item, Circle) and item.dot


# --- sampling ---------------------------------------------------------------------------


def _segment_samples(p: Point, q: Point, step: float) -> list[Point]:
    n = max(1, math.ceil(math.dist(p, q) / step))
    return [(p[0] + (q[0] - p[0]) * i / n, p[1] + (q[1] - p[1]) * i / n) for i in range(n + 1)]


def flatten_path(item: Path, steps: int = 32) -> list[list[Point]]:
    """Polylines approximating each subpath."""
    out: list[list[Point]] = []
    cur: Point = (0.0, 0.0)
    start: Point = cur
    for seg in item.segments:
        if seg[0] == "M":
            cur = start = seg[1]
            out.append([cur])
        elif seg[0] == "L":
            cur = seg[1]
            out[-1].append(cur)
        elif seg[0] == "Q":
            c, end = seg[1], seg[2]
            out[-1] += [_quad(cur, c, end, i / steps) for i in range(1, steps + 1)]
            cur = end
        elif seg[0] == "C":
            c1, c2, end = seg[1], seg[2], seg[3]
            out[-1] += [_cubic(cur, c1, c2, end, i / steps) for i in range(1, steps + 1)]
            cur = end
        else:
            out[-1].append(start)
            cur = start
    return out


def outline(item: Flat) -> list[list[Point]]:
    """Centre-line polylines of an item (circles and arcs at 2-degree steps)."""
    if isinstance(item, Poly):
        pts = list(item.points)
        return [[*pts, pts[0]] if item.closed else pts]
    if isinstance(item, Circle):
        return [[_arc_point(item.cx, item.cy, item.r, k * 2.0) for k in range(181)]]
    if isinstance(item, Arc):
        n = max(2, math.ceil((item.end - item.start) / 2.0))
        return [
            [
                _arc_point(item.cx, item.cy, item.r, item.start + (item.end - item.start) * i / n)
                for i in range(n + 1)
            ]
        ]
    if isinstance(item, Ellipse):
        t = math.radians(item.rotation)
        pts = []
        for k in range(181):
            a = math.radians(k * 2.0)
            x, y = item.rx * math.cos(a), item.ry * math.sin(a)
            pts.append(
                (
                    item.cx + x * math.cos(t) - y * math.sin(t),
                    item.cy + x * math.sin(t) + y * math.cos(t),
                )
            )
        return [pts]
    return flatten_path(item)


def samples(items: list[Flat], step: float = 0.05) -> list[Point]:
    """Points spaced about ``step`` apart along every item; dots add their centre."""
    out: list[Point] = []
    for item in items:
        if _is_dot(item):
            assert isinstance(item, Circle)  # noqa: S101 - narrowed by _is_dot
            out.append((item.cx, item.cy))
        for line in outline(item):
            for p, q in itertools.pairwise(line):
                out += _segment_samples(p, q, step)
    return out


def _polygon_area_centroid(pts: list[Point]) -> tuple[float, Point]:
    area = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1], strict=True):
        cross = x0 * y1 - x1 * y0
        area += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    area /= 2
    if abs(area) < 1e-12:
        return 0.0, (0.0, 0.0)
    return abs(area), (cx / (6 * area), cy / (6 * area))


def ink_centroid(items: list[Flat], stroke_width: float = 2.0) -> Point:
    """Area-weighted centre of the painted ink (overlaps are counted twice)."""
    total = sx = sy = 0.0

    def add(weight: float, p: Point) -> None:
        nonlocal total, sx, sy
        total += weight
        sx += weight * p[0]
        sy += weight * p[1]

    for item in items:
        if isinstance(item, Circle) and (item.dot or item.paint == "fill"):
            add(math.pi * item.r * item.r, (item.cx, item.cy))
        elif item.paint == "fill":
            for line in outline(item):
                area, c = _polygon_area_centroid(line[:-1] if line[0] == line[-1] else line)
                add(area, c)
        else:
            for line in outline(item):
                for p, q in itertools.pairwise(line):
                    add(math.dist(p, q) * stroke_width, ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2))
    if total == 0:
        raise SpecError("the shape has no ink")
    return (sx / total, sy / total)
