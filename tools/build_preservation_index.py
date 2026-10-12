"""Build a local preservation index from manifests, ZIP objects, and raw caches.

This is an offline bookkeeping and integrity tool.  It never follows URLs or
executes preserved content.  The index is deliberately capture-oriented:
multiple captures of one logical URL remain attached as evidence, while the
preferred map selects one valid capture for a 2010-consistent rendering.
"""

from __future__ import annotations

import argparse
import datetime as _datetime
import hashlib
import html
import json
import re
import urllib.parse
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


ANCHOR = "20101203214958"
ANCHOR_DATE = ANCHOR[:8]
PREFERRED_CUTOFF = "20101203235959"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".gif", ".png", ".swf", ".webp"}
CACHE_KINDS = {"js", "css", "xsl"}
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _rel(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} is not an object")
        value["_line_number"] = line_number
        records.append(value)
    return records


def _canonical_url(value: str) -> str:
    """Normalize only URL spelling that does not change the origin resource."""

    value = str(value or "")
    parsed = urllib.parse.urlsplit(value)
    if not parsed.scheme or not parsed.netloc:
        return value
    hostname = (parsed.hostname or "").lower()
    try:
        port = parsed.port
    except ValueError:
        port = None
    netloc = hostname
    if parsed.username is not None:
        user = urllib.parse.quote(parsed.username, safe="")
        password = ""
        if parsed.password is not None:
            password = ":" + urllib.parse.quote(parsed.password, safe="")
        netloc = f"{user}{password}@{netloc}"
    if port is not None and not (
        (parsed.scheme.lower() == "http" and port == 80)
        or (parsed.scheme.lower() == "https" and port == 443)
    ):
        netloc += f":{port}"
    return urllib.parse.urlunsplit(
        (parsed.scheme.lower(), netloc, parsed.path or "/", parsed.query, parsed.fragment)
    )


def _timestamp(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    match = re.search(r"(?<!\d)(\d{14})(?!\d)", text)
    if match:
        return match.group(1)
    for fmt in (
        "%a, %d %b %Y %H:%M:%S GMT",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
    ):
        try:
            parsed = _datetime.datetime.strptime(text, fmt)
            return parsed.strftime("%Y%m%d%H%M%S")
        except ValueError:
            continue
    return None


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _title(data: bytes) -> str | None:
    sample = data[:128 * 1024].decode("utf-8", errors="ignore")
    match = re.search(r"<title\b[^>]*>(.*?)</title\s*>", sample, re.I | re.S)
    if not match:
        return None
    return html.unescape(re.sub(r"\s+", " ", match.group(1)).strip())


def _magic(data: bytes, extension: str) -> tuple[bool | None, str]:
    extension = extension.casefold()
    if extension in {".jpg", ".jpeg"}:
        return data.startswith(b"\xff\xd8\xff"), "jpeg"
    if extension == ".gif":
        return data.startswith((b"GIF87a", b"GIF89a")), "gif"
    if extension == ".png":
        return data.startswith(PNG_MAGIC), "png"
    if extension == ".swf":
        return data.startswith((b"FWS", b"CWS", b"ZWS")), "swf"
    if extension == ".webp":
        return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP", "webp"
    return None, "unclassified"


def _error_title(title: str | None) -> bool:
    if not title:
        return False
    lower = title.casefold()
    return (
        "404" in lower
        or "not found" in lower
        or "page cannot be found" in lower
        or "error" in lower and "world of warcraft" in lower
    )


def _guide_title(title: str | None) -> bool:
    if not title:
        return False
    lower = title.casefold()
    return "world of warcraft" in lower and any(
        marker in lower for marker in ("beginner", "game guide", "guide")
    )


def _looks_like_html(data: bytes) -> bool:
    """Recognize an HTML error/guide response without treating XML/XSL as HTML."""

    sample = data[:128 * 1024].decode("utf-8", errors="ignore")
    sample = sample.lstrip("\ufeff \t\r\n")
    # A small leading comment is common in hand-authored HTML.  Keep the
    # check deliberately prefix-based so an XSL stylesheet containing a
    # literal-result <html> element is still accepted as XSL.
    while sample.startswith("<!--"):
        end = sample.find("-->", 4)
        if end < 0:
            break
        sample = sample[end + 3 :].lstrip(" \t\r\n")
    return bool(re.match(r"^<!doctype\s+html\b", sample, re.I) or re.match(r"^<(?:html|head|body)\b", sample, re.I))


def _body_status(data: bytes, original: str, role: str | None) -> dict[str, Any]:
    extension = Path(urllib.parse.urlsplit(original).path).suffix.casefold()
    image_ext = extension in IMAGE_EXTENSIONS
    script_style_ext = extension in {".js", ".css", ".xsl"}
    magic_ok, magic_type = _magic(data, extension)
    title = _title(data)
    error_title = _error_title(title)
    guide_title = _guide_title(title)
    html_body = _looks_like_html(data)
    if image_ext and magic_ok is True:
        status = "valid_entity"
    elif error_title:
        status = "soft404"
    elif script_style_ext and guide_title:
        status = "generic_guide"
    elif script_style_ext and html_body:
        status = "invalid_nonimage"
    elif image_ext and guide_title:
        status = "generic_guide"
    elif image_ext and magic_ok is False:
        status = "invalid_image"
    else:
        status = "valid_entity"
    return {
        "status": status,
        "extension": extension,
        "magic_type": magic_type,
        "magic_ok": magic_ok,
        "title": title,
        "error_page_title": error_title,
        "generic_guide_title": guide_title,
        "html_body": html_body,
        "bytes": len(data),
        "role": role,
    }


def _scope_for_role(role: str | None, source: str = "") -> str:
    if "core-gap" in source or "core_gap" in source:
        return "core_gap"
    if "navigation-images" in source:
        return "dependency_discovered"
    if role == "core":
        return "core_page"
    if role in {"core_image", "core_dependency"}:
        return "core_asset"
    if role in {"shared_image", "shared_dependency"}:
        if "shared-assets-plan" in source or "shared-recovery" in source or "menu-dependencies" in source:
            return "shared"
        return "shared"
    if role == "unresolved_dependency":
        return "unresolved_dependency"
    return "unclassified"


def _scope_for_plan_ref(ref: dict[str, Any], core_asset_logicals: set[str]) -> str:
    """Classify plan provenance without turning the raw dependency closure into
    extra core-asset or shared-cache logical URLs.

    ``dependencies/plan.json`` contains a deliberately broad closure.  Its
    JS/CSS/XSL records are the raw cache, while two discovered core images are
    outside the 58-item encyclopedia asset plan.  The dedicated plans remain
    authoritative for those scope boundaries.
    """

    source = str(ref.get("source", ""))
    role = ref.get("role")
    logical = str(ref.get("logical_url", ""))
    kind = str(ref.get("kind", "")).casefold()
    if "core-gap" in source or "core_gap" in source:
        return "core_gap"
    if "navigation-images" in source:
        return "dependency_discovered"
    if source == "research/core-plan.json" or role == "core":
        return "core_page"
    if source == "research/encyclopedia-assets-plan.json":
        if role in {"core_image", "core_dependency"}:
            return "core_asset"
    if source == "research/dependencies/plan.json":
        if role in {"shared_dependency", "core_dependency"} and kind in CACHE_KINDS:
            return "dependency_cache"
        if role == "core_image" and logical not in core_asset_logicals:
            return "dependency_discovered"
        if role in {"core_image", "core_dependency"}:
            return "core_asset"
    if role in {"shared_image", "shared_dependency"}:
        return "shared"
    return _scope_for_role(str(role) if role else None, source)


def _temporal_class(actual: str | None, scope: str, allow_same_day: bool = False) -> str:
    if actual is None:
        return "unknown"
    if actual <= ANCHOR:
        return "anchor_consistent"
    if allow_same_day and ANCHOR < actual <= PREFERRED_CUTOFF:
        return "same_day_core_supplement"
    return "temporal_supplement"


def _read_zip_bytes(zip_path: Path, entry: str) -> bytes | None:
    try:
        with zipfile.ZipFile(zip_path, "r", allowZip64=True) as archive:
            return archive.read(entry)
    except (OSError, KeyError, zipfile.BadZipFile):
        return None


def _plan_ref(path: Path, item: dict[str, Any], root: Path) -> dict[str, Any]:
    ref: dict[str, Any] = {
        "source": _rel(root, path),
        "original": str(item.get("original", "")),
        "logical_url": _canonical_url(str(item.get("original", ""))),
        "timestamp": str(item.get("timestamp", "")),
        "role": item.get("role"),
    }
    for key in (
        "kind",
        "cdx_digest",
        "expected_title",
        "source_plan",
        "target_output",
        "recovery_reason",
        "reason",
        "comparison_sha256",
        "later_actual_timestamp",
    ):
        if key in item:
            ref[key] = item[key]
    if "source" in item:
        # ``source`` on the ref is the plan file; retain an item's own
        # provenance separately for historical/gap plans.
        ref["item_source"] = item["source"]
    return ref


def _plan_items(path: Path) -> list[dict[str, Any]]:
    """Read only a plan's ``items`` schema; ignore summaries and errors."""

    try:
        obj = _load_json(path, {}) or {}
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(obj, dict) or not isinstance(obj.get("items"), list):
        return []
    result: list[dict[str, Any]] = []
    for item in obj["items"]:
        if not isinstance(item, dict):
            continue
        # These fields distinguish a request-plan item from summary/error
        # records that may happen to be stored beside it.
        if not item.get("original") or not item.get("timestamp") or not item.get("role"):
            continue
        result.append(item)
    return result


def _load_plans(root: Path) -> tuple[
    list[dict[str, Any]], list[Path], list[Path], list[Path]
]:
    core_path = root / "research" / "core-plan.json"
    asset_path = root / "research" / "encyclopedia-assets-plan.json"
    dependency_path = root / "research" / "dependencies" / "plan.json"
    plan_refs: list[dict[str, Any]] = []
    shared_plan_paths: list[Path] = []
    supplemental_plan_paths: list[Path] = []
    seen_paths: set[Path] = set()

    def add_plan(path: Path, bucket: list[Path] | None = None) -> None:
        if not path.exists():
            return
        resolved = path.resolve()
        if resolved in seen_paths:
            return
        seen_paths.add(resolved)
        if bucket is not None:
            bucket.append(path)
        for item in _plan_items(path):
            plan_refs.append(_plan_ref(path, item, root))

    for path in (core_path, asset_path, dependency_path):
        add_plan(path)

    research = root / "research"
    shared_paths = sorted(research.glob("shared-assets-plan-*.json"))
    menu_path = research / "menu-dependencies-plan.json"
    if menu_path.exists():
        shared_paths.append(menu_path)
    menu_images_path = research / "menu-images-plan.json"
    if menu_images_path.exists():
        shared_paths.append(menu_images_path)
    recovery = root / "backups" / "20101203" / "shared-recovery-plan.json"
    if recovery.exists():
        shared_paths.append(recovery)
    for path in shared_paths:
        add_plan(path, shared_plan_paths)

    # These plans are evidence/provenance inputs, but their URLs remain
    # deduplicated in the logical map.  The historical six therefore add
    # source refs without inflating logical URL counts.
    for path in (
        research / "historical-static-plan.json",
        research / "core-gap-recheck-plan.json",
        research / "navigation-images-plan.json",
    ):
        add_plan(path, supplemental_plan_paths)

    # Download workers may leave additional bounded recovery plans under the
    # backup root.  Inspect only files whose JSON has valid request items;
    # summary/errors documents are intentionally ignored.
    backup_root = root / "backups" / "20101203"
    for path in sorted(backup_root.rglob("*plan*.json")):
        add_plan(path, supplemental_plan_paths)

    return (
        plan_refs,
        shared_plan_paths,
        [core_path, asset_path, dependency_path],
        supplemental_plan_paths,
    )


def _load_validation(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    asset = _load_json(root / "research" / "encyclopedia-assets-validation.json", {}) or {}
    core = _load_json(root / "research" / "validation" / "core-validation.json", {}) or {}
    return asset, core


def _scan_zip_objects(root: Path) -> tuple[list[dict[str, Any]], dict[tuple[str, str], bytes], list[str]]:
    volumes: list[dict[str, Any]] = []
    bytes_by_location: dict[tuple[str, str], bytes] = {}
    errors: list[str] = []
    for zip_path in sorted((root / "backups" / "20101203").rglob("objects-*.zip")):
        volume: dict[str, Any] = {
            "zip_file": _rel(root, zip_path),
            "entry_count": 0,
            "crc_ok": False,
            "sha_named_entries_ok": True,
            "errors": [],
        }
        try:
            with zipfile.ZipFile(zip_path, "r", allowZip64=True) as archive:
                infos = archive.infolist()
                volume["entry_count"] = len(infos)
                bad = archive.testzip()
                if bad is not None:
                    message = f"{_rel(root, zip_path)}:CRC failure:{bad}"
                    volume["errors"].append(message)
                else:
                    volume["crc_ok"] = True
                seen: set[str] = set()
                for info in infos:
                    if info.filename in seen:
                        message = f"{_rel(root, zip_path)}:duplicate entry:{info.filename}"
                        volume["errors"].append(message)
                    seen.add(info.filename)
                    try:
                        data = archive.read(info.filename)
                    except (OSError, KeyError, zipfile.BadZipFile) as exc:
                        message = f"{_rel(root, zip_path)}:{info.filename}:read error:{exc}"
                        volume["errors"].append(message)
                        continue
                    location = (_rel(root, zip_path), info.filename)
                    bytes_by_location[location] = data
                    actual = _sha256(data)
                    name_match = re.fullmatch(r"objects/([0-9a-f]{64})\.bin", info.filename)
                    if name_match is None or name_match.group(1) != actual:
                        volume["sha_named_entries_ok"] = False
                        message = f"{_rel(root, zip_path)}:{info.filename}:SHA name mismatch:{actual}"
                        volume["errors"].append(message)
        except (OSError, zipfile.BadZipFile) as exc:
            message = f"{_rel(root, zip_path)}:ZIP open error:{exc}"
            volume["errors"].append(message)
        if volume["errors"]:
            errors.extend(volume["errors"])
        volumes.append(volume)
    return volumes, bytes_by_location, errors


def _manifest_paths(root: Path) -> list[Path]:
    return sorted((root / "backups" / "20101203").rglob("manifest.jsonl"))


def _manifest_capture(
    root: Path,
    source: Path,
    record: dict[str, Any],
    line_number: int,
    plan_by_logical: dict[str, list[dict[str, Any]]],
    bytes_by_location: dict[tuple[str, str], bytes],
) -> tuple[dict[str, Any] | None, str | None]:
    if record.get("status") != "success":
        return None, None
    original = str(record.get("original", ""))
    logical = _canonical_url(original)
    role = str(record.get("role") or "")
    scope = _scope_for_role(role, _rel(root, source))
    zip_part = str(record.get("zip_part", ""))
    zip_entry = str(record.get("zip_entry", ""))
    zip_path = source.parent / zip_part
    zip_location = (_rel(root, zip_path), zip_entry)
    data = bytes_by_location.get(zip_location)
    integrity: dict[str, Any] = {
        "zip_file": _rel(root, zip_path),
        "zip_entry": zip_entry,
        "sha256_matches_manifest": None,
        "length_matches_manifest": None,
        "object_present": data is not None,
    }
    if data is not None:
        integrity["sha256_matches_manifest"] = _sha256(data) == record.get("sha256")
        try:
            integrity["length_matches_manifest"] = len(data) == int(record.get("content_length"))
        except (TypeError, ValueError):
            integrity["length_matches_manifest"] = False
        body = _body_status(data, original, role)
    else:
        body = {
            "status": "unverified",
            "extension": Path(urllib.parse.urlsplit(original).path).suffix.casefold(),
            "magic_type": "unverified",
            "magic_ok": None,
            "title": None,
            "error_page_title": None,
            "generic_guide_title": None,
            "html_body": None,
            "bytes": None,
            "role": role,
        }
    actual = _timestamp(record.get("actual_timestamp")) or _timestamp(record.get("memento_datetime"))
    allow_same_day = scope == "core_asset"
    capture_id = f"manifest:{_rel(root, source)}:{line_number}"
    capture = {
        "capture_id": capture_id,
        "source_kind": "zip_manifest",
        "source_manifest": _rel(root, source),
        "manifest_line": line_number,
        "original": original,
        "logical_url": logical,
        "role": role,
        "scope": scope,
        "requested_timestamp": str(record.get("requested_timestamp", "")),
        "actual_timestamp": actual,
        "actual_timestamp_raw": record.get("actual_timestamp"),
        "actual_url": record.get("actual_url"),
        "memento_datetime": record.get("memento_datetime"),
        "http_status": record.get("http_status"),
        "sha256": record.get("sha256"),
        "content_length": record.get("content_length"),
        "temporal_class": _temporal_class(actual, scope, allow_same_day),
        "content": body,
        "object": {
            "sha256": record.get("sha256"),
            "zip_file": _rel(root, zip_path),
            "zip_entry": zip_entry,
        },
        "integrity": integrity,
        "plan_roles": sorted({str(ref.get("role")) for ref in plan_by_logical.get(logical, [])}),
    }
    return capture, capture_id


def _load_manifests(
    root: Path,
    plan_by_logical: dict[str, list[dict[str, Any]]],
    bytes_by_location: dict[tuple[str, str], bytes],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    captures: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for source in _manifest_paths(root):
        for record in _load_jsonl(source):
            records.append(record)
            line_number = int(record.pop("_line_number", 0))
            if record.get("status") == "success":
                capture, _ = _manifest_capture(root, source, record, line_number, plan_by_logical, bytes_by_location)
                if capture is not None:
                    captures.append(capture)
            else:
                failure = {
                    "failure_id": f"manifest-failure:{_rel(root, source)}:{line_number}",
                    "source_manifest": _rel(root, source),
                    "manifest_line": line_number,
                    "original": record.get("original"),
                    "logical_url": _canonical_url(str(record.get("original", ""))),
                    "role": record.get("role"),
                    "requested_timestamp": record.get("requested_timestamp"),
                    "status": record.get("status"),
                    "failure_reason": record.get("failure_reason") or record.get("error"),
                    "attempts": record.get("attempts"),
                }
                failures.append(failure)
    return captures, failures, records


def _cache_records(
    root: Path,
    dependency_plan: dict[str, Any],
    plan_by_logical: dict[str, list[dict[str, Any]]],
    core_asset_logicals: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    dependency_dir = root / "research" / "dependencies"
    fetch_records = list(dependency_plan.get("fetch_records", []))
    cache: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    raw_meta_paths = sorted((dependency_dir / "raw").glob("*.meta.json"))
    meta_by_raw: dict[str, tuple[Path, dict[str, Any]]] = {}
    for meta_path in raw_meta_paths:
        try:
            meta = _load_json(meta_path, {}) or {}
        except (OSError, json.JSONDecodeError) as exc:
            failures.append({"source_meta": _rel(root, meta_path), "error": f"metadata parse error:{exc}"})
            continue
        raw_file = str(meta.get("raw_file", ""))
        meta_by_raw[raw_file.replace("\\", "/")] = (meta_path, meta)

    referenced_raw: set[str] = set()
    for index, fetch in enumerate(fetch_records):
        original = str(fetch.get("original", ""))
        logical = _canonical_url(original)
        kind = str(fetch.get("kind", "")).casefold()
        raw_file = str(fetch.get("raw_file", "")).replace("\\", "/")
        referenced_raw.add(raw_file)
        meta_entry = meta_by_raw.get(raw_file)
        meta_path = meta_entry[0] if meta_entry else None
        raw_meta = meta_entry[1] if meta_entry else {}
        raw_path = dependency_dir / raw_file
        raw_exists = raw_path.is_file()
        raw_data = raw_path.read_bytes() if raw_exists else None
        raw_sha = _sha256(raw_data) if raw_data is not None else None
        status = fetch.get("status")
        body_check = fetch.get("body_check") or {}
        content_check = (
            _body_status(raw_data, original, str(fetch.get("role") or "shared_dependency"))
            if raw_data is not None
            else None
        )
        invalid_content_statuses = {"soft404", "generic_guide", "invalid_nonimage", "invalid_image"}
        invalid_content = bool(content_check and content_check.get("status") in invalid_content_statuses)
        valid = (
            status == 200
            and kind in CACHE_KINDS
            and raw_exists
            and raw_sha == fetch.get("sha256")
            and raw_sha == raw_meta.get("sha256", raw_sha)
            and not body_check.get("archive_error")
            and not invalid_content
        )
        scope = "core_asset" if logical in core_asset_logicals else "dependency_cache"
        actual = _timestamp(fetch.get("actual_timestamp")) or _timestamp(fetch.get("memento_datetime"))
        role = str(fetch.get("role") or "shared_dependency")
        cache_entry = {
            "cache_id": f"cache:{index + 1}",
            "original": original,
            "logical_url": logical,
            "kind": kind,
            "role": role,
            "scope": scope,
            "status": "valid_cache" if valid else "unverified_cache",
            "http_status": status,
            "requested_timestamp": fetch.get("selected_timestamp"),
            "actual_timestamp": actual,
            "actual_timestamp_raw": fetch.get("actual_timestamp"),
            "memento_datetime": fetch.get("memento_datetime"),
            "sha256": fetch.get("sha256"),
            "bytes": fetch.get("bytes"),
            "raw_file": _rel(root, raw_path) if raw_exists else None,
            "raw_meta": _rel(root, meta_path) if meta_path else None,
            "raw_sha256": raw_sha,
            "source_fetch_record": {"plan": "research/dependencies/plan.json", "index": index},
            "body_check": body_check,
            "content_check": content_check,
            "duplicate_of_core_asset": logical in core_asset_logicals,
            "counted_in_shared_cache": bool(valid and logical not in core_asset_logicals),
            "temporal_class": _temporal_class(actual, scope, scope == "core_asset"),
        }
        cache.append(cache_entry)
        if not valid:
            failures.append({
                "source_fetch_record": {"plan": "research/dependencies/plan.json", "index": index},
                "source_meta": _rel(root, meta_path) if meta_path else None,
                "original": original,
                "logical_url": logical,
                "status": status,
                "kind": kind,
                "error": fetch.get("error") or body_check.get("verdict") or (
                    f"invalid content:{content_check.get('status')}" if invalid_content else None
                ),
            })

    raw_evidence: list[dict[str, Any]] = []
    for raw_file, (meta_path, meta) in sorted(meta_by_raw.items()):
        raw_path = dependency_dir / raw_file
        exists = raw_path.is_file()
        sha = _sha256(raw_path.read_bytes()) if exists else None
        raw_evidence.append({
            "raw_evidence_id": f"raw:{_rel(root, meta_path)}",
            "original": meta.get("original"),
            "logical_url": _canonical_url(str(meta.get("original", ""))),
            "status": meta.get("status"),
            "raw_file": _rel(root, raw_path) if exists else None,
            "meta_file": _rel(root, meta_path),
            "sha256": meta.get("sha256"),
            "raw_sha256": sha,
            "bytes": meta.get("bytes"),
            "referenced_by_fetch_record": raw_file in referenced_raw,
            "sha_matches_metadata": bool(exists and sha == meta.get("sha256")),
        })
    first_raw_by_key: dict[tuple[str, str | None], str] = {}
    for evidence in raw_evidence:
        key = (str(evidence.get("logical_url", "")), evidence.get("raw_sha256"))
        previous = first_raw_by_key.get(key)
        if previous is not None:
            evidence["duplicate_of_raw_evidence"] = previous
        else:
            evidence["duplicate_of_raw_evidence"] = None
            first_raw_by_key[key] = str(evidence["raw_evidence_id"])
    return cache, failures, raw_evidence


def _image_validation_map(asset_validation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in asset_validation.get("items", []):
        if isinstance(item, dict):
            result[_canonical_url(str(item.get("original", "")))] = item
    return result


def _failure_map(failures: Iterable[dict[str, Any]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    for failure in failures:
        logical = str(failure.get("logical_url", ""))
        if logical:
            failure_id = str(failure.get("failure_id") or failure.get("source_fetch_record") or "failure")
            result[logical].append(failure_id)
    return result


def _preferred(captures: list[dict[str, Any]]) -> dict[str, Any] | None:
    eligible = [
        capture
        for capture in captures
        if capture.get("content", {}).get("status") == "valid_entity"
        and capture.get("temporal_class") in {"anchor_consistent", "same_day_core_supplement"}
    ]
    if not eligible:
        return None
    eligible.sort(
        key=lambda capture: (
            1 if capture.get("temporal_class") == "anchor_consistent" else 0,
            str(capture.get("actual_timestamp") or ""),
            str(capture.get("capture_id")),
        ),
        reverse=True,
    )
    return eligible[0]


def _logical_state(captures: list[dict[str, Any]], pending: bool) -> str:
    valid = [c for c in captures if c.get("content", {}).get("status") == "valid_entity"]
    soft = [c for c in captures if c.get("content", {}).get("status") == "soft404"]
    guide = [c for c in captures if c.get("content", {}).get("status") == "generic_guide"]
    preferred = _preferred(captures)
    if preferred is not None:
        if soft or guide or any(c.get("temporal_class") == "temporal_supplement" for c in valid):
            return "valid_with_supplements"
        return "valid"
    if valid:
        return "temporal_supplement_only"
    if soft and not guide:
        return "soft404"
    if guide:
        return "generic_guide"
    if captures:
        return "unverified"
    if pending:
        return "partial_pending"
    return "unverified"


def _gap_records(root: Path, logicals: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    gap_path = root / "research" / "gaps" / "missing_image_probe.json"
    gap = _load_json(gap_path, {}) or {}
    by_url = {
        _canonical_url(str(item.get("original", ""))): item
        for item in gap.get("records", [])
        if isinstance(item, dict) and item.get("original")
    }
    gap_paths = [
        "http://www.worldofwarcraft.com/info/encyclopedia/images/featured/featured_textbg.png",
        "http://www.worldofwarcraft.com/info/encyclopedia/images/icons/SentientMortals.jpg",
        "http://www.worldofwarcraft.com/info/encyclopedia/images/articles/alleriawindrunner.jpg",
        "http://www.worldofwarcraft.com/info/encyclopedia/images/articles/cenarioncircle.jpg",
        "http://www.worldofwarcraft.com/info/encyclopedia/images/articles/malfurionstormrage.jpg",
    ]
    # Keep dynamically discovered JS image references visible as gaps without
    # promoting them into the primary 58-item asset batch.  The navigation
    # plan is scoped as dependency_discovered when it is loaded.
    for logical, logical_item in sorted(logicals.items()):
        path = urllib.parse.urlsplit(logical).path.casefold()
        if (
            logical not in {_canonical_url(value) for value in gap_paths}
            and logical_item.get("scope") in {"core_gap", "dependency_discovered"}
            and "core_image" in {str(role) for role in logical_item.get("roles", [])}
            and path.startswith("/info/encyclopedia/images/")
            and Path(path).suffix.casefold() in IMAGE_EXTENSIONS
        ):
            gap_paths.append(logical)
    result: list[dict[str, Any]] = []
    for original in gap_paths:
        logical = _canonical_url(original)
        item = logicals.get(logical)
        gap_item = by_url.get(logical)
        active_reference = not logical.endswith("/featured/featured_textbg.png")
        state = item.get("state") if item else "unverified"
        scope = item.get("scope") if item else "core_gap"
        result.append({
            "original": original,
            "logical_url": logical,
            "active_reference": active_reference,
            "is_gap": active_reference and state not in {"valid", "valid_with_supplements"},
            "state": state,
            "scope": scope,
            "capture_ids": item.get("capture_ids", []) if item else [],
            "plan_refs": item.get("plan_refs", []) if item else [],
            "evidence": {
                "probe_file": _rel(root, gap_path) if gap_path.exists() else None,
                "probe_conclusion": gap_item.get("conclusion") if gap_item else None,
                "cdx_rows": len(gap_item.get("cdx_rows", [])) if gap_item else None,
                "anchor_status": (gap_item.get("anchor") or {}).get("status") if gap_item else None,
                "anchor_final_url": (gap_item.get("anchor") or {}).get("final_url") if gap_item else None,
                "anchor_body_verdict": ((gap_item.get("anchor") or {}).get("body") or {}).get("verdict") if gap_item else None,
            },
        })
    maiev = _canonical_url("http://www.worldofwarcraft.com/info/encyclopedia/images/articles/maievshadowsong.jpg")
    result.append({
        "original": "http://www.worldofwarcraft.com/info/encyclopedia/images/articles/maievshadowsong.jpg",
        "logical_url": maiev,
        "active_reference": True,
        "is_gap": False,
        "state": logicals.get(maiev, {}).get("state", "unverified"),
        "scope": logicals.get(maiev, {}).get("scope", "core_asset"),
        "capture_ids": logicals.get(maiev, {}).get("capture_ids", []),
        "plan_refs": logicals.get(maiev, {}).get("plan_refs", []),
        "evidence": {"note": "Parent validation reported a valid 2007 capture; no duplicate gap probe was requested."},
    })
    return result


def build(root: Path, index_path: Path, summary_path: Path) -> tuple[dict[str, Any], dict[str, Any], int]:
    plan_refs, shared_plan_paths, required_plan_paths, supplemental_plan_paths = _load_plans(root)
    excluded_logicals = {
        _canonical_url("http://www.worldofwarcraft.com/rss.xml"),
        _canonical_url("http://www.worldofwarcraft.com/new-hp/layout/index.xml"),
        _canonical_url("http://www.worldofwarcraft.com/new-hp/layout/styles/stylesheet.css"),
    }
    excluded_references = [
        {
            "logical_url": logical,
            "reason": (
                "RSS alternate content excluded from encyclopedia presentation"
                if logical.endswith("/rss.xml")
                else "unresolved XSL document reference; archive response retained as evidence"
                if logical.endswith("/layout/index.xml")
                else "XSL relative-path parse false positive; resolved stylesheet is /info/encyclopedia/styles/stylesheet.css"
            ),
            "plan_refs": [ref for ref in plan_refs if ref["logical_url"] == logical],
        }
        for logical in sorted(excluded_logicals)
    ]
    active_plan_refs = [ref for ref in plan_refs if ref["logical_url"] not in excluded_logicals]
    plan_by_logical: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for ref in active_plan_refs:
        if ref["logical_url"]:
            plan_by_logical[ref["logical_url"]].append(ref)

    asset_validation, core_validation = _load_validation(root)
    asset_validation_by_logical = _image_validation_map(asset_validation)
    core_asset_logicals = {
        ref["logical_url"]
        for ref in active_plan_refs
        if ref.get("source") == "research/encyclopedia-assets-plan.json"
        and ref.get("role") in {"core_image", "core_dependency"}
    }
    core_dependency_logicals = {
        ref["logical_url"]
        for ref in active_plan_refs
        if ref.get("source") == "research/encyclopedia-assets-plan.json"
        and ref.get("role") == "core_dependency"
    }

    volumes, bytes_by_location, zip_errors = _scan_zip_objects(root)
    captures, manifest_failures, manifest_records = _load_manifests(
        root, plan_by_logical, bytes_by_location
    )
    dependency_plan = _load_json(root / "research" / "dependencies" / "plan.json", {}) or {}
    cache, cache_failures, raw_evidence = _cache_records(
        root, dependency_plan, plan_by_logical, core_dependency_logicals
    )
    cache_integrity_errors = [
        {
            "cache_id": entry.get("cache_id"),
            "logical_url": entry.get("logical_url"),
            "raw_file": entry.get("raw_file"),
            "expected_sha256": entry.get("sha256"),
            "actual_sha256": entry.get("raw_sha256"),
        }
        for entry in cache
        if entry.get("http_status") == 200
        and (
            not entry.get("raw_file")
            or entry.get("raw_sha256") != entry.get("sha256")
        )
    ]
    fetch_records = list(dependency_plan.get("fetch_records", []))
    raw_evidence_by_logical: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for evidence in raw_evidence:
        raw_evidence_by_logical[str(evidence.get("logical_url", ""))].append(evidence)
    for excluded in excluded_references:
        logical = str(excluded["logical_url"])
        excluded["fetch_records"] = [
            {
                "index": index,
                "original": fetch.get("original"),
                "status": fetch.get("status"),
                "kind": fetch.get("kind"),
                "role": fetch.get("role"),
                "error": fetch.get("error"),
                "raw_file": fetch.get("raw_file"),
                "sha256": fetch.get("sha256"),
            }
            for index, fetch in enumerate(fetch_records)
            if _canonical_url(str(fetch.get("original", ""))) == logical
        ]
        excluded["cache_evidence"] = [
            failure for failure in cache_failures if failure.get("logical_url") == logical
        ]
        excluded["raw_evidence"] = raw_evidence_by_logical.get(logical, [])

    # Cache responses are preserved as capture-like evidence so they remain
    # visible in the logical URL's provenance without becoming ZIP objects.
    cache_captures: list[dict[str, Any]] = []
    for entry in cache:
        if entry.get("status") != "valid_cache":
            continue
        raw_path = root / str(entry.get("raw_file")) if entry.get("raw_file") else None
        data = raw_path.read_bytes() if raw_path and raw_path.is_file() else b""
        body = _body_status(data, str(entry["original"]), str(entry.get("role")))
        cache_captures.append({
            "capture_id": entry["cache_id"],
            "source_kind": "raw_cache",
            "source_manifest": entry.get("raw_meta"),
            "original": entry["original"],
            "logical_url": entry["logical_url"],
            "role": entry["role"],
            "scope": entry["scope"],
            "requested_timestamp": entry.get("requested_timestamp"),
            "actual_timestamp": entry.get("actual_timestamp"),
            "actual_timestamp_raw": entry.get("actual_timestamp_raw"),
            "memento_datetime": entry.get("memento_datetime"),
            "http_status": entry.get("http_status"),
            "sha256": entry.get("sha256"),
            "content_length": entry.get("bytes"),
            "temporal_class": entry.get("temporal_class"),
            "content": body,
            "raw_file": entry.get("raw_file"),
            "raw_meta": entry.get("raw_meta"),
            "integrity": {
                "raw_sha256_matches": entry.get("raw_sha256") == entry.get("sha256"),
                "raw_file_present": bool(raw_path and raw_path.is_file()),
            },
        })
    captures.extend(cache_captures)

    # A compact index of every physical object, deduplicated by SHA-256.  ZIP
    # entries are kept as locations so repeated payloads remain auditable.
    objects_by_sha: dict[str, dict[str, Any]] = {}
    for (zip_file, entry), data in bytes_by_location.items():
        sha = _sha256(data)
        info = objects_by_sha.setdefault(
            sha,
            {"sha256": sha, "bytes": len(data), "locations": [], "logical_urls": []},
        )
        info["locations"].append({"zip_file": zip_file, "zip_entry": entry})

    logicals: dict[str, dict[str, Any]] = {}
    for ref in active_plan_refs:
        logical = ref["logical_url"]
        if not logical:
            continue
        item = logicals.setdefault(
            logical,
            {
                "logical_url": logical,
                "originals": [],
                "scope": "unclassified",
                "roles": [],
                "planned": True,
                "plan_refs": [],
                "capture_ids": [],
                "failure_ids": [],
                "pending": False,
            },
        )
        if ref["original"] not in item["originals"]:
            item["originals"].append(ref["original"])
        item["plan_refs"].append(ref)
        role = ref.get("role")
        scope = _scope_for_plan_ref(ref, core_asset_logicals)
        priority = {
            "core_page": 5,
            "core_asset": 4,
            "core_gap": 4,
            "shared": 3,
            "dependency_cache": 2,
            "dependency_discovered": 1,
            "unclassified": 0,
        }
        if priority.get(scope, 0) > priority.get(item["scope"], 0):
            item["scope"] = scope
        if role and role not in item["roles"]:
            item["roles"].append(role)

    all_failures = manifest_failures + cache_failures
    failures_by_logical = _failure_map(all_failures)
    for capture in captures:
        logical = capture["logical_url"]
        item = logicals.setdefault(
            logical,
            {
                "logical_url": logical,
                "originals": [capture["original"]],
                "scope": capture.get("scope", "unclassified"),
                "roles": [capture.get("role")],
                "planned": False,
                "plan_refs": [],
                "capture_ids": [],
                "failure_ids": [],
                "pending": False,
            },
        )
        if capture["original"] not in item["originals"]:
            item["originals"].append(capture["original"])
        if capture.get("role") and capture["role"] not in item["roles"]:
            item["roles"].append(capture["role"])
        if capture.get("scope") == "core_page":
            item["scope"] = "core_page"
        elif item.get("scope") == "unclassified":
            item["scope"] = capture.get("scope", "unclassified")
        item["capture_ids"].append(capture["capture_id"])

    capture_by_id = {capture["capture_id"]: capture for capture in captures}
    for logical, item in logicals.items():
        item["capture_ids"] = list(dict.fromkeys(item["capture_ids"]))
        item["failure_ids"] = failures_by_logical.get(logical, [])
        if item["scope"] == "shared" and not item["capture_ids"]:
            item["pending"] = True
        selected = _preferred([capture_by_id[cid] for cid in item["capture_ids"] if cid in capture_by_id])
        item["preferred_capture_id"] = selected.get("capture_id") if selected else None
        item["state"] = _logical_state(
            [capture_by_id[cid] for cid in item["capture_ids"] if cid in capture_by_id],
            bool(item.get("pending")),
        )
        item["valid_capture_ids"] = [
            cid
            for cid in item["capture_ids"]
            if capture_by_id.get(cid, {}).get("content", {}).get("status") == "valid_entity"
        ]
        item["soft404_capture_ids"] = [
            cid
            for cid in item["capture_ids"]
            if capture_by_id.get(cid, {}).get("content", {}).get("status") == "soft404"
        ]

    # Explicitly add known and dynamically discovered core-image gaps as
    # unverified logical evidence.  They are not counted as successful core
    # assets unless they also belong to the primary asset plan; rerunning this
    # script automatically updates each gap's state.
    for gap in _gap_records(root, logicals):
        logical = gap["logical_url"]
        if logical not in logicals:
            logicals[logical] = {
                "logical_url": logical,
                "originals": [gap["original"]],
                "scope": "core_gap",
                "roles": ["core_gap"],
                "planned": False,
                "plan_refs": [],
                "capture_ids": [],
                "failure_ids": [],
                "pending": False,
                "preferred_capture_id": None,
                "state": "unverified",
                "valid_capture_ids": [],
                "soft404_capture_ids": [],
            }

    # Ensure ZIP object references point back to all logical URLs, including
    # duplicate payloads that are stored in more than one volume.
    for capture in captures:
        object_ref = capture.get("object")
        if not object_ref:
            continue
        sha = object_ref.get("sha256")
        if sha in objects_by_sha and capture["logical_url"] not in objects_by_sha[sha]["logical_urls"]:
            objects_by_sha[sha]["logical_urls"].append(capture["logical_url"])

    # Preserve the independent asset validator's 56/2 result as a source
    # cross-check while using local ZIP bytes and title/magic classification for
    # the actual preservation state.
    for logical, validation in asset_validation_by_logical.items():
        if logical in logicals:
            logicals[logical].setdefault("external_validation", {})["encyclopedia_assets"] = {
                "pass": validation.get("pass"),
                "image_magic_valid": validation.get("image_magic_valid"),
                "requested_timestamp": validation.get("requested_timestamp"),
                "actual_timestamp": validation.get("actual_timestamp"),
                "bytes": validation.get("bytes"),
                "source": "research/encyclopedia-assets-validation.json",
            }
    for item in core_validation.get("items", []):
        if not isinstance(item, dict):
            continue
        logical = _canonical_url(str(item.get("original", "")))
        if logical in logicals:
            logicals[logical].setdefault("external_validation", {})["core"] = {
                "validation_status": item.get("validation_status"),
                "checks": item.get("checks"),
                "source": "research/validation/core-validation.json",
            }

    logical_list = sorted(logicals.values(), key=lambda item: item["logical_url"])
    preferred_map = {
        item["logical_url"]: {
            "capture_id": item.get("preferred_capture_id"),
            "state": item.get("state"),
            "scope": item.get("scope"),
        }
        for item in logical_list
    }
    state_counts: dict[str, int] = defaultdict(int)
    scope_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    flag_counts: dict[str, int] = defaultdict(int)
    for item in logical_list:
        state_counts[item["state"]] += 1
        scope_counts[item["scope"]][item["state"]] += 1
        if item.get("valid_capture_ids"):
            flag_counts["has_valid_capture"] += 1
        if item.get("soft404_capture_ids"):
            flag_counts["has_soft404_capture"] += 1
        if item.get("pending"):
            flag_counts["has_partial_pending"] += 1
        if item.get("state") == "unverified":
            flag_counts["state_unverified"] += 1

    manifest_success = [capture for capture in captures if capture.get("source_kind") == "zip_manifest"]
    valid_manifest = [
        capture for capture in manifest_success if capture.get("content", {}).get("status") == "valid_entity"
    ]
    successful_logicals = {
        capture["logical_url"] for capture in manifest_success
    } | {entry["logical_url"] for entry in cache if entry.get("status") == "valid_cache"}
    valid_logicals = {
        item["logical_url"] for item in logical_list if item.get("state") in {"valid", "valid_with_supplements"}
    }
    preferred_2010 = {item["logical_url"] for item in logical_list if item.get("preferred_capture_id")}
    temporal_only = {item["logical_url"] for item in logical_list if item.get("state") == "temporal_supplement_only"}
    pending = {item["logical_url"] for item in logical_list if item.get("state") == "partial_pending"}
    unresolved = {item["logical_url"] for item in logical_list if item.get("state") == "unverified"}

    core_plan_count = sum(1 for ref in active_plan_refs if ref.get("source") == "research/core-plan.json")
    asset_plan_count = sum(1 for ref in active_plan_refs if ref.get("source") == "research/encyclopedia-assets-plan.json")
    shared_planned = {
        logical
        for logical, refs in plan_by_logical.items()
        if any(_scope_for_plan_ref(ref, core_asset_logicals) == "shared" for ref in refs)
    }
    shared_pending = sorted(shared_planned & pending)
    core_gaps = _gap_records(root, logicals)
    active_planned_logicals = {ref["logical_url"] for ref in active_plan_refs if ref["logical_url"]}

    index = {
        "schema_version": 1,
        "generated_at": _datetime.datetime.now(_datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "anchor_timestamp": ANCHOR,
        "policy": {
            "offline_only": True,
            "preferred_capture": "valid entity with actual timestamp at or before anchor; core assets may use same-day captures through 20101203235959",
            "preferred_cutoff": PREFERRED_CUTOFF,
            "late_capture": "valid capture after the allowed cutoff is retained as temporal_supplement and is not a 2010-consistent preferred capture",
            "soft404": "HTTP success is not validity; image magic and error/general-guide titles are checked locally",
            "deduplication": "logical URLs normalize default ports and case-fold hostnames; ZIP objects deduplicate by SHA-256 while retaining every location",
        },
        "sources": {
            "required_plans": [_rel(root, path) for path in required_plan_paths if path.exists()],
            "shared_plans": [_rel(root, path) for path in shared_plan_paths if path.exists()],
            "supplemental_plans": [_rel(root, path) for path in supplemental_plan_paths if path.exists()],
            "manifests": [_rel(root, path) for path in _manifest_paths(root)],
            "asset_validation": "research/encyclopedia-assets-validation.json",
            "core_validation": "research/validation/core-validation.json",
        },
        "summary": {
            "logical_url_counts": {
                "planned_logical_urls": len(active_planned_logicals),
                "indexed_logical_urls": len(logical_list),
                "successful_logical_urls": len(successful_logicals),
                "valid_logical_urls_with_preferred_capture": len(valid_logicals),
                "valid_2010_preferred_logical_urls": len(preferred_2010),
                "temporal_supplement_only_logical_urls": len(temporal_only),
                "soft404_only_logical_urls": state_counts.get("soft404", 0),
                "unverified_logical_urls": len(unresolved),
                "partial_pending_logical_urls": len(pending),
            },
            "scope_counts": {scope: dict(counts) for scope, counts in sorted(scope_counts.items())},
            "flag_counts": dict(sorted(flag_counts.items())),
            "core_plan_items": core_plan_count,
            "encyclopedia_asset_plan_items": asset_plan_count,
            "core_assets_external_validation": {
                "planned": asset_validation.get("planned"),
                "passed": asset_validation.get("passed"),
                "soft404_or_invalid": (asset_validation.get("planned") or 0) - (asset_validation.get("passed") or 0),
                "source": "research/encyclopedia-assets-validation.json",
            },
            "manifest_success_records": len(manifest_success),
            "valid_manifest_entities": len(valid_manifest),
            "cache_records": len(cache),
            "valid_cache_records": sum(entry.get("status") == "valid_cache" for entry in cache),
            "valid_shared_cache_records": sum(entry.get("counted_in_shared_cache") for entry in cache),
            "core_asset_cache_duplicates": sum(entry.get("duplicate_of_core_asset") for entry in cache),
            "shared_planned_logical_urls": len(shared_planned),
            "shared_pending_logical_urls": len(shared_pending),
            "deduplicated_zip_objects": len(objects_by_sha),
            "physical_zip_entries": sum(volume.get("entry_count", 0) for volume in volumes),
            "raw_evidence_files": len(raw_evidence),
            "raw_unreferenced_evidence_files": sum(not item.get("referenced_by_fetch_record") for item in raw_evidence),
            "cache_integrity_error_count": len(cache_integrity_errors),
            "excluded_logical_references": len(excluded_logicals),
            "core_image_gap_count": sum(1 for gap in core_gaps if gap.get("is_gap")),
            "core_image_gap_active_reference_count": sum(1 for gap in core_gaps if gap.get("active_reference")),
            "core_image_gap_resolved_reference_count": sum(
                1 for gap in core_gaps if gap.get("active_reference") and not gap.get("is_gap")
            ),
            "core_image_gap_excluded_reference_count": sum(1 for gap in core_gaps if not gap.get("active_reference")),
        },
        "zip_validation": {
            "volumes": volumes,
            "errors": zip_errors,
            "crc_ok": not any("CRC failure" in error or "ZIP open error" in error for error in zip_errors),
            "sha_named_entries_ok": not any("SHA name mismatch" in error for error in zip_errors),
            "object_reference_errors": [
                {
                    "capture_id": capture["capture_id"],
                    "logical_url": capture["logical_url"],
                    "integrity": capture.get("integrity"),
                }
                for capture in manifest_success
                if not capture.get("integrity", {}).get("object_present")
                or capture.get("integrity", {}).get("sha256_matches_manifest") is False
                or capture.get("integrity", {}).get("length_matches_manifest") is False
            ],
        },
        "objects": sorted(objects_by_sha.values(), key=lambda item: item["sha256"]),
        "preferred_map": preferred_map,
        "logical_urls": logical_list,
        "captures": sorted(captures, key=lambda item: item["capture_id"]),
        "cache_records": cache,
        "cache_integrity_errors": cache_integrity_errors,
        "raw_evidence": raw_evidence,
        "excluded_references": excluded_references,
        "failures": manifest_failures,
        "cache_failures": cache_failures,
        "core_image_gaps": core_gaps,
        "shared_pending": [
            {
                "logical_url": logical,
                "originals": logicals[logical].get("originals", []),
                "scope": logicals[logical].get("scope"),
                "plan_refs": logicals[logical].get("plan_refs", []),
                "failure_ids": logicals[logical].get("failure_ids", []),
                "status": "partial_pending",
            }
            for logical in shared_pending
        ],
    }

    summary = {
        "schema_version": 1,
        "generated_at": index["generated_at"],
        "anchor_timestamp": ANCHOR,
        "index": _rel(root, index_path),
        "sources": index["sources"],
        "counts": index["summary"],
        "zip_validation": {
            "crc_ok": index["zip_validation"]["crc_ok"],
            "sha_named_entries_ok": index["zip_validation"]["sha_named_entries_ok"],
            "object_reference_error_count": len(index["zip_validation"]["object_reference_errors"]),
            "errors": index["zip_validation"]["errors"],
            "volumes": index["zip_validation"]["volumes"],
        },
        "core_image_gaps": core_gaps,
        "excluded_references": excluded_references,
        "failure_locations": [
            {
                "failure_id": failure.get("failure_id"),
                "original": failure.get("original"),
                "source_manifest": failure.get("source_manifest"),
                "manifest_line": failure.get("manifest_line"),
                "failure_reason": failure.get("failure_reason"),
            }
            for failure in manifest_failures
        ],
        "cache_failure_locations": cache_failures,
        "cache_integrity_errors": cache_integrity_errors,
        "anomalies": {
            "temporal_supplement_actual_dates": sorted({
                str(capture.get("actual_timestamp"))
                for capture in captures
                if capture.get("temporal_class") == "temporal_supplement" and capture.get("actual_timestamp")
            }),
            "temporal_supplement_captures": [
                {
                    "capture_id": capture["capture_id"],
                    "logical_url": capture["logical_url"],
                    "actual_timestamp": capture.get("actual_timestamp"),
                    "source": capture.get("source_manifest") or capture.get("raw_file"),
                }
                for capture in captures
                if capture.get("temporal_class") == "temporal_supplement"
            ],
            "soft404_or_generic_guide_captures": [
                {
                    "capture_id": capture["capture_id"],
                    "logical_url": capture["logical_url"],
                    "status": capture.get("content", {}).get("status"),
                    "title": capture.get("content", {}).get("title"),
                    "source": capture.get("source_manifest") or capture.get("raw_file"),
                }
                for capture in captures
                if capture.get("content", {}).get("status") in {"soft404", "generic_guide"}
            ],
            "duplicate_raw_evidence": [
                item for item in raw_evidence if item.get("duplicate_of_raw_evidence")
            ],
        },
    }
    index_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    hard_errors = bool(
        zip_errors
        or index["zip_validation"]["object_reference_errors"]
        or cache_integrity_errors
    )
    return index, summary, 2 if hard_errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--index", type=Path, default=None)
    parser.add_argument("--summary", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    index_path = (args.index or root / "research" / "preservation-index.json").resolve()
    summary_path = (args.summary or root / "research" / "preservation-summary.json").resolve()
    index, summary, status = build(root, index_path, summary_path)
    print(json.dumps({
        "index": _rel(root, index_path),
        "summary": _rel(root, summary_path),
        "exit_status": status,
        "logical_urls": index["summary"]["logical_url_counts"],
        "zip_crc_ok": index["zip_validation"]["crc_ok"],
        "zip_sha_named_entries_ok": index["zip_validation"]["sha_named_entries_ok"],
        "object_reference_errors": len(index["zip_validation"]["object_reference_errors"]),
        "zip_errors": len(index["zip_validation"]["errors"]),
    }, ensure_ascii=False, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
