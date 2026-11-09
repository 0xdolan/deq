---
name: deq-shape-design
description: Rules for drawing, specifying or modifying Deq shapes (grid, strokes, dots, spec schema, construction maths). Use when adding or changing a shape or anything in spec/.
---

# Deq shape design

The format reference is `docs/design/shape-spec.md`, and the decision record is ADR 0007. This skill holds the working rules.

## Grid and defaults

- 24 × 24 units, live area `[1, 1, 22, 22]`, origin top left, up to 3 decimals.
- Stroke 2, round caps and joins. Centre lines stay within 2 to 22.
- Dots are filled, radius 1; the standalone `dot` shape uses radius 2.
- At least 3 units between parallel centre lines. For edges at an angle, measure square to the edge, not along an axis (nested lozenges need a scale step of 0.5, not 0.333).
- Build from the modules in `spec/grid.json` (see `docs/design/shape-spec.md`): circles r 5, 3, 2; dots r 1, 2; rays 2.5 out and 2.5 long; small V 3 × 3 and large V 6 × 6, each drawn as two `line`s; 45-degree pitch 4.5; teeth 3 long at pitch 3. Lint enforces the radii.
- One layer per part and an `id` on every top-level primitive. One shape per design: split images that show several designs, and only merge references that are exactly the same design.
- Compositions `use` other shapes at full size; never scale a used shape.
- Centre the visual box on the grid. Asymmetric shapes are shifted as a whole, and `symmetryCenter` is set when the centre is deliberately off 12, 12 (as on `kurdish-sun`).

## Workflow

1. Draw from a reference image in `assets/source-manifest.json` (its `motifs` list), never from a name alone.
2. Edit or add `spec/shapes/<id>.json`. Use generators (`repeat`, `radial`, `concentric`) instead of copied geometry, and `use` for compositions.
3. Record the maths in `construction`: radii, angles, intersections, and why each number was chosen.
4. Run `uv run deq-spec fmt`, then `uv run deq-spec sheet --set shapes --force` (and `--set concepts` for brand concepts).
5. Run `uv run deq-spec lint`; it must pass. Render the sheet to PNG (`inkscape … -o x.png`) and look at it, especially the small variants.
6. List a new id in `spec/catalog.json`. Ids never change; bump `version` when the geometry changes.

## Content rules

- Never invent a meaning or a Kurdish name. Cite a source id from `content/sources.json`, or use `"status": "unknown"` and `"text": null`.
- Every Sorani and Kurmanji name stays `needs-native-review` until a native speaker checks it.
- `sources` lists exactly the source ids cited in `names` and `meaning`; the lint enforces this.
- Drower's captions (`drower-1941`) go in `names.terms`, with the plate image `drower-ezidi-tattoo-designs-01`.

## Kurdish Sun and flag

- `spec/flag.json` must match the hash-pinned `spec/reference/Flag_of_Kurdistan.svg`. Never edit the reference file, and never change a flag value without checking it against the reference.
- The sun's inner radius is half its outer radius. Its height is R (1 + cos(π/21)): the 20-unit keyline in the icon, or half the flag height.
- The national emblem has 21 rays. Other ray counts are for design use only, and are never shown as the flag.
- Follow `deq-brand` for colour and flag usage.

## Generated files

- `metrics` in each shape, and `docs/design/*.svg`, are generated. Regenerate them; never edit them by hand.
- TS, Python and Rust shape data (Phase 3+) will be generated from `spec/` with a "generated, do not edit" header.
