# GitHub public deployment inventory (2026-10-12)

This is a read-only, offline inventory. No Git, Release, ZIP, site, or remote state was changed.

## Deployable runtime

Run `python tools/offline_mirror.py serve --site offline/site --manifest offline/build-manifest.json --host 127.0.0.1 --port 8765`. The frozen serving closure is `offline/site/**` plus `offline/build-manifest.json`; `offline/support/**` is retained for build/provenance context.

`offline/site`: 8,304 files, 539,027,834 bytes; largest file `offline/site/downloads/wallpapers/images/103/bloodelves_2560_1600.jpg` (3,929,521 bytes).
`offline/support`: 4 files, 47,667 bytes; largest file `offline/support/vendor/scriptaculous-1.6.5/effects.js` (32,635 bytes).
Combined serving tree plus support: 8,308 files / 539,075,501 bytes.
Manifest: 73,067,980 bytes, SHA-256 `397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459`, `8,304` file entries; output paths present 8,304/8,304.
The bounded workspace scan found 50,372 regular files / 10,982,915,018 bytes, excluding this inventory directory; D: free space was 19,318,562,816 bytes at scan time.
One manifest source reference is an archived ZIP-member locator (`backups/gap-review-20261011/late/menu-xml-20080914055020.zip#objects/b17f55397b566f5a5f60be6dd4d9939169d1cfb31f9cea196493dd5bd37f51d7.bin`); it is a build/provenance pointer and does not affect serving because all `8,304` output paths exist.

The serve path reads the site directory and manifest only. A clone of this serving closure does not need the raw source entities, approved maps, CDX responses, overlays, or historical ZIPs. Those inputs are required only when rebuilding the derived tree.

## Git selection

The proposed selection is 8,364 files / 640,403,689 bytes including the serving tree, support, manifest, source tools/tests/packaging/docs, and the explicitly listed final reports.
Largest selected non-directory file: `offline/build-manifest.json` (73,067,980 bytes). All selected files are below the 100 MiB Git blob limit: `True`.

Track all regular source/document files under `tools/`, `tests/`, `packaging/`, and `docs/`, excluding `__pycache__` and bytecode. Track the key final reports listed in `inventory.json`; their SHA-256 values make later release assembly auditable.

## Integrity and exclusions

Selected serving/support trees contain 0 symlink/reparse entries. Sensitive filename markers: 0; personal/private screenshot markers: 0.
The `offline/site/screenshots` paths are public historical site assets; the filename scan found no personal/private screenshot marker.

Exclude raw CDX/HTTP response forests, backups, mirror/source entities, old offline-site copies, generated caches, and the 2.25 GB historical ZIP from Git. Preserve those as local provenance or Release assets under the repository's separate volume plan.

## Acceptance limits

No clone, server launch, upload, or network request was performed. The report establishes static closure and size evidence; a final release should still run the existing browser acceptance report and a clean-clone loopback smoke before publishing.

See `inventory.json` for exact selected source/report paths, SHA-256 values, manifest checks, and runtime/build dependency distinctions.
