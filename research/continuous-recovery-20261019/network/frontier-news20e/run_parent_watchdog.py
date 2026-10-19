from __future__ import annotations

import datetime as dt
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
ADAPTER = ROOT / "adapter" / "frontier_news20e_adapter.py"
OUTPUT = ROOT / "output"
TEMP_STDOUT = ROOT / "parent-stdout.log"
TEMP_STDERR = ROOT / "parent-stderr.log"
FINAL_STDOUT = OUTPUT / "parent-stdout.log"
FINAL_STDERR = OUTPUT / "parent-stderr.log"
RECEIPT = OUTPUT / "parent-execution.json"
WATCHDOG_SECONDS = 960


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if any(OUTPUT.iterdir()):
        raise SystemExit("output directory must be empty before adapter execution")
    start = utc_now()
    disk_before = shutil.disk_usage(Path("D:/")).free
    with TEMP_STDOUT.open("w", encoding="utf-8", newline="") as stdout, TEMP_STDERR.open(
        "w", encoding="utf-8", newline=""
    ) as stderr:
        proc = subprocess.Popen(
            [sys.executable, str(ADAPTER), "--execute"],
            cwd=str(REPO),
            stdout=stdout,
            stderr=stderr,
            text=True,
        )
        timed_out = False
        try:
            return_code = proc.wait(timeout=WATCHDOG_SECONDS)
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            return_code = proc.wait()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    shutil.move(str(TEMP_STDOUT), str(FINAL_STDOUT))
    shutil.move(str(TEMP_STDERR), str(FINAL_STDERR))
    end = utc_now()
    disk_after = shutil.disk_usage(Path("D:/")).free
    receipt = {
        "schema": "frontier-news20e-parent-execution-v1",
        "command": [sys.executable, str(ADAPTER), "--execute"],
        "cwd": str(REPO),
        "start_utc": start,
        "end_utc": end,
        "watchdog_seconds": WATCHDOG_SECONDS,
        "timed_out": timed_out,
        "return_code": return_code,
        "disk_free_before_bytes": disk_before,
        "disk_free_after_bytes": disk_after,
        "stdout_path": str(FINAL_STDOUT.relative_to(REPO)).replace("\\", "/"),
        "stderr_path": str(FINAL_STDERR.relative_to(REPO)).replace("\\", "/"),
        "stdout_sha256": sha256(FINAL_STDOUT),
        "stderr_sha256": sha256(FINAL_STDERR),
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 124 if timed_out else return_code


if __name__ == "__main__":
    raise SystemExit(main())
