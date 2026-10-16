# v25 local implementation plan

This is a plan-only artifact. The v24 output, maps, receipts, source15 manifest, and production tools remain frozen. No v25 output is created before root gives the source gate and export GO.

The accepted exporter has no prior-tree or incremental mode. `export_pages(...)` rejects an existing output or `.partial`, loads every overlay map, walks all 8,357 manifest records, regenerates route/support files and provenance, and atomically promotes one complete tree. A copy-and-patch path would have to recreate the localizer, origin index, collection rendering, and provenance identity by hand. It is technically possible but not safe inside this window, so the recommended path is one new v25 wrapper using the unchanged exporter API and a new output path.

After root accepts the nine neighbor retry payloads, the wrapper should preflight the v24 bindings, source receipts, new primary/supplement map entries, and a separately named collection-map revision. It should preserve the v24 preview map and all existing 179 overlay records. The new collection map may extend the three accepted groups only with accepted images that have a real guide/gallery relation. It must not invent native gallery aliases or relabel later captures as baseline images.

The wrapper should call the unchanged exporter exactly once after GO. The expected output file count is `8637 + N` declared and `8638 + N` actual, where `N` is the count of newly accepted image overlays. Existing source records, preview counts `6/22`, and old overlay metadata must remain unchanged. A post-promotion exception retains the tree and receipt; it does not trigger a retry.

`check_v25_offline.py` is a parameterized, worker-only checker. Root supplies the v25 site, worker receipt, root acceptance, repeatable new receipts/maps, collection map, and expected primary/supplement additions. It verifies the frozen v24 provenance SHA, source15 manifest SHA, prior overlay metadata and bytes, route conservation, accepted receipt/map/output bindings, collection expansion, unchanged previews, output counts, provenance hashes, and an explicit changed-path allowlist. It writes only its own local receipt and does not run the exporter, browser, network, extraction, or publication.

The bounded estimate after the accepted receipt is available is 2 minutes for source/map preflight, 8 minutes for the full export, 3 minutes for offline QA, and 3 minutes for the root browser/publication handoff: 16 minutes total, leaving 24 minutes inside the 40-minute window.
