"""Validate shared-asset backup ZIPs and emit a derived content report.

This intentionally does not alter manifest/error files.  A successful HTTP
response is still subject to a small, deterministic image-content check.
"""

from __future__ import annotations

import argparse
import datetime as _datetime
import hashlib
import json
from pathlib import Path
import re
import urllib.parse
import zipfile
from typing import Any


PNG = b"\x89PNG\r\n\x1a\n"


def _magic(extension: str, data: bytes) -> tuple[bool | None, str]:
    extension = extension.casefold()
    if extension in {".jpg", ".jpeg"}:
        return data.startswith(b"\xff\xd8\xff"), "jpeg"
    if extension == ".gif":
        return data.startswith((b"GIF87a", b"GIF89a")), "gif"
    if extension == ".png":
        return data.startswith(PNG), "png"
    if extension == ".swf":
        return data.startswith((b"FWS", b"CWS", b"ZWS")), "swf"
    if extension == ".webp":
        return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP", "webp"
    return None, "unclassified"


def _soft_404(data: bytes) -> bool:
    sample = data[:64 * 1024].decode("utf-8", errors="ignore")
    # Archived origin pages commonly prefix the standard title with the site
    # name, e.g. "World of Warcraft - 404 File Not Found".
    return bool(re.search(r"<title>[^<]*404\s+file\s+not\s+found[^<]*</title>", sample, re.I))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number} is not an object")
            records.append(value)
    return records


def _key(record: dict[str, Any]) -> tuple[str, str]:
    return str(record.get("original", "")), str(record.get("requested_timestamp", ""))


def validate(plan_path: Path, output_dir: Path) -> dict[str, Any]:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    items = list(plan.get("items", []))
    records = _load_jsonl(output_dir / "manifest.jsonl")
    success = [record for record in records if record.get("status") == "success"]
    failed = [record for record in records if record.get("status") == "failed"]
    volumes: dict[str, zipfile.ZipFile] = {}
    crc_errors: list[str] = []
    for path in sorted(output_dir.glob("objects-*.zip")):
        archive = zipfile.ZipFile(path, "r", allowZip64=True)
        volumes[path.name] = archive
        bad = archive.testzip()
        if bad is not None:
            crc_errors.append(f"{path.name}:{bad}")

    item_reports: list[dict[str, Any]] = []
    verification_errors: list[str] = []
    expected_keys = {(str(item.get("original")), str(item.get("timestamp"))): item for item in items}
    success_by_key = {_key(record): record for record in success}
    manifest_keys = {_key(record) for record in records}
    unattempted = [
        {
            "original": str(item.get("original")),
            "requested_timestamp": str(item.get("timestamp")),
            "role": item.get("role"),
            "reason": "not_attempted_after_stop",
        }
        for key, item in expected_keys.items()
        if key not in manifest_keys
    ]
    actual_after_cutoff: list[dict[str, Any]] = []
    missing_memento: list[dict[str, Any]] = []

    for key, record in success_by_key.items():
        actual = record.get("actual_timestamp")
        if not record.get("memento_datetime"):
            missing_memento.append({"original": key[0], "requested_timestamp": key[1]})
        if isinstance(actual, str) and len(actual) >= 8 and actual[:8].isdigit() and actual[:8] > "20101231":
            actual_after_cutoff.append({
                "original": key[0],
                "requested_timestamp": key[1],
                "actual_timestamp": actual,
            })

        reason: list[str] = []
        data = b""
        try:
            part = str(record["zip_part"])
            entry = str(record["zip_entry"])
            data = volumes[part].read(entry)
            digest = hashlib.sha256(data).hexdigest()
            if digest != record.get("sha256"):
                verification_errors.append(f"{key[0]}:SHA mismatch")
            if len(data) != int(record.get("content_length", -1)):
                verification_errors.append(f"{key[0]}:length mismatch")
        except (KeyError, ValueError, OSError, zipfile.BadZipFile) as exc:
            verification_errors.append(f"{key[0]}:missing or unreadable ZIP reference:{exc}")
        item = expected_keys.get(key, {})
        role = item.get("role", record.get("role"))
        extension = Path(urllib.parse.urlsplit(key[0]).path).suffix.casefold()
        is_soft_404 = _soft_404(data)
        magic_ok, magic_type = _magic(extension, data)
        if role == "shared_image":
            if is_soft_404:
                status = "invalid-image"
                reason.append("html_soft404")
            elif magic_ok is False:
                status = "invalid-image"
                reason.append(f"magic_mismatch:{magic_type}")
            elif magic_ok is True:
                status = "valid-image"
            else:
                status = "unclassified-image"
                reason.append("unknown_extension")
        else:
            status = "http-success-non-image"
            if is_soft_404:
                status = "http-success-soft404"
                reason.append("html_soft404")
        item_reports.append({
            "original": key[0],
            "requested_timestamp": key[1],
            "actual_timestamp": record.get("actual_timestamp"),
            "role": role,
            "status": status,
            "extension": extension,
            "magic_type": magic_type,
            "magic_ok": magic_ok,
            "soft404_title": is_soft_404,
            "sha256": record.get("sha256"),
            "content_length": record.get("content_length"),
            "zip_part": record.get("zip_part"),
            "zip_entry": record.get("zip_entry"),
            "reasons": reason,
        })

    for archive in volumes.values():
        archive.close()

    summary_path = output_dir / "summary.json"
    run_summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    missing = list(run_summary.get("missing", []))
    expected_success = len(expected_keys)
    image_reports = [r for r in item_reports if r.get("role") == "shared_image"]
    return {
        "schema_version": 1,
        "generated_at": _datetime.datetime.now(_datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "plan": str(plan_path),
        "output": str(output_dir),
        "run": {
            "planned_items": len(items),
            "manifest_success_records": len(success),
            "manifest_failed_records": len(failed),
            "summary_success": run_summary.get("stats", {}).get("success"),
            "summary_failed": run_summary.get("stats", {}).get("failed"),
            "summary_missing_entries": len(missing),
            "unattempted_items": len(unattempted),
            "distinct_incomplete_items": len(unattempted) + len(failed),
            "stop_reason": run_summary.get("stop_reason"),
            "requests_started": run_summary.get("stats", {}).get("requests_started"),
            "content_bytes": run_summary.get("stats", {}).get("content_bytes"),
            "compressed_bytes": run_summary.get("stats", {}).get("compressed_bytes"),
        },
        "archive_validation": {
            "zip_volumes": len(volumes),
            "crc_errors": crc_errors,
            "verification_errors": verification_errors,
            "crc_ok": not crc_errors,
            "sha_and_lengths_ok": not verification_errors,
        },
        "content_validation": {
            "planned_success_keys": expected_success,
            "validated_success_records": len(item_reports),
            "valid_images": sum(r["status"] == "valid-image" for r in image_reports),
            "invalid_images": sum(r["status"] == "invalid-image" for r in image_reports),
            "unclassified_images": sum(r["status"] == "unclassified-image" for r in image_reports),
            "soft404_successes": sum(bool(r["soft404_title"]) for r in item_reports),
        },
        "anomalies": {
            "actual_capture_after_20101231": actual_after_cutoff,
            "success_without_memento_datetime": missing_memento,
        },
        "failures": failed,
        "missing": missing,
        "unattempted": sorted(unattempted, key=lambda r: (r["original"], r["requested_timestamp"])),
        "items": sorted(item_reports, key=lambda r: (r["original"], r["requested_timestamp"])),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = validate(args.plan, args.out)
    destination = args.report or (args.out / "content-validation.json")
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "report": str(destination),
        "crc_ok": report["archive_validation"]["crc_ok"],
        "sha_and_lengths_ok": report["archive_validation"]["sha_and_lengths_ok"],
        "valid_images": report["content_validation"]["valid_images"],
        "invalid_images": report["content_validation"]["invalid_images"],
        "soft404_successes": report["content_validation"]["soft404_successes"],
        "actual_after_20101231": len(report["anomalies"]["actual_capture_after_20101231"]),
        "success_without_memento": len(report["anomalies"]["success_without_memento_datetime"]),
    }, ensure_ascii=False, sort_keys=True))
    return 0 if report["archive_validation"]["crc_ok"] and report["archive_validation"]["sha_and_lengths_ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
