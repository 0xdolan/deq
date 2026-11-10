/**
 * Flat geometry: what a shape expands to, plus similarity transforms and path parsing.
 * Stroke widths and dot radii are never scaled, so compositions keep a 2-unit stroke.
 */
import { DeqError } from "./errors.js";
import type { Paint, Vec } from "./types.js";

/** `p' = [a c e; b d f] p`, with the uniform scale and the rotation angle it contains. */
export interface Transform {
  readonly a: number;
  readonly b: number;
  readonly c: number;
  readonly d: number;
  readonly e: number;
  readonly f: number;
  readonly scale: number;
  readonly angle: number;
}

export const IDENTITY: Transform = { a: 1, b: 0, c: 0, d: 1, e: 0, f: 0, scale: 1, angle: 0 };

export function apply(t: Transform, p: Vec): Vec {
  return [t.a * p[0] + t.c * p[1] + t.e, t.b * p[0] + t.d * p[1] + t.f];
}

/** The transform that applies `inner` first, then `outer`. */
export function chain(inner: Transform, outer: Transform): Transform {
  const o = outer;
  const s = inner;
  return {
    a: o.a * s.a + o.c * s.b,
    b: o.b * s.a + o.d * s.b,
    c: o.a * s.c + o.c * s.d,
    d: o.b * s.c + o.d * s.d,
    e: o.a * s.e + o.c * s.f + o.e,
    f: o.b * s.e + o.d * s.f + o.f,
    scale: s.scale * o.scale,
    angle: s.angle + o.angle,
  };
}

export function translate(dx: number, dy: number): Transform {
  return { ...IDENTITY, e: dx, f: dy };
}

/** Cosine and sine of `deg` degrees, exact at multiples of 90. */
export function cosSin(deg: number): Vec {
  const m = ((deg % 360) + 360) % 360;
  if (m === 0) return [1, 0];
  if (m === 90) return [0, 1];
  if (m === 180) return [-1, 0];
  if (m === 270) return [0, -1];
  const t = (deg * Math.PI) / 180;
  return [Math.cos(t), Math.sin(t)];
}

/** Rotate clockwise on screen (y points down) by `deg` about `center`. */
export function rotate(deg: number, center: Vec = [0, 0]): Transform {
  const [cos, sin] = cosSin(deg);
  const [cx, cy] = center;
  return {
    a: cos,
    b: sin,
    c: -sin,
    d: cos,
    e: cx - cos * cx + sin * cy,
    f: cy - sin * cx - cos * cy,
    scale: 1,
    angle: deg,
  };
}

export function scale(s: number, center: Vec = [0, 0]): Transform {
  const [cx, cy] = center;
  return { ...IDENTITY, a: s, d: s, e: cx - s * cx, f: cy - s * cy, scale: s };
}

/** A line, polyline or polygon. */
export interface FlatPoly {
  readonly kind: "poly";
  readonly points: readonly Vec[];
  readonly closed: boolean;
  readonly layer: string;
  readonly paint: Paint;
}

/** A circle; `dot` circles are filled and keep their radius under scaling. */
export interface FlatCircle {
  readonly kind: "circle";
  readonly cx: number;
  readonly cy: number;
  readonly r: number;
  readonly layer: string;
  readonly paint: Paint;
  readonly dot: boolean;
}

export interface FlatArc {
  readonly kind: "arc";
  readonly cx: number;
  readonly cy: number;
  readonly r: number;
  readonly start: number;
  readonly end: number;
  readonly layer: string;
  readonly paint: Paint;
}

export interface FlatEllipse {
  readonly kind: "ellipse";
  readonly cx: number;
  readonly cy: number;
  readonly rx: number;
  readonly ry: number;
  readonly rotation: number;
  readonly layer: string;
  readonly paint: Paint;
}

/** A path segment with absolute points. */
export type Segment =
  | readonly ["M", Vec]
  | readonly ["L", Vec]
  | readonly ["Q", Vec, Vec]
  | readonly ["C", Vec, Vec, Vec]
  | readonly ["Z"];

export interface FlatPath {
  readonly kind: "path";
  readonly segments: readonly Segment[];
  readonly layer: string;
  readonly paint: Paint;
}

/** One drawable item in canvas units. */
export type Flat = FlatPoly | FlatCircle | FlatArc | FlatEllipse | FlatPath;

const PATH_TOKEN = /[MLHVCQZ]|-?(?:\d+\.?\d*|\.\d+)/g;
const ARITY: Readonly<Record<string, number>> = { M: 2, L: 2, H: 1, V: 1, Q: 4, C: 6, Z: 0 };

/** Parse absolute `M L H V C Q Z` path data into segments with explicit points. */
export function parsePath(d: string): Segment[] {
  const tokens = d.match(PATH_TOKEN) ?? [];
  if (tokens.join("") !== d.replace(/\s+/g, "") || tokens[0] !== "M") {
    throw new DeqError("INVALID_SHAPE", `unsupported path data: ${JSON.stringify(d)}`);
  }
  const out: Segment[] = [];
  let cur: Vec = [0, 0];
  let start: Vec = cur;
  let i = 0;
  while (i < tokens.length) {
    const cmd = tokens[i] ?? "";
    const n = ARITY[cmd];
    if (n === undefined) {
      throw new DeqError("INVALID_SHAPE", `expected a path command at token ${String(i)}`);
    }
    const nums = tokens.slice(i + 1, i + 1 + n).map(Number);
    if (nums.length !== n || nums.some(Number.isNaN)) {
      throw new DeqError("INVALID_SHAPE", `${cmd} needs ${String(n)} numbers`);
    }
    i += 1 + n;
    const at = (k: number): number => nums[k] ?? 0;
    switch (cmd) {
      case "M":
        cur = start = [at(0), at(1)];
        out.push(["M", cur]);
        break;
      case "L":
        cur = [at(0), at(1)];
        out.push(["L", cur]);
        break;
      case "H":
        cur = [at(0), cur[1]];
        out.push(["L", cur]);
        break;
      case "V":
        cur = [cur[0], at(0)];
        out.push(["L", cur]);
        break;
      case "Q":
        cur = [at(2), at(3)];
        out.push(["Q", [at(0), at(1)], cur]);
        break;
      case "C":
        cur = [at(4), at(5)];
        out.push(["C", [at(0), at(1)], [at(2), at(3)], cur]);
        break;
      default:
        out.push(["Z"]);
        cur = start;
    }
  }
  return out;
}

function transformSegment(seg: Segment, t: Transform): Segment {
  switch (seg[0]) {
    case "M":
      return ["M", apply(t, seg[1])];
    case "L":
      return ["L", apply(t, seg[1])];
    case "Q":
      return ["Q", apply(t, seg[1]), apply(t, seg[2])];
    case "C":
      return ["C", apply(t, seg[1]), apply(t, seg[2]), apply(t, seg[3])];
    default:
      return seg;
  }
}

/** Apply a similarity transform; dot radii and stroke widths stay unscaled. */
export function transformFlat(item: Flat, t: Transform): Flat {
  if (t === IDENTITY) return item;
  switch (item.kind) {
    case "poly":
      return { ...item, points: item.points.map((p) => apply(t, p)) };
    case "circle": {
      const [cx, cy] = apply(t, [item.cx, item.cy]);
      return { ...item, cx, cy, r: item.dot ? item.r : item.r * t.scale };
    }
    case "arc": {
      const [cx, cy] = apply(t, [item.cx, item.cy]);
      const r = item.r * t.scale;
      return { ...item, cx, cy, r, start: item.start + t.angle, end: item.end + t.angle };
    }
    case "ellipse": {
      const [cx, cy] = apply(t, [item.cx, item.cy]);
      return {
        ...item,
        cx,
        cy,
        rx: item.rx * t.scale,
        ry: item.ry * t.scale,
        rotation: item.rotation + t.angle,
      };
    }
    case "path":
      return { ...item, segments: item.segments.map((s) => transformSegment(s, t)) };
  }
}

/** Vertices of a star polygon, outer vertex first at `rotation` degrees. */
export function starPoints(
  cx: number,
  cy: number,
  points: number,
  outer: number,
  inner: number,
  rotation: number,
): Vec[] {
  const out: Vec[] = [];
  for (let k = 0; k < points * 2; k++) {
    const r = k % 2 === 0 ? outer : inner;
    const [cos, sin] = cosSin(rotation + (k * 180) / points);
    out.push([cx + r * cos, cy + r * sin]);
  }
  return out;
}
