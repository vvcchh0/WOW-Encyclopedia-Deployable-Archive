# Related-site coverage inventory

Anchor capture: `20080512210044`. Generated: `2026-10-14T06:01:44Z`.

## Current integrated material

The frozen build manifest contains **8,304** route/entity rows. It also carries **1,031** supplement source records; those records are reported separately and are not added to the frozen entity count. The current pages-resources provenance lists **8,417** generated entries and the tree contains **8,418** physical files including provenance.

The current browserable source-entity set is **8,304 frozen entities + 19 image overlays = 8,323 source entities**. The frozen-row source metadata records actual capture timestamps from `20060105214700` to `20101203204310`; this is a metadata range and does not claim that every current page is from one capture version.

| Source host / namespace | Rows | HTML | Images | Other | Actual capture range |
| --- | ---: | ---: | ---: | ---: | --- |
| `(none)` | 7 | 2 | 1 | 4 | `None` - `None` |
| `forums.worldofwarcraft.com` | 106 | 1 | 91 | 14 | `20080508034452` - `20081206114202` |
| `worldofwarcraft.com` | 1 | 1 | 0 | 0 | `20080412081212` - `20080412081212` |
| `www.worldofwarcraft.com` | 8,190 | 915 | 7,033 | 242 | `20060105214700` - `20101203204310` |

The frozen source namespaces are the main `worldofwarcraft.com` site and its forums. This manifest does not contain integrated `wow-europe.com`, Blizzard, Armory, account/sign-up, or third-party source files.

The machine-readable summary separates primary manifest files from supplements and records both the concrete source URL host and the origin namespace. This preserves the one bare `worldofwarcraft.com` route and any source/namespace alias mismatch instead of silently folding it into a display label.

## Existing local material not yet integrated

The approved source-map indexes contain **884** valid local records across 29 maps. After route and SHA-256 de-duplication, `missing_from_frozen_manifest` is **22** entities. Of those, `present_in_current_overlay` is **19**, leaving `still_unmerged` at **3**. Duplicate source-map records account for the difference between map records and unique entities.

| Host | Unique local entities | Content groups |
| --- | ---: | --- |
| `www.worldofwarcraft.com` | 22 | image 22 |

The 19 overlay entries are the VISA/reward image resources already present in the current pages-resources tree. The three still-unmerged entries are unique late-capture Karazhan preview images. No related-domain local material was found in this bounded approved-map index set.

## Current unresolved references

The manifest records **27,700** unresolved references overall. The materialized host breakdown covers only the first **2,000** entries, so those per-host counts are an observed sample rather than totals.

| Host | Observed sample count |
| --- | ---: |
| `beta.worldofwarcraft.com` | 1 |
| `entertainment.upperdeck.com` | 6 |
| `forums.worldofwarcraft.com` | 351 |
| `media.worldofwarcraft.com` | 2 |
| `shop.blizzard.com` | 60 |
| `signup.worldofwarcraft.com` | 53 |
| `us.blizzard.com` | 440 |
| `www.blizzard.com` | 284 |
| `www.esrb.org` | 106 |
| `www.google-analytics.com` | 52 |
| `www.jinx.com` | 1 |
| `www.macromedia.com` | 1 |
| `www.mydomain` | 18 |
| `www.worldofwarcraft.co.kr` | 1 |
| `www.worldofwarcraft.com` | 536 |
| `www.wow-europe.com` | 4 |
| `www.wowarmory.com` | 82 |
| `www.wowchina.com` | 1 |
| `www.wowtaiwan.com.tw` | 1 |

## Related-site leads

The candidate indexes contain 1,907 deduplicated URLs. They are leads for future capture work and are not counted as downloaded material. The complete sanitized host/path ledger is in [`source-ledger.json`](source-ledger.json).

The candidate list includes the WoW Europe site, Blizzard subdomains, Armory, forums, account/sign-up hosts, and third-party links. Archive URLs themselves were excluded from the candidate host list.

## Method and limits

Counts were computed from the local build manifest, export provenance, bounded approved source maps, and existing candidate JSON indexes. No network requests were made and no raw archive tree was copied. See `sanitized-summary.json` for machine-readable counts and source-map coverage.
