# Storage inventory and low-repetition organization proposal

Generated at 2026-10-14T12:21:35.701573Z. This was a read-only local inventory; network access was not used and no existing source, backup, ZIP, or historical tree was modified.

## Current capacity

- Workspace logical files: 102,684; bytes: 15,491,395,569 (14.427 GiB).
- D: free after scan: 43,342,139,392 bytes (40.366 GiB); required minimum: 11,005,853,696 bytes (10.250 GiB); check: True.
- The root and top-level buckets count logical file bytes. Symlinks and reparse points were skipped; scan errors are listed in summary.json.

## Major derived trees

| Tree | Files | Bytes | GiB | v3 comparison |
|---|---:|---:|---:|---|
| .scratch/pages-historical-exhibits-20261014-v3 | 8,436 | 556,973,434 | 0.519 | canonical v3 provenance |
| .scratch/pages-resources-20261014-next | 8,436 | 556,962,330 | 0.519 | 7791 same; 644 changed; +0/-0 records |
| .scratch/pages-historical-exhibits-20261014 | 8,436 | 556,951,423 | 0.519 | 7794 same; 641 changed; +0/-0 records |
| .scratch/pages-historical-exhibits-20261014-v2 | 8,436 | 556,950,753 | 0.519 | 7796 same; 639 changed; +0/-0 records |
| .scratch/pages-historical-exhibits-20261014-final | 8,436 | 556,947,741 | 0.519 | 7794 same; 641 changed; +0/-0 records |
| .scratch/pages-resources-20261014 | 8,418 | 555,512,030 | 0.517 | 7769 same; 648 changed; +0/-18 records |
| .scratch/offline-package-smoke-20261011-retry | 572 | 62,983,096 | 0.059 | not a Pages provenance tree |
| .scratch/offline-package-smoke-20261011 | 571 | 62,981,392 | 0.059 | not a Pages provenance tree |
| .scratch/gallery-inspection-20261013 | 3 | 1,974,010 | 0.002 | not a Pages provenance tree |
| .scratch/pages-remote-baseline.json | 1 | 436 | 0.000 | not a Pages provenance tree |
| .scratch/pages-settings.json | 1 | 66 | 0.000 | not a Pages provenance tree |

The four older 8,435-record Pages variants are close copies by content records, but they are not exact full-tree duplicates. The early pages-resources-20261014 export has 8,417 records and is missing 18 v3 paths. The per-record SHA/length comparison in summary.json preserves this distinction.

## Existing delivery ZIPs

| ZIP | Bytes | Sidecar SHA-256 | Runtime archive check |
|---|---:|---|---|
| artifacts/WOW_Encyclopedia_20080512_full_source.zip | 14,272,092 | a8a41a5cb1e6a1a85fc5a379a6b3a53f860c720ca4f028c716fbee8ee7eb4e34 | sidecar only |
| artifacts/WOW_Encyclopedia_20080512_gap_review_20261011.zip | 321,588 | c7dc499ce7daf53422d48ff7b777cd2970e8b47768c6cb02dab925b046a95483 | sidecar only |
| artifacts/WOW_Encyclopedia_20080512_offline_20261011.zip | 16,885,336 | cfa0d0b34442759868905b8ab08ec2dde4270d4e7538eba7d7dcc2d9dfb6d5ae | sidecar only |
| artifacts/WOW_Encyclopedia_20080512_offline_recovery_20261012.zip | 2,251,344,514 | 66553fcd368ae5ee48dfb9f1b11897ac7fb3fd6a1983a0e303c2c088522c1c63 | sidecar only |
| artifacts/WOW_Encyclopedia_20080512_runtime_20261013.zip | 502,151,286 | 49048568821e307c03764d486e76ab952b4aea460dd38ccf53f973263386c115 | verified |
| artifacts/WOW_Encyclopedia_20080512_sample_and_reassessment.zip | 6,601,592 | 5d23d49010d98049162ea7ce64a0c6f4b84ad8f519cc435c0d5e3a3ed8c2bd25 | sidecar only |
| artifacts/WOW_Encyclopedia_20101203_source.zip | 3,563,037 | 9b074874780d93c55a9edd98e2dd2d498c524e4dddd2d09fd4c981e03550437d | sidecar only |

The 20261013 runtime ZIP was streamed once and matched its sidecar: 49048568821e307c03764d486e76ab952b4aea460dd38ccf53f973263386c115. Its bytes remain separate from the new v3 portable browser candidate.

## Compression and savings

- Reused full measurement for offline/site: 46,828,944 text bytes to 8,056,509 gzip-9 bytes, saving 38,772,435; images 490,291,407 to 486,122,052, saving 4,169,355.
- Other/SWF bytes total 1,907,483; the existing report did not claim a gzip saving for those binary kinds.
- Exact duplicate payload analysis found 179 groups / 243 redundant paths and a theoretical maximum of 2,066,256 bytes if paths could reference one content copy.
- v3 payload raw bytes from provenance: 549,434,795; estimated compressed payload: 499,706,618; estimated saving: 49,728,177. The estimate reuses measured category ratios and does not create an archive.

## Tool fit and executable organization plan

tools/package_runtime_archive.py cannot directly package v3. Its source collection is fixed to offline/site, offline/build-manifest.json, offline/support, and the runtime launcher files; it has no source-root or Pages-export option. A future v3 packer must include the current export tree plus provenance, the accepted 36 image overlays, historical exhibits, and the 50 directory fixes, then perform the same streamed verification contract.

The dry-run plan is portable-package-plan.ps1. It checks required inputs, the runtime sidecar, and free space, then prints intended staging/package inputs without moving, deleting, compressing, or creating an archive.

## Recommendations

1. Use .scratch/pages-historical-exhibits-20261014-v3 as the single canonical portable browser staging tree. It carries 8,435 Pages output records, 36 image overlays, the current historical exhibit output, and current export provenance. Keep the source manifest SHA tied to 397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459.
2. Retain each older Pages tree only as a named snapshot with its export-provenance.json and a compact v3 diff record; do not treat equal file names as equal content. The five older trees occupy 2,783,324,277 logical bytes together. Compared with v3, the older variants differ in 639–648 output hashes; the four 8,435-record variants differ only in HTML, while the early resources tree also differs in JS and Pages support records and has 18 missing records.
3. Keep artifacts/WOW_Encyclopedia_20080512_runtime_20261013.zip and its sidecar byte-for-byte unchanged. The existing runtime archive is 49048568821e307c03764d486e76ab952b4aea460dd38ccf53f973263386c115 and its current bytes match the sidecar. It is a separate 2008 runtime deliverable and should not be regenerated from the v3 Pages tree.
4. Before publishing a new portable ZIP, build a source-root-aware packer or wrapper that includes the v3 tree, export-provenance.json, the accepted 36 image overlays, historical exhibits, the 50 directory fixes, and a loopback launcher/server; verify the finished ZIP by streamed SHA, CRC, length, and whitelist checks. tools/package_runtime_archive.py hardcodes offline/site, offline/build-manifest.json, offline/support, and runtime launcher inputs. It has no source-root, Pages-export, overlay, or v3 provenance option, so it cannot directly package v3.
5. Use the existing measured compression profile for budgeting, then package once after acceptance. The offline/site report measured 38,772,435 bytes saved from text and 4,169,355 from images; the v3 payload is 549,434,795 raw bytes with an estimated 499,706,618 compressed bytes. This is an estimate, not a new archive result.
6. Keep at least 10 GiB plus 256 MiB free on D: before any future write, and use a separate temporary output directory for the new archive. The current inventory is read-only and D: was checked against the project safety threshold. No deletion, move, NTFS compression, or packaging was performed by this report.

## Validation and limits

- Sentinel hashes before and after the scan: True. The set includes offline/build-manifest.json, current v3 export-provenance.json, every existing ZIP sidecar, and package/compression source summaries.
- Representative actual v3 and older-tree files were hashed and checked against their provenance records. Full re-hashing of every older derived tree was intentionally avoided because the provenance records already carry per-output SHA-256 values; this keeps the inventory bounded and does not claim current old-tree bytes beyond the sampled files.
- No package was built, no NTFS compression was enabled, no directory was moved, and no historical ZIP or source tree was deleted.

Unknowns for the future portable package: exact compressor output, launcher/server inclusion, and the independent acceptance record for the 50 directory fixes require a packaging/acceptance pass after the source tree is frozen. Current provenance independently confirms 8,435 outputs and 36 image overlays.
