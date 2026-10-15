# NET-RSS-020 sanitized summary

- Window: `2026-10-15T13:41:33.343700+00:00` to `2026-10-15T13:43:45.840471+00:00`; report updated `2026-10-15T13:43:45.841455+00:00`.
- Targets: 8 (all exact pre-anchor CDX); attempts 16; source responses 14; CDX rows 134; valid payloads 7.
- Body bytes total `1018828`, valid payloads `993993`; stop `completed`.
- Cadence gate min dispatch `5.10899999999674` (required 5.1); min request-start `5.101740121841431` (required 5.0); accepted `True`.

| Rank | Target | Operation | Category | Format | CDX rows | Selected | Memento | PubDate/title evidence |
|---:|---|---|---|---|---:|---|---|---|
| 1 | `/news/rss-11-2007.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `valid_html_payload` | `html` | 13 | `20080402075319` | `2008-04-02T07:53:19+00:00` | `match` |
| 2 | `/news/rss-10-2007.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `valid_html_payload` | `html` | 16 | `20080402075848` | `2008-04-02T07:58:48+00:00` | `match` |
| 3 | `/news/rss-09-2007.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `valid_html_payload` | `html` | 14 | `20080402080213` | `2008-04-02T08:02:13+00:00` | `match` |
| 4 | `/news/rss-08-2007.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `transport_error` | `` | 0 | `` | `` | `unknown` |
| 5 | `/news/rss-03-2007.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `valid_html_payload` | `html` | 14 | `20080402081755` | `2008-04-02T08:17:55+00:00` | `match` |
| 6 | `/news/rss-02-2007.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `valid_html_payload` | `html` | 24 | `20080402081903` | `2008-04-02T08:19:03+00:00` | `match` |
| 7 | `/news/rss-12-2006.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `valid_html_payload` | `html` | 29 | `20080402082658` | `2008-04-02T08:26:58+00:00` | `match` |
| 8 | `/news/rss-11-2006.xml` | `exact_CDX_then_at_most_one_eligible_replay` | `valid_html_payload` | `html` | 24 | `20080402083029` | `2008-04-02T08:30:29+00:00` | `match` |
- HTML `/news/rss-11-2007.xml`: title `WoW -> Archived News -> November, 2007`; full h1 `39`, posted-date `39`, months `{"2007-11": 39}`, range `{"max": "2007-11-28", "min": "2007-11-01"}`; event/description dates kept separately `[]`.
- HTML `/news/rss-10-2007.xml`: title `WoW -> Archived News -> October, 2007`; full h1 `41`, posted-date `41`, months `{"2007-10": 41}`, range `{"max": "2007-10-31", "min": "2007-10-01"}`; event/description dates kept separately `[]`.
- HTML `/news/rss-09-2007.xml`: title `WoW -> Archived News -> September, 2007`; full h1 `29`, posted-date `29`, months `{"2007-09": 29}`, range `{"max": "2007-09-28", "min": "2007-09-01"}`; event/description dates kept separately `["2007/09/06"]`.
- HTML `/news/rss-03-2007.xml`: title `WoW -> Archived News -> March, 2007`; full h1 `27`, posted-date `27`, months `{"2007-03": 27}`, range `{"max": "2007-03-30", "min": "2007-03-01"}`; event/description dates kept separately `[]`.
- HTML `/news/rss-02-2007.xml`: title `WoW -> Archived News -> February, 2007`; full h1 `31`, posted-date `31`, months `{"2007-02": 31}`, range `{"max": "2007-02-28", "min": "2007-02-01"}`; event/description dates kept separately `[]`.
- HTML `/news/rss-12-2006.xml`: title `WoW -> Archived News -> December, 2006`; full h1 `41`, posted-date `41`, months `{"2006-12": 41}`, range `{"max": "2006-12-29", "min": "2006-12-01"}`; event/description dates kept separately `[]`.
- HTML `/news/rss-11-2006.xml`: title `WoW -> Archived News -> November, 2006`; full h1 `54`, posted-date `54`, months `{"2006-11": 54}`, range `{"max": "2006-11-30", "min": "2006-11-01"}`; event/description dates kept separately `["November 18, 2006", "November 20, 2006", "January 16, 2007"]`.

No CDX continuation, late-window request, redirect follow, or integration was performed. Valid entities remain isolated for parent review; exact scoped-empty classifications are not all-time absence claims.
