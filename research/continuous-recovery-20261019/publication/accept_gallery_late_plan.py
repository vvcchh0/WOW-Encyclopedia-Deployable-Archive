"""Root input review for a new, finite, CDX-only gallery prefix packet."""
import argparse
import ast
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
READ = lambda p: json.loads(p.read_bytes())
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def functions(path):
    tree = ast.parse(path.read_text("utf-8"))
    return {node.name: ast.dump(node, include_attributes=False) for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--packet", required=True)
    p.add_argument("--previous-packet", required=True)
    p.add_argument("--driver-sha", required=True)
    p.add_argument("--plan-sha", required=True)
    args = p.parse_args()
    assert re.fullmatch(r"gallery-late-rest\d+[a-z]", args.packet)
    directory = PUB.parent / "network" / args.packet
    plan_path = directory / "plan.json"
    driver_path = directory / (args.packet.replace("-", "_") + "_driver_v1.py")
    previous_driver = PUB.parent / "network" / args.previous_packet / (args.previous_packet.replace("-", "_") + "_driver_v1.py")
    assert SHA(plan_path) == args.plan_sha and SHA(driver_path) == args.driver_sha
    assert shutil.disk_usage(ROOT).free >= 11005853696
    assert not any((directory / name).exists() for name in ("batch-report.json", "attempt-records.json", "parent-execution-receipt.json"))
    before, after = functions(previous_driver), functions(driver_path)
    assert set(before) == set(after)
    changes = sorted(k for k in before if before[k] != after[k])
    assert set(changes) <= {"validate_inputs", "fixture", "plan_for_run"}, changes
    previous = PUB / f"root-{args.previous_packet}-source-acceptance.json"
    prior = READ(previous)
    assert prior["accepted"] and prior["is_network_batch"] and prior["failure_streak_end"] == 0
    state = READ(PUB.parent / "status.json")
    assert state["latest_network_batch"] == args.previous_packet
    assert state["latest_failure_tail"] == 0 and not state.get("in_flight_network_batch")
    plan = READ(plan_path)
    row = plan["input_bindings"]["latest_global_source_acceptance"]
    assert (ROOT / row["path"]).resolve() == previous.resolve() and row["sha256"] == SHA(previous)
    for row in plan["input_bindings"].values():
        assert SHA(ROOT / row["path"]) == row["sha256"], row["path"]
    policy = plan["policy"]
    for key, value in {"max_requests": 24, "max_attempts": 24, "window_seconds": 900.0,
                       "max_total_body_bytes": 33554432, "max_entity_body_bytes": 8388608,
                       "min_dispatch_seconds": 5.25, "min_request_start_seconds": 5.0,
                       "disk_floor_bytes": 11005853696, "direct_first": True,
                       "proxy": "http://127.0.0.1:7890", "tls_verification": True,
                       "automatic_redirects": 0, "stop_http_codes": [429, 503],
                       "cooldown_seconds": 120, "stop_on_five_consecutive_transport_failures": True,
                       "outer_watchdog_seconds": 960, "no_payload_replay": True}.items():
        assert policy[key] == value, key
    assert plan["index_only"] and not plan["payload_replay"] and plan["no_filename_guess"]
    assert plan["network_deadline_utc"] == "2026-10-19T13:15:00Z"
    assert datetime.now(timezone.utc) + timedelta(seconds=960) < datetime(2026, 10, 19, 13, 15, tzinfo=timezone.utc)
    completed = set()
    for path in PUB.glob("root-gallery-late-rest*-source-acceptance.json"):
        record = READ(path)
        assert record["accepted"]
        completed.update(row["prefix"] for row in record["results"] if row["complete_within_response"])
    # These three previously accepted windows are not reopened by this run.
    completed.update("http://www.worldofwarcraft.com/info/dungeons/images/" + segment + "/" for segment in ("karazhan", "blacktemple", "zulaman"))
    candidates = plan["candidates"]
    assert 1 <= len(candidates) <= 10 and len({r["prefix"] for r in candidates}) == len(candidates)
    for c in candidates:
        assert c["prefix"] not in completed, c["prefix"]
        w = c["query_window"]
        assert (w["from"], w["to"], w["limit"], w["matchType"], w["showResumeKey"]) == ("20080512210045", "20101207235959", 500, "prefix", True)
        source = c["source_evidence"]
        page = ROOT / source["path"]
        assert SHA(page) == source["sha256"]
        assert source["addshots_literal"] in page.read_text("utf-8").splitlines()[source["addshots_line"] - 1]
        assert c["prefix"] == "http://www.worldofwarcraft.com" + source["source_directory"]
    spec = importlib.util.spec_from_file_location("root_gallery_input_" + args.packet.replace("-", "_"), driver_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    _, normalized, _ = module.validate_inputs()
    assert len(normalized) == len(candidates)
    fixture = module.fixture()
    assert fixture["all_passed"] and fixture["network_requests"] == 0
    fixture_path = directory / "fixture-results.json"
    assert READ(fixture_path)["all_passed"]
    receipt = {"accepted": True, "root_go": True, "checked_utc": datetime.now(timezone.utc).isoformat(),
               "driver_sha256": args.driver_sha, "plan_sha256": args.plan_sha,
               "fixture_before_execution_sha256": SHA(fixture_path),
               "latest_network_source_path": previous.relative_to(ROOT).as_posix(), "latest_network_source_sha256": SHA(previous),
               "prior_failure_tail": 0, "target_count": len(candidates), "max_requests": 24,
               "max_seconds": 900, "max_body_bytes": 33554432, "outer_parent_watchdog_seconds": 960,
               "index_only": True, "payload_replays_allowed": 0, "network_deadline_utc": plan["network_deadline_utc"],
               "changed_functions": changes, "fixture_passed": fixture["passed"], "fixture_total": fixture["total"],
               "scope": "One new source-directory prefix packet only. Root independently checks actual source hashes/literals, all input bindings, fresh global tail, no duplicate accepted windows, bounded policy, unchanged transport/parser/identity AST and offline fixtures."}
    out = PUB / f"root-{args.packet}-execute-go.json"
    assert not out.exists()
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"accepted": True, "target_count": len(candidates), "changed_functions": changes, "fixture_passed": fixture["passed"]}))


if __name__ == "__main__":
    main()
