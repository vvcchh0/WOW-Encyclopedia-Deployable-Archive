# Early image digest verification with an explicit single LF

The request is to recover a browsable 2008 site while keeping original responses and actual capture dates. Early static images remain supplements: a complete, unfiltered exact CDX query for all of 2008 must first return `[]`.

The original plan-C run saved 67 distinct JPEG responses. All decoded fully, matched the requested URL and capture timestamp, and had a byte length equal to `x-archive-orig-content-length`. Their raw SHA-1 digests did not match the frozen CDX rows. Those original rejection reports remain unchanged.

Root independently tested a fixed set of 15 local hash variants. For all 67, only `Base32(SHA1(response_body + b'\n'))` matched the indexed digest. Three separately requested `im_` replay samples also matched their saved `id_` bodies. See [local hash diagnosis](root-local-hash-variant-diagnosis.json), [modifier comparison](root-modifier-probe/report.json), and [response diagnosis](agent-c/mismatch-diagnosis.json).

The exact single-LF hash relation is established. A legacy ARC record boundary included in the index digest is a plausible explanation; the underlying ARC records were not obtained, so this storage mechanism is not asserted as proven. Internet Archive's [CDX writer implementation](https://github.com/internetarchive/CDX-Writer/blob/master/cdx_writer.py) distinguishes a stored payload digest from a digest recomputed from parsed content. That implementation alone does not establish the cause for these captures.

The validator therefore gains a narrowly scoped, explicit verification mode rather than ignoring digest failures. It requires both `allow_pre2008_static_supplement` and `allow_legacy_arc_lf_framing`, an actual pre-2008 image, `temporal_class=pre2008_static_supplement`, `cdx_digest_mode=payload_plus_single_lf`, and a nonempty explanation. It compares the original indexed digest with exactly the response body followed by one LF. Missing flags, missing mode, other resource types, other years and other hash differences continue to fail. All existing ZIP, SHA-256, length, image and full-year empty-query checks remain in force.

The image response, ZIP member, SHA-256 and byte length are never changed. Evidence reports separately retain the raw payload SHA-1, the verified index digest, the suffix `0a`, the old rejected attempt and the new verification decision. New source maps are produced from preserved bytes; historical source maps and reports are not rewritten.

Acceptance requires negative tests for the opt-in boundary, independent root validation of newly exported sources, full validation after map integration, and a new frozen-build browser audit. This decision does not establish that the full historical website has been recovered.
