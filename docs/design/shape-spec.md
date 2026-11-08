# Shape spec

`spec/` is the single source of truth for every Deq shape. Renderers, exporters, icon packages and the site read it; nothing else defines geometry. The format decision is [ADR 0007](../decisions/0007-shape-spec-format.md).

| File                        | What it holds                                                          |
| --------------------------- | ---------------------------------------------------------------------- |
| `spec/grid.json`            | Canvas, live area, keylines, stroke and dot defaults                   |
| `spec/shapes/<id>.json`     | One shape: names, meaning, sources, layers, primitives, maths, metrics |
| `spec/catalog.json`         | Categories in display order, and deferred motifs                       |
| `spec/flag.json`            | The flag of Kurdistan: geometry, colours, sun, variants, sizes         |
| `spec/reference/*.svg`      | Hash-pinned reference files the lint checks against                    |
| `spec/schema/*.schema.json` | JSON Schemas (draft 2020-12)                                           |
| `assets/brand/concepts/`    | Logo concepts, in the shape format with category `brand`               |
| `docs/design/*.svg`         | Generated contact sheets (do not edit)                                 |

## The grid

- 24 × 24 units, origin top left, y down. The live area is `[1, 1, 22, 22]`. Numbers have at most 3 decimals.
- Stroke 2, round caps and joins, `fill: none`, `stroke: currentColor`. Centre lines therefore stay within 2 to 22 so the ink stays inside the live area.
- Dots are filled circles of radius 1 (a standalone `dot` uses radius 2).
- Keylines: the circle of radius 10, the 18 × 18 square, and 20 × 16 and 16 × 20 rectangles.
- Keep at least 3 units between parallel centre lines (1 unit of clear space between strokes).

## A shape file

Keys, in canonical order:

```text
$schema, id, version, category, names, aliases, tags, meaning, sources, layers,
primitives, symmetry, symmetryCenter?, parameters, construction, references, metrics
```

- `id`: kebab-case, equal to the file name, never changed. `version` goes up when the geometry changes.
- `names`: `en`, plus `ckb` and `kmr` objects with `text` (or null), `status` (`needs-native-review` until a native speaker checks it), `sources`, `images` and an optional `note`. `terms` lists transliterated names from sources (for example Drower's captions).
- `meaning`: either `{ "status": "unknown", "note"? }` or `{ "status": "sourced", "statements": [{ "text", "sources", "images" }] }`. Never write a meaning without a citation.
- `sources`: every source id cited anywhere in `names` or `meaning`, and only those. Ids come from `content/sources.json`; image ids from `assets/source-manifest.json`.
- `layers`: names in drawing order. Every top-level primitive has a `layer`, and every declared layer is used. Exporters write one group per layer.
- `symmetry`: `none`, `mirror-x` (left–right), `mirror-y` (top–bottom), `mirror-xy`, or `rotational-N`, checked at the defaults about `symmetryCenter` (default `[12, 12]`).
- `construction`: plain-language steps with the maths behind each number.
- `references`: `images` (manifest ids) and `files` (repository paths).
- `metrics`: written by `deq-spec fmt`. Do not edit.

## Primitives

| Type         | Fields                                                                                                                       |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| `line`       | `x1 y1 x2 y2`                                                                                                                |
| `polyline`   | `points` (open)                                                                                                              |
| `polygon`    | `points` (closed)                                                                                                            |
| `path`       | `d`: absolute `M L H V C Q Z` only                                                                                           |
| `circle`     | `cx cy r`                                                                                                                    |
| `dot`        | `cx cy r?` (filled, default r 1)                                                                                             |
| `arc`        | `cx cy r start end`: degrees clockwise from +x, `start < end ≤ start + 360`                                                  |
| `ellipse`    | `cx cy rx ry`                                                                                                                |
| `rect`       | `x y width height`                                                                                                           |
| `star`       | `cx cy points outerRadius innerRadius rotation`                                                                              |
| `repeat`     | `count`, `step [dx, dy]` or `spread [w, h]`, `align` (`center`/`start`), `element`                                           |
| `radial`     | `count center start sweep element`: sweep 360 spaces copies 360/n apart; otherwise the first and last copies sit at the ends |
| `concentric` | `count center scaleStep element`: copy i is scaled by 1 − i · scaleStep                                                      |
| `use`        | `shape params? transform?`: `translate`, `scale` (≤ 4), `rotate`, `origin` (default [12, 12])                                |

Any primitive may take `paint` (`stroke` or `fill`), `id`, and `when`. Generators may nest up to 6 deep, and a shape may expand to at most 2000 primitives.

- **Counts** are an integer from 1 to 64, or `{ "param": "name" }`.
- **`when`** maps parameter names to a value, or to a list of values; the primitive is drawn only when all of them match.
- **`use`** draws the referenced shape with its own layers merged into the `use`'s layer. Stroke width and dot radius are not scaled.

## Parameters

```json
"parameters": {
  "rays": { "type": "integer", "min": 3, "max": 11, "default": 7, "description": "…" },
  "centerDot": { "type": "boolean", "default": false, "description": "…" },
  "style": { "type": "enum", "values": ["lines", "dots"], "default": "lines", "description": "…" }
}
```

The lint expands every combination of each integer's min, default and max, both booleans and every enum value. When there are more than 256 combinations, it varies one parameter at a time instead. Every combination must stay inside the live area.

## Commands

```sh
uv run deq-spec lint                      # every check; runs in `just test` and CI
uv run deq-spec fmt                       # recompute metrics, canonical layout
uv run deq-spec render roj-half-sun --param rays=5 > sun.svg
uv run deq-spec sheet --set shapes --force     # docs/design/shapes-contact-sheet.svg
uv run deq-spec sheet --set concepts --force   # docs/design/logo-concepts.svg
```

## The flag

`spec/flag.json` follows the Wikimedia Commons SVG pinned in `spec/reference/`. Its main values:

- **Field:** 3:2, 900 × 600. Three bands of 200: red `#ED2024`, white `#FFFFFF` and green `#278E43`.
- **Sun:** yellow `#FEBD11`, 21 rays, first ray up.
- **Sun size:** R = 300 / (1 + cos(π/21)) = 150.842, so the star is exactly half the flag height. The inner radius is R / 2.
- **Sun centre:** (450, 300.842). It sits 0.842 below the middle because the star reaches R above its centre but only R cos(π/21) below.

The lint checks all of this against the SVG, along with the colour conversions and contrast ratios. Pantone values are `null` until verified from a primary source.
