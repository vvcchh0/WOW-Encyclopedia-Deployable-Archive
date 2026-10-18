# v32 runner preparation

`execute_v32.py` is export-only. It requires the independent
`research/continuous-recovery-20261018/publication/root-v32-input-acceptance.json`
with `accepted: true`, `preflight_sha256` equal to the frozen v32 preflight,
103 public-copy rows totalling 1,734,198 bytes, every prepared and frozen
binding, `network_requests: 0`, and `export_executed: false`. It also requires
the explicit `--go --root-export-go` pair.

The one export call reuses the frozen v30 map closure and the single v32
primary delta map containing news49 plus next70 (103 items). The empty v32
supplement map is included for schema closure; the frozen v30 supplement maps
remain the source of the 89 supplement overlays. It refuses an existing v32
output, `.partial` directory, or build receipt and checks the D-drive floor
before and immediately before calling `export_pages`.

The planned output is `.scratch/pages-resources-20261018-v32`, with 8,897
declared / 8,898 actual files and 439 overlays. Future popup24 resources are
excluded. A failure after the exporter starts writes one failure receipt and
leaves the partial output for review; it never retries or overwrites a receipt.
