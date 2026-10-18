"""Root review of one exact-image plan against an explicitly selected URL set."""
import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "research/continuous-recovery-20261018"

def read(path):
    return json.loads(path.read_bytes())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def local(value):
    path = (ROOT / value).resolve()
    path.relative_to(ROOT.resolve())
    return path

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--originals", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-attempts", type=int, default=24)
    parser.add_argument("--max-seconds", type=float, default=240)
    args = parser.parse_args()
    path, selected, output = local(args.plan), local(args.originals), local(args.output)
    path.relative_to(BASE / "network")
    output.relative_to(BASE / "publication")
    assert not output.exists()
    plan, expected = read(path), read(selected)
    assert isinstance(expected, list) and 1 <= len(expected) <= 20 and len(expected) == len(set(expected))
    assert plan["candidate_count"] == len(plan["candidates"]) == len(expected)
    assert {item["original"] for item in plan["candidates"]} == set(expected)
    current = read(BASE / "status.json")
    latest_path = BASE / current["latest_source_acceptance"]
    latest = read(latest_path)
    tail = latest["failure_streak_end"]
    assert current["latest_failure_tail"] == tail < 5
    previous = plan["previous_batch"]
    receipt_path = previous.get("acceptance_receipt_path") or previous.get("tail_receipt_path")
    assert local(receipt_path) == latest_path.resolve(), "plan did not bind latest actual batch"
    assert previous["prior_failure_tail"] == tail
    policy = plan["policy"]
    assert policy["prior_failure_tail"] == tail
    assert policy["max_attempts"] <= args.max_attempts <= 40
    assert policy["window_seconds"] <= args.max_seconds <= 600
    assert policy["max_total_body_bytes"] <= 16 * 1024**2 and policy["max_entity_body_bytes"] <= 8 * 1024**2
    assert policy["min_dispatch_seconds"] >= 5.25 and policy["min_request_start_seconds"] >= 5
    assert policy["disk_floor_bytes"] >= 11005853696
    assert policy["direct_first"] is True and policy["transport_policy"] == "batch_after_direct_failure"
    assert policy["proxy"] == "http://127.0.0.1:7890" and policy["tls_verification"] is True
    assert policy["automatic_redirects"] == 0 and set(policy["stop_http_codes"]) == {429, 503}
    assert policy["cooldown_seconds"] >= 120
    assert policy["from"] == "20130612000000" and policy["to"] == "20130612235959"
    bindings_path = path.with_name("input-bindings.json")
    bindings = read(bindings_path)
    driver = local(bindings["driver_path"])
    accepted_driver = read(BASE / "publication/root-late-thumbnail-driver-fixture-adaptation-acceptance.json")
    assert accepted_driver["accepted"] and sha(driver) == accepted_driver["new_driver_sha256"]
    assert bindings["plan_sha256"] == sha(path) and bindings["driver_sha256"] == sha(driver)
    for candidate in plan["candidates"]:
        evidence = candidate["source_evidence"]
        source = local(evidence["path"])
        assert sha(source) == evidence["sha256"]
        line = source.read_text(encoding="utf-8").splitlines()[evidence["line"] - 1]
        literal = evidence["literal"]
        assert literal == candidate["original"]
        assert literal in line or quote(literal, safe="") in line
        assert candidate["query"]["matchType"] == "exact" and candidate["query"]["collapse"] is False
        assert candidate["query"]["showResumeKey"] is True
        # Any fallback needs a separate row-membership review; unreviewed
        # positive rows must not be smuggled into a normal discovery batch.
        assert not candidate.get("known_positive_cache_rows")
        assert candidate["replay"]["no_redirects"] is True and candidate["replay"]["verify_tls"] is True
    spec = importlib.util.spec_from_file_location("root_reviewed_exact_driver", driver)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.configure_from_plan(path)
    module.load_and_validate_inputs()
    free = shutil.disk_usage(ROOT).free
    assert free >= 11005853696
    result = {"accepted": True, "checked_utc": datetime.now(timezone.utc).isoformat(),
              "plan": path.relative_to(ROOT).as_posix(), "plan_sha256": sha(path),
              "bindings_sha256": sha(bindings_path), "driver_sha256": sha(driver),
              "selected_originals_sha256": sha(selected), "selected_originals": expected,
              "latest_source_acceptance_sha256": sha(latest_path), "starting_failures": tail,
              "max_requests": policy["max_attempts"], "max_seconds": policy["window_seconds"],
              "network_requests": 0, "disk_free_bytes": free, "one_bounded_batch_eligible": True}
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))

if __name__ == "__main__":
    main()
