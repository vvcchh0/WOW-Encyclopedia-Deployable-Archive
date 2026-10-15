# Network core pages 3 — sanitized recovery summary

Accepted LOCAL35 reconciliation SHA-256: `81f346c89100204d35448e5c1d20fcfa7532f3e9b7569b5edff2ea1886735016`.
Request window: `2026-10-15T07:40:44.952479+00:00` to `2026-10-15T07:42:40.845497+00:00`; report updated offline: `2026-10-15T07:59:33.708121+00:00`.
Attempts: `21`; source HTTP responses: `18`; failed attempts: `3`; CDX source responses: `11`; replay source responses: `7`; CDX capture-index rows: `292`; normalized eligible rows: `259`; other-origin rows retained as metadata: `21`; selected captures: `8`; corrected preferred candidates: `11`; corrected candidate-only targets: `3`; valid entities: `7`.
Categories: `indexed_candidates_not_replayed` 3, `transport_error` 2, `valid_html` 7.
Disk free before/after: `30301741056` / `30293749760` bytes; stop reason: `batch completed`.

Actual Memento values below come only from valid replay response headers. CDX timestamps and request hints are recorded separately.

| # | target | query original URL | category | CDX HTTP | replay HTTP | corrected candidate | actual Memento | payload bytes | CDX rows | unrequested reason |
|---:|---|---|---|---:|---:|---|---|---:|---:|---|
| 1 | `/news/wow-news2005.html` | `http://www.worldofwarcraft.com/news/wow-news2005.html` | `transport_error` |  |  | `` | `` | 0 | 0 | `no_replay_after_query_transport_error` |
| 2 | `/news/wow-news2004.html` | `http://www.worldofwarcraft.com/news/wow-news2004.html` | `valid_html` | 200 | 200 | `20080402082208` | `2008-04-02T08:22:08+00:00` | 315315 | 39 | `` |
| 3 | `/news/wow-news-06-2005.html` | `http://www.worldofwarcraft.com/news/wow-news-06-2005.html` | `indexed_candidates_not_replayed` | 200 |  | `20080224163853` | `` | 0 | 31 | `replay_deferred_for_parent_decision_after_normalized_cdx_candidate` |
| 4 | `/news/wow-news-07-2005.html` | `http://www.worldofwarcraft.com/news/wow-news-07-2005.html` | `valid_html` | 200 | 200 | `20080224005152` | `2006-03-15T22:54:20+00:00` | 117691 | 17 | `` |
| 5 | `/news/wow-news-08-2005.html` | `http://www.worldofwarcraft.com/news/wow-news-08-2005.html` | `valid_html` | 200 | 200 | `20080212211102` | `2006-03-15T22:53:09+00:00` | 126775 | 14 | `` |
| 6 | `/news/wow-news-09-2005.html` | `http://www.worldofwarcraft.com/news/wow-news-09-2005.html` | `valid_html` | 200 | 200 | `20080218112104` | `2006-03-15T22:48:08+00:00` | 127546 | 19 | `` |
| 7 | `/news/wow-news-10-2005.html` | `http://www.worldofwarcraft.com/news/wow-news-10-2005.html` | `valid_html` | 200 | 200 | `20080215161353` | `2007-09-30T20:11:16+00:00` | 78599 | 21 | `` |
| 8 | `/news/wow-news-11-2005.html` | `http://www.worldofwarcraft.com/news/wow-news-11-2005.html` | `valid_html` | 200 | 200 | `20080221175446` | `2006-03-15T21:53:28+00:00` | 114682 | 31 | `` |
| 9 | `/pvp/battlegrounds/battlegroups.html` | `http://www.worldofwarcraft.com/pvp/battlegrounds/battlegroups.html` | `indexed_candidates_not_replayed` | 200 |  | `20061126175958` | `` | 0 | 6 | `replay_deferred_for_parent_decision_after_normalized_cdx_candidate` |
| 10 | `/burningcrusade/townhall/professions.html` | `http://www.worldofwarcraft.com/burningcrusade/townhall/professions.html` | `indexed_candidates_not_replayed` | 200 |  | `20080112221541` | `` | 0 | 7 | `replay_deferred_for_parent_decision_after_normalized_cdx_candidate` |
| 11 | `/ptr` | `http://www.worldofwarcraft.com/ptr/` | `valid_html` | 200 | 200 | `20080212211107` | `2006-11-10T07:59:27+00:00` | 9100 | 97 | `` |
| 12 | `/wrath/artwork.xml` | `http://www.worldofwarcraft.com/wrath/artwork.xml` | `transport_error` | 200 |  | `20080509123333` | `` | 0 | 10 | `` |

Bodies and original headers/traces remain only below this batch's raw directory. Valid entities are listed in `payload-source-map.json` for review; no entity was copied into the offline mirror.
