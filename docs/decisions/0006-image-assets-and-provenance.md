# 6. Image assets and provenance

- Status: accepted
- Date: 2026-11-08

## Decision

- **Masters plus a build script.** Git holds one master per image: WebP, longest edge at most 2400 px, quality 90, with all metadata (EXIF, GPS, ICC, XMP) stripped. Responsive variants are generated, never committed. That means AVIF, WebP and JPEG at 480, 960, 1600 and 2400 px, plus a 16 px blurred placeholder. They are written to the gitignored `assets/.generated/`.
- **`scripts/deq-assets`**: a private Python tool in the uv workspace, not published. It is held to the same rules as the libraries: mypy strict, Ruff, and coverage of at least 95%. Its subcommands are `inventory`, `process`, `verify`, `variants` and `contact-sheet`. It never follows symlinks, refuses paths that leave the project, and never overwrites a changed file without `--force`. It uses one dependency, Pillow 13.0.0.
- **`assets/source-manifest.json` is the single record of every image.** Each entry holds the original's filename and SHA-256, the master's SHA-256 and size, the category, subject, credit, source and rights, and the motifs it shows. Excluded files (duplicates, archives) are listed with a reason. Running `deq-assets verify` in `just test` and CI fails the build in any of these cases:
  - a master is missing, changed, unlisted or still carries metadata;
  - a `sourceId` is not found in `content/sources.json`.
- **Attribution levels**: `confirmed` means the image was found on a cited page that credits it. `inferred` means there is evidence, but no match. `unknown` means the origin was not found. The owner confirms `inferred` and supplies `unknown` (see `docs/research/image-attribution.md`). A `confirmed` entry needs a `sourceId`.
- **Animations**: the GIF frame folders were rebuilt as animated WebP, at 100 ms per frame, with a poster frame. MP4/WebM output is deferred to the site build (Phase 7+), so that Phase 1 does not depend on ffmpeg.
- **Duplicates** are found by SHA-256 and difference hash (dHash, Hamming distance ≤ 4), then confirmed by eye. Of each set, the largest copy is kept.
- **Archiving**: URL status is recorded in `content/sources.json` (`custom.status`, `custom.archiveUrl`). Nothing was submitted to the Wayback Machine.
- **uv age gate**: `exclude-newer = "7 days"` in the root `pyproject.toml`, the same rule as pnpm's `minimumReleaseAge`. Relocking under the gate moved five dev tools back to their newest release older than 7 days: pip 26.2.2, platformdirs 4.14.3, py-serializable 2.1.0, Ruff 0.17.3 and zizmor 1.31.1.

## Consequences

- The repository stays small (about 14 MB of masters), and the site can generate any size it needs.
- Adding or replacing an image means running `deq-assets process` and committing the master and the manifest together. CI catches a missing step.
- The manifest is written by the tool, so Prettier ignores it.
- The site must show the credit recorded for every image, and must not present `inferred` or `unknown` credits as confirmed.
