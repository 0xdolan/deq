import { describe, expect, it } from "vitest";

import { escapeXml, num, roundHalfEven } from "./format.js";

describe("roundHalfEven", () => {
  it.each([
    [0.5, 0],
    [1.5, 2],
    [2.5, 2],
    [-0.5, 0],
    [-1.5, -2],
    [2.4, 2],
    [2.6, 3],
    [-2.6, -3],
  ])("%d -> %d", (x, want) => {
    expect(roundHalfEven(x)).toBe(want);
  });
});

describe("num", () => {
  it.each([
    [0, "0"],
    [-0, "0"],
    [12, "12"],
    [-3, "-3"],
    [1.5, "1.5"],
    [0.1 + 0.2, "0.3"],
    [16.666666, "16.667"],
    [-0.0004, "0"],
    [-0.0006, "-0.001"],
    [0.0625, "0.062"],
    [5.505, "5.505"],
    [1e-9, "0"],
    [123456.789, "123456.789"],
    [-10.05, "-10.05"],
  ])("%d -> %s", (x, want) => {
    expect(num(x)).toBe(want);
  });
});

describe("escapeXml", () => {
  it("escapes markup characters", () => {
    expect(escapeXml(`a&b<c>"d"'e'`)).toBe("a&amp;b&lt;c&gt;&quot;d&quot;&#39;e&#39;");
  });
  it("drops characters XML cannot hold and keeps tab and newlines", () => {
    expect(escapeXml("a\u0000b\u001Fc￾\td\ne")).toBe("abc\td\ne");
  });
  it("keeps Kurdish text", () => {
    expect(escapeXml("خۆر roj")).toBe("خۆر roj");
  });
});
