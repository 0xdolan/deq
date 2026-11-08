"""End-to-end tests of the command line."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

from conftest import make_image
from deq_assets import cli
from deq_assets.manifest import ManifestError, load


def run(*args: str | Path) -> int:
    return cli.main([str(a) for a in args])


def process(p: dict[str, Path], *extra: str) -> int:
    return run("process", "--manifest", p["manifest"], "--src", p["src"], *extra)


def verify(p: dict[str, Path]) -> int:
    return run("verify", "--manifest", p["manifest"], "--sources", p["sources"])


def test_process_verify_variants_sheet(
    project: dict[str, Path], capsys: pytest.CaptureFixture[str]
) -> None:
    assert verify(project) == 1  # not processed yet
    assert process(project) == 0
    manifest = load(project["manifest"])
    image, anim = manifest.assets
    assert image.master is not None
    assert (image.master.width, image.master.height) == (2400, 1200)
    assert anim.master is not None
    assert (anim.master.frames, anim.master.frame_ms) == (3, cli.FRAME_MS)
    with Image.open(project["root"] / anim.file) as webp:
        assert getattr(webp, "n_frames", 1) == 3
    assert process(project) == 0  # idempotent
    assert "wrote 0 files" in capsys.readouterr().out
    assert verify(project) == 0

    out = project["tmp"] / "generated"
    assert run("variants", "--manifest", project["manifest"], "--out", out) == 0
    assert (out / "images/story/historical/test-image-01-2400.avif").is_file()
    assert (out / "images/story/historical/test-image-01-480.jpg").is_file()
    assert (out / "video/test-anim-poster-40.webp").is_file()
    placeholders = json.loads((out / "placeholders.json").read_text())
    assert placeholders["test-anim"].startswith("data:image/webp;base64,")

    sheet = project["tmp"] / "sheet.jpg"
    args = ("contact-sheet", "--manifest", project["manifest"], "--out", sheet)
    assert run(*args) == 0
    assert run(*args) == 2  # exists
    assert run(*args, "--force", "--category", "story/contemporary") == 0


def test_verify_reports_problems(project: dict[str, Path]) -> None:
    assert process(project) == 0
    root = project["root"]
    manifest = load(project["manifest"])
    image, anim = manifest.assets
    (root / "images" / "extra.webp").write_bytes(b"x")
    (root / anim.file).write_bytes((root / image.file).read_bytes())
    (root / "video" / "test-anim-poster.webp").unlink()
    project["sources"].write_text("[]")
    errors = cli.verify(manifest, root, project["sources"])
    joined = "\n".join(errors)
    assert "not in sources.json" in joined
    assert "hash mismatch" in joined
    assert "missing" in joined
    assert "unlisted file: images/extra.webp" in joined


def test_verify_metadata_and_size(project: dict[str, Path]) -> None:
    assert process(project) == 0
    manifest = load(project["manifest"])
    image = manifest.assets[0]
    path = project["root"] / image.file
    exif = Image.Exif()
    exif[0x010E] = "caption"
    Image.new("RGB", (10, 10)).save(path, exif=exif)
    errors = cli.verify(manifest, project["root"], project["sources"])
    assert any("metadata present" in e for e in errors)
    assert any("size differs" in e for e in errors)


def test_process_refuses_changed_files(project: dict[str, Path]) -> None:
    assert process(project) == 0
    target = project["root"] / "images/story/historical/test-image-01.webp"
    target.write_bytes(b"changed")
    assert process(project) == 2
    assert process(project, "--force") == 0
    assert target.read_bytes() != b"changed"


def test_process_detects_source_changes(project: dict[str, Path]) -> None:
    make_image(project["src"] / "a.png", (10, 10), "blue")
    assert process(project) == 2


def test_process_detects_frame_changes(project: dict[str, Path]) -> None:
    make_image(project["src"] / "frames" / "f009.jpg")
    assert process(project) == 2


def test_process_detects_excluded_changes(project: dict[str, Path]) -> None:
    (project["src"] / "a-copy.png").write_bytes(b"other")
    assert process(project) == 2


def test_source_errors(project: dict[str, Path]) -> None:
    with pytest.raises(ManifestError, match="plain name"):
        cli._source(project["src"], "../a.png")
    with pytest.raises(ManifestError, match="missing source"):
        cli._source(project["src"], "nope.png")
    (project["src"] / "link.png").symlink_to(project["src"] / "a.png")
    with pytest.raises(ManifestError, match="symlink"):
        cli._source(project["src"], "link.png")
    (project["tmp"] / "empty").mkdir()
    with pytest.raises(ManifestError, match="no frames"):
        cli.frames_digest(project["tmp"] / "empty")


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("{}", "must be a list"),
        ('[{"id": 1}]', "string id"),
        ('[{"id": "a"}, {"id": "a"}]', "duplicate ids"),
    ],
)
def test_source_ids_errors(tmp_path: Path, content: str, message: str) -> None:
    path = tmp_path / "s.json"
    path.write_text(content)
    with pytest.raises(ManifestError, match=message):
        cli.source_ids(path)


def test_source_ids_symlink(tmp_path: Path) -> None:
    real = tmp_path / "s.json"
    real.write_text("[]")
    (tmp_path / "l.json").symlink_to(real)
    with pytest.raises(ManifestError, match="symlink"):
        cli.source_ids(tmp_path / "l.json")


def test_inventory_command(project: dict[str, Path], capsys: pytest.CaptureFixture[str]) -> None:
    assert run("inventory", project["src"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert [i["file"] for i in report["images"]] == ["a-copy.png", "a.png"]
    assert report["duplicates"] == [["a-copy.png", "a.png"]]


def test_bad_manifest_returns_2(tmp_path: Path) -> None:
    path = tmp_path / "m.json"
    path.write_text("{not json")
    assert run("verify", "--manifest", path) == 2
