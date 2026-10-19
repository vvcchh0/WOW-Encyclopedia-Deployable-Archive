# v35 browser preparation record

Prepared-only state; no Node, HTTP server, Playwright, or external request was
run. The promoted output is `.scratch/pages-resources-20261019-v35` and is
bound to provenance SHA
`f37f73ba4cdd63b1190b895a2d770dd94b2b764ad5fc219a5fd34bad93a3c4d0`.

The input is `v35-browser-input.json` (SHA-256
`98aa5f0dfad8cc249c5c8c3180ca3714b4054aaea54025dcfdb5ac4db4bcd8c3`). It
binds the accepted R2 native input, v35 primary map, v35 finalization check,
correct root v35 gate, and root's accepted promotion receipt. It contains 23
static targets and one native target (`news10-15-07-904`), with 24 exact image
length/SHA/dimension records.

Prepared implementation SHAs:

- `check_v35_new_images.cjs`: `10f864c20fa548419725e8e5900a7fa39c40f57a96a780d3f749e51b1bfe961b`
- `execute_v35_browser.py`: `a9d7a14ce8d94cbd6989654319a5d917d3639b81114da169dbff5544a0d88453`
- `README.md`: `485c3b19891a7a6ed6667960301d3f688f758fa65c926f60da84d466d5e30538`

Syntax validation passed with the bundled Python and Node runtimes. The
future root-authorized command is:

```powershell
& 'C:\Program Files\Python311\python.exe' -X utf8 `
  research/continuous-recovery-20261019/integration/v35/browser/execute_v35_browser.py `
  --go --root-browser-go
```

The wrapper refuses existing result/receipt files, verifies all five bindings
and promoted provenance before launch, and uses a hard 300-second
`subprocess.run` timeout. The harness uses a loopback-only server, maps `.htm`
to HTML MIME, records blocked external URLs/console/page/request/server
failures, validates all static image DOM facts and HTTP bytes, then clicks the
original Beowulf `.hoverContainer` toggle and restores its expanded state
before checking the native image.

The screenshots are viewport-bounded: the static capture scrolls to the first
new image, and the native capture scrolls to the Beowulf image. No full-page
2004 archive screenshot is produced.
