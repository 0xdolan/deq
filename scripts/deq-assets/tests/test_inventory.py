"""Tests for scanning, duplicate grouping and contact sheets."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from conftest import make_image
from deq_assets import inventory


def test_scan_and_duplicates(tmp_path: Path) -> None:
    a = make_image(tmp_path / "a.png", (64, 48), "red")
    (tmp_path / "b.png").write_bytes(a.read_bytes())
    Image.open(a).save(tmp_path / "c.jpg", quality=95)
    Image.linear_gradient("L").save(tmp_path / "d.png")
    (tmp_path / "notes.txt").write_text("x")
    (tmp_path / "sub").mkdir()
    (tmp_path / "link.png").symlink_to(a)
    entries = inventory.scan(tmp_path)
    assert [e.path.name for e in entries] == ["a.png", "b.png", "c.jpg", "d.png"]
    groups = inventory.duplicate_groups(entries)
    assert [[e.path.name for e in g] for g in groups] == [["a.png", "b.png", "c.jpg"]]


def test_contact_sheet(tmp_path: Path) -> None:
    paths = [make_image(tmp_path / f"{i}.png") for i in range(5)]
    out = tmp_path / "sheets" / "s.jpg"
    inventory.contact_sheet(paths, [str(i) for i in range(5)], out, cell=100, columns=2)
    with Image.open(out) as sheet:
        assert sheet.size == (200, 3 * 128)


def test_contact_sheet_length_mismatch(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="same length"):
        inventory.contact_sheet([tmp_path / "a.png"], [], tmp_path / "s.jpg")
