# GitHub Pages v55 accepted-change verification

This preparation binds the exact 69 rows in `research/continuous-recovery-20261022/root-v55-export-acceptance.json` at `online_changes_from_v53` to the accepted local tree `.scratch/pages-resources-20261022-v55`. It independently checked each listed file's byte count and SHA-256, and bound the v55 browser acceptance receipt and matching `export-provenance.json`. The accepted list totals 15,966,420 bytes. The export receipt's separate `added` plus `changed` summary contains 24 entries; this batch follows the explicitly supplied `online_changes_from_v53` roster and records that count separately rather than substituting it.

The request transport, TLS configuration, pacing, response-size enforcement, disk check, and status/cooldown handling reuse the hash-pinned v53 verifier and its shared transport. This adapter fixes the batch at 69 logical objects, 138 maximum HTTP attempts, a 1,200-second hard batch limit, 64 MiB total and per-object response limits, 30-second request timeout, 6.2-second request-start spacing, and an 11,005,853,696-byte D: free-space floor. It uses direct first and process-local `127.0.0.1:7890` only after transfer failure. Redirects and automatic retries are off. HTTP 429/503 stops immediately with cooldown handling; five consecutive transfer failures stop the batch and preserve the failure tail and cooldown.

The Pages commit and Actions run are pending deployment. They are `null` in the current plan and manifest, so production execution is refused. After root supplies the deployment identifiers, set `pages_commit` and `actions_run` in `plan.json`, then rerun offline validation. The wrapper carries those fields into the manifest, offline record, and bindings. Root must then create a fresh GO bound to the new hashes; an older GO cannot authorize this batch.

Offline preparation and fixture command:

```powershell
python -B research/continuous-recovery-20261022/network/github-pages-v55-changes69/verify_pages_v55_changes69.py --offline-validate
```

The fixture exercises all 69 objects with synthetic successful bodies plus one synthetic direct transfer failure followed by a proxy success. It reports 69 matches across 70 mocked attempts. That temporary mock runtime is removed; the production `runtime/` stays absent and no real request, subprocess, download, or Git operation is performed.

The only future network entry point is:

```powershell
python -B research/continuous-recovery-20261022/network/github-pages-v55-changes69/verify_pages_v55_changes69.py --execute --go <fresh-root-v55-GO.json>
```

The GO must use schema `wow-root-github-pages-v55-changes69-go/v1`, set `accepted` and `root_go` to true, identify this batch, have a future `valid_until`, and bind the plan, wrapper, manifest, offline validation, input bindings, pinned v53 wrapper/transport, both accepted receipts, object-set hash, Pages commit, and Actions run. Raw HTTP headers, response bodies, and cookie jars remain private below `runtime/private/raw/`; `runtime/object-match-summary.json` contains only curated URL, status, MIME, byte/hash match, timing, transport and aggregate data.
