"""Inventory source images: hashes, sizes and duplicate groups (exact and perceptual)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

from deq_assets.images import SOURCE_SUFFIXES, ImageInfo, hamming, info, load

#: Maximum dHash distance at which two images count as visually identical.
NEAR_DUPLICATE_DISTANCE = 4


@dataclass(frozen=True, slots=True)
class Entry:
    """One source image and its facts."""

    path: Path
    info: ImageInfo


def scan(root: Path) -> list[Entry]:
    """Return every source image directly inside ``root`` (sorted, symlinks skipped)."""
    entries = []
    for path in sorted(root.iterdir()):
        if path.is_symlink() or not path.is_file():
            continue
        if path.suffix.lower() in SOURCE_SUFFIXES:
            entries.append(Entry(path, info(path)))
    return entries


def duplicate_groups(entries: list[Entry]) -> list[list[Entry]]:
    """Group byte-identical or visually identical images; only groups of 2+ are returned."""
    parent = list(range(len(entries)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, a in enumerate(entries):
        for j in range(i + 1, len(entries)):
            b = entries[j]
            same = a.info.sha256 == b.info.sha256
            if same or hamming(a.info.dhash, b.info.dhash) <= NEAR_DUPLICATE_DISTANCE:
                parent[find(j)] = find(i)
    groups: dict[int, list[Entry]] = {}
    for i, entry in enumerate(entries):
        groups.setdefault(find(i), []).append(entry)
    return [group for group in groups.values() if len(group) > 1]


def contact_sheet(
    paths: list[Path], labels: list[str], out: Path, cell: int = 320, columns: int = 4
) -> None:
    """Write a labelled grid of thumbnails to ``out`` (JPEG)."""
    if len(paths) != len(labels):
        raise ValueError("paths and labels must have the same length")
    rows = max(1, -(-len(paths) // columns))
    label_h = 28
    sheet = Image.new("RGB", (columns * cell, rows * (cell + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    for index, (path, label) in enumerate(zip(paths, labels, strict=True)):
        thumb = load(path).convert("RGB")
        thumb.thumbnail((cell - 8, cell - 8))
        x = (index % columns) * cell
        y = (index // columns) * (cell + label_h)
        sheet.paste(thumb, (x + (cell - thumb.width) // 2, y + (cell - thumb.height) // 2))
        draw.text((x + 6, y + cell + 4), label, fill="black", font_size=18)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, "JPEG", quality=85)
