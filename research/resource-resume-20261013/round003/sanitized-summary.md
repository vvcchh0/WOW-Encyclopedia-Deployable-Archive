# Round003 serial transport recovery

This summary contains no raw response headers, Cookie values, or response-body content. Raw captures remain local under `round003`. The run used one serial curl request at a time through `http://127.0.0.1:7890`, HTTP/1.1, retry 0, 15s connect timeout, 60s request timeout, and TLS verification.

CDX counts: {"accepted": 0, "attempted": 30, "complete": 29, "complete_empty": 29, "not_attempted": 0, "parse_error": 0, "planned": 30, "transport_or_http_error": 1, "validation_failed": 0}; recovered CDX candidates: 0.
Entity counts including the reused probe: {"accepted": 18, "attempted": 17, "complete": 0, "complete_empty": 0, "not_attempted": 0, "parse_error": 0, "planned": 18, "transport_or_http_error": 0, "validation_failed": 0}; network GETs: 17; reused probe: 1.
Total curl requests: `47`; decoded response bytes: `119253`; stop reason: `planned_recovery_completed`.

The round stops before starting another item after three consecutive failures with the same failure signature. Existing complete CDX records and the Round002 accepted border-bot entity were skipped; the successful rank-2 proxy probe was copied locally and reused without another GET.

Accepted resources are listed in `sanitized-summary.json`; raw headers and bodies are stored only inside the round003 directory and are excluded from this report.
