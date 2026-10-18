# v30 export wrapper preparation

`execute_v30.py` is the only v30 export entry point. It is prepared but has
not been run. Its final SHA-256 is
`5e8524f73c58efeff117fba21ffa5e04233aa9afd81b6c5146b8bec7922fc2db`.

The wrapper requires both `--go` and `--root-export-go`, a root input receipt
at `research/continuous-recovery-20261018/publication/root-v30-input-acceptance.json`
with `accepted: true`, the unified `map_bindings` and `preflight_sha256` fields,
the accepted 33 public image copies (156857 bytes), zero network requests, and
no prior export. It verifies matching SHA bindings for the v30 builder, runner, primary/supplement maps,
impact, source-byte audit, preparation, preflight, frozen v28/v29 closure,
source manifest, current exporter, and historical-exhibits tool. It refuses an
existing v30 output, `.partial` output, or worker receipt, and checks the D:
free-space floor before the single exporter call.

The wrapper does not invoke `build_pages_v30.py --prepare/--preflight` and does
not rewrite any prepared input. On a failed exporter call it preserves the
partial output and writes one failure receipt; it never retries. On success it
expects 8,794 declared / 8,795 actual files, 247 primary overlays, 89
supplement overlays, 336 total overlays, 39 guide images, and 22 previews,
then writes `v30-build-receipt.json`.

The frozen builder is
`f9fbc95042d6f0e4894d280af6de5276db41746ccc6dc0fe5a8e8d3f6b027026` and the
prepared maps/preflight are recorded in `v30-preflight.json`. No export,
network request, map mutation, old-version mutation, commit, or publication
was performed in this preparation.
