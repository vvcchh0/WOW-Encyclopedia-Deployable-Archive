# Local route audit

Offline static audit of all derived HTML/XML/CSS in `.scratch/pages-historical-exhibits-20261014-v3`.
The v3 source tree, build manifest, provenance, and route map were read only; this compact summary was derived from the saved v3 JSON without a second scan.

Scanned 1013 HTML/XML files and 61 CSS files, yielding 140010 static reference occurrences; 0 dynamic expressions were skipped.
Outcomes: 113028 resolved, 0 proven repair candidates (0 unique; 0 emitted), and 26982 unresolved occurrences.
Known placeholders: 26975 occurrences and 24380 legacy raw groups (the raw value includes `source=` and is not a requested-target count).
Input hashes unchanged: True. Full v3 details: `research/local-maintenance-20261014/route-audit/details-v3.json.gz` (23626839 bytes before gzip).

## Requested target aggregation

Exact requested targets after stripping only URL fragments: **2934 unique**, **26975 occurrences**. Groups without a requested field: 2 (7 occurrences); these remain separate external/excluded evidence.
This evidence inventory is not claimed equivalent to the 3358 recovery queue.

| scope | unique targets | occurrences |
| --- | ---: | ---: |
| external_host | 2293 | 20702 |
| primary_worldofwarcraft_host | 641 | 6273 |

### Highest occurrence exact targets

| target | occurrences | scope | class |
| --- | ---: | --- | --- |
| `http://www.blizzard.com/privacy.shtml` | 1514 | external_host | known_placeholder |
| `http://www.esrb.org/esrbratings_guide.asp` | 1273 | external_host | known_placeholder |
| `http://www.blizzard.com` | 900 | external_host | known_placeholder |
| `http://forums.worldofwarcraft.com/` | 701 | external_host | known_placeholder |
| `http://shop.blizzard.com/` | 642 | external_host | known_placeholder |
| `http://forums.worldofwarcraft.com/board.html?forumId=11124` | 641 | external_host | known_placeholder |
| `http://signup.worldofwarcraft.com/` | 641 | external_host | known_placeholder |
| `http://forums.worldofwarcraft.com/board.html?forumId=10001` | 640 | external_host | known_placeholder |
| `http://forums.worldofwarcraft.com/board.html?forumId=11110&sid=1` | 640 | external_host | known_placeholder |
| `http://us.blizzard.com/support/article.xml?articleId=21465` | 640 | external_host | known_placeholder |
| `http://www.blizzard.com/press/` | 640 | external_host | known_placeholder |
| `http://forums.worldofwarcraft.com/board.html?forumId=11123` | 639 | external_host | known_placeholder |
| `http://forums.worldofwarcraft.com/realmforums.shtml` | 639 | external_host | known_placeholder |
| `http://us.blizzard.com/support/article.xml?articleId=21422` | 639 | external_host | known_placeholder |
| `http://us.blizzard.com/support/index.xml?categoryId=2415&rootCategoryId=2318&gameId=11` | 639 | external_host | known_placeholder |
| `http://us.blizzard.com/support/index.xml?rootCategoryId=2316&gameId=11` | 639 | external_host | known_placeholder |
| `http://us.blizzard.com/support/index.xml?rootCategoryId=2317&gameId=11` | 639 | external_host | known_placeholder |
| `http://us.blizzard.com/support/index.xml?rootCategoryId=2318&gameId=11` | 639 | external_host | known_placeholder |
| `http://us.blizzard.com/support/index.xml?rootCategoryId=2691&gameId=11` | 639 | external_host | known_placeholder |
| `http://us.blizzard.com/blizzcast` | 638 | external_host | known_placeholder |

## Proven repair candidates

No proven repair candidates were emitted.

## Missing and unproven evidence

There are 24382 missing groups (26982 occurrences); compact examples are capped at 20 per classification. Full rows are in the gzip archive.

### external_or_uncollected (2 groups, 7 occurrences)

- `info/items/socketeditems.html:604` `http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=8,0,0,0` (6 refs) — absolute URL has no exact frozen origin identity
- `info/races/dancing.html:564` `http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,29,0` (1 refs) — absolute URL has no exact frozen origin identity

### known_placeholder (24380 groups, 26975 occurrences)

- `info/basics/factions/zandalar/quests.html:701` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=https%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Ffactions%2Fzandalar%2Fquests.html&requested=http%3A%2F%2Fimgs.worldofwarcraft.co.kr%2Fimages%2Fb.gif&reason=external-or-uncollected-resource` (216 refs; requested=http://imgs.worldofwarcraft.co.kr/images/b.gif) — placeholder requested identity has no exact local origin/route evidence
- `downloads/movies.html:572` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fdownloads%2Fmovies.html&requested=http%3A%2F%2Fwww.divx.com%2Fdivx%2F&reason=external-or-uncollected-resource` (63 refs; requested=http://www.divx.com/divx/) — placeholder requested identity has no exact local origin/route evidence
- `downloads/movies.html:574` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fdownloads%2Fmovies.html&requested=http%3A%2F%2Fwww.divx.com%2Fdivx%2Fmac%2F&reason=external-or-uncollected-resource` (32 refs; requested=http://www.divx.com/divx/mac/) — placeholder requested identity has no exact local origin/route evidence
- `info/basics/highleveloptions.html:649` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=https%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fbasics%2Fhighleveloptions.html&requested=http%3A%2F%2Fimgs.worldofwarcraft.co.kr%2Fimages%2Fb.gif&reason=external-or-uncollected-resource` (16 refs; requested=http://imgs.worldofwarcraft.co.kr/images/b.gif) — placeholder requested identity has no exact local origin/route evidence
- `info/raiddungeons/fourdragons/index.html:589` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=https%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fraiddungeons%2Ffourdragons%2F&requested=http%3A%2F%2Fimgs.worldofwarcraft.co.kr%2Fimages%2Fb.gif&reason=external-or-uncollected-resource` (16 refs; requested=http://imgs.worldofwarcraft.co.kr/images/b.gif) — placeholder requested identity has no exact local origin/route evidence
- `info/underdev/1p8/fourdragons.html:602` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=https%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Funderdev%2F1p8%2Ffourdragons.html&requested=http%3A%2F%2Fimgs.worldofwarcraft.co.kr%2Fimages%2Fb.gif&reason=external-or-uncollected-resource` (16 refs; requested=http://imgs.worldofwarcraft.co.kr/images/b.gif) — placeholder requested identity has no exact local origin/route evidence
- `news/wow-news-01-2006.html:455` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=https%3A%2F%2Fwww.worldofwarcraft.com%2Fnews%2Fwow-news-01-2006.html&requested=http%3A%2F%2Fwww.blizzard.com%2Finblizz%2Ffanart%2Fpage28.shtml&reason=external-or-uncollected-resource` (15 refs; requested=http://www.blizzard.com/inblizz/fanart/page28.shtml) — placeholder requested identity has no exact local origin/route evidence
- `pvp/tournament/items.xml.html:1351` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%3A80%2Fpvp%2Ftournament%2Fitems.xml%3F&requested=http%3A%2F%2Fwww.wowarmory.com%2Fimages%2Ficons%2F21x21%2Finv_pants_mail_15.png&reason=external-or-uncollected-resource` (15 refs; requested=http://www.wowarmory.com/images/icons/21x21/inv_pants_mail_15.png) — placeholder requested identity has no exact local origin/route evidence
- `downloads/movies.html:560` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fdownloads%2Fmovies.html&requested=http%3A%2F%2Fwww.adobe.com%2Fshockwave%2Fdownload%2Fdownload.cgi%3FP1_Prod_Version%3DShockwaveFlash&reason=external-or-uncollected-resource` (13 refs; requested=http://www.adobe.com/shockwave/download/download.cgi?P1_Prod_Version=ShockwaveFlash) — placeholder requested identity has no exact local origin/route evidence
- `news/wow-news-02-2006.html:316` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=https%3A%2F%2Fwww.worldofwarcraft.com%2Fnews%2Fwow-news-02-2006.html&requested=http%3A%2F%2Fwww.blizzard.com%2Finblizz%2Ffanart%2Fpage29.shtml&reason=external-or-uncollected-resource` (13 refs; requested=http://www.blizzard.com/inblizz/fanart/page29.shtml) — placeholder requested identity has no exact local origin/route evidence
- `pvp/tournament/items.xml.html:1339` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%3A80%2Fpvp%2Ftournament%2Fitems.xml%3F&requested=http%3A%2F%2Fwww.wowarmory.com%2Fimages%2Ficons%2F21x21%2Finv_gauntlets_25.png&reason=external-or-uncollected-resource` (12 refs; requested=http://www.wowarmory.com/images/icons/21x21/inv_gauntlets_25.png) — placeholder requested identity has no exact local origin/route evidence
- `pvp/tournament/items.xml.html:1793` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%3A80%2Fpvp%2Ftournament%2Fitems.xml%3F&requested=http%3A%2F%2Fwww.wowarmory.com%2Fimages%2Ficons%2F21x21%2Finv_pants_cloth_05.png&reason=external-or-uncollected-resource` (12 refs; requested=http://www.wowarmory.com/images/icons/21x21/inv_pants_cloth_05.png) — placeholder requested identity has no exact local origin/route evidence
- `pvp/tournament/items.xml.html:1367` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%3A80%2Fpvp%2Ftournament%2Fitems.xml%3F&requested=http%3A%2F%2Fwww.wowarmory.com%2Fimages%2Ficons%2F21x21%2Finv_shoulder_14.png&reason=external-or-uncollected-resource` (11 refs; requested=http://www.wowarmory.com/images/icons/21x21/inv_shoulder_14.png) — placeholder requested identity has no exact local origin/route evidence
- `pvp/tournament/items.xml.html:1335` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%3A80%2Fpvp%2Ftournament%2Fitems.xml%3F&requested=http%3A%2F%2Fwww.wowarmory.com%2Fimages%2Ficons%2F21x21%2Finv_helmet_15.png&reason=external-or-uncollected-resource` (10 refs; requested=http://www.wowarmory.com/images/icons/21x21/inv_helmet_15.png) — placeholder requested identity has no exact local origin/route evidence
- `info/index.html:1103` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=https%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2F&requested=https%3A%2F%2Fwww.worldofwarcraft.com%2Finfo%2Fimages%2Fbottom.jpg&reason=external-or-uncollected-resource` (9 refs; requested=https://www.worldofwarcraft.com/info/images/bottom.jpg) — placeholder requested identity has no exact local origin/route evidence
- `news/wow-news-03-2006.html:819` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=https%3A%2F%2Fwww.worldofwarcraft.com%2Fnews%2Fwow-news-03-2006.html&requested=http%3A%2F%2Fwww.blizzard.com%2Finblizz%2Ffanart%2Fpage30.shtml&reason=external-or-uncollected-resource` (9 refs; requested=http://www.blizzard.com/inblizz/fanart/page30.shtml) — placeholder requested identity has no exact local origin/route evidence
- `news/wow-news-06-2006.html:328` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnews%2Fwow-news-06-2006.html&requested=http%3A%2F%2Fwww.blizzard.com%2Finblizz%2Ffanart%2Fpage34.shtml&reason=external-or-uncollected-resource` (9 refs; requested=http://www.blizzard.com/inblizz/fanart/page34.shtml) — placeholder requested identity has no exact local origin/route evidence
- `pvp/tournament/items.xml.html:1789` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing-image.svg?source=http%3A%2F%2Fwww.worldofwarcraft.com%3A80%2Fpvp%2Ftournament%2Fitems.xml%3F&requested=http%3A%2F%2Fwww.wowarmory.com%2Fimages%2Ficons%2F21x21%2Finv_helmet_30.png&reason=external-or-uncollected-resource` (9 refs; requested=http://www.wowarmory.com/images/icons/21x21/inv_helmet_30.png) — placeholder requested identity has no exact local origin/route evidence
- `burningcrusade/movies.html:137` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=https%3A%2F%2Fwww.worldofwarcraft.com%2Fburningcrusade%2Fmovies.html&requested=http%3A%2F%2Fwww.divx.com%2Fdivx%2F&reason=external-or-uncollected-resource` (8 refs; requested=http://www.divx.com/divx/) — placeholder requested identity has no exact local origin/route evidence
- `news/wow-news-06-2006.html:270` `/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?source=http%3A%2F%2Fwww.worldofwarcraft.com%2Fnews%2Fwow-news-06-2006.html&requested=http%3A%2F%2Fwww.worldofwarcraft.com%2Fcommunity%2Fsubmission%2Fcomic-rules.html&reason=invalid-overlay-or-uncollected-site-resource` (8 refs; requested=http://www.worldofwarcraft.com/community/submission/comic-rules.html) — placeholder requested identity has no exact local origin/route evidence

## Validation

`details-v3.json.gz` decompresses byte-exactly to the saved v3 JSON; source SHA-256 `92a73329ab22f6885aa9599ed70202e1fcb16cd9e4c70544f42fce3cae9af8dd`; gzip SHA-256 `e141aab26a22ab5fbb0099620d634d5f5bf4fb420f9fedd8ef239fac1b2af2a6`.
The compact JSON is intentionally bounded and contains at most 100 representative/example rows per human-facing section; `representative_refs` retains 16 rows.
