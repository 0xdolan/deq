/**
 * Deterministic number and text formatting for SVG output. The Python and Rust renderers
 * implement the same rules so golden fixtures match byte for byte (ADR 0008).
 */

/** Round half to even (banker's rounding) on a finite double. */
export function roundHalfEven(v: number): number {
  const f = Math.floor(v);
  const d = v - f;
  if (d > 0.5) return f + 1;
  if (d < 0.5) return f;
  return f % 2 === 0 ? f : f + 1;
}

/**
 * Format a number with at most 3 decimals: `roundHalfEven(x * 1000)` thousandths, printed
 * without trailing zeros, without a leading `+`, and with `-0` as `0`.
 */
export function num(x: number): string {
  const k = roundHalfEven(x * 1000);
  if (k === 0) return "0";
  const sign = k < 0 ? "-" : "";
  const a = Math.abs(k);
  const whole = Math.floor(a / 1000);
  const frac = a % 1000;
  if (frac === 0) return `${sign}${String(whole)}`;
  const digits = String(frac).padStart(3, "0").replace(/0+$/, "");
  return `${sign}${String(whole)}.${digits}`;
}

const ESCAPES: Readonly<Record<string, string>> = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;",
};

// Characters XML 1.0 does not allow, even escaped.
// eslint-disable-next-line no-control-regex
const NOT_XML = /[\u0000-\u0008\u000B\u000C\u000E-\u001F￾￿]/g;

/** Escape text for XML character data and double-quoted attributes; drop invalid characters. */
export function escapeXml(s: string): string {
  return s.replace(NOT_XML, "").replace(/[&<>"']/g, (c) => ESCAPES[c] ?? c);
}
