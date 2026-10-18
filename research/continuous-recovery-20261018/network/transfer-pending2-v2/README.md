# transfer-pending2-v2 offline preparation

This directory prepares one bounded retry batch for two exact image originals
that have no accepted payload. It performs no HTTP, does not invoke the
reusable image driver, and refuses to overwrite an existing batch directory.

The immutable v2 queue retains the source page, exact line, page SHA, prior
plan and prior attempt receipt for each target:

| rank | original | source citation | prior result |
| --- | --- | --- | --- |
| 1 | `http://www.worldofwarcraft.com/news/images/08-02/02-06-08-3.jpg` | `.scratch/pages-resources-20261016-v25/news/rss-02-2008.xml.html:3338`, SHA `63b9ac73b8d146ed735b0ed08ed187a979235a5f9a0296cae5699d8564ded81f` | prior exact-CDX transport failure: curl 35, no source status, zero body; no replay |
| 2 | `http://www.worldofwarcraft.com/news/images/05-02/EU2.jpg` | `.scratch/pages-resources-20261018-v30/news/wow-news2005.html:2027`, SHA `3d4935a1d6fb6d33408cda74945a5f2584128cd574feae0f4340814c5055724e` | prior replay partial: source status 200, curl 28, 489580-byte partial body; no accepted image |

Both source lines bind the requested URL in URL-encoded form. The queue also
binds prior plan, source acceptance, output state and cache-status hashes; the
targets are not treated as 404 or complete-empty results.

The plan selects exactly two queue rows. Its `candidate_count` remains 2, but
`policy.max_originals` is 20 because that is a fixed contract enforced by the
frozen reusable-image driver. The retry bounds remain 8 requests in 100
seconds, 8 MiB total body, and 4 MiB per entity, with direct-first/proxy
fallback, TLS verification, no redirects, cadence and disk-floor checks, and
the existing 429/503 and five-failure stop rules.

The plan uses the immutable frozen driver at
`research/continuous-recovery-20261018/network/reusable-image-driver-v3/reusable_image_driver.py`
(SHA `4a19422f0dd8e2f7e1ffdd088836c7ab80450afb91aeedc6cdb94fa4c6bfe955`).
The factory reads the current recovery `status.json`, latest accepted source
receipt and `latest_control_gate` at invocation time, then writes an immutable
batch-local status snapshot. A future parent GO must precede any driver
execution.

The factory writes canonical UTF-8/LF JSON to a sibling temporary directory,
checks containment and disk space, and atomically renames the complete batch.
It refuses an existing batch, an active cooldown, a closed resume gate, driver
SHA drift, URL credentials/queries/fragments/non-default ports, citation drift,
or an escape path.

Offline validation:

```powershell
& 'C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -m unittest discover -s research/continuous-recovery-20261018/network/transfer-pending2-v2 -p 'test_*.py' -v
```

The tests validate the frozen queue citations, prior failure classifications,
dynamic source/control bindings, policy limits, canonical LF bytes and
SHA/size bindings from a temporary atomic fixture, containment refusal, and an
actual import/configure/`load_and_validate_inputs()` call on the frozen driver.
That loader check is offline and does not enter the driver's HTTP execution
path.