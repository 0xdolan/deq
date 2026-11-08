# 7. Shape spec format

- Status: accepted
- Date: 2026-11-08

## Context

Phase 2 needs one source of truth that the TypeScript, Python and Rust renderers, the exporters and the site can all read. It must describe the 45 approved motifs, the Kurdish Sun and the flag exactly, carry names, meanings and sources, and be checkable by machine before any code is generated from it.

## Decision

- **JSON files, one per shape**, in `spec/shapes/<id>.json`, validated by JSON Schema draft 2020-12 (`spec/schema/shape.schema.json`). The grid (`spec/grid.json`), the catalog (`spec/catalog.json`) and the flag (`spec/flag.json`) have their own schemas.
- **Geometry as declarative primitives** on the 24 × 24 grid: line, polyline, polygon, path (absolute M, L, H, V, C, Q, Z only), circle, dot, arc, ellipse, rect and star, plus four generators: `repeat`, `radial`, `concentric` and `use`. Generators replace copied geometry, so a ray count or dot count is one parameter. `use` references another shape, and compositions are built only that way.
- **Parameters** are typed (integer with min and max, boolean, enum) and bound with `{ "param": name }` in counts or with `when` on a primitive. There are no expressions: no arithmetic, no `eval`, nothing a renderer has to interpret beyond the listed fields. Each renderer can implement the format in a few hundred lines.
- **Stroke 2 and dot radius 1 are not scaled** by `use` transforms, so a referenced shape keeps the system's line weight.
- **Metrics are computed, not written by hand.** `deq-spec fmt` recomputes the bounding box, visual box, optical centre, stroke-to-size ratio and primitive count, and writes every file in one canonical layout (100 columns). `deq-spec lint` fails if a file is stale.
- **`scripts/deq-spec`** is a private Python tool in the uv workspace, held to the same rules as `deq-assets` (mypy strict, Ruff, coverage of at least 95%). It has one dependency, `jsonschema` 4.26.0. `lint` runs in `just test` and CI. It checks:
  - the schemas, file names and aliases;
  - layers, 3-decimal precision and parameter defaults;
  - that cited sources and images exist;
  - that every parameter combination stays inside the live area;
  - the declared symmetry, the metrics and the formatting;
  - the catalog;
  - that the flag matches the reference SVG;
  - that the committed contact sheets are current.
- **The flag is pinned to a reference file.** `spec/reference/Flag_of_Kurdistan.svg` is a byte-identical copy of the public-domain Wikimedia Commons file, pinned by SHA-256 and SHA-1. The lint parses it only after the hash matches. It then checks every band, colour and sun vertex against `spec/flag.json` (within 0.01 units). Where Wikipedia's RGB triples disagree with its own hex codes, the SVG's hex codes win, and the other colour spaces are computed from them.
- **Kurdish Sun proportions** come from the flag: inner radius = outer radius / 2. The star's height, R (1 + cos(π/21)), equals the 20-unit keyline in the icon and half the flag height on the flag.
- **Logo concepts** use the same format, in `assets/brand/concepts/` with category `brand`, so they are linted and drawn by the same tools.

## Consequences

- Renderers in Phases 3 to 5 read only JSON and need no maths beyond affine transforms and star points.
- The format has no expressions, so some constructions (for example the crescent's horn angles) are worked out once and written as numbers. The maths is recorded in each shape's `construction` steps.
- Adding a primitive type means changing the schema, `deq-spec` and every renderer together.
- The contact sheets in `docs/design/` are generated and committed so that reviewers can see the shapes without running anything. The lint keeps them in step with the spec.
