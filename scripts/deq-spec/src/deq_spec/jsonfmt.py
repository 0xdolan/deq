"""Canonical JSON layout for spec files: anything that fits in 100 columns stays on one line."""

from __future__ import annotations

import json
import math

WIDTH = 100
INDENT = "  "


def _scalar(value: object) -> str:
    if isinstance(value, float) and math.isfinite(value) and value == int(value):
        return str(int(value))
    return json.dumps(value, ensure_ascii=False)


def _inline(value: object) -> str:
    if isinstance(value, dict):
        if not value:
            return "{}"
        inner = ", ".join(
            f"{json.dumps(k, ensure_ascii=False)}: {_inline(v)}" for k, v in value.items()
        )
        return "{ " + inner + " }"
    if isinstance(value, list):
        return "[" + ", ".join(_inline(v) for v in value) + "]"
    return _scalar(value)


def _dump(value: object, level: int, prefix_len: int) -> str:
    one = _inline(value)
    if len(INDENT) * level + prefix_len + len(one) <= WIDTH or not isinstance(value, dict | list):
        return one
    if not value:
        return one
    pad = INDENT * (level + 1)
    if isinstance(value, dict):
        items = []
        for k, v in value.items():
            key = json.dumps(k, ensure_ascii=False) + ": "
            items.append(pad + key + _dump(v, level + 1, len(key)))
        return "{\n" + ",\n".join(items) + "\n" + INDENT * level + "}"
    items = [pad + _dump(v, level + 1, 0) for v in value]
    return "[\n" + ",\n".join(items) + "\n" + INDENT * level + "]"


def dumps(value: object) -> str:
    """Serialise ``value`` in the canonical layout, with a trailing newline."""
    return _dump(value, 0, 0) + "\n"
