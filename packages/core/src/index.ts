/**
 * @0xdolan/deq-core: the reference renderer for Deq shapes. Pure ESM, no DOM, no I/O.
 *
 * ```ts
 * import { render, listShapes, compose } from "@0xdolan/deq-core";
 * const svg = render("roj-half-sun", { size: 48, color: "#ED2024" });
 * ```
 *
 * @packageDocumentation
 */
export { DeqError } from "./errors.js";
export type { DeqErrorCode } from "./errors.js";
export { MAX_DEPTH, MAX_FLAT, expand, expandShape, resolveParams } from "./expand.js";
export { escapeXml, num, roundHalfEven } from "./format.js";
export type {
  Flat,
  FlatArc,
  FlatCircle,
  FlatEllipse,
  FlatPath,
  FlatPoly,
  Segment,
} from "./geometry.js";
export { DEFAULT_OPTIONS, resolveOptions } from "./options.js";
export type { RenderOptions, ResolvedOptions } from "./options.js";
export { getShape, hasShape, listCategories, listShapes } from "./registry.js";
export { CANVAS, compose, render, renderShapeData } from "./svg.js";
export type { CompositionPart } from "./svg.js";
export type * from "./types.js";

/** The npm package name. */
export const packageName = "@0xdolan/deq-core" as const;
