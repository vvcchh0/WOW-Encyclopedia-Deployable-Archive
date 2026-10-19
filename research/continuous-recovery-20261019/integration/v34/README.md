# v34 preparation

This directory contains preparation-only inputs for a future v34 rebuild. It
uses the frozen source15 site and manifest, the accepted v33 closure (459
primary overlays, 100 supplements, 559 total), and the unchanged guide maps
(39 collection images in 3 groups and 22 previews). The two v34 maps are
explicit empty deltas: no unaccepted network folder or pending source is read.

The planned change is the accepted exact-route contest navigation fallback in
the current exporter (`e5b3a53381ddcf0b5037a726d328c7dd99fa5d2f8e24e047e474a3853305643a`).
The future output is `.scratch/pages-resources-20261019-v34`; preparation does
not use the already-derived v33 tree as a source.

Offline preparation:

```powershell
& 'C:\Program Files\Python311\python.exe' -X utf8 research/continuous-recovery-20261019/integration/v34/build_pages_v34.py --prepare --preflight
```

Future execution requires root to create and accept
`research/continuous-recovery-20261019/publication/root-v34-input-acceptance.json`.
Only then may this one-shot command run:

```powershell
& 'C:\Program Files\Python311\python.exe' -X utf8 research/continuous-recovery-20261019/integration/v34/execute_v34.py --go --root-export-go
```

The runner requires the exact prepared hashes, zero new image rows, the D:
disk floor, and an absent output/partial/receipt. It refuses to run without
the explicit root gate and has no network or publication behavior. The r2
runner also refuses to start at or after `2026-10-19T13:30:00Z`, passes a
`650000000` byte output bound to the exporter, and is intended to run under a
parent watchdog capped at 900 seconds.
