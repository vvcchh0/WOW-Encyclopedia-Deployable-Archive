# Runtime package verification

Archive: `artifacts/WOW_Encyclopedia_20080512_runtime_20261013.zip`; SHA256 `49048568821e307c03764d486e76ab952b4aea460dd38ccf53f973263386c115`; bytes `502,151,286`.
Members: `8,316`; CRC/SHA256/length/whitelist/checksum verification: `True`.

## Scope

This is a lightweight browse-only package for the 2008-05-12 21:00:44 baseline. It contains the derived site, matching manifest, runtime support and launch files, a package README, and FILE_SHA256SUMS.txt. It excludes the full forensic/raw-download archives and does not claim to close the documented 3,358 gaps.

All source members were written with lossless DEFLATE level 6. Images were copied byte-for-byte and were not re-encoded.

Compression-level correction: the initial level-9 declaration was corrected after code review because explicit ZipInfo writes use the stdlib `_compresslevel=6` path. The existing ZIP payload and SHA256 are unchanged. The original ZIP and split volumes were not read as package inputs and were not modified.

## Budget preflight

- Workspace before: 11,497,586,151 B; conservative ZIP upper bound: 684,654,278 B; projected workspace: 12,182,240,429 B (< 14,000,000,000).
- Disk free before: 28,203,601,920 B; projected free: 27,518,947,642 B (> 11,005,853,696).
- Both guards passed before writing: workspace=`True`, disk=`True`.

## Verification

The finished ZIP was streamed once with ZipFile: every member's decompressed bytes were hashed with SHA256, length and central-directory CRC32 were checked, the exact whitelist was enforced, and FILE_SHA256SUMS.txt was parsed and compared. No full extraction directory was created.

Manifest SHA256: `397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459`; manifest site records: `8,304`; packaged site records: `8,304`.
