"""Correct the inherited legacy-menu scope without erasing the initial snapshot."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent


def main() -> None:
    initial = OUT / "ledger.initial.json"
    current = OUT / "ledger.scope-review.json"
    if current.exists():
        raise SystemExit("Refusing to overwrite scope-review checkpoint")
    ledger = json.loads(initial.read_text(encoding="utf-8"))
    for item in ledger["items"]:
        if item["group"] == "Legacy menu":
            item.update({
                "scope": "legacy_content_scope_review",
                "page_status": "current_audit_pending",
                "resource_status": "not_assessed",
                "interaction_status": "not_assessed",
                "task_ids": ["LOCAL-SIDEBAR-001"],
                "next_action": "Classify by historical menu hierarchy and audit the v8 route; prior parser exclusion is not a business-scope decision",
                "scope_review_reason": "The inherited inventory labels 579 legacy observations as excluded, including explicit News RSS and guide routes.",
            })
        elif item["scope"] == "excluded_business_or_external":
            item["scope"] = "excluded_structural_business_or_external"
    ledger["generated_utc"] = datetime.now(timezone.utc).isoformat()
    ledger["supersedes"] = "research/continuous-recovery-20261015/ledger.initial.json"
    ledger["scope_correction"] = {
        "reason": "Prior inventory's Legacy menu is an unclassified parser bucket, not an evidence-backed exclusion.",
        "evidence": [{"path": "research/navigation-gaps-20261015/inventory.json", "pointer": "/excluded_entries", "sample": "Menu2_1 /news/rss-05-2008.xml at menu1_var.js:135"}],
        "prior_counts_preserved": {"entries": 588, "excluded_entries": 653},
        "scope_review_count": 579,
        "explicit_structural_business_or_external_count": 74,
    }
    ledger["summary"]["scopes"] = dict(Counter(x["scope"] for x in ledger["items"]))
    ledger["summary"]["scope_excluded"] = 74
    ledger["summary"]["legacy_scope_review"] = 579
    current.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(current), "sha256": hashlib.sha256(current.read_bytes()).hexdigest(), "summary": ledger["summary"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
