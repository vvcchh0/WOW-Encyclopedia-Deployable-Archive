# v31 runner preparation

`execute_v31.py` is a gate-only export wrapper. It does not prepare or rewrite
the frozen v31 maps. A future run must use:

```text
python.exe -X utf8 research/continuous-recovery-20261018/integration/v31/execute_v31.py --go --root-export-go
```

The wrapper requires `publication/root-v31-input-acceptance.json` with
`accepted: true`, `preflight_sha256` matching the frozen v31 preflight, 49
root-accepted public copies totaling 480639 bytes, complete SHA bindings for
the runner, builder, maps, preflight/audits, v30 closure, source manifest,
accepted tool supersessions, and runtime-impact receipt, plus
`network_requests: 0` and `export_executed: false`. It rejects an existing
v31 output, partial output, or build receipt and checks the D: free-space
floor before and immediately before the exporter call.

The frozen v30 closure remains 247 primary, 89 supplement, and 336 total
overlay records. v31 adds 49 primary news assets and no new supplement
assets, giving expected 296/89/385 overlays, 8843 declared files, and 8844
actual files. The exporter pin is the root-accepted
`7c3684fb777e9c21b07fe8c8a1be0418810f448e99dd582ed4c9d9c342764dea`; the
historical exhibits pin remains
`35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011`.

No v31 export or publication was performed while preparing this runner.
