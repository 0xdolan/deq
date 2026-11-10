/** Deterministic, accessible SVG output for shapes and compositions. */
import * as v from "valibot";

import { DeqError } from "./errors.js";
import { expandShape } from "./expand.js";
import { cosSin } from "./geometry.js";
import type { Flat } from "./geometry.js";
import { escapeXml, num } from "./format.js";
import { ParamsSchema, issueLines, resolveOptions } from "./options.js";
import type { RenderOptions, ResolvedOptions } from "./options.js";
import { getShape } from "./registry.js";
import type { ShapeData, UsePrimitive, Vec } from "./types.js";

/** Canvas size in grid units. */
export const CANVAS = 24;
const CENTER = CANVAS / 2;

function pts(points: readonly Vec[]): string {
  return points.map(([x, y]) => `${num(x)},${num(y)}`).join(" ");
}

function isClosed(item: Flat): boolean {
  switch (item.kind) {
    case "poly":
      return item.closed;
    case "circle":
      return !item.dot;
    case "ellipse":
      return true;
    case "arc":
      return item.end - item.start >= 360;
    case "path":
      return item.segments.some((s) => s[0] === "Z");
  }
}

/** Paint attributes of one element, given the resolved options. */
function paintAttrs(item: Flat, o: ResolvedOptions): string {
  const filled = item.paint === "fill" || (item.kind === "circle" && item.dot);
  if (filled) {
    const op = o.strokeOpacity === 1 ? "" : ` fill-opacity="${num(o.strokeOpacity)}"`;
    return ` fill="currentColor"${op} stroke="none"`;
  }
  if (o.fill !== "none" && isClosed(item)) {
    const op = o.fillOpacity === 1 ? "" : ` fill-opacity="${num(o.fillOpacity)}"`;
    return ` fill="${escapeXml(o.fill)}"${op}`;
  }
  return "";
}

function circle(cx: number, cy: number, r: number): string {
  return `<circle cx="${num(cx)}" cy="${num(cy)}" r="${num(r)}"`;
}

/** One SVG element; stroke attributes are inherited from the root. */
export function element(item: Flat, o: ResolvedOptions): string {
  const paint = paintAttrs(item, o);
  switch (item.kind) {
    case "poly": {
      const [p, q] = item.points;
      if (!item.closed && item.points.length === 2 && p && q) {
        return `<line x1="${num(p[0])}" y1="${num(p[1])}" x2="${num(q[0])}" y2="${num(q[1])}"/>`;
      }
      const tag = item.closed ? "polygon" : "polyline";
      return `<${tag} points="${pts(item.points)}"${paint}/>`;
    }
    case "circle":
      return `${circle(item.cx, item.cy, item.dot ? item.r * o.dotScale : item.r)}${paint}/>`;
    case "arc": {
      const sweep = item.end - item.start;
      if (sweep >= 360) return `${circle(item.cx, item.cy, item.r)}${paint}/>`;
      const [c0, s0] = cosSin(item.start);
      const [c1, s1] = cosSin(item.end);
      const r = num(item.r);
      const large = sweep > 180 ? 1 : 0;
      const from = `${num(item.cx + item.r * c0)} ${num(item.cy + item.r * s0)}`;
      const to = `${num(item.cx + item.r * c1)} ${num(item.cy + item.r * s1)}`;
      return `<path d="M${from}A${r} ${r} 0 ${String(large)} 1 ${to}"/>`;
    }
    case "ellipse": {
      const rot =
        item.rotation % 360 === 0
          ? ""
          : ` transform="rotate(${num(item.rotation)} ${num(item.cx)} ${num(item.cy)})"`;
      return `<ellipse cx="${num(item.cx)}" cy="${num(item.cy)}" rx="${num(item.rx)}" ry="${num(item.ry)}"${rot}${paint}/>`;
    }
    case "path": {
      const d = item.segments
        .map(
          (seg) =>
            seg[0] +
            seg
              .slice(1)
              .map((p) => `${num((p as Vec)[0])} ${num((p as Vec)[1])}`)
              .join(" "),
        )
        .join("");
      return `<path d="${d}"${paint}/>`;
    }
  }
}

function body(items: readonly Flat[], o: ResolvedOptions): string {
  const colored = Object.keys(o.layerColors).length > 0;
  if (!colored) return items.map((item) => element(item, o)).join("");
  // Group by layer in first-use order so each layer can carry its own colour.
  const layers = new Map<string, string[]>();
  for (const item of items) {
    const list = layers.get(item.layer) ?? [];
    list.push(element(item, o));
    layers.set(item.layer, list);
  }
  let out = "";
  for (const [layer, elements] of layers) {
    const c = o.layerColors[layer];
    // Re-declare stroke: SVG 1.1 renderers resolve currentColor where it is declared.
    const style = c === undefined ? "" : ` color="${escapeXml(c)}" stroke="currentColor"`;
    out += `<g data-layer="${escapeXml(layer)}"${style}>${elements.join("")}</g>`;
  }
  return out;
}

function groupTransform(o: ResolvedOptions): string {
  const parts: string[] = [];
  if (o.rotation % 360 !== 0)
    parts.push(`rotate(${num(o.rotation)} ${num(CENTER)} ${num(CENTER)})`);
  if (o.flipX || o.flipY) {
    parts.push(
      `translate(${o.flipX ? num(CANVAS) : "0"} ${o.flipY ? num(CANVAS) : "0"})`,
      `scale(${o.flipX ? "-1" : "1"} ${o.flipY ? "-1" : "1"})`,
    );
  }
  return parts.join(" ");
}

/** Build the SVG document for expanded items. */
function document(items: readonly Flat[], o: ResolvedOptions, defaultTitle: string): string {
  const box = CANVAS + 2 * o.padding;
  const stroke = o.absoluteStrokeWidth ? (o.strokeWidth * box) / o.size : o.strokeWidth;
  const title = o.title ?? defaultTitle;
  const label = o.ariaLabel ?? title;
  const a11y =
    title === "" && label === ""
      ? ' aria-hidden="true"'
      : ` role="img" aria-label="${escapeXml(label)}"`;
  const colorAttr = o.color === "currentColor" ? "" : ` color="${escapeXml(o.color)}"`;
  const opacity = o.strokeOpacity === 1 ? "" : ` stroke-opacity="${num(o.strokeOpacity)}"`;
  const vb = `${num(-o.padding)} ${num(-o.padding)} ${num(box)} ${num(box)}`;
  let out =
    `<svg xmlns="http://www.w3.org/2000/svg" width="${num(o.size)}" height="${num(o.size)}" viewBox="${vb}"` +
    ` fill="none" stroke="currentColor" stroke-width="${num(stroke)}"` +
    ` stroke-linecap="${o.linecap}" stroke-linejoin="${o.linejoin}"${colorAttr}${opacity}${a11y}>`;
  if (title !== "") out += `<title>${escapeXml(title)}</title>`;
  if (o.background !== "none") {
    out += `<rect x="${num(-o.padding)}" y="${num(-o.padding)}" width="${num(box)}" height="${num(box)}" fill="${escapeXml(o.background)}" stroke="none"/>`;
  }
  const transform = groupTransform(o);
  const inner = body(items, o);
  out += transform ? `<g transform="${transform}">${inner}</g>` : inner;
  return `${out}</svg>`;
}

function checkLayers(shape: ShapeData, o: ResolvedOptions): void {
  const unknown = Object.keys(o.layerColors).filter((l) => !shape.layers.includes(l));
  if (unknown.length > 0) {
    const issues = unknown.map(
      (l) => `layerColors.${l}: not a layer of ${shape.id} (${shape.layers.join(", ")})`,
    );
    throw new DeqError("INVALID_OPTIONS", `invalid render options: ${issues.join("; ")}`, issues);
  }
}

/** Render a shape description (already validated) to an SVG string. */
export function renderShapeData(shape: ShapeData, options: RenderOptions = {}): string {
  const o = resolveOptions(options);
  checkLayers(shape, o);
  return document(expandShape(shape, o.params), o, shape.names.en);
}

/**
 * Render the catalog shape `id` as a standalone SVG string.
 *
 * ```ts
 * render("roj-half-sun", { size: 48, strokeWidth: 1.5, color: "#ED2024", params: { rays: 9 } });
 * ```
 *
 * @throws {DeqError} `UNKNOWN_SHAPE`, `INVALID_OPTIONS` or `INVALID_PARAMETER`.
 */
export function render(id: string, options: RenderOptions = {}): string {
  return renderShapeData(getShape(id), options);
}

/** One shape placed in a composition. */
export interface CompositionPart {
  /** Catalog shape id. */
  readonly shape: string;
  /** Parameter values of that shape. */
  readonly params?: UsePrimitive["params"];
  /** Placement: `p' = R(rotate) * (scale * (p - origin)) + origin + translate`. */
  readonly transform?: UsePrimitive["transform"];
  /** Layer id for this part. Default: the shape id. */
  readonly layer?: string;
}

const vec = v.tuple([v.pipe(v.number(), v.finite()), v.pipe(v.number(), v.finite())]);
const PartSchema = v.strictObject({
  shape: v.pipe(v.string(), v.maxLength(64)),
  params: v.optional(ParamsSchema),
  transform: v.optional(
    v.strictObject({
      translate: v.optional(vec),
      scale: v.optional(v.pipe(v.number(), v.finite(), v.gtValue(0), v.maxValue(4))),
      rotate: v.optional(v.pipe(v.number(), v.finite(), v.minValue(-360), v.maxValue(360))),
      origin: v.optional(vec),
    }),
  ),
  layer: v.optional(
    v.pipe(v.string(), v.regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/, "must be a layer id")),
  ),
});
/** Drop keys whose value is `undefined` (valibot output for absent optional keys). */
function definedOnly<T extends object>(o: T): { [K in keyof T]: Exclude<T[K], undefined> } {
  return Object.fromEntries(Object.entries(o).filter(([, x]) => x !== undefined)) as {
    [K in keyof T]: Exclude<T[K], undefined>;
  };
}

const PartsSchema = v.pipe(v.array(PartSchema), v.minLength(1), v.maxLength(64));

/**
 * Render several catalog shapes placed on one 24 x 24 canvas. Stroke widths and dot radii
 * are not scaled. `options.params` is not used (give each part its own `params`).
 *
 * @throws {DeqError} `INVALID_OPTIONS`, `UNKNOWN_SHAPE` or `INVALID_PARAMETER`.
 */
export function compose(parts: readonly CompositionPart[], options: RenderOptions = {}): string {
  const result = v.safeParse(PartsSchema, parts);
  if (!result.success) {
    const lines = issueLines(result.issues);
    throw new DeqError("INVALID_OPTIONS", `invalid composition: ${lines.join("; ")}`, lines);
  }
  const primitives: UsePrimitive[] = result.output.map((p) => {
    getShape(p.shape);
    const use: UsePrimitive = { type: "use", shape: p.shape, layer: p.layer ?? p.shape };
    return {
      ...use,
      ...(p.params ? { params: p.params } : {}),
      ...(p.transform ? { transform: definedOnly(p.transform) } : {}),
    };
  });
  const layers = [...new Set(primitives.map((p) => p.layer ?? ""))];
  const shape: ShapeData = {
    id: "composition",
    version: 1,
    category: "composition",
    names: {
      en: "Composition",
      ckb: { text: null, status: "none" },
      kmr: { text: null, status: "none" },
    },
    aliases: [],
    tags: [],
    layers,
    symmetry: "none",
    parameters: {},
    primitives,
  };
  return renderShapeData(shape, { ...options, params: {} });
}
