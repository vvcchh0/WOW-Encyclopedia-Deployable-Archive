# Navigation70 v32 offline plan factory

`prepare_navigation70.py` is a local-only factory for the frozen
`publication/navigation-link-selected70.json` queue.  It validates the queue
SHA, every primary and alternate citation file/line/hash, the current accepted
source receipt and the current CONTROL03 gate.  It then prepares one batch of
ten exact originals with the reusable-image-v3 contract.  Alternate navigation
links remain provenance context; they are never merged into a candidate's
same-original `all_references`.

The factory does not perform CDX requests, replay requests, driver execution,
image downloads, or publication.  A future invocation must name one batch and
will refuse an existing batch directory:

```powershell
& "C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -X utf8 `
  research/continuous-recovery-20261018/network/navigation70-v32/prepare_navigation70.py `
  --batch-index 1
```

The seven batches are ranks 1–10, 11–20, through 61–70.  The first ten are,
in order, `07-08/ss01.jpg`, `ss02.jpg`, `tcg01.jpg`, `tcg02.jpg`, `tcg03.jpg`,
`wow-bc.jpg`, `07-07/comic-full.jpg`, `07-11/comic1.jpg`, `comic2.jpg`, and
`info/basics/images/trade/ss01.jpg`.

Each future plan uses the frozen exact window
`20000101000000..20080512210044`, 24 attempts in 240 seconds, 16 MiB total and
8 MiB per entity, 5.25-second dispatch and 5-second start cadence, TLS with no
automatic redirects, direct-first `4` / proxy `20` transport budget, and a
120-second 429/503 cooldown.  The disk floor is 11,005,853,696 bytes.  The
factory records the current source receipt, current failure tail and CONTROL03
receipt at invocation; those bindings are audit inputs and do not authorize
network execution.  Parent GO remains required.

JSON plans and the batch-local status snapshot are serialized as explicit
UTF-8 bytes with LF line endings.  This keeps precomputed SHA-256 and byte
length bindings identical to the files written on Windows.  Batch temporary
and target paths are resolved and checked to remain below this factory before
the atomic rename or failure cleanup; an existing batch remains immutable.

`test_prepare_navigation70.py` is an offline unittest module.  It reads the
real frozen queue and citations, tests batch bounds, duplicate detection,
credential/query rejection, closed-gate/cooldown refusal, and existing-batch
refusal.  Its atomic fixture verifies actual plan and snapshot bytes against
their bindings and rejects an escaping document safely.  It does not call
`main`, create a real plan, or contact the network.
