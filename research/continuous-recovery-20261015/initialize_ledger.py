"""Create an evidence-linked, local-only recovery ledger from the frozen audit."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
INVENTORY = ROOT / "research/navigation-gaps-20261015/inventory.json"
BASELINE = ROOT / "offline/build-manifest.json"
EXPECTED_BASELINE_SHA256 = "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "ledger.initial.json"
    if target.exists():
        raise SystemExit("Refusing to overwrite the initial checkpoint")
    baseline_sha = sha256(BASELINE)
    if baseline_sha != EXPECTED_BASELINE_SHA256:
        raise SystemExit(f"Frozen baseline hash changed: {baseline_sha}")
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    records = []
    for key, in_scope in (("entries", True), ("excluded_entries", False)):
        for index, entry in enumerate(inventory[key]):
            source = {k: entry.get(k) for k in ("source_path", "source_role", "source_line", "menu_id")}
            identity = json.dumps([source, entry.get("href"), entry.get("label")], sort_keys=True)
            coverage = entry.get("coverage", {})
            records.append({
                "item_id": "menu-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16],
                "inventory_pointer": f"{key}/{index}",
                "group": entry.get("section", "Unknown"),
                "label": entry.get("label"),
                "href": entry.get("href"),
                "normalized_route": coverage.get("normalized_route"),
                "scope": "content_recovery" if in_scope else "excluded_business_or_external",
                "page_status": "current_audit_pending" if in_scope else "scope_excluded",
                "resource_status": "not_assessed" if in_scope else "scope_excluded",
                "interaction_status": "not_assessed" if in_scope else "historical_exhibit_only_or_external",
                "prior_inventory_status": coverage.get("status"),
                "prior_inventory_preview": inventory["scope"]["export_preview"],
                "evidence": [source, {"path": "research/navigation-gaps-20261015/inventory.json", "pointer": f"/{key}/{index}"}],
                "task_ids": ["LOCAL-SIDEBAR-001"] if in_scope else [],
                "next_action": "Audit the v8 route and its dependencies" if in_scope else "Retain scope reason; do not restore sensitive forms or follow social endpoints",
            })
    ids = [x["item_id"] for x in records]
    if len(ids) != len(set(ids)):
        raise SystemExit("Menu observation identity collision")
    ledger = {
        "schema": "continuous-wow-recovery-ledger/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "deadline_utc": "2026-10-15T14:44:00+00:00",
        "inputs": {"inventory": "research/navigation-gaps-20261015/inventory.json", "inventory_sha256": sha256(INVENTORY), "baseline": "offline/build-manifest.json", "baseline_sha256": baseline_sha},
        "current_preview": ".scratch/pages-resources-20261015-v8",
        "status_note": "Prior v5 inventory is retained as historical evidence; current page/resource/interaction states require a new v8 audit.",
        "summary": {"observations": len(records), "in_scope": len(inventory["entries"]), "scope_excluded": len(inventory["excluded_entries"]), "in_scope_distinct_routes_prior": inventory["summary"]["distinct_local_routes"], "groups": dict(Counter(x["group"] for x in records))},
        "items": records,
    }
    target.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(target.relative_to(ROOT)), "sha256": sha256(target), "summary": ledger["summary"], "baseline_unchanged": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
