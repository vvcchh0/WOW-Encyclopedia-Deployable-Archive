# GitHub Pages v55 remaining-60 verification

This batch is prepared for exactly the 60 rows in `root-v55-online-partial-acceptance9.json` under `remaining`. The nine rows already verified in `objects` are excluded. The adapter cross-checks both lists against the pinned original 69-object manifest and the accepted v55 export/browser receipts before it writes its plan.

The pinned source receipts are:

- Partial acceptance: `research/continuous-recovery-20261022/root-v55-online-partial-acceptance9.json` (`b31b5918ce9e2dce4d34358924c9997eff55645943e6357c5ebc69b1f1ea40a0`)
- Original 69-object manifest: `research/continuous-recovery-20261022/network/github-pages-v55-changes69/object-manifest.json` (`951ac6924f84fa82710bfd8563ced83627a3012bf030f3cd6833cb9980808f6e`)
- Prior partial-batch public summary: `research/continuous-recovery-20261022/network/github-pages-v55-changes69/runtime/object-match-summary.json` (`656f621ebbd5c4676ff8fd9e525471440d26885b5a0227554a4a249a37f1cfec`)
- Accepted v55 export and browser receipts: `root-v55-export-acceptance.json` (`c5dd21e64d4680dbccaf091ab17302bc2039d3036afc0cbed2f87f1b39517b54`) and `root-v55-browser-acceptance.json` (`2269a96243d24ee3c492258866e9130a16a8f08156177f7dcdc8c38a75bca35e`)

Run only the offline preparation and fixtures with:

```powershell
python -B research/continuous-recovery-20261022/network/github-pages-v55-remaining60/verify_pages_v55_remaining60.py --offline-validate
```

The fixtures exercise all 60 objects through injected mock attempts, including one direct transfer failure followed by proxy success. They verify that a 6.39-second measured interval passes the 5.0-second hard minimum even though it is below the 6.4-second scheduling target, and that 4.99 seconds stops the batch. The offline path does not issue network requests or subprocess calls and removes its isolated temporary runtimes; the production `runtime/` must remain absent.

Execution policy: at most 60 logical objects, 120 HTTP attempts, 1,200 seconds, 64 MiB total response bytes and 64 MiB per object; request timeout 30 seconds; D: free-space floor 11,005,853,696 bytes before and after every request and around batch writes. The adapter passes a 6.4-second cadence target to the hash-pinned v53 transport, whose default remains 6.2 seconds, and independently stops only if the recorded actual interval is below 5.0 seconds. Direct is first; process-local `127.0.0.1:7890` is allowed only after transport failure. TLS verification stays on, redirects and automatic retries stay off. HTTP 429/503 stop with cooldown handling; five consecutive transfer failures stop and preserve their tail/cooldown.

The only production entry point is `--execute --go PATH` with a fresh root GO using schema `wow-root-github-pages-v55-remaining60-go/v1`. It must bind the plan, wrapper, manifest, offline validation, input bindings, both accepted receipts, partial acceptance, original 69-object manifest, prior public summary, shared transport hashes, object-set hash, Pages commit, and Actions run. No GO is included or exercised here.

Execution response bodies, headers, and cookie jars are private under `runtime/private/raw/`. The public summary contains curated URL, status, MIME, byte/hash, transport, timing, match, stop, and disk fields only.
