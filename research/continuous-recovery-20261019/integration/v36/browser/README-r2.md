# v36 browser preparation r2

This r2 is an isolated correction of the prepared r1 harness. The r1 files
remain byte-preserved and are not overwritten. No browser, server, or network
execution has occurred.

The r2 entry point is:

```text
C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 research/continuous-recovery-20261019/integration/v36/browser/execute_v36_browser_r2.py --go --root-browser-go
```

The runner uses the same frozen parent plan
`../v36-browser-plan-r1.json`, the same v36 provenance, and the same 51/53
coverage. It writes only `results/v36-browser-r2.json`,
`v36-browser-run-receipt-r2.json`, and `screenshots-r2/`; all three are absent
until root authorizes execution. The single child process has a hard 300-second
timeout and the loopback server still aborts every external request.

Two r2 corrections are bounded to the harness:

1. Stylesheet pages are found only when an actual HTML `<link>` has a
   `rel` token of `stylesheet` and its resolved href equals the target CSS
   route. Candidate HTML is limited to the corresponding top-level site
   section (`/toplist/` or `/pvp/`), which includes parent pages such as
   `toplist/index.html`. Arbitrary basename text no longer counts as a CSS
   reference. If no real link exists, the CSS target remains pending.
2. Background screenshots use a unique filename derived from the real output
   page path. Before capture, the harness scrolls the actual matching image or
   computed-background element into view without changing display/visibility.

The r2 harness remains strict about `text_literal` and CSS rows: it records
real DOM/computed-style facts, never injects a synthetic visual element, and
keeps unmatched or hidden rows as explicit pending results.
