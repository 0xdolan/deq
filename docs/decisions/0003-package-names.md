# 3. Package names

- Status: accepted
- Date: 2026-11-08

## Context

`deq` is already taken on npm, PyPI and crates.io, and the npm scope `@deq` belongs to someone else (checked 2026-11-08).

## Decision

| Registry  | Names                                                                                                                                                                                                       |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| npm       | `@0xdolan/deq-core`, `@0xdolan/deq-icons`, `@0xdolan/deq-react`, `@0xdolan/deq-vue`, `@0xdolan/deq-svelte`, `@0xdolan/deq-elements`, `@0xdolan/deq-exporters`, `@0xdolan/deq-generator`, `@0xdolan/deq-cli` |
| PyPI      | `deq-shapes` (import `deq_shapes`)                                                                                                                                                                          |
| crates.io | `deq-shapes` (library), `deq-cli` (binary `deq`)                                                                                                                                                            |

The CLI command is `deq` everywhere.

## Consequences

The `@0xdolan` npm scope is the owner's existing scope. PyPI and crates.io names should be reserved early, at the first release at the latest.
