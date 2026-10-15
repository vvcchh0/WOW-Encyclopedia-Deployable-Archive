#!/usr/bin/env python3
"""Reconcile raw request 13-15 metadata without changing original receipts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "wayback-window"


def headers(path: Path) -> tuple[int | None, dict[str, str]]:
    status = None
    final: dict[str, str] = {}
    for line in path.read_text(encoding="iso-8859-1", errors="replace").splitlines():
        match = re.match(r"^HTTP/\d(?:\.\d)?\s+(\d{3})(?:\s+(.*))?$", line.strip(), re.I)
        if match:
            reason = (match.group(2) or "").lower()
            if "connection established" not in reason:
                status = int(match.group(1))
                final = {}
            continue
        if status is not None and ":" in line:
            key, value = line.split(":", 1)
            final[key.strip().lower()] = value.strip()
    return status, final


def cdx_rows(path: Path) -> tuple[list[dict[str, Any]], str | None]:
    if not path.is_file() or path.stat().st_size == 0:
        return [], None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload or not isinstance(payload[0], list):
        return [], None
    header = [str(value) for value in payload[0]]
    rows = [
        {key: value for key, value in zip(header, item)}
        for item in payload[1:]
        if isinstance(item, list)
    ]
    token = next((item[0] for item in reversed(payload[1:]) if isinstance(item, list) and len(item) == 1 and isinstance(item[0], str)), None)
    return rows, token


def main() -> int:
    original_path = OUT / "request-records.json"
    original = json.loads(original_path.read_text(encoding="utf-8"))
    specs = [
        (13, "ssotd_screens_prefix_resume_page1", "cdx", "13-ssotd_screens_prefix_resume_page1.body", "13-ssotd_screens_prefix_resume_page1.headers.txt", "13-ssotd_screens_prefix_resume_page1.trace.txt"),
        (14, "exact_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314.jpg", "cdx_image_exact", "14-exact_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314.jpg.body", "14-exact_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314.jpg.headers.txt", "14-exact_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314.jpg.trace.txt"),
        (15, "exact_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314-thumb.jpg", "cdx_image_exact", "15-exact_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314-thumb.jpg.body", "15-exact_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314-thumb.jpg.headers.txt", "15-exact_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314-thumb.jpg.trace.txt"),
    ]
    reconciled = list(original)
    for index, label, kind, body_name, header_name, trace_name in specs:
        body = OUT / "raw" / body_name
        header = OUT / "raw" / header_name
        rows, token = cdx_rows(body)
        status, header_map = headers(header)
        reconciled.append({
            "request_index": index,
            "label": label,
            "kind": kind,
            "status": status,
            "curl_exit": 0,
            "transport_error": False,
            "body_bytes": body.stat().st_size if body.is_file() else 0,
            "body_sha256": hashlib.sha256(body.read_bytes()).hexdigest() if body.is_file() else None,
            "headers_path": f"raw/{header_name}",
            "body_path": f"raw/{body_name}",
            "trace_path": f"raw/{trace_name}",
            "headers": header_map,
            "rows": rows,
            "rows_count": len(rows),
            "parse_error": None,
            "resume_token": token,
            "reconciled_from_raw": True,
        })
    reconciled.sort(key=lambda record: int(record.get("request_index", 0)))
    target = OUT / "request-records-reconciled.json"
    target.write_text(json.dumps(reconciled, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": "research/media-screenshots-20261015/wayback-window/request-records-reconciled.json",
        "records": len(reconciled),
        "indices": [record["request_index"] for record in reconciled],
        "reconciled_rows": {str(index): next(record["rows_count"] for record in reconciled if record["request_index"] == index) for index in (13, 14, 15)},
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
