# Underdev Arathi dynamic-route review

Generated 2026-10-21T13:13:05.550587Z. This is a read-only local audit; no network, production, export, or Git write was performed.

The r3 input contains **22 observed targets** on `/pvp/battlegrounds/info-arathi.html`: `/info/underdev/index.htmlimages/arathi/ss5-thumb.jpg` through `ss30-thumb.jpg` with the two numbers present in the page but absent as exact local files (`ss17`, `ss18`). The target string is a runtime concatenation defect, not an original resource path. Source16 keeps `path = "/info/underdev/"` (line 619) and `theDirectory = "images/arathi/"` (line 622); the screenshot helper concatenates these values with `ssN-thumb.jpg`. v51 changed only the path assignment to `.../info/underdev/index.html` (line 624), so the runtime constructs `index.htmlimages/...`.

The v51 route map contains the intended exact route for **20/22** targets and the corresponding v51 JPEGs are byte-identical to the Source16-derived files. **2** exact payloads (`ss17-thumb.jpg`, `ss18-thumb.jpg`) are absent in the checked Source16/offline/v51 roots and manifests; other same-basename images were excluded. Therefore these rows should not remain a 22-item resource-gap count: fix the narrow dynamic directory-base rewrite first, then track only the two exact absent entities as resource gaps.

A bounded next-round fix should preserve a trailing directory base for this dynamic assignment (or equivalent page-scoped guard) instead of resolving `/info/underdev/` to its index document. Do not add a generic repeated-slash alias or substitute another route's image.

Per-target hashes, manifest timestamps/roles, route-map presence, line references, and r3 marker metrics are in [`underdev-final-routing-review.json`](underdev-final-routing-review.json).
