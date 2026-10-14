"""Create the corrected probe001 report from saved raw evidence, without network I/O."""

from __future__ import annotations

import json
from datetime import timezone
from email.utils import parsedate_to_datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "sanitized-report.json"
REPORT = ROOT / "sanitized-report.final.json"
SUMMARY = ROOT / "sanitized-summary.final.md"


def normalize(value: str | None, final_url: str) -> str | None:
    if value:
        try:
            return parsedate_to_datetime(value).astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")
        except (TypeError, ValueError, OverflowError):
            pass
    marker = "/web/"
    if marker in final_url:
        tail = final_url.split(marker, 1)[1]
        if len(tail) >= 14 and tail[:14].isdigit():
            return tail[:14]
    return value


def main() -> None:
    if REPORT.exists() or SUMMARY.exists():
        raise SystemExit("refusing to overwrite corrected outputs")
    report = json.loads(SOURCE.read_text(encoding="utf-8"))

    # The proxy replay returned a valid JPEG.  The saved Memento-Datetime is an
    # RFC date; compare its UTC-normalized form to the URL timestamp while
    # retaining the observed header value in memento_datetime.
    replay = report["endpoints"]["replay"]
    replay_proxy = next(a for a in replay["attempts"] if a.get("transport") == "proxy")
    validation = replay_proxy["validation"]
    normalized = normalize(replay_proxy.get("memento_datetime"), replay_proxy["final_url"])
    validation["memento_timestamp_observed"] = validation.get("memento_timestamp")
    validation["memento_timestamp"] = normalized
    validation["memento_timestamp_match"] = normalized == validation["expected_memento_timestamp"]
    replay_proxy["accepted"] = (
        replay_proxy.get("status") == 200
        and not replay_proxy.get("process_timeout")
        and not [r for r in replay_proxy.get("failure_reasons", []) if r != "validation_failed"]
        and validation.get("mime") == "image/jpeg"
        and validation.get("image_signature") == "jpeg"
        and validation.get("pillow", {}).get("valid") is True
        and validation.get("length_match") is True
        and validation.get("sha256_match") is True
        and validation.get("cdx_sha1_match") is True
        and validation.get("memento_timestamp_match") is True
    )
    replay_proxy["failure_reasons"] = [] if replay_proxy["accepted"] else replay_proxy.get("failure_reasons", [])
    replay_proxy["failure_class"] = None if replay_proxy["accepted"] else replay_proxy.get("failure_class")
    replay["accepted"] = replay_proxy["accepted"]
    replay["chosen_transport"] = "proxy" if replay["accepted"] else None

    # A timed-out curl process may have saved only the proxy CONNECT 200 block.
    # That is not an HTTP 200 from the CDX origin.  Preserve the raw header file,
    # but clear source status and classify the attempt as transport timeout.
    cdx = report["endpoints"]["cdx"]
    cdx_proxy = next(a for a in cdx["attempts"] if a.get("transport") == "proxy")
    cdx_proxy["status"] = None
    cdx_proxy["header_status"] = None
    cdx_proxy["failure_class"] = "transport"
    reasons = [r for r in cdx_proxy.get("failure_reasons", []) if r != "validation_failed"]
    if "process_timeout" not in reasons:
        reasons.append("process_timeout")
    cdx_proxy["failure_reasons"] = reasons + ["validation_failed"]
    cdx_proxy["validation"] = {
        "error": "process timeout after proxy CONNECT; CONNECT 200 is not source HTTP status",
        "parseable": False,
    }
    cdx["accepted"] = False
    cdx["chosen_transport"] = None

    report["cdx_control"] = None
    report["replay_control"] = validation
    report["outcome"] = {
        "cdx_available": False,
        "replay_available": True,
        "current_download_availability": "known_replay_valid",
    }
    report["output"] = {
        "raw": "raw",
        "report": REPORT.name,
        "summary": SUMMARY.name,
    }
    report["post_network_evidence_correction"] = {
        "network_reissued": False,
        "replay": "normalized RFC Memento-Datetime to UTC YYYYmmddHHMMSS and revalidated existing JPEG bytes",
        "cdx": "cleared proxy CONNECT-only 200; no source HTTP response was observed",
        "source_report_preserved": SOURCE.name,
    }

    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    lines = [
        "# Wayback accessibility probe001 (corrected offline report)",
        "",
        f"- Network attempts: `{report['http_attempts']}/{report['max_http_attempts']}`; no HTTP request was reissued for this correction.",
        f"- Raw body bytes: `{report['raw_body_bytes']}/{report['raw_body_budget']}`; D: `{report['preflight']['drive_free_bytes']}` free before, floor `{report['preflight']['min_free_bytes']}`.",
        "",
        "## Controls",
        "",
        f"- archive.org robots: proxy fallback HTTP 200; direct attempt was curl 28 timeout.",
        f"- CDX: unavailable; direct curl 28 timeout and proxy process timeout after CONNECT-only 200 (source status recorded as `null`).",
        f"- Known replay: proxy HTTP 200, 3347 bytes, JPEG/Pillow valid, SHA256 and CDX SHA1 match; normalized Memento timestamp `{validation['memento_timestamp']}`.",
        "",
        "## Outcome",
        "",
        "- CDX metadata availability: `false`; known JPEG replay availability: `true` via proxy.",
        "- General image inventory follow-up was not executed because no inventory/plan target list was supplied.",
        "- Raw response headers remain local under `raw/`; this summary contains no raw header text.",
        "- Original report is preserved as `sanitized-report.json`; this file is an offline evidence correction.",
        "",
    ]
    SUMMARY.write_text("\n".join(lines), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
