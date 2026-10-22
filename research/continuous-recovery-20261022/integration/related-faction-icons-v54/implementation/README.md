# Related faction icon loader implementation

This directory records the local adapter implementation for the fixed v54
three-image map. The loader reads the pinned Source16 build manifest, source
acceptance, semantic audit, repository JPEG bytes, decision, and root input
pins. It returns an in-memory frozen bundle for the exporter; it does not write
site files or perform network access.

The visible notice identifies a later 2015 game-database source. The original
Source16 GIF bytes and pixel identity remain unknown. The source acceptance
record remains unchanged; its initial browser-acceptance value is surfaced as
`initial_source_record_browser_acceptance=false`, separately from the newer
derived-trial decision.

Validation commands run from the repository root:

```powershell
python -X utf8 -m unittest tests.test_related_faction_icons -v
python -X utf8 -m unittest tests.test_related_faction_icons_pages -v
```

The loader-specific suite covers the exact three payloads, 36×36 single-frame
JPEG decoding, all eleven notice routes, catalog curation, path boundaries,
same-length payload drift, and wrong-format/dimension rejection. The exporter
consumer suite exercises route reuse, notices, provenance, manifest checks,
and collision rejection.
