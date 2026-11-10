# @0xdolan/deq-core

The reference renderer for Deq, the parametric design system of traditional Kurdish tattoo motifs. It is pure ESM with no DOM and no I/O, and it turns any of the 93 catalog shapes into minimal, deterministic, accessible SVG.

```ts
import { render, compose, listShapes, getShape } from "@0xdolan/deq-core";

render("kurdish-sun"); // 24 × 24, currentColor, stroke 2
render("roj-half-sun", { size: 48, color: "#ED2024", params: { rays: 9 } });
render("kurdish-flag", {
  layerColors: { top: "#ED2024", bottom: "#278E43", sun: "#FEBD11" },
});
render("comb", { title: "" }); // decorative: aria-hidden, no <title>

compose([
  { shape: "kurdish-sun", transform: { scale: 0.5, translate: [-6, 0] } },
  { shape: "comb", transform: { scale: 0.5, translate: [6, 0] } },
]);

listShapes("celestial").map((s) => s.id);
getShape("kurdsh-sun"); // DeqError UNKNOWN_SHAPE: … Did you mean kurdish-sun?
```

## Options

| Option                       | Default        | Notes                                  |
| ---------------------------- | -------------- | -------------------------------------- |
| `size`                       | 24             | px, 1 to 8192                          |
| `color`                      | `currentColor` | strokes and dots                       |
| `strokeWidth`                | 2              | grid units, 0.05 to 12                 |
| `absoluteStrokeWidth`        | false          | keep `strokeWidth` in px at any size   |
| `fill`, `fillOpacity`        | `none`, 1      | closed outlines only                   |
| `strokeOpacity`              | 1              | strokes and dots                       |
| `linecap`, `linejoin`        | `round`        |                                        |
| `dotScale`                   | 1              | 0.1 to 4                               |
| `rotation`, `flipX`, `flipY` | 0, false       | about the canvas centre                |
| `padding`, `background`      | 0, `none`      | grid units                             |
| `layerColors`                | none           | colour per layer id                    |
| `title`, `ariaLabel`         | English name   | `title: ""` marks the image decorative |
| `params`                     | defaults       | shape parameters, e.g. `{ rays: 9 }`   |

`DEFAULT_OPTIONS` holds every default (useful for "reset" controls). Invalid input throws `DeqError` with a stable `code` and one line per problem in `issues`.

## Reference

- [API reference](../../docs/api/core.md) (generated)
- [Output contract and golden fixtures](../../docs/decisions/0008-core-renderer-and-golden-fixtures.md)
- [Shape spec guide](../../docs/design/shape-spec.md)

## Development

```sh
pnpm --filter @0xdolan/deq-core generate   # rebuild src/generated/shapes.ts from spec/
pnpm --filter @0xdolan/deq-core fixtures   # rewrite spec/fixtures/
pnpm --filter @0xdolan/deq-core docs       # rewrite docs/api/core.md
pnpm --filter @0xdolan/deq-core test       # unit, property and freshness tests with coverage
```

License: GPL-3.0-or-later.
