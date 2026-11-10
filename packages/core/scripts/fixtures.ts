/**
 * Writes the golden fixtures to `spec/fixtures/` from the built library (`dist/`, so run
 * `tsc -p tsconfig.build.json` first; the `fixtures` package script does).
 *
 *   node scripts/fixtures.ts           write (and remove stale SVGs)
 *   node scripts/fixtures.ts --check   fail if any fixture is missing, stale or extra
 */
import { mkdirSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import type * as Core from "../src/index.ts";
import { fixtureCases, manifest, renderCase } from "./fixture-cases.ts";
import { readText } from "./generate-shapes.ts";

/** The built library; a computed specifier so typechecking does not need `dist/`. */
const DIST: string = new URL("../dist/index.js", import.meta.url).href;
const { compose, listShapes, render } = (await import(DIST)) as typeof Core;

const here = dirname(fileURLToPath(import.meta.url));
const OUT = join(here, "..", "..", "..", "spec", "fixtures");
const SUBDIRS = ["shapes", "params", "options", "compose"];

const check = process.argv.includes("--check");
const cases = fixtureCases(listShapes());
const expected = new Map<string, string>([["manifest.json", manifest(cases)]]);
for (const c of cases) expected.set(c.file, renderCase(c, { render, compose }));

function existing(): string[] {
  const out: string[] = [];
  for (const sub of SUBDIRS) {
    let names: string[];
    try {
      names = readdirSync(join(OUT, sub));
    } catch {
      continue;
    }
    for (const n of names) if (n.endsWith(".svg")) out.push(`${sub}/${n}`);
  }
  return out;
}

function read(path: string): string | undefined {
  try {
    return readText(path, 1024 * 1024);
  } catch (err) {
    if ((err as NodeJS.ErrnoException).code === "ENOENT") return undefined;
    throw err;
  }
}

const problems: string[] = [];
for (const rel of existing()) {
  if (expected.has(rel)) continue;
  if (check) problems.push(`extra: ${rel}`);
  else rmSync(join(OUT, rel));
}
for (const [rel, text] of expected) {
  const path = join(OUT, rel);
  const current = read(path);
  if (current === text) continue;
  if (check) {
    problems.push(`${current === undefined ? "missing" : "stale"}: ${rel}`);
  } else {
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(path, text);
  }
}
if (problems.length > 0) {
  console.error(
    `${problems.slice(0, 20).join("\n")}\nrun \`pnpm --filter @0xdolan/deq-core fixtures\``,
  );
  process.exit(1);
}
console.log(`${String(cases.length)} fixtures ${check ? "up to date" : "written"}`);
