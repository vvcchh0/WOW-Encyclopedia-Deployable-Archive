## GitHub Pages export verification

- Output: .scratch/pages-preview-final
- Project prefix: /WOW-Encyclopedia-Deployable-Archive/
- Source manifest SHA-256: 397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459
- On-disk files/bytes: 8399 / 555433910 (includes export-provenance.json)
- Provenance records: 8398; duplicate output paths: 0
- Frozen source records covered: 8304 with 8304 unique source paths
- .nojekyll: True; README provenance hash: True

The final exporter now maps exact-topic search synchronously through window.__WOWPages.mapHref, wraps Element.prototype.innerHTML while preserving the native descriptor, and exposes mapCssImages for the cascade avatar path. The cascade derivation takes the topic basename before constructing the icon URL. The runtime also preserves all document.write/writeln arguments, maps dynamic images and CSS backgrounds, and passed Node vm.Script syntax validation with 0 control bytes.

Derived XML/XSL records: 18/19 parsed. The only derived failure is new-hp/layout/layout.xsl; its frozen source is also malformed because of nested unescaped attribute quotes. Fourteen frozen XSL sources have historical XML parse errors; most are made parseable in the derived output by escaping bare ampersands.

Fixture compile and unittest checks passed (2 tests). The output is derived and does not alter offline/site or offline/build-manifest.json. Uncollected or missing resources remain explicit local placeholders and are never fetched from the network. Parent browser QA remains pending.

