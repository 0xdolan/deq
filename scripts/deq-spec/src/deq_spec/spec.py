"""Load spec files and expand shapes (generators, conditions, references) into flat geometry."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from deq_spec import SpecError
from deq_spec import geometry as g

#: Largest spec file accepted (bytes).
MAX_FILE_BYTES = 256 * 1024
#: Deepest nesting of generators and references.
MAX_DEPTH = 6
#: Most flat primitives one shape may expand to.
MAX_FLAT = 2000

type Json = Any
type ParamValue = int | bool | str


def read_json(path: Path) -> Json:
    """Read a JSON file, refusing symlinks and oversized files."""
    if path.is_symlink():
        raise SpecError(f"{path}: refusing symlink")
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise SpecError(f"{path}: {exc.strerror}") from exc
    if size > MAX_FILE_BYTES:
        raise SpecError(f"{path}: file is larger than {MAX_FILE_BYTES} bytes")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SpecError(f"{path}: invalid JSON: {exc}") from exc


@dataclass
class Registry:
    """Shapes by id, so compositions can resolve references."""

    shapes: dict[str, Json] = field(default_factory=dict)
    paths: dict[str, Path] = field(default_factory=dict)

    def get(self, shape_id: str) -> Json:
        try:
            return self.shapes[shape_id]
        except KeyError:
            raise SpecError(f"unknown shape {shape_id!r}") from None


def resolve_params(
    shape: Json, overrides: Mapping[str, ParamValue] | None = None
) -> dict[str, ParamValue]:
    """Defaults merged with ``overrides``, type- and range-checked."""
    decls: dict[str, Json] = shape.get("parameters", {})
    values: dict[str, ParamValue] = {name: d["default"] for name, d in decls.items()}
    for name, value in (overrides or {}).items():
        if name not in decls:
            raise SpecError(f"{shape['id']}: unknown parameter {name!r}")
        values[name] = value
    for name, value in values.items():
        d = decls[name]
        kind = d["type"]
        if kind == "integer":
            if isinstance(value, bool) or not isinstance(value, int):
                raise SpecError(f"{shape['id']}: parameter {name!r} must be an integer")
            if not d["min"] <= value <= d["max"]:
                raise SpecError(f"{shape['id']}: {name}={value} is outside {d['min']}..{d['max']}")
        elif kind == "boolean":
            if not isinstance(value, bool):
                raise SpecError(f"{shape['id']}: parameter {name!r} must be true or false")
        elif value not in d["values"]:
            raise SpecError(f"{shape['id']}: {name}={value!r} is not one of {d['values']}")
    return values


def _count(value: Json, params: Mapping[str, ParamValue], where: str) -> int:
    if isinstance(value, dict):
        name = value["param"]
        if name not in params:
            raise SpecError(f"{where}: unknown parameter {name!r}")
        value = params[name]
    if isinstance(value, bool) or not isinstance(value, int):
        raise SpecError(f"{where}: count must be an integer")
    if value < 0:
        raise SpecError(f"{where}: count must not be negative")
    return value


def when_matches(prim: Json, params: Mapping[str, ParamValue], where: str) -> bool:
    for name, expected in prim.get("when", {}).items():
        if name not in params:
            raise SpecError(f"{where}: `when` uses unknown parameter {name!r}")
        actual = params[name]
        options = expected if isinstance(expected, list) else [expected]
        if not any(type(o) is type(actual) and o == actual for o in options):
            return False
    return True


@dataclass(frozen=True)
class _Ctx:
    params: Mapping[str, ParamValue]
    transform: g.Transform
    layer: str
    depth: int
    where: str
    stack: tuple[str, ...]


def expand(
    shape: Json,
    registry: Registry,
    overrides: Mapping[str, ParamValue] | None = None,
) -> list[g.Flat]:
    """Expand ``shape`` at the given parameters into flat geometry."""
    params = resolve_params(shape, overrides)
    out: list[g.Flat] = []
    for i, prim in enumerate(shape["primitives"]):
        ctx = _Ctx(
            params,
            g.IDENTITY,
            prim.get("layer", ""),
            0,
            f"{shape['id']}.primitives[{i}]",
            (shape["id"],),
        )
        _expand(prim, ctx, registry, out)
    return out


def _add(out: list[g.Flat], item: g.Flat, ctx: _Ctx) -> None:
    if len(out) >= MAX_FLAT:
        raise SpecError(f"{ctx.where}: expands to more than {MAX_FLAT} primitives")
    out.append(g.transform_flat(item, ctx.transform))


def _expand(prim: Json, ctx: _Ctx, registry: Registry, out: list[g.Flat]) -> None:
    if ctx.depth > MAX_DEPTH:
        raise SpecError(f"{ctx.where}: nested deeper than {MAX_DEPTH}")
    if not when_matches(prim, ctx.params, ctx.where):
        return
    layer = prim.get("layer", ctx.layer)
    if not layer:
        raise SpecError(f"{ctx.where}: no layer")
    ctx = _Ctx(ctx.params, ctx.transform, layer, ctx.depth, ctx.where, ctx.stack)
    kind = prim["type"]
    paint = prim.get("paint", "stroke")
    if kind == "line":
        _add(out, g.Poly(((prim["x1"], prim["y1"]), (prim["x2"], prim["y2"])), False, layer), ctx)
    elif kind in {"polyline", "polygon"}:
        pts = tuple((p[0], p[1]) for p in prim["points"])
        _add(out, g.Poly(pts, kind == "polygon", layer, paint), ctx)
    elif kind == "rect":
        x, y, w, h = prim["x"], prim["y"], prim["width"], prim["height"]
        _add(out, g.Poly(((x, y), (x + w, y), (x + w, y + h), (x, y + h)), True, layer, paint), ctx)
    elif kind == "star":
        n = _count(prim["points"], ctx.params, ctx.where)
        if n < 2:
            raise SpecError(f"{ctx.where}: a star needs at least 2 points")
        pts = g.star_points(
            prim["cx"], prim["cy"], n, prim["outerRadius"], prim["innerRadius"], prim["rotation"]
        )
        _add(out, g.Poly(pts, True, layer, paint), ctx)
    elif kind == "circle":
        _add(out, g.Circle(prim["cx"], prim["cy"], prim["r"], layer, paint), ctx)
    elif kind == "dot":
        _add(out, g.Circle(prim["cx"], prim["cy"], prim.get("r", 1), layer, "fill", dot=True), ctx)
    elif kind == "arc":
        if not prim["start"] < prim["end"] <= prim["start"] + 360:
            raise SpecError(f"{ctx.where}: arc needs start < end <= start + 360")
        _add(out, g.Arc(prim["cx"], prim["cy"], prim["r"], prim["start"], prim["end"], layer), ctx)
    elif kind == "ellipse":
        _add(out, g.Ellipse(prim["cx"], prim["cy"], prim["rx"], prim["ry"], 0.0, layer, paint), ctx)
    elif kind == "path":
        _add(out, g.Path(g.parse_path(prim["d"]), layer, paint), ctx)
    elif kind == "radial":
        n = _count(prim["count"], ctx.params, ctx.where)
        sweep = prim["sweep"]
        step = (sweep / n if sweep >= 360 else sweep / (n - 1)) if n > 1 else 0.0
        center = (prim["center"][0], prim["center"][1])
        for i in range(n):
            t = g.rotate(prim["start"] + i * step, center).then(ctx.transform)
            _expand(prim["element"], _child(ctx, t, "element"), registry, out)
    elif kind == "repeat":
        n = _count(prim["count"], ctx.params, ctx.where)
        if "step" in prim:
            dx, dy = prim["step"]
        else:
            sx, sy = prim["spread"]
            dx, dy = (sx / (n - 1), sy / (n - 1)) if n > 1 else (0.0, 0.0)
        c = (n - 1) / 2 if prim.get("align", "center") == "center" else 0.0
        for i in range(n):
            t = g.translate((i - c) * dx, (i - c) * dy).then(ctx.transform)
            _expand(prim["element"], _child(ctx, t, "element"), registry, out)
    elif kind == "concentric":
        n = _count(prim["count"], ctx.params, ctx.where)
        center = (prim["center"][0], prim["center"][1])
        for i in range(n):
            s = 1 - i * prim["scaleStep"]
            if s <= 0:
                raise SpecError(f"{ctx.where}: copy {i} would have scale {s:.3f}")
            t = g.scale(s, center).then(ctx.transform)
            _expand(prim["element"], _child(ctx, t, "element"), registry, out)
    elif kind == "use":
        _expand_use(prim, ctx, registry, out)
    else:  # pragma: no cover - the schema rejects other types
        raise SpecError(f"{ctx.where}: unknown primitive type {kind!r}")


def _child(ctx: _Ctx, t: g.Transform, name: str) -> _Ctx:
    return _Ctx(ctx.params, t, ctx.layer, ctx.depth + 1, f"{ctx.where}.{name}", ctx.stack)


def use_transform(prim: Json) -> g.Transform:
    tr = prim.get("transform", {})
    origin = tuple(tr.get("origin", [12, 12]))
    o = (float(origin[0]), float(origin[1]))
    dx, dy = tr.get("translate", [0, 0])
    t = g.scale(tr.get("scale", 1), o)
    if tr.get("rotate", 0):
        t = t.then(g.rotate(tr["rotate"], o))
    return t.then(g.translate(dx, dy))


def _expand_use(prim: Json, ctx: _Ctx, registry: Registry, out: list[g.Flat]) -> None:
    target_id = prim["shape"]
    if target_id in ctx.stack:
        raise SpecError(f"{ctx.where}: reference cycle {' -> '.join((*ctx.stack, target_id))}")
    target = registry.get(target_id)
    params = resolve_params(target, prim.get("params"))
    t = use_transform(prim).then(ctx.transform)
    for i, sub in enumerate(target["primitives"]):
        sub_ctx = _Ctx(
            params,
            t,
            ctx.layer,
            ctx.depth + 1,
            f"{ctx.where}->{target_id}[{i}]",
            (*ctx.stack, target_id),
        )
        before = len(out)
        _expand(sub, sub_ctx, registry, out)
        # Every part of a referenced shape lands in the layer of the `use`.
        for k in range(before, len(out)):
            out[k] = _relayer(out[k], ctx.layer)


def _relayer(item: g.Flat, layer: str) -> g.Flat:
    return replace(item, layer=layer)


def round3(x: float) -> float | int:
    """Round to the grid's 3 decimals; whole numbers become ints."""
    r = round(x, 3) + 0.0
    if math.isclose(r, round(r), abs_tol=1e-9):
        return round(r)
    return r
