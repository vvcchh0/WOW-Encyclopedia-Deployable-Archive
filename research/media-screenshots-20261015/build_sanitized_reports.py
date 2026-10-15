#!/usr/bin/env python3
"""Write compact, non-destructive CDX summaries and capture ledger."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    inventory = read_json(OUT / "inventory.json")
    window = inventory["saved_cdx_coverage"]["wayback_window"]
    late = read_json(OUT / "late-image-source-map.json")
    records = read_json(OUT / "wayback-window/request-records.json")
    entry_range = records[1].get("rows", []) if len(records) > 1 else []
    years: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "rows": 0,
            "status_counts": Counter(),
            "mime_counts": Counter(),
            "host_counts": Counter(),
            "status200_html": 0,
        }
    )
    for row in entry_range:
        timestamp = str(row.get("timestamp", ""))
        if not re.fullmatch(r"\d{14}", timestamp):
            continue
        year = timestamp[:4]
        item = years[year]
        item["rows"] += 1
        item["status_counts"][str(row.get("statuscode"))] += 1
        item["mime_counts"][str(row.get("mimetype"))] += 1
        original = str(row.get("original", ""))
        item["host_counts"][original.split("/")[2] if "/" in original else "[unknown]"] += 1
        if row.get("statuscode") == "200" and row.get("mimetype") == "text/html":
            item["status200_html"] += 1
    year_summary = {}
    for year, item in sorted(years.items()):
        year_summary[year] = {
            "rows": item["rows"],
            "status_counts": dict(sorted(item["status_counts"].items())),
            "mime_counts": dict(sorted(item["mime_counts"].items())),
            "host_counts": dict(sorted(item["host_counts"].items())),
            "status200_html": item["status200_html"],
        }

    sanitized = {
        "schema_version": 1,
        "kind": "media_ssotd_sanitized_summary",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "US MEDIA Screenshot of the Day local coverage plus bounded Wayback evidence",
        "entry": {
            "relative_href": inventory["media_entry"]["canonical_relative_href"],
            "source_base_url": inventory["media_entry"]["source_identity"],
            "all_time_cdx_rows": window["entry_trailing_slash"]["all_time_rows"],
            "cdx_rows_2006_2010": window["entry_trailing_slash"]["from_2006_to_2010_rows"],
            "year_summary_2006_2010": year_summary,
            "parent_index_exact_empty": window["parent_exact_index_query"],
        },
        "local": {
            "offline_site_files": inventory["frozen_inputs"]["offline_site"]["file_count"],
            "manifest_sha256": inventory["frozen_inputs"]["offline_build_manifest"]["sha256"],
            "static_ui_files": inventory["local_ssotd_assets"]["static_ui"]["file_count"],
            "static_ui_decoded": inventory["local_ssotd_assets"]["static_ui"]["decoded_count"],
            "dynamic_full_local": inventory["local_ssotd_assets"]["dynamic_full_local_count"],
            "dynamic_thumb_local": inventory["local_ssotd_assets"]["dynamic_thumb_local_count"],
            "game_guide_combined_slots": inventory["game_guide_distinction"]["combined_slots"],
            "game_guide_expected_entities": inventory["game_guide_distinction"]["expected_direct_full_thumb_entities"],
        },
        "cdx_coverage": {
            "screens_prefix_first_valid_rows": window["screens_prefix_first_page"]["valid_data_rows"],
            "screens_prefix_first_resume": window["screens_prefix_first_page"]["resume_token_present"],
            "screens_prefix_deduped_canonical_pages": window["screens_prefix_first_page"]["deduped_canonical_page_count"],
            "screens_prefix_alias_queries": window["screens_prefix_first_page"]["alias_queries"],
            "screens_prefix_resume_valid_rows": window["screens_prefix_resume_page"]["valid_data_rows"],
            "screens_prefix_resume": window["screens_prefix_resume_page"]["resume_token_present"],
            "screens_filtered_status200_image_rows": window["filtered_prefix"]["status200_image_rows"],
            "exact_ss1314_rows": len(window["exact_image_series"]["rows"]),
            "exact_ss1314_status200_image_rows": window["exact_image_series"]["status200_image_rows"],
            "exact_ss1314_thumb_rows": len(window["exact_thumb_control"]["rows"]),
            "show_num_pages": window["show_num_pages"],
            "host_variants": window["screens_prefix_first_page"]["host_variants"],
            "request_count": window["source_budget"]["observed_requests"],
            "body_bytes": window["source_budget"]["observed_body_bytes"],
        },
        "validated_late_images": [
            {
                "logical_url": item["logical_url"],
                "actual_timestamp": item["actual_timestamp"],
                "length": item["length"],
                "dimensions": item["dimensions"],
                "sha256": item["sha256"],
                "mime": item["mime"],
                "cdx_digest": item["cdx_digest"],
                "replay_status": item["replay_status"],
                "digest_match": item["digest_match"],
                "local_path": item["local_path"],
            }
            for item in late["items"]
        ],
        "limits": [
            "Prefix pagination is only two pages plus one filtered page; no complete total is claimed.",
            "A CDX valid JSON empty array is scoped to the exact target and query range.",
            "The two validated late images are supplement overlay evidence and are not 2008 captures.",
            "Guide gallery counts are kept separate from MEDIA SSOTD.",
        ],
        "source_files": [
            "research/media-screenshots-20261015/inventory.json",
            "research/media-screenshots-20261015/capture-query-plan.json",
            "research/media-screenshots-20261015/wayback-window/request-records.json",
            "research/media-screenshots-20261015/wayback-window/request-records-reconciled.json",
            "research/media-screenshots-20261015/wayback-window/extended-summary.json",
            "research/media-screenshots-20261015/wayback-window/raw/",
            "research/media-screenshots-20261015/late-image-source-map.json",
        ],
    }

    exact_rows = window["exact_image_series"]["rows"]
    ledger = {
        "schema_version": 1,
        "kind": "media_ssotd_capture_ledger",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "logical_entry": inventory["media_entry"]["source_identity"],
        "entries": [
            {
                "ledger_id": "entry-trailing-slash-all",
                "target": "http://www.worldofwarcraft.com/downloads/ssotd/",
                "match_type": "exact",
                "query_scope": "all time",
                "cdx_rows": window["entry_trailing_slash"]["all_time_rows"],
                "evidence": "wayback-window/request-records.json:1",
                "interpretation": "Historical entry captures plus redirects/revisits; status and host distributions remain in raw record.",
            },
            {
                "ledger_id": "entry-trailing-slash-2006-2010",
                "target": "http://www.worldofwarcraft.com/downloads/ssotd/",
                "match_type": "exact",
                "query_scope": "2006-2010",
                "cdx_rows": window["entry_trailing_slash"]["from_2006_to_2010_rows"],
                "year_summary": year_summary,
                "evidence": "wayback-window/request-records.json:2",
                "interpretation": "2006-2010 control; no 2006 row was inferred when the returned rows begin later.",
            },
            {
                "ledger_id": "screens-prefix-page-0",
                "target": "http://www.worldofwarcraft.com/downloads/ssotd/images/screens/",
                "match_type": "prefix",
                "valid_data_rows": window["screens_prefix_first_page"]["valid_data_rows"],
                "resume_token_present": True,
                "selected_status200_images": window["screens_prefix_first_page"]["status200_image_rows"],
                "evidence": "wayback-window/raw/07-ssotd_screens_prefix_rows_all.body",
                "interpretation": "Trailing empty row and one-element resume token are metadata, not captures.",
            },
            {
                "ledger_id": "screens-prefix-resume-page-1",
                "target": "http://www.worldofwarcraft.com/downloads/ssotd/images/screens/",
                "match_type": "prefix",
                "valid_data_rows": window["screens_prefix_resume_page"]["valid_data_rows"],
                "resume_token_present": True,
                "selected_status200_images": window["screens_prefix_resume_page"]["status200_image_rows"],
                "evidence": "wayback-window/raw/13-ssotd_screens_prefix_resume_page1.body",
                "interpretation": "One resumed page only; full prefix remains incomplete.",
            },
            {
                "ledger_id": "ss1314-exact-time-series",
                "target": window["exact_image_series"]["full_target"],
                "match_type": "exact",
                "cdx_rows": exact_rows,
                "evidence": "wayback-window/raw/14-exact_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314.jpg.body",
                "interpretation": "The 2010 status-200 image row is replay-validated below; later redirect/revisit rows remain index-only.",
            },
            {
                "ledger_id": "late-validated-images",
                "target": "two real full-image payloads",
                "match_type": "memento replay",
                "items": late["items"],
                "evidence": "late-image-source-map.json and replay_validation.json files",
                "interpretation": "Supplement overlay with actual 2010 timestamps, not a 2008 baseline claim.",
            },
        ],
        "year_summary_2006_2010": year_summary,
        "request_budget": {
            "source_requests": window["source_budget"]["observed_requests"],
            "max_source_requests": window["source_budget"]["max_requests"],
            "body_bytes": window["source_budget"]["observed_body_bytes"],
            "stop": "extended_plan_complete",
        },
    }
    (OUT / "sanitized-summary.json").write_text(json.dumps(sanitized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "capture-ledger.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "sanitized_summary": "research/media-screenshots-20261015/sanitized-summary.json",
        "capture_ledger": "research/media-screenshots-20261015/capture-ledger.json",
        "entry_years": sorted(year_summary),
        "exact_rows": len(exact_rows),
        "late_images": len(late["items"]),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
