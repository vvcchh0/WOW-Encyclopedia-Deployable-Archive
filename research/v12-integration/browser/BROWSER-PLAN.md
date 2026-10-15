# V12 focused browser acceptance plan

Status: prepared; waiting for the root agent to declare the loopback server at `http://127.0.0.1:29008/WOW-Encyclopedia-Deployable-Archive/` ready.

This bounded run covers only the three V12 RSS path additions and one real accordion interaction:

- `/news/rss-07-2007.xml`: exported HTML, title identity, 57 posted dates, all July 2007, and the matching `.news-entry-date` values.
- `/news/rss-06-2007.xml`: exported HTML, title identity, 49 posted dates, all June 2007, and the matching `.news-entry-date` values.
- `/news/rss-04-2007.xml`: exported HTML, title identity, 39 posted dates, all April 2007, and the matching `.news-entry-date` values.
- `/news/newsarchive.css`: a real stylesheet link and a real GET response on each of the three pages; expected 109 bytes and SHA-256 `69915a4eea19ec455a60b89bc3a724bdffcc91bd2d617aa7b`.
- One genuinely default-collapsed entry selected from the July page. The runner clicks its visible `h1 a` with ordinary Playwright `locator.click()`, records the before/after display, visibility, rectangle, entry identity, and toggle evidence, and saves one screenshot.

The runner binds the selected-source, acceptance, V12 source receipt, V12 manifest, final export provenance, and final route map before exercising pages. It requires source count 8344 and 183 aliases, and it checks the date arrays from both `.posted-date` and `.news-entry-date` for exact equality. It records final URLs, titles, visible body length, response/request diagnostics, page errors, console errors, request failures, and unknown 404 responses separately.

The request gate allows only GET and HEAD requests whose origin is the supplied loopback server and whose path is under the deployment prefix. External origins, paths outside the prefix, and every other method are aborted and recorded. The runner does not start a server, use the network, alter DOM styles, inject entries, or use force clicks. Known placeholder 404s are retained as diagnostics and are not silently counted as recovered resources.

Prepared command (runtime is intentionally not run until the server-ready declaration):

```powershell
& "C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe" research/v12-integration/browser/v12_acceptance.js --server-ready --base-url http://127.0.0.1:29008 --prefix /WOW-Encyclopedia-Deployable-Archive/ --playwright-module "C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright" --manifest .scratch/offline-navigation-20261015-v12/build-manifest.json --provenance .scratch/pages-resources-20261015-v12/export-provenance.json --route-map .scratch/pages-resources-20261015-v12/__offline/route-map.json --output research/v12-integration/browser/v12-browser-receipt.json --screenshot-dir research/v12-integration/browser/screenshots
```

The runner passed `node --check` before runtime. The final receipt must distinguish executed, passed, failed, and skipped checks; it must report the actual server/export hashes used at runtime and remain a focused V12 result rather than a rerun of the V11 image/viewer matrix.
