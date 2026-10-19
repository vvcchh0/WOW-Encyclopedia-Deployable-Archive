"""Fixed-path adapter for the frontier-news04 packet.

This module imports the frozen 20261018 V3 driver by SHA and changes only its
in-memory NETWORK module global to the 20261019 network root.  It deliberately
accepts no plan, output, URL, or receipt path arguments.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
NETWORK_ROOT = ROOT / "research" / "continuous-recovery-20261019" / "network"
PACKET = NETWORK_ROOT / "frontier-news04"
PLAN_PATH = PACKET / "plan.json"
BINDINGS_PATH = PACKET / "input-bindings.json"
OUTPUT_DIR = PACKET / "output"
ADAPTER_FIXTURE_PATH = PACKET / "adapter" / "fixture-results.json"
FROZEN_DRIVER_PATH = ROOT / "research" / "continuous-recovery-20261018" / "network" / "reusable-image-driver-v3" / "reusable_image_driver.py"
GO_RECEIPT_PATH = ROOT / "research" / "continuous-recovery-20261019" / "publication" / "root-frontier-news04-execute-go.json"
EXPECTED_DRIVER_SHA256 = "4a19422f0dd8e2f7e1ffdd088836c7ab80450afb91aeedc6cdb94fa4c6bfe955"
NETWORK_DEADLINE_UTC = "2026-10-19T13:15:00Z"
PARENT_WATCHDOG_SECONDS = 300


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def require_fixed_inputs() -> dict:
    if not PLAN_PATH.is_file() or not BINDINGS_PATH.is_file():
        raise RuntimeError("fixed frontier-news04 plan or bindings are missing")
    if not FROZEN_DRIVER_PATH.is_file():
        raise RuntimeError("frozen V3 driver is missing")
    actual_driver_sha = sha_file(FROZEN_DRIVER_PATH)
    if actual_driver_sha != EXPECTED_DRIVER_SHA256:
        raise RuntimeError(f"frozen V3 driver SHA changed: {actual_driver_sha}")
    plan = read_json(PLAN_PATH)
    bindings = read_json(BINDINGS_PATH)
    if plan.get("output_dir") != "research/continuous-recovery-20261019/network/frontier-news04/output":
        raise RuntimeError("frontier-news04 output path is not the fixed packet output")
    if plan.get("candidate_count") != 4 or len(plan.get("candidates") or []) != 4:
        raise RuntimeError("frontier-news04 candidate count is not exactly four")
    if plan.get("policy", {}).get("network_deadline_utc") != NETWORK_DEADLINE_UTC:
        raise RuntimeError("frontier-news04 network deadline changed")
    if plan.get("previous_batch", {}).get("prior_failure_tail") != 0:
        raise RuntimeError("frontier-news04 prior failure tail is not zero")
    return plan | {"_bindings": bindings}


def load_frozen_driver():
    """Load V3, redirecting only its in-memory path guard."""
    spec = importlib.util.spec_from_file_location("frontier_news04_frozen_v3", FROZEN_DRIVER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load frozen V3 module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.sha_file(FROZEN_DRIVER_PATH) != EXPECTED_DRIVER_SHA256:
        raise RuntimeError("frozen V3 SHA changed after import")
    module.NETWORK = NETWORK_ROOT
    module.configure_from_plan(PLAN_PATH)
    module.load_and_validate_inputs()
    return module


def check_tail_and_control(plan: dict) -> None:
    previous = plan.get("previous_batch") or {}
    tail_path = (ROOT / previous["tail_receipt_path"]).resolve()
    if sha_file(tail_path) != previous.get("tail_receipt_sha256"):
        raise RuntimeError("latest source tail receipt changed")
    tail = read_json(tail_path)
    if tail.get("accepted") is not True or tail.get("failure_streak_end") != 0:
        raise RuntimeError("latest source tail receipt is not accepted zero")
    gate_path = (ROOT / previous["control_gate_receipt_path"]).resolve()
    if sha_file(gate_path) != previous.get("control_gate_receipt_sha256"):
        raise RuntimeError("control gate receipt changed")
    gate = read_json(gate_path)
    if not (gate.get("accepted") is True and gate.get("resume_gate_passed") is True and gate.get("control_final_streak") == 0):
        raise RuntimeError("control gate does not authorize zero tail")


def check_go_receipt(plan: dict) -> dict:
    if not GO_RECEIPT_PATH.is_file():
        raise RuntimeError(f"root GO receipt is required: {rel(GO_RECEIPT_PATH)}")
    receipt = read_json(GO_RECEIPT_PATH)
    adapter_sha = sha_file(Path(__file__).resolve())
    expected = {
        "accepted": True,
        "root_go": True,
        "plan_sha256": sha_file(PLAN_PATH),
        "driver_sha256": EXPECTED_DRIVER_SHA256,
        "adapter_sha256": adapter_sha,
        "plan_path": rel(PLAN_PATH),
        "latest_source_acceptance_sha256": plan["previous_batch"]["acceptance_receipt_sha256"],
        "control_gate_sha256": plan["previous_batch"]["control_gate_receipt_sha256"],
        "prior_failure_tail": 0,
        "resume_gate_passed": True,
        "control_final_streak": 0,
        "network_deadline_utc": NETWORK_DEADLINE_UTC,
    }
    for key, value in expected.items():
        if receipt.get(key) != value:
            raise RuntimeError(f"root GO receipt mismatch: {key}")
    return receipt


def check_start_window() -> None:
    now = datetime.now(timezone.utc)
    deadline = parse_utc(NETWORK_DEADLINE_UTC)
    if now + timedelta(seconds=PARENT_WATCHDOG_SECONDS) >= deadline:
        raise RuntimeError("less than the 300-second parent watchdog remains before the network deadline")


def check_output_empty() -> None:
    if OUTPUT_DIR.exists() and any(OUTPUT_DIR.iterdir()):
        raise RuntimeError("frontier-news04 output is nonempty; refusing duplicate execution")


def run_fixture() -> dict:
    plan = require_fixed_inputs()
    check_tail_and_control(plan)
    module = load_frozen_driver()
    result = module.run_fixtures(ADAPTER_FIXTURE_PATH)
    summary = {
        "adapter": rel(Path(__file__).resolve()),
        "mode": "fixture",
        "network_requests": result.get("network_requests"),
        "all_passed": result.get("all_passed"),
        "test_count": len(result.get("tests", {})),
        "failed_tests": [name for name, value in result.get("tests", {}).items() if not value],
        "fixture_path": rel(ADAPTER_FIXTURE_PATH),
        "fixture_sha256": sha_file(ADAPTER_FIXTURE_PATH),
        "driver_sha256": EXPECTED_DRIVER_SHA256,
        "plan_sha256": sha_file(PLAN_PATH),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def execute() -> dict:
    plan = require_fixed_inputs()
    check_tail_and_control(plan)
    receipt = check_go_receipt(plan)
    check_start_window()
    check_output_empty()
    module = load_frozen_driver()
    result = module.execute()
    print(json.dumps({
        "adapter": rel(Path(__file__).resolve()),
        "mode": "execute",
        "go_receipt": rel(GO_RECEIPT_PATH),
        "plan_sha256": sha_file(PLAN_PATH),
        "driver_sha256": EXPECTED_DRIVER_SHA256,
        "adapter_sha256": sha_file(Path(__file__).resolve()),
        "result": result,
    }, ensure_ascii=False, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Fixed frontier-news04 V3 path adapter")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fixture", action="store_true", help="run the fixed offline fixture only")
    group.add_argument("--execute", action="store_true", help="execute only after the fixed root GO receipt exists")
    args = parser.parse_args()
    try:
        if args.fixture:
            result = run_fixture()
            return 0 if result.get("all_passed") and result.get("network_requests") == 0 else 1
        execute()
        return 0
    except Exception as exc:  # Keep refusal explicit and side-effect free.
        print(json.dumps({"status": "refused", "error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
