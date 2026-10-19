# v37 browser preparation r1

This is a preparation-only harness for the already-built
`.scratch/pages-resources-20261019-v37` output. It has not opened a browser,
started a server, or made a request.

Coverage is limited to the 21 new primary images and the real Toplist page:

- `news/wow-news2004.html`: each accepted image is probed from the loopback
  server and compared with v37 provenance bytes. The page is inspected for
  the real `<img>` element, natural dimensions, decode state, and computed
  visibility. Hidden DOM is not revealed and no toggle is invented.
- `toplist/index.html`: original Prototype/logic script loads, `window.onload`
  initialization, default `body.wide`, existing ranking/navigation content,
  and the `body.wide a.next` / `body.wide a.prev` CSS candidates. A CSS image
  counts only when a real visible element has a local decoded background;
  declaration-only and commented `lion-top` rows remain pending/excluded.

The loopback server serves only the promoted v37 output with correct HTML,
XML, HTM, JS, CSS, and image MIME types. Playwright aborts non-loopback
requests and records them. The runner has a 300-second hard subprocess limit,
requires `--go --root-browser-go`, and refuses to run until root supplies
`publication/root-v37-browser-execute-go.json` with bindings for the plan,
harness, runner, and native-input file. It writes only `results/`,
`screenshots-r1/`, and the run receipt after that GO. There is no automatic
retry.

Planned command (do not run until root review/GO):

```text
C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 research/continuous-recovery-20261019/integration/v37/browser/execute_v37_browser.py --go --root-browser-go
```
