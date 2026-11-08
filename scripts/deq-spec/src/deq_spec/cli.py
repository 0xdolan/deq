"""``deq-spec``: lint, format, render and contact sheets for spec/."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from deq_spec import SpecError, jsonfmt, lint, metrics, render, sheet
from deq_spec.spec import ParamValue, expand, read_json

SHEETS = {
    "shapes": Path("docs/design/shapes-contact-sheet.svg"),
    "concepts": Path("docs/design/logo-concepts.svg"),
}


def _write(path: Path, text: str, *, force: bool) -> None:
    if path.is_symlink():
        raise SpecError(f"{path}: refusing to write through a symlink")
    if path.exists() and not force:
        raise SpecError(f"{path} exists; pass --force to overwrite")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sheet(root: Path, which: str) -> str:
    repo = lint.Repo(root)
    reg = lint.load_registry(repo)
    if which == "shapes":
        return sheet.shapes_sheet(reg, read_json(repo.spec / "catalog.json"))
    ids = sorted(sid for sid, p in reg.paths.items() if p.parent == repo.concepts)
    return sheet.concepts_sheet(reg, ids)


def format_files(root: Path, *, check: bool) -> list[Path]:
    """Recompute metrics and rewrite in canonical layout. Returns the files that changed."""
    repo = lint.Repo(root)
    reg = lint.load_registry(repo)
    changed: list[Path] = []
    for sid, path in sorted(reg.paths.items()):
        data = reg.shapes[sid]
        try:
            data["metrics"] = metrics.compute(expand(data, reg))
        except (SpecError, KeyError, TypeError) as exc:
            raise SpecError(f"{path}: cannot compute metrics: {exc}") from exc
        changed += _format(path, data, check=check)
    for path in (repo.spec / "grid.json", repo.spec / "catalog.json", repo.spec / "flag.json"):
        if path.is_file():
            changed += _format(path, read_json(path), check=check)
    return changed


def _format(path: Path, data: object, *, check: bool) -> list[Path]:
    text = jsonfmt.dumps(data)
    if path.read_text(encoding="utf-8") == text:
        return []
    if not check:
        path.write_text(text, encoding="utf-8")
    return [path]


def _param(text: str) -> tuple[str, ParamValue]:
    name, sep, raw = text.partition("=")
    if not sep or not name:
        raise argparse.ArgumentTypeError(f"expected name=value, got {text!r}")
    value: ParamValue
    if raw in {"true", "false"}:
        value = raw == "true"
    elif raw.lstrip("-").isdigit():
        value = int(raw)
    else:
        value = raw
    return name, value


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="deq-spec", description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path.cwd(), help="repository root (default: cwd)"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("lint", help="check every spec file")
    p_fmt = sub.add_parser("fmt", help="recompute metrics and format spec files")
    p_fmt.add_argument("--check", action="store_true", help="only report files that would change")
    p_render = sub.add_parser("render", help="render one shape as SVG")
    p_render.add_argument("shape")
    p_render.add_argument("--param", type=_param, action="append", default=[], metavar="NAME=VALUE")
    p_render.add_argument("--out", type=Path)
    p_render.add_argument("--force", action="store_true")
    p_sheet = sub.add_parser("sheet", help="write a contact sheet SVG")
    p_sheet.add_argument("--set", choices=sorted(SHEETS), default="shapes")
    p_sheet.add_argument("--out", type=Path, help="default: the committed sheet under docs/design/")
    p_sheet.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    root: Path = args.root.resolve()

    try:
        if args.command == "lint":
            report = lint.lint(root)
            for name, rel in SHEETS.items():
                path = root / rel
                if not path.is_file() or path.read_text(encoding="utf-8") != build_sheet(
                    root, name
                ):
                    report.add(
                        str(rel),
                        f"stale or missing: run `uv run deq-spec sheet --set {name} --force`",
                    )
            for e in report.errors:
                print(e, file=sys.stderr)
            if report.errors:
                print(f"deq-spec lint: {len(report.errors)} problem(s)", file=sys.stderr)
                return 1
            print(f"deq-spec lint: {report.checked} shapes OK")
            return 0
        if args.command == "fmt":
            changed = format_files(root, check=args.check)
            for path in changed:
                print(path.relative_to(root))
            return 1 if args.check and changed else 0
        if args.command == "render":
            repo = lint.Repo(root)
            reg = lint.load_registry(repo)
            items = expand(reg.get(args.shape), reg, dict(args.param))
            text = render.svg(items, title=args.shape)
            if args.out is None:
                sys.stdout.write(text)
            else:
                _write(args.out, text, force=args.force)
            return 0
        out = args.out if args.out is not None else root / SHEETS[args.set]
        _write(out, build_sheet(root, args.set), force=args.force)
        print(out)
        return 0
    except SpecError as exc:
        print(f"deq-spec: {exc}", file=sys.stderr)
        return 2
