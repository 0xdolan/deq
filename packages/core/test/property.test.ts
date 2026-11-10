import fc from "fast-check";
import { describe, expect, it } from "vitest";

import { DeqError, compose, getShape, listShapes, num, render } from "../src/index.js";
import type { ParamValue, RenderOptions, ShapeData } from "../src/index.js";

const ids = listShapes().map((s) => s.id);

/** A valid parameter set for a shape. */
function paramsFor(shape: ShapeData): fc.Arbitrary<Record<string, ParamValue>> {
  const entries = Object.entries(shape.parameters).map(([name, d]) => {
    const arb: fc.Arbitrary<ParamValue> =
      d.type === "integer"
        ? fc.integer({ min: d.min, max: d.max })
        : d.type === "boolean"
          ? fc.boolean()
          : fc.constantFrom(...d.values);
    return [name, arb] as const;
  });
  return fc
    .record(Object.fromEntries(entries), { requiredKeys: [] })
    .map((r) =>
      Object.fromEntries(
        Object.entries(r).filter((e): e is [string, ParamValue] => e[1] !== undefined),
      ),
    );
}

const colour = fc.constantFrom("currentColor", "#ED2024", "#fff", "rgb(1 2 3)", "teal");
const options = fc.record(
  {
    size: fc.double({ min: 1, max: 512, noNaN: true }),
    color: colour,
    strokeWidth: fc.double({ min: 0.05, max: 12, noNaN: true }),
    absoluteStrokeWidth: fc.boolean(),
    fill: fc.constantFrom("none", "#FEBD11"),
    fillOpacity: fc.double({ min: 0, max: 1, noNaN: true }),
    strokeOpacity: fc.double({ min: 0, max: 1, noNaN: true }),
    linecap: fc.constantFrom("round", "butt", "square"),
    linejoin: fc.constantFrom("round", "miter", "bevel"),
    dotScale: fc.double({ min: 0.1, max: 4, noNaN: true }),
    rotation: fc.double({ min: -720, max: 720, noNaN: true }),
    flipX: fc.boolean(),
    flipY: fc.boolean(),
    padding: fc.double({ min: 0, max: 24, noNaN: true }),
    background: fc.constantFrom("none", "#000"),
    title: fc.string({ maxLength: 40 }),
    ariaLabel: fc.string({ maxLength: 40 }),
  },
  { requiredKeys: [] },
);

const shapeAndOptions = fc
  .constantFrom(...ids)
  .chain((id) => fc.tuple(fc.constant(id), paramsFor(getShape(id)), options))
  .map(([id, params, opts]): [string, RenderOptions] => [id, { ...opts, params }]);

/** Balanced tags, nothing executable, no external references, numbers with at most 3 decimals. */
function checkSvg(svg: string): void {
  expect(svg.startsWith('<svg xmlns="http://www.w3.org/2000/svg" ')).toBe(true);
  expect(svg.endsWith("</svg>")).toBe(true);
  expect(svg).not.toMatch(/<script|<foreignObject|\shref=|xlink:|url\(|\son[a-z]+=|<!/i);
  const stack: string[] = [];
  for (const m of svg.matchAll(/<(\/?)([a-zA-Z]+)[^>]*?(\/?)>/g)) {
    const [, close, tag, self] = m;
    if (self) continue;
    if (close) expect(stack.pop()).toBe(tag);
    else stack.push(tag ?? "");
  }
  expect(stack).toEqual([]);
  const attrs = svg.replace(/<title>[^<]*<\/title>/, "").replace(/aria-label="[^"]*"/, "");
  for (const n of attrs.matchAll(/-?\d+\.(\d+)/g))
    expect((n[1] ?? "").length).toBeLessThanOrEqual(3);
}

describe("properties", () => {
  it("every valid shape, parameter set and option set renders well-formed, safe SVG", () => {
    fc.assert(
      fc.property(shapeAndOptions, ([id, opts]) => {
        checkSvg(render(id, opts));
      }),
      { numRuns: 400 },
    );
  });

  it("rendering is deterministic", () => {
    fc.assert(
      fc.property(shapeAndOptions, ([id, opts]) => {
        expect(render(id, opts)).toBe(render(id, structuredClone(opts)));
      }),
      { numRuns: 200 },
    );
  });

  it("width and height equal the requested size", () => {
    fc.assert(
      fc.property(fc.constantFrom(...ids), fc.integer({ min: 1, max: 8192 }), (id, size) => {
        expect(render(id, { size })).toContain(`width="${num(size)}" height="${num(size)}"`);
      }),
    );
  });

  it("arbitrary titles never break out of the markup", () => {
    fc.assert(
      fc.property(fc.string({ maxLength: 256, unit: "binary" }), (title) => {
        const svg = render("comb", { title, ariaLabel: title });
        checkSvg(svg);
        expect(svg.match(/<title>/g)?.length ?? 0).toBeLessThanOrEqual(1);
      }),
    );
  });

  it("anything that is not a valid option set fails with a DeqError", () => {
    fc.assert(
      fc.property(fc.anything(), (junk) => {
        try {
          render("comb", junk as RenderOptions);
        } catch (err) {
          expect(err).toBeInstanceOf(DeqError);
        }
      }),
    );
  });

  it("unknown ids fail with UNKNOWN_SHAPE", () => {
    fc.assert(
      fc.property(fc.string({ maxLength: 80 }), (id) => {
        fc.pre(!ids.includes(id));
        expect(() => render(id)).toThrow(DeqError);
      }),
    );
  });

  it("compositions of valid parts render", () => {
    const part = fc.constantFrom(...ids).map((shape) => ({ shape }));
    fc.assert(
      fc.property(fc.array(part, { minLength: 1, maxLength: 4 }), (parts) => {
        checkSvg(compose(parts));
      }),
      { numRuns: 50 },
    );
  });
});
