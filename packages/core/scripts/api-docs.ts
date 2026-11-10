/**
 * Generates the API reference `docs/api/core.md` from the public exports of `src/index.ts`
 * and their TSDoc comments, using the TypeScript compiler API.
 *
 *   node scripts/api-docs.ts           write the file
 *   node scripts/api-docs.ts --check   fail if the file is out of date
 */
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import ts from "typescript";

const here = dirname(fileURLToPath(import.meta.url));
const PKG = join(here, "..");
export const API_DOC = join(PKG, "..", "..", "docs", "api", "core.md");

const SIG_FORMAT: ts.TypeFormatFlags =
  ts.TypeFormatFlags.NoTruncation | ts.TypeFormatFlags.UseSingleQuotesForStringLiteralType;
const FORMAT: ts.TypeFormatFlags = SIG_FORMAT | ts.TypeFormatFlags.WriteArrowStyleSignature;

function oneLine(s: string): string {
  return s.replace(/\s+/g, " ").trim();
}

/** Comment text with `{@link X}` written as code. */
function text(parts: ts.SymbolDisplayPart[] | undefined): string {
  return ts
    .displayPartsToString(parts ?? [])
    .replace(/\{@link\s+([^}\s]+)\s*\}/g, "`$1`")
    .trim();
}

/** True when the symbol is declared in this package, not in a TypeScript lib file. */
function ownMember(p: ts.Symbol): boolean {
  return (p.declarations ?? []).some((d) => !d.getSourceFile().fileName.includes("/node_modules/"));
}

function docOf(sym: ts.Symbol, checker: ts.TypeChecker): string {
  const tags = sym
    .getJsDocTags(checker)
    .filter((t) => t.name === "throws" || t.name === "deprecated")
    .map((t) => `**@${t.name}** ${text(t.text)}`);
  return [text(sym.getDocumentationComment(checker)), ...tags].filter(Boolean).join("\n\n");
}

function members(sym: ts.Symbol, checker: ts.TypeChecker): string[] {
  const type = checker.getDeclaredTypeOfSymbol(sym);
  return checker
    .getPropertiesOfType(type)
    .filter((p) => ownMember(p) && p.getName() !== "prototype")
    .map((p) => {
      const decl = p.valueDeclaration ?? p.declarations?.[0];
      const optional = (p.flags & ts.SymbolFlags.Optional) !== 0 ? "?" : "";
      const t = decl
        ? checker.typeToString(checker.getTypeOfSymbolAtLocation(p, decl), undefined, FORMAT)
        : "unknown";
      const doc = oneLine(text(p.getDocumentationComment(checker)));
      return `- \`${p.getName()}${optional}: ${oneLine(t)}\`${doc ? `: ${doc}` : ""}`;
    });
}

/** The Markdown text of the API reference. */
export function generateApiDocs(): string {
  const config = ts.getParsedCommandLineOfConfigFile(
    join(PKG, "tsconfig.build.json"),
    {},
    {
      ...ts.sys,
      onUnRecoverableConfigFileDiagnostic: (d) => {
        throw new Error(ts.flattenDiagnosticMessageText(d.messageText, "\n"));
      },
    },
  );
  if (!config) throw new Error("cannot read tsconfig.build.json");
  const entry = join(PKG, "src", "index.ts");
  const program = ts.createProgram([entry], config.options);
  const checker = program.getTypeChecker();
  const source = program.getSourceFile(entry);
  const moduleSym = source && checker.getSymbolAtLocation(source);
  if (!moduleSym) throw new Error("cannot load src/index.ts");

  const sections = {
    Functions: [] as string[],
    Classes: [] as string[],
    Constants: [] as string[],
    Interfaces: [] as string[],
    Types: [] as string[],
  };
  const exports = checker
    .getExportsOfModule(moduleSym)
    .sort((a, b) => (a.getName() < b.getName() ? -1 : 1));
  for (const exp of exports) {
    const name = exp.getName();
    const sym = exp.flags & ts.SymbolFlags.Alias ? checker.getAliasedSymbol(exp) : exp;
    const doc = docOf(sym, checker);
    const decl = sym.valueDeclaration ?? sym.declarations?.[0];
    if (!decl) continue;
    const block = (sig: string, extra: string[] = []): string =>
      [
        `### \`${name}\``,
        "",
        "```ts",
        sig,
        "```",
        ...(doc ? ["", doc] : []),
        ...(extra.length ? ["", ...extra] : []),
      ].join("\n");
    if (sym.flags & ts.SymbolFlags.Function) {
      const type = checker.getTypeOfSymbolAtLocation(sym, decl);
      const sigs = checker
        .getSignaturesOfType(type, ts.SignatureKind.Call)
        .map((s) => `function ${name}${checker.signatureToString(s, undefined, SIG_FORMAT)}`);
      sections.Functions.push(block(sigs.join("\n")));
    } else if (sym.flags & ts.SymbolFlags.Class) {
      sections.Classes.push(block(`class ${name}`, members(sym, checker)));
    } else if (sym.flags & ts.SymbolFlags.Variable) {
      const t = checker.typeToString(
        checker.getTypeOfSymbolAtLocation(sym, decl),
        undefined,
        FORMAT,
      );
      sections.Constants.push(block(`const ${name}: ${oneLine(t)}`));
    } else if (sym.flags & ts.SymbolFlags.Interface) {
      sections.Interfaces.push(block(`interface ${name}`, members(sym, checker)));
    } else if (sym.flags & ts.SymbolFlags.TypeAlias && ts.isTypeAliasDeclaration(decl)) {
      sections.Types.push(block(`type ${name} = ${oneLine(decl.type.getText())}`));
    }
  }
  const out = [
    "<!-- Generated by packages/core/scripts/api-docs.ts from the TSDoc comments; do not edit. -->",
    "",
    "# `@0xdolan/deq-core` API",
    "",
    "The reference renderer for Deq shapes. Pure ESM, no DOM, no I/O. See the",
    "[package README](../../packages/core/README.md) for an introduction.",
  ];
  for (const [title, blocks] of Object.entries(sections)) {
    if (blocks.length === 0) continue;
    out.push("", `## ${title}`, "", blocks.join("\n\n"));
  }
  return `${out.join("\n")}\n`;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const text = generateApiDocs();
  if (process.argv.includes("--check")) {
    if (readFileSync(API_DOC, "utf8") !== text) {
      console.error(`${API_DOC} is out of date: run \`pnpm --filter @0xdolan/deq-core docs\``);
      process.exit(1);
    }
  } else {
    mkdirSync(dirname(API_DOC), { recursive: true });
    writeFileSync(API_DOC, text);
  }
}
