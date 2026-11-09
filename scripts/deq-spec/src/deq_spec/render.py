"""Preview SVG renderer for flat geometry. The reference renderer is @0xdolan/deq-core (Phase 3)."""

from __future__ import annotations

import math
from collections.abc import Mapping
from xml.sax.saxutils import escape, quoteattr

from deq_spec import geometry as g
from deq_spec.spec import round3


def num(x: float) -> str:
    return str(round3(x))


def _pts(points: tuple[g.Point, ...] | list[g.Point]) -> str:
    return " ".join(f"{num(x)},{num(y)}" for x, y in points)


def _paint(item: g.Flat) -> str:
    if item.paint == "fill":
        return ' fill="currentColor" stroke="none"'
    return ""


def element(item: g.Flat) -> str:
    """One SVG element for a flat item (stroke attributes come from the parent group)."""
    if isinstance(item, g.Poly):
        if not item.closed and len(item.points) == 2:
            (x1, y1), (x2, y2) = item.points
            return f'<line x1="{num(x1)}" y1="{num(y1)}" x2="{num(x2)}" y2="{num(y2)}"/>'
        tag = "polygon" if item.closed else "polyline"
        return f'<{tag} points="{_pts(item.points)}"{_paint(item)}/>'
    if isinstance(item, g.Circle):
        fill = ' fill="currentColor" stroke="none"' if item.dot or item.paint == "fill" else ""
        return f'<circle cx="{num(item.cx)}" cy="{num(item.cy)}" r="{num(item.r)}"{fill}/>'
    if isinstance(item, g.Arc):
        sweep = item.end - item.start
        if sweep >= 360:
            return f'<circle cx="{num(item.cx)}" cy="{num(item.cy)}" r="{num(item.r)}"/>'
        a0, a1 = math.radians(item.start), math.radians(item.end)
        x0, y0 = item.cx + item.r * math.cos(a0), item.cy + item.r * math.sin(a0)
        x1, y1 = item.cx + item.r * math.cos(a1), item.cy + item.r * math.sin(a1)
        large = 1 if sweep > 180 else 0
        r = num(item.r)
        return f'<path d="M{num(x0)} {num(y0)}A{r} {r} 0 {large} 1 {num(x1)} {num(y1)}"/>'
    if isinstance(item, g.Ellipse):
        rot = (
            f' transform="rotate({num(item.rotation)} {num(item.cx)} {num(item.cy)})"'
            if item.rotation
            else ""
        )
        return (
            f'<ellipse cx="{num(item.cx)}" cy="{num(item.cy)}" '
            f'rx="{num(item.rx)}" ry="{num(item.ry)}"{rot}{_paint(item)}/>'
        )
    parts: list[str] = []
    for seg in item.segments:
        parts.append(seg[0] + " ".join(f"{num(p[0])} {num(p[1])}" for p in seg[1:]))
    return f'<path d="{"".join(parts)}"{_paint(item)}/>'


def group(
    items: list[g.Flat],
    *,
    stroke_width: float = 2,
    layer_colors: Mapping[str, str] | None = None,
    color: str = "currentColor",
) -> str:
    """The shape's items grouped by layer, in first-use order, inside one styled <g>."""
    layers: dict[str, list[str]] = {}
    for item in items:
        layers.setdefault(item.layer, []).append(element(item))
    body = []
    for layer, elements in layers.items():
        c = (layer_colors or {}).get(layer)
        # Re-declare stroke: SVG 1.1 renderers resolve currentColor where it is declared.
        style = f' color={quoteattr(c)} stroke="currentColor"' if c else ""
        body.append(f"<g data-layer={quoteattr(layer)}{style}>{''.join(elements)}</g>")
    return (
        f'<g fill="none" stroke="currentColor" stroke-width="{num(stroke_width)}" '
        f'stroke-linecap="round" stroke-linejoin="round" color={quoteattr(color)}>'
        f"{''.join(body)}</g>"
    )


def svg(items: list[g.Flat], *, size: int = 24, title: str | None = None, **kwargs: object) -> str:
    """A standalone 24 x 24 SVG document."""
    head = f"<title>{escape(title)}</title>" if title else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        'viewBox="0 0 24 24">'
        f"{head}{group(items, **kwargs)}</svg>\n"  # type: ignore[arg-type]
    )
