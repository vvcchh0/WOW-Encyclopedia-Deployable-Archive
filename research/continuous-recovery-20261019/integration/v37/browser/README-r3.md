# v37 browser preparation r3

This is an additive preparation revision. The r1 and r2 harnesses, runners,
receipts, and planned output paths remain unchanged. No browser, server, or
network request has been run for r3.

The r3 runner continues to bind the frozen r2 browser plan
`research/continuous-recovery-20261019/integration/v37/v37-browser-plan-r2.json`
and the completed v37 provenance. It writes only the r3-named result, run
receipt, and `screenshots-r3/` after a separate root browser GO gate.

The CSS check now maps a source target such as
`http://www.worldofwarcraft.com/toplist/images/en/next-wide.gif` to the
derived project-relative path `toplist/images/en/next-wide.gif`. It scans the
actual derived `styles-en.css` URL tokens and requires an exact project path
match; a `missing-image.svg?requested=...` token or a basename match cannot
satisfy this check. Computed backgrounds are likewise accepted only when a
visible candidate contains the same exact canonical target path. Local GET,
MIME, length, SHA, and image decode remain separate evidence, and missing
exact CSS assets or hidden/data-only rows remain explicit pending findings.

The r3 files were syntax-checked only:

```text
C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe --check research/continuous-recovery-20261019/integration/v37/browser/check_v37_images_toplist_r3.cjs
C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 -m py_compile research/continuous-recovery-20261019/integration/v37/browser/execute_v37_browser_r3.py
```

The planned command remains root-gated and must not be run from this
preparation step:

```text
C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 research/continuous-recovery-20261019/integration/v37/browser/execute_v37_browser_r3.py --go --root-browser-go
```
