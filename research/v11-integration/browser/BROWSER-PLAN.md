# V11 focused local browser acceptance

This directory contains the single bounded browser run for the root-owned v11
export. The runner never starts a server. It requires the coordinator's
`--server-ready` confirmation for `http://127.0.0.1:29007` and applies a hard
request gate: only `GET` and `HEAD` requests to that exact loopback origin and
the supplied `/WOW-Encyclopedia-Deployable-Archive/` prefix continue. External
origins, non-HTTP URLs, prefix escapes, and every other method are aborted and
reported independently.

The run binds the runner SHA, `tools/export_github_pages.py` SHA, v11 source
manifest, final export provenance, and final export route-map at runtime. The
source receipt and three-entity map are pinned to their accepted SHA values;
the final export files are required to exist and their actual hashes are
recorded in the receipt.

The exact focused command is:

```powershell
& "C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe" `
  research/v11-integration/browser/v11_acceptance.js `
  --server-ready `
  --base-url "http://127.0.0.1:29007" `
  --prefix "/WOW-Encyclopedia-Deployable-Archive/" `
  --playwright-module "C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\playwright" `
  --manifest ".scratch/offline-navigation-20261015-v11/build-manifest.json" `
  --provenance ".scratch/pages-resources-20261015-v11/export-provenance.json" `
  --route-map ".scratch/pages-resources-20261015-v11/__offline/route-map.json" `
  --output "research/v11-integration/browser/v11-browser-receipt.json"
```

The executed checks are seven RSS-path HTML pages with their historical title
and posted-date evidence, the real `newsarchive.css` response plus computed
rules on existing RSS markup, the two BlizzCast JPEG page instances and Arena
GIF page instance with exact HTTP/MIME/SHA/decode and DOM visibility evidence,
and the common12 viewer route with index 12 and accepted displayed-image
provenance. The GIF result is static decode evidence only; no animation claim
is made. Any duplicate original image references are retained as observed
multiplicity.

Known artwork/border 404s are recorded as known gaps. Unknown 404s, page
errors, non-generic console errors, failed requests, and blocked requests are
separate failures. The runner does not inject DOM, replace `shotList`, force a
click, start a server, or retry unrelated historical scenarios.
