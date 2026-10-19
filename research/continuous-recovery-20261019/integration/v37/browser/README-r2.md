# v37 browser preparation r2

This r2 plan binds the completed v37 output while retaining r1 unchanged. No browser or network request has been made.

- Plan: `research/continuous-recovery-20261019/integration/v37/v37-browser-plan-r2.json` (SHA-256 `379d9d84c3a9c74cdd385409eaad161cfc931d54cda0d2f890839ef9e8299ea2`)
- Output provenance: `.scratch/pages-resources-20261019-v37/export-provenance.json` (SHA-256 `595ee130b42be7caa2bd6dba4477f163368ec823aed7830e2c844bd333b3f065`)
- Build receipt: `research/continuous-recovery-20261019/integration/v37/v37-build-receipt.json` (SHA-256 `d80b8ac1e8aa8a14d2b73b76e1ea220cc1dd478b03ddb6501cda6d0f5d583d4e`)
- Scope: 21 new news images, Toplist page, two CSS candidates, zero native toggles.

The additive r2 harness `check_v37_images_toplist_r2.cjs` probes all 21 exact output bytes and asserts HTTP status, MIME, length, SHA, and expected natural dimensions. A news row passes DOM coverage only when the real element is visible, complete, decoded, and has positive expected dimensions. The harness records `typeof window.Prototype`, `Prototype.Version`, `typeof init`, `body.wide`, current `document.spells` data, visible containers, error text, and real navigation. If a visible `body.wide a.next` exists it performs one real next-to-prev sequence; otherwise navigation remains pending without synthetic controls. CSS candidates always receive a local GET/decode check, while visibility is reported separately. Hidden/unmatched rows and absent ranking data remain explicit pending assertions; a zero-error run is never promoted to overall pass when pending rows remain.

The r2 Python runner `execute_v37_browser_r2.py` requires a separate accepted root browser GO gate and enforces a 300-second hard subprocess timeout. It writes only `results/v37-browser-r2.json`, `v37-browser-run-receipt-r2.json`, and `screenshots-r2/` after GO.

Planned command (root review/GO required):

```text
C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 research/continuous-recovery-20261019/integration/v37/browser/execute_v37_browser_r2.py --go --root-browser-go
```
