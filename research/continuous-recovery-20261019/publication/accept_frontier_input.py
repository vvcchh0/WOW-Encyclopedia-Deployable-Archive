"""Bind a root-reviewed shortlist slice to one bounded exact-image execution."""
import argparse
import ast
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "research/continuous-recovery-20261019"
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
READ = lambda p: json.loads(p.read_bytes())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", required=True)
    parser.add_argument("--plan-sha", required=True)
    parser.add_argument("--adapter-sha", required=True)
    parser.add_argument("--first-rank", required=True, type=int)
    parser.add_argument("--last-rank", required=True, type=int)
    parser.add_argument("--latest-source", required=True)
    args = parser.parse_args()
    assert re.fullmatch(r"frontier-[a-z0-9-]+", args.packet)
    packet = RUN / "network" / args.packet
    out = RUN / f"publication/root-{args.packet}-execute-go.json"
    assert not out.exists()
    output_dir = packet / "output"
    assert not output_dir.exists() or not any(output_dir.iterdir())
    path = packet / "plan.json"
    assert SHA(path) == args.plan_sha
    plan = READ(path)
    shortlist_path = RUN / "local-audit/resource-frontier-v33-r2/resource-frontier-candidates.json"
    assert SHA(shortlist_path) == "ee9c6240c76e14ad80c3aac2cdd655970499bb3ac8ee6592295f8f39e95c686a"
    selected = [r for r in READ(shortlist_path)["candidate_shortlist"]
                if args.first_rank <= r["rank"] <= args.last_rank]
    assert 1 <= len(selected) <= 20 and len(selected) == args.last_rank - args.first_rank + 1
    assert all(r["state"] == "uncovered" for r in selected)
    assert [r["requested_url"] for r in selected] == [r["original"] for r in plan["candidates"]]
    assert len(selected) == plan["candidate_count"]
    policy = plan["policy"]
    assert (policy["max_attempts"], policy["window_seconds"], policy["max_total_body_bytes"],
            policy["max_entity_body_bytes"]) == (80, 900, 33554432, 8388608)
    assert policy["tls_verification"] and policy["direct_first"] and policy["automatic_redirects"] == 0
    assert policy["min_dispatch_seconds"] >= 5.25 and policy["min_request_start_seconds"] >= 5
    assert policy["disk_floor_bytes"] == 11005853696
    assert policy["network_deadline_utc"] == "2026-10-19T13:15:00Z"
    for entry in plan["input_bindings"].values():
        bound = (ROOT / entry["path"]).resolve()
        bound.relative_to(ROOT)
        assert SHA(bound) == entry["sha256"]
    for row in plan["candidates"]:
        evidence = row["source_evidence"]
        page = (ROOT / evidence["path"]).resolve()
        page.relative_to(ROOT / ".scratch/pages-resources-20261018-v33")
        assert SHA(page) == evidence["sha256"]
        line = page.read_text(encoding="utf-8").splitlines()[evidence["line"] - 1]
        assert row["original"] in line or quote(row["original"], safe="") in line
        source15 = row["source_page_context"]["source15_page"]
        source15_page = ROOT / source15["path"]
        assert SHA(source15_page) == source15["sha256"]
        source15_lines = source15_page.read_text(encoding="utf-8").splitlines()
        assert any(row["original"] in source15_lines[n - 1] or quote(row["original"], safe="") in source15_lines[n - 1]
                   for n in source15["matched_lines"])
    previous = plan["previous_batch"]
    assert previous["acceptance_receipt_path"] == args.latest_source
    tail_path = ROOT / args.latest_source
    tail = READ(tail_path)
    assert tail["accepted"] and tail["failure_streak_end"] == 0
    assert SHA(tail_path) == previous["acceptance_receipt_sha256"]
    adapter = packet / f"adapter/{args.packet.replace('-', '_')}_adapter.py"
    assert SHA(adapter) == args.adapter_sha
    tree = ast.parse(adapter.read_text(encoding="utf-8"))
    writes = [ast.unparse(n.targets[0]) for n in ast.walk(tree)
              if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Attribute)
              and ast.unparse(n.targets[0]).startswith("module.")]
    assert writes == ["module.NETWORK"]
    fixtures = READ(packet / "adapter/fixture-results.json")
    assert fixtures["all_passed"] and fixtures["network_requests"] == 0 and len(fixtures["tests"]) == 32
    dedup = READ(packet / "dedupe-audit.json")
    assert dedup["network_requests"] == 0
    matches = dedup["independent_execution_surface_scan"]["actual_execution_or_cdx_matches"]
    assert set(matches) == {r["original"] for r in plan["candidates"]}
    assert not any(matches.values())
    free = shutil.disk_usage(ROOT).free
    assert free >= 11005853696
    receipt = {"accepted": True, "root_go": True,
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "plan_path": path.relative_to(ROOT).as_posix(), "plan_sha256": SHA(path),
        "driver_sha256": "4a19422f0dd8e2f7e1ffdd088836c7ab80450afb91aeedc6cdb94fa4c6bfe955",
        "adapter_sha256": SHA(adapter),
        "latest_source_acceptance_sha256": SHA(tail_path),
        "control_gate_sha256": previous["control_gate_receipt_sha256"],
        "prior_failure_tail": 0, "resume_gate_passed": True, "control_final_streak": 0,
        "network_deadline_utc": "2026-10-19T13:15:00Z", "parent_watchdog_seconds": 960,
        "disk_free_before_bytes": free, "shortlist_ranks": [args.first_rank, args.last_rank],
        "scope": "One execution only; exact reviewed shortlist, max80 attempts/900s/32MiB; external960s parent watchdog required. No automatic retry."}
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"root_go": True, "targets": len(selected), "packet": args.packet, "disk_free_bytes": free}))


if __name__ == "__main__":
    main()
