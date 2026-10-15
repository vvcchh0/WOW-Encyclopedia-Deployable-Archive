"""NET-RSS-010 bounded exact RSS recovery.

This small adapter owns only ``network-rss10``.  It reuses the accepted
NET-WRATH-008/core-pages3 transport and NET-CONTROL-007 dispatch gate, and
the RSS006 body observers.  The adapter adds only the 2006-07..2007-05
candidate declaration, RSS/HTML month evidence, and report assembly.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
RECONCILIATION = ROOT / "research/continuous-recovery-20261015/local-target-reconcile/reconciliation.json"
RECON_ACCEPTANCE = ROOT / "research/continuous-recovery-20261015/local-target-reconcile-acceptance.json"
RSS6_CANDIDATES = ROOT / "research/continuous-recovery-20261015/network-rss6/candidates.json"
RSS6_REPORT = ROOT / "research/continuous-recovery-20261015/network-rss6/batch-report.json"
RSS6_ACCEPTANCE = ROOT / "research/continuous-recovery-20261015/rss6-acceptance.json"
W8_PATH = ROOT / "research/continuous-recovery-20261015/network-wrath8/wrath8.py"
RSS6_PATH = ROOT / "research/continuous-recovery-20261015/network-rss6/rss_batch6.py"
GATE_PATH = ROOT / "research/continuous-recovery-20261015/network-control7/control7.py"
CORE_PATH = ROOT / "research/continuous-recovery-20261015/network-core-pages3/core_pages3.py"

EXPECTED_RECON_SHA256 = "81f346c89100204d35448e5c1d20fcfa7532f3e9b7569b5edff2ea1886735016"
EXPECTED_RSS10 = [
    "http://www.worldofwarcraft.com/news/rss-05-2007.xml",
    "http://www.worldofwarcraft.com/news/rss-04-2007.xml",
    "http://www.worldofwarcraft.com/news/rss-03-2007.xml",
    "http://www.worldofwarcraft.com/news/rss-02-2007.xml",
    "http://www.worldofwarcraft.com/news/rss-01-2007.xml",
    "http://www.worldofwarcraft.com/news/rss-12-2006.xml",
    "http://www.worldofwarcraft.com/news/rss-11-2006.xml",
    "http://www.worldofwarcraft.com/news/rss-10-2006.xml",
    "http://www.worldofwarcraft.com/news/rss-09-2006.xml",
    "http://www.worldofwarcraft.com/news/rss-08-2006.xml",
    "http://www.worldofwarcraft.com/news/rss-07-2006.xml",
]

MAX_TARGETS = 11
MAX_ATTEMPTS = 32
WINDOW_SECONDS = 8 * 60
INTERVAL_SECONDS = 1.25
MIN_FREE_BYTES = 11_005_853_696
MAX_TOTAL_BODY_BYTES = 64 * 1024 * 1024
MAX_ENTITY_BODY_BYTES = 16 * 1024 * 1024
PROXY = "http://127.0.0.1:7890"
USER_AGENT = "wow-recovery-rss10/20261015"
STOP_CODES = {429, 503}
REDIRECT_CODES = {301, 302, 303, 307, 308}
RSS_RE = re.compile(r"^/news/rss-(\d{2})-(\d{4})\.xml$")


def load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


w8 = load(W8_PATH, "rss10_accepted_w8")
rss6 = load(RSS6_PATH, "rss10_accepted_rss6")
core = w8.core
gate_mod = w8.gate_mod

# The imported accepted helpers are redirected only in memory.  No accepted
# batch output is changed; all transport files written by this process land
# below this batch directory.
w8.OUT = OUT
w8.RAW = RAW
w8.MAX_ATTEMPTS = MAX_ATTEMPTS
w8.WINDOW = WINDOW_SECONDS
w8.INTERVAL = INTERVAL_SECONDS
w8.MIN_FREE = MIN_FREE_BYTES
w8.MAX_TOTAL = MAX_TOTAL_BODY_BYTES
w8.MAX_ENTITY = MAX_ENTITY_BODY_BYTES
w8.PROXY = PROXY
w8.UA = USER_AGENT
core.OUT = OUT
core.RAW = RAW
core.USER_AGENT = USER_AGENT
core.PROXY = PROXY
core.MAX_ATTEMPTS = MAX_ATTEMPTS
core.WINDOW_SECONDS = WINDOW_SECONDS
core.MIN_INTERVAL_SECONDS = 0.0
core.MIN_FREE_BYTES = MIN_FREE_BYTES
core.MAX_TOTAL_BODY_BYTES = MAX_TOTAL_BODY_BYTES
core.MAX_ENTITY_BODY_BYTES = MAX_ENTITY_BODY_BYTES
gate_mod.INTERVAL_SECONDS = INTERVAL_SECONDS
gate_mod.OUT = OUT
gate_mod.RAW = RAW
rss6.OUT = OUT
rss6.RAW = RAW
rss6.core.OUT = OUT
rss6.core.RAW = RAW


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def relative(path: Path) -> str:
    return path.relative_to(OUT).as_posix()


def free_bytes() -> int:
    return int(shutil.disk_usage(OUT).free)


def input_digest(path: Path) -> dict[str, Any]:
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(path), "bytes": path.stat().st_size}


def parse_target(target: str, original: str) -> tuple[int, int]:
    target_match = RSS_RE.fullmatch(target)
    original_match = re.fullmatch(r"http://www\.worldofwarcraft\.com/news/rss-(\d{2})-(\d{4})\.xml", original)
    if not target_match or not original_match or target_match.groups() != original_match.groups():
        raise RuntimeError(f"RSS target/original is not exact: {target} / {original}")
    month, year = int(target_match.group(1)), int(target_match.group(2))
    if not 1 <= month <= 12:
        raise RuntimeError(f"invalid RSS month: {target}")
    return year, month


def verify_inputs() -> dict[str, Any]:
    paths = [RECONCILIATION, RECON_ACCEPTANCE, RSS6_CANDIDATES, RSS6_REPORT, RSS6_ACCEPTANCE]
    if any(not path.exists() for path in paths):
        raise RuntimeError("one or more RSS010 provenance inputs are missing")
    recon_sha = sha(RECONCILIATION)
    if recon_sha != EXPECTED_RECON_SHA256:
        raise RuntimeError(f"reconciliation SHA mismatch: {recon_sha}")
    recon = read(RECONCILIATION)
    acceptance = read(RECON_ACCEPTANCE)
    if acceptance.get("accepted") is not True or acceptance.get("network_requests") != 0:
        raise RuntimeError("local reconciliation acceptance is not accepted/network-free")
    if acceptance.get("report_sha256") != EXPECTED_RECON_SHA256:
        raise RuntimeError("local reconciliation acceptance does not bind frozen report SHA")
    if recon.get("network_performed") or recon.get("network_request_count") != 0:
        raise RuntimeError("reconciliation unexpectedly records network activity")

    rss_rows: dict[str, dict[str, Any]] = {}
    for row in recon.get("rows") or []:
        target = str(row.get("target") or "")
        original = str(row.get("exact_original_url") or "")
        if not RSS_RE.fullmatch(target):
            continue
        year, month = parse_target(target, original)
        if not row.get("source_menu"):
            raise RuntimeError(f"RSS row has no source menu: {target}")
        value = dict(row)
        value.update({"year": year, "month": month, "query_original": original})
        rss_rows[original] = value
    if len(rss_rows) != 23:
        raise RuntimeError(f"expected 23 exact RSS rows, got {len(rss_rows)}")

    old_candidates = read(RSS6_CANDIDATES)
    old_report = read(RSS6_REPORT)
    old_acceptance = read(RSS6_ACCEPTANCE)
    old_originals = [str(row.get("query_original") or "") for row in old_candidates.get("targets") or []]
    if len(old_originals) != 12 or len(set(old_originals)) != 12:
        raise RuntimeError("RSS006 candidate evidence is not twelve distinct exact originals")
    if set(old_originals) & set(EXPECTED_RSS10):
        raise RuntimeError("RSS010 overlaps an RSS006 candidate")
    if old_report.get("schema") != "continuous-wow-rss6-report/v1" or old_report.get("target_count") != 12:
        raise RuntimeError("RSS006 report identity mismatch")
    if old_acceptance.get("accepted") is not True or old_acceptance.get("report_sha256") != sha(RSS6_REPORT):
        raise RuntimeError("RSS006 acceptance does not bind the saved RSS006 report")

    selected = [rss_rows[original] for original in EXPECTED_RSS10]
    if any(original not in rss_rows for original in EXPECTED_RSS10):
        raise RuntimeError("one or more declared RSS010 originals are absent from reconciliation")
    return {
        "reconciliation": recon,
        "reconciliation_sha256": recon_sha,
        "acceptance": acceptance,
        "rss_rows": rss_rows,
        "selected": selected,
        "rss6_candidates": old_candidates,
        "rss6_report": old_report,
        "rss6_acceptance": old_acceptance,
        "input_digests": {str(path.relative_to(ROOT)).replace("\\", "/"): input_digest(path) for path in paths},
    }


def policy() -> dict[str, Any]:
    return {
        "max_targets": MAX_TARGETS,
        "max_attempts": MAX_ATTEMPTS,
        "network_window_seconds": WINDOW_SECONDS,
        "minimum_dispatch_interval_seconds": INTERVAL_SECONDS,
        "minimum_free_bytes": MIN_FREE_BYTES,
        "max_total_body_bytes": MAX_TOTAL_BODY_BYTES,
        "max_entity_body_bytes": MAX_ENTITY_BODY_BYTES,
        "direct_first_then_confirmed_transport": True,
        "direct_connect_timeout_seconds": core.DIRECT_CONNECT_SECONDS,
        "direct_total_timeout_seconds": core.DIRECT_MAX_SECONDS,
        "proxy": PROXY,
        "proxy_connect_timeout_seconds": core.PROXY_CONNECT_SECONDS,
        "proxy_total_timeout_seconds": core.PROXY_MAX_SECONDS,
        "automatic_redirects": 0,
        "manual_redirect_follow": 0,
        "stop_http_codes": sorted(STOP_CODES),
        "tls_verification": "curl_default_verification_enabled",
        "concurrent_source_requests": 1,
        "cdx": {
            "from": core.FROM_TIMESTAMP,
            "to": core.TO_TIMESTAMP,
            "match_type": "exact",
            "columns": core.CDX_COLUMNS,
            "limit": core.CDX_LIMIT,
            "collapse": "digest",
            "selection": "latest same-origin status-200 pre-anchor capture; redirects retained as index evidence and never followed",
        },
        "uri_identity": "same scheme, lower-cased host, path and query; only default ports normalize; bare/www and http/https remain separate",
        "body_classification": "real body RSS/Atom/XML versus expanded HTML; XML extension never substitutes for body format",
        "script_execution": False,
    }


def make_candidates(inputs: dict[str, Any]) -> dict[str, Any]:
    selected = []
    for rank, row in enumerate(inputs["selected"], start=1):
        selected.append({
            "rank": rank,
            "target": row["target"],
            "query_original": row["query_original"],
            "year": row["year"],
            "month": row["month"],
            "source_menu": row["source_menu"],
            "cdx_query_url": core.cdx_query_url(row["query_original"]),
            "selection": "latest same-origin status-200 capture within exact pre-anchor CDX query",
            "same_origin_policy": "same scheme/lowercase host/path/query; only default HTTP80 or HTTPS443 normalizes",
            "body_policy": "classify observed body; do not execute scripts or infer XML from .xml extension",
        })
    old_targets = inputs["rss6_candidates"].get("targets") or []
    return {
        "schema": "continuous-wow-network-rss10-candidates/v1",
        "batch_id": "NET-RSS-010",
        "generated_utc": utc(),
        "network_requests": 0,
        "target_count": len(selected),
        "selection": {
            "rule": "newest-to-oldest exact URL month order for 2007-05..2006-07",
            "included_originals": [row["query_original"] for row in selected],
            "rss6_exclusion_count": len(old_targets),
            "rss6_excluded_originals": [row["query_original"] for row in old_targets],
            "rss6_exclusion_reason": "already selected in RSS006; do not retry failed or not_requested RSS006 members",
            "overlap_count": 0,
        },
        "targets": selected,
        "policy": policy(),
        "input_digests": inputs["input_digests"],
        "accepted_reuse": {
            "transport": str(W8_PATH.relative_to(ROOT)).replace("\\", "/"),
            "dispatch_gate": str(GATE_PATH.relative_to(ROOT)).replace("\\", "/"),
            "rss_body_helpers": str(RSS6_PATH.relative_to(ROOT)).replace("\\", "/"),
            "no_accepted_outputs_modified": True,
        },
    }


def prepare() -> int:
    inputs = verify_inputs()
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    candidates = make_candidates(inputs)
    write(OUT / "candidates.json", candidates)
    write(OUT / "batch-config.json", {
        "schema": "continuous-wow-network-rss10-config/v1",
        "batch_id": "NET-RSS-010",
        "candidate_sha256": sha(OUT / "candidates.json"),
        "candidate_path": str((OUT / "candidates.json").relative_to(ROOT)).replace("\\", "/"),
        "network_requests": 0,
        "policy": candidates["policy"],
        "accepted_reuse": candidates["accepted_reuse"],
    })
    d = free_bytes()
    plan = {
        "schema": "continuous-wow-network-rss10-plan/v1",
        "batch_id": "NET-RSS-010",
        "mode": "plan_only",
        "prepared_utc": utc(),
        "candidate_sha256": sha(OUT / "candidates.json"),
        "target_count": len(candidates["targets"]),
        "target_order": [row["query_original"] for row in candidates["targets"]],
        "disk_free_bytes": d,
        "minimum_free_bytes": MIN_FREE_BYTES,
        "network_requests": 0,
        "ready": d >= MIN_FREE_BYTES,
        "rss6_exclusion": candidates["selection"],
    }
    write(OUT / "plan.json", plan)
    print(json.dumps({
        "mode": "plan_only",
        "batch_id": "NET-RSS-010",
        "network_requests": 0,
        "target_count": len(candidates["targets"]),
        "targets": plan["target_order"],
        "candidate_sha256": plan["candidate_sha256"],
        "disk_free_bytes": d,
        "ready": plan["ready"],
    }, ensure_ascii=False))
    return 0


def body(attempt: dict[str, Any] | None) -> bytes:
    return w8.body(attempt)


def public_attempt(attempt: dict[str, Any]) -> dict[str, Any]:
    return core.source_attempt_view(attempt)


def latest_status_200(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    eligible = [row for row in records if row.get("statuscode_int") == 200 and row.get("valid_replay_candidate")]
    return sorted(eligible, key=lambda row: row.get("timestamp", ""), reverse=True)[0] if eligible else None


MONTH_NUMBERS = {
    name.lower(): number for number, name in enumerate(
        ("January", "February", "March", "April", "May", "June", "July", "August",
         "September", "October", "November", "December"), start=1
    )
}


def date_month_pairs(text: str) -> list[tuple[str, tuple[int, int]]]:
    """Extract conservative visible date forms without treating numeric IDs as dates."""
    found: list[tuple[str, tuple[int, int]]] = []
    named = re.compile(
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)"
        r"\s+\d{1,2},?\s+((?:19|20)\d{2})\b", re.IGNORECASE)
    iso = re.compile(r"\b((?:19|20)\d{2})[-/](\d{1,2})[-/](\d{1,2})\b")
    mdy = re.compile(r"\b(\d{1,2})[-/](\d{1,2})[-/](\d{2})\b")
    for match in named.finditer(text):
        found.append((match.group(0), (int(match.group(2)), MONTH_NUMBERS[match.group(1).lower()])))
    for match in iso.finditer(text):
        month = int(match.group(2))
        if 1 <= month <= 12:
            found.append((match.group(0), (int(match.group(1)), month)))
    for match in mdy.finditer(text):
        month, day, short_year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if 1 <= month <= 12 and 1 <= day <= 31:
            found.append((match.group(0), (2000 + short_year if short_year < 70 else 1900 + short_year, month)))
    return found


def title_month_pairs(title: str) -> list[tuple[str, tuple[int, int]]]:
    pattern = re.compile(
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)"
        r"\s*,?\s*((?:19|20)\d{2})\b", re.IGNORECASE)
    return [(match.group(0), (int(match.group(2)), MONTH_NUMBERS[match.group(1).lower()]))
            for match in pattern.finditer(title)]


def month_evidence_from_pairs(values: list[tuple[str, tuple[int, int]]], year: int, month: int) -> dict[str, Any]:
    matching = [value for value, pair in values if pair == (year, month)]
    mismatch = [value for value, pair in values if pair != (year, month)]
    if matching and mismatch:
        state = "mixed"
    elif matching:
        state = "match"
    elif mismatch:
        state = "mismatch"
    else:
        state = "unknown"
    return {
        "expected_year": year,
        "expected_month": month,
        "date_field_count": len(values),
        "matching_count": len(matching),
        "mismatch_count": len(mismatch),
        "unparseable_count": 0,
        "matching_examples": matching[:10],
        "mismatch_examples": mismatch[:10],
        "unparseable_examples": [],
        "state": state,
    }


def html_date_evidence(body_bytes: bytes, observation: dict[str, Any], year: int, month: int) -> dict[str, Any]:
    text = body_bytes.decode("utf-8", errors="replace")
    title = str(observation.get("title") or "")
    body_dates = date_month_pairs(text)
    title_dates = title_month_pairs(title)
    body_evidence = month_evidence_from_pairs(body_dates, year, month)
    title_evidence = month_evidence_from_pairs(title_dates, year, month)
    title_mismatch = bool(title_dates and any(pair != (year, month) for _, pair in title_dates))
    body_match = any(pair == (year, month) for _, pair in body_dates)
    return {
        "declared_url_year": year,
        "declared_url_month": month,
        "title": observation.get("title"),
        "title_date_tokens": [value for value, _ in title_dates[:20]],
        "title_year_months": [[y, m] for _, (y, m) in title_dates[:20]],
        "title_matches_url_month": [pair == (year, month) for _, pair in title_dates[:20]],
        "title_month_evidence": title_evidence,
        "posted_or_visible_date_tokens": [value for value, _ in body_dates[:100]],
        "posted_or_visible_year_months": [[y, m] for _, (y, m) in body_dates[:100]],
        "posted_date_evidence": body_evidence,
        "article_month_matches_url": body_match,
        "source_anomaly": (
            "title_month_differs_but_body_date_matches" if title_mismatch and body_match
            else "title_month_differs_from_declared_url" if title_mismatch else None
        ),
    }


def validate_replay(item: dict[str, Any], replay: dict[str, Any], capture: dict[str, Any]) -> tuple[str, str, dict[str, Any] | None]:
    if not replay or not replay.get("executed"):
        return "not_requested", replay.get("unrequested_reason", "replay_not_requested") if replay else "replay_not_requested", None
    status = replay.get("source_status")
    if replay.get("transport_error"):
        return "transport_error", replay.get("transport_reason") or "curl_or_tls_failure", None
    if status in STOP_CODES:
        return "rate_limited", f"source_status_{status}", {"retry_after": replay.get("retry_after")}
    if status == 404:
        return "not_archived", "replay_http_404", None
    if status != 200:
        return "http_response", f"source_status_{status}", None
    valid, reason, metrics = rss6.validate_body(replay, capture, item["year"], item["month"])
    metrics["valid"] = valid
    metrics["validation_reason"] = reason
    if metrics.get("body_format") == "html":
        observation = metrics.get("body_observation") or {}
        metrics["html_month_evidence"] = html_date_evidence(body(replay), observation, item["year"], item["month"])
    if valid and metrics.get("body_format") == "rss_xml":
        return "valid_rss_payload", reason, metrics
    if valid and metrics.get("body_format") == "html":
        return "valid_html_payload", reason, metrics
    if reason == "not_archived_or_error_html":
        return "soft404", reason, metrics
    return "invalid_payload", reason, metrics


def unrequested_result(item: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "rank": item["rank"],
        "target": item["target"],
        "query_original": item["query_original"],
        "year": item["year"],
        "month": item["month"],
        "source_menu": item["source_menu"],
        "query_url": item["cdx_query_url"],
        "cdx": {"query_performed": False, "source_status": None, "source_response_count": 0,
                "capture_index_count": 0, "eligible_status_200_count": 0, "redirect_index_count": 0,
                "capture_records": [], "selected_capture": None, "other_origin_metadata": None, "attempts": []},
        "replay_attempt_count": 0,
        "replay_source_response_count": 0,
        "replay_hops": [],
        "category": "not_requested",
        "reason": reason,
        "actual_memento": None,
        "source_status": None,
        "content_type": None,
        "body_bytes": 0,
        "body_sha256": None,
        "validation": None,
        "entity_valid": False,
        "unrequested_reason": reason,
    }


def run_one(item: dict[str, Any], transport: str | None, state: Any, gate: Any, window_started: float) -> tuple[dict[str, Any], str]:
    attempts: list[dict[str, Any]] = []

    def issue(url: str, chosen_transport: str, kind: str) -> dict[str, Any]:
        ok, why = w8.dispatch_ok(state, window_started)
        if not ok:
            if why and not state.stop_reason:
                state.stop_reason = why
                state.stop_detail = {"reason": why}
            return {"executed": False, "attempt": state.attempts + 1, "kind": kind,
                    "target_key": item["query_original"], "transport": chosen_transport, "url": url,
                    "unrequested_reason": why or "limit_before_request"}
        return w8.request(url, chosen_transport, kind, item["query_original"], state, gate, window_started)

    chosen = transport
    if chosen is None:
        query = issue(item["cdx_query_url"], "direct", "cdx")
        attempts.append(query)
        if query.get("executed") and query.get("transport_error") and not state.stop_reason:
            query_proxy = issue(item["cdx_query_url"], "proxy", "cdx")
            attempts.append(query_proxy)
            chosen = "proxy"
        else:
            chosen = "direct"
    else:
        attempts.append(issue(item["cdx_query_url"], chosen, "cdx"))

    query = next((value for value in reversed(attempts) if value.get("executed")), attempts[-1] if attempts else None)
    records = (query or {}).get("cdx_records") or []
    valid_all: list[dict[str, Any]] = []
    selected = None
    replays: list[dict[str, Any]] = []
    if query and query.get("executed") and query.get("source_status") == 200 and query.get("cdx_parse_valid"):
        valid_all = core.valid_cdx_records(records, item["query_original"])
        eligible = [row for row in valid_all if row.get("statuscode_int") == 200]
        selected = latest_status_200(valid_all)
        query["cdx_valid_records"] = valid_all
        query["cdx_eligible_status200_records"] = eligible
        query["cdx_capture_index_count"] = len(records)
        query["cdx_valid_capture_count"] = len(eligible)
        if selected is not None and not state.stop_reason:
            replays.append(issue(core.replay_url(selected), chosen or "direct", "replay"))

    if not query or not query.get("executed"):
        category, reason, validation = "not_requested", (query or {}).get("unrequested_reason", "query_not_requested"), None
    elif query.get("transport_error"):
        category, reason, validation = "transport_error", query.get("transport_reason") or "curl_or_tls_failure", None
    elif query.get("source_status") in STOP_CODES:
        category, reason, validation = "rate_limited", f"source_status_{query.get('source_status')}", {"retry_after": query.get("retry_after")}
    elif not query.get("cdx_parse_valid"):
        category, reason, validation = "cdx_invalid", query.get("cdx_parse_error") or "cdx_parse_failed", None
    elif not records:
        category, reason, validation = "cdx_empty_in_range", "no_index_rows_in_requested_range", None
    elif selected is None:
        category, reason, validation = "cdx_no_valid_200", "index_rows_without_same_origin_status_200", None
    elif not replays or not replays[-1].get("executed"):
        category, reason, validation = "not_requested", (replays[-1] if replays else {}).get("unrequested_reason", "replay_not_requested"), None
    else:
        category, reason, validation = validate_replay(item, replays[-1], selected)

    final = replays[-1] if replays else None
    raw = body(final)
    result = {
        "rank": item["rank"],
        "target": item["target"],
        "query_original": item["query_original"],
        "year": item["year"],
        "month": item["month"],
        "source_menu": item["source_menu"],
        "query_url": item["cdx_query_url"],
        "cdx": {
            "query_performed": bool(attempts),
            "source_status": query.get("source_status") if query else None,
            "source_response_count": sum(value.get("source_status") is not None for value in attempts),
            "capture_index_count": len(records),
            "eligible_status_200_count": sum(row.get("statuscode_int") == 200 and row.get("valid_replay_candidate") for row in valid_all),
            "redirect_index_count": sum(row.get("statuscode_int") in REDIRECT_CODES for row in records),
            "capture_records": records,
            "selected_capture": selected,
            "other_origin_metadata": core.other_origin_metadata(records, item["query_original"]),
            "attempts": [public_attempt(value) for value in attempts],
        },
        "replay_attempt_count": sum(value.get("executed", False) for value in replays),
        "replay_source_response_count": sum(value.get("source_status") is not None for value in replays),
        "replay_hops": [public_attempt(value) for value in replays],
        "category": category,
        "reason": reason,
        "actual_memento": final.get("memento_datetime") if final and final.get("executed") else None,
        "source_status": final.get("source_status") if final and final.get("executed") else None,
        "content_type": final.get("content_type") if final and final.get("executed") else None,
        "body_bytes": len(raw) if final and final.get("executed") else 0,
        "body_sha256": hashlib.sha256(raw).hexdigest() if raw else None,
        "validation": validation,
        "entity_valid": category in {"valid_rss_payload", "valid_html_payload"},
        "unrequested_reason": reason if category == "not_requested" else None,
        "transport_used_after_first": chosen,
    }
    return result, chosen or transport or "direct"


def source_map_entry(result: dict[str, Any]) -> dict[str, Any]:
    selected = result["cdx"].get("selected_capture") or {}
    validation = result.get("validation") or {}
    replay = next((value for value in reversed(result.get("replay_hops") or []) if value.get("executed")), {})
    observation = validation.get("body_observation") or {}
    return {
        "target": result["target"],
        "query_original": result["query_original"],
        "captured_original": selected.get("original"),
        "actual_memento": result["actual_memento"],
        "source_status": result["source_status"],
        "content_type": result["content_type"],
        "body_bytes": result["body_bytes"],
        "body_sha256": result["body_sha256"],
        "raw_body_path": (replay.get("raw") or {}).get("body"),
        "raw_headers_path": (replay.get("raw") or {}).get("headers"),
        "captured_original_url": selected.get("original"),
        "capture_timestamp": selected.get("timestamp"),
        "cdx_statuscode": selected.get("statuscode"),
        "cdx_digest": selected.get("digest"),
        "cdx_length": selected.get("length"),
        "cdx_digest_calculated": validation.get("cdx_digest_calculated"),
        "cdx_digest_match": validation.get("cdx_digest_match"),
        "body_format": validation.get("body_format"),
        "rss_observation": observation if validation.get("body_format") == "rss_xml" else None,
        "html_observation": observation if validation.get("body_format") == "html" else None,
        "html_month_evidence": validation.get("html_month_evidence"),
        "selection": "latest same-origin status-200 capture in exact pre-anchor CDX range",
        "integration": "source evidence only; entity remains in this batch raw directory",
    }


def write_outputs(candidates: dict[str, Any], results: list[dict[str, Any]], state: Any,
                  started_utc: str, finished_utc: str, updated_utc: str,
                  disk_before: int, disk_after: int, transport: str | None, gate: Any,
                  postflight: dict[str, Any]) -> None:
    counts: dict[str, int] = {}
    for result in results:
        counts[result["category"]] = counts.get(result["category"], 0) + 1
    entities = [source_map_entry(result) for result in results if result.get("entity_valid")]
    intervals = [entry["interval_since_previous_dispatch_seconds"] for entry in gate.dispatches
                 if entry.get("interval_since_previous_dispatch_seconds") is not None]
    min_interval = min(intervals) if intervals else None
    request_window_elapsed = (datetime.fromisoformat(finished_utc) - datetime.fromisoformat(started_utc)).total_seconds()
    report = {
        "schema": "continuous-wow-network-rss10-batch-report/v1",
        "batch_id": "NET-RSS-010",
        "mode": "executed",
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "request_window_finished_utc": finished_utc,
        "request_window_elapsed_seconds": round(request_window_elapsed, 3),
        "report_updated_utc": updated_utc,
        "inputs": {"candidates": str((OUT / "candidates.json").relative_to(ROOT)).replace("\\", "/"),
                   "candidates_sha256": sha(OUT / "candidates.json"),
                   "input_digests": candidates["input_digests"]},
        "policy": candidates["policy"],
        "preflight": {"drive": "D:", "disk_free_bytes_before": disk_before,
                      "disk_free_bytes_after": disk_after, "minimum_free_bytes": MIN_FREE_BYTES},
        "transport": {"confirmed_transport_after_first_request": transport,
                      "curl": str(core.CURL),
                      "helper": str(CORE_PATH.relative_to(ROOT)).replace("\\", "/"),
                      "dispatch_gate": str(GATE_PATH.relative_to(ROOT)).replace("\\", "/")},
        "target_count": len(results),
        "distinct_target_count": len({result["query_original"] for result in results}),
        "category_counts": counts,
        "capture_index_count_fetched": sum(result["cdx"]["capture_index_count"] for result in results),
        "capture_index_count": sum(result["cdx"]["capture_index_count"] for result in results),
        "eligible_status_200_capture_count": sum(result["cdx"]["eligible_status_200_count"] for result in results),
        "redirect_index_count": sum(result["cdx"]["redirect_index_count"] for result in results),
        "valid_entity_count": len(entities),
        "valid_rss_count": sum(result["category"] == "valid_rss_payload" for result in results),
        "valid_html_count": sum(result["category"] == "valid_html_payload" for result in results),
        "cdx_source_response_count": sum(result["cdx"]["source_response_count"] for result in results),
        "replay_source_response_count": sum(result["replay_source_response_count"] for result in results),
        "source_response_count": state.source_responses,
        "source_request_count": state.attempts,
        "transport_attempt_count": state.attempts,
        "failed_attempt_count": state.failed_attempts,
        "total_body_bytes": state.total_body_bytes,
        "payload_body_bytes": sum(result["body_bytes"] for result in results if result.get("entity_valid")),
        "max_entity_body_observed_bytes": max((result["body_bytes"] for result in results), default=0),
        "dispatch_count": len(gate.dispatches),
        "minimum_start_interval_seconds": min_interval,
        "stop_reason": state.stop_reason,
        "stop_detail": state.stop_detail,
        "rate_limit": state.rate_limit,
        "batch_policy_accepted": (min_interval is None or min_interval >= INTERVAL_SECONDS) and state.attempts <= MAX_ATTEMPTS,
        "postflight": postflight,
        "results": results,
        "raw_evidence_note": "Raw headers, traces, stderr and bodies remain below this batch raw directory. Zero-byte bodies from no-response attempts are local placeholders, not source content; CONNECT 200 is excluded by the shared source-block parser; CDX length is index metadata only.",
    }
    write(OUT / "batch-report.json", report)
    source_map = {
        "schema": "continuous-wow-network-rss10-source-map/v1",
        "batch_id": "NET-RSS-010",
        "report_sha256": sha(OUT / "batch-report.json"),
        "entries": entities,
        "entity_count": len(entities),
        "integration_held": True,
    }
    write(OUT / "rss-source-map.json", source_map)
    write(OUT / "redirect-evidence.json", {"schema": "continuous-wow-network-rss10-redirect-evidence/v1", "entries": []})
    summary = {
        "schema": "continuous-wow-network-rss10-sanitized-summary/v1",
        "batch_id": "NET-RSS-010",
        "mode": "executed",
        "report_sha256": sha(OUT / "batch-report.json"),
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "request_window_finished_utc": finished_utc,
        "request_window_elapsed_seconds": round(request_window_elapsed, 3),
        "report_updated_utc": updated_utc,
        "network_requests": state.attempts,
        "source_response_count": state.source_responses,
        "failed_attempt_count": state.failed_attempts,
        "target_count": len(results),
        "category_counts": counts,
        "capture_index_count": report["capture_index_count"],
        "eligible_status_200_capture_count": report["eligible_status_200_capture_count"],
        "valid_entity_count": len(entities),
        "valid_rss_count": report["valid_rss_count"],
        "valid_html_count": report["valid_html_count"],
        "total_body_bytes": state.total_body_bytes,
        "payload_body_bytes": report["payload_body_bytes"],
        "max_entity_body_observed_bytes": report["max_entity_body_observed_bytes"],
        "disk_free_bytes_before": disk_before,
        "disk_free_bytes_after": disk_after,
        "dispatch_count": len(gate.dispatches),
        "minimum_start_interval_seconds": min_interval,
        "batch_policy_accepted": report["batch_policy_accepted"],
        "stop_reason": state.stop_reason,
        "targets": [{"rank": result["rank"], "target": result["target"], "year": result["year"], "month": result["month"],
                     "category": result["category"], "reason": result["reason"], "actual_memento": result["actual_memento"],
                     "body_format": (result.get("validation") or {}).get("body_format"),
                     "title": ((result.get("validation") or {}).get("body_observation") or {}).get("title"),
                     "month_evidence": ((result.get("validation") or {}).get("body_observation") or {}).get("month_evidence") or
                                       ((result.get("validation") or {}).get("html_month_evidence")),
                     "unrequested_reason": result.get("unrequested_reason")} for result in results],
        "raw_evidence_note": report["raw_evidence_note"],
    }
    write(OUT / "sanitized-summary.json", summary)
    md_lines = [
        "# NET-RSS-010 sanitized summary",
        "",
        f"Targets: {len(results)}; source attempts: {state.attempts}; source responses: {state.source_responses}; valid entities: {len(entities)}.",
        f"Categories: {json.dumps(counts, ensure_ascii=False, sort_keys=True)}.",
        f"Body bytes: {state.total_body_bytes}; valid payload bytes: {report['payload_body_bytes']}; minimum dispatch interval: {min_interval}.",
        f"Stop reason: {state.stop_reason or 'completed'}; policy accepted: {report['batch_policy_accepted']}.",
        "",
        "| # | target | category | body format | Memento | reason |",
        "|---:|---|---|---|---|---|",
    ]
    for result in results:
        fmt = (result.get("validation") or {}).get("body_format") or ""
        md_lines.append(f"| {result['rank']} | `{result['target']}` | {result['category']} | {fmt} | {result['actual_memento'] or ''} | {result['reason'] or ''} |")
    (OUT / "sanitized-summary.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")


def rebuild_reports_offline() -> int:
    """Repair derived HTML month evidence without touching raw or networking."""
    report_path = OUT / "batch-report.json"
    summary_path = OUT / "sanitized-summary.json"
    if not report_path.exists() or not summary_path.exists():
        raise RuntimeError("cannot rebuild before an executed report exists")
    report = read(report_path)
    summary = read(summary_path)
    if report.get("batch_id") != "NET-RSS-010" or report.get("source_request_count") is None:
        raise RuntimeError("unexpected RSS010 report for offline rebuild")
    for result in report.get("results") or []:
        validation = result.get("validation") or {}
        replay = next((value for value in reversed(result.get("replay_hops") or []) if value.get("executed")), None)
        raw_path = ((replay or {}).get("raw") or {}).get("body")
        if not result.get("entity_valid") or validation.get("body_format") != "html" or not raw_path:
            continue
        path = OUT / raw_path
        if not path.exists():
            raise RuntimeError(f"valid HTML raw body missing during offline rebuild: {raw_path}")
        validation["html_month_evidence"] = html_date_evidence(path.read_bytes(), validation.get("body_observation") or {}, result["year"], result["month"])
        result["validation"] = validation
    updated = utc()
    report["report_updated_utc"] = updated
    report.setdefault("request_window_elapsed_seconds", round((datetime.fromisoformat(report["finished_utc"]) - datetime.fromisoformat(report["started_utc"])).total_seconds(), 3))
    report.setdefault("max_entity_body_observed_bytes", max((result.get("body_bytes", 0) for result in report.get("results") or []), default=0))
    report["offline_rebuild"] = {
        "updated_utc": updated,
        "network_requests": 0,
        "reason": "corrected derived HTML title and posted-date month parsing; raw attempts, Memento, hashes, CDX rows and finished/request-window timestamps preserved",
    }
    write(report_path, report)
    entities = [source_map_entry(result) for result in report.get("results") or [] if result.get("entity_valid")]
    source_map = {
        "schema": "continuous-wow-network-rss10-source-map/v1",
        "batch_id": "NET-RSS-010",
        "report_sha256": sha(report_path),
        "entries": entities,
        "entity_count": len(entities),
        "integration_held": True,
        "offline_rebuild": {"updated_utc": updated, "network_requests": 0},
    }
    write(OUT / "rss-source-map.json", source_map)
    write(OUT / "payload-source-map.json", source_map)
    summary["report_sha256"] = sha(report_path)
    summary["report_updated_utc"] = updated
    summary["request_window_elapsed_seconds"] = report["request_window_elapsed_seconds"]
    summary["max_entity_body_observed_bytes"] = report["max_entity_body_observed_bytes"]
    summary["targets"] = [
        {
            "rank": result["rank"],
            "target": result["target"],
            "year": result["year"],
            "month": result["month"],
            "category": result["category"],
            "reason": result["reason"],
            "actual_memento": result["actual_memento"],
            "body_format": (result.get("validation") or {}).get("body_format"),
            "title": ((result.get("validation") or {}).get("body_observation") or {}).get("title"),
            "month_evidence": ((result.get("validation") or {}).get("body_observation") or {}).get("month_evidence") or
                              ((result.get("validation") or {}).get("html_month_evidence")),
            "unrequested_reason": result.get("unrequested_reason"),
        }
        for result in report.get("results") or []
    ]
    summary["offline_rebuild"] = {"updated_utc": updated, "network_requests": 0}
    write(summary_path, summary)
    md_lines = [
        "# NET-RSS-010 sanitized summary", "",
        f"Targets: {summary['target_count']}; source attempts: {summary['network_requests']}; source responses: {summary['source_response_count']}; valid entities: {summary['valid_entity_count']}.",
        f"Categories: {json.dumps(summary['category_counts'], ensure_ascii=False, sort_keys=True)}.",
        f"Body bytes: {summary['total_body_bytes']}; valid payload bytes: {summary['payload_body_bytes']}; minimum dispatch interval: {summary['minimum_start_interval_seconds']}.",
        f"Stop reason: {summary.get('stop_reason') or 'completed'}; policy accepted: {summary['batch_policy_accepted']}.",
        "Derived month evidence was rebuilt offline; raw attempts and request-window timestamps were preserved.", "",
        "| # | target | category | title | body date state | anomaly | Memento |", "|---:|---|---|---|---|---|---|",
    ]
    for result in report.get("results") or []:
        validation = result.get("validation") or {}
        ev = validation.get("html_month_evidence") or {}
        body_state = (ev.get("posted_date_evidence") or {}).get("state") or ""
        md_lines.append(f"| {result['rank']} | `{result['target']}` | {result['category']} | {((validation.get('body_observation') or {}).get('title') or '').replace('|', ' ')} | {body_state} | {ev.get('source_anomaly') or ''} | {result.get('actual_memento') or ''} |")
    (OUT / "sanitized-summary.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(json.dumps({"mode": "offline_rebuild", "network_requests": 0, "report_updated_utc": updated,
                      "report_sha256": sha(report_path), "entity_count": len(entities)}, ensure_ascii=False))
    return 0


def execute() -> int:
    inputs = verify_inputs()
    candidates = make_candidates(inputs)
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    candidate_path = OUT / "candidates.json"
    expected_targets = [row["query_original"] for row in candidates["targets"]]
    if not candidate_path.exists():
        write(candidate_path, candidates)
    else:
        existing = read(candidate_path)
        existing_targets = [row.get("query_original") for row in existing.get("targets") or []]
        if (existing.get("batch_id") != "NET-RSS-010" or existing.get("network_requests") != 0
                or existing_targets != expected_targets or existing.get("target_count") != MAX_TARGETS):
            raise RuntimeError("existing RSS010 candidates are not a zero-network declaration")
        candidates = existing
    disk_before = free_bytes()
    if disk_before < MIN_FREE_BYTES:
        raise RuntimeError(f"disk free below threshold before dispatch: {disk_before}")
    started_utc = utc()
    window_started = time.monotonic()
    state = core.RunState(window_started)
    journal = {
        "schema": "continuous-wow-network-rss10-dispatch-log/v1",
        "batch_id": "NET-RSS-010",
        "simulation": False,
        "policy": {"minimum_dispatch_interval_seconds": INTERVAL_SECONDS, "max_attempts": MAX_ATTEMPTS, "network_window_seconds": WINDOW_SECONDS},
        "disk_preflight": {"checked_utc": started_utc, "disk_free_bytes": disk_before, "minimum_free_bytes": MIN_FREE_BYTES},
        "dispatches": [],
    }
    gate = gate_mod.GateState(datetime.now(timezone.utc) - timedelta(seconds=1), journal_path=OUT / "dispatch-log.json", journal=journal)
    gate.persist()
    results: list[dict[str, Any]] = []
    transport: str | None = None
    postflight: dict[str, Any] = {}
    try:
        for item in candidates["targets"]:
            if state.stop_reason:
                results.append(unrequested_result(item, state.stop_reason))
                continue
            result, transport = run_one(item, transport, state, gate, window_started)
            results.append(result)
    finally:
        postflight = gate_mod.persist_postflight(gate, state.attempts, free_fn=free_bytes)
    finished_utc = utc()
    disk_after = free_bytes()
    write_outputs(candidates, results, state, started_utc, finished_utc, utc(), disk_before, disk_after, transport, gate, postflight)
    print(json.dumps({
        "mode": "executed",
        "batch_id": "NET-RSS-010",
        "network_requests": state.attempts,
        "source_responses": state.source_responses,
        "failed_attempts": state.failed_attempts,
        "target_count": len(results),
        "categories": {key: sum(result["category"] == key for result in results) for key in sorted({result["category"] for result in results})},
        "valid_entities": sum(result.get("entity_valid", False) for result in results),
        "disk_free_before": disk_before,
        "disk_free_after": disk_after,
        "minimum_start_interval_seconds": min((x["interval_since_previous_dispatch_seconds"] for x in gate.dispatches if x.get("interval_since_previous_dispatch_seconds") is not None), default=None),
        "stop_reason": state.stop_reason,
    }, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    if sum(bool(value) for value in (args.prepare, args.execute, args.rebuild)) != 1:
        parser.error("choose exactly one of --prepare, --execute or --rebuild")
    if args.prepare:
        return prepare()
    if args.execute:
        return execute()
    return rebuild_reports_offline()


if __name__ == "__main__":
    raise SystemExit(main())
