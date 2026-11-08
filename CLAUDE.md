# Deq: project rules for AI agents

Deq turns traditional Kurdish tattoo (deq) motifs into an open, parametric design system: shape spec, renderers in TS/Python/Rust, exporters, icon packages, fonts, a website with Studio, and a cited cultural story. The full plan is in `PRD-detailed.md` (local only, never committed). Current phase: **0 done** (foundation).

## Hard rules

- **Never commit** `temp/`, `PRD`, `PRD-detailed.md`. They are gitignored, blocked by a pre-commit hook (`just forbidden`) and checked in CI.
- **Attribution**: every commit is authored by `0xdolan <0xdolan@gmail.com>`. Never add Claude, Anthropic or any AI as author or co-author; no "Generated with" lines in commits, PRs, issues, files or release notes. commitlint enforces this.
- **Gitflow**: work on `feature/*` (or `fix/*`, `docs/*`, `chore/*`) off `develop`, PR into `develop` with green CI. `release/x.y.z` and `hotfix/x.y.z` merge into `main` and back into `develop`. Pushing is allowed; ask before force-pushing, deleting branches or tags, publishing packages, or weakening repository settings.
- **Security first**: follow `.claude/skills/deq-security/SKILL.md` for every change.
- **One phase at a time**: implement only the requested phase; ask about anything ambiguous.
- **Keep these rules current**: at the end of each phase or change request, update this file, the skills in `.claude/skills/` and `CHANGELOG.md` (Unreleased).

## Commands

| Task                             | Command                                                                                |
| -------------------------------- | -------------------------------------------------------------------------------------- |
| Install everything, enable hooks | `just setup`                                                                           |
| Full local CI (same as GitHub)   | `just ci`                                                                              |
| Stages                           | `just lint`, `just typecheck`, `just test`, `just build`, `just audit`, `just secrets` |
| Format                           | `just fmt`                                                                             |
| CI in Docker                     | `just docker-ci`                                                                       |

## Layout

- `packages/<name>` → npm `@0xdolan/deq-<name>` (core, icons, react, vue, svelte, elements, exporters, generator, cli). TS 6.0 strict, built with `tsc`, tested with Vitest (coverage ≥ 95% lines).
- `python/deq-shapes` → PyPI `deq-shapes`, import `deq_shapes`. uv workspace, mypy --strict, Ruff, pytest (coverage ≥ 95%).
- `rust/deq-shapes`, `rust/deq-cli` (binary `deq`) → crates.io. Edition 2024, MSRV 1.85, toolchain pinned 1.99.1, `unsafe` forbidden, clippy pedantic, no unwrap/expect/panic.
- `spec/` (single source of truth for shapes, Phase 2+), `apps/site` (Astro site, Phase 7+), `docs/` (guides, ADRs in `docs/decisions/`).
- `.github/actions/setup` is the shared toolchain setup for workflows.

## Conventions

- Conventional Commits (`feat(core): ...`). One unified SemVer version for all packages.
- Actions pinned to full SHAs with a version comment; `permissions: {}` at the top; `persist-credentials: false`.
- Exact dependency versions; pnpm refuses versions younger than 7 days.
- Record decisions as ADRs (`docs/decisions/NNNN-title.md`).
- Generated files carry a "generated, do not edit" header.

## Skills

`deq-security`, `deq-release`, `deq-shape-design`, `deq-export`, `deq-content`, `deq-i18n`, `deq-brand` in `.claude/skills/`.
