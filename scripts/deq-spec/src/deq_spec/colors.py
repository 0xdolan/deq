"""Color conversions and WCAG contrast for the flag palette."""

from __future__ import annotations

import math


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    h = value.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"expected #RRGGBB, got {value!r}")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb_to_hsl(rgb: tuple[int, int, int]) -> list[float]:
    """``[hue deg, saturation %, lightness %]`` rounded to 1 decimal."""
    r, g, b = (c / 255 for c in rgb)
    hi, lo = max(r, g, b), min(r, g, b)
    light = (hi + lo) / 2
    if hi == lo:
        return [0.0, 0.0, round(light * 100, 1)]
    d = hi - lo
    sat = d / (2 - hi - lo) if light > 0.5 else d / (hi + lo)
    if hi == r:
        hue = ((g - b) / d) % 6
    elif hi == g:
        hue = (b - r) / d + 2
    else:
        hue = (r - g) / d + 4
    return [round(hue * 60, 1), round(sat * 100, 1), round(light * 100, 1)]


def _linear(c: int) -> float:
    v = c / 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def rgb_to_oklch(rgb: tuple[int, int, int]) -> list[float]:
    """``[L, C, hue deg]`` (Ottosson's OKLab), rounded to 3, 3 and 1 decimals."""
    r, g, b = (_linear(c) for c in rgb)
    lc = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    mc = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    sc = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(v) ** (1 / 3), v) for v in (lc, mc, sc))
    lightness = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    bb = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    chroma = math.hypot(a, bb)
    hue = math.degrees(math.atan2(bb, a)) % 360 if chroma > 1e-4 else 0.0
    return [round(lightness, 3), round(chroma, 3) + 0.0, round(hue, 1)]


def rgb_to_cmyk(rgb: tuple[int, int, int]) -> list[int]:
    """Naive (not color-managed) conversion, whole percent."""
    r, g, b = (c / 255 for c in rgb)
    k = 1 - max(r, g, b)
    if k >= 1:
        return [0, 0, 0, 100]
    return [round((1 - v - k) / (1 - k) * 100) for v in (r, g, b)] + [round(k * 100)]


def luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = (_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    """WCAG 2.x contrast ratio, rounded to 2 decimals."""
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return round((la + 0.05) / (lb + 0.05), 2)
