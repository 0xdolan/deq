---
name: deq-shape-design
description: Rules for drawing, specifying or modifying Deq shapes (grid, strokes, dots, spec schema, construction maths). Use when adding or changing a shape or anything in spec/.
---

# Deq shape design

> Phase 0 stub. Phase 2 fills in the schema reference and construction examples.

## Grid and defaults (PRD §8.1)

- Canvas 24 × 24 units, 1-unit safe padding (live area 22 × 22), origin top-left, up to 3 decimals.
- Stroke width 2, round caps and joins, `fill: none`, `stroke: currentColor`.
- Dots are filled circles, radius 1 (optically equal to a 2-unit stroke).

## Rules

- Each shape is one JSON file in `spec/shapes/`, validated by `spec/schema/shape.schema.json`. IDs are kebab-case and never change.
- Every shape lists its primitives, named layers, symmetry, metrics, construction steps with maths, parameters, references and sources.
- Never invent a meaning: cite a source or mark it `"unknown"`.
- Compositions reference base shapes; they do not copy geometry.
- TS, Python and Rust code is generated from the spec; never edit generated shape data by hand.
