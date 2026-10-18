# v27 input and closure proposal

Status: prepared, offline-preflighted, root-accepted, and exported once under the guarded GO. Publication was not executed.

## Frozen closure

The proposal reuses the accepted v26 closure without changing it:

- source15 manifest: `D:\WOW_Encyclopedia\.scratch\offline-navigation-20261015-v15\build-manifest.json`, SHA-256 `d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002`, anchor `20080512210044`;
- v25 provenance: `.scratch/pages-resources-20261016-v25/export-provenance.json`, SHA-256 `e0f6d3d631091d091ed4e515030e64136eda6b17368236f8e815453a141d579e`;
- v26 provenance: `.scratch/pages-resources-20261018-v26/export-provenance.json`, SHA-256 `f5580948c5df72a744577e15bf9165ee7ec477c5adf4b458e5db0241acd9c332`;
- accepted v26 export: `research/continuous-recovery-20261018/publication/root-v26-export-acceptance.json`, SHA-256 `4addc91ba8166da663f44220a46dcafd7c974be0cdd53267bb18c9cb05692373`, with 8,654 declared and 8,655 actual files;
- v26 guide collection remains 3 groups/39 images and guide previews remain 22;
- approved exporter: `tools/export_github_pages.py`, SHA-256 `943f57e2f62582e2659c98766e98deeeda60c9c1d131326f6f0ad6e7fbfd4a00`.

The frozen v25 primary/supplement map closure and the accepted v26 news and neighbor maps are checked by SHA in `build_pages_v27.py`. The builder does not hash old image payloads during preparation or preflight.

## New accepted inputs

There are 27 new original-byte copies: 23 `www.worldofwarcraft.com` primary news overlays and 4 `www.blizzard.com` supplements. The 10th batch2 candidate, `http://www.worldofwarcraft.com/news/images/08-02/02-06-08-3.jpg`, remains transport-unknown and is intentionally excluded.

| accepted public-copy receipt | source receipt SHA-256 | public-copy receipt SHA-256 | count | bytes | role |
|---|---|---:|---:|---:|---|
| `publication/root-news8-next-public-copy-acceptance.json` | `4556ae3670a21f783d9f3f6efff321a3ee404c50edf5c46d56f4c0d1836eea32` | `d0ff0ceed01649f869f886ee178cd260e56553db0a88a3cb2452b42b29b86583` | 8 | 103,004 | 4 primary + 4 Blizzard supplement |
| `publication/root-news20-batch1-public-copy-acceptance.json` | `cc9c41ada9a7a1a820632370a5de97881416e74c09f086c5fb07faf37e14c6b7` | `43c78a0095fc671fb99d15775ecb3b6b9aea64a8e53156728ea050b3be3ccc0d` | 10 | 72,137 | primary news body |
| `publication/root-news20-batch2-public-copy-acceptance.json` | `a2f3f3015d73c9ff2a986647bcc9eb3ce4078b4f5106242637bc2d77bc730229` | `e26605ed0debbf86acb87d54522c3c7d65221a39646ddfc919e35959122ef9df` | 9 | 89,711 | primary news body |

The exact original URL, capture timestamp, MIME, length, SHA-256, CDX digest, and integration copy path for every row are in the two maps below. All `local_path` values point into `integration/v27/accepted-images/`; no private payload path is staged.

- Primary map: `v27-primary-source-map.json`, 23 items, SHA-256 `173b83af29adcdf3acb0d90292df1427dc1ef35bee1be3d84874769f6df1d3f9`.
- Blizzard supplement map: `v27-blizzard-supplement-source-map.json`, 4 items, SHA-256 `00daa553e5d9c640cadc72aeee8a92bed98758d02b1a576b40740b1b42b740b7`.

The four supplement routes preserve their distinct origin namespace:

```text
_origins/www.blizzard.com/WoW/images/screens/fansitekit.jpg
_origins/www.blizzard.com/WoW/images/screens/transportation/ss11-thumb.jpg
_origins/www.blizzard.com/WoW/images/screens/transportation/ss12-thumb.jpg
_origins/www.blizzard.com/WoW/images/screens/transportation/ss14-thumb.jpg
```

The 23 primary output paths are the exact `/news/...`, `/screenshots/...`, or `/contests/...` paths encoded in `v27-primary-source-map.json`; the 19 newly recovered 2008 body paths are:

```text
news/images/08-01/01-02-08-1.jpg
news/images/08-01/01-02-08-2.jpg
news/images/08-01/01-02-08-3.jpg
news/images/08-01/01-09-08-1.jpg
news/images/08-01/01-09-08-2.jpg
news/images/08-01/01-09-08-3.jpg
news/images/08-01/01-16-08-1.jpg
news/images/08-01/01-16-08-2.jpg
news/images/08-01/01-16-08-3.jpg
news/images/08-01/01-30-08-3.jpg
news/images/08-01/01-31-08.jpg
news/images/08-02/02-05-08-1.jpg
news/images/08-02/02-05-08-2.jpg
news/images/08-02/02-06-08-1.jpg
news/images/08-02/02-06-08-2.jpg
news/images/08-02/02-07-08-1.jpg
news/images/08-02/02-07-08-2.gif
news/images/08-02/02-12-08-1.jpg
news/images/08-02/02-14-08-1.jpg
```

The four news8 primary paths are `contests/07-10-pumpkin/images/news_pumpkin.jpg`, `news/images/06-07/artcontestlogo.gif`, `news/images/07-02/upgradenow.gif`, and `screenshots/images/thaddeus.jpg`.

## Static impact estimate

`v27-impact-estimate.json` is a source-manifest reference estimate only (SHA-256 `d298efee0012b0580b34e8bba21dffa341ea39f55b7cb950444c36f4c823ff18`). It found four affected source routes:

- `/news/rss-01-2008.xml` — 10 batch1/early batch2 image references;
- `/news/rss-02-2008.xml` — 2 late batch2 image references;
- `/news/rss-07-2006.xml` — 1 `artcontestlogo.gif` reference;
- `/news/wow-news2004.html` — 2 `thaddeus.jpg` references.

The estimate is 16 placeholder reference occurrences across 4 unique page routes. Twelve of the 27 accepted assets have no frozen manifest reference: `news_pumpkin.jpg`, `upgradenow.gif`, all four Blizzard supplements, and six batch2 paths whose references are outside the frozen manifest projection. These remain valid accepted overlay inputs; the estimate does not claim browser or post-export proof.

## Preflight and minimal builder

`build_pages_v27.py` is the only new executable draft. It imports the frozen v25 map constants, appends the v26 and v27 maps, validates the three public-copy receipts and only the 27 integration copies, checks the frozen JSON/map/tool SHAs, and runs the exporter loaders only on the two new maps. It has no network operation and does not call a full export unless both `--go --root-export-go` are provided after root acceptance.

Real preparation command:

```powershell
$py='C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -X utf8 research/continuous-recovery-20261018/integration/v27/build_pages_v27.py --prepare --preflight
```

Result: exit 0, `network_requests=0`, `export_executed=false`. Preflight receipt: `v27-preflight.json`, SHA-256 `268787d944a4c420638f785c202e8288ff834fa371149673ca2065b3d8e9da5b`. It checked 216,325 bytes of new primary copies and 48,527 bytes of new supplement copies; old image payloads were not rehashed. The expected future export closure is 148 primary overlays, 75 supplement overlays, 223 total overlays, 8,681 declared files, 8,682 actual files, guide collection 39, and guide previews 22.

Preparation receipt: `v27-input-preparation.json`, SHA-256 `513b60015051e6f4073b842f4e9de3a2832e8e7756215a7fe3eac886bec1acf2`. No output, partial output, worker receipt, v26 file, old map, source manifest, or tool was modified. D: free space was 47,517,454,336 bytes before preparation and 47,517,384,704 bytes after it, above the required 11,005,853,696-byte floor.

The root acceptance bound the two map SHAs, the impact SHA, the preflight SHA, all three source receipts, and the approved exporter tool before the single `--go --root-export-go` call.

## Single export result

Root supplied `publication/root-v27-input-acceptance.json` and authorized one execution of:

```powershell
$py='C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -X utf8 research/continuous-recovery-20261018/integration/v27/build_pages_v27.py --go --root-export-go
```

The run completed with `published=false`, `network_requests_by_builder=0`, 8,681 declared files, 8,682 actual files, 223 overlays, 148 primary overlays, 75 supplement overlays, 39 guide-collection images, and 22 guide previews. Output: `.scratch/pages-resources-20261018-v27`. Build receipt SHA-256 is `297a2c29147f6bf134302fcdd3524f875553d6badcf313e5edd319524b4c2087`; provenance SHA-256 is `271e474b80ce936c3a68b567a7c3e42c86851eb371772fa8108498613aa1f012`.

The 27 new output routes were checked against their integration copies: all 27 existed and all 27 SHA-256 values matched, including the four `_origins/www.blizzard.com/...` routes. The final output had no `.partial` directory and no duplicate export was run.
