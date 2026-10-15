# Local resource deduplication — LOCAL-RESOURCE-DEDUP-003

Generated `2026-10-15T08:15:06.045628Z`. This was a local-only pass: network requests **0**; no production, frozen tree, Git, or deployment changes.

## Page identity

| Page | Route | Derived bytes/SHA | Source staging bytes/SHA | Placeholder occurrences | Unique literal URLs |
|---|---|---|---|---:|---:|
| `zandalar_quests` | `/info/basics/factions/zandalar/quests.html` | 307100 / `95292f7f15271a7873f4dc9dffe68326d72d4664dc213706643190229d5cc261` | 266950 / `7bfb9d92e087ada248315c316ecb0cf01e2176d0250d012a2d09c9b678f8774f` | 252 | 34 |
| `eu_regionals` | `/community/tournaments/euregionals/index.html` | 198997 / `aea0b132e25d61333ef1752eb6a51df1dff59bc5fcc0a6e0ebcfc9db3f3d0dc2` | 183519 / `f5262ddfd3cc61aea980523c0b5bae035775a12ca5d84befb6ec97ebd8220411` | 256 | 175 |
| `insider11_arena` | `/insider/11/arena.xml` | 88146 / `47de7c686ef6eb082213f755e65c89aa701435cbbacd3616b852736a5c5200f6` | 79267 / `e5b1da92429a296788b43e4605292081d9bf015723f3e20a5d2a0d8e6169c044` | 56 | 54 |
| `high_level_options` | `/info/basics/highleveloptions.html` | 88296 / `52090ee9897224661b09ba097ba3fb5172ecdd5f8fbffecea0acf95610a6d973` | 75844 / `f59bbddcfcabba1ce5a7b0f7d7d75ebb6939d4a00f482272c92430c237bc3f1f` | 59 | 41 |

## Dedup and local salvage

The four pages contain **623** placeholder occurrences: **623** literal URL occurrences across **217** unique canonical URLs, plus **0** dynamic/relative values retained separately. Status counts: `{'network_candidate_exact_url': 217}`. Resource purposes: `{'analytics_script': 2, 'layout_spacer': 1, 'page_body_feed': 1, 'page_body_icon': 24, 'page_body_image': 4, 'page_navigation': 95, 'script_condition_reference': 2, 'template_border_or_chrome': 70, 'third_party_footer_or_navigation': 18}`; scopes: `{'non_request_script_literal': 2, 'page_body': 29, 'page_navigation': 113, 'shared_template': 73}`. Of the 217 inventory URLs, **102** are static asset candidates, **113** are page/navigation URLs, and **2** are non-request script-condition literals covering **4** occurrences.

- Exact local map/manifest entities are recorded with local path, SHA-256, byte length, and image Pillow verification when applicable.
- No basename, path, or cross-origin substitution is treated as an alias.
- Existing post-anchor records retain their temporal class; missing placeholders remain `baseline_target_unverified`.

## Highest-value findings

- `1x` `page_body_image` (`page_body`) `http://www.worldofwarcraft.com/insider/11/images/arena/bladesedgemap.jpg` across insider11_arena: `network_candidate_exact_url`; Queue exact URL for a capture preserving origin, path, MIME, timestamp, length, and SHA-256.
- `1x` `page_body_image` (`page_body`) `http://www.worldofwarcraft.com/insider/11/images/arena/float.gif` across insider11_arena: `network_candidate_exact_url`; Queue exact URL for a capture preserving origin, path, MIME, timestamp, length, and SHA-256.
- `1x` `page_body_image` (`page_body`) `http://www.worldofwarcraft.com/insider/11/images/arena/lordaeronmap.gif` across insider11_arena: `network_candidate_exact_url`; Queue exact URL for a capture preserving origin, path, MIME, timestamp, length, and SHA-256.
- `1x` `page_body_image` (`page_body`) `http://www.worldofwarcraft.com/insider/11/images/arena/nagrandmap.jpg` across insider11_arena: `network_candidate_exact_url`; Queue exact URL for a capture preserving origin, path, MIME, timestamp, length, and SHA-256.
- `7x` `page_body_icon` (`page_body`) `http://armory.wow-europe.com/images/icons/class/2.png` across eu_regionals: `network_candidate_exact_url`; Queue exact URL for a capture preserving origin, path, MIME, timestamp, length, and SHA-256.
- `7x` `page_body_icon` (`page_body`) `http://armory.wow-europe.com/images/icons/race/5-0.png` across eu_regionals: `network_candidate_exact_url`; Queue exact URL for a capture preserving origin, path, MIME, timestamp, length, and SHA-256.
- `6x` `page_body_icon` (`page_body`) `http://armory.wow-europe.com/images/icons/class/1.png` across eu_regionals: `network_candidate_exact_url`; Queue exact URL for a capture preserving origin, path, MIME, timestamp, length, and SHA-256.
- `6x` `page_body_icon` (`page_body`) `http://armory.wow-europe.com/images/icons/class/5.png` across eu_regionals: `network_candidate_exact_url`; Queue exact URL for a capture preserving origin, path, MIME, timestamp, length, and SHA-256.
- `6x` `page_body_icon` (`page_body`) `http://armory.wow-europe.com/images/icons/class/7.png` across eu_regionals: `network_candidate_exact_url`; Queue exact URL for a capture preserving origin, path, MIME, timestamp, length, and SHA-256.
- `6x` `page_body_icon` (`page_body`) `http://armory.wow-europe.com/images/icons/class/9.png` across eu_regionals: `network_candidate_exact_url`; Queue exact URL for a capture preserving origin, path, MIME, timestamp, length, and SHA-256.

## Network asset queue

`network-asset-queue.json` contains 16 exact static URLs (limit 16), ordered by semantic purpose so正文 image/icon/static resources precede shared template spacers. Page/navigation placeholders and nonliteral expressions are excluded from the asset queue but remain in the inventory; shared template candidates are listed separately.

| Rank | URL | Purpose | References | Page coverage |
|---:|---|---|---:|---|
| 01 | `http://www.worldofwarcraft.com/insider/11/images/arena/bladesedgemap.jpg` | `page_body_image` | 1 | insider11_arena |
| 02 | `http://www.worldofwarcraft.com/insider/11/images/arena/float.gif` | `page_body_image` | 1 | insider11_arena |
| 03 | `http://www.worldofwarcraft.com/insider/11/images/arena/lordaeronmap.gif` | `page_body_image` | 1 | insider11_arena |
| 04 | `http://www.worldofwarcraft.com/insider/11/images/arena/nagrandmap.jpg` | `page_body_image` | 1 | insider11_arena |
| 05 | `http://armory.wow-europe.com/images/icons/class/2.png` | `page_body_icon` | 7 | eu_regionals |
| 06 | `http://armory.wow-europe.com/images/icons/race/5-0.png` | `page_body_icon` | 7 | eu_regionals |
| 07 | `http://armory.wow-europe.com/images/icons/class/1.png` | `page_body_icon` | 6 | eu_regionals |
| 08 | `http://armory.wow-europe.com/images/icons/class/5.png` | `page_body_icon` | 6 | eu_regionals |
| 09 | `http://armory.wow-europe.com/images/icons/class/7.png` | `page_body_icon` | 6 | eu_regionals |
| 10 | `http://armory.wow-europe.com/images/icons/class/9.png` | `page_body_icon` | 6 | eu_regionals |
| 11 | `http://armory.wow-europe.com/images/icons/class/4.png` | `page_body_icon` | 4 | eu_regionals |
| 12 | `http://armory.wow-europe.com/images/icons/class/8.png` | `page_body_icon` | 4 | eu_regionals |
| 13 | `http://armory.wow-europe.com/images/icons/race/10-1.png` | `page_body_icon` | 4 | eu_regionals |
| 14 | `http://armory.wow-europe.com/images/icons/race/7-0.png` | `page_body_icon` | 4 | eu_regionals |
| 15 | `http://armory.wow-europe.com/images/icons/race/1-1.png` | `page_body_icon` | 3 | eu_regionals |
| 16 | `http://armory.wow-europe.com/images/icons/race/11-1.png` | `page_body_icon` | 3 | eu_regionals |

## Local salvage result

`local-salvage-proposals.json` records the exact lookup scope and page-specific salvage decisions. The current pass found no exact local payload in the approved maps or v7c manifest for the 217 literal URLs; the 232-reference Korean `b.gif` is retained as one shared `layout_spacer` candidate with markup evidence and is not counted as正文缺图. Any visible layout fallback remains a disclosed derived-layer proposal only.

## Lookup scope and validation

The pass read only the final audit/proposals, four v8 derived HTML/provenance entries, v7c build manifest, and the approved static/page source maps listed in `input_hashes`. It did not scan the whole raw workspace.

Every page identity has menu evidence, proposal ID, derived/source path, byte length, and SHA-256. Every reference retains page, line, tag/attribute, markup or CSS context, requested URL, and role evidence.
