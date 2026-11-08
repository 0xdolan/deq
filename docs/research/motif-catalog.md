# Motif catalog

> **Status: approved for Phase 2** on 2026-11-08. The owner delegated the review to the maintainer agent (PRD §8.2); see [Decisions](#decisions). The owner can reverse any decision before or during Phase 2.

The motifs below were tagged on every image in [`assets/source-manifest.json`](../../assets/source-manifest.json) (the `motifs` field), then grouped into the categories proposed in PRD §8.2.

- **Kurdish names** come only from cited sources. All Sorani names and most Kurmanji names are marked _needs native review_; none were invented.
- **Seen in** lists up to three asset ids. Run `uv run deq-assets contact-sheet --category story/patterns --out sheet.jpg` (any manifest category) to see every image in a category.
- **Named in** lists sources that mention the motif (ids in [`content/sources.json`](../../content/sources.json)). Meanings, with citations, are in [notes.md](notes.md#meanings-of-the-symbols).

## Contact sheets

Each cell is labelled with its asset id.

| Sheet                                             | Images                             |
| ------------------------------------------------- | ---------------------------------- |
| [historical](sheets/historical.jpg)               | Drower, Field and de Morgan plates |
| [patterns](sheets/patterns.jpg)                   | Prints, pendants and motif sheets  |
| [contemporary](sheets/contemporary.jpg)           | Modern deq and artwork             |
| [references-shapes](sheets/references-shapes.jpg) | Shape reference images             |

## `celestial`

| Id               | Motif                                                                    | Kurmanji                            | Sorani              | Seen in                                                                                            | Named in                                              |
| ---------------- | ------------------------------------------------------------------------ | ----------------------------------- | ------------------- | -------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| `roj-half-sun`   | Half sun: an arc or half disc with rays, usually on the forehead or chin | _roj_ [natakallam-2024]             | needs native review | `deq-ttt-temporary-sheet-01`, `deq-ttt-gift-voucher-01`, `fate-temel-portrait-01` (+11 more)       | aljazeera-2023, amargi-2025, kurdistan-chronicle-2026 |
| `roj-sun-circle` | Full sun: a circle or dot disc with rays                                 | _roj_ [natakallam-2024]             | needs native review | `drower-ezidi-tattoo-designs-01`, `field-tattoo-drawings-02`, `field-tattoo-drawings-04` (+2 more) | ozgur-2021 (nine-dot disc), drower-1941               |
| `heyv-crescent`  | Crescent moon                                                            | _heyv_ [natakallam-2024]            | needs native review | `drower-ezidi-tattoo-designs-01`, `field-tattoo-drawings-03`, `field-tattoo-drawings-04` (+1 more) | natgeo-2015, mee-2022, wikipedia-deq                  |
| `sterk-star`     | Star: four to eight points, drawn with lines or dots                     | _stêrin_ (plural) [natakallam-2024] | needs native review | `elu-dot-work-abdomen-01`, `deq-ttt-temporary-sheet-01`, `thesis-motif-table-01` (+6 more)         | sbs-2022, diplomatic-xal                              |

## `nature`

| Id            | Motif                                                 | Kurmanji                             | Sorani              | Seen in                                                                                      | Named in                  |
| ------------- | ----------------------------------------------------- | ------------------------------------ | ------------------- | -------------------------------------------------------------------------------------------- | ------------------------- |
| `tree-branch` | Tree of life: a vertical stem with angled branches    | _rewik_ (plants) [natakallam-2024]   | needs native review | `thesis-motif-table-01`, `hand-drawn-motif-sheets-01`, `field-tattoo-drawings-01` (+7 more)  | ozgur-2021, wikipedia-deq |
| `wheat-arrow` | Wheat ear or arrow: a stem with paired upward strokes | needs native review                  | needs native review | `deq-ttt-temporary-sheet-01`, `hand-drawn-motif-sheets-01`, `tablo-spike-pendant-01`         | —                         |
| `fork`        | Fork or Y form (an inverted fork on the forehead)     | Turkish _ters çatal_ [indyturk-2020] | needs native review | `deq-ttt-temporary-sheet-01`, `thesis-motif-table-01`, `hand-drawn-motif-sheets-01`          | indyturk-2020             |
| `spike`       | Spike: a tall pointed stem                            | needs native review                  | needs native review | `tablo-spike-pendant-01`                                                                     | —                         |
| `ring-stem`   | A small circle on a short stem                        | needs native review                  | needs native review | `field-tattoo-drawings-01`, `field-tattoo-drawings-03`, `field-tattoo-drawings-04` (+2 more) | —                         |

## `geometric`

| Id                 | Motif                                        | Kurmanji            | Sorani              | Seen in                                                                                               | Named in                                                         |
| ------------------ | -------------------------------------------- | ------------------- | ------------------- | ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `cross`            | Plain cross                                  | needs native review | needs native review | `thesis-motif-table-01`, `hand-drawn-motif-sheets-01`, `drower-ezidi-tattoo-designs-01` (+1 more)     | ozgur-2021, wikipedia-deq, kurdistan-chronicle-2026, drower-1941 |
| `cross-dotted`     | Cross with dots in the angles or at the ends | needs native review | needs native review | `drower-ezidi-tattoo-designs-01`, `field-tattoo-drawings-04`, `de-morgan-fig-28-kilakan` (+2 more)    | —                                                                |
| `x-mark`           | Diagonal cross                               | needs native review | needs native review | `field-tattoo-drawings-04`                                                                            | —                                                                |
| `lozenge`          | Diamond                                      | needs native review | needs native review | `elu-dot-work-abdomen-01`, `elu-dot-work-ear-neck-01`, `de-morgan-fig-29-kilakan-kialhours` (+2 more) | wikipedia-deq, kurdistan-chronicle-2026                          |
| `lozenge-nested`   | Nested diamonds                              | needs native review | needs native review | `elu-thigh-pattern-01`                                                                                | —                                                                |
| `triangle-dotted`  | Triangle of lines or dots                    | needs native review | needs native review | `thesis-motif-table-01`, `deq-motifs-animation-01`                                                    | ozgur-2021                                                       |
| `chevron`          | Chevron, or the inverted V on the chin       | needs native review | needs native review | `deq-ttt-temporary-sheet-01`, `thesis-motif-table-01`, `hand-drawn-motif-sheets-01` (+5 more)         | natgeo-2015, mee-2022                                            |
| `chevron-stack`    | Stacked chevrons                             | needs native review | needs native review | `drower-ezidi-tattoo-designs-01`                                                                      | —                                                                |
| `crossed-chevrons` | Two chevrons crossing (a crown-like form)    | needs native review | needs native review | `thesis-motif-table-01`, `zozane-vertical-motif-print-01`, `vertical-motif-stack-01` (+2 more)        | amargi-2025 (crown), deq-ttt-archive (_taç_)                     |
| `comb`             | Comb or rake: a bar with parallel teeth      | needs native review | needs native review | `deq-ttt-temporary-sheet-01`, `deq-ttt-gift-voucher-01`, `thesis-motif-table-01` (+4 more)            | aljazeera-2023, amargi-2025, drower-1941                         |
| `ladder`           | Ladder: two rails with rungs                 | needs native review | needs native review | `thesis-motif-table-01`, `fatma-arik-ladder-hands-01`                                                 | aljazeera-2023                                                   |
| `spindle`          | Spindle                                      | needs native review | needs native review | `drower-ezidi-tattoo-designs-01`                                                                      | drower-1941                                                      |
| `dimlich`          | _Dimlich_, as captioned by Drower            | needs native review | needs native review | `drower-ezidi-tattoo-designs-01`                                                                      | drower-1941                                                      |

## `dots`

| Id             | Motif                                         | Kurmanji            | Sorani              | Seen in                                                                                            | Named in                                |
| -------------- | --------------------------------------------- | ------------------- | ------------------- | -------------------------------------------------------------------------------------------------- | --------------------------------------- |
| `dot`          | Single dot (for example between the eyebrows) | needs native review | needs native review | `drower-ezidi-tattoo-designs-01`, `field-tattoo-drawings-02`                                       | wikipedia-deq                           |
| `dot-trio`     | Three dots in a triangle                      | needs native review | needs native review | `deq-ttt-temporary-sheet-01`, `elu-dot-trio-temple-01`, `drower-ezidi-tattoo-designs-01` (+3 more) | aljazeera-2023, amargi-2025, ozgur-2021 |
| `dot-row`      | A row of dots                                 | needs native review | needs native review | `elu-dot-work-abdomen-01`, `elu-thigh-pattern-01`                                                  | —                                       |
| `dot-quincunx` | Five dots, as on a die                        | needs native review | needs native review | `elu-dot-work-abdomen-01`                                                                          | —                                       |
| `dot-rosette`  | Dots in a ring around a centre dot            | needs native review | needs native review | `elu-dot-work-ear-neck-01`, `deq-motifs-animation-01`                                              | —                                       |
| `dot-cluster`  | A free grid or cluster of dots                | needs native review | needs native review | `elu-dot-work-ear-neck-01`, `field-tattoo-drawings-01`, `de-morgan-fig-28-kilakan` (+3 more)       | —                                       |

## `lines-and-borders`

| Id            | Motif                                             | Kurmanji            | Sorani              | Seen in                                                                        | Named in |
| ------------- | ------------------------------------------------- | ------------------- | ------------------- | ------------------------------------------------------------------------------ | -------- |
| `zigzag`      | Zig-zag (water) line                              | needs native review | needs native review | `thesis-motif-table-01`                                                        | —        |
| `arrow-row`   | A row of arrowheads or chevrons used as a band    | needs native review | needs native review | `deq-ttt-temporary-sheet-01`, `elu-thigh-pattern-01`, `tablo-spike-pendant-01` | —        |
| `band-border` | Bracelet or band border around the wrist or ankle | needs native review | needs native review | `field-tattoo-drawings-04`, `de-morgan-fig-29-kilakan-kialhours`               | —        |

## `human-and-animal`

| Id                | Motif                                    | Kurmanji                           | Sorani              | Seen in                          | Named in                                    |
| ----------------- | ---------------------------------------- | ---------------------------------- | ------------------- | -------------------------------- | ------------------------------------------- |
| `gazelle`         | Gazelle                                  | _xezal_ [natakallam-2024]          | needs native review | `drower-ezidi-tattoo-designs-01` | dailysabah-2016, wikipedia-deq, amargi-2025 |
| `fish`            | Fish                                     | needs native review                | needs native review | `tablo-fish-pendant-01`          | image caption (@tablo.chn)                  |
| `sandgrouse-foot` | Sandgrouse foot                          | needs native review                | needs native review | `drower-ezidi-tattoo-designs-01` | drower-1941, wikipedia-deq                  |
| `doll`            | Doll: a simple human figure              | _bûkoke_ (dolls) [natakallam-2024] | needs native review | `drower-ezidi-tattoo-designs-01` | drower-1941, wikipedia-deq                  |
| `darwish`         | _Darwish_ figure, as captioned by Drower | needs native review                | needs native review | `drower-ezidi-tattoo-designs-01` | drower-1941                                 |

## `compositions`

| Id                     | Motif                                                  | Kurmanji            | Sorani              | Seen in                                                                                                   | Named in                                 |
| ---------------------- | ------------------------------------------------------ | ------------------- | ------------------- | --------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| `chin-composition`     | Traditional chin layout (chevron, dots, vertical stem) | needs native review | needs native review | `de-morgan-fig-27-tchomaklou`, `de-morgan-fig-28-kilakan`, `fate-temel-portrait-01` (+10 more)            | natgeo-2015, mee-2022                    |
| `forehead-composition` | Traditional forehead layout (sun, fork, dots)          | needs native review | needs native review | `de-morgan-fig-27-tchomaklou`, `de-morgan-fig-28-kilakan`, `aljazeera-framed-elder-portrait-01` (+7 more) | indyturk-2020                            |
| `hand-composition`     | Back-of-hand and finger layout                         | needs native review | needs native review | `elder-man-tattooed-hands-01`, `field-tattoo-drawings-02`, `field-tattoo-drawings-03` (+10 more)          | —                                        |
| `foot-composition`     | Foot and ankle layout                                  | needs native review | needs native review | `field-tattoo-drawings-01`                                                                                | —                                        |
| `vertical-stack`       | A vertical stack of motifs (neck to chest, or a print) | needs native review | needs native review | `natakallam-symbols-of-nature-01`, `zozane-vertical-motif-print-01`, `vertical-motif-stack-01`            | ozgur-2021 (tree of life, neck to chest) |
| `circle-over-comb`     | A circle above a comb                                  | needs native review | needs native review | `deq-motifs-animation-01`                                                                                 | —                                        |
| `drower-union`         | The 'common union of symbols' on Drower's plate        | needs native review | needs native review | `drower-ezidi-tattoo-designs-01`                                                                          | drower-1941                              |

## `kurdish-symbols`

| Id             | Motif                                                             | Kurmanji            | Sorani              | Seen in  | Named in                                     |
| -------------- | ----------------------------------------------------------------- | ------------------- | ------------------- | -------- | -------------------------------------------- |
| `kurdish-sun`  | Kurdish Sun with 21 rays (PRD §8.3), parameter `rays`             | _roj_               | needs native review | none yet | wikipedia (flag article), to cite in Phase 2 |
| `kurdish-flag` | Flag of Kurdistan, 2:3, from the Wikimedia Commons SVG (PRD §8.3) | needs native review | needs native review | none yet | Wikimedia Commons, to cite in Phase 2        |

## Named in sources but not seen in any image

**Deferred:** these motifs stay on the list but are not drawn until there is a reference image (from the owner or a cited source). Drawing them from a written name alone would invent a form that no source shows.

| Id                  | Kurmanji                              | Named in                                                         |
| ------------------- | ------------------------------------- | ---------------------------------------------------------------- |
| `snake`             | _marin_ (snakes) [natakallam-2024]    | natakallam-2024, diplomatic-xal, ozgur-2021 (men)                |
| `peacock`           | needs native review                   | hilton-tattooed-women, dailysabah-2016, diplomatic-xal           |
| `scorpion`          | needs native review                   | ozgur-2021 (men)                                                 |
| `scissors`          | _meqes_ / _cawbirr_ [natakallam-2024] | natakallam-2024                                                  |
| `millipede`         | needs native review                   | dailysabah-2016                                                  |
| `mirror`            | needs native review                   | amargi-2025                                                      |
| `rebab`             | needs native review                   | amargi-2025                                                      |
| `eye`               | needs native review                   | dailysabah-2016                                                  |
| `bird`              | needs native review                   | ozgur-2021                                                       |
| `octagon`           | needs native review                   | ozgur-2021                                                       |
| `square`            | needs native review                   | ozgur-2021                                                       |
| `divided-rectangle` | needs native review                   | ozgur-2021                                                       |
| `daqqayeh`          | needs native review                   | drower-1941, wikipedia-deq (on the Drower plate, not yet tagged) |
| `res-daqq`          | needs native review                   | drower-1941, wikipedia-deq (on the Drower plate, not yet tagged) |

Özgür Politika also names a pistol and a sword among men's tattoos [ozgur-2021]. They are not in the catalog: only one source names them, and no image shows them. They stay in the research notes.

## Count and the Phase 2 target

This draft has 43 motifs tagged on images (7 of them compositions), 2 Kurdish symbols from PRD §8.3, and 14 motifs named only in sources. That is 59 candidates in all. PRD §8.2 targets at least 60 base shapes in v1.0, plus parametric variants (for example ray count, dot count and stroke). The Phase 2 spec will turn the approved list into shapes, with variants such as dot counts or nesting depth, and with compositions built by reference from base shapes.

## Decisions

Made on 2026-11-08 on the owner's behalf, at their request.

1. **Motifs:** all 43 tagged motifs and the 2 Kurdish symbols are approved as listed, with no renames or merges. Phase 2 can still merge two motifs if their geometry turns out to be the same shape with a different parameter (for example `chevron` and `chevron-stack`).
2. **Categories:** the eight categories proposed in PRD §8.2 are kept.
3. **Source-only motifs:** the 14 are deferred until a reference image exists. They are not drawn from their names alone.
4. **Pistol and sword:** left out (see above).
5. **Kurdish names:** still open. Every Sorani name, and every Kurmanji name not given by a source, stays marked _needs native review_ until a native speaker checks it. No name will be invented.
6. **Phase 2 target:** 45 drawable base shapes (43 motifs and the 2 symbols), with parametric variants (ray count, dot count, nesting depth, stroke). The PRD target of at least 60 base shapes applies to v1.0, and the deferred motifs are the path to it as reference images arrive.
