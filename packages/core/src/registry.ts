import { DeqError } from "./errors.js";
import { SHAPES } from "./generated/shapes.js";
import type { ShapeData } from "./types.js";

const BY_ID: ReadonlyMap<string, ShapeData> = new Map(SHAPES.map((s) => [s.id, s]));

/** Levenshtein distance, for "did you mean" hints. */
function distance(a: string, b: string): number {
  let prev = Array.from({ length: b.length + 1 }, (_, j) => j);
  for (let i = 1; i <= a.length; i++) {
    const row = [i];
    for (let j = 1; j <= b.length; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      row.push(Math.min((prev[j] ?? 0) + 1, (row[j - 1] ?? 0) + 1, (prev[j - 1] ?? 0) + cost));
    }
    prev = row;
  }
  return prev[b.length] ?? 0;
}

/** Up to 3 known ids close to `id` (also matching aliases and substrings). */
export function suggest(id: string): string[] {
  const q = id.toLowerCase();
  const scored = SHAPES.map((s) => {
    const names = [s.id, ...s.aliases];
    const best = Math.min(...names.map((n) => (n.includes(q) ? 0 : distance(q, n))));
    return { id: s.id, best };
  });
  const limit = Math.max(2, Math.floor(q.length / 3));
  return scored
    .filter((s) => s.best <= limit)
    .sort((a, b) => a.best - b.best || (a.id < b.id ? -1 : 1))
    .slice(0, 3)
    .map((s) => s.id);
}

/** The shape with this id. Throws `DeqError` (`UNKNOWN_SHAPE`) with suggestions otherwise. */
export function getShape(id: string): ShapeData {
  const shape = typeof id === "string" ? BY_ID.get(id) : undefined;
  if (shape) return shape;
  const label = typeof id === "string" ? JSON.stringify(id.slice(0, 64)) : typeof id;
  const hints = typeof id === "string" ? suggest(id.slice(0, 64)) : [];
  const hint = hints.length > 0 ? ` Did you mean ${hints.join(", ")}?` : "";
  throw new DeqError("UNKNOWN_SHAPE", `unknown shape ${label}.${hint} See listShapes().`);
}

/** True when a shape with this id exists. */
export function hasShape(id: string): boolean {
  return BY_ID.has(id);
}

/** Every shape, in catalog order, optionally only one category. */
export function listShapes(category?: string): readonly ShapeData[] {
  return category === undefined ? SHAPES : SHAPES.filter((s) => s.category === category);
}

/** Category ids in catalog order. */
export function listCategories(): readonly string[] {
  return [...new Set(SHAPES.map((s) => s.category))];
}
