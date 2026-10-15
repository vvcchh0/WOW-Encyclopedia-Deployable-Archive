# V14 focused browser acceptance plan

Status: prepared; waiting for root final V14 source acceptance and explicit loopback preview READY. The runner has passed syntax-only validation and has not contacted a server.

The final selected map is fixed at nine accepted RSS-path expanded HTML entries and 350 total posted-date articles. The runner derives each route title, expected count, month, and year from the selected map and checks that article_posted_date_count equals the sum of article_posted_dates frequencies. It never uses the number of unique date keys as the article count.

The final NET020+NET021 map has nine entries:

- /news/rss-11-2007.xml, 39 articles
- /news/rss-10-2007.xml, 41 articles
- /news/rss-09-2007.xml, 29 articles
- /news/rss-03-2007.xml, 27 articles
- /news/rss-02-2007.xml, 31 articles
- /news/rss-12-2006.xml, 41 articles
- /news/rss-11-2006.xml, 54 articles
- /news/rss-08-2006.xml, 35 articles
- /news/rss-10-2006.xml, 53 articles

The final map path is `research/continuous-recovery-20261015/selected-final-rss14-source-map.json` with SHA-256 `7019d82bca12be63f5ad832ae72729c1ac8b8fa3c4c4b6936f2d452f780d166b`. Each selected page is checked for HTTP 200, visible body, title identity, all posted-date values, all news-entry-date values, matching arrays, and month/year correspondence to its RSS route. The May partial-capture special case is not hardcoded for this batch.

For every selected page the runner checks the real newsarchive.css link and a local GET response. Expected CSS is 109 bytes with SHA-256 69915a4eea19ec455a60b89c64ed661fc55d48bc3a724bdffcc91bd2d617aa7b.

One genuinely default-collapsed entry is selected dynamically from the first selected page. The runner clicks its visible h1 a once with ordinary Playwright locator.click(), records the before/after ancestor class, body/news-item/description display, visibility, rectangles, title href, nearest hoverContainer onclick, and saves exactly one expanded-entry PNG. It does not run the old V13 four-action matrix; the two explicitly retained July anchor regressions below are separate focused checks.

The final focused run also repeats two already specified July 2007 regressions: `news7-30-07-513` on `/news/rss-07-2007.xml` gets one fresh context for `anchor-center` and one fresh context for `anchor-enter`; each context performs two activations and must observe collapsed -> expanded -> collapsed state. The checks record the selected `.news-item` display/visibility and ancestor class, original toggle href, parent `onclick`, and 14x11 anchor box. The title and `li` center cases remain out of this V14 run.

The request gate allows only GET and HEAD requests to the supplied loopback origin and deployment prefix. External origins, outside-prefix paths, and every other method are aborted and recorded. The runner does not start a server, use force clicks, call page functions, modify DOM styles or handlers, inject entries, or perform network requests outside the loopback preview. Unknown 404s, request failures, page errors, console errors, and blocked requests are separate failures.

Prepared inputs:

- Final selected map: research/continuous-recovery-20261015/selected-final-rss14-source-map.json, SHA-256 7019d82bca12be63f5ad832ae72729c1ac8b8fa3c4c4b6936f2d452f780d166b.
- Independent acceptance inputs: research/continuous-recovery-20261015/rss20-acceptance.json, SHA-256 decc5d48b5a55ffff2026299da1b8822ecd7f87d0ec4fa03e771286ebc346de4; and research/continuous-recovery-20261015/rss21-acceptance.json, SHA-256 535f854d7e13573a8a36b6cc8548ef0f20a08314a62beb4ef52ceecec07130cc. Both have `accepted: true`.
- The final source receipt and source plan are optional runner arguments and must be supplied by root after NET021 acceptance for final source binding.
- Final manifest, provenance, and route map are runtime arguments. Their actual SHA values are recorded and may be checked with expected hash arguments.
- tools/export_github_pages.py is bound by path and actual SHA at runtime.

Syntax-only command already run:

    & C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe --check research/v14-integration/browser/v14_acceptance.js

Runtime command template, intentionally not run until root supplies final source paths, expected hashes, and READY preview:

    & C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe research/v14-integration/browser/v14_acceptance.js --server-ready --base-url <root-v14-loopback> --prefix /WOW-Encyclopedia-Deployable-Archive/ --playwright-module C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright --manifest <v14-manifest> --provenance <v14-export-provenance> --route-map <v14-route-map> --selected research/continuous-recovery-20261015/selected-final-rss14-source-map.json --acceptance research/continuous-recovery-20261015/rss20-acceptance.json --acceptance-secondary research/continuous-recovery-20261015/rss21-acceptance.json --expected-selected-sha256 7019d82bca12be63f5ad832ae72729c1ac8b8fa3c4c4b6936f2d452f780d166b --expected-acceptance-sha256 decc5d48b5a55ffff2026299da1b8822ecd7f87d0ec4fa03e771286ebc346de4 --expected-acceptance-secondary-sha256 535f854d7e13573a8a36b6cc8548ef0f20a08314a62beb4ef52ceecec07130cc --toggle-route /news/rss-07-2007.xml --toggle-entry-id news7-30-07-513 --source-receipt <v14-source-receipt> --source-plan <v14-source-plan> --production-file tools/export_github_pages.py --output research/v14-integration/browser/v14-browser-receipt.json --screenshot-dir research/v14-integration/browser/screenshots

The runtime receipt must distinguish executed, passed, failed, and skipped checks and include the actual runner command, source/manifest/provenance/route-map/production hashes, selected page metadata, request diagnostics, and the single screenshot hash. This preparation phase has no runtime result.
