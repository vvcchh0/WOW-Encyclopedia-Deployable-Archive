#!/usr/bin/env python3
"""Root-gated, hard-timeout wrapper for the prepared v38 browser harness."""
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
INPUT = BROWSER_DIR.parent / "v38-browser-plan-r1.json"
HARNESS = BROWSER_DIR / "check_v38_images_toplist_r1.cjs"
RESULT = BROWSER_DIR / "results/v38-browser-r1.json"
RUN_RECEIPT = BROWSER_DIR / "v38-browser-run-receipt-r1.json"
SCREENSHOTS = BROWSER_DIR / "screenshots-r1"
NATIVE_INPUT = ROOT / "research/continuous-recovery-20261019/integration/v37/v37-native-ui-inputs.json"
NODE = Path(r"C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe")
GATE = ROOT / "research/continuous-recovery-20261019/publication/root-v38-browser-execute-go.json"
OUTPUT = ROOT / ".scratch/pages-resources-20261019-v38"
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


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise SystemExit(f"missing {label}: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{label} is not an object")
    return value


def gate_binding(gate: dict, rel: str, expected: str) -> bool:
    for row in gate.get("map_bindings", []):
        if row.get("path", "").replace("\\", "/") == rel and row.get("sha256") == expected:
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--go", action="store_true")
    parser.add_argument("--root-browser-go", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    if args.preflight and (args.go or args.root_browser_go):
        raise SystemExit("runner preflight cannot include browser execution flags")
    if not args.preflight and (not args.go or not args.root_browser_go):
        raise SystemExit("browser run requires --go --root-browser-go")
    if not NODE.is_file():
        raise SystemExit(f"bundled node runtime missing: {NODE}")
    if not INPUT.is_file() or not HARNESS.is_file():
        raise SystemExit("v38 browser plan/harness missing")
    if RESULT.exists() or RUN_RECEIPT.exists():
        raise SystemExit("refusing existing v38 browser result or receipt")
    plan = read_json(INPUT, "v38 browser plan")
    if plan.get("status") != "prepared_waiting_root_v38_browser_go":
        raise SystemExit("v38 browser plan is not waiting for root browser GO")
    if plan.get("network_requests") != 0 or plan.get("export_executed") is not True:
        raise SystemExit("v38 browser plan output/export gate failed")
    if plan.get("scope", {}).get("new_image_target_count") != 21 or plan.get("scope", {}).get("css_target_count") != 2 or plan.get("scope", {}).get("toplist_page_target_count") != 1 or plan.get("scope", {}).get("toplist_script_target_count") != 2 or plan.get("scope", {}).get("native_toggle_target_count") != 0:
        raise SystemExit("v38 browser plan coverage gate failed")
    output = under(OUTPUT, ROOT / ".scratch", "v38 output")
    provenance_rel = plan.get("output_provenance", {}).get("path", ".scratch/pages-resources-20261019-v38/export-provenance.json")
    provenance = under(ROOT / provenance_rel, ROOT, "v38 provenance")
    if not output.is_dir() or not provenance.is_file():
        raise SystemExit(f"promoted v38 output/provenance missing: {output}")
    if not plan.get("output_provenance", {}).get("sha256") or plan["output_provenance"]["sha256"] != sha256(provenance):
        raise SystemExit("v38 provenance SHA differs from browser plan")
    gate_required = {
        "research/continuous-recovery-20261019/integration/v38/v38-browser-plan-r1.json": sha256(INPUT),
        "research/continuous-recovery-20261019/integration/v38/browser/check_v38_images_toplist_r1.cjs": sha256(HARNESS),
        "research/continuous-recovery-20261019/integration/v38/browser/execute_v38_browser_r1.py": sha256(Path(__file__).resolve()),
        "research/continuous-recovery-20261019/integration/v37/v37-native-ui-inputs.json": sha256(NATIVE_INPUT),
    }
    if args.preflight:
        print(json.dumps({
            "status": "preflight_passed",
            "plan": {"path": str(INPUT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(INPUT)},
            "provenance": {"path": str(provenance.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(provenance)},
            "bindings": [{"path": rel, "sha256": value, "exists": Path(ROOT / rel).is_file()} for rel, value in gate_required.items()],
            "browser_started": False,
            "network_requests": 0,
        }, ensure_ascii=False))
        return 0
    gate = read_json(GATE, "root v38 browser GO gate")
    if gate.get("accepted") is not True or gate.get("browser_execute_go") is not True:
        raise SystemExit("root v38 browser GO gate is not accepted")
    for rel, expected in gate_required.items():
        if not gate_binding(gate, rel, expected):
            raise SystemExit(f"root browser gate binding mismatch: {rel}")
    started = time.monotonic()
    started_utc = now_utc()
    command = [str(NODE), str(HARNESS), "--go", "--root-browser-go", "--input", str(INPUT), "--result", str(RESULT), "--screenshots", str(SCREENSHOTS)]
    try:
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=MAX_SECONDS, check=False)
        timed_out = False
        stdout, stderr = completed.stdout or "", completed.stderr or ""
    except subprocess.TimeoutExpired as exc:
        completed = None
        timed_out = True
        stdout, stderr = str(exc.stdout or ""), str(exc.stderr or "")
    receipt = {
        "schema": "wow-recovery.integration.v38-browser-run-receipt-r1.v1",
        "status": "timed_out" if timed_out else ("completed" if completed and completed.returncode == 0 else "failed"),
        "started_utc": started_utc,
        "finished_utc": now_utc(),
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "timeout_seconds": MAX_SECONDS,
        "command": command,
        "input": {"path": str(INPUT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(INPUT)},
        "harness_sha256": sha256(HARNESS),
        "runner_sha256": sha256(Path(__file__).resolve()),
        "root_gate": {"path": str(GATE.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(GATE)},
        "output": {"path": ".scratch/pages-resources-20261019-v38", "provenance_sha256": sha256(provenance)},
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
