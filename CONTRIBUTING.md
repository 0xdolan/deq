# Contributing to Deq

Thank you for helping. This guide covers the workflow; the [development setup](docs/dev/setup.md) covers the tools.

## Ground rules

- Follow the [Code of Conduct](CODE_OF_CONDUCT.md).
- Report security issues privately ([SECURITY.md](SECURITY.md)), never in public issues.
- Every fact, image or video added to the story needs a source.
- Only add images you have the right to share, with full credit.

## Branches (gitflow)

| Branch                                      | Purpose                        | Branches from | Merges into          |
| ------------------------------------------- | ------------------------------ | ------------- | -------------------- |
| `main`                                      | Released code only. Protected. | —             | —                    |
| `develop`                                   | Integration branch. Protected. | `main`        | —                    |
| `feature/<slug>`                            | New work                       | `develop`     | `develop` (PR)       |
| `fix/<slug>`, `docs/<slug>`, `chore/<slug>` | Fixes, docs, maintenance       | `develop`     | `develop` (PR)       |
| `release/x.y.z`                             | Release preparation            | `develop`     | `main` and `develop` |
| `hotfix/x.y.z`                              | Urgent fix to a release        | `main`        | `main` and `develop` |

Pull requests need passing CI. Feature PRs are squash-merged; release and hotfix PRs use merge commits so the history shows each release.

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): summary`, for example `feat(core): add dot primitive`. Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`. A `commit-msg` hook checks this.

## Before you open a PR

```sh
just ci
```

This runs linting, type checks, tests with coverage gates, builds, dependency audits and a secret scan, the same as GitHub CI.

## Code standards

- **TypeScript**: `strict` plus extra checks; no `any`; ESLint `strictTypeChecked`.
- **Python**: `mypy --strict`, Ruff.
- **Rust**: `clippy -D warnings`, `unsafe` forbidden, no `unwrap`/`expect`/`panic` in library code.
- Tests for every change. Coverage gates: TS and Python ≥ 95% lines, Rust ≥ 90%.
- Validate all external input. No `eval`, `new Function` or untrusted `innerHTML`.

## Licensing

By contributing, you agree that your contribution is licensed under [GPL-3.0-or-later](LICENSE).
