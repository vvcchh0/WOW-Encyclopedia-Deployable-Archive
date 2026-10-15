# Core pages integration — accepted v9 mirror checkpoint

This directory contains the bounded local integration of the accepted core-page
payloads into a fresh v9 staging tree. The earlier pending preparation remains
as a historical snapshot; the current accepted map and build receipt are kept
separately below.

`prepare_core_pages.py` performs only local reads and writes. Its earlier
preparation step verified the seven core-pages3 body lengths and SHA-256
values against the payload map, `core-pages3-acceptance.json`, and
`root-content-review-0753.json`. The current v9 builder additionally verifies
the accepted pages4/core selection and NET005 static selection. Both steps
check the frozen manifest anchor and record its SHA-256. Body and header paths
remain in their original batch directories; the derived maps point to those
paths and do not copy, rewrite, or delete raw bytes.

The v9 build reuses the existing `.scratch/offline-navigation-20261015-v7c`
baseline and preserves its source/image overlays. The preparation record and
build receipt store
the v7c build-manifest SHA
(`f66906976031d47027be9ccff5deaac9955b6b96950cad468664e1985f7c0808`) as a
local preservation checkpoint; no v7c file was changed in this run.

The current selected core map is
`research/continuous-recovery-20261015/core-pages-integration/core-pages-source-map.selected.json`
(11 targets: eight News HTML bodies, BC professions, Wrath artwork, and the
retained 2006 PTR body). The coordinator's
`research/continuous-recovery-20261015/selected-core-pages-source-map.json`
is the accepted upstream selection that this derived map records. The pages4
acceptance receipt is accepted with zero network requests and contributes nine
valid HTTP 200 entities. The old 2004 News and PTR raw entities remain from
pages3. `/ptr` has the explicit `/ptr/index.html` output route and exact `/ptr`
and `/ptr/` aliases.

The independently accepted NET005 static map is
`research/continuous-recovery-20261015/selected-static-source-map.json`
(11 targets: two Wrath artwork counter scripts, three domestic arena images,
and six exact-origin `armory.wow-europe.com` images). The v9-derived copy is
`selected-static-source-map.v9.json`; it keeps the foreign logical URLs and
places those payloads under `/_origins/armory.wow-europe.com/`. Its acceptance
receipt is `assets5-acceptance.json`, and the original source-map SHA recorded
there is checked before the derived map is used. The two counter scripts are
both retained, so the Wrath gallery has the common and locale-specific static
inputs available for the later browser check.

The independently accepted decision
`research/continuous-recovery-20261015/battlegroups-alias-decision.json`
adds only the compatibility alias
`/pvp/battlegrounds/battlegroups.html` →
`/pvp/battlegrounds/battlegroups/index.html`; it does not add a new HTML
entity or copy a dispatcher redirect body.

## Historical preparation command

```powershell
& "C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -X utf8 -u "research/continuous-recovery-20261015/core-pages-integration/prepare_core_pages.py" --prepare
```

This command writes the earlier pending snapshot:

- `core-pages-source-map.pending.json` in this directory;
- `.scratch/offline-navigation-20261015-v9/PREPARATION.json`.

It does not touch `offline/site`, `offline/build-manifest.json`, or v7c.

## Completed v9 build

`build_core_pages_v9.py` validates the selected local body/header paths, exact
lengths and SHA-256 values, HTTP 200 status, pre-anchor timestamps, acceptance
receipts, the frozen anchor, the accepted Battlegroups alias decision, and the
NET005 static payloads. It then runs the existing offline mirror recipe with
zero network requests. The current successful mirror receipt is
`.scratch/offline-navigation-20261015-v9/BUILD-RECEIPT.json`.

The current v9 outputs are `.scratch/offline-navigation-20261015-v9/site` and
`.scratch/offline-navigation-20261015-v9/build-manifest.json`. The v9 manifest
has 8,328 routes (the 8,306 v7c records plus the 11 selected core routes and
the 11 accepted static payload routes), and its SHA-256 is
`0da72688ec5057650c2ef46a4634097323dc9c43eb19997afcad264b12dba3b8`.
The mirror receipt reports 8,328 derived files/routes, 11 accepted core
targets, and 11 accepted static targets. Every v7c route has the same source
SHA, source length, kind, and role in v9; no v7c route is missing or changed.
The existing image-overlay baseline remains 38 records: 19 primary and 19
supplement records.

This is deliberately a mirror-only checkpoint. No current `pages` directory
is published by this worker; the old
`.scratch/offline-navigation-20261015-v9/BUILD-RECEIPT-pre-map-correction.json`
and the old `PREPARATION.json` remain historical intermediate records. Root's
final exporter run must consume this v9 site/manifest with the established v8
image-overlay flags, preserving all 38 overlays, and then perform the browser
acceptance. This plan does not treat the pre-correction Pages tree as a
publication target.

The eight News entries continue through the existing exporter with their
captured article bodies intact. The PTR entry should be passed through
`tools/historical_exhibits.py`, which emits the neutral title
`World of Warcraft Public Test Realm — Historical Exhibit`, source-backed
historical facts, and only the confirmed local archive links for home, guide,
PTR FAQ, and test-realm patch notes. Character-copy, download, forum, form,
and script behavior from the captured page must not be exposed as active
controls. The home link must use the generated Pages root `index.html`; the
captured `/index.xml` entity is emitted separately as `index.xml.html` and is
not the root-page link.

## Browser acceptance plan for the completed v9 build

After root's final Pages export, run the existing local Playwright/validation
harness against `/ptr`, `/ptr/`, and `/ptr/index.html` on desktop and a narrow
viewport. Confirm the neutral title and UTC capture date, no operational
controls or external request, and working local links to the four confirmed
archive routes. Visit the Battlegroups `.html` compatibility alias and confirm
that it resolves to the existing canonical index without changing its source
bytes. Visit the Wrath artwork page after both accepted counter scripts and
the nine accepted images are present; record whether the gallery is statically
complete and whether any dynamic behavior remains unverified. Check that the
page has no horizontal overflow and that all eight News routes retain their
captured title/date headings. The local build and focused unit tests report
zero network requests; final Pages/browser results belong to root.
