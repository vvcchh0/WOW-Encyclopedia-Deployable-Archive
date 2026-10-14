# Wayback accessibility probe001 (corrected offline report)

- Network attempts: `6/14`; no HTTP request was reissued for this correction.
- Raw body bytes: `3585/33554432`; D: `40523395072` free before, floor `11005853696`.

## Controls

- archive.org robots: proxy fallback HTTP 200; direct attempt was curl 28 timeout.
- CDX: unavailable; direct curl 28 timeout and proxy process timeout after CONNECT-only 200 (source status recorded as `null`).
- Known replay: proxy HTTP 200, 3347 bytes, JPEG/Pillow valid, SHA256 and CDX SHA1 match; normalized Memento timestamp `20080512212653`.

## Outcome

- CDX metadata availability: `false`; known JPEG replay availability: `true` via proxy.
- General image inventory follow-up was not executed because no inventory/plan target list was supplied.
- Raw response headers remain local under `raw/`; this summary contains no raw header text.
- Original report is preserved as `sanitized-report.json`; this file is an offline evidence correction.
