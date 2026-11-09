"""Fixtures: a temporary copy of the parts of the repository that deq-spec reads."""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from deq_spec import jsonfmt

ROOT = Path(__file__).resolve().parents[3]
COPY = [
    "spec",
    "assets/source-manifest.json",
    "assets/brand",
    "content/sources.json",
    "docs/design/shapes-contact-sheet.svg",
    "docs/design/logo-concepts.svg",
]


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    for rel in COPY:
        src, dst = ROOT / rel, tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
    return tmp_path


type Editor = Callable[[str, Callable[[Any], Any]], None]


@pytest.fixture
def edit(repo: Path) -> Editor:
    """Load a JSON file under the copy, let ``fn`` mutate it, write it back canonically."""

    def _edit(rel: str, fn: Callable[[Any], Any]) -> None:
        path = repo / rel
        data = json.loads(path.read_text(encoding="utf-8"))
        result = fn(data)
        path.write_text(jsonfmt.dumps(data if result is None else result), encoding="utf-8")

    return _edit
