"""Compact, root-GO-gated verifier for six fixed GitHub Pages v53 objects."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PLAN, MANIFEST = OUT / "plan.json", OUT / "object-manifest.json"
FIXTURE, BINDINGS = OUT / "offline-validation.json", OUT / "input-bindings.json"
RUNTIME = OUT / "runtime"
TRANSPORT = ROOT / "research/continuous-recovery-20261022/network/archivecraft-dungeons01/archivecraft_dungeons01.py"
TRANSPORT_SHA = "7b95fa17bff6aa5245dc9fe45331652f02db5419c0e7ac14ff454af9d0fcad00"
RECEIPT = ROOT / "research/continuous-recovery-20261022/integration/v53-build-receipt.json"
RECEIPT_REL = "research/continuous-recovery-20261022/integration/v53-build-receipt.json"
RECEIPT_SHA = "c8f52998832fcb4add9a98496f67dae66b4fe80df3243fa04bec63d624a8ffb6"
BATCH = "github-pages-v53-changes06"
BASE = "https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/"
LOCAL = ".scratch/pages-resources-20261022-v53/"
COMMIT, ACTIONS_RUN = "f068318efedc86b6e7572213482f702b308ae362", "39758597461"
DISK_FLOOR, START_GAP, MAX_LOGICAL, MAX_ATTEMPTS = 11_005_853_696, 6.2, 6, 12
MAX_SECONDS, REQUEST_SECONDS, CONNECT_SECONDS = 400.0, 30.0, 10
TOTAL_CAP, OBJECT_CAP, COOLDOWN = 32 * 1024 * 1024, 16 * 1024 * 1024, 120
PATHS = [
    "__offline/related-guide-images/professions-page-title.png",
    "__offline/pages_runtime.js",
    "__offline/related-guide-images.json",
    "__offline/route-map.json",
    "burningcrusade/townhall/professions.html",
    "export-provenance.json",
]
MIMES = {
    PATHS[0]: ["image/png"], PATHS[1]: ["application/javascript", "text/javascript"],
    PATHS[2]: ["application/json"], PATHS[3]: ["application/json"],
    PATHS[4]: ["text/html"], PATHS[5]: ["application/json"],
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def runner():
    if not TRANSPORT.is_file() or sha(TRANSPORT) != TRANSPORT_SHA:
        raise RuntimeError("reviewed shared transport changed or is missing")
    spec = importlib.util.spec_from_file_location("archivecraft_shared_transport", TRANSPORT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load reviewed shared transport")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    mod.MAX_RESPONSE_BYTES = OBJECT_CAP
    return mod


def preflight() -> tuple[dict[str, Any], dict[str, Any], Any]:
    plan, manifest = read(PLAN), read(MANIFEST)
    if plan.get("mode") != "prepared" or plan.get("root_go_required") is not True or plan.get("batch_id") != BATCH:
        raise RuntimeError("plan is not prepared and root-GO-gated")
    if manifest.get("batch_id") != BATCH or plan.get("network_requests_at_prepare") != 0:
        raise RuntimeError("batch identity or preparation scope mismatch")
    expected_policy = {
        "maximum_logical_objects": MAX_LOGICAL, "maximum_http_attempts": MAX_ATTEMPTS,
        "maximum_batch_seconds": int(MAX_SECONDS), "maximum_request_seconds": int(REQUEST_SECONDS),
        "connect_timeout_seconds": CONNECT_SECONDS, "minimum_request_start_seconds": START_GAP,
        "maximum_total_body_bytes": TOTAL_CAP, "maximum_object_body_bytes": OBJECT_CAP,
        "maximum_response_bytes": OBJECT_CAP, "maximum_attempts_per_object": 2,
        "minimum_transport_failure_cooldown_seconds": COOLDOWN, "stop_http_statuses": [429, 503],
        "disk_floor_bytes": DISK_FLOOR, "process_proxy": "http://127.0.0.1:7890",
        "direct_first": True, "proxy_fallback_only_after_transfer_failure": True,
        "tls_verification": True, "follow_redirects": False, "automatic_retries": 0,
    }
    if plan.get("policy") != expected_policy or plan.get("target_base_url") != BASE:
        raise RuntimeError("fixed plan policy mismatch")
    if plan.get("pages_commit") != COMMIT or str(plan.get("actions_run")) != ACTIONS_RUN:
        raise RuntimeError("Pages commit or Actions run mismatch")
    if plan.get("transport_runner_sha256") != TRANSPORT_SHA or sha(TRANSPORT) != TRANSPORT_SHA:
        raise RuntimeError("shared runner hash mismatch")
    if sha(MANIFEST) != plan.get("object_manifest_sha256") or digest(manifest.get("objects")) != plan.get("object_set_sha256"):
        raise RuntimeError("manifest binding mismatch")
    objects = manifest.get("objects")
    if not isinstance(objects, list) or len(objects) != MAX_LOGICAL or [x.get("path") for x in objects] != PATHS:
        raise RuntimeError("fixed six-object roster mismatch")
    if manifest.get("target_base_url") != BASE:
        raise RuntimeError("manifest base URL mismatch")
    local_root = (ROOT / LOCAL.rstrip("/")).resolve()
    for obj in objects:
        path = obj["path"]
        if obj.get("url") != BASE + path or obj.get("accepted_mime_types") != MIMES[path] or obj.get("local_path") != LOCAL + path:
            raise RuntimeError(f"target or local path mismatch: {path}")
        local = (ROOT / obj["local_path"]).resolve()
        if not local.is_relative_to(local_root) or not local.is_file():
            raise RuntimeError(f"missing or out-of-scope local object: {path}")
        if local.stat().st_size != obj.get("local_bytes") or sha(local) != obj.get("local_sha256"):
            raise RuntimeError(f"local byte/hash mismatch: {path}")
        if not 0 < obj["local_bytes"] <= OBJECT_CAP:
            raise RuntimeError(f"object exceeds 16 MiB: {path}")
    if sum(x["local_bytes"] for x in objects) > TOTAL_CAP:
        raise RuntimeError("object set exceeds 32 MiB")
    if manifest.get("source", {}).get("build_receipt_path") != RECEIPT_REL or manifest.get("source", {}).get("build_receipt_sha256") != RECEIPT_SHA or sha(RECEIPT) != RECEIPT_SHA:
        raise RuntimeError("source build receipt binding mismatch")
    receipt_doc = read(RECEIPT)
    receipt = receipt_doc.get("result", {})
    if receipt.get("base_path") != "/WOW-Encyclopedia-Deployable-Archive/" or receipt_doc.get("network_requests") != 0 or receipt_doc.get("published") is not False or receipt.get("output") != str(ROOT / LOCAL.rstrip("/")):
        raise RuntimeError("source build receipt scope mismatch")
    mod = runner()
    if (mod.MIN_START_SECONDS, mod.REQUEST_SECONDS, mod.CONNECT_SECONDS) != (START_GAP, REQUEST_SECONDS, CONNECT_SECONDS):
        raise RuntimeError("reused transport timing constants changed")
    mod.require_disk("plan and source preflight")
    if RUNTIME.exists():
        raise RuntimeError("runtime already exists; refusing repeat batch")
    return plan, manifest, mod


def offline_mock_execute_smoke(plan: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    before = datetime.now(timezone.utc)
    calls = []
    with tempfile.TemporaryDirectory(prefix="offline-mock-execute-", dir=OUT) as temp:
        temp_root = Path(temp)
        go_path = temp_root / "mock-root-go.json"
        bindings = read(BINDINGS)
        expected = {key: bindings[key] for key in ("plan_sha256", "wrapper_sha256", "object_manifest_sha256", "offline_validation_sha256", "transport_runner_sha256", "source_build_receipt_sha256", "object_set_sha256")}
        go = {"accepted": True, "root_go": True, "batch_id": BATCH, "valid_until": (before + timedelta(minutes=5)).isoformat().replace("+00:00", "Z"), **expected, "input_bindings_sha256": sha(BINDINGS)}
        go_path.write_text(json.dumps(go), encoding="utf-8")

        def mock_attempt(target, attempt_no, use_proxy, last_start, batch_start, remaining, paths, *, cadence_seconds, batch_seconds):
            obj = next(item for item in manifest["objects"] if item["object_id"] == target["target_id"])
            now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            calls.append({"object_id": obj["object_id"], "transport": "proxy" if use_proxy else "direct"})
            return ({
                "attempt": attempt_no, "logical_request": target["target_id"], "url": target["url"],
                "transport": "proxy" if use_proxy else "direct", "request_started_utc": now,
                "request_finished_utc": now, "actual_start_interval_seconds": None,
                "effective_url": target["url"], "returncode": 0, "http_status": 200,
                "timed_out": False, "transport_failed": False, "response_cap_exceeded": False,
                "body_bytes": obj["local_bytes"], "body_sha256": obj["local_sha256"],
                "header_parse": {"content_type": obj["accepted_mime_types"][0]},
                "_body_file": "offline-mock-only",
            }, time.monotonic())

        isolated_runtime = temp_root / "runtime-smoke"
        with contextlib.redirect_stdout(io.StringIO()):
            exit_code = execute(go_path, runtime=isolated_runtime, attempt_fn=mock_attempt)
        private_path = isolated_runtime / "private" / "report.json"
        public_path = isolated_runtime / "object-match-summary.json"
        private = read(private_path)
        public = read(public_path)
        started = datetime.fromisoformat(private["started_utc"].replace("Z", "+00:00"))
        after = datetime.now(timezone.utc)
        if exit_code != 0 or len(calls) != 6 or any(item["transport"] != "direct" for item in calls):
            raise RuntimeError("offline mock execute did not make six direct stub attempts")
        if public.get("accepted") is not True or public.get("http_attempt_count") != 6 or not all(item["matches_local"] for item in public["objects"]):
            raise RuntimeError("offline mock execute summaries did not accept all six expected objects")
        if not private_path.is_file() or not public_path.is_file() or started.year < 2026 or started < before or started > after:
            raise RuntimeError("offline mock report path or UTC batch start is invalid")
        if RUNTIME.exists():
            raise RuntimeError("offline mock smoke unexpectedly created the real runtime")
        return {"passed": True, "network_requests": 0, "real_subprocess_calls": 0, "mock_attempts": len(calls), "all_six_matched": True, "private_report_written": True, "public_summary_written": True, "batch_started_utc": private["started_utc"], "isolated_runtime_removed": True, "real_runtime_absent": True}


def offline_validate() -> int:
    plan, manifest, mod = preflight()
    direct = mod.curl_command({"target_id": "fixture", "url": BASE + PATHS[0]}, use_proxy=False, headers=OUT / "h", body=OUT / "b", cookie=OUT / "c", max_time_seconds=REQUEST_SECONDS, remaining_body_bytes=OBJECT_CAP)
    proxy = mod.curl_command({"target_id": "fixture", "url": BASE + PATHS[0]}, use_proxy=True, headers=OUT / "h", body=OUT / "b", cookie=OUT / "c", max_time_seconds=REQUEST_SECONDS, remaining_body_bytes=OBJECT_CAP)
    if not ("--tlsv1.2" in direct and direct[direct.index("--proto") + 1] == "=https" and direct[direct.index("--retry") + 1] == "0" and direct[direct.index("--max-redirs") + 1] == "0" and direct[direct.index("--noproxy") + 1] == "*" and proxy[proxy.index("--proxy") + 1] == "http://127.0.0.1:7890"):
        raise RuntimeError("shared transport command policy check failed")
    mod.require_disk("before offline receipt")
    result = {"schema": "wow-recovery.github-pages-v53-changes06.offline-validation.v1", "batch_id": BATCH, "all_passed": True, "network_requests": 0, "objects": len(manifest["objects"]), "total_local_bytes": sum(x["local_bytes"] for x in manifest["objects"]), "maximum_object_bytes": max(x["local_bytes"] for x in manifest["objects"]), "transport_command_policy_checked": True}
    FIXTURE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_bindings(plan)
    try:
        result["offline_mock_execute_smoke"] = offline_mock_execute_smoke(plan, manifest)
    except Exception as exc:
        result["all_passed"] = False
        result["offline_mock_execute_smoke"] = {"passed": False, "error": f"{type(exc).__name__}: {exc}"}
    FIXTURE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_bindings(plan)
    mod.require_disk("after offline receipt")
    if result["all_passed"] is not True:
        raise RuntimeError("offline mock execute smoke failed; see offline-validation.json")
    print(json.dumps({"all_passed": True, "network_requests": 0, "objects": len(manifest["objects"]), "offline_validation_sha256": sha(FIXTURE), "input_bindings_sha256": sha(BINDINGS), "mock_attempts": result["offline_mock_execute_smoke"]["mock_attempts"]}))
    return 0


def write_bindings(plan: dict[str, Any]) -> None:
    BINDINGS.write_text(json.dumps({
        "schema": "wow-recovery.github-pages-v53-changes06.input-bindings.v1", "batch_id": BATCH,
        "plan_sha256": sha(PLAN), "wrapper_sha256": sha(Path(__file__)),
        "object_manifest_sha256": sha(MANIFEST), "offline_validation_sha256": sha(FIXTURE),
        "transport_runner_sha256": TRANSPORT_SHA, "source_build_receipt_sha256": RECEIPT_SHA,
        "object_set_sha256": plan["object_set_sha256"], "pages_commit": COMMIT, "actions_run": ACTIONS_RUN,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def mime(record: dict[str, Any]) -> str | None:
    value = record.get("header_parse", {}).get("content_type")
    return value.split(";", 1)[0].strip().lower() if isinstance(value, str) else None


def matches(obj: dict[str, Any], record: dict[str, Any]) -> bool:
    return record.get("returncode") == 0 and record.get("http_status") == 200 and mime(record) in obj["accepted_mime_types"] and record.get("body_bytes") == obj["local_bytes"] and record.get("body_sha256") == obj["local_sha256"] and record.get("effective_url") == obj["url"] and not record.get("timed_out") and not record.get("response_cap_exceeded") and not record.get("transport_failed")


def public_url(raw: str | None) -> str | None:
    try:
        parsed = urlsplit(raw or "")
        if parsed.scheme != "https" or parsed.hostname != "vvcchh0.github.io" or parsed.username or parsed.password:
            return None
        return urlunsplit(("https", parsed.hostname, parsed.path or "/", "", ""))
    except ValueError:
        return None


def execute(go_path: Path, *, runtime: Path = RUNTIME, attempt_fn=None) -> int:
    plan, manifest, mod = preflight()
    if not FIXTURE.is_file() or not BINDINGS.is_file() or read(FIXTURE).get("all_passed") is not True or read(FIXTURE).get("network_requests") != 0:
        raise RuntimeError("offline validation is not complete")
    binding = read(BINDINGS)
    expected = {"plan_sha256": sha(PLAN), "wrapper_sha256": sha(Path(__file__)), "object_manifest_sha256": sha(MANIFEST), "offline_validation_sha256": sha(FIXTURE), "transport_runner_sha256": TRANSPORT_SHA, "source_build_receipt_sha256": RECEIPT_SHA, "object_set_sha256": plan["object_set_sha256"]}
    if any(binding.get(key) != value for key, value in expected.items()):
        raise RuntimeError("input binding mismatch")
    if not go_path.is_file():
        raise RuntimeError("root GO missing")
    go = read(go_path)
    required_go = {**expected, "input_bindings_sha256": sha(BINDINGS)}
    if go.get("accepted") is not True or go.get("root_go") is not True or go.get("batch_id") != BATCH or any(go.get(key) != value for key, value in required_go.items()):
        raise RuntimeError("root GO authorization or hash binding mismatch")
    if not isinstance(go.get("valid_until"), str) or datetime.fromisoformat(go["valid_until"].replace("Z", "+00:00")) <= datetime.now(timezone.utc):
        raise RuntimeError("root GO expired or missing expiry")
    if runtime.exists():
        raise RuntimeError("refusing pre-existing execution runtime")
    mod.require_disk("before authorized batch")
    paths = mod.make_paths(runtime)
    runtime.mkdir(parents=True, exist_ok=False)
    paths.private.mkdir(parents=True, exist_ok=True)
    paths.raw.mkdir(parents=True, exist_ok=True)
    mod.MAX_RESPONSE_BYTES = OBJECT_CAP
    disk_start = mod.require_disk("batch start")
    batch_started_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    batch_start = time.monotonic()
    last_start = None
    attempts: list[dict[str, Any]] = []
    rows = [{"object_id": x["object_id"], "path": x["path"], "url": x["url"], "expected_bytes": x["local_bytes"], "expected_sha256": x["local_sha256"], "expected_mime": x["accepted_mime_types"], "attempts": [], "matches_local": False} for x in manifest["objects"]]
    total = 0
    streak = 0
    failure_tail: list[dict[str, Any]] = []
    stop, cooldown = "completed", None
    for obj, row in zip(manifest["objects"], rows):
        object_bytes = 0
        for use_proxy in (False, True):
            if len(attempts) >= MAX_ATTEMPTS or time.monotonic() - batch_start >= MAX_SECONDS:
                stop = "attempt_or_time_budget_exhausted"
                break
            remaining = min(TOTAL_CAP - total, OBJECT_CAP - object_bytes)
            if remaining <= 0:
                stop = "body_budget_exhausted"
                break
            mod.require_disk(f"before HTTP attempt {len(attempts) + 1}")
            try:
                call_attempt = attempt_fn or mod.run_attempt
                record, last_start = call_attempt({"target_id": obj["object_id"], "url": obj["url"]}, len(attempts) + 1, use_proxy, last_start, batch_start, remaining, paths, cadence_seconds=START_GAP, batch_seconds=MAX_SECONDS)
            except RuntimeError as exc:
                stop = "batch_time_budget_exhausted" if "window exhausted" in str(exc) else "request_precondition_failed"
                break
            record["object_id"] = obj["object_id"]
            attempts.append(record)
            row["attempts"].append(record)
            amount = record.get("body_bytes", 0)
            total += amount
            object_bytes += amount
            mod.require_disk(f"after HTTP attempt {len(attempts)}")
            reason, wait_until = mod.handle_status(record)
            if reason:
                stop, cooldown = reason, wait_until
            elif record.get("actual_start_interval_seconds") is not None and record["actual_start_interval_seconds"] < START_GAP:
                stop = "request_start_spacing_below_minimum"
            elif record.get("response_cap_exceeded") or total > TOTAL_CAP or object_bytes > OBJECT_CAP:
                stop = "response_or_body_cap_exceeded"
            elif record.get("transport_failed") or record.get("timed_out") or record.get("http_status") is None or record.get("returncode") not in (0, None):
                streak += 1
                failure_tail.append({key: record.get(key) for key in ("attempt", "object_id", "transport", "request_started_utc", "request_finished_utc", "http_status", "returncode", "timed_out")})
                failure_tail = failure_tail[-5:]
                if streak >= 5:
                    stop = "five_consecutive_transfer_failures"
                    cooldown = mod.cooldown_from_record(record, COOLDOWN)
            else:
                streak, failure_tail = 0, []
                row["matches_local"] = matches(obj, record)
            if stop != "completed":
                break
            failed = bool(record.get("transport_failed") or record.get("timed_out") or record.get("http_status") is None or record.get("returncode") not in (0, None))
            if failed and not use_proxy:
                continue
            break
        if stop != "completed":
            break
    finished = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    complete = all(row["attempts"] for row in rows)
    accepted = complete and all(row["matches_local"] for row in rows) and stop == "completed"
    private = {"schema": "wow-recovery.github-pages-v53-changes06.private-report.v1", "batch_id": BATCH, "go_sha256": sha(go_path), "started_utc": batch_started_utc, "finished_utc": finished, "stop_reason": stop, "cooldown_not_before_utc": cooldown, "attempt_count": len(attempts), "total_response_body_bytes": total, "consecutive_transfer_failures": streak, "consecutive_transfer_failure_tail": failure_tail, "attempts": attempts, "objects": rows, "raw_http_and_cookies_private": True}
    public_rows = []
    for row in rows:
        final = row["attempts"][-1] if row["attempts"] else {}
        public_rows.append({"object_id": row["object_id"], "path": row["path"], "url": public_url(row["url"]), "expected_bytes": row["expected_bytes"], "expected_sha256": row["expected_sha256"], "expected_mime": row["expected_mime"], "attempts": [{"transport": a.get("transport"), "started_utc": a.get("request_started_utc"), "finished_utc": a.get("request_finished_utc"), "start_interval_seconds": a.get("actual_start_interval_seconds"), "status": a.get("http_status"), "effective_url": public_url(a.get("effective_url")), "bytes": a.get("body_bytes"), "sha256": a.get("body_sha256"), "mime": mime(a)} for a in row["attempts"]], "observed_bytes": final.get("body_bytes"), "observed_sha256": final.get("body_sha256"), "observed_mime": mime(final) if final else None, "matches_local": row["matches_local"]})
    public = {"schema": "wow-recovery.github-pages-v53-changes06.public-summary.v1", "batch_id": BATCH, "pages_commit": COMMIT, "actions_run": ACTIONS_RUN, "started_utc": private["started_utc"], "finished_utc": finished, "complete": complete, "accepted": accepted, "stop_reason": stop, "cooldown_not_before_utc": cooldown, "http_attempt_count": len(attempts), "direct_attempt_count": sum(a.get("transport") == "direct" for a in attempts), "proxy_attempt_count": sum(a.get("transport") == "proxy" for a in attempts), "total_response_body_bytes": total, "disk_free_before_bytes": disk_start, "disk_free_after_bytes": mod.require_disk("batch finish"), "consecutive_transfer_failure_tail": failure_tail, "objects": public_rows, "raw_http_and_cookies_private": True}
    mod.require_disk("before execution summaries")
    report_path = paths.private / "report.json"
    summary_path = runtime / "object-match-summary.json"
    report_path.write_text(json.dumps(private, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    mod.require_disk("after execution summaries")
    print(json.dumps({"accepted": accepted, "matches": sum(bool(x["matches_local"]) for x in rows), "http_attempts": len(attempts), "direct_attempts": public["direct_attempt_count"], "proxy_attempts": public["proxy_attempt_count"], "stop_reason": stop}))
    return 0 if accepted else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline-validate", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--go", type=Path)
    args = parser.parse_args()
    if args.offline_validate and args.execute:
        raise SystemExit("choose only one mode")
    if args.execute:
        if args.go is None:
            raise SystemExit("--execute requires --go PATH")
        return execute(args.go)
    if args.offline_validate:
        if args.go is not None:
            raise SystemExit("--go is only valid with --execute")
        return offline_validate()
    if args.go is not None:
        raise SystemExit("--go is only valid with --execute")
    plan, manifest, _ = preflight()
    print(json.dumps({"prepared": True, "batch_id": plan["batch_id"], "objects": len(manifest["objects"]), "network_requests_at_prepare": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
