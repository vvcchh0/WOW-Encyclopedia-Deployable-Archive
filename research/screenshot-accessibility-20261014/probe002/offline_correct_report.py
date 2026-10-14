"""Create probe002 semantic correction outputs from existing local evidence only."""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "sanitized-report.json"
REPORT = ROOT / "sanitized-report.final.json"
SUMMARY = ROOT / "sanitized-summary.final.md"


def main() -> None:
    if REPORT.exists() or SUMMARY.exists():
        raise SystemExit("refusing to overwrite corrected outputs")
    report = copy.deepcopy(json.loads(SOURCE.read_text(encoding="utf-8")))
    known_good_retrieved = 0
    for item in report["items"]:
        outcome = item["outcome"]
        item["new_unique_resources"] = 0
        outcome["new_unique_resources"] = 0
        outcome["requested_url_timestamp_hint"] = item["timestamp"]
        if item["known_good"] and outcome.get("restored"):
            outcome["classification"] = "known_good_retrieved"
            outcome["known_good_retrieved"] = True
            outcome["image_retrieved"] = True
            known_good_retrieved += 1
        elif outcome.get("classification") == "expected_missing_404":
            # The 404 page has no Memento-Datetime.  The timestamp in the
            # replay URL is a request hint, not an observed capture date.
            outcome["memento_timestamp"] = None
            outcome["memento_timestamp_source"] = None
            outcome["actual_capture_timestamp"] = None
            outcome["interpretation"] = (
                "current replay returned HTTP 404/page indication for this requested capture; "
                "this does not establish that all dates or all gallery images are absent"
            )
            outcome["image_retrieved"] = False
        for attempt in item["attempts"]:
            validation = attempt.get("validation", {})
            validation["requested_url_timestamp_hint"] = item["timestamp"]
            if item["known_good"] and outcome.get("classification") == "known_good_retrieved" and attempt.get("accepted"):
                validation["classification"] = "known_good_retrieved"
                validation["known_good_retrieved"] = True
                validation["image_retrieved"] = True
                validation["new_unique_resources"] = 0
            elif outcome.get("classification") == "expected_missing_404":
                validation["new_unique_resources"] = 0
            if not attempt.get("memento_datetime"):
                validation["memento_timestamp"] = None
                validation["memento_timestamp_source"] = None
                validation["actual_capture_timestamp"] = None
            if outcome.get("classification") == "expected_missing_404":
                validation["image_retrieved"] = False
            attempt["validation"] = validation

    report["known_good_retrieved"] = known_good_retrieved
    report["new_unique_resources"] = 0
    report["semantic_correction"] = {
        "network_requests_added": 0,
        "source_report_preserved": SOURCE.name,
        "known_good": "mirror-present controls are labeled known_good_retrieved; retrieved images do not count as new resources",
        "missing_404": "no Memento-Datetime means actual_capture_timestamp is null; replay URL timestamp is retained only as requested_url_timestamp_hint",
        "scope": "404 evidence applies only to the requested URL/capture and does not establish absence across all dates or all 50 galleries",
    }
    report["output"] = {"raw": "raw", "report": REPORT.name, "summary": SUMMARY.name}
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    lines = [
        "# Wayback replay probe002 (semantic correction)",
        "",
        f"- Network requests added by this correction: `0`; original network attempts remain `{report['http_attempts']}/{report['max_http_attempts']}`.",
        f"- Known-good items retrieved from already-present mirror resources: `{known_good_retrieved}`; new unique resources: `0`.",
        f"- Raw body bytes: `{report['raw_body_bytes']}/{report['raw_body_budget']}`; D preflight `{report['preflight']['passed']}`.",
        "",
        "## Items",
        "",
    ]
    for item in report["items"]:
        outcome = item["outcome"]
        lines.extend(
            [
                f"### `{item['id']}` — {item['category']}",
                "",
                f"- Original: `{item['original']}`; requested capture: `{item['timestamp']}`; known good: `{item['known_good']}`.",
                f"- Outcome: `{outcome['classification']}`; image retrieved: `{outcome.get('image_retrieved', False)}`; new unique resources: `{item['new_unique_resources']}`.",
                f"- Actual capture: `{outcome.get('actual_capture_timestamp')}`; requested URL timestamp hint: `{outcome.get('requested_url_timestamp_hint')}`.",
            ]
        )
        if outcome["classification"] == "expected_missing_404":
            lines.append("- Interpretation: current replay returned HTTP 404/page indication for this requested capture only; this does not establish that all dates or all 50 galleries are absent.")
        for attempt in item["attempts"]:
            lines.append(f"- `{attempt['transport']}` status `{attempt['status']}`, bytes `{attempt['wire_bytes']}`, elapsed `{attempt['elapsed_seconds']}`, failures `{','.join(attempt['failure_reasons']) or 'none'}`.")
        lines.append("")
    lines.extend(
        [
            "## Scope",
            "",
            "- Original `sanitized-report.json` is preserved; this report is an offline semantic correction from its saved raw evidence.",
            "- Raw response headers and bodies remain local under `raw/`; this summary contains no raw header text.",
            "",
        ]
    )
    SUMMARY.write_text("\n".join(lines), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
