# NET-RSS-021 proposal only

This directory contains a declaration only. No network request was made and execution is not authorized by this proposal.

- Targets: 3 exact RSS routes; source proposal SHA `966e2e3236fad23023fdd57ee6cbd9177ca3d867ba63f2931dbc1cac5ac1dd4c`.
- Existing NET020 evidence: `9338941a3fb48f03b33d7947aaa568836039baddc2d8c777ee880d6544e91f46`; NET020 completed with 16 attempts, 14 source responses and 7 valid HTML entities.
- Scope: one exact pre-anchor CDX page per target, then at most one latest eligible same-origin status-200 replay.
- Cadence: request starts at least 5.0s apart; dispatch monotonic timestamps at least 5.1s apart.
- Caps: 12 attempts, 240s, 32MiB total body, 16MiB single body, disk floor 11005853696B.
- Stop: 14:05Z cutoff, 429/503, five consecutive transport failures, or any cap; no continuation, late window, redirect follow, or automatic next batch.

| Rank | Exact URL | Prior state | Current evidence | Menu evidence |
|---:|---|---|---|---|
| 1 | `http://www.worldofwarcraft.com/news/rss-08-2006.xml` | `cdx_transport_unknown` | not in NET020; prior NET010 transport_unknown | August, 2006 @ mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu1_var.js:161 (/news/rss-08-2006.xml ) |
| 2 | `http://www.worldofwarcraft.com/news/rss-10-2006.xml` | `cdx_transport_unknown` | not in NET020; prior NET010 transport_unknown | October, 2006 @ mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu1_var.js:159 (/news/rss-10-2006.xml ) |
| 3 | `http://www.worldofwarcraft.com/news/rss-08-2007.xml` | `cdx_transport_unknown` | NET020 `transport_error` / source HTTP `None` / CDX rows `0` | August, 2007 @ mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu1_var.js:147 (/news/rss-08-2007.xml ) |

No all-time archive absence claim is made. Root must issue a separate execution authorization before any request.
