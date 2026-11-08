# 4. Security baseline

- Status: accepted
- Date: 2026-11-08

## Decision

- **GitHub Actions**: every action pinned to a full commit SHA (with the version in a comment); `permissions: {}` at the top level and least privilege per job; `persist-credentials: false`; checked by **actionlint** and **zizmor**.
  - zizmor's `self-repository` rule is disabled: actionlint 1.7.12 does not yet support GitHub's `$/...` syntax for local actions. Revisit when upgrading actionlint.
- **Supply chain**: lockfiles committed and installed with `--frozen-lockfile` / `--frozen` / `--locked`; pnpm `minimumReleaseAge` of 7 days and `onlyBuiltDependencies`; Dependabot with a 7-day cooldown, targeting `develop`.
- **Scanning**: CodeQL (actions, JS/TS, Python, Rust), OpenSSF Scorecard, gitleaks (pre-commit and CI), pnpm audit, pip-audit, cargo-deny, OSV-Scanner (scheduled), dependency review on PRs.
  - **cargo-deny** covers RustSec advisories, so a separate cargo-audit run is not needed.
  - **Trivy** image scanning is deferred until the project publishes a Docker image; the `ci` image is local-only.
  - **minimatch override**: ESLint 10.14 depends on `minimatch@^10`, which is affected by GHSA-g3hv-75wg-m249 and only fixed in 11.x. `pnpm-workspace.yaml` overrides it to 11.0.3 (lint verified). Remove the override once ESLint depends on a patched release.
- **Docker**: base images pinned by digest, tool downloads verified by SHA-256, non-root user, all capabilities dropped, `no-new-privileges`.
- **Commits**: commitlint rejects AI attribution trailers.

## Consequences

Updating an action or image means updating its SHA or digest; Dependabot does this automatically.
