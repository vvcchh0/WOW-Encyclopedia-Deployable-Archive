# v56 Pages change verification preparation

This batch is for the 22 entries in the future root export receipt's
online_changes_from_v55 list. It does not contain an object manifest yet:
paths and hashes are intentionally read only after
research/continuous-recovery-20261022/root-v56-export-acceptance.json and
root-v56-browser-acceptance.json exist and are accepted.

Run the offline policy check first:

    python -X utf8 research/continuous-recovery-20261022/network/github-pages-v56-changes22/verify_v56_changes22.py --offline-validate

After root supplies the final Pages commit and successful Actions run, prepare
the fixed input manifest with those exact identifiers:

    python -X utf8 research/continuous-recovery-20261022/network/github-pages-v56-changes22/verify_v56_changes22.py --prepare --pages-commit <full-commit-sha> --actions-run <numeric-run-id>

Preparation requires root export accepted=true, browser accepted=true for
v56, matching local site and provenance hashes, no browser page errors or
external requests, and exact local size/SHA-256 agreement for every accepted
change row. It refuses any row count other than 22, duplicate or unsafe path,
unsupported MIME suffix, changed local bytes, out-of-scope file, or byte-cap
violation. Preparation performs no network requests and refuses to overwrite
an existing manifest/plan/bindings set.

Root GO must use schema wow-root-github-pages-v56-changes22-go/v1 with
accepted=true, root_go=true, batch_id=github-pages-v56-changes22,
an unexpired UTC valid_until, and exact values for every go_required_fields
entry in plan.json. The execution command is:

    python -X utf8 research/continuous-recovery-20261022/network/github-pages-v56-changes22/verify_v56_changes22.py --execute --go <root-go-json>

The runner is pinned to the reviewed v53 transport adapter and shared request
runner. It targets the fixed GitHub Pages base URL, uses direct first and only
falls back to the process-local 127.0.0.1:7890 proxy after a transfer
failure, verifies TLS, disables redirects and automatic retries, schedules
request starts at 6.4 seconds, and stops if measured starts are under the
5.0-second hard minimum. Limits are 22 logical objects, 44 HTTP attempts, 20
minutes, 64 MiB total and per object, 30-second requests, and a disk floor of
11,005,853,696 bytes before/after requests and summary writes. HTTP 429/503
and five consecutive transfer failures stop the batch; failure tails are
preserved and the fifth transfer failure sets a cooldown of at least 120
seconds. The first execution creates runtime/ with exclusive directory
creation; any existing runtime blocks another batch.

Raw response bodies, headers, and cookies stay under runtime/private/.
runtime/object-match-summary.json contains only safe URLs and curated
status, timing, MIME, length, and SHA-256 observations. No request, object,
manifest, or GO has been fabricated or executed in this preparation.

The offline fixture tests the 6.39-second allowed interval versus the
4.99-second hard stop, direct-to-proxy fallback condition, five-entry failure
tail and cooldown floor, request/time/body caps, transport command flags, and
the 22-object target count. Its synthetic roster is descriptive only; it is
not a persistent target manifest.
