---
name: deq-content
description: Rules for writing Deq story, history, shape meanings and sources, and for using images and videos. Use when editing content/, the story, or the sources page.
---

# Deq content

> Updated in Phase 1 (research and assets). Phase 10 extends it for the story.

- Every factual sentence cites a source in `content/sources.json` (CSL-JSON). Where sources disagree, say so. Never invent facts.
- Every image has a caption, credit, source URL, and alt text in en, ckb and kmr; record it in `assets/source-manifest.json`. Strip EXIF/GPS metadata.
- Use every processed image in the story. Rename to ASCII kebab-case.
- YouTube: embed via `youtube-nocookie.com` behind a click-to-load facade. Link Instagram; do not embed it.
- The credits page includes a "rights holders: contact us for corrections or removal" note.

## Sources (`content/sources.json`)

- CSL-JSON array. `id` is kebab-case (`<publisher>-<year>`, `yt-<slug>`, `instagram-<handle>`). Set `accessed` to the date you read the page.
- `custom.group`: `articles`, `academic`, `photo-essays`, `video`, `social` or `archives` (the groups on the `/sources` page).
- `custom.status`: `ok`, `archived` (read from Wayback, so set `custom.archiveUrl`), `partial` (metadata only), `blocked` (refused automated access; do not retry or work around it) or `to-verify` (a cited work not yet checked).
- Fetch with an honest user agent (`deq-research/0.1 (+https://github.com/0xdolan/deq)`). Never spoof a browser.
- Research notes live in `docs/research/notes.md`, one cited fact per bullet, with disagreements listed rather than merged.

## Images (`assets/`)

- Originals stay in `temp/images/` (never committed). Process with `uv run deq-assets process`. This writes metadata-free WebP masters (max 2400 px) to `assets/images/<category>/` and animated WebP to `assets/video/`.
- Categories: `story/{historical,ethnographic,contemporary,artists,patterns,documentary}` and `references/shapes`.
- Every file, kept or excluded, has a record in `assets/source-manifest.json`. `uv run deq-assets verify` (in `just test` and CI) checks hashes, metadata, unlisted files and `sourceId`s.
- `attribution`: `confirmed` (found on a cited page that credits it, so a `sourceId` is required), `inferred` (evidence but no match; say what the evidence is in `attributionNote`) or `unknown`. Never upgrade an attribution without new evidence. Never show an inferred credit as confirmed.
- `rights`: `owner-permission` (the owner's statement) or a licence id such as `cc-by-nc-sa-2.0` when the source page states one. Add new licence ids to `RIGHTS` in `scripts/deq-assets/src/deq_assets/manifest.py`, and honour their terms (credit, non-commercial, share-alike) on the site.
- Tag `motifs` with ids from `docs/research/motif-catalog.md`.
- Responsive variants are built with `uv run deq-assets variants` into the gitignored `assets/.generated/`. Never commit them.
- Captions and alt text (en, ckb, kmr) are added with the story (Phase 10).
