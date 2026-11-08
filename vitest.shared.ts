import { defineConfig } from "vitest/config";

/** Shared Vitest settings; every package extends this. Coverage gates follow PRD §11. */
export default defineConfig({
  test: {
    include: ["src/**/*.test.ts", "test/**/*.test.ts"],
    coverage: {
      provider: "v8",
      include: ["src/**/*.ts"],
      exclude: ["src/**/*.test.ts"],
      reporter: ["text-summary", "lcov"],
      thresholds: { lines: 95, functions: 95, branches: 90, statements: 95 },
    },
  },
});
