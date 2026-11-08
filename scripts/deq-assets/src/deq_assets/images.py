"""Image primitives: hashing, perceptual hashing, metadata-free re-encoding and resizing."""

from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps

#: Formats accepted as source images.
SOURCE_SUFFIXES = frozenset({".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"})
#: Longest edge of a committed master image, in pixels.
MASTER_MAX_EDGE = 2400
#: WebP quality for masters (visually lossless for photographs).
MASTER_QUALITY = 90
#: Responsive widths generated for the site; never upscaled.
VARIANT_WIDTHS = (480, 960, 1600, 2400)
#: Output formats for responsive variants.
VARIANT_FORMATS = ("avif", "webp", "jpeg")
#: Width of the blur placeholder.
PLACEHOLDER_WIDTH = 16


@dataclass(frozen=True, slots=True)
class ImageInfo:
    """Facts about one image file."""

    sha256: str
    format: str
    width: int
    height: int
    dhash: str


def sha256_file(path: Path) -> str:
    """Return the hex SHA-256 of a file, read in chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dhash(image: Image.Image, size: int = 8) -> str:
    """Return a 64-bit difference hash as 16 hex digits (perceptual, for near-duplicates)."""
    gray = image.convert("L").resize((size + 1, size), Image.Resampling.LANCZOS)
    pixels = gray.tobytes()
    bits = 0
    for row in range(size):
        for col in range(size):
            left = pixels[row * (size + 1) + col]
            right = pixels[row * (size + 1) + col + 1]
            bits = (bits << 1) | int(left > right)
    return f"{bits:0{size * size // 4}x}"


def hamming(a: str, b: str) -> int:
    """Return the number of differing bits between two hex hashes of equal length."""
    if len(a) != len(b):
        raise ValueError("hashes must have the same length")
    return (int(a, 16) ^ int(b, 16)).bit_count()


def load(path: Path) -> Image.Image:
    """Open an image, apply its EXIF orientation and convert it to RGB or RGBA."""
    with Image.open(path) as raw:
        raw.seek(0)
        image = ImageOps.exif_transpose(raw)
        mode = (
            "RGBA" if image.mode in {"RGBA", "LA", "PA"} or "transparency" in image.info else "RGB"
        )
        return image.convert(mode)


def info(path: Path) -> ImageInfo:
    """Return hash, format, size and perceptual hash of an image file."""
    with Image.open(path) as raw:
        fmt = (raw.format or path.suffix.lstrip(".")).lower()
    image = load(path)
    return ImageInfo(sha256_file(path), fmt, image.width, image.height, dhash(image))


def fit(image: Image.Image, max_edge: int) -> Image.Image:
    """Downscale so the longest edge is at most ``max_edge``; never upscale."""
    if max(image.size) <= max_edge:
        return image.copy()
    scaled = image.copy()
    scaled.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
    return scaled


def resize_width(image: Image.Image, width: int) -> Image.Image:
    """Resize to ``width`` keeping the aspect ratio; never upscale."""
    if image.width <= width:
        return image.copy()
    height = max(1, round(image.height * width / image.width))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def encode(image: Image.Image, fmt: str, quality: int) -> bytes:
    """Encode without any metadata (no EXIF, XMP, GPS or ICC profile)."""
    buffer = io.BytesIO()
    if fmt == "jpeg":
        flat = image
        if image.mode == "RGBA":
            flat = Image.new("RGB", image.size, (255, 255, 255))
            flat.paste(image, mask=image.getchannel("A"))
        flat.save(buffer, "JPEG", quality=quality, optimize=True, progressive=True)
    elif fmt == "webp":
        image.save(buffer, "WEBP", quality=quality, method=6)
    elif fmt == "avif":
        image.save(buffer, "AVIF", quality=quality)
    else:
        raise ValueError(f"unsupported output format: {fmt}")
    return buffer.getvalue()


def has_metadata(path: Path) -> bool:
    """Return True if the file carries EXIF, XMP or GPS metadata."""
    with Image.open(path) as image:
        if image.getexif():
            return True
        return any(key in image.info for key in ("exif", "xmp", "XML:com.adobe.xmp"))
