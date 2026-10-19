#!/usr/bin/env python3
"""Run the v35 partial check behind a real 300-second subprocess timeout."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if parent.name == "WOW_Encyclopedia")
FINALIZER = Path(__file__).resolve().with_name("finalize_v35_partial.py")
START = time.monotonic()
try:
    completed = subprocess.run(
        [sys.executable, str(FINALIZER), "--check"],
        cwd=ROOT,
        check=False,
        timeout=300,
    )
except subprocess.TimeoutExpired:
    elapsed = time.monotonic() - START
    print(f"v35 partial check hard watchdog expired after {elapsed:.3f}s", file=sys.stderr)
    raise SystemExit(124)
elapsed = time.monotonic() - START
print(f"v35 partial check returncode={completed.returncode} elapsed_seconds={elapsed:.6f}")
raise SystemExit(completed.returncode)
