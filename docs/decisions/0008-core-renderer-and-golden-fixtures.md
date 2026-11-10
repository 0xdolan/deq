# 8. Core renderer and golden fixtures

- Status: accepted
- Date: 2026-11-09

## Context

Phase 3 builds `@0xdolan/deq-core`, the reference renderer. Later phases add renderers in Python and Rust, framework wrappers, exporters and the Studio. They must all draw a shape the same way. Without one exact definition of the output, small differences in rounding, attribute order or angle maths would creep in and nobody would notice.

## Decision

- **TypeScript is the reference renderer.** `@0xdolan/deq-core` is pure ESM with no DOM, no I/O and one runtime dependency. It exports `render`, `compose`, `getShape`, `listShapes`, `listCategories`, `hasShape`, `expand`, `expandShape`, `resolveOptions` and `DEFAULT_OPTIONS`, plus the types. The spec is built into `src/generated/shapes.ts` by `scripts/generate-shapes.ts`. That script refuses symlinks and files over 256 KB.
- **Expansion follows `deq-spec`.** Shapes expand exactly as `scripts/deq-spec` does:
  - every primitive and generator in ADR 0007, plus `when` and `{param}` counts;
  - `use` re-layers its parts to the use's layer;
  - the transform is `p' = R(rotate)·(scale·(p − origin)) + origin + translate`;
  - stroke widths and dot radii are not scaled;
  - limits: nesting depth 6 and 2000 flat items, with `LIMIT_EXCEEDED` above them.
- **The output contract.** Every renderer must produce exactly this:
  - **Numbers:** `k = roundHalfEven(x × 1000)`, written from integer thousandths. Trailing zeros are trimmed, and `-0` becomes `0`. Binary floating-point formatting is never used.
  - **Angles:** `cos` and `sin` are exact at multiples of 90°, so axis-aligned points never gain `1e-16` noise.
  - **Root element:** `<svg>` with attributes in this order: `xmlns`, `width`, `height`, `viewBox`, `fill="none"`, `stroke="currentColor"`, `stroke-width`, `stroke-linecap`, `stroke-linejoin`, then optional `color` and `stroke-opacity`, then `role="img"` and `aria-label`. Inside it comes `<title>`, then an optional background `<rect>`, then an optional `<g transform>` holding rotation and flips.
  - **Shape elements:**
    - Elements come in expansion order.
    - Two-point open polylines become `<line>`.
    - Arcs become a `<path>` with one `A` command. A full arc becomes a `<circle>`.
    - Dots are `<circle fill="currentColor" stroke="none">`.
    - `fill` applies only to closed outlines: polygons, non-dot circles, ellipses, paths ending in `Z`, and full arcs.
  - **Layer colours:** `<g data-layer>` groups appear only when `layerColors` is given, in first-use order.
  - **Accessibility:** `role="img"`, `<title>` and `aria-label` default to the shape's English name. A `title` of `""` makes the image decorative: `aria-hidden="true"` and no title.
  - **Safety:** no scripts, no `href`, no `url()`, no `var()`. Colours must match a strict pattern. All text is XML-escaped, and characters XML cannot hold are dropped.
- **Options are validated at runtime with valibot** (1.5.0), with strict objects and documented ranges. It is small and tree-shakable, and it gives typed issues. Every error is a `DeqError` with a stable `code`: `UNKNOWN_SHAPE` (with "did you mean" suggestions), `INVALID_OPTIONS`, `INVALID_PARAMETER`, `INVALID_SHAPE` or `LIMIT_EXCEEDED`.
- **Golden fixtures are the parity contract.** `spec/fixtures/` holds 278 cases, listed in `manifest.json`:
  - every shape at its defaults;
  - the minimum and maximum of every integer parameter, and every other enum or boolean value;
  - every option;
  - layer colours;
  - compositions.

  Each SVG is the exact render output with no header or trailing newline, because other renderers compare it byte for byte. The manifest and `spec/fixtures/README.md` carry the "generated" note instead. `pnpm --filter @0xdolan/deq-core fixtures` rewrites them, and a Vitest test fails when they are stale.

- **Property tests** (fast-check) check that random valid shapes, parameters and options always give well-formed, safe and deterministic SVG, and that invalid input always throws `DeqError`.
- **API docs come from the TypeScript compiler API.** `scripts/api-docs.ts` writes `docs/api/core.md` from the TSDoc comments, and a test keeps the file fresh. TypeDoc was rejected: 0.28 needs minimatch 10. The fix for GHSA-g3hv-75wg-m249 exists only in minimatch 11, which the workspace override enforces, and TypeDoc crashes on 11.

## Consequences

- Python and Rust renderers (and any exporter that draws) pass when their output equals every fixture. Any change to the output contract is a breaking change: it needs a new ADR and regenerated fixtures.
- After a shape changes in `spec/`, run `generate`, then `fixtures`, then `docs` if the API changed. The tests catch any step that was missed.
- The generated files (`src/generated/`, `spec/fixtures/`, `docs/api/`) are excluded from Prettier so their bytes stay exact.
