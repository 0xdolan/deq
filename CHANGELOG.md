# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html) with one unified version for all packages.

## [Unreleased]

### Added

- Phase 0 foundation: pnpm + Turborepo, Cargo and uv workspaces with placeholder packages (`@0xdolan/deq-*`, `deq-shapes`, `deq-cli`).
- Strict TypeScript, ESLint, Prettier, Ruff, mypy, rustfmt and clippy configuration.
- Local CI (`just ci`), git hooks (lefthook, commitlint, gitleaks) and a Docker CI image.
- GitHub Actions: CI on Linux, macOS and Windows; CodeQL; OpenSSF Scorecard; scheduled audits; Dependabot.
- pnpm override pinning `minimatch` to 11.0.3 (GHSA-g3hv-75wg-m249) until ESLint ships a patched dependency.
- Project documents: README, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, architecture decision records, AI rules and skills.
- Phase 1 research: bibliography of 34 sources (`content/sources.json`), cited research notes, URL status for every link, and an image attribution review in `docs/research/`.
- 47 images and 2 animations processed into metadata-free WebP masters, recorded with provenance and rights in `assets/source-manifest.json`.
- `scripts/deq-assets`: a private tool to inventory, process, verify and build responsive variants and contact sheets; `deq-assets verify` runs in `just test` and CI.
- Motif catalog with contact sheets (`docs/research/motif-catalog.md`): 45 approved motifs for Phase 2, plus 14 deferred until reference images exist.
- ADR 0006: image assets and provenance.
- Phase 2 shape spec (`spec/`): JSON Schemas for the grid, shapes, catalog and flag; the 24 × 24 grid with keylines; all 45 approved motifs as parametric shapes with layers, construction maths, names (needing native review) and cited metadata.
- The parametric 21-ray Kurdish Sun (`kurdish-sun`), with proportions taken from the flag.
- Flag of Kurdistan spec (`spec/flag.json`): geometry, colours in HEX, RGB, HSL, OKLCH and CMYK (Pantone pending verification), contrast pairs, variants and sizes, checked against the hash-pinned Wikimedia Commons SVG.
- Four symbol-only logo concepts in `assets/brand/concepts/`, shown mono and in flag colours in `docs/design/logo-concepts.svg`; the owner chose concept A, the chin mark.
- `scripts/deq-spec`: a private tool to lint, format, render and draw contact sheets; `deq-spec lint` runs in `just test` and CI.
- Shape spec guide (`docs/design/shape-spec.md`), shapes contact sheet and ADR 0007: shape spec format.
- Three sources: Wikipedia's articles on the flag and the Kurdish Sun, and the Commons flag SVG.

### Changed

- uv now refuses releases younger than 7 days (`exclude-newer`). The relock moved pip, platformdirs, py-serializable, Ruff and zizmor back to their previous releases.
