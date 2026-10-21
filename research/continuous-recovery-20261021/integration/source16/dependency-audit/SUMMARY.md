# Source16 dependency audit summary

Scope: eight Source16 body pages; local Source16 destination plus v42 route-map/file evidence; no network and no site/exporter writes.

Observed 403 dependency uses, 147 unique target/status groups, and 30 ranked gaps (cap 30).

## Per-page counts

| Page | Present | Missing | Dynamic unresolved | Dynamic missing | External |
|---|---:|---:|---:|---:|---:|
| `contest-050609` | 38 | 2 | 1 | 0 | 1 |
| `content-index-shtml` | 59 | 0 | 5 | 0 | 1 |
| `tinfoilhat` | 102 | 23 | 2 | 0 | 1 |
| `two-headed-ogre` | 38 | 4 | 1 | 0 | 1 |
| `fan-site-program` | 33 | 0 | 1 | 0 | 1 |
| `moltencore` | 0 | 8 | 0 | 0 | 1 |
| `patch-092904` | 37 | 0 | 1 | 0 | 1 |
| `bardclass` | 10 | 21 | 4 | 1 | 1 |

## Highest-priority concrete gaps

The rows below are page-use evidence with exact output line numbers. Dynamic variable expressions are excluded from this list; the one exact missing runtime SWF is retained separately.

| Rank | Page | Kind | Route | Line | Reason |
|---:|---|---|---|---:|---|
| 1 | `moltencore` | `css` | `/moltencore/css.css` | 8 | `local_missing`; raw `css.css` |
| 2 | `bardclass` | `css` | `/wrath/images/artwork/ss31-thumb.jpg` | 201 | `local_missing`; raw `/wrath/images/artwork/ss31-thumb.jpg` |
| 3 | `bardclass` | `css` | `/wrath/images/artwork/ss32-thumb.jpg` | 207 | `local_missing`; raw `/wrath/images/artwork/ss32-thumb.jpg` |
| 4 | `bardclass` | `css` | `/wrath/images/artwork/ss33-thumb.jpg` | 213 | `local_missing`; raw `/wrath/images/artwork/ss33-thumb.jpg` |
| 5 | `bardclass` | `css` | `/wrath/images/artwork/ss34-thumb.jpg` | 219 | `local_missing`; raw `/wrath/images/artwork/ss34-thumb.jpg` |
| 6 | `bardclass` | `css` | `/wrath/images/layout/header18-l.jpg` | 13 | `local_missing`; raw `/wrath/images/layout/header18-l.jpg` |
| 7 | `bardclass` | `css` | `/wrath/images/layout/header18-r.jpg` | 14 | `local_missing`; raw `/wrath/images/layout/header18-r.jpg` |
| 8 | `bardclass` | `css` | `/wrath/images/layout/header18-t.jpg` | 12 | `local_missing`; raw `/wrath/images/layout/header18-t.jpg` |
| 9 | `bardclass` | `css` | `/wrath/images/screenshots/ss45-thumb.jpg` | 225 | `local_missing`; raw `/wrath/images/screenshots/ss45-thumb.jpg` |
| 10 | `moltencore` | `image` | `/moltencore/images/backarrow.gif` | 167 | `local_missing`; raw `images/backarrow.gif` |
| 11 | `moltencore` | `image` | `/moltencore/images/ss2-thumb.gif` | 42 | `local_missing`; raw `images/ss2-thumb.gif` |
| 12 | `moltencore` | `image` | `/moltencore/images/ss3-thumb.gif` | 43 | `local_missing`; raw `images/ss3-thumb.gif` |
| 13 | `moltencore` | `image` | `/moltencore/images/ss4-thumb.gif` | 44 | `local_missing`; raw `images/ss4-thumb.gif` |
| 14 | `bardclass` | `image` | `/wrath/images/artwork/ss35-thumb.jpg` | 244 | `local_missing`; raw `/wrath/images/artwork/ss35-thumb.jpg` |
| 15 | `bardclass` | `image` | `/wrath/images/artwork/ss36-thumb.jpg` | 247 | `local_missing`; raw `/wrath/images/artwork/ss36-thumb.jpg` |
| 16 | `bardclass` | `image` | `/wrath/images/artwork/ss37-thumb.jpg` | 250 | `local_missing`; raw `/wrath/images/artwork/ss37-thumb.jpg` |
| 17 | `bardclass` | `image` | `/wrath/images/artwork/ss38-thumb.jpg` | 262 | `local_missing`; raw `/wrath/images/artwork/ss38-thumb.jpg` |
| 18 | `bardclass` | `image` | `/wrath/images/artwork/ss39-thumb.jpg` | 265 | `local_missing`; raw `/wrath/images/artwork/ss39-thumb.jpg` |
| 19 | `bardclass` | `image` | `/wrath/images/artwork/ss40-thumb.jpg` | 268 | `local_missing`; raw `/wrath/images/artwork/ss40-thumb.jpg` |
| 20 | `bardclass` | `image` | `/wrath/images/layout/bard-item.gif` | 329 | `local_missing`; raw `../../images/layout/bard-item.gif` |
| 21 | `bardclass` | `image` | `/wrath/images/layout/bard-talenticon1.png` | 294 | `local_missing`; raw `../../images/layout/bard-talenticon1.png` |
| 22 | `bardclass` | `image` | `/wrath/images/layout/bard-talenticon2.png` | 308 | `local_missing`; raw `../../images/layout/bard-talenticon2.png` |
| 23 | `bardclass` | `swf` | `/wrath/flash/global/bard_idle.swf` | 184 | `dynamic_local_missing`; raw `/wrath/flash/global/bard_idle.swf` |
| 24 | `bardclass` | `link` | `/wrath/css/newarmorsetsstyle.css` | 146 | `local_missing`; raw `/wrath/css/newarmorsetsstyle.css` |
| 25 | `bardclass` | `link` | `/wrath/features/bard/strings/en_us/rss.xml` | 7 | `local_missing`; raw `strings/en_us/rss.xml` |
| 26 | `moltencore` | `script` | `/moltencore/embedflash.js` | 63 | `local_missing`; raw `embedflash.js` |
| 27 | `moltencore` | `script` | `/moltencore/functions.js` | 17 | `local_missing`; raw `functions.js` |
| 28 | `moltencore` | `script` | `/moltencore/tooltip.js` | 16 | `local_missing`; raw `tooltip.js` |
| 29 | `bardclass` | `script` | `/wrath/js/tooltip-standalone.js` | 145 | `local_missing`; raw `/wrath/js/tooltip-standalone.js` |
| 30 | `bardclass` | `script` | `/wrath/strings/en_us/features/externalizeddata.js` | 145 | `local_missing`; raw `/wrath/strings/en_us/features/externalizeddata.js` |

## Interpretation

* MoltenCore has a missing page stylesheet (`css.css` line 8), three gallery thumbnails, and its local helper scripts/back arrow. The audit does not infer whether any absent original binary is recoverable.
* Bard has missing header skin backgrounds, artwork thumbnails, talent decoration images, stylesheet/helper scripts, and one exact runtime `bard_idle.swf` target at line 184. The runtime target is not one of the three already validated Flash exhibits, so it remains a source/decision item rather than an automatic restore proposal.
* Tinfoil Hat and Two-Headed Ogre contain page-specific image/CSS targets absent from both the Source16 destination and v42 local evidence. Contest has two page thumbnails with the same evidence boundary.
* Dynamic `roothost + literal`, menu-icon concatenation, and other variable expressions remain in `targets` as `dynamic_unresolved`; they are not counted as concrete missing files.

See `dependency-audit.json` for source hashes, manifest records, route-map booleans, all line-level uses, and the capped `priority_gaps`; `dependency-audit.csv` contains the row-level table.
