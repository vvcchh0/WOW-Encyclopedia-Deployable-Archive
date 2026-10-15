# Three gallery local plan

Generated `2026-10-15T11:28:50.477265Z` with `network_requests=0`. Scope is Black Temple, Serpentshrine Cavern, and Magister's Terrace. Karazhan, Fishing, and the Zul'Aman wrapper are excluded.

## Matrix

| gallery | route | shots | source addshots | expected entities | manifest full/thumb | provenance full/thumb | prior prefix evidence | final addshots |
|---|---|---:|---|---:|---:|---:|---|---|
| Black Temple | `/info/dungeons/black-temple-gallery.html` | 48 | `/info/dungeons/images/blacktemple/` `ss` | 96 | 0/0 | 0/0 | `not_checked` | `/WOW-Encyclopedia-Deployable-Archive/info/dungeons/images/blacktemple/` |
| Serpentshrine Cavern | `/info/dungeons/serpentshrine-gallery.html` | 29 | `/info/dungeons/images/serpentshrine/` `ss` | 58 | 0/0 | 0/0 | `not_checked` | `/WOW-Encyclopedia-Deployable-Archive/info/dungeons/images/serpentshrine/` |
| Magister's Terrace | `/info/dungeons/magisters-terrace-gallery.html` | 47 | `/info/dungeons/images/magisters/` `ss` | 94 | 0/0 | 0/0 | `not_checked` | `/WOW-Encyclopedia-Deployable-Archive/info/dungeons/images/magisters/` |

All three source page payloads and v10 derived/final export HTML files are hash-recorded in JSON. The source page capture timestamp and source/derived SHA are retained per row. The shared JS rule is recorded with its actual v10 file SHA and lines 471-487/506-507.

## Exact prefix proposals

- **Black Temple**: `http://www.worldofwarcraft.com/info/dungeons/images/blacktemple/`; `matchType=prefix`, `statuscode:200`, `mimetype=image/*`, `collapse=digest`; proposed window `20060101000000`–`20081231235959`. This is a query proposal, not capture evidence.
- **Serpentshrine Cavern**: `http://www.worldofwarcraft.com/info/dungeons/images/serpentshrine/`; `matchType=prefix`, `statuscode:200`, `mimetype=image/*`, `collapse=digest`; proposed window `20060101000000`–`20081231235959`. This is a query proposal, not capture evidence.
- **Magister's Terrace**: `http://www.worldofwarcraft.com/info/dungeons/images/magisters/`; `matchType=prefix`, `statuscode:200`, `mimetype=image/*`, `collapse=digest`; proposed window `20060101000000`–`20081231235959`. This is a query proposal, not capture evidence.

## Findings and limits

The three galleries contain 124 slots and 248 expected direct full/thumb entities. Current v10 manifest and export provenance contain zero direct full and zero direct thumbnail records for all three prefixes. The explicitly inspected old evidence covers only Karazhan/Fishing, so these three prefixes remain `not_checked`; no absence claim is made.

The current final export has `3` localized addshots directories and `0` missing.html addshots directories for these three pages. This is a static export-path observation only. The direct screenshot entities remain absent from current manifest/provenance.

No production, source, ledger, export, or frozen baseline file was changed. No full URL enumeration was performed.
