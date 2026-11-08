"""Typed schema, loading and validation for ``assets/source-manifest.json``.

Paths inside the manifest are relative to the manifest's own directory (``assets/``).
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Literal, cast

MANIFEST_VERSION = 1

#: Allowed categories (§5.1 rule 4). Images live in ``images/<category>/``.
CATEGORIES = (
    "story/historical",
    "story/ethnographic",
    "story/contemporary",
    "story/artists",
    "story/patterns",
    "story/documentary",
    "references/shapes",
)
Attribution = Literal["confirmed", "inferred", "unknown"]
ATTRIBUTIONS: tuple[Attribution, ...] = ("confirmed", "inferred", "unknown")
RIGHTS = ("owner-permission", "cc-by-nc-sa-2.0")

_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SHA = re.compile(r"^[0-9a-f]{64}$")


class ManifestError(ValueError):
    """The manifest is malformed or inconsistent."""


@dataclass(slots=True)
class Original:
    """The source file in ``temp/`` the asset was made from."""

    filename: str
    sha256: str
    format: str
    width: int
    height: int
    frames: int = 1


@dataclass(slots=True)
class Master:
    """The committed, metadata-free master file."""

    sha256: str
    width: int
    height: int
    bytes: int
    frames: int = 1
    frame_ms: int = 0


@dataclass(slots=True)
class Asset:
    """One image or animation and its provenance."""

    id: str
    kind: Literal["image", "animation"]
    category: str
    subject: str
    credit: str
    attribution: Attribution
    attribution_note: str
    source_id: str | None
    source_url: str | None
    rights: str
    original: Original
    motifs: list[str] = field(default_factory=list)
    used_in: list[str] = field(default_factory=list)
    master: Master | None = None
    poster_sha256: str | None = None

    @property
    def file(self) -> str:
        """Master path relative to the manifest directory."""
        if self.kind == "animation":
            return f"video/{self.id}.webp"
        return f"images/{self.category}/{self.id}.webp"

    @property
    def poster(self) -> str | None:
        """Poster frame path for animations."""
        return f"video/{self.id}-poster.webp" if self.kind == "animation" else None


@dataclass(slots=True)
class Excluded:
    """A source file that was not kept (duplicate or archive of another file)."""

    filename: str
    sha256: str
    reason: str
    duplicate_of: str


@dataclass(slots=True)
class Manifest:
    """The whole manifest."""

    assets: list[Asset]
    excluded: list[Excluded]
    version: int = MANIFEST_VERSION
    notes: list[str] = field(default_factory=list)

    def by_id(self) -> dict[str, Asset]:
        """Index assets by id."""
        return {asset.id: asset for asset in self.assets}


_CAMEL = {
    "attribution_note": "attributionNote",
    "source_id": "sourceId",
    "source_url": "sourceUrl",
    "used_in": "usedIn",
    "poster_sha256": "posterSha256",
    "frame_ms": "frameMs",
    "duplicate_of": "duplicateOf",
}


def _camel(data: object) -> object:
    if isinstance(data, dict):
        items = cast("dict[str, object]", data).items()
        return {_CAMEL.get(k, k): _camel(v) for k, v in items}
    if isinstance(data, list):
        return [_camel(v) for v in cast("list[object]", data)]
    return data


def _req(data: dict[str, Any], key: str, kind: type, where: str) -> Any:  # noqa: ANN401
    if key not in data:
        raise ManifestError(f"{where}: missing '{key}'")
    value = data[key]
    if kind is int and isinstance(value, bool):
        raise ManifestError(f"{where}: '{key}' must be int")
    if not isinstance(value, kind):
        raise ManifestError(f"{where}: '{key}' must be {kind.__name__}")
    return value


def _opt_str(data: dict[str, Any], key: str, where: str) -> str | None:
    value = data.get(key)
    if value is not None and not isinstance(value, str):
        raise ManifestError(f"{where}: '{key}' must be str or null")
    return value


def _str_list(data: dict[str, Any], key: str, where: str) -> list[str]:
    value = data.get(key, [])
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ManifestError(f"{where}: '{key}' must be a list of strings")
    return cast("list[str]", value)


def _original(data: object, where: str) -> Original:
    if not isinstance(data, dict):
        raise ManifestError(f"{where}: 'original' must be an object")
    raw = cast("dict[str, Any]", data)
    return Original(
        filename=_req(raw, "filename", str, where),
        sha256=_req(raw, "sha256", str, where),
        format=_req(raw, "format", str, where),
        width=_req(raw, "width", int, where),
        height=_req(raw, "height", int, where),
        frames=raw.get("frames", 1),
    )


def _master(data: object, where: str) -> Master | None:
    if data is None:
        return None
    if not isinstance(data, dict):
        raise ManifestError(f"{where}: 'master' must be an object or null")
    raw = cast("dict[str, Any]", data)
    return Master(
        sha256=_req(raw, "sha256", str, where),
        width=_req(raw, "width", int, where),
        height=_req(raw, "height", int, where),
        bytes=_req(raw, "bytes", int, where),
        frames=raw.get("frames", 1),
        frame_ms=raw.get("frameMs", 0),
    )


def _asset(data: object, index: int) -> Asset:
    where = f"assets[{index}]"
    if not isinstance(data, dict):
        raise ManifestError(f"{where}: must be an object")
    raw = cast("dict[str, Any]", data)
    kind = _req(raw, "kind", str, where)
    if kind not in {"image", "animation"}:
        raise ManifestError(f"{where}: unknown kind '{kind}'")
    attribution = _req(raw, "attribution", str, where)
    if attribution not in ATTRIBUTIONS:
        raise ManifestError(f"{where}: unknown attribution '{attribution}'")
    return Asset(
        id=_req(raw, "id", str, where),
        kind=cast("Literal['image', 'animation']", kind),
        category=_req(raw, "category", str, where),
        subject=_req(raw, "subject", str, where),
        credit=_req(raw, "credit", str, where),
        attribution=cast("Attribution", attribution),
        attribution_note=_req(raw, "attributionNote", str, where),
        source_id=_opt_str(raw, "sourceId", where),
        source_url=_opt_str(raw, "sourceUrl", where),
        rights=_req(raw, "rights", str, where),
        original=_original(raw.get("original"), where),
        motifs=_str_list(raw, "motifs", where),
        used_in=_str_list(raw, "usedIn", where),
        master=_master(raw.get("master"), where),
        poster_sha256=_opt_str(raw, "posterSha256", where),
    )


def _excluded(data: object, index: int) -> Excluded:
    where = f"excluded[{index}]"
    if not isinstance(data, dict):
        raise ManifestError(f"{where}: must be an object")
    raw = cast("dict[str, Any]", data)
    return Excluded(
        filename=_req(raw, "filename", str, where),
        sha256=_req(raw, "sha256", str, where),
        reason=_req(raw, "reason", str, where),
        duplicate_of=_req(raw, "duplicateOf", str, where),
    )


def parse(data: object) -> Manifest:
    """Build a :class:`Manifest` from decoded JSON and validate it."""
    if not isinstance(data, dict):
        raise ManifestError("manifest must be an object")
    raw = cast("dict[str, Any]", data)
    if raw.get("version") != MANIFEST_VERSION:
        raise ManifestError(f"unsupported manifest version: {raw.get('version')!r}")
    assets = raw.get("assets", [])
    excluded = raw.get("excluded", [])
    if not isinstance(assets, list) or not isinstance(excluded, list):
        raise ManifestError("'assets' and 'excluded' must be lists")
    manifest = Manifest(
        assets=[_asset(a, i) for i, a in enumerate(cast("list[object]", assets))],
        excluded=[_excluded(e, i) for i, e in enumerate(cast("list[object]", excluded))],
        notes=_str_list(raw, "notes", "manifest"),
    )
    validate(manifest)
    return manifest


def validate(manifest: Manifest) -> None:
    """Check ids, categories, hashes and cross references; raise on the first problem."""
    seen: set[str] = set()
    for asset in manifest.assets:
        where = f"asset '{asset.id}'"
        if not _ID.match(asset.id):
            raise ManifestError(f"{where}: id must be kebab-case ASCII")
        if asset.id in seen:
            raise ManifestError(f"{where}: duplicate id")
        seen.add(asset.id)
        if asset.category not in CATEGORIES:
            raise ManifestError(f"{where}: unknown category '{asset.category}'")
        if asset.rights not in RIGHTS:
            raise ManifestError(f"{where}: unknown rights '{asset.rights}'")
        if not _SHA.match(asset.original.sha256):
            raise ManifestError(f"{where}: original sha256 is not a hex digest")
        if asset.master is not None and not _SHA.match(asset.master.sha256):
            raise ManifestError(f"{where}: master sha256 is not a hex digest")
        if asset.source_url is not None and not asset.source_url.startswith("https://"):
            raise ManifestError(f"{where}: sourceUrl must be https")
        if not asset.subject.strip() or not asset.credit.strip():
            raise ManifestError(f"{where}: subject and credit are required")
        if asset.attribution == "confirmed" and asset.source_id is None:
            raise ManifestError(f"{where}: confirmed attribution needs a sourceId")
    for item in manifest.excluded:
        if item.duplicate_of not in seen:
            raise ManifestError(f"excluded '{item.filename}': unknown duplicateOf")
        if not _SHA.match(item.sha256):
            raise ManifestError(f"excluded '{item.filename}': sha256 is not a hex digest")


def safe_path(root: Path, relative: str) -> Path:
    """Resolve ``relative`` under ``root``; refuse absolute paths, ``..`` and symlinks."""
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or not pure.parts:
        raise ManifestError(f"unsafe path: {relative}")
    path = root.joinpath(*pure.parts)
    current = root
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            raise ManifestError(f"refusing symlink: {current}")
    return path


def load(path: Path) -> Manifest:
    """Read and validate a manifest file."""
    if path.is_symlink():
        raise ManifestError(f"refusing symlink: {path}")
    with path.open(encoding="utf-8") as handle:
        return parse(json.load(handle))


def to_json(manifest: Manifest) -> str:
    """Serialise with camelCase keys, computed paths and a trailing newline."""
    data: dict[str, Any] = {
        "version": manifest.version,
        "notes": manifest.notes,
        "assets": [],
        "excluded": [_camel(asdict(e)) for e in manifest.excluded],
    }
    for asset in manifest.assets:
        record = cast("dict[str, Any]", _camel(asdict(asset)))
        ordered = {"id": record.pop("id"), "kind": record.pop("kind"), "file": asset.file}
        if asset.poster is not None:
            ordered["poster"] = asset.poster
        ordered.update(record)
        data["assets"].append(ordered)
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def save(manifest: Manifest, path: Path) -> None:
    """Validate and write the manifest."""
    validate(manifest)
    if path.is_symlink():
        raise ManifestError(f"refusing symlink: {path}")
    path.write_text(to_json(manifest), encoding="utf-8")
