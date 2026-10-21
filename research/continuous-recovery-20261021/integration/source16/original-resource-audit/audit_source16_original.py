#!/usr/bin/env python3
"""Read-only original-evidence audit for the Source16 dependency gaps.

This is deliberately smaller than the talent audit: it uses the eight-page
Source16 dependency report as its exact target set, scans only the named
acquisition/backup layers, reads ZIP central directories, and opens only a
matched member (or a small direct file) for byte/image validation.
"""

from __future__ import annotations

import csv
import hashlib
import json
import mimetypes
import os
import re
import shutil
import stat
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import unquote, urlsplit

try:
    from PIL import Image
except Exception:  # pragma: no cover - receipt records this as unavailable
    Image = None


ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
DEP_JSON = ROOT / "research/continuous-recovery-20261021/integration/source16/dependency-audit/dependency-audit.json"
DEP_CSV = ROOT / "research/continuous-recovery-20261021/integration/source16/dependency-audit/dependency-audit.csv"
FREE_FLOOR = 11_005_853_696
MAX_BODY_READ = 64 * 1024 * 1024

BACKUP_ROOTS = [
    "backups/20080512",
    "backups/resource-recovery-2008",
    "backups/site-recovery-2008",
    "backups/site-expansion-2008",
    "backups/final-cdx-image-wave-20261012",
    "backups/final-pre2008-image-wave-20261012",
    "backups/final-single-image-followup-20261012",
    "backups/shared-image-final-followup-20261012",
    "backups/gap-review-20261011",
]
SOURCE_ZIPS = [
    "artifacts/WOW_Encyclopedia_20080512_full_source.zip",
    "artifacts/WOW_Encyclopedia_20101203_source.zip",
    "artifacts/WOW_Encyclopedia_20080512_sample_and_reassessment.zip",
    "artifacts/WOW_Encyclopedia_20080512_gap_review_20261011.zip",
]
CATALOG_NAME_RE = re.compile(r"(?:catalog|mapping|index|summary|completion|manifest|source|inventory|validation)", re.I)
URL_FIELDS = {"original", "original_url", "requested_url", "actual_url", "final_url", "url", "target", "path", "original_path"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path).replace("\\", "/")


def norm_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("\\", "/")
    replay = re.search(r"(?:id|im)_/", text)
    if replay:
        text = text[replay.end():]
    if re.match(r"^https?://", text, re.I):
        text = urlsplit(text).path or "/"
    else:
        # Direct mirrors and source ZIPs often retain a host prefix (sometimes
        # after a project/mirror directory).  Keep only the path after that
        # host; this is an exact alias, not a basename match.
        marker = re.search(r"(?:https?://)?(?:www\.)?worldofwarcraft\.com(?:_80)?/", text, re.I)
        if marker:
            text = "/" + text[marker.end():]
    for _ in range(4):
        decoded = unquote(text)
        if decoded == text:
            break
        text = decoded
    text = text.split("?", 1)[0].split("#", 1)[0]
    text = re.sub(r"^/+", "/", text)
    prefixes = (
        "/WOW-Encyclopedia-Deployable-Archive",
        "/www.worldofwarcraft.com_80",
        "/www.worldofwarcraft.com",
        "/worldofwarcraft.com",
    )
    changed = True
    while changed:
        changed = False
        for prefix in prefixes:
            if text == prefix:
                text = "/"
                changed = True
                break
            if text.startswith(prefix + "/"):
                text = text[len(prefix):]
                changed = True
                break
    return text or "/"


def variants(target: str) -> set[str]:
    return {norm_path(v) or v for v in (target, target.replace("'", "%27"), target.replace("'", "%2527"))}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_zip_member(name: str) -> bool:
    normalized = name.replace("\\", "/")
    return not (normalized.startswith("/") or any(part == ".." for part in normalized.split("/")))


def expected_mime(name: str) -> str | None:
    ext = Path(name).suffix.lower()
    return {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".png": "image/png",
        ".css": "text/css", ".js": "text/javascript", ".xml": "application/xml", ".swf": "application/x-shockwave-flash",
    }.get(ext) or mimetypes.guess_type(name)[0]


def validate_body(data: bytes, name: str) -> dict[str, Any]:
    result: dict[str, Any] = {"length": len(data), "sha256": sha256_bytes(data), "mime": expected_mime(name)}
    ext = Path(name).suffix.lower()
    if ext in {".jpg", ".jpeg", ".gif", ".png", ".webp"}:
        if Image is None:
            result.update({"image_valid": None, "image_validation": "PIL unavailable"})
        else:
            try:
                with Image.open(BytesIO(data)) as image:
                    frames = 1
                    try:
                        frames = int(getattr(image, "n_frames", 1))
                    except Exception:
                        frames = 1
                    image.verify()
                    result.update({"image_valid": True, "format": image.format, "width": image.width, "height": image.height, "frames": frames})
            except Exception as error:
                result.update({"image_valid": False, "image_validation": str(error)[:240]})
    elif ext == ".swf":
        result.update({"swf_magic": data[:3].decode("ascii", "replace"), "swf_valid": data[:3] in {b"FWS", b"CWS", b"ZWS"}})
    else:
        result["nonempty"] = bool(data)
    return result


def iter_strings(value: Any, pointer: str = "") -> Iterable[tuple[str, str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_pointer = f"{pointer}/{str(key).replace('~', '~0').replace('/', '~1')}"
            if isinstance(child, str):
                yield child_pointer, str(key), child
            else:
                yield from iter_strings(child, child_pointer)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_pointer = f"{pointer}/{index}"
            if isinstance(child, str):
                yield child_pointer, "[list]", child
            else:
                yield from iter_strings(child, child_pointer)


def iter_manifest_records(path: Path, stats: dict[str, Any]) -> Iterable[tuple[int, dict[str, Any]]]:
    if path.suffix.lower() == ".json":
        try:
            value = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, json.JSONDecodeError):
            stats["json_errors"] += 1
            return
        records = value if isinstance(value, list) else [value]
        for line_no, record in enumerate(records, 1):
            stats["records"] += 1
            if isinstance(record, dict):
                yield line_no, record
        return
    try:
        handle = path.open("r", encoding="utf-8", errors="replace")
    except OSError:
        return
    with handle:
        for line_no, line in enumerate(handle, 1):
            stats["records"] += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                stats["json_errors"] += 1
                continue
            if isinstance(record, dict):
                yield line_no, record


def content_type(record: dict[str, Any]) -> str | None:
    headers = record.get("response_headers") or record.get("headers") or {}
    if isinstance(headers, dict):
        for key, value in headers.items():
            if str(key).lower() == "content-type":
                return str(value).split(";", 1)[0].strip().lower()
    for key in ("mime", "mime_type", "content_type"):
        if record.get(key):
            return str(record[key]).split(";", 1)[0].strip().lower()
    return None


def status_number(record: dict[str, Any]) -> int | None:
    for key in ("http_status", "status_code", "response_status"):
        try:
            return int(record.get(key))
        except (TypeError, ValueError):
            pass
    return None


def manifest_fields(record: dict[str, Any]) -> Iterable[tuple[str, str]]:
    for key, value in record.items():
        if key in URL_FIELDS and isinstance(value, str):
            yield key, value
    attempts = record.get("attempts")
    if isinstance(attempts, list):
        for index, attempt in enumerate(attempts):
            if isinstance(attempt, dict):
                for key, value in attempt.items():
                    if key in URL_FIELDS and isinstance(value, str):
                        yield f"attempts[{index}].{key}", value


def archive_member_info(path: Path, member: str, cache: dict[str, dict[str, zipfile.ZipInfo]]) -> dict[str, Any] | None:
    if not path.is_file() or not safe_zip_member(member):
        return None
    key = str(path.resolve())
    if key not in cache:
        try:
            with zipfile.ZipFile(path, "r") as archive:
                cache[key] = {info.filename: info for info in archive.infolist()}
        except (OSError, zipfile.BadZipFile):
            cache[key] = {}
    info = cache[key].get(member) or cache[key].get(member.lstrip("/"))
    if info is None or info.is_dir():
        return None
    mode = (info.external_attr >> 16) & 0xFFFF
    return {
        "archive": rel(path), "member": info.filename, "file_size": info.file_size,
        "compress_size": info.compress_size, "crc32": f"{info.CRC:08x}",
        "date_time": list(info.date_time), "encrypted": bool(info.flag_bits & 0x1),
        "symlink": stat.S_ISLNK(mode),
    }


def read_archive_body(path: Path, member: str, logical_name: str | None = None) -> dict[str, Any]:
    if not path.is_file() or not safe_zip_member(member):
        return {"body_read": False, "body_error": "unsafe_or_missing_archive"}
    try:
        with zipfile.ZipFile(path, "r") as archive:
            info = archive.getinfo(member)
            if info.is_dir() or info.flag_bits & 0x1:
                return {"body_read": False, "body_error": "directory_or_encrypted"}
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                return {"body_read": False, "body_error": "symlink_member"}
            if info.file_size > MAX_BODY_READ:
                return {"body_read": False, "body_error": "member_above_read_cap", "read_cap": MAX_BODY_READ}
            data = archive.read(info)
        return {"body_read": True, **validate_body(data, logical_name or info.filename)}
    except (OSError, KeyError, RuntimeError, zipfile.BadZipFile) as error:
        return {"body_read": False, "body_error": str(error)[:240]}


def safe_archive_for_manifest(manifest: Path, zip_part: Any) -> Path | None:
    if not isinstance(zip_part, str) or not zip_part:
        return None
    candidate = (manifest.parent / zip_part).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def build_target_rows() -> tuple[dict[str, dict[str, Any]], int, int]:
    with DEP_CSV.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    targets: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row.get("status") not in {"local_missing", "dynamic_local_missing"}:
            continue
        route = norm_path(row.get("route"))
        if not route:
            continue
        kind = row.get("kind") or "unknown"
        key = f"{route}\0{kind}"
        item = targets.setdefault(key, {"target": route, "kind": kind, "uses": [], "pages": set(), "raw_urls": set(), "lines": set(), "contexts": set()})
        item["pages"].add(row.get("page_id"))
        item["raw_urls"].add(row.get("raw_url"))
        item["lines"].add(row.get("line"))
        item["contexts"].add(row.get("context"))
        item["uses"].append({"page_id": row.get("page_id"), "page_route": row.get("page_route"), "raw_url": row.get("raw_url"), "line": row.get("line"), "element": row.get("element"), "attribute": row.get("attribute"), "context": row.get("context")})
    static_count = sum(1 for item in targets.values() if item["kind"] != "swf")
    swf_count = sum(1 for item in targets.values() if item["kind"] == "swf")
    for item in targets.values():
        item["pages"] = sorted(x for x in item["pages"] if x)
        item["raw_urls"] = sorted(x for x in item["raw_urls"] if x)
        item["lines"] = sorted(x for x in item["lines"] if x)
        item["contexts"] = sorted(x for x in item["contexts"] if x)
    return targets, static_count, swf_count


def main() -> int:
    started = utc_now()
    targets, static_count, swf_count = build_target_rows()
    by_variant = {variant: key for key, item in targets.items() for variant in variants(item["target"])}
    by_route = {item["target"]: key for key, item in targets.items()}
    evidence: dict[str, list[dict[str, Any]]] = defaultdict(list)
    candidate_evidence: dict[str, list[dict[str, Any]]] = defaultdict(list)
    stats: dict[str, Any] = {"manifest_files": 0, "manifest_bytes": 0, "manifest_records": 0, "manifest_json_errors": 0, "catalog_files": 0, "catalog_bytes": 0, "catalog_json_errors": 0, "central_archives": 0, "central_archive_bytes": 0, "central_entries": 0, "central_bad_archives": 0, "central_exact_matches": 0, "central_basename_candidates": 0, "direct_files_checked": 0, "direct_exact_hits": 0, "direct_basename_candidates": 0}
    zip_cache: dict[str, dict[str, zipfile.ZipInfo]] = {}
    body_cache: dict[tuple[str, str], dict[str, Any]] = {}
    basename_to_keys: dict[str, set[str]] = defaultdict(set)
    for key, item in targets.items():
        basename_to_keys[Path(item["target"]).name.lower()].add(key)

    # Exact direct-path and same-basename candidate search in the explicitly
    # documented raw/direct roots only.
    direct_roots = [(ROOT / "mirror/20080512", "mirror_2008"), (ROOT / "research/acquisition-2008/integration/superseded-trial-export", "superseded_trial_export")]
    for root, label in direct_roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            stats["direct_files_checked"] += 1
            name_lower = path.name.lower()
            keys = basename_to_keys.get(name_lower, set())
            if not keys:
                continue
            normalized = norm_path(path.relative_to(root).as_posix())
            if label == "superseded_trial_export":
                relpath = path.relative_to(root).as_posix()
                normalized = norm_path(relpath)
            for key in keys:
                item = targets[key]
                is_exact = normalized in variants(item["target"])
                try:
                    size = path.stat().st_size
                    if size <= MAX_BODY_READ:
                        body = path.read_bytes()
                        checked = validate_body(body, path.name)
                    else:
                        checked = {"body_read": False, "body_error": "file_above_read_cap", "read_cap": MAX_BODY_READ, "length": size, "sha256": sha256_file(path)}
                except OSError as error:
                    checked = {"body_read": False, "body_error": str(error)[:240]}
                record = {"kind": "direct_file", "root": label, "path": rel(path), "normalized_path": normalized, "exact_route": is_exact, **checked}
                if is_exact:
                    evidence[key].append(record); stats["direct_exact_hits"] += 1
                else:
                    candidate_evidence[key].append({"kind": "direct_basename_candidate", "root": label, "path": rel(path), "normalized_path": normalized, **{k: v for k, v in checked.items() if k in {"length", "sha256", "mime", "format", "width", "height", "frames", "image_valid", "swf_magic", "swf_valid"}}}); stats["direct_basename_candidates"] += 1

    # Named raw manifests under the nine backup roots.  This keeps source
    # status/length/hash evidence but deliberately omits private raw URLs.
    manifest_paths: list[Path] = []
    backup_inventory: list[dict[str, Any]] = []
    for relative in BACKUP_ROOTS:
        root = ROOT / relative
        inv = {"root": relative, "exists": root.is_dir(), "manifest_files": 0, "manifest_bytes": 0, "zip_files": 0, "zip_bytes": 0}
        if root.is_dir():
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                if "manifest" in path.name.lower() and path.suffix.lower() in {".json", ".jsonl"}:
                    manifest_paths.append(path); inv["manifest_files"] += 1; inv["manifest_bytes"] += path.stat().st_size
                if path.suffix.lower() == ".zip":
                    inv["zip_files"] += 1; inv["zip_bytes"] += path.stat().st_size
        backup_inventory.append(inv)
    # One small acquisition manifest is outside the backup roots.  Include it
    # as metadata evidence, while keeping the rest of acquisition catalogs in
    # the separate catalog pass below.
    acq_manifest_root = ROOT / "research/acquisition-2008"
    if acq_manifest_root.is_dir():
        manifest_paths.extend(path for path in acq_manifest_root.rglob("*") if path.is_file() and "manifest" in path.name.lower() and path.suffix.lower() in {".json", ".jsonl"})
    mstats = {"json_errors": 0, "records": 0}
    for manifest in sorted(set(manifest_paths)):
        stats["manifest_files"] += 1; stats["manifest_bytes"] += manifest.stat().st_size
        for line_no, record in iter_manifest_records(manifest, mstats):
            seen: set[tuple[str, str]] = set()
            for field, value in manifest_fields(record):
                normalized = norm_path(value)
                key = by_variant.get(normalized)
                basename_keys = basename_to_keys.get(Path(normalized or value).name.lower(), set())
                if key is None:
                    # Preserve a same-basename source lead at its actual
                    # historical path, without treating it as the requested
                    # route.  This is useful for regional/same-topic review.
                    for candidate_key in sorted(basename_keys):
                        if (candidate_key, field) in seen:
                            continue
                        seen.add((candidate_key, field))
                        zip_entry = record.get("zip_entry") or record.get("object_entry") or record.get("object_path")
                        zip_part = record.get("zip_part") or record.get("zip_file") or record.get("archive")
                        archive = safe_archive_for_manifest(manifest, zip_part)
                        member = archive_member_info(archive, str(zip_entry), zip_cache) if archive is not None and isinstance(zip_entry, str) else None
                        candidate: dict[str, Any] = {"kind": "manifest_basename_candidate", "manifest": rel(manifest), "line": line_no, "matched_field": field, "normalized": normalized, "status": record.get("status"), "http_status": status_number(record), "content_type": content_type(record), "role": record.get("role"), "sha256": record.get("sha256"), "content_length": record.get("content_length") or record.get("length"), "zip_part": rel(archive) if archive else None, "zip_entry": zip_entry, "archive_member": member}
                        if member and archive and member.get("file_size", 0) <= MAX_BODY_READ and not member.get("encrypted") and not member.get("symlink"):
                            body_key = (str(archive.resolve()), member["member"])
                            candidate["body"] = body_cache.setdefault(body_key, read_archive_body(archive, member["member"], normalized))
                        candidate_evidence[candidate_key].append(candidate)
                    continue
                if (key, field) in seen:
                    continue
                seen.add((key, field))
                zip_entry = record.get("zip_entry") or record.get("object_entry") or record.get("object_path")
                zip_part = record.get("zip_part") or record.get("zip_file") or record.get("archive")
                archive = safe_archive_for_manifest(manifest, zip_part)
                member = archive_member_info(archive, str(zip_entry), zip_cache) if archive is not None and isinstance(zip_entry, str) else None
                rec: dict[str, Any] = {"kind": "manifest", "manifest": rel(manifest), "line": line_no, "matched_field": field, "normalized": normalized, "status": record.get("status"), "http_status": status_number(record), "content_type": content_type(record), "role": record.get("role"), "sha256": record.get("sha256"), "content_length": record.get("content_length") or record.get("length"), "zip_part": rel(archive) if archive else None, "zip_entry": zip_entry, "archive_member": member}
                if member and archive and member.get("file_size", 0) <= MAX_BODY_READ and not member.get("encrypted") and not member.get("symlink"):
                    body_key = (str(archive.resolve()), member["member"])
                    rec["body"] = body_cache.setdefault(body_key, read_archive_body(archive, member["member"], normalized or item["target"]))
                evidence[key].append(rec)
    stats["manifest_records"] = mstats["records"]; stats["manifest_json_errors"] = mstats["json_errors"]

    # Acquisition catalog/index evidence.  These records prove a path was
    # mentioned, but are never treated as an entity without bytes.
    catalog_root = ROOT / "research/acquisition-2008"
    catalog_paths = sorted(p for p in catalog_root.rglob("*.json") if CATALOG_NAME_RE.search(p.name)) if catalog_root.is_dir() else []
    for path in catalog_paths:
        stats["catalog_files"] += 1; stats["catalog_bytes"] += path.stat().st_size
        try:
            value = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, json.JSONDecodeError):
            stats["catalog_json_errors"] += 1; continue
        for pointer, field, text in iter_strings(value):
            normalized = norm_path(text)
            key = by_variant.get(normalized)
            if not key:
                continue
            evidence[key].append({"kind": "catalog", "file": rel(path), "pointer": pointer, "field": field, "normalized": normalized, "value": text.split("?", 1)[0][:500]})

    # Central directories of the four small source archives and all ZIPs under
    # the nine named historical backup roots.  No member is extracted here.
    archive_paths: list[tuple[Path, str]] = []
    for relative in SOURCE_ZIPS:
        archive_paths.append((ROOT / relative, "source_zip"))
    for relative in BACKUP_ROOTS:
        root = ROOT / relative
        if root.is_dir():
            archive_paths.extend((path, "historical_backup_zip") for path in root.rglob("*.zip") if path.is_file())
    for archive, archive_kind in sorted(set(archive_paths), key=lambda pair: str(pair[0])):
        stats["central_archives"] += 1; stats["central_archive_bytes"] += archive.stat().st_size if archive.is_file() else 0
        if not archive.is_file():
            continue
        try:
            with zipfile.ZipFile(archive, "r") as handle:
                infos = handle.infolist()
        except (OSError, zipfile.BadZipFile):
            stats["central_bad_archives"] += 1; continue
        stats["central_entries"] += len(infos)
        for info in infos:
            if info.is_dir() or not safe_zip_member(info.filename):
                continue
            normalized = norm_path(info.filename)
            exact_key = by_variant.get(normalized)
            base_keys = basename_to_keys.get(Path(info.filename).name.lower(), set())
            for key in base_keys:
                item = targets[key]
                is_exact = exact_key == key and normalized in variants(item["target"])
                member = {"kind": archive_kind, "archive": rel(archive), "member": info.filename, "normalized": normalized, "file_size": info.file_size, "compress_size": info.compress_size, "crc32": f"{info.CRC:08x}", "date_time": list(info.date_time), "encrypted": bool(info.flag_bits & 0x1), "symlink": stat.S_ISLNK((info.external_attr >> 16) & 0xFFFF), "exact_route": is_exact}
                if is_exact:
                    stats["central_exact_matches"] += 1
                    if info.file_size <= MAX_BODY_READ and not member["encrypted"] and not member["symlink"]:
                        body_key = (str(archive.resolve()), info.filename)
                        member["body"] = body_cache.setdefault(body_key, read_archive_body(archive, info.filename, item["target"]))
                    evidence[key].append(member)
                else:
                    candidate_evidence[key].append({"kind": "archive_basename_candidate", "archive": rel(archive), "member": info.filename, "normalized": normalized, "file_size": info.file_size, "compress_size": info.compress_size, "crc32": f"{info.CRC:08x}", "date_time": list(info.date_time), "archive_layer": archive_kind})
                    stats["central_basename_candidates"] += 1

    def classify(key: str) -> str:
        item = targets[key]; rows = evidence.get(key, []); candidates = candidate_evidence.get(key, [])
        valid = []
        for row in rows:
            if row.get("kind") == "direct_file" and row.get("exact_route") and row.get("nonempty") is not False:
                valid.append(row)
            elif row.get("body", {}).get("body_read") and row.get("body", {}).get("nonempty", True) is not False:
                body = row["body"]
                if item["kind"] in {"image", "css", "swf", "script", "link"}:
                    if item["kind"] == "image" and body.get("image_valid") is not True:
                        continue
                    if item["kind"] == "swf" and body.get("swf_valid") is not True:
                        continue
                valid.append(row)
        if valid:
            if item["kind"] == "image": return "exact_usable_image"
            if item["kind"] == "css": return "exact_usable_css"
            if item["kind"] == "swf": return "exact_usable_swf"
            return "exact_usable_text_or_script"
        if rows:
            manifest_or_catalog = any(row.get("kind") in {"manifest", "catalog"} for row in rows)
            if manifest_or_catalog:
                return "metadata_only_or_unvalidated"
            return "matched_member_unread_or_invalid"
        if candidates:
            return "different_path_candidate_only"
        return "not_found_in_scanned_layers"

    output_targets: list[dict[str, Any]] = []
    class_counts: Counter[str] = Counter()
    for key, item in sorted(targets.items(), key=lambda pair: (pair[1]["target"], pair[1]["kind"])):
        classification = classify(key); class_counts[classification] += 1
        unique_candidates: list[dict[str, Any]] = []
        seen_candidates: set[tuple[Any, Any, Any]] = set()
        for candidate in candidate_evidence.get(key, []):
            body = candidate.get("body") or {}
            candidate_path = candidate.get("normalized") or candidate.get("normalized_path") or candidate.get("member") or candidate.get("path")
            candidate_sha = candidate.get("sha256") or body.get("sha256") or candidate.get("crc32")
            candidate_length = candidate.get("content_length") or candidate.get("length") or candidate.get("file_size") or body.get("length")
            dedupe_key = (candidate_path, candidate_sha, candidate_length)
            if dedupe_key in seen_candidates:
                continue
            seen_candidates.add(dedupe_key)
            unique_candidates.append(candidate)
        output_targets.append({
            "target": item["target"], "kind": item["kind"], "pages": item["pages"], "raw_urls": item["raw_urls"], "source_lines": item["lines"], "contexts": item["contexts"], "uses": item["uses"], "classification": classification,
            "exact_or_metadata_evidence": evidence.get(key, []), "different_path_candidates": unique_candidates[:50],
            "candidate_count_truncated": max(0, len(unique_candidates) - 50),
        })

    # A compact companion index makes the useful same-basename leads easier to
    # review without treating them as exact-route recovery candidates.
    validated_candidates: list[dict[str, Any]] = []
    for item in output_targets:
        for candidate in item["different_path_candidates"]:
            body = candidate.get("body") or {}
            validation = body if body.get("body_read") else candidate
            valid = bool(validation.get("image_valid") is True or validation.get("swf_valid") is True or validation.get("nonempty") is True)
            if not valid:
                continue
            validated_candidates.append({
                "requested_target": item["target"], "kind": item["kind"],
                "candidate_path": candidate.get("normalized") or candidate.get("normalized_path") or candidate.get("member") or candidate.get("path"),
                "source": candidate.get("manifest") or candidate.get("archive") or candidate.get("path"),
                "member": candidate.get("zip_entry") or candidate.get("member"),
                "mime": candidate.get("content_type") or validation.get("mime"),
                "length": candidate.get("content_length") or candidate.get("length") or candidate.get("file_size") or validation.get("length"),
                "sha256": candidate.get("sha256") or validation.get("sha256"),
                "format": validation.get("format"), "width": validation.get("width"), "height": validation.get("height"), "frames": validation.get("frames"),
                "image_valid": validation.get("image_valid"), "swf_valid": validation.get("swf_valid"),
            })

    free = shutil.disk_usage(ROOT).free
    if free < FREE_FLOOR:
        raise RuntimeError(f"D free-space floor violated before write: {free}")
    OUT.mkdir(parents=True, exist_ok=True)
    finished = utc_now()
    payload = {
        "schema": "source16-original-resource-audit/v1", "startedUtc": started, "finishedUtc": finished,
        "scope": {"dependency_input": rel(DEP_JSON), "dependency_csv": rel(DEP_CSV), "static_missing_count": static_count, "dynamic_missing_swf_count": swf_count, "unique_targets": len(output_targets), "network": "not used", "body_policy": "ZIP central directories first; only exact matched member/direct file at or below 64 MiB was read", "excluded": ["frozen Source16/v42/v43 site modification", "full historical ZIP extraction", "network/CDX/Wayback", "unrelated HTML/script body scans"]},
        "layers_checked": {"docs": ["docs/acquisition-2008.md", "docs/archive-method.md"], "backup_roots": backup_inventory, "manifest_files": [rel(p) for p in sorted(set(manifest_paths))], "manifest_stats": {"files": stats["manifest_files"], "bytes": stats["manifest_bytes"], "records": stats["manifest_records"], "json_errors": stats["manifest_json_errors"]}, "catalog_files_count": stats["catalog_files"], "catalog_bytes": stats["catalog_bytes"], "catalog_json_errors": stats["catalog_json_errors"], "direct_exact_roots": [rel(root) for root, _ in direct_roots], "source_zips": [{"path": rel(ROOT / p), "exists": (ROOT / p).is_file(), "bytes": (ROOT / p).stat().st_size if (ROOT / p).is_file() else None} for p in SOURCE_ZIPS], "historical_zip_central_directory": {"archives": stats["central_archives"], "archive_bytes": stats["central_archive_bytes"], "entries": stats["central_entries"], "bad_archives": stats["central_bad_archives"], "exact_member_matches": stats["central_exact_matches"], "same_basename_candidates": stats["central_basename_candidates"]}, "direct_search": {"files_checked": stats["direct_files_checked"], "exact_hits": stats["direct_exact_hits"], "same_basename_candidates": stats["direct_basename_candidates"]}},
        "classification_counts": dict(class_counts), "targets": output_targets,
        "notes": ["An exact usable classification requires bytes from a direct file or exact ZIP member and image/SWF validation where applicable.", "Catalog or manifest path/status/hash references without a readable body remain metadata_only_or_unvalidated.", "Same-basename members/files at a different path are candidates only; they are not substituted for the requested route.", "This is a scoped local-layer result, not a claim about all historical sources."]
    }
    (OUT / "curated-inventory.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "candidate-summary.json").write_text(json.dumps({
        "schema": "source16-original-resource-candidates/v1", "validated_candidate_pairs": len(validated_candidates),
        "validated_candidate_targets": len({row["requested_target"] for row in validated_candidates}), "candidates": validated_candidates,
        "note": "Candidates share a basename but have a different normalized path; they are source leads only and are not exact-route substitutions.",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = ["target", "kind", "classification", "pages", "raw_urls", "source_lines", "evidence_count", "candidate_count"]
    with (OUT / "curated-inventory.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for item in output_targets:
            writer.writerow({"target": item["target"], "kind": item["kind"], "classification": item["classification"], "pages": ";".join(item["pages"]), "raw_urls": ";".join(item["raw_urls"]), "source_lines": ";".join(item["source_lines"]), "evidence_count": len(item["exact_or_metadata_evidence"]), "candidate_count": len(item["different_path_candidates"])})
    (OUT / "README.md").write_text(
        "# Source16 original-resource audit\n\n"
        f"审计时间 `{started}`–`{finished}`；输入为 Source16 dependency-audit 的 `{static_count}` 个静态 `local_missing` 和 `{swf_count}` 个动态 `bard_idle.swf`。本批只读本地 acquisition metadata、命名 backup manifests、两个 direct raw roots、四个小 Source ZIP 及九个历史备份根的 ZIP 中央目录；没有联网、没有解压历史 ZIP、没有改 Source16/v42/v43。\n\n"
        f"分类计数：`{dict(class_counts)}`。本批没有 exact-route 可恢复实体；`candidate-summary.json` 中有 `{len(validated_candidates)}` 个跨路径同 basename 候选对（涉及 `{len({row['requested_target'] for row in validated_candidates})}` 个目标），其中图片候选已用实际字节和 PIL 解码核验。它们只作为地区/同主题来源线索，不替代精确目标。\n\n"
        "`curated-inventory.json` 保留每个目标的来源页、原始使用行、证据层、长度/SHA/CRC/图片验证和候选；`curated-inventory.csv` 为精简索引。结果是已列本地层的范围性审计，不推断未查网络来源。\n",
        encoding="utf-8",
    )
    print(json.dumps({"targets": len(output_targets), "static": static_count, "dynamic_swf": swf_count, "classification_counts": dict(class_counts), "stats": stats, "output": rel(OUT)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
