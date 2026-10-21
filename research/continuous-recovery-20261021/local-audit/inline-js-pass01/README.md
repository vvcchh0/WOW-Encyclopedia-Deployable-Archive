# v45 non-gallery inline JavaScript syntax pass

This read-only audit parsed the actual v45 HTML records listed as `html` or `menu_html` in export provenance. Records whose route/output/source path identified an explicit gallery, SSOTD, screenshot, or original-art collection were excluded. External scripts and JSON script blocks were not rechecked here; the prior external-JavaScript audit covered the former.

Scope: 946 provenance HTML records; 879 included; 67 excluded; 0 missing output records.
HTMLParser found 12051 executable inline occurrences and 2322 unique bodies after SHA256 deduplication.
Node `--check`: 2322 unique bodies checked; 2322 passed, 0 failed, 0 timed out, 0 unknown. Each check had a 5-second timeout and used `.scratch/test-temp-20261021/inline-js-pass01` for temporary files.

No syntax failures were observed in the deduplicated executable inline set.

Evidence: `inline-inventory.json`, `syntax-results.json`, `failure-analysis.json`, and `audit_inline_js.py`. JavaScript was parsed only; no page script, handler, or network request was executed.
