#!/usr/bin/env python3
"""Bounded GALLERY23 image replays using the accepted transport and gate."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import re
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RAW = OUT / "raw"
CORE_PATH = ROOT / "research/continuous-recovery-20261015/network-core-pages3/core_pages3.py"
GATE_PATH = ROOT / "research/continuous-recovery-20261015/network-control7/control7.py"
ASSET_PATH = ROOT / "research/continuous-recovery-20261015/network-assets5/asset_batch5.py"
ANCHOR = "20080512210044"
AUTH_START = datetime.fromisoformat("2026-10-15T15:03:05+00:00")
AUTH_END = datetime.fromisoformat("2026-10-15T15:35:00+00:00")
MAX_ATTEMPTS = 24
WINDOW_SECONDS = 360
MIN_DISPATCH = 5.1
MIN_START = 5.0
MIN_FREE = 11_005_853_696
MAX_TOTAL = 32 * 1024 * 1024
MAX_ENTITY = 8 * 1024 * 1024
STOP_HTTP = {429, 503}
UA = "wow-recovery-gallery23/20261015"
PLAN = OUT / "gallery23-plan.json"
CANDIDATES = OUT / "candidates.json"
CONFIG = OUT / "config.json"
JOURNAL = OUT / "dispatch-journal.json"
REPORT = OUT / "batch-report.json"
SUMMARY = OUT / "sanitized-summary.json"
SUMMARY_MD = OUT / "sanitized-summary.md"

TARGETS = [
    {"rank": 1, "url": "http://www.wow-europe.com:80/screenoftheday/screenoftheday/10702-01.jpg", "timestamp": "20070218110247", "digest": "VKOKERQVOQ4C2MQCY2INRXGLLEGT3SUH", "kind": "eu_full"},
    {"rank": 2, "url": "http://wow-europe.com/screenoftheday/screenoftheday/10702-01-thumb.jpg", "timestamp": "20070201161104", "digest": "4CIJR35PIPY3D4QBVZLYP7D5Y75QC6L6", "kind": "eu_thumb"},
    {"rank": 3, "url": "http://wow-europe.com:80/screenoftheday/screenoftheday/10703-14.jpg", "timestamp": "20070319092606", "digest": "CQJAVUMDXEQNF4NAHD3ZFK2EOT2AA5VY", "kind": "eu_full"},
    {"rank": 4, "url": "http://www.wow-europe.com/screenoftheday/screenoftheday/10703-14-thumb.jpg", "timestamp": "20070314035505", "digest": "ROVAFCCSMC33UBIL53T5Y4V4J3D5SFZQ", "kind": "eu_thumb"},
]
for name in ("ss42.jpg", "ss42-thumb.jpg", "ss44.jpg", "ss44-thumb.jpg", "ss47.jpg", "ss47-thumb.jpg"):
    TARGETS.append({"rank": len(TARGETS) + 1, "url": "http://www.worldofwarcraft.com/info/dungeons/images/karazhan/" + name, "timestamp": ANCHOR, "digest": None, "kind": "karazhan"})


def load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


core = load(CORE_PATH, "gallery23_core")
gate_mod = load(GATE_PATH, "gallery23_gate")
asset = load(ASSET_PATH, "gallery23_asset")
core.OUT = OUT; core.RAW = RAW; core.PROXY = "http://127.0.0.1:7890"; core.USER_AGENT = UA
core.MAX_ATTEMPTS = MAX_ATTEMPTS; core.WINDOW_SECONDS = WINDOW_SECONDS; core.MIN_FREE_BYTES = MIN_FREE
core.MAX_TOTAL_BODY_BYTES = MAX_TOTAL; core.MAX_ENTITY_BODY_BYTES = MAX_ENTITY; core.MIN_INTERVAL_SECONDS = 0.0
core.DIRECT_CONNECT_SECONDS = 8; core.PROXY_CONNECT_SECONDS = 8; core.DIRECT_MAX_SECONDS = 30; core.PROXY_MAX_SECONDS = 30; core.STOP_HTTP_CODES = STOP_HTTP
gate_mod.OUT = OUT; gate_mod.RAW = RAW; gate_mod.INTERVAL_SECONDS = MIN_DISPATCH; gate_mod.MIN_FREE_BYTES = MIN_FREE; gate_mod.MAX_TOTAL_BODY_BYTES = MAX_TOTAL; gate_mod.MAX_ENTITY_BYTES = MAX_ENTITY
asset.OUT = OUT; asset.RAW = RAW


def now() -> str: return datetime.now(timezone.utc).isoformat()
def free() -> int: return int(shutil.disk_usage(OUT).free)
def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""): h.update(b)
    return h.hexdigest()
def write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
def rel(path: Path) -> str: return path.resolve().relative_to(OUT.resolve()).as_posix()
def parse_iso(v: str | None) -> datetime | None:
    try: return datetime.fromisoformat(str(v).replace("Z", "+00:00")).astimezone(timezone.utc) if v else None
    except ValueError: return None
def b32sha1(body: bytes) -> str:
    import base64
    return base64.b32encode(hashlib.sha1(body).digest()).decode("ascii").rstrip("=")


def replay_url(item: dict[str, Any]) -> str:
    return f"https://web.archive.org/web/{item['timestamp']}id_/{item['url']}"


def prepare() -> int:
    OUT.mkdir(parents=True, exist_ok=True); RAW.mkdir(parents=True, exist_ok=True)
    disk = free()
    if disk < MIN_FREE: raise SystemExit("disk_floor")
    candidates = {"schema": "wow-recovery.gallery23-candidates.v1", "batch_id": "GALLERY23-20261015", "network_requests": 0, "target_count": len(TARGETS), "entries": [{**x, "replay_url": replay_url(x), "cdx_digest_status": "provided" if x["digest"] else "unavailable_for_karazhan_anchor", "redirect_policy": "at_most_one_same_origin_preanchor_manual_hop"} for x in TARGETS], "policy": {"max_attempts": MAX_ATTEMPTS, "window_seconds": WINDOW_SECONDS, "max_total_body_bytes": MAX_TOTAL, "max_entity_body_bytes": MAX_ENTITY, "min_dispatch_monotonic_seconds": MIN_DISPATCH, "min_request_start_utc_seconds": MIN_START, "disk_floor_bytes": MIN_FREE, "automatic_redirects": 0, "manual_redirects_per_entity": 1, "cdx_requests": 0, "availability_requests": 0, "hard_cutoff_utc": AUTH_END.isoformat()}}
    write(CANDIDATES, candidates)
    config = {"schema": "wow-recovery.gallery23-config.v1", "batch_id": candidates["batch_id"], "prepared_utc": now(), "network_requests": 0, "disk_free_bytes": disk, "candidates_sha256": sha(CANDIDATES), "policy": candidates["policy"]}
    write(CONFIG, config)
    write(PLAN, {"schema": "wow-recovery.gallery23-plan.v1", "mode": "plan_only", "batch_id": candidates["batch_id"], "prepared_utc": now(), "network_requests": 0, "target_count": 10, "input": "four supplied EU CDX identities plus six Karazhan anchor URLs", "outputs": {"raw": rel(RAW), "journal": rel(JOURNAL), "report": rel(REPORT), "summary": rel(SUMMARY)}, "disk_free_bytes": disk, "candidates_sha256": sha(CANDIDATES), "config_sha256": sha(CONFIG)})
    print(json.dumps({"mode": "prepared", "network_requests": 0, "target_count": 10, "disk_free_bytes": disk}))
    return 0


def wait_wall(last_started: datetime | None) -> None:
    if last_started:
        while True:
            remain = MIN_START - (datetime.now(timezone.utc) - last_started).total_seconds()
            if remain <= 0: return
            time.sleep(min(60, max(remain, 0.01)))


def dispatch(url: str, label: str, transport: str, state: Any, gate: Any, window_started: float, last_started: datetime | None) -> tuple[dict[str, Any] | None, datetime | None]:
    if datetime.now(timezone.utc) >= AUTH_END or state.attempts >= MAX_ATTEMPTS or free() < MIN_FREE or time.monotonic() - window_started >= WINDOW_SECONDS:
        state.stop_reason = state.stop_reason or "cap_or_cutoff_or_disk"; return None, last_started
    wait_wall(last_started)
    rec = gate.before_dispatch(state.attempts + 1, transport, label)
    if datetime.now(timezone.utc) >= AUTH_END or free() < MIN_FREE:
        rec["not_executed_reason"] = "cutoff_or_disk"; gate.persist(); state.stop_reason = "cutoff_or_disk"; return None, last_started
    attempt = core.run_request(url, transport, "replay", label, state, state.attempts + 1)
    attempt["dispatch"] = rec; rec.update({"request_start_utc": attempt.get("started_utc"), "finished_utc": attempt.get("finished_utc"), "source_status": attempt.get("source_status"), "curl_exit": attempt.get("curl_exit"), "body_bytes": attempt.get("body_bytes"), "transport_error": attempt.get("transport_error")}); gate.persist()
    return attempt, parse_iso(attempt.get("started_utc")) or last_started


def pair(url: str, label: str, state: Any, gate: Any, window_started: float, last_started: datetime | None) -> tuple[list[dict[str, Any]], datetime | None]:
    got: list[dict[str, Any]] = []
    for transport in ("direct", "proxy"):
        a, last_started = dispatch(url, label, transport, state, gate, window_started, last_started)
        if a is None: break
        got.append(a)
        if not a.get("transport_error"): break
        if state.stop_reason: break
    return got, last_started


def image_observation(attempt: dict[str, Any] | None, item: dict[str, Any]) -> tuple[dict[str, Any], str]:
    body = b""
    if attempt and attempt.get("executed"):
        body = (OUT / str((attempt.get("raw") or {}).get("body") or "")).read_bytes()
    expected = item.get("digest")
    calc = b32sha1(body) if body else None
    memento = parse_iso(attempt.get("memento_datetime") if attempt else None)
    capture = datetime.strptime(item["timestamp"], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    dec: dict[str, Any] = {"library": "Pillow", "verify": "not_run", "load": "not_run", "format": None, "width": None, "height": None, "mode": None, "error": None}
    pillow_ok = False
    try:
        with asset.Image.open(io.BytesIO(body)) as im:
            dec["format"] = im.format; dec["width"], dec["height"] = im.size; dec["mode"] = im.mode; im.verify()
        dec["verify"] = "passed"
        with asset.Image.open(io.BytesIO(body)) as im: im.load()
        dec["load"] = "passed"; pillow_ok = bool(dec["format"] and dec["width"] and dec["height"])
    except Exception as exc: dec["error"] = type(exc).__name__ + ": " + str(exc)
    digest_status = "match" if expected and calc == expected else ("mismatch" if expected else "unavailable")
    valid = bool(attempt and attempt.get("source_status") == 200 and memento and memento <= datetime.strptime(ANCHOR, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc) and pillow_ok and digest_status == "match" and capture == memento)
    if valid: category = "valid_image"
    elif attempt and attempt.get("source_status") in {301, 302, 303, 307, 308}: category = "redirect_unfollowed"
    elif not attempt or attempt.get("transport_error") or attempt.get("source_status") is None: category = "transport_error"
    elif attempt.get("source_status") == 404: category = "not_archived"
    elif pillow_ok and digest_status == "unavailable": category = "image_candidate_no_cdx_digest"
    elif digest_status == "mismatch": category = "cdx_digest_mismatch"
    else: category = "invalid_image"
    return {"valid": valid, "category": category, "source_status": attempt.get("source_status") if attempt else None, "actual_memento": attempt.get("memento_datetime") if attempt else None, "actual_memento_matches_capture": bool(memento and memento == capture), "body_bytes": len(body), "body_sha256": hashlib.sha256(body).hexdigest() if body else None, "cdx_digest_expected": expected, "cdx_digest_calculated": calc, "cdx_digest_status": digest_status, "content_type": attempt.get("content_type") if attempt else None, "raw_body_path": (attempt.get("raw") or {}).get("body") if attempt else None, "raw_headers_path": (attempt.get("raw") or {}).get("headers") if attempt else None, "decode": dec}, category


def legal_follow(location: str | None, item: dict[str, Any]) -> str | None:
    if not location: return None
    p = urlsplit(location)
    if p.scheme not in {"http", "https"} or (p.hostname or "").lower() not in {"web.archive.org", "web.archive.org"} or not p.path.startswith("/web/"): return None
    tail = p.path[5:]; ts = tail[:14] if len(tail) >= 14 and tail[:14].isdigit() else ""
    if not ts or ts > ANCHOR: return None
    x = tail[14:]; x = x[3:] if x.startswith("id_") else x
    original = unquote(x)
    if core.normalized_url_identity(original) != core.normalized_url_identity(item["url"]): return None
    return location


def execute() -> int:
    if REPORT.exists(): raise SystemExit("report_exists")
    OUT.mkdir(parents=True, exist_ok=True); RAW.mkdir(parents=True, exist_ok=True)
    disk_before = free()
    if disk_before < MIN_FREE: raise SystemExit("disk_floor_before")
    started = now(); ws = time.monotonic(); state = core.RunState(ws)
    journal = {"schema": "wow-recovery.gallery23-dispatch-journal.v1", "batch_id": "GALLERY23-20261015", "simulation": False, "authorization_window": {"start_utc": AUTH_START.isoformat(), "end_utc": AUTH_END.isoformat()}, "policy": {"max_attempts": MAX_ATTEMPTS, "min_dispatch_monotonic_seconds": MIN_DISPATCH, "min_request_start_utc_seconds": MIN_START, "disk_floor_bytes": MIN_FREE}, "disk_preflight": {"checked_utc": started, "disk_free_bytes": disk_before, "minimum_free_bytes": MIN_FREE}, "dispatches": []}
    write(JOURNAL, journal); gate = gate_mod.GateState(AUTH_START, journal_path=JOURNAL, journal=journal)
    last = None; all_attempts = []; results = []; source_count = 0; redirects = 0
    try:
        for item in TARGETS:
            if state.stop_reason: results.append({**item, "category": "not_requested", "reason": state.stop_reason}); continue
            url = replay_url(item); hop = 0; item_attempts = []; current = url; final = None; follow_log = []
            while True:
                attempts, last = pair(current, f"r{item['rank']}-hop{hop}", state, gate, ws, last); item_attempts.extend(attempts); all_attempts.extend(attempts)
                final = attempts[-1] if attempts else None
                obs, category = image_observation(final, item); follow_log.append({"url": current, "attempts": [core.source_attempt_view(x) for x in attempts], "observation": obs})
                if category == "valid_image" or not final or final.get("source_status") != 302 or hop >= 1: break
                loc = legal_follow(final.get("location"), item)
                redirects += 1
                if not loc: break
                current = loc; hop += 1
            source_count += sum(a.get("source_status") is not None for a in item_attempts)
            results.append({**item, "category": category, "attempt_count": len(item_attempts), "source_response_count": sum(a.get("source_status") is not None for a in item_attempts), "actual_memento": obs.get("actual_memento"), "body_bytes": obs.get("body_bytes"), "body_sha256": obs.get("body_sha256"), "validation": obs, "operations": follow_log})
            if state.stop_reason in {"endpoint_status_429", "endpoint_status_503", "five_consecutive_tls_or_transport_failures", "attempt_limit", "network_window_exhausted", "disk_free_below_threshold"}: break
    finally:
        post = gate_mod.persist_postflight(gate, state.attempts, free_fn=free)
    if not state.stop_reason: state.stop_reason = "completed" if len(results) == len(TARGETS) else "cutoff_or_cap"
    dispatches = journal.get("dispatches") or []
    di = [dispatches[i]["dispatch_monotonic"] - dispatches[i-1]["dispatch_monotonic"] for i in range(1, len(dispatches))]
    times = [parse_iso(a.get("started_utc")) for a in all_attempts if parse_iso(a.get("started_utc"))]
    ri = [(times[i]-times[i-1]).total_seconds() for i in range(1, len(times))]
    report = {"schema": "wow-recovery.gallery23-batch-report.v1", "batch_id": "GALLERY23-20261015", "mode": "executed", "target_count": len(TARGETS), "started_utc": started, "finished_utc": now(), "authorization_window": {"start_utc": AUTH_START.isoformat(), "end_utc": AUTH_END.isoformat()}, "attempt_count": state.attempts, "source_response_count": source_count, "failed_attempt_count": sum(bool(a.get("transport_error")) for a in all_attempts), "total_body_bytes": state.total_body_bytes, "valid_image_count": sum(r.get("category") == "valid_image" for r in results), "candidate_no_digest_count": sum(r.get("category") == "image_candidate_no_cdx_digest" for r in results), "redirect_evidence_count": redirects, "results": results, "attempts": [core.source_attempt_view(a) for a in all_attempts], "stop_reason": state.stop_reason, "stop_detail": state.stop_detail, "disk_preflight": journal["disk_preflight"], "disk_postflight": post, "cadence": {"dispatch_intervals": di, "request_start_intervals": ri, "min_dispatch_monotonic_seconds": min(di) if di else None, "min_request_start_utc_seconds": min(ri) if ri else None, "required_dispatch_monotonic_seconds": MIN_DISPATCH, "required_request_start_utc_seconds": MIN_START}, "policy": {"max_attempts": MAX_ATTEMPTS, "window_seconds": WINDOW_SECONDS, "max_total_body_bytes": MAX_TOTAL, "max_entity_body_bytes": MAX_ENTITY, "automatic_redirects": 0, "cdx_requests": 0, "availability_requests": 0, "hard_cutoff_utc": AUTH_END.isoformat()}, "raw_evidence_note": "Raw headers, traces and bodies remain local; supplied CDX digest is required for valid_image, Karazhan anchor bodies without matching CDX remain candidates only."}
    write(REPORT, report)
    summary = {"schema": "wow-recovery.gallery23-sanitized-summary.v1", "batch_id": report["batch_id"], "attempt_count": report["attempt_count"], "source_response_count": report["source_response_count"], "valid_image_count": report["valid_image_count"], "candidate_no_digest_count": report["candidate_no_digest_count"], "results": [{k: v for k, v in r.items() if k not in {"operations"}} for r in results], "stop_reason": report["stop_reason"], "disk_preflight": report["disk_preflight"], "disk_postflight": report["disk_postflight"], "cadence": report["cadence"], "raw_evidence_note": report["raw_evidence_note"]}
    write(SUMMARY, summary); SUMMARY_MD.write_text("\n".join(["# GALLERY23 sanitized summary", f"- Targets: `{len(TARGETS)}`; attempts `{report['attempt_count']}`; source responses `{report['source_response_count']}`.", f"- Valid images: `{report['valid_image_count']}`; no-CDX candidates: `{report['candidate_no_digest_count']}`; stop `{report['stop_reason']}`.", "- Raw headers, traces and bodies remain local; no source/export integration."]) + "\n", encoding="utf-8")
    journal["report_written_utc"] = now(); journal["report_sha256"] = sha(REPORT); write(JOURNAL, journal)
    print(json.dumps({"mode": "executed", "exit": 0, "attempts": report["attempt_count"], "source_responses": report["source_response_count"], "valid_images": report["valid_image_count"], "candidates_no_digest": report["candidate_no_digest_count"], "stop_reason": report["stop_reason"], "disk_free_before": disk_before, "disk_free_after": post["disk_free_bytes"]}))
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--prepare", action="store_true"); p.add_argument("--execute", action="store_true"); a = p.parse_args()
    if a.prepare == a.execute: p.error("choose exactly one")
    raise SystemExit(prepare() if a.prepare else execute())
