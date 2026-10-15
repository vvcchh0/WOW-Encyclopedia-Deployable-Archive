# NET-RSS-021 sanitized summary

- Window: `2026-10-15T13:53:45.087707+00:00` to `2026-10-15T13:54:44.324839+00:00`; report updated `2026-10-15T13:54:44.324839+00:00`.
- Targets: 3 (all exact pre-anchor CDX); attempts 6; source responses 4; CDX rows 54; valid payloads 2.
- Body bytes total `326250`, valid payloads `316313`; stop `completed`.
- Cadence gate min dispatch `5.10899999999674` (required 5.1); min request-start `5.100589990615845` (required 5.0); accepted `True`.

| Rank | Target | Operation | Category | Format | CDX rows | Selected | Memento | PubDate/title evidence |
|---:|---|---|---|---|---:|---|---|---|
| 1 | `/news/rss-08-2006.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `valid_html_payload` | `html` | 23 | `20080402083605` | `2008-04-02T08:36:05+00:00` | `match` |
| 2 | `/news/rss-10-2006.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `valid_html_payload` | `html` | 31 | `20080402083154` | `2008-04-02T08:31:54+00:00` | `match` |
| 3 | `/news/rss-08-2007.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `transport_error` | `` | 0 | `` | `` | `unknown` |
- HTML `/news/rss-08-2006.xml`: title `WoW -> Archived News -> August, 2006`; full h1 `35`, posted-date `35`, months `{"2006-08": 35}`, range `{"max": "2006-08-31", "min": "2006-08-01"}`; event/description dates kept separately `["2006/08/11"]`.
- HTML `/news/rss-10-2006.xml`: title `WoW -> Archived News -> October, 2006`; full h1 `53`, posted-date `53`, months `{"2006-10": 53}`, range `{"max": "2006-10-31", "min": "2006-10-01"}`; event/description dates kept separately `[]`.

No CDX continuation, late-window request, redirect follow, or integration was performed. Valid entities remain isolated for parent review; exact scoped-empty classifications are not all-time absence claims.
