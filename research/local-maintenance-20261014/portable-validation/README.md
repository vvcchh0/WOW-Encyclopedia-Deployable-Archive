# Portable browser bundle QA

This directory owns the independent, one pass QA runner for the 2026-10-14
portable browse package. It is prepared before the package exists; the runner
must only be invoked after the package producer has published the final ZIP,
its `.sha256` sidecar, the generation JSON report, and the exact v5 source
directory.

Run from `D:\WOW_Encyclopedia` with the fixed local runtimes:

```powershell
C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe `
  research/local-maintenance-20261014/portable-validation/validate_portable_bundle.py `
  --archive artifacts/WOW_Encyclopedia_20080512_browser_20261014_v5.zip `
  --report research/local-maintenance-20261014/portable-package-v5-report.json `
  --source-site .scratch/pages-local-maintenance-20261014-v5 `
  --scratch-root '.scratch/local bundle smoke 20261014 v5' `
  --output 'research/local-maintenance-20261014/portable-validation/v5/portable-bundle-validation-v5.json'
```

The command refuses an existing evidence file or an existing extraction tree.
It verifies the ZIP SHA against the report and sidecar, rejects unsafe member
names and symlink modes, checks the D: free-space reserve, and extracts only
to `.scratch/local bundle smoke 20261014 v5`. The packaged server is then started
from the extracted root with this exact shape:

```text
<isolated-python> -I tools/serve_pages_preview.py --site site --port 0
```

The Python smoke uses an explicit empty proxy handler and loopback-only GET or
HEAD requests. The Node companion starts the supplied Chrome executable with
Playwright's `--disable-client-side-phishing-detection` default removed. Its
six scenarios are old XML with JavaScript on/off, encyclopedia menu and Elune
search, the 390 px JavaScript-off login exhibit, a query-safe unknown 404, and
the socketeditems and dancing Flash metadata pages. External requests and
POST or other non-GET requests are aborted and counted as failures. CSP
`object-src 'none'` messages and the expected unknown-route 404 are recorded
under `expected` separately.

The compact evidence report, run-suffixed browser report, and two run-suffixed
screenshots remain beside the requested output JSON. Output paths may contain
spaces; pass them as one quoted PowerShell argument. A
passing run removes the newly created extraction tree after stopping the
server and browser; pass `--keep-scratch` when the successful extraction is
needed for inspection. A failed run leaves the extraction tree and logs in
place. No retry loop or product repair is built into the runner.
