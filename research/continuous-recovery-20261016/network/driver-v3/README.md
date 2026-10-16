# Gallery prefix driver v3

`gallery_prefix_driver_v3.py` is an execution-ready successor to the frozen GALLERYPREFIX01 driver. It is not a network receipt. The current artifact was run only with `--fixture` and made zero requests.

The cadence fix uses a 5.25 second monotonic scheduling floor, re-reads monotonic time after every sleep, and retains the UTC request-start floor for restart timing checks. The fixture models early sleep return and quantization, a fresh monotonic origin after restart, remaining byte/time caps, and per-request disk-floor recording. The fixture reports the measured dispatch and start minima instead of copying a configured threshold. The restart check covers timing mapping only; execution does not auto-resume a partially written journal.

The driver binds the prepared GALLERYPREFIX02 plan. Its future `--execute` path remains parent-GO gated by the plan and keeps the index-only/no-pagination/no-payload-replay boundary.
