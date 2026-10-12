# WOW Encyclopedia 2008 recovery package

This directory contains one large ZIP stream split into three byte-range
assets for GitHub Release upload. The `.001`, `.002`, and `.003` files are **not
independent ZIP archives** and must be downloaded together in the recorded
order.

The source stream is `WOW_Encyclopedia_20080512_offline_recovery_20261012.zip`,
length `2251344514` bytes, SHA256
`66553fcd368ae5ee48dfb9f1b11897ac7fb3fd6a1983a0e303c2c088522c1c63`.

After downloading all assets, run the verifier from the repository checkout:

```text
python tools/release_archive.py verify --manifest release-assets.json
python tools/release_archive.py join --manifest release-assets.json --output WOW_Encyclopedia_20080512_offline_recovery_20261012.zip
```

`verify` streams each part and the combined SHA256 without creating a second
full ZIP. `join` writes only a new `.partial` file, verifies every part and the
combined digest, and atomically publishes the requested ZIP. Existing output
and partial files are refused. `SHA256SUMS.txt` contains the source and part
digests.

For Windows, use a short extraction path such as `D:\WoW2008` to avoid the
legacy path-length limit. The recovered site preserves explicit gaps and is
not a claim that every historical resource or dynamic data feed was captured;
the package reports and browser evidence record those limitations.

No network access is required for verification, joining, or extraction.
