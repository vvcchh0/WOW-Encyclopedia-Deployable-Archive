#!/usr/bin/env python3
"""Follow one saved CDX resume token, then exact/replay two real samples."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

import query_wayback as q


OUT = q.OUT
RECORDS = OUT / "request-records.json"


def extract_resume_token() -> str | None:
    body = OUT / "raw/07-ssotd_screens_prefix_rows_all.body"
    payload = json.loads(body.read_text(encoding="utf-8"))
    for item in reversed(payload[1:]):
        if isinstance(item, list) and len(item) == 1 and isinstance(item[0], str):
            return item[0]
    return None


def valid_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row for row in rows
        if re.fullmatch(r"\d{14}", str(row.get("timestamp", "")))
        and row.get("original")
        and row.get("statuscode")
    ]


def main() -> int:
    previous = json.loads(RECORDS.read_text(encoding="utf-8")) if RECORDS.is_file() else []
    window = q.Window()
    window.records = previous
    window.source_requests = len(previous)
    window.total_body = sum(int(record.get("body_bytes") or 0) for record in previous)
    window.last_start = time.monotonic() - q.START_INTERVAL
    token = extract_resume_token()
    if not token:
        raise RuntimeError("resume token not found in canonical prefix raw body")
    target = "http://www.worldofwarcraft.com/downloads/ssotd/images/screens/"
    resume_url = q.cdx_target_url(target, match_type="prefix", resumeKey=token)
    resume_result = window.run("ssotd_screens_prefix_resume_page1", resume_url, "cdx", True)
    resume_valid = valid_rows(resume_result.get("rows", []))
    candidates = [
        "http://www.worldofwarcraft.com/downloads/ssotd/images/screens/ss1314.jpg",
        "http://www.worldofwarcraft.com/downloads/ssotd/images/screens/ss1314-thumb.jpg",
    ]
    exact_results: list[dict[str, Any]] = []
    selected: list[dict[str, Any]] = []
    for original in candidates:
        result = window.run(
            "exact_" + q.safe_name(original),
            q.cdx_target_url(original),
            "cdx_image_exact",
            True,
        )
        exact_results.append(result)
        selected.extend(q.choose_image_rows(result.get("rows", [])))
        if window.stop_reason:
            break
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in selected:
        original = str(row.get("original"))
        if original not in seen:
            unique.append(row)
            seen.add(original)
    replay_validations: list[dict[str, Any]] = []
    for row in unique:
        if window.stop_reason:
            break
        label = "replay_" + q.safe_name(str(row["original"]))
        replay = window.run(label, q.replay_url(row), "memento_replay", False)
        replay["selected_cdx_row"] = row
        replay["payload_probe"] = q.pillow_probe(OUT / replay["body_path"])
        replay_validations.append(replay)
        (OUT / f"{replay['request_index']:02d}-{q.safe_name(label)}_validation.json").write_text(
            json.dumps(replay, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    summary = {
        "schema_version": 1,
        "started_utc": previous[0]["started_utc"] if previous else q.now(),
        "finished_utc": q.now(),
        "proxy": q.PROXY,
        "serial": True,
        "minimum_interval_seconds": q.START_INTERVAL,
        "max_source_requests": q.MAX_SOURCE_REQUESTS,
        "source_requests": window.source_requests,
        "total_body_bytes": window.total_body,
        "stop_reason": window.stop_reason or "resume_and_samples_complete",
        "resume_token_source": "raw/07-ssotd_screens_prefix_rows_all.body",
        "resume_token": token,
        "resume_page_valid_rows": len(resume_valid),
        "resume_page_raw_rows": resume_result.get("rows_count", 0),
        "exact_results": [
            {
                "label": result.get("label"),
                "status": result.get("status"),
                "body_bytes": result.get("body_bytes"),
                "rows_count": result.get("rows_count"),
                "parse_error": result.get("parse_error"),
            }
            for result in exact_results
        ],
        "replay_validations": replay_validations,
        "pagination_interpretation": "The first canonical prefix page is capped at 1000 data rows and carries a resume token. One follow-up page was requested; no total count is claimed.",
    }
    RECORDS.write_text(json.dumps(window.records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_requests": window.source_requests,
        "total_body_bytes": window.total_body,
        "stop_reason": summary["stop_reason"],
        "resume_valid_rows": len(resume_valid),
        "exact_results": summary["exact_results"],
        "replays": len(replay_validations),
        "decoded_replays": sum(bool(item.get("payload_probe", {}).get("decoded")) for item in replay_validations),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
