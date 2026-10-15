"""Independently inspect persisted network evidence; never issue requests."""
from __future__ import annotations

import hashlib
import io
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BATCH = OUT / "wayback-karazhan-batch1"
EXPECTED_BASELINE = "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_status(headers: str) -> int | None:
    statuses = []
    for line in headers.splitlines():
        match = re.match(r"^HTTP/\d(?:\.\d)?\s+(\d{3})(?:\s+(.*))?$", line.strip(), re.I)
        if match and "connection established" not in (match.group(2) or "").lower():
            statuses.append(int(match.group(1)))
    return statuses[-1] if statuses else None


def main() -> None:
    report_path = BATCH / "batch-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    old = json.loads((ROOT / report["inputs"]["batch_report"]).read_text(encoding="utf-8"))
    expected = []
    for item in old["results"]:
        if item["category"] == "transport_error" and not any(h.get("source_status") is not None for h in item.get("hops", [])):
            if item["original_url"] not in expected:
                expected.append(item["original_url"])
    errors = []
    if [r["original_url"] for r in report["results"]] != expected[:30]:
        errors.append("candidate order does not match the first thirty old unknown original URLs")
    hops = [h for r in report["results"] for h in r.get("hops", []) if h.get("executed")]
    payloads = []
    valid_images = 0
    for hop in hops:
        body_path = (BATCH / hop["body_path"]).resolve()
        headers_path = (BATCH / hop["headers_path"]).resolve()
        if not body_path.is_relative_to(BATCH.resolve()) or not headers_path.is_relative_to(BATCH.resolve()):
            errors.append("evidence path escaped batch directory")
            continue
        body = body_path.read_bytes()
        headers = headers_path.read_text(encoding="utf-8", errors="replace")
        actual_status = source_status(headers)
        if actual_status != hop.get("source_status"):
            errors.append(f"source status mismatch: {headers_path.name}")
        if len(body) != hop["body_bytes"]:
            errors.append(f"length mismatch: {body_path.name}")
        if body and sha256(body) != hop.get("body_sha256"):
            errors.append(f"SHA256 mismatch: {body_path.name}")
        if not body and hop.get("body_sha256") is not None:
            errors.append(f"empty local artifact claimed as source payload: {body_path.name}")
        if actual_status == 404:
            text = body.decode("utf-8", errors="replace").lower()
            if not ("wayback machine" in text and "has not archived" in text):
                errors.append(f"404 body lacks expected unarchived marker: {body_path.name}")
        decoded = False
        try:
            Image.open(io.BytesIO(body)).verify()
            image = Image.open(io.BytesIO(body))
            image.load()
            decoded = True
            valid_images += 1
        except Exception:
            pass
        payloads.append({"target_id": hop["target_id"], "transport": hop["transport"], "source_status": actual_status, "curl_exit": hop.get("curl_exit"), "body_bytes": len(body), "body_sha256": sha256(body) if body else None, "decoded_image": decoded})
    counts = {"source_request_count": len(hops), "transport_attempt_count": len(hops), "source_response_count": sum(h.get("source_status") is not None for h in hops), "failed_attempt_count": sum(h.get("source_status") is None for h in hops)}
    for key, count in counts.items():
        if report.get(key) != count:
            errors.append(f"aggregate mismatch: {key} report={report.get(key)} actual={count}")
    body_bytes = sum(p["body_bytes"] for p in payloads)
    if body_bytes != report["total_body_bytes"]:
        errors.append("aggregate body bytes mismatch")
    if len(hops) > 32 or body_bytes > 64 * 1024 * 1024 or any(p["body_bytes"] > 16 * 1024 * 1024 for p in payloads):
        errors.append("network resource limit exceeded")
    baseline = sha256((ROOT / "offline/build-manifest.json").read_bytes())
    if baseline != EXPECTED_BASELINE:
        errors.append("frozen baseline changed")
    started = datetime.fromisoformat(report["started_utc"])
    finished = datetime.fromisoformat(report["finished_utc"])
    seconds = (finished - started).total_seconds()
    if seconds > 480 or seconds < 0:
        errors.append(f"network window outside bounds: {seconds}")
    result = {
        "schema": "continuous-wow-network-acceptance/v1",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "accepted": not errors,
        "network_requests_by_acceptance": 0,
        "report": str(report_path.relative_to(ROOT)).replace("\\", "/"),
        "report_sha256": sha256(report_path.read_bytes()),
        "counts": counts,
        "target_categories": dict(Counter(r["category"] for r in report["results"])),
        "body_bytes": body_bytes,
        "valid_images": valid_images,
        "network_window_seconds": seconds,
        "baseline_sha256": baseline,
        "prior_karazhan_not_archived": 59,
        "newly_classified_not_archived": sum(r["category"] == "not_archived" for r in report["results"]),
        "remaining_transport_unknown_total": 67 - sum(r["category"] == "not_archived" for r in report["results"]),
        "checks": ["candidate order", "raw source headers excluding CONNECT", "all persisted body lengths and SHA256", "Wayback unarchived HTML marker", "independent Pillow image decoding", "aggregate counts", "request and body limits", "network window", "frozen manifest hash"],
        "not_independently_verified": ["1.2-second scheduling interval is enforced by the inspected serial script; per-hop absolute start timestamps are not stored in the report", "disk-free measurements are batch receipts, not historical volume telemetry"],
        "errors": errors,
        "payloads": payloads,
    }
    (OUT / "network-batch1-acceptance.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in {"payloads", "checks", "not_independently_verified"}}, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
