# Development setup

[← README](../../README.md)

## Tools

| Tool              | Version                                          | Install                                                |
| ----------------- | ------------------------------------------------ | ------------------------------------------------------ |
| Node.js           | 24 (see `.nvmrc`)                                | nvm, fnm, or your package manager                      |
| pnpm              | pinned in `package.json` (`packageManager`)      | `corepack enable`                                      |
| uv                | ≥ 0.13                                           | <https://docs.astral.sh/uv/>                           |
| Python            | ≥ 3.12 (`.python-version` picks the dev default) | `uv python install`                                    |
| Rust              | pinned in `rust-toolchain.toml`                  | rustup: <https://rustup.rs/>                           |
| just              | ≥ 1.40                                           | <https://just.systems/>                                |
| gitleaks          | ≥ 8.28                                           | <https://github.com/gitleaks/gitleaks/releases>        |
| actionlint        | ≥ 1.7                                            | <https://github.com/rhysd/actionlint/releases>         |
| cargo-deny        | ≥ 0.18                                           | <https://github.com/EmbarkStudios/cargo-deny/releases> |
| act (optional)    | ≥ 0.2.80                                         | <https://github.com/nektos/act/releases>               |
| Docker (optional) | with Compose v2                                  | <https://docs.docker.com/>                             |

Verify downloaded binaries against the release's published checksums before installing them.

## First run

```sh
git clone https://github.com/0xdolan/deq.git
cd deq
git switch develop
just setup
just ci
```

## Common tasks

| Command                                                     | What it does                                                                               |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `just ci`                                                   | Everything CI runs: forbidden-file check, lint, typecheck, test, build, audit, secret scan |
| `just lint` / `just typecheck` / `just test` / `just build` | One stage                                                                                  |
| `just fmt`                                                  | Format TS, Python and Rust                                                                 |
| `just audit`                                                | pnpm audit, pip-audit, cargo-deny                                                          |
| `just secrets`                                              | gitleaks on history and source folders                                                     |
| `just docker-ci`                                            | `just ci` inside the pinned Docker image                                                   |
| `just act-ci`                                               | Run the GitHub CI workflow locally with act                                                |

## Git hooks (lefthook)

- **pre-commit**: forbidden files, gitleaks on staged changes, Prettier, ESLint, Ruff, rustfmt, actionlint.
- **commit-msg**: commitlint (Conventional Commits, no AI attribution).
- **pre-push**: typecheck and tests.

## Never commit

`temp/`, `PRD` and `PRD-detailed.md` are gitignored, blocked by a pre-commit hook and checked again in CI.
