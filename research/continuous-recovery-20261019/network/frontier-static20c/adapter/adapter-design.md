# frontier-static20c adapter design

The packet imports the SHA-pinned reusable-image V3 driver and changes only the imported module's in-memory `NETWORK` guard to `research/continuous-recovery-20261019/network`. The frozen
driver file is unchanged.

The fixed adapter accepts exactly `--fixture` or `--execute`; it accepts no plan, URL, output, or
receipt path arguments. Fixture mode calls the frozen `run_fixtures` entrypoint and produced 32/32
passes with zero network requests. Execute mode requires the packet plan, bindings, the latest
`root-frontier-news16b-source-acceptance.json` tail-zero receipt, historical CONTROL03, and a
separate root GO receipt. It checks an empty output directory and a 960-second parent watchdog
window before calling the frozen `execute` entrypoint.

The packet requests r2 shortlist ranks 41..60. Ranks 41..57 have frozen Source15 page hashes and
v33 marker lines and are prepared as the 17-candidate execution slice. Ranks 58..60 are retained
in the selection audit but excluded because their related-origin CSS source page has no frozen
source path/hash; no citation is invented. Each candidate uses fresh exact CDX first,
then at most two distinct digest replays, with identity variants retained but never replayed. The
offline dedupe audit found no exact match in execution/report/CDX surfaces; browser missing-image
overlays and plan/queue records remain explicitly excluded from execution evidence.

Policy is bounded at 80 attempts, 900 seconds, 32 MiB total, 8 MiB per entity, 5.25 second
dispatch cadence, 5.0 second request-start cadence, TLS verification, no redirects, direct-first
then batch proxy, and the frozen disk/429/503/five-failure stop rules. No automatic GO, pagination,
retry, or follow-up batch is implemented.

The frozen driver identity fixture assumes its first synthetic candidate is HTTP so it can test
default-port and scheme-variant classification. Because this packet begins with the exact HTTPS
rank 41, fixture mode temporarily seeds only that synthetic fixture with exact HTTP rank 46 via a
local `patch.object` loader; execution always uses the unchanged 17-candidate plan and strict
HTTP/HTTPS identity policy.
