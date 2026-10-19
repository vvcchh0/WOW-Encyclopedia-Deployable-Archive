# Portable publication tools — 2026-10-19

This revision keeps the accepted 2026-10-18 v33 package, source tree and
local/export/browser/Pages receipts as immutable inputs. Output receipts and
the release tag use 2026-10-19. It does not rebuild or rename the ZIP.

The independent package check is recorded in
`../../publication/root-v33-portable-acceptance.json`. Its browser scope is
explicitly partial; package integrity does not certify every historical UI.
The separately recorded current UI audit can add coverage without changing
that bundle.

`create_upload_release.py --version v33` creates an owned draft and uploads
only the processed ZIP, its sidecar and NOTICE. `publish_release.py --version
v33` verifies the exact assets, publishes, then verifies the tag and assets
again. Neither script replaces assets or forces tags. They require the exact
main/origin-main target and stop operations at 14:15 UTC on 2026-10-19.
Each subprocess is bounded by its own timeout and the remaining wall time.
Import and fixture tests perform no network mutations.

The source/checker differences and test results are recorded in
`../../publication/root-release-tools-v3-acceptance.json`.
