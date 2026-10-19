# Initial v36 preparation attempt

The first offline preflight wrote the two new map candidates, then entered the initial extractor. The extractor's per-line/per-target variant construction made the read-only Source15 text pass materially slow; it was stopped after a bounded observation (PID 41328, roughly 30 minutes wall time, CPU time rising, no network/export/output). The partial map bytes are preserved here for audit only and are not accepted inputs. The extractor was then changed to precompile one combined literal pattern and scan only matched lines before the final preflight rerun.
