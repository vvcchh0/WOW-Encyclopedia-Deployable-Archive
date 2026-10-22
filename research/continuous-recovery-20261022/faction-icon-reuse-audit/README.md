# Faction icon reuse audit

Read-only local audit of the ten faction icon rows in `research/continuous-recovery-20261021/publication/v52-remaining-resource-targets.csv`.

Result: **0 reusable candidates**. Every target is absent from the v52 route map and Source16 exact-file/alias records, and no exact output file exists in either frozen tree. A repository-wide case-insensitive filename-stem search found no saved image with any of the ten target stems. Per-target route/page evidence and source-byte SHA-256 values are in [`audit.json`](audit.json).

The 986-item set is a later **CraftedRO WotLK 3.3.5a talent-calculator source supplement**, not an Armory image set. The source acceptance records retrieval at `2026-10-21T04:39:55.289652+00:00`; the original capture timestamp is null and no original 2008 icons were recovered. Its accepted scope is same-path 36×36 single-frame JPEG talent icons for nine talent calculators.

Page context: the Zangarmarsh reward script names `Incendic Rod`, `Libram of Zeal`, `Totem of Impact`, `Idol of Savagery`, `Mark of Defiance`, `Mark of Conquest`, and `Mark of Vindication` at Source16 lines 114, 137, 157, 177, 197, 218, and 239 respectively (each occurs for Alliance and Horde). The scroll icons are used for crafting patterns/plans (`INV_Scroll_03.gif`) and designs/recipes (`INV_Scroll_06.gif`). `honorholdtoken.gif` has no textual reference in either frozen faction subtree.

Two title-word leads were rejected: Shaman talent `Totem of Wrath` is not faction reward `Totem of Impact`; Paladin talent `Vindication` is not the item `Mark of Vindication`. Neither is mapped to a faction icon route, and neither has an established 2008 image identity. No candidate image was copied or substituted.

No network access was used. Only this JSON and README were written in the assigned folder; no raw HTML, cookie data, full DOM, or full script lines were copied.
