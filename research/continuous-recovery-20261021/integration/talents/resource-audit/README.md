# Talent resource audit

Generated `2026-10-21T02:48:22.495988Z` from the existing talent browser receipt. The receipt contains **61 unique HTTP 404 routes from 61 events**: 27 dynamic tree backgrounds and 34 dynamic talent icon requests across 9 classes.

The audit checked the exact URL, `%27` and `%2527` apostrophe forms, lowercase route form, v41 `route-map.json`, v41 `export-provenance.json`, both manifests' original URL indexes/aliases, the Source15 build manifest/site, and the tracked `offline` manifest/site. It scanned only the three `shared/global/talents` subtrees for local files. It did not use the network or inspect historical ZIP contents.

Results are in `resource-audit.json` (full evidence) and `resource-audit.csv` (one row per unique route). Each row separates the missing image payload record from the Source15 script lines that construct the request. A `source-script-only-no-image-record` row has no exact image bytes or manifest row available locally; the script evidence is not an image source record.

Counts: `{'source-script-only-no-image-record': 61}`. Exact v41 files: `0`. Exact Source15/offline files: `0`. Route-map/alias matches: `0`. Manifest original URL/alias matches: `0`. Same-normalized-name candidates in the same talent subtree: `0`.

The minimum repair for missing payloads is to retain the original dynamic route and wait for exact original/Source15 bytes before registering a route. Similar spell icons and unrelated `background.jpg` files are not accepted as substitutes.
