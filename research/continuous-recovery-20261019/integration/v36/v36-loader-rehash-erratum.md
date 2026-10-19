# v36 loader rehash erratum

Status: additive clarification only. This note does not amend the frozen
`v36-preflight.json`, `v36-source-closure.json`, maps, root acceptance gate, or
their recorded bindings.

The preparation field `old_image_payloads_rehashed: false` is inherited
template wording. It means that preparation did not run a separate duplicate
full-image audit after map construction. It must not be read as a statement
that the exporter skipped validation of old overlay payloads.

The pinned exporter (`tools/export_github_pages.py`, SHA
`60fa3cb3279bd2478de73d861fc648efaeda760ca8ee609e4ba3cf3b3030f35d`) reads
each existing overlay payload and performs its recorded length and SHA-256
checks in the image-overlay loaders (the `read_bytes`/`hashlib.sha256` path at
the loader implementation around lines 447–451). Consequently the v36
preflight loader validation covered the inherited closure: 534 primary records
(`22,054,019` bytes) and 100 supplement records (`11,186,023` bytes), with no
HTTP requests and no export execution during preparation.

The false legacy field is retained for byte-for-byte audit history. No frozen
JSON or accepted binding was rewritten, and no loader pass was rerun for this
clarification.
