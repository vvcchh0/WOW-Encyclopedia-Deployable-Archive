#!/usr/bin/env python3
"""Root-gated, hard-timeout wrapper for the prepared v36 browser harness."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


EXPECTED_ROOT = Path(r"D:\WOW_Encyclopedia")
ROOT = next(parent.resolve() for parent in Path(__file__).resolve().parents if parent.name == EXPECTED_ROOT.name)
if ROOT != EXPECTED_ROOT.resolve():
    raise SystemExit(f"unexpected workspace root: {ROOT}")
BROWSER_DIR = Path(__file__).resolve().parent
INPUT = BROWSER_DIR.parent / "v36-browser-plan-r1.json"
HARNESS = BROWSER_DIR / "check_v36_images_r2.cjs"
RESULT = BROWSER_DIR / "results/v36-browser-r2.json"
RUN_RECEIPT = BROWSER_DIR / "v36-browser-run-receipt-r2.json"
NODE = Path(r"C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe")
MAX_SECONDS = 300


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def under(path: Path, base: Path, label: str) -> Path:
    candidate, root = path.resolve(strict=False), base.resolve(strict=False)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise SystemExit(f"{label} escapes {root}: {candidate}") from exc
    return candidate


def read_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise SystemExit(f"missing {label}: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{label} is not an object")
    return value


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def output_text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value or "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--go", action="store_true")
    parser.add_argument("--root-browser-go", action="store_true")
    args = parser.parse_args()
    if not args.go or not args.root_browser_go:
        raise SystemExit("browser run requires --go --root-browser-go")
    if not NODE.is_file():
        raise SystemExit(f"bundled node runtime missing: {NODE}")
    if not HARNESS.is_file() or not INPUT.is_file():
        raise SystemExit("v36 browser harness/plan missing")
    if RESULT.exists() or RUN_RECEIPT.exists():
        raise SystemExit("refusing existing v36 browser result or receipt")
    plan = read_json(INPUT, "v36 browser plan")
    if plan.get("status") != "prepared_waiting_root_browser_go":
        raise SystemExit("v36 browser plan is not waiting for root GO")
    if plan.get("scope", {}).get("network_requests") != 0 or plan.get("scope", {}).get("export_executed_by_plan") is not False:
        raise SystemExit("v36 browser plan offline/export gate failed")
    if plan.get("coverage", {}).get("target_count") != 51 or plan.get("coverage", {}).get("reference_count") != 53:
        raise SystemExit("v36 browser plan coverage gate failed")
    output = under(ROOT / plan["scope"]["output_root"], ROOT / ".scratch", "v36 output")
    provenance = output / "export-provenance.json"
    if not output.is_dir() or not provenance.is_file():
        raise SystemExit(f"promoted v36 output/provenance missing: {output}")
    if sha256(provenance) != plan["scope"]["provenance_sha256"]:
        raise SystemExit("promoted v36 provenance SHA mismatch")
    started = time.monotonic()
    started_utc = now_utc()
    command = [str(NODE), str(HARNESS), "--go", "--root-browser-go", "--input", str(INPUT), "--result", str(RESULT), "--screenshots", str(BROWSER_DIR / "screenshots-r2")]
    try:
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=MAX_SECONDS, check=False)
        timed_out = False
        stdout, stderr = output_text(completed.stdout), output_text(completed.stderr)
    except subprocess.TimeoutExpired as exc:
        completed = None
        timed_out = True
        stdout, stderr = output_text(exc.stdout), output_text(exc.stderr)
    elapsed = time.monotonic() - started
    receipt = {
        "schema": "wow-recovery.integration.v36-browser-run-receipt-r2.v1",
        "status": "timed_out" if timed_out else ("completed" if completed and completed.returncode == 0 else "failed"),
        "started_utc": started_utc,
        "finished_utc": now_utc(),
        "elapsed_seconds": round(elapsed, 6),
        "timeout_seconds": MAX_SECONDS,
        "command": command,
        "input": {"path": str(INPUT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(INPUT)},
        "harness_sha256": sha256(HARNESS),
        "output": {"path": plan["scope"]["output_root"], "provenance_sha256": plan["scope"]["provenance_sha256"]},
        "result": {"path": str(RESULT.relative_to(ROOT)).replace("\\", "/"), "exists": RESULT.exists(), "sha256": sha256(RESULT) if RESULT.exists() else None},
        "returncode": None if timed_out else completed.returncode,
        "stdout": stdout[-20000:],
        "stderr": stderr[-20000:],
        "external_requests_expected": 0,
    }
    RUN_RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(receipt, ensure_ascii=False))
    return 124 if timed_out else completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
