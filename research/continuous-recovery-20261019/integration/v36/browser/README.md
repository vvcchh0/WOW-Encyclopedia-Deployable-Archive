# v36 browser preparation

This directory contains a prepared, root-gated loopback browser check for the
frozen v36 output. It has not executed a browser, started a server, or made an
HTTP request.

Inputs and scope:

- Plan: `../v36-browser-plan-r1.json` (51 targets, 53 references; the plan
  itself binds the frozen native-input and v36 provenance SHA-256 values).
- Output: `.scratch/pages-resources-20261019-v36`; no source, map, output, or
  receipt is modified by this harness.
- Harness: `check_v36_images.cjs`.
- Runner: `execute_v36_browser.py`; it requires both `--go` and
  `--root-browser-go`, refuses an existing result/receipt, and enforces a
  single `subprocess.run(..., timeout=300)` invocation.
- Future command, only after root GO:

  ```text
  C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 research/continuous-recovery-20261019/integration/v36/browser/execute_v36_browser.py --go --root-browser-go
  ```

The harness serves only `127.0.0.1` with exact output bytes and correct
`.html`, `.htm`, `.xml`, CSS, JavaScript, and raster MIME types. Playwright
aborts every non-loopback request and reports the URL. Each of the 51 raster
targets receives a direct local `Image` decode probe. The real page DOM/CSS is
then inspected by source route: HTML image references require an actual local
`<img>` match; `text_literal` and CSS references require an actual computed
background match; Visa rows require visible historical-exhibit figures.

No hidden DOM is forced visible and no synthetic app interaction is injected.
Unmatched or hidden rows remain `pending_reason` entries in the eventual
result. The six Visa rows additionally audit forms, Flash/object/embed,
mouseover/click controls, and external/business links. Planned screenshots are
absolute paths under `screenshots-r1/`: one news view, one background/style
view, and one Visa exhibit view.

Expected coverage is 35 news static targets, 7 other static targets, 3 CSS
targets, 6 Visa exhibit targets, and zero native toggles. The CSS source input
does not provide a selector/property value for the three CSS targets; the
harness resolves actual stylesheet-linked HTML pages and records computed
selectors/backgrounds, leaving unresolved cases pending rather than guessing.
