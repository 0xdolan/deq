---
name: deq-i18n
description: Translation and right-to-left rules for Deq (English, Sorani ckb, Kurmanji kmr). Use when adding UI strings or content in any language.
---

# Deq i18n

> Phase 0 stub. Phase 7 adds the catalog format and tooling.

- Locales: `en` (default), `ckb` (Sorani, Arabic script, right-to-left), `kmr` (Kurmanji, Latin script).
- No hard-coded UI strings; all strings live in typed message catalogs. Missing keys fail CI.
- Use CSS logical properties so layouts mirror correctly in RTL.
- AI-drafted translations are marked "needs native review" until a native speaker approves them.
