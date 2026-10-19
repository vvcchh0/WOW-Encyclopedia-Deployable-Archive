# v33 resource frontier audit (offline)
This audit read the frozen v33 export and historical local evidence only. It issued **0 network requests** and proposes no executable plan.
## Coverage ledger
- v33 `missing-image.svg` image-marker uniques observed by this scan: **1411**; news **386**, static **642**, JavaScript-derived marker URLs **383**. The frozen v33 expectation declares **900** static missing images / **386** news uniques, while the separate native dynamic-gallery ledger remains **3368** entities. These scopes are not merged.
- State counts: `{"complete_empty_or_404": 36, "encoding_variant_review": 3, "excluded_or_deferred": 3, "executed_evidence_needs_row_review": 14, "plan_or_queue_only": 10, "uncovered": 1345}`.
- Canonical boundary recount: **900** unique / **1524** occurrences across **1104** HTML/HTM/XML/CSS files (excluding `_origins/`); news **386**. Expanded-minus-canonical is **511**: extra `_origins` **131**, extra JS/JS-path **383** (origin/JS overlap **3**), other **0**.
- URL normalization: 902 raw unique values collapse to 900 canonical keys; explicit default-port raw values **16**, HTTP/HTTPS same host/path groups **7**. HTTP and HTTPS remain distinct unless an accepted source-reviewed alias says otherwise.
- Historical evidence scan now includes output source maps and batch reports plus 20261016 publication/local-audit and 20261018 integration; URL-bearing files **1258**, executed URL keys **2782**, planned/queue URL keys **2299**. Ten representative row-level dedup examples are in `dedup_examples` in the JSON; plan-only rows remain non-executed.
- Explicit v33 navigation recovery: 71 unique originals; 71 accepted or explicit aliases.
- New high-information candidate ledger: **80** (40 news, 40 static).
- The old `next-frontier-selected70.json` exclusion closure has 10 rows: `{"complete_empty_or_404": 4, "encoding_variant_review": 3, "excluded_or_deferred": 3}`. These rows are excluded before candidate selection; space-containing small-pets literals remain encoding-review only.
- The machine-readable JSON contains the complete 80-row `candidate_shortlist` with URL, state, and marker source line; it is intentionally separate from the larger ledger and dynamic 3368-entity scope.

## Candidate shortlist

|rank|category|state|URL|source|line|
|---:|---|---|---|---|---:|
|1|news|uncovered|`http://www.worldofwarcraft.com/contests/beowulf/images/beowulf_news.jpg`|`.scratch/pages-resources-20261018-v33/news/rss-10-2007.xml.html`|2258|
|2|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-06/european-beta/signups.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3787|
|3|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-06/fanart/fanart01.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|4230|
|4|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-06/fanart/fanart02.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|4231|
|5|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-06/fanart/fanart03.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|4232|
|6|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-06/fanart/fanart04.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|4152|
|7|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-06/fanart/fanart05.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|4153|
|8|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-06/fanart/fanart06.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|4154|
|9|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-06/fanart/fanart07.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|4023|
|10|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-06/fanart/fanart08.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|4024|
|11|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-06/fanart/fanart09.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3825|
|12|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-06/fanart/fanart10.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3826|
|13|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-06/fanart/fanart11.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3827|
|14|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-06/fanart/fanart12.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3828|
|15|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-06/pvp/pvp1alliance.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3990|
|16|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-06/pvp/pvp2horde.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3991|
|17|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-07/european-beta/signups.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3691|
|18|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-07/fanart/fanart13.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3721|
|19|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-07/fanart/fanart15.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3722|
|20|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-07/fanart/fanart17.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3620|
|21|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-07/fanart/fanart18.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3621|
|22|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-07/fanart/fanart20.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3622|
|23|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-07/fanart/fanart21.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3623|
|24|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-07/fanart/fanart22.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3570|
|25|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-07/fanart/fanart23.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3571|
|26|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-07/fanart/fanart24.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3572|
|27|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-07/fanart/fanart25.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3573|
|28|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-07/fanart/fanart26.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3370|
|29|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-07/fanart/fanart27.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3371|
|30|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-07/fanart/fanart28.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3372|
|31|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-07/fanart/fanart29.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3373|
|32|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-08/fanart/fanart30.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3295|
|33|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-08/fanart/fanart31.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3296|
|34|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-08/fanart/fanart32.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3297|
|35|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-08/fanart/fanart33.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3298|
|36|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-08/fanart/fanart34.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3299|
|37|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-08/fanart/fanart35.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3203|
|38|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-08/fanart/fanart37.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3204|
|39|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-08/fanart/fanart38.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3205|
|40|news|uncovered|`http://www.worldofwarcraft.com/news/images/04-08/fanart/fanart39.jpg`|`.scratch/pages-resources-20261018-v33/news/wow-news2004.html`|3206|
|41|static|uncovered|`https://www.worldofwarcraft.com/insider/07/images/hr.jpg`|`.scratch/pages-resources-20261018-v33/insider/07/anatomy.html`|459|
|42|static|uncovered|`https://www.worldofwarcraft.com/insider/12/images/12-magtheridon-right.png`|`.scratch/pages-resources-20261018-v33/insider/12/magtheridon.xml.html`|640|
|43|static|uncovered|`https://www.worldofwarcraft.com/insider/12/images/12-magtheridon-title.jpg`|`.scratch/pages-resources-20261018-v33/insider/12/magtheridon.xml.html`|637|
|44|static|uncovered|`https://www.worldofwarcraft.com/bcattunement/images/wow-bc.gif`|`.scratch/pages-resources-20261018-v33/bcattunement/index.html`|38|
|45|static|uncovered|`https://www.worldofwarcraft.com/bcattunement/images/wow-classic.gif`|`.scratch/pages-resources-20261018-v33/bcattunement/index.html`|40|
|46|static|uncovered|`http://www.worldofwarcraft.com/burningcrusade/townhall/images/professions/container.jpg`|`.scratch/pages-resources-20261018-v33/burningcrusade/townhall/professions.html`|424|
|47|static|uncovered|`http://www.worldofwarcraft.com/burningcrusade/townhall/images/professions/dropback.gif`|`.scratch/pages-resources-20261018-v33/burningcrusade/townhall/professions.html`|396|
|48|static|uncovered|`http://www.worldofwarcraft.com/contests/l70etc-musicvideo/images/flashbannerbg.jpg`|`.scratch/pages-resources-20261018-v33/contests/l70etc-musicvideo/contest.css`|31|
|49|static|uncovered|`http://www.worldofwarcraft.com/contests/l70etc-musicvideo/images/l70etc-error.jpg`|`.scratch/pages-resources-20261018-v33/contests/l70etc-musicvideo/contest.css`|64|
|50|static|uncovered|`http://www.worldofwarcraft.com/insider/11/images/arena/bg.jpg`|`.scratch/pages-resources-20261018-v33/insider/11/arena.xml.html`|644|
|51|static|uncovered|`http://www.worldofwarcraft.com/pvp/battlegrounds/battlegroups/images/day.jpg`|`.scratch/pages-resources-20261018-v33/pvp/battlegrounds/battlegroups/index.html`|103|
|52|static|uncovered|`http://www.worldofwarcraft.com/pvp/tournament/images/lion-top.gif`|`.scratch/pages-resources-20261018-v33/pvp/tournament/css.css`|38|
|53|static|uncovered|`https://www.worldofwarcraft.com/bcattunement/images/townhall-bar-big.jpg`|`.scratch/pages-resources-20261018-v33/bcattunement/index.html`|36|
|54|static|uncovered|`https://www.worldofwarcraft.com/bcattunement/images/townhall-bar.gif`|`.scratch/pages-resources-20261018-v33/bcattunement/index.html`|35|
|55|static|uncovered|`https://www.worldofwarcraft.com/bcattunement/images/wow-bc-off.gif`|`.scratch/pages-resources-20261018-v33/bcattunement/index.html`|39|
|56|static|uncovered|`https://www.worldofwarcraft.com/bcattunement/images/wow-classic-off.gif`|`.scratch/pages-resources-20261018-v33/bcattunement/index.html`|41|
|57|static|uncovered|`https://www.worldofwarcraft.com/shared/wow-com/images/screenshots/ss_bg.gif`|`.scratch/pages-resources-20261018-v33/info/basics/guildbanks.html`|242|
|58|static|uncovered|`http://forums.worldofwarcraft.com/images/class-list.jpg`|`.scratch/pages-resources-20261018-v33/_origins/forums.worldofwarcraft.com/css/forums.css`|21|
|59|static|uncovered|`http://forums.worldofwarcraft.com/images/options-message-box-top.gif`|`.scratch/pages-resources-20261018-v33/_origins/forums.worldofwarcraft.com/css/forums.css`|146|
|60|static|uncovered|`http://forums.worldofwarcraft.com/images/portrait-frame-propass.gif`|`.scratch/pages-resources-20261018-v33/_origins/forums.worldofwarcraft.com/css/forums.css`|389|
|61|static|uncovered|`http://forums.worldofwarcraft.com/images/post-message-box-bot.gif`|`.scratch/pages-resources-20261018-v33/_origins/forums.worldofwarcraft.com/css/forums.css`|144|
|62|static|uncovered|`http://forums.worldofwarcraft.com/images/post-message-box-sides.gif`|`.scratch/pages-resources-20261018-v33/_origins/forums.worldofwarcraft.com/css/forums.css`|143|
|63|static|uncovered|`http://www.worldofwarcraft.com/support/images/indicator2.gif`|`.scratch/pages-resources-20261018-v33/policy/index.html`|286|
|64|static|uncovered|`http://www.worldofwarcraft.com/toplist/images/en/next-wide.gif`|`.scratch/pages-resources-20261018-v33/toplist/includes-client/css/styles-en.css`|55|
|65|static|uncovered|`http://www.worldofwarcraft.com/toplist/images/en/prev-wide.gif`|`.scratch/pages-resources-20261018-v33/toplist/includes-client/css/styles-en.css`|56|
|66|static|uncovered|`http://www.worldofwarcraft.com/community/tournaments/images/data0.gif`|`.scratch/pages-resources-20261018-v33/community/tournaments/euregionals/index.html`|413|
|67|static|uncovered|`http://www.worldofwarcraft.com/community/tournaments/images/data1.gif`|`.scratch/pages-resources-20261018-v33/community/tournaments/euregionals/index.html`|412|
|68|static|uncovered|`http://www.worldofwarcraft.com/info/encyclopedia/images/featured/featured_textbg.png`|`.scratch/pages-resources-20261018-v33/info/encyclopedia/styles/stylesheet.css`|135|
|69|static|uncovered|`http://www.worldofwarcraft.com/insider/06/images/talentinterviewbg.jpg`|`.scratch/pages-resources-20261018-v33/insider/06/interview.html`|286|
|70|static|uncovered|`http://www.worldofwarcraft.com/toplist/images/top-left.jpg`|`.scratch/pages-resources-20261018-v33/toplist/includes-client/css/styles.css`|155|
|71|static|uncovered|`http://www.worldofwarcraft.com/toplist/images/top-right.jpg`|`.scratch/pages-resources-20261018-v33/toplist/includes-client/css/styles.css`|158|
|72|static|uncovered|`http://www.worldofwarcraft.com/visa/images/credit_back_1.jpg`|`.scratch/pages-resources-20261018-v33/visa/css/creditcard.css`|36|
|73|static|uncovered|`http://www.worldofwarcraft.com/visa/images/credit_back_2.jpg`|`.scratch/pages-resources-20261018-v33/visa/css/creditcard.css`|28|
|74|static|uncovered|`http://www.worldofwarcraft.com/visa/images/credit_back_3-2.jpg`|`.scratch/pages-resources-20261018-v33/visa/css/creditcard.css`|51|
|75|static|uncovered|`http://www.worldofwarcraft.com/visa/images/credit_back_3.jpg`|`.scratch/pages-resources-20261018-v33/visa/css/creditcard.css`|43|
|76|static|uncovered|`http://www.worldofwarcraft.com/visa/images/title_1.png`|`.scratch/pages-resources-20261018-v33/visa/css/creditcard.css`|142|
|77|static|uncovered|`http://www.worldofwarcraft.com/visa/images/title_2.png`|`.scratch/pages-resources-20261018-v33/visa/css/creditcard.css`|160|
|78|static|uncovered|`http://www.worldofwarcraft.com/visa/images/title_3.png`|`.scratch/pages-resources-20261018-v33/visa/css/creditcard.css`|178|
|79|static|uncovered|`http://www.worldofwarcraft.com/visa/images/title_4.png`|`.scratch/pages-resources-20261018-v33/visa/css/creditcard.css`|196|
|80|static|uncovered|`http://www.worldofwarcraft.com/visa/images/title_5.png`|`.scratch/pages-resources-20261018-v33/visa/css/creditcard.css`|214|

## Representative row-level dedup evidence

The following ten examples show why a URL is excluded or held for review. Execution/source-map evidence is distinct from plan/queue evidence.

|state|URL|execution evidence|plan/queue evidence|
|---|---|---|---|
|complete_empty_or_404|`http://www.blizzard.com/wwi2007/photos/coree1-040-thumb.jpg`|`research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/output/batch-report.json; research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/output/source-map.json`|`research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/input-bindings.json; research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/plan.json`|
|complete_empty_or_404|`http://www.blizzard.com/wwi2007/photos/coree1-042-thumb.jpg`|`research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/output/batch-report.json; research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/output/source-map.json`|`research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/input-bindings.json; research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/plan.json`|
|complete_empty_or_404|`http://www.blizzard.com/wwi2007/photos/coree1-065-thumb.jpg`|`research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/output/batch-report.json; research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/output/source-map.json`|`research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/input-bindings.json; research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/plan.json`|
|complete_empty_or_404|`http://www.blizzard.com/wwi2007/photos/coree1-144-thumb.jpg`|`research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/output/batch-report.json; research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/output/source-map.json`|`research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/input-bindings.json; research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/plan.json`|
|complete_empty_or_404|`http://www.blizzard.com/wwi2007/photos/coree1-169-thumb.jpg`|`research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/output/batch-report.json; research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/output/source-map.json`|`research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/input-bindings.json; research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/plan.json`|
|complete_empty_or_404|`http://www.blizzard.com/wwi2007/photos/coree1-200-thumb.jpg`|`research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/output/batch-report.json; research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/output/source-map.json`|`research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/input-bindings.json; research/continuous-recovery-20261018/network/next-frontier70-v29/batch-05/plan.json`|
|complete_empty_or_404|`http://www.worldofwarcraft.com/community/tournaments/images/achieve-pvp-wreath.jpg`|`research/continuous-recovery-20261018/network/static40-v32/batch-01/output/batch-report.json; research/continuous-recovery-20261018/network/static40-v32/batch-01/output/source-map.json`|`research/continuous-recovery-20261018/network/static40-v32/static40-source-queue.json; research/continuous-recovery-20261018/network/static40-v32/batch-01/input-bindings.json`|
|complete_empty_or_404|`http://www.worldofwarcraft.com/images/Socket_Blue.png`|`research/continuous-recovery-20261018/network/static40-v32/batch-02/output/batch-report.json; research/continuous-recovery-20261018/network/static40-v32/batch-02/output/source-map.json`|`research/continuous-recovery-20261018/network/static40-v32/static40-source-queue.json; research/continuous-recovery-20261018/network/static40-v32/batch-02/input-bindings.json`|
|complete_empty_or_404|`http://www.worldofwarcraft.com/images/Socket_Meta.png`|`research/continuous-recovery-20261018/network/static40-v32/batch-02/output/batch-report.json; research/continuous-recovery-20261018/network/static40-v32/batch-02/output/source-map.json`|`research/continuous-recovery-20261018/network/static40-v32/static40-source-queue.json; research/continuous-recovery-20261018/network/static40-v32/batch-02/input-bindings.json`|
|complete_empty_or_404|`http://www.worldofwarcraft.com/images/Socket_Yellow.png`|`research/continuous-recovery-20261018/network/static40-v32/batch-02/output/batch-report.json; research/continuous-recovery-20261018/network/static40-v32/batch-02/output/source-map.json`|`research/continuous-recovery-20261018/network/static40-v32/static40-source-queue.json; research/continuous-recovery-20261018/network/static40-v32/batch-02/input-bindings.json`|
Plan-only and queue-only references remain evidence of prior planning, not requests. Exact execution/source-map evidence is excluded from the new pool even when no payload was accepted. Explicit scheme/default-port variants are retained in the machine ledger for review and are never promoted to strict same-URL success.
## August 2007 remainder
The page `news/rss-08-2007.xml` has six explicit full-image originals (`wow-bc.jpg`, `tcg01–03.jpg`, `ss01–02.jpg`). They are already in the accepted navigation70 overlay. The same page's fan-art blocks expose local thumbnails and external Blizzard landing pages; those are not new exact image URLs. No `ssN` or fan-art filename is inferred. The source page SHA and line hits are in `resource-frontier-candidates.json` under `august_2007`.

## Prior exclusion closure

The exact rows and reasons are recorded under `legacy_exclusion_closure`. The three encyclopedia article images are retained as complete bounded error/no-eligible evidence from the 2026-10-11 review, the lordaeron map is a complete-empty bounded interval, sponsors remain deferred, and the three literal-space small-pets paths are held for a separately reviewed URI serialization. None enters the strict candidate waves.
## Proposed bounded follow-up (draft only)
Use the generated waves only after root review: four exact targets per wave, exact CDX first, at most eight requests / 180 seconds / 16 MiB total / 8 MiB entity, TLS validation, direct then process proxy, 5.25-second dispatch spacing, no redirects or automatic pagination. Replay requires a separately reviewed eligible CDX row. Stop on 429/503, five consecutive transfer failures, disk below 11005853696 bytes, or the 13:15 UTC cutoff.
## Inputs
- `research/continuous-recovery-20261018/publication/v33-export-expectations-r2.json` SHA-256 `301fde4f61205c815cb6845751fdf6d25baf170ebe1402d8c88a0031c3872251`
- `.scratch/pages-resources-20261018-v33/export-provenance.json` SHA-256 `99ac5b0a2bc7d257b2fe3c4b18a0bb74023c3c57051be3a4f4efe20258f4c8f5`
- `research/continuous-recovery-20261018/local-audit/static-frontier-v32/static-frontier-v32-candidates.json` SHA-256 `72c00aa28e7c19c86de7f877983d049662f543be48960d2879a0f566bf15657f`
- `research/continuous-recovery-20261018/integration/v33/v33-primary-source-map.json` SHA-256 `285b6f56b932a74ba6da0c30b64256b8cff05f165ec1636b682a48000ea27972`
- `research/continuous-recovery-20261018/integration/v33/v33-supplement-source-map.json` SHA-256 `6ab2cc11483a62588c093f6ec927d99ad9e550a4fbb7a52471e273bbcaabb6bc`
- `.scratch/offline-navigation-20261015-v15/site/news/rss-08-2007.xml` SHA-256 `622db0022d5e81a9fff9e14bac4a3394bc5f8fa5c61e02a34b4efa66c3ca3fc1`
- `research/continuous-recovery-20261018/publication/next-frontier-selected70.json` SHA-256 `654135870971139ac04427119bcf01d4d9981af60d182f068b7da6a99187551a`
- `docs/gap-review-20261011.md` SHA-256 `07d9bbed16e74cff0ce425a38a2d30208c3c7504423dc3a2f75ffd8297ef800c`
- `research/gap-review-20261011/errors/review-report.zh.md` SHA-256 `e6f1c917069a7852409e5d3eec2a1f8dec5a01e242614b4f33500990c208070f`
- `research/gap-review-20261011/errors/cdx-summary-variants-core.json` SHA-256 `f4a624b0369e09073941e505ada89ee1e90760f8339367f6884f6652da2d361a`

The latest real network tail is gallery-late-gap01 tail 0 (report SHA `5419b3c59df71946d9ff0670ccb4ebec2273eb7a6096d590fd621fb33c5b5f4b`); this audit did not modify status or reuse an older NET53 gate.
