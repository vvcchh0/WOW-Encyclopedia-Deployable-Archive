# Wrath Wallpapers local baseline audit

Generated `2026-10-15T05:54:21.443838+00:00` from frozen local files only; no network was performed.

The page layer and wallpaper asset layer are counted separately. The current frozen baseline has the page route and all 28 linked original images, 4 thumbnails, and 4 shadow PNGs.

## Page and source identity

| Layer | Evidence | Result |
|---|---|---|
| Derived page | `offline/site/wrath/wallpapers.xml`; 16971 bytes; SHA-256 `ad124c1a01fc6e01fc9213d296f31ab68eb2813ce74b8d796e83d6c640641b03` | present |
| Frozen manifest page entry | route `/wrath//wallpapers.xml`; role `frontier_full_local_page_2008`; actual capture `20080509072957` | page-layer recovery |
| Navigation-gap raw page | `research/navigation-gaps-20261015/wayback-missing/raw/wrath_wallpapers-20080402070813.bin`; actual/indexed capture `20080402070813`; 14178 bytes; SHA-256 `1c8328245cd45c1a9dfb09d6230eda831d60ca11ef65f73b8054d00e7e124a34` | separate 2008-04-02 source evidence |
| Menu source | `offline/site/new-hp/js/menu3_var.js` line 663; `Menu14_2_3` → `/wrath/wallpapers.xml` | local menu evidence present |

The frozen page entry is derived from `20080509072957` at `/wrath//wallpapers.xml`; the separately retained navigation-gap raw source is the validated `20080402070813` capture of `/wrath/wallpapers.xml`. These timestamps identify different page source records.

## Seven linked sizes

| Size | Page links | Existing original files | Missing originals |
|---|---:|---:|---:|
| `800x600` | 4 | 4 | 0 |
| `1024x768` | 4 | 4 | 0 |
| `1280x960` | 4 | 4 | 0 |
| `1280x1024` | 4 | 4 | 0 |
| `1600x1200` | 4 | 4 | 0 |
| `1680x1050` | 4 | 4 | 0 |
| `1920x1200` | 4 | 4 | 0 |

Each of the seven size labels is linked once for each of four wallpaper sets, giving 28 original-image links. The local baseline contains all 28.

## Wallpaper sets

| Set | Title | Original links | Originals present | Thumbnail | Shadow | Missing |
|---|---|---:|---:|---|---|---:|
| `wall2` | Valgarde Dragon Pens | 7 | 7 | present | present | 0 |
| `wall6` | Utgarde Keep | 7 | 7 | present | present | 0 |
| `wall7` | Daggercap Bay | 7 | 7 | present | present | 0 |
| `wall8` | Logo | 7 | 7 | present | present | 0 |

Sets present in the page are `wall6` (Utgarde Keep), `wall8` (Logo), `wall2` (Valgarde Dragon Pens), and `wall7` (Daggercap Bay).

## Layered result

- Page route: **present** in the frozen baseline (`offline/site/wrath/wallpapers.xml`).
- Page links: **28 original links across 7 sizes and 4 sets**.
- Wallpaper materials: **28/28 originals, 4/4 thumbnails, and 4/4 shadows present**; missing material count `0`.
- A future derived preview can therefore report page-route recovery and wallpaper-material coverage independently.

## Persistent evidence files

- `offline/build-manifest.json` — frozen page and static-asset manifest with source/derived hashes and capture timestamps.
- `research/navigation-gaps-20261015/wayback-missing/source-map.json` — sanitized validated source identity for the 2008-04-02 raw page.
- `research/navigation-gaps-20261015/wayback-missing/replays/wrath_wallpapers-20080402070813.json` — replay validation metadata.
- `research/navigation-gaps-20261015/wayback-missing/cdx/wrath_wallpapers-baseline.json` — 12-row queried CDX range; index evidence only.

