"""Fixed-path offline/GO adapter for frontier-news20f.

Only the imported frozen V3 module's in-memory NETWORK guard is redirected to
this packet.  The adapter accepts no arbitrary plan, URL, output, or receipt
paths.  ``--fixture`` never starts curl; ``--execute`` requires a separate
root GO receipt and leaves the parent process to enforce its 960-second
watchdog.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[5]
NETWORK_ROOT = ROOT / "research" / "continuous-recovery-20261019" / "network"
PACKET = NETWORK_ROOT / "frontier-news20f"
PLAN_PATH = PACKET / "plan.json"
BINDINGS_PATH = PACKET / "input-bindings.json"
OUTPUT_DIR = PACKET / "output"
FIXTURE_PATH = PACKET / "adapter" / "fixture-results.json"
FROZEN_DRIVER_PATH = ROOT / "research" / "continuous-recovery-20261018" / "network" / "reusable-image-driver-v3" / "reusable_image_driver.py"
GO_RECEIPT_PATH = ROOT / "research" / "continuous-recovery-20261019" / "publication" / "root-frontier-news20f-execute-go.json"
EXPECTED_DRIVER_SHA256 = "4a19422f0dd8e2f7e1ffdd088836c7ab80450afb91aeedc6cdb94fa4c6bfe955"
NETWORK_DEADLINE_UTC = "2026-10-19T13:15:00Z"
PARENT_WATCHDOG_SECONDS = 960
LATEST_SOURCE_PATH = ROOT / "research" / "continuous-recovery-20261019" / "publication" / "root-frontier-news20e-source-acceptance.json"
CONTROL_PATH = ROOT / "research" / "continuous-recovery-20261018" / "publication" / "root-control03-source-acceptance.json"


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
        raise RuntimeError("fixed frontier-news20f plan or bindings are missing")
    if not FROZEN_DRIVER_PATH.is_file():
        raise RuntimeError("frozen V3 driver is missing")
    if sha_file(FROZEN_DRIVER_PATH) != EXPECTED_DRIVER_SHA256:
        raise RuntimeError("frozen V3 driver SHA changed")
    plan = read_json(PLAN_PATH)
    bindings = read_json(BINDINGS_PATH)
    if plan.get("output_dir") != "research/continuous-recovery-20261019/network/frontier-news20f/output":
        raise RuntimeError("frontier-news20f output path is not fixed")
    if plan.get("candidate_count") != 20 or len(plan.get("candidates") or []) != 20:
        raise RuntimeError("frontier-news20f candidate count is not exactly twenty")
    expected_keys = [f"FRONTIER-NEWS20F-{rank:02d}" for rank in range(101, 121)]
    if [item.get("target_key") for item in plan["candidates"]] != expected_keys:
        raise RuntimeError("frontier-news20f target order/rank slice changed")
    expected_by_extension = {
        ".jpg": ("image/jpeg", "JPEG", False, "JPEG"),
        ".jpeg": ("image/jpeg", "JPEG", False, "JPEG"),
        ".gif": ("image/gif", "GIF", True, "GIF"),
        ".png": ("image/png", "PNG", False, "PNG"),
    }
    format_counts = {}
    for item in plan["candidates"]:
        original = str(item.get("original") or "")
        suffix = Path(urlsplit(original).path).suffix.lower()
        if suffix not in expected_by_extension:
            raise RuntimeError(f"unsupported expected format suffix: {item.get('target_key')}")
        mime, pillow, all_gif_frames, group = expected_by_extension[suffix]
        expected = item.get("expected") or {}
        if item.get("expected_mime") != [mime] or expected.get("mime_types") != [mime]:
            raise RuntimeError(f"top-level/nested expected MIME mismatch: {item.get('target_key')}")
        if expected.get("pillow_formats") != [pillow] or expected.get("all_gif_frames") is not all_gif_frames:
            raise RuntimeError(f"nested expected Pillow/GIF contract mismatch: {item.get('target_key')}")
        if expected.get("format_group") != group or expected.get("extension") != suffix:
            raise RuntimeError(f"nested expected format group mismatch: {item.get('target_key')}")
        format_counts[group] = format_counts.get(group, 0) + 1
    if plan.get("format_groups"):
        for group, count in format_counts.items():
            if (plan["format_groups"].get(group) or {}).get("count") != count:
                raise RuntimeError(f"format group count mismatch: {group}")
    policy = plan.get("policy") or {}
    expected_policy = {
        "max_originals": 20,
        "max_attempts": 80,
        "window_seconds": 900.0,
        "max_total_body_bytes": 33554432,
        "max_entity_body_bytes": 8388608,
        "transport_policy": "batch_after_direct_failure",
        "network_deadline_utc": NETWORK_DEADLINE_UTC,
        "prior_failure_tail": 0,
    }
    for key, value in expected_policy.items():
        if policy.get(key) != value:
            raise RuntimeError(f"frontier-news20f policy changed: {key}")
    previous = plan.get("previous_batch") or {}
    if previous.get("prior_failure_tail") != 0:
        raise RuntimeError("frontier-news20f prior failure tail is not zero")
    if previous.get("acceptance_receipt_path") != rel(LATEST_SOURCE_PATH):
        raise RuntimeError("frontier-news20f latest source is not news20e acceptance")
    if previous.get("control_gate_receipt_path") != rel(CONTROL_PATH):
        raise RuntimeError("frontier-news20f control gate changed")
    if bindings.get("plan_sha256") != sha_file(PLAN_PATH):
        raise RuntimeError("plan SHA mismatch in input-bindings")
    if bindings.get("driver_sha256") != EXPECTED_DRIVER_SHA256:
        raise RuntimeError("driver SHA mismatch in input-bindings")
    if bindings.get("adapter_sha256") != sha_file(Path(__file__).resolve()):
        raise RuntimeError("adapter SHA mismatch in input-bindings")
    return plan | {"_bindings": bindings}


def load_frozen_driver():
    spec = importlib.util.spec_from_file_location("frontier_news20f_frozen_v3", FROZEN_DRIVER_PATH)
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
    previous = plan["previous_batch"]
    tail_path = ROOT / previous["tail_receipt_path"]
    if sha_file(tail_path) != previous["tail_receipt_sha256"]:
        raise RuntimeError("latest news20e source receipt changed")
    tail = read_json(tail_path)
    if tail.get("accepted") is not True or tail.get("failure_streak_end") != 0:
        raise RuntimeError("latest news20e source receipt is not accepted zero-tail")
    gate_path = ROOT / previous["control_gate_receipt_path"]
    if sha_file(gate_path) != previous["control_gate_receipt_sha256"]:
        raise RuntimeError("CONTROL03 receipt changed")
    gate = read_json(gate_path)
    if not (gate.get("accepted") is True and gate.get("resume_gate_passed") is True and gate.get("control_final_streak") == 0):
        raise RuntimeError("CONTROL03 does not authorize zero tail")


def check_go_receipt(plan: dict) -> dict:
    if not GO_RECEIPT_PATH.is_file():
        raise RuntimeError(f"root GO receipt is required: {rel(GO_RECEIPT_PATH)}")
    receipt = read_json(GO_RECEIPT_PATH)
    expected = {
        "accepted": True,
        "root_go": True,
        "plan_sha256": sha_file(PLAN_PATH),
        "driver_sha256": EXPECTED_DRIVER_SHA256,
        "adapter_sha256": sha_file(Path(__file__).resolve()),
        "plan_path": rel(PLAN_PATH),
        "latest_source_acceptance_sha256": plan["previous_batch"]["acceptance_receipt_sha256"],
        "control_gate_sha256": plan["previous_batch"]["control_gate_receipt_sha256"],
        "prior_failure_tail": 0,
        "resume_gate_passed": True,
        "control_final_streak": 0,
        "network_deadline_utc": NETWORK_DEADLINE_UTC,
        "parent_watchdog_seconds": PARENT_WATCHDOG_SECONDS,
    }
    for key, value in expected.items():
        if receipt.get(key) != value:
            raise RuntimeError(f"root GO receipt mismatch: {key}")
    return receipt


def check_start_window() -> None:
    if datetime.now(timezone.utc) + timedelta(seconds=PARENT_WATCHDOG_SECONDS) >= parse_utc(NETWORK_DEADLINE_UTC):
        raise RuntimeError("less than the 960-second parent watchdog remains before the network deadline")


def check_output_empty() -> None:
    if OUTPUT_DIR.exists() and any(OUTPUT_DIR.iterdir()):
        raise RuntimeError("frontier-news20f output is nonempty; refusing duplicate execution")


def run_fixture() -> dict:
    plan = require_fixed_inputs()
    check_tail_and_control(plan)
    module = load_frozen_driver()
    result = module.run_fixtures(FIXTURE_PATH)
    summary = {
        "adapter": rel(Path(__file__).resolve()),
        "mode": "fixture",
        "network_requests": result.get("network_requests"),
        "all_passed": result.get("all_passed"),
        "test_count": len(result.get("tests", {})),
        "failed_tests": [name for name, value in result.get("tests", {}).items() if not value],
        "fixture_path": rel(FIXTURE_PATH),
        "fixture_sha256": sha_file(FIXTURE_PATH),
        "driver_sha256": EXPECTED_DRIVER_SHA256,
        "plan_sha256": sha_file(PLAN_PATH),
        "candidate_count": plan.get("candidate_count"),
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
    parser = argparse.ArgumentParser(description="Fixed frontier-news20f V3 path adapter")
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
    except Exception as exc:
        print(json.dumps({"status": "refused", "error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
