# v36 runner preparation

`execute_v36.py` is a one-shot, export-only wrapper. It reads the frozen v36
maps/preflight and root-v36 input gate, verifies every map, source/public-copy
receipt, v35 closure, current exporter, and contest-tool acceptance SHA, then
calls `export_pages` exactly once with `max_bytes=None`, the D: free-space
floor, the frozen primary/supplement maps, and the v36 primary delta. It
requires `--go --root-export-go`, an accepted root gate, and a parent 600-second
watchdog. It never reads pending network folders, regenerates maps, or
publishes Pages.
