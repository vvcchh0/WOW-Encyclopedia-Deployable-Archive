# v33 input proposal

v33 is a preparation-only delta over the accepted v32 closure. The frozen
v32 closure remains 350 primary, 89 supplement, and 439 total overlays. The
root source-receipts manifest names 120 new public-copy images (17971331
bytes): 109 official `www.worldofwarcraft.com` primary images and
11 explicit Armory/Blizzard supplement images. The planned
closure is 459 primary, 100 supplement, and
559 total overlays.

The source manifest is `research/continuous-recovery-20261018/publication/root-v33-source-receipts-manifest-r2.json` with SHA
`d167a3a6fb79cea2a2b6226238f6b42de3cf80fbd873ce1f32ecd1fe240f2e7d`. No pending directory, unaccepted receipt, or private
payload path is inspected. Each batch must bind an accepted original source
receipt and an accepted original-byte public-copy receipt, and each public
copy is checked for exact length, SHA-256, CDX digest, MIME/magic, and image
decodability before a map can be written.

The impact estimate separates navigation `missing.html` href recoveries from
`missing-image.svg` static markers using every frozen v32 overlay origin plus
all explicit v33 origins. It does not claim those counts are post-export
browser results. The existing exporter route healing is pinned to
`2a6fa4256ad0853797ae10748ef7842896614d419bdb7ad208d9b258dc8e6488`, historical exhibits to
`35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011`, and the v32 popup/navigation/retired
Armory/attunement acceptance receipts are bound in preparation evidence.

`execute_v33.py` is export-only and requires a separately accepted
`root-v33-input-acceptance.json` plus the explicit `--go --root-export-go`
pair. Until that gate is accepted, no v33 output, partial output, build
receipt, network request, or publication is permitted.
