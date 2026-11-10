import { describe, expect, it } from "vitest";

import { DeqError } from "./errors.js";
import * as g from "./geometry.js";
import type { Flat } from "./geometry.js";

const close = (a: readonly number[], b: readonly number[]): void => {
  expect(a.length).toBe(b.length);
  a.forEach((x, i) => {
    expect(x).toBeCloseTo(b[i] ?? Number.NaN, 9);
  });
};

describe("transforms", () => {
  it("rotates clockwise on screen about a centre", () => {
    close(g.apply(g.rotate(90, [12, 12]), [22, 12]), [12, 22]);
    close(g.apply(g.rotate(45), [1, 0]), [Math.SQRT1_2, Math.SQRT1_2]);
  });
  it("is exact at multiples of 90 degrees", () => {
    expect(g.cosSin(-90)).toEqual([0, -1]);
    expect(g.cosSin(180)).toEqual([-1, 0]);
    expect(g.cosSin(450)).toEqual([0, 1]);
    expect(g.cosSin(720)).toEqual([1, 0]);
  });
  it("chains inner then outer and tracks scale and angle", () => {
    const t = g.chain(g.scale(2, [12, 12]), g.chain(g.rotate(30), g.translate(1, 2)));
    expect(t.scale).toBe(2);
    expect(t.angle).toBe(30);
    const p = g.apply(g.scale(2, [12, 12]), [13, 12]);
    close(g.apply(t, [13, 12]), g.apply(g.translate(1, 2), g.apply(g.rotate(30), p)));
  });
});

describe("parsePath", () => {
  it("parses every supported command into absolute segments", () => {
    expect(g.parsePath("M1 2 L3 4 H5 V6 Q7 8 9 10 C1 2 3 4 5 6 Z")).toEqual([
      ["M", [1, 2]],
      ["L", [3, 4]],
      ["L", [5, 4]],
      ["L", [5, 6]],
      ["Q", [7, 8], [9, 10]],
      ["C", [1, 2], [3, 4], [5, 6]],
      ["Z"],
    ]);
  });
  it("accepts compact numbers", () => {
    expect(g.parsePath("M.5-1L-2 .25")).toEqual([
      ["M", [0.5, -1]],
      ["L", [-2, 0.25]],
    ]);
  });
  it.each(["L1 2", "M1 2 l3 4", "M1", "M1 2 Q1 2 3", "", "M1 2 A1 1 0 0 1 3 4", "M1 2 3"])(
    "rejects %j",
    (d) => {
      expect(() => g.parsePath(d)).toThrow(DeqError);
    },
  );
});

describe("transformFlat", () => {
  const t = g.chain(g.scale(2), g.rotate(90));
  it("returns the item unchanged for the identity", () => {
    const item: Flat = {
      kind: "circle",
      cx: 1,
      cy: 2,
      r: 3,
      layer: "a",
      paint: "stroke",
      dot: false,
    };
    expect(g.transformFlat(item, g.IDENTITY)).toBe(item);
  });
  it("scales circles but not dots", () => {
    const c = g.transformFlat(
      { kind: "circle", cx: 1, cy: 0, r: 3, layer: "a", paint: "stroke", dot: false },
      t,
    );
    const d = g.transformFlat(
      { kind: "circle", cx: 1, cy: 0, r: 1, layer: "a", paint: "fill", dot: true },
      t,
    );
    expect(c).toMatchObject({ r: 6 });
    expect(d).toMatchObject({ r: 1 });
    if (c.kind === "circle") close([c.cx, c.cy], [0, 2]);
  });
  it("rotates arcs and ellipses", () => {
    const a = g.transformFlat(
      { kind: "arc", cx: 0, cy: 0, r: 1, start: 0, end: 90, layer: "a", paint: "stroke" },
      t,
    );
    expect(a).toMatchObject({ r: 2, start: 90, end: 180 });
    const e = g.transformFlat(
      { kind: "ellipse", cx: 0, cy: 0, rx: 1, ry: 2, rotation: 0, layer: "a", paint: "stroke" },
      t,
    );
    expect(e).toMatchObject({ rx: 2, ry: 4, rotation: 90 });
  });
  it("maps every point of polys and paths", () => {
    const p = g.transformFlat(
      { kind: "poly", points: [[1, 0]], closed: false, layer: "a", paint: "stroke" },
      t,
    );
    if (p.kind === "poly") close(p.points[0] ?? [], [0, 2]);
    const path = g.transformFlat(
      {
        kind: "path",
        segments: g.parsePath("M1 0L1 0Q1 0 1 0C1 0 1 0 1 0Z"),
        layer: "a",
        paint: "stroke",
      },
      t,
    );
    if (path.kind === "path") {
      for (const seg of path.segments)
        for (const pt of seg.slice(1)) close(pt as readonly number[], [0, 2]);
      expect(path.segments.at(-1)).toEqual(["Z"]);
    }
  });
});

describe("starPoints", () => {
  it("alternates outer and inner radii starting at the rotation", () => {
    const pts = g.starPoints(0, 0, 4, 2, 1, -90);
    expect(pts).toHaveLength(8);
    close(pts[0] ?? [], [0, -2]);
    close(pts[2] ?? [], [2, 0]);
    expect(Math.hypot(...(pts[1] ?? [0, 0]))).toBeCloseTo(1, 9);
  });
});
