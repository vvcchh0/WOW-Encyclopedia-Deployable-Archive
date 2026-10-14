# Offline salvage audit

Only existing local files were read. No network request was made and the original gallery artifacts, maps and provenance were left unchanged.

The audit found `3` HTTP-200 JPEG candidates with CDX digest mismatch among the 20 attempted entities, checked against `87` CDX rows, `14` accepted gallery items and the current export provenance.

| Rank | Path | Memento/origin identity | JPEG decode | SHA-1 in same capture row | Duplicate | Decision |
|---:|---|---|---|---|---|---|
| 4 | `http://www.wow-europe.com/screenoftheday/screenoftheday/10703-14-thumb.jpg` | pass | pass | fail | no | reject |
| 11 | `http://www.wow-europe.com/screenoftheday/screenoftheday/10704-01-thumb.jpg` | pass | pass | fail | no | reject |
| 15 | `http://www.wow-europe.com/screenoftheday/screenoftheday/10703-13-thumb.jpg` | pass | pass | fail | no | reject |

All three candidates have matching local Memento timestamps, original Link metadata, final replay URL, HTTP 200, JPEG magic and complete Pillow decode. Each fails the decisive identity check: its recomputed SHA-1 is absent from the complete CDX table for the same origin/path/capture, and in fact absent from the 87-row table entirely.

The mismatch evidence is concrete:

| Rank | Actual capture | CDX length | Local JPEG length | CDX digest | Recomputed SHA-1 |
|---:|---:|---:|---:|---|---|
| 4 | `20070314035505` | 13285 | 12972 | `ROVAFCCSMC33UBIL53T5Y4V4J3D5SFZQ` | `E2ZYHEDGESFURHKUF7CIV7ZWSICTE2FK` |
| 11 | `20070401235727` | 10078 (also 10077 at `20070401100315`) | 9778 | `WZYOKYPZRRA52FBPN5MCMMQUKVNOWS3P` | `7KWPH4TDEFQGDSDQGVXZND37RLMJQ2U5` |
| 15 | `20070313204814` | 13114 | 12829 | `PTEAGK4HMU4UGD6XJCXCBOX3BJNDWSWT` | `CCM76TVJA6TYF2L5GJFOWZ7DPMXGAUFK` |

`10704-01-thumb.jpg` has two CDX rows for the same path and the same expected digest at different timestamps. Neither row contains the recomputed JPEG digest, so the body cannot be assigned to either capture. Different timestamps or same-name paths cannot repair that mismatch.

The resulting [source-map.json](source-map.json) intentionally contains zero items.
