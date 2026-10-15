from __future__ import annotations
import argparse, base64, hashlib, importlib.util, io, json, shutil, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except Exception:
    Image = None

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
PLAN = ROOT / "research/continuous-recovery-20261015/news-assets13-approved-plan.json"
REVIEW = ROOT / "research/continuous-recovery-20261015/rss7-resource-review/rss7-resource-review.json"
QUEUE = ROOT / "research/continuous-recovery-20261015/rss7-resource-review/network-resource-candidates.json"
ACCEPT = ROOT / "research/continuous-recovery-20261015/rss7-acceptance.json"
if not ACCEPT.exists():
    ACCEPT = ROOT / "research/continuous-recovery-20261015/rss7-resource-acceptance.json"
CORE_PATH = ROOT / "research/continuous-recovery-20261015/network-core-pages3/core_pages3.py"
GATE_PATH = ROOT / "research/continuous-recovery-20261015/network-control7/control7.py"
PLAN_SHA = "49e8d0d434430c52f68ad9ac45a971ec7d75876d1673178e6b858ae675e15c31"
REVIEW_SHA = "5813b0fe714ab8d7d21b33a86142b8d0b5f5cb0a6774194c27ff7650748a7bba"
QUEUE_SHA = "4c9efd703e1ad9e0e26e4f353936dac28b9018659d2b674a474b131e049364b5"
ACCEPT_SHA = "8d97fcfc61fb47d0e15b1f8802a38dcc65bd1aa44b110144f40a2014b9c2d422"
LEDGER = [
 "research/continuous-recovery-20261015/assets5-acceptance.json",
 "research/continuous-recovery-20261015/mixed9-acceptance.json",
 "research/continuous-recovery-20261015/wrath8-acceptance.json",
 "research/continuous-recovery-20261015/rss6-acceptance.json",
 "research/continuous-recovery-20261015/rss10-acceptance.json",
 "research/continuous-recovery-20261015/network-batch1-acceptance.json",
 "research/continuous-recovery-20261015/resource-dedup-acceptance.json",
]
FROM_TS, TO_TS = "20040101000000", "20080512210044"
PROXY, UA = "http://127.0.0.1:7890", "wow-recovery-news-assets13/20261015"
MAX_TARGETS, MAX_ATTEMPTS, WINDOW = 16, 32, 480
INTERVAL, MIN_FREE = 1.25, 11_005_853_696
MAX_TOTAL, MAX_ENTITY = 64 * 1024 * 1024, 16 * 1024 * 1024
STOP, REDIRECTS = {429, 503}, {301, 302, 303, 307, 308}

def mod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load " + str(path))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

core = mod(CORE_PATH, "news_assets13_core")
gate_mod = mod(GATE_PATH, "news_assets13_gate")
core.OUT, core.RAW, core.USER_AGENT, core.PROXY = OUT, RAW, UA, PROXY
core.MAX_ATTEMPTS, core.WINDOW_SECONDS = MAX_ATTEMPTS, WINDOW
core.MIN_INTERVAL_SECONDS, core.MIN_FREE_BYTES = 0.0, MIN_FREE
core.MAX_TOTAL_BODY_BYTES, core.MAX_ENTITY_BODY_BYTES = MAX_TOTAL, MAX_ENTITY
gate_mod.OUT, gate_mod.RAW, gate_mod.INTERVAL_SECONDS = OUT, RAW, INTERVAL

def utc():
    return datetime.now(timezone.utc).isoformat()

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def jread(path):
    return json.loads(path.read_text(encoding="utf-8"))

def jwrite(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def free():
    return int(shutil.disk_usage(OUT).free)

def body(attempt):
    if not attempt:
        return b""
    p = OUT / str((attempt.get("raw") or {}).get("body") or "")
    return p.read_bytes() if p.exists() else b""

def sha256b(value):
    return hashlib.sha256(value).hexdigest()

def b32sha1(value):
    return base64.b32encode(hashlib.sha1(value).digest()).decode("ascii") if value else None

def inputs():
    out = {}
    for p in (PLAN, REVIEW, QUEUE, ACCEPT):
        out[str(p.relative_to(ROOT)).replace("\\", "/")] = {"sha256": sha(p), "bytes": p.stat().st_size}
    return out

def prior_hits(urls):
    out = {}
    paths = [ROOT / x for x in LEDGER]
    for url in urls:
        hits = [str(p.relative_to(ROOT)).replace("\\", "/") for p in paths if url in p.read_text(encoding="utf-8", errors="replace")]
        out[url] = {"status": "exact_hit_in_bounded_ledger" if hits else "not_seen_in_bounded_ledger", "exact_text_hits": hits, "checked_files": LEDGER, "absence_claim": False, "note": "Bounded ledger absence is not evidence of never requested."}
    return out

def verify():
    got = inputs()
    expected = {
        str(PLAN.relative_to(ROOT)).replace("\\", "/"): PLAN_SHA,
        str(REVIEW.relative_to(ROOT)).replace("\\", "/"): REVIEW_SHA,
        str(QUEUE.relative_to(ROOT)).replace("\\", "/"): QUEUE_SHA,
        str(ACCEPT.relative_to(ROOT)).replace("\\", "/"): ACCEPT_SHA,
    }
    for key, value in expected.items():
        if got[key]["sha256"] != value:
            raise RuntimeError("input SHA drift " + key)
    plan = jread(PLAN)
    if plan.get("execute_allowed") is not True:
        raise RuntimeError("execute_allowed is not true")
    acc = jread(ACCEPT)
    if acc.get("accepted") is not True or acc.get("network_requests_by_acceptance") != 0:
        raise RuntimeError("RSS7 acceptance precondition failed")
    return got

def candidates():
    plan, queue = jread(PLAN), jread(QUEUE)
    pts = plan.get("targets") or []
    qrows = {x.get("exact_original_url"): x for x in queue.get("candidates") or []}
    if len(pts) != MAX_TARGETS:
        raise RuntimeError("unexpected plan target count")
    urls = [str(x["url"]) for x in pts]
    if len(set(urls)) != MAX_TARGETS:
        raise RuntimeError("non-distinct plan targets")
    hits = prior_hits(urls)
    rows = []
    for x in pts:
        url = str(x["url"])
        q = qrows.get(url) or {}
        rows.append({
            "rank": x.get("rank"), "kind": x.get("kind"), "target": url, "query_original": url,
            "source_original_queue_rank": x.get("source_original_queue_rank"),
            "page_coverage": x.get("page_coverage") or [], "contexts": x.get("contexts") or [],
            "plan_reason": x.get("reason"),
            "queue_metadata": {k: q.get(k) for k in ("queue_rank", "reference_count", "resource_scope", "resource_types", "resource_purposes")},
            "prior_request_check": hits[url],
            "initial_status": "uncovered_by_bounded_prior_ledger" if not hits[url]["exact_text_hits"] else "prior_exact_identity_requires_revalidation",
        })
    return {
        "schema": "continuous-wow-network-news-assets13-candidates/v1",
        "batch_id": "NET-NEWS-ASSETS-013", "generated_utc": utc(), "network_requests": 0,
        "input_digests": inputs(),
        "policy": {"preanchor_from": FROM_TS, "preanchor_to": TO_TS, "max_targets": MAX_TARGETS, "max_attempts": MAX_ATTEMPTS, "network_window_seconds": WINDOW, "minimum_dispatch_interval_seconds": INTERVAL, "minimum_free_bytes": MIN_FREE, "max_total_body_bytes": MAX_TOTAL, "max_entity_body_bytes": MAX_ENTITY, "no_redirects": True, "no_external_follow": True, "integration_held": True},
        "prior_request_scope": {"files": LEDGER, "absence_is_not_never_requested": True, "source_maps_searched": False, "reason": "Only the approved bounded acceptance/request ledger was searched."},
        "targets": rows,
    }

ALIASES = {"timestamp": "timestamp", "original": "original", "url": "original", "original_url": "original", "mimetype": "mimetype", "mime": "mimetype", "mime_type": "mimetype", "statuscode": "statuscode", "status": "statuscode", "status_code": "statuscode", "digest": "digest", "length": "length"}

def canon(value):
    return ALIASES.get(value.strip().lower().replace("-", "_"))

def parse_cdx(value):
    text = value.decode("utf-8", errors="replace")
    if not text.strip() or text.strip().lower() in {"[]", "no captures found", "no captures"}:
        return [], True, None, None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        lines = [x for x in text.splitlines() if x.strip()]
        header = lines[0].split("\t") if lines else []
        return records_header(header, [x.split("\t") for x in lines[1:]])
    if isinstance(payload, list):
        if not payload:
            return [], True, None, None
        if isinstance(payload[0], list):
            return records_header([str(x) for x in payload[0]], payload[1:])
        if all(isinstance(x, dict) for x in payload):
            fields = sorted({str(k) for x in payload for k in x})
            return records_dict(payload, fields)
        return [], False, "cdx_shape", None
    if isinstance(payload, dict):
        rows = payload.get("records") or payload.get("captures") or []
        if not isinstance(rows, list):
            return [], False, "cdx_shape", None
        if not rows:
            return [], True, None, None
        fields = sorted({str(k) for x in rows for k in x}) if all(isinstance(x, dict) for x in rows) else []
        return records_dict(rows, fields) if fields else ([], False, "cdx_shape", None)
    return [], False, "cdx_shape", None

def records_header(header, rows):
    fields = {canon(x) for x in header}
    if not {"timestamp", "original", "statuscode"}.issubset(fields):
        return [], False, "cdx_header_missing", header
    pos = {}
    for i, value in enumerate(header):
        key = canon(value)
        if key and key not in pos:
            pos[key] = i
    out = []
    for row in rows:
        if not isinstance(row, list):
            return [], False, "cdx_row_shape", header
        out.append({key: str(row[i]) if i < len(row) else "" for key, i in pos.items()})
    return out, True, None, header

def records_dict(rows, fields):
    if not {"timestamp", "original", "statuscode"}.issubset({canon(x) for x in fields}):
        return [], False, "cdx_header_missing", fields
    out = []
    for row in rows:
        item = {}
        for field in fields:
            key = canon(field)
            if key and key not in item:
                item[key] = str(row.get(field, ""))
        out.append(item)
    return out, True, None, fields

def decorate(rows, requested):
    out = []
    for i, r in enumerate(rows):
        status = int(r["statuscode"]) if r.get("statuscode", "").isdigit() else None
        match = core.original_match_kind(r.get("original", ""), requested)
        in_range = bool(r.get("timestamp") and FROM_TS <= r["timestamp"] <= TO_TS)
        valid = bool(in_range and match is not None and status in ({200} | REDIRECTS) and core.parse_timestamp(r.get("timestamp")))
        out.append({**r, "record_index": i, "statuscode_int": status, "within_query_range": in_range, "original_match_kind": match, "exact_original_match": match == "exact", "valid_replay_candidate": valid})
    return out

def selected(rows):
    rows = [x for x in rows if x.get("valid_replay_candidate") and x.get("statuscode_int") == 200]
    return max(rows, key=lambda x: x.get("timestamp", "")) if rows else None

def cdx_url(url):
    return core.cdx_query_url(url)

def okay(state, started):
    if state.stop_reason:
        return False, state.stop_reason
    if state.attempts >= MAX_ATTEMPTS:
        return False, "attempt_limit"
    if time.monotonic() - started >= WINDOW:
        return False, "network_window_exhausted"
    if free() < MIN_FREE:
        return False, "disk_free_below_threshold"
    if state.total_body_bytes >= MAX_TOTAL:
        return False, "total_body_limit"
    return True, None

def public_attempt(x):
    keys = ("attempt", "kind", "transport", "url", "started_utc", "finished_utc", "dispatch_utc", "dispatch_monotonic", "dispatch_interval_seconds", "curl_exit", "source_status", "connect_status", "content_type", "location", "retry_after", "memento_datetime", "body_bytes", "body_sha256", "transport_error", "transport_reason", "local_zero_byte_body_placeholder", "body_is_source_response", "raw")
    return {k: x.get(k) for k in keys}

def request(url, transport, kind, key, state, gate, started):
    ok, why = okay(state, started)
    if not ok:
        return {"executed": False, "attempt": state.attempts + 1, "kind": kind, "target_key": key, "transport": transport, "url": url, "unrequested_reason": why or "limit_before_request"}
    n = state.attempts + 1
    g = gate.before_dispatch(n, transport, key)
    x = core.run_request(url, transport, kind, key, state, n)
    x.update({"dispatch_utc": g["dispatch_utc"], "dispatch_monotonic": g["dispatch_monotonic"], "dispatch_interval_seconds": g["interval_since_previous_dispatch_seconds"], "gate_persisted_before_transport": g["persisted_before_transport"]})
    b = body(x)
    x["local_zero_byte_body_placeholder"] = bool(x.get("source_status") is None and not b)
    x["body_is_source_response"] = x.get("source_status") is not None
    if kind == "cdx":
        rows, good, err, header = parse_cdx(b) if x.get("source_status") == 200 and not x.get("transport_error") else ([], False, "no_200_source_response", None)
        x.update({"cdx_records": rows, "cdx_parse_valid": good, "cdx_parse_error": err, "cdx_header_fields_observed": header})
    return x

def image_check(b, content_type):
    out = {"mime": (content_type or "").split(";", 1)[0].strip().lower() or None, "pillow_available": Image is not None, "verify_ok": False, "load_ok": False, "format": None, "size": None, "mode": None}
    if Image is None:
        out["reason"] = "pillow_unavailable"
        return out
    if not out["mime"] or not out["mime"].startswith("image/"):
        out["reason"] = "content_type_not_image"
        return out
    try:
        with Image.open(io.BytesIO(b)) as im:
            im.verify()
        out["verify_ok"] = True
        with Image.open(io.BytesIO(b)) as im:
            im.load()
            out.update({"load_ok": True, "format": im.format, "size": [int(im.width), int(im.height)], "mode": im.mode})
    except Exception as exc:
        out["reason"] = type(exc).__name__
    return out

def validate(item, replay, cap):
    b = body(replay)
    digest32 = b32sha1(b)
    val = {"body_format": item["kind"], "body_bytes": len(b), "body_sha256": sha256b(b) if b else None, "cdx_digest": cap.get("digest"), "cdx_digest_calculated": digest32, "cdx_digest_match": bool(cap.get("digest") and digest32 and cap.get("digest") == digest32), "content_type": replay.get("content_type"), "actual_memento": replay.get("memento_datetime")}
    if replay.get("transport_error") or replay.get("source_status") is None:
        return "transport_error", replay.get("transport_reason") or "curl_or_tls_failure", val
    if replay.get("source_status") in STOP:
        val["retry_after"] = replay.get("retry_after")
        return "rate_limited", "source_status_" + str(replay.get("source_status")), val
    if replay.get("source_status") != 200:
        return "soft404", "replay_source_status_" + str(replay.get("source_status")), val
    if not replay.get("memento_datetime"):
        return "soft404", "missing_actual_memento", val
    if not b:
        return "soft404", "empty_source_body", val
    html = core.html_info(b, replay.get("content_type"))
    val["html_info"] = html
    if html.get("is_html") or html.get("markers"):
        return "soft404", "html_or_wayback_error_body", val
    if item["kind"] == "stylesheet":
        mime = (replay.get("content_type") or "").split(";", 1)[0].strip().lower()
        val["mime"], val["css_nonempty"] = mime or None, bool(b.strip())
        if mime != "text/css" or not b.strip():
            return "soft404", "not_text_css_or_empty", val
        return "valid_stylesheet", "validated_text_css_source", val
    val["image"] = image_check(b, replay.get("content_type"))
    if not val["image"].get("verify_ok") or not val["image"].get("load_ok"):
        return "soft404", "image_verify_or_load_failed", val
    return "valid_image", "validated_pillow_image_source", val

def not_requested(item, reason):
    return {"rank": item["rank"], "target": item["target"], "kind": item["kind"], "source_original_queue_rank": item.get("source_original_queue_rank"), "category": "not_requested", "reason": reason, "actual_memento": None, "source_status": None, "content_type": None, "body_bytes": 0, "body_sha256": None, "validation": None, "entity_valid": False, "cdx": {"query_performed": False, "query_url": cdx_url(item["target"]), "source_response_count": 0, "capture_index_count": 0, "eligible_status_200_count": 0, "redirect_index_count": 0, "capture_records": [], "selected_capture": None, "attempts": []}, "replay_attempt_count": 0, "replay_source_response_count": 0, "replay_hops": [], "unrequested_reason": reason}

def run_one(item, transport, state, gate, started):
    attempts = []
    def issue(url, trans, kind):
        return request(url, trans, kind, item["query_original"], state, gate, started)
    chosen = transport
    query = cdx_url(item["query_original"])
    if chosen is None:
        first = issue(query, "direct", "cdx")
        attempts.append(first)
        if first.get("executed") and first.get("transport_error") and not state.stop_reason:
            attempts.append(issue(query, "proxy", "cdx"))
            chosen = "proxy"
        else:
            chosen = "direct"
    else:
        attempts.append(issue(query, chosen, "cdx"))
    q = next((x for x in reversed(attempts) if x.get("executed")), attempts[-1])
    raw_rows = q.get("cdx_records") or []
    rows = decorate(raw_rows, item["query_original"])
    cap = selected(rows)
    replay = None
    if q.get("executed") and q.get("source_status") == 200 and q.get("cdx_parse_valid") and cap and not state.stop_reason:
        replay = issue(core.replay_url(cap), chosen or "direct", "replay")
    if not q.get("executed"):
        category, reason, val = "not_requested", q.get("unrequested_reason", "query_not_requested"), None
    elif q.get("transport_error") and q.get("source_status") is None:
        category, reason, val = "transport_error", q.get("transport_reason") or "curl_or_tls_failure", None
    elif q.get("source_status") in STOP:
        category, reason, val = "rate_limited", "source_status_" + str(q.get("source_status")), {"retry_after": q.get("retry_after")}
    elif not q.get("cdx_parse_valid"):
        category, reason, val = "transport_error", q.get("cdx_parse_error") or "cdx_parse_failed", None
    elif not raw_rows:
        category, reason, val = "cdx_empty_in_scoped_window", "no_index_rows_in_preanchor_window", None
    elif cap is None:
        category, reason, val = "cdx_rows_without_valid_200", "no_same_origin_status_200_capture", {"redirect_index_count": sum(x.get("statuscode_int") in REDIRECTS for x in rows)}
    elif not replay or not replay.get("executed"):
        category, reason, val = "not_requested", (replay or {}).get("unrequested_reason", "replay_not_requested"), None
    else:
        category, reason, val = validate(item, replay, cap)
    rb = body(replay)
    return {
        "rank": item["rank"], "target": item["target"], "kind": item["kind"], "source_original_queue_rank": item.get("source_original_queue_rank"), "category": category, "reason": reason,
        "actual_memento": replay.get("memento_datetime") if replay and replay.get("executed") else None,
        "source_status": replay.get("source_status") if replay and replay.get("executed") else None,
        "content_type": replay.get("content_type") if replay and replay.get("executed") else None,
        "body_bytes": len(rb) if replay and replay.get("executed") else 0, "body_sha256": sha256b(rb) if rb else None,
        "validation": val, "entity_valid": category in {"valid_stylesheet", "valid_image"},
        "cdx": {"query_performed": any(x.get("executed") for x in attempts), "query_url": query, "source_status": q.get("source_status"), "source_response_count": sum(x.get("source_status") is not None for x in attempts), "capture_index_count": len(raw_rows), "eligible_status_200_count": sum(bool(x.get("valid_replay_candidate")) and x.get("statuscode_int") == 200 for x in rows), "redirect_index_count": sum(x.get("statuscode_int") in REDIRECTS for x in rows), "cdx_header_fields_observed": q.get("cdx_header_fields_observed"), "capture_records": rows, "selected_capture": cap, "other_origin_metadata": core.other_origin_metadata(raw_rows, item["query_original"]), "attempts": [public_attempt(x) for x in attempts]},
        "replay_attempt_count": int(bool(replay and replay.get("executed"))), "replay_source_response_count": int(bool(replay and replay.get("source_status") is not None)), "replay_hops": [public_attempt(replay)] if replay else [], "unrequested_reason": reason if category == "not_requested" else None,
    }, chosen or transport or "direct"

def source_entry(row):
    cap = row["cdx"].get("selected_capture") or {}
    val = row.get("validation") or {}
    replay = next((x for x in reversed(row.get("replay_hops") or []) if x.get("source_status") is not None), {})
    image = val.get("image") or {}
    return {"target": row["target"], "query_original_url": row["target"], "captured_original_url": cap.get("original"), "actual_memento": row["actual_memento"], "source_status": row["source_status"], "content_type": row["content_type"], "body_bytes": row["body_bytes"], "body_sha256": row["body_sha256"], "raw_body_path": (replay.get("raw") or {}).get("body"), "raw_headers_path": (replay.get("raw") or {}).get("headers"), "capture_timestamp": cap.get("timestamp"), "cdx_statuscode": cap.get("statuscode"), "cdx_digest": cap.get("digest"), "cdx_length": cap.get("length"), "cdx_digest_calculated": val.get("cdx_digest_calculated"), "cdx_digest_match": val.get("cdx_digest_match"), "body_format": val.get("body_format"), "mime": val.get("mime") or image.get("mime"), "decode": image if row["kind"] == "image" else {"css_nonempty": val.get("css_nonempty")}, "integration": "source evidence only; entity remains in this batch raw directory"}

def outputs(candidates_value, results, state, started_utc, finished_utc, before, after, transport, gate, postflight):
    counts = {}
    for x in results:
        counts[x["category"]] = counts.get(x["category"], 0) + 1
    entities = [source_entry(x) for x in results if x.get("entity_valid")]
    dispatch_intervals = [x.get("interval_since_previous_dispatch_seconds") for x in gate.dispatches if x.get("interval_since_previous_dispatch_seconds") is not None]
    request_starts = []
    for result in results:
        for attempt in result.get("cdx", {}).get("attempts", []) + result.get("replay_hops", []):
            if attempt.get("started_utc"):
                request_starts.append((datetime.fromisoformat(attempt["started_utc"]), attempt.get("attempt"), result.get("rank"), attempt.get("kind")))
    request_starts.sort()
    start_intervals = [(request_starts[i][0] - request_starts[i - 1][0]).total_seconds() for i in range(1, len(request_starts))]
    minimum = min(start_intervals) if start_intervals else None
    dispatch_minimum = min(dispatch_intervals) if dispatch_intervals else None
    interval_deviation = None
    if minimum is not None and minimum < INTERVAL:
        pairs = []
        for i in range(1, len(request_starts)):
            delta = (request_starts[i][0] - request_starts[i - 1][0]).total_seconds()
            if delta < INTERVAL:
                pairs.append({"seconds": delta, "previous": {"attempt": request_starts[i - 1][1], "rank": request_starts[i - 1][2], "kind": request_starts[i - 1][3], "started_utc": request_starts[i - 1][0].isoformat()}, "current": {"attempt": request_starts[i][1], "rank": request_starts[i][2], "kind": request_starts[i][3], "started_utc": request_starts[i][0].isoformat()}})
        interval_deviation = {"required_seconds": INTERVAL, "observed_request_start_minimum_seconds": minimum, "observed_pairs": pairs, "dispatch_gate_minimum_seconds": dispatch_minimum, "reason": "gate dispatch timestamps met the interval, but actual core request-start timestamps include sub-interval gaps"}
    elapsed = (datetime.fromisoformat(finished_utc) - datetime.fromisoformat(started_utc)).total_seconds()
    policy = (minimum is None or minimum >= INTERVAL) and state.attempts <= MAX_ATTEMPTS
    report = {"schema": "continuous-wow-network-news-assets13-batch-report/v1", "batch_id": "NET-NEWS-ASSETS-013", "mode": "executed", "started_utc": started_utc, "finished_utc": finished_utc, "request_window_finished_utc": finished_utc, "request_window_elapsed_seconds": round(elapsed, 3), "report_updated_utc": utc(), "inputs": {"candidates_sha256": sha(OUT / "candidates.json"), "input_digests": candidates_value["input_digests"]}, "policy": candidates_value["policy"], "preflight": {"drive": "D:", "disk_free_bytes_before": before, "disk_free_bytes_after": after, "minimum_free_bytes": MIN_FREE}, "transport": {"confirmed_transport_after_first_request": transport, "curl": str(core.CURL), "helper": str(CORE_PATH.relative_to(ROOT)).replace("\\", "/"), "dispatch_gate": str(GATE_PATH.relative_to(ROOT)).replace("\\", "/")}, "target_count": len(results), "distinct_target_count": len({x["target"] for x in results}), "category_counts": counts, "capture_index_count": sum(x["cdx"]["capture_index_count"] for x in results), "eligible_status_200_capture_count": sum(x["cdx"]["eligible_status_200_count"] for x in results), "redirect_index_count": sum(x["cdx"]["redirect_index_count"] for x in results), "valid_entity_count": len(entities), "valid_stylesheet_count": sum(x["category"] == "valid_stylesheet" for x in results), "valid_image_count": sum(x["category"] == "valid_image" for x in results), "cdx_source_response_count": sum(x["cdx"]["source_response_count"] for x in results), "replay_source_response_count": sum(x["replay_source_response_count"] for x in results), "source_response_count": state.source_responses, "source_request_count": state.attempts, "transport_attempt_count": state.attempts, "failed_attempt_count": state.failed_attempts, "total_body_bytes": state.total_body_bytes, "payload_body_bytes": sum(x["body_bytes"] for x in results if x.get("entity_valid")), "max_entity_body_observed_bytes": max((x["body_bytes"] for x in results), default=0), "dispatch_count": len(gate.dispatches), "minimum_start_interval_seconds": minimum, "dispatch_gate_minimum_interval_seconds": dispatch_minimum, "interval_policy_deviation": interval_deviation, "stop_reason": state.stop_reason, "stop_detail": state.stop_detail, "rate_limit": state.rate_limit, "batch_policy_accepted": policy and interval_deviation is None, "postflight": postflight, "results": results, "raw_evidence_note": "Raw headers, traces, stderr and bodies remain below this batch raw directory. Zero-byte no-response bodies are local placeholders, not source content; CONNECT 200 is excluded; CDX length is index metadata only."}
    jwrite(OUT / "batch-report.json", report)
    smap = {"schema": "continuous-wow-network-news-assets13-source-map/v1", "batch_id": "NET-NEWS-ASSETS-013", "report_sha256": sha(OUT / "batch-report.json"), "entries": entities, "entity_count": len(entities), "integration_held": True}
    jwrite(OUT / "payload-source-map.json", smap)
    jwrite(OUT / "redirect-evidence.json", {"schema": "continuous-wow-network-news-assets13-redirect-evidence/v1", "entries": [], "note": "No redirects followed; redirect rows remain in target CDX records."})
    summary = {"schema": "continuous-wow-network-news-assets13-sanitized-summary/v1", "batch_id": "NET-NEWS-ASSETS-013", "mode": "executed", "report_sha256": sha(OUT / "batch-report.json"), "started_utc": started_utc, "finished_utc": finished_utc, "request_window_finished_utc": finished_utc, "request_window_elapsed_seconds": round(elapsed, 3), "report_updated_utc": report["report_updated_utc"], "network_requests": state.attempts, "source_response_count": state.source_responses, "failed_attempt_count": state.failed_attempts, "target_count": len(results), "category_counts": counts, "capture_index_count": report["capture_index_count"], "eligible_status_200_capture_count": report["eligible_status_200_capture_count"], "valid_entity_count": len(entities), "valid_stylesheet_count": report["valid_stylesheet_count"], "valid_image_count": report["valid_image_count"], "total_body_bytes": state.total_body_bytes, "payload_body_bytes": report["payload_body_bytes"], "disk_free_bytes_before": before, "disk_free_bytes_after": after, "dispatch_count": len(gate.dispatches), "minimum_start_interval_seconds": minimum, "dispatch_gate_minimum_interval_seconds": dispatch_minimum, "interval_policy_deviation": interval_deviation, "batch_policy_accepted": report["batch_policy_accepted"], "stop_reason": state.stop_reason, "targets": [{"rank": x["rank"], "target": x["target"], "kind": x["kind"], "category": x["category"], "reason": x["reason"], "source_status": x["source_status"], "actual_memento": x["actual_memento"], "body_bytes": x["body_bytes"], "body_sha256": x["body_sha256"], "capture_timestamp": (x["cdx"].get("selected_capture") or {}).get("timestamp"), "unrequested_reason": x.get("unrequested_reason")} for x in results], "raw_evidence_note": report["raw_evidence_note"]}
    jwrite(OUT / "sanitized-summary.json", summary)
    lines = ["# NET-NEWS-ASSETS-013 sanitized summary", "", f"Targets: {len(results)}; source attempts: {state.attempts}; real source responses: {state.source_responses}; valid entities: {len(entities)}.", f"Categories: {json.dumps(counts, ensure_ascii=False, sort_keys=True)}.", f"Index rows: {report['capture_index_count']}; response bytes: {state.total_body_bytes}; valid payload bytes: {report['payload_body_bytes']}.", f"Actual request-start minimum interval: {minimum}; gate dispatch minimum: {dispatch_minimum}; policy accepted: {report['batch_policy_accepted']}; stop: {state.stop_reason or 'completed'}.", "", "| # | target | kind | category | source status | Memento | bytes | reason |", "|---:|---|---|---|---:|---|---:|---|"]
    lines += [f"| {x['rank']} | {x['target']} | {x['kind']} | {x['category']} | {x['source_status'] or ''} | {x['actual_memento'] or ''} | {x['body_bytes']} | {x['reason']} |" for x in results]
    lines += ["", "Raw headers/traces/bodies are local evidence only. Zero-byte no-response bodies are local placeholders, not source content. CDX length is not body length. Valid entities remain unintegrated."]
    (OUT / "sanitized-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

def prepare():
    got = verify()
    c = candidates()
    OUT.mkdir(parents=True, exist_ok=True)
    jwrite(OUT / "candidates.json", c)
    cfg = {"schema": "continuous-wow-network-news-assets13-config/v1", "batch_id": "NET-NEWS-ASSETS-013", "prepared_utc": utc(), "network_requests": 0, "input_digests": got, "candidates_sha256": sha(OUT / "candidates.json"), "reuse": {"transport": str(CORE_PATH.relative_to(ROOT)).replace("\\", "/"), "dispatch_gate": str(GATE_PATH.relative_to(ROOT)).replace("\\", "/")}, "execution": c["policy"], "selection": "latest same-origin status-200 pre-anchor capture; default port only; bare/www and http/https separate; no redirects/follows"}
    jwrite(OUT / "config.json", cfg)
    print(json.dumps({"mode": "prepared", "batch_id": "NET-NEWS-ASSETS-013", "network_requests": 0, "target_count": len(c["targets"]), "candidates_sha256": cfg["candidates_sha256"], "input_digests": got}, ensure_ascii=False))

def rebuild_interval_report():
    report_path = OUT / "batch-report.json"
    summary_path = OUT / "sanitized-summary.json"
    journal_path = OUT / "dispatch-log.json"
    if not report_path.exists() or not summary_path.exists() or not journal_path.exists():
        raise RuntimeError("executed report, summary and journal are required")
    report = jread(report_path)
    summary = jread(summary_path)
    journal = jread(journal_path)
    starts = []
    for result in report.get("results") or []:
        for attempt in (result.get("cdx", {}).get("attempts", []) + result.get("replay_hops", [])):
            if attempt.get("started_utc"):
                starts.append((datetime.fromisoformat(attempt["started_utc"]), attempt.get("attempt"), result.get("rank"), attempt.get("kind")))
    starts.sort()
    pairs = []
    for i in range(1, len(starts)):
        delta = (starts[i][0] - starts[i - 1][0]).total_seconds()
        if delta < INTERVAL:
            pairs.append({"seconds": delta, "previous": {"attempt": starts[i - 1][1], "rank": starts[i - 1][2], "kind": starts[i - 1][3], "started_utc": starts[i - 1][0].isoformat()}, "current": {"attempt": starts[i][1], "rank": starts[i][2], "kind": starts[i][3], "started_utc": starts[i][0].isoformat()}})
    observed = min(((starts[i][0] - starts[i - 1][0]).total_seconds() for i in range(1, len(starts))), default=None)
    gate_intervals = [x.get("interval_since_previous_dispatch_seconds") for x in journal.get("dispatches", []) if x.get("interval_since_previous_dispatch_seconds") is not None]
    gate_min = min(gate_intervals) if gate_intervals else None
    deviation = {"required_seconds": INTERVAL, "observed_request_start_minimum_seconds": observed, "observed_pairs": pairs, "dispatch_gate_minimum_seconds": gate_min, "reason": "offline correction: actual core request-start timestamps are the compliance measurement; gate dispatch timestamps are retained separately"} if observed is not None and observed < INTERVAL else None
    report["minimum_start_interval_seconds"] = observed
    report["dispatch_gate_minimum_interval_seconds"] = gate_min
    report["interval_policy_deviation"] = deviation
    report["batch_policy_accepted"] = bool(report.get("source_request_count", 0) <= MAX_ATTEMPTS and deviation is None)
    report["report_updated_utc"] = utc()
    report["offline_correction"] = {"network_requests": 0, "updated_utc": report["report_updated_utc"], "reason": "corrected compliance fields from gate dispatch interval to actual recorded request-start interval; finished/request-window timestamps and raw evidence preserved"}
    jwrite(report_path, report)
    source_map_path = OUT / "payload-source-map.json"
    source_map = jread(source_map_path)
    source_map["report_sha256"] = sha(report_path)
    jwrite(source_map_path, source_map)
    summary["report_sha256"] = sha(report_path)
    summary["minimum_start_interval_seconds"] = observed
    summary["dispatch_gate_minimum_interval_seconds"] = gate_min
    summary["interval_policy_deviation"] = deviation
    summary["batch_policy_accepted"] = report["batch_policy_accepted"]
    summary["report_updated_utc"] = report["report_updated_utc"]
    summary["offline_correction"] = report["offline_correction"]
    jwrite(summary_path, summary)
    lines = ["# NET-NEWS-ASSETS-013 sanitized summary", "", f"Targets: {summary.get('target_count')}; source attempts: {summary.get('network_requests')}; real source responses: {summary.get('source_response_count')}; valid entities: {summary.get('valid_entity_count')}.", f"Categories: {json.dumps(summary.get('category_counts'), ensure_ascii=False, sort_keys=True)}.", f"Actual request-start minimum interval: {observed}; gate dispatch minimum: {gate_min}; policy accepted: {report['batch_policy_accepted']}; stop: {report.get('stop_reason') or 'completed'}.", "Offline correction updated derived timing/compliance fields only; raw attempts and finished/request-window timestamps were preserved.", "", "| # | target | kind | category | source status | Memento | bytes | reason |", "|---:|---|---|---|---:|---|---:|---|"]
    lines += [f"| {x['rank']} | {x['target']} | {x['kind']} | {x['category']} | {x['source_status'] or ''} | {x['actual_memento'] or ''} | {x['body_bytes']} | {x['reason']} |" for x in report.get("results") or []]
    lines += ["", "Raw headers/traces/bodies are local evidence only. Zero-byte no-response bodies are local placeholders, not source content. CDX length is not body length. Valid entities remain unintegrated."]
    (OUT / "sanitized-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"mode": "offline_rebuild", "network_requests": 0, "finished_utc": report.get("finished_utc"), "request_window_finished_utc": report.get("request_window_finished_utc"), "report_updated_utc": report["report_updated_utc"], "observed_request_start_minimum_seconds": observed, "dispatch_gate_minimum_seconds": gate_min, "batch_policy_accepted": report["batch_policy_accepted"], "report_sha256": sha(report_path), "source_map_sha256": sha(source_map_path)}, ensure_ascii=False))

def execute():
    verify()
    cp = OUT / "candidates.json"
    if not cp.exists():
        raise RuntimeError("run --prepare first")
    c = jread(cp)
    if c.get("batch_id") != "NET-NEWS-ASSETS-013" or len(c.get("targets") or []) != MAX_TARGETS:
        raise RuntimeError("candidate declaration mismatch")
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    before = free()
    if before < MIN_FREE:
        raise RuntimeError("disk free below threshold")
    started_utc, started = utc(), time.monotonic()
    state = core.RunState(started)
    journal = {"schema": "continuous-wow-network-news-assets13-dispatch-log/v1", "batch_id": "NET-NEWS-ASSETS-013", "simulation": False, "policy": {"minimum_dispatch_interval_seconds": INTERVAL, "max_attempts": MAX_ATTEMPTS, "network_window_seconds": WINDOW}, "disk_preflight": {"checked_utc": started_utc, "disk_free_bytes": before, "minimum_free_bytes": MIN_FREE}, "dispatches": []}
    gate = gate_mod.GateState(datetime.now(timezone.utc) - timedelta(seconds=1), journal_path=OUT / "dispatch-log.json", journal=journal)
    gate.persist()
    results, transport, postflight = [], None, {}
    try:
        for item in c["targets"]:
            if state.stop_reason:
                results.append(not_requested(item, state.stop_reason))
                continue
            row, transport = run_one(item, transport, state, gate, started)
            results.append(row)
    finally:
        postflight = gate_mod.persist_postflight(gate, state.attempts, free_fn=free)
    finished_utc, after = utc(), free()
    outputs(c, results, state, started_utc, finished_utc, before, after, transport, gate, postflight)
    print(json.dumps({"mode": "executed", "batch_id": "NET-NEWS-ASSETS-013", "network_requests": state.attempts, "source_responses": state.source_responses, "failed_attempts": state.failed_attempts, "target_count": len(results), "categories": {k: sum(x["category"] == k for x in results) for k in sorted({x["category"] for x in results})}, "valid_entities": sum(x.get("entity_valid", False) for x in results), "disk_free_before": before, "disk_free_after": after, "minimum_start_interval_seconds": min((x["interval_since_previous_dispatch_seconds"] for x in gate.dispatches if x.get("interval_since_previous_dispatch_seconds") is not None), default=None), "stop_reason": state.stop_reason}, ensure_ascii=False))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--prepare", action="store_true")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--rebuild", action="store_true")
    a = p.parse_args()
    if sum(bool(x) for x in (a.prepare, a.execute, a.rebuild)) != 1:
        p.error("choose exactly one")
    (prepare if a.prepare else execute if a.execute else rebuild_interval_report)()

