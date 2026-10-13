"""Offline Git-clone smoke validation for the publication checkpoint.

This script reads only the local clone and the already captured loopback
server logs.  It does not start a server or make network requests.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


CLONE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
MANIFEST = CLONE / "offline" / "build-manifest.json"
REQUEST_LOG = OUT / "server-requests.jsonl"
HEALTH = OUT / "health.json"
ROUTES = OUT / "routes.json"


def sha256_file(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            h.update(chunk)
    return h.hexdigest(), size


def inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(CLONE), *args], text=True, stderr=subprocess.STDOUT
    ).strip()


manifest_sha, manifest_size = sha256_file(MANIFEST)
manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
items = manifest.get("files", [])
records = []
missing = []
nonregular = []
unsafe = []
hash_mismatch = []
length_mismatch = []
routes_seen = set()

for item in items:
    output_path = item.get("output_path")
    route = item.get("route")
    if not isinstance(output_path, str):
        unsafe.append({"route": route, "output_path": output_path, "reason": "not_string"})
        continue
    candidate = (CLONE / output_path).resolve()
    if not inside(candidate, CLONE):
        unsafe.append({"route": route, "output_path": output_path, "reason": "outside_clone"})
        continue
    if route in routes_seen:
        unsafe.append({"route": route, "output_path": output_path, "reason": "duplicate_route"})
    routes_seen.add(route)
    if not candidate.exists():
        missing.append({"route": route, "output_path": output_path})
        continue
    if not candidate.is_file():
        nonregular.append({"route": route, "output_path": output_path})
        continue
    got_sha, got_len = sha256_file(candidate)
    expected_sha = item.get("derived_sha256")
    expected_len = item.get("derived_length")
    if expected_sha and got_sha.lower() != str(expected_sha).lower():
        hash_mismatch.append({"route": route, "output_path": output_path, "expected": expected_sha, "actual": got_sha})
    if expected_len is not None and got_len != int(expected_len):
        length_mismatch.append({"route": route, "output_path": output_path, "expected": expected_len, "actual": got_len})
    records.append({"route": route, "output_path": output_path, "sha256": got_sha, "length": got_len})

request_records = []
if REQUEST_LOG.exists():
    for line_number, line in enumerate(REQUEST_LOG.read_text(encoding="utf-8").splitlines(), 1):
        try:
            request_records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            request_records.append({"line": line_number, "parse_error": str(exc)})

external_routes = []
for record in request_records:
    route = record.get("route")
    if isinstance(route, str) and ("://" in route or not route.startswith("/")):
        external_routes.append(record)

top_level = {p.name: p for p in CLONE.iterdir()}
size_total = 0
for record in records:
    size_total += int(record["length"])

report = {
    "clone": str(CLONE),
    "git_head": git("rev-parse", "HEAD"),
    "git_status_porcelain": git("status", "--porcelain"),
    "core_longpaths": git("config", "--get", "core.longpaths"),
    "manifest": {
        "path": str(MANIFEST),
        "sha256": manifest_sha,
        "bytes": manifest_size,
        "file_records": len(items),
        "unique_routes": len(routes_seen),
        "derived_bytes_sum": size_total,
    },
    "file_validation": {
        "hashed": len(records),
        "missing": missing,
        "nonregular": nonregular,
        "unsafe_or_duplicate": unsafe,
        "hash_mismatch": hash_mismatch,
        "length_mismatch": length_mismatch,
        "pass": not (missing or nonregular or unsafe or hash_mismatch or length_mismatch),
    },
    "clone_layout": {
        "offline_site_present": (CLONE / "offline" / "site").is_dir(),
        "mirror_present": (CLONE / "mirror").exists(),
        "backups_present": (CLONE / "backups").exists(),
        "top_level_entries": sorted(top_level),
    },
    "loopback_log": {
        "health": json.loads(HEALTH.read_text(encoding="utf-8")) if HEALTH.exists() else None,
        "route_check": json.loads(ROUTES.read_text(encoding="utf-8")) if ROUTES.exists() else None,
        "request_records": len(request_records),
        "status_counts": {str(code): sum(1 for r in request_records if r.get("status") == code) for code in sorted({r.get("status") for r in request_records if isinstance(r.get("status"), int)})},
        "external_or_nonlocal_routes": external_routes,
        "parse_errors": [r for r in request_records if "parse_error" in r],
        "all_local_routes": not external_routes and not any("parse_error" in r for r in request_records),
    },
}

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "clone-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "git_head": report["git_head"],
    "core_longpaths": report["core_longpaths"],
    "manifest_sha256": manifest_sha,
    "file_records": len(items),
    "hashed": len(records),
    "file_pass": report["file_validation"]["pass"],
    "request_records": len(request_records),
    "all_local_routes": report["loopback_log"]["all_local_routes"],
    "mirror_present": report["clone_layout"]["mirror_present"],
    "backups_present": report["clone_layout"]["backups_present"],
}, ensure_ascii=False))
if not report["file_validation"]["pass"]:
    raise SystemExit(2)
