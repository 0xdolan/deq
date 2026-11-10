import { readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { API_DOC, generateApiDocs } from "../scripts/api-docs.ts";
import { fixtureCases, manifest, renderCase } from "../scripts/fixture-cases.ts";
import { OUT_FILE, SPEC_DIR, generateShapes } from "../scripts/generate-shapes.ts";
import { compose, listShapes, render } from "../src/index.js";

const FIXTURES = join(SPEC_DIR, "fixtures");
const cases = fixtureCases(listShapes());

describe("generated data", () => {
  it("src/generated/shapes.ts matches spec/ (run `pnpm --filter @0xdolan/deq-core generate`)", () => {
    expect(readFileSync(OUT_FILE, "utf8")).toBe(generateShapes());
  });
});

describe("golden fixtures (run `pnpm --filter @0xdolan/deq-core fixtures` after a change)", () => {
  it("manifest lists every case", () => {
    expect(readFileSync(join(FIXTURES, "manifest.json"), "utf8")).toBe(manifest(cases));
    expect(new Set(cases.map((c) => c.name)).size).toBe(cases.length);
  });
  it.each(cases.map((c) => [c.name, c] as const))("%s", (_name, c) => {
    expect(renderCase(c, { render, compose })).toBe(readFileSync(join(FIXTURES, c.file), "utf8"));
  });
});

describe("API reference", () => {
  it("docs/api/core.md matches the TSDoc comments (run `pnpm --filter @0xdolan/deq-core docs`)", () => {
    expect(readFileSync(API_DOC, "utf8")).toBe(generateApiDocs());
  }, 30_000);
});
