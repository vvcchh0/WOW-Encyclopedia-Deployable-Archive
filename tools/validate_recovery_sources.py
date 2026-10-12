"""Validate locally recovered source-map entities without network access.

The validator checks provenance and bytes before interpreting content.  It is
deliberately independent from the downloader and mirror builder so a recovery
map can be audited before it is allowed into either one.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import html
import importlib
import io
import json
import os
from pathlib import Path
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from typing import Any
import urllib.parse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "research/recovery-source-validation.json"
ANCHOR_TIMESTAMP = "20080512210044"
ANCHOR = datetime.strptime(ANCHOR_TIMESTAMP, "%Y%m%d%H%M%S")
PRE2008_CDX_FROM = "20080101000000"
PRE2008_CDX_TO = "20081231235959"
LEGACY_ARC_LF_FRAMING_MODE = "payload_plus_single_lf"
ALLOWED_EXACT_HOSTS = {"worldofwarcraft.com", "blizzard.com"}
IMAGE_MIME_PREFIX = "image/"
# XHTML is an XML representation on the wire.  Keep it on the XML path so a
# malformed XHTML response is reported as a parse failure; a .xml body served
# as text/html remains on the tolerant HTML path.
HTML_MIMES = {"text/html"}
XML_MIMES = {"text/xml", "application/xml", "application/xhtml+xml", "application/rss+xml", "application/atom+xml"}
HTML_ERROR_MARKERS = (
    "404 file not found",
    "404 not found",
    "file not found",
    "page cannot be found",
    "this url has been excluded",
    "wayback machine error",
    "got an http status code of 404",
    "requested page could not be found",
    "wayback machine",
    "internet archive wayback",
)
ZIP_FIELDS = ("zip_file", "zip_entry")


class ValidationFailure(Exception):
    """Raised for a map or entity hard failure collected in the report."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def mime_base(value: Any) -> str:
    return str(value or "").split(";", 1)[0].strip().casefold()


def declared_mime(item: dict[str, Any]) -> str:
    value = (item.get("mime") or item.get("declared_mime") or item.get("source_mime")
             or item.get("response_content_type") or item.get("content_type"))
    if not value:
        headers = item.get("response_headers")
        if isinstance(headers, dict):
            for key, candidate in headers.items():
                if str(key).casefold() == "content-type":
                    value = candidate
                    break
    return str(value or "")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cdx_sha1_digest(data: bytes) -> str:
    encoded = base64.b32encode(hashlib.sha1(data).digest()).decode("ascii")
    return encoded.rstrip("=")


def resolve_workspace_path(value: Any, *, field: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValidationFailure(f"{field}: missing path")
    raw = Path(value)
    path = (raw if raw.is_absolute() else ROOT / raw).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValidationFailure(f"{field}: path escapes workspace: {value!r}") from exc
    return path


def source_url(item: dict[str, Any]) -> str:
    return str(item.get("logical_url") or item.get("original") or item.get("source_url") or "")


def validate_public_url(url: str) -> None:
    if not url:
        raise ValidationFailure("logical_url: missing official URL")
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme.casefold() not in {"http", "https"} or not parsed.hostname:
        raise ValidationFailure(f"logical_url: not an HTTP(S) URL: {url!r}")
    host = parsed.hostname.casefold().rstrip(".")
    if not (host in ALLOWED_EXACT_HOSTS or any(host.endswith("." + parent) for parent in ALLOWED_EXACT_HOSTS)):
        raise ValidationFailure(f"logical_url: host is not an official public host: {url!r}")
    if "__offline" in parsed.path.casefold() or "__offline" in parsed.query.casefold():
        raise ValidationFailure(f"logical_url: synthetic offline route is forbidden: {url!r}")
    if parsed.fragment:
        raise ValidationFailure(f"logical_url: fragments are not source entities: {url!r}")


def _provenance_url_key(value: Any) -> tuple[str, str, str, str] | None:
    """Normalize URL identity for a CDX evidence-to-item comparison.

    CDX evidence may use HTTP while a source map uses HTTPS.  The recovery
    contract treats those schemes, the site's www/no-www spelling, and default
    ports as equivalent.  Path and query remain significant.
    """

    if not isinstance(value, str) or not value.strip():
        return None
    parsed = urllib.parse.urlsplit(value.strip())
    if parsed.scheme.casefold() not in {"http", "https"} or not parsed.hostname:
        return None
    host = parsed.hostname.casefold().rstrip(".")
    if host in {"worldofwarcraft.com", "www.worldofwarcraft.com"}:
        host = "worldofwarcraft.com"
    try:
        port = parsed.port
    except ValueError:
        return None
    if port in {None, 80, 443}:
        normalized_port = ""
    else:
        normalized_port = f":{port}"
    return (host, normalized_port, parsed.path or "/", parsed.query)


def _pre2008_query_contract(query_url: Any, expected_url: str) -> list[str]:
    """Return violations of the bounded full-2008 exact-CDX contract."""

    errors: list[str] = []
    if not isinstance(query_url, str) or not query_url.strip():
        return ["year_fallback_evidence query_url is missing"]
    parsed = urllib.parse.urlsplit(query_url)
    if parsed.scheme.casefold() not in {"http", "https"}:
        errors.append("year_fallback_evidence query scheme must be http or https")
    if parsed.hostname is None or parsed.hostname.casefold().rstrip(".") != "web.archive.org":
        errors.append("year_fallback_evidence query host must be web.archive.org")
    if parsed.path != "/cdx/search/cdx":
        errors.append("year_fallback_evidence query path must be /cdx/search/cdx")
    params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    def single_param(name: str) -> str:
        matching_keys = [key for key in params if key.casefold() == name.casefold()]
        if len(matching_keys) != 1:
            errors.append(f"year_fallback_evidence query must contain one {name} parameter")
            return ""
        values = params[matching_keys[0]]
        if len(values) != 1:
            errors.append(f"year_fallback_evidence query {name} parameter must be single-valued")
            return ""
        return values[0]

    query_target = single_param("url")
    if _provenance_url_key(query_target) != _provenance_url_key(expected_url):
        errors.append(f"year_fallback_evidence query URL target mismatch: {query_target!r}")
    match_type = single_param("matchType")
    if match_type.casefold() != "exact":
        errors.append("year_fallback_evidence query must set matchType=exact")
    from_value = single_param("from")
    if from_value != PRE2008_CDX_FROM:
        errors.append("year_fallback_evidence query must start at 20080101000000")
    to_value = single_param("to")
    if to_value != PRE2008_CDX_TO:
        errors.append("year_fallback_evidence query must end at 20081231235959")
    output = single_param("output")
    if output.casefold() != "json":
        errors.append("year_fallback_evidence query must request output=json")
    # `fl=...statuscode...mimetype` is a projection, not a filter, and is
    # required by the preserved A query.  Reject actual status/MIME filters
    # and all pagination/collapse knobs because they weaken empty-CDX proof.
    forbidden_keys = {"statuscode", "mimetype", "collapse", "shownumpages", "page", "filter"}
    for key in params:
        if key.casefold() in forbidden_keys:
            errors.append(f"year_fallback_evidence query has forbidden filter/pagination parameter: {key}")
    return errors


def _pre2008_supplement_evidence(item: dict[str, Any]) -> dict[str, Any]:
    """Validate the explicit metadata needed for an earlier static image.

    This gate is intentionally separate from the normal 2008 timestamp gate.
    A caller must opt in, and the returned evidence remains visibly marked as
    a supplement so it cannot be mistaken for the fixed baseline snapshot.
    """

    errors: list[str] = []
    kind = str(item.get("kind") or "").casefold()
    if kind != "image":
        errors.append("pre-2008 static supplement requires kind=image")
    mime = mime_base(declared_mime(item))
    if not mime.startswith(IMAGE_MIME_PREFIX):
        errors.append(f"pre-2008 static supplement requires image/* MIME: {declared_mime(item)!r}")
    if item.get("temporal_class") != "pre2008_static_supplement":
        errors.append("pre-2008 static supplement requires temporal_class=pre2008_static_supplement")
    note = item.get("supplement_note")
    if not isinstance(note, str) or not note.strip():
        errors.append("pre-2008 static supplement requires non-empty supplement_note")
    evidence_value = item.get("year_fallback_evidence")
    evidence_path: Path | None = None
    if not isinstance(evidence_value, str) or not evidence_value.strip():
        errors.append("pre-2008 static supplement requires year_fallback_evidence")
    else:
        try:
            evidence_path = resolve_workspace_path(evidence_value, field="year_fallback_evidence")
            if not evidence_path.name.casefold().endswith(".meta.json"):
                raise ValidationFailure("year_fallback_evidence must be an A CDX .meta.json path")
            if not evidence_path.is_file():
                raise ValidationFailure(f"year_fallback_evidence does not exist: {evidence_value!r}")
            try:
                metadata = json.loads(evidence_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise ValidationFailure(f"year_fallback_evidence is not valid JSON metadata: {evidence_value!r}") from exc
            if not isinstance(metadata, dict):
                raise ValidationFailure("year_fallback_evidence metadata must be a JSON object")
            required_metadata_fields = (
                "original",
                "query_url",
                "status",
                "http_status",
                "raw_path",
                "metadata_path",
                "body_length",
                "body_sha256",
                "coverage_status",
                "truncated",
                "row_count",
                "candidate_rows",
                "parse_error",
            )
            missing_metadata_fields = [field for field in required_metadata_fields if field not in metadata]
            if missing_metadata_fields:
                raise ValidationFailure(
                    "year_fallback_evidence metadata missing fields: "
                    + ", ".join(missing_metadata_fields)
                )
            metadata_path_value = metadata.get("metadata_path")
            if metadata_path_value:
                try:
                    declared_metadata_path = resolve_workspace_path(
                        metadata_path_value, field="year_fallback_evidence.metadata_path"
                    )
                    if declared_metadata_path != evidence_path:
                        raise ValidationFailure("year_fallback_evidence metadata_path does not identify this file")
                except ValidationFailure:
                    raise
            expected_url = source_url(item)
            if _provenance_url_key(metadata.get("original")) != _provenance_url_key(expected_url):
                raise ValidationFailure(
                    "year_fallback_evidence original does not match item logical_url/original"
                )
            query_errors = _pre2008_query_contract(metadata.get("query_url"), expected_url)
            if query_errors:
                raise ValidationFailure("; ".join(query_errors))
            if metadata.get("status") != "success":
                raise ValidationFailure(f"year_fallback_evidence status is not success: {metadata.get('status')!r}")
            try:
                if int(metadata.get("http_status")) != 200:
                    raise ValidationFailure(
                        f"year_fallback_evidence HTTP status is not 200: {metadata.get('http_status')!r}"
                    )
            except (TypeError, ValueError) as exc:
                raise ValidationFailure("year_fallback_evidence HTTP status is invalid") from exc
            if metadata.get("truncated") is not False:
                raise ValidationFailure("year_fallback_evidence must have truncated=false")
            if metadata.get("coverage_status") != "complete_empty":
                raise ValidationFailure(
                    f"year_fallback_evidence coverage is not complete_empty: {metadata.get('coverage_status')!r}"
                )
            if metadata.get("parse_error") not in {None, ""}:
                raise ValidationFailure("year_fallback_evidence has a parse error")
            row_count = metadata.get("row_count")
            if not isinstance(row_count, int) or row_count != 0:
                raise ValidationFailure("year_fallback_evidence contains CDX rows")
            candidate_rows = metadata.get("candidate_rows")
            if not isinstance(candidate_rows, list) or candidate_rows:
                raise ValidationFailure("year_fallback_evidence contains candidate rows")
            raw_value = metadata.get("raw_path")
            raw_path = resolve_workspace_path(raw_value, field="year_fallback_evidence.raw_path")
            if not raw_path.is_file():
                raise ValidationFailure(f"year_fallback_evidence raw_path does not exist: {raw_value!r}")
            raw_data = raw_path.read_bytes()
            declared_length = metadata.get("body_length")
            if not isinstance(declared_length, int) or declared_length != len(raw_data):
                raise ValidationFailure(
                    f"year_fallback_evidence raw length mismatch: {len(raw_data)} != {declared_length!r}"
                )
            raw_sha = sha256_bytes(raw_data)
            if raw_sha.casefold() != str(metadata.get("body_sha256") or "").casefold():
                raise ValidationFailure("year_fallback_evidence raw SHA256 mismatch")
            try:
                parsed_raw = json.loads(raw_data.decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError) as exc:
                raise ValidationFailure("year_fallback_evidence raw body is not valid JSON") from exc
            if parsed_raw != []:
                raise ValidationFailure("year_fallback_evidence raw body is not a complete empty [] response")
            metadata_sha = sha256_bytes(evidence_path.read_bytes())
            supplied_metadata_sha = item.get("year_fallback_evidence_sha256")
            if supplied_metadata_sha is not None and str(supplied_metadata_sha).casefold() != metadata_sha.casefold():
                raise ValidationFailure(
                    f"year_fallback_evidence SHA256 mismatch: {metadata_sha} != {supplied_metadata_sha}"
                )
        except ValidationFailure as exc:
            errors.append(str(exc))
    if errors:
        raise ValidationFailure("; ".join(errors))
    assert evidence_path is not None
    metadata = json.loads(evidence_path.read_text(encoding="utf-8"))
    raw_path = resolve_workspace_path(metadata["raw_path"], field="year_fallback_evidence.raw_path")
    metadata_sha = sha256_bytes(evidence_path.read_bytes())
    raw_data = raw_path.read_bytes()
    return {
        "temporal_class": "pre2008_static_supplement",
        "supplement_note": str(note).strip(),
        "year_fallback_evidence": evidence_path.relative_to(ROOT).as_posix(),
        "year_fallback_evidence_sha256": metadata_sha,
        "evidence_original": metadata["original"],
        "evidence_query_url": metadata["query_url"],
        "evidence_metadata_status": metadata["status"],
        "evidence_http_status": metadata["http_status"],
        "evidence_metadata_path": evidence_path.relative_to(ROOT).as_posix(),
        "evidence_metadata_sha256": metadata_sha,
        "evidence_raw_path": raw_path.relative_to(ROOT).as_posix(),
        "evidence_raw_sha256": sha256_bytes(raw_data),
        "evidence_raw_length": len(raw_data),
        "evidence_cdx_row_count": metadata["row_count"],
        "supplement_mime": mime,
        "supplement_kind": kind,
    }


def parse_actual_timestamp(item: dict[str, Any], *, allow_pre2008_static_supplement: bool = False) -> tuple[str, datetime]:
    value = item.get("actual_timestamp")
    if not isinstance(value, str) or not re.fullmatch(r"\d{14}", value):
        raise ValidationFailure("actual_timestamp: required 14-digit timestamp")
    try:
        parsed = datetime.strptime(value, "%Y%m%d%H%M%S")
    except ValueError as exc:
        raise ValidationFailure(f"actual_timestamp: invalid value {value!r}") from exc
    if parsed.year < 2008:
        if not allow_pre2008_static_supplement:
            raise ValidationFailure(
                f"actual_timestamp: not a 2008 capture: {value}; "
                "use --allow-pre2008-static-supplement for an explicitly evidenced static image"
            )
        _pre2008_supplement_evidence(item)
    elif parsed.year != 2008:
        raise ValidationFailure(f"actual_timestamp: not a 2008 capture: {value}")
    return value, parsed


def time_bucket(parsed: datetime) -> str:
    if parsed.year < 2008:
        return "before_2008_static_supplement"
    if parsed == ANCHOR:
        return "at_anchor"
    if parsed < ANCHOR:
        return "before_anchor_within_90_days" if parsed >= ANCHOR - timedelta(days=90) else "before_anchor_older_than_90_days"
    return "after_anchor_other_2008"


def load_pillow() -> Any:
    """Load Pillow from the bundled runtime when the active interpreter lacks it."""

    try:
        return importlib.import_module("PIL.Image")
    except (ModuleNotFoundError, ImportError):
        candidates: list[Path] = []
        home = Path.home()
        runtime_root = home / ".cache/codex-runtimes"
        if runtime_root.is_dir():
            candidates.extend(runtime_root.glob("*/dependencies/python/Lib/site-packages"))
        codex_home = os.environ.get("CODEX_HOME")
        if codex_home:
            candidates.extend(Path(codex_home).glob("**/python/Lib/site-packages"))
        for candidate in candidates:
            if (candidate / "PIL").is_dir() and str(candidate) not in sys.path:
                sys.path.insert(0, str(candidate))
                try:
                    return importlib.import_module("PIL.Image")
                except (ModuleNotFoundError, ImportError):
                    continue
        raise ValidationFailure("image: Pillow is unavailable in active or bundled Python")


def reject_html_error(data: bytes) -> str | None:
    text = data[:2_000_000].decode("utf-8", errors="ignore").casefold()
    if not text.strip():
        return "empty entity body"
    if "<html" in text or "<!doctype html" in text or "<title" in text:
        for marker in HTML_ERROR_MARKERS:
            if marker in text:
                return f"HTML error/soft404 marker: {marker}"
    return None


def validate_image(data: bytes, mime: str) -> dict[str, Any]:
    if reject_html_error(data):
        raise ValidationFailure(reject_html_error(data) or "HTML error body presented as image")
    if mime == "image/svg+xml":
        try:
            root = ET.fromstring(data)
        except ET.ParseError as exc:
            raise ValidationFailure(f"SVG parse failed: {exc}") from exc
        return {"pillow_verified": False, "vector_format": "svg", "root_tag": root.tag}
    if mime in {"image/x-shockwave-flash", "application/x-shockwave-flash"}:
        if not data.startswith((b"FWS", b"CWS", b"ZWS")):
            raise ValidationFailure("SWF magic signature is missing")
        return {"pillow_verified": False, "binary_format": "swf"}
    image = load_pillow()
    try:
        with image.open(io.BytesIO(data)) as probe:
            image_format = str(probe.format or "").upper()
            frame_count = int(getattr(probe, "n_frames", 1) or 1)
            probe.verify()
        with image.open(io.BytesIO(data)) as loaded:
            for frame in range(frame_count):
                if frame:
                    loaded.seek(frame)
                loaded.load()
    except Exception as exc:  # Pillow uses several exception classes by version.
        raise ValidationFailure(f"Pillow verify/load failed: {exc}") from exc
    expected_formats = {
        "image/jpeg": {"JPEG"},
        "image/png": {"PNG"},
        "image/gif": {"GIF"},
        "image/webp": {"WEBP"},
        "image/bmp": {"BMP"},
        "image/tiff": {"TIFF"},
        "image/x-icon": {"ICO"},
        "image/vnd.microsoft.icon": {"ICO"},
    }
    expected = expected_formats.get(mime)
    if expected and image_format not in expected:
        raise ValidationFailure(f"MIME {mime} does not match Pillow format {image_format}")
    return {"pillow_verified": True, "pillow_format": image_format, "frame_count": frame_count}


def validate_xml(data: bytes) -> dict[str, Any]:
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise ValidationFailure(f"XML parse failed: {exc}") from exc
    prefix = data[:16_384].decode("utf-8", errors="ignore")
    pis = re.findall(r"<\?xml-stylesheet\s+([^?]+)\?>", prefix, flags=re.IGNORECASE)
    dependencies: list[str] = []
    for pi in pis:
        match = re.search(r"href\s*=\s*['\"]([^'\"]+)['\"]", pi, flags=re.IGNORECASE)
        if match:
            dependencies.append(html.unescape(match.group(1)))
    return {
        "genuine_xml": True,
        "xml_root": root.tag,
        "xml_stylesheet_dependencies": dependencies,
        "xml_stylesheet_pi_count": len(pis),
    }


def validate_html(data: bytes) -> dict[str, Any]:
    error = reject_html_error(data)
    if error:
        raise ValidationFailure(error)
    text = data.decode("utf-8", errors="ignore").casefold()
    if "<html" not in text and "<!doctype" not in text:
        raise ValidationFailure("HTML entity has no recognizable HTML root")
    return {"genuine_html": True}


def validate_content(data: bytes, item: dict[str, Any]) -> dict[str, Any]:
    mime = mime_base(declared_mime(item))
    if not mime:
        raise ValidationFailure("MIME: missing declared content type")
    result: dict[str, Any] = {"declared_mime": declared_mime(item), "mime_base": mime}
    kind = str(item.get("kind") or "").casefold()
    if mime.startswith(IMAGE_MIME_PREFIX):
        result.update(validate_image(data, mime))
        result["content_status"] = "valid_image"
    elif mime in XML_MIMES or kind == "xml":
        result.update(validate_xml(data))
        result["content_status"] = "valid_xml"
    elif mime in HTML_MIMES or kind in {"html", "page"}:
        result.update(validate_html(data))
        result["content_status"] = "valid_html"
    else:
        result["content_status"] = "bytes_only"
    return result


def read_zip_provenance(item: dict[str, Any], local_data: bytes, *, allow_no_zip: bool) -> dict[str, Any]:
    present = [field for field in ZIP_FIELDS if item.get(field)]
    if not present:
        if allow_no_zip:
            return {"zip_provenance": "omitted_by_allow_no_zip"}
        raise ValidationFailure("zip provenance is required; use --allow-no-zip only for an old comparison map")
    if len(present) != len(ZIP_FIELDS):
        raise ValidationFailure("zip_file and zip_entry must be supplied together")
    zip_path = resolve_workspace_path(item["zip_file"], field="zip_file")
    entry = str(item["zip_entry"])
    # ZIP member names are archive-relative.  Reject absolute and drive
    # qualified names in addition to traversal segments before asking
    # ZipFile for an entry, so a map cannot use a surprising member spelling
    # as provenance.
    normalized_entry = entry.replace("\\", "/")
    entry_path = Path(normalized_entry)
    if (
        not entry
        or "\x00" in entry
        or normalized_entry.startswith("/")
        or entry_path.is_absolute()
        or bool(re.match(r"^[A-Za-z]:($|/)", normalized_entry))
        or bool(entry_path.drive)
        or ".." in entry_path.parts
    ):
        raise ValidationFailure(f"zip_entry is unsafe: {entry!r}")
    if not zip_path.is_file():
        raise ValidationFailure(f"zip_file does not exist: {item['zip_file']}")
    try:
        with zipfile.ZipFile(zip_path) as archive:
            info = archive.getinfo(entry)
            zip_data = archive.read(info)
            crc = f"{info.CRC:08x}"
    except (KeyError, zipfile.BadZipFile, RuntimeError, OSError) as exc:
        raise ValidationFailure(f"ZIP provenance read failed: {exc}") from exc
    if len(zip_data) != len(local_data):
        raise ValidationFailure(f"ZIP/local length mismatch: {len(zip_data)} != {len(local_data)}")
    if sha256_bytes(zip_data) != sha256_bytes(local_data):
        raise ValidationFailure("ZIP/local SHA256 mismatch")
    return {
        "zip_provenance": "verified",
        "zip_file": item["zip_file"],
        "zip_entry": entry,
        "zip_crc32": crc,
        "zip_length": len(zip_data),
        "zip_sha256": sha256_bytes(zip_data),
    }


def validate_item(item: Any, index: int, *, allow_no_zip: bool,
                  allow_pre2008_static_supplement: bool = False,
                  allow_legacy_arc_lf_framing: bool = False) -> dict[str, Any]:
    evidence: dict[str, Any] = {"index": index, "accepted": False}
    if not isinstance(item, dict):
        evidence["errors"] = ["item is not an object"]
        return evidence
    evidence.update({"logical_url": source_url(item), "local_path": item.get("local_path"), "role": item.get("role"), "kind": item.get("kind")})
    errors: list[str] = []
    try:
        url = source_url(item)
        validate_public_url(url)
        evidence["logical_url"] = url
    except ValidationFailure as exc:
        errors.append(str(exc))
    status = item.get("http_status", item.get("status"))
    if status is not None:
        try:
            if int(status) != 200:
                errors.append(f"HTTP status is not 200: {status}")
        except (TypeError, ValueError):
            errors.append(f"HTTP status is invalid: {status!r}")
    try:
        timestamp, parsed = parse_actual_timestamp(
            item, allow_pre2008_static_supplement=allow_pre2008_static_supplement
        )
        evidence["actual_timestamp"] = timestamp
        evidence["time_bucket"] = time_bucket(parsed)
        evidence["actual_year"] = parsed.year
        if parsed.year < 2008:
            evidence["baseline_status"] = "supplement_only_before_2008"
            evidence["pre2008_static_supplement"] = _pre2008_supplement_evidence(item)
    except ValidationFailure as exc:
        errors.append(str(exc))
    try:
        local_path = resolve_workspace_path(item.get("local_path"), field="local_path")
        if not local_path.is_file():
            raise ValidationFailure(f"local_path does not exist: {item.get('local_path')!r}")
        local_data = local_path.read_bytes()
        actual_sha = sha256_bytes(local_data)
        actual_length = len(local_data)
        evidence.update({"local_path_resolved": str(local_path.relative_to(ROOT).as_posix()), "actual_sha256": actual_sha, "actual_length": actual_length})
        expected_sha = str(item.get("sha256") or item.get("source_sha256") or "")
        if not expected_sha:
            raise ValidationFailure("sha256: missing expected digest")
        if actual_sha.casefold() != expected_sha.casefold():
            raise ValidationFailure(f"local SHA256 mismatch: {actual_sha} != {expected_sha}")
        expected_length = item.get("content_length", item.get("source_length"))
        if expected_length is None:
            raise ValidationFailure("content_length: missing expected length")
        if int(expected_length) != actual_length:
            raise ValidationFailure(f"local length mismatch: {actual_length} != {expected_length}")
        evidence["expected_sha256"] = expected_sha
        evidence["expected_length"] = int(expected_length)
        try:
            evidence.update(read_zip_provenance(item, local_data, allow_no_zip=allow_no_zip))
        except ValidationFailure as exc:
            errors.append(str(exc))
        digest = item.get("cdx_digest")
        if digest is None:
            errors.append("cdx_digest: missing field")
        elif str(digest).strip() not in {"", "-"}:
            expected_digest = str(digest).strip()
            calculated = cdx_sha1_digest(local_data)
            evidence["calculated_cdx_digest"] = calculated
            evidence["cdx_digest_match"] = calculated.casefold() == expected_digest.casefold()
            if not evidence["cdx_digest_match"]:
                # A small set of legacy pre-2008 image records has a CDX
                # digest over the preserved payload followed by one virtual
                # framing LF.  The saved entity remains byte-for-byte the
                # payload; no LF is appended to local files or ZIP members.
                # This is opt-in and deliberately narrower than the normal
                # digest path: never mutate bytes or silently fall back.
                mode = item.get("cdx_digest_mode")
                legacy_evidence = {
                    "raw_payload_digest": calculated,
                    "framed_digest": cdx_sha1_digest(local_data + b"\n"),
                    "verified_digest": expected_digest,
                    "mode": mode,
                    "cdx_framing_note": str(item.get("cdx_framing_note") or "").strip() or None,
                    "suffix_hex0a": "0a",
                    "accepted": False,
                }
                evidence["legacy_arc_lf_framing"] = legacy_evidence
                eligible_scope = (
                    allow_legacy_arc_lf_framing
                    and allow_pre2008_static_supplement
                    and evidence.get("actual_year", 2008) < 2008
                    and item.get("kind") == "image"
                    and item.get("temporal_class") == "pre2008_static_supplement"
                    and mode == LEGACY_ARC_LF_FRAMING_MODE
                    and bool(str(item.get("cdx_framing_note") or "").strip())
                )
                raw_payload_digest = legacy_evidence["raw_payload_digest"]
                if (
                    eligible_scope
                    and raw_payload_digest
                    and legacy_evidence["framed_digest"].casefold() == expected_digest.casefold()
                ):
                    legacy_evidence["accepted"] = True
                    evidence["cdx_digest_match"] = True
                    evidence["cdx_digest_match_mode"] = LEGACY_ARC_LF_FRAMING_MODE
                else:
                    errors.append(f"CDX digest mismatch: {calculated} != {digest}")
        else:
            evidence["cdx_digest_match"] = None
        try:
            evidence["content"] = validate_content(local_data, item)
        except ValidationFailure as exc:
            errors.append(str(exc))
    except (ValidationFailure, OSError, ValueError, TypeError) as exc:
        errors.append(str(exc))
    evidence["errors"] = errors
    evidence["accepted"] = not errors
    return evidence


def validate_maps(map_paths: list[Path], *, allow_no_zip: bool,
                  allow_pre2008_static_supplement: bool = False,
                  allow_legacy_arc_lf_framing: bool = False) -> dict[str, Any]:
    evidence: list[dict[str, Any]] = []
    map_errors: list[str] = []
    for map_path in map_paths:
        map_record: dict[str, Any] = {"map": str(map_path), "accepted": False, "items": 0}
        try:
            map_path = map_path.resolve()
            map_path.relative_to(ROOT.resolve())
            data = json.loads(map_path.read_text(encoding="utf-8"))
            items = data.get("files") if isinstance(data, dict) else None
            if not isinstance(items, list):
                raise ValidationFailure("map must contain a files array")
            map_record["map"] = map_path.relative_to(ROOT).as_posix()
            map_record["items"] = len(items)
            map_record["anchor_timestamp"] = data.get("anchor_timestamp", ANCHOR_TIMESTAMP)
            map_record["item_evidence"] = [
                validate_item(
                    item,
                    index,
                    allow_no_zip=allow_no_zip,
                    allow_pre2008_static_supplement=allow_pre2008_static_supplement,
                    allow_legacy_arc_lf_framing=allow_legacy_arc_lf_framing,
                )
                for index, item in enumerate(items)
            ]
            map_record["accepted"] = all(item.get("accepted") for item in map_record["item_evidence"])
            if not map_record["accepted"]:
                map_errors.append(f"{map_record['map']}: one or more entities failed")
        except (OSError, json.JSONDecodeError, ValidationFailure, ValueError) as exc:
            map_record["errors"] = [str(exc)]
            map_errors.append(f"{map_path}: {exc}")
        evidence.append(map_record)

    item_evidence = [item for record in evidence for item in record.get("item_evidence", [])]
    buckets = Counter(str(item.get("time_bucket")) for item in item_evidence if item.get("time_bucket"))
    summary = {
        "maps": len(evidence),
        "maps_accepted": sum(1 for record in evidence if record.get("accepted")),
        "items": len(item_evidence),
        "items_accepted": sum(1 for item in item_evidence if item.get("accepted")),
        "items_failed": sum(1 for item in item_evidence if not item.get("accepted")),
        "time_buckets": dict(sorted(buckets.items())),
        "before_anchor_count": buckets.get("before_anchor_within_90_days", 0) + buckets.get("before_anchor_older_than_90_days", 0),
        "at_anchor_count": buckets.get("at_anchor", 0),
        "before_anchor_within_90_days_count": buckets.get("before_anchor_within_90_days", 0),
        "before_anchor_older_than_90_days_count": buckets.get("before_anchor_older_than_90_days", 0),
        "after_anchor_other_2008_count": buckets.get("after_anchor_other_2008", 0),
        "before_2008_static_supplement_count": buckets.get("before_2008_static_supplement", 0),
    }
    accepted = bool(evidence) and not map_errors and summary["items"] > 0
    return {
        "schema_version": 1,
        "generated_utc": utc_now(),
        "network_performed": False,
        "anchor_timestamp": ANCHOR_TIMESTAMP,
        "allow_no_zip": allow_no_zip,
        "allow_pre2008_static_supplement": allow_pre2008_static_supplement,
        "allow_legacy_arc_lf_framing": allow_legacy_arc_lf_framing,
        "maps": evidence,
        "summary": summary,
        "accepted": accepted,
        "errors": map_errors,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", dest="maps", action="append", type=Path, required=True, help="source map JSON; repeat for multiple maps")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="validation report JSON path")
    parser.add_argument("--allow-no-zip", action="store_true", help="allow a map item without zip_file/zip_entry provenance for old comparisons")
    parser.add_argument(
        "--allow-pre2008-static-supplement",
        action="store_true",
        help="allow only explicitly evidenced pre-2008 image supplements; never baseline",
    )
    parser.add_argument(
        "--allow-legacy-arc-lf-framing",
        action="store_true",
        help="allow explicitly evidenced pre-2008 image CDX payload-plus-single-LF framing",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    maps = [path if path.is_absolute() else ROOT / path for path in args.maps]
    report = args.report if args.report.is_absolute() else ROOT / args.report
    try:
        result = validate_maps(
            [path.resolve() for path in maps],
            allow_no_zip=args.allow_no_zip,
            allow_pre2008_static_supplement=args.allow_pre2008_static_supplement,
            allow_legacy_arc_lf_framing=args.allow_legacy_arc_lf_framing,
        )
    except Exception as exc:  # keep a machine-readable report for malformed invocation inputs
        result = {
            "schema_version": 1,
            "generated_utc": utc_now(),
            "network_performed": False,
            "anchor_timestamp": ANCHOR_TIMESTAMP,
            "allow_no_zip": args.allow_no_zip,
            "allow_pre2008_static_supplement": args.allow_pre2008_static_supplement,
            "allow_legacy_arc_lf_framing": args.allow_legacy_arc_lf_framing,
            "maps": [],
            "summary": {"maps": len(maps), "items": 0, "items_accepted": 0, "items_failed": 0},
            "accepted": False,
            "errors": [f"{type(exc).__name__}: {exc}"],
        }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(report), "accepted": result["accepted"], "summary": result["summary"]}, ensure_ascii=False))
    return 0 if result["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
