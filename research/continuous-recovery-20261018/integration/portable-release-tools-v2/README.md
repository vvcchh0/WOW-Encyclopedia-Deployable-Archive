# Portable release tools (2026-10-18)

This directory prepares three parameterized release helpers. They are not
invoked during preparation, and no ZIP, GitHub draft, upload, publication, or
release receipt is created here.

Each command requires `--version vNN`. The resolved paths are versioned under
the current run:

```text
site:       .scratch/pages-resources-20261018-vNN/
archive:    artifacts/WOW_Encyclopedia_20080512_browser_20261018_vNN.zip
receipts:   research/continuous-recovery-20261018/publication/root-vNN-*.json
package:    research/continuous-recovery-20261018/publication/vNN-portable-package-report.json
tag:        archive-20080512-browser-20261018
```

`check_portable.py` reads the final local, export, browser, and Pages-online
receipts plus `export-provenance.json`, then checks the package report and
every ZIP member. It preserves the v24 contract for exact member allowlisting,
`FILE_SHA256SUMS.txt`, CRC reads, SHA-256 and length, path traversal and
symlink rejection, compression accounting, disk-floor checks, and isolated
packaged-server GET/HEAD smoke. Guide, gallery, image, browser, and
Pages-online routes are resolved through the provenance `route` to actual
`output_path` index; for example, `/pvp/worldpvp/index.xml` is checked as
`pvp/worldpvp/index.xml.html`. The fixed smoke set also requires the actual
home, encyclopedia, August-news, offline route-map, and
`__offline/pages_runtime.js` files, plus the Karazhan gallery when present.
Every derived smoke path must exist in the final site before the server is
started. The current v32 provenance derives 3 guide groups and 39 guide
images. Changed/new smoke objects come from the versioned root local acceptance
receipt rather than a historical v24 path list.

`create_upload_release.py` verifies the accepted portable ZIP, sidecar, and
`NOTICE.md` bytes; requires `git rev-parse HEAD == git rev-parse origin/main`;
uses the fixed 2026-10-18 tag and deadline; and refuses unrelated assets,
asset replacement, forced tags, unowned drafts, and existing saved-config
adoption. An existing draft is recoverable only when its saved config matches
the exact release id, tag, target, portable-receipt SHA, and three local asset
hashes. GitHub calls occur only if this script is explicitly run later.

`publish_release.py` rechecks all three GitHub asset names, states, sizes, and
SHA-256 digests before and after changing the owned draft to published, then
resolves the tag and requires its commit to equal the exact main/origin-main
target. It refuses an existing publication receipt or an already-published
unowned release. If the saved config is an owned `draft: false` record and the
live release matches its exact id, tag, target, portable-acceptance SHA, and
three asset digests, it writes a recovered publication receipt after read-only
reverification and performs no release mutation.

Bounded offline validation:

```powershell
$py = 'C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
Get-ChildItem .\research\continuous-recovery-20261018\integration\portable-release-tools -Filter '*.py' |
  ForEach-Object { & $py -X utf8 -m py_compile $_.FullName }
& $py -X utf8 -m unittest discover -s .\research\continuous-recovery-20261018\integration\portable-release-tools -p 'test_*.py' -v
```

The fixture checks version/path parameterization, traversal rejection,
provenance-derived route/output paths and group/image counts, actual v32 receipt
shapes, owned-publication recovery, and import-only behavior. It does not
invoke `git`, `gh`, ZIP creation, upload, or publication.
