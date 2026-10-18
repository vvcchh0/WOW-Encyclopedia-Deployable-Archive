# v28 input proposal (offline, export not run)

This preparation extends the accepted v27 closure with forty new primary news
image overlays. The four root-owned public-copy receipts are the only new
inputs; each row was checked against its publication copy, SHA-256, length,
and CDX digest by `build_pages_v28.py`. All forty logical URLs are on
`www.worldofwarcraft.com`, and none overlaps a v27 primary or supplement
logical URL. No source bytes are re-encoded or copied into an integration
private-payload directory.

| receipt | SHA-256 | rows | bytes |
| --- | --- | ---: | ---: |
| `research/continuous-recovery-20261018/publication/root-news-unplanned-batch1-public-copy-acceptance.json` | `ee9132a5eac7977ee35ae64cf59d7e446792123a02782f28545a29542b77a816` | 10 | 143870 |
| `research/continuous-recovery-20261018/publication/root-news-unplanned-batch2-public-copy-acceptance.json` | `5c75c481619e79855d383e5334d58a363f316c31d09cfeb5424d96b14ece8dd2` | 10 | 118616 |
| `research/continuous-recovery-20261018/publication/root-news-unplanned-batch3-public-copy-acceptance.json` | `94dcabf875123ba6073ba835bda6e7f4e830cc5c994f882423874f8e812878ab` | 10 | 84073 |
| `research/continuous-recovery-20261018/publication/root-news-unplanned-batch4-public-copy-acceptance.json` | `6d898543de9df58561fb863e7124205b42de6e982c95bb1bb63efd93745a57f8` | 10 | 89705 |

The new map is
`v28-primary-source-map.json` (40 items, 436264 bytes; SHA-256
`d06182cd3b82eae3eaebdb88229bb6efaed8b2b0fdf8f44d7ffa71bbeb20abd2`). It
contains the logical URL, capture timestamp, MIME/dimensions, length, SHA,
CDX digest, and the root public-copy receipt/path for each accepted image. The
map remains `accepted: false` until root input acceptance.

The v28 closure reuses the frozen v25 maps, v26 news/neighbor/guide maps, and
v27 primary/Blizzard supplement maps byte-for-byte. The v27 anchors are:

- `v27-primary-source-map.json` SHA
  `173b83af29adcdf3acb0d90292df1427dc1ef35bee1be3d84874769f6df1d3f9`;
- `v27-blizzard-supplement-source-map.json` SHA
  `00daa553e5d9c640cadc72aeee8a92bed98758d02b1a576b40740b1b42b740b7`;
- v27 preflight SHA
  `268787d944a4c420638f785c202e8288ff834fa371149673ca2065b3d8e9da5b`;
- v27 build receipt SHA
  `297a2c29147f6bf134302fcdd3524f875553d6badcf313e5edd319524b4c2087`;
- v27 output provenance SHA
  `271e474b80ce936c3a68b567a7c3e42c86851eb371772fa8108498613aa1f012`.

The accepted runtime inputs are frozen to exporter SHA
`943f57e2f62582e2659c98766e98deeeda60c9c1d131326f6f0ad6e7fbfd4a00` and
historical-exhibits SHA
`35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011`.
The root-owned expectations binding is
`research/continuous-recovery-20261018/publication/v28-export-expectations.json`
(SHA `7166c32af313f488f1527eaf7672666d825e950d0b33d8eb3475d09e770daf30`);
it is read-only and was not regenerated.

Relative to v27, v28 adds forty primary image records: primary 148 to 188,
supplement remains 75, and total overlays 223 to 263. The expected export
closure is 8357 source records, 8721 declared files, 8722 actual files,
guide collection 39, and guide previews 22. Relative to the online v26
baseline, v28 is 67 additional image records in total (primary +63 and
supplement +4); the v27 four Blizzard supplement records remain part of the
frozen closure. The historical 2007 upgrade announcement is an existing-page
transformation and does not add a page or a new native gallery.

The static root expectations independently project 1146 unique missing images
and 1901 missing occurrences before these forty new marker matches, reducing
the expected integrated counts to 1106 unique images and 1861 occurrences;
40 unique addresses and 40 occurrences are removed by this batch. The
generated impact estimate is deliberately labeled a static
manifest projection (`v28-impact-estimate.json`, SHA
`203cd14484bf5f239c3b42e7380363ee4baa65956885803a73c98f3b736d2146`): it
found 13 manifest references across three routes, while root's expectations
file remains the authoritative full marker audit.

The builder draft is `build_pages_v28.py` (SHA
`e9ba376dec05ac5443a3f2264a5c6b9321780d9921dc0a72f3fac83343d9f7e4`), and
that hash is recorded in both generated audit receipts. Offline preparation and loader preflight completed with no network requests
and no export. The preparation receipt is
`v28-input-preparation.json` (SHA
`fe0b346824cba36f92676a048fb94f8532bc8b01a9fdf0db64e849cbd6a13a6d`); the
preflight receipt is `v28-preflight.json` (SHA
`a5390b8950ff4908b692f31baf7b635e7cecef39cc7d9dd47e151d0e4d1022fa`). The
preflight loaded 40 new primary records and checked 436264 new bytes, while
the frozen closure totals 188 primary, 75 supplement, and 263 total overlays.
The v28 output, partial output, and build receipt do not exist. A later
export requires root input acceptance and the explicit `--go --root-export-go`
gate; this preparation does not grant that gate.
