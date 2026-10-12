# Wayback backup tool

`wayback_backup.py` consumes a finite plan and preserves the original HTTP
entity bytes returned by a Wayback identity replay. It does not crawl links,
execute downloaded content, or call Firecrawl.

Example:

```powershell
python tools/wayback_backup.py `
  --plan plan.json `
  --out backups/run-20101203214958 `
  --budget-root D:\WOW_Encyclopedia `
  --max-bytes 14000000000 `
  --min-free-bytes 10737418240 `
  --max-requests 120
```

The plan is finite and contains an anchor plus explicit items:

```json
{
  "anchor_timestamp": "20101203214958",
  "items": [
    {
      "original": "http://www.worldofwarcraft.com/info/encyclopedia/index.xml",
      "timestamp": "20101203214958",
      "role": "core"
    }
  ]
}
```

Only `http` and `https` originals whose host is `worldofwarcraft.com` or
`blizzard.com` (or a subdomain) are accepted. Every request starts as
`https://web.archive.org/web/{timestamp}id_/{original}`. Redirects are allowed
only while the redirect target remains HTTPS on `web.archive.org`; an external
or HTTP final URL is rejected. HTTP status other than 200 and known Wayback
error-page markers are failures even when the server returns an HTML page with
status 200.

An HTTP 200 only means that an entity was preserved; it does not establish
that an image is usable. For shared-image batches, run
`tools/validate_shared_content.py` after the download. The derived
`content-validation.json` checks ZIP CRC/SHA/length references, detects JPEG,
GIF, PNG, SWF and WebP magic, and rejects origin HTML soft404 titles such as
`World of Warcraft - 404 File Not Found` without changing the original
manifest or ZIP evidence.

`manifest.jsonl` status `success` means that the HTTP entity was preserved; it
does not mean that the logical resource is content-valid. An origin soft404 or
an HTML guide replay can return HTTP 200 and is retained in the ZIP as
evidence. Use the `content-validation.json` and the `preservation-index.json`
validity overlays to decide whether an image or other typed resource is usable;
keep the preserved error entity for audit and recovery decisions.

Each item gets at most two network attempts. `--max-requests` limits the total
number of network attempts, including retries. If it is omitted, the finite
plan size supplies a bound of two attempts per item. Network failures, HTTP
429, and HTTP 5xx failures are retried once. Retries use a short delay by
default; a `Retry-After` response is honored for 429 up to 30 seconds. The
delay can be adjusted with `--retry-delay-seconds`. Three consecutive
item-level site failures stop the run. `--deadline-seconds` adds an optional
wall-clock deadline.

Successful entities are buffered up to `--max-object-bytes` (64 MiB by
default), SHA-256 hashed, and written once as `objects/sha256.bin` inside
`objects-0001.zip`, `objects-0002.zip`, and so on. Volumes use
`ZIP_DEFLATED` with `allowZip64=True` and target 64 MiB or 100 objects; a
single object may exceed a very small custom target because ZIP headers are
also stored. No uncompressed object copy is created on disk. A repeated
payload reuses the existing ZIP entry while each URL/timestamp relationship
is retained in the manifest.

`--budget-root` is the complete tree charged against `--max-bytes`; pass the
workspace root (`D:\WOW_Encyclopedia` in this checkout), rather than only the
backup output directory, when research files and backups share one budget.
Every decoded response chunk and every planned ZIP/metadata write checks the
tree size and free space. `--reserve-bytes` (64 MiB by default) is charged as
additional safety headroom. The free-space check is made on the filesystem
containing `--budget-root`, so an explicit `--budget-root` is recommended.

The output files are:

* `manifest.jsonl`: one success or failure record per item attempted in this
  run, including source URL, requested and actual timestamps, final URL,
  case-insensitive `Memento-Datetime`, response headers, status, SHA-256,
  entity length, ZIP part and entry. `timestamp_drift` explicitly reports
  whether the actual Memento timestamp differs from the requested timestamp.
  Resumed successes are recorded with
  `skipped: true` and `skip_reason: "verified_existing"`.
* `errors.jsonl`: failure records and attempt details, including short error
  body previews where useful.
* `summary.json`: counts, byte totals, limits, stop reason, failed items and
  missing items.
* `objects-*.zip`: compressed payload volumes.

On startup every managed ZIP is CRC-checked and every SHA-named object is
rehashed. Every prior successful manifest record must point to an existing
entry with matching SHA and length. A malformed manifest, missing entry,
corrupt ZIP, duplicate SHA object, or mismatched reference stops recovery with
an error; corrupt volumes are never silently skipped. Appending with Python's
`zipfile` rewrites the central directory in the last volume. A crash during
that rewrite can leave the volume unreadable; the next run fails loudly so the
volume can be restored from a filesystem snapshot or removed deliberately.
An orphan ZIP entry from a crash after ZIP close but before manifest append is
validated but is not treated as a logical URL mapping.

The tool uses only Python 3.11 standard-library modules. It writes no remote
scripts and must be run with a finite plan and a bounded request count or the
finite plan default. The repository tests use injected offline fetchers and do
not perform network downloads. After a bounded batch stops, the
`tools/build_shared_recovery_plan.py` helper can derive a new plan containing
only items without verified success records while preserving each source plan
and target output group. Run a derived group only with a healthy connection and
bounded retry; acquisition is user-authorized.

## Derived offline browsing site

`offline_mirror.py` builds a separate, derived browsing tree from the verified
2008 source export. It never contacts the network and never changes the source
files, ZIPs, or manifests:

```powershell
python tools/offline_mirror.py build
python tools/offline_mirror.py serve --host 127.0.0.1 --port 8765
```

An additional validated local files map can be layered without editing the
primary map by repeating `--extra-map path/to/map.json`.  Its `files` records
use `logical_url` (or `original`), `local_path`, and the recorded `mime`; a
present `sha256` is checked and a missing digest is computed and marked as
inferred.  Existing primary routes win collisions, and skipped or loaded
extra records are listed in `build-manifest.json`.  A mapped domain-root
entity is materialized as `/index.html` and becomes the `/` alias, while the
explicit encyclopedia route remains `/info/encyclopedia/index.xml`.

The build writes `offline/site/` and `offline/build-manifest.json`. The original
URL paths are retained, including `.xml` encyclopedia pages. Pages whose source
map MIME is `text/html` are served as HTML even when their historical filename
ends in `.xml`; the original XML stylesheet processing instruction is handled
only in the derived copy. Every derived file records its source SHA-256 and the
transformation reason. The one valid late `menu.xml` is included only as an
explicitly marked reconstruction supplement.

Known same-site resources are rewritten to local paths. Missing or invalid
image entities use a visible local placeholder; missing pages and scripts use
local placeholders, and preserved HTML error entities are never used as images.
If `offline/support/compat.js` and `compat.css` exist, the build copies and
injects them at `/__offline/compat.js` and `/__offline/compat.css`. The server
binds to loopback, rejects traversal, applies a self-only CSP with the legacy
inline/eval allowances needed by the archived menu, and exposes
`/__offline/api/url-map` and `/__offline/api/log` for acceptance checks. It
does not fetch uncollected routes.

## 2008 source integration and export

`build_2008_preservation.py` runs offline. It combines the final 2008 core and
dependency plans, original manifests, explicit source catalogs, and CDX-verified
payload reuse. It validates ZIP objects and separates usable historical entities,
late supplements, origin error bodies, and missing files. A finished older batch
does not close newly discovered unattempted URLs. Interrupted batches retain their
original summary and use an explicit `termination.json` sidecar when superseded.
The IE completion batch has a custom five-item preservation summary. Its separate
`completion.json` records a local terminal verification bound to the manifest,
summary and ZIP hashes; it does not invent an original downloader finish time.

```powershell
python tools/build_2008_preservation.py
python tools/build_2008_preservation.py --export
python tools/verify_2008_export.py
python research/acquisition-2008/acceptance/audit_dependency_closure.py
```

The optional export writes unchanged preferred entities to `mirror/20080512/`
and records source MIME, actual capture date, historical CDX proof, SHA-256, and
byte length in `url-map.json`. It checks space, path containment, and Windows
case collisions, and refuses to replace differing existing files or mappings.
The `.xml` article names contain HTML entities served as `text/html`; a future
local server must use the recorded MIME. This export does not rewrite links or
establish that the site works offline.

`verify_2008_images.py` adds full raster-image structure and pixel decoding to
the source and ZIP checks. It requires Pillow; the acquisition tools themselves
remain stdlib-only. In this environment it is run using the bundled runtime:

```powershell
& 'C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools/verify_2008_images.py
```

The checker reads the exported mapping and changes no image. Flash and legacy IE
behavior components are preserved as source; they are not executed by validation.

After the final report and export are reviewed,
`python packaging/package_reassessment.py --full-2008` creates the new full source ZIP,
checks every member against its source SHA-256, and verifies that the two earlier
packages remain unchanged. The report and package verification file state known
archival gaps; a full acquisition scope does not imply zero missing resources.
