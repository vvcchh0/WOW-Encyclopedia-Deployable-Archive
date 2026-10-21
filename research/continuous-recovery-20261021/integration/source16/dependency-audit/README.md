# Source16 dependency audit

"
        "This is a local, read-only audit of the eight Source16 body pages. It parses actual HTML resource attributes and CSS declarations, ignores HTML comments, and records only recognized runtime targets from `printFlash`, `document.write`, and `roothost` in a separate dynamic class. It does not inspect the network or alter Source16/v42.

"
        "`dependency-audit.json` is the evidence record; `dependency-audit.csv` contains one row per observed use with source line; `priority-gaps.csv` is capped at 30 ranked page-use gaps.
