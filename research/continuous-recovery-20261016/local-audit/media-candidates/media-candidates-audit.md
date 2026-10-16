# MEDIA/SSOTD candidate audit

- Scope: saved canonical CDX rows only; network requests by this audit: `0`.
- Raw rows: `2082` (`1000 + 1000 + NET-SSOTD-012 terminal 82`); deduplicated rows: `2076` after six exact duplicate row instances.
- Status categories: `{'archive_404': 21, 'redirect': 1971, 'revisit': 47, 'status200_non_image': 41, 'valid_status200_image_index_row': 2}`.
- Temporal buckets: `{'baseline_le_anchor': 10, 'late_2008': 46, 'post_2008': 2026}`; pre-2008 and baseline status-200 image candidates: `0`.
- v17 exclusion scope: `8527` provenance records, `69` image overlays; v15 source manifest: `8357` records.

## Candidate result

**New exact-CDX-supported candidates: 0.** The only two status-200 image rows are the already accepted post-2008 `ss1314.jpg` and `ss1336.jpg`; both match complete v17 route/provenance records and are excluded.

| Original | CDX timestamp/digest | Source body | Route/provenance | Temporal | Pair relation |
|---|---|---|---|---|---|
| `http://www.worldofwarcraft.com/downloads/ssotd/images/screens/ss1314.jpg` | `20100810173046` / `4AKYT7KIDFUKL2OD6WVGY63CXMXIHGF3` | `research/media-screenshots-20261015/wayback-window/raw/07-ssotd_screens_prefix_rows_all.body#350` (SHA `0117cc0e7a4433e8cf030d63208e276ccfad8bd8bb4453c2bccf582bc5b2db46`) | `image_overlay` `research/media-screenshots-20261015/late-image-source-map.json` | `post_2008` | `full` ↔ `http://www.worldofwarcraft.com/downloads/ssotd/images/screens/ss1314-thumb.jpg`; counterpart status-200 image rows: 0 |
| `http://www.worldofwarcraft.com/downloads/ssotd/images/screens/ss1336.jpg` | `20100602102329` / `G7QSOMUMRMS3XPH4YYARXYFK76RTOBHZ` | `research/media-screenshots-20261015/wayback-window/raw/07-ssotd_screens_prefix_rows_all.body#396` (SHA `0117cc0e7a4433e8cf030d63208e276ccfad8bd8bb4453c2bccf582bc5b2db46`) | `image_overlay` `research/media-screenshots-20261015/late-image-source-map.json` | `post_2008` | `full` ↔ `http://www.worldofwarcraft.com/downloads/ssotd/images/screens/ss1336-thumb.jpg`; counterpart status-200 image rows: 0 |

## Accounting

- Raw category conservation: `{'archive_404': 21, 'redirect': 1971, 'revisit': 47, 'status200_non_image': 41, 'valid_status200_image_index_row': 2}`; sum `2082`.
- Raw temporal conservation: `{'baseline_le_anchor': 10, 'late_2008': 46, 'post_2008': 2026}`; sum `2082`.
- Redirect/revisit/index rows are retained as evidence and are never counted as payload recovery.
- NET-SSOTD-012 terminal82 has `valid_payload_entities=0`; no additional replay target is emitted.

## Boundaries

The source page derives a numeric SSOTD range `ss1.jpg` through `ss1340.jpg` at the saved anchor timestamp, using the frozen `startDate` and `ssotd-screenie.js` rules. Numeric slot coverage does not turn a post-2008 capture into a baseline-2008 asset.
