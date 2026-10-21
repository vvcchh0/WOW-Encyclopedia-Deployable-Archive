# Phase 2 local non-gallery audit

Selected and browser-checked 34/34 v39 pages on loopback; every response was HTTP 200. Local HTTP errors=0, failed local requests=0, blocked non-loopback requests=0.

Timing: browser batch measured 86,169 ms and finished at 2026-10-21T01:58:09.520Z; start estimate 2026-10-21T01:56:43.351Z. The later trace/interaction/report work is recorded separately and is the reason this phase exceeded the original 20-minute window.

## Actionable findings

- **P1 talent-shared-js-syntax** (reproduced): Repair the exporter/source transformation that inserts __offline/missing.html into quoted JavaScript strings at these two lines; preserve the original JS string delimiters. Re-run the four talent pages before considering all other class calculators.
- **P1 zangarmarsh-reward-icons** (reproduced-visible): Only supply exact local item/token assets or a source-backed mapping; do not substitute the semantically different Zandalar token.
- **P2 dynamic-subnav-icons** (reproduced-visible): Route/rewrite only the resulting dynamic subnav paths to exact local assets if an exact source-backed file is found; do not substitute icon_character.jpg for black/reputation/player-vs-player artwork without visual/source confirmation.
- **P3 zandalar-border-fillers** (active-but-no-visible-collapse): Do not bulk-replace from a guessed b.gif. Existing candidates differ in dimensions/appearance: new-hp/images/smallcaps/b.gif (32x32), shared/wow-com/images/smallcaps/blue/b.gif (39x38), plain/b.gif (38x36), red/b.gif (40x38).
- **P3 old-rss-image-gaps** (reproduced-missing-local-assets): Keep as unknown until exact local captures are found; do not fabricate or reuse unrelated screenshot/gallery media.
- **excluded commented-alterac-map** (excluded-by-scope): No repair in this batch; retain as commented/hidden evidence per scope.

## Targeted interaction evidence

- Zangarmarsh Alliance/Horde links switched `allianceRewards`/`hordeRewards` visibility without page errors; the missing reward icons are the visual defect.
- Alterac `area[href^="javascript:viewDiv"]` is inside the commented corpse-loot block; DOM-only invocation raised a null-style error and is excluded from visible repair scope.

## Priority follow-up pages

1. `/info/classes/druid/talents.html` — shared talent calculator syntax failure; visible calculator never initializes
2. `/info/classes/hunter/talents.html` — same shared syntax failure
3. `/info/classes/mage/talents.html` — same shared syntax failure
4. `/info/classes/warrior/talents.html` — same shared syntax failure
5. `/info/basics/factions/zangarmarsh/zangarpvp.xml.html` — visible reward icons missing; Alliance/Horde switch itself works
6. `/info/basics/factions/zandalar/quests.html` — visible subnav icon gap; 1x1 border fillers show no layout collapse
7. `/info/basics/reputation.html` — same missing reputation subnav target
8. `/pvp/index.html` — same missing Player vs Player subnav target
9. `/downloads/movies.html` — same missing Media subnav target
10. `/community/index.html` — same missing Community subnav target

## Scope/limitations

- No network or browser outside 127.0.0.1 was used. No gallery, screenshot collection, historical ZIP, or production file was touched.
- The exact local asset inventory found no safe replacements for the observed dynamic subnav/reward/RSS targets.
