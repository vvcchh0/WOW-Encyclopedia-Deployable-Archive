# v36 browser plan r1

Status: prepared and waiting for the root browser GO. This is an additive
read-only plan. It does not change the v36 maps, preflight, output, source
receipts, or exporter, and it has not opened a browser or made a request.

The executable target ledger is
`v36-browser-plan-r1.json` (SHA-256
`b486aeb601abbce94c441f5566649ee30e1001b9e2d6c1e50ace147cf1ca95a3`). It was
derived from the frozen
`v36-native-ui-inputs.json` (SHA-256
`b945faba376f600d169b4ed798c95bbc44643d8352244d56a6e1595bae3b1bbc`) and
pins the v36 provenance
`74494d4cd1153299e9c957fbe75488cd35d4d26c013a60f36e4293c1f454e88c`.

Coverage is 51 accepted image targets and 53 source references:

- 35 static news images from `news/wow-news2004.html`, all in the recorded
  `postContainer` source context. The source input has no native toggle IDs;
  inspect the actual local `<img>`/`<source>` element and its natural dimensions
  and decode state. Do not synthesize an expansion or claim a toggle.
- 7 other static source references: one ordinary HTML image from
  `insider/07/anatomy.html`, plus six style/background literals from
  `insider/12/magtheridon.xml` (two),
  `burningcrusade/townhall/professions.html` (two),
  `insider/11/arena.xml`, and `insider/06/interview.html`. These six are
  `text_literal` evidence. Check the actual output style or computed
  background and raster decode; a source marker alone is not an `<img>` or a
  proof that the background is visible.
- 3 CSS source targets: `pvp/tournament/css.css` and the next/previous rules in
  `toplist/includes-client/css/styles-en.css`. The input records five CSS
  references because next and previous each have normal/hover rules. Their
  `property` fields are currently null, so the browser run must resolve the
  selector and computed property from the actual output and keep unresolved or
  hidden cases explicitly pending.
- 6 Visa exhibit figures from `visa/css/creditcard.css`, rendered on the
  derived `/visa/index.html` page. Verify each local raster's `src`, natural
  dimensions, decode, and figure visibility. Also assert that the page has no
  application or signup form, `ApplyNow`/account CTA, issuer/business target,
  mouseover/Flash action, or external business navigation. Only the existing
  local archive/reward exhibit navigation may remain.

Every ledger row carries the exact original URL, served output path, source
page, source-page SHA-256, source line/column, source reference kind, and the
frozen display class. The run must use those rows as its locator evidence and
must retain failed, hidden, or unresolved rows rather than promoting them to a
visual success.

Execution boundary for the future root-authorized run:

1. Serve only `.scratch/pages-resources-20261019-v36`; use the already
   accepted local server conventions and correct HTML MIME for `.html`, `.xml`
   derived `.html`, and `.htm` assets.
2. Intercept and count all external requests. Expected external requests are
   zero. Do not fall back to the network or to a guessed same-basename asset.
3. Run in bounded batches. For each HTML-image target, record actual local
   `src`, natural width/height, `complete`, decode result, bounding-box
   visibility, and the source page/line binding. For text/CSS targets, record
   the actual selector/style property, computed background URL, decode, and
   visibility; classify declaration-only or hidden cases as such.
4. Preserve the original 2004 news page context and do not force hidden DOM
   into view. A native toggle is only successful when the original page control
   is activated and the expected container becomes visible; the frozen v36
   input currently declares zero such toggles.
5. Keep screenshots and result receipts additive under the v36 browser folder;
   do not overwrite the export or preparation receipts. The browser run is
   separately gated and is not part of this preparation.

The input ledger is intentionally more conservative than a source-only
claim: CSS/text literals remain runtime checks, Visa figures are a historical
exhibit contract, and zero native toggles is an input fact rather than a claim
that every source page is visually interactive.
