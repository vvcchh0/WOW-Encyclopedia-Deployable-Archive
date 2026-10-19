#!/usr/bin/env python3
"""One root-local, hard-timeout wrapper for the Toplist runtime diagnosis."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"D:\WOW_Encyclopedia")
DIAG_DIR = ROOT / "research/continuous-recovery-20261019/integration/toplist-runtime-diagnosis"
HARNESS = DIAG_DIR / "diagnose_toplist_runtime.cjs"
RESULT = DIAG_DIR / "results/toplist-runtime-diagnosis.json"
RECEIPT = DIAG_DIR / "toplist-runtime-diagnosis-run-receipt.json"
NODE = Path(r"C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe")
MAX_SECONDS = 90


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if not args.run:
        raise SystemExit("diagnosis requires --run")
    if ROOT.resolve() != Path(r"D:\WOW_Encyclopedia").resolve():
        raise SystemExit(f"unexpected root: {ROOT}")
    if not NODE.is_file() or not HARNESS.is_file():
        raise SystemExit("bundled node or diagnosis harness missing")
    if RESULT.exists() or RECEIPT.exists():
        raise SystemExit("refusing existing diagnosis result or receipt")
    started = time.monotonic()
    started_utc = now_utc()
    command = [str(NODE), str(HARNESS)]
    try:
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=MAX_SECONDS, check=False)
        timed_out = False
        stdout, stderr = completed.stdout or "", completed.stderr or ""
    except subprocess.TimeoutExpired as exc:
        completed = None
        timed_out = True
        stdout, stderr = str(exc.stdout or ""), str(exc.stderr or "")
    receipt = {
        "schema": "wow-recovery.integration.toplist-runtime-diagnosis-run-receipt.v1",
        "status": "timed_out" if timed_out else ("completed" if completed and completed.returncode == 0 else "failed"),
        "started_utc": started_utc,
        "finished_utc": now_utc(),
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "timeout_seconds": MAX_SECONDS,
        "command": command,
        "harness_sha256": sha256(HARNESS),
        "result": {"path": str(RESULT.relative_to(ROOT)).replace("\\", "/"), "exists": RESULT.exists(), "sha256": sha256(RESULT) if RESULT.exists() else None},
        "returncode": None if timed_out else completed.returncode,
        "stdout": stdout[-20000:],
        "stderr": stderr[-20000:],
        "external_requests_expected": 0,
        "automatic_retry": False,
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(receipt, ensure_ascii=False))
    return 124 if timed_out else completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
