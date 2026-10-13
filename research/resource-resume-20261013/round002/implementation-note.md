# Round002 runner implementation note

`run_round002.py` remains the compatibility entrypoint and hands off to
`run_round002_impl.py`. The `preflight` and `cdx-plan` phases are local-only.
The new `cdx` phase is gated by both `--allow-network` and the parent release
token; it uses one pooled transport per worker, at most four workers, one
full-year exact query per logical URL, a 60 second request timeout, no retry,
and a 1,200 second batch deadline. Queries omit status/mime filters,
`collapse`, and `showNumPages`. Successful HTTP-200 responses are retained as
raw JSON with headers and a complete/parse result; parsed rows retain all
statuses and MIME values. Existing per-URL metadata is reused without a
blind retry.

The generated entity plan chooses the latest status-200 image capture not
after `20080512210044` as `baseline_2008`; when none exists it selects the
earliest 2008 image after the anchor as `late_2008`. The `entity` phase makes
one `id_` request per selected item, preserves the body before digest
validation, and records actual Memento time, MIME, magic, Pillow decode,
SHA-256, and independent CDX SHA-1 Base32 results. Only strict accepted
records enter `entity-source-map.json`; failures retain metadata and any
observable body. When at least one entity is accepted, the phase also writes
an untracked local `evidence.zip` plus `evidence-verification.json`; CDX/raw
and metadata members are preserved, entity bytes use `ZIP_STORED`, and every
member is checked for CRC, size, and SHA-256 before the ZIP is retained.
Shared decoded response bytes are capped at 128 MiB, each
request is guarded by the 14,000,000,000-byte workspace / 11,000,000,000-byte
free-space / 256 MiB reserve checks, and each object is capped at 16 MiB.

Local validation on 2026-10-13:

* bundled Python 3.12 `py_compile` for both runner files: exit 0;
* `run_round002.py --self-test`: exit 0; headered/headerless CDX parsing,
  baseline/late selection, empty/malformed response handling: pass;
* `--phase preflight` and `--phase cdx-plan`: exit 0, 50 planned queries,
  network false;
* `--phase cdx --allow-network` without the parent token: rejected before any
  request (exit 1);
* a local mocked transport fixture: one PNG entity accepted with CDX digest,
  MIME/magic, Pillow, actual timestamp, and SHA-256 checks; no Archive request.

The real CDX/entity phases were not started in this preparation pass. The
implementation files were SHA-256 hashed after the checks; current values are
recorded in the parent task response and should be recomputed before a live
release.

The mocked local entity fixture exercised the accepted path but was removed;
therefore no evidence ZIP was created in this preparation pass.

For an HTTP-level non-200 CDX response, the reviewed pooled transport exposes
bounded status/headers/body-preview/traceback through `FetchError` rather than
the full body. The runner records that error and never labels it a complete
empty result; successful HTTP-200 CDX responses retain the full raw JSON.
