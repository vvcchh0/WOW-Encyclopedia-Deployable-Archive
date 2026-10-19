#!/usr/bin/env python3
"""Single outer watchdog for the accepted v37 export.

This wrapper is execution-only.  It never prepares maps, changes the runner,
or retries the command.  The accepted runner already owns the inner 600-second
child-export watchdog; this process adds the required 720-second hard bound.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if ROOT.name != "WOW_Encyclopedia":
    raise RuntimeError(f"unexpected repository root: {ROOT}")
HERE = Path(__file__).resolve().parent
RUNNER = HERE / "execute_v37.py"
OUTPUT = ROOT / ".scratch/pages-resources-20261019-v37"
BUILD_RECEIPT = HERE / "v37-build-receipt.json"
PARENT_RECEIPT = HERE / "v37-parent-execution-receipt.json"
STDOUT_LOG = HERE / "v37-parent-stdout.log"
STDERR_LOG = HERE / "v37-parent-stderr.log"
GATE = ROOT / "research/continuous-recovery-20261019/publication/root-v37-input-acceptance.json"
FLOOR = 11_005_853_696
OUTER_TIMEOUT = 720
EXPECTED_RUNNER_SHA = "__ROOT_V37_RUNNER_SHA__"
EXPECTED_GATE_SHA = "__ROOT_V37_GATE_SHA__"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def tree_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def write_receipt(payload: dict) -> None:
    if PARENT_RECEIPT.exists():
        raise RuntimeError(f"refusing existing parent receipt: {PARENT_RECEIPT}")
    PARENT_RECEIPT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    for path in (PARENT_RECEIPT, STDOUT_LOG, STDERR_LOG):
        if path.exists():
            raise RuntimeError(f"refusing existing execution artifact: {path}")
    if not GATE.is_file() or sha(GATE) != EXPECTED_GATE_SHA:
        raise RuntimeError("v37 root acceptance gate SHA differs")
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    if gate.get("accepted") is not True or gate.get("export_executed") is not False or gate.get("network_requests") not in (0, None):
        raise RuntimeError("v37 root gate is not an unexecuted accepted gate")
    if not RUNNER.is_file() or sha(RUNNER) != EXPECTED_RUNNER_SHA:
        raise RuntimeError("accepted v37 runner SHA differs")
    if OUTPUT.exists() or OUTPUT.with_name(OUTPUT.name + ".partial").exists() or BUILD_RECEIPT.exists():
        raise RuntimeError("v37 output, partial, or build receipt already exists")
    free_before = shutil.disk_usage(ROOT).free
    if free_before < FLOOR:
        raise RuntimeError(f"D below v36 floor before parent runner: {free_before}")
    started = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    command = [sys.executable, "-X", "utf8", str(RUNNER), "--go", "--root-export-go"]
    completed = False
    timed_out = False
    returncode = None
    error = None
    try:
        with STDOUT_LOG.open("xb") as stdout, STDERR_LOG.open("xb") as stderr:
            result = subprocess.run(command, cwd=str(ROOT), stdout=stdout, stderr=stderr, timeout=OUTER_TIMEOUT, check=False)
            returncode = result.returncode
        completed = returncode == 0
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        error = f"TimeoutExpired: {exc}"
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    ended = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    free_after = shutil.disk_usage(ROOT).free
    stdout_tail = STDOUT_LOG.read_text(encoding="utf-8", errors="replace")[-12000:] if STDOUT_LOG.exists() else ""
    stderr_tail = STDERR_LOG.read_text(encoding="utf-8", errors="replace")[-12000:] if STDERR_LOG.exists() else ""
    provenance = OUTPUT / "export-provenance.json"
    stats = {}
    actual_files = None
    if provenance.is_file():
        try:
            stats = json.loads(provenance.read_text(encoding="utf-8")).get("stats") or {}
        except Exception as exc:
            error = error or f"provenance-read: {type(exc).__name__}: {exc}"
    if OUTPUT.is_dir():
        actual_files = sum(1 for item in OUTPUT.rglob("*") if item.is_file())
    receipt = {
        "schema": "wow-recovery.integration.v37-parent-execution-receipt.v1",
        "status": "completed" if completed else "failed",
        "executed_by": "/root/local_recovery_20261018",
        "command": command,
        "outer_timeout_seconds": OUTER_TIMEOUT,
        "inner_runner_timeout_seconds": 600,
        "checked_utc_start": started,
        "checked_utc_end": ended,
        "returncode": returncode,
        "timed_out": timed_out,
        "error": error,
        "root_input_acceptance": {"path": rel(GATE), "sha256": sha(GATE)},
        "runner": {"path": rel(RUNNER), "sha256": sha(RUNNER)},
        "stdout_log": {"path": rel(STDOUT_LOG), "sha256": sha(STDOUT_LOG), "bytes": STDOUT_LOG.stat().st_size} if STDOUT_LOG.exists() else None,
        "stderr_log": {"path": rel(STDERR_LOG), "sha256": sha(STDERR_LOG), "bytes": STDERR_LOG.stat().st_size} if STDERR_LOG.exists() else None,
        "stdout_tail": stdout_tail,
        "stderr_tail": stderr_tail,
        "output": rel(OUTPUT),
        "build_receipt": {"path": rel(BUILD_RECEIPT), "sha256": sha(BUILD_RECEIPT)} if BUILD_RECEIPT.exists() else None,
        "provenance": {"path": rel(provenance), "sha256": sha(provenance)} if provenance.is_file() else None,
        "stats": stats,
        "actual_files": actual_files,
        "tree_bytes": tree_bytes(OUTPUT) if OUTPUT.is_dir() else None,
        "network_requests": 0,
        "published": False,
        "disk_free_before_bytes": free_before,
        "disk_free_after_bytes": free_after,
        "disk_free_floor_bytes": FLOOR,
    }
    write_receipt(receipt)
    print(json.dumps({"status": receipt["status"], "returncode": returncode, "timed_out": timed_out, "output": receipt["output"], "actual_files": actual_files, "stats": stats, "provenance": receipt["provenance"], "parent_receipt": rel(PARENT_RECEIPT)}, ensure_ascii=False))
    if not completed:
        raise SystemExit(returncode or 1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
