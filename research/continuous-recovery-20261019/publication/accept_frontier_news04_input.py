"""Independently bind the four exact news targets and the minimal path adapter."""
import ast
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "research/continuous-recovery-20261019"
PACKET = RUN / "network/frontier-news04"
OUT = RUN / "publication/root-frontier-news04-execute-go.json"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OUT.exists() and not (PACKET / "output").exists()
    plan_path = PACKET / "plan.json"
    plan = json.loads(plan_path.read_bytes())
    assert sha(plan_path) == "fc3f421191d9f88df03675c1bf7833b383ad4a5dede269e9ed988ea3833198a5"
    expected = ["http://www.worldofwarcraft.com/contests/beowulf/images/beowulf_news.jpg",
                "http://www.worldofwarcraft.com/news/images/04-06/european-beta/signups.jpg",
                "http://www.worldofwarcraft.com/news/images/04-06/fanart/fanart01.jpg",
                "http://www.worldofwarcraft.com/news/images/04-06/fanart/fanart02.jpg"]
    assert [r["original"] for r in plan["candidates"]] == expected
    policy = plan["policy"]
    assert (policy["max_attempts"], policy["window_seconds"], policy["max_total_body_bytes"],
            policy["max_entity_body_bytes"]) == (16, 240, 16777216, 8388608)
    assert policy["tls_verification"] and policy["direct_first"]
    assert policy["min_dispatch_seconds"] >= 5.25 and policy["min_request_start_seconds"] >= 5
    assert policy["disk_floor_bytes"] == 11005853696
    for entry in plan["input_bindings"].values():
        path = (ROOT / entry["path"]).resolve()
        path.relative_to(ROOT)
        assert sha(path) == entry["sha256"]
    for row in plan["candidates"]:
        evidence = row["source_evidence"]
        page = ROOT / evidence["path"]
        assert sha(page) == evidence["sha256"]
        line = page.read_text(encoding="utf-8").splitlines()[evidence["line"] - 1]
        assert row["original"] in line or quote(row["original"], safe="") in line
        assert not row["source_page_context"]["historical_execution_evidence"]
    previous = plan["previous_batch"]
    tail = json.loads((ROOT / previous["tail_receipt_path"]).read_bytes())
    assert tail["accepted"] and tail["failure_streak_end"] == 0
    adapter = PACKET / "adapter/frontier_news04_adapter.py"
    assert sha(adapter) == "ece3fb63ae1dc2b354ce4eb76c2cc9254a25c296583cf9b98fe446d8ccde6dc4"
    tree = ast.parse(adapter.read_text(encoding="utf-8"))
    writes = [ast.unparse(n.targets[0]) for n in ast.walk(tree)
              if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Attribute)
              and ast.unparse(n.targets[0]).startswith("module.")]
    assert writes == ["module.NETWORK"]
    fixtures = PACKET / "adapter/fixture-results.json"
    data = json.loads(fixtures.read_bytes())
    assert data["all_passed"] and data["network_requests"] == 0 and len(data["tests"]) == 32
    free = shutil.disk_usage(ROOT).free
    assert free >= 11005853696
    receipt = {"accepted": True, "root_go": True,
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "plan_path": plan_path.relative_to(ROOT).as_posix(), "plan_sha256": sha(plan_path),
        "driver_sha256": "4a19422f0dd8e2f7e1ffdd088836c7ab80450afb91aeedc6cdb94fa4c6bfe955",
        "adapter_sha256": sha(adapter),
        "latest_source_acceptance_sha256": previous["acceptance_receipt_sha256"],
        "control_gate_sha256": previous["control_gate_receipt_sha256"],
        "prior_failure_tail": 0, "resume_gate_passed": True, "control_final_streak": 0,
        "network_deadline_utc": "2026-10-19T13:15:00Z",
        "parent_watchdog_seconds": 300, "disk_free_before_bytes": free,
        "scope": "One execution only; four exact sources, up to16 attempts/240s/16MiB. Worker must use a separate300s parent watchdog. No automatic retry."}
    OUT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"root_go": True, "targets": len(expected), "disk_free_bytes": free}))


if __name__ == "__main__":
    main()
