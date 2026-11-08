"""Tests for image primitives."""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from PIL import Image

from conftest import make_image
from deq_assets import images


def test_sha256_and_info(tmp_path: Path) -> None:
    path = make_image(tmp_path / "a.png")
    info = images.info(path)
    assert info.format == "png"
    assert (info.width, info.height) == (64, 48)
    assert len(info.sha256) == 64
    assert len(info.dhash) == 16


def test_dhash_similar_and_different(tmp_path: Path) -> None:
    a = images.load(make_image(tmp_path / "a.png", color="red"))
    b = images.load(make_image(tmp_path / "b.jpg", color="red"))
    gradient = Image.linear_gradient("L").convert("RGB")
    assert images.hamming(images.dhash(a), images.dhash(b)) <= 4
    assert images.hamming(images.dhash(a), images.dhash(gradient)) > 4


def test_hamming_length_mismatch() -> None:
    with pytest.raises(ValueError, match="same length"):
        images.hamming("ab", "abc")


def test_load_modes(tmp_path: Path) -> None:
    rgba = tmp_path / "rgba.png"
    Image.new("RGBA", (4, 4), (1, 2, 3, 0)).save(rgba)
    assert images.load(rgba).mode == "RGBA"
    palette = tmp_path / "p.gif"
    image = Image.new("P", (4, 4), 0)
    image.save(palette, transparency=0)
    assert images.load(palette).mode == "RGBA"
    gray = tmp_path / "l.png"
    Image.new("L", (4, 4), 9).save(gray)
    assert images.load(gray).mode == "RGB"


def test_load_applies_exif_orientation(tmp_path: Path) -> None:
    path = tmp_path / "rot.jpg"
    exif = Image.Exif()
    exif[0x0112] = 6  # rotate 90 degrees
    Image.new("RGB", (40, 20), "white").save(path, exif=exif)
    assert images.load(path).size == (20, 40)
    assert images.has_metadata(path)


def test_fit_and_resize() -> None:
    image = Image.new("RGB", (400, 200))
    assert images.fit(image, 1000).size == (400, 200)
    assert images.fit(image, 100).size == (100, 50)
    assert images.resize_width(image, 800).size == (400, 200)
    assert images.resize_width(image, 100).size == (100, 50)


@pytest.mark.parametrize("fmt", ["jpeg", "webp", "avif"])
def test_encode_has_no_metadata(tmp_path: Path, fmt: str) -> None:
    image = Image.new("RGBA", (8, 8), (10, 20, 30, 128))
    path = tmp_path / f"out.{fmt}"
    path.write_bytes(images.encode(image, fmt, 80))
    assert not images.has_metadata(path)
    with Image.open(io.BytesIO(path.read_bytes())) as decoded:
        assert decoded.size == (8, 8)


def test_encode_rejects_unknown_format() -> None:
    with pytest.raises(ValueError, match="unsupported"):
        images.encode(Image.new("RGB", (2, 2)), "bmp", 80)


def test_has_metadata_xmp(tmp_path: Path) -> None:
    path = tmp_path / "x.webp"
    Image.new("RGB", (4, 4)).save(path, xmp=b"<x:xmpmeta/>")
    assert images.has_metadata(path)
