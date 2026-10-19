# frontier-news20f adapter design

The packet imports the SHA-pinned reusable-image V3 driver and changes only the imported module's in-memory `NETWORK` guard to `research/continuous-recovery-20261019/network`. The frozen
driver file is unchanged.

The fixed adapter accepts exactly `--fixture` or `--execute`; it accepts no plan, URL, output, or
receipt path arguments. Fixture mode calls the frozen `run_fixtures` entrypoint and produced 32/32
passes with zero network requests. Execute mode requires the packet plan, bindings, the latest
`root-frontier-news20e-source-acceptance.json` tail-zero receipt, historical CONTROL03, and a
separate root GO receipt. It checks an empty output directory and a 960-second parent watchdog
window before calling the frozen `execute` entrypoint.

The packet contains exactly extension shortlist ranks 101..120. Each candidate uses fresh exact CDX first,
then at most two distinct digest replays, with identity variants retained but never replayed. The
offline dedupe audit found no exact match in execution/report/CDX surfaces; browser missing-image
overlays and plan/queue records remain explicitly excluded from execution evidence.

Expected image format is derived from each exact URL suffix. Top-level `expected_mime` and nested
`expected.mime_types`, `expected.pillow_formats`, `expected.all_gif_frames`, `expected.extension`,
and `expected.format_group` are checked for consistency; the packet summary records counts by format.

Policy is bounded at 80 attempts, 900 seconds, 32 MiB total, 8 MiB per entity, 5.25 second
dispatch cadence, 5.0 second request-start cadence, TLS verification, no redirects, direct-first
then batch proxy, and the frozen disk/429/503/five-failure stop rules. No automatic GO, pagination,
retry, or follow-up batch is implemented.
