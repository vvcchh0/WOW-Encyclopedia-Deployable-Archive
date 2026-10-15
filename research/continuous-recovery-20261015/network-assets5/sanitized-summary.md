# NET-ASSETS-005 sanitized recovery summary

Input candidates SHA-256: 71d084172c775ddae8063e622ae45c1fc2e8b72283030c6dc31d9110abfdcf0a.
Request window: 2026-10-15T08:32:09.773735+00:00 to 2026-10-15T08:33:53.424743+00:00; report updated: 2026-10-15T08:33:53.424743+00:00.
Attempts: 27; source responses: 23; failed attempts: 4; CDX source responses: 12; replay source responses: 11; valid entities: 11; redirect evidence: 0.
Categories: cdx_empty_in_range 1, transport_error 3, valid_image 9, valid_javascript_counter 2.
Disk free before/after: 39025238016 / 38991900672 bytes.

| # | kind | URL | category | capture | source HTTP | Memento | bytes | reason |
|---:|---|---|---|---|---:|---|---:|---|
| 1 | javascript_counter | http://www.worldofwarcraft.com/wrath/images/artwork/artworkcounter.js | valid_javascript_counter | 20080402024808 | 200 | 2008-04-02T02:48:08+00:00 | 28 | valid_script |
| 2 | javascript_counter | http://www.worldofwarcraft.com/wrath/images/artwork/en_us/artworkcounter.js | valid_javascript_counter | 20080402024820 | 200 | 2008-04-02T02:48:20+00:00 | 24 | valid_script |
| 3 | image | http://www.worldofwarcraft.com/insider/11/images/arena/bladesedgemap.jpg | valid_image | 20080402014105 | 200 | 2008-04-02T01:41:05+00:00 | 11366 | valid_image |
| 4 | image | http://www.worldofwarcraft.com/insider/11/images/arena/float.gif | valid_image | 20080402013957 | 200 | 2008-04-02T01:39:57+00:00 | 16394 | valid_image |
| 5 | image | http://www.worldofwarcraft.com/insider/11/images/arena/lordaeronmap.gif | cdx_empty_in_range |  |  |  | 0 | no_capture_rows_in_query_range |
| 6 | image | http://www.worldofwarcraft.com/insider/11/images/arena/nagrandmap.jpg | valid_image | 20080402014001 | 200 | 2008-04-02T01:40:01+00:00 | 15951 | valid_image |
| 7 | image | http://armory.wow-europe.com/images/icons/class/2.png | valid_image | 20070313200001 | 200 | 2007-03-13T20:00:01+00:00 | 1054 | valid_image |
| 8 | image | http://armory.wow-europe.com/images/icons/race/5-0.png | valid_image | 20070313200020 | 200 | 2007-03-13T20:00:20+00:00 | 1052 | valid_image |
| 9 | image | http://armory.wow-europe.com/images/icons/class/1.png | valid_image | 20070313195950 | 200 | 2007-03-13T19:59:50+00:00 | 971 | valid_image |
| 10 | image | http://armory.wow-europe.com/images/icons/class/5.png | transport_error |  |  |  | 0 | no_http_status |
| 11 | image | http://armory.wow-europe.com/images/icons/class/7.png | valid_image | 20080402081053 | 200 | 2008-04-02T08:10:53+00:00 | 1011 | valid_image |
| 12 | image | http://armory.wow-europe.com/images/icons/class/9.png | valid_image | 20070810182234 | 200 | 2007-08-10T18:22:34+00:00 | 1174 | valid_image |
| 13 | image | http://armory.wow-europe.com/images/icons/class/4.png | transport_error |  |  |  | 0 | no_http_status |
| 14 | image | http://armory.wow-europe.com/images/icons/class/8.png | valid_image | 20070313200100 | 200 | 2007-03-13T20:01:00+00:00 | 985 | valid_image |
| 15 | image | http://armory.wow-europe.com/images/icons/race/10-1.png | transport_error |  |  |  | 0 | no_http_status |

Counter scripts were observed as text only; no JavaScript was executed and no count was inferred from missing values.
Original headers, traces, bodies, and scripts remain only in this batch raw directory. No entity was copied into the offline mirror.
