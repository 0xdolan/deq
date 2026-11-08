# Phase 1 research

Phase 1 organises and credits the source knowledge and images that Deq builds on (PRD §15).

| File                                                               | Contents                                                                                                            |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| [`content/sources.json`](../../content/sources.json)               | Bibliography (CSL-JSON): 30 sources from the owner's list, 3 referenced works to verify and 1 image source (Flickr) |
| [notes.md](notes.md)                                               | Key facts per story chapter, with citations and disagreements                                                       |
| [`assets/source-manifest.json`](../../assets/source-manifest.json) | Every image and animation, with provenance, credit and rights                                                       |
| [image-attribution.md](image-attribution.md)                       | Attribution review list for the owner (confirmed, inferred, unknown)                                                |
| [motif-catalog.md](motif-catalog.md)                               | Motif catalog and contact sheets (approved for Phase 2)                                                             |

## Method

- Every URL in the owner's link list was fetched once, with an honest user agent (`deq-research/0.1`). Pages that refused automated clients were not retried and not worked around. They are recorded as `blocked`, for the owner to read in a browser.
- Dead or moved pages were read from their Wayback Machine snapshots (`archived`). Nothing was submitted to Save Page Now, by owner decision.
- YouTube: title and channel come from oEmbed. Descriptions and transcripts were not retrieved, so the status is `partial`.
- Instagram: only the public profile header was read, because posts need a login (`partial`). PRD §8.12 says to link Instagram, not embed it.

## URL status

The owner's list has 33 URLs: 31 distinct, mapping to 30 sources (one URL repeats with a `#11` fragment). Status meanings:

- `ok`: read in full.
- `archived`: read from a Wayback snapshot.
- `partial`: metadata only.
- `blocked`: refused automated access (HTTP 403, a login wall, or a robots policy).

No link was found dead.

| #   | URL                                                                                                             | Source id                 | Status                          |
| --- | --------------------------------------------------------------------------------------------------------------- | ------------------------- | ------------------------------- |
| 1   | en.wikipedia.org/wiki/Deq\_(tattoo)                                                                             | wikipedia-deq             | ok                              |
| 2   | dailysabah.com/feature/2016/01/13/deq-a-dying-art-among-turkeys-kurdish-women                                   | dailysabah-2016           | ok                              |
| 3   | kurdistanchronicle.com/babat/4852                                                                               | kurdistan-chronicle-2026  | ok                              |
| 4   | sbs.com.au/…/fate-temels-desire-to-keep-traditional-tattooing-deq-xal-alive/n7e8v4lqw                           | sbs-2022                  | partial (audio not transcribed) |
| 5   | instagram.com/deq.artstudio                                                                                     | instagram-deq-artstudio   | partial                         |
| 6   | australiangeographic.com.au/news/2010/03/oppressed-kurds-express-culture-in-australia                           | ausgeo-2010               | ok                              |
| 7   | web.archive.org/web/20210416140716/…indyturk.com/node/166691/…/kadim-zamanlarin-izi-deq                         | indyturk-2020             | archived                        |
| 8   | middleeasteye.net/discover/middle-east-face-tattoos-traditional-amazigh-bedouin-kurdish                         | mee-2022                  | ok                              |
| 9   | aljazeera.com/features/longform/2023/1/8/deq-the-tattooist-preserving-the-ink-of-a-disappearing-culture         | aljazeera-2023            | ok                              |
| 10  | youtube.com/watch?v=yjRU3eKpGkM                                                                                 | yt-aljazeera-newsfeed     | partial                         |
| 11  | youtube.com/watch?v=8fSC-JO1x4Y                                                                                 | yt-yavuklu-kadim-izler    | partial                         |
| 12  | reddit.com/r/kurdistan/comments/1bjs3mv/kurdish_tattoos_deq                                                     | reddit-kurdistan-deq      | blocked                         |
| 13  | youtube.com/watch?v=Hk3iN5yPgLI                                                                                 | yt-yavuklu-part1          | partial                         |
| 14  | youtube.com/@ahmetyavuklu\_                                                                                     | yt-yavuklu-channel        | partial                         |
| 15  | youtube.com/watch?v=VDlbjuFV_S8                                                                                 | yt-yavuklu-last-marks     | partial                         |
| 16  | youtube.com/watch?v=oVUaLRwh03I                                                                                 | yt-great-big-story        | partial                         |
| 17  | iranicaonline.org/articles/kalkubi                                                                              | iranica-kalkubi           | blocked                         |
| 18  | nationalgeographic.com/photography/article/the-last-tattooed-women-of-kobane                                    | natgeo-2015               | ok                              |
| 19  | jodihilton.com/tattooed-women                                                                                   | hilton-tattooed-women     | ok                              |
| 20  | jodihilton.com/tattooed-women#11 (same page as 19)                                                              | hilton-tattooed-women     | ok                              |
| 21  | dailysabah.com/… (repeat of 2)                                                                                  | dailysabah-2016           | ok                              |
| 22  | deq-ttt.com/deq-archive                                                                                         | deq-ttt-archive           | ok                              |
| 23  | deq-ttt.com                                                                                                     | deq-ttt-home              | ok                              |
| 24  | deq-ttt.com/deq-documentary                                                                                     | deq-ttt-documentary       | ok                              |
| 25  | instagram.com/deq.ttt                                                                                           | instagram-deq-ttt         | partial                         |
| 26  | theamargi.com/posts/deq-a-mesopotamian-tattoo-tradition-revived-in-istanbul                                     | amargi-2025               | ok                              |
| 27  | natakallam.com/blog/deq-kurdish-tattooing                                                                       | natakallam-2024           | ok                              |
| 28  | web.archive.org/web/20191110174048/…diplomaticmagazine.net/culture/1728                                         | diplomatic-xal            | archived                        |
| 29  | web.archive.org/web/20230119235251/…ozgurpolitika.com/haberi-antik-cagdan-gunumuze-ulasan-bir-gelenekdeq-149128 | ozgur-2021                | archived                        |
| 30  | aljazeera.com/… (repeat of 9)                                                                                   | aljazeera-2023            | ok                              |
| 31  | gettyimages.ca/editorial-images/news/event/tattooed-women-of-kobani/775145598                                   | getty-kobani              | blocked                         |
| 32  | pressreader.com/uae/the-national-news/20141109/281676843196541                                                  | pressreader-national-2014 | blocked                         |
| 33  | surprisinglives.net/women-koban-facial-tattooing                                                                | surprisinglives-2015      | ok                              |

Totals across the 30 sources: 14 `ok`, 3 `archived`, 9 `partial`, 4 `blocked`. Every URL is accounted for.

**Owner follow-up:** open the four blocked pages in a browser, and tell us whether the content should change any notes. For Iranica, a copy of the article text is enough.
