"""Offline verification of the 35-target reconciliation and exact queue."""
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report_path = OUT / "local-target-reconcile/reconciliation.json"
    report = read(report_path)
    queue_path = OUT / "local-target-reconcile/network-query-queue.json"
    queue = read(queue_path)
    accepted_sidebar = read(OUT / "sidebar-acceptance.json")
    errors = []
    targets = {row["target"] for row in report["rows"]}
    if targets != set(accepted_sidebar["missing_routes"]) or len(report["rows"]) != 35:
        errors.append("35-target identity conservation failed")
    if sum(r["observation_count"] for r in report["rows"]) != 40:
        errors.append("40-observation conservation failed")
    for name, entry in report["input_hashes"].items():
        if sha(ROOT / name) != entry["sha256"]:
            errors.append("input hash mismatch: " + name)
    checked_entities = 0

    def walk(value):
        nonlocal checked_entities
        if isinstance(value, list):
            for child in value:
                walk(child)
        elif isinstance(value, dict):
            if "path" in value and "exists" in value:
                path = ROOT / value["path"]
                if path.exists() != value["exists"]:
                    errors.append("declared file presence mismatch: " + value["path"])
                if value["exists"] and "sha256" in value:
                    checked_entities += 1
                    if sha(path) != value["sha256"] or path.stat().st_size != value["length"]:
                        errors.append("entity bytes mismatch: " + value["path"])
            for child in value.values():
                walk(child)

    walk(report["rows"])
    for entry in queue["entries"]:
        if entry["target"] not in targets or not entry["menu_evidence"] or entry["exact_original_url"] != "http://www.worldofwarcraft.com" + entry["target"]:
            errors.append("queue identity/source mismatch")
        if entry["target"].startswith(("/account", "/loginsupport")):
            errors.append("sensitive surface in queue")
    if len(queue["entries"]) != 12 or len({r["target"] for r in queue["entries"]}) != 12:
        errors.append("queue conservation failed")
    result = {"schema": "continuous-wow-local-target-acceptance/v1", "checked_utc": datetime.now(timezone.utc).isoformat(), "accepted": not errors, "network_requests": 0, "report": "research/continuous-recovery-20261015/local-target-reconcile/reconciliation.json", "report_sha256": sha(report_path), "queue_sha256": sha(queue_path), "targets": 35, "observations": 40, "target_types": {"rss": sum(t.startswith('/news/rss-') for t in targets), "news_html": sum(t.startswith('/news/wow-news') for t in targets), "other": sum(not t.startswith('/news/') for t in targets)}, "classification_counts": dict(Counter(r["classification"] for r in report["rows"])), "checked_entity_occurrences": checked_entities, "alias_proof_status": "No historical equivalence proof is accepted for BC professions or legacy Battlegroups .html; both require exact source or redirect/content evidence before integration.", "search_scope": "Declared v7c manifest/source entities, v8 route-map, mirror URL-map and exact staging paths; not a claim about every possible historical archive.", "errors": errors}
    (OUT / "local-target-reconcile-acceptance.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
