# Round002 sanitized execution summary

Generated `2026-10-13T13:56:07.186225+00:00`. This report intentionally contains no response headers, Cookie values, or response-body content. Raw CDX/entity metadata and bytes remain local under `round002`.

The public Pages release URL `https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/` was passed only as the runner's parent-release scheduling flag; it was not an account credential.

## Execution

- CDX precheck: session `71775`, exit `0`, one real exact-2008 request. HTTP `200`; complete JSON array; 4 candidate rows; 1 entity selection.
- Remaining CDX batch: session `76532`, exit `0`. The existing rank-1 metadata was reused, so 49 new queries were issued. Aggregate summary: 50 attempted, 20 complete (1 complete empty, 19 with rows), 30 transport errors, 0 not attempted.
- Entity batch: session `68045`, exit `0`. 19 planned and attempted, 1 accepted, 0 validation failures, 18 transport errors, 0 not attempted.

## Error evidence

CDX statuses were `20 complete` and `30 transport_or_http_error`. The observed HTTP-status histogram was `200: 20`, `null transport status: 30`. Every CDX transport error was `FetchError` with `network_error:[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1010)`, at ranks 21–50; this is a same-error run of 30 and was never treated as an empty index.

Entity statuses were `1 accepted` and `18 transport_or_http_error`. The observed HTTP-status histogram was `200: 1`, `null transport status: 18`. Every entity transport error was the same `FetchError`/SSL EOF signature at ranks 2–19; this is a same-error run of 18 and was never treated as an empty index.

The current runner used four workers and submitted all bounded pending futures when each phase began. Its ordinary `FetchError` path does not set the stop event and has no consecutive-same-error counter; it also does not cancel or suppress later queued futures. Therefore records after the third same transport error were still attempted. This is a runner limitation against the required three-same-failure stop rule. No retry, additional batch, or proxy switch was performed.

## Accepted resource

- URL: `https://www.worldofwarcraft.com/visa/reward/images/border-bot.gif`
- Capture: `20080402093136` (`baseline_2008`)
- MIME/magic/Pillow: `image/gif` / `gif` / valid
- Length: `1235` bytes
- SHA-256: `b0e30447e867b280a465b999aa7a92a3a1b16dda3b1a51a53365c3ef187dd5de`
- CDX SHA-1 Base32: `2JQRFJR3IKEMZUZYFONXMJOUGBHVVOEY` (match)
- Actual timestamp and Content-Length checks: passed

## Evidence and storage

`evidence.zip` is `112410` bytes with `97` members. ZIP CRC, member sizes, and independent SHA-256 checks passed; the single entity raw member uses `ZIP_STORED`. The round002 output occupies about `815006` bytes after the run, with `26145792000` bytes free on D:. Existing backup maps, ZIPs, and other trees were not overwritten.

Sanitized files written for the parent are `sanitized-summary.json` and this file.
