# NET-RSS-016 sanitized summary

- Window: `2026-10-15T12:08:55.420140+00:00` to `2026-10-15T12:09:30.115333+00:00`; report updated `2026-10-15T12:18:28.943939+00:00`.
- Targets: 8 (6 CDX, 2 saved replays); attempts 11; source responses 5; CDX rows 25; valid payloads 3.
- Body bytes total `507904`, valid payloads `503221`; stop `five_consecutive_tls_or_transport_failures`.
- Gate min dispatch `1.3589999999967404`, min request-start `1.3539838790893555`, accepted `True`.

| Rank | Target | Operation | Category | Format | CDX rows | Selected | Month/title evidence |
|---:|---|---|---|---|---:|---|---|
| 1 | `/news/rss-07-2007.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `valid_html_payload` | `html` | 13 | `20080402080637` | `match` |
| 2 | `/news/rss-06-2007.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `valid_html_payload` | `html` | 12 | `20080402080828` | `match` |
| 3 | `/news/rss-04-2007.xml` | `replay_saved_eligible_capture_without_requery` | `valid_html_payload` | `html` | 0 | `20080402081359` | `match` |
| 4 | `/news/rss-09-2006.xml` | `replay_saved_eligible_capture_without_requery` | `transport_error` | `` | 0 | `20080402083522` | `unknown` |
| 5 | `/news/rss-05-2008.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `transport_error` | `` | 0 | `` | `unknown` |
| 6 | `/news/rss-12-2007.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `transport_error` | `` | 0 | `` | `unknown` |
| 7 | `/news/rss-11-2007.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `transport_error` | `` | 0 | `` | `unknown` |
| 8 | `/news/rss-10-2007.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `transport_error` | `` | 0 | `` | `unknown` |
- HTML `/news/rss-07-2007.xml` full-source evidence: h1 `57`, posted-date `57`, months `{"2007-07": 57}`, range `{"max": "2007-07-31", "min": "2007-07-01"}`; event/description date candidates retained separately `["July 22, 2007"]`.
- HTML `/news/rss-06-2007.xml` full-source evidence: h1 `49`, posted-date `49`, months `{"2007-06": 49}`, range `{"max": "2007-06-29", "min": "2007-06-01"}`; event/description date candidates retained separately `["2007/06/27", "June 10, 2007"]`.
- HTML `/news/rss-04-2007.xml` full-source evidence: h1 `39`, posted-date `39`, months `{"2007-04": 39}`, range `{"max": "2007-04-30", "min": "2007-04-01"}`; event/description date candidates retained separately `["August 3, 2007"]`.

No CDX continuation or redirect follow was performed. Accepted entities remain isolated for parent review and were not integrated.
