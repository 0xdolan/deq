"""Tests for manifest parsing, validation and serialisation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from conftest import asset_record
from deq_assets import manifest as m


def doc(*assets: dict[str, Any], excluded: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"version": 1, "assets": list(assets), "excluded": excluded or []}


def test_parse_round_trip(tmp_path: Path) -> None:
    master = {"sha256": "1" * 64, "width": 2, "height": 3, "bytes": 9}
    parsed = m.parse(doc(asset_record(master=master)))
    assert parsed.by_id()["test-image-01"].file == "images/story/historical/test-image-01.webp"
    path = tmp_path / "manifest.json"
    m.save(parsed, path)
    data = json.loads(path.read_text())
    assert data["assets"][0]["file"] == "images/story/historical/test-image-01.webp"
    assert data["assets"][0]["sourceId"] == "src-one"
    assert data["assets"][0]["master"]["frameMs"] == 0
    assert m.load(path).assets[0].master == parsed.assets[0].master


def test_animation_paths() -> None:
    parsed = m.parse(doc(asset_record(kind="animation")))
    asset = parsed.assets[0]
    assert asset.file == "video/test-image-01.webp"
    assert asset.poster == "video/test-image-01-poster.webp"
    assert '"poster"' in m.to_json(parsed)
    assert m.parse(doc(asset_record())).assets[0].poster is None


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ([], "must be an object"),
        ({"version": 2}, "unsupported manifest version"),
        ({"version": 1, "assets": {}}, "must be lists"),
        (doc("x"), r"assets\[0\]: must be an object"),  # type: ignore[arg-type]
        (doc(asset_record(kind="video")), "unknown kind"),
        (doc(asset_record(attribution="maybe")), "unknown attribution"),
        (doc({"kind": "image", "attribution": "unknown"}), "missing 'id'"),
        (doc(asset_record(id=5)), "'id' must be str"),
        (doc(asset_record(sourceId=3)), "'sourceId' must be str or null"),
        (doc(asset_record(motifs=[1])), "list of strings"),
        (doc(asset_record(original="x")), "'original' must be an object"),
        (doc(asset_record(original={"filename": "a"})), "missing 'sha256'"),
        (doc(asset_record(master="x")), "'master' must be an object or null"),
        (doc(asset_record(master={"sha256": "1" * 64, "width": True})), "'width' must be int"),
        (doc(asset_record(id="Bad_Id")), "kebab-case"),
        (doc(asset_record(), asset_record()), "duplicate id"),
        (doc(asset_record(category="story/other")), "unknown category"),
        (doc(asset_record(rights="cc0")), "unknown rights"),
        (doc(asset_record(master={"sha256": "x", "width": 1, "height": 1, "bytes": 1})), "master"),
        (doc(asset_record(sourceUrl="http://x")), "https"),
        (doc(asset_record(subject=" ")), "subject and credit"),
        (doc(asset_record(sourceId=None)), "needs a sourceId"),
        (doc(asset_record(), excluded=["x"]), r"excluded\[0\]: must be an object"),  # type: ignore[list-item]
        (
            doc(
                asset_record(),
                excluded=[{"filename": "f", "sha256": "0" * 64, "reason": "r", "duplicateOf": "z"}],
            ),
            "unknown duplicateOf",
        ),
        (
            doc(
                asset_record(),
                excluded=[
                    {"filename": "f", "sha256": "x", "reason": "r", "duplicateOf": "test-image-01"}
                ],
            ),
            "not a hex digest",
        ),
    ],
)
def test_parse_errors(data: object, message: str) -> None:
    with pytest.raises(m.ManifestError, match=message):
        m.parse(data)


def test_bad_original_sha() -> None:
    record = asset_record()
    record["original"]["sha256"] = "nope"
    with pytest.raises(m.ManifestError, match="original sha256"):
        m.parse(doc(record))


def test_safe_path(tmp_path: Path) -> None:
    assert m.safe_path(tmp_path, "images/a.webp") == tmp_path / "images" / "a.webp"
    for bad in ("/etc/passwd", "../x", "a/../../x", ""):
        with pytest.raises(m.ManifestError, match="unsafe path"):
            m.safe_path(tmp_path, bad)
    (tmp_path / "real").mkdir()
    (tmp_path / "images").symlink_to(tmp_path / "real")
    with pytest.raises(m.ManifestError, match="symlink"):
        m.safe_path(tmp_path, "images/a.webp")


def test_load_and_save_refuse_symlinks(tmp_path: Path) -> None:
    real = tmp_path / "real.json"
    real.write_text(json.dumps(doc(asset_record())))
    link = tmp_path / "link.json"
    link.symlink_to(real)
    with pytest.raises(m.ManifestError, match="symlink"):
        m.load(link)
    with pytest.raises(m.ManifestError, match="symlink"):
        m.save(m.load(real), link)
