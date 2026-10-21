# v51 processed archive release adapter

This isolated adapter pins source date `20261021`, version `v51`, tag
`archive-20080512-browser-20261021-v51`, and the 2026-10-21 14:10 UTC
cutoff. It validates an already-created ZIP, reads every member and CRC,
rejects traversal, encryption, and symlinks, extracts the packaged server into
the space-containing smoke directory, and performs real loopback GET/HEAD
checks.

It never creates an archive or contacts GitHub during checking. The upload and
publish scripts retain the owned-draft, three-asset digest, no-clobber, and
published-recovery guards, but are preparation-only in this task.

The v51 smoke selector also validates the source-backed The Broken display mapping: both the historical `thumb-thebroken.jpg` address and the dynamic `thumb-broken.jpg` address resolve to the one canonical JPEG and its public catalog. The expected v51 tree contract is 10,143 files; this adapter does not claim that count until the final v51 receipts and provenance exist.

The optional Aldor/Scryers smoke is gated by the explicit
`research/continuous-recovery-20261021/publication/root-v51-final-acceptance.json`
record. It requires an accepted `aldor_scryers_lore` object naming the helper
and both faction page paths. The current v49 record says the lore panel is a
known gap and the v49 site has no helper, so preparation records this gate as
missing and does not treat the source adapter acceptance as a release pass.

This directory is a checker and preparation artifact. It does not create an
archive, upload assets, contact GitHub, or publish a release.
