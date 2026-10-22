# Related talent icons v55 loader

Implemented an explicit v1/v2 dispatch in `tools/related_talent_icons.py`. The v1 path still calls the original 986-image loader and keeps its asset records, catalog asset rows, notice, and public bundle shape unchanged. The v2 path validates the pinned map, decision, semantic audit, source acceptance, base map, and root pins, then appends the 20 accepted on/off JPEGs from same-class later-source paths.

The added catalog contains all 1,006 public assets and 20 explicit source mappings. Each mapping identifies its historical target route, later repository path and pinned-commit raw URL, reason, old/new data references, raw byte hashes, and `original_2008_pixel_identity: unknown`. The loader does not write pages or site files, fetch sources, or change data, CSS, or talent behavior.

Validation ran from `D:\WOW_Encyclopedia` with `TEMP` and `TMP` set to `D:\WOW_Encyclopedia\.scratch\test-temp-20261022`:

```powershell
python -X utf8 -m unittest tests.test_related_talent_icons tests.test_related_talent_icons_v2 tests.test_related_talent_pages
python -m py_compile tools/related_talent_icons.py tests/test_related_talent_icons_v2.py
git diff --check -- tools/related_talent_icons.py
```

The test run passed all 16 tests. A direct real-input smoke check loaded 986 v1 assets and 1,006 v2 assets; the first 986 asset records and catalog asset rows match v1 exactly, and the notice is unchanged. It decoded all 20 added JPEGs after validating SHA-256, Git blob SHA-1, length, 36×36 dimensions, and one frame.

The parent agent still owns full export and real-browser acceptance. This receipt records loader and unit-test evidence only; it does not claim production export or browser acceptance.
