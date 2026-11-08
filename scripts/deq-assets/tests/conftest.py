"""Shared fixtures: a tiny source folder, manifest and sources file built in tmp_path."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from PIL import Image

from deq_assets import images
from deq_assets.cli import frames_digest


def make_image(path: Path, size: tuple[int, int] = (64, 48), color: str = "red") -> Path:
    """Write a simple image with a diagonal so dHash is not flat."""
    image = Image.new("RGB", size, color)
    for i in range(min(size)):
        image.putpixel((i, i), (0, 0, 0))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return path


def asset_record(**overrides: Any) -> dict[str, Any]:  # noqa: ANN401
    """Return a valid image asset record."""
    record: dict[str, Any] = {
        "id": "test-image-01",
        "kind": "image",
        "category": "story/historical",
        "subject": "A test image",
        "credit": "Test Author",
        "attribution": "confirmed",
        "attributionNote": "made in a test",
        "sourceId": "src-one",
        "sourceUrl": "https://example.org/a",
        "rights": "owner-permission",
        "motifs": ["sun"],
        "usedIn": [],
        "original": {
            "filename": "a.png",
            "sha256": "0" * 64,
            "format": "png",
            "width": 64,
            "height": 48,
        },
        "master": None,
    }
    record.update(overrides)
    return record


@pytest.fixture
def project(tmp_path: Path) -> dict[str, Path]:
    """Create temp/ sources, an unprocessed manifest and a sources file."""
    src = tmp_path / "temp"
    a = make_image(src / "a.png", (3000, 1500), "red")
    dup = src / "a-copy.png"
    dup.write_bytes(a.read_bytes())
    frames = src / "frames"
    for index, color in enumerate(("red", "green", "blue")):
        make_image(frames / f"f{index:03d}.jpg", (40, 30), color)
    _, digest = frames_digest(frames)
    assets = tmp_path / "assets"
    assets.mkdir()
    manifest = {
        "version": 1,
        "notes": ["test"],
        "assets": [
            asset_record(
                original={
                    "filename": "a.png",
                    "sha256": images.sha256_file(a),
                    "format": "png",
                    "width": 3000,
                    "height": 1500,
                }
            ),
            asset_record(
                id="test-anim",
                kind="animation",
                category="story/contemporary",
                attribution="unknown",
                sourceId=None,
                sourceUrl=None,
                original={
                    "filename": "frames",
                    "sha256": digest,
                    "format": "jpeg",
                    "width": 40,
                    "height": 30,
                    "frames": 3,
                },
            ),
        ],
        "excluded": [
            {
                "filename": "a-copy.png",
                "sha256": images.sha256_file(dup),
                "reason": "byte-identical",
                "duplicateOf": "test-image-01",
            }
        ],
    }
    path = assets / "source-manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    sources = tmp_path / "sources.json"
    sources.write_text(json.dumps([{"id": "src-one", "type": "webpage"}]), encoding="utf-8")
    return {"src": src, "manifest": path, "root": assets, "sources": sources, "tmp": tmp_path}
