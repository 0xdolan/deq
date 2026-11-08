"""Semantic lint for spec/: schemas, references, grid bounds, symmetry, metrics, formatting."""

from __future__ import annotations

import math
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from deq_spec import SpecError, flag, jsonfmt, metrics
from deq_spec import geometry as g
from deq_spec.spec import Json, Registry, expand, read_json

EPS = 1e-6


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    checked: int = 0

    def add(self, where: str, message: str) -> None:
        self.errors.append(f"{where}: {message}")


@dataclass
class Repo:
    """Paths of everything the lint reads, relative to the repository root."""

    root: Path

    @property
    def spec(self) -> Path:
        return self.root / "spec"

    @property
    def shapes(self) -> Path:
        return self.spec / "shapes"

    @property
    def concepts(self) -> Path:
        return self.root / "assets" / "brand" / "concepts"

    def schema(self, name: str) -> Draft202012Validator:
        schema = read_json(self.spec / "schema" / f"{name}.schema.json")
        Draft202012Validator.check_schema(schema)
        return Draft202012Validator(schema)

    def source_ids(self) -> set[str]:
        return {s["id"] for s in read_json(self.root / "content" / "sources.json")}

    def asset_ids(self) -> set[str]:
        return {a["id"] for a in read_json(self.root / "assets" / "source-manifest.json")["assets"]}


def shape_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    files = sorted(directory.glob("*.json"))
    for f in files:
        if f.is_symlink():
            raise SpecError(f"{f}: refusing symlink")
    return files


def _rel(path: Path, root: Path) -> str:
    """``path`` relative to ``root`` with forward slashes, so messages match on every OS."""
    return path.relative_to(root).as_posix()


def load_registry(repo: Repo, report: Report | None = None) -> Registry:
    """All shapes (spec/shapes and the brand concepts) keyed by id."""
    reg = Registry()
    for path in [*shape_files(repo.shapes), *shape_files(repo.concepts)]:
        data = read_json(path)
        sid = data.get("id") if isinstance(data, dict) else None
        if not isinstance(sid, str):
            if report is not None:
                report.add(_rel(path, repo.root), "no string `id`")
            continue
        if sid in reg.shapes:
            if report is not None:
                also = _rel(reg.paths[sid], repo.root)
                report.add(_rel(path, repo.root), f"duplicate id {sid!r} (also {also})")
            continue
        reg.shapes[sid] = data
        reg.paths[sid] = path
    return reg


def _schema_errors(validator: Draft202012Validator, data: Json) -> Iterator[str]:
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        loc = "/".join(str(p) for p in err.absolute_path) or "(root)"
        yield f"schema: {loc}: {err.message[:300]}"


def _numbers(value: Json, path: str = "") -> Iterator[tuple[str, float]]:
    if isinstance(value, bool):
        return
    if isinstance(value, int | float):
        yield path, value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from _numbers(v, f"{path}/{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _numbers(v, f"{path}/{i}")


def _walk(prims: list[Json]) -> Iterator[Json]:
    for p in prims:
        yield p
        if "element" in p:
            yield from _walk([p["element"]])


def _cited(value: Json, key: str) -> set[str]:
    """Every id under a ``key`` list anywhere in names/meaning."""
    found: set[str] = set()
    if isinstance(value, dict):
        for k, v in value.items():
            if k == key and isinstance(v, list):
                found |= {x for x in v if isinstance(x, str)}
            else:
                found |= _cited(v, key)
    elif isinstance(value, list):
        for v in value:
            found |= _cited(v, key)
    return found


def _within(box: tuple[float, float, float, float], area: list[float]) -> bool:
    x, y, w, h = box
    ax, ay, aw, ah = area
    return x >= ax - EPS and y >= ay - EPS and x + w <= ax + aw + EPS and y + h <= ay + ah + EPS


def lint_shape(
    path: Path,
    data: Json,
    reg: Registry,
    repo: Repo,
    ctx: dict[str, Any],
    report: Report,
) -> None:
    where = _rel(path, repo.root)
    errs = list(_schema_errors(ctx["shape_schema"], data))
    if errs:
        for e in errs:
            report.add(where, e)
        return
    sid = data["id"]
    if path.stem != sid:
        report.add(where, f"file name must be {sid}.json")
    for alias in data["aliases"]:
        if alias in reg.shapes:
            report.add(where, f"alias {alias!r} is also a shape id")

    # Layers.
    prims = list(_walk(data["primitives"]))
    used = {p["layer"] for p in prims if "layer" in p}
    for i, p in enumerate(data["primitives"]):
        if "layer" not in p:
            report.add(where, f"primitives[{i}] needs a layer")
    for layer in sorted(used - set(data["layers"])):
        report.add(where, f"layer {layer!r} is used but not declared")
    for layer in sorted(set(data["layers"]) - used):
        report.add(where, f"layer {layer!r} is declared but not used")

    # Grid precision.
    for loc, v in _numbers(data["primitives"], "primitives"):
        if abs(v * 1000 - round(v * 1000)) > EPS:
            report.add(where, f"{loc}: {v} has more than 3 decimals")

    # Parameters.
    for name, d in data["parameters"].items():
        if d["type"] == "integer" and not d["min"] <= d["default"] <= d["max"]:
            report.add(where, f"parameter {name}: default outside min..max")
        if d["type"] == "enum" and d["default"] not in d["values"]:
            report.add(where, f"parameter {name}: default is not one of its values")

    # Sources, images and files.
    cited = _cited({"n": data["names"], "m": data["meaning"]}, "sources")
    for s in sorted(cited - set(data["sources"])):
        report.add(where, f"source {s!r} is cited but not listed in `sources`")
    for s in sorted(set(data["sources"]) - ctx["sources"]):
        report.add(where, f"unknown source {s!r} (not in content/sources.json)")
    images = _cited({"n": data["names"], "m": data["meaning"]}, "images") | set(
        data["references"]["images"]
    )
    for img in sorted(images - ctx["assets"]):
        report.add(where, f"unknown image {img!r} (not in assets/source-manifest.json)")
    for f in data["references"]["files"]:
        target = (repo.root / f).resolve()
        if repo.root.resolve() not in target.parents or not target.is_file():
            report.add(where, f"referenced file {f!r} does not exist in the repository")

    # Geometry: bounds over parameter combinations.
    live = ctx["grid"]["liveArea"]
    try:
        for combo in metrics.combos(data["parameters"]):
            items = expand(data, reg, combo)
            if not items:
                report.add(where, f"{combo or 'defaults'}: expands to nothing")
                continue
            box = g.bbox(items, metrics.STROKE)
            if not _within(box, live):
                shown = [round(v, 3) for v in box]
                report.add(
                    where, f"{combo or 'defaults'}: visual box {shown} leaves the live area {live}"
                )
        items = expand(data, reg)
    except SpecError as exc:
        report.add(where, str(exc))
        return

    center = tuple(data.get("symmetryCenter", [12, 12]))
    for e in metrics.symmetry_errors(items, data["symmetry"], (float(center[0]), float(center[1]))):
        report.add(where, e)

    expected = metrics.compute(items)
    if data["metrics"] != expected:
        report.add(where, "metrics are stale: run `uv run deq-spec fmt`")

    text = path.read_text(encoding="utf-8")
    if text != jsonfmt.dumps(data):
        report.add(where, "not canonically formatted: run `uv run deq-spec fmt`")
    report.checked += 1


def lint(root: Path) -> Report:
    """Run every rule over the repository at ``root``."""
    repo = Repo(root)
    report = Report()
    grid = read_json(repo.spec / "grid.json")
    for e in _schema_errors(repo.schema("grid"), grid):
        report.add("spec/grid.json", e)
    ctx: dict[str, Any] = {
        "shape_schema": repo.schema("shape"),
        "sources": repo.source_ids(),
        "assets": repo.asset_ids(),
        "grid": grid,
    }
    reg = load_registry(repo, report)
    if not reg.shapes:
        report.add("spec/shapes", "no shapes found")
    for sid in sorted(reg.shapes):
        lint_shape(reg.paths[sid], reg.shapes[sid], reg, repo, ctx, report)

    _lint_catalog(repo, reg, report)
    for path in (repo.spec / "grid.json", repo.spec / "catalog.json", repo.spec / "flag.json"):
        if path.is_file() and path.read_text(encoding="utf-8") != jsonfmt.dumps(read_json(path)):
            report.add(_rel(path, root), "not canonically formatted: run `uv run deq-spec fmt`")

    flag_path = repo.spec / "flag.json"
    if not flag_path.is_file():
        report.add("spec/flag.json", "missing")
    else:
        data = read_json(flag_path)
        errs = list(_schema_errors(repo.schema("flag"), data))
        for e in errs:
            report.add("spec/flag.json", e)
        if not errs:
            for e in flag.check(data, root):
                report.add("spec/flag.json", e)
            _lint_sun_ratio(data, reg, report)
    return report


def _lint_catalog(repo: Repo, reg: Registry, report: Report) -> None:
    where = "spec/catalog.json"
    path = repo.spec / "catalog.json"
    if not path.is_file():
        report.add(where, "missing")
        return
    data = read_json(path)
    errs = list(_schema_errors(repo.schema("catalog"), data))
    for e in errs:
        report.add(where, e)
    if errs:
        return
    listed: dict[str, int] = {}
    for cat in data["categories"]:
        for sid in cat["shapes"]:
            listed[sid] = listed.get(sid, 0) + 1
            if sid in reg.shapes and reg.shapes[sid].get("category") != cat["id"]:
                report.add(where, f"{sid} is listed under {cat['id']} but its category differs")
    spec_ids = {s for s, p in reg.paths.items() if p.parent == repo.shapes}
    for sid in sorted(spec_ids - set(listed)):
        report.add(where, f"shape {sid} is not listed")
    for sid in sorted(set(listed) - spec_ids):
        report.add(where, f"listed shape {sid} does not exist in spec/shapes")
    for sid, n in sorted(listed.items()):
        if n > 1:
            report.add(where, f"shape {sid} is listed {n} times")
    for d in data["deferred"]:
        if d["id"] in spec_ids:
            report.add(where, f"deferred motif {d['id']} is also a shape")
        if "drawnAs" in d and d["drawnAs"] not in spec_ids:
            report.add(where, f"deferred motif {d['id']}: drawnAs {d['drawnAs']!r} is not a shape")


def _lint_sun_ratio(flag_data: Json, reg: Registry, report: Report) -> None:
    sun = reg.shapes.get("kurdish-sun")
    if sun is None:
        report.add("spec/shapes", "kurdish-sun is missing")
        return
    stars = [p for p in sun["primitives"] if p.get("type") == "star"]
    want = flag_data["sun"]["innerToOuter"]
    for p in stars:
        ratio = p["innerRadius"] / p["outerRadius"]
        # The outline variant strokes inside the filled outline, so it keeps the ratio loosely.
        if p.get("when", {}).get("variant", "filled") == "filled" and not math.isclose(
            ratio, want, abs_tol=1e-3
        ):
            report.add(
                "spec/shapes/kurdish-sun.json",
                f"inner/outer {ratio:.4f} != flag innerToOuter {want}",
            )
