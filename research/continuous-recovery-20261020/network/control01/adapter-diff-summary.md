# control01 preparation summary

Prepared 2026-10-20 under the current six-hour recovery window. This packet has made zero network requests.

## Package

- plan: plan.json — SHA-256 e989e8b25af6d17eb60407e93e317b2b525f9731dff92250e20244a9a6ff1bdf, 4707 bytes
- driver: control01_driver.py — SHA-256 ae099cd19401522a9bc59f74262ec5a644450043e49b393d4a1e371e823bdd84, 24801 bytes
- parent watchdog: parent-execute-once.py — SHA-256 e12e8dbf3a92897f22ea10903ae98e05c52b09b727b5f34a9a5bdb0b62f435be, 5142 bytes
- offline fixture: fixture-results.json — SHA-256 fd7d3730308a281e48c457bf393d9cd0e9306f6b05bd878c23a286060707ee98, 831 bytes
- input bindings: input-bindings.json — SHA-256 684574f956edb528f25dd9de6a74f06a6cb65fe3e134c5df0e147ce149666a4b, 2499 bytes

## Deliberate differences from the frozen 2026-10-19 control

- New batch identity CONTROL-01-20261020, current-day paths/schemas, and GO path research/continuous-recovery-20261020/publication/root-control01-execute-go.json.
- Schedule is bound to run start 2026-10-20T08:33:22Z, network cutoff 2026-10-20T13:15:00Z, and deadline 2026-10-20T14:33:22Z; both driver and parent watchdog refuse execution outside it.
- Latest failure is rebound to the actual private report SHA 3638dc60ad3c2d68512260206c8519683b8622d7b619d5d9a8c5e9e26b50786c and current source-acceptance SHA 6556a52a0526814c26af1aa7e78d315284dd47add637cdb9c96736cdad71c78a, with final proxy status 429 at 2026-10-19T11:54:01.282450Z.
- The exact original, CDX field set/date range, frozen parser SHA 85457ea1baa96c474e33ffc01210b4f6d96b3d6d276dc7a2b56aff3cd8376530, direct-first transport order, proxy address, TLS verification, two-request cap, 120-second child cap, 180-second parent watchdog, 1 MiB body caps, cadence, disk floor, stop codes, no replay/pagination/redirects remain bounded as accepted.

No raw HTTP, cookies, image payloads, old receipts, publication files, or source files were copied or changed.

## Offline evidence and pending gate

fixture-results.json has 14/14 cases passed, reports zero network requests and no raw output; its timestamp is the actual fixture run time. The fixture is deliberately not self-bound in input-bindings.json. offline-validation.json records the successful fixture, read-only binding validation, and Python syntax compilation. Network execution is pending the separately written root GO and must not start from this package until the parent explicitly reviews and accepts the hash bindings.
