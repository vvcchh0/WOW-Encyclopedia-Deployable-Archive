# frontier-news04 adapter

This adapter is a fixed-path compatibility boundary for the unchanged V3
driver. It imports
`research/continuous-recovery-20261018/network/reusable-image-driver-v3/reusable_image_driver.py`
and verifies its SHA before loading it. The only runtime adaptation is an
in-memory assignment of the imported module's `NETWORK` global to
`research/continuous-recovery-20261019/network`; no driver source is copied or
edited.

The adapter accepts exactly one of these commands:

```text
python -X utf8 research/continuous-recovery-20261019/network/frontier-news04/adapter/frontier_news04_adapter.py --fixture
python -X utf8 research/continuous-recovery-20261019/network/frontier-news04/adapter/frontier_news04_adapter.py --execute
```

Both commands use the fixed `frontier-news04/plan.json`,
`frontier-news04/input-bindings.json`, and `frontier-news04/output` paths. No
path, URL, plan, or output override is accepted. Fixture mode writes only the
new `adapter/fixture-results.json`. Execute mode requires the independent root
receipt `research/continuous-recovery-20261019/publication/root-frontier-news04-execute-go.json`,
checks its plan/driver/adapter hashes, verifies the bound source tail and
CONTROL03 gate, rejects nonempty output, and rejects startup when fewer than
300 seconds remain before `2026-10-19T13:15:00Z`.

The packet remains unchanged: four exact originals, CDX first, up to two frozen
distinct-digest replay candidates per target, `max_attempts=16`, 240 seconds,
16 MiB total, 8 MiB per entity, TLS, no redirects, direct-first process proxy,
cadence, disk-floor, and 429/503/failure-tail stops. The adapter adds no source,
fallback, retry, or budget policy.

No network operation is performed by fixture mode. Execute is intentionally
refused until root writes the fixed GO receipt.
