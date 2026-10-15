"""Independently validate saved core-page evidence and derive follow-up inputs."""
import base64
import hashlib
import html
import json
import re
from collections import Counter
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from accept_network_batch1 import source_status

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BATCH = OUT / "network-core-pages3"
ANCHOR = "20080512210044"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def uri_identity(url):
    value = urlsplit(url)
    return (value.scheme.casefold(), (value.hostname or "").casefold(), value.port or (443 if value.scheme.casefold() == "https" else 80), value.path or "/", value.query)


def main():
    report_path = BATCH / "batch-report.json"
    report = read(report_path)
    errors = []
    attempts = []
    payloads = []
    index_summaries = []
    followup = []
    if len(report["results"]) != 12:
        errors.append("twelve-target conservation failed")
    for result in report["results"]:
        cdx = result["cdx"]
        query = parse_qs(urlsplit(cdx["query_url"]).query)
        if query.get("url") != [result["query_original_url"]] or query.get("matchType") != ["exact"] or query.get("to") != [ANCHOR]:
            errors.append("CDX exact query mismatch: " + result["target"])
        all_attempts = cdx["attempts"] + result.get("replay_hops", [])
        attempts.extend(h for h in all_attempts if h.get("executed"))
        raw_rows = []
        for attempt in cdx["attempts"]:
            if attempt.get("source_status") == 200:
                data = read(BATCH / attempt["raw"]["body"])
                if data:
                    raw_rows = [dict(zip(data[0], row)) for row in data[1:] if isinstance(row, list) and len(row) == len(data[0])]
                if raw_rows != cdx["capture_records"]:
                    errors.append("raw CDX row mismatch: " + result["target"])
        eligible = [row for row in raw_rows if uri_identity(row["original"]) == uri_identity(result["query_original_url"]) and str(row["timestamp"]) <= ANCHOR and str(row["statuscode"]) in {"200", "301", "302", "303", "307", "308"}]
        fields = ("timestamp", "original", "mimetype", "statuscode", "digest", "length")
        expected_eligible = {tuple(row.get(key) for key in fields) for row in eligible}
        recorded_eligible = {tuple(row.get(key) for key in fields) for row in cdx.get("eligible_capture_records", [])}
        if recorded_eligible != expected_eligible:
            errors.append("default-port exact-origin eligibility mismatch: " + result["target"])
        index_summaries.append({"target": result["target"], "rows": len(raw_rows), "status_counts": dict(Counter(str(row["statuscode"]) for row in raw_rows)), "mime_counts": dict(Counter(row["mimetype"] for row in raw_rows)), "original_authorities": dict(Counter(urlsplit(row["original"]).netloc for row in raw_rows)), "exact_origin_default_port_normalized_candidates": len(eligible), "bare_or_other_origin_records": sum(uri_identity(row["original"]) != uri_identity(result["query_original_url"]) for row in raw_rows)})
        actual_stamp = None
        if result["category"] == "valid_html":
            hop = result["replay_hops"][-1]
            body = (BATCH / hop["raw"]["body"]).read_bytes()
            headers = (BATCH / hop["raw"]["headers"]).read_text(encoding="utf-8", errors="replace")
            memento = re.search(r"^Memento-Datetime:\s*([^\r\n]+)", headers, re.M | re.I)
            actual = parsedate_to_datetime(memento.group(1)).astimezone(timezone.utc) if memento else None
            actual_stamp = actual.strftime("%Y%m%d%H%M%S") if actual else None
            selected = cdx["selected_capture"]
            body_sha1 = base64.b32encode(hashlib.sha1(body).digest()).decode("ascii")
            text = body.decode("utf-8", errors="replace")
            match = re.search(r"<title[^>]*>(.*?)</title>", text, re.S | re.I)
            title = html.unescape(re.sub(r"\s+", " ", match.group(1)).strip()) if match else None
            if actual is None or actual_stamp > ANCHOR or actual.isoformat() != result["actual_memento_or_null"]:
                errors.append("actual Memento invalid: " + result["target"])
            if not selected or not any(all(selected.get(key) == row.get(key) for key in ("timestamp", "original", "mimetype", "statuscode", "digest", "length")) for row in raw_rows) or selected["timestamp"] != actual_stamp:
                errors.append("selected capture does not bind actual payload: " + result["target"])
            if selected and body_sha1 != selected["digest"]:
                errors.append("CDX digest mismatch: " + result["target"])
            if not title or re.search(r"\b404\b|not found|page cannot be found|wayback machine", title, re.I):
                errors.append("possible error body: " + result["target"])
            payloads.append({"target": result["target"], "query_original_url": result["query_original_url"], "captured_original_url": selected["original"] if selected else None, "actual_memento": actual.isoformat() if actual else None, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(), "cdx_digest_match": body_sha1 == selected.get("digest") if selected else False, "title": title, "source_path": str((BATCH / hop["raw"]["body"]).relative_to(ROOT)).replace("\\", "/"), "integration_role": "historical_ptr_exhibit" if result["target"] == "/ptr" else "archived_news_html"})
        preferred = max(eligible, key=lambda row: row["timestamp"]) if eligible else None
        if preferred and (actual_stamp is None or preferred["timestamp"] > actual_stamp):
            followup.append({"target": result["target"], "query_original_url": result["query_original_url"], "action": "replay_saved_cdx_candidate", "candidate": preferred, "prior_accepted_memento": result.get("actual_memento_or_null"), "reason": "indexed target not replayed or newer exact-origin default-port-normalized candidate", "priority": 0 if result["target"] in {"/news/wow-news-06-2005.html", "/burningcrusade/townhall/professions.html", "/pvp/battlegrounds/battlegroups.html", "/wrath/artwork.xml"} else 2})
        elif result["target"] == "/news/wow-news2005.html" and not raw_rows:
            followup.append({"target": result["target"], "query_original_url": result["query_original_url"], "action": "retry_failed_exact_cdx_query", "query_url": cdx["query_url"], "priority": 1, "reason": "prior query never received a source HTTP response"})
    attempts.sort(key=lambda item: item["attempt"])
    starts = []
    total_bytes = 0
    for attempt in attempts:
        body = (BATCH / attempt["raw"]["body"]).read_bytes()
        headers = (BATCH / attempt["raw"]["headers"]).read_text(encoding="utf-8", errors="replace")
        if source_status(headers) != attempt["source_status"] or len(body) != attempt["body_bytes"] or (body and hashlib.sha256(body).hexdigest() != attempt["body_sha256"]):
            errors.append("raw attempt mismatch: " + str(attempt["attempt"]))
        if attempt.get("automatic_redirects") != 0:
            errors.append("automatic redirect occurred")
        starts.append(datetime.fromisoformat(attempt["started_utc"]))
        total_bytes += len(body)
    intervals = [(b-a).total_seconds() for a, b in zip(starts, starts[1:])]
    count = sum(item["source_status"] is not None for item in attempts)
    if len(attempts) != report["source_request_count"] or count != report["source_response_count"] or total_bytes != report["total_body_bytes"]:
        errors.append("aggregate attempt/response/body count mismatch")
    seconds = (datetime.fromisoformat(report["finished_utc"])-datetime.fromisoformat(report["started_utc"])).total_seconds()
    if len(attempts) > 32 or seconds > 480 or total_bytes > 67108864 or min(intervals) < 1.2:
        errors.append("bounded request/time/bytes/interval limit exceeded")
    acceptance = {"schema": "continuous-wow-core-pages-acceptance/v1", "checked_utc": datetime.now(timezone.utc).isoformat(), "accepted": not errors, "network_requests_by_acceptance": 0, "report_sha256": sha(report_path), "attempts": len(attempts), "source_http_responses": count, "total_body_bytes": total_bytes, "network_window_seconds": seconds, "minimum_start_interval_seconds": min(intervals), "accepted_payloads": payloads, "cdx_distribution": index_summaries, "selection_limitation": "Original batch excluded literal default-port URL variants. Seven older payloads remain valid; saved-row follow-up candidates preserve raw origins and do not merge bare/www hosts or schemes.", "errors": errors}
    (OUT / "core-pages3-acceptance.json").write_text(json.dumps(acceptance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    followup.sort(key=lambda item: (item["priority"], item["target"]))
    queue = {"schema": "continuous-wow-core-pages-followup/v1", "derived_from": "research/continuous-recovery-20261015/core-pages3-acceptance.json", "default_port_normalization_only": True, "original_older_entities_preserved": True, "targets": followup, "network_requests": 0}
    (OUT / "core-pages4-candidates.json").write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"accepted": not errors, "attempts": len(attempts), "source_http_responses": count, "payloads": len(payloads), "followup_targets": len(followup), "body_bytes": total_bytes, "seconds": seconds, "minimum_interval": min(intervals), "errors": errors}, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
