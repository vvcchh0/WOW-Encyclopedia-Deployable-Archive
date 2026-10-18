# v33 Pages publication boundary

This folder contains the v33 publication preparation and bounded online
verification helpers.  It does not publish, push, call GitHub, call `curl`, or
create an online receipt during local preparation.

`publish_v33.py --prepare` is intentionally a late-stage root gate.  It reads
the root-frozen v33 source-receipts manifest, the completed v33 provenance and
the four accepted v33 input/export/browser/static-metrics receipts.  It then
compares every provenance record with the accepted v32 local site, requires
all prior image-overlay metadata to remain byte-for-byte equivalent, derives
the new image count and byte total from the manifest, and binds every new or
changed local site object (plus `export-provenance.json`).  The object list is
bounded to 256 entries.  The prior Pages baseline is the accepted v32 commit
`0bcb961f64ea3527bfed41bacf21e670d47a6c3c` and the prior v32 provenance is
read from `.scratch/pages-resources-20261018-v32/export-provenance.json`.

The resulting local gate is written to
`research/continuous-recovery-20261018/publication/root-v33-local-acceptance.json`;
the code remains under this integration folder so root-owned publication
outputs do not get confused with implementation files.

The command is deferred until root has frozen the source manifest, output, and
acceptance receipts:

```powershell
& "$env:CODEX_PRIMARY_PYTHON" -X utf8 research/continuous-recovery-20261018/integration/v33/publication/publish_v33.py --prepare
```

`verify_pages_v33.py --go --root-pages-online-go` is a separate root-owned
online step.  It reads the unpublished local gate and a root-created
`v33-pages-publication.json`, checks the exact Pages build commit before and
after the object pass, tries direct HTTPS before the local proxy in one
process, keeps redirects disabled, and verifies each local object by status,
MIME, length, and SHA.  It is bounded to 256 objects, 512 attempts, 900
seconds, 256 MiB of response bodies, and the same D-drive free-space floor.

The preparation scripts derive counts from the current v33 manifest and
provenance.  They do not retain the earlier provisional 118-image estimate as
an acceptance requirement.  At this preparation checkpoint the v33 manifest,
output, root acceptance receipts, and local gate were absent; therefore no
prepare, publish, online, or network operation was run.
