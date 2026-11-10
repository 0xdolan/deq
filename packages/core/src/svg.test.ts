import { describe, expect, it } from "vitest";

import { shape } from "../test/helpers.js";
import { element } from "./svg.js";
import {
  DEFAULT_OPTIONS,
  DeqError,
  compose,
  getShape,
  hasShape,
  listCategories,
  listShapes,
  packageName,
  render,
  renderShapeData,
  resolveOptions,
} from "./index.js";

const err = (fn: () => unknown): DeqError => {
  try {
    fn();
  } catch (e) {
    if (e instanceof DeqError) return e;
    throw e;
  }
  throw new Error("expected a DeqError");
};

describe("registry", () => {
  it("lists every catalog shape and category", () => {
    expect(packageName).toBe("@0xdolan/deq-core");
    expect(listShapes().length).toBe(93);
    expect(listCategories()).toContain("celestial");
    expect(listShapes("celestial").every((s) => s.category === "celestial")).toBe(true);
    expect(hasShape("roj-half-sun")).toBe(true);
    expect(hasShape("nope")).toBe(false);
    expect(getShape("roj-half-sun").names.en).toBe("Half sun");
  });
  it("suggests close ids for unknown shapes", () => {
    const e = err(() => getShape("roj-haf-sun"));
    expect(e.code).toBe("UNKNOWN_SHAPE");
    expect(e.message).toMatch(/Did you mean roj-half-sun/);
    expect(err(() => getShape("zzzzzzzzzzzzzzzzzzzzzzzz")).message).not.toMatch(/Did you mean/);
    expect(err(() => getShape(42 as unknown as string)).message).toMatch(/unknown shape number/);
  });
});

describe("render", () => {
  const svg = render("roj-half-sun");
  it("writes a minimal, accessible document", () => {
    expect(
      svg.startsWith(
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"',
      ),
    ).toBe(true);
    expect(svg).toContain('role="img" aria-label="Half sun"><title>Half sun</title>');
    expect(svg).not.toMatch(/<script|href|url\(|on[a-z]+=/i);
    expect(render("roj-half-sun")).toBe(svg);
  });
  it("draws open arcs as paths and dots as filled circles", () => {
    expect(svg).toContain('<path d="M7 16.5A5 5 0 0 1 17 16.5"/>');
    expect(svg).toContain('<circle cx="12" cy="16.5" r="2" fill="currentColor" stroke="none"/>');
  });
  it("applies size, colour, stroke, caps and opacity", () => {
    const out = render("roj-half-sun", {
      size: 48,
      color: "#ED2024",
      strokeWidth: 1.5,
      linecap: "butt",
      linejoin: "bevel",
      strokeOpacity: 0.5,
    });
    expect(out).toContain('width="48" height="48"');
    expect(out).toContain(
      'stroke-width="1.5" stroke-linecap="butt" stroke-linejoin="bevel" color="#ED2024"',
    );
    expect(out).toContain('stroke-opacity="0.5"');
    expect(out).toContain('fill="currentColor" fill-opacity="0.5" stroke="none"');
  });
  it("keeps absolute stroke widths constant in pixels", () => {
    expect(render("comb", { size: 96, strokeWidth: 2, absoluteStrokeWidth: true })).toContain(
      'stroke-width="0.5"',
    );
    expect(render("comb", { size: 12, absoluteStrokeWidth: true, padding: 6 })).toContain(
      'stroke-width="6"',
    );
  });
  it("scales dots with dotScale", () => {
    expect(render("roj-half-sun", { dotScale: 1.5 })).toContain('r="3" fill="currentColor"');
  });
  it("adds padding, background, rotation and flips", () => {
    const out = render("roj-half-sun", {
      padding: 2,
      background: "white",
      rotation: 30,
      flipX: true,
    });
    expect(out).toContain('viewBox="-2 -2 28 28"');
    expect(out).toContain(
      '<rect x="-2" y="-2" width="28" height="28" fill="white" stroke="none"/>',
    );
    expect(out).toContain('<g transform="rotate(30 12 12) translate(24 0) scale(-1 1)">');
    expect(render("roj-half-sun", { flipY: true })).toContain(
      'transform="translate(0 24) scale(1 -1)"',
    );
    expect(render("roj-half-sun", { rotation: 360 })).not.toContain("transform");
  });
  it("fills closed outlines only", () => {
    const out = renderShapeData(
      shape([
        { type: "circle", cx: 12, cy: 12, r: 5, layer: "a" },
        {
          type: "polyline",
          points: [
            [1, 1],
            [2, 2],
            [3, 1],
          ],
          layer: "a",
        },
        { type: "arc", cx: 12, cy: 12, r: 3, start: 0, end: 360, layer: "a" },
        { type: "path", d: "M1 1L2 2L3 1Z", layer: "a" },
        { type: "path", d: "M1 1L2 2", layer: "a" },
        { type: "ellipse", cx: 12, cy: 12, rx: 3, ry: 2, layer: "b" },
        {
          type: "polygon",
          points: [
            [1, 1],
            [2, 2],
            [3, 1],
          ],
          paint: "fill",
          layer: "b",
        },
      ]),
      { fill: "#FEBD11", fillOpacity: 0.25 },
    );
    const filled = out.match(/fill="#FEBD11" fill-opacity="0.25"/g) ?? [];
    expect(filled).toHaveLength(4);
    expect(out).toContain('<polyline points="1,1 2,2 3,1"/>');
    expect(out).toContain('<path d="M1 1L2 2"/>');
    expect(out).toContain('<circle cx="12" cy="12" r="3" fill="#FEBD11"');
    expect(out).toContain('<polygon points="1,1 2,2 3,1" fill="currentColor" stroke="none"/>');
    expect(
      renderShapeData(shape([{ type: "circle", cx: 1, cy: 1, r: 1, layer: "a" }]), { fill: "red" }),
    ).toContain('r="1" fill="red"/>');
  });
  it("rotates ellipses with a transform attribute", () => {
    const base = {
      kind: "ellipse",
      cx: 12,
      cy: 12,
      rx: 3,
      ry: 2,
      layer: "a",
      paint: "stroke",
    } as const;
    expect(element({ ...base, rotation: 30 }, DEFAULT_OPTIONS)).toBe(
      '<ellipse cx="12" cy="12" rx="3" ry="2" transform="rotate(30 12 12)"/>',
    );
    expect(element({ ...base, rotation: 0 }, DEFAULT_OPTIONS)).toBe(
      '<ellipse cx="12" cy="12" rx="3" ry="2"/>',
    );
  });
  it("groups layers when layer colours are given", () => {
    const out = render("roj-half-sun", { layerColors: { rays: "#FEBD11" } });
    expect(out).toContain('<g data-layer="arc">');
    expect(out).toContain('<g data-layer="rays" color="#FEBD11" stroke="currentColor">');
    const e = err(() => render("roj-half-sun", { layerColors: { ray: "red" } }));
    expect(e.code).toBe("INVALID_OPTIONS");
    expect(e.issues[0]).toMatch(/not a layer of roj-half-sun/);
  });
  it("escapes titles and supports decorative images", () => {
    const out = render("comb", { title: "<b>&", ariaLabel: '"x"' });
    expect(out).toContain('aria-label="&quot;x&quot;"><title>&lt;b&gt;&amp;</title>');
    const deco = render("comb", { title: "", ariaLabel: "" });
    expect(deco).toContain('aria-hidden="true"');
    expect(deco).not.toContain("<title>");
    expect(render("comb", { title: "" })).toContain('aria-hidden="true"');
    const labelled = render("comb", { title: "", ariaLabel: "Teeth" });
    expect(labelled).toContain('role="img" aria-label="Teeth">');
    expect(labelled).not.toContain("<title>");
  });
  it("passes shape parameters", () => {
    expect(render("roj-half-sun", { params: { rays: 3 } }).match(/<line/g)).toHaveLength(3);
    expect(err(() => render("roj-half-sun", { params: { rays: 99 } })).code).toBe(
      "INVALID_PARAMETER",
    );
  });
});

describe("options", () => {
  it("documents every default", () => {
    expect(resolveOptions()).toEqual(DEFAULT_OPTIONS);
    expect(resolveOptions(null)).toEqual(DEFAULT_OPTIONS);
    expect(Object.isFrozen(DEFAULT_OPTIONS)).toBe(true);
  });
  it.each([
    [{ size: 0 }, "size"],
    [{ size: Number.NaN }, "size"],
    [{ color: "url(#x)" }, "color"],
    [{ color: "red;stroke:blue" }, "color"],
    [{ fill: "var(--x)" }, "fill"],
    [{ strokeOpacity: 2 }, "strokeOpacity"],
    [{ linecap: "flat" }, "linecap"],
    [{ layerColors: { __proto__x: "red" } }, "layerColors"],
    [{ params: { "bad-name": 1 } }, "params"],
    [{ params: { n: Number.POSITIVE_INFINITY } }, "params"],
    [{ title: "x".repeat(300) }, "title"],
    [{ unknown: 1 }, "unknown"],
    ["red", ""],
  ])("rejects %j", (opts, key) => {
    const e = err(() => render("comb", opts as never));
    expect(e.code).toBe("INVALID_OPTIONS");
    expect(e.issues.join(" ")).toContain(key);
  });
  it.each([
    "#fff",
    "#FFFF",
    "#ED2024",
    "#ED202480",
    "rebeccapurple",
    "rgb(1 2 3 / 50%)",
    "oklch(0.7 0.1 30)",
    "currentColor",
  ])("accepts the colour %s", (color) => {
    expect(() => render("comb", { color })).not.toThrow();
  });
});

describe("compose", () => {
  it("places shapes without scaling strokes", () => {
    const out = compose(
      [
        { shape: "roj-half-sun", transform: { translate: [0, -4] } },
        { shape: "comb", layer: "base", params: {}, transform: { translate: [0, 7], scale: 1 } },
      ],
      { layerColors: { base: "#ED2024" } },
    );
    expect(out).toContain('aria-label="Composition"');
    expect(out).toContain('<g data-layer="roj-half-sun">');
    expect(out).toContain('<g data-layer="base" color="#ED2024" stroke="currentColor">');
    expect(out).toContain('stroke-width="2"');
  });
  it("ignores options.params and validates parts", () => {
    expect(() => compose([{ shape: "comb" }], { params: { x: 1 } })).not.toThrow();
    expect(err(() => compose([])).code).toBe("INVALID_OPTIONS");
    expect(err(() => compose([{ shape: "comb", transform: { scale: 0 } }])).code).toBe(
      "INVALID_OPTIONS",
    );
    expect(err(() => compose([{ shape: "comb", layer: "Bad Layer" }])).code).toBe(
      "INVALID_OPTIONS",
    );
    expect(err(() => compose([{ shape: "nope" }])).code).toBe("UNKNOWN_SHAPE");
    expect(err(() => compose([{ shape: "roj-half-sun", params: { rays: 0 } }])).code).toBe(
      "INVALID_PARAMETER",
    );
  });
});
