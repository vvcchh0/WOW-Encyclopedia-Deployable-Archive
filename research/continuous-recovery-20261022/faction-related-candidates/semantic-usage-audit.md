# Faction icon candidate usage audit

Read-only local audit prepared 2026-10-22. It made no network requests and changed no site, map, tools, tests, or Git state. The full curated result is in [`semantic-usage-audit.json`](semantic-usage-audit.json); it records each matching data-script line, item label, faction, reputation bracket, tooltip excerpt, page route and page/script hash without copying full page HTML or raw image payloads.

## Finding

The three GitHub JPEGs are useful later-related candidates, but the local evidence does not establish that their pixels match the missing Source16 GIFs. The only exact item-role tie is for `INV_Wand_11.gif`: its two reward rows name **Incendic Rod** for Alliance and Horde. The Scroll stems are shared icons for many different reward objects, so they do not designate one scroll item.

| Missing target | Source16 occurrences | Referencing pages | Evidence in the reward data |
|---|---:|---:|---|
| `/info/basics/factions/images/icons/INV_Scroll_03.gif` | 58 | 10 | 31 Patterns, 13 Plans, 9 Recipes, 3 Designs, 1 Schematic, 1 other label; 39 `playerFaction=alliance` and 19 `playerFaction=horde` rows across Friendly through Exalted |
| `/info/basics/factions/images/icons/INV_Scroll_06.gif` | 25 | 10 | 14 Recipes and 11 Designs; 21 `playerFaction=alliance` and 4 `playerFaction=horde` rows across Friendly through Exalted |
| `/info/basics/factions/images/icons/INV_Wand_11.gif` | 2 | 1 | Both rows are `Incendic Rod`, one `playerFaction=alliance` and one `playerFaction=horde`, both Friendly |

For example, `INV_Scroll_03.gif` is used for “Pattern: Flameheart Bracers” (tooltip says “Requires The Aldor - Friendly”) and “Pattern: Blastguard Belt” (tooltip says “Requires The Aldor - Honored”). `INV_Scroll_06.gif` appears with “Design: Gleaming Golden Draenite” and its “Requires The Aldor - Friendly” tooltip, among other designs and recipes. The Wand tooltip starts “Incendic Rod | Binds when picked up | Ranged Wand | 129 - 240 Fire Damage”. All 85 item rows had a parsed tooltip excerpt; the JSON keeps one excerpt per defined tier.

## Where the references are used

The 10 pages using both Scroll targets are:

- `/info/basics/factions/aldorscryers/aldor-scryers.xml`
- `/info/basics/factions/cenarionxp/cenarionxp.xml`
- `/info/basics/factions/consortium/consortium.xml`
- `/info/basics/factions/hellfire/hellfire.xml`
- `/info/basics/factions/keepers/keepers.xml`
- `/info/basics/factions/lowercity/lowercity.xml`
- `/info/basics/factions/nagrand/nagrand.xml`
- `/info/basics/factions/shatar/shatar.xml`
- `/info/basics/factions/sporeggar/sporeggar.xml`
- `/info/basics/factions/violeteye/violeteye.xml`

The Wand target is used on `/info/basics/factions/zangarmarsh/zangarpvp.xml`.
The matching v53 export pages use the same route tails with `.xml.html`, under the `/WOW-Encyclopedia-Deployable-Archive/` base path. The JSON lists every page’s script include line and hash, plus the source and v53 hashes for all 11 reward scripts. In Source16, the per-page reward scripts occur at line 577; in v53 they occur at line 582.

The data is rendered dynamically. Source16’s shared `rewardstable-new.js` sets `itemIcon.src = rewardItem.itemIcon` (line 142), assigns the `style_icon` class (144), and binds tooltip display to hover over the reward name (160). The table has separate Alliance and Horde containers. Its `itemStats[0..3]` bracket selection maps to Friendly, Honored, Revered and Exalted. In Source16’s stylesheet, `.style_icon` is placed at `left:7px; top:5px` (line 1); the item cell is 207×55 px (line 2), while the icon rule itself sets no width or height. Therefore the original GIF’s displayed and native dimensions are unknown. A replacement JPEG would have a 36×36 native size and, absent another applicable style, would render at its intrinsic size; verify this in Chrome after any integration.

Source16 has no file with any of the three exact target basenames anywhere in its saved site. The v53 export also has none at those targets: its reward scripts preserve the requested image paths in offline missing-image placeholders. The data-script declarations are the only occurrences of these names in Source16; in v53 they remain in those transformed scripts as missing-resource requests. The JSON includes all 85 source and 85 v53 occurrence lines, plus the hashes and page references. The shared renderer and stylesheet are referenced from 17 faction pages in each tree. The `playerFaction` field is literally `alliance` or `horde`, but page tabs can be labeled “The Aldor”/“The Scryers”, “Honor Hold”/“Thrallmar”, “Kurenai”/“Mag'har”, or “Alliance”/“Horde”. Treat the field as the source’s table grouping, not an independent proof of in-game faction eligibility. All 10 Scroll pages contain the four reputation controls; the Zangarmarsh Wand page has no reputation selector and both item rows are Friendly.

## Candidate provenance and boundary

All three candidates are JPEGs from `boom8866/coolwow2` commit `09c52b7673871b8048da92e5a13ed753fc08162f`, dated 2015-12-16, with no original-capture date. Each is 36×36, one frame. Their exact local payload sizes, SHA-256 and Git blob SHA-1 values are in the JSON, bound to the accepted `runtime/public-inventory.json` record. No same-stem image exists in the saved Source16 tree, and there is no original GIF payload or pixel comparison. The `Scroll` basename is therefore a weak category hint, while the Wand row’s `Incendic Rod` label confirms item role but not image identity. If reused, annotate it as `later_related_source` and identify the JPEG’s repository/commit/format explicitly; do not describe it as recovered Source16 GIF bytes or a confirmed visual match.

## Minimal integration record and browser check

If the parent elects to try these assets, the smallest source note is one provenance entry per JPEG, attached to the corresponding missing target path. Mark the link as later-related and the byte/pixel identity to the original GIF as unknown. The target set is exactly the three paths in the table. The Scroll entries would affect the 10 listed reward pages; the Wand entry would affect only the Zangarmarsh PvP page.

For Chrome verification after an approved integration: open all 11 v53 page routes (prefix each `.xml.html` route with `/WOW-Encyclopedia-Deployable-Archive`), inspect Network for the three exact target URLs and successful image decodes, then check both visible table tabs on representative pages, hover reward labels to verify tooltips, and inspect `naturalWidth`, `naturalHeight`, and computed `width`/`height` on the icon. Use the page’s displayed tab names, since they can differ from the script’s `playerFaction` values. On the Scroll pages, click Friendly, Honored, Revered and Exalted controls and verify rows still show icons. The existing v53 browser acceptance did not cover these faction pages, so this would be new coverage.

## Unknowns

- Original Source16 GIF bytes, format/MIME, dimensions, animation, and pixels.
- Whether any candidate JPEG is visually identical to its missing GIF counterpart.
- Whether the 36×36 JPEGs’ intrinsic size is the intended rendered size in each browser/layout; no fixed icon width or height appears in the shared rule.
- The v53 browser result for these faction pages; only their local export structure and hashes were checked here.
