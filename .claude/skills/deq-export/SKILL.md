---
name: deq-export
description: Export formats and the exporter contract for Deq shapes (SVG, layered SVG, PDF, AI, PSD, PNG, ICO, JSX, Figma). Use when adding or changing an exporter.
---

# Deq exporters

> Phase 0 stub. Phase 4 fills in the API and per-format details.

- Every exporter takes `(shapes[], options)` and preserves named layers where the format supports them.
- Formats: optimised SVG, layered SVG (Inkscape layer groups), sprite, HTML, JSX/TSX, Vue, Svelte, data URI/CSS, PDF (OCG layers), AI (PDF-compatible), PSD (ag-psd), EPS (optional), PNG/JPG/WebP/AVIF, favicon pack, Figma (copy-as-SVG plus plugin), spec JSON. Adobe XD: SVG import only.
- Output is deterministic and contains no scripts or external references.
- Each format needs round-trip tests.
