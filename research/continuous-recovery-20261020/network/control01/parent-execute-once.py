"""One-shot 180-second parent watchdog for the 2026-10-20 control01 batch.

This wrapper is intentionally inert until the separately written root GO
receipt binds all prepared hashes. It never retries a timed-out child and
refuses to launch outside the current recovery schedule.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "research" / "continuous-recovery-20261020"
DRIVER = OUT / "control01_driver.py"
PLAN = OUT / "plan.json"
FIXTURE = OUT / "fixture-results.json"
BINDINGS = OUT / "input-bindings.json"
GO = BASE / "publication" / "root-control01-execute-go.json"
RAW = OUT / "raw"
REPORT = OUT / "control-report.json"
STATE = OUT / "state.json"
RECEIPT = OUT / "parent-execution-receipt.json"
STDOUT = OUT / "parent-stdout.txt"
STDERR = OUT / "parent-stderr.txt"
DISK_FLOOR = 11_005_853_696
RUN_START_UTC = "2026-10-20T08:33:22Z"
NETWORK_STOP_UTC = "2026-10-20T13:15:00Z"
RUN_DEADLINE_UTC = "2026-10-20T14:33:22Z"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    now_utc = datetime.now(timezone.utc)
    run_start = datetime.fromisoformat(RUN_START_UTC.replace("Z", "+00:00"))
    network_stop = datetime.fromisoformat(NETWORK_STOP_UTC.replace("Z", "+00:00"))
    run_deadline = datetime.fromisoformat(RUN_DEADLINE_UTC.replace("Z", "+00:00"))
    if now_utc < run_start:
        raise SystemExit("recovery run has not started")
    if now_utc >= network_stop:
        raise SystemExit("network batch cutoff has passed")
    if now_utc >= run_deadline:
        raise SystemExit("recovery run deadline has passed")
    if RECEIPT.exists() or REPORT.exists() or STATE.exists() or RAW.exists():
        raise SystemExit("refusing rerun: output/raw/receipt already exists")
    if not GO.is_file():
        raise SystemExit(f"missing root GO receipt: {rel(GO)}")
    go = json.loads(GO.read_text(encoding="utf-8"))
    if go.get("accepted") is not True or go.get("root_go") is not True:
        raise SystemExit("root GO is not accepted/root_go")
    expected = {
        "plan_sha256": sha(PLAN),
        "driver_sha256": sha(DRIVER),
        "fixture_sha256": sha(FIXTURE),
        "input_bindings_sha256": sha(BINDINGS),
    }
    for key, value in expected.items():
        if go.get(key) != value:
            raise SystemExit(f"root GO {key} mismatch")
    disk_before = shutil.disk_usage(ROOT).free
    if disk_before < DISK_FLOOR:
        raise SystemExit(f"disk floor failed: {disk_before}")
    started = time.monotonic()
    started_utc = now()
    command = [sys.executable, "-X", "utf8", str(DRIVER), "--execute"]
    try:
        completed = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180, check=False)
        timed_out = False
        returncode = completed.returncode
        stdout = completed.stdout or b""
        stderr = completed.stderr or b""
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = None
        stdout = exc.stdout or b""
        stderr = exc.stderr or b""
    if isinstance(stdout, str):
        stdout = stdout.encode("utf-8", errors="replace")
    if isinstance(stderr, str):
        stderr = stderr.encode("utf-8", errors="replace")
    STDOUT.write_bytes(stdout)
    STDERR.write_bytes(stderr)
    disk_after = shutil.disk_usage(ROOT).free
    receipt = {
        "schema": "wow-recovery.control01-parent-receipt.v1",
        "started_utc": started_utc,
        "finished_utc": now(),
        "elapsed_seconds": time.monotonic() - started,
        "timeout_seconds": 180,
        "timed_out": timed_out,
        "returncode": returncode,
        "command": command,
        "go_path": rel(GO),
        "go_sha256": sha(GO),
        "plan_sha256": sha(PLAN),
        "driver_sha256": sha(DRIVER),
        "fixture_sha256": sha(FIXTURE),
        "input_bindings_sha256": sha(BINDINGS),
        "stdout_path": rel(STDOUT),
        "stdout_sha256": sha(STDOUT),
        "stderr_path": rel(STDERR),
        "stderr_sha256": sha(STDERR),
        "disk_free_before_bytes": disk_before,
        "disk_free_after_bytes": disk_after,
        "disk_floor_bytes": DISK_FLOOR,
        "child_report_present": REPORT.exists(),
        "child_state_present": STATE.exists(),
        "raw_present": RAW.exists(),
        "retry_count": 0,
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if returncode == 0 and not timed_out else 1


if __name__ == "__main__":
    raise SystemExit(main())
