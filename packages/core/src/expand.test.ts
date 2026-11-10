import { describe, expect, it } from "vitest";

import { DeqError } from "./errors.js";
import { MAX_DEPTH, MAX_FLAT, expand, expandShape, resolveParams, useTransform } from "./expand.js";
import { shape } from "../test/helpers.js";
import type { ParameterDecl, Primitive } from "./types.js";

const PARAMS: Readonly<Record<string, ParameterDecl>> = {
  n: { type: "integer", min: 0, max: 5, default: 2, description: "n" },
  on: { type: "boolean", default: true, description: "on" },
  style: { type: "enum", values: ["x", "y"], default: "x", description: "style" },
};

const code = (fn: () => unknown): string => {
  try {
    fn();
  } catch (err) {
    if (err instanceof DeqError) return err.code;
    throw err;
  }
  return "none";
};

describe("resolveParams", () => {
  const s = shape([], PARAMS);
  it("fills defaults and applies overrides", () => {
    expect(resolveParams(s)).toEqual({ n: 2, on: true, style: "x" });
    expect(resolveParams(s, { n: 5, on: false, style: "y" })).toEqual({
      n: 5,
      on: false,
      style: "y",
    });
  });
  it.each([
    [{ m: 1 }, /unknown parameter "m"/],
    [{ n: 1.5 }, /must be an integer/],
    [{ n: "2" }, /must be an integer/],
    [{ n: 6 }, /outside 0\.\.5/],
    [{ on: 1 }, /true or false/],
    [{ style: "z" }, /not one of x, y/],
    [{ style: 1 }, /not one of/],
  ])("rejects %j", (over, msg) => {
    expect(() => resolveParams(s, over)).toThrow(msg);
    expect(code(() => resolveParams(s, over))).toBe("INVALID_PARAMETER");
  });
  it("lists no known parameters for a shape without any", () => {
    expect(() => resolveParams(shape([]), { x: 1 })).toThrow(/known: none/);
  });
  it("does not treat inherited keys as parameters", () => {
    expect(() => resolveParams(s, JSON.parse('{"toString": 1}') as Record<string, number>)).toThrow(
      /unknown parameter/,
    );
  });
});

describe("expandShape", () => {
  it("draws primitives only when `when` matches", () => {
    const s = shape(
      [
        { type: "dot", cx: 1, cy: 1, layer: "a", when: { on: true } },
        { type: "dot", cx: 2, cy: 2, layer: "a", when: { style: ["y"] } },
        { type: "dot", cx: 3, cy: 3, layer: "a", when: { n: [1, 2] } },
      ],
      PARAMS,
    );
    expect(expandShape(s).map((f) => (f.kind === "circle" ? f.cx : 0))).toEqual([1, 3]);
    expect(expandShape(s, { on: false, style: "y", n: 4 })).toHaveLength(1);
  });
  it("rejects `when` on an unknown parameter", () => {
    const s = shape([{ type: "dot", cx: 1, cy: 1, layer: "a", when: { nope: true } }]);
    expect(code(() => expandShape(s))).toBe("INVALID_SHAPE");
  });
  it("needs a layer", () => {
    expect(() => expandShape(shape([{ type: "dot", cx: 1, cy: 1 }]))).toThrow(/no layer/);
  });
  it("repeats by step, by spread and from the start", () => {
    const el: Primitive = { type: "dot", cx: 12, cy: 12 };
    const xs = (p: Primitive): number[] =>
      expandShape(shape([p], PARAMS)).map((f) => (f.kind === "circle" ? f.cx : Number.NaN));
    expect(xs({ type: "repeat", count: 3, step: [2, 0], element: el, layer: "a" })).toEqual([
      10, 12, 14,
    ]);
    expect(xs({ type: "repeat", count: 3, spread: [8, 0], element: el, layer: "a" })).toEqual([
      8, 12, 16,
    ]);
    expect(xs({ type: "repeat", count: 1, spread: [8, 0], element: el, layer: "a" })).toEqual([12]);
    expect(
      xs({
        type: "repeat",
        count: { param: "n" },
        step: [1, 0],
        align: "start",
        element: el,
        layer: "a",
      }),
    ).toEqual([12, 13]);
    expect(() => xs({ type: "repeat", count: 2, element: el, layer: "a" })).toThrow(
      /step or spread/,
    );
  });
  it("spreads radial copies over a partial or full sweep", () => {
    const el: Primitive = { type: "dot", cx: 22, cy: 12 };
    const angles = (sweep: number, count: number): number[] =>
      expandShape(
        shape([
          { type: "radial", count, center: [12, 12], start: 0, sweep, element: el, layer: "a" },
        ]),
      ).map((f) =>
        f.kind === "circle"
          ? Math.round((Math.atan2(f.cy - 12, f.cx - 12) * 180) / Math.PI)
          : Number.NaN,
      );
    expect(angles(180, 3)).toEqual([0, 90, 180]);
    expect(angles(360, 4)).toEqual([0, 90, 180, -90]);
    expect(angles(360, 1)).toEqual([0]);
    expect(angles(360, 0)).toEqual([]);
  });
  it("scales concentric copies and refuses non-positive scales", () => {
    const el: Primitive = { type: "circle", cx: 12, cy: 12, r: 10 };
    const rs = expandShape(
      shape([
        {
          type: "concentric",
          count: 3,
          center: [12, 12],
          scaleStep: 0.25,
          element: el,
          layer: "a",
        },
      ]),
    ).map((f) => (f.kind === "circle" ? f.r : 0));
    expect(rs).toEqual([10, 7.5, 5]);
    expect(() =>
      expandShape(
        shape([
          {
            type: "concentric",
            count: 5,
            center: [12, 12],
            scaleStep: 0.25,
            element: el,
            layer: "a",
          },
        ]),
      ),
    ).toThrow(/scale/);
  });
  it("validates counts, stars and arcs", () => {
    const el: Primitive = { type: "dot", cx: 1, cy: 1 };
    expect(() =>
      expandShape(
        shape([
          { type: "repeat", count: { param: "missing" }, step: [1, 0], element: el, layer: "a" },
        ]),
      ),
    ).toThrow(/count/);
    expect(() =>
      expandShape(shape([{ type: "repeat", count: -1, step: [1, 0], element: el, layer: "a" }])),
    ).toThrow(/count/);
    const star = {
      type: "star",
      cx: 12,
      cy: 12,
      outerRadius: 5,
      innerRadius: 2,
      rotation: 0,
      layer: "a",
    } as const;
    expect(() => expandShape(shape([{ ...star, points: 1 }]))).toThrow(/at least 2/);
    expect(expandShape(shape([{ ...star, points: 5 }]))[0]).toMatchObject({
      kind: "poly",
      closed: true,
    });
    expect(() =>
      expandShape(shape([{ type: "arc", cx: 0, cy: 0, r: 1, start: 90, end: 90, layer: "a" }])),
    ).toThrow(/arc needs/);
  });
  it("turns every primitive kind into flat items", () => {
    const kinds = expandShape(
      shape([
        { type: "line", x1: 0, y1: 0, x2: 1, y2: 1, layer: "a" },
        {
          type: "polyline",
          points: [
            [0, 0],
            [1, 1],
            [2, 0],
          ],
          layer: "a",
        },
        {
          type: "polygon",
          points: [
            [0, 0],
            [1, 1],
            [2, 0],
          ],
          paint: "fill",
          layer: "a",
        },
        { type: "rect", x: 1, y: 1, width: 2, height: 3, layer: "a" },
        { type: "circle", cx: 1, cy: 1, r: 2, layer: "a" },
        { type: "dot", cx: 1, cy: 1, r: 2, layer: "a" },
        { type: "arc", cx: 1, cy: 1, r: 2, start: 0, end: 90, layer: "a" },
        { type: "ellipse", cx: 1, cy: 1, rx: 2, ry: 1, layer: "a" },
        { type: "path", d: "M0 0L1 1", layer: "a" },
      ]),
    ).map((f) => f.kind);
    expect(kinds).toEqual([
      "poly",
      "poly",
      "poly",
      "poly",
      "circle",
      "circle",
      "arc",
      "ellipse",
      "path",
    ]);
  });
  it("limits the number of flat items", () => {
    const el: Primitive = { type: "dot", cx: 1, cy: 1 };
    const big = shape([
      {
        type: "repeat",
        count: 64,
        step: [0, 0],
        layer: "a",
        element: { type: "repeat", count: 64, step: [0, 0], element: el },
      },
    ]);
    expect(code(() => expandShape(big))).toBe("LIMIT_EXCEEDED");
    expect(MAX_FLAT).toBe(2000);
  });
  it("limits nesting depth", () => {
    let el: Primitive = { type: "dot", cx: 1, cy: 1 };
    for (let i = 0; i <= MAX_DEPTH + 1; i++)
      el = { type: "repeat", count: 1, step: [0, 0], element: el };
    expect(code(() => expandShape(shape([{ ...el, layer: "a" }])))).toBe("LIMIT_EXCEEDED");
  });
});

describe("use", () => {
  it("places a catalog shape in the layer of the `use`", () => {
    const items = expandShape(
      shape([{ type: "use", shape: "roj-half-sun", layer: "b", params: { rays: 3 } }]),
    );
    expect(items.length).toBe(expand("roj-half-sun", { rays: 3 }).length);
    expect(new Set(items.map((f) => f.layer))).toEqual(new Set(["b"]));
  });
  it("detects reference cycles", () => {
    const s = { ...shape([]), id: "roj-half-sun" };
    const looped = {
      ...s,
      primitives: [{ type: "use", shape: "roj-half-sun", layer: "a" }] as const,
    };
    expect(() => expandShape(looped)).toThrow(/reference cycle/);
  });
  it("applies scale, then rotation, then translation about the origin", () => {
    const t = useTransform({
      transform: { scale: 0.5, rotate: 90, translate: [1, 2], origin: [0, 0] },
    });
    expect([t.a, t.b, t.e, t.f].map((x) => Math.round(x * 1000) / 1000)).toEqual([0, 0.5, 1, 2]);
    expect(useTransform({})).toMatchObject({ a: 1, d: 1, e: 0, f: 0 });
  });
  it("reports unknown shapes", () => {
    expect(code(() => expand("no-such-shape"))).toBe("UNKNOWN_SHAPE");
  });
});
