# MEDIA redirect target plan

Status: local-only plan from saved evidence. This audit made no network requests and does not add a source-map entry.

The saved MEDIA/SSOTD inventory has 2,082 rows: 1,971 redirects, 21 archive 404 rows, 47 revisits, 41 status-200 non-image rows, and 2 valid status-200 image rows. The two valid image rows are `ss1314.jpg` and `ss1336.jpg`; their payloads are already accepted as late supplements. The accepted inventory reports zero new candidates, and the local candidate audit explicitly records that no URL was guessed, downloaded, replayed, or integrated.

The only saved first-hop redirect probe is the exact original `http://www.worldofwarcraft.com/downloads/ssotd/images/screens/ss1057-thumb.jpg` at capture `20101227014645`. Its CDX row is status `301`, MIME `text/html`, digest `EHJDW7RFCFWMSQBGL67RQNFHDIQOHYZG`, and indexed length `594`. The saved source response is also `301 Moved Permanently`, `text/html; charset=iso-8859-1`, 242 bytes. Its `Location` is:

```text
https://web.archive.org/web/20101227014645id_/http://us.battle.net/wow/en/media/
```

The raw HTML names the same destination. Automatic redirect following and manual follow hops were both zero. The saved acceptance classifies this as a historical redirect to a generic Battle.net media portal, with zero recovered payloads. The portal is a traceable destination candidate, not an image URL or a CDN proof.

The offline SSOTD source text gives a separate native-gallery rule. [`index.html`](../../../../.scratch/offline-navigation-20261015-v15/site/downloads/ssotd/index.html) lines 63–83 send a HEAD request to `anachronos.xml`, derive a screenshot number, and call `addshots("/downloads/ssotd/images/screens", "ss", currentShotNumber)`. [`ssotd-screenie.js`](../../../../.scratch/offline-navigation-20261015-v15/site/new-hp/js/ssotd-screenie.js) lines 432–468 construct `/downloads/ssotd/images/screens/ssN.jpg` and derive `-thumb.jpg` paths. These lines name the native WoW origin path; they do not name a CDN hostname. The only explicit external media destination in the saved evidence is the historical `us.battle.net/wow/en/media/` Location above.

The traceable next target is therefore the exact `ss1057-thumb.jpg` redirect record. If a future network window is explicitly authorized, query the exact recorded original and record any first-hop Location without automatic follow. A later image can enter a source map only after exact CDX timestamp/digest/length agreement, replay HTTP 200, image MIME and magic validation, decoding, and byte provenance. A generic portal Location must never be converted into a guessed image path.

Native SSOTD entities stay separate from static news overlays and from the 3368-entity dynamic-gallery scope. Full and thumbnail paths remain separate. Redirect, revisit, HTML, empty-index, and transport-failure rows remain evidence states rather than recovered payloads. The machine-readable evidence, hashes, line references, and target classes are in [`media-redirect-target-plan.json`](media-redirect-target-plan.json).

The plan does not modify v27 output, v26 files, native gallery maps, or exporter tools.
