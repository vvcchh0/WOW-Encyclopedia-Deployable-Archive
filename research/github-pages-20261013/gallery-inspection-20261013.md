# Player Screenshot Galleries inventory (read-only, 2026-10-13)

## Scope and counting rule

The source list is `offline/site/info/index.html:539-591`; the final `Screenshot of the Day` link at line 591 is excluded. The list contains 50 links. Forty-nine links are gallery HTML pages with `numShots` plus `addshots`; the Zul'Aman entry at line 542 is an XML wrapper. Its linked `offline/site/info/dungeons/zulaman-gallery.html` is the actual gallery (`numShots=60`, `addshots` at source line 123 and export line 129), so it is reported separately.

`offline/site/new-hp/js/guidegallery-screenie.js:471-487` constructs one full URL per slot as `sourceDirectory + "ss" + N + ".jpg"`; `:506-507` derives the thumbnail by replacing `.jpg` with `-thumb.jpg`. A slot is counted once; the full and thumbnail are two separate entity checks, and a pair is valid only if both files are real JPEGs (JPEG magic `ff d8 ff`). SVG/HTML placeholders and layout images are excluded.

## Aggregate result

| Scope | gallery pages/links | shot slots | expected direct entities | valid direct full | valid direct thumb | valid direct pairs | manifest full/thumb records | export addshots rewritten to missing placeholder |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 49 gallery HTML links from the index | 49 | 1,624 | 3,248 | 0 | 0 | 0 | 0 / 0 | 49 / 49 |
| Zul'Aman underlying gallery (wrapper listed at index line 542) | 1 | 60 | 120 | 0 | 0 | 0 | 0 / 0 | 1 / 1 |
| Combined dynamic gallery content | 50 | 1,684 | 3,368 | 0 | 0 | 0 | 0 / 0 | 50 / 50 |

The 49-row machine inventory is in [gallery-inventory-20261013.json](gallery-inventory-20261013.json); it checked all 1,624 full/thumb pairs against `offline/site`, `.scratch/pages-preview-final`, `offline/build-manifest.json`, `.scratch/pages-preview-final/export-provenance.json`, and `.scratch/pages-preview-final/__offline/route-map.json`.

| List category | index links | dynamic links | dynamic slots | direct full/thumb/pair valid | placeholder rewrites |
|---|---:|---:|---:|---:|---:|
| Dungeon | 15 | 15 | 537 | 0 / 0 / 0 | 15 |
| Event | 6 | 6 | 242 | 0 / 0 / 0 | 6 |
| Flying Mount | 4 | 4 | 64 | 0 / 0 / 0 | 4 |
| Mount | 7 | 7 | 83 | 0 / 0 / 0 | 7 |
| Profession | 1 | 1 | 66 | 0 / 0 / 0 | 1 |
| PvP | 4 | 4 | 175 | 0 / 0 / 0 | 4 |
| Raid | 9 | 8 | 272 | 0 / 0 / 0 | 8 (plus Zul'Aman underlying page) |
| Region | 1 | 1 | 49 | 0 / 0 / 0 | 1 |
| TCG Gallery | 1 | 1 | 47 | 0 / 0 / 0 | 1 |
| TCG Mount | 1 | 1 | 47 | 0 / 0 / 0 | 1 |
| TCG Picnic Basket | 1 | 1 | 42 | 0 / 0 / 0 | 1 |

## Representative rows and raw screenshot URLs

| gallery | `numShots` | source `addshots` line | export `addshots` line | source base | first expected full / thumb | direct source valid full/thumb/pair | manifest + route-map direct records |
|---|---:|---:|---:|---|---|---:|---:|
| Karazhan | 63 | `offline/site/info/dungeons/karazhan-gallery.html:126` | `.scratch/pages-preview-final/info/dungeons/karazhan-gallery.html:132` | `/info/dungeons/images/karazhan/` | `http://www.worldofwarcraft.com/info/dungeons/images/karazhan/ss1.jpg` / `.../ss1-thumb.jpg` | 0 / 0 / 0 | 0 / 0 |
| Black Temple | 48 | `offline/site/info/dungeons/black-temple-gallery.html:112` | `.scratch/pages-preview-final/info/dungeons/black-temple-gallery.html:118` | `/info/dungeons/images/blacktemple/` | `http://www.worldofwarcraft.com/info/dungeons/images/blacktemple/ss1.jpg` / `.../ss1-thumb.jpg` | 0 / 0 / 0 | 0 / 0 |
| Warsong Gulch | 29 | `offline/site/pvp/battlegrounds/warsong-gulch-gallery.html:96` | `.scratch/pages-preview-final/pvp/battlegrounds/warsong-gulch-gallery.html:102` | `/pvp/battlegrounds/warsonggulch/` | `http://www.worldofwarcraft.com/pvp/battlegrounds/warsonggulch/ss1.jpg` / `.../ss1-thumb.jpg` | 0 / 0 / 0 | 0 / 0 |
| Fishing | 66 | `offline/site/info/professions/fishing-gallery.html:129` | `.scratch/pages-preview-final/info/professions/fishing-gallery.html:135` | `/info/professions/images/fishing/ss/` | `https://www.worldofwarcraft.com/info/professions/images/fishing/ss/ss1.jpg` / `.../ss1-thumb.jpg` | 0 / 0 / 0 | 0 / 0 |
| Zul'Aman underlying gallery | 60 | `offline/site/info/dungeons/zulaman-gallery.html:123` | `.scratch/pages-preview-final/info/dungeons/zulaman-gallery.html:129` | `/info/dungeons/images/zulaman/` | `http://www.worldofwarcraft.com/info/dungeons/images/zulaman/ss1.jpg` / `.../ss1-thumb.jpg` | 0 / 0 / 0 | 0 / 0 |

The source HTMLs and the exported HTMLs exist. For example, export provenance records the gallery pages as transformed static files with one placeholder reference each: Karazhan at `.scratch/pages-preview-final/export-provenance.json:17615-17629`, Fishing at `:18321-18335`, and Warsong at `:24890-24904`. The export route-map resolves the HTML routes, but direct expected screenshot routes such as `/info/dungeons/images/karazhan/ss1.jpg`, `/info/professions/images/fishing/ss/ss1.jpg`, and `/pvp/battlegrounds/warsonggulch/ss1.jpg` have no route-map entries and no manifest/provenance records.

## What is actually saved

There are 19 valid JPEG *preview thumbnails* in nested `thumbs/` directories, separately from the 3,368 direct dynamic entities above:

* Fishing: 4 (`ss1`, `ss34`, `ss49`, `ss53`), source preview links at `offline/site/info/professions/fishing.html:1492-1495`; exported links remain deployed at `.scratch/pages-preview-final/info/professions/fishing.html:1497-1500`.
* Hallow's End: 4, source links at `offline/site/info/events/hallowsend/index.html:1177-1188`; export routes are present.
* Brewfest: 4, source links at `offline/site/info/events/brewfest/index.html:1036-1047`; export routes are present.
* Winter's Veil: 4, source links at `offline/site/info/events/winterveil/index.html:713-724`; export routes are present.
* Zul'Aman wrapper: 3, source links at `offline/site/info/dungeons/zulaman.xml:781-805`; export wrapper links are at `.scratch/pages-preview-final/info/dungeons/zulaman.xml.html:786-810`.

All 19 pass JPEG magic checks and have `kind=image`, `mime=image/jpeg`, manifest records, provenance records, and route-map entries. Representative manifest evidence: Fishing at `offline/build-manifest.json:1226863-1226877`, Brewfest at `:1217664-1217678`, Hallow's End at `:1220680-1220694`, and Winter's Veil at `:1222812-1222826`. Their paths are `/.../thumbs/ssN-thumb.jpg`; the dynamic `shotList` asks for `/.../ssN.jpg` and `/.../ssN-thumb.jpg`, so these preview files do not satisfy the dynamic full/thumb pair. No corresponding full image is present beside these 19 nested thumbs.

Fishing also has two unrelated guide-page full/thumb pairs at `/info/professions/images/fishing/ss1.jpg` and `ss2.jpg`, referenced by `offline/site/info/professions/fishing.html:1000` and `:1054`; they are outside the gallery's `/info/professions/images/fishing/ss/` directory and are not counted. Likewise, Warsong's `images/warsonggulch/scores/ss01.jpg` pair is a static battleground guide dependency, not the gallery's `/pvp/battlegrounds/warsonggulch/ssN.jpg` sequence.

## Diagnosis

The primary gap is **uncollected/not downloaded direct screenshot entities**: zero direct full/thumb records exist in the source library, manifest, provenance, or deployed route-map for all dynamic slots. The pages themselves are present and deployed.

There is also a separate **static compatibility/export rewrite bug**. Source `addshots` retains the real directory (for example Karazhan `:126`, Fishing `:129`), while export rewrites its first argument to `/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html?...requested=<original screenshot directory>...` (Karazhan `:132`, Fishing `:135`, etc.). Because `addshots` concatenates `ssN.jpg` after that string, the browser requests a placeholder URL rather than the original screenshot path. This explains the false missing display and would still need fixing after assets are restored; fixing it alone cannot create the 3,368 absent entities.

The recent 19 accepted resources in `research/resource-resume-20261013/round002/entity-source-map.json:2-19` and `round003/entity-source-map.json:2-278` are Visa/reward assets (`/visa/reward/images/...`, plus `/visa/images/pixel.gif`), not any gallery screenshot directory. They are unrelated to these gaps.
