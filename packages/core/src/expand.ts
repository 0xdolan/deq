/** Expand a shape (generators, conditions, references) into flat geometry. */
import { DeqError } from "./errors.js";
import * as g from "./geometry.js";
import { getShape } from "./registry.js";
import type { Count, ParamValue, Params, Primitive, ShapeData, UsePrimitive } from "./types.js";

/** Deepest nesting of generators and references. */
export const MAX_DEPTH = 6;
/** Most flat items one render may produce. */
export const MAX_FLAT = 2000;

function fail(where: string, message: string): never {
  throw new DeqError("INVALID_PARAMETER", `${where}: ${message}`);
}

/** Parameter defaults merged with `overrides`, type- and range-checked. */
export function resolveParams(
  shape: ShapeData,
  overrides: Params = {},
): Record<string, ParamValue> {
  const values: Record<string, ParamValue> = {};
  for (const [name, decl] of Object.entries(shape.parameters)) values[name] = decl.default;
  for (const [name, value] of Object.entries(overrides)) {
    if (!Object.hasOwn(shape.parameters, name)) {
      const known = Object.keys(shape.parameters);
      fail(shape.id, `unknown parameter "${name}" (known: ${known.join(", ") || "none"})`);
    }
    values[name] = value;
  }
  for (const [name, decl] of Object.entries(shape.parameters)) {
    const v = values[name];
    if (decl.type === "integer") {
      if (typeof v !== "number" || !Number.isInteger(v)) {
        fail(shape.id, `parameter "${name}" must be an integer`);
      }
      if (v < decl.min || v > decl.max) {
        fail(shape.id, `${name}=${String(v)} is outside ${String(decl.min)}..${String(decl.max)}`);
      }
    } else if (decl.type === "boolean") {
      if (typeof v !== "boolean") fail(shape.id, `parameter "${name}" must be true or false`);
    } else if (typeof v !== "string" || !decl.values.includes(v)) {
      fail(shape.id, `${name}=${JSON.stringify(v)} is not one of ${decl.values.join(", ")}`);
    }
  }
  return values;
}

interface Ctx {
  readonly params: Readonly<Record<string, ParamValue>>;
  readonly transform: g.Transform;
  readonly layer: string;
  readonly depth: number;
  readonly where: string;
  readonly stack: readonly string[];
}

function invalid(ctx: Ctx, message: string): never {
  throw new DeqError("INVALID_SHAPE", `${ctx.where}: ${message}`);
}

function count(value: Count, ctx: Ctx): number {
  const v = typeof value === "number" ? value : ctx.params[value.param];
  if (typeof v !== "number" || !Number.isInteger(v) || v < 0) {
    invalid(ctx, "count must be a non-negative integer");
  }
  return v;
}

function whenMatches(prim: Primitive, ctx: Ctx): boolean {
  for (const [name, expected] of Object.entries(prim.when ?? {})) {
    if (!Object.hasOwn(ctx.params, name)) invalid(ctx, `\`when\` uses unknown parameter "${name}"`);
    const actual = ctx.params[name];
    const options: readonly ParamValue[] = Array.isArray(expected) ? expected : [expected];
    if (!options.some((o) => o === actual)) return false;
  }
  return true;
}

function child(ctx: Ctx, t: g.Transform): Ctx {
  return {
    ...ctx,
    transform: g.chain(t, ctx.transform),
    depth: ctx.depth + 1,
    where: `${ctx.where}.element`,
  };
}

function add(out: g.Flat[], item: g.Flat, ctx: Ctx): void {
  if (out.length >= MAX_FLAT) {
    throw new DeqError(
      "LIMIT_EXCEEDED",
      `${ctx.where}: expands to more than ${String(MAX_FLAT)} items`,
    );
  }
  out.push(g.transformFlat(item, ctx.transform));
}

function expandPrim(prim: Primitive, parent: Ctx, out: g.Flat[]): void {
  if (parent.depth > MAX_DEPTH) {
    throw new DeqError(
      "LIMIT_EXCEEDED",
      `${parent.where}: nested deeper than ${String(MAX_DEPTH)}`,
    );
  }
  if (!whenMatches(prim, parent)) return;
  const layer = prim.layer ?? parent.layer;
  if (!layer) invalid(parent, "no layer");
  const ctx: Ctx = { ...parent, layer };
  switch (prim.type) {
    case "line":
      add(
        out,
        poly(
          [
            [prim.x1, prim.y1],
            [prim.x2, prim.y2],
          ],
          false,
          layer,
          "stroke",
        ),
        ctx,
      );
      break;
    case "polyline":
      add(out, poly(prim.points, false, layer, "stroke"), ctx);
      break;
    case "polygon":
      add(out, poly(prim.points, true, layer, prim.paint ?? "stroke"), ctx);
      break;
    case "rect": {
      const { x, y, width: w, height: h } = prim;
      const pts: g.FlatPoly["points"] = [
        [x, y],
        [x + w, y],
        [x + w, y + h],
        [x, y + h],
      ];
      add(out, poly(pts, true, layer, prim.paint ?? "stroke"), ctx);
      break;
    }
    case "star": {
      const n = count(prim.points, ctx);
      if (n < 2) invalid(ctx, "a star needs at least 2 points");
      const pts = g.starPoints(
        prim.cx,
        prim.cy,
        n,
        prim.outerRadius,
        prim.innerRadius,
        prim.rotation,
      );
      add(out, poly(pts, true, layer, prim.paint ?? "stroke"), ctx);
      break;
    }
    case "circle":
      add(
        out,
        {
          kind: "circle",
          cx: prim.cx,
          cy: prim.cy,
          r: prim.r,
          layer,
          paint: prim.paint ?? "stroke",
          dot: false,
        },
        ctx,
      );
      break;
    case "dot":
      add(
        out,
        {
          kind: "circle",
          cx: prim.cx,
          cy: prim.cy,
          r: prim.r ?? 1,
          layer,
          paint: "fill",
          dot: true,
        },
        ctx,
      );
      break;
    case "arc":
      if (!(prim.start < prim.end && prim.end <= prim.start + 360)) {
        invalid(ctx, "arc needs start < end <= start + 360");
      }
      add(
        out,
        {
          kind: "arc",
          cx: prim.cx,
          cy: prim.cy,
          r: prim.r,
          start: prim.start,
          end: prim.end,
          layer,
          paint: "stroke",
        },
        ctx,
      );
      break;
    case "ellipse":
      add(
        out,
        {
          kind: "ellipse",
          cx: prim.cx,
          cy: prim.cy,
          rx: prim.rx,
          ry: prim.ry,
          rotation: 0,
          layer,
          paint: prim.paint ?? "stroke",
        },
        ctx,
      );
      break;
    case "path":
      add(
        out,
        { kind: "path", segments: g.parsePath(prim.d), layer, paint: prim.paint ?? "stroke" },
        ctx,
      );
      break;
    case "radial": {
      const n = count(prim.count, ctx);
      const stepAngle = n > 1 ? (prim.sweep >= 360 ? prim.sweep / n : prim.sweep / (n - 1)) : 0;
      for (let i = 0; i < n; i++) {
        expandPrim(
          prim.element,
          child(ctx, g.rotate(prim.start + i * stepAngle, prim.center)),
          out,
        );
      }
      break;
    }
    case "repeat": {
      const n = count(prim.count, ctx);
      let dx = 0;
      let dy = 0;
      if (prim.step) {
        [dx, dy] = prim.step;
      } else if (prim.spread) {
        if (n > 1) [dx, dy] = [prim.spread[0] / (n - 1), prim.spread[1] / (n - 1)];
      } else {
        invalid(ctx, "repeat needs step or spread");
      }
      const c = (prim.align ?? "center") === "center" ? (n - 1) / 2 : 0;
      for (let i = 0; i < n; i++) {
        expandPrim(prim.element, child(ctx, g.translate((i - c) * dx, (i - c) * dy)), out);
      }
      break;
    }
    case "concentric": {
      const n = count(prim.count, ctx);
      for (let i = 0; i < n; i++) {
        const s = 1 - i * prim.scaleStep;
        if (s <= 0) invalid(ctx, `copy ${String(i)} would have scale ${s.toFixed(3)}`);
        expandPrim(prim.element, child(ctx, g.scale(s, prim.center)), out);
      }
      break;
    }
    case "use":
      expandUse(prim, ctx, out);
      break;
  }
}

function poly(
  points: g.FlatPoly["points"],
  closed: boolean,
  layer: string,
  paint: g.FlatPoly["paint"],
): g.FlatPoly {
  return { kind: "poly", points, closed, layer, paint };
}

/** The placement transform of a `use`. */
export function useTransform(prim: Pick<UsePrimitive, "transform">): g.Transform {
  const tr = prim.transform ?? {};
  const origin = tr.origin ?? [12, 12];
  let t = g.scale(tr.scale ?? 1, origin);
  if (tr.rotate) t = g.chain(t, g.rotate(tr.rotate, origin));
  const [dx, dy] = tr.translate ?? [0, 0];
  return g.chain(t, g.translate(dx, dy));
}

function expandUse(prim: UsePrimitive, ctx: Ctx, out: g.Flat[]): void {
  if (ctx.stack.includes(prim.shape)) {
    invalid(ctx, `reference cycle ${[...ctx.stack, prim.shape].join(" -> ")}`);
  }
  const target = getShape(prim.shape);
  const params = resolveParams(target, prim.params);
  const t = g.chain(useTransform(prim), ctx.transform);
  target.primitives.forEach((sub, i) => {
    const before = out.length;
    expandPrim(
      sub,
      {
        params,
        transform: t,
        layer: ctx.layer,
        depth: ctx.depth + 1,
        where: `${ctx.where}->${target.id}[${String(i)}]`,
        stack: [...ctx.stack, target.id],
      },
      out,
    );
    // Every part of a referenced shape lands in the layer of the `use`.
    for (let k = before; k < out.length; k++) {
      const item = out[k];
      if (item) out[k] = { ...item, layer: ctx.layer };
    }
  });
}

/** Expand `shape` into flat geometry with the given parameter values. */
export function expandShape(shape: ShapeData, params: Params = {}): g.Flat[] {
  const values = resolveParams(shape, params);
  const out: g.Flat[] = [];
  shape.primitives.forEach((prim, i) => {
    expandPrim(
      prim,
      {
        params: values,
        transform: g.IDENTITY,
        layer: prim.layer ?? "",
        depth: 0,
        where: `${shape.id}.primitives[${String(i)}]`,
        stack: [shape.id],
      },
      out,
    );
  });
  return out;
}

/** Expand the catalog shape `id` into flat geometry. */
export function expand(id: string, params: Params = {}): g.Flat[] {
  return expandShape(getShape(id), params);
}
