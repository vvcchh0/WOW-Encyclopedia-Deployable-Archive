# Toplist v36 browser-error diagnosis

## Scope and evidence boundary

This is a read-only comparison of the frozen Source15 snapshot, v35 output, v36 output, and the already-frozen v36 browser r2 result. No source tree, exporter, accepted output, map, or browser result was changed. No network request or new browser run was made.

The structured evidence is in [toplist-diagnosis-evidence.json](toplist-diagnosis-evidence.json), SHA-256 `b180770d4abaa954b2ed508bf67528cdaaa5479836ec300688d56cd930bc4b96`. The frozen browser result used here is `research/continuous-recovery-20261019/integration/v36/browser/results/v36-browser-r2.json`, 166466 bytes, SHA-256 `6c080800a2f6cc0ae2ee7483834c62b43ec8d6cab216a80d1c4481d266114889`.

## What changed

`toplist/index.html` is byte-identical in v35 and v36: 19059 bytes, SHA-256 `95dcdb612e7a41992916ab4ca75c464ea127eb332f14a61ff308a9b7dcdb5792`. Its Source15 baseline is 15792 bytes, SHA-256 `d98878e2a7c62adcd0cc0cd9c43d786d61f696552e76de653f47dc48bb8679ec`.

The page loads the relevant scripts at these derived lines:

- line 11: `toplist/includes-client/js/prototype.js`
- line 12: `toplist/includes-client/js/scriptaculous.js?load=effects`
- line 101: `toplist/includes-client/js/logic.js`
- line 317: inline `window.onload = init;`

The Source15 counterparts are lines 7, 8, 97, and 311 respectively. The generated page adds the project prefix, the offline runtime/banner, and placeholder/localized paths, but the v35 and v36 HTML bytes are the same. The full bounded HTML diff is [index-source15-v35.diff](excerpts/index-source15-v35.diff); [index-v35-v36.diff](excerpts/index-v35-v36.diff) is empty.

The relevant source/derived bytes are:

| asset | Source15 | v35 | v36 |
|---|---:|---:|---:|
| `toplist/includes-client/js/prototype.js` | 64868 bytes, `4efde4e87b2db7b8cb6b81f70ab4972c3cfbcd7d329d0752ad223abe67fa9120` | 65110, `83ac7f8b8926b4f4c176aa20e1841cc502063d1c6f4dfa669eead54544d8bc3b` | identical to v35 |
| `toplist/includes-client/js/logic.js` | 47479, `1c0a50ff5fd1af19663b925e502c3a3b2dab0eb905874d95966e8bf35504eabe` | 48689, `d2579e183174394d3b8784512718ae53453bac56b64f65db1e8d37263bbcd4ca` | identical to v35 |
| `toplist/includes-client/js/scriptaculous.js` | 2404, `a59f8cfa0f9de98fc196d1bb7a9669958d7ec6ad9bd50f80e0c110b50f3e4c75` | identical | identical |
| `toplist/includes-client/css/styles.css` | 9964, `e0374f02a5c701a510296a38a63f05f23dd0e9427d58fb759b80dbb9ba897a70` | 10900, `9b1b8a736e5939b6e2f605adaa9fea8a18f144f89dcb4945513ebf3e5a5250b5` | identical to v35 |
| `toplist/includes-client/css/styles-en.css` | 3349, `dcb317cc8183f2064994a13dba8133e5d41a9c73a729eed4039a5a59083ea921` | 3709, `f95d43bd96d643e8154d0c3ac8116314dec44ee24c7093dad027c155a120f6a4` | 2841, `6485acf1cbaf116cff11ee4ccfb3f8555085c0fb47dc212dc1d1f0cd1fedbd74` |
| `__offline/pages_runtime.js` | absent | 1204617, `541cf0e0c9c07fadb8611b2243f3ec078fe0dad9957648f12c5fea34ccb3c17f` | 1210579, `8e33e2c974f39e3a2ae7ea02f493aaa6f1dfb15475952d22cd28393f653e7994` |

The v35/v36 provenance classifies `prototype.js` as transformed `expanded_approved_page_text_dependency` with one placeholder reference and `logic.js` as transformed `late_2008_static_dependency_after_anchor` with five placeholder references. `styles-en.css` is a transformed `toplist_localized_stylesheet_after_anchor`; v36 changes only the four `next-wide`/`prev-wide` hover/background declarations from missing-image placeholders to collected local images. That CSS restoration is unrelated to the JavaScript parse failures. The provenance rows are retained in the evidence JSON.

## Exact failures and causal chain

The frozen browser result recorded all four errors on the same v36 Toplist URL:

`http://127.0.0.1:1110/WOW-Encyclopedia-Deployable-Archive/toplist/index.html`

1. `SyntaxError: Invalid regular expression flags` maps to derived `prototype.js:261`. Source15 line 261 is valid `escapedString.replace(/'/g, '\\\'')`; the derived line has a missing-image URL inserted between the regex delimiter and `g`. The exact lines are in [v35-prototype-lines258-263.txt](excerpts/v35-prototype-lines258-263.txt) and [prototype-source15-v35.diff](excerpts/prototype-source15-v35.diff).
2. `script.aculo.us requires the Prototype JavaScript framework >= 1.5.0` is a downstream runtime error from unchanged `scriptaculous.js:33-38`: the preceding Prototype file did not parse, so `Prototype` was never defined. `scriptaculous.js` itself passes Node syntax checking in Source15, v35, and v36.
3. `SyntaxError: Unexpected identifier 'width'` maps to derived `logic.js:681`. The source line contains an HTML fragment inside a JavaScript string with escaped attribute quotes. The derived localizer consumes the closing backslash/quote while replacing `/toplist/images/pixel.gif`, leaving `...resource" width=...` with an unescaped quote that terminates the JavaScript string. The exact lines are in [v35-logic-lines678-697.txt](excerpts/v35-logic-lines678-697.txt) and [logic-source15-v35.diff](excerpts/logic-source15-v35.diff).
4. `ReferenceError: init is not defined` is at the frozen page line 317. `init` is defined by `logic.js:906`, but that file cannot load after error 3. The inline block itself passes Node syntax checking; see [v36-index-lines308-329.txt](excerpts/v36-index-lines308-329.txt).

The Source15 versions of both affected external files pass `node --check`. The v35 and v36 versions fail at exactly the two lines above. All other eight checked external Toplist/shared JavaScript files pass for Source15; six of eight pass for each derived version. All three non-empty inline blocks pass for Source15, v35, and v36 (9/9), and both injected `pages_runtime.js` files pass (2/2). These are offline syntax checks, not a substitute for a post-fix browser run.

## Root cause assessment

The failure is introduced by the derived JavaScript URL-rewrite stage, before the v36-specific image additions. The current exporter defines `_ROOT_LITERAL_RE` at `tools/export_github_pages.py:122-124` as a generic quote followed by `/...`, then applies it to every raw-text script body through `rewrite_inline_scripts` and `rewrite_root_literals` at lines 725-759 and 818-856. It does not distinguish a JavaScript regular-expression literal from a quoted string, and it does not preserve escaped HTML attribute quotes inside a JavaScript string.

That explains both malformed lines and the version relationship: Source15 is syntactically valid, v35 introduces the malformed derived bytes, and v36 retains the same `prototype.js`, `logic.js`, and `index.html` bytes. There is no evidence here that the Wayback/source snapshot already contained these syntax errors. The old Prototype 1.5 runtime may have separate modern-browser compatibility limits, but these four observed errors are explained by the deterministic derived rewrite and should be fixed before assessing those limits.

The minimal evidence excerpt for the existing rewrite boundary is [exporter-root-literal-lines.txt](excerpts/exporter-root-literal-lines.txt), SHA-256 `99ab684563159b013c5355c6ef39d535f06ce396cddfb771d4bb42f7c0fc3eac`. The exporter file was only read; its current SHA-256 is `60fa3cb3279bd2478de73d861fc648efaeda760ca8ee609e4ba3cf3b3030f35d`.

## Narrow reversible repair candidate

Keep the Toplist page and ranking data intact. In a future exporter change, constrain script URL localization to a JavaScript-aware path:

- for the exact Toplist script assets (or an equally narrow JS-tokenized pass), rewrite only URLs inside actual JavaScript string literals;
- skip regular-expression literals, comments, and expressions, so `/\\'/g` in Prototype is never treated as a URL;
- when a URL occurs inside an HTML fragment carried by a JavaScript string, replace the URL value while preserving the surrounding escaped `\\"` attribute quotes and JavaScript string delimiters;
- leave the existing non-script CSS/HTML localization and v36 `styles-en.css` image restoration unchanged.

A focused regression should feed the two exact source fragments above through the candidate rewrite, run `node --check` on the resulting Prototype and logic bodies, and assert that the ranking HTML string still contains a valid `src=\"...\" width=...` fragment. The production acceptance should then run one local Toplist page with external requests blocked and verify that `Prototype` loads, `init` is defined, `body.wide`/intro/navigation are present, and ranking content remains available. No broad catch or removal of the ranking display is warranted.

This diagnosis does not apply that repair, rerun the browser, or alter any frozen output. Root must decide whether to implement a route-scoped lexer/rewriter or another equally narrow reversible fix.

## Produced artifacts

- [toplist-diagnosis-evidence.json](toplist-diagnosis-evidence.json): source/v35/v36 hashes, provenance rows, script/link line inventory, browser errors, Node checks, and finding summary.
- [excerpts/index-source15-v35.diff](excerpts/index-source15-v35.diff), [excerpts/prototype-source15-v35.diff](excerpts/prototype-source15-v35.diff), [excerpts/logic-source15-v35.diff](excerpts/logic-source15-v35.diff), [excerpts/styles-en-v35-v36.diff](excerpts/styles-en-v35-v36.diff): bounded diffs.
- [excerpts/v35-prototype-lines258-263.txt](excerpts/v35-prototype-lines258-263.txt), [excerpts/v35-logic-lines678-697.txt](excerpts/v35-logic-lines678-697.txt), [excerpts/v36-index-lines308-329.txt](excerpts/v36-index-lines308-329.txt): exact failure contexts.
- [excerpts/exporter-root-literal-lines.txt](excerpts/exporter-root-literal-lines.txt): existing exporter rewrite boundary.

Validation commands used:

```powershell
node --check .scratch/offline-navigation-20261015-v15/site/toplist/includes-client/js/prototype.js
node --check .scratch/pages-resources-20261019-v35/toplist/includes-client/js/prototype.js
node --check .scratch/pages-resources-20261019-v36/toplist/includes-client/js/prototype.js
node --check .scratch/offline-navigation-20261015-v15/site/toplist/includes-client/js/logic.js
node --check .scratch/pages-resources-20261019-v35/toplist/includes-client/js/logic.js
node --check .scratch/pages-resources-20261019-v36/toplist/includes-client/js/logic.js
```

Results: Source15 prototype/logic pass; v35/v36 prototype fail with `Invalid regular expression flags` at line 261; v35/v36 logic fail with `Unexpected identifier 'width'` at line 681. The full bounded command results and all other checks are in the evidence JSON.
