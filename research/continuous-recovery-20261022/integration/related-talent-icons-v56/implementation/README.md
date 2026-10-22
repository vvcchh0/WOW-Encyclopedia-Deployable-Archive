# v56 browser acceptance harness

Run after the v56 export is complete and a loopback-only server serves that export:

```powershell
node research/continuous-recovery-20261022/integration/related-talent-icons-v56/implementation/browser-check.cjs 24786 .scratch/pages-resources-20261022-v56
```

The script checks the nine selected canonical talents, 18 pinned JPEG routes, their actual browser responses, original class-data tooltips, legal rank allocation through the page handlers, and saved-link reloads. It also verifies that v56 preserves the v55 catalog prefix and that the five class-data responses still match the v55 derived bytes; Source16 raw hashes are recorded separately from derived response hashes.

It only continues same-origin loopback requests and aborts off-origin requests. It does not fulfill or replace responses or edit talent data. `--preflight-only` checks the export tree without launching Chrome. Each run writes a timestamped receipt and screenshots under `implementation/runs/v56/`. The 390 known baseline missing targets are reported separately from new errors.

The harness is prepared for root execution; a syntax check or preflight does not establish Chrome acceptance.
