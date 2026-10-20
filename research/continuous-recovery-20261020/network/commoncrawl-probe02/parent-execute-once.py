"""Single future root-GO-gated parent watchdog for Common Crawl probe02."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
DRIVER = OUT / "commoncrawl_probe02.py"
PLAN = OUT / "plan.json"
BINDINGS = OUT / "input-bindings.json"
FIXTURE = OUT / "fixture-results.json"
GO = ROOT / "research" / "continuous-recovery-20261020" / "publication" / "root-commoncrawl-probe02-execute-go.json"
RECEIPT = OUT / "parent-execution-receipt.json"
STDOUT = OUT / "parent-stdout.txt"
STDERR = OUT / "parent-stderr.txt"
WATCHDOG_SECONDS = 240.0


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def main() -> int:
    if not GO.is_file():
        raise RuntimeError(f"missing future root GO receipt: {GO}")
    go = json.loads(GO.read_text(encoding="utf-8"))
    if go.get("accepted") is not True or go.get("root_go") is not True:
        raise RuntimeError("root GO is not accepted/root_go")
    expected = {
        "plan_sha256": sha_file(PLAN),
        "driver_sha256": sha_file(DRIVER),
        "fixture_sha256": sha_file(FIXTURE),
        "input_bindings_sha256": sha_file(BINDINGS),
        "parent_sha256": sha_file(Path(__file__)),
    }
    for key, value in expected.items():
        if go.get(key) != value:
            raise RuntimeError(f"root GO {key} mismatch")
    if RECEIPT.exists() or STDOUT.exists() or STDERR.exists():
        raise RuntimeError("parent output exists; refusing rerun")
    started = datetime.now(timezone.utc)
    started_mono = time.monotonic()
    child = subprocess.Popen([sys.executable, str(DRIVER), "--execute"], cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timed_out = False
    try:
        stdout, stderr = child.communicate(timeout=WATCHDOG_SECONDS)
    except subprocess.TimeoutExpired:
        timed_out = True
        child.kill()
        stdout, stderr = child.communicate()
    finished = datetime.now(timezone.utc)
    STDOUT.write_bytes(stdout or b"")
    STDERR.write_bytes(stderr or b"")
    receipt = {
        "schema": "wow-recovery.commoncrawl-probe02-parent-receipt.v1",
        "batch_id": "COMMONCRAWL-PROBE02-20261020",
        "root_go_receipt": str(GO.relative_to(ROOT)).replace("\\", "/"),
        "root_go_sha256": sha_file(GO),
        "started_utc": iso(started),
        "finished_utc": iso(finished),
        "elapsed_seconds": round(time.monotonic() - started_mono, 6),
        "watchdog_seconds": WATCHDOG_SECONDS,
        "timed_out": timed_out,
        "child_returncode": child.returncode,
        "stdout_path": str(STDOUT.relative_to(ROOT)).replace("\\", "/"),
        "stderr_path": str(STDERR.relative_to(ROOT)).replace("\\", "/"),
        "stdout_bytes": len(stdout or b""),
        "stderr_bytes": len(stderr or b""),
        "wayback_requests": 0,
        "direct_only": True,
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 124 if timed_out else (child.returncode or 0)


if __name__ == "__main__":
    raise SystemExit(main())
