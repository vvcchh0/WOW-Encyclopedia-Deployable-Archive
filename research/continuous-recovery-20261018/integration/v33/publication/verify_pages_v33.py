#!/usr/bin/env python3
"""Bounded online verifier for a later root-owned v33 Pages publication.

Importing this module is offline.  HTTP and GitHub build-state calls occur only
after ``--go --root-pages-online-go`` and an accepted v33 publication report.
The verifier checks the exact Pages commit before and after every bounded
object request, trying direct transport before the proxy in one process.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
EXPECTED_ROOT = "d:/wow_encyclopedia"
if ROOT.as_posix().casefold().rstrip("/") != EXPECTED_ROOT:
    raise RuntimeError(f"nested v33 publication root must be D:/WOW_Encyclopedia, got {ROOT}")

PUB = Path(__file__).resolve().parent
SITE = ROOT / ".scratch/pages-resources-20261018-v33"
ROOT_PUBLICATION = ROOT / "research/continuous-recovery-20261018/publication"
LOCAL_GATE = ROOT_PUBLICATION / "root-v33-local-acceptance.json"
PUBLISH_REPORT = ROOT_PUBLICATION / "v33-pages-publication.json"
PROGRESS_REPORT = ROOT_PUBLICATION / "v33-pages-online-progress.json"
FINAL_REPORT = ROOT_PUBLICATION / "root-v33-pages-online-acceptance.json"
BASE = "https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/"
MIN_FREE_BYTES = 11_005_853_696
MAX_ATTEMPTS = 512
MAX_SECONDS = 900
MAX_BODY_BYTES = 256 * 1024 * 1024
SOURCE_LIST_TIMEOUT = 30
OTHER_TIMEOUT = 8


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def safe_root_path(relative: str, label: str) -> Path:
    normalized = str(relative).replace("\\", "/")
    if not normalized or normalized.startswith("/") or ".." in normalized.split("/"):
        raise RuntimeError(f"unsafe {label} path: {relative}")
    path = (ROOT / normalized).resolve()
    if path != ROOT.resolve() and not path.is_relative_to(ROOT.resolve()):
        raise RuntimeError(f"{label} escapes D:/WOW_Encyclopedia: {relative}")
    return path


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} is not an object: {path}")
    return value


def load_objects() -> list[dict[str, Any]]:
    gate = read_json(LOCAL_GATE, "v33 local acceptance")
    if gate.get("accepted") is not True or gate.get("published") is not False:
        raise RuntimeError("v33 local acceptance is not an unpublished accepted gate")
    expected_local_site = str(SITE.relative_to(ROOT)).replace("\\", "/")
    if gate.get("local_site") != expected_local_site:
        raise RuntimeError("v33 local acceptance points at a different local site")
    bindings = gate.get("bindings")
    if not isinstance(bindings, list) or not bindings:
        raise RuntimeError("v33 local acceptance has no binding list")
    seen_bindings: set[str] = set()
    for index, raw in enumerate(bindings):
        if not isinstance(raw, dict) or not raw.get("path") or not raw.get("sha256") or not isinstance(raw.get("bytes"), int):
            raise RuntimeError(f"v33 binding {index} lacks path/SHA/bytes")
        normalized = str(raw["path"]).replace("\\", "/")
        if normalized in seen_bindings:
            raise RuntimeError(f"duplicate v33 binding path: {normalized}")
        seen_bindings.add(normalized)
        path = safe_root_path(normalized, "v33 binding")
        if not path.is_file() or sha256_file(path).casefold() != str(raw["sha256"]).casefold() or path.stat().st_size != raw["bytes"]:
            raise RuntimeError(f"v33 binding hash/length mismatch: {normalized}")
    objects = gate.get("objects")
    if not isinstance(objects, list) or not 1 <= len(objects) <= 256:
        raise RuntimeError("v33 verifier requires 1..256 accepted local objects")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(objects):
        if not isinstance(raw, dict) or not raw.get("path") or not raw.get("sha256"):
            raise RuntimeError(f"v33 local object {index} has no path/SHA")
        path = str(raw["path"]).replace("\\", "/")
        if path in seen or path.startswith("/") or ".." in path.split("/"):
            raise RuntimeError(f"unsafe or duplicate v33 local object path: {path}")
        seen.add(path)
        if not isinstance(raw.get("bytes"), int) or not isinstance(raw.get("sha256"), str):
            raise RuntimeError(f"v33 local object {index} has invalid expected bytes/SHA")
        _, actual = local_object(path)
        if actual["bytes"] != raw["bytes"] or actual["sha256"].casefold() != raw["sha256"].casefold():
            raise RuntimeError(f"v33 local object hash/length mismatch: {path}")
        result.append({**raw, "path": path, "mime": set(raw.get("mime") or [])})
    return result


def build_state() -> dict[str, Any]:
    result = subprocess.run(
        ["gh", "api", "repos/vvcchh0/WOW-Encyclopedia-Deployable-Archive/pages/builds/latest"],
        capture_output=True,
        text=True,
        timeout=45,
        check=False,
    )
    state: dict[str, Any] = {
        "command": "gh api repos/vvcchh0/WOW-Encyclopedia-Deployable-Archive/pages/builds/latest",
        "returncode": result.returncode,
        "status": None,
        "commit": None,
        "updated_at": None,
        "error": None,
    }
    if result.returncode == 0:
        try:
            payload = json.loads(result.stdout)
            state.update({key: payload.get(key) for key in ("status", "commit", "updated_at", "error")})
        except json.JSONDecodeError as exc:
            state["error"] = f"invalid gh JSON: {exc}"
    else:
        state["error"] = (result.stderr or result.stdout).strip()[:2000]
    return state


def expected_commit() -> str:
    report = read_json(PUBLISH_REPORT, "v33 publication report")
    commit = str(report.get("new_commit_sha") or "").casefold()
    if len(commit) != 40 or any(char not in "0123456789abcdef" for char in commit):
        raise RuntimeError("v33 publication report has no exact 40-character new_commit_sha")
    return commit


def local_object(relative: str) -> tuple[bytes, dict[str, Any]]:
    path = SITE / relative
    resolved = path.resolve()
    if resolved != SITE.resolve() and not resolved.is_relative_to(SITE.resolve()):
        raise RuntimeError(f"v33 object escapes local site: {relative}")
    if not path.is_file():
        raise RuntimeError(f"missing local v33 object: {relative}")
    data = path.read_bytes()
    return data, {"bytes": len(data), "sha256": sha256_bytes(data)}


def curl_command(relative: str, transport: str, timeout: float, body: Path, remaining_budget: int) -> list[str]:
    command = [
        "curl.exe", "--silent", "--show-error", "--max-time", str(max(1, int(timeout))),
        "--connect-timeout", str(min(8, max(1, int(timeout)))),
        "--max-filesize", str(min(16 * 1024 * 1024, max(1, remaining_budget))),
        "--proto", "=https", "--tlsv1.2", "--output", str(body),
        "--write-out", "%{http_code}\n%{content_type}", BASE + relative,
    ]
    if transport == "direct":
        command[1:1] = ["--noproxy", "*"]
    elif transport == "proxy":
        command[1:1] = ["--noproxy", "", "--proxy", "http://127.0.0.1:7890"]
    else:
        raise ValueError(f"unsupported transport: {transport}")
    return command


def run_attempt(relative: str, transport: str, timeout: float, remaining_budget: int) -> dict[str, Any]:
    data, local = local_object(relative)
    del data
    disk = shutil.disk_usage(ROOT).free
    if disk < MIN_FREE_BYTES:
        raise RuntimeError("D disk floor reached before v33 online check")
    with tempfile.TemporaryDirectory(prefix="v33-online-", dir=PUB) as temporary:
        body = Path(temporary) / "body"
        command = curl_command(relative, transport, timeout, body, remaining_budget)
        started = stamp()
        try:
            process = subprocess.run(command, capture_output=True, text=True, timeout=timeout + 5, check=False)
            output = process.stdout.splitlines()
            payload = body.read_bytes() if body.exists() else b""
            status = int(output[0]) if output and output[0].isdigit() else None
            content_type = output[1] if len(output) > 1 else ""
            mime = content_type.split(";", 1)[0].strip().casefold()
            return {
                "transport": transport, "started_utc": started, "finished_utc": stamp(),
                "command": command, "curl_exit": process.returncode, "http_status": status,
                "content_type": content_type, "mime": mime, "bytes": len(payload),
                "sha256": sha256_bytes(payload), "matches_local": payload == (SITE / relative).read_bytes(),
                "stderr": process.stderr[-2000:] if process.stderr else "",
                "budget_remaining_before": remaining_budget, "disk_free_before_bytes": disk,
                "local_sha256": local["sha256"],
            }
        except subprocess.TimeoutExpired as exc:
            payload = body.read_bytes() if body.exists() else b""
            return {
                "transport": transport, "started_utc": started, "finished_utc": stamp(),
                "command": command, "curl_exit": None, "http_status": None, "content_type": "", "mime": "",
                "bytes": len(payload), "sha256": sha256_bytes(payload), "matches_local": False,
                "timeout": True, "error": str(exc), "budget_remaining_before": remaining_budget,
                "disk_free_before_bytes": disk, "local_sha256": local["sha256"],
            }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--go", action="store_true")
    parser.add_argument("--root-pages-online-go", action="store_true")
    args = parser.parse_args(argv)
    if not args.go or not args.root_pages_online_go:
        parser.error("v33 online verification requires --go --root-pages-online-go")
    if FINAL_REPORT.exists():
        raise RuntimeError(f"refusing existing v33 online acceptance: {FINAL_REPORT}")
    objects = load_objects()
    commit = expected_commit()
    before = build_state()
    if before.get("status") != "built" or str(before.get("commit") or "").casefold() != commit:
        raise RuntimeError("expected v33 Pages commit must finish building before object checks")
    report: dict[str, Any] = {
        "schema": "wow-recovery.root.v33-pages-online-acceptance.v1",
        "started_utc": stamp(), "expected_pages_commit": commit,
        "local_site": str(SITE.relative_to(ROOT)).replace("\\", "/"), "base_url": BASE,
        "build_before": before, "objects": [],
        "policy": {
            "exact_object_count": len(objects), "direct_first": True, "proxy_only_in_same_process": True,
            "tls_verification": True, "redirects": False, "maximum_attempts": MAX_ATTEMPTS,
            "maximum_seconds": MAX_SECONDS, "maximum_body_bytes": MAX_BODY_BYTES,
            "source_list_timeout_seconds": SOURCE_LIST_TIMEOUT, "other_timeout_seconds": OTHER_TIMEOUT,
            "failed_attempts_retained": True,
        },
    }
    deadline = time.monotonic() + MAX_SECONDS
    attempts = 0
    total_body_bytes = 0
    for spec in objects:
        relative = spec["path"]
        _, local_meta = local_object(relative)
        obj: dict[str, Any] = {
            "path": relative, "local_bytes": local_meta["bytes"], "local_sha256": local_meta["sha256"],
            "expected_mime": sorted(spec["mime"]), "source_list": bool(spec.get("source_list")),
            "attempts": [], "accepted": False,
        }
        timeout = SOURCE_LIST_TIMEOUT if obj["source_list"] else OTHER_TIMEOUT
        for transport in ("direct", "proxy"):
            if time.monotonic() >= deadline or attempts >= MAX_ATTEMPTS or total_body_bytes >= MAX_BODY_BYTES:
                break
            attempts += 1
            attempt = run_attempt(relative, transport, min(timeout, max(1, deadline - time.monotonic())), MAX_BODY_BYTES - total_body_bytes)
            obj["attempts"].append(attempt)
            total_body_bytes += int(attempt.get("bytes", 0) or 0)
            obj["accepted"] = (
                attempt.get("curl_exit") == 0 and attempt.get("http_status") == 200
                and attempt.get("matches_local") is True and attempt.get("mime") in spec["mime"]
            )
            if obj["accepted"]:
                break
        report["objects"].append(obj)
        report.update({"attempts": attempts, "total_body_bytes": total_body_bytes, "accepted_objects": sum(bool(item["accepted"]) for item in report["objects"])})
        PROGRESS_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    after = build_state()
    report.update({"build_after": after, "finished_utc": stamp(), "attempts": attempts, "total_body_bytes": total_body_bytes, "accepted_objects": sum(bool(item["accepted"]) for item in report["objects"]), "disk_free_bytes": shutil.disk_usage(ROOT).free})
    report["accepted"] = (
        report["accepted_objects"] == len(objects) and before.get("status") == "built"
        and str(before.get("commit") or "").casefold() == commit and after.get("status") == "built"
        and str(after.get("commit") or "").casefold() == commit and attempts <= MAX_ATTEMPTS
        and total_body_bytes <= MAX_BODY_BYTES and report["disk_free_bytes"] >= MIN_FREE_BYTES
    )
    FINAL_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"accepted": report["accepted"], "objects": report["accepted_objects"], "attempts": attempts, "build_before": before, "build_after": after}, ensure_ascii=False))
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
