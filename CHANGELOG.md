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
