// @ts-check
import { RuleConfigSeverity } from "@commitlint/types";

const AI_ATTRIBUTION = /co-authored-by:.*(claude|anthropic)|generated with .*claude/i;

/**
 * Owner rule: commits must never carry AI attribution.
 * @type {import("@commitlint/types").Rule}
 */
const noAiAttribution = (parsed) => {
  const raw = parsed["raw"];
  const text = typeof raw === "string" ? raw : "";
  return [!AI_ATTRIBUTION.test(text), "Commit messages must not contain AI attribution."];
};

/** @type {import("@commitlint/types").UserConfig} */
export default {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "no-ai-attribution": [RuleConfigSeverity.Error, "always"],
  },
  plugins: [{ rules: { "no-ai-attribution": noAiAttribution } }],
};
