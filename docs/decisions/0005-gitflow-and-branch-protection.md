# 5. Gitflow and branch protection

- Status: accepted
- Date: 2026-11-08

## Decision

- `main` (default, released code) and `develop` (integration) are protected: pull request required, required status checks, no force-push, no deletion, rules also apply to admins, conversation resolution required.
- **No required approving reviews**: the project has one maintainer, and GitHub does not allow approving your own PR.
- **No linear-history rule**: gitflow merges `release/*` and `hotfix/*` into `main` with merge commits, and back-merges into `develop`. Feature PRs are squash-merged.
- Tags are annotated `vX.Y.Z` on `main`.

## Consequences

Every change, including the maintainer's, goes through a PR with green CI. Add required reviews if more maintainers join.
