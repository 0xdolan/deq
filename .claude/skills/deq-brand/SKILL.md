---
name: deq-brand
description: Deq logo, color and Kurdish flag usage rules. Use when making brand assets, marketing images, or anything with the flag or Kurdish Sun.
---

# Deq brand

> Phase 2 filled in the flag and the logo concepts. Phase 12 adds the lockup, wordmark and brand tokens.

## Logo

- Symbol only until Phase 12: no wordmark or lockup.
- The concepts are in `assets/brand/concepts/logo-concept-*.json`, in the shape format with category `brand`, on the 24-unit grid. They are drawn mono and in flag colours in `docs/design/logo-concepts.svg` (`uv run deq-spec sheet --set concepts --force`).
- The owner picks one concept before Phase 2 merges. Record the choice in `docs/research/motif-catalog.md` and here, and delete or archive the others only when asked.

## Flag of Kurdistan

- `spec/flag.json` is the only source for flag values, and the lint checks it against the hash-pinned Commons SVG in `spec/reference/`.
- 3:2 ratio. Equal red `#ED2024`, white `#FFFFFF` and green `#278E43` bands, with a yellow `#FEBD11` sun of 21 rays, first ray up, half the flag height, inner radius half the outer radius.
- Pantone values are `null` until verified from a primary source; never quote one.
- Use only the variants listed in `spec/flag.json` (full colour, mono black, mono white, outline, high contrast, square). Never recolour, stretch or change the ray count of the flag itself.

## Colour

- All colour pairs must meet WCAG AA where they carry text or meaning; `spec/flag.json` lists the measured contrast pairs.
- No pair of flag colours reaches 4.5:1. Red on white (4.35) and white on green (4.17) pass only for large text and graphics (3:1). Never use yellow on white (1.68) or red on green (1.04) to carry meaning; use black or white text instead.
