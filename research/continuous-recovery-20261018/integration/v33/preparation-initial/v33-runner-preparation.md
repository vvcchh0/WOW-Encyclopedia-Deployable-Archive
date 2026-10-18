# v33 runner preparation

`execute_v33.py` is a one-shot export wrapper. It never regenerates maps or
preflight, refuses an existing output/partial/receipt, checks the accepted
root input gate's exact `map_bindings` and public-copy list, and requires
`--go --root-export-go`. The exporter receives the frozen v28 primary and
supplement closure plus v29, v30, v32, and the two v33 delta maps. The source
manifest is the only authority for the new image count; pending folders are
never scanned. Root must supply post-export declared/actual file expectations
before authorizing the run.
