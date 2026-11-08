# Deq task runner. `just ci` runs the same checks as GitHub CI.
set shell := ["bash", "-euo", "pipefail", "-c"]

# List recipes
default:
    @just --list

# Install all dependencies from lockfiles and enable git hooks
setup:
    pnpm install --frozen-lockfile
    uv sync --frozen
    pnpm exec lefthook install

# Run every CI check locally
ci: forbidden lint typecheck test build audit secrets

# Format all code
fmt:
    pnpm format
    uv run ruff format
    uv run ruff check --fix
    cargo fmt --all

# Lint and format checks (TS, Python, Rust, GitHub workflows)
lint:
    pnpm lint
    pnpm format:check
    uv run ruff check
    uv run ruff format --check
    cargo fmt --all --check
    cargo clippy --workspace --all-targets --locked -- -D warnings
    actionlint
    uv run zizmor --offline .github

# Type checks
typecheck:
    pnpm typecheck
    uv run mypy

# Unit tests with coverage gates
test:
    pnpm test
    uv run pytest
    uv run deq-assets verify
    cargo test --workspace --locked

# Build all packages
build:
    pnpm build
    cargo build --workspace --locked
    uv build --all-packages --out-dir target/python-dist --quiet

# Dependency audits (npm, PyPI, crates)
audit:
    pnpm audit --audit-level moderate
    uv run pip-audit --skip-editable --progress-spinner off
    cargo deny check

# Scan git history and the working tree for secrets
secrets:
    gitleaks git --redact --no-banner .
    gitleaks dir --redact --no-banner packages python rust scripts docs .github spec content assets

# Fail if files that must never be committed are tracked or staged
forbidden:
    #!/usr/bin/env bash
    set -euo pipefail
    bad=$( { git ls-files; git diff --cached --name-only; } | grep -E '^(temp/|PRD$|PRD-detailed\.md$)' || true)
    if [[ -n "$bad" ]]; then echo "Forbidden files tracked or staged:"; echo "$bad"; exit 1; fi
    echo "forbidden: ok"

# Run CI in a clean Docker container
docker-ci:
    docker compose run --rm --build ci

# Run the GitHub Actions CI workflow locally with act
act-ci:
    act pull_request -W .github/workflows/ci.yml
