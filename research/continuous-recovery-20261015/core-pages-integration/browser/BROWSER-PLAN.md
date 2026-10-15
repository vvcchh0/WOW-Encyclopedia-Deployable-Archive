# v9 local browser acceptance preparation

This directory is the bounded browser-validation surface for the root-owned
final Pages export. The runner does not start a server. It refuses to run
unless `--server-ready` is supplied, and it accepts only loopback HTTP traffic
under the supplied Pages prefix. External origins, other non-GET/HEAD methods,
and requests outside the prefix are aborted and retained in the receipt.

The current preparation covers the 11 accepted core targets plus the approved
Battlegroups compatibility alias. PTR aliases are checked separately, so they
do not inflate the 12-target count.

## Evidence inputs and route mapping

- v9 mirror manifest: `.scratch/offline-navigation-20261015-v9/build-manifest.json`
  (expected SHA-256 `0da72688ec5057650c2ef46a4634097323dc9c43eb19997afcad264b12dba3b8`,
  8,328 routes).
- Pages output is expected to use the existing base path
  `/WOW-Encyclopedia-Deployable-Archive/`; pass the actual root-owned base path
  explicitly if it differs.
- Logical `/wrath/artwork.xml` is an HTML record. The exporter therefore emits
  the browser file `wrath/artwork.xml.html`; the runner checks that concrete
  Pages path while retaining the logical route in the receipt.
- The Wrath artwork counters are read from the two accepted local scripts at
  runtime: `screenshotsCommonTotal = 12` and `screenshotsLocTotal = 1`.
  Existing `thumbnailslayout.js` supplies `screenshotsPerPage = 9`; the runner
  derives the expected page count and page-1/page-2 card counts from those
  values and decodes every displayed thumbnail and full image.
- The artwork index uses query pagination. Its card links point to
  `/wrath/art.xml?s=n`; the v9 manifest has no `art.xml` viewer route. The
  runner clicks a real card and records the resulting viewer gap. It does not
  substitute the existing Wrath `fiatLux` lightbox on
  `wrath/features/northrend/howling-fjord.xml.html`, which is checked separately
  as an independent historical interaction.
- The one old SSOTD overlay regression is
  `downloads/ssotd/images/screens/ss1336.jpg`, expected to be 150,293 bytes with
  SHA-256
  `58fcb8db67bc56bf21566fbc05de0d1372a71f4ac4ef65e4eb247ab95abeb289`.
  These values come from the accepted v8 export provenance and are checked by
  a same-origin browser fetch plus image decode.

## Checks performed when the server is ready

1. Visit every core target and record request URL, final URL, HTTP status,
   title, visible text, headings/date evidence, page errors, console errors,
   failed requests, and horizontal overflow. The eight News routes must retain
   their captured month/year date headings.
2. Visit `/ptr`, `/ptr/`, and `/ptr/index.html`. Each must expose the neutral
   historical-exhibit title and sections, no form or editable controls, no
   `javascript:` anchors or inline action handlers, and only the injected local
   Pages runtime script. Archive home, Game Guide, PTR FAQ, and test-realm
   patch notes are opened and must return HTTP 200 with visible text.
3. Visit the old sidebar Battlegroups URL
   `/pvp/battlegrounds/battlegroups.html`; it must return HTTP 200, settle on
   `/pvp/battlegrounds/battlegroups/index.html`, and show a non-empty canonical
   page without a 404/missing-route body.
4. Visit the Wrath artwork page on pages 1 and 2. Assert both counter scripts
   loaded, derive `13` total entries and `2` pages from the live values, expect
   9 cards on page 1 and 4 on page 2, decode every displayed thumbnail and full
  image once, and retain the five provenance-matched pairs and eight known
  missing pairs separately. Record each card's shared border overlay DOM and
  fallback query, click a real card, and record its `/wrath/art.xml?s=n`
  response as the known viewer gap.
5. Open and close a known Wrath `fiatLux` lightbox as a separate control, then
   on SSOTD load the accepted old overlay, exercise previous, next, and close,
   and retain open state plus image digest evidence.
6. Write `v9-browser-receipt.json` and screenshot PNGs under this directory.
   The receipt includes all request route classes and safety failures; a
   browser run is passed only with no disallowed requests, failed requests,
   page errors, unexpected console errors, or check failures.

## Authorized run command

Run only after root explicitly reports loopback server port `29005` ready:

```powershell
$node = "C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
$playwright = "C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\playwright"
& $node "research/continuous-recovery-20261015/core-pages-integration/browser/v9_acceptance.js" `
  --server-ready `
  --base-url "http://127.0.0.1:29005" `
  --prefix "/WOW-Encyclopedia-Deployable-Archive/" `
  --playwright-module $playwright `
  --manifest ".scratch/offline-navigation-20261015-v9/build-manifest.json" `
  --provenance ".scratch/pages-resources-20261015-v9/export-provenance.json" `
  --output "research/continuous-recovery-20261015/core-pages-integration/browser/v9-browser-receipt.json"
```

Final loopback execution used the same command with `--server-ready` and
`--skip-fiatlux` after the independent fiatLux interaction attempt was retained
in `v9-browser-receipt.corrected-run.json`. The final receipt passed 18 checks
with 3,097 requests, zero blocked requests, zero request failures, zero page
errors, and seven final screenshots. The initial and intermediate receipts are
also retained as `v9-browser-receipt.initial-run.json`,
`v9-browser-receipt.corrected-run.json`, and
`v9-browser-receipt.provenance-run.json`.
