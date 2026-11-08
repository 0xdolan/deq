# 2. Monorepo and toolchains

- Status: accepted
- Date: 2026-11-08

## Context

The project ships TypeScript, Python and Rust packages that must stay in sync with one shape specification.

## Decision

- One repository with a **pnpm workspace + Turborepo** (TS), a **Cargo workspace** (Rust) and a **uv workspace** (Python).
- Pinned toolchains: Node 24 (`.nvmrc`), pnpm via `packageManager`, Rust via `rust-toolchain.toml` (1.99.1; MSRV 1.85 for edition 2024), Python ≥ 3.12 (dev default 3.14).
- **TypeScript 6.0**, not 7.0: typescript-eslint 8.x supports TypeScript < 6.1 only. Revisit when typescript-eslint supports 7.x.
- `just` is the single task runner; `just ci` mirrors GitHub CI.

## Consequences

Contributors need Node, uv, rustup and just. The Docker `ci` image provides all of them for a clean run.
