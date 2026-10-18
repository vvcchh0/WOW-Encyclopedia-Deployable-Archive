# Static40 v32 offline plan factory

`static40-source-queue.json` is a preparation-only queue derived from the
frozen v32 static-frontier audit. It retains candidate priority rows 1–10 and
12–41, exactly 40 literal HTTP(S) image destinations. Candidate page paths,
line numbers, page SHA-256 values, contexts, and prior execution/CDX state are
retained in each row. The one excluded row is the literal-space URL
`http://www.worldofwarcraft.com/info/basics/images/small pets/icon.gif`; it is
preserved under `excluded_targets` for separate transport review and is not
silently repaired.

The queue is bound to the v32 audit SHA
`72c00aa28e7c19c86de7f877983d049662f543be48960d2879a0f566bf15657f`, the
navigation-exclusion correction SHA
`cc665a6ba455977f267e5f7e22b8bf4907d58a9581809b695f2fbc1b92bc564d`, and queue
SHA `8cd75a65935eb416ab12ed70fa1b2f86335939a409173df899bdb7f8d48d95f9`.
The factory confirms that no selected normalized identity overlaps the corrected
70-row navigation exclusion.

`prepare_static40.py --batch-index N` prepares one ten-target plan for ranks
1–10, 11–20, 21–30, or 31–40. It re-reads the latest accepted source receipt,
tail, status, and CONTROL03 gate at invocation, validates every cited v32 page
again, and binds the frozen reusable-image-v3 driver. The policy is exact CDX
from `20000101000000` through `20080512210044`, 24 attempts in 240 seconds,
16 MiB total, 8 MiB per entity, direct-first 4 / proxy 20, no redirects, TLS
verification, and 120-second 429/503 cooldown. Parent GO remains required.

The factory writes explicit UTF-8/LF bytes and checks resolved factory,
temporary, target, and document paths before atomic rename or cleanup. This
turn created no real batch and made no CDX, replay, driver, status, or exporter
call.

Focused validation:

```powershell
$py = 'C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -X utf8 -m py_compile .\research\continuous-recovery-20261018\network\static40-v32\prepare_static40.py .\research\continuous-recovery-20261018\network\static40-v32\test_prepare_static40.py
& $py -X utf8 -m unittest discover -s .\research\continuous-recovery-20261018\network\static40-v32 -p 'test_*.py' -v
```

