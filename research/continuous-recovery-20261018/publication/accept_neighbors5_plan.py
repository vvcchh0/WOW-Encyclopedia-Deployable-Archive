"""Review the exact five-neighbor execution plan without network access."""
import hashlib
import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "research/continuous-recovery-20261018"
DIRECTORY = BASE / "network/neighbors5-v3"
OUT = BASE / "publication/root-neighbors5-plan-acceptance.json"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_bytes())

def objects(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from objects(value)
    elif isinstance(node, list):
        for value in node:
            yield from objects(value)

def main():
    assert not OUT.exists()
    driver = BASE / "network/reusable-image-driver-v3/reusable_image_driver.py"
    core = read(BASE / "publication/root-v3-driver-fixture-adaptation-acceptance.json")
    assert core["accepted"] and sha(driver) == core["new_driver_sha256"]
    path = DIRECTORY / "plan.json"
    plan, bindings = read(path), read(DIRECTORY / "input-bindings.json")
    assert bindings["plan_sha256"] == sha(path) and bindings["driver_sha256"] == sha(driver)
    pending = read(ROOT / "research/focused-recovery-20261016-2301/pending-neighbors5.json")
    expected = {item["original"] for item in pending["items"]}
    assert len(expected) == 5 and {item["original"] for item in plan["candidates"]} == expected
    assert plan["candidate_count"] == len(plan["candidates"]) == 5
    policy = plan["policy"]
    assert policy["max_attempts"] <= 24 and policy["window_seconds"] <= 240
    assert policy["max_total_body_bytes"] <= 16 * 1024**2 and policy["max_entity_body_bytes"] <= 8 * 1024**2
    assert policy["min_dispatch_seconds"] >= 5.25 and policy["min_request_start_seconds"] >= 5
    assert policy["disk_floor_bytes"] >= 11005853696
    assert policy["transport_policy"] == "batch_after_direct_failure" and policy["direct_first"] is True
    assert policy["proxy"] == "http://127.0.0.1:7890" and policy["tls_verification"] is True
    assert policy["automatic_redirects"] == 0 and set(policy["stop_http_codes"]) == {429, 503}
    assert policy["cooldown_seconds"] >= 120 and policy["prior_failure_tail"] == 0
    assert policy["from"] == "20000101000000" and policy["to"] == "20080512210044"
    for entry in plan["input_bindings"].values():
        bound = (ROOT / entry["path"]).resolve()
        bound.relative_to(ROOT.resolve())
        assert sha(bound) == entry["sha256"]
    latest = read(ROOT / plan["previous_batch"]["acceptance_receipt_path"])
    assert latest["accepted"] and latest["failure_streak_end"] == 0
    assert latest["source_responses"] >= 4 and latest["requests"] == 5
    prefix = read(ROOT / "research/continuous-recovery-20261016/publication/root-gallery-prefix04-acceptance.json")
    frozen_rows = [x for x in objects(prefix) if {"original", "timestamp", "digest", "mimetype", "statuscode"} <= set(x)]
    details = []
    for candidate in plan["candidates"]:
        evidence = candidate["source_evidence"]
        source = ROOT / evidence["path"]
        assert sha(source) == evidence["sha256"]
        assert candidate["original"] in source.read_text(encoding="utf-8").splitlines()[evidence["line"] - 1]
        assert evidence["row"] in frozen_rows
        fallback = candidate.get("known_positive_cache_rows", [])
        assert fallback and all(row in frozen_rows for row in fallback)
        assert candidate.get("fallback_label") == "best_known_cached_not_latest"
        assert candidate["cdx_mode"] == "fresh" and candidate["query"]["matchType"] == "exact"
        assert candidate["query"]["collapse"] is False and candidate["query"]["showResumeKey"] is True
        assert candidate["replay"]["no_redirects"] is True and candidate["replay"]["verify_tls"] is True
        details.append({"original": candidate["original"], "bound_positive_rows": len(fallback)})
    spec = importlib.util.spec_from_file_location("reviewed_driver_v3", driver)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.configure_from_plan(path)
    module.load_and_validate_inputs()
    free = shutil.disk_usage(ROOT).free
    assert free >= 11005853696
    result = {"accepted": True, "checked_utc": datetime.now(timezone.utc).isoformat(),
              "plan_sha256": sha(path), "bindings_sha256": sha(DIRECTORY / "input-bindings.json"),
              "driver_sha256": sha(driver), "targets": details, "network_requests": 0,
              "disk_free_bytes": free, "one_bounded_batch_eligible": True,
              "scope": "Exact pending set, source row membership, literal lines, driver inputs and limits. Execution requires a separate root GO."}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))

if __name__ == "__main__":
    main()
