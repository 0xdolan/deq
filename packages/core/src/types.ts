/**
 * Types of the shape data shipped with the library. They mirror the render-relevant part of
 * `spec/schema/shape.schema.json`; the spec files are the single source of truth.
 */

/** A point or vector in grid units. */
export type Vec = readonly [number, number];

/** A shape parameter value. */
export type ParamValue = number | boolean | string;

/** Parameter values by name. */
export type Params = Readonly<Record<string, ParamValue>>;

/** A count, either fixed or read from a parameter. */
export type Count = number | { readonly param: string };

/** How a closed primitive is painted. */
export type Paint = "stroke" | "fill";

/** Fields every primitive may carry. */
interface Common {
  readonly id?: string;
  readonly layer?: string;
  /** Draw only when every listed parameter has the value (or one of the values). */
  readonly when?: Readonly<Record<string, ParamValue | readonly (number | string)[]>>;
}

export interface LinePrimitive extends Common {
  readonly type: "line";
  readonly x1: number;
  readonly y1: number;
  readonly x2: number;
  readonly y2: number;
}

export interface PolylinePrimitive extends Common {
  readonly type: "polyline";
  readonly points: readonly Vec[];
}

export interface PolygonPrimitive extends Common {
  readonly type: "polygon";
  readonly points: readonly Vec[];
  readonly paint?: Paint;
}

export interface PathPrimitive extends Common {
  readonly type: "path";
  readonly d: string;
  readonly paint?: Paint;
}

export interface CirclePrimitive extends Common {
  readonly type: "circle";
  readonly cx: number;
  readonly cy: number;
  readonly r: number;
  readonly paint?: Paint;
}

export interface DotPrimitive extends Common {
  readonly type: "dot";
  readonly cx: number;
  readonly cy: number;
  readonly r?: number;
}

export interface ArcPrimitive extends Common {
  readonly type: "arc";
  readonly cx: number;
  readonly cy: number;
  readonly r: number;
  /** Degrees, clockwise on screen from the positive x axis. */
  readonly start: number;
  readonly end: number;
}

export interface EllipsePrimitive extends Common {
  readonly type: "ellipse";
  readonly cx: number;
  readonly cy: number;
  readonly rx: number;
  readonly ry: number;
  readonly paint?: Paint;
}

export interface RectPrimitive extends Common {
  readonly type: "rect";
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
  readonly paint?: Paint;
}

export interface StarPrimitive extends Common {
  readonly type: "star";
  readonly cx: number;
  readonly cy: number;
  readonly points: Count;
  readonly outerRadius: number;
  readonly innerRadius: number;
  readonly rotation: number;
  readonly paint?: Paint;
}

export interface RadialPrimitive extends Common {
  readonly type: "radial";
  readonly count: Count;
  readonly center: Vec;
  readonly start: number;
  readonly sweep: number;
  readonly element: Primitive;
}

export interface RepeatPrimitive extends Common {
  readonly type: "repeat";
  readonly count: Count;
  readonly step?: Vec;
  readonly spread?: Vec;
  readonly align?: "start" | "center";
  readonly element: Primitive;
}

export interface ConcentricPrimitive extends Common {
  readonly type: "concentric";
  readonly count: Count;
  readonly center: Vec;
  readonly scaleStep: number;
  readonly element: Primitive;
}

/** Placement of a referenced shape: `p' = R(rotate) * (scale * (p - origin)) + origin + translate`. */
export interface UseTransform {
  readonly translate?: Vec;
  readonly scale?: number;
  readonly rotate?: number;
  readonly origin?: Vec;
}

export interface UsePrimitive extends Common {
  readonly type: "use";
  readonly shape: string;
  readonly params?: Params;
  readonly transform?: UseTransform;
}

/** One typed element of a shape. */
export type Primitive =
  | LinePrimitive
  | PolylinePrimitive
  | PolygonPrimitive
  | PathPrimitive
  | CirclePrimitive
  | DotPrimitive
  | ArcPrimitive
  | EllipsePrimitive
  | RectPrimitive
  | StarPrimitive
  | RadialPrimitive
  | RepeatPrimitive
  | ConcentricPrimitive
  | UsePrimitive;

/** A shape-specific parameter declaration. */
export type ParameterDecl =
  | {
      readonly type: "integer";
      readonly min: number;
      readonly max: number;
      readonly default: number;
      readonly description: string;
    }
  | { readonly type: "boolean"; readonly default: boolean; readonly description: string }
  | {
      readonly type: "enum";
      readonly values: readonly string[];
      readonly default: string;
      readonly description: string;
    };

/** A Kurdish name. `text` is null until a native speaker has reviewed it. */
export interface KurdishName {
  readonly text: string | null;
  readonly status: string;
}

/** A shape as shipped with the library. */
export interface ShapeData {
  readonly id: string;
  readonly version: number;
  readonly category: string;
  readonly names: {
    readonly en: string;
    readonly ckb: KurdishName;
    readonly kmr: KurdishName;
  };
  readonly aliases: readonly string[];
  readonly tags: readonly string[];
  readonly layers: readonly string[];
  readonly symmetry: string;
  readonly parameters: Readonly<Record<string, ParameterDecl>>;
  readonly primitives: readonly Primitive[];
}
