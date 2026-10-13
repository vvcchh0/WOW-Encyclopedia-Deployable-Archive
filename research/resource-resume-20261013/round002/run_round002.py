#!/usr/bin/env python3
"""Bounded Round002 dispatcher; dry-run by default.

This wrapper stages the finite exact-CDX plan and delegates future entity work
to the existing bounded runner. It never opens Archive by default. A parent
release token and ``--allow-network`` are both required for entity phase.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "research" / "resource-resume-20261013"
PLAN = BASE / "round002-plan.json"
OUT = BASE / "round002"
FROM = "20080101000000"
TO = "20081231235959"
MAX_ITEMS = 50
MAX_ENTITY_BYTES = 16 * 1024 * 1024
BODY_BUDGET = 128 * 1024 * 1024
DEADLINE = 1200
MIN_FREE = 11_000_000_000
RESERVE = 256 * 1024 * 1024


def sha(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def main():
    # The implementation lives beside this compatibility wrapper so existing
    # callers keep the historical path while cdx/entity now perform the
    # bounded, evidence-preserving phases.  Importing here also keeps the
    # dry-run wrapper's original module import harmless.
    from run_round002_impl import main as implementation_main
    return implementation_main()

    # Historical dispatcher retained below for auditability; unreachable
    # after the reviewed implementation handoff above.
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--phase", choices=("preflight", "cdx-plan", "entity"), default="preflight")
    ap.add_argument("--plan", type=Path, default=PLAN)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--entity-plan", type=Path)
    ap.add_argument("--allow-network", action="store_true")
    ap.add_argument("--parent-release-token")
    args = ap.parse_args()
    plan_path = args.plan if args.plan.is_absolute() else ROOT / args.plan
    out = args.out if args.out.is_absolute() else ROOT / args.out
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    items = plan.get("items", [])
    if len(items) > MAX_ITEMS:
        raise SystemExit(f"Round002 plan exceeds {MAX_ITEMS} items")
    if len({x.get("logical_url") for x in items}) != len(items):
        raise SystemExit("Round002 plan has duplicate URLs")
    out.mkdir(parents=True, exist_ok=True)
    state = {
        "schema_version": 1,
        "kind": "resource_resume_round002_state",
        "generated_utc": now(),
        "network_performed": False,
        "plan": plan_path.resolve().relative_to(ROOT).as_posix(),
        "plan_sha256": sha(plan_path),
        "items": len(items),
        "constraints": {
            "archive_streams": 4,
            "entity_max_bytes": MAX_ENTITY_BYTES,
            "response_body_budget_bytes": BODY_BUDGET,
            "per_request_timeout_seconds": 60,
            "deadline_seconds": DEADLINE,
            "workspace_max_bytes": 14_000_000_000,
            "disk_free_reserve_bytes": MIN_FREE,
            "reserve_bytes": RESERVE,
            "retries": 0,
        },
        "phase": args.phase,
        "allow_network": bool(args.allow_network),
    }
    if args.phase == "preflight":
        state.update({"status": "preflight_only", "note": "No network operation; wait for parent Pages/network release."})
        (out / "preflight.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"phase": args.phase, "items": len(items), "network": False}, ensure_ascii=False))
        return 0
    if args.phase == "cdx-plan":
        requests = []
        for x in items:
            requests.append({
                "rank": x["rank"],
                "logical_url": x["logical_url"],
                "query_url": "https://web.archive.org/cdx/search/cdx?" + urlencode({"url": x["logical_url"], "from": FROM, "to": TO, "matchType": "exact", "output": "json"}),
                "query_window": {"from": FROM, "to": TO},
                "network_performed": False,
            })
        state.update({"status": "cdx_plan_ready", "requests": requests, "planned_queries": len(requests)})
        (out / "cdx-request-plan.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"phase": args.phase, "planned_queries": len(requests), "network": False}, ensure_ascii=False))
        return 0
    if not args.allow_network or not args.parent_release_token:
        raise SystemExit("entity phase requires explicit --allow-network and --parent-release-token")
    if not args.entity_plan:
        raise SystemExit("entity phase requires a CDX-validated finite --entity-plan")
    entity_plan = args.entity_plan if args.entity_plan.is_absolute() else ROOT / args.entity_plan
    # Reuse the already reviewed bounded dispatcher; the parent may instead
    # substitute the reviewed pooled runner after CDX validation.
    delegated = ROOT / "research" / "resource-resume-20261013" / "round001" / "run_round001.py"
    cmd = [sys.executable, str(delegated), "--phase", "entity", "--plan", str(plan_path), "--out", str(out), "--entity-plan", str(entity_plan), "--allow-network", "--parent-release-token", args.parent_release_token, "--max-requests", str(MAX_ITEMS), "--deadline-seconds", str(DEADLINE)]
    state.update({"status": "entity_runner_started", "network_performed": True, "delegated_command": cmd})
    (out / "entity-start.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
