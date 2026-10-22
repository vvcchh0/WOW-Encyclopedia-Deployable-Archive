# Related guide images v53 loader implementation

The guide-image adapter now accepts the pinned v2 one-image input and the pinned v3 two-image input through the existing `load_related_guide_image_bundle` interface. The v2 path retains its one JPEG, compatibility alias, catalog shape, metadata, and notice behavior. The v3 path retains The Broken JPEG and adds the Profession Updates PNG as a current related-source banner; its historical capture time remains unknown.

For v3, the loader checks the exact map, decision, source-acceptance, and `root-input-pins.json` hashes and values; verifies the Source16 manifest binding; checks both upstream source-acceptance file paths, hashes, schemas, and image roles; and rejects unexpected entry routes or payload paths. Payloads are checked by byte count and SHA256. JPEGs retain the shared JPEG validation; PNGs must decode fully as a single-frame 324×72 PNG. A changed, damaged, alternate-format, or re-encoded PNG therefore fails validation.

The v3 bundle returns two assets, three route reuses (the two static routes and The Broken compatibility route), and attribution notices for both guide pages. The catalog keeps the same route mappings. The Profession Updates item is labeled as a current ArchiveCraft source, observed 2026-10-22, with no 2008 capture claim.

Validation run from `D:\WOW_Encyclopedia`:

```powershell
python -m unittest tests.test_related_guide_images tests.test_related_guide_pages -v
python -m py_compile tools/related_guide_images.py tests/test_related_guide_images.py
```

Results: 12 focused loader and consumer tests passed; both edited Python files compiled successfully. Test temporary directories are created under `.scratch/test-temp-20261022` on D:. Full site export and Chrome/browser image review remain with the parent acceptance step.
