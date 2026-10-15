# V13 focused browser acceptance plan

Status: completed once against the root-declared loopback preview; the final receipt and the preserved first harness-failure receipt are recorded beside this plan.

This bounded run covers:

- /news/rss-09-2006.xml: real HTML title containing September, 2006, 38 posted-date and 38 news-entry-date values, all September 2006.
- /news/rss-05-2008.xml: real HTML title containing May, 2008, 11 matching date values, all May 2008. The accepted source is an observed May 1 through May 8 partial capture; the run makes no full-month claim.
- /news/rss-12-2007.xml: real HTML title containing December, 2007, 29 matching date values, all December 2007.
- /news/newsarchive.css: a stylesheet attached in the real DOM and a real local GET on all three pages; expected 109 bytes and SHA-256 69915a4eea19ec455a60b89c64ed661fc55d48bc3a724bdffcc91d2d617aa7b.
- The established default-collapsed V12 news entry news7-30-07-513 on /news/rss-07-2007.xml, exercised in four fresh browser contexts: visible h1 a locator click, physical center click on li.news-toggle, physical center click on the matched anchor, and focused anchor Enter. Each action must produce collapsed -> expanded -> collapsed and records the ancestor class, body/news-item/description display and visibility, li and anchor rectangles, original href, nearest hoverContainer onclick, and actual click/focus details. Anchor actions require the observed 14px by 11px box.
- One screenshot only: anchor-center-expanded entry evidence.

The runner uses ordinary Playwright actions. It does not call toggleEntry, edit DOM styles or handlers, inject list entries, use force, add requests, or start a server. The request gate permits only GET/HEAD requests to the supplied loopback origin and deployment prefix. External origins, outside-prefix paths, and every other method are aborted and recorded. Known placeholder 404s remain diagnostics; unknown 404s, request failures, page errors, console errors, or blocked requests are separate failures.

The runner binds these accepted source inputs before page checks:

- research/v13-integration/source/v13-source-receipt.json, SHA-256 e3f2f51c4be9eaa10e30e0143fc301b166dbc4e84feb134933658f8e9d1befe2, source count 8347.
- research/v13-integration/source/v13-source-plan.json, SHA-256 118d767da3a0f6ce4588ccde079a6832d3c93d5890991da3210af03bf5bc0ff1.
- research/continuous-recovery-20261015/selected-rss18-source-map.json, SHA-256 e3af3c2c9cb8c40b96bd5a6964d32faac92d4a2e6da158bcb34ad9b59313c591.
- research/continuous-recovery-20261015/rss18-acceptance.json, SHA-256 e5ed5e6ada59892ef211442eac60e8378742f8e3c95b9533188a8da0f290ca74.
- V13 source manifest .scratch/offline-navigation-20261015-v13/build-manifest.json, SHA-256 b9f26e1aa4544b5b1279c7a7e54acbf1306da5518c6a3b7aa685e05df9cfbdc9. Root may bind the final export manifest and expected SHA at runtime.
- Final export provenance and route map are runtime inputs supplied by root; the runner records and optionally checks their expected hashes.
- tools/export_github_pages.py is bound at runtime by path and SHA.

Prepared syntax-only command:

    & C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe --check research/v13-integration/browser/v13_acceptance.js

Root-declared runtime command:

    & C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe research/v13-integration/browser/v13_acceptance.js --server-ready --base-url http://127.0.0.1:29009 --prefix /WOW-Encyclopedia-Deployable-Archive/ --playwright-module C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright --manifest .scratch/offline-navigation-20261015-v13/build-manifest.json --provenance .scratch/pages-resources-20261015-v13/export-provenance.json --route-map .scratch/pages-resources-20261015-v13/__offline/route-map.json --source-receipt research/v13-integration/source/v13-source-receipt.json --source-plan research/v13-integration/source/v13-source-plan.json --selected research/continuous-recovery-20261015/selected-rss18-source-map.json --acceptance research/continuous-recovery-20261015/rss18-acceptance.json --production-file tools/export_github_pages.py --output research/v13-integration/browser/v13-browser-receipt.json --screenshot-dir research/v13-integration/browser/screenshots

Acceptance requires the runtime receipt to distinguish executed, passed, failed, and skipped checks and to include the actual command, node path, runner SHA, source/provenance/route-map/production hashes, response diagnostics, and screenshot hash. The first runtime stopped before navigation on a local date-frequency assertion; the corrected single runtime completed the listed checks. See execution-binding.json and the two receipts.


