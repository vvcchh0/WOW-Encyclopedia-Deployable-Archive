#!/usr/bin/env python3
"""Use the extended window for two known image replays and one filtered prefix."""

from __future__ import annotations

import base64
import hashlib
import json
import time
from pathlib import Path
from urllib.parse import urlencode

import query_wayback as q


OUT = q.OUT
RECORDS = OUT / "request-records.json"


def cdx_digest(body: bytes) -> str | None:
    if not body:
        return None
    return base64.b32encode(hashlib.sha1(body).digest()).decode("ascii").rstrip("=")


def filtered_prefix_url() -> str:
    params = [
        ("url", "http://www.worldofwarcraft.com/downloads/ssotd/images/screens/"),
        ("matchType", "prefix"),
        ("output", "json"),
        ("fl", "timestamp,original,statuscode,mimetype,digest,length"),
        ("showResumeKey", "true"),
        ("limit", "1000"),
        ("filter", "statuscode:200"),
        ("filter", "mimetype:image/.*"),
    ]
    return "https://web.archive.org/cdx/search/cdx?" + urlencode(params)


def main() -> int:
    previous = json.loads(RECORDS.read_text(encoding="utf-8")) if RECORDS.is_file() else []
    window = q.Window()
    window.records = previous
    window.source_requests = 15
    prior_extra = [
        OUT / "raw/13-ssotd_screens_prefix_resume_page1.body",
        OUT / "raw/14-exact_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314.jpg.body",
        OUT / "raw/15-exact_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314-thumb.jpg.body",
    ]
    window.total_body = sum(int(record.get("body_bytes") or 0) for record in previous)
    window.total_body += sum(path.stat().st_size for path in prior_extra if path.is_file())
    window.last_start = time.monotonic() - q.START_INTERVAL
    targets = [
        {
            "timestamp": "20100810173046",
            "original": "http://www.worldofwarcraft.com/downloads/ssotd/images/screens/ss1314.jpg",
            "digest": "4AKYT7KIDFUKL2OD6WVGY63CXMXIHGF3",
            "length": "77789",
        },
        {
            "timestamp": "20100602102329",
            "original": "http://www.worldofwarcraft.com/downloads/ssotd/images/screens/ss1336.jpg",
            "digest": "G7QSOMUMRMS3XPH4YYARXYFK76RTOBHZ",
            "length": "150927",
        },
    ]
    replay_results = []
    for target in targets:
        request = f"https://web.archive.org/web/{target['timestamp']}id_/{target['original']}"
        result = window.run("replay_" + q.safe_name(target["original"]), request, "memento_replay", False)
        body_path = OUT / result["body_path"]
        body = body_path.read_bytes() if body_path.is_file() else b""
        headers = result.get("headers", {})
        observed = cdx_digest(body)
        result.update({
            "selected_cdx_row": target,
            "payload_probe": q.pillow_probe(body_path),
            "observed_cdx_digest": observed,
            "digest_match": observed == target["digest"],
            "memento_datetime": headers.get("memento-datetime"),
            "content_type": headers.get("content-type"),
            "content_length": headers.get("content-length"),
        })
        replay_results.append(result)
        (OUT / f"{result['request_index']:02d}-{q.safe_name(target['original'])}_replay_validation.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if window.stop_reason:
            break
    filtered_result = None
    if not window.stop_reason:
        filtered_result = window.run(
            "ssotd_screens_prefix_filtered_200_image",
            filtered_prefix_url(),
            "cdx_filtered_prefix",
            True,
        )
    filtered_rows = filtered_result.get("rows", []) if filtered_result else []
    summary = {
        "schema_version": 1,
        "finished_utc": q.now(),
        "proxy": q.PROXY,
        "serial": True,
        "minimum_interval_seconds": q.START_INTERVAL,
        "max_source_requests": q.MAX_SOURCE_REQUESTS,
        "source_requests": window.source_requests,
        "total_body_bytes": window.total_body,
        "stop_reason": window.stop_reason or "extended_plan_complete",
        "replay_results": replay_results,
        "filtered_prefix": {
            "request_index": filtered_result.get("request_index") if filtered_result else None,
            "status": filtered_result.get("status") if filtered_result else None,
            "body_bytes": filtered_result.get("body_bytes") if filtered_result else None,
            "rows_count_raw": filtered_result.get("rows_count") if filtered_result else None,
            "parse_error": filtered_result.get("parse_error") if filtered_result else None,
            "status200_image_rows": len(filtered_rows),
            "resume_token_present": any(
                isinstance(row, dict) and set(row) == {"timestamp"} for row in filtered_rows
            ),
        },
        "stop_rule": "Only two known image replays and one filtered prefix were added after the first window; no further requests are planned.",
    }
    RECORDS.write_text(json.dumps(window.records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "extended-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_requests": window.source_requests,
        "total_body_bytes": window.total_body,
        "stop_reason": summary["stop_reason"],
        "replays": [
            {
                "label": item["label"],
                "status": item["status"],
                "decoded": item["payload_probe"].get("decoded"),
                "digest_match": item["digest_match"],
            }
            for item in replay_results
        ],
        "filtered_status": summary["filtered_prefix"]["status"],
        "filtered_rows": summary["filtered_prefix"]["status200_image_rows"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
