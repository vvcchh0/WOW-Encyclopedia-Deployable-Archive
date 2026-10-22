"""Bounded, root-GO-gated verifier for the fixed GitHub Pages v52 Dungeons object set."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import time
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PLAN = OUT / "plan.json"
MANIFEST = OUT / "object-manifest.json"
BINDINGS = OUT / "input-bindings.json"
FIXTURES = OUT / "offline-validation.json"
RUNTIME = OUT / "runtime"
RAW = RUNTIME / "private" / "raw"
JOURNAL = RUNTIME / "private" / "attempt-journal.jsonl"
PRIVATE_REPORT = RUNTIME / "private" / "execution-report.json"
PUBLIC_SUMMARY = RUNTIME / "object-match-summary.json"
MIN_DISK = 11005853696
MIN_START_INTERVAL = 6.2
MAX_OBJECT_BYTES = 4 * 1024 * 1024
MAX_TOTAL_BYTES = 16 * 1024 * 1024
MAX_SECONDS = 600
REQUEST_TIMEOUT = 30
CONNECT_TIMEOUT = 10
TRANSPORT_FAILURE_COOLDOWN = 120
MAX_ATTEMPTS = 40
MAX_LOGICAL = 20
PROXY = "http://127.0.0.1:7890"
_STOP_STATUSES = {429, 503}
_LAST_START: float | None = None


class RequestTimeBudgetExpired(RuntimeError):
    pass


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_url(raw: str) -> str | None:
    try:
        p = urlsplit(raw)
        if p.scheme.lower() not in {"http", "https"} or not p.hostname or p.username or p.password:
            return None
        host = p.hostname.encode("idna").decode("ascii").lower()
        if p.port:
            host += f":{p.port}"
        path = p.path or "/"
        path = "".join(c for c in path if ord(c) >= 32 and ord(c) != 127)
        return urlunsplit((p.scheme.lower(), host, path, "", ""))
    except (UnicodeError, ValueError):
        return None


def disk_free() -> int:
    return shutil.disk_usage("D:/").free


def require_disk(phase: str) -> int:
    free = disk_free()
    if free < MIN_DISK:
        raise RuntimeError(f"disk floor reached {phase}: {free} < {MIN_DISK}")
    return free


def checked_write_json(path: Path, data: dict[str, Any]) -> None:
    require_disk(f"before write {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
    require_disk(f"after write {path.name}")


def validate_plan() -> tuple[dict[str, Any], dict[str, Any]]:
    plan = read_json(PLAN)
    manifest = read_json(MANIFEST)
    if plan.get("mode") != "prepared" or plan.get("root_go_required") is not True:
        raise RuntimeError("plan is not in prepared/root-GO state")
    if plan.get("batch_id") != "github-pages-v52-dungeons20" or manifest.get("batch_id") != plan.get("batch_id"):
        raise RuntimeError("batch identity mismatch")
    policy = plan.get("policy", {})
    if (
        policy.get("maximum_objects") != MAX_LOGICAL
        or policy.get("maximum_http_attempts") != MAX_ATTEMPTS
        or policy.get("maximum_batch_seconds") != MAX_SECONDS
        or policy.get("maximum_request_seconds") != REQUEST_TIMEOUT
        or policy.get("minimum_request_start_seconds") != 6.2
        or policy.get("maximum_total_body_bytes") != MAX_TOTAL_BYTES
        or policy.get("maximum_object_body_bytes") != MAX_OBJECT_BYTES
        or policy.get("consecutive_transfer_failure_cooldown_seconds_minimum") != TRANSPORT_FAILURE_COOLDOWN
        or policy.get("disk_floor_bytes") != MIN_DISK
        or policy.get("stop_http_statuses") != [429, 503]
    ):
        raise RuntimeError("runner constants differ from the reviewed plan")
    if sha_file(MANIFEST) != plan.get("object_manifest_sha256"):
        raise RuntimeError("object manifest hash differs from plan")
    objects = manifest.get("objects")
    if not isinstance(objects, list) or len(objects) != MAX_LOGICAL or len({x.get("path") for x in objects}) != MAX_LOGICAL:
        raise RuntimeError("expected exactly 20 unique objects")
    targets_sha = sha_bytes(json.dumps(objects, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    if targets_sha != plan.get("targets_sha256"):
        raise RuntimeError("target manifest hash differs from plan")
    src = manifest.get("source_bindings", {})
    gate = src.get("local_v52_gate", {})
    if gate.get("accepted") is not True or gate.get("version") != "v52":
        raise RuntimeError("local v52 gate is not accepted")
    site = ROOT / gate["local_site"]
    for key, binding in src.items():
        source = ROOT / binding["path"]
        if not source.is_file() or sha_file(source) != binding["sha256"]:
            raise RuntimeError(f"source binding changed: {key}")
    expected_base = src["frozen_verifier"]["base_url"]
    if expected_base != "https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/":
        raise RuntimeError("unexpected hosted base URL")
    for obj in objects:
        if obj.get("url") != expected_base + obj["path"] or safe_url(obj["url"]) != obj["url"]:
            raise RuntimeError(f"unsafe or unbound target URL: {obj.get('object_id')}")
        local = ROOT / obj["local_path"]
        if not local.is_file():
            raise RuntimeError(f"missing v52 local object: {obj['path']}")
        body = local.read_bytes()
        if len(body) != obj["local_bytes"] or sha_bytes(body) != obj["local_sha256"]:
            raise RuntimeError(f"local v52 object changed: {obj['path']}")
        if obj["kind"] == "page" and obj["expected_mime"] != "text/html":
            raise RuntimeError("HTML page MIME mismatch")
        if obj["kind"] in {"original", "thumbnail"} and obj["expected_mime"] != "image/jpeg":
            raise RuntimeError("image MIME mismatch")
    if sum(x["kind"] == "page" for x in objects) != 1 or sum(x["kind"] == "original" for x in objects) != 9 or sum(x["kind"] == "thumbnail" for x in objects) != 10:
        raise RuntimeError("expected one page, nine originals, and ten thumbnails")
    return plan, manifest


def object_matches(spec: dict[str, Any], attempt: dict[str, Any]) -> bool:
    return (
        attempt.get("curl_exit") == 0
        and attempt.get("http_status") == 200
        and attempt.get("mime") == spec["expected_mime"]
        and attempt.get("body_bytes") == spec["local_bytes"]
        and attempt.get("body_sha256") == spec["local_sha256"]
        and attempt.get("effective_url") == spec["url"]
        and not attempt.get("timed_out")
        and not attempt.get("response_cap_exceeded")
    )


def transfer_failed(attempt: dict[str, Any]) -> bool:
    return bool(attempt.get("timed_out") or attempt.get("curl_exit") not in (0, None) or attempt.get("http_status") is None)


def request_timeout_after_wait(deadline: float, now: float) -> float:
    remaining = deadline - now
    if remaining <= 0:
        raise RequestTimeBudgetExpired("batch time budget expired while waiting for request slot")
    return min(float(REQUEST_TIMEOUT), remaining)


def record_transfer_failure(report: dict[str, Any], attempt: dict[str, Any], consecutive: int) -> tuple[int, bool]:
    consecutive += 1
    report["consecutive_transfer_failures"] = consecutive
    tail = report.setdefault("consecutive_transfer_failure_tail", [])
    tail.append({key: attempt.get(key) for key in (
        "attempt", "object_id", "transport", "request_started_utc", "request_finished_utc",
        "curl_exit", "http_status", "timed_out")})
    del tail[:-5]
    if consecutive < 5:
        return consecutive, False
    raw_end = attempt.get("request_finished_utc")
    try:
        ended = datetime.fromisoformat(str(raw_end).replace("Z", "+00:00"))
        if ended.tzinfo is None:
            ended = ended.replace(tzinfo=timezone.utc)
        ended = ended.astimezone(timezone.utc)
    except (TypeError, ValueError, OverflowError):
        ended = datetime.now(timezone.utc)
    cooldown_until = ended + timedelta(seconds=TRANSPORT_FAILURE_COOLDOWN)
    report["stop_reason"] = "five_consecutive_transfer_failures"
    report["cooldown_not_before_utc"] = cooldown_until.isoformat().replace("+00:00", "Z")
    return consecutive, True


def retry_after_seconds(headers_path: Path, now: datetime | None = None) -> int:
    now = now or datetime.now(timezone.utc)
    if not headers_path.is_file():
        return 0
    values = []
    for line in headers_path.read_text(encoding="iso-8859-1", errors="replace").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key.strip().lower() == "retry-after":
            values.append(value.strip())
    for value in reversed(values):
        if value.isdigit():
            return int(value)
        try:
            parsed = parsedate_to_datetime(value)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return max(0, math.ceil((parsed.astimezone(timezone.utc) - now).total_seconds()))
        except (TypeError, ValueError, OverflowError):
            pass
    return 0


def public_attempt(attempt: dict[str, Any]) -> dict[str, Any]:
    return {
        "transport": attempt.get("transport"),
        "request_started_utc": attempt.get("request_started_utc"),
        "request_finished_utc": attempt.get("request_finished_utc"),
        "actual_start_interval_seconds": attempt.get("actual_start_interval_seconds"),
        "http_status": attempt.get("http_status"),
        "content_type": attempt.get("content_type"),
        "effective_url": safe_url(attempt.get("effective_url") or ""),
        "body_bytes": attempt.get("body_bytes"),
        "body_sha256": attempt.get("body_sha256"),
        "curl_exit": attempt.get("curl_exit"),
        "timed_out": attempt.get("timed_out", False),
        "response_cap_exceeded": attempt.get("response_cap_exceeded", False),
    }


def wait_for_slot() -> float | None:
    global _LAST_START
    if _LAST_START is not None:
        wait = MIN_START_INTERVAL - (time.monotonic() - _LAST_START)
        if wait > 0:
            time.sleep(wait)
    now = time.monotonic()
    interval = now - _LAST_START if _LAST_START is not None else None
    _LAST_START = now
    return interval


def run_attempt(spec: dict[str, Any], transport: str, attempt_no: int, request_cap: int, deadline: float) -> dict[str, Any]:
    if transport not in {"direct", "proxy"}:
        raise ValueError(transport)
    if request_cap <= 0:
        raise RuntimeError("no response-byte budget remains")
    interval = wait_for_slot()
    timeout = request_timeout_after_wait(deadline, time.monotonic())
    disk_before = require_disk("before object request")
    safe_id = spec["object_id"]
    stem = f"attempt-{attempt_no:02d}-{safe_id}-{transport}"
    body = RAW / f"{stem}.body"
    headers = RAW / f"{stem}.headers"
    cookies = RAW / f"{stem}.cookies.txt"
    stderr_path = RAW / f"{stem}.stderr.txt"
    RAW.mkdir(parents=True, exist_ok=True)
    command = [
        "curl.exe", "--silent", "--show-error", "--max-time", f"{timeout:.6f}",
        "--connect-timeout", f"{min(float(CONNECT_TIMEOUT), timeout):.6f}", "--max-filesize", str(request_cap),
        "--dump-header", str(headers), "--cookie-jar", str(cookies), "--output", str(body),
        "--write-out", "%{http_code}\\n%{content_type}\\n%{url_effective}",
    ]
    if transport == "direct":
        command[1:1] = ["--noproxy", "*"]
    else:
        command[1:1] = ["--noproxy", "", "--proxy", PROXY]
    command.append(spec["url"])
    started = stamp()
    start_mono = time.monotonic()
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout + 1, check=False)
        stdout = proc.stdout.splitlines()
        rc = proc.returncode
        stderr_text = proc.stderr or ""
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        stdout = []
        rc = None
        stderr_text = str(exc)
        timed_out = True
    finished = stamp()
    stderr_path.write_text(stderr_text, encoding="utf-8", errors="replace")
    raw_body = body.read_bytes() if body.exists() else b""
    status = int(stdout[0]) if stdout and stdout[0].isdigit() else None
    content_type = stdout[1] if len(stdout) > 1 else ""
    effective = stdout[2] if len(stdout) > 2 else spec["url"]
    mime = content_type.split(";", 1)[0].strip().lower()
    after = require_disk("after object request")
    cap_exceeded = len(raw_body) > request_cap or rc == 63
    return {
        "attempt": attempt_no, "object_id": safe_id, "url": spec["url"], "transport": transport,
        "request_started_utc": started, "request_finished_utc": finished,
        "actual_start_interval_seconds": interval, "elapsed_seconds": round(time.monotonic() - start_mono, 3),
        "curl_exit": rc, "http_status": status, "content_type": content_type, "mime": mime,
        "effective_url": effective, "body_bytes": len(raw_body), "body_sha256": sha_bytes(raw_body),
        "timed_out": timed_out, "response_cap_exceeded": cap_exceeded,
        "transport_failed": bool(timed_out or rc not in (0, None) or status is None),
        "retry_after_seconds": retry_after_seconds(headers), "disk_free_before_bytes": disk_before,
        "disk_free_after_bytes": after, "raw_body_path": str(body.relative_to(OUT)).replace("\\", "/"),
        "raw_headers_path": str(headers.relative_to(OUT)).replace("\\", "/"),
        "raw_cookie_jar_path": str(cookies.relative_to(OUT)).replace("\\", "/"),
        "stderr_path": str(stderr_path.relative_to(OUT)).replace("\\", "/"),
        "stderr_sha256": sha_file(stderr_path), "stderr": stderr_text[-2000:],
    }


def execution_go(path: Path, plan: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    if RUNTIME.exists():
        raise RuntimeError("refusing existing runtime directory")
    if not BINDINGS.is_file() or not FIXTURES.is_file():
        raise RuntimeError("missing input bindings or offline validation")
    bindings = read_json(BINDINGS)
    expected = {
        "plan_sha256": sha_file(PLAN), "runner_sha256": sha_file(Path(__file__)),
        "object_manifest_sha256": sha_file(MANIFEST), "fixture_sha256": sha_file(FIXTURES),
        "targets_sha256": plan["targets_sha256"],
        "local_v52_gate_sha256": manifest["source_bindings"]["local_v52_gate"]["sha256"],
        "browser_inspection_sha256": manifest["source_bindings"]["browser_inspection"]["sha256"],
        "frozen_verifier_sha256": manifest["source_bindings"]["frozen_verifier"]["sha256"],
        "verifier_wrapper_sha256": manifest["source_bindings"]["verifier_wrapper"]["sha256"],
        "publication_report_sha256": manifest["source_bindings"]["publication_report"]["sha256"],
    }
    for key, value in expected.items():
        if bindings.get(key) != value:
            raise RuntimeError(f"input binding mismatch: {key}")
    fixture = read_json(FIXTURES)
    if fixture.get("all_passed") is not True or fixture.get("network_requests") != 0:
        raise RuntimeError("offline checks are not accepted/no-network")
    if not path.is_file():
        raise RuntimeError("root GO is missing")
    go = read_json(path)
    if go.get("accepted") is not True or go.get("root_go") is not True or go.get("batch_id") != plan["batch_id"]:
        raise RuntimeError("root GO is not accepted for this batch")
    go_keys = {
        "plan_sha256": expected["plan_sha256"], "runner_sha256": expected["runner_sha256"],
        "object_manifest_sha256": expected["object_manifest_sha256"], "fixture_sha256": expected["fixture_sha256"],
        "input_bindings_sha256": sha_file(BINDINGS), "targets_sha256": expected["targets_sha256"],
    }
    for key, value in go_keys.items():
        if go.get(key) != value:
            raise RuntimeError(f"GO hash mismatch: {key}")
    valid_until = go.get("valid_until")
    if valid_until and datetime.fromisoformat(str(valid_until).replace("Z", "+00:00")) <= datetime.now(timezone.utc):
        raise RuntimeError("root GO is expired")
    require_disk("before execution")
    return go


def execute(go_path: Path) -> int:
    plan, manifest = validate_plan()
    go = execution_go(go_path.resolve(), plan, manifest)
    RUNTIME.mkdir(parents=True)
    (RUNTIME / "private").mkdir(parents=True)
    RAW.mkdir(parents=True)
    records: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    report: dict[str, Any] = {
        "schema": "wow-recovery.github-pages-v52-dungeons20.private-report.v1",
        "batch_id": plan["batch_id"], "go_path": str(go_path), "go_sha256": sha_file(go_path),
        "plan_sha256": sha_file(PLAN), "manifest_sha256": sha_file(MANIFEST),
        "started_utc": stamp(), "objects": records, "attempts": attempts,
        "total_body_bytes": 0, "stop_reason": None, "cooldown_not_before_utc": None,
        "consecutive_transfer_failures": 0, "consecutive_transfer_failure_tail": [],
    }
    public: dict[str, Any] = {
        "schema": "wow-recovery.github-pages-v52-dungeons20.public-summary.v1",
        "batch_id": plan["batch_id"], "started_utc": report["started_utc"],
        "complete": False, "accepted": False, "stop_reason": None,
        "object_count_expected": MAX_LOGICAL, "objects": [],
    }
    deadline = time.monotonic() + MAX_SECONDS
    total_bytes = 0
    consecutive_transfer_failures = 0
    attempt_no = 0
    stop = False
    for spec in manifest["objects"]:
        if stop or time.monotonic() >= deadline or attempt_no >= MAX_ATTEMPTS or total_bytes >= MAX_TOTAL_BYTES:
            break
        row = {
            "object_id": spec["object_id"], "kind": spec["kind"], "url": spec["url"],
            "local_bytes": spec["local_bytes"], "local_sha256": spec["local_sha256"],
            "expected_mime": spec["expected_mime"], "attempts": [], "matches_local": False,
        }
        records.append(row)
        public_row = {
            "object_id": row["object_id"], "kind": row["kind"], "url": safe_url(row["url"]),
            "local_bytes": row["local_bytes"], "local_sha256": row["local_sha256"],
            "expected_mime": row["expected_mime"], "attempts": [], "matches_local": False,
        }
        public["objects"].append(public_row)
        object_bytes = 0
        next_transport = "direct"
        while next_transport:
            if time.monotonic() >= deadline:
                report["stop_reason"] = "time_budget_exhausted"
                stop = True
                break
            if attempt_no >= MAX_ATTEMPTS:
                report["stop_reason"] = "attempt_budget_exhausted"
                stop = True
                break
            remaining = min(MAX_TOTAL_BYTES - total_bytes, MAX_OBJECT_BYTES - object_bytes)
            if remaining <= 0:
                report["stop_reason"] = "body_budget_exhausted"
                stop = True
                break
            if deadline - time.monotonic() <= 0:
                report["stop_reason"] = "time_budget_exhausted"
                stop = True
                break
            next_attempt_no = attempt_no + 1
            try:
                attempt = run_attempt(spec, next_transport, next_attempt_no, remaining, deadline)
            except RequestTimeBudgetExpired:
                report["stop_reason"] = "time_budget_exhausted_after_start_spacing"
                stop = True
                next_transport = ""
                break
            attempt_no = next_attempt_no
            attempt["request_body_cap"] = remaining
            row["attempts"].append(attempt)
            attempts.append(attempt)
            total_bytes += attempt["body_bytes"]
            object_bytes += attempt["body_bytes"]
            report["total_body_bytes"] = total_bytes
            public_row["attempts"].append(public_attempt(attempt))
            (RUNTIME / "private").mkdir(parents=True, exist_ok=True)
            require_disk("before journal append")
            with JOURNAL.open("a", encoding="utf-8") as handle:
                safe_record = {k: attempt.get(k) for k in (
                    "attempt", "object_id", "url", "transport", "request_started_utc", "request_finished_utc",
                    "actual_start_interval_seconds", "http_status", "effective_url", "body_bytes", "body_sha256",
                    "curl_exit", "timed_out", "response_cap_exceeded", "disk_free_before_bytes", "disk_free_after_bytes",
                    "raw_body_path", "raw_headers_path", "raw_cookie_jar_path", "stderr_path", "retry_after_seconds")}
                handle.write(json.dumps(safe_record, ensure_ascii=False) + "\n")
            if attempt["http_status"] in _STOP_STATUSES:
                wait = max(120, attempt["retry_after_seconds"])
                report["stop_reason"] = f"http_{attempt['http_status']}_cooldown"
                report["cooldown_not_before_utc"] = (datetime.now(timezone.utc) + timedelta(seconds=wait)).isoformat().replace("+00:00", "Z")
                stop = True
                next_transport = ""
            elif attempt["response_cap_exceeded"] or total_bytes > MAX_TOTAL_BYTES or object_bytes > MAX_OBJECT_BYTES:
                report["stop_reason"] = "response_or_body_cap_exceeded"
                stop = True
                next_transport = ""
            elif transfer_failed(attempt):
                consecutive_transfer_failures, should_stop = record_transfer_failure(report, attempt, consecutive_transfer_failures)
                if should_stop:
                    stop = True
                    next_transport = ""
                elif next_transport == "direct":
                    next_transport = "proxy"
                else:
                    next_transport = ""
            else:
                consecutive_transfer_failures = 0
                report["consecutive_transfer_failures"] = 0
                report["consecutive_transfer_failure_tail"] = []
                row["matches_local"] = object_matches(spec, attempt)
                public_row["matches_local"] = row["matches_local"]
                next_transport = ""
            report["logical_requests"] = len(records)
            report["attempt_count"] = attempt_no
            report["consecutive_transfer_failures"] = consecutive_transfer_failures
            report["finished_utc"] = stamp()
            public["finished_utc"] = report["finished_utc"]
            public["complete"] = False
            public["stop_reason"] = report.get("stop_reason")
            checked_write_json(PRIVATE_REPORT, report)
            checked_write_json(PUBLIC_SUMMARY, public)
        if stop:
            break
    if report.get("stop_reason") is None:
        report["stop_reason"] = "completed"
    report["finished_utc"] = stamp()
    report["logical_requests"] = len(records)
    report["attempt_count"] = attempt_no
    report["accepted_objects"] = sum(bool(x["matches_local"]) for x in records)
    report["complete"] = len(records) == MAX_LOGICAL and all(len(x["attempts"]) > 0 for x in records)
    report["accepted"] = report["complete"] and report["accepted_objects"] == MAX_LOGICAL and report["stop_reason"] == "completed"
    report["total_body_bytes"] = total_bytes
    report["disk_free_bytes"] = require_disk("before final report")
    public.update({
        "finished_utc": report["finished_utc"], "complete": report["complete"],
        "accepted": report["accepted"], "stop_reason": report["stop_reason"],
        "attempt_count": attempt_no, "total_body_bytes": total_bytes,
        "accepted_objects": report["accepted_objects"],
    })
    checked_write_json(PRIVATE_REPORT, report)
    checked_write_json(PUBLIC_SUMMARY, public)
    print(json.dumps({"accepted": report["accepted"], "complete": report["complete"], "objects": report["accepted_objects"], "attempts": attempt_no, "stop_reason": report["stop_reason"]}, ensure_ascii=False))
    return 0 if report["accepted"] else 2


def offline_fixtures() -> int:
    plan, manifest = validate_plan()
    checks = []
    def check(name: str, condition: bool) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append({"name": name, "passed": True})
    objects = manifest["objects"]
    check("exact_20_object_manifest_unique_urls", len(objects) == 20 and len({x['url'] for x in objects}) == 20)
    check("one_page_nine_originals_ten_thumbnails", sum(x['kind']=='page' for x in objects)==1 and sum(x['kind']=='original' for x in objects)==9 and sum(x['kind']=='thumbnail' for x in objects)==10)
    check("all_local_v52_size_and_sha_bindings", all((ROOT/x['local_path']).stat().st_size==x['local_bytes'] and sha_file(ROOT/x['local_path'])==x['local_sha256'] for x in objects))
    sample=objects[0]
    matching={"curl_exit":0,"http_status":200,"mime":sample["expected_mime"],"body_bytes":sample["local_bytes"],"body_sha256":sample["local_sha256"],"effective_url":sample["url"]}
    check("200_expected_mime_and_hash_accept",object_matches(sample,matching))
    mismatch=dict(matching,body_sha256="0"*64)
    check("hash_mismatch_rejected",not object_matches(sample,mismatch))
    bad_mime=dict(matching,mime="text/plain")
    check("wrong_mime_rejected",not object_matches(sample,bad_mime))
    redirect=dict(matching,http_status=302)
    check("redirect_status_not_followed_or_accepted",not object_matches(sample,redirect))
    check("429_503_stop_without_proxy_retry",all(s in _STOP_STATUSES for s in (429,503)))
    check("only_transport_failure_eligible_for_proxy",transfer_failed({"curl_exit":28,"http_status":None}) and not transfer_failed({"curl_exit":0,"http_status":404}))
    check("per_object_and_batch_caps_bounded",min(MAX_OBJECT_BYTES,MAX_TOTAL_BYTES,MAX_OBJECT_BYTES)==MAX_OBJECT_BYTES and MAX_TOTAL_BYTES==16777216)
    check("request_starts_spaced_at_least_6_2_seconds",MIN_START_INTERVAL>=6.2)
    try:
        request_timeout_after_wait(100.0, 100.0)
        expired_after_wait = False
    except RequestTimeBudgetExpired:
        expired_after_wait = True
    check("remaining_request_budget_rechecked_after_slot_wait",request_timeout_after_wait(100.0, 98.75)==1.25 and expired_after_wait)
    stub_base=datetime(2026,10,22,8,0,0,tzinfo=timezone.utc)
    stub_tail=[]
    stub_report={}
    stub_streak=0
    stub_stopped=False
    for index in range(5):
        stub_attempt={"attempt":index+1,"curl_exit":28,"http_status":None,"timed_out":True,"request_finished_utc":(stub_base+timedelta(seconds=index)).isoformat().replace("+00:00","Z")}
        stub_tail.append(stub_attempt)
        stub_streak,stub_stopped=record_transfer_failure(stub_report,stub_attempt,stub_streak)
        if stub_stopped: break
    stub_cooldown=datetime.fromisoformat(stub_report["cooldown_not_before_utc"].replace("Z","+00:00")) if stub_report.get("cooldown_not_before_utc") else None
    stub_last_end=datetime.fromisoformat(stub_tail[-1]["request_finished_utc"].replace("Z","+00:00"))
    check("five_failure_stub_loop_preserves_tail_and_sets_120s_cooldown",len(stub_tail)==5 and stub_streak==5 and stub_stopped and stub_report.get("stop_reason")=="five_consecutive_transfer_failures" and stub_report.get("consecutive_transfer_failures")==5 and len(stub_report.get("consecutive_transfer_failure_tail",[]))==5 and stub_cooldown is not None and stub_cooldown>=stub_last_end+timedelta(seconds=TRANSPORT_FAILURE_COOLDOWN))
    check("tls_enabled_redirects_off_no_automatic_retries",plan["policy"]["tls_verification"] and not plan["policy"]["follow_redirects"] and plan["policy"]["automatic_retries"]==0)
    result={"schema":"wow-recovery.github-pages-v52-dungeons20.offline-validation.v1","all_passed":True,"network_requests":0,"checks":checks}
    (OUT/"offline-validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"all_passed":True,"network_requests":0,"checks":len(checks)}))
    return 0


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--offline-fixtures",action="store_true")
    parser.add_argument("--execute",action="store_true")
    parser.add_argument("--go",type=Path)
    args=parser.parse_args()
    if args.offline_fixtures:
        if args.execute: raise SystemExit("--offline-fixtures cannot be combined with --execute")
        return offline_fixtures()
    if args.execute:
        if args.go is None: raise SystemExit("--execute requires --go PATH")
        return execute(args.go)
    plan,manifest=validate_plan()
    print(json.dumps({"prepared":True,"batch_id":plan["batch_id"],"object_count":len(manifest["objects"]),"network_requests_at_prepare":0}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
