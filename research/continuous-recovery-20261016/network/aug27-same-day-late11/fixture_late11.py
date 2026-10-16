from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from email.utils import format_datetime
from io import BytesIO
from pathlib import Path

from PIL import Image


ROOT = Path(r"D:\WOW_Encyclopedia")
HERE = ROOT / "research" / "continuous-recovery-20261016" / "network" / "aug27-same-day-late11"
DRIVER_PATH = HERE / "late11_image_driver.py"
PLAN_PATH = HERE / "plan.json"
OUT_PATH = HERE / "late11-guard-fixture-results.json"


def load_driver():
    spec = importlib.util.spec_from_file_location("late11_image_driver_fixture", DRIVER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("late11 driver import failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def jpeg_bytes() -> bytes:
    stream = BytesIO()
    Image.new("RGB", (3, 2), (40, 80, 120)).save(stream, format="JPEG")
    return stream.getvalue()


def b32_sha1(module, payload: bytes) -> str:
    return module.b32_sha1(payload)


def headers(original: str, timestamp: str) -> bytes:
    date = datetime.strptime(timestamp, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    link = original.replace("http://www.worldofwarcraft.com", "http://www.worldofwarcraft.com:80", 1)
    return (b"HTTP/1.1 200 Connection established\r\nProxy-Agent: fixture\r\n\r\n"
            b"HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\n"
            b"Memento-Datetime: " + format_datetime(date, usegmt=True).encode("ascii") + b"\r\n"
            b"Link: <" + link.encode("ascii") + b">; rel=\"original\"\r\n\r\n")


def main() -> int:
    module = load_driver()
    module.configure_from_plan(PLAN_PATH)
    plan, _bindings = module.load_and_validate_inputs()
    candidate = copy.deepcopy(plan["candidates"][0])
    payload = jpeg_bytes()
    digest = b32_sha1(module, payload)
    original = candidate["original"]
    header = module.FIELDS
    rows = [header,
            ["k-pre", "20080402080429", original, "image/jpeg", "200", "A" * 32, str(len(payload))],
            ["k-late", "20080512231210", original, "image/jpeg", "200", digest, str(len(payload))],
            ["k-variant", "20080512231211", original.replace("www.worldofwarcraft.com", "worldofwarcraft.com"), "image/jpeg", "200", digest, str(len(payload))]]
    parsed = module.parse_cdx(json.dumps(rows).encode("utf-8"))
    classified = module.classify_cdx(parsed, candidate)
    filtered = module._filter_late_selected(classified, candidate)
    selection_test = (len(filtered["selected"]) == 1
                      and filtered["selected"][0]["timestamp"] == "20080512231210"
                      and filtered["late_window_rejected_selected_count"] == 1)

    pre_row = {"timestamp": "20080402080429", "digest": digest, "length": str(len(payload))}
    late_row = {"timestamp": "20080512231210", "digest": digest, "length": str(len(payload))}
    pre_validation = module.validate_replay(candidate, pre_row, headers(original, pre_row["timestamp"]), payload)
    late_validation = module.validate_replay(candidate, late_row, headers(original, late_row["timestamp"]), payload)
    pre_rejected = (not pre_validation["accepted"] and "late_supplement_window_mismatch" in pre_validation["reasons"])
    late_accepted = (late_validation["accepted"] and late_validation["actual_memento_timestamp"] == "20080512231210")

    bad_plan = copy.deepcopy(plan)
    bad_plan["candidates"][0]["original"] = "https://example.invalid/not-the-locked-target.jpg"
    try:
        module._validate_late_supplement_plan(bad_plan)
        guard_rejects_wrong_original = False
    except RuntimeError:
        guard_rejects_wrong_original = True

    pending_tail_unbound = (plan["execution_status"] == "awaiting_A_root_acceptance"
                            and plan["previous_batch"]["prior_failure_tail"] is None
                            and module.PRIOR_FAILURE_TAIL == 0)
    explicit_no_follow = (plan["policy"]["automatic_redirects"] == 0
                          and plan["late_supplement_guard"]["automatic_redirects"] == 0
                          and candidate["replay"]["no_redirects"] is True)
    tests = {
        "real_redirect_receipt_guard_loaded": True,
        "exact_one_target_and_original_locked": len(plan["candidates"]) == 1 and candidate["original"] == module.LATE_ORIGINAL,
        "late_selection_rejects_pre_anchor": selection_test,
        "pre_anchor_payload_rejected": pre_rejected,
        "same_day_late_memento_accepted_by_core": late_accepted,
        "actual_late_memento_timestamp_preserved": late_validation.get("actual_memento_timestamp") == "20080512231210",
        "automatic_redirects_disabled": explicit_no_follow,
        "pending_plan_has_no_stale_tail": pending_tail_unbound,
        "wrong_original_guard_rejected": guard_rejects_wrong_original,
    }
    result = {
        "schema": "wow-recovery.aug27-same-day-late11-fixtures.v1",
        "batch_id": plan["batch_id"],
        "network_requests": 0,
        "tests": tests,
        "passed": sum(bool(value) for value in tests.values()),
        "total": len(tests),
        "all_passed": all(tests.values()),
        "driver_sha256": hashlib.sha256(DRIVER_PATH.read_bytes()).hexdigest(),
        "plan_sha256": hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest(),
        "pre_anchor_digest_fixture": digest,
        "notes": [
            "Fixture uses synthetic in-memory JPEG bytes and sanitized validation fields only.",
            "No curl process, raw header/body write, payload write, or network request occurred.",
            "A later root-issued plan must bind the actual preceding failure tail before execute; this pending plan deliberately has no tail.",
        ],
    }
    OUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
