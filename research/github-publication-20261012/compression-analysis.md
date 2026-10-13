# Offline deployment compression analysis

Input: `offline/site` (8,304 files, 539,027,834 bytes). Manifest SHA256: `397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459`; site inventory SHA256: `418baadfc262524278c8b0d340eb727fbe97962864e6c24a1fc3d7f737d33997`.
This is a read-only measurement. No site file, manifest, ZIP, compressed artifact, or serving behavior was changed.

## Categories

| Kind | Files | Raw bytes | Gzip-9 bytes | Delta |
|---|---:|---:|---:|---:|
| css | 61 | 489,827 | 97,569 | 392,258 |
| html | 775 | 33,630,459 | 6,249,720 | 27,380,739 |
| image | 7,123 | 490,291,407 | 486,122,052 | 4,169,355 |
| javascript | 161 | 3,387,887 | 484,229 | 2,903,658 |
| other | 5 | 8,761 | n/a | n/a |
| swf | 16 | 1,898,722 | n/a | n/a |
| xml | 163 | 9,320,771 | 1,224,991 | 8,095,780 |

## Main measurements

- HTML/XML/JS/CSS/JSON gzip-9: 46,828,944 → 8,056,509 bytes; theoretical reduction 38,772,435 bytes (82.80% when nonzero).
- Images gzip-9 probe: 490,291,407 → 486,122,052 bytes; delta -4,169,355 bytes. Images were not re-encoded and no output was saved.
- Exact SHA256 duplicates: 179 groups; retaining one payload per group could save at most 2,066,256 bytes across 243 duplicate paths.
- Git object pack files: 497,531,702 bytes; HEAD site tree reports 539,027,834 bytes. No repack/prune/delete was run.

## Recommendation

The current Git object store already uses zlib compression and content-addressed objects. Static text gzip can materially reduce transfer size, but it requires an explicit serving/deployment decision and is not enabled by this measurement. Exact duplicate savings are a storage optimization opportunity only if the deployment layer supports shared payloads; the current site keeps separate paths. Images should remain in their original lossless/lossy encoding because gzip is not an image re-encoder and the probe measures little or negative benefit.

The JSON contains every file's relative path, kind, raw byte length, SHA256 and measured gzip size where applicable, plus duplicate groups and Git/manifest provenance.
