/** Render options (PRD §8.1), their defaults and runtime validation. */
import * as v from "valibot";

import { DeqError } from "./errors.js";
import type { Params } from "./types.js";

/**
 * CSS colours accepted in options: hex, named colours, `currentColor`, and the colour
 * functions with plain numeric arguments. `url(...)`, `var(...)` and anything that could
 * reference external content are rejected.
 */
const COLOR =
  /^(?:#[0-9a-fA-F]{3,4}|#[0-9a-fA-F]{6}|#[0-9a-fA-F]{8}|[a-zA-Z]{3,32}|(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\([0-9a-zA-Z.,%/\s+-]{1,64}\))$/;
const LAYER = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const PARAM = /^[a-z][a-zA-Z0-9]*$/;

const color = v.pipe(v.string(), v.maxLength(80), v.regex(COLOR, "must be a CSS colour"));
const unit = v.pipe(v.number(), v.finite(), v.minValue(0), v.maxValue(1));
const text = v.pipe(v.string(), v.maxLength(256));

/** Shape parameter overrides: `{ rays: 9, centerDot: false }`. */
export const ParamsSchema = v.pipe(
  v.record(
    v.pipe(v.string(), v.regex(PARAM, "must be a parameter name")),
    v.union([v.pipe(v.number(), v.finite()), v.boolean(), v.pipe(v.string(), v.maxLength(64))]),
  ),
  v.check((r) => Object.keys(r).length <= 32, "at most 32 parameters"),
);

/** Schema of {@link RenderOptions}. Unknown keys are rejected. */
export const RenderOptionsSchema = v.strictObject({
  size: v.optional(v.pipe(v.number(), v.finite(), v.minValue(1), v.maxValue(8192))),
  color: v.optional(color),
  strokeWidth: v.optional(v.pipe(v.number(), v.finite(), v.minValue(0.05), v.maxValue(12))),
  absoluteStrokeWidth: v.optional(v.boolean()),
  fill: v.optional(v.union([v.literal("none"), color])),
  fillOpacity: v.optional(unit),
  strokeOpacity: v.optional(unit),
  linecap: v.optional(v.picklist(["round", "butt", "square"])),
  linejoin: v.optional(v.picklist(["round", "miter", "bevel"])),
  dotScale: v.optional(v.pipe(v.number(), v.finite(), v.minValue(0.1), v.maxValue(4))),
  rotation: v.optional(v.pipe(v.number(), v.finite(), v.minValue(-3600), v.maxValue(3600))),
  flipX: v.optional(v.boolean()),
  flipY: v.optional(v.boolean()),
  padding: v.optional(v.pipe(v.number(), v.finite(), v.minValue(0), v.maxValue(24))),
  background: v.optional(v.union([v.literal("none"), color])),
  layerColors: v.optional(
    v.pipe(
      v.record(v.pipe(v.string(), v.regex(LAYER, "must be a layer id")), color),
      v.check((r) => Object.keys(r).length <= 64, "at most 64 layer colours"),
    ),
  ),
  title: v.optional(text),
  ariaLabel: v.optional(text),
  params: v.optional(ParamsSchema),
});

/**
 * Options accepted by `render` and `compose`. Every option is optional; see
 * {@link DEFAULT_OPTIONS} for the defaults.
 */
export interface RenderOptions {
  /** Output width and height in px. Default 24. */
  readonly size?: number;
  /** Stroke and dot colour (CSS colour). Default `currentColor`. */
  readonly color?: string;
  /** Stroke width in grid units. Default 2. */
  readonly strokeWidth?: number;
  /** Keep the stroke `strokeWidth` px wide at any `size`. Default false. */
  readonly absoluteStrokeWidth?: boolean;
  /** Fill for closed outlines (circles, polygons, closed paths). Default `none`. */
  readonly fill?: string;
  /** Opacity of `fill`, 0 to 1. Default 1. */
  readonly fillOpacity?: number;
  /** Opacity of the ink (strokes and dots), 0 to 1. Default 1. */
  readonly strokeOpacity?: number;
  /** Default `round`. */
  readonly linecap?: "round" | "butt" | "square";
  /** Default `round`. */
  readonly linejoin?: "round" | "miter" | "bevel";
  /** Multiplies every dot radius. Default 1. */
  readonly dotScale?: number;
  /** Degrees clockwise about the canvas centre. Default 0. */
  readonly rotation?: number;
  /** Mirror left to right. Default false. */
  readonly flipX?: boolean;
  /** Mirror top to bottom. Default false. */
  readonly flipY?: boolean;
  /** Extra space around the 24 x 24 canvas, in grid units. Default 0. */
  readonly padding?: number;
  /** Background colour painted behind the shape, or `none`. Default `none`. */
  readonly background?: string;
  /** Colour per layer id, overriding `color` for that layer. */
  readonly layerColors?: Readonly<Record<string, string>>;
  /** Accessible title. Default: the shape's English name. `""` marks the image decorative. */
  readonly title?: string;
  /** Accessible label. Default: the title. */
  readonly ariaLabel?: string;
  /** Shape parameter values, for example `{ rays: 9 }`. Default: each parameter's default. */
  readonly params?: Params;
}

/** Options after validation, with every default filled in. */
export interface ResolvedOptions {
  readonly size: number;
  readonly color: string;
  readonly strokeWidth: number;
  readonly absoluteStrokeWidth: boolean;
  readonly fill: string;
  readonly fillOpacity: number;
  readonly strokeOpacity: number;
  readonly linecap: "round" | "butt" | "square";
  readonly linejoin: "round" | "miter" | "bevel";
  readonly dotScale: number;
  readonly rotation: number;
  readonly flipX: boolean;
  readonly flipY: boolean;
  readonly padding: number;
  readonly background: string;
  readonly layerColors: Readonly<Record<string, string>>;
  readonly title: string | undefined;
  readonly ariaLabel: string | undefined;
  readonly params: Params;
}

/** The documented default of every option (used by "reset" controls). */
export const DEFAULT_OPTIONS: ResolvedOptions = Object.freeze({
  size: 24,
  color: "currentColor",
  strokeWidth: 2,
  absoluteStrokeWidth: false,
  fill: "none",
  fillOpacity: 1,
  strokeOpacity: 1,
  linecap: "round",
  linejoin: "round",
  dotScale: 1,
  rotation: 0,
  flipX: false,
  flipY: false,
  padding: 0,
  background: "none",
  layerColors: Object.freeze({}),
  title: undefined,
  ariaLabel: undefined,
  params: Object.freeze({}),
});

/** Turn valibot issues into readable lines such as `size: Invalid value`. */
export function issueLines(issues: readonly v.BaseIssue<unknown>[]): string[] {
  return issues.map((issue) => {
    const path = (issue.path ?? []).map((p) => String(p.key)).join(".");
    return path ? `${path}: ${issue.message}` : issue.message;
  });
}

/** Validate `options` and fill in defaults. Throws `DeqError` (`INVALID_OPTIONS`). */
export function resolveOptions(options: unknown = {}): ResolvedOptions {
  const result = v.safeParse(RenderOptionsSchema, options ?? {});
  if (!result.success) {
    const lines = issueLines(result.issues);
    throw new DeqError("INVALID_OPTIONS", `invalid render options: ${lines.join("; ")}`, lines);
  }
  const o = result.output;
  return {
    size: o.size ?? DEFAULT_OPTIONS.size,
    color: o.color ?? DEFAULT_OPTIONS.color,
    strokeWidth: o.strokeWidth ?? DEFAULT_OPTIONS.strokeWidth,
    absoluteStrokeWidth: o.absoluteStrokeWidth ?? DEFAULT_OPTIONS.absoluteStrokeWidth,
    fill: o.fill ?? DEFAULT_OPTIONS.fill,
    fillOpacity: o.fillOpacity ?? DEFAULT_OPTIONS.fillOpacity,
    strokeOpacity: o.strokeOpacity ?? DEFAULT_OPTIONS.strokeOpacity,
    linecap: o.linecap ?? DEFAULT_OPTIONS.linecap,
    linejoin: o.linejoin ?? DEFAULT_OPTIONS.linejoin,
    dotScale: o.dotScale ?? DEFAULT_OPTIONS.dotScale,
    rotation: o.rotation ?? DEFAULT_OPTIONS.rotation,
    flipX: o.flipX ?? DEFAULT_OPTIONS.flipX,
    flipY: o.flipY ?? DEFAULT_OPTIONS.flipY,
    padding: o.padding ?? DEFAULT_OPTIONS.padding,
    background: o.background ?? DEFAULT_OPTIONS.background,
    layerColors: o.layerColors ?? DEFAULT_OPTIONS.layerColors,
    title: o.title,
    ariaLabel: o.ariaLabel,
    params: o.params ?? DEFAULT_OPTIONS.params,
  };
}
