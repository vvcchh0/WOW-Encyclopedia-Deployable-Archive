# v52 processed archive release adapter

This isolated adapter prepares source date `20261021`, version `v52`, tag
`archive-20080512-browser-20261021-v52`, and the 2026-10-21 14:10 UTC release
cutoff. It validates an already-created ZIP, reads every member and CRC,
rejects traversal, encryption, and symlinks, extracts the packaged server into
the space-containing smoke directory, and performs real loopback GET/HEAD
checks.

It never creates an archive or contacts GitHub during checking. The upload and
publish scripts retain the owned-draft, three-asset digest, no-clobber, and
published-recovery guards, but are preparation-only here. Existing assets,
drafts, tags, and publication receipts are never overwritten.

The v52 smoke selector retains the source-backed The Broken display mapping:
both the historical `thumb-thebroken.jpg` address and dynamic
`thumb-broken.jpg` address resolve to one canonical JPEG and its public catalog.
The accepted tree declaration is **10,143** site files, while the currently
observed processed tree is **10,144** files. This adapter records those as
separate facts and does not silently reconcile them or assert final v52
acceptance.

The optional Aldor/Scryers smoke remains gated by the explicit
`research/continuous-recovery-20261021/publication/root-v52-final-acceptance.json`
record. It requires an accepted `aldor_scryers_lore` object naming the helper
and both faction page paths. This preparation does not claim that gate has
passed; it preserves the gate requirement for the later root review.

This directory is a checker and preparation artifact. It does not create an
archive, upload assets, contact GitHub, or publish a release.