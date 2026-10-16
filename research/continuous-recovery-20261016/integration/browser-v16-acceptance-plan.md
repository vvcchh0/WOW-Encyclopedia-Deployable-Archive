# v16 browser acceptance plan (exported, browser checks pending)

The single authorized v16 export is complete; browser checks remain pending. The output is `.scratch/pages-resources-20261016-v16`. No publication was performed.

## Inputs and expected overlay routes

- Reuse `.scratch/offline-navigation-20261015-v15` and its anchor `20080512210044`.
- Final primary overlay count: 28 (19 existing primary records + 9 root-accepted NEWS01/NEWS02 JPEGs).
- Final supplement count: 21 (19 existing supplements + 2 accepted EU2 records).
- Final total: 49 image overlays, confirmed in `root-build-v16.json`, `export-provenance.json`, and `v16-postbuild-verification.json`.
- NEWS01/NEWS02 routes to check directly:
  - `/news/images/06-07/7-13-06-1.jpg` (130x100, 5,493 bytes)
  - `/news/images/06-07/7-27-06-1.jpg` (130x100, 8,477 bytes)
  - `/news/images/06-07/7-27-06-3.jpg` (130x100, 8,110 bytes)
  - `/news/images/06-07/7-13-06-2.jpg` (130x100, 8,769 bytes)
  - `/news/images/06-07/7-13-06-3.jpg` (130x100, 7,033 bytes)
  - `/news/images/06-07/7-27-06-2.jpg` (130x100, 8,740 bytes)
  - `/news/images/07-01/1-18-07-1.jpg` (130x100, 6,962 bytes)
  - `/news/images/07-01/1-18-07-2.jpg` (130x100, 6,030 bytes)
  - `/news/images/07-01/1-18-07-3.jpg` (130x100, 7,189 bytes)
- EU2 related-origin routes to check under the loader's origin namespace:
  - `/_origins/www.wow-europe.com/screenoftheday/screenoftheday/10702-01.jpg`
  - `/_origins/wow-europe.com/screenoftheday/screenoftheday/10703-14.jpg`

## Static and provenance checks

1. Load each of the nine NEWS01/NEWS02 URLs and assert status 200, JPEG magic, 130x100 dimensions, exact accepted byte length/SHA-256, and provenance points to `v16-primary-news-image-source-map.json`.
2. Load the related-images index at `/__offline/related-images/index.html`; assert both EU2 cards exist, retain `pre_2008`, and show the normalized related origin without being mapped into the US Game Guide route.
3. Assert the existing 19 primary/supplement overlays and both EU2 records remain in provenance with source-map hashes and no route collision.
4. Assert `/info/dungeons/karazhan-gallery.html` still uses its local dynamic route and that its current accepted late preview overlays remain available; no NEWS01 asset is treated as a Karazhan entity.
5. Assert `/downloads/ssotd/index.html` still renders the two existing late MEDIA full-image controls and that the two exact thumbs remain separate unresolved controls.
6. Visit one representative page from the 50 player galleries and inspect that missing direct images remain local missing markers. The separate 19 nested thumb routes are payload-available frozen-v15 files with known 2008 capture dates; v4 records their parent/JS relation evidence, and this v16 export does not implement a thumb fallback or promote them into this overlay map.
7. Run the existing v15 sidebar/home smoke checks against the v16 output, then record route, static path, source map, source SHA/length, and screenshot evidence in a new v16 browser receipt.

## Suggested execution order

1. Start a local server rooted at `.scratch/pages-resources-20261016-v16`.
2. Run the existing `research/focused-recovery-20261015-2303/integration/browser_v15.cjs` checks with the output root and add the NEWS01/EU2 checks above.
3. Capture a receipt under this integration directory. Keep `published=false` until root accepts the complete browser evidence.

The browser plan intentionally excludes network requests, publication, and any mutation of the v15 source or manifest. The final input maps are `v16-primary-news-image-source-map.json` and `v16-eu-image-source-map.json`; old NEWS01 receipts remain preserved.
