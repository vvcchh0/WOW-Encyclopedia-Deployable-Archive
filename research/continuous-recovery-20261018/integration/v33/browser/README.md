# v33 browser delta preparation

`prepare_v33_browser.py` is an offline, read-only preparer. It refuses to
run until the root source-receipts manifest, v33 maps, completed v33 output,
v33 provenance, impact/audit files, and the frozen v32 browser baseline are
present. It derives source-page routes and reference classes from the v15
manifest, including the exact `popUpOmega` image argument, and records all
old-plus-new recovery references from the v33 impact estimate. It does not
scan pending folders, issue requests, launch a browser, or regenerate maps.

The resulting `v33-browser-input.json` is immutable. It binds every source,
map, provenance, baseline, exporter, and checker file by SHA-256. Root must
write an accepted `publication/root-v33-browser-input-acceptance.json` that
binds this input SHA before the checker can run.

`check_v33_browser.cjs` is a one-shot bounded Playwright checker. It requires
both `--go` and `--root-browser-go`, refuses an existing result, starts an
ephemeral loopback server over the v33 output only, aborts external requests,
checks exact bytes/MIME/dimensions, clicks every derived full-size popup link,
checks unique ordinary image hrefs, and records visible versus CSS
declaration-only static targets. It captures representative arena and
Silvermoon screenshots and writes one immutable result under this directory.
No v32 baseline browser suite is rerun.

Preparation (only after root's v33 output exists):

```powershell
& "$env:CODEX_PRIMARY_PYTHON" -X utf8 integration/v33/browser/prepare_v33_browser.py --prepare
```

Execution (only after root's browser input gate and explicit GO):

```powershell
node integration/v33/browser/check_v33_browser.cjs --go --root-browser-go
```

The execution command is intentionally not run by preparation work.
