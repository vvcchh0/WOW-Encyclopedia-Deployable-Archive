# v37 browser plan r1

Status: prepared and waiting for the root browser GO. This is an additive
read-only ledger; it does not change v36/v37 maps, output, source receipts, or
tools, and it has not opened a browser or made a request.

The ledger is `research/continuous-recovery-20261019/integration/v37/v37-browser-plan-r1.json` (SHA-256
`a922f0e15928f18af3231532c3214493e07b72ed753ef187258bbfd9290d161f` after writing) and binds the v37 native input
`research/continuous-recovery-20261019/integration/v37/v37-native-ui-inputs.json` (SHA-256 `41403b12e3e0869a358fde4434e606246bed9a8f196d0cc55eccfd4f06b83263`).

Coverage is 21 new accepted images plus a separate real Toplist check. All 21
new references are on `news/wow-news2004.html` in recorded `postContainer`
contexts, one exact source line per image, with zero native toggles. The later
browser run must inspect local response bytes, actual `img` source, natural
dimensions, decode state, and visibility without forcing hidden DOM.

Toplist coverage is the original page's Prototype/logic script loading,
`window.onload = init`, default `body.wide` assignment, existing ranking and
navigation content, and the two `body.wide` next/previous CSS backgrounds. The
CSS images count only after a real visible matching element is observed and its
local raster decodes; the commented `lion-top` declaration is explicitly
excluded.

The prior v36 browser result remains a byte/output baseline for already-covered
rows only; its pending/false outcomes are not rewritten as v37 success. The
future run must serve only `.scratch/pages-resources-20261019-v37`, intercept
external requests (expected zero), use correct HTML/XML/HTM MIME, run under a
300-second hard subprocess timeout, and preserve every failed or unresolved row.
No browser, export, network request, or publication was performed by this
preparation.
