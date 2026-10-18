# v33 source delta summary

This is an offline, candidate-only checkpoint list. Root review is still required; it is not an export or deployment claim.

- Authoritative source manifest: research/continuous-recovery-20261018/publication/root-v33-source-receipts-manifest-r2.json (SHA-256 d167a3a6fb79cea2a2b6226238f6b42de3cf80fbd873ce1f32ecd1fe240f2e7d).
- Historical manifest retained and superseded: research/continuous-recovery-20261018/publication/root-v33-source-receipts-manifest.json (SHA-256 a7907560e4b57e348a5c865966b4eb8f048e9cb0b8ff76e9ff0c4bf27f786a93).
- r2 source delta: **120 original-byte images / 17,971,331 bytes**; **109 primary / 11 explicit dated supplements**.
- Source origins: **111 canonical-host / 9 related-host**. Two canonical-host captures dated 2006/2007 were reclassified as dated supplements (474,339 bytes); bytes and accepted copies are unchanged.

## Material classes

- Popup/story: **21**.
- Navigation/news/wallpaper: **68**.
- Guide/static: **29**.
- Ordinary news transfer: **2**.

The r2 host/time policy is authoritative for primary versus supplement. Older per-family role labels are not reused when they conflict with r2.

## Recovery history boundary

- The active status has **53 numbered NET batches** plus **3 control entries** (56 entries total).
- Status classifications: control_accepted=3, index_source_accepted=1, source_accepted=50, source_accepted_with_five_replay_redirects=1, stopped_503=1.
- Historical status totals are **376 accepted images / 21792269 bytes**, with **256 published** and **120 accepted but unpublished** at the snapshot.
- This task made zero network requests. The active status file was read for counts only and is excluded from the candidate list.

## Native archive boundary kept separate

- Native Karazhan: **47** checked, **114 archive 404** responses, **12 observed 302/redirect** responses, **0 transport unknown** remaining. No native image was accepted from that probe.
- Late-2013 thumbnail follow-up: **12 exact indices checked**, all **12 captured 301 HTML**; no image was accepted.
- These index/redirect results are not mixed into the 120 v33 accepted original-byte images.

## Candidate and exclusion boundary

- Candidate JSON contains **312 hashed local files**, including all 45 source/public/visual receipts, 120 accepted original-byte image copies, clean batch plans/bindings/cache/status snapshots/selection manifests, queues, factory scripts/tests/README files, v33 implementation/maps/preflight, and root acceptance helpers/proofs.
- Excluded: runtime output/raw/private payloads, decoded bodies, state and batch reports, headers/Cookies/traces, copied network directories, mutable active status, superseded pre-r2 integration working files, and unaccepted factory-v1 plans.
- Receipt rows can retain private payload metadata for audit, but those values and paths are not copied into the candidate file list. Local source-page HTML/raw payloads are likewise provenance-only and omitted.

## Review status

- Integrity checks passed offline: manifest hashes, all source/public row pairs, all 120 accepted-copy byte lengths and SHA-256 values, and r2 role counts.
- No deployment, page publication, or scientific/runtime completion is inferred from these files.
