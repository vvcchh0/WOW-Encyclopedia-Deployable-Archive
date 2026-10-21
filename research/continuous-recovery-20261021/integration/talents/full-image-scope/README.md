# Talent full image scope (v42)

Generated: 2026-10-21T03:34:02.179Z

This is a read-only initial DOM/response audit of the nine v42 talent pages at http://127.0.0.1:34881/WOW-Encyclopedia-Deployable-Archive. No calculator controls were clicked, no points were changed, and all non-loopback requests were aborted.

## Counts

- DOM image/background references observed: 5061; normal non-placeholder references: 1677; unique normal DOM URLs: 52.
- Static placeholder targets (decoded missing-image.svg requested): 1232 unique / 3330 references.
- Dynamic image HTTP/request errors: 61 unique / 61 references.
- DOM-observed image/background targets with no v42 local file and no image error response: 27 unique / 54 references.
- Merged missing targets (placeholder + dynamic error + DOM-only local-missing): 1259 unique.

| class | static unique/refs | dynamic unique/refs | DOM-only local-missing unique/refs | merged unique | page errors | failed local requests | blocked external |
|---|---:|---:|---:|---:|---:|---:|---:|
| druid | 154/375 | 15/21 | 3/6 | 157 | 0 | 0 | 0 |
| hunter | 155/377 | 7/13 | 3/6 | 158 | 0 | 0 | 0 |
| mage | 164/383 | 7/13 | 3/6 | 167 | 0 | 0 | 0 |
| paladin | 164/371 | 7/13 | 3/6 | 167 | 0 | 0 | 0 |
| priest | 155/367 | 3/9 | 3/6 | 158 | 0 | 0 | 0 |
| rogue | 164/385 | 3/9 | 3/6 | 167 | 0 | 0 | 0 |
| shaman | 155/362 | 13/19 | 3/6 | 158 | 0 | 0 | 0 |
| warlock | 155/370 | 3/9 | 3/6 | 158 | 0 | 0 | 0 |
| warrior | 159/374 | 3/9 | 3/6 | 162 | 0 | 0 | 0 |

## Classification and limits

Static placeholders are based on the actual DOM URL ending in __offline/missing-image.svg and the decoded requested query value. Dynamic errors are image-like local responses >=400 or failed image requests observed by Playwright. DOM-only local-missing targets are actual computed/inline image URLs with no v42 file and no corresponding image error response (for example tree backgrounds on hidden rows). Repeated references are retained in the receipt and counted separately from unique targets in missing-targets.json/csv.

Local correspondence uses only the v42 export root, route-map.json, and export-provenance.json. A local file existing or a route returning a placeholder is not counted as the requested image being available.

Uncovered: hover/state-generated talent images were not activated; stylesheet-only URLs not present in computed/inline background values are outside this DOM pass; no source, route, module, or production file was changed.
