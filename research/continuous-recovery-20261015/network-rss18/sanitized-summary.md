# NET-RSS-018 sanitized summary

- Window: `2026-10-15T12:49:29.473069+00:00` to `2026-10-15T12:49:52.734290+00:00`; report updated `2026-10-15T12:49:52.734290+00:00`.
- Targets: 8 (7 CDX, 1 saved replay); attempts 11; source responses 5; CDX rows 12; valid payloads 3.
- Body bytes total `341091`, valid payloads `338761`; stop `five_consecutive_tls_or_transport_failures`.
- Gate min dispatch `1.3589999999967404`, min request-start `1.3553400039672852`, accepted `True`.

| Rank | Target | Operation | Category | Format | CDX rows | Selected | Memento | PubDate/title evidence |
|---:|---|---|---|---|---:|---|---|---|
| 1 | `/news/rss-09-2006.xml` | `replay_saved_capture_without_CDX` | `valid_html_payload` | `html` | 0 | `20080402083522` | `2008-04-02T08:35:22+00:00` | `match` |
| 2 | `/news/rss-05-2008.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `valid_html_payload` | `html` | 2 | `20080512204839` | `2008-05-12T20:48:39+00:00` | `match` |
| 3 | `/news/rss-12-2007.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `valid_html_payload` | `html` | 10 | `20080402073657` | `2008-04-02T07:36:57+00:00` | `match` |
| 4 | `/news/rss-11-2007.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `transport_error` | `` | 0 | `` | `` | `unknown` |
| 5 | `/news/rss-10-2007.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `transport_error` | `` | 0 | `` | `` | `unknown` |
| 6 | `/news/rss-09-2007.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `transport_error` | `` | 0 | `` | `` | `unknown` |
| 7 | `/news/rss-08-2007.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `transport_error` | `` | 0 | `` | `` | `unknown` |
| 8 | `/news/rss-03-2007.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `transport_error` | `` | 0 | `` | `` | `unknown` |
- HTML `/news/rss-09-2006.xml`: title `WoW -> Archived News -> September, 2006`; full h1 `38`, posted-date `38`, months `{"2006-09": 38}`, range `{"max": "2006-09-29", "min": "2006-09-01"}`; event/description dates kept separately `["2006/09/19", "2006/09/05"]`.
- HTML `/news/rss-05-2008.xml`: title `WoW -> Archived News -> May, 2008`; full h1 `11`, posted-date `11`, months `{"2008-05": 11}`, range `{"max": "2008-05-08", "min": "2008-05-01"}`; event/description dates kept separately `["May 7, 2008"]`.
- HTML `/news/rss-12-2007.xml`: title `WoW -> Archived News -> December, 2007`; full h1 `29`, posted-date `29`, months `{"2007-12": 29}`, range `{"max": "2007-12-21", "min": "2007-12-01"}`; event/description dates kept separately `[]`.

No CDX continuation, late-window request, redirect follow, or integration was performed. Valid entities remain isolated for parent review.
