# v29 runner preparation

execute_v29.py is the separate v29 execution wrapper. It does not call the
v28 builder main; it imports only the frozen v28 closure constants and
read-only validation helper. The frozen v28 primary tuple already contains the
v25/v26/v27/v28 primary maps. A future export appends the immutable v29
primary map, while the frozen v28 supplement tuple is reused unchanged.

The offline readiness command is:

    & 'C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 research/continuous-recovery-20261018/integration/v29/execute_v29.py --prepare

It checks the pinned v28 closure, v29 map and preflight, public-copy lengths,
the output/partial/receipt guards, and the disk floor. It performs zero
network requests and writes no files. If the root acceptance receipt already
exists, --prepare verifies every listed map_bindings SHA and all 40
public-copy SHA/length entries, but it still stops before export.

The only export entry is:

    & 'C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 research/continuous-recovery-20261018/integration/v29/execute_v29.py --go --root-export-go

This entry requires an accepted
research/continuous-recovery-20261018/publication/root-v29-input-acceptance.json,
requires exact bindings for the frozen v28 builder/map and v29 map/preflight,
the approved exporter and historical-exhibits tool, and refuses an existing
v29 output, .partial directory, or build receipt. It records UTC start/end,
the exact command, root acceptance receipt, closure map hashes, output
provenance SHA, actual file count, and disk free space before and after the
single exporter call. A failed export writes one failure receipt and must not
be retried over that receipt or partial output.

Pinned inputs:

- v28 builder: e9ba376dec05ac5443a3f2264a5c6b9321780d9921dc0a72f3fac83343d9f7e4
- v28 primary map: d06182cd3b82eae3eaebdb88229bb6efaed8b2b0fdf8f44d7ffa71bbeb20abd2
- v28 provenance: 6f42a33a67480f95b229e05611659d7ae4a562df1a3092a71f287532c936f793
- v29 primary map: fc1e9f4e5da090fd22c6f8eea6d333f6899b01dedfc2dec2b106be98411d58ed
- v29 preflight: b29e1e7f69cf17391084d8fb0770008e1b850c9e9b2f92ad5900c65e68ab0194
- exporter: 943f57e2f62582e2659c98766e98deeeda60c9c1d131326f6f0ad6e7fbfd4a00
- historical exhibits: 35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011

Expected post-export counts remain 8761 declared / 8762 actual files,
228 primary overlays, 75 supplement overlays, 303 total overlays, guide
collection 39, and previews 22.
