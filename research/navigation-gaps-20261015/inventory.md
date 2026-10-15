# Navigation gaps local inventory (2026-10-15)

This report is local-only. It reads the frozen 2008-05-12 mirror, the frozen build manifest, and the existing `pages-local-maintenance-20261014-v5` preview. No network acquisition was performed.

Anchor: `20080512210044` (`2008-05-12`). Frozen `offline/site` and `offline/build-manifest.json` were not modified. Ignored paths are not treated as evidence of absence.

## Archived News first check

- `game_guide_navigation` `mirror/20080512/www.worldofwarcraft.com/shared/wow-com/includes-client/navtree.js:647` — `Archived News` → `/info/archivednews.html`; status `content_route`; export `.scratch/pages-local-maintenance-20261014-v5/info/archivednews.html`; 155598 bytes; title `WoW -> News -> Archived News`; `69` explicit offline-missing references.
- `legacy_menu1` `mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu1_var.js:132` — `Archived News` → ``; status `external_or_dynamic`; export `None`; None bytes; title `None`; `0` explicit offline-missing references.
- `legacy_menu3` `mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu3_var.js:135` — `Archived News` → `/info/archivednews.html`; status `content_route`; export `.scratch/pages-local-maintenance-20261014-v5/info/archivednews.html`; 155598 bytes; title `WoW -> News -> Archived News`; `69` explicit offline-missing references.
- `late_menu_xml` `research/site-recovery-2008/.menu.xml:5` — `Archived News` → `/news/wow-news-06-2006.html`; status `content_route`; export `.scratch/pages-local-maintenance-20261014-v5/news/wow-news-06-2006.html`; 115434 bytes; title `WoW -> Old News -> June, 2006`; `104` explicit offline-missing references.

Both `/info/archivednews.html` and the legacy `/news/wow-news-06-2006.html` are real local pages. Their missing references are external or uncollected links inside otherwise readable historical pages; they are not empty route placeholders.

## Coverage summary

Entries after exact `(label, href, source role)` de-duplication: **588**; distinct local routes: **411**.

| Section | Entries |
| --- | ---: |
| Community | 58 |
| Game Guide | 470 |
| Media | 33 |
| News | 10 |
| Workshop | 17 |

| Status | Entries |
| --- | ---: |
| `content_route` | 563 |
| `external_or_dynamic` | 22 |
| `missing_export_route` | 3 |

## Candidate repair and acquisition queue

| Priority | Action | Route / node | Current evidence |
| --- | --- | --- | --- |
| P0 | publish_or_route-verify-existing-content | `/info/archivednews.html` | content_route |
| P0 | publish_or_route-verify-existing-content | `/info/archivednews.html` | content_route |
| P0 | publish_or_route-verify-existing-content | `/news/wow-news-06-2006.html` | content_route |
| P1 | repair-derived-navigation-node-id | `main_navigation:Menu1_6_10` | navtree-main assigns Menu1_6_10 twice; the later Fan Sites assignment overwrites Fan Wallpapers in runtime JavaScript |
| P2 |  | `/burningcrusade/trial/index.html` | missing_export_route |
| P2 |  | `/pvp/flash-rewards/` | missing_export_route |
| P2 |  | `/wrath/wallpapers.xml` | missing_export_route |

## Navigation coverage table

| Section | Label | Original href | Current status | Route / source evidence |
| --- | --- | --- | --- | --- |
| Community | Community | `/community/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community.html` |
| Community | Forums | `http://forums.worldofwarcraft.com/` | `external_or_dynamic` | `—` |
| Community | Fan Wallpapers | `/downloads/wallpapers/fan-wallpapers/` | `content_route`; duplicate id | `.scratch/pages-local-maintenance-20261014-v5/downloads/wallpapers/fan-wallpapers.html` |
| Community | Fan Sites | `/community/fansites.html` | `content_route`; duplicate id | `.scratch/pages-local-maintenance-20261014-v5/community/fansites.html` |
| Community | Comics | `/community/comics.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics.html` |
| Community | April, 2008 Comics | `/community/comics/2008-04.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2008-04.html` |
| Community | July, 2007 Comics | `/community/comics/2007-07.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2007-07.html` |
| Community | June, 2007 Comics | `/community/comics/2007-06.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2007-06.html` |
| Community | May, 2007 Comics | `/community/comics/2007-05.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2007-05.html` |
| Community | April, 2007 Comics | `/community/comics/2007-04.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2007-04.html` |
| Community | March, 2007 Comics | `/community/comics/2007-03.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2007-03.html` |
| Community | February, 2007 Comics | `/community/comics/2007-02.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2007-02.html` |
| Community | January, 2007 Comics | `/community/comics/2007-01.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2007-01.html` |
| Community | December, 2006 Comics | `/community/comics/2006-12.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2006-12.html` |
| Community | November, 2006 Comics | `/community/comics/2006-11.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2006-11.html` |
| Community | October, 2006 Comics | `/community/comics/2006-10.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2006-10.html` |
| Community | March, 2008 Comics | `/community/comics/2008-03.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2008-03.html` |
| Community | September, 2006 Comics | `/community/comics/2006-09.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2006-09.html` |
| Community | August, 2006 Comics | `/community/comics/2006-08.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2006-08.html` |
| Community | July, 2006 Comics | `/community/comics/2006-07.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2006-07.html` |
| Community | June, 2006 Comics | `/community/comics/2006-06.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2006-06.html` |
| Community | May, 2006 Comics | `/community/comics/2006-05.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2006-05.html` |
| Community | PA Comics | `/community/pa-comics.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/pa-comics.html` |
| Community | February, 2008 Comics | `/community/comics/2008-02.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2008-02.html` |
| Community | January, 2008 Comics | `/community/comics/2008-01.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2008-01.html` |
| Community | December, 2007 Comics | `/community/comics/2007-12.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2007-12.html` |
| Community | November, 2007 Comics | `/community/comics/2007-11.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2007-11.html` |
| Community | October, 2007 Comics | `/community/comics/2007-10.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2007-10.html` |
| Community | September, 2007 Comics | `/community/comics/2007-09.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2007-09.html` |
| Community | August, 2007 Comics | `/community/comics/2007-08.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics/2007-08.html` |
| Community | Community Spotlight | `/community/communitylinks.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/communitylinks.html` |
| Community | Contests | `/contests/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/contests.html` |
| Community | Machinima | `/community/machinima/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/machinima.html` |
| Community | Welcome | `/community/machinima/welcome.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/machinima/welcome.html` |
| Community | Fair-Use Guide | `/community/machinima/letter.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/machinima/letter.html` |
| Community | Movies | `/community/machinima/movies.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/machinima/movies.html` |
| Community | Guild Relations | `/community/guildrelations.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/guildrelations.html` |
| Community | Guild Nexus | `/community/guildnexus.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/guildnexus.html` |
| Community | Player Stories | `/community/stories/index.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/stories/index.xml.html` |
| Community | Current Stories | `/community/stories/stories.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/stories/stories.xml.html` |
| Community | Story Archive | `/community/stories/archive.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/stories/archive.xml.html` |
| Community | Submit a Story | `/community/stories/submit.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/stories/submit.html` |
| Community | Real-Life Events | `/community/reallifeevents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/reallifeevents.html` |
| Community | Blizzard Regionals | `/community/tournaments/euregionals/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/tournaments/euregionals/index.html` |
| Community | Lanwar '06 | `/community/tournaments/lanwar.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/tournaments/lanwar.html` |
| Community | CPL '06 | `/community/tournaments/cpl.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/tournaments/cpl.html` |
| Community | Fan Art | `http://www.blizzard.com/us/inblizz/fanart/ScreenShot.html` | `external_or_dynamic` | `—` |
| Community | Overview | `/community/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community.html` |
| Community | Fansites | `/community/fansites.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/fansites.html` |
| Community | Fan Wallpapers | `/downloads/wallpapers/fan-wallpapers/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/downloads/wallpapers/fan-wallpapers.html` |
| Community | Beta Signup | `/misc/beta-signup.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/misc/beta-signup.html` |
| Community | Comics | `/community/comics.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/comics.html` |
| Community | Machinima | `/community/machinima/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/machinima.html` |
| Community | Player Stories | `/community/stories/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/stories.html` |
| Community | Contests | `/contests/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/contests.html` |
| Community | Guild Relations | `/community/guildrelations.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/guildrelations.html` |
| Community | Real-Life Events | `/community/reallifeevents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/reallifeevents.html` |
| Community | Fan Art | `http://www.blizzard.com/inblizz/fanart/` | `external_or_dynamic` | `—` |
| Game Guide | Game Guide | `/info/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Introduction | `/info/#introduction` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | General FAQ | `/info/faq/general.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/general.html` |
| Game Guide | Horde vs Alliance | `/info/faq/hordevalliance.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/hordevalliance.html` |
| Game Guide | Items | `/info/faq/items.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/items.html` |
| Game Guide | NPCs | `/info/faq/npcs.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/npcs.html` |
| Game Guide | Paid Character Transfer | `http://www.blizzard.com/support/wowbilling/?id=abl02008p` | `external_or_dynamic` | `—` |
| Game Guide | Parental Controls | `http://www.blizzard.com/support/wowbilling/?id=abl01917p` | `external_or_dynamic` | `—` |
| Game Guide | Patches | `/info/faq/patches.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/patches.html` |
| Game Guide | PTR | `/info/faq/ptr.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/ptr.html` |
| Game Guide | Recruit-A-Friend | `http://www.blizzard.com/support/wowbilling/?id=abl01997p` | `external_or_dynamic` | `—` |
| Game Guide | Scroll of Resurrection | `http://www.blizzard.com/support/wowbilling/?id=abl02140p` | `external_or_dynamic` | `—` |
| Game Guide | Quests | `/info/faq/quests.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/quests.html` |
| Game Guide | Battlegrounds | `/pvp/battlegrounds/faq.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/faq.html` |
| Game Guide | Races | `/info/faq/races.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/races.html` |
| Game Guide | Realms | `/info/faq/realms.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/realms.html` |
| Game Guide | Skills | `/info/faq/skills.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/skills.html` |
| Game Guide | Spells | `/info/faq/spells.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/spells.html` |
| Game Guide | Support | `/info/faq/support.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/support.html` |
| Game Guide | Technology | `/info/faq/technology.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/technology.html` |
| Game Guide | Transportation | `/info/faq/transportation.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/transportation.html` |
| Game Guide | World | `/info/faq/world.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/world.html` |
| Game Guide | Burning Crusade | `/burningcrusade/faq.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/burningcrusade/faq.html` |
| Game Guide | Wrath of Lich King | `/wrath/faq.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/wrath/faq.xml.html` |
| Game Guide | Blizzard Downloader | `/info/faq/blizzarddownloader.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/blizzarddownloader.html` |
| Game Guide | Character | `/info/faq/characters.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/characters.html` |
| Game Guide | Classes | `/info/faq/classes.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/classes.html` |
| Game Guide | Dungeons | `/info/faq/dungeons.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/dungeons.html` |
| Game Guide | Gameplay | `/info/faq/gameplay.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/gameplay.html` |
| Game Guide | Guide | `/info/faq/guide.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/guide.html` |
| Game Guide | Honor System | `/pvp/honor-system-faq.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/honor-system-faq.html` |
| Game Guide | Encyclopedia | `/info/encyclopedia/index.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/encyclopedia/index.xml.html` |
| Game Guide | Timeline | `/info/story/timeline.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/timeline.html` |
| Game Guide | History | `/info/story/timeline.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/timeline.html` |
| Game Guide | Chapter 1 | `/info/story/chapter1.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/chapter1.html` |
| Game Guide | Chapter 2 | `/info/story/chapter2.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/chapter2.html` |
| Game Guide | Chapter 3 | `/info/story/chapter3.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/chapter3.html` |
| Game Guide | Chapter 4 | `/info/story/chapter4.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/chapter4.html` |
| Game Guide | Chapter 5 | `/info/story/chapter5.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/chapter5.html` |
| Game Guide | Chapter 6 | `/info/story/chapter6.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/chapter6.html` |
| Game Guide | Lore | `/info/story/index.html#lore` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/index.html` |
| Game Guide | The Murlocs | `/misc/murloclore/murlocs.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/misc/murloclore/murlocs.html` |
| Game Guide | Road to Damnation | `/info/underdev/1p11/roadtodamnation.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/underdev/1p11/roadtodamnation.html` |
| Game Guide | Shifting Sands | `/info/story/shiftingsands.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/shiftingsands.html` |
| Game Guide | The Trolls | `/info/story/troll/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/troll.html` |
| Game Guide | History 1 | `/info/story/troll/history.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/troll/history.html` |
| Game Guide | Ice Troll Tribes | `/info/story/troll/icetribes.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/troll/icetribes.html` |
| Game Guide | Sand Trolls | `/info/story/troll/sandtrolls.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/troll/sandtrolls.html` |
| Game Guide | Sand Troll Tribes | `/info/story/troll/sandtribes.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/troll/sandtribes.html` |
| Game Guide | Other Trolls | `/info/story/troll/othertrolls.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/troll/othertrolls.html` |
| Game Guide | History 2 | `/info/story/troll/history2.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/troll/history2.html` |
| Game Guide | Biology | `/info/story/troll/biology.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/troll/biology.html` |
| Game Guide | Trivia | `/info/story/troll/trollsandnightelves.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/troll/trollsandnightelves.html` |
| Game Guide | Forest Trolls | `/info/story/troll/foresttrolls.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/troll/foresttrolls.html` |
| Game Guide | Forest Troll Tribes | `/info/story/troll/foresttribes.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/troll/foresttribes.html` |
| Game Guide | Jungle Trolls | `/info/story/troll/jungletrolls.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/troll/jungletrolls.html` |
| Game Guide | Jungle Troll Tribes | `/info/story/troll/jungletribes.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/troll/jungletribes.html` |
| Game Guide | Ice Trolls | `/info/story/troll/icetrolls.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/troll/icetrolls.html` |
| Game Guide | Undead Plague | `/info/story/undeadplague.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/undeadplague.html` |
| Game Guide | The Story So Far | `/burningcrusade/townhall/story.html#top` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/burningcrusade/townhall/story.html` |
| Game Guide | Shaman/Paladins | `/burningcrusade/townhall/classcombo.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/burningcrusade/townhall/classcombo.html` |
| Game Guide | Unbroken | `/info/story/unbroken/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/unbroken.html` |
| Game Guide | Rise of Lich King | `/wrath/features/story/story.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/wrath/features/story/story.xml.html` |
| Game Guide | About Game Guide | `/info/faq/guide.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/guide.html` |
| Game Guide | Archived News | `/info/archivednews.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/archivednews.html` |
| Game Guide | Content Index | `/info/basics/content-index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/content-index.html` |
| Game Guide | Credits | `/info/credits.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/credits.html` |
| Game Guide | Report Errors | `/info/faq/guide.html#errors` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/guide.html` |
| Game Guide | General Links | `/info/basics/general-links.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/general-links.html` |
| Game Guide | Intro to WoW | `/info/beginners/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/beginners/index.html` |
| Game Guide | Credits | `/info/basics/classic-credits.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/classic-credits.html` |
| Game Guide | Classic Credits | `/info/basics/classic-credits.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/classic-credits.html` |
| Game Guide | BC Credits | `/info/basics/bc-credits.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/bc-credits.html` |
| Game Guide | What is WoW | `/info/basics/guide.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/guide.html` |
| Game Guide | Features | `/features/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/features/index.html` |
| Game Guide | WoW Classic | `/misc/features.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/misc/features.html` |
| Game Guide | Burning Crusade | `/info/burningcrusade/index.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/burningcrusade/index.xml.html` |
| Game Guide | Wrath | `/wrath/features.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/wrath/features.xml.html` |
| Game Guide | Look & Feel | `/info/beginners/index.html#lookAndFeel` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/beginners/index.html` |
| Game Guide | Story | `/info/story/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/index.html` |
| Game Guide | Awards | `/misc/awards.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/misc/awards.html` |
| Game Guide | FAQ | `/info/faq/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq.html` |
| Game Guide | System Req. | `/info/faq/technology.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/technology.html` |
| Game Guide | Classic System Req. | `/info/faq/technology.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/technology.html` |
| Game Guide | BC System Req. | `/burningcrusade/faq.html#sys` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/burningcrusade/faq.html` |
| Game Guide | Free Trials | `http://www.worldofwarcraft.com/burningcrusade/trial/index.html?referrer=WORLDOFWARCRAFT&source=wowhome&promo=1` | `missing_export_route` | `—` |
| Game Guide | Getting Started | `/info/#gettingstarted` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Quick Start | `/info/basics/gettingstarted.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/gettingstarted.html` |
| Game Guide | Small Pets | `/info/basics/smallpets.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/smallpets.html` |
| Game Guide | Items | `/info/items/basics.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/items/basics.html` |
| Game Guide | Monster Basics | `/info/basics/monsterbasics.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/monsterbasics.html` |
| Game Guide | NPCs | `/info/basics/npcs.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/npcs.html` |
| Game Guide | Rest System | `/info/basics/resting.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/resting.html` |
| Game Guide | Glossary | `/info/basics/glossary.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/glossary.html` |
| Game Guide | Realm Types | `/info/basics/realmtypes.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/realmtypes.html` |
| Game Guide | First Few Levels | `/info/basics/firstfewlevels.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/firstfewlevels.html` |
| Game Guide | Character Attributes | `/info/basics/characters.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/characters.html` |
| Game Guide | Character Titles | `/info/basics/titles.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/titles.html` |
| Game Guide | Controls | `/info/basics/controls.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/controls.html` |
| Game Guide | Chat | `/info/basics/chat.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/chat.html` |
| Game Guide | Overview | `/info/basics/chat-overview.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/chat-overview.html` |
| Game Guide | Customization | `/info/basics/chat-customization.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/chat-customization.html` |
| Game Guide | Other | `/info/basics/chat-other.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/chat-other.html` |
| Game Guide | Q and A | `/info/basics/chat-qna.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/chat-qna.html` |
| Game Guide | Command Glossary | `/info/basics/chat-commandglossary.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/chat-commandglossary.html` |
| Game Guide | Emotes | `/info/basics/emotes.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/emotes.html` |
| Game Guide | Dancing | `/info/races/dancing.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/races/dancing.html` |
| Game Guide | High-End Content | `/info/basics/highleveloptions.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/highleveloptions.html` |
| Game Guide | Macros | `/info/basics/macros.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/macros.html` |
| Game Guide | Slash Commands | `/info/basics/slashcommands.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/slashcommands.html` |
| Game Guide | Combat | `/info/basics/combat.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/combat.html` |
| Game Guide | Death System | `/info/basics/death.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/death.html` |
| Game Guide | Duels | `/info/basics/duels.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/duels.html` |
| Game Guide | Resistances | `/info/basics/resistances.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/resistances.html` |
| Game Guide | Spells & Abilities | `/info/basics/spells.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/spells.html` |
| Game Guide | Quests | `/info/basics/quests.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/quests.html` |
| Game Guide | Basics | `/info/basics/questbasics.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/questbasics.html` |
| Game Guide | Levels | `/info/basics/questlevels.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/questlevels.html` |
| Game Guide | Management | `/info/basics/questmanagement.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/questmanagement.html` |
| Game Guide | Daily Quests | `/info/basics/dailyquests.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/dailyquests.html` |
| Game Guide | Combat Pets | `/info/basics/combatpets.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/combatpets.html` |
| Game Guide | Guide | `/info/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Character | `/info/#character` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Game Guide | `/info/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Races | `/info/races/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/races/index.html` |
| Game Guide | FAQ | `/info/faq/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq.html` |
| Game Guide | Draenei | `/info/races/draenei.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/races/draenei.html` |
| Game Guide | Undead | `/info/races/undead.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/races/undead.html` |
| Game Guide | Dwarves | `/info/races/dwarves.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/races/dwarves.html` |
| Game Guide | Gnomes | `/info/races/gnomes.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/races/gnomes.html` |
| Game Guide | Humans | `/info/races/humans.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/races/humans.html` |
| Game Guide | Night Elves | `/info/races/nightelves.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/races/nightelves.html` |
| Game Guide | Blood Elves | `/info/races/bloodelves.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/races/bloodelves.html` |
| Game Guide | Orcs | `/info/races/orcs.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/races/orcs.html` |
| Game Guide | Tauren | `/info/races/tauren.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/races/tauren.html` |
| Game Guide | Trolls | `/info/races/trolls.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/races/trolls.html` |
| Game Guide | Introduction | `/info/#introduction` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Classes | `/info/classes/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/index.html` |
| Game Guide | Druid | `/info/classes/druid/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/druid.html` |
| Game Guide | Class Links | `/info/classes/classlinks.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/classlinks.html` |
| Game Guide | Druid Spells | `/info/classes/druid/spells.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/druid/spells.html` |
| Game Guide | Druid Shape Shifting | `/info/classes/druid/shapeshifting.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/druid/shapeshifting.html` |
| Game Guide | Druid Tips | `/info/classes/druid/tips.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/druid/tips.html` |
| Game Guide | Talents | `/info/classes/druid/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/druid/talents.html` |
| Game Guide | Hunter | `/info/classes/hunter/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/hunter.html` |
| Game Guide | Hunter Spells | `/info/classes/hunter/spells.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/hunter/spells.html` |
| Game Guide | Hunter Pets | `/info/classes/hunter/pets.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/hunter/pets.html` |
| Game Guide | Hunter Tips | `/info/classes/hunter/tips.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/hunter/tips.html` |
| Game Guide | Talents | `/info/classes/hunter/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/hunter/talents.html` |
| Game Guide | Mage | `/info/classes/mage/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/mage.html` |
| Game Guide | Mage Spells | `/info/classes/mage/spells.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/mage/spells.html` |
| Game Guide | Mage Tips | `/info/classes/mage/tips.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/mage/tips.html` |
| Game Guide | Talents | `/info/classes/mage/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/mage/talents.html` |
| Game Guide | Paladin | `/info/classes/paladin/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/paladin.html` |
| Game Guide | Paladin Spells | `/info/classes/paladin/spells.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/paladin/spells.html` |
| Game Guide | Paladin Tips | `/info/classes/paladin/tips.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/paladin/tips.html` |
| Game Guide | Talents | `/info/classes/paladin/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/paladin/talents.html` |
| Game Guide | Priest | `/info/classes/priest/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/priest.html` |
| Game Guide | Priest Spells | `/info/classes/priest/spells.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/priest/spells.html` |
| Game Guide | Talents | `/info/classes/priest/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/priest/talents.html` |
| Game Guide | Rogue | `/info/classes/rogue/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/rogue.html` |
| Game Guide | Rogue Spells | `/info/classes/rogue/spells.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/rogue/spells.html` |
| Game Guide | Rogue Tips | `/info/classes/rogue/tips.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/rogue/tips.html` |
| Game Guide | Talents | `/info/classes/rogue/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/rogue/talents.html` |
| Game Guide | Shaman | `/info/classes/shaman/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/shaman.html` |
| Game Guide | Shaman Spells | `/info/classes/shaman/spells.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/shaman/spells.html` |
| Game Guide | Shaman Totems | `/info/classes/shaman/totems.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/shaman/totems.html` |
| Game Guide | Shaman Tips | `/info/classes/shaman/tips.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/shaman/tips.html` |
| Game Guide | Talents | `/info/classes/shaman/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/shaman/talents.html` |
| Game Guide | Warlock | `/info/classes/warlock/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/warlock.html` |
| Game Guide | Warlock Spells | `/info/classes/warlock/spells.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/warlock/spells.html` |
| Game Guide | Warlock Tips | `/info/classes/warlock/tips.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/warlock/tips.html` |
| Game Guide | Talents | `/info/classes/warlock/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/warlock/talents.html` |
| Game Guide | Warrior | `/info/classes/warrior/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/warrior.html` |
| Game Guide | Warrior Spells | `/info/classes/warrior/spells.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/warrior/spells.html` |
| Game Guide | Warrior Tips | `/info/classes/warrior/tips.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/warrior/tips.html` |
| Game Guide | Talents | `/info/classes/warrior/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/warrior/talents.html` |
| Game Guide | Getting Started | `/info/#gettingstarted` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Talents | `/info/classes/talent-index/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/talent-index.html` |
| Game Guide | Talent Basics | `/info/basics/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/talents.html` |
| Game Guide | Warrior | `/info/classes/warrior/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/warrior/talents.html` |
| Game Guide | Druid | `/info/classes/druid/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/druid/talents.html` |
| Game Guide | Hunter | `/info/classes/hunter/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/hunter/talents.html` |
| Game Guide | Mage | `/info/classes/mage/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/mage/talents.html` |
| Game Guide | Paladin | `/info/classes/paladin/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/paladin/talents.html` |
| Game Guide | Priest | `/info/classes/priest/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/priest/talents.html` |
| Game Guide | Rogue | `/info/classes/rogue/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/rogue/talents.html` |
| Game Guide | Shaman | `/info/classes/shaman/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/shaman/talents.html` |
| Game Guide | Warlock | `/info/classes/warlock/talents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/warlock/talents.html` |
| Game Guide | Character | `/info/#character` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Professions | `/info/professions/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/professions/index.html` |
| Game Guide | Introduction | `/info/professions/intro.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/professions/intro.html` |
| Game Guide | Herbalism | `/info/professions/herbalism.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/professions/herbalism.html` |
| Game Guide | Leatherworking | `/info/professions/leatherworking.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/professions/leatherworking.html` |
| Game Guide | Mining | `/info/professions/mining.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/professions/mining.html` |
| Game Guide | Skinning | `/info/professions/skinning.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/professions/skinning.html` |
| Game Guide | Tailoring | `/info/professions/tailoring.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/professions/tailoring.html` |
| Game Guide | Jewelcrafting | `/info/professions/jewelcrafting.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/professions/jewelcrafting.html` |
| Game Guide | Socketed Items | `/info/items/socketeditems.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/items/socketeditems.html` |
| Game Guide | Profession Links | `/info/professions/professionlinks.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/professions/professionlinks.html` |
| Game Guide | Basics | `/info/professions/basics.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/professions/basics.html` |
| Game Guide | Alchemy | `/info/professions/alchemy.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/professions/alchemy.html` |
| Game Guide | Blacksmithing | `/info/professions/blacksmithing.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/professions/blacksmithing.html` |
| Game Guide | Cooking | `/info/professions/cooking.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/professions/cooking.html` |
| Game Guide | Enchanting | `/info/professions/enchanting.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/professions/enchanting.html` |
| Game Guide | Engineering | `/info/professions/engineering.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/professions/engineering.html` |
| Game Guide | First Aid | `/info/professions/firstaid.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/professions/firstaid.html` |
| Game Guide | Fishing | `/info/professions/fishing.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/professions/fishing.html` |
| Game Guide | Items | `/info/#items` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | World Locations | `/info/#world` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Transportation | `/info/#transportation` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Player Interaction | `/info/#playerinteraction` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Player vs Player | `/info/#pvp` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Reputations | `/info/basics/reputation.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/reputation.html` |
| Game Guide | Basics | `/info/basics/reputation.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/reputation.html` |
| Game Guide | Classic | `/info/basics/factions/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions.html` |
| Game Guide | Argent Dawn | `/info/basics/factions/argent/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/argent/index.html` |
| Game Guide | Brood of Nozdormu | `/info/basics/factions/broodofnozdormu/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/broodofnozdormu/index.html` |
| Game Guide | Cenarion Circle | `/info/basics/factions/cenarion/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/cenarion/index.html` |
| Game Guide | Darkmoon Faire | `/info/basics/factions/darkmoon/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/darkmoon/index.html` |
| Game Guide | Rewards | `/info/basics/factions/darkmoon/rewards.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/darkmoon/rewards.html` |
| Game Guide | Fortune Teller | `/info/basics/factions/darkmoon/buffs.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/darkmoon/buffs.html` |
| Game Guide | Thorium Brotherhood | `/info/basics/factions/thorium/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/thorium/index.html` |
| Game Guide | Timbermaw Hold | `/info/basics/factions/timbermaw/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/timbermaw/index.html` |
| Game Guide | Zandalar Tribe | `/info/basics/factions/zandalar/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/zandalar/index.html` |
| Game Guide | Vendor Rewards | `/info/basics/factions/zandalar/vendor.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/zandalar/vendor.html` |
| Game Guide | Class Quest Rewards | `/info/basics/factions/zandalar/quests.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/zandalar/quests.html` |
| Game Guide | Burning Crusade | `/info/basics/reputation.html#BC` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/reputation.html` |
| Game Guide | Hellfire Peninsula | `/info/basics/factions/hellfire/hellfire.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/hellfire/hellfire.xml.html` |
| Game Guide | The Sha'tar | `/info/basics/factions/shatar/shatar.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/shatar/shatar.xml.html` |
| Game Guide | Keepers of Time | `/info/basics/factions/keepers/keepers.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/keepers/keepers.xml.html` |
| Game Guide | Scale of the Sands | `/info/basics/factions/keepers/scale.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/keepers/scale.xml.html` |
| Game Guide | Nagrand | `/info/basics/factions/nagrand/nagrand.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/nagrand/nagrand.xml.html` |
| Game Guide | Nagrand PvP | `/info/basics/factions/halaa/halaa.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/halaa/halaa.xml.html` |
| Game Guide | Violet Eye | `/info/basics/factions/violeteye/violeteye.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/violeteye/violeteye.xml.html` |
| Game Guide | Violet Eye Rings | `/info/basics/factions/violeteye/violeteyerings.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/violeteye/violeteyerings.xml.html` |
| Game Guide | Ogri'la | `http://armory.worldofwarcraft.com/search.xml?fl[source]=reputation&fl[faction]=1038&searchType=items` | `external_or_dynamic` | `—` |
| Game Guide | Ogri'la Tips | `/info/basics/factions/ogrila-tips.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/ogrila-tips.html` |
| Game Guide | Sha'tari Skyguard | `http://armory.worldofwarcraft.com/search.xml?fl[source]=reputation&fl[faction]=1031&searchType=items` | `external_or_dynamic` | `—` |
| Game Guide | Sha'tari Skyguard Tips | `/info/basics/factions/skyguard-tips.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/skyguard-tips.html` |
| Game Guide | Netherwing | `http://armory.worldofwarcraft.com/search.xml?fl[source]=reputation&fl[faction]=1015&searchType=items` | `external_or_dynamic` | `—` |
| Game Guide | Netherwing Tips | `/info/basics/factions/netherwing-tips.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/netherwing-tips.html` |
| Game Guide | Hellfire PvP | `/info/basics/factions/hellfire/hellfire-tokens.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/hellfire/hellfire-tokens.xml.html` |
| Game Guide | Ashtongue | `http://armory.worldofwarcraft.com/search.xml?fl[source]=reputation&fl[faction]=1012&searchType=items` | `external_or_dynamic` | `—` |
| Game Guide | Badges of Justice | `/info/basics/factions/badgesofjustice/badges-of-justice.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/badgesofjustice/badges-of-justice.html` |
| Game Guide | Badges of Justice 2 | `/info/basics/factions/badgesofjustice/badges-of-justice2.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/badgesofjustice/badges-of-justice2.html` |
| Game Guide | Cenarion Expedition | `/info/basics/factions/cenarionxp/cenarionxp.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/cenarionxp/cenarionxp.xml.html` |
| Game Guide | Sporeggar | `/info/basics/factions/sporeggar/sporeggar.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/sporeggar/sporeggar.xml.html` |
| Game Guide | Zangarmarsh PvP | `/info/basics/factions/zangarmarsh/zangarpvp.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/zangarmarsh/zangarpvp.xml.html` |
| Game Guide | Inscriptions | `/info/basics/factions/aldorscryers/aldor-scryers-tokens.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/aldorscryers/aldor-scryers-tokens.xml.html` |
| Game Guide | Lower City | `/info/basics/factions/lowercity/lowercity.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/lowercity/lowercity.xml.html` |
| Game Guide | The Consortium | `/info/basics/factions/consortium/consortium.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/consortium/consortium.xml.html` |
| Game Guide | Bone Wastes | `/info/basics/factions/bonewastes/bonewastes.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/bonewastes/bonewastes.xml.html` |
| Game Guide | Armory Listing | `http://armory.worldofwarcraft.com/factions.xml` | `external_or_dynamic` | `—` |
| Game Guide | Items | `/info/#items` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Basics | `/info/items/basics.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/items/basics.html` |
| Game Guide | Trading | `/info/basics/trading.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/trading.html` |
| Game Guide | Auction Houses | `/info/basics/auctionhouses.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/auctionhouses.html` |
| Game Guide | Auction House Tips | `/info/basics/auctionhousetips.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/auctionhousetips.html` |
| Game Guide | Chat Auctions | `/info/basics/chatauctions.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/chatauctions.html` |
| Game Guide | Food/Drink | `/info/basics/food.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/food.html` |
| Game Guide | High Level Armor Sets | `/info/items/armorsets/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/items/armorsets.html` |
| Game Guide | Item Database | `http://armory.worldofwarcraft.com/item-search.xml` | `external_or_dynamic` | `—` |
| Game Guide | Item Management | `/info/items/management.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/items/management.html` |
| Game Guide | Bags | `/info/basics/bags.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/bags.html` |
| Game Guide | Banking | `/info/basics/banking.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/banking.html` |
| Game Guide | Dressing Room | `/info/items/dressingroom/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/items/dressingroom.html` |
| Game Guide | Merchants | `/info/basics/merchants.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/merchants.html` |
| Game Guide | Mail | `/info/basics/mail.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mail.html` |
| Game Guide | The World | `/info/#world` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | World Map | `/info/flashmap/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/flashmap.html` |
| Game Guide | Outland Map | `/burningcrusade/townhall/outlandmap.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/burningcrusade/townhall/outlandmap.html` |
| Game Guide | Exploring the Map | `/info/basics/map.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/map.html` |
| Game Guide | Regions | `/info/basics/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics.html` |
| Game Guide | Region Levels | `/info/basics/regionlevels.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/regionlevels.html` |
| Game Guide | Silithus Intro | `/info/story/shiftingsands.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/shiftingsands.html` |
| Game Guide | Dungeons | `/info/basics/dungeons.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/dungeons.html` |
| Game Guide | Instancing | `/info/basics/instancing.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/instancing.html` |
| Game Guide | Dungeon Tips | `/info/basics/dungeontips.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/dungeontips.html` |
| Game Guide | Classic Dungeons | `/info/basics/worlddungeons.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | Blackfathom Deeps | `/info/basics/worlddungeons.html#Blackfathom Deeps` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | Razorfen Kraul | `/info/basics/worlddungeons.html#Razorfen Kraul` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | Scholomance | `/info/basics/worlddungeons.html#Scholomance` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | Shadowfang Keep | `/info/basics/worlddungeons.html#Shadowfang Keep` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | Stratholme | `/info/basics/worlddungeons.html#Stratholme` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | Scarlet Monastery | `/info/basics/worlddungeons.html#The Scarlet Monastery` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | The Stockades | `/info/basics/worlddungeons.html#The Stockades` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | The Sunken Temple | `/info/basics/worlddungeons.html#The Sunken Temple` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | Uldaman | `/info/basics/worlddungeons.html#Uldaman` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | Wailing Caverns | `/info/basics/worlddungeons.html#Wailing Caverns` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | Zul&#39;Farrak | `/info/basics/worlddungeons.html#ZulFarrak` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | Blackrock Depths | `/info/basics/worlddungeons.html#Blackrock Depths` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | Blackrock Spire | `/info/basics/worlddungeons.html#Blackrock Spire` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | Deadmines | `/info/basics/worlddungeons.html#Deadmines` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | Dire Maul | `/info/basics/worlddungeons.html#Dire Maul` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | Gnomeregan | `/info/basics/worlddungeons.html#Gnomeregan` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | Maraudon | `/info/basics/worlddungeons.html#Maraudon` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | Ragefire Chasm | `/info/basics/worlddungeons.html#Ragefire Chasm` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | Razorfen Downs | `/info/basics/worlddungeons.html#Razorfen Downs` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/worlddungeons.html` |
| Game Guide | BC Dungeons | `/info/basics/bcworlddungeons.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/bcworlddungeons.html` |
| Game Guide | Hellfire Citadel | `/info/dungeons/hellfire-citadel.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/dungeons/hellfire-citadel.xml.html` |
| Game Guide | Coilfang Reservoir | `/info/dungeons/coilfang-reservoir.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/dungeons/coilfang-reservoir.xml.html` |
| Game Guide | Auchindoun | `/info/dungeons/auchindoun.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/dungeons/auchindoun.xml.html` |
| Game Guide | Caverns of Time | `/info/dungeons/caverns-of-time.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/dungeons/caverns-of-time.xml.html` |
| Game Guide | Tempest Keep | `/info/dungeons/tempest-keep.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/dungeons/tempest-keep.xml.html` |
| Game Guide | Raid Areas | `/info/basics/raidarea.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/raidarea.html` |
| Game Guide | Raid Calendar | `/calendar/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/calendar.html` |
| Game Guide | Classic Raid Areas | `/info/basics/raidarea.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/raidarea.html` |
| Game Guide | Blackwing Lair | `/info/basics/raidarea.html#bwl` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/raidarea.html` |
| Game Guide | Molten Core | `/info/basics/raidarea.html#mc` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/raidarea.html` |
| Game Guide | Onyxia&#39;s Lair | `/info/basics/raidarea.html#onx` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/raidarea.html` |
| Game Guide | Zul&#39;Gurub | `/info/basics/raidarea.html#ZG` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/raidarea.html` |
| Game Guide | Ahn&#39;Qiraj | `/info/basics/raidarea.html#aq20` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/raidarea.html` |
| Game Guide | AQ Ranking | `/wareffort/servers.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/wareffort/servers.html` |
| Game Guide | AQ Server Stats | `/wareffort/wareffort.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/wareffort/wareffort.html` |
| Game Guide | Obsidian Destroyers | `/info/raiddungeons/ahnqiraj/obsidian.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/raiddungeons/ahnqiraj/obsidian.html` |
| Game Guide | Moam | `/info/raiddungeons/ahnqiraj/moam.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/raiddungeons/ahnqiraj/moam.html` |
| Game Guide | Anubisaths | `/info/raiddungeons/ahnqiraj/anubisath.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/raiddungeons/ahnqiraj/anubisath.html` |
| Game Guide | Ossirian | `/info/raiddungeons/ahnqiraj/ossirian.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/raiddungeons/ahnqiraj/ossirian.html` |
| Game Guide | Naxxaramas | `/info/basics/raidarea.html#naxx` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/raidarea.html` |
| Game Guide | Outdoor | `/info/basics/raidarea.html#outdoor` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/raidarea.html` |
| Game Guide | BC Raid Areas | `/info/basics/bcraidarea.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/bcraidarea.html` |
| Game Guide | Magtheridon's Lair | `/info/dungeons/hellfire-citadel.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/dungeons/hellfire-citadel.xml.html` |
| Game Guide | Doomwalker | `/info/dungeons/doomwalker.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/dungeons/doomwalker.xml.html` |
| Game Guide | Serpentshrine Cavern | `/info/dungeons/coilfang-reservoir.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/dungeons/coilfang-reservoir.xml.html` |
| Game Guide | Tempest Keep: The Eye | `/info/dungeons/tempest-keep.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/dungeons/tempest-keep.xml.html` |
| Game Guide | Gruul's Lair | `/info/dungeons/gruuls-lair.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/dungeons/gruuls-lair.xml.html` |
| Game Guide | The Battle for Mount Hyjal | `/info/dungeons/caverns-of-time.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/dungeons/caverns-of-time.xml.html` |
| Game Guide | Black Temple | `/info/dungeons/black-temple.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/dungeons/black-temple.xml.html` |
| Game Guide | Karazhan | `/info/dungeons/karazhan.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/dungeons/karazhan.xml.html` |
| Game Guide | Zul'Aman | `/info/dungeons/zulaman.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/dungeons/zulaman.xml.html` |
| Game Guide | Doom Lord Kazzak | `/info/dungeons/doom-lord-kazzak.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/dungeons/doom-lord-kazzak.xml.html` |
| Game Guide | Major Cities | `/info/basics/cities.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/cities.html` |
| Game Guide | Darnassus | `/info/basics/cities.html#darnassus` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/cities.html` |
| Game Guide | Ironforge | `/info/basics/cities.html#ironforge` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/cities.html` |
| Game Guide | Orgrimmar | `/info/basics/cities.html#orgrimmar` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/cities.html` |
| Game Guide | Stormwind | `/info/basics/cities.html#stormwind` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/cities.html` |
| Game Guide | Thunder Bluff | `/info/basics/cities.html#thunderbluff` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/cities.html` |
| Game Guide | Undercity | `/info/basics/cities.html#undercity` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/cities.html` |
| Game Guide | In-Game Events | `/community/ingameevents.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/ingameevents.html` |
| Game Guide | Events Calendar | `/info/events/calendar/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/events/calendar.html` |
| Game Guide | Winter Veil | `/info/events/winterveil/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/events/winterveil.html` |
| Game Guide | AQ War Effort | `/wareffort/servers.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/wareffort/servers.html` |
| Game Guide | Battlegrounds Holiday | `/community/ingameevents.html#calltoarms` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/ingameevents.html` |
| Game Guide | Darkmoon Faire Event | `/info/basics/factions/darkmoon/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/darkmoon.html` |
| Game Guide | Elemental Invasions | `/community/ingameevents.html#elemental` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/ingameevents.html` |
| Game Guide | Fishing Extravaganza | `/info/events/fishing/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/events/fishing.html` |
| Game Guide | Gurubashi Arena | `/community/ingameevents.html#gurubashi` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/ingameevents.html` |
| Game Guide | Scourge Invasion | `/info/events/scourgeinvasion/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/events/scourgeinvasion.html` |
| Game Guide | Brewfest | `/info/events/brewfest/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/events/brewfest.html` |
| Game Guide | New Year&#39;s Eve | `/info/events/newyears/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/events/newyears.html` |
| Game Guide | Lunar Festival | `/info/events/lunarnewyears/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/events/lunarnewyears.html` |
| Game Guide | Love is in the Air | `/info/events/loveisintheair/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/events/loveisintheair.html` |
| Game Guide | Noblegarden | `/community/ingameevents.html#noblegarden` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/community/ingameevents.html` |
| Game Guide | Children&#39;s Week | `/info/events/childrensweek/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/events/childrensweek.html` |
| Game Guide | Midsummer Fire Festival | `/info/events/midsummer/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/events/midsummer.html` |
| Game Guide | Harvest Festival | `/info/events/harvestfestival/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/events/harvestfestival.html` |
| Game Guide | Hallow&#39;s End | `/info/events/hallowsend/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/events/hallowsend.html` |
| Game Guide | Transportation | `/info/#transportation` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Mounts | `/info/basics/mounts/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/index.html` |
| Game Guide | Racial Mounts | `/info/basics/mounts/index.html#racial` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/index.html` |
| Game Guide | Horses | `/info/basics/mounts/horses.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/horses.html` |
| Game Guide | Hawkstriders | `/info/basics/mounts/hawkstriders.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/hawkstriders.html` |
| Game Guide | Kodos | `/info/basics/mounts/kodos.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/kodos.html` |
| Game Guide | Mechanostriders | `/info/basics/mounts/mechanostriders.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/mechanostriders.html` |
| Game Guide | Nightsabers | `/info/basics/mounts/nightsabers.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/nightsabers.html` |
| Game Guide | Rams | `/info/basics/mounts/rams.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/rams.html` |
| Game Guide | Raptors | `/info/basics/mounts/raptors.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/raptors.html` |
| Game Guide | Skeletal Horses | `/info/basics/mounts/skeletalhorses.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/skeletalhorses.html` |
| Game Guide | Wolves | `/info/basics/mounts/wolves.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/wolves.html` |
| Game Guide | Elekks | `/info/basics/mounts/elekks.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/elekks.html` |
| Game Guide | Class Mounts | `/info/basics/mounts/index.html#class` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/index.html` |
| Game Guide | Paladin Mounts | `/info/basics/mounts/paladin.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/paladin.html` |
| Game Guide | Warlock Mounts | `/info/basics/mounts/warlock.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/warlock.html` |
| Game Guide | Alterac Valley Mounts | `/info/basics/mounts/special.html#av` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/special.html` |
| Game Guide | PvP Reward Mounts | `/info/basics/mounts/special.html#pvp` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/special.html` |
| Game Guide | Talbuks | `/info/basics/mounts/special.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/special.html` |
| Game Guide | Special Mounts | `/info/basics/mounts/special.html#misc` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/special.html` |
| Game Guide | Flying Mounts | `/info/basics/mounts/flying.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/flying.html` |
| Game Guide | Public Transportation | `/info/basics/publictransportation.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/publictransportation.html` |
| Game Guide | Gryphons | `/info/basics/publictransportation.html#gryphons` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/publictransportation.html` |
| Game Guide | Hippogryphs | `/info/basics/publictransportation.html#hippogryphs` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/publictransportation.html` |
| Game Guide | Deeprun Tram | `/info/basics/publictransportation.html#deepruntram` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/publictransportation.html` |
| Game Guide | Wyverns | `/info/basics/publictransportation.html#wyverns` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/publictransportation.html` |
| Game Guide | Vampire Bats | `/info/basics/publictransportation.html#bats` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/publictransportation.html` |
| Game Guide | Goblin Zeppelin | `/info/basics/publictransportation.html#zeppelin` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/publictransportation.html` |
| Game Guide | Boats | `/info/basics/publictransportation.html#boats` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/publictransportation.html` |
| Game Guide | Transportation FAQ | `/info/faq/transportation.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/transportation.html` |
| Game Guide | Player Interaction | `/info/#playerinteraction` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Guilds | `/info/basics/guilds.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/guilds.html` |
| Game Guide | Joining Guilds | `/info/basics/joiningguilds.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/joiningguilds.html` |
| Game Guide | Guild Management | `/info/basics/guildtab.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/guildtab.html` |
| Game Guide | Guild Leadership | `/info/basics/guildleadership.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/guildleadership.html` |
| Game Guide | Guild Banks | `/info/basics/guildbanks.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/guildbanks.html` |
| Game Guide | Parties/Raids | `/info/basics/parties.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/parties.html` |
| Game Guide | Roles | `/info/basics/partyroles.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/partyroles.html` |
| Game Guide | Find a Party | `/info/basics/partygrouping.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/partygrouping.html` |
| Game Guide | Looking for Group | `/burningcrusade/townhall/lookingforgroup.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/burningcrusade/townhall/lookingforgroup.html` |
| Game Guide | Etiquette | `/info/basics/partyrules.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/partyrules.html` |
| Game Guide | Party Tips | `/info/basics/partytips.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/partytips.html` |
| Game Guide | Pulling | `/info/basics/partiespulling.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/partiespulling.html` |
| Game Guide | Crowd Control | `/info/basics/partycrowdcontrol.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/partycrowdcontrol.html` |
| Game Guide | Raid Groups | `/info/basics/raidgroups.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/raidgroups.html` |
| Game Guide | Raid Tips | `/info/basics/raidtips.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/raidtips.html` |
| Game Guide | How to Be Nice | `/info/basics/benice.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/benice.html` |
| Game Guide | Voice Chat | `/info/basics/voicechat.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/voicechat.html` |
| Game Guide | Q&A | `/info/basics/chat-qna.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/chat-qna.html` |
| Game Guide | Macro Guide I | `/info/basics/macroguide-one.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/macroguide-one.html` |
| Game Guide | Player vs Player | `/pvp/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp.html` |
| Game Guide | Arena | `/pvp/arena/index.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/arena/index.xml.html` |
| Game Guide | Halaa PvP Tips | `/pvp/worldpvp/halaa-tips.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/worldpvp/halaa-tips.xml.html` |
| Game Guide | Rewards | `http://www.wowarmory.com/pvprewards.xml` | `external_or_dynamic` | `—` |
| Game Guide | General Rewards | `/pvp/rewards-general.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/rewards-general.html` |
| Game Guide | Vindicator Rewards | `/pvp/rewards-vindicators-armor.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/rewards-vindicators-armor.html` |
| Game Guide | Level 60 and 70 Weapons | `/pvp/rewards-weapons.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/rewards-weapons.html` |
| Game Guide | Armor Sets | `/info/items/armorsets/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/items/armorsets.html` |
| Game Guide | Mounts | `/info/basics/mounts/special.html#pvp` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/mounts/special.html` |
| Game Guide | Alterac Valley Rewards | `/info/basics/factions/alterac/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/alterac/index.html` |
| Game Guide | Arathi Basin Rewards | `/info/basics/factions/arathi/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/arathi/index.html` |
| Game Guide | Warsong Gulch Rewards | `/info/basics/factions/warsong/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/warsong/index.html` |
| Game Guide | Arena Tournament | `http://armory.worldofwarcraft.com/arena-tournament.xml` | `external_or_dynamic` | `—` |
| Game Guide | Arena Intro | `/pvp/arena/index.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/arena/index.xml.html` |
| Game Guide | Inside Areas | `/insider/11/arena.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/insider/11/arena.xml.html` |
| Game Guide | Armory Listing | `http://armory.worldofwarcraft.com/pvprewards.xml` | `external_or_dynamic` | `—` |
| Game Guide | Honor System | `/pvp/honorguide.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/honorguide.html` |
| Game Guide | FAQ | `/pvp/honor-system-faq.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/honor-system-faq.html` |
| Game Guide | Ranks | `/pvp/ranks.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/ranks.html` |
| Game Guide | Honor vs. Arena | `/pvp/honorvsarena.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/honorvsarena.html` |
| Game Guide | PvP Combat | `/info/basics/pvpcombat.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/pvpcombat.html` |
| Game Guide | Surviving PvP | `/info/basics/survivingpvp.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/survivingpvp.html` |
| Game Guide | Battlegrounds | `/pvp/battlegrounds/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/index.html` |
| Game Guide | General Info | `/pvp/battlegrounds/info.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/info.html` |
| Game Guide | Queue System | `/pvp/battlegrounds/battlegrounds-queue-system.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/battlegrounds-queue-system.html` |
| Game Guide | Battlegroups | `/pvp/battlegrounds/battlegroups/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/battlegroups/index.html` |
| Game Guide | FAQ | `/pvp/battlegrounds/faq.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/faq.html` |
| Game Guide | Alterac Valley | `/pvp/battlegrounds/info-alteracvalley.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/info-alteracvalley.html` |
| Game Guide | Quests | `/pvp/battlegrounds/quests-alterac.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/quests-alterac.html` |
| Game Guide | Enemies | `/pvp/battlegrounds/enemies-alterac.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/enemies-alterac.html` |
| Game Guide | Map | `/pvp/battlegrounds/map-alterac.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/map-alterac.html` |
| Game Guide | Rewards | `/info/basics/factions/alterac/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/alterac/index.html` |
| Game Guide | Score Screen | `/pvp/battlegrounds/scores-alterac.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/scores-alterac.html` |
| Game Guide | Tips | `/pvp/battlegrounds/tips-alterac.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/tips-alterac.html` |
| Game Guide | Arathi Basin | `/pvp/battlegrounds/info-arathi.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/info-arathi.html` |
| Game Guide | Map | `/pvp/battlegrounds/map-arathi.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/map-arathi.html` |
| Game Guide | Rewards | `/info/basics/factions/arathi/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/arathi/index.html` |
| Game Guide | Score Screen | `/pvp/battlegrounds/scores-arathi.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/scores-arathi.html` |
| Game Guide | Warsong Gulch | `/pvp/battlegrounds/info-warsong.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/info-warsong.html` |
| Game Guide | Power-Ups | `/pvp/battlegrounds/powerups-warsong.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/powerups-warsong.html` |
| Game Guide | Rewards | `/info/basics/factions/warsong/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/basics/factions/warsong/index.html` |
| Game Guide | Score Screen | `/pvp/battlegrounds/scores-warsong.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/scores-warsong.html` |
| Game Guide | Eye of the Storm | `/pvp/battlegrounds/eyeofthestorm/index.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/eyeofthestorm/index.xml.html` |
| Game Guide | Horde vs Alliance FAQ | `/info/faq/hordevalliance.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/faq/hordevalliance.html` |
| Game Guide | Azeroth Outdoor PvP | `/pvp/outdoorpvp.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/outdoorpvp.xml.html` |
| Game Guide | Outland Outdoor PvP | `/pvp/worldpvp/index.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/worldpvp/index.xml.html` |
| Game Guide | Game Guide | `/info/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Player vs Player | `/info/#pvp` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | FAQ | `/info/#faq` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Story | `/info/story/index.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/story/index.html` |
| Game Guide | Burning Crusade | `/burningcrusade/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/burningcrusade.html` |
| Game Guide | Wrath of Lich King | `/wrath/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/wrath.html` |
| Game Guide | Under Development | `/info/underdev/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/underdev.html` |
| Game Guide | Previous Patches | `/info/underdev/implemented/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/underdev/implemented.html` |
| Game Guide | Introduction | `/info/#introduction` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Getting Started | `/info/#gettingstarted` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Character | `/info/#character` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Reputations | `/info/#reputations` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Items | `/info/#items` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | The World | `/info/#world` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Transportation | `/info/#transportation` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Game Guide | Player Interaction | `/info/#playerinteraction` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| Media | Media | `/burningcrusade/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/burningcrusade.html` |
| Media | Screenshots | `/burningcrusade/screenshots.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/burningcrusade/screenshots.html` |
| Media | Wallpapers | `/burningcrusade/wallpapers.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/burningcrusade/wallpapers.html` |
| Media | Movies | `/burningcrusade/movies.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/burningcrusade/movies.html` |
| Media | Media | `/wrath/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/wrath.html` |
| Media | Screenshots | `/wrath/screenshots.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/wrath/screenshots.xml.html` |
| Media | Wallpapers | `/wrath/wallpapers.xml` | `missing_export_route` | `—` |
| Media | Movies | `/wrath/movies.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/wrath/movies.xml.html` |
| Media | Media | `/downloads/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/downloads.html` |
| Media | Complete List | `/downloads/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/downloads.html` |
| Media | Screenshots | `http://www.worldofwarcraft.com/downloads/ssotd/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/downloads/ssotd.html` |
| Media | Movies | `/downloads/movies.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/downloads/movies.html` |
| Media | Music | `/downloads/sounds.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/downloads/sounds.html` |
| Media | Wallpapers | `/downloads/wallpapers.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/downloads/wallpapers.html` |
| Media | Other Downloads | `/downloads/other-downloads.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/downloads/other-downloads.html` |
| Media | Lords of the Dance | `/info/races/dancing.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/races/dancing.html` |
| Media | Media Player Skin | `/downloads/other-downloads.html#skins` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/downloads/other-downloads.html` |
| Media | Desktop Theme | `/downloads/other-downloads.html#themes` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/downloads/other-downloads.html` |
| Media | Custom UI Toolkit | `/ui/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/ui.html` |
| Media | Language Pack | `/downloads/languagepack-en.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/downloads/languagepack-en.xml.html` |
| Media | Paquete de Idiomas | `/downloads/languagepack-es.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/downloads/languagepack-es.xml.html` |
| Media | Gadgetzan Times | `/gadgetzan/archives.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/gadgetzan/archives.html` |
| Media | BlizzCast | `http://us.blizzard.com/blizzcast/` | `external_or_dynamic` | `—` |
| Media | Overview | `/downloads/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/downloads.html` |
| Media | BlizzCast | `http://us.blizzard.com/blizzcast` | `external_or_dynamic` | `—` |
| Media | Screenshots | `/downloads/ssotd/#latest` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/downloads/ssotd.html` |
| Media | Movies | `/downloads/movies.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/downloads/movies.html` |
| Media | Music | `/downloads/sounds.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/downloads/sounds.html` |
| Media | Wallpapers | `/downloads/wallpapers.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/downloads/wallpapers.html` |
| Media | Other Downloads | `/downloads/other-downloads.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/downloads/other-downloads.html` |
| Media | Gadgetzan Times | `/gadgetzantimes/archives.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/gadgetzantimes/archives.html` |
| Media | Blizzard Store | `http://shop.blizzard.com/` | `external_or_dynamic` | `—` |
| Media | Promotion | `/misc/promotion.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/misc/promotion.html` |
| News | Current News | `/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/index.html` |
| News | News | `/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/index.html` |
| News | Archived News | `/info/archivednews.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/archivednews.html` |
| News | Current News | `/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/index.html` |
| News | Guide News | `/info/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info.html` |
| News | Archived News | `` | `external_or_dynamic` | `—` |
| News | Current News | `/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/index.html` |
| News | Archived News | `/news/wow-news-06-2006.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/news/wow-news-06-2006.html` |
| News | Awards and Honors | `/misc/awards.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/misc/awards.html` |
| News | Press Releases | `http://www.blizzard.com/press/` | `external_or_dynamic` | `—` |
| Workshop | Workshop | `/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/index.html` |
| Workshop | PvP Rankings | `/pvp/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp.html` |
| Workshop | Talent Calculators | `/info/classes/talent-index/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/talent-index.html` |
| Workshop | Events Calendar | `/info/events/calendar/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/events/calendar.html` |
| Workshop | Raid Calendar | `/calendar/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/calendar.html` |
| Workshop | World Map | `/info/flashmap/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/flashmap.html` |
| Workshop | PvP Minisite | `/pvp/flash-rewards/` | `missing_export_route` | `—` |
| Workshop | War Effort Ranking | `/wareffort/servers.html` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/wareffort/servers.html` |
| Workshop | Armory | `http://www.wowarmory.com/` | `external_or_dynamic` | `—` |
| Workshop | Arena | `/misc/arenatournament/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/misc/arenatournament.html` |
| Workshop | Encyclopedia | `/info/encyclopedia/index.xml` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/encyclopedia/index.xml.html` |
| Workshop | Talent Calculators | `/info/classes/talent-index/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/classes/talent-index.html` |
| Workshop | Events Calendar | `/info/events/calendar/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/events/calendar.html` |
| Workshop | Armor Sets | `/info/items/armorsets/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/items/armorsets.html` |
| Workshop | World Map | `/info/flashmap/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/info/flashmap.html` |
| Workshop | Top Lists | `/toplist/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/toplist.html` |
| Workshop | Battlegroups | `/pvp/battlegrounds/battlegroups/` | `content_route` | `.scratch/pages-local-maintenance-20261014-v5/pvp/battlegrounds/battlegroups.html` |

## Evidence sources

- `mirror/20080512/www.worldofwarcraft.com/shared/wow-com/includes-client/navtree-main.js` — SHA-256 `f8a5b736dea8251dac9a975410c31007db9671999fde4f1ed9a23bf2f662b2b2`, 30327 bytes.
- `mirror/20080512/www.worldofwarcraft.com/shared/wow-com/includes-client/navtree.js` — SHA-256 `83555626f751c7b16efd8333ba3932c45b5b5f03bffed311a2a38b9763132e0b`, 74665 bytes.
- `mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu1_var.js` — SHA-256 `db6a8e2417adc01e542d4728a9223e38c304b188a1c1a3ba6466ef223223ea0b`, 13744 bytes.
- `mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu3_var.js` — SHA-256 `2e9e1caf73c2395e1280610ab6e7cf8821478d3a297d94bbc0669d9ab4054715`, 81806 bytes.
- `research/site-recovery-2008/.menu.xml` — SHA-256 `b17f55397b566f5a5f60be6dd4d9939169d1cfb31f9cea196493dd5bd37f51d7`, 5820 bytes.

The raw menu rows preserve source line numbers and raw JavaScript in `inventory.json`. `repair-plan.json` records pending network work with `actual_capture_timestamp: null`; `cdx_status: not_attempted_offline` means this local phase did not query CDX, not that no capture exists.
