# Available-resource route review

Generated 2026-10-21T12:10:53.169998+00:00. Local no-network review of the unaccepted v50 candidate; no production code, site output, frozen source, or Git was changed.

## Exact existing T.gif

The approved entity is `http://www.worldofwarcraft.com/wrath//images/letters/T.gif`, captured at `20080423095102`, MIME `image/gif`, length `1419`, SHA256 `0a82046107b2f5a45b258143cd8f862030980507bad23190c54445b43b3a62ad`. v50 already contains the exact bytes at `wrath/images/letters/T.gif` and provenance preserves the logical double-slash route. Four actual static page references were found: Howling Fjord, Grizzly Hills, Borean Tundra, and the Source16 Bard page.

The v50 route map has only `routes["/wrath//images/letters/T.gif"]` pointing at `/WOW-Encyclopedia-Deployable-Archive/wrath/images/letters/T.gif`; the single-slash key is absent although the static file exists. The minimal proposal is one entry in `tools/export_github_pages.py:141` `COMPATIBILITY_ROUTE_ALIASES`:

```python
"/wrath/images/letters/T.gif": "/wrath//images/letters/T.gif"
```

This exact alias adds no payload, no generic `//` collapse, no D/F expansion, and no new HTML redirect because the output path already exists. The proposal was not executed here.

## Community-anniversary anomaly

The only closeout `url_uncertain` row is `/community/anniversaries/WOW-Encyclopedia-Deployable-Archive/__offline/missing.html`, observed on `/community/anniversaries/year1timeline.html`. It is classified as an **actual export transform bug**, not probe-only concatenation. Source16/v16 has `var theDirectory = "/images/year1/";` (line 241). v50 rewrites it to a Pages-prefixed `__offline/missing.html` placeholder (line 246). The unchanged screenshot helper concatenates `path + theDirectory + ssN-thumb.jpg` (line 16), while its path initialization retains the Pages prefix. The exporter `rewrite_root_literals` path (`tools/export_github_pages.py:832-866`) localizes this semicolon-terminated literal, while its `+` guard only protects literals immediately followed by `+`. The accepted phase3 browser row captures the resulting duplicate-prefix requested value. Closeout `clean_path` (`build_closeout.py:57-81`) only strips a leading project prefix and preserves the embedded prefix as `url_uncertain`; it does not create it.

This issue is separate from T.gif and remains unmodified. The screenshot directory is still uncollected; no screenshot recovery is claimed.

See `route-review.json` for selected hashes, exact records, route-map observation, acceptance assertions, and the browser-observed value; `t-gif-references.csv` contains the four page references.

D-drive free space before writing: 25662652416 bytes (floor 11005853696).
