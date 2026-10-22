#!/usr/bin/env python3
"""Prepare a receipt-bound manifest or run one root-GO-authorized v56 Pages check."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable
from urllib.parse import quote, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PLAN, MANIFEST = OUT / "plan.json", OUT / "object-manifest.json"
FIXTURE, BINDINGS, RUNTIME = OUT / "offline-validation.json", OUT / "input-bindings.json", OUT / "runtime"
EXPORT_REL = "research/continuous-recovery-20261022/root-v56-export-acceptance.json"
BROWSER_REL = "research/continuous-recovery-20261022/root-v56-browser-acceptance.json"
EXPORT_PATH, BROWSER_PATH = ROOT / EXPORT_REL, ROOT / BROWSER_REL
BASE = "https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/"
BATCH = "github-pages-v56-changes22"
GO_SCHEMA = "wow-root-github-pages-v56-changes22-go/v1"
CORE_REL = "research/continuous-recovery-20261022/network/github-pages-v53-changes06/verify_pages_v53_changes06.py"
CORE_PATH = ROOT / CORE_REL
CORE_SHA = "deddfab9dad1c3d1e472d7b0ad6454746c91b9707265e6f9dd1093ecdc019a70"
TRANSPORT_REL = "research/continuous-recovery-20261022/network/archivecraft-dungeons01/archivecraft_dungeons01.py"
TRANSPORT_PATH = ROOT / TRANSPORT_REL
TRANSPORT_SHA = "7b95fa17bff6aa5245dc9fe45331652f02db5419c0e7ac14ff454af9d0fcad00"

DISK_FLOOR = 11_005_853_696
SCHEDULE_TARGET_SECONDS, MIN_ACTUAL_SECONDS = 6.4, 5.0
TRANSPORT_DEFAULT_SECONDS = 6.2
MAX_LOGICAL, MAX_ATTEMPTS, MAX_SECONDS = 22, 44, 20 * 60
REQUEST_SECONDS, CONNECT_SECONDS = 30, 10
TOTAL_CAP = OBJECT_CAP = 64 * 1024 * 1024
COOLDOWN, STOP_STATUSES = 120, [429, 503]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40,64}$")
MIME_BY_SUFFIX = {
    ".gif": ["image/gif"], ".html": ["text/html"], ".jpeg": ["image/jpeg"],
    ".jpg": ["image/jpeg"], ".js": ["application/javascript", "text/javascript"],
    ".json": ["application/json"], ".png": ["image/png"], ".svg": ["image/svg+xml"],
    ".webp": ["image/webp"],
}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def canonical_sha(value: Any) -> str:
    return sha_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def safe_site_path(raw: Any) -> str:
    if not isinstance(raw, str) or not raw or "\\" in raw or raw.startswith("/") or ":" in raw:
        raise RuntimeError(f"unsafe site-relative path: {raw!r}")
    p = PurePosixPath(raw)
    if p.as_posix() != raw or any(x in ("", ".", "..") for x in p.parts):
        raise RuntimeError(f"non-canonical site-relative path: {raw!r}")
    return raw


def policy() -> dict[str, Any]:
    return {
        "max_logical_objects": MAX_LOGICAL, "max_http_attempts": MAX_ATTEMPTS,
        "max_batch_seconds": MAX_SECONDS, "request_timeout_seconds": REQUEST_SECONDS,
        "connect_timeout_seconds": CONNECT_SECONDS,
        "request_start_schedule_target_seconds": SCHEDULE_TARGET_SECONDS,
        "minimum_actual_start_interval_seconds": MIN_ACTUAL_SECONDS,
        "reused_transport_default_cadence_seconds": TRANSPORT_DEFAULT_SECONDS,
        "max_total_body_bytes": TOTAL_CAP, "max_object_body_bytes": OBJECT_CAP,
        "max_attempts_per_object": 2, "max_consecutive_transfer_failures": 5,
        "min_transfer_failure_cooldown_seconds": COOLDOWN, "stop_statuses": STOP_STATUSES,
        "disk_floor_bytes": DISK_FLOOR, "direct_first": True,
        "process_proxy": "http://127.0.0.1:7890", "proxy_only_after_transfer_failure": True,
        "tls_verification": True, "redirects": False, "automatic_retries": 0,
    }


def _read_receipts() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], Path]:
    if not EXPORT_PATH.is_file() or not BROWSER_PATH.is_file():
        raise RuntimeError("root v56 export/browser receipts are not available yet")
    export, browser = read_json(EXPORT_PATH), read_json(BROWSER_PATH)
    if export.get("accepted") is not True or not re.fullmatch(
        r"wow-root-v56-export-acceptance/v[0-9]+", str(export.get("schema", ""))
    ):
        raise RuntimeError("root v56 export acceptance is missing or not accepted")
    if (browser.get("schema") != "wow-root-final-browser-acceptance/v1"
            or browser.get("accepted") is not True or browser.get("version") != "v56"):
        raise RuntimeError("root browser acceptance is missing or not accepted for v56")
    local = export.get("local_site")
    if not isinstance(local, str) or browser.get("local_site") != local:
        raise RuntimeError("export/browser receipts must name the same local_site")
    safe_site_path(local)
    provenance = export.get("export_provenance_sha256")
    if not isinstance(provenance, str) or not SHA256_RE.fullmatch(provenance):
        raise RuntimeError("accepted export provenance SHA-256 is invalid")
    if browser.get("export_provenance_sha256") != provenance:
        raise RuntimeError("browser receipt provenance differs from export acceptance")
    if (browser.get("external_requests") != [] or browser.get("page_errors") != []
            or browser.get("asset_fulfillments") != 0):
        raise RuntimeError("browser receipt does not meet the accepted offline-browse boundary")
    if export.get("all_actual_file_hashes_match_provenance") is not True:
        raise RuntimeError("export acceptance does not attest all actual file hashes")
    site = (ROOT / local).resolve(strict=True)
    if not site.is_dir() or not site.is_relative_to(ROOT.resolve()):
        raise RuntimeError("accepted local site escapes workspace or is not a directory")
    prov_path = site / "export-provenance.json"
    if not prov_path.is_file() or prov_path.is_symlink() or sha(prov_path) != provenance:
        raise RuntimeError("local export provenance differs from receipt")
    change_rows = export.get("online_changes_from_v55")
    if not isinstance(change_rows, list) or len(change_rows) != MAX_LOGICAL:
        raise RuntimeError("root export receipt must supply exactly 22 online_changes_from_v55 rows")
    objects, seen = [], set()
    for i, row in enumerate(change_rows, 1):
        if not isinstance(row, dict):
            raise RuntimeError(f"malformed accepted change row {i}")
        path = safe_site_path(row.get("path"))
        if path in seen:
            raise RuntimeError(f"duplicate accepted path: {path}")
        seen.add(path)
        digest, length = row.get("sha256"), row.get("bytes")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest) or not isinstance(length, int) or length <= 0:
            raise RuntimeError(f"invalid accepted digest/length: {path}")
        if length > OBJECT_CAP:
            raise RuntimeError(f"accepted object exceeds per-object cap: {path}")
        types = MIME_BY_SUFFIX.get(PurePosixPath(path).suffix.lower())
        if types is None:
            raise RuntimeError(f"no reviewed MIME mapping for accepted path: {path}")
        local_path = site / PurePosixPath(path)
        cursor = site
        linked_component = False
        for component in PurePosixPath(path).parts:
            cursor = cursor / component
            linked_component = linked_component or cursor.is_symlink()
        if linked_component or not local_path.is_file() or not local_path.resolve().is_relative_to(site):
            raise RuntimeError(f"accepted local file missing, linked, or outside site: {path}")
        if local_path.stat().st_size != length or sha(local_path) != digest:
            raise RuntimeError(f"local bytes/hash differ from accepted receipt: {path}")
        objects.append({
            "object_id": f"object-{i:03d}-{sha_bytes(path.encode('utf-8'))[:10]}",
            "path": path, "url": BASE + quote(path, safe="/-._~"),
            "local_path": f"{local}/{path}", "local_bytes": length,
            "local_sha256": digest, "accepted_mime_types": types,
        })
    if sum(x["local_bytes"] for x in objects) > TOTAL_CAP:
        raise RuntimeError("exact 22-object roster exceeds total response-byte cap")
    return export, browser, objects, site


def _check_deployment(commit: str, run: str, export: dict[str, Any], browser: dict[str, Any]) -> None:
    if not COMMIT_RE.fullmatch(commit) or not run.isdigit():
        raise RuntimeError("Pages commit must be a full lowercase SHA and Actions run a numeric id")
    for receipt in (export, browser):
        if receipt.get("pages_commit") is not None and receipt["pages_commit"] != commit:
            raise RuntimeError("Pages commit differs from root acceptance receipt")
        if receipt.get("actions_run") is not None and str(receipt["actions_run"]) != run:
            raise RuntimeError("Actions run differs from root acceptance receipt")


def _object_set_sha(objects: list[dict[str, Any]]) -> str:
    return canonical_sha([{"path": x["path"], "sha256": x["local_sha256"], "bytes": x["local_bytes"]} for x in objects])


def _bindings(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "wow-recovery.github-pages-v56-changes22.input-bindings.v1",
        "batch_id": BATCH, "plan_sha256": sha(PLAN), "wrapper_sha256": sha(Path(__file__)),
        "object_manifest_sha256": sha(MANIFEST), "offline_validation_sha256": sha(FIXTURE),
        "shared_v53_wrapper_sha256": CORE_SHA, "transport_runner_sha256": TRANSPORT_SHA,
        "export_acceptance_sha256": sha(EXPORT_PATH), "browser_acceptance_sha256": sha(BROWSER_PATH),
        "object_set_sha256": plan["object_set_sha256"], "export_provenance_sha256": plan["export_provenance_sha256"],
        "pages_commit": plan["pages_commit"], "actions_run": plan["actions_run"],
    }


def prepare(commit: str, run: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if not FIXTURE.is_file() or read_json(FIXTURE).get("all_passed") is not True:
        raise RuntimeError("run --offline-validate before receipt-bound preparation")
    if any(p.exists() for p in (PLAN, MANIFEST, BINDINGS)):
        raise RuntimeError("plan/manifest/bindings already exist; refusing overwrite")
    export, browser, objects, _site = _read_receipts()
    _check_deployment(commit, run, export, browser)
    source = {
        "change_list": "root export receipt online_changes_from_v55",
        "local_site": export["local_site"], "export_acceptance_path": EXPORT_REL,
        "export_acceptance_sha256": sha(EXPORT_PATH), "browser_acceptance_path": BROWSER_REL,
        "browser_acceptance_sha256": sha(BROWSER_PATH), "export_provenance_sha256": export["export_provenance_sha256"],
        "pages_commit": commit, "actions_run": run,
    }
    manifest = {"schema": "wow-recovery.github-pages-v56-changes22.object-manifest.v1",
                "batch_id": BATCH, "target_base_url": BASE, "source": source, "objects": objects}
    write_json(MANIFEST, manifest)
    plan = {
        "schema": "wow-recovery.github-pages-v56-changes22.plan.v1", "batch_id": BATCH,
        "mode": "prepared", "root_go_required": True, "network_requests_at_prepare": 0,
        "pages_commit": commit, "actions_run": run, "target_base_url": BASE,
        "local_site": export["local_site"], "object_count": MAX_LOGICAL,
        "object_total_bytes": sum(x["local_bytes"] for x in objects),
        "object_manifest_sha256": sha(MANIFEST), "object_set_sha256": _object_set_sha(objects),
        "export_acceptance_path": EXPORT_REL, "export_acceptance_sha256": sha(EXPORT_PATH),
        "browser_acceptance_path": BROWSER_REL, "browser_acceptance_sha256": sha(BROWSER_PATH),
        "export_provenance_sha256": export["export_provenance_sha256"],
        "shared_v53_wrapper_path": CORE_REL, "shared_v53_wrapper_sha256": CORE_SHA,
        "transport_runner_path": TRANSPORT_REL, "transport_runner_sha256": TRANSPORT_SHA,
        "policy": policy(),
        "go_required_fields": ["plan_sha256", "wrapper_sha256", "object_manifest_sha256",
            "offline_validation_sha256", "input_bindings_sha256", "shared_v53_wrapper_sha256",
            "transport_runner_sha256", "export_acceptance_sha256", "browser_acceptance_sha256",
            "object_set_sha256", "export_provenance_sha256", "pages_commit", "actions_run"],
        "raw_handling": "HTTP headers, bodies, and cookies private under runtime/private/raw; public summary is curated",
    }
    write_json(PLAN, plan)
    write_json(BINDINGS, _bindings(plan))
    return plan, manifest


def _load_transport():
    if not CORE_PATH.is_file() or sha(CORE_PATH) != CORE_SHA:
        raise RuntimeError("pinned v53 wrapper changed")
    if not TRANSPORT_PATH.is_file() or sha(TRANSPORT_PATH) != TRANSPORT_SHA:
        raise RuntimeError("pinned shared transport changed")
    spec = importlib.util.spec_from_file_location("accepted_v53_pages_core", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load pinned v53 wrapper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    transport = module.runner()
    if (transport.MIN_START_SECONDS, transport.REQUEST_SECONDS, transport.CONNECT_SECONDS) != (
        TRANSPORT_DEFAULT_SECONDS, REQUEST_SECONDS, CONNECT_SECONDS
    ):
        raise RuntimeError("reused transport defaults changed")
    transport.MAX_RESPONSE_BYTES = OBJECT_CAP
    return transport


def preflight() -> tuple[dict[str, Any], dict[str, Any], Any]:
    if any(not p.is_file() for p in (PLAN, MANIFEST, BINDINGS, FIXTURE)):
        raise RuntimeError("prepared plan, manifest, bindings, and offline fixture are required")
    plan, manifest, binding, fixture = map(read_json, (PLAN, MANIFEST, BINDINGS, FIXTURE))
    if (plan.get("schema") != "wow-recovery.github-pages-v56-changes22.plan.v1"
            or plan.get("mode") != "prepared" or plan.get("root_go_required") is not True
            or plan.get("network_requests_at_prepare") != 0 or plan.get("batch_id") != BATCH):
        raise RuntimeError("plan is not prepared and root-GO-gated")
    if manifest.get("schema") != "wow-recovery.github-pages-v56-changes22.object-manifest.v1" or manifest.get("batch_id") != BATCH:
        raise RuntimeError("manifest identity mismatch")
    if plan.get("policy") != policy() or plan.get("target_base_url") != BASE or manifest.get("target_base_url") != BASE:
        raise RuntimeError("fixed policy or Pages target mismatch")
    if plan.get("object_manifest_sha256") != sha(MANIFEST) or fixture.get("all_passed") is not True or fixture.get("network_requests") != 0:
        raise RuntimeError("manifest/offline fixture binding mismatch")
    export, browser, expected, _site = _read_receipts()
    _check_deployment(str(plan.get("pages_commit", "")), str(plan.get("actions_run", "")), export, browser)
    if manifest.get("objects") != expected or len(expected) != MAX_LOGICAL:
        raise RuntimeError("manifest does not match the exact accepted 22-row roster")
    if plan.get("object_set_sha256") != _object_set_sha(expected) or plan.get("object_count") != MAX_LOGICAL:
        raise RuntimeError("object-set digest/count mismatch")
    for field, path in (("export_acceptance_sha256", EXPORT_PATH), ("browser_acceptance_sha256", BROWSER_PATH)):
        if plan.get(field) != sha(path) or manifest.get("source", {}).get(field) != sha(path):
            raise RuntimeError(f"root receipt binding mismatch: {field}")
    provenance = export["export_provenance_sha256"]
    if plan.get("export_provenance_sha256") != provenance or manifest.get("source", {}).get("export_provenance_sha256") != provenance:
        raise RuntimeError("provenance binding mismatch")
    if (manifest.get("source", {}).get("pages_commit") != plan.get("pages_commit")
            or manifest.get("source", {}).get("actions_run") != plan.get("actions_run")):
        raise RuntimeError("Pages commit/Actions run binding mismatch")
    if binding != _bindings(plan):
        raise RuntimeError("input binding values changed")
    _require_runtime_absent(RUNTIME)
    transport = _load_transport()
    transport.require_disk("v56 source preflight")
    return plan, manifest, transport


def mime(record: dict[str, Any]) -> str | None:
    raw = record.get("header_parse", {}).get("content_type")
    return raw.split(";", 1)[0].strip().lower() if isinstance(raw, str) else None


def _matches(obj: dict[str, Any], record: dict[str, Any]) -> bool:
    return (record.get("returncode") == 0 and record.get("http_status") == 200
            and mime(record) in obj["accepted_mime_types"] and record.get("body_bytes") == obj["local_bytes"]
            and record.get("body_sha256") == obj["local_sha256"] and record.get("effective_url") == obj["url"]
            and not record.get("timed_out") and not record.get("response_cap_exceeded")
            and not record.get("transport_failed"))


def _public_url(raw: str | None) -> str | None:
    try:
        p = urlsplit(raw or "")
        if p.scheme != "https" or p.hostname != "vvcchh0.github.io" or p.username or p.password:
            return None
        return urlunsplit(("https", p.hostname, p.path or "/", "", ""))
    except ValueError:
        return None


def _transfer_failed(rec: dict[str, Any]) -> bool:
    return bool(rec.get("transport_failed") or rec.get("timed_out") or rec.get("http_status") is None
                or rec.get("returncode") not in (0, None))


def _budget_stop(count: int, elapsed: float) -> str | None:
    if count >= MAX_ATTEMPTS:
        return "attempt_budget_exhausted"
    if elapsed >= MAX_SECONDS:
        return "batch_time_budget_exhausted"
    return None


def _require_runtime_absent(path: Path) -> None:
    if path.exists():
        raise RuntimeError("runtime already exists; refusing repeated execution")


def _interval_stop(record: dict[str, Any]) -> str | None:
    interval = record.get("actual_start_interval_seconds")
    return "actual_request_start_below_five_second_hard_minimum" if interval is not None and interval < MIN_ACTUAL_SECONDS else None


def _should_proxy_after(record: dict[str, Any], used_proxy: bool) -> bool:
    return _transfer_failed(record) and not used_proxy


def _remaining_body(total: int, object_bytes: int) -> int:
    return min(TOTAL_CAP - total, OBJECT_CAP - object_bytes)


def _append_failure_tail(tail: list[dict[str, Any]], record: dict[str, Any]) -> list[dict[str, Any]]:
    keys = ("attempt", "object_id", "transport", "request_started_utc", "request_finished_utc",
            "http_status", "returncode", "timed_out")
    return (tail + [{key: record.get(key) for key in keys}])[-5:]


def _go_values(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "plan_sha256": sha(PLAN), "wrapper_sha256": sha(Path(__file__)),
        "object_manifest_sha256": sha(MANIFEST), "offline_validation_sha256": sha(FIXTURE),
        "input_bindings_sha256": sha(BINDINGS), "shared_v53_wrapper_sha256": CORE_SHA,
        "transport_runner_sha256": TRANSPORT_SHA, "export_acceptance_sha256": sha(EXPORT_PATH),
        "browser_acceptance_sha256": sha(BROWSER_PATH), "object_set_sha256": plan["object_set_sha256"],
        "export_provenance_sha256": plan["export_provenance_sha256"],
        "pages_commit": plan["pages_commit"], "actions_run": plan["actions_run"],
    }


def execute(go_path: Path) -> dict[str, Any]:
    plan, manifest, transport = preflight()
    if not go_path.is_file():
        raise RuntimeError("root GO file is missing")
    go = read_json(go_path)
    if (go.get("schema") != GO_SCHEMA or go.get("accepted") is not True or go.get("root_go") is not True
            or go.get("batch_id") != BATCH or any(go.get(k) != v for k, v in _go_values(plan).items())):
        raise RuntimeError("GO does not bind approval to every v56 input")
    try:
        expires = datetime.fromisoformat(str(go.get("valid_until", "")).replace("Z", "+00:00"))
    except ValueError as exc:
        raise RuntimeError("GO expiry is invalid") from exc
    if expires.tzinfo is None or expires <= datetime.now(timezone.utc):
        raise RuntimeError("GO is expired")
    _require_runtime_absent(RUNTIME)
    transport.require_disk("before v56 batch runtime")
    paths = transport.make_paths(RUNTIME)
    RUNTIME.mkdir(parents=True, exist_ok=False)
    paths.private.mkdir(parents=True, exist_ok=True)
    paths.raw.mkdir(parents=True, exist_ok=True)
    transport.MAX_RESPONSE_BYTES = OBJECT_CAP
    disk_before = transport.require_disk("v56 batch start")
    started_utc = datetime.now(timezone.utc)
    batch_start = time.monotonic()
    attempts, rows = [], [{
        "object_id": x["object_id"], "path": x["path"], "url": x["url"],
        "expected_bytes": x["local_bytes"], "expected_sha256": x["local_sha256"],
        "expected_mime": x["accepted_mime_types"], "attempts": [], "matches_local": False,
    } for x in manifest["objects"]]
    total, streak, failure_tail = 0, 0, []
    stop, cooldown_until, last_start = "completed", None, None
    for obj, row in zip(manifest["objects"], rows):
        object_bytes = 0
        for use_proxy in (False, True):
            budget = _budget_stop(len(attempts), time.monotonic() - batch_start)
            if budget:
                stop = budget
                break
            remaining = _remaining_body(total, object_bytes)
            if remaining <= 0:
                stop = "body_budget_exhausted"
                break
            transport.require_disk(f"before HTTP attempt {len(attempts) + 1}")
            try:
                record, last_start = transport.run_attempt(
                    {"target_id": obj["object_id"], "url": obj["url"]}, len(attempts) + 1,
                    use_proxy, last_start, batch_start, remaining, paths,
                    cadence_seconds=SCHEDULE_TARGET_SECONDS, batch_seconds=MAX_SECONDS,
                )
            except RuntimeError as exc:
                stop = "batch_time_budget_exhausted" if "window exhausted" in str(exc) else "request_precondition_failed"
                break
            if not isinstance(record, dict):
                stop = "malformed_attempt_record"
                break
            record["object_id"] = obj["object_id"]
            attempts.append(record)
            row["attempts"].append(record)
            body_bytes = record.get("body_bytes", 0)
            if not isinstance(body_bytes, int) or body_bytes < 0:
                stop = "malformed_body_length"
                break
            total += body_bytes
            object_bytes += body_bytes
            transport.require_disk(f"after HTTP attempt {len(attempts)}")
            status_stop, wait_until = transport.handle_status(record)
            if status_stop:
                stop, cooldown_until = status_stop, wait_until
            elif _interval_stop(record):
                stop = _interval_stop(record)
            elif record.get("response_cap_exceeded") or total > TOTAL_CAP or object_bytes > OBJECT_CAP:
                stop = "response_or_body_cap_exceeded"
            elif _transfer_failed(record):
                streak += 1
                failure_tail = _append_failure_tail(failure_tail, record)
                if streak >= 5:
                    stop = "five_consecutive_transfer_failures"
                    cooldown_until = transport.cooldown_from_record(record, COOLDOWN)
            else:
                streak, failure_tail = 0, []
                row["matches_local"] = _matches(obj, record)
            if stop != "completed":
                break
            if _should_proxy_after(record, use_proxy):
                continue
            break
        if stop != "completed":
            break
    finished_utc = datetime.now(timezone.utc)
    complete = all(row["attempts"] for row in rows)
    accepted = complete and all(row["matches_local"] for row in rows) and stop == "completed"
    common = {
        "batch_id": BATCH, "pages_commit": plan["pages_commit"], "actions_run": plan["actions_run"],
        "export_acceptance_sha256": sha(EXPORT_PATH), "browser_acceptance_sha256": sha(BROWSER_PATH),
        "export_provenance_sha256": plan["export_provenance_sha256"],
        "schedule_target_seconds": SCHEDULE_TARGET_SECONDS, "minimum_actual_request_start_seconds": MIN_ACTUAL_SECONDS,
        "started_utc": started_utc.isoformat().replace("+00:00", "Z"),
        "finished_utc": finished_utc.isoformat().replace("+00:00", "Z"),
        "elapsed_seconds": max(0.0, time.monotonic() - batch_start), "stop_reason": stop,
        "cooldown_not_before_utc": cooldown_until, "http_attempt_count": len(attempts),
        "total_response_body_bytes": total, "consecutive_transfer_failures": streak,
        "consecutive_transfer_failure_tail": failure_tail, "raw_http_and_cookies_private": True,
    }
    private = {"schema": "wow-recovery.github-pages-v56-changes22.private-report.v1", **common,
               "go_sha256": sha(go_path), "attempts": attempts, "objects": rows}
    public_rows = []
    for row in rows:
        last = row["attempts"][-1] if row["attempts"] else {}
        public_rows.append({
            "object_id": row["object_id"], "path": row["path"], "url": _public_url(row["url"]),
            "expected_bytes": row["expected_bytes"], "expected_sha256": row["expected_sha256"],
            "expected_mime": row["expected_mime"],
            "attempts": [{"transport": a.get("transport"), "started_utc": a.get("request_started_utc"),
                "finished_utc": a.get("request_finished_utc"), "start_interval_seconds": a.get("actual_start_interval_seconds"),
                "status": a.get("http_status"), "effective_url": _public_url(a.get("effective_url")),
                "bytes": a.get("body_bytes"), "sha256": a.get("body_sha256"), "mime": mime(a)} for a in row["attempts"]],
            "observed_bytes": last.get("body_bytes"), "observed_sha256": last.get("body_sha256"),
            "observed_mime": mime(last) if last else None, "matches_local": row["matches_local"],
        })
    public = {"schema": "wow-recovery.github-pages-v56-changes22.public-summary.v1", **common,
        "complete": complete, "accepted": accepted,
        "direct_attempt_count": sum(a.get("transport") == "direct" for a in attempts),
        "proxy_attempt_count": sum(a.get("transport") == "proxy" for a in attempts),
        "disk_free_before_bytes": disk_before, "disk_free_after_bytes": transport.require_disk("v56 finish"),
        "objects": public_rows}
    transport.require_disk("before v56 summary writes")
    write_json(paths.private / "report.json", private)
    write_json(RUNTIME / "object-match-summary.json", public)
    transport.require_disk("after v56 summary writes")
    return {"accepted": accepted, "matches": sum(bool(x["matches_local"]) for x in rows),
            "http_attempts": len(attempts), "direct_attempts": public["direct_attempt_count"],
            "proxy_attempts": public["proxy_attempt_count"], "stop_reason": stop, "runtime": str(RUNTIME)}


def _assert_transport_cli(transport: Any) -> None:
    direct = transport.curl_command({"target_id": "fixture", "url": BASE + "offline"}, use_proxy=False,
        headers=OUT / "fixture.headers", body=OUT / "fixture.body", cookie=OUT / "fixture.cookie",
        max_time_seconds=REQUEST_SECONDS, remaining_body_bytes=OBJECT_CAP)
    proxy = transport.curl_command({"target_id": "fixture", "url": BASE + "offline"}, use_proxy=True,
        headers=OUT / "fixture.headers", body=OUT / "fixture.body", cookie=OUT / "fixture.cookie",
        max_time_seconds=REQUEST_SECONDS, remaining_body_bytes=OBJECT_CAP)
    if ("--tlsv1.2" not in direct or direct[direct.index("--proto") + 1] != "=https"
        or direct[direct.index("--retry") + 1] != "0" or direct[direct.index("--max-redirs") + 1] != "0"
        or direct[direct.index("--noproxy") + 1] != "*"
        or proxy[proxy.index("--proxy") + 1] != "http://127.0.0.1:7890"):
        raise RuntimeError("reused transport differs from direct-first/TLS/no-redirect/no-retry policy")


def offline_validate() -> int:
    if RUNTIME.exists():
        raise RuntimeError("production runtime exists; refusing offline validation")
    transport = _load_transport()
    _assert_transport_cli(transport)
    now = datetime.now(timezone.utc)
    failure_rows = [{"request_finished_utc": (now + timedelta(seconds=i)).isoformat().replace("+00:00", "Z")} for i in range(5)]
    tail = []
    for index, row in enumerate([*failure_rows, {"request_finished_utc": now.isoformat().replace("+00:00", "Z")}], 1):
        tail = _append_failure_tail(tail, {"attempt": index, **row})
    synthetic_roster = [{"path": f"synthetic/icons/{i:02d}.png"} for i in range(MAX_LOGICAL)]
    status_stops = {}
    for status in STOP_STATUSES:
        reason, not_before = transport.handle_status({
            "http_status": status, "request_finished_utc": now.isoformat().replace("+00:00", "Z"),
            "retry_after": None,
        })
        stop_at = datetime.fromisoformat(str(not_before).replace("Z", "+00:00"))
        status_stops[str(status)] = reason == f"endpoint_status_{status}" and stop_at >= now + timedelta(seconds=COOLDOWN)
    with tempfile.TemporaryDirectory(prefix="runtime-guard-fixture-", dir=OUT) as temp_name:
        guard_runtime = Path(temp_name) / "runtime"
        guard_runtime.mkdir()
        try:
            _require_runtime_absent(guard_runtime)
            runtime_guard_passed = False
        except RuntimeError:
            runtime_guard_passed = True
    cooldown = datetime.fromisoformat(failure_rows[-1]["request_finished_utc"].replace("Z", "+00:00")) + timedelta(seconds=COOLDOWN)
    checks = {
        "schedule_target_seconds": SCHEDULE_TARGET_SECONDS,
        "hard_minimum_seconds": MIN_ACTUAL_SECONDS,
        "6p39_allowed": _interval_stop({"actual_start_interval_seconds": 6.39}) is None,
        "4p99_stops": _interval_stop({"actual_start_interval_seconds": 4.99}) is not None,
        "exact_logical_target_count": MAX_LOGICAL,
        "synthetic_roster_count": len(synthetic_roster),
        "maximum_http_attempts": MAX_ATTEMPTS,
        "max_attempts_support_direct_and_proxy_per_object": MAX_ATTEMPTS == 2 * MAX_LOGICAL,
        "batch_time_cap_seconds": MAX_SECONDS,
        "total_and_per_object_body_caps": [TOTAL_CAP, OBJECT_CAP],
        "five_failure_tail_count": len(tail),
        "five_failure_cooldown_seconds": (cooldown - datetime.fromisoformat(failure_rows[-1]["request_finished_utc"].replace("Z", "+00:00"))).total_seconds(),
        "429_503_immediate_stop_and_cooldown": all(status_stops.values()),
        "proxy_only_after_transfer_failure": _should_proxy_after({"transport_failed": True, "returncode": 7}, False)
            and not _should_proxy_after({"http_status": 404, "returncode": 0}, False)
            and not _should_proxy_after({"transport_failed": True, "returncode": 7}, True),
        "time_budget_stops_at_limit": _budget_stop(0, MAX_SECONDS) == "batch_time_budget_exhausted",
        "attempt_budget_stops_at_limit": _budget_stop(MAX_ATTEMPTS, 0) == "attempt_budget_exhausted",
        "body_budget_stops_at_limit": _remaining_body(TOTAL_CAP, 0) == 0,
        "runtime_duplicate_guard": runtime_guard_passed,
        "transport_commands_checked": True,
        "network_requests": 0,
    }
    checks["all_passed"] = (
        checks["6p39_allowed"] and checks["4p99_stops"]
        and checks["max_attempts_support_direct_and_proxy_per_object"]
        and checks["five_failure_tail_count"] == 5 and checks["five_failure_cooldown_seconds"] >= COOLDOWN
        and checks["429_503_immediate_stop_and_cooldown"]
        and checks["synthetic_roster_count"] == MAX_LOGICAL
        and checks["proxy_only_after_transfer_failure"] and checks["time_budget_stops_at_limit"]
        and checks["attempt_budget_stops_at_limit"] and checks["body_budget_stops_at_limit"]
        and checks["runtime_duplicate_guard"]
        and checks["network_requests"] == 0
    )
    fixture = {"schema": "wow-recovery.github-pages-v56-changes22.offline-validation.v1",
        "batch_id": BATCH, "synthetic_data_only": True, **checks}
    write_json(FIXTURE, fixture)
    if not checks["all_passed"]:
        raise RuntimeError("offline v56 policy fixture failed")
    print(json.dumps({"all_passed": True, "network_requests": 0, "offline_validation_sha256": sha(FIXTURE)}))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--offline-validate", action="store_true")
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--execute", action="store_true")
    p.add_argument("--pages-commit")
    p.add_argument("--actions-run")
    p.add_argument("--go", type=Path)
    a = p.parse_args()
    if a.offline_validate:
        if a.pages_commit or a.actions_run or a.go: raise SystemExit("offline validation accepts no deployment pins/GO")
        return offline_validate()
    if a.prepare:
        if not a.pages_commit or not a.actions_run or a.go: raise SystemExit("--prepare requires --pages-commit and --actions-run")
        plan, manifest = prepare(a.pages_commit, a.actions_run)
        print(json.dumps({"prepared": True, "batch_id": BATCH, "objects": len(manifest["objects"]),
            "bytes": plan["object_total_bytes"], "pages_commit": plan["pages_commit"], "actions_run": plan["actions_run"],
            "network_requests_at_prepare": 0, "plan_sha256": sha(PLAN), "manifest_sha256": sha(MANIFEST),
            "bindings_sha256": sha(BINDINGS)}))
        return 0
    if not a.go or a.pages_commit or a.actions_run: raise SystemExit("--execute requires --go PATH only")
    result = execute(a.go)
    print(json.dumps({k: v for k, v in result.items() if k != "runtime"}, ensure_ascii=False))
    return 0 if result["accepted"] else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"verify_v56_changes22: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2)
