# Security policy

## Supported versions

Deq is pre-release. Until v1.0.0, only the latest commit on `main` receives security fixes. After v1.0.0, the latest minor release is supported.

## Reporting a vulnerability

Please **do not** open a public issue. Report privately through [GitHub Security Advisories](https://github.com/0xdolan/deq/security/advisories/new).

Include what you found, how to reproduce it, and its impact. You will get an acknowledgement within 7 days and a status update within 14 days. Credit is given in the advisory unless you ask otherwise.

## Scope

In scope: the npm, PyPI and crates.io packages, the CLIs, the fonts, the website and Studio (for example XSS through imported SVG or shared URLs), and the CI/CD workflows.

## How the project stays secure

- Strict typing and input validation in all languages; imported SVG is sanitised.
- GitHub Actions pinned to commit SHAs, least-privilege permissions, checked by actionlint and zizmor.
- Dependency audits (pnpm audit, pip-audit, cargo-deny, OSV-Scanner), Dependabot with a 7-day cooldown, and pnpm's 7-day minimum release age.
- CodeQL, OpenSSF Scorecard, and gitleaks secret scanning on commit and in CI.
- Signed releases with provenance and SBOMs (from the first release).
