# v43 local browser probe summary

Run: `2026-10-21T04:54:40.960Z` to `2026-10-21T04:55:02.864Z`; duration `22536 ms`; server `http://127.0.0.1:54464/WOW-Encyclopedia-Deployable-Archive`.

The run used Playwright with service workers blocked. Only the supplied loopback HTTP port and data/blob/about URLs were allowed; no external request reached the server. All 15 targets returned HTTP 200; the receipt records one alias page with three real loopback image 404 responses.

## Canonical Source16 pages

| Page | Title | Source capture | Phrase checks | Placeholders (img/CSS) | Errors |
|---|---|---|---|---:|---|
| `source16-contest-050609` | WoW -> Contests -> Insider Battlegrounds Screenshot Contest | `20080509140330` | PASS: historical contest invited players; PASS: June 20th, 2005 | 2/0 | pageerror `0`, requestfailed `0`, HTTP error `0` |
| `source16-content-index` | WoW -> Info -> Basics -> Content Index | `20080511191306` | PASS: Battlegrounds Mini-Site; PASS: Warlock Talents | 2/0 | pageerror `0`, requestfailed `0`, HTTP error `0` |
| `source16-tinfoilhat` | WoW -> Info -> Items -> Introducing the Tinfoil Hat | `20080512010107` | PASS: Schematic: Tinfoil Hat; PASS: Crafting the Tinfoil Hat | 10/11 | pageerror `0`, requestfailed `0`, HTTP error `0` |
| `source16-two-headed-ogre` | WoW -> April Fools! | `20080511191314` | PASS: Choosing the Two-headed Player Race; PASS: Two-headed Ogre Origins | 4/0 | pageerror `0`, requestfailed `0`, HTTP error `0` |
| `source16-fan-site-program` | WoW -> Community -> Fan Site Program | `20080511142305` | PASS: historical fan site program; PASS: does not accept applications | 0/0 | pageerror `0`, requestfailed `0`, HTTP error `0` |
| `source16-moltencore` | World of Warcraft: The Molten Core | `20080512040326` | PASS: WORLD OF WARCRAFT COMING TO CONSOLES WITH; PASS: April 1, 2008 | 4/0 | pageerror `0`, requestfailed `0`, HTTP error `0` |
| `source16-patch-092904` | WoW -> Patch Notes | `20080511162102` | PASS: Warlock Talents Added; PASS: New Model & Animation System | 0/0 | pageerror `0`, requestfailed `0`, HTTP error `0` |
| `source16-bardclass` | World of Warcraft: Wrath of the Lich King | `20080512010059` | PASS: Unveiling the Bard Hero Class; PASS: Sample Talents | 10/8 | pageerror `0`, requestfailed `0`, HTTP error `0` |

## Alias and legacy observations

| Page | Status/final URL | Phrase result | Placeholder count | Action/HTTP note |
|---|---|---|---:|---|
| `alias-contest-no-slash` | `200` `http://127.0.0.1:54464/WOW-Encyclopedia-Deployable-Archive/contests/05-06-09/` | PASS: historical contest invited players; PASS: June 20th, 2005 | 2/0 | HTTP errors: 0 |
| `alias-contest-slash` | `200` `http://127.0.0.1:54464/WOW-Encyclopedia-Deployable-Archive/contests/05-06-09/` | PASS: historical contest invited players; PASS: June 20th, 2005 | 2/0 | HTTP errors: 0 |
| `alias-content-index-shtml` | `200` `http://127.0.0.1:54464/WOW-Encyclopedia-Deployable-Archive/info/basics/content-index.shtml.html` | PASS: Battlegrounds Mini-Site; PASS: Warlock Talents | 2/0 | HTTP errors: 0 |
| `alias-moltencore-no-slash` | `200` `http://127.0.0.1:54464/WOW-Encyclopedia-Deployable-Archive/moltencore/` | PASS: WORLD OF WARCRAFT COMING TO CONSOLES WITH; PASS: April 1, 2008 | 4/0 | HTTP errors: 0 |
| `alias-moltencore-slash` | `200` `http://127.0.0.1:54464/WOW-Encyclopedia-Deployable-Archive/moltencore/` | PASS: WORLD OF WARCRAFT COMING TO CONSOLES WITH; PASS: April 1, 2008 | 4/0 | HTTP errors: 0 |
| `alias-wrath-index-xml` | `200` `http://127.0.0.1:54464/WOW-Encyclopedia-Deployable-Archive/wrath/index.xml.html` | not configured | 0/0 | HTTP errors: 3 |
| `legacy-news-06-2005` | `200` `http://127.0.0.1:54464/WOW-Encyclopedia-Deployable-Archive/news/wow-news-06-2005.html` | FAIL: Insider Battlegrounds Screen Shot Contest; FAIL: June 20th, 2005 | 14/0 | click-contest-entry: clicked=True, expanded=True, navigation=200 |

## Scope notes

- The 8 canonical pages each had a title and both page-specific phrases in the selected main-content selector; menu text was not used for those checks.
- The 2005 news article was visible and its `Submit a Screenshot` contest link was clicked successfully, navigating to the contest page with HTTP 200 and no new page error. The first receipt used a too-narrow legacy phrase selector, so its legacy phrase fields are recorded as false even though the action evidence proves the article/link; the probe script now uses `#main-content` for future runs. No second browser run was performed.
- Placeholder counts are DOM/CSS observations. A local HTTP 200 for `__offline/missing-image.svg` is not counted as the requested image being present.
- The only real loopback 404s were the three Wrath alias featured-image URLs: `northrend.jpg`, `grizzlyhills.jpg`, and `utgardekeep.jpg`.
