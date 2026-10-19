# v37 runner preparation

`execute_v37.py` is a one-shot, export-only wrapper. It reads the frozen v37
maps/preflight and root-v37 input gate, verifies every v36 closure map,
source/public-copy receipt, current exporter, historical-exhibit tool, Toplist
compatibility module and acceptance receipt, then calls `export_pages` exactly
once with `max_bytes=None`, the D: free-space floor, the frozen primary/
supplement maps, and the v37 primary delta. It requires `--go
--root-export-go`, an accepted root gate, and a 600-second inner watchdog
under a 720-second parent watchdog. It never reads pending network folders,
regenerates maps, or publishes Pages.
