"""Build and optionally export the 2008 preservation index.

The command is intentionally offline.  It reads acquisition plans, manifests,
saved ZIP members and baseline files; it never follows a URL and never executes
preserved HTML/JavaScript.  It is tolerant of a downloader that is still
running: an unfinished manifest is reported as partial and its missing items
remain explicit.

Usage::

    python tools/build_2008_preservation.py
    python tools/build_2008_preservation.py --export

Without ``--export`` only the integration report is written.  ``--export``
performs a preflight size/free-space check before materialising valid preferred
entities under ``mirror/20080512``.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import sys
import urllib.parse
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ANCHOR = "20080512210044"
ANCHOR_DAY = ANCHOR[:8]
WORKSPACE_LIMIT = 14_000_000_000
MIN_FREE = 10 * 1024**3
WRITE_RESERVE = 256 * 1024**2
HTML_EXTS = {".html", ".htm", ".xml"}
IMAGE_EXTS = {".jpg", ".jpeg", ".gif", ".png", ".webp", ".swf"}
SCRIPT_EXTS = {".js", ".css", ".xsl", ".xslt"}


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return default


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    if not path.exists():
        return result
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            result.append({"status": "invalid_manifest_line", "_line": line_number, "_raw": line[:500]})
            continue
        if isinstance(value, dict):
            value["_line"] = line_number
            result.append(value)
    return result


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cdx_sha1(data: bytes) -> str:
    return base64.b32encode(hashlib.sha1(data).digest()).decode("ascii").rstrip("=")


def timestamp(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    match = re.search(r"(?<!\d)(\d{14})(?!\d)", text)
    if match:
        return match.group(1)
    for fmt in ("%a, %d %b %Y %H:%M:%S GMT", "%a, %d %b %Y %H:%M:%S %Z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return dt.datetime.strptime(text, fmt).strftime("%Y%m%d%H%M%S")
        except ValueError:
            pass
    return None


def canonical_url(value: str) -> str:
    """Normalize scheme/host/default port while preserving path spelling/query."""

    value = str(value or "")
    parsed = urllib.parse.urlsplit(value)
    if not parsed.scheme or not parsed.netloc:
        return value
    host = parsed.hostname or ""
    netloc = host.lower()
    try:
        port = parsed.port
    except ValueError:
        port = None
    if port is not None and not ((parsed.scheme.lower() == "http" and port == 80) or (parsed.scheme.lower() == "https" and port == 443)):
        netloc += f":{port}"
    return urllib.parse.urlunsplit((parsed.scheme.lower(), netloc, parsed.path or "/", parsed.query, ""))


def title_of(data: bytes) -> str | None:
    sample = data[:256 * 1024].decode("utf-8", errors="ignore")
    match = re.search(r"<title\b[^>]*>(.*?)</title\s*>", sample, re.I | re.S)
    if not match:
        return None
    return html.unescape(re.sub(r"\s+", " ", match.group(1)).strip())


def text_sample(data: bytes) -> str:
    return data[:256 * 1024].decode("utf-8", errors="ignore")


def html_like(data: bytes) -> bool:
    text = text_sample(data).lstrip("\ufeff \t\r\n")
    # The preserved encyclopedia pages are served as text/html even though
    # their first line is an unterminated ``xml-stylesheet`` processing
    # instruction.  A strict XML parser therefore reports ``unclosed token``
    # while a browser's HTML parser still reaches the real ``<html>`` root.
    # Strip only leading comments/processing-instruction lines for the body
    # sniff; retain the original bytes and strict-XML diagnostics elsewhere.
    while True:
        if text.startswith("<!--"):
            end = text.find("-->", 4)
            if end < 0:
                break
            text = text[end + 3 :].lstrip()
            continue
        if text.startswith("<?"):
            end = text.find("?>", 2)
            if end >= 0:
                text = text[end + 2 :].lstrip()
                continue
            # The historical first line has no closing ``?>``.  Treat one
            # physical line as the browser-tolerated PI and continue sniffing.
            newline = text.find("\n")
            if newline >= 0:
                text = text[newline + 1 :].lstrip()
            break
        break
    return bool(re.match(r"^(?:<!doctype\s+html\b|<html\b|<head\b|<body\b)", text, re.I))


def magic(data: bytes, extension: str) -> tuple[bool | None, str]:
    extension = extension.casefold()
    if extension in {".jpg", ".jpeg"}:
        return data.startswith(b"\xff\xd8\xff"), "jpeg"
    if extension == ".gif":
        return data.startswith((b"GIF87a", b"GIF89a")), "gif"
    if extension == ".png":
        return data.startswith(b"\x89PNG\r\n\x1a\n"), "png"
    if extension == ".webp":
        return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP", "webp"
    if extension == ".swf":
        return data.startswith((b"FWS", b"CWS", b"ZWS")), "swf"
    return None, "unclassified"


def error_title(title: str | None) -> bool:
    if not title:
        return False
    value = title.casefold()
    return "404" in value or "not found" in value or ("error" in value and "world of warcraft" in value)


def guide_title(title: str | None) -> bool:
    if not title:
        return False
    value = title.casefold()
    return "world of warcraft" in value and any(x in value for x in ("beginner", "game guide", "guide"))


def redirect_target_of(data: bytes, original: str) -> str | None:
    """Return a canonical meta-refresh target when the document has one."""

    text = text_sample(data)
    match = re.search(
        r"<meta\b[^>]*http-equiv\s*=\s*['\"]?refresh['\"]?[^>]*content\s*=\s*['\"]?([^>\"']+)",
        text,
        re.I,
    )
    if not match:
        match = re.search(r"<meta\b[^>]*content\s*=\s*['\"]?([^>\"']+)[^>]*http-equiv\s*=\s*['\"]?refresh", text, re.I)
    if not match:
        return None
    content = html.unescape(match.group(1))
    target_match = re.search(r"url\s*=\s*([^;]+)", content, re.I)
    if not target_match:
        target_match = re.search(r"(?:^|;)\s*([^;]+)", content, re.I)
    if not target_match:
        return None
    target = target_match.group(1).strip().strip("'\"")
    if not target:
        return None
    return canonical_url(urllib.parse.urljoin(original, target))


def declared_mime(headers: dict[str, Any] | None) -> str | None:
    if not headers:
        return None
    for key, value in headers.items():
        if str(key).casefold() == "content-type":
            return str(value)
    return None


def mime_family(mime: str | None, data: bytes = b"") -> str:
    value = (mime or "").casefold()
    if value.startswith("text/html"):
        return "html"
    if value.startswith("application/xhtml+xml") or value.startswith("application/xml") or value.endswith("+xml"):
        return "xml"
    if value.startswith("image/"):
        return "image"
    if "javascript" in value or value in {"text/css", "text/xsl"}:
        return "script_style"
    if html_like(data):
        return "html_sniffed"
    return "other"


def normalized_title(value: str | None) -> str:
    if not value:
        return ""
    value = value.casefold().replace("&", " and ")
    value = re.sub(r"[^\w\s]+", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip()


def title_matches(actual: str | None, expected: str | None) -> bool:
    a, e = normalized_title(actual), normalized_title(expected)
    if not a or not e:
        return False
    if a == e:
        return True
    if a.removeprefix("the ") == e.removeprefix("the "):
        return True
    return a.endswith(" " + e) or e.endswith(" " + a)


def classify_body(data: bytes, original: str, role: str | None, kind: str | None, mime: str | None, expected_title: str | None = None) -> dict[str, Any]:
    path = urllib.parse.urlsplit(original).path
    extension = Path(path).suffix.casefold()
    title = title_of(data)
    text = text_sample(data)
    html_body = html_like(data)
    error = error_title(title) or "/errors/error404.html" in original.casefold()
    guide = guide_title(title)
    is_image = str(kind or "").casefold() == "image" or extension in IMAGE_EXTS or (mime or "").casefold().startswith("image/")
    is_script = str(kind or "").casefold() in {"js", "css", "xsl", "xslt"} or extension in SCRIPT_EXTS
    family = mime_family(mime, data)
    xml_kind = str(kind or "").casefold() in {"xml", "xsl", "xslt"} or family == "xml" or extension in {".xsl", ".xslt"}
    xml_parse_error: str | None = None
    redirect_target: str | None = None
    if is_image:
        magic_ok, magic_type = magic(data, extension)
        if magic_ok is True and not error and not guide:
            status = "valid_image"
        elif error:
            status = "origin404"
        elif guide:
            status = "modernGuide"
        else:
            status = "invalid_image"
    elif extension == ".htc" or str(kind or "").casefold() in {"htc", "legacy_component"}:
        # IE behavior components use public: elements and JScript, often
        # without XML namespace declarations. Preserve and identify the
        # component representation without pretending it is strict XML or
        # executing it in a modern browser.
        magic_ok, magic_type = None, "ie_behavior_component"
        if error:
            status = "origin404"
        elif guide or html_body:
            status = "modernGuide" if guide else "invalid_legacy_component"
        elif re.search(r"<public:component\b", text, re.I) and re.search(r"<script\b", text, re.I):
            status = "valid_legacy_component"
        else:
            status = "invalid_legacy_component"
    elif xml_kind:
        magic_ok, magic_type = magic(data, extension)
        if error:
            status = "origin404"
        elif guide or html_body:
            # XML MIME/plan metadata wins only for genuine XML/XSL.  An HTML
            # error page replayed with an XML suffix remains invalid.
            status = "modernGuide" if guide else "invalid_xml_html_body"
        else:
            try:
                ET.fromstring(data)
            except (ET.ParseError, ValueError) as exc:
                xml_parse_error = str(exc)
                status = "invalid_xsl" if str(kind or "").casefold() in {"xsl", "xslt"} or extension in {".xsl", ".xslt"} else "invalid_xml"
            else:
                status = "valid_xsl" if str(kind or "").casefold() in {"xsl", "xslt"} or extension in {".xsl", ".xslt"} else "valid_xml"
    elif is_script:
        magic_ok, magic_type = magic(data, extension)
        if error:
            status = "origin404"
        elif guide or html_body:
            status = "modernGuide" if guide else "invalid_non_html_script"
        elif data:
            status = "valid_script_style"
        else:
            status = "empty"
    else:
        magic_ok, magic_type = magic(data, extension)
        redirect_target = redirect_target_of(data, original)
        redirect = redirect_target is not None or bool(re.search(r"<meta\b[^>]*(?:http-equiv\s*=\s*['\"]?refresh|url\s*=)", text, re.I))
        if error:
            status = "origin404"
        elif guide:
            status = "modernGuide"
        elif redirect:
            expected_redirect = canonical_url(urllib.parse.urljoin(original, "index.xml"))
            status = "valid_redirect_document" if redirect_target == expected_redirect else "redirect_html"
        elif html_body and (title_matches(title, expected_title) if expected_title else True):
            status = "valid_html"
        elif html_body:
            status = "html_title_mismatch"
        else:
            status = "invalid_non_html_body"
    return {
        "status": status,
        "extension": extension,
        "declared_mime": mime,
        "mime_family": mime_family(mime, data),
        "magic_type": magic_type,
        "magic_ok": magic_ok,
        "title": title,
        "expected_title": expected_title,
        "title_match": title_matches(title, expected_title) if expected_title else None,
        "html_body": html_body,
        "redirect_target": redirect_target if not (is_image or is_script or xml_kind) else None,
        "xml_parse_error": xml_parse_error,
        "bytes": len(data),
    }


def _catalog_values(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, list):
        for entry in value:
            yield from _catalog_values(entry)
    elif isinstance(value, dict):
        for key in ("items", "entries", "records", "captures", "entities"):
            if isinstance(value.get(key), list):
                yield from _catalog_values(value[key])
                return
        if value.get("original") or value.get("logical_url") or value.get("url"):
            yield value


def catalog_referenced_zip_paths() -> list[Path]:
    """Find only ZIPs explicitly named by saved catalog records.

    The normal scan covers current 2008/sample backup roots.  A later catalog
    may point at a selected 2010 payload ZIP; that ZIP is opened on demand for
    CRC/object verification, without recursively traversing the whole 2010
    archive tree.
    """

    result: set[Path] = set()
    bases = [ROOT / "research" / "acquisition-2008" / name for name in ("core", "dependencies", "reuse", "text-completion", "ie-completion", "remaining-download", "final-completion")]
    for base in bases:
        if not base.exists():
            continue
        for catalog_path in sorted(p for p in base.glob("*.json") if "catalog" in p.name.casefold()):
            value = load_json(catalog_path, {})
            for item in _catalog_values(value):
                source = item.get("source") if isinstance(item.get("source"), dict) else {}
                manifest_name = item.get("manifest") or item.get("source_manifest") or source.get("manifest")
                zip_name = item.get("zip_file") or item.get("zip_part") or source.get("zip_file") or source.get("zip_part")
                if not zip_name:
                    continue
                candidates: list[Path] = []
                if manifest_name:
                    manifest_path = ROOT / str(manifest_name).replace("\\", "/")
                    candidates.append(manifest_path.parent / str(zip_name))
                candidates.extend([
                    catalog_path.parent / str(zip_name),
                    ROOT / str(zip_name).replace("\\", "/"),
                ])
                for candidate in candidates:
                    if candidate.exists() and candidate.is_file() and candidate.suffix.casefold() == ".zip":
                        result.add(candidate.resolve())
                        break
    return sorted(result)


def scan_zips() -> tuple[dict[tuple[str, str], bytes], list[dict[str, Any]], list[str]]:
    sources = [ROOT / "backups" / "20080512", ROOT / "backups" / "20080512-sample"]
    sources.extend(catalog_referenced_zip_paths())
    data_by_location: dict[tuple[str, str], bytes] = {}
    reports: list[dict[str, Any]] = []
    errors: list[str] = []
    seen: set[Path] = set()
    for base in sources:
        if not base.exists():
            continue
        zip_paths = [base] if base.is_file() and base.suffix.casefold() == ".zip" else sorted(base.rglob("*.zip"))
        for path in zip_paths:
            if path.resolve() in seen:
                continue
            seen.add(path.resolve())
            report: dict[str, Any] = {"zip_file": rel(path), "entry_count": 0, "crc_ok": False, "sha_named_entries_ok": True, "errors": []}
            try:
                with zipfile.ZipFile(path, "r", allowZip64=True) as archive:
                    infos = archive.infolist()
                    report["entry_count"] = len(infos)
                    bad = archive.testzip()
                    if bad is None:
                        report["crc_ok"] = True
                    else:
                        report["errors"].append(f"CRC failure:{bad}")
                    seen_names: set[str] = set()
                    for info in infos:
                        if info.filename in seen_names:
                            report["errors"].append(f"duplicate entry:{info.filename}")
                        seen_names.add(info.filename)
                        try:
                            body = archive.read(info.filename)
                        except Exception as exc:  # pragma: no cover - corrupted archive path
                            report["errors"].append(f"read error:{info.filename}:{exc}")
                            continue
                        data_by_location[(rel(path), info.filename)] = body
                        match = re.fullmatch(r"objects/([0-9a-f]{64})\.bin", info.filename)
                        if match and match.group(1) != sha256(body):
                            report["sha_named_entries_ok"] = False
                            report["errors"].append(f"SHA name mismatch:{info.filename}")
            except (OSError, zipfile.BadZipFile) as exc:
                report["errors"].append(f"ZIP open error:{exc}")
            if report["errors"]:
                errors.extend([f"{report['zip_file']}:{x}" for x in report["errors"]])
            reports.append(report)
    return data_by_location, reports, errors


def manifest_candidates(data_by_location: dict[tuple[str, str], bytes]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    paths: list[Path] = []
    for base in (ROOT / "backups" / "20080512", ROOT / "backups" / "20080512-sample"):
        if base.exists():
            paths.extend(sorted(base.rglob("manifest.jsonl")))
    for path in paths:
        for item in load_jsonl(path):
            line = item.pop("_line", 0)
            item["source_manifest"] = rel(path)
            item["manifest_line"] = line
            if item.get("status") != "success":
                failures.append({
                    "source_manifest": rel(path),
                    "manifest_line": line,
                    "original": item.get("original"),
                    "logical_url": canonical_url(str(item.get("original", ""))),
                    "status": item.get("status"),
                    "failure_reason": item.get("failure_reason") or item.get("error"),
                    "requested_timestamp": item.get("requested_timestamp"),
                })
                continue
            zip_part = item.get("zip_part")
            zip_entry = item.get("zip_entry")
            zip_path = path.parent / str(zip_part) if zip_part else None
            zip_rel = rel(zip_path) if zip_path and zip_path.exists() else None
            body = data_by_location.get((zip_rel, str(zip_entry))) if zip_rel and zip_entry else None
            item["zip_file"] = zip_rel
            item["body_available"] = body is not None
            item["body_bytes"] = body
            records.append(item)
    return records, failures


def direct_candidate(original: str, body_path: Path, headers_path: Path | None, role: str, kind: str, requested: str, actual: str | None = None, expected_digest: str | None = None, source_note: str | None = None) -> dict[str, Any]:
    body = body_path.read_bytes()
    headers_doc = load_json(headers_path, {}) if headers_path else {}
    headers = headers_doc.get("headers", {}) if isinstance(headers_doc, dict) else {}
    url = None
    if isinstance(headers_doc, dict):
        url = headers_doc.get("url") or headers_doc.get("requested")
    actual_from_url = timestamp(url)
    actual = actual or actual_from_url
    return {
        "original": original,
        "logical_url": canonical_url(original),
        "source_type": "direct_file",
        "source_file": rel(body_path),
        "source_manifest": None,
        "manifest_line": None,
        "zip_file": None,
        "zip_entry": None,
        "requested_timestamp": requested,
        "actual_timestamp": actual,
        "actual_url": url,
        "http_status": headers_doc.get("status", 200) if isinstance(headers_doc, dict) else 200,
        "response_headers": headers,
        "sha256": sha256(body),
        "content_length": len(body),
        "declared_mime": declared_mime(headers),
        "cdx_digest": expected_digest,
        "source_note": source_note,
        "body_available": True,
        "body_bytes": body,
        "role": role,
        "kind": kind,
    }


def manifest_to_candidate(record: dict[str, Any], data_by_location: dict[tuple[str, str], bytes]) -> dict[str, Any]:
    body = record.get("body_bytes")
    original = str(record.get("original", ""))
    headers = record.get("response_headers") or {}
    mime = declared_mime(headers)
    if body is not None:
        body_hash = sha256(body)
        body_length = len(body)
    else:
        body_hash = record.get("sha256")
        body_length = record.get("content_length")
    return {
        "original": original,
        "logical_url": canonical_url(original),
        "source_type": "manifest_zip",
        "source_file": None,
        "source_manifest": record.get("source_manifest"),
        "manifest_line": record.get("manifest_line"),
        "zip_file": record.get("zip_file"),
        "zip_entry": record.get("zip_entry"),
        "requested_timestamp": timestamp(record.get("requested_timestamp")),
        "actual_timestamp": timestamp(record.get("actual_timestamp")) or timestamp(record.get("memento_datetime")) or timestamp(record.get("actual_url")),
        "actual_url": record.get("actual_url"),
        "http_status": record.get("http_status"),
        "response_headers": headers,
        "sha256": body_hash,
        "manifest_sha256": record.get("sha256"),
        "content_length": body_length,
        "manifest_content_length": record.get("content_length"),
        "declared_mime": mime,
        "cdx_digest": record.get("cdx_digest") or record.get("cdx_sha1"),
        "source_note": record.get("role"),
        "body_available": body is not None,
        "body_bytes": body,
        "role": record.get("role"),
        "kind": record.get("kind"),
    }


def discover_catalog_records(data_by_location: dict[tuple[str, str], bytes]) -> list[dict[str, Any]]:
    """Accept common final-catalog shapes without requiring one exact schema."""

    paths: list[Path] = []
    for base in (ROOT / "research" / "acquisition-2008" / name for name in ("core", "dependencies", "reuse", "text-completion", "ie-completion", "remaining-download", "final-completion")):
        if base.exists():
            paths.extend(sorted(p for p in base.glob("*.json") if "catalog" in p.name.casefold()))
    result: list[dict[str, Any]] = []

    def collect(value: Any) -> Iterable[dict[str, Any]]:
        if isinstance(value, list):
            for x in value:
                yield from collect(x)
        elif isinstance(value, dict):
            for key in ("items", "entries", "records", "captures", "entities"):
                if isinstance(value.get(key), list):
                    yield from collect(value[key])
                    return
            if value.get("original") or value.get("logical_url") or value.get("url"):
                yield value

    for path in paths:
        value = load_json(path)
        for item in collect(value):
            original = item.get("original") or item.get("logical_url") or item.get("url")
            if not original:
                continue
            item = dict(item)
            item["source_catalog"] = rel(path)
            item["original"] = str(original)
            source = item.get("source") if isinstance(item.get("source"), dict) else {}
            body: bytes | None = None
            body_path = item.get("body_path") or item.get("source_file") or item.get("file") or source.get("body_path") or source.get("source_file") or source.get("file")
            if body_path:
                p = ROOT / str(body_path).replace("\\", "/")
                if p.exists() and p.is_file():
                    body = p.read_bytes()
                    item["source_file"] = rel(p)
            manifest_name = item.get("manifest") or item.get("source_manifest") or source.get("manifest")
            item["source_manifest"] = manifest_name
            zfile = item.get("zip_file") or item.get("zip_part") or source.get("zip_file") or source.get("zip_part")
            zentry = item.get("zip_entry") or source.get("zip_entry")
            if zentry:
                item["zip_entry"] = str(zentry)
            item["cdx_raw_source"] = item.get("cdx_raw_source") or source.get("cdx_raw_source")
            if item.get("provenance") == "cdx_verified_payload_reuse" or item.get("selection_status") == "cdx_verified_payload_reuse":
                item.setdefault("acquisition", "reuse")
            if body is None and zfile and zentry:
                zip_candidates: list[Path] = []
                if manifest_name:
                    manifest_path = ROOT / str(manifest_name).replace("\\", "/")
                    zip_candidates.append(manifest_path.parent / str(zfile))
                zip_candidates.extend([
                    path.parent / str(zfile),
                    ROOT / str(zfile).replace("\\", "/"),
                ])
                for p in zip_candidates:
                    if p.exists() and p.is_file():
                        body = data_by_location.get((rel(p), str(zentry)))
                        if body is not None:
                            item["zip_file"] = rel(p)
                            break
                if body is None:
                    item["zip_file"] = str(zfile)
            item["body_bytes"] = body
            item["body_available"] = body is not None
            item["actual_timestamp"] = timestamp(item.get("actual_timestamp") or item.get("entity_observed_capture_timestamp") or item.get("memento_datetime") or item.get("actual_url"))
            item["requested_timestamp"] = timestamp(item.get("requested_timestamp"))
            item["indexed_capture_timestamp"] = timestamp(
                item.get("indexed_capture_timestamp")
                or item.get("selected_pre_anchor_cdx_timestamp")
                or source.get("indexed_capture_timestamp")
            )
            item["response_headers"] = item.get("response_headers") or item.get("headers") or source.get("response_headers") or {}
            item["declared_mime"] = item.get("declared_mime") or item.get("mime") or item.get("response_mime") or item.get("content_type") or source.get("mime") or source.get("response_mime") or declared_mime(item["response_headers"])
            item["manifest_sha256"] = item.get("sha256")
            item["manifest_content_length"] = item.get("content_length") or item.get("bytes")
            item["cdx_digest"] = item.get("cdx_digest") or item.get("cdx_sha1") or item.get("selection_cdx_digest") or source.get("cdx_digest")
            item["content_length"] = len(body) if body is not None else item.get("content_length")
            item["sha256"] = sha256(body) if body is not None else item.get("sha256")
            item["logical_url"] = canonical_url(str(original))
            item["source_type"] = "catalog"
            item["role"] = item.get("role")
            item["kind"] = item.get("kind")
            result.append(item)
    return result


def commented_reference_reason(item: dict[str, Any]) -> str | None:
    """Detect a plan item whose every local source reference is commented out.

    This is deliberately narrow: it only reads the small local source files
    already named by dependency-plan.json and never treats an absent source as
    proof that a URL is inactive.  The known ``featured_textbg.png`` CSS URL
    is wrapped in a ``/* ... */`` comment and is therefore an inactive
    historical candidate rather than an active missing image.
    """

    sources = item.get("sources") or []
    seen = 0
    active = 0
    for source in sources:
        local = source.get("from_local_source") or {}
        body_name = local.get("body") or local.get("source_file")
        reference = str(source.get("reference") or "")
        if not body_name or not reference:
            continue
        body_path = ROOT / str(body_name).replace("\\", "/")
        if not body_path.exists() or not body_path.is_file():
            continue
        try:
            text = body_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        needles = [reference, urllib.parse.unquote(reference)]
        if reference.startswith("../") or reference.startswith("./"):
            needles.append(Path(reference).name)
        position = -1
        needle_used = ""
        for needle in needles:
            if needle:
                position = text.find(needle)
                if position >= 0:
                    needle_used = needle
                    break
        if position < 0:
            continue
        seen += 1
        before = text[:position]
        if before.rfind("/*") <= before.rfind("*/"):
            active += 1
    if seen and active == 0:
        return "commented_reference"
    return None


def load_plan_meta() -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    full = load_json(ROOT / "research" / "acquisition-2008" / "core" / "full-plan.json", {}) or {}
    mapping = load_json(ROOT / "research" / "acquisition-2008" / "core" / "source-mapping.json", {}) or {}
    dep = load_json(ROOT / "research" / "acquisition-2008" / "dependencies" / "dependency-plan.json", {}) or {}
    core_items = full.get("items", []) if isinstance(full, dict) else []
    map_by_logical = {canonical_url(str(x.get("original", ""))): x for x in mapping.get("items", []) if x.get("original")}
    meta_by_logical: dict[str, dict[str, Any]] = {}
    for item in core_items:
        if not item.get("original"):
            continue
        logical = canonical_url(str(item["original"]))
        mapped = map_by_logical.get(logical, {})
        selection = mapped.get("selection", {}) or {}
        cache = mapped.get("cache", {}) or {}
        meta_by_logical.setdefault(logical, {}).update({
            "logical_url": logical,
            "core": True,
            "expected_title": item.get("expected_title") or map_by_logical.get(logical, {}).get("expected_title"),
            "role": "core_page",
            "kind": "html",
            "selected_timestamp": timestamp(item.get("timestamp") or selection.get("timestamp")),
            "indexed_capture_timestamp": timestamp(item.get("selected_pre_anchor_cdx_timestamp") or selection.get("timestamp")),
            "cdx_digest": item.get("selection_cdx_digest") or selection.get("digest"),
            "cdx_length": item.get("selection_cdx_length") or selection.get("length"),
            "cdx_mimetype": item.get("selection_cdx_mimetype") or selection.get("mimetype"),
            "acquisition": item.get("acquisition") or mapped.get("acquisition"),
            "cache_source": cache.get("cache_source"),
            "expected_sha256": cache.get("sha256"),
            "expected_content_length": cache.get("bytes"),
            "originals": [item.get("original")],
            "plan_scopes": ["core"],
        })
    dep_items = dep.get("items", []) if isinstance(dep, dict) else []
    for item in dep_items:
        if not item.get("original"):
            continue
        logical = canonical_url(str(item["original"]))
        old = meta_by_logical.setdefault(logical, {"logical_url": logical, "originals": [], "plan_scopes": []})
        old.setdefault("originals", []).append(item.get("original"))
        old.setdefault("plan_scopes", []).append("dependencies")
        inactive_reason = commented_reference_reason(item)
        if inactive_reason:
            old.setdefault("inactive_reason", inactive_reason)
        if not old.get("core"):
            old.setdefault("role", item.get("role"))
            old.setdefault("kind", item.get("kind"))
            sel = item.get("selection") or {}
            old.setdefault("selected_timestamp", timestamp(item.get("timestamp") or sel.get("timestamp")))
            # A fallback anchor request is not an observed CDX row.
            old.setdefault("indexed_capture_timestamp", timestamp(sel.get("timestamp")) if sel.get("digest") else None)
            old.setdefault("cdx_digest", sel.get("digest"))
            old.setdefault("cdx_length", sel.get("length"))
            old.setdefault("cdx_mimetype", sel.get("mimetype"))
            existing = item.get("existing") or {}
            old.setdefault("acquisition", "reuse" if existing else ("download" if item.get("download") else None))
            old.setdefault("cache_source", existing.get("provenance"))
            old.setdefault("expected_sha256", existing.get("sha256"))
            old.setdefault("expected_content_length", existing.get("bytes"))
        elif item.get("role") in {"core_image", "core_dependency"}:
            old.setdefault("related_roles", []).append(item.get("role"))
    deferred = dep.get("deferred_core", []) if isinstance(dep, dict) else []
    return meta_by_logical, core_items, dep_items, {"deferred": deferred, "dependency_counts": dep.get("counts", {}), "dependency_limits": dep.get("limits", {})}


def build_candidates(meta_by_logical: dict[str, dict[str, Any]], data_by_location: dict[tuple[str, str], bytes], manifests: list[dict[str, Any]], catalogs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = [manifest_to_candidate(r, data_by_location) for r in manifests]
    candidates.extend(catalogs)
    # Explicit baseline provenance is authoritative for the exact homepage and
    # the three encyclopedia JS/CSS inputs.  Their headers provide the actual
    # replay timestamp and MIME.
    baseline = ROOT / "research" / "baseline"
    baseline_items = [
        ("http://www.worldofwarcraft.com/info/encyclopedia/index.xml", baseline / "index.xml", baseline / "headers.json", "core_page", "html", ANCHOR),
        ("http://www.worldofwarcraft.com/info/encyclopedia/scripts/cascade.js", baseline / "scripts" / "cascade.js", baseline / "scripts" / "cascade.js.headers.json", "shared_dependency", "js", "20080512210044"),
        ("http://www.worldofwarcraft.com/info/encyclopedia/scripts/topic-list.js", baseline / "scripts" / "topic-list.js", baseline / "scripts" / "topic-list.js.headers.json", "shared_dependency", "js", "20080512210044"),
        ("http://www.worldofwarcraft.com/info/encyclopedia/styles/stylesheet.css", baseline / "styles" / "stylesheet.css", baseline / "styles" / "stylesheet.css.headers.json", "shared_dependency", "css", "20080512210044"),
    ]
    for original, body_path, headers_path, role, kind, requested in baseline_items:
        if body_path.exists():
            candidates.append(direct_candidate(original, body_path, headers_path, role, kind, requested, source_note="baseline_explicit"))
    # Attach plan CDX metadata and classify every available body.
    for candidate in candidates:
        logical = candidate["logical_url"]
        meta = meta_by_logical.get(logical, {})
        candidate["plan_meta"] = meta
        candidate["role"] = candidate.get("role") or meta.get("role")
        candidate["kind"] = candidate.get("kind") or meta.get("kind")
        candidate["expected_title"] = meta.get("expected_title")
        # A reuse catalog carries a specific CDX row whose digest proves these
        # bytes existed historically.  A generic download plan timestamp must
        # not replace that row or the observed entity's actual date.
        reuse_catalog = candidate.get("acquisition") == "reuse" and candidate.get("cdx_digest")
        candidate["indexed_capture_timestamp"] = (candidate.get("indexed_capture_timestamp") or meta.get("indexed_capture_timestamp")) if reuse_catalog else (meta.get("indexed_capture_timestamp") or candidate.get("indexed_capture_timestamp"))
        candidate["expected_cdx_digest"] = candidate.get("cdx_digest") or meta.get("cdx_digest")
        candidate["acquisition"] = candidate.get("acquisition") or meta.get("acquisition")
        candidate["cache_source"] = meta.get("cache_source") or candidate.get("cache_source") or candidate.get("provenance")
        candidate["expected_sha256"] = meta.get("expected_sha256") or candidate.get("expected_sha256")
        candidate["expected_content_length"] = meta.get("expected_content_length") or candidate.get("expected_content_length")
        if candidate.get("body_available") and candidate.get("body_bytes") is not None:
            candidate["body"] = classify_body(candidate["body_bytes"], candidate["original"], candidate.get("role"), candidate.get("kind"), candidate.get("declared_mime") or meta.get("cdx_mimetype"), candidate.get("expected_title"))
            candidate["computed_sha256"] = sha256(candidate["body_bytes"])
            candidate["computed_cdx_sha1"] = cdx_sha1(candidate["body_bytes"])
            expected_sha = candidate.get("manifest_sha256") or candidate.get("expected_sha256")
            if expected_sha:
                candidate["sha256_matches_manifest"] = candidate["computed_sha256"] == expected_sha
            else:
                candidate["sha256_matches_manifest"] = True
            expected_length = candidate.get("manifest_content_length")
            if expected_length is None:
                expected_length = candidate.get("expected_content_length")
            if expected_length is not None:
                try:
                    candidate["length_matches_manifest"] = len(candidate["body_bytes"]) == int(expected_length)
                except (TypeError, ValueError):
                    candidate["length_matches_manifest"] = False
            else:
                candidate["length_matches_manifest"] = True
            expected = str(candidate.get("expected_cdx_digest") or "")
            candidate["cdx_digest_matches"] = (candidate["computed_cdx_sha1"] == expected) if expected else None
            candidate["integrity_ok"] = bool(candidate["sha256_matches_manifest"] and candidate["length_matches_manifest"] and candidate["cdx_digest_matches"] is not False)
        else:
            candidate["body"] = {"status": "missing", "bytes": None}
            candidate["computed_sha256"] = None
            candidate["computed_cdx_sha1"] = None
            candidate["sha256_matches_manifest"] = None
            candidate["length_matches_manifest"] = None
            candidate["cdx_digest_matches"] = None
            candidate["integrity_ok"] = False
        # requested/selected timestamps are planning facts, not an observed
        # replay date.  Keep actual/entity time unknown unless the manifest,
        # archive URL, or direct headers supplied it.
        candidate["actual_timestamp"] = candidate.get("actual_timestamp")
        # Keep payload-reuse provenance explicit.  For the baseline homepage,
        # `indexed_capture_timestamp` is the pre-anchor CDX row while the
        # observed body was saved from the exact anchor replay.  These are
        # separate facts and must not be collapsed into a synthetic memento.
        candidate["entity_observed_capture_timestamp"] = candidate.get("actual_timestamp")
        candidate["cdx_verified_payload_reuse"] = bool(
            candidate.get("acquisition") == "reuse"
            and candidate.get("expected_cdx_digest")
            and candidate.get("cdx_digest_matches") is True
            and candidate.get("indexed_capture_timestamp")
            and candidate.get("entity_observed_capture_timestamp")
            and candidate.get("indexed_capture_timestamp") != candidate.get("entity_observed_capture_timestamp")
        )
        # A verified payload reuse inherits the historical CDX capture's
        # temporal position.  The later replay used to obtain the identical
        # bytes remains visible as `entity_observed_capture_timestamp`.
        temporal_reference = (
            candidate.get("indexed_capture_timestamp")
            if candidate.get("cdx_verified_payload_reuse")
            else candidate.get("entity_observed_capture_timestamp")
        )
        candidate["temporal_reference_timestamp"] = temporal_reference
        actual = temporal_reference
        if actual and actual <= ANCHOR:
            candidate["temporal_class"] = "anchor_consistent"
        elif actual and actual[:8] == ANCHOR_DAY and not meta.get("core") and candidate.get("role") not in {"core_page", "core"}:
            candidate["temporal_class"] = "same_day_static"
        elif actual:
            candidate["temporal_class"] = "temporal_supplement"
        else:
            candidate["temporal_class"] = "unknown"
        body_status = candidate["body"].get("status")
        candidate["body_valid"] = body_status in {
            "valid_html",
            "valid_image",
            "valid_script_style",
            "valid_xml",
            "valid_xsl",
            "valid_redirect_document",
            "valid_legacy_component",
        } and bool(candidate.get("integrity_ok"))
        candidate["candidate_state"] = "missing" if body_status == "missing" else ("preferred_candidate" if candidate["body_valid"] and candidate["temporal_class"] in {"anchor_consistent", "same_day_static"} else ("supplement_only" if candidate["body_valid"] else "invalid"))
    return candidates


def candidate_public(candidate: dict[str, Any] | None) -> dict[str, Any] | None:
    if candidate is None:
        return None
    drop = {"body_bytes", "plan_meta"}
    return {k: v for k, v in candidate.items() if k not in drop}


def choose_candidates(meta_by_logical: dict[str, dict[str, Any]], candidates: list[dict[str, Any]], core_items: list[dict[str, Any]], dep_items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    by_logical: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for c in candidates:
        if c.get("logical_url"):
            by_logical[c["logical_url"]].append(c)
    # Every planned URL, including duplicated deferred-core references, is
    # represented in plan_records below.
    logical_records: dict[str, dict[str, Any]] = {}
    expected_timestamp: dict[str, str | None] = {}
    for item in core_items + dep_items:
        if not item.get("original"):
            continue
        logical = canonical_url(str(item["original"]))
        meta = meta_by_logical.get(logical, {})
        logical_records.setdefault(logical, {"logical_url": logical, "originals": [], "plan_scopes": [], "roles": []})
        rec = logical_records[logical]
        rec["originals"].append(item["original"])
        scope = "core" if item in core_items else "dependencies"
        rec["plan_scopes"].append(scope)
        rec["roles"].append(item.get("role") or meta.get("role"))
        expected_timestamp.setdefault(logical, timestamp(item.get("timestamp") or (item.get("selection") or {}).get("timestamp")))
    for logical, meta in meta_by_logical.items():
        logical_records.setdefault(logical, {"logical_url": logical, "originals": meta.get("originals", []), "plan_scopes": meta.get("plan_scopes", []), "roles": [meta.get("role")]})
    preferred_runtime: dict[str, dict[str, Any]] = {}
    for logical, record in logical_records.items():
        meta = meta_by_logical.get(logical, {})
        pool = by_logical.get(logical, [])
        valid = [x for x in pool if x.get("body_valid")]
        target = meta.get("selected_timestamp") or expected_timestamp.get(logical)
        core = bool(meta.get("core"))
        def rank(c: dict[str, Any]):
            temporal = {"anchor_consistent": 0, "same_day_static": 1, "temporal_supplement": 2, "unknown": 3}.get(c.get("temporal_class"), 4)
            historical = c.get("temporal_reference_timestamp") or c.get("actual_timestamp")
            exact = 0 if target and historical == target else 1
            exact_home = 0 if core and logical.endswith("/index.xml") and c.get("actual_timestamp") == ANCHOR else 1
            source = 0 if c.get("source_note") == "baseline_explicit" else 1
            indexed_evidence = 0 if c.get("indexed_capture_timestamp") and c.get("expected_cdx_digest") and c.get("cdx_digest_matches") is True else 1
            return (exact_home, temporal, exact, source, -int(historical or "0"), indexed_evidence)
        valid_sorted = sorted(valid, key=rank)
        selected = valid_sorted[0] if valid_sorted else None
        invalid = [x for x in pool if x.get("candidate_state") == "invalid"]
        supplement = [x for x in valid if x.get("temporal_class") == "temporal_supplement"]
        if selected is not None:
            state = "preferred" if selected.get("temporal_class") in {"anchor_consistent", "same_day_static"} else "supplement-only"
            if state == "preferred":
                preferred_runtime[logical] = selected
        elif invalid:
            state = "invalid"
        elif supplement:
            state = "supplement-only"
        else:
            state = "missing"
        record.update({
            "state": state,
            "role": meta.get("role"),
            "kind": meta.get("kind"),
            "activity_scope": "inactive" if (meta.get("inactive_reason") or meta.get("role") == "historical_entry_candidate") else "active",
            "inactive_reason": meta.get("inactive_reason") or ("historical_entry_candidate" if meta.get("role") == "historical_entry_candidate" else None),
            "expected_title": meta.get("expected_title"),
            "selected_capture": candidate_public(selected),
            "candidate_count": len(pool),
            "valid_candidate_count": len(valid),
            "invalid_candidate_count": len(invalid),
            "candidates": [candidate_public(x) for x in pool],
        })
    return list(logical_records.values()), preferred_runtime


def public_plan_records(core_items: list[dict[str, Any]], dep_items: list[dict[str, Any]], deferred: list[dict[str, Any]], logical_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for scope, items in (("core", core_items), ("dependencies", dep_items), ("deferred_core", deferred)):
        for item in items:
            original = item.get("original")
            if not original:
                continue
            logical = canonical_url(str(original))
            logical_record = logical_map.get(logical, {})
            records.append({
                "plan_scope": scope,
                "original": original,
                "logical_url": logical,
                "role": item.get("role") or item.get("kind"),
                "kind": item.get("kind"),
                "timestamp": timestamp(item.get("timestamp") or (item.get("selection") or {}).get("timestamp")),
                "state": logical_record.get("state", "missing"),
                "activity_scope": logical_record.get("activity_scope", "active"),
                "inactive_reason": logical_record.get("inactive_reason"),
                "selected_capture_id": (logical_record.get("selected_capture") or {}).get("source_manifest") and f"{logical_record['selected_capture'].get('source_manifest')}:{logical_record['selected_capture'].get('manifest_line')}",
                "alias_of_core": scope == "deferred_core",
            })
    return records


def dependency_edges() -> dict[str, Any]:
    graph_path = ROOT / "research" / "acquisition-2008" / "dependencies" / "dependency-graph.json"
    graph = load_json(graph_path, {}) or {}
    edges = graph.get("edges", []) if isinstance(graph, dict) else []
    unresolved = graph.get("unresolved", []) if isinstance(graph, dict) else []
    by_target: Counter[str] = Counter()
    by_kind: Counter[str] = Counter()
    by_role: Counter[str] = Counter()
    examples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges:
        target = canonical_url(str(edge.get("resolved") or edge.get("to") or ""))
        if not target:
            continue
        by_target[target] += 1
        by_kind[str(edge.get("kind") or "unknown")] += 1
        by_role[str(edge.get("role") or "unknown")] += 1
        if len(examples[target]) < 8:
            examples[target].append({k: edge.get(k) for k in ("from", "reference", "kind", "role", "ref_type")})
    return {
        "source": rel(graph_path) if graph_path.exists() else None,
        "node_count": len(graph.get("nodes", [])) if isinstance(graph, dict) else 0,
        "edge_count": len(edges),
        "edge_kind_counts": dict(by_kind),
        "edge_role_counts": dict(by_role),
        "referenced_target_count": len(by_target),
        "referenced_target_counts": dict(by_target),
        "reference_examples": dict(examples),
        "unresolved_reference_count": len(unresolved),
        "unresolved_reason_counts": dict(Counter(str(x.get("reason") or "unknown") for x in unresolved if isinstance(x, dict))),
        "reference_integrity_errors": [x for x in unresolved if isinstance(x, dict) and not str(x.get("reason") or "").startswith("dynamic_")],
    }


def download_batches(planned_logicals: set[str]) -> dict[str, Any]:
    """Summarize local downloader batches without treating superseded runs as active.

    A stopped first dependency attempt left ``dependencies/text/summary.json``
    without ``finished_at``.  Its only current-plan success is duplicated by
    the finished ``text-v2`` batch and its failed URLs are no longer planned;
    it is therefore retained as stale evidence rather than blocking the active
    acquisition status.
    """

    summaries: list[dict[str, Any]] = []
    for base in (ROOT / "backups" / "20080512", ROOT / "backups" / "20080512-sample"):
        if not base.exists():
            continue
        for summary_path in sorted(base.rglob("summary.json")):
            summary = load_json(summary_path, {}) or {}
            termination_path = summary_path.parent / "termination.json"
            termination = load_json(termination_path, {}) or {}
            manifest_path = summary_path.parent / "manifest.jsonl"
            records = load_jsonl(manifest_path)
            completion_path = summary_path.parent / "completion.json"
            completion = load_json(completion_path, {}) or {}
            # A custom preservation summary may replace the downloader's
            # schema. Accept a separately observed terminal state only when
            # it remains bound to the exact local manifest, summary and ZIPs.
            completion_ok = bool(
                completion.get("status") == "completed_verified"
                and manifest_path.exists()
                and completion.get("manifest_sha256") == sha256(manifest_path.read_bytes())
                and completion.get("summary_sha256") == sha256(summary_path.read_bytes())
                and len(records) == completion.get("manifest_success_count")
                and all(x.get("status") == "success" for x in records)
                and completion.get("zip_sha256")
                and all(
                    (summary_path.parent / name).is_file()
                    and sha256((summary_path.parent / name).read_bytes()) == digest
                    for name, digest in completion.get("zip_sha256", {}).items()
                )
            )
            coverage = {canonical_url(str(x.get("original", ""))) for x in records if x.get("original")}
            successes = {canonical_url(str(x.get("original", ""))) for x in records if x.get("original") and x.get("status") == "success"}
            summaries.append({
                "summary_file": rel(summary_path),
                "manifest_file": rel(manifest_path) if manifest_path.exists() else None,
                "finished_at": summary.get("finished_at"),
                "termination": termination,
                "termination_file": rel(termination_path) if termination_path.exists() else None,
                "completion_file": rel(completion_path) if completion_path.exists() else None,
                "completion_verified": completion_ok,
                "completion_observed_at": completion.get("observed_at_utc"),
                "planned_items": summary.get("planned_items"),
                "coverage": coverage,
                "successes": successes,
                "failures": [x for x in records if x.get("status") != "success"],
            })
    finished_successes: set[str] = set()
    for batch in summaries:
        if batch["finished_at"] or batch["completion_verified"]:
            finished_successes.update(batch["successes"])
    active_failures: list[dict[str, Any]] = []
    stale_failures: list[dict[str, Any]] = []
    batch_statuses: list[dict[str, Any]] = []
    unfinished_active: list[str] = []
    for batch in summaries:
        overlap = batch["coverage"] & planned_logicals
        if batch["finished_at"]:
            state = "finished"
        elif batch["completion_verified"]:
            state = "completed_verified"
        elif batch["termination"].get("status") == "stopped_superseded":
            # A separately recorded stop is terminal without inventing the
            # downloader's original finished_at.  The source summary remains
            # unchanged and the replacement plans are recorded in the sidecar.
            state = "stopped_superseded"
        elif not overlap:
            state = "stale_unrelated"
        elif overlap <= finished_successes:
            state = "superseded"
        else:
            state = "unfinished_active"
            unfinished_active.append(batch["summary_file"])
        for failure in batch["failures"]:
            item = {
                "summary_file": batch["summary_file"],
                "manifest_file": batch["manifest_file"],
                "original": failure.get("original"),
                "logical_url": canonical_url(str(failure.get("original", ""))),
                "failure_reason": failure.get("failure_reason") or failure.get("error"),
                "status": failure.get("status"),
            }
            if item["logical_url"] in planned_logicals and item["logical_url"] not in finished_successes and state in {"finished", "unfinished_active", "stopped_superseded"}:
                active_failures.append(item)
            else:
                stale_failures.append(item)
        batch_statuses.append({
            "summary_file": batch["summary_file"],
            "manifest_file": batch["manifest_file"],
            "finished_at": batch["finished_at"],
            "completion_file": batch["completion_file"],
            "completion_verified": batch["completion_verified"],
            "completion_observed_at": batch["completion_observed_at"],
                "termination_file": batch["termination_file"],
                "termination": batch["termination"],
            "status": state,
            "planned_items": batch["planned_items"],
            "planned_overlap_count": len(overlap),
            "success_count": len(batch["successes"]),
            "failure_count": len(batch["failures"]),
        })
    return {
        "batches": batch_statuses,
        "all_active_finished": not unfinished_active,
        "unfinished_active_batches": unfinished_active,
        "active_failures": active_failures,
        "stale_failures": stale_failures,
    }


def tree_size(root: Path) -> int:
    total = 0
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if not (Path(base) / d).is_symlink()]
        for name in files:
            p = Path(base) / name
            try:
                if not p.is_symlink():
                    total += p.stat().st_size
            except OSError:
                pass
    return total


def safe_segment(value: str, default: str = "_") -> str:
    value = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", "_", value)
    value = value.rstrip(" .") or default
    if value.casefold() in {"con", "prn", "aux", "nul"} or re.fullmatch(r"com[1-9]|lpt[1-9]", value.casefold()):
        value = "_" + value
    return value


def mirror_path(original: str) -> Path:
    # Canonicalisation removes default :80/:443 before constructing the
    # Windows-safe host directory.  The URL itself remains in url-map.json.
    canonical = canonical_url(original)
    parsed = urllib.parse.urlsplit(canonical)
    host = safe_segment(parsed.netloc.lower() or parsed.hostname or "host")
    segments = [safe_segment(urllib.parse.unquote(x), "_") for x in parsed.path.split("/") if x]
    if not segments:
        segments = ["__root__"]
    if parsed.path.endswith("/"):
        segments.append("__index__")
    if parsed.query:
        digest = hashlib.sha256(parsed.query.encode("utf-8")).hexdigest()[:16]
        stem = Path(segments[-1]).stem
        suffix = Path(segments[-1]).suffix
        segments[-1] = safe_segment(f"{stem}__query_{digest}{suffix}")
    return ROOT / "mirror" / "20080512" / host / Path(*segments)


def workspace_preflight(write_bytes: int, mirror_targets: list[tuple[Path, bytes]]) -> dict[str, Any]:
    existing = tree_size(ROOT)
    disk = shutil.disk_usage(ROOT)
    additional = sum(len(data) for path, data in mirror_targets if not path.exists()) + write_bytes
    return {
        "workspace_bytes_before_outputs": existing,
        "workspace_limit_bytes": WORKSPACE_LIMIT,
        "estimated_new_bytes": additional,
        "workspace_bytes_after_estimate": existing + additional,
        "workspace_budget_ok": existing + additional <= WORKSPACE_LIMIT,
        "disk_free_bytes": disk.free,
        "min_free_bytes": MIN_FREE,
        "write_reserve_bytes": WRITE_RESERVE,
        "free_space_ok": disk.free >= MIN_FREE + WRITE_RESERVE + additional,
    }


def export_preferred(preferred: dict[str, dict[str, Any]], output_index: dict[str, Any]) -> dict[str, Any]:
    targets: list[tuple[Path, bytes]] = []
    map_items: list[dict[str, Any]] = []
    collisions: list[dict[str, Any]] = []
    by_target: dict[Path, str] = {}
    by_target_casefold: dict[str, str] = {}
    mirror_root = (ROOT / "mirror" / "20080512").resolve()
    existing_casefold: dict[str, tuple[Path, str]] = {}
    if mirror_root.exists():
        for existing_path in mirror_root.rglob("*"):
            if not existing_path.is_file():
                continue
            try:
                key = existing_path.resolve().relative_to(mirror_root).as_posix().casefold()
                existing_casefold[key] = (existing_path, sha256(existing_path.read_bytes()))
            except (OSError, ValueError):
                continue
    for logical, candidate in sorted(preferred.items()):
        body = candidate.get("body_bytes")
        if body is None:
            continue
        original = str(candidate.get("original") or logical)
        target = mirror_path(original)
        try:
            target.resolve().relative_to(mirror_root)
        except ValueError:
            collisions.append({"target": str(target), "reason": "mirror_path_escape", "original": original})
            continue
        target_key = target.resolve().relative_to(mirror_root).as_posix().casefold()
        target_sha = str(candidate.get("computed_sha256"))
        existing_match = existing_casefold.get(target_key)
        if existing_match is not None and existing_match[1] != target_sha:
            collisions.append({"target": target_key, "existing_path": rel(existing_match[0]), "previous_sha256": existing_match[1], "new_sha256": target_sha, "original": original, "reason": "windows_casefold_collision"})
        prior = by_target.get(target)
        if prior is not None and prior != target_sha:
            collisions.append({"target": rel(target), "previous_sha256": prior, "new_sha256": target_sha, "original": original})
        prior_casefold = by_target_casefold.get(target_key)
        if prior_casefold is not None and prior_casefold != target_sha:
            collisions.append({"target": target_key, "previous_sha256": prior_casefold, "new_sha256": target_sha, "original": original, "reason": "windows_casefold_collision"})
        by_target[target] = target_sha
        by_target_casefold[target_key] = target_sha
        targets.append((target, body))
        map_items.append({
            "logical_url": logical,
            "original": original,
            "local_path": rel(target),
            "mime": candidate.get("body", {}).get("declared_mime") or candidate.get("declared_mime"),
            "mime_family": candidate.get("body", {}).get("mime_family"),
            "actual_timestamp": candidate.get("actual_timestamp"),
            "requested_timestamp": candidate.get("requested_timestamp"),
            "indexed_capture_timestamp": candidate.get("indexed_capture_timestamp"),
            "entity_observed_capture_timestamp": candidate.get("actual_timestamp"),
            "temporal_reference_timestamp": candidate.get("temporal_reference_timestamp"),
            "temporal_class": candidate.get("temporal_class"),
            "acquisition": candidate.get("acquisition"),
            "cdx_verified_payload_reuse": candidate.get("cdx_verified_payload_reuse"),
            "source_catalog": candidate.get("source_catalog"),
            "cdx_raw_source": candidate.get("cdx_raw_source"),
            "source_manifest": candidate.get("source_manifest"),
            "manifest_line": candidate.get("manifest_line"),
            "source_file": candidate.get("source_file"),
            "zip_file": candidate.get("zip_file"),
            "zip_entry": candidate.get("zip_entry"),
            "sha256": candidate.get("computed_sha256"),
            "content_length": len(body),
            "role": candidate.get("plan_meta", {}).get("role") or candidate.get("role"),
            "kind": candidate.get("plan_meta", {}).get("kind") or candidate.get("kind"),
            "source_role": candidate.get("role"),
            "cdx_digest": candidate.get("expected_cdx_digest"),
            "cdx_digest_matches": candidate.get("cdx_digest_matches"),
        })
    if collisions:
        return {"status": "stopped_collision", "collisions": collisions, "written": 0, "preflight": workspace_preflight(0, [])}
    url_map_bytes = json.dumps({"anchor": ANCHOR, "unmodified_entities": True, "offline_rendering_verified": False, "note": "Preferred historical entities only. HTML serialized with .xml filenames needs its recorded text/html MIME during reconstruction. Later supplements and error entities remain in the source index and ZIPs, outside this tree.", "files": map_items}, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    preflight = workspace_preflight(len(url_map_bytes), targets)
    if not preflight["workspace_budget_ok"] or not preflight["free_space_ok"]:
        return {"status": "stopped_budget", "written": 0, "preflight": preflight, "planned_files": len(targets)}
    mirror_root = ROOT / "mirror" / "20080512"
    mirror_root.mkdir(parents=True, exist_ok=True)
    written = 0
    skipped_same = 0
    for target, body in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if target.read_bytes() != body:
                return {"status": "stopped_existing_different_bytes", "written": written, "target": rel(target), "preflight": preflight}
            skipped_same += 1
            continue
        target.write_bytes(body)
        written += 1
    url_map = mirror_root / "url-map.json"
    if url_map.exists() and url_map.read_bytes() != url_map_bytes:
        return {"status": "stopped_existing_url_map_conflict", "written": written, "preflight": preflight}
    if not url_map.exists():
        url_map.write_bytes(url_map_bytes)
        written += 1
    return {"status": "exported", "written": written, "skipped_same": skipped_same, "planned_files": len(targets), "preflight": preflight, "url_map": rel(url_map)}


def build_report(do_export: bool = False) -> tuple[dict[str, Any], dict[str, Any], str]:
    meta_by_logical, core_items, dep_items, dep_info = load_plan_meta()
    data_by_location, zip_reports, zip_errors = scan_zips()
    manifests, manifest_failures = manifest_candidates(data_by_location)
    catalogs = discover_catalog_records(data_by_location)
    candidates = build_candidates(meta_by_logical, data_by_location, manifests, catalogs)
    logical_records, preferred_runtime = choose_candidates(meta_by_logical, candidates, core_items, dep_items)
    logical_map = {x["logical_url"]: x for x in logical_records}
    plan_records = public_plan_records(core_items, dep_items, dep_info.get("deferred", []), logical_map)
    # Attach source-role and selected-capture information to future catalog
    # records without making catalog presence a completion signal.
    catalog_paths = sorted({x.get("source_catalog") for x in catalogs if x.get("source_catalog")})
    core_states = [logical_map.get(canonical_url(str(x.get("original", ""))), {}).get("state") for x in core_items]
    dep_records = [logical_map.get(canonical_url(str(x.get("original", ""))), {}) for x in dep_items]
    dep_states = [x.get("state") for x in dep_records]
    active_dep_records = [x for x in dep_records if x.get("activity_scope", "active") == "active"]
    active_dep_states = [x.get("state") for x in active_dep_records]
    inactive_dep_records = [x for x in dep_records if x.get("activity_scope") == "inactive"]
    core_valid_html = 0
    for item in core_items:
        rec = logical_map.get(canonical_url(str(item.get("original", ""))), {})
        selected = rec.get("selected_capture") or {}
        body = selected.get("body") or {}
        if rec.get("state") == "preferred" and body.get("status") == "valid_html" and (body.get("title_match") or item.get("original", "").endswith("index.xml")):
            core_valid_html += 1
    by_state = Counter(x.get("state") for x in logical_records)
    active_by_state = Counter(x.get("state") for x in active_dep_records)
    by_role = Counter(str(x.get("role") or "unknown") for x in logical_records)
    graph_summary = dependency_edges()
    planned_logicals = {
        canonical_url(str(x.get("original", "")))
        for x in (core_items + dep_items)
        if x.get("original")
    }
    batch_summary = download_batches(planned_logicals)
    batch_status_by_manifest = {
        str(x.get("manifest_file")): x.get("status")
        for x in batch_summary.get("batches", [])
        if x.get("manifest_file")
    }
    manifest_failures_report: list[dict[str, Any]] = []
    active_manifest_failures: list[dict[str, Any]] = []
    stale_manifest_failures: list[dict[str, Any]] = []
    saved_success_urls = {canonical_url(str(x.get("original", ""))) for x in manifests if x.get("original")}
    for failure in manifest_failures:
        annotated = dict(failure)
        batch_state = batch_status_by_manifest.get(str(failure.get("source_manifest")), "unknown")
        annotated["batch_status"] = batch_state
        failed_logical = canonical_url(str(failure.get("original", "")))
        annotated["superseded_by_success"] = failed_logical in saved_success_urls
        annotated["stale_evidence"] = failed_logical not in planned_logicals or annotated["superseded_by_success"] or batch_state in {"superseded", "stale_unrelated"}
        manifest_failures_report.append(annotated)
        if annotated["stale_evidence"]:
            stale_manifest_failures.append(annotated)
        else:
            active_manifest_failures.append(annotated)
    reference_errors = graph_summary.get("reference_integrity_errors", [])
    core_complete = core_valid_html == len(core_items) and all(x == "preferred" for x in core_states)
    dependency_complete = bool(active_dep_records) and all(x == "preferred" for x in active_dep_states)
    integrity_complete = not zip_errors and not reference_errors
    batches_complete = bool(batch_summary.get("all_active_finished"))
    # A finished batch does not prove that a subsequently expanded plan was
    # attempted.  Keep unattempted additions in progress until acquisition or
    # explicit bounded recovery evidence accounts for them.
    attempted = {canonical_url(str(x.get("original", ""))) for x in manifests if x.get("original")}
    attempted.update(x["logical_url"] for x in candidates if x.get("body_available"))
    recovery = load_json(ROOT / "research/acquisition-2008/recovery/recovery-catalog.json", {}) or {}
    controls = recovery.get("corrected_query_summaries", [])
    recovery_control_ok = any(x.get("status") == 200 and not x.get("capped") and (x.get("image_rows") or 0) > 0 for x in controls)
    investigated = {
        canonical_url(str(x.get("logical_url", "")))
        for x in recovery.get("entities", [])
        if recovery_control_ok and x.get("logical_url") and x.get("status") in {"no_corrected_prefix_candidate", "non_image_cdx_only"}
    }
    unattempted = sorted(planned_logicals - attempted - investigated)
    coverage = {"planned_urls": len(planned_logicals), "attempted_or_saved_urls": len(planned_logicals & attempted), "bounded_recovery_without_body_urls": sorted((planned_logicals & investigated) - attempted), "not_yet_attempted_urls": unattempted}
    overall_complete = core_complete and dependency_complete and integrity_complete and batches_complete and not unattempted
    if not batches_complete or unattempted:
        acquisition_status = "in_progress"
    elif not core_complete or not integrity_complete:
        acquisition_status = "validation_incomplete"
    elif overall_complete:
        acquisition_status = "complete"
    else:
        acquisition_status = "completed_with_archive_gaps"
    index: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "mode": "offline" if not do_export else "offline_with_export",
        "network_performed": False,
        "anchor_timestamp": ANCHOR,
        "sources": {
            "core_full_plan": rel(ROOT / "research/acquisition-2008/core/full-plan.json"),
            "core_source_mapping": rel(ROOT / "research/acquisition-2008/core/source-mapping.json"),
            "dependency_plan": rel(ROOT / "research/acquisition-2008/dependencies/dependency-plan.json"),
            "dependency_graph": rel(ROOT / "research/acquisition-2008/dependencies/dependency-graph.json"),
            "manifests": sorted({x.get("source_manifest") for x in manifests if x.get("source_manifest")}),
            "catalogs": catalog_paths,
        },
        "completion": {
            "overall": "complete" if overall_complete else "partial",
            "acquisition_status": acquisition_status,
            "core_planned": len(core_items),
            "core_preferred": sum(x == "preferred" for x in core_states),
            "core_valid_html": core_valid_html,
            "core_all_valid_html": core_complete,
            "dependency_plan_items": len(dep_items),
            "dependency_preferred": sum(x == "preferred" for x in active_dep_states),
            "active_dependency_plan_items": len(active_dep_records),
            "active_dependency_state_counts": dict(active_by_state),
            "inactive_dependency_items": len(inactive_dep_records),
            "logical_urls": len(logical_records),
            "state_counts": dict(by_state),
            "role_counts": dict(by_role),
            "unfinished_dependency_manifest_failures": len(active_manifest_failures),
            "stale_dependency_manifest_failures": len(stale_manifest_failures),
            "download_batches_finished": batches_complete,
            "zip_integrity_ok": not zip_errors,
            "reference_integrity_ok": not reference_errors,
            "catalogs_seen": len(catalog_paths),
            "not_yet_attempted_urls": len(unattempted),
        },
        "zip_validation": {"volumes": zip_reports, "errors": zip_errors},
        "manifest_failures": manifest_failures_report,
        "download_batches": batch_summary,
        "acquisition_coverage": coverage,
        "dependency_summary": {**graph_summary, "plan_counts": dep_info.get("dependency_counts", {}), "plan_limits": dep_info.get("dependency_limits", {})},
        "logical_urls": logical_records,
        "plan_records": plan_records,
    }
    summary: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": index["generated_at"],
        "anchor_timestamp": ANCHOR,
        "network_performed": False,
        "status": index["completion"],
        "zip_crc_failures": zip_errors,
        "core": {"planned": len(core_items), "preferred": sum(x == "preferred" for x in core_states), "valid_html": core_valid_html, "all_valid_html": core_complete},
        "dependencies": {"planned": len(dep_items), "preferred": sum(x == "preferred" for x in active_dep_states), "active_planned": len(active_dep_records), "inactive_planned": len(inactive_dep_records), "manifest_failures": len(active_manifest_failures), "stale_manifest_failures": len(stale_manifest_failures), "states": dict(Counter(active_dep_states))},
        "acquisition_status": acquisition_status,
        "acquisition_coverage": coverage,
        "download_batches": batch_summary,
        "reference_integrity_errors": reference_errors,
        "resource_classes": dict(by_role),
        "state_counts": dict(by_state),
        "catalogs": catalog_paths,
    }
    export_result = None
    if do_export:
        export_result = export_preferred(preferred_runtime, index)
        index["export"] = export_result
        summary["export"] = export_result
    out_dir = ROOT / "research" / "acquisition-2008" / "integration"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    validation = render_validation(index, summary)
    (out_dir / "validation.md").write_text(validation, encoding="utf-8")
    return index, summary, validation


def render_validation(index: dict[str, Any], summary: dict[str, Any]) -> str:
    status = index["completion"]
    lines = [
        "# 2008 preservation integration validation",
        "",
        f"Generated `{index['generated_at']}`. This run was offline (`network_performed=false`) at anchor `{ANCHOR}`.",
        "",
        "## Completion",
        "",
        f"- Overall: **{status['overall']}**.",
        f"- Acquisition status: **{status['acquisition_status']}**; active download batches finished: `{status['download_batches_finished']}`.",
        f"- Core pages: {status['core_preferred']}/{status['core_planned']} preferred; valid HTML/title bodies: {status['core_valid_html']}/{status['core_planned']}.",
        f"- Dependency plan records: {status['dependency_plan_items']} ({status['active_dependency_plan_items']} active, {status['inactive_dependency_items']} inactive); preferred active logical URLs: {status['dependency_preferred']}; unfinished manifest failures: {status['unfinished_dependency_manifest_failures']}; stale evidence failures: {status['stale_dependency_manifest_failures']}.",
        f"- Logical URL states: `{json.dumps(status['state_counts'], ensure_ascii=False, sort_keys=True)}`.",
        "",
        "A null `finished_at` blocks acquisition unless superseded by finished work, an explicit `termination.json` sidecar, or a `completed_verified` completion.json bound to the exact manifest, summary and ZIP hashes. The custom IE preservation summary is retained without inventing a downloader finish time. Historical failed requests later followed by saved responses remain as superseded evidence. Newly added plan URLs without acquisition or bounded recovery evidence also keep acquisition in progress.",
        f"Current plan URLs without acquisition/recovery evidence: `{len(summary['acquisition_coverage']['not_yet_attempted_urls'])}`.",
        "",
        "## Integrity checks",
        "",
        f"- ZIP volumes scanned: {len(index['zip_validation']['volumes'])}; CRC/SHA named-entry errors: {len(index['zip_validation']['errors'])}.",
        "- Each available selected body records manifest SHA-256/length checks and, when a plan digest exists, SHA-1/Base32 CDX digest comparison. CDX `length` is retained as metadata; replay body length can differ from CDX length while the CDX digest matches the saved body.",
        "- HTML/XML MIME family and body sniffing are retained separately. Core `.xml` pages are accepted only when their body is HTML-like and their title matches the expected plan title (with the known homepage `The Warcraft Encyclopedia` alias). True XML/XSL dependencies use strict ElementTree parsing and report `valid_xml`/`valid_xsl`.",
        "- Images require the extension-appropriate magic; CSS/JS bodies are rejected when they are HTML error/modern-guide pages. A historical `index.html` meta-refresh to the encyclopedia index is recorded as `valid_redirect_document` and kept outside the active dependency completeness count.",
        "",
        "## State meanings",
        "",
        "- `preferred`: valid body with a capture at or before the 2008 anchor, or an explicitly recorded same-day static capture.",
        "- `supplement-only`: valid body only after the anchor; it is retained as provenance and never preferred automatically.",
        "- `invalid`: body exists but is an origin 404, modern guide, redirect, non-image, or integrity failure.",
        "- `missing`: no usable body is present yet; manifest failures and their reasons remain in `index.json`.",
        "",
        "## Dependency closure",
        "",
        f"The saved graph contributes {index['dependency_summary']['node_count']} nodes, {index['dependency_summary']['edge_count']} edges and {index['dependency_summary']['referenced_target_count']} referenced targets. It retains {index['dependency_summary']['unresolved_reference_count']} dynamic unresolved expressions and {len(index['dependency_summary']['reference_integrity_errors'])} non-dynamic reference errors. Plan counts are `{json.dumps(index['dependency_summary']['plan_counts'], ensure_ascii=False, sort_keys=True)}`.",
        "",
        "## Export",
        "",
    ]
    if "export" in summary:
        lines.append(f"Export result: `{json.dumps(summary['export'], ensure_ascii=False, sort_keys=True)}`")
    else:
        lines.append("No export was requested. Use `python tools/build_2008_preservation.py --export` after reviewing the index; the exporter preflights workspace size/free space and refuses different existing bytes.")
    lines += [
        "",
        "## Reproduction",
        "",
        "```powershell",
        "python tools/build_2008_preservation.py",
        "python tools/build_2008_preservation.py --export",
        "```",
        "",
        "The first command is the safe report-only run. Both commands are local-only and do not make network requests.",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build offline 2008 preservation index; optional safe mirror export")
    parser.add_argument("--export", action="store_true", help="preflight and export preferred valid bodies to mirror/20080512")
    args = parser.parse_args(argv)
    try:
        index, summary, _ = build_report(args.export)
    except Exception as exc:  # provide a concise CLI failure without hiding tracebacks in debugging
        print(f"build_2008_preservation: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"index": "research/acquisition-2008/integration/index.json", "summary": "research/acquisition-2008/integration/summary.json", "validation": "research/acquisition-2008/integration/validation.md", "overall": summary["status"]["overall"], "core": summary["core"], "dependencies": summary["dependencies"], "export": summary.get("export")}, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
