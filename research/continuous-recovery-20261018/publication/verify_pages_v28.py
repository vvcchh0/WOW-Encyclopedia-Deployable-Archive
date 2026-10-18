"""Verify the accepted published v28 objects against the accepted local site.

This verifier is prepared for a later root publication stage and is not run by
the local preparation task.  It records the exact Pages build commit before
and after object checks, tries direct transport before the proxy inside one
process, and retains every failed attempt in progress/final JSON reports.
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


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SITE = ROOT / ".scratch/pages-resources-20261018-v28"
BASE = "https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/"
PUBLISH_REPORT = OUT / "v28-pages-publication.json"
PROGRESS_REPORT = OUT / "v28-online-progress.json"
FINAL_REPORT = OUT / "root-v28-pages-online-acceptance.json"
MAX_ATTEMPTS = 256
MAX_SECONDS = 600
MAX_BODY_BYTES = 128 * 1024 * 1024
SOURCE_LIST_TIMEOUT = 30
OTHER_TIMEOUT = 8

OBJECTS = [dict(x, mime=set(x['mime'])) for x in json.loads((OUT / 'root-v28-local-acceptance.json').read_bytes())['objects']]
assert 1 <= len(OBJECTS) <= 128



def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def build_state() -> dict[str, Any]:
    """Read the Pages build state without hiding a failed API invocation."""
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
            state.update({k: payload.get(k) for k in ["status", "commit", "updated_at", "error"]})
        except json.JSONDecodeError as exc:
            state["error"] = f"invalid gh JSON: {exc}"
    else:
        state["error"] = (result.stderr or result.stdout).strip()[:2000]
    return state


def load_expected_commit() -> str:
    if not PUBLISH_REPORT.is_file():
        raise RuntimeError(f"missing publication report: {PUBLISH_REPORT}")
    report = json.loads(PUBLISH_REPORT.read_text(encoding="utf-8"))
    commit = report.get("new_commit_sha")
    if not isinstance(commit, str) or len(commit) != 40:
        raise RuntimeError("publication report has no exact 40-character new_commit_sha")
    return commit.lower()


def local_object(relative: str) -> tuple[bytes, dict[str, Any]]:
    path = SITE / relative
    if not path.is_file():
        raise RuntimeError(f"missing local v28 object: {relative}")
    data = path.read_bytes()
    return data, {"bytes": len(data), "sha256": sha256_bytes(data)}


def run_attempt(relative: str, transport: str, timeout: float, remaining_budget: int) -> dict[str, Any]:
    data, local = local_object(relative)
    del data
    disk = shutil.disk_usage(ROOT).free
    if disk < 11005853696:
        raise RuntimeError("disk floor reached before online check")
    with tempfile.TemporaryDirectory(prefix="v28-online-", dir=OUT) as temp:
        body = Path(temp) / "body"
        curl = [
            "curl.exe", "--silent", "--show-error", "--max-time", str(timeout),
            "--connect-timeout", str(min(8,timeout)), "--max-filesize", str(min(remaining_budget,16*1024**2)),
            "--output", str(body), "--write-out", "%{http_code}\n%{content_type}",
            BASE + relative,
        ]
        if transport == "direct":
            curl[1:1] = ["--noproxy", "*"]
        elif transport == "proxy":
            curl[1:1] = ["--noproxy", "", "--proxy", "http://127.0.0.1:7890"]
        else:
            raise ValueError(transport)
        started = stamp()
        try:
            process = subprocess.run(curl, capture_output=True, text=True, timeout=timeout + 5, check=False)
            stdout = process.stdout.splitlines()
            payload = body.read_bytes() if body.exists() else b""
            status = int(stdout[0]) if stdout and stdout[0].isdigit() else None
            content_type = stdout[1] if len(stdout) > 1 else ""
            mime = content_type.split(";", 1)[0].strip().lower()
            return {
                "transport": transport,
                "started_utc": started,
                "finished_utc": stamp(),
                "curl_exit": process.returncode,
                "http_status": status,
                "content_type": content_type,
                "mime": mime,
                "bytes": len(payload),
                "sha256": sha256_bytes(payload),
                "matches_local": payload == (SITE / relative).read_bytes(),
                "stderr": process.stderr[-2000:] if process.stderr else "",
                "budget_remaining_before": remaining_budget,
                "disk_free_before_bytes": disk,
            }
        except subprocess.TimeoutExpired as exc:
            payload = body.read_bytes() if body.exists() else b""
            return {
                "transport": transport,
                "started_utc": started,
                "finished_utc": stamp(),
                "curl_exit": None,
                "http_status": None,
                "content_type": "",
                "mime": "",
                "bytes": len(payload),
                "sha256": sha256_bytes(payload),
                "matches_local": False,
                "timeout": True,
                "error": str(exc),
                "budget_remaining_before": remaining_budget,
                "disk_free_before_bytes": disk,
            }


def main() -> int:
    expected_commit = load_expected_commit()
    if not 1 <= len(OBJECTS) <= 128 or len({item["path"] for item in OBJECTS}) != len(OBJECTS):
        raise RuntimeError("verifier requires a bounded unique object list from the accepted local gate")
    before = build_state()
    if before.get("status") != "built" or (before.get("commit") or "").lower() != expected_commit:
        raise RuntimeError("expected Pages commit must finish building before object checks")
    report: dict[str, Any] = {
        "schema": "wow-recovery.root.v28.pages-online-acceptance.v1",
        "started_utc": stamp(),
        "expected_pages_commit": expected_commit,
        "local_site": str(SITE.relative_to(ROOT)).replace("\\", "/"),
        "base_url": BASE,
        "build_before": before,
        "objects": [],
        "policy": {
            "exact_object_count": len(OBJECTS),
            "direct_first": True,
            "proxy_only_in_same_process": True,
            "tls_verification": True,
            "redirects": False,
            "maximum_attempts": MAX_ATTEMPTS,
            "maximum_seconds": MAX_SECONDS,
            "maximum_body_bytes": MAX_BODY_BYTES,
            "source_list_timeout_seconds": SOURCE_LIST_TIMEOUT,
            "other_timeout_seconds": OTHER_TIMEOUT,
            "failed_attempts_retained": True,
        },
    }
    deadline = time.monotonic() + MAX_SECONDS
    attempts = 0
    total_body_bytes = 0
    for spec in OBJECTS:
        relative = spec["path"]
        local, local_meta = local_object(relative)
        del local
        obj: dict[str, Any] = {
            "path": relative,
            "local_bytes": local_meta["bytes"],
            "local_sha256": local_meta["sha256"],
            "expected_mime": sorted(spec["mime"]),
            "source_list": spec["source_list"],
            "attempts": [],
            "accepted": False,
        }
        timeout = SOURCE_LIST_TIMEOUT if spec["source_list"] else OTHER_TIMEOUT
        for transport in ("direct", "proxy"):
            if time.monotonic() >= deadline or attempts >= MAX_ATTEMPTS or total_body_bytes >= MAX_BODY_BYTES:
                break
            attempts += 1
            attempt = run_attempt(relative, transport, min(timeout,deadline-time.monotonic()), MAX_BODY_BYTES - total_body_bytes)
            obj["attempts"].append(attempt)
            total_body_bytes += int(attempt.get("bytes", 0) or 0)
            obj["accepted"] = (
                attempt.get("curl_exit") == 0
                and attempt.get("http_status") == 200
                and attempt.get("matches_local") is True
                and attempt.get("mime") in spec["mime"]
            )
            if obj["accepted"]:
                break
        report["objects"].append(obj)
        report["attempts"] = attempts
        report["total_body_bytes"] = total_body_bytes
        report["accepted_objects"] = sum(bool(item["accepted"]) for item in report["objects"])
        PROGRESS_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    after = build_state()
    report.update({
        "build_after": after,
        "finished_utc": stamp(),
        "attempts": attempts,
        "total_body_bytes": total_body_bytes,
        "accepted_objects": sum(bool(item["accepted"]) for item in report["objects"]),
        "disk_free_bytes": shutil.disk_usage(ROOT).free,
    })
    report["accepted"] = (
        report["accepted_objects"] == len(OBJECTS)
        and before.get("status") == "built"
        and (before.get("commit") or "").lower() == expected_commit
        and after.get("status") == "built"
        and after.get("commit", "").lower() == expected_commit
        and total_body_bytes <= MAX_BODY_BYTES and attempts <= MAX_ATTEMPTS
        and report["disk_free_bytes"] >= 11005853696
    )
    FINAL_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"accepted": report["accepted"], "objects": report["accepted_objects"], "attempts": attempts, "build_before": before, "build_after": after}, ensure_ascii=False))
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    if FINAL_REPORT.exists():
        raise RuntimeError("refusing to overwrite accepted online receipt")
    raise SystemExit(main())
