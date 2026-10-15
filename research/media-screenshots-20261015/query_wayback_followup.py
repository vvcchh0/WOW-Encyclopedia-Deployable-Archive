#!/usr/bin/env python3
"""Continue the authorized Wayback window without repeating prior requests."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import query_wayback as q


OUT = q.OUT
RECORDS = OUT / "request-records.json"


def main() -> int:
    previous: list[dict[str, Any]] = []
    if RECORDS.is_file():
        previous = json.loads(RECORDS.read_text(encoding="utf-8"))
    window = q.Window()
    window.records = previous
    window.source_requests = len(previous)
    window.total_body = sum(int(record.get("body_bytes") or 0) for record in previous)
    window.last_start = time.monotonic() - q.START_INTERVAL
    targets = [
        (
            "ssotd_screens_prefix_rows_all",
            q.cdx_target_url(
                "http://www.worldofwarcraft.com/downloads/ssotd/images/screens/",
                match_type="prefix",
            ),
        ),
        (
            "ssotd_screens_prefix_rows_port80",
            q.cdx_target_url(
                "http://www.worldofwarcraft.com:80/downloads/ssotd/images/screens/",
                match_type="prefix",
            ),
        ),
        (
            "ssotd_screens_prefix_rows_bare_port80",
            q.cdx_target_url(
                "http://worldofwarcraft.com:80/downloads/ssotd/images/screens/",
                match_type="prefix",
            ),
        ),
        (
            "ssotd_screens_prefix_rows_bare",
            q.cdx_target_url(
                "http://worldofwarcraft.com/downloads/ssotd/images/screens/",
                match_type="prefix",
            ),
        ),
    ]
    all_rows: list[dict[str, Any]] = []
    for label, url in targets:
        result = window.run(label, url, "cdx", True)
        all_rows.extend(result.get("rows", []))
        if window.stop_reason:
            break

    # The 2008-05-12 page capture and the frozen script's startDate imply
    # number 1340. This is an explicitly labelled capture-date-derived probe,
    # not a claim that CDX has already confirmed the current total.
    derived = [
        (
            "ssotd_capture_date_derived_ss1340_exact",
            q.cdx_target_url(
                "http://www.worldofwarcraft.com/downloads/ssotd/images/screens/ss1340.jpg"
            ),
        ),
        (
            "ssotd_capture_date_derived_ss1340_thumb_exact",
            q.cdx_target_url(
                "http://www.worldofwarcraft.com/downloads/ssotd/images/screens/ss1340-thumb.jpg"
            ),
        ),
    ]
    derived_rows: list[dict[str, Any]] = []
    for label, url in derived:
        result = window.run(label, url, "cdx_image_exact", True)
        derived_rows.extend(result.get("rows", []))
        if window.stop_reason:
            break

    image_rows = all_rows + derived_rows
    full_row, thumb_row = q.choose_image_rows(image_rows)
    selected = [row for row in (full_row, thumb_row) if row]
    existing_originals = {
        str(row.get("original"))
        for record in previous
        for row in record.get("rows", [])
    }
    selected = [row for row in selected if str(row.get("original")) not in existing_originals]
    for row in selected:
        if window.stop_reason:
            break
        label = "followup_image_replay_" + q.safe_name(str(row["original"]))
        replay = window.run(label, q.replay_url(row), "memento_replay", False)
        replay["selected_cdx_row"] = row
        body_path = OUT / replay["body_path"]
        replay["payload_probe"] = q.pillow_probe(body_path)
        (OUT / f"{replay['request_index']:02d}-{q.safe_name(label)}_validation.json").write_text(
            json.dumps(replay, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    summary = {
        "schema_version": 1,
        "started_utc": window.records[0]["started_utc"] if window.records else q.now(),
        "finished_utc": q.now(),
        "proxy": q.PROXY,
        "serial": True,
        "minimum_interval_seconds": q.START_INTERVAL,
        "max_source_requests": q.MAX_SOURCE_REQUESTS,
        "source_requests": window.source_requests,
        "followup_requests": window.source_requests - len(previous),
        "total_body_bytes": window.total_body,
        "stop_reason": window.stop_reason or "followup_plan_complete",
        "transport_failure_streak_at_stop": window.transport_failures,
        "records_file": "request-records.json",
        "raw_directory": "raw/",
        "prefix_rows_observed_in_followup": len(all_rows),
        "capture_date_derived_rows_observed": len(derived_rows),
        "selected_rows": selected,
        "interpretation": [
            "The first four follow-up prefix requests differ from the earlier showNumPages requests by omitting showNumPages; the latter returned HTTP 200 with zero body and no parseable JSON.",
            "ss1340 and ss1340-thumb are capture-date-derived probes from the local 2008-05-12 page date, not an inferred total.",
            "CDX rows are index evidence; replay validation is recorded separately and CONNECT 200 is excluded from source status.",
        ],
    }
    RECORDS.write_text(json.dumps(window.records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_requests": window.source_requests,
        "followup_requests": summary["followup_requests"],
        "total_body_bytes": window.total_body,
        "stop_reason": summary["stop_reason"],
        "prefix_rows": len(all_rows),
        "derived_rows": len(derived_rows),
        "full_row": full_row,
        "thumb_row": thumb_row,
        "selected_replays": len(selected),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
