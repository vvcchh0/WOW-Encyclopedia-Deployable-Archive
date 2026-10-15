# Local implementation validation

Generated 2026-10-15T05:30:54Z. This check was local only: no network requests were made and the whole site was not built.

The four delegated derived fixes are ready for the parent build:

- **SSOTD clock** — `/downloads/ssotd/index.html` now derives `currentShotNumber` from the recorded route capture `20080512204328` and `startDate=12671`, yielding `1340`. The live `HEAD anachronos.xml` dependency is removed from the derived page; gallery pagination and hash behavior remain covered by `test_ssotd_clock_uses_recorded_capture_and_preserves_gallery_contract`.
- **Community nav IDs** — the derived `navtree-main.js` changes the Community parent count from `10` to `11`, keeps Fan Wallpapers at `Menu1_6_10`, and exposes Fan Sites as `Menu1_6_11`. The direct/idempotence and export-pipeline tests confirm both links and frozen source preservation.
- **Archived News aliases** — only the five verified near routes receive compatibility recovery: `dailyquests.shtml`, `titles.shtml`, `benice.shtml`, `credits.shtml`, and the duplicate `info/info/items/armorsets/` path. `test_archived_news_compatibility_aliases_rewrite_only_verified_targets` covers the derived links, redirect files, route map, and placeholder removal.
- **SSOTD thumbnail fallback** — a verified full image is used as the thumbnail only when its verified `-thumb.jpg` route is absent. Existing thumbnails retain priority, and unknown shots remain unchanged. Direct and pipeline tests cover this behavior.

The later image supplement policy is also validated. The default 2008 cutoff remains active. The explicit `--allow-later-image-supplements` / `allow_later_image_supplements=True` opt-in accepts a 2010 capture only when its source map declares `post_2008`; a wrong class is rejected, and a primary baseline map remains restricted to the anchor. `PagesImageOverlayTests.test_later_supplement_requires_explicit_opt_in_and_post_2008_class` passed in the preceding local image-overlay run.

The requested command was run with the repository Python runtime:

```text
C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -X utf8 -m unittest discover -s tests -p 'test_github_pages_export.py'
.....................
----------------------------------------------------------------------
Ran 21 tests in 2.538s

OK
```

`py_compile` and `git diff --check` passed. `git diff --quiet -- offline/site offline/build-manifest.json` reported `frozen_diff=clean`.

The repair-plan fixture audit found no remaining `policy-runtime-recovery`, `fixture-site`, or `fixture` token and no nonempty `raw_source_candidates` entry. The known `research/policy-runtime-recovery-20261012/fixture-site/policy/index.html` fixture is therefore absent from `repair-plan.json` and is not used as Free Trials evidence.

The exporter is frozen for parent integration and full-site construction.
