"""Offline independent checks and current ledger integration; no network."""
from __future__ import annotations

import hashlib
import io
import json
import re
from collections import Counter
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BASELINE_SHA = "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name: str, value: dict) -> None:
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    checked = datetime.now(timezone.utc).isoformat()
    audit_path = OUT / "sidebar-audit/audit.json"
    audit = read(audit_path)
    inventory = read(ROOT / "research/navigation-gaps-20261015/inventory.json")
    routes = read(ROOT / ".scratch/pages-resources-20261015-v8/__offline/route-map.json")
    errors = []
    input_drift = []
    records = audit["records"]
    if len(records) != 1241 or len({r["record_id"] for r in records}) != 1241:
        errors.append("menu observation count or identity conservation failed")
    for entry in audit["input_hashes"]:
        if entry.get("exists") and digest(ROOT / entry["path"]) != entry["sha256"]:
            if entry["path"] == "CHANGELOG.md":
                input_drift.append({"path": entry["path"], "audit_sha256": entry["sha256"], "current_sha256": digest(ROOT / entry["path"]), "reason": "Root agent concurrently added publication receipts; this contextual input is not used for route or payload checks."})
            else:
                errors.append("input hash changed: " + entry["path"])
    observed = Counter()
    for record in records:
        index = int(re.search(r":(\d+):", record["record_id"]).group(1))
        inventory_key = "entries" if record["scope"] == "in_scope" else "excluded_entries"
        expected = inventory[inventory_key][index]
        for field in ("source_path", "source_line", "menu_id", "href", "label"):
            if expected[field] != record[field]:
                errors.append(f"inventory identity mismatch {record['record_id']} {field}")
        observed[(inventory_key, index)] += 1
        route = record.get("normalized_route")
        target = routes["routes"].get(route) or routes["aliases"].get(route)
        if record["current_page_status"].startswith("resolved"):
            if target != record.get("resolved_static_url"):
                errors.append("route mapping mismatch: " + record["record_id"])
            page = ROOT / record["resolved_path"]
            if not page.is_file() or page.stat().st_size != record["page_bytes"] or digest(page) != record["page_sha256"]:
                errors.append("page content mismatch: " + record["record_id"])
        elif record["current_page_status"] == "missing_export_route" and target is not None:
            errors.append("false missing route: " + record["record_id"])
        if record["current_page_status"].startswith("resolved") and record.get("interaction_validation") != "static_indication_only":
            errors.append("interaction claim exceeds static audit: " + record["record_id"])
    if len(observed) != 1241 or any(v != 1 for v in observed.values()):
        errors.append("inventory pointers are not a bijection")
    for route in ("/info/faq/technology.html", "/info/races/dancing.html", "/wrath/features.xml", "/info/burningcrusade/index.xml", "/wareffort/servers.html", "/calendar/"):
        samples = [r for r in records if r["href"].strip() == route]
        if not samples or any(not r["current_page_status"].startswith("resolved") for r in samples):
            errors.append("legacy normalization regression: " + route)
    baseline = digest(ROOT / "offline/build-manifest.json")
    if baseline != BASELINE_SHA:
        errors.append("frozen baseline changed")
    missing = sorted({r["normalized_route"] for r in records if r["current_page_status"] == "missing_export_route"})
    acceptance = {"schema": "continuous-wow-sidebar-acceptance/v1", "checked_utc": checked, "accepted": not errors, "network_requests": 0, "audit": "research/continuous-recovery-20261015/sidebar-audit/audit.json", "audit_sha256": digest(audit_path), "menu_observations": len(records), "original_in_scope": 588, "legacy_reviewed": 579, "explicit_original_exclusions": 74, "page_status_counts": dict(Counter(r["current_page_status"] for r in records if r.get("effective_in_scope"))), "distinct_missing_routes": len(missing), "missing_routes": missing, "resolved_distinct_files": len({r["resolved_path"] for r in records if r["current_page_status"].startswith("resolved")}), "baseline_sha256": baseline, "checks": ["all inventory identities and pointers", "all current resolved route targets", "all resolved page lengths and SHA256", "all missing route keys", "six prior normalization false positives", "all critical input hashes", "static interaction claim limits for resolved pages", "frozen manifest"], "contextual_input_drift": input_drift, "not_checked": ["runtime browser behavior", "every asset dependency beyond the worker's static scan", "historical equivalence of potential route aliases"], "errors": errors}
    save("sidebar-acceptance.json", acceptance)
    if errors:
        raise SystemExit(json.dumps(acceptance, ensure_ascii=False))

    ledger = read(OUT / "ledger.scope-review.json")
    by_id = {}
    for record in records:
        source = {k: record.get(k) for k in ("source_path", "source_role", "source_line", "menu_id")}
        identity = json.dumps([source, record.get("href"), record.get("label")], sort_keys=True)
        by_id["menu-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]] = record
    for item in ledger["items"]:
        record = by_id[item["item_id"]]
        item.update({"page_status": record["current_page_status"], "resource_status": record["asset_status"], "interaction_status": record["interaction_status"], "interaction_validation": record.get("interaction_validation"), "normalized_route": record.get("normalized_route"), "resolved_path": record.get("resolved_path"), "next_action": record["next_action"], "priority": record["priority"], "audit_record_id": record["record_id"]})
        item["evidence"].append({"path": "research/continuous-recovery-20261015/sidebar-audit/audit.json", "record_id": record["record_id"]})
        role = record["source_role"]
        if item["group"] == "Legacy menu":
            item["prior_group"] = "Legacy menu"
            if role == "legacy_menu1":
                item["group"] = "News"
                item["group_reason"] = "menu1_var.js Current News / Archived News / Awards / Press top-level headings"
            elif role == "legacy_menu3":
                item["group"] = "Game Guide"
                item["group_reason"] = "menu3_var.js Game Guide, expansions, and Under Development headings"
            elif role == "late_menu_xml":
                category = record["menu_id"].split(":", 1)[0]
                item["group"] = {"menuAccount": "Account", "menuForums": "Forums", "menuSupport": "Support", "menuInteractive": "Interactive", "menuMedia": "Media", "menuNews": "News", "menuGameGuide": "Game Guide"}.get(category, category)
                item["group_reason"] = "menu.xml category name " + category
        if record["current_page_status"] == "business_or_sensitive":
            item["scope"] = "historical_business_exhibit_only"
        elif record.get("effective_in_scope"):
            item["scope"] = "content_recovery" if record["current_page_status"] != "external_or_dynamic" else "external_or_dynamic_no_acquisition"
    ledger.update({"generated_utc": checked, "supersedes": "research/continuous-recovery-20261015/ledger.scope-review.json", "sidebar_acceptance": "research/continuous-recovery-20261015/sidebar-acceptance.json", "status_note": "Current page/resource/interaction fields now reflect the accepted v8 local sidebar audit. Historical inventory counts and statuses remain explicitly named; interaction evidence is static only."})
    ledger["summary"].pop("in_scope", None)
    ledger["summary"].pop("scope_excluded", None)
    ledger["summary"].update({"historical_inventory_in_scope_observations": 588, "historical_inventory_excluded_observations": 653, "explicit_original_exclusions": 74, "current_audited_observations": 1167, "current_content_route_observations": 1107, "groups": dict(Counter(i["group"] for i in ledger["items"])), "scopes": dict(Counter(i["scope"] for i in ledger["items"])), "page_status_counts": acceptance["page_status_counts"], "distinct_missing_routes": len(missing), "legacy_scope_review": 0, "legacy_reviewed": 579})
    save("ledger.current.json", ledger)

    control_dir = OUT / "network-control2"
    control_path = control_dir / "control-report.json"
    control = read(control_path)
    control_errors = []
    attempts = control["attempts"]
    if len(attempts) != 2 or datetime.fromisoformat(control["started_utc"]) < datetime.fromisoformat(control["not_before_utc"]):
        control_errors.append("request cap or cooldown guard failed")
    source_responses = 0
    for attempt in attempts:
        headers = (control_dir / attempt["raw"]["headers"]).read_text(encoding="utf-8", errors="replace")
        matches = [m for m in re.finditer(r"^HTTP/\d(?:\.\d)?\s+(\d{3})([^\r\n]*)", headers, re.M | re.I) if "connection established" not in m.group(2).lower()]
        status = int(matches[-1].group(1)) if matches else None
        source_responses += status is not None
        if status != attempt["source_status"]:
            control_errors.append("source status mismatch")
        body = (control_dir / attempt["raw"]["body"]).read_bytes()
        if len(body) != attempt["body_bytes"]:
            control_errors.append("control body length mismatch")
        if status == 200:
            if len(body) != 3347 or hashlib.sha256(body).hexdigest() != control["expected"]["sha256"]:
                control_errors.append("known JPEG payload mismatch")
            Image.open(io.BytesIO(body)).verify()
            image = Image.open(io.BytesIO(body)); image.load()
            if image.size != (150, 110) or image.format != "JPEG":
                control_errors.append("known JPEG decode mismatch")
            memento = re.search(r"^Memento-Datetime:\s*([^\r\n]+)", headers, re.M | re.I)
            actual = parsedate_to_datetime(memento.group(1)).astimezone(timezone.utc).isoformat() if memento else None
            if actual != "2008-05-12T21:26:53+00:00":
                control_errors.append("actual Memento mismatch")
    if source_responses != control["source_response_count"]:
        control_errors.append("control aggregate response count mismatch")
    control_acceptance = {"schema": "continuous-wow-control-acceptance/v1", "checked_utc": checked, "accepted": not control_errors, "network_requests_by_acceptance": 0, "control_report": "research/continuous-recovery-20261015/network-control2/control-report.json", "report_sha256": digest(control_path), "source_request_count": 2, "source_response_count": source_responses, "ready": not control_errors and control["category"] == "valid_image", "body_bytes": 3347, "dimensions": [150, 110], "sha256": control["expected"]["sha256"], "memento": "2008-05-12T21:26:53+00:00", "errors": control_errors}
    save("control2-acceptance.json", control_acceptance)
    print(json.dumps({"sidebar": {k: v for k, v in acceptance.items() if k not in {"missing_routes", "checks", "not_checked"}}, "control": control_acceptance}, ensure_ascii=False))
    if control_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
