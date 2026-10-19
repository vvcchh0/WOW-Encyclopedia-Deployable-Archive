# Source15 and late gallery audit r3

R3 is additive; r2 remains unchanged. No network request was made.

## Corrections

Real v37 root: .scratch/pages-resources-20261019-v37. Every candidate uses provenance output_path plus actual file length/SHA and frozen source-manifest host identity. Complete ledger rows keep an empty uncovered interval; only open rows retain uncovered windows.

## 50-gallery coverage

Rows: 50; park 21; open 29 (source_503 1, not_queried 28). Park means do not repeat the same complete prefix window, not a gallery-wide 404 or final recovery claim.

| rank | gallery | prior | r3 | uncovered | source page |
|---:|---|---|---|---|---|
| 1 | Karazhan | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/karazhan-gallery.html:126 |
| 2 | Zul'Aman | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/zulaman-gallery.html:123 |
| 3 | Magtheridon's Lair | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/mag-gallery.html:78 |
| 4 | Gruul's Lair | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/gruul-gallery.html:84 |
| 5 | Serpentshrine Cavern | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/serpentshrine-gallery.html:92 |
| 6 | The Battle for Mount Hyjal - Caverns of Time | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/cot-hyjal-gallery.html:108 |
| 7 | Tempest Keep - The Eye | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/tk-the-eye-gallery.html:106 |
| 8 | Black Temple | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/black-temple-gallery.html:112 |
| 9 | Doom Lord Kazzak | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/doom-lord-kazzak-gallery.html:72 |
| 10 | Magister's Terrace | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/magisters-terrace-gallery.html:110 |
| 11 | Hellfire Citadel - Hellfire Ramparts | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/hc-hellfire-ramparts-gallery.html:95 |
| 12 | Hellfire Citadel - The Blood Furnace | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/hc-blood-furnace-gallery.html:102 |
| 13 | Hellfire Citadel - The Shattered Halls | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/hc-shatteredhalls-gallery.html:113 |
| 14 | Coilfang Reservoir - The Underbog | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/cr-underbog-gallery.html:103 |
| 15 | Caverns of Time - Escape from Durnholde | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/cot-escape-gallery.html:101 |
| 16 | Caverns of Time - Opening of the Dark Portal | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/cot-opening-gallery.html:93 |
| 17 | Coilfang Reservoir - The Steam Vaults | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/cr-steamvaults-gallery.html:93 |
| 18 | Auchindoun - Mana-Tombs | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/auc-mana-tombs-gallery.html:93 |
| 19 | Auchindoun - Auchenai Crypts | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/auc-crypts-gallery.html:100 |
| 20 | Auchindoun - Sethekk Halls | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/auc-sethek-halls-gallery.html:101 |
| 21 | Auchindoun - Shadow Labyrinth | complete | park | none (complete) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/auc-shadow-lab-gallery.html:86 |
| 22 | Tempest Keep - The Mechanar | source_503 | open | 20080512210045..20101207235959 (source_503) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/tk-mech-gallery.html:98 |
| 23 | Tempest Keep - The Botanica | not_queried | open | 20080512210045..20101207235959 (not_queried) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/tk-botanica-gallery.html:82 |
| 24 | Tempest Keep - The Arcatraz | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/dungeons/tk-arcatraz-gallery.html:112 |
| 25 | Warsong Gulch | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/pvp/battlegrounds/warsong-gulch-gallery.html:96 |
| 26 | Isle of Quel'Danas | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/regions/isle-of-queldanas-gallery.html:112 |
| 27 | Amani War Bear | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/basics/mounts/bear-gallery.html:87 |
| 28 | Riding Turtle | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/basics/mounts/turtle-gallery.html:75 |
| 29 | Swift White Hawkstrider | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/basics/mounts/swiftwhitehawkstrider-gallery.html:78 |
| 30 | Qiraji battle tank | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/basics/mounts/aq-battletank-gallery.html:67 |
| 31 | Raven Mount | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/basics/mounts/raven-mount-gallery.html:72 |
| 32 | Black War Elekk | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/basics/mounts/black-war-elekk-gallery.html:69 |
| 33 | Fiery Warhorse | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/basics/mounts/fiery-warhorse-gallery.html:76 |
| 34 | Cenarion War Mount | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/basics/mounts/cenarion-gallery.html:76 |
| 35 | Flying Machine | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/basics/mounts/flyingmachine-gallery.html:85 |
| 36 | Phoenix | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/basics/mounts/phoenix-gallery.html:78 |
| 37 | X-51 Nether-Rocket | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/basics/mounts/rocket-mount-gallery.html:77 |
| 38 | Fishing | not_queried | open | 20090101000000..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/professions/fishing-gallery.html:129 |
| 39 | Lunar Festival | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/events/lunarnewyears/gallery.html:98 |
| 40 | Love is in the Air | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/events/loveisintheair/gallery.html:97 |
| 41 | Hallow's End | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/events/hallowsend/gallery.html:128 |
| 42 | Brewfest | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/events/brewfest/gallery.html:114 |
| 43 | Winter's Veil | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/events/winterveil/gallery.html:100 |
| 44 | Darkmoon Faire: Level 70 Elite Tauren Chieftain | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/events/darkmoon/gallery.html:83 |
| 45 | TCG Gallery | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/items/tcg-gallery.html:110 |
| 46 | TCG Spectral Tiger | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/basics/mounts/spectral-gallery.html:110 |
| 47 | TCG Picnic Basket | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/info/items/tcg-picnic-gallery.html:105 |
| 48 | City Attacks | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/pvp/worldpvp/cityattacks-gallery.html:166 |
| 49 | Halaa PvP | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/pvp/worldpvp/halaa-gallery.html:77 |
| 50 | World PvP | not_queried | open | 20080512210045..20101207235959 (?) | .scratch/offline-navigation-20261015-v15/site/pvp/worldpvp/worldpvp-gallery.html:93 |


## v37 identity and continuation queue

Status counts: {'v37_local_host_match_scheme_variant': 204, 'v37_local_exact_identity': 207, 'v37_no_provenance_route': 6}. Late complete-prefix overlap: {'no_matching_frozen_complete_prefix': 417}.

| rank | exact URL | r3 status | host match | bytes/SHA match | ledger dedupe |
|---:|---|---|---|---|---|
| 1 | http://www.worldofwarcraft.com/04-09/pvp/koreapvp/ss01.jpg | v37_no_provenance_route | False | False | no_matching_frozen_complete_prefix |
| 2 | http://www.worldofwarcraft.com/04-09/pvp/koreapvp/ss02.jpg | v37_no_provenance_route | False | False | no_matching_frozen_complete_prefix |
| 3 | http://www.worldofwarcraft.com/04-09/pvp/koreapvp/ss06.jpg | v37_no_provenance_route | False | False | no_matching_frozen_complete_prefix |
| 4 | http://www.worldofwarcraft.com/04-09/pvp/koreapvp/ss05.jpg | v37_no_provenance_route | False | False | no_matching_frozen_complete_prefix |
| 5 | http://www.worldofwarcraft.com/04-09/pvp/koreapvp/ss04.jpg | v37_no_provenance_route | False | False | no_matching_frozen_complete_prefix |
| 6 | http://www.worldofwarcraft.com/04-09/pvp/koreapvp/ss07.jpg | v37_no_provenance_route | False | False | no_matching_frozen_complete_prefix |

The queue excludes files that are already present with canonical host identity and matching bytes/SHA. A path-only or host-mismatched match is retained separately and never treated as a US canonical resource. No URL was requested or accepted.
