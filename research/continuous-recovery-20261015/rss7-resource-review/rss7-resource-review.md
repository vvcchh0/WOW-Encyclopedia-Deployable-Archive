# RSS7 resource review

Generated `2026-10-15T11:14:45.320481Z`. This is a local static review of the seven selected v10 RSS-path HTML pages; `network_requests=0`. Navigation anchors are recorded separately and are not promoted to the image/resource queue.

## Verified scope

The seven selected raw payloads and seven exported HTML pages each matched their selected/provenance SHA-256 and byte length. The review found **1373** exact request-bearing resource references and **193** unique original URLs. **95** entities are byte-readable locally; **92** have exact scheme/host/path/query identity, while **3** readable entities are HTTP-request/HTTPS-source scheme mismatches and are not counted as exact recovery. A further **98** are not mapped or otherwise unresolved locally. There are **132** unique body-image candidates after separating small-cap/layout assets and third-party promotion.

Navigation evidence contains 1183 anchor references across 320 unique URLs. Static markup evidence contains 7 forms, 284 inline event attributes, and six shared script-src dependencies per page; none was executed.

## Input hashes

| input | bytes | SHA-256 |
|---|---:|---|
| `research/continuous-recovery-20261015/selected-v10-final-additions.json` | 19720 | `c73b02d2f9353402eb4b568640e1359031e25756604cbbc5f21552f0acd52a55` |
| `.scratch/offline-navigation-20261015-v10/build-manifest.json` | 75463144 | `bc664a728da4bb6c5a49b2c2d46bc2837e2ae40e8a09f6e59c6dc755caa83d86` |
| `.scratch/pages-resources-20261015-v10/export-provenance.json` | 7855373 | `7c585c7cf343411c91051650d26a9a78afb98101009f2f14732c574f108217f6` |
| `research/v10-integration/source/v10-additions-source-map.json` | 107225 | `369a458b2942da1aadfbf1a5f072ba3df971d43bc34a8e7c570f788214595a74` |

## Page verification

| target | raw bytes/SHA prefix | exported bytes/SHA prefix | refs | nav refs |
|---|---:|---:|---:|---:|
| `/news/rss-04-2008.xml` | 67073 / `b628d495c914…` | 88068 / `54fdfae13fe7…` | 130 | 136 |
| `/news/rss-03-2008.xml` | 122880 / `9bab7f97ee07…` | 160253 / `a46e7eb09bab…` | 187 | 268 |
| `/news/rss-02-2008.xml` | 155377 / `dea7ecdf447b…` | 201341 / `ce131535da46…` | 231 | 363 |
| `/news/rss-01-2008.xml` | 106709 / `8edd3c3499ff…` | 141771 / `ddf104d00941…` | 176 | 235 |
| `/news/rss-05-2007.xml` | 135008 / `089e2d02cbd0…` | 173990 / `f123d65f2003…` | 206 | 291 |
| `/news/rss-01-2007.xml` | 158160 / `fb9d0f61c6a0…` | 200826 / `15e0c2901942…` | 214 | 332 |
| `/news/rss-07-2006.xml` | 135703 / `58f8763be3a0…` | 176336 / `e98d95e0aa2f…` | 229 | 292 |

## Source identity correction

The manifest origin index is host/path based, so this pass additionally compared each requested scheme/host/path/query with the row's `source_base_url`. The three readable-but-non-exact rows are listed explicitly below; their bytes remain evidence, but they are not exact HTTP-source recovery.

- `http://www.worldofwarcraft.com/community/images/comics/comics195.jpg` → requested identity `False`; source `https://www.worldofwarcraft.com/community/images/comics/comics195.jpg`; fields `scheme`; local `.scratch/offline-navigation-20261015-v10/site/community/images/comics/comics195.jpg`, 8949 bytes, `bc7e1683cc310afa5971e5d3ffdf68c1f7f234ac6702692130862b7207a8fac7`.
- `http://www.worldofwarcraft.com/news/images/06-02/love.jpg` → requested identity `False`; source `https://www.worldofwarcraft.com/news/images/06-02/love.jpg`; fields `scheme`; local `.scratch/offline-navigation-20261015-v10/site/news/images/06-02/love.jpg`, 12498 bytes, `522a1cd13c82a7e493119c8402905d2395a6ff1b673a1d80d5311be57edfbcdf`.
- `http://www.worldofwarcraft.com/community/images/comics/comics29.jpg` → requested identity `False`; source `https://www.worldofwarcraft.com/community/images/comics/comics29.jpg`; fields `scheme`; local `.scratch/offline-navigation-20261015-v10/site/community/images/comics/comics29.jpg`, 12538 bytes, `2c13d93cc80028f73020a38e799f505ab18051a4fef0f80db5bb842c614830c4`.

## Prior-request evidence boundary

The candidate `prior_request` field checks only the explicitly bounded acceptance/request-ledger files recorded in the JSON. `not_checked` means no exact full URL hit was found there; it does not claim that the URL was never requested.

- `research/continuous-recovery-20261015/assets5-acceptance.json` — `23f4ca8b4ffd54d67f67075600742f1fd5b968406f6eaca303d57c267bbfd397`
- `research/continuous-recovery-20261015/mixed9-acceptance.json` — `989a559c56733d34c39b806e1e1d42be6b50e337cc4dd9221423ec31da89866b`
- `research/continuous-recovery-20261015/wrath8-acceptance.json` — `ee552b25a056eed66a7b602f2d5e5254db37d411c75f4726f69adde876ef70d7`
- `research/continuous-recovery-20261015/rss6-acceptance.json` — `eec2fe529f56f547c38b49740f302c85ebcbe49edc701f3a1e28ba65f9be77c2`
- `research/continuous-recovery-20261015/rss10-acceptance.json` — `f87d84d7c801f90050a6e1a8cbc308104b4e6c7ad133d70db6172c55896e04c0`
- `research/continuous-recovery-20261015/network-batch1-acceptance.json` — `acdc9e1574f4c1cccacbc88b8e16e42a78a23cc6067b1afa148f7386fff71552`
- `research/continuous-recovery-20261015/resource-dedup-acceptance.json` — `63cddc7ec45cc586d837625ad13edade655f2a8d4db72bffb86ae9e8302ddadd`


## Local salvage evidence samples

These are locally readable manifest-mapped entities with real byte length/SHA/MIME evidence; the full set is in `rss7-resource-review.json`.

- `http://www.worldofwarcraft.com/new-hp/images/burningcrusade/statue-left.jpg` → `.scratch/offline-navigation-20261015-v10/site/new-hp/images/burningcrusade/statue-left.jpg`; 11124 bytes, `70cb15bbcff6df5cd7ca1dec2c7316d616a1d05d5d0a93c7641d0fe4084da47b`, manifest MIME `image/jpeg`, byte signature `image/jpeg`; 7 reference(s).
- `http://www.worldofwarcraft.com/new-hp/images/ectppsvivendi.gif` → `.scratch/offline-navigation-20261015-v10/site/new-hp/images/ectppsvivendi.gif`; 1249 bytes, `b706885a878e88f730684f15cc998e5b95578fd1423d9c278acfead247e633cf`, manifest MIME `image/gif`, byte signature `image/gif`; 7 reference(s).
- `http://www.worldofwarcraft.com/community/images/comics/comics115.jpg` → `.scratch/offline-navigation-20261015-v10/site/community/images/comics/comics115.jpg`; 10289 bytes, `a01ff9bfc49e149a9ef0aeea30aa831a65db0a832d308c58c27c0a1e84e7ce59`, manifest MIME `image/jpeg`, byte signature `image/jpeg`; 1 reference(s).
- `http://www.worldofwarcraft.com/community/images/comics/comics116.jpg` → `.scratch/offline-navigation-20261015-v10/site/community/images/comics/comics116.jpg`; 8277 bytes, `f0af32377251e856122acf7e7eff97d0e9bd0500c8a21a836388f119b417f083`, manifest MIME `image/jpeg`, byte signature `image/jpeg`; 1 reference(s).
- `http://www.worldofwarcraft.com/community/images/comics/comics117.jpg` → `.scratch/offline-navigation-20261015-v10/site/community/images/comics/comics117.jpg`; 10980 bytes, `ff61bd24079cd0606c580fc9655b8e3aafad00658447baa1583bf99315df8501`, manifest MIME `image/jpeg`, byte signature `image/jpeg`; 1 reference(s).
- `http://www.worldofwarcraft.com/community/images/comics/comics118.jpg` → `.scratch/offline-navigation-20261015-v10/site/community/images/comics/comics118.jpg`; 9635 bytes, `593f9c2fad57bef32422c4a19d6bd9c366d830505b24b9ad28f629e33a16b980`, manifest MIME `image/jpeg`, byte signature `image/jpeg`; 1 reference(s).
- `http://www.worldofwarcraft.com/community/images/comics/comics119.jpg` → `.scratch/offline-navigation-20261015-v10/site/community/images/comics/comics119.jpg`; 8250 bytes, `42e924b433b6868fbb7d8cb6fba0c883d5df6dc98ad6b0ac7f49de5f5a0eedbc`, manifest MIME `image/jpeg`, byte signature `image/jpeg`; 1 reference(s).
- `http://www.worldofwarcraft.com/community/images/comics/comics120.jpg` → `.scratch/offline-navigation-20261015-v10/site/community/images/comics/comics120.jpg`; 11095 bytes, `15b961e1f45fc0b0af13ee7685c851082b949d69b7f0a301fa831ddba4bb37f3`, manifest MIME `image/jpeg`, byte signature `image/jpeg`; 1 reference(s).
- `http://www.worldofwarcraft.com/community/images/comics/comics121.jpg` → `.scratch/offline-navigation-20261015-v10/site/community/images/comics/comics121.jpg`; 9638 bytes, `3a861a404b43c9496549033bccb5c31349221cf29ae5db94bee08b41b07b9671`, manifest MIME `image/jpeg`, byte signature `image/jpeg`; 1 reference(s).
- `http://www.worldofwarcraft.com/community/images/comics/comics122.jpg` → `.scratch/offline-navigation-20261015-v10/site/community/images/comics/comics122.jpg`; 10068 bytes, `5c8c80732af0a7ddee3c64e1de9e7fc1fadc3b2331d8c234bb965c62673fa6b7`, manifest MIME `image/jpeg`, byte signature `image/jpeg`; 1 reference(s).
- `http://www.worldofwarcraft.com/community/images/comics/comics173.jpg` → `.scratch/offline-navigation-20261015-v10/site/community/images/comics/comics173.jpg`; 11768 bytes, `babc17c5d09e55ed0c2cb646ead884bfde11b645944bc8aca8f33dd65b536e0d`, manifest MIME `image/jpeg`, byte signature `image/jpeg`; 1 reference(s).
- `http://www.worldofwarcraft.com/community/images/comics/comics174.jpg` → `.scratch/offline-navigation-20261015-v10/site/community/images/comics/comics174.jpg`; 7153 bytes, `a4610a287b46c4e3a2ad20fefc704e6980464b8fa797dfa887bd6c03d7b56e12`, manifest MIME `image/jpeg`, byte signature `image/jpeg`; 1 reference(s).

## Priority exact-URL candidates

The queue is capped at 16 unique URLs. Each entry retains source line/context evidence in both the JSON review and queue. `not_mapped_or_unknown` means no local v10 origin-index entity was found; it is not a claim that an external capture exists.

1. `http://www.worldofwarcraft.com/news/images/08-01/01-10-08-01.jpg` — **P1**, not_mapped_or_unknown, 2 reference(s), pages: `/news/rss-02-2008.xml, /news/rss-01-2008.xml`.
   Purpose: body_illustration_candidate; evidence: `research/continuous-recovery-20261015/network-rss6/raw/08-http_www.worldofwarcraft.com_news_rss-02-2008.xml-replay-proxy.body` line 979: <a href="http://us.blizzard.com/blizzcast/archive/episode2.xml"><img align="right" border="0" src="/news/images/08-01/01-10-08-01.jpg"></a>
2. `http://www.worldofwarcraft.com/news/images/08-02/arenatourney2.gif` — **P1**, not_mapped_or_unknown, 2 reference(s), pages: `/news/rss-02-2008.xml`.
   Purpose: body_illustration_candidate; evidence: `research/continuous-recovery-20261015/network-rss6/raw/08-http_www.worldofwarcraft.com_news_rss-02-2008.xml-replay-proxy.body` line 720: <a href="http://www.worldofwarcraft.com/pvp/tournament/index.xml"><img src="/news/images/08-02/arenatourney2.gif" style="float:right; border:0;"></a>
3. `http://www.worldofwarcraft.com/news/images/06-07/7-13-06-1.jpg` — **P1**, not_mapped_or_unknown, 1 reference(s), pages: `/news/rss-07-2006.xml`.
   Purpose: body_illustration_candidate; evidence: `research/continuous-recovery-20261015/network-rss10/raw/17-http_www.worldofwarcraft.com_news_rss-07-2006.xml-replay-proxy.body` line 2459: <a href="http://www.blizzard.com/inblizz/fanart/"><img border="0" height="100" src="/news/images/06-07/7-13-06-1.jpg" width="130"></a>
4. `http://www.worldofwarcraft.com/news/images/06-07/7-13-06-2.jpg` — **P1**, not_mapped_or_unknown, 1 reference(s), pages: `/news/rss-07-2006.xml`.
   Purpose: body_illustration_candidate; evidence: `research/continuous-recovery-20261015/network-rss10/raw/17-http_www.worldofwarcraft.com_news_rss-07-2006.xml-replay-proxy.body` line 2460: <a href="http://www.blizzard.com/inblizz/fanart/"><img border="0" height="100" src="/news/images/06-07/7-13-06-2.jpg" width="130"></a>
5. `http://www.worldofwarcraft.com/news/images/06-07/7-13-06-3.jpg` — **P1**, not_mapped_or_unknown, 1 reference(s), pages: `/news/rss-07-2006.xml`.
   Purpose: body_illustration_candidate; evidence: `research/continuous-recovery-20261015/network-rss10/raw/17-http_www.worldofwarcraft.com_news_rss-07-2006.xml-replay-proxy.body` line 2461: <a href="http://www.blizzard.com/inblizz/fanart/"><img border="0" height="100" src="/news/images/06-07/7-13-06-3.jpg" width="130"></a>
6. `http://www.worldofwarcraft.com/news/images/06-07/7-27-06-1.jpg` — **P1**, not_mapped_or_unknown, 1 reference(s), pages: `/news/rss-07-2006.xml`.
   Purpose: body_illustration_candidate; evidence: `research/continuous-recovery-20261015/network-rss10/raw/17-http_www.worldofwarcraft.com_news_rss-07-2006.xml-replay-proxy.body` line 1196: <a href="http://www.blizzard.com/inblizz/fanart/"><img border="0" height="100" src="/news/images/06-07/7-27-06-1.jpg" width="130"></a>
7. `http://www.worldofwarcraft.com/news/images/06-07/7-27-06-2.jpg` — **P1**, not_mapped_or_unknown, 1 reference(s), pages: `/news/rss-07-2006.xml`.
   Purpose: body_illustration_candidate; evidence: `research/continuous-recovery-20261015/network-rss10/raw/17-http_www.worldofwarcraft.com_news_rss-07-2006.xml-replay-proxy.body` line 1197: <a href="http://www.blizzard.com/inblizz/fanart/"><img border="0" height="100" src="/news/images/06-07/7-27-06-2.jpg" width="130"></a>
8. `http://www.worldofwarcraft.com/news/images/06-07/7-27-06-3.jpg` — **P1**, not_mapped_or_unknown, 1 reference(s), pages: `/news/rss-07-2006.xml`.
   Purpose: body_illustration_candidate; evidence: `research/continuous-recovery-20261015/network-rss10/raw/17-http_www.worldofwarcraft.com_news_rss-07-2006.xml-replay-proxy.body` line 1198: <a href="http://www.blizzard.com/inblizz/fanart/"><img border="0" height="100" src="/news/images/06-07/7-27-06-3.jpg" width="130"></a>
9. `http://www.worldofwarcraft.com/news/images/06-07/thumb-rogue.jpg` — **P1**, not_mapped_or_unknown, 1 reference(s), pages: `/news/rss-07-2006.xml`.
   Purpose: body_illustration_candidate; evidence: `research/continuous-recovery-20261015/network-rss10/raw/17-http_www.worldofwarcraft.com_news_rss-07-2006.xml-replay-proxy.body` line 2834: <a href="http://www.worldofwarcraft.com/info/classes/rogues2/talents.html"><img align="right" border="0" height="66" src="/news/images/06-07/thumb-rogue.jpg" style="margin-left:10px;" width="66"></a><img align="left" height="32" src="/new-hp/images/smallcaps/n.gif" style="padding-right: 3px;" width…
10. `http://www.worldofwarcraft.com/news/images/07-01/1-18-07-1.jpg` — **P1**, not_mapped_or_unknown, 1 reference(s), pages: `/news/rss-01-2007.xml`.
   Purpose: body_illustration_candidate; evidence: `research/continuous-recovery-20261015/network-rss10/raw/09-http_www.worldofwarcraft.com_news_rss-01-2007.xml-replay-proxy.body` line 1506: <a href="http://www.blizzard.com/inblizz/fanart/page39.shtml"><img border="0" height="100" src="/news/images/07-01/1-18-07-1.jpg" width="130"></a>
11. `http://www.worldofwarcraft.com/news/images/07-01/1-18-07-2.jpg` — **P1**, not_mapped_or_unknown, 1 reference(s), pages: `/news/rss-01-2007.xml`.
   Purpose: body_illustration_candidate; evidence: `research/continuous-recovery-20261015/network-rss10/raw/09-http_www.worldofwarcraft.com_news_rss-01-2007.xml-replay-proxy.body` line 1507: <a href="http://www.blizzard.com/inblizz/fanart/page39.shtml"><img border="0" height="100" src="/news/images/07-01/1-18-07-2.jpg" width="130"></a>
12. `http://www.worldofwarcraft.com/news/images/07-01/1-18-07-3.jpg` — **P1**, not_mapped_or_unknown, 1 reference(s), pages: `/news/rss-01-2007.xml`.
   Purpose: body_illustration_candidate; evidence: `research/continuous-recovery-20261015/network-rss10/raw/09-http_www.worldofwarcraft.com_news_rss-01-2007.xml-replay-proxy.body` line 1508: <a href="http://www.blizzard.com/inblizz/fanart/page39.shtml"><img border="0" height="100" src="/news/images/07-01/1-18-07-3.jpg" width="130"></a>
13. `http://www.worldofwarcraft.com/news/images/07-01/1-18-07-4.gif` — **P1**, not_mapped_or_unknown, 1 reference(s), pages: `/news/rss-01-2007.xml`.
   Purpose: body_illustration_candidate; evidence: `research/continuous-recovery-20261015/network-rss10/raw/09-http_www.worldofwarcraft.com_news_rss-01-2007.xml-replay-proxy.body` line 1241: <a href="http://www.zboard.com/experience/worldofwarcraft/"><img border="0" height="113" src="/news/images/07-01/1-18-07-4.gif" width="412"></a>
14. `http://www.worldofwarcraft.com/news/images/07-01/1-25-07-1.jpg` — **P1**, not_mapped_or_unknown, 1 reference(s), pages: `/news/rss-01-2007.xml`.
   Purpose: body_illustration_candidate; evidence: `research/continuous-recovery-20261015/network-rss10/raw/09-http_www.worldofwarcraft.com_news_rss-01-2007.xml-replay-proxy.body` line 944: <a href="http://www.blizzard.com/inblizz/fanart/page40.shtml"><img border="0" height="100" src="/news/images/07-01/1-25-07-1.jpg" width="130"></a>
15. `http://www.worldofwarcraft.com/news/images/07-01/1-25-07-2.jpg` — **P1**, not_mapped_or_unknown, 1 reference(s), pages: `/news/rss-01-2007.xml`.
   Purpose: body_illustration_candidate; evidence: `research/continuous-recovery-20261015/network-rss10/raw/09-http_www.worldofwarcraft.com_news_rss-01-2007.xml-replay-proxy.body` line 945: <a href="http://www.blizzard.com/inblizz/fanart/page40.shtml"><img border="0" height="100" src="/news/images/07-01/1-25-07-2.jpg" width="130"></a>
16. `http://www.worldofwarcraft.com/news/images/07-01/1-25-07-3.jpg` — **P1**, not_mapped_or_unknown, 1 reference(s), pages: `/news/rss-01-2007.xml`.
   Purpose: body_illustration_candidate; evidence: `research/continuous-recovery-20261015/network-rss10/raw/09-http_www.worldofwarcraft.com_news_rss-01-2007.xml-replay-proxy.body` line 946: <a href="http://www.blizzard.com/inblizz/fanart/page40.shtml"><img border="0" height="100" src="/news/images/07-01/1-25-07-3.jpg" width="130"></a>

## Boundaries

- `a[href]` is navigation evidence, not an image or asset candidate.
- `/new-hp/images/smallcaps/*.gif` is classified as repeated 32px drop-cap/layout markup from its path, dimensions, and adjacent text; it is not ranked as正文素材.
- `news-sc2.jpg` is kept as a linked third-party promotion and excluded from the正文 queue.
- Static forms, inline handlers, and scripts show only source presence. No interaction, MIME fetch, payload decode, or network request was performed by this review.
- No basename substitution or cross-origin alias was made; exact origin and URL are retained.
