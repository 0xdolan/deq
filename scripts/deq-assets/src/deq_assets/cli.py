"""Command line: ``deq-assets {inventory,process,verify,variants,contact-sheet}``.

- ``inventory``: hashes, sizes and duplicate groups of a source folder (JSON on stdout).
- ``process``: build metadata-free WebP masters from ``temp/`` and fill computed fields.
- ``verify``: check committed masters against the manifest and ``content/sources.json`` (CI).
- ``variants``: generate responsive AVIF/WebP/JPEG variants and blur placeholders (site build).
- ``contact-sheet``: a labelled grid of masters for review.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from PIL import Image

from deq_assets import images, inventory
from deq_assets.manifest import Asset, Manifest, ManifestError, Master, load, safe_path, save

#: Frame duration for rebuilt animations (the GIF frame folders carry no timing).
FRAME_MS = 100
#: WebP quality for animation frames.
ANIMATION_QUALITY = 80
#: Folders under the asset root that hold committed masters.
MASTER_DIRS = ("images", "video")


def _write(path: Path, data: bytes, *, force: bool) -> bool:
    """Write ``data``; identical content is a no-op, different content needs ``force``.

    Returns True if the file was written.
    """
    if path.exists():
        if path.read_bytes() == data:
            return False
        if not force:
            raise ManifestError(f"{path} exists with different content (use --force)")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb" if force else "xb") as handle:
        handle.write(data)
    return True


def _source(src: Path, filename: str) -> Path:
    if "/" in filename or "\\" in filename or filename in {"", ".", ".."}:
        raise ManifestError(f"source filename must be a plain name: {filename!r}")
    path = src / filename
    if path.is_symlink():
        raise ManifestError(f"refusing symlink: {path}")
    if not path.exists():
        raise ManifestError(f"missing source: {path}")
    return path


def frames_digest(folder: Path) -> tuple[list[Path], str]:
    """Return the sorted frame files of a folder and one SHA-256 over their hashes."""
    frames = sorted(
        p
        for p in folder.iterdir()
        if p.is_file() and not p.is_symlink() and p.suffix.lower() in images.SOURCE_SUFFIXES
    )
    if not frames:
        raise ManifestError(f"no frames in {folder}")
    digest = hashlib.sha256()
    for frame in frames:
        digest.update(f"{frame.name}:{images.sha256_file(frame)}\n".encode())
    return frames, digest.hexdigest()


def encode_animation(frames: list[Path], frame_ms: int) -> bytes:
    """Encode frames as a looping, metadata-free animated WebP."""
    loaded = [images.load(f).convert("RGB") for f in frames]
    buffer = io.BytesIO()
    loaded[0].save(
        buffer,
        "WEBP",
        save_all=True,
        append_images=loaded[1:],
        duration=frame_ms,
        loop=0,
        quality=ANIMATION_QUALITY,
        method=4,
    )
    return buffer.getvalue()


def _process_image(asset: Asset, src: Path, root: Path, *, force: bool) -> int:
    path = _source(src, asset.original.filename)
    if images.sha256_file(path) != asset.original.sha256:
        raise ManifestError(f"{asset.id}: source hash differs from manifest")
    master = images.fit(images.load(path), images.MASTER_MAX_EDGE)
    data = images.encode(master, "webp", images.MASTER_QUALITY)
    written = int(_write(safe_path(root, asset.file), data, force=force))
    asset.master = Master(hashlib.sha256(data).hexdigest(), master.width, master.height, len(data))
    return written


def _process_animation(asset: Asset, src: Path, root: Path, *, force: bool) -> int:
    folder = _source(src, asset.original.filename)
    frames, digest = frames_digest(folder)
    if digest != asset.original.sha256 or len(frames) != asset.original.frames:
        raise ManifestError(f"{asset.id}: frame folder differs from manifest")
    data = encode_animation(frames, FRAME_MS)
    first = images.load(frames[0]).convert("RGB")
    poster = images.encode(first, "webp", images.MASTER_QUALITY)
    poster_path = asset.poster
    assert poster_path is not None  # noqa: S101 - animations always have a poster
    written = int(_write(safe_path(root, asset.file), data, force=force))
    written += int(_write(safe_path(root, poster_path), poster, force=force))
    asset.master = Master(
        hashlib.sha256(data).hexdigest(),
        first.width,
        first.height,
        len(data),
        frames=len(frames),
        frame_ms=FRAME_MS,
    )
    asset.poster_sha256 = hashlib.sha256(poster).hexdigest()
    return written


def process(manifest: Manifest, src: Path, root: Path, *, force: bool = False) -> int:
    """Build every master and check excluded files; return the number of files written."""
    written = 0
    for asset in manifest.assets:
        handler = _process_animation if asset.kind == "animation" else _process_image
        written += handler(asset, src, root, force=force)
    for item in manifest.excluded:
        path = _source(src, item.filename)
        if path.is_file() and images.sha256_file(path) != item.sha256:
            raise ManifestError(f"excluded {item.filename}: hash differs from manifest")
    return written


def source_ids(path: Path) -> set[str]:
    """Return the ids in a CSL-JSON file."""
    if path.is_symlink():
        raise ManifestError(f"refusing symlink: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ManifestError(f"{path}: CSL-JSON must be a list")
    ids = [item.get("id") for item in data if isinstance(item, dict)]
    if len(ids) != len(data) or not all(isinstance(i, str) for i in ids):
        raise ManifestError(f"{path}: every item needs a string id")
    if len(set(ids)) != len(ids):
        raise ManifestError(f"{path}: duplicate ids")
    return {str(i) for i in ids}


def _check_file(path: Path, sha: str, label: str) -> list[str]:
    if path.is_symlink() or not path.is_file():
        return [f"{label}: missing {path}"]
    errors = []
    if images.sha256_file(path) != sha:
        errors.append(f"{label}: hash mismatch for {path}")
    if images.has_metadata(path):
        errors.append(f"{label}: metadata present in {path}")
    return errors


def verify(manifest: Manifest, root: Path, sources: Path) -> list[str]:
    """Return every problem found (empty means the manifest and files agree)."""
    errors: list[str] = []
    ids = source_ids(sources)
    expected: set[Path] = set()
    for asset in manifest.assets:
        if asset.source_id is not None and asset.source_id not in ids:
            errors.append(f"{asset.id}: sourceId '{asset.source_id}' not in {sources.name}")
        if asset.master is None:
            errors.append(f"{asset.id}: not processed")
            continue
        path = safe_path(root, asset.file)
        expected.add(path)
        errors += _check_file(path, asset.master.sha256, asset.id)
        if asset.poster is not None:
            poster = safe_path(root, asset.poster)
            expected.add(poster)
            errors += _check_file(poster, asset.poster_sha256 or "", asset.id)
        elif path.is_file():
            with Image.open(path) as image:
                if image.size != (asset.master.width, asset.master.height):
                    errors.append(f"{asset.id}: size differs from manifest")
    for folder in MASTER_DIRS:
        base = root / folder
        if base.is_dir():
            for path in sorted(base.rglob("*")):
                if path.is_file() and path not in expected:
                    errors.append(f"unlisted file: {path.relative_to(root)}")
    return errors


def variants(manifest: Manifest, root: Path, out: Path, *, force: bool = False) -> int:
    """Write responsive variants and ``placeholders.json``; return files written."""
    written = 0
    placeholders: dict[str, str] = {}
    for asset in manifest.assets:
        rel = asset.poster or asset.file
        image = images.load(safe_path(root, rel))
        stem = rel.removesuffix(".webp")
        widths = [w for w in images.VARIANT_WIDTHS if w < image.width] + [
            min(image.width, images.VARIANT_WIDTHS[-1])
        ]
        for width in sorted(set(widths)):
            resized = images.resize_width(image, width)
            for fmt in images.VARIANT_FORMATS:
                ext = "jpg" if fmt == "jpeg" else fmt
                data = images.encode(resized, fmt, 70 if fmt == "avif" else 80)
                written += int(_write(safe_path(out, f"{stem}-{width}.{ext}"), data, force=force))
        tiny = images.encode(images.resize_width(image, images.PLACEHOLDER_WIDTH), "webp", 50)
        placeholders[asset.id] = "data:image/webp;base64," + base64.b64encode(tiny).decode()
    index = json.dumps(placeholders, indent=2, sort_keys=True) + "\n"
    written += int(_write(safe_path(out, "placeholders.json"), index.encode(), force=force))
    return written


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="deq-assets", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    inv = sub.add_parser("inventory", help="hash and group a source folder")
    inv.add_argument("src", type=Path)

    for name in ("process", "verify", "variants", "contact-sheet"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--manifest", type=Path, default=Path("assets/source-manifest.json"))
        if name == "process":
            cmd.add_argument("--src", type=Path, default=Path("temp/images"))
        if name == "verify":
            cmd.add_argument("--sources", type=Path, default=Path("content/sources.json"))
        if name == "variants":
            cmd.add_argument("--out", type=Path, default=Path("assets/.generated"))
        if name == "contact-sheet":
            cmd.add_argument("--out", type=Path, required=True)
            cmd.add_argument("--category", default=None)
        if name in {"process", "variants", "contact-sheet"}:
            cmd.add_argument("--force", action="store_true", help="overwrite changed files")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point; returns the process exit code."""
    args = _parser().parse_args(argv)
    try:
        if args.command == "inventory":
            entries = inventory.scan(args.src)
            report = {
                "images": [{"file": e.path.name, **asdict(e.info)} for e in entries],
                "duplicates": [
                    [e.path.name for e in group] for group in inventory.duplicate_groups(entries)
                ],
            }
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0
        manifest_path: Path = args.manifest
        manifest = load(manifest_path)
        root = manifest_path.parent
        if args.command == "process":
            count = process(manifest, args.src, root, force=args.force)
            save(manifest, manifest_path)
            print(f"processed {len(manifest.assets)} assets, wrote {count} files")
        elif args.command == "verify":
            errors = verify(manifest, root, args.sources)
            for error in errors:
                print(error, file=sys.stderr)
            if errors:
                return 1
            print(f"ok: {len(manifest.assets)} assets verified")
        elif args.command == "variants":
            count = variants(manifest, root, args.out, force=args.force)
            print(f"wrote {count} variant files to {args.out}")
        else:
            chosen = [a for a in manifest.assets if args.category in {None, a.category}]
            if args.out.exists() and not args.force:
                raise ManifestError(f"{args.out} exists (use --force)")
            paths = [safe_path(root, a.poster or a.file) for a in chosen]
            inventory.contact_sheet(paths, [a.id for a in chosen], args.out)
            print(f"wrote {args.out}")
    except (ManifestError, OSError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
