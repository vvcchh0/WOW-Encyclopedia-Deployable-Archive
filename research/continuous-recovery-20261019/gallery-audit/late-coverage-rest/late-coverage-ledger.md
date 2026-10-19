# Gallery late coverage rest audit

Generated `2026-10-19T10:02:24.995951Z` from frozen local evidence only; external requests: **0**.

Target window: **20080512210045..20101207235959** (after frozen anchor `20080512210044` through 2010-12-07 23:59:59). Frozen registry: `research/continuous-recovery-20261016/local-audit/gallery-final-v7/gallery-prefix-registry-v7.json` SHA `2579f66841bf6102d90f5dbfe819902337bff03f6e3ac7191239ae041e2d97d6`.

The latest gallery source authority is the accepted gap01 receipt, not the unchanged status snapshot. It corrects the old Karazhan/Black Temple transport_unknown labels. Zul’Aman is closed because its late prefix already completed. No image payload was accepted or replayed by these index records. The current global network tail is separately bound to `research/continuous-recovery-20261019/publication/root-frontier-news20f-source-acceptance.json` SHA `5c9c965737f3ef1282a85c516663a5f216b93f8fc627a7dcddb382fd6707d165` (tail0); the gallery gap01 receipt is used only for gallery-specific correction.

## Result

- Groups audited: **50**.
- Late prefix complete: **3** (Karazhan, Zul'Aman, Black Temple).
- Current late transport/parse unknown: **0**.
- Not complete through 2010-12-07 and still unqueried/residual: **47**.
- New network requests: **0**; no replay, redirect follow, pagination, or filename guessing.

## Receipt correction

| Receipt | Target result | Interpretation |
|---|---|---|
| `research/continuous-recovery-20261018/publication/root-gallery-late-window-source-acceptance.json` | Karazhan: 20090101000000..20101207235959, valid=False, complete=False, rows=0; Zul'Aman: 20080512210045..20101207235959, valid=True, complete=True, rows=63; Black Temple: 20080512210045..20101207235959, valid=False, complete=False, rows=0 | historical first late-window receipt; Kara/Black Temple invalid, Zul complete; requests=6, source responses=1, stop=completed_candidate_queue |
| `research/continuous-recovery-20261018/publication/root-gallery-retry2-source-acceptance.json` | Karazhan: 20090101000000..20101207235959, valid=False, complete=False, rows=0; Black Temple: 20080512210045..20101207235959, valid=False, complete=False, rows=0 | historical retry receipt; endpoint 503, no valid index; requests=4, source responses=1, stop=endpoint_status_503 |
| `research/continuous-recovery-20261019/publication/root-gallery-late-gap01-source-acceptance.json` | Karazhan: 20090101000000..20101207235959, valid=True, complete=True, rows=52; Black Temple: 20080512210045..20101207235959, valid=True, complete=True, rows=68 | latest accepted gap01 receipt; corrects stale Kara/Black Temple unknown; requests=4, source responses=2, stop=None |

Old r2 Kara/Black Temple unknown is historical only. Gap01 returned valid complete CDX responses: Kara 52 rows over 20090101..20101207 and Black Temple 68 rows over 20080512 21:00:45..20101207. Neither yielded a strict native full-size/thumb candidate or payload. Kara’s saved complete 2008 prefix supplies anchor+1..2008-12-31; accepted intervals therefore close the target. Zul’Aman’s accepted late response has 63 rows, 29 nested image rows, and no strict direct candidate.

## All 50 groups

|#|Gallery|Exact source directory|Slots|Late status|Accepted complete coverage|Residual target|
|---:|---|---|---:|---|---|---|
|1|Karazhan|`http://www.worldofwarcraft.com/info/dungeons/images/karazhan/`|63|**complete**|20080512210045..20081231235959, 20090101000000..20101207235959|—|
|2|Zul'Aman|`http://www.worldofwarcraft.com/info/dungeons/images/zulaman/`|60|**complete**|20080512210045..20101207235959|—|
|3|Magtheridon's Lair|`http://www.worldofwarcraft.com/info/dungeons/images/mag/`|15|**not_queried**|—|20080512210045..20101207235959|
|4|Gruul's Lair|`http://www.worldofwarcraft.com/info/dungeons/images/gruul/`|21|**not_queried**|—|20080512210045..20101207235959|
|5|Serpentshrine Cavern|`http://www.worldofwarcraft.com/info/dungeons/images/serpentshrine/`|29|**not_queried**|—|20080512210045..20101207235959|
|6|The Battle for Mount Hyjal - Caverns of Time|`http://www.worldofwarcraft.com/info/dungeons/images/battle/`|44|**not_queried**|—|20080512210045..20101207235959|
|7|Tempest Keep - The Eye|`http://www.worldofwarcraft.com/info/dungeons/images/theeye/`|43|**not_queried**|—|20080512210045..20101207235959|
|8|Black Temple|`http://www.worldofwarcraft.com/info/dungeons/images/blacktemple/`|48|**complete**|20080512210045..20101207235959|—|
|9|Doom Lord Kazzak|`http://www.worldofwarcraft.com/info/dungeons/images/doomlordkazzak/`|9|**not_queried**|—|20080512210045..20101207235959|
|10|Magister's Terrace|`http://www.worldofwarcraft.com/info/dungeons/images/magisters/`|47|**not_queried**|—|20080512210045..20101207235959|
|11|Hellfire Citadel - Hellfire Ramparts|`http://www.worldofwarcraft.com/info/dungeons/images/hellfireramparts/`|32|**not_queried**|—|20080512210045..20101207235959|
|12|Hellfire Citadel - The Blood Furnace|`http://www.worldofwarcraft.com/info/dungeons/images/bloodfurnace/`|39|**not_queried**|—|20080512210045..20101207235959|
|13|Hellfire Citadel - The Shattered Halls|`http://www.worldofwarcraft.com/info/dungeons/images/shatteredhalls/`|50|**not_queried**|—|20080512210045..20101207235959|
|14|Coilfang Reservoir - The Underbog|`http://www.worldofwarcraft.com/info/dungeons/images/underbog/`|40|**not_queried**|—|20080512210045..20101207235959|
|15|Caverns of Time - Escape from Durnholde|`http://www.worldofwarcraft.com/info/dungeons/images/escape/`|38|**not_queried**|—|20080512210045..20101207235959|
|16|Caverns of Time - Opening of the Dark Portal|`http://www.worldofwarcraft.com/info/dungeons/images/opening/`|30|**not_queried**|—|20080512210045..20101207235959|
|17|Coilfang Reservoir - The Steam Vaults|`http://www.worldofwarcraft.com/info/dungeons/images/steamvaults/`|30|**not_queried**|—|20080512210045..20101207235959|
|18|Auchindoun - Mana-Tombs|`http://www.worldofwarcraft.com/info/dungeons/images/manatombs/`|30|**not_queried**|—|20080512210045..20101207235959|
|19|Auchindoun - Auchenai Crypts|`http://www.worldofwarcraft.com/info/dungeons/images/crypts/`|37|**not_queried**|—|20080512210045..20101207235959|
|20|Auchindoun - Sethekk Halls|`http://www.worldofwarcraft.com/info/dungeons/images/sethekhalls/`|38|**not_queried**|—|20080512210045..20101207235959|
|21|Auchindoun - Shadow Labyrinth|`http://www.worldofwarcraft.com/info/dungeons/images/shadowlabs/`|23|**not_queried**|—|20080512210045..20101207235959|
|22|Tempest Keep - The Mechanar|`http://www.worldofwarcraft.com/info/dungeons/images/mech/`|35|**not_queried**|—|20080512210045..20101207235959|
|23|Tempest Keep - The Botanica|`http://www.worldofwarcraft.com/info/dungeons/images/botanica/`|19|**not_queried**|—|20080512210045..20101207235959|
|24|Tempest Keep - The Arcatraz|`http://www.worldofwarcraft.com/info/dungeons/images/arcatraz/`|49|**not_queried**|—|20080512210045..20101207235959|
|25|Warsong Gulch|`http://www.worldofwarcraft.com/pvp/battlegrounds/warsonggulch/`|29|**not_queried**|—|20080512210045..20101207235959|
|26|Isle of Quel'Danas|`http://www.worldofwarcraft.com/info/regions/isleofq/`|49|**not_queried**|—|20080512210045..20101207235959|
|27|Amani War Bear|`http://www.worldofwarcraft.com/info/basics/images/mounts/bear/`|24|**not_queried**|—|20080512210045..20101207235959|
|28|Riding Turtle|`http://www.worldofwarcraft.com/info/basics/mounts/turtle/`|12|**not_queried**|—|20080512210045..20101207235959|
|29|Swift White Hawkstrider|`http://www.worldofwarcraft.com/info/basics/mounts/whitehawkstrider/`|15|**not_queried**|—|20080512210045..20101207235959|
|30|Qiraji battle tank|`http://www.worldofwarcraft.com/info/basics/mounts/aqbattletank/`|4|**not_queried**|—|20080512210045..20101207235959|
|31|Raven Mount|`http://www.worldofwarcraft.com/info/basics/mounts/ravenmount/`|9|**not_queried**|—|20080512210045..20101207235959|
|32|Black War Elekk|`http://www.worldofwarcraft.com/info/basics/mounts/blackwarelekk/`|6|**not_queried**|—|20080512210045..20101207235959|
|33|Fiery Warhorse|`http://www.worldofwarcraft.com/info/basics/mounts/fierywarhorse/`|13|**not_queried**|—|20080512210045..20101207235959|
|34|Cenarion War Mount|`http://www.worldofwarcraft.com/info/basics/mounts/cenarion/`|13|**not_queried**|—|20080512210045..20101207235959|
|35|Flying Machine|`http://www.worldofwarcraft.com/info/basics/mounts/flying/flyingmachine/`|22|**not_queried**|—|20080512210045..20101207235959|
|36|Phoenix|`http://www.worldofwarcraft.com/info/basics/mounts/flying/phoenix/`|15|**not_queried**|—|20080512210045..20101207235959|
|37|X-51 Nether-Rocket|`http://www.worldofwarcraft.com/info/basics/mounts/flying/rocketmount/`|14|**not_queried**|—|20080512210045..20101207235959|
|38|Fishing|`http://www.worldofwarcraft.com/info/professions/images/fishing/ss/`|66|**not_queried**|20080512210045..20081231235959|20090101000000..20101207235959|
|39|Lunar Festival|`http://www.worldofwarcraft.com/info/events/lunarnewyears/images/ss/`|35|**not_queried**|—|20080512210045..20101207235959|
|40|Love is in the Air|`http://www.worldofwarcraft.com/info/events/loveisintheair/images/ss/`|34|**not_queried**|—|20080512210045..20101207235959|
|41|Hallow's End|`http://www.worldofwarcraft.com/info/events/hallowsend/images/newscreenshots/`|65|**not_queried**|—|20080512210045..20101207235959|
|42|Brewfest|`http://www.worldofwarcraft.com/info/events/brewfest/images/ss/`|51|**not_queried**|—|20080512210045..20101207235959|
|43|Winter's Veil|`http://www.worldofwarcraft.com/info/events/winterveil/images/ss/`|37|**not_queried**|—|20080512210045..20101207235959|
|44|Darkmoon Faire: Level 70 Elite Tauren Chieftain|`http://www.worldofwarcraft.com/info/events/darkmoon/images/ss/`|20|**not_queried**|—|20080512210045..20101207235959|
|45|TCG Gallery|`http://www.worldofwarcraft.com/info/items/images/tcg/`|47|**not_queried**|—|20080512210045..20101207235959|
|46|TCG Spectral Tiger|`http://www.worldofwarcraft.com/info/basics/mounts/spectral/`|47|**not_queried**|—|20080512210045..20101207235959|
|47|TCG Picnic Basket|`http://www.worldofwarcraft.com/info/items/images/picnic/`|42|**not_queried**|—|20080512210045..20101207235959|
|48|City Attacks|`http://www.worldofwarcraft.com/pvp/worldpvp/images/city/`|102|**not_queried**|—|20080512210045..20101207235959|
|49|Halaa PvP|`http://www.worldofwarcraft.com/pvp/worldpvp/images/ss/`|14|**not_queried**|—|20080512210045..20101207235959|
|50|World PvP|`http://www.worldofwarcraft.com/pvp/worldpvp/images/worldpvp/`|30|**not_queried**|—|20080512210045..20101207235959|

The 47 `not_queried` rows can have a bounded 2008 overlap in v7, but their residual late interval is not complete through 2010-12-07. A partial overlap is not promoted to `complete`.

## Limited next-prefix draft (no network)

These ten exact prefixes are only a root-review draft. Each comes from a frozen source page `addshots` literal and declared slot count; no `ssN` filename is invented. Kara, Black Temple, and Zul’Aman are excluded because their late windows are complete at index level.

|Draft|Registry|Gallery|Exact prefix|Source page line|Window|
|---:|---:|---|---|---|---|
|1|3|Magtheridon's Lair|`http://www.worldofwarcraft.com/info/dungeons/images/mag/`|`.scratch/offline-navigation-20261015-v15/site/info/dungeons/mag-gallery.html:78`|20080512210045..20101207235959|
|2|4|Gruul's Lair|`http://www.worldofwarcraft.com/info/dungeons/images/gruul/`|`.scratch/offline-navigation-20261015-v15/site/info/dungeons/gruul-gallery.html:84`|20080512210045..20101207235959|
|3|5|Serpentshrine Cavern|`http://www.worldofwarcraft.com/info/dungeons/images/serpentshrine/`|`.scratch/offline-navigation-20261015-v15/site/info/dungeons/serpentshrine-gallery.html:92`|20080512210045..20101207235959|
|4|6|The Battle for Mount Hyjal - Caverns of Time|`http://www.worldofwarcraft.com/info/dungeons/images/battle/`|`.scratch/offline-navigation-20261015-v15/site/info/dungeons/cot-hyjal-gallery.html:108`|20080512210045..20101207235959|
|5|7|Tempest Keep - The Eye|`http://www.worldofwarcraft.com/info/dungeons/images/theeye/`|`.scratch/offline-navigation-20261015-v15/site/info/dungeons/tk-the-eye-gallery.html:106`|20080512210045..20101207235959|
|6|9|Doom Lord Kazzak|`http://www.worldofwarcraft.com/info/dungeons/images/doomlordkazzak/`|`.scratch/offline-navigation-20261015-v15/site/info/dungeons/doom-lord-kazzak-gallery.html:72`|20080512210045..20101207235959|
|7|10|Magister's Terrace|`http://www.worldofwarcraft.com/info/dungeons/images/magisters/`|`.scratch/offline-navigation-20261015-v15/site/info/dungeons/magisters-terrace-gallery.html:110`|20080512210045..20101207235959|
|8|11|Hellfire Citadel - Hellfire Ramparts|`http://www.worldofwarcraft.com/info/dungeons/images/hellfireramparts/`|`.scratch/offline-navigation-20261015-v15/site/info/dungeons/hc-hellfire-ramparts-gallery.html:95`|20080512210045..20101207235959|
|9|12|Hellfire Citadel - The Blood Furnace|`http://www.worldofwarcraft.com/info/dungeons/images/bloodfurnace/`|`.scratch/offline-navigation-20261015-v15/site/info/dungeons/hc-blood-furnace-gallery.html:102`|20080512210045..20101207235959|
|10|13|Hellfire Citadel - The Shattered Halls|`http://www.worldofwarcraft.com/info/dungeons/images/shatteredhalls/`|`.scratch/offline-navigation-20261015-v15/site/info/dungeons/hc-shatteredhalls-gallery.html:113`|20080512210045..20101207235959|

Any future acceptance would require a valid complete CDX response with no resume key, strict host/scheme identity, and explicit separation of direct full-size rows, nested previews, and identity variants. It would not replay an image automatically.

## Source-page and JS boundary

Shared JS `.scratch/offline-navigation-20261015-v15/site/new-hp/js/guidegallery-screenie.js` SHA `b0e619c361c315b60eca6d05c92f38efc3eed1f773bfbdb971af6c2deb3e0a4c` shows `addshots` constructing `sourceDirectory + filename + number + .jpg` (lines 471–487) and `printPages` deriving `-thumb.jpg` (lines 501–507). This supports only a mechanism inference about dynamic discovery versus static guide previews; it does not prove crawler behavior or authorize filename expansion.

## Evidence boundary and stop conditions

- Index rows are not payloads; an empty/invalid/transport result is not an image 404.
- Do not repeat the accepted Zul’Aman late window or accepted Kara/Black Temple gap01 windows.
- Do not follow redirects, query regional/guide aliases, or promote HTTPS/scheme variants to the HTTP native identity.
- This audit wrote only its own `late-coverage-rest/` directory and made zero network requests.
