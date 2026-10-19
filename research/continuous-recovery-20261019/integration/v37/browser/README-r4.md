# v37 browser preparation r4

R4 preserves the failed r3 attempt and changes only the harness initialization
bug and output identity. `parseArgs` now uses `path.dirname(BROWSER_DIR)` for
the frozen plan containment check; r4 writes only `results/v37-browser-r4.json`
and `screenshots-r4/`. The CSS exact-path and exact-computed-background checks
from r3 are unchanged.

The real no-browser preflight is:

```text
C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe research/continuous-recovery-20261019/integration/v37/browser/check_v37_images_toplist_r4.cjs --preflight
```

It validates the frozen r2 plan and resolves absolute input, result, and
screenshot paths without starting a browser, server, or network request. The
actual r4 execution remains root-gated with a 300-second timeout:

```text
C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 research/continuous-recovery-20261019/integration/v37/browser/execute_v37_browser_r4.py --go --root-browser-go
```
