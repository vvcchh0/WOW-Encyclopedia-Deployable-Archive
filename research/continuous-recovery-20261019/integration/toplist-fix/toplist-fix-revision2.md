# Toplist compatibility fixture portability — revision 2

This revision makes `tests/test_toplist_compat.py` independent of the ignored
`.scratch/offline-navigation-20261015-v15` tree. The test now reads the two
byte-preserving files in `tests/fixtures/toplist-source15/` by fixture
basename. The production Toplist helper and exporter were not changed.

The fixtures are verified against the Source15 manifest
`d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002`:

- `prototype.js`: 64868 bytes,
  `4efde4e87b2db7b8cb6b81f70ab4972c3cfbcd7d329d0752ad223abe67fa9120`
- `logic.js`: 47479 bytes,
  `1c0a50ff5fd1af19663b925e502c3a3b2dab0eb905874d95966e8bf35504eabe`

The fixture provenance and rights note are in
`tests/fixtures/toplist-source15/README.md`, with the repository's existing
`NOTICE.md` governing archived-material rights.

## Focused validation

The only rerun for this revision was the three-test focused suite, wrapped in
`subprocess.run(..., timeout=120)`:

```text
python -X utf8 -m unittest discover -s tests -p test_toplist_compat.py -v
```

It returned `0`, ran `3` tests, and completed in `1.184801` seconds. The
captured output is
`subprocess-test-output-r2.txt` (SHA-256
`047e12087bad53fd184ee897f6e6084eccb2c1f957707ff4f5600c28fca71d0b`). The
earlier fixture-path failure from the first bounded attempt is preserved as
`subprocess-test-output-r2-initial-fixture-path.txt` rather than overwritten.

The previous revision-1 verification receipt remains unchanged at
`toplist-fix-verification.json`; the 34-test exporter regression recorded
there was not rerun for this portability-only revision. No export, browser
run, network request, or commit/push was performed.
