# v35 new-image browser preparation

This folder prepares the bounded browser check for the 24 root-accepted v35
news images. It does not start a server or browser during preparation. The
future run uses only the promoted
`.scratch/pages-resources-20261019-v35` tree, with a loopback server and
Playwright's external-request abort route.

The accepted R2 input has 23 static `postContainer` references from
`wow-news2004.html` and one native news entry from
`rss-10-2007.xml` (`news10-15-07-904`). The static page is checked by exact
output path, HTTP bytes/SHA, natural dimensions, decoding, and computed
visibility. The Beowulf entry is checked through its original visible
`.hoverContainer` toggle: the harness records the class transition and leaves
the entry expanded before checking its image. No hidden element is promoted to
visible for the test.

The server maps `.htm` to `text/html; charset=utf-8`, as in the accepted v34
menu check. It records image response length/SHA/MIME, console messages,
page errors, failed requests, server errors, and every blocked external URL.
The result is accepted only if all 24 targets are exact, the native toggle was
clicked, external requests are zero, and no page/request/server errors occur.

Execution is root-gated and hard-bounded:

```powershell
& 'C:\Program Files\Python311\python.exe' -X utf8 `
  research/continuous-recovery-20261019/integration/v35/browser/execute_v35_browser.py `
  --go --root-browser-go
```

The Python wrapper uses `subprocess.run(..., timeout=300)` for the Node
harness and refuses existing result/receipt files. It also verifies every
frozen binding and the promoted v35 provenance before starting Playwright.
