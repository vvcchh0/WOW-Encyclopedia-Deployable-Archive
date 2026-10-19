"""Create the local-only continuation input from the frozen Oct18 r7 evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "research/continuous-recovery-20261018/integration/v33/browser/v33-browser-input-r7.json"
OUT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(rel: str) -> dict[str, str]:
    path = ROOT / rel
    return {"path": rel, "sha256": sha256(path)}


def main() -> None:
    frozen = json.loads(SOURCE.read_text(encoding="utf-8"))
    refs = frozen["source_references"]
    target_rows = refs["ordinary_image_hrefs"] + refs["static_render_targets"]
    target_originals = {row["original"] for row in target_rows}
    target_items = [
        item
        for item in frozen["new_originals"] + frozen["validated_old_originals"]
        if item.get("original") in target_originals
    ]
    data = {
        "schema": "wow-recovery.local-audit.v33-ui-input.v1",
        "status": "prepared_local_only",
        "prepared_utc": "2026-10-19T05:59:00Z",
        "scope_note": (
            "Read-only local v33 UI continuation; no exporter/site bytes/status changes. "
            "Prior 21 popup and 23 ordinary checks are reused from frozen Oct18 r5; "
            "46 ordinary and 30 static targets remain."
        ),
        "frozen_bindings": {
            "browser_input_r7": binding(
                "research/continuous-recovery-20261018/integration/v33/browser/v33-browser-input-r7.json"
            ),
            "browser_result_r5": binding(
                "research/continuous-recovery-20261018/integration/v33/browser/results/v33-browser-result-r5.json"
            ),
            "root_browser_acceptance": binding(
                "research/continuous-recovery-20261018/publication/root-v33-browser-acceptance.json"
            ),
            "css_viewer_baseline": binding(
                "research/continuous-recovery-20261018/integration/v33/browser/results/tournament-viewer-baseline.json"
            ),
            "v33_provenance": frozen["source_bindings"]["v33_provenance"],
        },
        "output": frozen["output"],
        "counts": {
            "total_ordinary": len(refs["ordinary_image_hrefs"]),
            "prior_ordinary_processed": 23,
            "remaining_ordinary": 46,
            "total_static": len(refs["static_render_targets"]),
            "prior_static_processed": 0,
            "remaining_static": 30,
            "prior_popup_processed": 21,
            "new_originals_reused": 120,
        },
        "source_references": {
            "ordinary_image_hrefs": refs["ordinary_image_hrefs"],
            "static_render_targets": refs["static_render_targets"],
        },
        "news_toggle_ids": frozen["browser_plan"]["news_toggle_ids"],
        "known_baseline_error_rules": frozen["known_baseline_error_rules"],
        "items_for_targets": target_items,
        "prior_result_summary": {
            "accepted": False,
            "failure": (
                "Dragon Hunt hidden ss05 anchor was selected before the native toggle; "
                "r5 stopped at ordinary_image_hrefs=23."
            ),
            "external_requests": 0,
            "request_failures": 0,
            "unresolved_original_controls": [
                {
                    "original": "http://www.worldofwarcraft.com/pvp/tournament/images/ss5.jpg",
                    "status": "known_unresolved_from_r5",
                }
            ],
        },
        "execution_contract": {
            "local_server_host": "127.0.0.1",
            "external_requests_allowed": False,
            "batch_max_targets": 12,
            "batch_deadline_seconds_max": 720,
            "must_use_visible_native_controls": True,
            "must_not_unhide_arbitrary_dom": True,
            "no_overwrite_results": True,
        },
        "dragon_hunt_focus": {
            "page_output": "community/reallifeevents.html",
            "toggle_id": "dragonhunt",
            "toggle_selector": "a[onclick*='toggleComplete(\\'dragonhunt\\'']",
            "original": "http://www.worldofwarcraft.com/community/images/reallifeevents/dragonhunt/ss05.jpg",
            "source_line": 700,
            "expected_dimensions": [750, 563],
            "expected_served_output_path": "community/images/reallifeevents/dragonhunt/ss05.jpg",
        },
    }
    output = OUT / "v33-ui-audit-input-r7.json"
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(output)
    print(sha256(output))
    print(output.stat().st_size)


if __name__ == "__main__":
    main()
