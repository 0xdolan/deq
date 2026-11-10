import type { ParameterDecl, Primitive, ShapeData } from "../src/types.js";

/** A throwaway shape for tests. */
export function shape(
  primitives: readonly Primitive[],
  parameters: Readonly<Record<string, ParameterDecl>> = {},
): ShapeData {
  return {
    id: "test",
    version: 1,
    category: "test",
    names: { en: "Test", ckb: { text: null, status: "none" }, kmr: { text: null, status: "none" } },
    aliases: [],
    tags: [],
    layers: ["a", "b"],
    symmetry: "none",
    parameters,
    primitives,
  };
}
