# v35 partial finalization plan

This folder owns a bounded recovery check for
`.scratch/pages-resources-20261019-v35.partial`. The normal v35 export wrote a
complete partial tree and its provenance before spending time in the exporter
tail's workspace-size accounting. This plan validates the existing tree in
place; it does not rebuild or publish it.

`finalize_v35_partial.py --check` binds the corrected root gate
`research/continuous-recovery-20261019/publication/root-v35-input-acceptance.json`
(SHA-256
`1d3705381773e5040724f957512987719946e36876765f84395e804fdee655fd`), the
partial provenance SHA
`f37f73ba4cdd63b1190b895a2d770dd94b2b764ad5fc219a5fd34bad93a3c4d0`, and the
frozen v35 map, preparation, preflight, builder, and runner SHAs. It verifies
the declared 9,041 paths plus the provenance file, streams every declared file
with eight I/O workers, checks all 24 new public copies (191,943 bytes), and
compares all 559 old image-overlay metadata records with v34 without
rehashing the old image payloads. The v34-to-partial common-path delta is
expected to be the four derived paths recorded in the receipt; the other 24
changes are the new overlay paths.

The check records free bytes against the 11,005,853,696-byte floor and never
calls `workspace_size`, performs a network request, calls the exporter, or
creates the normal output directory. `run_check_v35.py` is the required outer
watchdog: it invokes the checker with `subprocess.run(..., timeout=300)` and
returns 124 on a hard timeout. A failed check receipt remains evidence and is
not silently replaced; reruns should be separately reviewed.

Promotion is a separate, dormant path. It requires `--promote --root-go`, a
passed check receipt and its exact SHA, a still-absent output path, the same
partial provenance SHA, and the frozen exporter SHA
`e5b3a53381ddcf0b5037a726d328c7dd99fa5d2f8e24e047e474a3853305643a`. Only
then does it call the frozen `_promote_partial_output` rename helper. No
promotion is authorized by this preparation or by the check command.
