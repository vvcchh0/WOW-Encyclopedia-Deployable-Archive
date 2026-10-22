# ArchiveCraft Dungeons page batch

This directory prepares a bounded, root-GO-gated observation of the four ArchiveCraft pages not already present in the accepted local cache. It does not acquire the nine image files.

The reusable runner is `archivecraft_dungeons01.py`. Its five-page allowlist is fixed in the script and the plan roster. `plan.json` schedules four URLs and points at the existing Dungeons landing-page body under the prior batch's private runtime. The cache stays in its original location and retains its original 2026-10-21 observation time. The runner verifies the cache byte length and SHA-256 before accepting the plan.

`target-config.schema.json` describes the URL, page-target, and local-cache evidence fields. A cached page must bind its exact URL to an HTTP 200 response, observation time, body length, and SHA-256. Any changed request set changes `plan.json`; regenerate the hashes in `input-bindings.json` and require a root GO document bound to the resulting hashes before any network execution.

The runner has three modes:

- `--offline-fixtures` exercises parsing, provenance extraction, URL filtering, redirects, rate limits, transport fallback, payload budgets, private raw-file retention, and no-network behavior. It uses only stub responses and temporary directories.
- No flags validates the plan and prints the prepared state. It makes no network requests.
- `--execute --go PATH` is the only network entry point. It refuses execution if cache review is incomplete, the runtime directory already exists, input hashes differ, the GO is absent/expired/mismatched, or the D: free-space floor is not met.

The four remaining targets are `townhall/dungeons/instances/`, `townhall/dungeons/instances/outland/`, `/about/`, and `/disclaimer/`. The first two support page-level tracing of dungeon media; About and Disclaimer record what the site itself says about asset sources and scope. The reported Wayback/Reddit/Imgur/GitHub attribution and the separate 2003 article lead remain source statements until checked against the captured pages and source evidence.

Only static HTML is parsed. The public inventory reports safe source URLs, observation times, request start/end, status, effective URL, safely filtered redirect edges, body length/SHA-256, title, matching source statements, image-tag links, enclosing image links, and figure captions. Query strings, fragments, URL credentials, and control characters are excluded. Ordinary navigation links and XML index entries are not image links. Raw headers, cookies, stderr, and full response HTML stay under `runtime/private/`; only a sanitized inventory is written publicly.

The runner will issue no more than 10 curl attempts in a 10-minute window, with starts separated by at least 6.2 seconds, total body bytes capped at 16 MiB, and each logical page capped at 4 MiB across direct and proxy attempts. It tries direct first and uses process-local `127.0.0.1:7890` only after a transport failure. TLS verification is enabled; redirects and curl retries are disabled. HTTP 429/503 stop immediately with a cooldown of at least 120 seconds or the longer Retry-After value. Five consecutive transfer failures also stop the batch and preserve the failed raw tail. The runner checks free space on D: before and after each attempt and before/after report writes, requiring at least 11,005,853,696 bytes.

## Current status

The Dungeons landing page is reused from `research/continuous-recovery-20261021/network/archivecraft-guides01/runtime/private/raw/attempt-04-archivecraft-dungeons-direct.body`; it is not copied or re-fetched. The other four pages were absent from the parent-provided prior-cache review and are queued for the later root-GO batch. `reuse_review.complete` means only that the local cache reconciliation is complete; it does not indicate root approval to execute.

The reported 2003-12-10 article is recorded in `plan.json` as a parent-supplied lead. It was not retrieved during this offline preparation. The parent also reports that Source16/v52 already contains nine 2008-04-02 full-size screenshot entities; their image decoding, thumbnail, and display checks are being handled separately. This batch therefore makes no image request. No Wayback/CDX call, page discovery, paid crawler, publication, or change to Source15/16, accepted builds, or historical ZIPs is part of this batch.
