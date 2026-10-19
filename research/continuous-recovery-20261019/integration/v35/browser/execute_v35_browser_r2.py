#!/usr/bin/env python3
"""Root-gated, hard-timeout wrapper for the v35 browser harness."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


EXPECTED_ROOT = Path(r"D:\WOW_Encyclopedia")
ROOT = next(parent.resolve() for parent in Path(__file__).resolve().parents if parent.name == EXPECTED_ROOT.name)
if ROOT != EXPECTED_ROOT.resolve():
    raise SystemExit(f"unexpected workspace root: {ROOT}")
BROWSER_DIR = Path(__file__).resolve().parent
INPUT = BROWSER_DIR / "v35-browser-input.json"
HARNESS = BROWSER_DIR / "check_v35_new_images_r2.cjs"
RESULT = BROWSER_DIR / "results/v35-new-images-r2.json"
RUN_RECEIPT = BROWSER_DIR / "v35-browser-run-receipt-r2.json"
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


def verify_binding(binding: dict, label: str) -> None:
    if not isinstance(binding, dict) or not isinstance(binding.get("path"), str) or not isinstance(binding.get("sha256"), str):
        raise SystemExit(f"malformed {label}")
    path = under(ROOT / binding["path"], ROOT, label)
    if not path.is_file():
        raise SystemExit(f"missing {label}: {path}")
    actual = sha256(path)
    if actual != binding["sha256"]:
        raise SystemExit(f"{label} SHA mismatch: {actual} != {binding['sha256']}")


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
        raise SystemExit("browser harness/input missing")
    if RESULT.exists() or RUN_RECEIPT.exists():
        raise SystemExit("refusing existing v35 browser result or receipt")
    input_value = read_json(INPUT, "v35 browser input")
    if input_value.get("status") != "prepared_waiting_root_v35_browser_go":
        raise SystemExit("browser input is not waiting for root GO")
    if input_value.get("network_requests") != 0 or input_value.get("export_executed") is not False:
        raise SystemExit("browser input offline/export gate failed")
    for name, binding in input_value.get("frozen_bindings", {}).items():
        verify_binding(binding, f"binding {name}")
    output = under(ROOT / input_value["output"]["path"], ROOT / ".scratch", "v35 output")
    if not output.is_dir() or not (output / "export-provenance.json").is_file():
        raise SystemExit(f"promoted v35 output/provenance missing: {output}")
    if sha256(output / "export-provenance.json") != input_value["output"]["provenance_sha256"]:
        raise SystemExit("promoted v35 provenance SHA mismatch")
    started = time.monotonic()
    started_utc = now_utc()
    command = [str(NODE), str(HARNESS), "--go", "--root-browser-go", "--input", str(INPUT), "--result", str(RESULT)]
    try:
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=MAX_SECONDS, check=False)
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        completed = None
        timed_out = True
        stdout = output_text(exc.stdout)
        stderr = output_text(exc.stderr)
    else:
        stdout = output_text(completed.stdout)
        stderr = output_text(completed.stderr)
    elapsed = time.monotonic() - started
    receipt = {
        "schema": "wow-recovery.integration.v35-browser-run-receipt.v1",
        "status": "timed_out" if timed_out else ("completed" if completed and completed.returncode == 0 else "failed"),
        "started_utc": started_utc,
        "finished_utc": now_utc(),
        "elapsed_seconds": round(elapsed, 6),
        "timeout_seconds": MAX_SECONDS,
        "command": command,
        "input": {"path": str(INPUT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(INPUT)},
        "harness_sha256": sha256(HARNESS),
        "result": {"path": str(RESULT.relative_to(ROOT)).replace("\\", "/"), "exists": RESULT.exists(), "sha256": sha256(RESULT) if RESULT.exists() else None},
        "returncode": None if timed_out else completed.returncode,
        "stdout": stdout[-20000:],
        "stderr": stderr[-20000:],
        "network_requests_expected": 0,
    }
    RUN_RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(receipt, ensure_ascii=False))
    return 124 if timed_out else completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
