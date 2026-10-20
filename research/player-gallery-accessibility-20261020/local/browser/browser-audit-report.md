# Player gallery browser audit

This receipt records the bounded loopback Playwright run against the frozen v39 export. It visited all 50 current gallery-content routes and the Zul'Aman XML wrapper serially, with external browser requests aborted. The run started at `2026-10-20T14:13:13.815Z`, finished at `2026-10-20T14:13:42.852Z`, and took 29,034 ms. The server and browser were closed after the run.

## Browser result

- Gallery routes: **50 requested, 50 visited, 50 HTTP/navigation successes**.
- Extra wrapper: **1 requested, 1 visited, 1 success**. `/info/dungeons/zulaman.xml` returned a local 302 to `/info/dungeons/zulaman.xml.html`, which returned 200. It has no native gallery runtime (`numShots`/`shotList` absent) and remains a separate wrapper check.
- Page errors: **0**. Local request failures: **0**. External activity: **0** (all browser requests were restricted to loopback).
- Runtime native list: **1,684** `shotList` entries across the 50 gallery pages; every visited gallery had matching `numShots` and `shotList` lengths.
- First-page native grid: **580 cells across all 50 pages; all 580 rendered the local `__offline/missing-image.svg` fallback**. `native_image_404s: 0` means the fallback SVG endpoint returned HTTP 200; it does not mean native JPEG full/thumb targets were available. The exact 3,368 native full/thumb identities come from the static package and root acceptance, not from the browser result's prior working `Set` values.

The browser output now omits those working `Set` fields rather than serializing them as `{}`. Each result points to the static identity source in `identitySource`; the compact interpretation and counts are also in [browser-audit-summary.json](browser-audit-summary.json).

## Separate guide layers

Guide material is reported separately from native screenshot targets:

- **Guide previews:** 6 provenance groups with 22 images. The browser observed 22 preview images in Fishing (4), Hallow's End (4), Brewfest (4), Winter's Veil (4), Zul'Aman (3), and City Attacks (3); all **22/22 decoded** in the page DOM, with zero preview placeholders.
- **Guide image collections:** 3 provenance groups with 39 large images: Love is in the Air (12), Lunar Festival (11), and World PvP (16). The all50 gallery plus Zul'Aman-wrapper pass observed **0** collection image routes in the browser DOM; these are not native `numShots` sequences. An exact provenance-listed local v39 Pillow check found the files present and decodable **39/39**, recorded separately in [guide-layer-decode-check.json](guide-layer-decode-check.json). That local decode is not a browser observation.
- The 39 guide collection images and 22 previews are therefore not added to native screenshot counts, and the browser result does not infer native availability from their presence.

## Screenshots

Screenshots were taken after scrolling the existing gallery content into view, without injecting markup or images. Each is 1440×1000 RGB:

- [Karazhan](screenshots/karazhan.png) — SHA-256 `0f133db25352165933d95f70e0db001cdd6b8cdb73caffbab50c7ee6277e35f5`
- [Black Temple](screenshots/black-temple.png) — SHA-256 `614fbae35442af558a62997d90a47e3a9a45b6ab976ae87c9dc854550d4f0324`
- [Fishing](screenshots/fishing.png) — SHA-256 `380cc0bca99db30b85641c63ff3ddb39925b13cef215d7252c11270ce9fb5787`
- [Lunar Festival](screenshots/lunar-festival.png) — SHA-256 `4ac514d6c7f87bc9097beeb8ab2885d8ddbc39a838622b32825a4fb03739826a`

## Inputs and boundaries

- Frozen v39 provenance SHA-256: `02b1cd43766288f96c879ef464d7198bb09d1085008ae3e500773d594f6c7760`.
- Static identity input: [gallery-accessibility-50.json](../gallery-accessibility-50.json). Root independently validated its 50 declarations and 3,368 exact target identities.
- Full raw browser receipt: [browser-audit-all50.json](browser-audit-all50.json).
- The browser pass was local-only and did not query archive or network sources. The guide-layer decode check read only the 61 exact provenance-listed image files (22 previews and 39 collection images); it did not perform a recursive workspace scan.
- After the completed browser run, the JSON receipts were enriched offline with the explicit placeholder and guide-layer interpretation, and the runner was patched to omit non-observation `Set` fields. The browser was not rerun for that metadata-only change.

