# Karazhan accessibility diagnostics

- Initial report: `sanitized-report.json`; continuation reports: `sanitized-report.continued.json`, `continuation2-result.json`.
- Logical curl calls: `56`; observed non-CONNECT source response blocks: `63`; CONNECT blocks: `55`; redirect blocks: `30`.
- Duplicate target requests: `1`; duplicate was `ss8` after the initial in-flight raw result was omitted from the first report and then re-requested by continuation1.
- Initial stop bug: cumulative transport/5xx counter; 404 responses were interleaved and should reset the consecutive streak. The final report corrects this semantics offline.
- continuation2 stopped after five consecutive curl35 transport failures with CONNECT-only headers (`ss25-thumb`, `ss26`, `ss26-thumb`, `ss27`, `ss27-thumb`); no Memento or source response was observed for those failures.
- Redirect evidence with a 2013 Memento date and guide location is classified as `other_html` subtype `redirect_not_image_with_incomplete_chain` when curl timed out or hit the redirect cap; initial automatic chains requested guide replay URLs, but no completed guide-page body was obtained; later checks stopped at the image URL capture redirect.
- Timeouts can leave unknown additional HTTP requests inside a curl redirect chain; logical curl calls and observed header response blocks are therefore reported separately.
