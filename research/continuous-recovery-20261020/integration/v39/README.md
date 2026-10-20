# v39 local input preparation

This directory prepares a local-only v39 exporter input for two accepted
`payload_digest_reuse` image overlays. The runner starts from the frozen
Source15 site and manifest and reads the new map under this directory. It does
not use the v38 output as an export source, and this preparation step did not
run it.

The target routes and their CDX index dates are:

- `/news/images/04-12/ordernow.jpg` at `20080402082301`
- `/news/images/05-10/trolldire.jpg` at `20080402080557`

Each item carries a separate accepted local payload source URL and May 2008
capture timestamp. The loader must publish the target provenance with
`actual_capture_timestamp: null` and `capture_timestamp_basis:
target_cdx_digest`; the payload source date remains evidence for the reused
bytes. The map's source bytes are the staged r2 copies, each bound by its
SHA-256, length, and CDX SHA-1 digest.

The 2004 news route is handled by the route-scoped historical transformation
in `tools/historical_exhibits.py`; it preserves the headline/date and sibling
entries while replacing only the localized Dec. 16 store notice body with a
static figure and historical notice.

Review `v39-input-preparation.json` and the map before any future `--go` run.

The scoped test and compile receipts are recorded in
`v39-test-execution-receipt.json`; the test counts remain separated by
command (8, 2, and 52).
