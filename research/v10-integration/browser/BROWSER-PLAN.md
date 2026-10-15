# v10 focused local browser acceptance

This directory is the bounded browser-validation surface for the root-owned
v10 Pages export. The runner never starts a server. It refuses to run unless
`--server-ready` is supplied. The coordinator must first confirm the loopback
server at `http://127.0.0.1:29006` is ready.

The request gate allows only `GET` and `HEAD` requests whose origin is the
supplied loopback origin and whose path is under
`/WOW-Encyclopedia-Deployable-Archive/`. External origins, other methods, and
local paths outside that prefix are aborted and retained in the receipt. No
Wayback or other network request is allowed.

## Frozen inputs

- v10 source receipt:
  `research/v10-integration/source/v10-source-receipt.json`, SHA-256
  `23b7e5cdfc9b26aea42e7fe8840670adb38c29d8e6e0486cb298a65911006cd5`.
- v10 selected additions:
  `research/continuous-recovery-20261015/selected-v10-final-additions.json`,
  SHA-256
  `c73b02d2f9353402eb4b568640e1359031e25756604cbbc5f21552f0acd52a55`.
- native viewer acceptance:
  `research/continuous-recovery-20261015/native-viewer-acceptance.json`,
  SHA-256
  `cf20b540bc6ef0bbea97342aec87f73c99231f8a86ac13dc9a2df6027dab1120`.
- v10 source manifest:
  `.scratch/offline-navigation-20261015-v10/build-manifest.json`, SHA-256
  `bc664a728da4bb6c5a49b2c2d46bc2837e2ae40e8a09f6e59c6dc755caa83d86`.
- root exporter:
  `tools/export_github_pages.py`, SHA-256
  `e6c13afe80a691bbeda46abe7f5b9b1b74bd3f28f1c4a2a08e946eedf7aa9569`.

The export provenance input is expected at
`.scratch/pages-resources-20261015-v10/export-provenance.json`; the runner
records its actual SHA and does not fabricate a value before root export is
ready.

## Checks

1. Load the seven new RSS-path pages as their concrete `.xml.html` Pages
   files. Require HTTP 200, visible HTML, the selected source title/heading,
   and posted-date evidence. Preserve the accepted anomalies: the April 2008
   path carries the March 2008 title, and the July 2006 path carries the
   September 2006 title.
2. Load Wrath artwork pages 1 and 2. Require both accepted counter scripts,
   common 12 plus locale 1, nine cards then four cards, and record every card
   link. Keep the five provenance-matched image pairs separate from the eight
   missing pairs. Decorative `ssborder1.png` absence is recorded separately;
   placeholder SVG decode is never counted as original-image recovery.
3. Click the real card center through its actual 243x193 anchor hit area. The
   observed destination must be the actual `/wrath/art.xml?s=12` logical
   viewer route (or its exported `.html?s=12` form), and the response/body
   result is recorded as resolved or the known viewer gap. No substitute
   Howling-Fjord lightbox is used.
4. Exercise the real viewer with `s=1`, `s=3`, `s=13`, missing, empty, `0`,
   negative, out-of-range, duplicate, unsafe integer, and encoded expression
   inputs. Record current/index/total and previous/next behavior. A missing
   adjacent image is an asset gap, not evidence that viewer indexing failed.
   The runner never injects a synthetic shot list.
5. Confirm the root route and runtime paths do not create an
   `index.htmlimages` request. Record every unknown 404, page error, console
   error, failed request, blocked request, and external reference separately.

Screenshots and receipt are written only below this directory. The run is
bounded to one invocation after the coordinator reports port 29006 ready; it
does not retry known missing resources or run the full v9 scenario set.

## Authorized command after server readiness

```powershell
$node = "C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
$playwright = "C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\playwright"
& $node "research/v10-integration/browser/v10_acceptance.js" `
  --server-ready `
  --base-url "http://127.0.0.1:29006" `
  --prefix "/WOW-Encyclopedia-Deployable-Archive/" `
  --playwright-module $playwright `
  --manifest ".scratch/offline-navigation-20261015-v10/build-manifest.json" `
  --provenance ".scratch/pages-resources-20261015-v10/export-provenance.json" `
  --output "research/v10-integration/browser/v10-browser-receipt.json"
```

This command is intentionally not run until root explicitly reports that the
29006 server is ready.
