/** Why an operation failed. */
export type DeqErrorCode =
  "UNKNOWN_SHAPE" | "INVALID_OPTIONS" | "INVALID_PARAMETER" | "INVALID_SHAPE" | "LIMIT_EXCEEDED";

/** The only error type the library throws. `code` is stable; `message` is for people. */
export class DeqError extends Error {
  override readonly name = "DeqError";
  readonly code: DeqErrorCode;
  /** Validation problems, one line each (for `INVALID_OPTIONS`). */
  readonly issues: readonly string[];

  constructor(code: DeqErrorCode, message: string, issues: readonly string[] = []) {
    super(message);
    this.code = code;
    this.issues = issues;
  }
}
