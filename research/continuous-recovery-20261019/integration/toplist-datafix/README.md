# Toplist datafix preparation

This directory records the bounded, source-hash-guarded data/CSS repair for the frozen Source15 Toplist logic asset. It does not modify Source15, v37/v36 outputs, accepted maps, the exporter, or production data.

The diagnostic found three missing requests outside the local site prefix: `/toplist/data/en/killedby_10052008.js`, `/toplist/images/table-left.jpg`, and `/toplist/images/table-right.jpg`. Source15 has zero accepted Toplist data routes, so the derived logic keeps the original `dataDir` and feed derivation but maps only exact `/toplist/data/<lang>/<feed>.js` entries present in `PagesLocalizer.route_to_static`. Unknown feeds render the historical missing-date message without creating an XHR; future accepted routes use only their local static path.

The two table edge CSS URLs use the existing `css_url` localizer and placeholder path when no exact accepted image exists. The Prototype remains byte-for-byte unchanged. `toplist-datafix-verification.json` contains source pins, synthetic runtime evidence, test command, and SHA256 values.
