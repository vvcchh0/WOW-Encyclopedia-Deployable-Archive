# v44 gap-union reconciliation

This is an independent correction to the saved v44 browser receipt. The
original `v44-browser-receipt.json` remains byte-for-byte unchanged (SHA-256
`81d6bc41fb3c1941ccd9ab80dbcb907f2ceeb182926c5c896e101fcf690b6b5c`). No
browser run was repeated.

The receipt has 242 unique `missing-image.svg` image requests and 4 unique
computed CSS placeholder requests, giving 246 placeholder targets. It also
records 35 unique real HTTP 404 URLs. Eight 404 URLs are the apostrophe-named
skill images already present in the placeholder set; the other 27 are the
tree `background.jpg` requests. Therefore the complete observed union is
`242 + 4 + 35 - 8 = 273` unique targets.

All 273 targets are in the previous 1,259-target scope (`new_not_old=0`). The
related-talent bundle contains 986 paths, so the arithmetic reconciliation is
`1259 - 986 = 273`. This is a scope reconciliation only; it does not claim
that any of the 273 targets is recovered or that a placeholder is an original
image.

The exact eight-way overlap and 27 background-only URLs are recorded in
`v44-gap-union-reconciliation.json`.
