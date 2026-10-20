# Common Crawl probe02 preparation

This packet binds the five exact missing news image routes at queue ranks 121,
123, 126, 136, and 137 to the root-accepted prepared queue and the accepted
CC01 `CC-MAIN-2008-2009` collection endpoint.  It reuses the frozen CC01
headers parser and records the accepted CC01 driver as a transport reference;
the new driver is a smaller direct-only exact-query adapter.

The future execution order is exactly five index requests.  Each query uses
`output=json`, `limit=10`, `matchType=exact`, and `showResumeKey=true`.  A
resume key or ten rows sets `incomplete` and never triggers pagination.  Rows
are curated as metadata fields only (`date`, `digest`, `filename`, `offset`,
and `length`); no ARC or image payload is requested.

The packet enforces at most five direct HTTPS attempts over 180 seconds, a
5.25-second request-start cadence, 1 MiB total and 128 KiB per-body limits,
20-second curl limits, a 240-second parent watchdog, TLS verification, no
redirects, no retries, no process proxy environment, and disk floor checks.
429/503 stop immediately with parser-normalized integer or HTTP-date
`Retry-After`, applying a minimum 120-second cooldown; two consecutive
502/504 responses stop the batch.  A 200 response is parsed only when curl
exited zero without an exception; a curl 63/124 or body-limit failure is
recorded as invalid/incomplete `transport_or_body_limit`.  Preparation and
the offline fixture made zero network requests and wrote no raw HTTP.

Only a future root GO receipt that binds plan, driver, fixture, input
bindings, and parent hashes can enter execution.  The current packet contains
no raw response, report, or index-record output.
