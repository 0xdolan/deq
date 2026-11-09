"""Check spec/flag.json against the reference SVG and recompute its derived values."""

from __future__ import annotations

import hashlib
import math
import re
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from deq_spec import colors
from deq_spec import geometry as g

NUMBER = re.compile(r"[MmLlHhVvZz]|-?(?:\d+\.?\d*|\.\d+)")
SVG_NS = "{http://www.w3.org/2000/svg}"
#: Largest reference file accepted (bytes).
MAX_SVG_BYTES = 64 * 1024


def parse_polygon(d: str) -> list[g.Point]:
    """Vertices of a single closed subpath using M, L, H, V (absolute or relative) and Z."""
    tokens = NUMBER.findall(d)
    pts: list[g.Point] = []
    x = y = 0.0
    cmd = ""
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.isalpha():
            cmd = tok
            i += 1
            if cmd in "Zz":
                break
            continue
        if not cmd:
            raise ValueError("path data must start with a command")
        if cmd in "MLml":
            dx, dy = float(tokens[i]), float(tokens[i + 1])
            i += 2
            x, y = (x + dx, y + dy) if cmd.islower() and pts else (dx, dy)
            if cmd == "m":
                cmd = "l"
            elif cmd == "M":
                cmd = "L"
        else:
            v = float(tok)
            i += 1
            if cmd == "h":
                x += v
            elif cmd == "H":
                x = v
            elif cmd == "v":
                y += v
            else:  # "V": the only command left that NUMBER matches
                y = v
        pts.append((x, y))
    return pts


def _close(a: float, b: float, tol: float = 0.0015) -> bool:
    return math.isclose(a, b, abs_tol=tol)


def check(data: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    src = data["source"]
    path = root / src["file"]
    if path.is_symlink() or not path.is_file():
        return [f"reference file {src['file']} is missing or a symlink"]
    raw = path.read_bytes()
    if len(raw) > MAX_SVG_BYTES:
        return [f"reference file {src['file']} is larger than {MAX_SVG_BYTES} bytes"]
    if hashlib.sha256(raw).hexdigest() != src["sha256"]:
        return [f"reference file {src['file']}: sha256 does not match"]
    if hashlib.sha1(raw, usedforsecurity=False).hexdigest() != src["sha1"]:
        errors.append("reference sha1 does not match")

    svg = ET.fromstring(raw)  # noqa: S314 - trusted: hash-pinned file
    width, height = float(svg.get("width", "0")), float(svg.get("height", "0"))
    if [width, height] != data["viewBox"]:
        errors.append(f"viewBox {data['viewBox']} != reference {[width, height]}")
    ar = data["aspectRatio"]
    if not _close(width / height, ar["width"] / ar["height"]):
        errors.append("aspectRatio does not match the reference")

    fills: dict[str, list[g.Point]] = {}
    for el in svg.iter(f"{SVG_NS}path"):
        fills[el.get("fill", "").lower()] = parse_polygon(el.get("d", ""))
    hexes = {c["id"]: c["hex"] for c in data["colors"]}
    aliases = {"#fff": "#ffffff"}
    ref_fills = {aliases.get(k, k): v for k, v in fills.items()}

    for c in data["colors"]:
        if c["hex"].lower() not in ref_fills:
            errors.append(f"color {c['id']} {c['hex']} is not used in the reference")
        rgb = colors.hex_to_rgb(c["hex"])
        expected = {
            "rgb": list(rgb),
            "hsl": colors.rgb_to_hsl(rgb),
            "oklch": colors.rgb_to_oklch(rgb),
            "cmyk": colors.rgb_to_cmyk(rgb),
        }
        for key, value in expected.items():
            if c[key] != value:
                errors.append(f"color {c['id']}: {key} {c[key]} != computed {value}")

    for band in data["bands"]:
        pts = ref_fills.get(hexes[band["color"]].lower())
        if band["color"] == "white":
            ok = band["y"] >= 0 and band["y"] + band["height"] <= height
        elif pts is None:
            ok = False
        else:
            ys = [p[1] for p in pts]
            xs = [p[0] for p in pts]
            ok = (
                _close(min(ys), band["y"])
                and _close(max(ys) - min(ys), band["height"])
                and _close(min(xs), 0)
                and _close(max(xs), width)
            )
        if not ok:
            errors.append(
                f"band {band['color']} y={band['y']} h={band['height']} "
                "does not match the reference"
            )
    if sum(b["height"] for b in data["bands"]) != height:
        errors.append("bands do not cover the flag height")

    sun = data["sun"]
    r_out, r_in = sun["outerRadius"], sun["innerRadius"]
    cx, cy = sun["center"]
    if not _close(r_in / r_out, sun["innerToOuter"], 1e-4):
        errors.append("sun innerRadius / outerRadius != innerToOuter")
    bbh = r_out * (1 + math.cos(math.pi / sun["rays"]))
    derived = {
        "boundingBoxHeight": bbh,
        "heightToFlagHeight": bbh / height,
        "outerDiameterToFlagHeight": 2 * r_out / height,
    }
    for key, value in derived.items():
        if not _close(sun[key], value):
            errors.append(f"sun {key} {sun[key]} != computed {value:.5f}")
    sun_pts = ref_fills.get(hexes["yellow"].lower(), [])
    model = g.star_points(cx, cy, sun["rays"], r_out, r_in, sun["rotation"])
    if len(sun_pts) != len(model):
        errors.append(
            f"sun has {len(sun_pts)} vertices in the reference, the spec gives {len(model)}"
        )
    else:
        worst = max(min(math.dist(p, q) for q in model) for p in sun_pts)
        if worst > 0.01:
            errors.append(f"sun vertices differ from the reference by up to {worst:.4f}")

    for item in data["contrast"]:
        a, b = (colors.hex_to_rgb(hexes[k]) for k in item["pair"])
        if item["ratio"] != colors.contrast(a, b):
            errors.append(f"contrast {item['pair']}: {item['ratio']} != {colors.contrast(a, b)}")

    variant_ids = [v["id"] for v in data["variants"]]
    if len(set(variant_ids)) != len(variant_ids):
        errors.append("variant ids must be unique")
    for s in data["sizes"]:
        if s["variant"] not in variant_ids:
            errors.append(f"size {s['use']!r} uses unknown variant {s['variant']!r}")
        if s["unit"] != "px" and "dpi" in s:
            px = [
                round(v / (25.4 if s["unit"] == "mm" else 2.54) * s["dpi"])
                for v in (s["width"], s["height"])
            ]
            if s.get("pixels") != px:
                errors.append(f"size {s['use']!r}: pixels should be {px}")
    return errors
