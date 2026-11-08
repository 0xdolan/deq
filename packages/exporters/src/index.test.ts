import { describe, expect, it } from "vitest";

import { packageName } from "./index.js";

describe("package stub", () => {
  it("exposes its npm name", () => {
    expect(packageName).toBe("@0xdolan/deq-exporters");
  });
});
