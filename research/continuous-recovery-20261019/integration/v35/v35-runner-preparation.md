# v35 runner preparation

`execute_v35.py` is a one-shot, export-only wrapper. It reads the frozen v35
maps/preflight and root-v35 input gate, verifies every map, source/public-copy
receipt, v34 closure, current exporter, and contest-tool acceptance SHA, then
calls `export_pages` exactly once with `max_bytes=None`, the D: free-space
floor, the frozen primary/supplement maps, and the v35 primary delta. It
requires `--go --root-export-go`, an accepted root gate, and a parent 900-second
watchdog. It never reads pending network folders, regenerates maps, or
publishes Pages.
