# Final v9 sidebar static audit

- Generated UTC: 2026-10-15T09:38:24.937903+00:00; network requests: 0.
- Scope: all 1,241 menu observations: 588 original entries, 579 Legacy menu observations reclassified with parser_unclassified_legacy, and 74 true scope exclusions.
- Route/page/resource evidence is local. Interaction fields remain static_indication_only; browser results and runtime gaps remain separate.

## Inputs and conservation

- Menu conservation: total 1241/1241; original 588/588; legacy 579/579; true excluded 74/74.
- Frozen offline/build-manifest.json: 397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459; expected 397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459; unchanged=True.
- v9 route map: 8470 routes, 189 aliases, 99 keys in both maps.
- All six declared v9 task inputs were re-hashed and matched; the full list is in audit.json input_contract_verification.

## Current v9 effective page state

- Resolved current route/alias/recovered: 1081.
- External or dynamic: 54; business or sensitive: 6; missing export route: 26.
- Missing distinct routes: 23.
- Distinct resolved v9 files read and SHA-256 checked: 460; mismatches: 0.
- Per-menu page states: {'business_or_sensitive': 6, 'external_or_dynamic': 54, 'missing_export_route': 26, 'resolved': 926, 'resolved_recovered': 3, 'resolved_via_alias': 152}.

## v8 to v9 route delta

Page-state changes from the accepted v8 audit: 14 observations across 12 distinct routes; prior resolved-route regressions: 0.
- /news/wow-news2005.html — 2005 Archive from mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu1_var.js:170: missing_export_route -> resolved; .scratch/pages-resources-20261015-v9/news/wow-news2005.html; 206583 bytes; SHA f092c2eabb57d7efec15cd9b85b1ff38237503344047d8d3f2b003706e5eac29; map route -> /WOW-Encyclopedia-Deployable-Archive/news/wow-news2005.html.
- /news/wow-news-11-2005.html — November, 2005 from mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu1_var.js:172: missing_export_route -> resolved; .scratch/pages-resources-20261015-v9/news/wow-news-11-2005.html; 75495 bytes; SHA ee4df7cae666fac16cf59cbb679285d3a8a0bff5d71614e188904c22cf8d388d; map route -> /WOW-Encyclopedia-Deployable-Archive/news/wow-news-11-2005.html.
- /news/wow-news-10-2005.html — October, 2005 from mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu1_var.js:173: missing_export_route -> resolved; .scratch/pages-resources-20261015-v9/news/wow-news-10-2005.html; 107031 bytes; SHA 3f80a039b8cc24cef6c6587eb6118702deca6c72ce051a90cce28fdb1b3df6be; map route -> /WOW-Encyclopedia-Deployable-Archive/news/wow-news-10-2005.html.
- /news/wow-news-09-2005.html — September, 2005 from mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu1_var.js:174: missing_export_route -> resolved; .scratch/pages-resources-20261015-v9/news/wow-news-09-2005.html; 95832 bytes; SHA 793eed5e68bebf610369fe38493a2b9caa351cd55d048edc02eacf29cca5c50f; map route -> /WOW-Encyclopedia-Deployable-Archive/news/wow-news-09-2005.html.
- /news/wow-news-08-2005.html — August, 2005 from mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu1_var.js:175: missing_export_route -> resolved; .scratch/pages-resources-20261015-v9/news/wow-news-08-2005.html; 91312 bytes; SHA b95aacc181f7eb12eee9815c48f33791bb9bfd1727c414a3c476c64e2538546b; map route -> /WOW-Encyclopedia-Deployable-Archive/news/wow-news-08-2005.html.
- /news/wow-news-07-2005.html — July, 2005 from mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu1_var.js:176: missing_export_route -> resolved; .scratch/pages-resources-20261015-v9/news/wow-news-07-2005.html; 81242 bytes; SHA 3bc13dcb615afa69b4cfde68e44066914fb87a7698403ac60675d4563b28fc08; map route -> /WOW-Encyclopedia-Deployable-Archive/news/wow-news-07-2005.html.
- /news/wow-news-06-2005.html — June, 2005 from mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu1_var.js:177: missing_export_route -> resolved; .scratch/pages-resources-20261015-v9/news/wow-news-06-2005.html; 85988 bytes; SHA 7bfaf17dd73b79497b8d457236dbddff2f6bda70b1d0cd3d4df55bd3280fa7c4; map route -> /WOW-Encyclopedia-Deployable-Archive/news/wow-news-06-2005.html.
- /news/wow-news2005.html — Jan - May, 2005 from mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu1_var.js:178: missing_export_route -> resolved; .scratch/pages-resources-20261015-v9/news/wow-news2005.html; 206583 bytes; SHA f092c2eabb57d7efec15cd9b85b1ff38237503344047d8d3f2b003706e5eac29; map route -> /WOW-Encyclopedia-Deployable-Archive/news/wow-news2005.html.
- /news/wow-news2004.html — 2004 Archive from mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu1_var.js:180: missing_export_route -> resolved; .scratch/pages-resources-20261015-v9/news/wow-news2004.html; 455210 bytes; SHA 03d9bcc9ac35d0daa28cf01e3abea7b2c60e03e857f0a5d86897466ee670fe21; map route -> /WOW-Encyclopedia-Deployable-Archive/news/wow-news2004.html.
- /pvp/battlegrounds/battlegroups.html — Cross-Realm BGs from mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu3_var.js:545: missing_export_route -> resolved; .scratch/pages-resources-20261015-v9/pvp/battlegrounds/battlegroups/index.html; 31373 bytes; SHA 671d5df2bbd04f579caec04e27659122cdc5504dbbc7fd5532c062f670dfbf11; map route_and_alias -> /WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/battlegroups/index.html.
- /burningcrusade/townhall/professions.html — Professions from mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu3_var.js:637: missing_export_route -> resolved; .scratch/pages-resources-20261015-v9/burningcrusade/townhall/professions.html; 66334 bytes; SHA b30028c9bd8a017df7de170a928a0290a8110c8f63d3b7248817c3cf2bfc97df; map route -> /WOW-Encyclopedia-Deployable-Archive/burningcrusade/townhall/professions.html.
- /wrath/artwork.xml — Artwork from mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu3_var.js:662: missing_export_route -> resolved; .scratch/pages-resources-20261015-v9/wrath/artwork.xml.html; 15633 bytes; SHA a7ddeddbb0d312e6facf1c5e530b8802447f93a9037484369040e087448d61e4; map route -> /WOW-Encyclopedia-Deployable-Archive/wrath/artwork.xml.html.
- /ptr/ — Public Test Realm from mirror/20080512/www.worldofwarcraft.com/new-hp/js/menu3_var.js:668: missing_export_route -> resolved_via_alias; .scratch/pages-resources-20261015-v9/ptr/index.html; 4407 bytes; SHA 6bb2b99e8a79e1771a4a834746d621ac981fbdb83a9720e2d2b82305a544046b; map alias -> /WOW-Encyclopedia-Deployable-Archive/ptr/index.html.
- /ptr/ — Public Test Realm from research/site-recovery-2008/.menu.xml:20: missing_export_route -> resolved_via_alias; .scratch/pages-resources-20261015-v9/ptr/index.html; 4407 bytes; SHA 6bb2b99e8a79e1771a4a834746d621ac981fbdb83a9720e2d2b82305a544046b; map alias -> /WOW-Encyclopedia-Deployable-Archive/ptr/index.html.

## Remaining static boundaries

- The 23 missing routes are legacy News RSS targets listed in delta-summary.json; no monthly-similarity alias is inferred.
- /wrath/artwork.xml resolves, but the observed card href /wrath/art.xml?s=12 remains a viewer gap. The browser receipt separately records five provenance-backed common image pairs, eight missing pairs, and the shared ssborder1.png placeholder; missing-image fallback is not recovery.
- Account, Forums, Support, and WoW Main records remain static/excluded exhibits and are accounted for in the 74-record exclusion count.
- No production route map, frozen manifest, ledger, browser receipt, or old audit was edited. repair-proposals.json in this directory is advisory only.

## Method and evidence

- audit_local_v9.py reapplies the accepted local classifier to the same 1,241 source identities with v9 route-map.json and export-provenance.json. It performs no network acquisition.
- Every resolved menu record stores source menu path/line, v9 resolved path, byte length, page SHA-256, provenance binding, route target and alias target where present, plus evidence strings.
- Independent precheck research/continuous-recovery-20261015/v9-route-independent-precheck.json is a cross-check, not a substitute for per-record evidence; SHA-256 881c8f720c15b25946cbe9195de64cceb02557d80bd2713dc6a461c3b06627fa.

## Ledger grouping cross-check
- Read-only source: research/continuous-recovery-20261015/ledger.current.json; SHA-256 178da25a57fb9e6211b40228b6d6cc1545d40606791d9fb39e23dcb49f758412; generated 2026-10-15T07:25:11.457433+00:00; current preview .scratch/pages-resources-20261015-v8.
- Its group/scope summary was retained as grouping context. v9 page/resource statuses were recomputed from the final v9 route map and provenance; ledger.current was not edited.
