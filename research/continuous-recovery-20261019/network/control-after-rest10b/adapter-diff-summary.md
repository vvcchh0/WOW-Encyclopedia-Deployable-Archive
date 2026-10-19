# control-after-rest10b offline packet

This packet is prepared only. It has sent zero network requests and does not
modify the completed `gallery-late-rest10b` batch. The future execution command
is:

```powershell
python -X utf8 parent-execute-once.py
```

The parent wrapper refuses to start until
`publication/root-control-after-rest10b-execute-go.json` is accepted and binds
the plan, driver, fixture, and input-binding hashes. It uses one real
`subprocess.run(timeout=180)` and never resubmits a timeout.

## Exact control endpoint

The packet uses the already successful exact CDX query for
`http://www.worldofwarcraft.com/news/images/08-02/02-14-08-2.jpg`, with the
known 2008-04-02 capture `20080402035201`, `image/jpeg`, digest
`TJ2TFHNGVSA64RRRP3UD2CQZCP4TTRND`, and `limit=10&showResumeKey=true`.
It is a control-only CDX query: no image replay, redirect following, or
pagination. The historical success is evidence for this endpoint; it does not
override the latest 10b 503.

## Packet-local changes

- `control_after_rest10b.py` imports the SHA-pinned frozen `parse_headers` and
  `parse_cdx` functions from the Oct16 control parser.
- It binds the final 10b report (`3a629514...`), root partial acceptance
  (`73cfbbe...`), `resume_gate_passed=false`, terminal 503, and cooldown
  `2026-10-19T10:46:35.479615Z`.
- It allows at most two attempts: direct first, then the process proxy. It
  enforces the 120-second window, 2 MiB total/1 MiB entity caps, 5.25-second
  dispatch cadence, 5-second request-start cadence, TLS verification, no
  redirects, disk floor, and 429/503/five-transport-failure stops.
- `--fixture` only exercises local parser, identity, resume, cap, cadence,
  stop, and disk checks. It produced 12/12 passing cases with zero requests.

Final prepared artifact hashes:

| file | bytes | SHA-256 |
|---|---:|---|
| `plan.json` | 5160 | `11a2d7506737924fd8060139d7eddb90acf38a1b960af0ee91c177e745be5b48` |
| `input-bindings.json` | 3861 | `b56b4d68ad2d35a08dad6eaa5a2e0f9dec15528bef533b69acc9454ed554f23c` |
| `control_after_rest10b.py` | 22500 | `93d1c9977f2ac324a4a2bfbc485bf613f07d89fea5973ed123e00842ac937a78` |
| `fixture-results.json` | 776 | `f78e0d0a579cde5c34d7523b483ad02796043c83b64729d6c25ec10685a48d90` |
| `parent-execute-once.py` | 4426 | `18ac808ea83e4f5b9afa4273416e0f0403226550472fbd8330b985886cfc1612` |

No GO receipt, report, state, raw directory, or parent execution receipt was
created in this packet.
