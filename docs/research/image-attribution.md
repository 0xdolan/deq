# Image attribution review

Every image and animation in [`assets/source-manifest.json`](../../assets/source-manifest.json) has one of three attribution levels:

- `confirmed`: the image appears on a cited source page, and that page names who made it.
- `inferred`: there is strong evidence (a filename, a caption, a watermark, a site's media id), but the image was not matched on a fetched page.
- `unknown`: the origin was not found.

Totals: 49 assets. 23 confirmed, 16 inferred, 10 unknown.

Every asset has the rights value `owner-permission`, based on the owner's statement that they may use these images. The site must still show each credit as recorded here (PRD §8.12).

## Confirmed

| Credit                        | Images | Source id                |
| ----------------------------- | ------ | ------------------------ |
| Jaclynn Ashly / Al Jazeera    | 15     | aljazeera-2023           |
| Elu (deq-ttt), via NaTakallam | 6      | natakallam-2024          |
| Kurdistan Chronicle           | 2      | kurdistan-chronicle-2026 |

## Inferred: please confirm or correct

Is this credit right? If you know the publication, page or licence, add it.

| Id                                   | Category           | Current credit                                   | Evidence                                                                                                                         | Original filename                                             |
| ------------------------------------ | ------------------ | ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| `elder-man-tattooed-hands-01`        | story/ethnographic | Unknown Flickr photographer (photo 18573478922)  | Filename is a Flickr download (photo id 18573478922); photographer and licence not yet checked.                                  | `18573478922_a1dc3e0321_k.jpg`                                |
| `deq-ttt-temporary-sheet-01`         | story/artists      | Elu (deq-ttt)                                    | Wix media id prefix 1e3cce_ is the deq-ttt.com site's; this exact image was not found on the fetched pages.                      | `1e3cce_18bc84eb77504f68833cd22330c50e29~mv2.avif`            |
| `deq-ttt-gift-voucher-01`            | story/artists      | Elu (deq-ttt)                                    | Wix media id prefix 1e3cce_ is the deq-ttt.com site's; this exact image was not found on the fetched pages.                      | `1e3cce_4cfb3e86088647a0b7c34ea5ed2bb7ca~mv2.avif`            |
| `drower-ezidi-tattoo-designs-01`     | story/historical   | E. S. Drower (attributed)                        | Plate captioned 'Tattoo designs'; widely shared as Ezidi deq recorded by E. S. Drower. Book, page and plate number not verified. | `Drower_zps83k3mlor.webp`                                     |
| `field-tattoo-drawings-01`           | story/historical   | Henry Field (attributed)                         | Line drawings in the style of Henry Field's body-marking survey; publication and figure not verified.                            | `Field_zpsgv2tgurh.webp`                                      |
| `field-tattoo-drawings-02`           | story/historical   | Henry Field (attributed)                         | Line drawings in the style of Henry Field's body-marking survey; publication and figure not verified.                            | `Field2_zpsacrvbpbh.webp`                                     |
| `field-tattoo-drawings-03`           | story/historical   | Henry Field (attributed)                         | Line drawings in the style of Henry Field's body-marking survey; publication and figure not verified.                            | `Field3_zpsiwk6qnhs.webp`                                     |
| `field-tattoo-drawings-04`           | story/historical   | Henry Field (attributed)                         | Line drawings in the style of Henry Field's body-marking survey; publication and figure not verified.                            | `Field5_zpsfosduqow.webp`                                     |
| `de-morgan-fig-27-tchomaklou`        | story/historical   | Jacques de Morgan, Mission scientifique en Perse | Printed caption: 'Fig. 27. — Tatouages des femmes kurdes de Tchômaklou.' Volume and page not verified.                           | `P54_zps9qweemmm.webp`                                        |
| `de-morgan-fig-28-kilakan`           | story/historical   | Jacques de Morgan, Mission scientifique en Perse | Printed caption: 'Fig. 28. — Tatouages des femmes kurdes de Kilakân.' Volume and page not verified.                              | `P55_zps9bjqeqsm.webp`                                        |
| `de-morgan-fig-29-kilakan-kialhours` | story/historical   | Jacques de Morgan, Mission scientifique en Perse | Printed caption: 'Fig. 29. — Tatouages des femmes kurdes. — Kilakân et Kialhours.' Volume and page not verified.                 | `P56_zpsdasahqgt.webp`                                        |
| `tablo-sun-pendant-01`               | story/patterns     | @tablo.chn (Instagram)                           | Screenshot of an Instagram post by @tablo.chn; the filename is a Reddit image name. The Reddit post was not found.               | `kurdish-deq-kurdish-tattoo-دەقی-کوردی-v0-2ikvqffecfme1.webp` |
| `tablo-spike-pendant-01`             | story/patterns     | @tablo.chn (Instagram)                           | Screenshot of an Instagram post by @tablo.chn; the filename is a Reddit image name. The Reddit post was not found.               | `kurdish-deq-kurdish-tattoo-دەقی-کوردی-v0-80dhf8i5cfme1.webp` |
| `tablo-crown-pendant-01`             | story/patterns     | @tablo.chn (Instagram)                           | Screenshot of an Instagram post by @tablo.chn; the filename is a Reddit image name. The Reddit post was not found.               | `kurdish-deq-kurdish-tattoo-دەقی-کوردی-v0-b7ogizn0cfme1.webp` |
| `tablo-fish-pendant-01`              | story/patterns     | @tablo.chn (Instagram)                           | Screenshot of an Instagram post by @tablo.chn; the filename is a Reddit image name. The Reddit post was not found.               | `kurdish-deq-kurdish-tattoo-دەقی-کوردی-v0-wp9ak3r9cfme1.webp` |
| `kobani-woman-portrait-01`           | story/documentary  | Jodi Hilton (attributed)                         | Filename matches Jodi Hilton's 'tattooed women of Kobani' series; this frame was not matched on the fetched page.                | `tattooed_kobani08.JPG.jpeg`                                  |

## Unknown: please supply the source

Where did this image come from, and who made it? If nobody knows, should it stay out of the story?

| Id                               | Category           | Current credit                  | Evidence                                                                                      | Original filename                                    |
| -------------------------------- | ------------------ | ------------------------------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| `zozane-vertical-motif-print-01` | story/patterns     | Zozane (signature on the print) | Filename is a Redbubble product image; signed 'Zozane'. Shop page not found.                  | `bg,f8f8f8-flat,750x,075,f-pad,750x1000,f8f8f8.webp` |
| `elder-deq-painting-01`          | story/contemporary | Unknown (source not found)      | Generic download filename; artist not found.                                                  | `download (1).jpeg`                                  |
| `elder-man-tattooed-hands-02`    | story/ethnographic | Unknown (source not found)      | Generic download filename; photographer not found.                                            | `download (2).jpeg`                                  |
| `deq-ink-and-hands-01`           | story/ethnographic | Unknown (source not found)      | Generic download filename. Possibly the Daily Sabah ink-mixing photo (not verified).          | `download (3).jpeg`                                  |
| `elder-forehead-chin-deq-03`     | story/ethnographic | Unknown (source not found)      | Generic download filename; a photographer's watermark is visible but unreadable at this size. | `download.jpeg`                                      |
| `vertical-motif-stack-01`        | story/patterns     | Unknown (source not found)      | Generic search-result filename. Similar to the Zozane print but not the same image.           | `images.jpeg`                                        |
| `roj-sun-collage-01`             | story/contemporary | Unknown (source not found)      | Owner-named file; origin not found.                                                           | `roj-deq-001.png`                                    |
| `roj-sun-portrait-01`            | story/contemporary | Unknown (source not found)      | Owner-named file; origin not found.                                                           | `roj-deq-002.jpg`                                    |
| `deq-portraits-slideshow-01`     | story/contemporary | Unknown (source not found)      | ezgif.com frame export; the original GIF and its maker were not found.                        | `ezgif-627e8ef7268e5d6d-jpg`                         |
| `deq-motifs-animation-01`        | references/shapes  | Unknown (source not found)      | ezgif.com frame export; the original GIF and its maker were not found.                        | `ezgif-629ed8354ca14f9f-jpg`                         |

## How to record an answer

Edit the asset in `assets/source-manifest.json`: set `credit`, `attribution`, `attributionNote`, and `sourceId` (add the work to `content/sources.json` first if it is new). Then run `uv run deq-assets verify`. A `confirmed` attribution needs a `sourceId`.
