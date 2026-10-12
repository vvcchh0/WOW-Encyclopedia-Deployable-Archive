"""Build a bounded, resumable first-ring inventory for the archived WoW site.

The default command is offline.  It reads the already-preserved 52 encyclopedia
pages, topic-list.js, and locally saved navigation sources, then writes a
finite frontier and a Wayback plan template.  ``--query-cdx`` (with explicit
``--allow-network``) performs bounded exact-CDX queries and preserves each raw
response; ``--fetch`` delegates a selected plan to the existing
``tools/wayback_backup.py`` contract.  This module never executes downloaded
JavaScript.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
from html.parser import HTMLParser
import hashlib
import json
import posixpath
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import zlib
import xml.etree.ElementTree as ET
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "research" / "site-expansion-2008"
RECOVERY_DEFAULT_OUT = ROOT / "research" / "site-recovery-2008"
ANCHOR = "20080512210044"
RECOVERY_QUERY_TO = "20081231235959"
# Prefix CDX requests need an explicit lower bound on some Archive shards;
# without it the same request can return the 102-byte null-row placeholder.
# Keep the bound finite while retaining pre-2008 rows as historical context.
RECOVERY_QUERY_FROM = "2006"
MAX_OBJECT_BYTES = 16 * 1024 * 1024
MAX_WORKSPACE_BYTES = 14_000_000_000
MIN_FREE_BYTES = 10 * 1024**3
RESERVE_BYTES = 256 * 1024**2
MAX_ARCHIVE_FLOWS = 2
MAX_REQUESTS = 40
MAX_CDX_BYTES = 4 * 1024 * 1024
RECOVERY_PREFIXES = (
    ("info", "http://www.worldofwarcraft.com/info/"),
    ("community", "http://www.worldofwarcraft.com/community/"),
    ("downloads", "http://www.worldofwarcraft.com/downloads/"),
    ("news", "http://www.worldofwarcraft.com/news/"),
    ("misc", "http://www.worldofwarcraft.com/misc/"),
    ("pvp", "http://www.worldofwarcraft.com/pvp/"),
    ("burningcrusade", "http://www.worldofwarcraft.com/burningcrusade/"),
    ("wrath", "http://www.worldofwarcraft.com/wrath/"),
    ("features", "http://www.worldofwarcraft.com/features/"),
    ("wareffort", "http://www.worldofwarcraft.com/wareffort/"),
    ("calendar", "http://www.worldofwarcraft.com/calendar/"),
    ("contests", "http://www.worldofwarcraft.com/contests/"),
    ("gadgetzantimes", "http://www.worldofwarcraft.com/gadgetzantimes/"),
)
RECOVERY_EXACT_ALIASES = (
    ("home", "http://www.worldofwarcraft.com/"),
    ("index-xml", "http://www.worldofwarcraft.com/index.xml"),
    ("info-index-xml", "http://www.worldofwarcraft.com/info/index.xml"),
)
# These two historical entry documents are not sidebar nodes (the menu points
# the root alias at ``/``), but they are needed to recover the public homepage
# data route and to record the separate /info/index.xml lookup as missing when
# the Archive has no row.  They stay finite, are fetched as page entities, and
# are never treated as static assets.
RECOVERY_ALIAS_PAGES = (
    {
        "original": "http://www.worldofwarcraft.com/index.xml",
        "role": "site_recovery_home_alias",
        "kind": "page",
        "labels": ["WoW Main", "Homepage XML alias"],
        "categories": ["Home"],
        "parents": [{"url": "research/site-recovery-2008/.navtree-main.js", "label": "WoW Main", "line": 124}],
        "route_aliases": ["/"],
    },
    {
        "original": "http://www.worldofwarcraft.com/info/index.xml",
        "role": "site_recovery_guide_alias",
        "kind": "page",
        "labels": ["Guide XML alias"],
        "categories": ["Guide"],
        "parents": [{"url": "research/site-recovery-2008/.navtree-main.js", "label": "Guide", "line": 161}],
        "route_aliases": ["/info", "/info/"],
    },
)
RECOVERY_BATCH_ENTITIES = 100
PRIMARY_SEED_PATHS = {
    "/",
    "/index.html",
    "/community",
    "/community/comics.html",
    "/community/stories",
    "/downloads",
    "/downloads/movies.html",
    "/info/archivednews.html",
    "/info/basics",
    "/info/story/index.html",
    "/news/wow-news-06-2006.html",
    "/pvp",
    "/pvp/battlegrounds",
}
# The exact early captures are useful comparison evidence, but they are not
# part of the active 2008-near first-ring export.  Keep this policy explicit
# so a later local map rebuild cannot silently re-promote them.
COMPARISON_ONLY_URLS = {
    "http://www.worldofwarcraft.com/",
    "http://www.worldofwarcraft.com/info/basics",
}
DEFERRED_BULK_PREFIXES = (
    "/community/comics/",
    "/community/machinima/",
    "/community/tournaments/",
)

MAIN_HOSTS = {"worldofwarcraft.com", "www.worldofwarcraft.com"}
OFFICIAL_RELATED_HOSTS = {
    "wow-europe.com", "www.wow-europe.com", "blizzard.com", "www.blizzard.com",
    "warcraftchina.com", "wowtaiwan.com.tw", "worldofwarcraft.co.kr",
}
SOCIAL_HOST_MARKERS = ("facebook.", "twitter.", "youtube.", "flickr.", "forums.")
ARMORY_MARKERS = ("armory", "battle.net", "account", "login", "store", "support")
LARGE_EXTENSIONS = {
    ".7z", ".avi", ".dmg", ".exe", ".flv", ".gz", ".iso", ".mov", ".mp4",
    ".msi", ".pkg", ".rar", ".tar", ".torrent", ".wmv", ".zip",
}
STATIC_EXTENSIONS = {
    ".bmp", ".css", ".gif", ".htc", ".ico", ".jpeg", ".jpg", ".js", ".json",
    ".png", ".svg", ".swf", ".ttf", ".webp", ".woff", ".xml", ".xsl", ".xslt",
}
PAGE_EXTENSIONS = {"", ".asp", ".aspx", ".cfm", ".html", ".htm", ".php", ".xml"}
URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.I)
ROOT_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_])/(?:shared|new-hp|info|images|v2|community|support|account|download|wow)"
    r"[A-Za-z0-9_./?&=%:+#@~,-]*",
    re.I,
)
QUOTED_RE = re.compile(r"[\"']([^\"'\r\n]{1,1024})[\"']")
TOPIC_RE = re.compile(
    r"new\s+topicElement\(\s*[\"']([^\"']+)[\"']\s*,\s*[\"']([^\"']+\.xml)[\"']",
    re.I,
)
URL_FUNCTION_RE = re.compile(r"url\(\s*[\"']?([^\"')\s]+)", re.I)


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def timestamp_digits(value: Any) -> str | None:
    """Return a Wayback-style 14-digit timestamp when one is present."""
    match = re.search(r"(20\d{2}\d{10})", str(value or ""))
    return match.group(1) if match else None


def capture_time_bucket(value: Any) -> str:
    """Classify an existing timestamp without treating a request anchor as fact."""
    timestamp = timestamp_digits(value)
    if not timestamp:
        return "unknown"
    if timestamp <= ANCHOR:
        return "at_or_before_anchor"
    if timestamp.startswith(ANCHOR[:8]):
        return "same_day_after_anchor"
    if timestamp[:4] == ANCHOR[:4]:
        return "same_year_supplement"
    return "outside_2008_supplement"


def cdx_identity(value: str) -> tuple[str, str, str] | None:
    """Compare CDX URL aliases while keeping host/path/query exact."""
    logical = canonical_url(value)
    if not logical:
        return None
    parsed = urllib.parse.urlsplit(logical)
    host = parsed.hostname.casefold().rstrip(".") if parsed.hostname else ""
    if parsed.port is not None and not (
        (parsed.scheme == "http" and parsed.port == 80)
        or (parsed.scheme == "https" and parsed.port == 443)
    ):
        host = f"{host}:{parsed.port}"
    return host, parsed.path or "/", parsed.query


def _cdx_record_from_mapping(value: Any, source: str, row_number: int) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    url = value.get("original") or value.get("url") or value.get("original_url")
    timestamp = value.get("timestamp") or value.get("capture_timestamp")
    status = value.get("statuscode") or value.get("status") or value.get("http_status")
    if not isinstance(url, str) or not timestamp:
        return None
    timestamp = str(timestamp)
    if not re.fullmatch(r"\d{14}", timestamp):
        return None
    record = {
        "timestamp": timestamp,
        "original": url,
        "statuscode": str(status or ""),
        "digest": value.get("digest"),
        "length": value.get("length") or value.get("content_length"),
        "mimetype": value.get("mimetype") or value.get("mime") or value.get("declared_mime"),
        "source_file": source,
        "source_row": row_number,
    }
    record["identity"] = cdx_identity(url)
    return record


def _cdx_record_from_row(
    row: list[Any] | tuple[Any, ...],
    header: list[str] | None,
    source: str,
    row_number: int,
) -> dict[str, Any] | None:
    values = [str(item) if item is not None else "" for item in row]
    if header:
        mapping = {str(key).casefold(): values[index] for index, key in enumerate(header) if index < len(values)}
        return _cdx_record_from_mapping(mapping, source, row_number)
    timestamp_index = next((index for index, value in enumerate(values) if re.fullmatch(r"\d{14}", value)), None)
    if timestamp_index is None:
        return None
    url_index = next((index for index, value in enumerate(values) if value.startswith(("http://", "https://"))), None)
    if url_index is None:
        return None
    status_index = next((index for index, value in enumerate(values) if re.fullmatch(r"\d{3}", value)), None)
    mime_index = next((index for index, value in enumerate(values) if "/" in value and " " not in value), None)
    digest_index = next(
        (index for index, value in enumerate(values) if index not in {timestamp_index, url_index} and re.fullmatch(r"[A-Za-z0-9+/_=-]{16,}", value)),
        None,
    )
    length_index = next(
        (index for index, value in enumerate(values) if value.isdigit() and index not in {timestamp_index, status_index}),
        None,
    )
    return _cdx_record_from_mapping(
        {
            "timestamp": values[timestamp_index],
            "original": values[url_index],
            "statuscode": values[status_index] if status_index is not None else "",
            "digest": values[digest_index] if digest_index is not None else None,
            "length": values[length_index] if length_index is not None else None,
            "mimetype": values[mime_index] if mime_index is not None else None,
        },
        source,
        row_number,
    )


def _cdx_payload_records(payload: Any, source: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    def visit(value: Any, row_base: int = 0) -> None:
        if isinstance(value, dict):
            direct = _cdx_record_from_mapping(value, source, row_base)
            if direct:
                records.append(direct)
                return
            for key in ("rows", "results", "records", "data", "captures"):
                if key in value:
                    visit(value[key], row_base)
            return
        if not isinstance(value, list):
            return
        if value and all(isinstance(item, (str, int, float)) for item in value):
            row = _cdx_record_from_row(value, None, source, row_base)
            if row:
                records.append(row)
            return
        header: list[str] | None = None
        start = 0
        if value and isinstance(value[0], list) and all(isinstance(item, str) for item in value[0]):
            first = [str(item).casefold() for item in value[0]]
            if "timestamp" in first and ("original" in first or "url" in first):
                header = [str(item) for item in value[0]]
                start = 1
        for index, item in enumerate(value[start:], start=start + row_base):
            if isinstance(item, dict):
                record = _cdx_record_from_mapping(item, source, index)
            elif isinstance(item, list):
                record = _cdx_record_from_row(item, header, source, index)
            else:
                record = None
            if record:
                records.append(record)

    visit(payload)
    return records


def load_cdx_records(paths: Iterable[Path]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Read saved CDX responses only; this function never performs a request."""
    records: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for path in paths:
        source = rel(path)
        try:
            size = path.stat().st_size
            if size > MAX_CDX_BYTES:
                errors.append({"source_file": source, "error": "cdx_file_over_limit", "bytes": size})
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            errors.append({"source_file": source, "error": f"read_error:{type(exc).__name__}:{exc}"})
            continue
        parsed = False
        try:
            payload = json.loads(text)
            records.extend(_cdx_payload_records(payload, source))
            parsed = True
        except (ValueError, TypeError):
            pass
        if not parsed:
            header: list[str] | None = None
            for line_number, line in enumerate(text.splitlines(), start=1):
                if not line.strip() or line.startswith("#"):
                    continue
                parts = line.split()
                if parts and all(token.casefold() in {"timestamp", "original", "url", "statuscode", "status", "digest", "length", "mimetype", "mime", "urlkey", "offset", "filename"} for token in parts):
                    header = parts
                    continue
                record = _cdx_record_from_row(parts, header, source, line_number)
                if record:
                    records.append(record)
    return records, errors


def canonical_url(value: str, base: str | None = None) -> str | None:
    raw = value.strip()
    if not raw or raw.startswith(("#", "javascript:", "mailto:", "data:", "vbscript:")):
        return None
    if base:
        raw = urllib.parse.urljoin(base, raw)
    try:
        parsed = urllib.parse.urlsplit(raw)
    except ValueError:
        return None
    if parsed.scheme.casefold() not in {"http", "https"} or not parsed.hostname:
        return None
    scheme = parsed.scheme.casefold()
    host = parsed.hostname.casefold().rstrip(".")
    port = parsed.port
    if port is not None and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        host = f"{host}:{port}"
    path = parsed.path or "/"
    # Keep query semantics but normalize repeated slashes and dot segments.
    path = posixpath.normpath(path)
    if parsed.path.startswith("/") and not path.startswith("/"):
        path = "/" + path
    if path == ".":
        path = "/"
    return urllib.parse.urlunsplit((scheme, host, path, parsed.query, ""))


def display_url(value: str) -> str:
    return value


def official_main(url: str) -> bool:
    host = urllib.parse.urlsplit(url).hostname or ""
    return host.casefold().rstrip(".") in MAIN_HOSTS


def classify_url(url: str) -> dict[str, Any]:
    parsed = urllib.parse.urlsplit(url)
    host = (parsed.hostname or "").casefold().rstrip(".")
    path = parsed.path.casefold()
    suffix = Path(parsed.path).suffix.casefold()
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    if host in MAIN_HOSTS:
        host_scope = "primary_official"
    elif host in OFFICIAL_RELATED_HOSTS or host.endswith(".worldofwarcraft.com"):
        host_scope = "official_related"
    elif any(marker in host for marker in SOCIAL_HOST_MARKERS):
        host_scope = "social_or_forum"
    else:
        host_scope = "external"
    template_value = f"{parsed.path}?{parsed.query}"
    has_template_placeholder = bool(
        re.search(r"\{[^}]+\}|\$\{?[_A-Za-z][_A-Za-z0-9]*\}?", template_value)
    )
    if has_template_placeholder:
        category, action = "dynamic_template", "review"
    elif host_scope == "social_or_forum":
        category, action = "social_external", "exclude"
    elif any(marker in host for marker in ARMORY_MARKERS) or any(
        token in path for token in ("/login", "/account", "/billing", "/checkout", "/payment", "/armory")
    ):
        category, action = "dynamic_account", "exclude"
    elif suffix in LARGE_EXTENSIONS:
        category, action = "large_media_or_download", "exclude"
    elif host_scope == "external":
        category, action = "external_unknown", "review"
    elif host_scope == "official_related":
        category, action = "official_related_domain", "review"
    elif "/info/encyclopedia/" in path and suffix in {".xml", ".xsl", ".xslt"}:
        category, action = "encyclopedia_page_or_transform", "candidate"
    elif suffix in STATIC_EXTENSIONS:
        category, action = "static_resource", "candidate"
    elif suffix in PAGE_EXTENSIONS or not suffix:
        category, action = "site_page", "candidate"
    else:
        category, action = "unknown_internal", "review"
    if query and action == "candidate":
        category, action = "parameterized_internal", "review"
    return {
        "host_scope": host_scope,
        "category": category,
        "action": action,
        "suffix": suffix,
        "query_keys": sorted({key.casefold() for key, _ in query}),
    }


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.references: list[tuple[str, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if value is None:
                continue
            lname = name.casefold()
            if lname in {"href", "src", "action", "data", "poster", "cite", "longdesc"}:
                self.references.append((value, f"html-{lname}", tag))
            elif lname == "style":
                for match in URL_FUNCTION_RE.finditer(value):
                    self.references.append((match.group(1), "css-url-inline", tag))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def extract_references(source_url: str, body: bytes, source_kind: str) -> list[dict[str, Any]]:
    if source_kind == "binary":
        return []
    text = body.decode("utf-8", errors="replace")
    found: list[tuple[str, str, str]] = []
    if source_kind == "html":
        parser = ReferenceParser()
        try:
            parser.feed(text)
            found.extend(parser.references)
        except Exception:
            pass
    for match in URL_FUNCTION_RE.finditer(text):
        found.append((match.group(1), "css-url", "url()"))
    for match in URL_RE.finditer(text):
        found.append((match.group(0).rstrip("),.;'\""), "absolute-literal", "text"))
    for match in ROOT_PATH_RE.finditer(text):
        found.append((match.group(0).rstrip("),.;'\""), "root-literal", "text"))
    if source_kind in {"js", "xsl", "css"}:
        for match in QUOTED_RE.finditer(text):
            value = match.group(1).strip()
            if value.startswith(("/", "http://", "https://")):
                found.append((value, "static-literal", "quoted"))
    if source_kind == "topic-list":
        for match in TOPIC_RE.finditer(text):
            found.append((f"/info/encyclopedia/{match.group(2)}", "topic-list-entry", match.group(1)))
    dedup: dict[tuple[str, str], dict[str, Any]] = {}
    for raw, ref_type, context in found:
        raw = raw.strip()
        if raw.startswith(("#", "javascript:", "mailto:", "data:", "vbscript:")):
            continue
        if source_kind == "xsl" and ref_type == "css-url" and not raw.startswith(("/", "http://", "https://")):
            # XSL is a transform source; relative CSS URLs can be emitted into
            # the rendered page and must not be resolved against layout.xsl.
            continue
        target = canonical_url(raw, source_url)
        if not target:
            continue
        key = (target, ref_type)
        if key not in dedup:
            dedup[key] = {
                "url": target,
                "raw": raw,
                "ref_type": ref_type,
                "context": context[:160],
            }
    return list(dedup.values())


def load_integration_core() -> list[dict[str, Any]]:
    path = ROOT / "research/acquisition-2008/integration/index.json"
    data = load_json(path)
    return [item for item in data.get("logical_urls", []) if "core" in item.get("plan_scopes", [])]


def read_selected_capture(item: dict[str, Any]) -> tuple[bytes | None, dict[str, Any]]:
    capture = item.get("selected_capture") or {}
    source_type = capture.get("source_type")
    if source_type == "direct_file" and capture.get("source_file"):
        path = ROOT / str(capture["source_file"]).replace("\\", "/")
        if path.is_file():
            body = path.read_bytes()
            return body, {
                "source_type": source_type,
                "source_file": rel(path),
                "sha256": sha256(body),
                "bytes": len(body),
                "actual_timestamp": capture.get("actual_timestamp"),
                "actual_url": capture.get("actual_url"),
            }
    zip_file = capture.get("zip_file")
    zip_entry = capture.get("zip_entry")
    if zip_file and zip_entry:
        path = ROOT / str(zip_file).replace("\\", "/")
        try:
            with zipfile.ZipFile(path, "r") as archive:
                body = archive.read(str(zip_entry))
            return body, {
                "source_type": source_type or "manifest_zip",
                "zip_file": rel(path),
                "zip_entry": zip_entry,
                "sha256": sha256(body),
                "bytes": len(body),
                "actual_timestamp": capture.get("actual_timestamp"),
                "actual_url": capture.get("actual_url"),
            }
        except (OSError, KeyError, zipfile.BadZipFile) as exc:
            return None, {"source_type": source_type, "error": f"{type(exc).__name__}:{exc}"}
    return None, {"source_type": source_type, "error": "selected_capture_body_unavailable"}


def load_nav_sources() -> list[dict[str, Any]]:
    wanted: list[dict[str, Any]] = []
    seen: set[str] = set()
    patterns = ("navtree", "topnav", "layout.xsl", "menu.xml")
    for manifest_path in sorted((ROOT / "backups").rglob("manifest.jsonl")):
        try:
            lines = manifest_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line_no, line in enumerate(lines, start=1):
            try:
                record = json.loads(line)
            except (ValueError, TypeError):
                continue
            original = str(record.get("original") or "")
            if record.get("status") != "success" or not original or not any(p in original.casefold() for p in patterns):
                continue
            logical = canonical_url(original)
            if not logical or logical in seen:
                continue
            zip_part = record.get("zip_part")
            zip_file = record.get("zip_file")
            path = ROOT / str(zip_file).replace("\\", "/") if zip_file else manifest_path.parent / str(zip_part or "")
            try:
                with zipfile.ZipFile(path, "r") as archive:
                    body = archive.read(str(record.get("zip_entry")))
            except (OSError, KeyError, zipfile.BadZipFile):
                continue
            seen.add(logical)
            suffix = Path(urllib.parse.urlsplit(logical).path).suffix.casefold()
            if suffix in {".xsl", ".xslt"}:
                kind = "xsl"
            elif suffix == ".xml":
                kind = "xml"
            elif suffix == ".css":
                kind = "css"
            elif suffix in {".js", ".htc"}:
                kind = "js"
            elif suffix in STATIC_EXTENSIONS:
                kind = "binary"
            else:
                kind = "text"
            wanted.append({
                "source_url": logical,
                "source_kind": kind,
                "body": body,
                "locator": {
                    "manifest": rel(manifest_path),
                    "manifest_line": line_no,
                    "zip_file": rel(path),
                    "zip_entry": record.get("zip_entry"),
                    "actual_timestamp": record.get("actual_timestamp"),
                    "sha256": sha256(body),
                    "bytes": len(body),
                },
            })
    topic_path = ROOT / "research/baseline/scripts/topic-list.js"
    if topic_path.is_file():
        body = topic_path.read_bytes()
        headers_path = ROOT / "research/baseline/scripts/topic-list.js.headers.json"
        headers = load_json(headers_path) if headers_path.is_file() else {}
        wanted.append({
            "source_url": "http://www.worldofwarcraft.com/info/encyclopedia/scripts/topic-list.js",
            "source_kind": "topic-list",
            "body": body,
            "locator": {
                "source_file": rel(topic_path),
                "headers_file": rel(headers_path) if headers_path.is_file() else None,
                "actual_timestamp": headers.get("headers", {}).get("memento-datetime"),
                "sha256": sha256(body),
                "bytes": len(body),
            },
        })
    return wanted


def load_existing_states() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    integration_path = ROOT / "research/acquisition-2008/integration/index.json"
    if integration_path.is_file():
        data = load_json(integration_path)
        for item in data.get("logical_urls", []):
            logical = canonical_url(str(item.get("logical_url") or ""))
            if logical:
                result[logical] = {
                    "state": item.get("state"),
                    "activity_scope": item.get("activity_scope"),
                    "role": item.get("role"),
                    "kind": item.get("kind"),
                    "selected_capture": item.get("selected_capture"),
                    "source": "integration/index.json",
                }
    dep_path = ROOT / "research/acquisition-2008/dependencies/dependency-plan-final.json"
    if dep_path.is_file():
        data = load_json(dep_path)
        for item in data.get("items", []):
            logical = canonical_url(str(item.get("original") or ""))
            if not logical:
                continue
            result.setdefault(logical, {})
            result[logical]["dependency_selection"] = item.get("selection")
            result[logical]["dependency_existing"] = item.get("existing")
            result[logical]["dependency_kind"] = item.get("kind")
    return result


def build_inventory(out_dir: Path, max_requests: int = MAX_REQUESTS) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    core_items = load_integration_core()
    nav_sources = load_nav_sources()
    existing = load_existing_states()
    source_records: list[dict[str, Any]] = []
    all_references: list[dict[str, Any]] = []
    missing_sources: list[dict[str, Any]] = []
    for item in core_items:
        body, locator = read_selected_capture(item)
        logical = canonical_url(str(item.get("logical_url") or ""))
        if body is None:
            missing_sources.append({"source_url": logical, "locator": locator})
            continue
        source = {
            "source_url": logical,
            "source_kind": "html",
            "expected_title": item.get("expected_title"),
            "locator": locator,
            "reference_count": 0,
        }
        refs = extract_references(logical or str(item.get("logical_url")), body, "html")
        for ref in refs:
            ref.update({"parent_url": logical, "parent_kind": "core_html", "parent_locator": locator})
        source["reference_count"] = len(refs)
        source_records.append(source)
        all_references.extend(refs)
    for source in nav_sources:
        refs = extract_references(source["source_url"], source["body"], source["source_kind"])
        source_records.append({
            "source_url": source["source_url"],
            "source_kind": source["source_kind"],
            "locator": source["locator"],
            "reference_count": len(refs),
        })
        for ref in refs:
            ref.update({"parent_url": source["source_url"], "parent_kind": source["source_kind"], "parent_locator": source["locator"]})
        all_references.extend(refs)
    grouped: dict[str, dict[str, Any]] = {}
    for ref in all_references:
        target = ref["url"]
        if target not in grouped:
            grouped[target] = {
                "url": target,
                "classification": classify_url(target),
                "parents": [],
                "raw_forms": [],
                "reference_types": [],
            }
        node = grouped[target]
        parent = {
            "url": ref.get("parent_url"),
            "kind": ref.get("parent_kind"),
            "ref_type": ref.get("ref_type"),
            "raw": ref.get("raw"),
            "context": ref.get("context"),
        }
        if parent not in node["parents"]:
            node["parents"].append(parent)
        if ref.get("raw") not in node["raw_forms"]:
            node["raw_forms"].append(ref.get("raw"))
        if ref.get("ref_type") not in node["reference_types"]:
            node["reference_types"].append(ref.get("ref_type"))
    nodes = []
    for url, node in sorted(grouped.items()):
        state = existing.get(url, {})
        selected = state.get("selected_capture") or {}
        dep_selection = state.get("dependency_selection") or {}
        action = node["classification"]["action"]
        existing_state = state.get("state")
        if existing_state in {"invalid", "missing"} and not selected:
            acquisition_state = "known_archive_gap"
        elif existing_state == "supplement-only" and not selected:
            acquisition_state = "known_archive_gap"
        elif existing_state == "supplement-only" and selected:
            acquisition_state = "existing_supplement"
        elif existing_state == "preferred" or selected.get("source_type"):
            acquisition_state = "existing_preferred"
        elif state.get("dependency_existing"):
            acquisition_state = "existing_dependency"
        elif action == "candidate":
            acquisition_state = "pending_exact_cdx"
        else:
            acquisition_state = "excluded_or_review"
        priority = 99
        parsed_path = urllib.parse.urlsplit(url).path.casefold()
        if action == "candidate":
            path_parts = [part for part in parsed_path.split("/") if part]
            first_segment = path_parts[0] if path_parts else ""
            if parsed_path in PRIMARY_SEED_PATHS:
                priority = 0
            elif "/info/encyclopedia/" in parsed_path:
                priority = 10
            elif first_segment in {"gameguide", "story", "stories", "news", "downloads", "community", "workshop", "support", "pvp", "insider"} and len(path_parts) <= 2:
                priority = 5
            elif first_segment in {"gameguide", "story", "stories", "news", "downloads", "community", "workshop", "support", "pvp", "insider", "info"}:
                priority = 15
            elif node["classification"]["category"] == "static_resource":
                priority = 20
            else:
                priority = 30
        node.update({
            "depth": 1,
            "acquisition_state": acquisition_state,
            "existing_state": state,
            "selected_capture": selected or None,
            "known_selection": dep_selection or None,
            "capture_policy": {
                "primary": "latest status-200 exact CDX at or before 20080512210044",
                "same_day_static": "allowed only when exact CDX establishes the date",
                "supplement_90_days": "label only; never substitute for primary",
                "year_2008_supplement": "label only; never substitute for primary",
            },
            "requested_timestamp_template": ANCHOR if action == "candidate" else None,
            "requested_timestamp_is_capture_fact": False,
            "priority": priority,
            "frontier_eligible": not any(parsed_path.startswith(prefix) for prefix in DEFERRED_BULK_PREFIXES),
        })
        nodes.append(node)
    candidate_nodes = [
        node for node in nodes
        if node["frontier_eligible"]
        and node["acquisition_state"] in {"pending_exact_cdx", "existing_dependency", "existing_preferred"}
    ]
    candidate_nodes.sort(
        key=lambda node: (
            0 if node["acquisition_state"] == "pending_exact_cdx" else 1,
            node["priority"],
            node["url"],
        )
    )
    plan_nodes = candidate_nodes[:max_requests]
    frontier = {
        "schema_version": 1,
        "anchor_timestamp": ANCHOR,
        "mode": "offline_preparation",
        "network_performed": False,
        "max_requests": max_requests,
        "items": [
            {
                "frontier_id": hashlib.sha256(node["url"].encode()).hexdigest()[:16],
                "original": node["url"],
                "depth": 1,
                "status": "existing_reuse" if node["acquisition_state"].startswith("existing") else "pending_exact_cdx",
                "attempts": 0,
                "parents": node["parents"],
                "classification": node["classification"],
                "requested_timestamp": ANCHOR,
                "requested_timestamp_is_capture_fact": False,
            }
            for node in plan_nodes
        ],
    }
    wayback_plan = {
        "schema_version": 1,
        "anchor_timestamp": ANCHOR,
        "network_performed": False,
        "selection_requires_exact_cdx": True,
        "items": [
            {
                "original": node["url"],
                "timestamp": ANCHOR,
                "role": "site_expansion_first_ring",
                "selection_status": "pending_exact_cdx" if node["acquisition_state"] == "pending_exact_cdx" else "existing_reuse",
                "requested_timestamp_is_capture_fact": False,
                "parents": node["parents"],
            }
            for node in plan_nodes
            if node["acquisition_state"] == "pending_exact_cdx"
        ],
    }
    categories: dict[str, int] = {}
    actions: dict[str, int] = {}
    states: dict[str, int] = {}
    for node in nodes:
        category = str(node["classification"]["category"])
        action = str(node["classification"]["action"])
        state = str(node["acquisition_state"])
        categories[category] = categories.get(category, 0) + 1
        actions[action] = actions.get(action, 0) + 1
        states[state] = states.get(state, 0) + 1
    inventory = {
        "schema_version": 1,
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "anchor_timestamp": ANCHOR,
        "network_performed": False,
        "source_policy": {
            "core_pages": "52 selected offline integration captures",
            "topic_list": "baseline 2008 topic-list.js",
            "shared_navigation": "locally saved navtree/topnav/layout sources only",
            "javascript_execution": "never; static literals only",
        },
        "source_records": source_records,
        "missing_sources": missing_sources,
        "nodes": nodes,
        "summary": {
            "core_source_count": len(core_items),
            "core_sources_read": sum(1 for item in source_records if item["source_kind"] == "html"),
            "nav_source_count": sum(1 for item in source_records if item["source_kind"] != "html"),
            "unique_first_ring_urls": len(nodes),
            "categories": categories,
            "actions": actions,
            "acquisition_states": states,
            "planned_frontier_items": len(frontier["items"]),
            "pending_exact_cdx_items": len(wayback_plan["items"]),
            "deferred_bulk_urls": sum(1 for node in nodes if not node["frontier_eligible"]),
        },
    }
    node_urls = [node["url"] for node in nodes]
    frontier_urls = [item["original"] for item in frontier["items"]]
    plan_urls = [item["original"] for item in wayback_plan["items"]]
    selected_buckets: dict[str, int] = {}
    for node in nodes:
        selected = node.get("selected_capture") or {}
        bucket = capture_time_bucket(selected.get("actual_timestamp")) if selected else "not_selected"
        selected_buckets[bucket] = selected_buckets.get(bucket, 0) + 1
    validation = {
        "schema_version": 1,
        "generated_utc": inventory["generated_utc"],
        "network_performed": False,
        "checks": {
            "core_52_sources_loaded": len(core_items) == 52 and inventory["summary"]["core_sources_read"] == 52,
            "core_source_missing_count_zero": len(missing_sources) == 0,
            "first_ring_urls_unique": len(node_urls) == len(set(node_urls)),
            "frontier_urls_unique": len(frontier_urls) == len(set(frontier_urls)),
            "frontier_subset_of_inventory": set(frontier_urls).issubset(set(node_urls)),
            "frontier_respects_max_requests": len(frontier_urls) <= max_requests,
            "all_plan_timestamps_are_placeholders": all(
                item.get("requested_timestamp_is_capture_fact") is False for item in wayback_plan["items"]
            ),
            "no_fragment_in_canonical_urls": all("#" not in url for url in node_urls),
            "no_network_flag_anywhere": (
                inventory["network_performed"] is False
                and frontier["network_performed"] is False
                and wayback_plan["network_performed"] is False
            ),
        },
        "counts": {
            "core_source_count": len(core_items),
            "core_sources_read": inventory["summary"]["core_sources_read"],
            "missing_sources": len(missing_sources),
            "nav_source_records": inventory["summary"]["nav_source_count"],
            "unique_first_ring_urls": len(node_urls),
            "frontier_items": len(frontier_urls),
            "pending_exact_cdx_items": len(plan_urls),
            "deferred_bulk_urls": sum(1 for node in nodes if not node["frontier_eligible"]),
        },
        "existing_selected_capture_time_buckets": selected_buckets,
        "date_policy": {
            "anchor_timestamp": ANCHOR,
            "anchor_is_not_capture_fact": True,
            "existing_capture_timestamps_are_preserved": True,
            "post_anchor_items_require_supplement_label": True,
        },
        "limits": {
            "max_requests": max_requests,
            "max_archive_flows": MAX_ARCHIVE_FLOWS,
            "max_object_bytes": MAX_OBJECT_BYTES,
            "workspace_budget_bytes": MAX_WORKSPACE_BYTES,
            "minimum_free_bytes": MIN_FREE_BYTES,
            "reserve_bytes": RESERVE_BYTES,
        },
    }
    url_map_template = {
        "schema_version": 1,
        "generated_utc": inventory["generated_utc"],
        "network_performed": False,
        "status": "offline_template",
        "files": [
            {
                "logical_url": node["url"],
                "local_path": router_local_path(node["url"]),
                "mime": (node.get("selected_capture") or {}).get("declared_mime"),
                "kind": (node.get("existing_state") or {}).get("kind") or node["classification"]["category"],
                "role": (node.get("existing_state") or {}).get("role"),
                "sha256": (node.get("selected_capture") or {}).get("sha256"),
                "actual_timestamp": (node.get("selected_capture") or {}).get("actual_timestamp"),
                "indexed_capture_timestamp": (node.get("selected_capture") or {}).get("indexed_capture_timestamp"),
                "source_parent_urls": [parent.get("url") for parent in node.get("parents", []) if parent.get("url")],
                "cdx_digest": (node.get("selected_capture") or {}).get("cdx_digest"),
                "manifest": (node.get("selected_capture") or {}).get("source_manifest"),
                "zip_file": (node.get("selected_capture") or {}).get("zip_file"),
                "zip_entry": (node.get("selected_capture") or {}).get("zip_entry"),
                "redirect_chain": [(node.get("selected_capture") or {}).get("actual_url")],
                "error_class": None,
                "acquisition_state": node["acquisition_state"],
            }
            for node in nodes
        ],
        "note": "Template only: populated validated-url-map.json is written after --fetch verifies ZIP bytes; no entity bytes are exported here.",
    }
    (out_dir / "link-inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "frontier.json").write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "wayback-plan-template.json").write_text(json.dumps(wayback_plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plan = {
        "schema_version": 1,
        "anchor_timestamp": ANCHOR,
        "network_performed": False,
        "limits": {
            "max_requests": max_requests,
            "max_archive_flows": MAX_ARCHIVE_FLOWS,
            "max_object_bytes": MAX_OBJECT_BYTES,
            "workspace_budget_bytes": MAX_WORKSPACE_BYTES,
            "minimum_free_bytes": MIN_FREE_BYTES,
            "reserve_bytes": RESERVE_BYTES,
            "three_consecutive_site_failures": True,
        },
        "phases": [
            {"name": "exact_cdx_selection", "status": "pending_network_release", "scope": "planned frontier only"},
            {"name": "entity_fetch", "status": "pending_network_release", "scope": "selected status-200 captures only"},
            {"name": "recursive_next_ring", "status": "disabled", "reason": "first-ring review required before expansion"},
        ],
        "items": plan_nodes,
    }
    (out_dir / "crawl-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "url-map-template.json").write_text(json.dumps(url_map_template, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_lines = [
        "# 官网相近时期第一圈离线发现（2008）",
        "",
        "本阶段只读取现有 52 个核心页面、topic-list.js 与本地 shared navigation；未发 Archive 请求，未执行 JavaScript。",
        "",
        f"- 核心源：{len(core_items)}，成功读取：{inventory['summary']['core_sources_read']}，缺失：{len(missing_sources)}。",
        f"- 导航/脚本源：{inventory['summary']['nav_source_count']}。",
        f"- 去重第一圈 URL：{len(nodes)}；有限 frontier：{len(frontier['items'])}；待 exact-CDX：{len(wayback_plan['items'])}；延后批量归档：{inventory['summary']['deferred_bulk_urls']}。",
        f"- 计划上限：{max_requests} 请求、{MAX_ARCHIVE_FLOWS} Archive 流、单对象 {MAX_OBJECT_BYTES} bytes、workspace {MAX_WORKSPACE_BYTES} bytes、D 盘保留 {MIN_FREE_BYTES} bytes + {RESERVE_BYTES} bytes。",
        "",
        "## 分类统计",
        "",
        f"- category: `{json.dumps(categories, ensure_ascii=False, sort_keys=True)}`",
        f"- action: `{json.dumps(actions, ensure_ascii=False, sort_keys=True)}`",
        f"- acquisition_state: `{json.dumps(states, ensure_ascii=False, sort_keys=True)}`",
        "",
        "## 离线验收",
        "",
        "- `validation.json` 检查核心源读取、URL 去重、frontier 子集、占位时间戳和无网络标记；所有检查应为 `true`。",
        f"- 已选本地捕获日期分桶：`{json.dumps(selected_buckets, ensure_ascii=False, sort_keys=True)}`；这些实际日期保留在节点状态，不能由锚点覆盖。",
        "",
        "## 时间与获取规则",
        "",
        "计划模板里的 20080512210044 只是未来 CDX/实体请求锚点，不能当作捕获事实。放行后 `--query-cdx --allow-network` 按 URL 做有限 exact-CDX 查询并保存原始响应，或 `--select --cdx` 读取已保存响应，选择 <= 锚点的 status-200 记录；同日静态资源、锚点 ±90 日与 2008 年内记录只作明确标注的补充。已有本地实体进入 reuse，保留 manifest、实际日期、MIME、来源父链接和跳转链。",
        "",
        "## 排除规则",
        "",
        "外部社交/论坛、账号/支付/Armory 等动态路径、大型下载与视频不进入实体抓取 frontier；相关官方域名进入 review。参数化 URL、XSL 运行时相对资源和 `{icon}`/`{$letter}` 等模板占位符保留在清单中并标记 review，不把日历、示例字符串或动态拼接当作静态页面。已知 invalid/missing/supplement-only 记录不重复加入本轮队列；月度漫画、machinima/tournament 子树延后。",
        "",
        "## 可续传接口",
        "",
        "`frontier.json` 保存每项状态、父链接和尝试次数；`--query-cdx`/`--select` 生成带真实 CDX timestamp、digest、length、MIME 的 `wayback-plan-selected.json` 后，`--fetch --allow-network` 才会交给 `tools/wayback_backup.py`。递归下一圈保持 disabled，只有第一圈审阅后才启用。",
        "`--select --cdx <saved-response>` 读取保存的 CDX 响应，选择锚点前最新 status-200；它只写 `wayback-plan-selected.json`，绝不联网。放行后 `--fetch --allow-network` 复用现有 downloader，完成后校验 ZIP SHA256/长度并生成 `validated-url-map.json`。",
        "",
        "## 复现",
        "",
        "```powershell",
        "python tools\\expand_wayback_site.py --offline",
        "python tools\\expand_wayback_site.py --help",
        "```",
        "",
    ]
    (out_dir / "report.md").write_text("\n".join(report_lines), encoding="utf-8")
    return {"inventory": inventory, "frontier": frontier, "crawl_plan": plan}


def _read_response_limited(stream, limit: int = MAX_CDX_BYTES) -> tuple[bytes, bool]:
    body = stream.read(limit + 1)
    return body[:limit], len(body) > limit


def query_exact_cdx(
    out_dir: Path,
    *,
    max_queries: int,
    timeout_seconds: float,
    deadline_seconds: float,
) -> dict[str, Any]:
    """Query one exact URL at a time and preserve every raw response."""
    template_path = out_dir / "wayback-plan-template.json"
    template = load_json(template_path)
    query_items = list(template.get("items", []))[:max_queries]
    raw_dir = out_dir / "cdx"
    raw_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    results: list[dict[str, Any]] = []
    consecutive_failures = 0
    stop_reason: str | None = None
    for attempt, item in enumerate(query_items, start=1):
        if time.monotonic() - started >= deadline_seconds:
            stop_reason = "deadline"
            break
        original = str(item.get("original") or "")
        query = urllib.parse.urlencode([
            ("url", original),
            ("matchType", "exact"),
            ("output", "json"),
            ("fl", "timestamp,original,statuscode,digest,length,mimetype"),
            ("filter", "statuscode:200"),
            ("to", ANCHOR),
        ])
        request_url = f"https://web.archive.org/cdx/search/cdx?{query}"
        stem = f"{attempt:04d}-{sha256(original.encode('utf-8'))[:16]}"
        raw_path = raw_dir / f"{stem}.json"
        meta_path = raw_dir / f"{stem}.meta.json"
        query_started = time.monotonic()
        result: dict[str, Any] = {
            "attempt": attempt,
            "original": original,
            "requested_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "request_url": request_url,
            "match_type": "exact",
            "to_timestamp": ANCHOR,
            "status": None,
            "final_url": None,
            "response_headers": {},
            "body_bytes": 0,
            "body_sha256": None,
            "truncated": False,
            "error": None,
        }
        body = b""
        try:
            request = urllib.request.Request(
                request_url,
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "identity",
                    "User-Agent": "WOW-Encyclopedia-site-expansion/1.0",
                },
                method="GET",
            )
            with urllib.request.urlopen(request, timeout=min(timeout_seconds, 30.0)) as response:
                body, truncated = _read_response_limited(response)
                result["status"] = int(response.status)
                result["final_url"] = response.geturl()
                result["response_headers"] = {str(key): str(value) for key, value in response.headers.items()}
                result["truncated"] = truncated
        except urllib.error.HTTPError as exc:
            result["status"] = int(exc.code)
            result["final_url"] = exc.geturl()
            result["response_headers"] = {str(key): str(value) for key, value in exc.headers.items()}
            try:
                body, truncated = _read_response_limited(exc)
                result["truncated"] = truncated
            except Exception as body_exc:
                result["error"] = f"http_error_body:{type(body_exc).__name__}:{body_exc}"
        except Exception as exc:
            result["error"] = f"{type(exc).__name__}:{exc}"
        raw_path.write_bytes(body)
        result["raw_file"] = rel(raw_path)
        result["body_bytes"] = len(body)
        result["body_sha256"] = sha256(body) if body else None
        result["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        result["duration_seconds"] = round(time.monotonic() - query_started, 3)
        meta_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        results.append(result)
        status = result.get("status")
        site_failure = bool(result.get("error")) or status is None or status == 429 or (status is not None and status >= 500)
        if site_failure:
            consecutive_failures += 1
            if consecutive_failures >= 3:
                stop_reason = "three_consecutive_site_failures"
                break
        else:
            consecutive_failures = 0
    if stop_reason is None:
        stop_reason = "plan_complete" if len(results) == len(query_items) else "no_more_queries"
    summary = {
        "schema_version": 1,
        "network_performed": True,
        "anchor_timestamp": ANCHOR,
        "started_at": dt.datetime.fromtimestamp(time.time() - (time.monotonic() - started), dt.timezone.utc).isoformat(),
        "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "timeout_seconds": min(timeout_seconds, 30.0),
        "deadline_seconds": deadline_seconds,
        "max_queries": max_queries,
        "max_archive_flows": MAX_ARCHIVE_FLOWS,
        "retry_policy": "no automatic CDX retry; stop after three consecutive site failures",
        "attempts": len(results),
        "stop_reason": stop_reason,
        "raw_directory": rel(raw_dir),
        "http_status_counts": {
            str(status): sum(row.get("status") == status for row in results)
            for status in sorted({row.get("status") for row in results}, key=lambda value: str(value))
        },
        "errors": [
            {"original": row["original"], "error": row.get("error"), "status": row.get("status")}
            for row in results
            if row.get("error") or row.get("status") not in {200, 404}
        ],
    }
    (out_dir / "cdx-query-results.json").write_text(json.dumps({"schema_version": 1, "results": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "cdx-query-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def select_exact_cdx(out_dir: Path, cdx_paths: Iterable[Path]) -> dict[str, Any]:
    """Select <=anchor status-200 CDX rows from saved responses only."""
    cdx_paths = list(cdx_paths)
    template_path = out_dir / "wayback-plan-template.json"
    if not template_path.is_file():
        raise RuntimeError("wayback-plan-template.json is missing; run --offline first")
    template = load_json(template_path)
    records, source_errors = load_cdx_records(cdx_paths)
    by_identity: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for record in records:
        identity = record.get("identity")
        if identity:
            by_identity.setdefault(identity, []).append(record)
    selected_items: list[dict[str, Any]] = []
    missing_items: list[dict[str, Any]] = []
    for item in template.get("items", []):
        original = str(item.get("original") or "")
        identity = cdx_identity(original)
        matches = [
            record
            for record in by_identity.get(identity, [])
            if record.get("statuscode") == "200" and str(record.get("timestamp", "")) <= ANCHOR
        ]
        if not matches:
            missing_items.append({
                "original": original,
                "reason": "no_status_200_cdx_at_or_before_anchor",
                "candidate_rows": len(by_identity.get(identity, [])),
            })
            continue
        chosen = max(matches, key=lambda record: (str(record.get("timestamp", "")), bool(record.get("digest"))))
        selected = dict(item)
        selected.update({
            "timestamp": chosen["timestamp"],
            "requested_timestamp_is_capture_fact": True,
            "selection_status": "selected_primary_exact_cdx",
            "indexed_capture_timestamp": chosen["timestamp"],
            # Keep the CDX row's own original URL.  The plan item is the
            # canonical logical URL and can differ by scheme or trailing
            # slash; the selected row is the capture identity to replay.
            "cdx_original": chosen.get("original"),
            "cdx_digest": chosen.get("digest"),
            "cdx_length": chosen.get("length"),
            "declared_mime": chosen.get("mimetype"),
            "cdx_source_file": chosen.get("source_file"),
            "cdx_source_row": chosen.get("source_row"),
        })
        selected_items.append(selected)
    selected_plan = {
        "schema_version": 1,
        "anchor_timestamp": ANCHOR,
        "network_performed": False,
        "selection_requires_exact_cdx": False,
        "selection_policy": "latest status-200 exact CDX at or before anchor; scheme/default-port aliases only",
        "cdx_source_files": [rel(path) for path in cdx_paths],
        "cdx_record_count": len(records),
        "source_errors": source_errors,
        "items": selected_items,
        "missing": missing_items,
    }
    selected_path = out_dir / "wayback-plan-selected.json"
    selected_path.write_text(json.dumps(selected_plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    selection_report = {
        "schema_version": 1,
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "network_performed": False,
        "anchor_timestamp": ANCHOR,
        "source_files": [rel(path) for path in cdx_paths],
        "cdx_record_count": len(records),
        "selected_count": len(selected_items),
        "missing_count": len(missing_items),
        "source_errors": source_errors,
        "missing": missing_items,
        "selected_plan": rel(selected_path),
    }
    (out_dir / "cdx-selection.json").write_text(json.dumps(selection_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"selected_plan": selected_plan, "selection_report": selection_report}


def router_local_path(url: str) -> str:
    """Return a deterministic future-router path without writing entity bytes."""
    logical = canonical_url(url) or url
    parsed = urllib.parse.urlsplit(logical)
    host = re.sub(r"[^A-Za-z0-9._-]", "_", parsed.netloc)
    path = parsed.path or "/"
    parts = [re.sub(r"[^A-Za-z0-9._-]", "_", part) for part in path.split("/") if part]
    if not parts or path.endswith("/"):
        parts.append("index.html")
    if parsed.query:
        parts[-1] = f"{parts[-1]}__q_{sha256(parsed.query.encode('utf-8'))[:12]}"
    return "/".join(["site-expansion-2008", host, *parts])


def _manifest_body_and_info(record: dict[str, Any], manifest_path: Path) -> tuple[bytes, zipfile.ZipInfo]:
    zip_file = record.get("zip_file")
    if zip_file:
        zip_path = ROOT / str(zip_file).replace("\\", "/")
    else:
        zip_path = manifest_path.parent / str(record.get("zip_part") or "")
    with zipfile.ZipFile(zip_path, "r") as archive:
        info = archive.getinfo(str(record["zip_entry"]))
        return archive.read(info), info


def _manifest_body(record: dict[str, Any], manifest_path: Path) -> bytes:
    return _manifest_body_and_info(record, manifest_path)[0]


def _body_kind(url: str, mime: str, body: bytes) -> str:
    lower_mime = (mime or "").casefold()
    suffix = Path(urllib.parse.urlsplit(url).path).suffix.casefold()
    html_head = body[:8192]
    looks_html = bool(re.search(rb"<!doctype\s+html|<html(?:\s|>)|<head(?:\s|>)", html_head, re.I))
    if looks_html or lower_mime.startswith("text/html") or "xhtml" in lower_mime:
        return "html"
    if lower_mime.startswith("image/") or body.startswith((b"GIF8", b"\x89PNG", b"\xff\xd8\xff", b"BM")):
        return "image"
    if "css" in lower_mime or suffix == ".css":
        return "css"
    if "javascript" in lower_mime or "ecmascript" in lower_mime or suffix in {".js", ".htc"}:
        return "js"
    if "xml" in lower_mime or suffix in {".xml", ".xsl", ".xslt"}:
        return "xml"
    return "binary"


def _wayback_error_marker(body: bytes) -> str | None:
    text = body[:128 * 1024].decode("utf-8", errors="ignore").casefold()
    markers = (
        "wayback machine error",
        "no archived snapshot",
        "this url has been excluded",
        "the requested url was not found",
        "got an http 404 response",
        "got an http 429 response",
        "got an http 5xx response",
        "memento not found",
        "timetravel error",
        "404 file not found",
        "modern guide",
        "battle.net error",
        "error - battle.net",
    )
    for marker in markers:
        if marker in text:
            return marker
    title = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    if title and ("not found" in title.group(1) or "404" in title.group(1)):
        return "error_title_not_found"
    return None


def _image_decode_error(body: bytes, out_dir: Path) -> str | None:
    """Require a full Pillow decode when available; otherwise remain pending."""
    runtime = Path(r"C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
    image_path: Path | None = None
    try:
        import PIL.Image  # type: ignore[import-not-found]
        from io import BytesIO

        with PIL.Image.open(BytesIO(body)) as image:
            image.verify()
        with PIL.Image.open(BytesIO(body)) as image:
            image.load()
        return None
    except ImportError:
        if not runtime.is_file():
            return "image_decode_unverified_pillow_unavailable"
        try:
            with tempfile.NamedTemporaryFile(prefix=".image-validate-", suffix=".bin", dir=out_dir, delete=False) as stream:
                stream.write(body)
                image_path = Path(stream.name)
            probe = subprocess.run(
                [
                    str(runtime),
                    "-c",
                    "from PIL import Image; import sys; im=Image.open(sys.argv[1]); im.verify(); im=Image.open(sys.argv[1]); im.load()",
                    str(image_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=20,
            )
            if probe.returncode != 0:
                return f"image_decode_error:{probe.stderr.strip()[:160]}"
            return None
        except (OSError, subprocess.SubprocessError) as exc:
            return f"image_decode_unverified:{type(exc).__name__}"
        finally:
            if image_path is not None:
                try:
                    image_path.unlink()
                except OSError:
                    pass
    except Exception as exc:
        return f"image_decode_error:{type(exc).__name__}"


def _entity_validation_errors(item: dict[str, Any], record: dict[str, Any], body: bytes, mime: str, out_dir: Path) -> list[str]:
    errors: list[str] = []
    digest = str(item.get("cdx_digest") or "")
    if not digest:
        errors.append("cdx_digest_missing")
    else:
        computed = base64.b32encode(hashlib.sha1(body).digest()).decode("ascii").rstrip("=")
        if computed.casefold() != digest.casefold():
            errors.append("cdx_sha1_base32_mismatch")
    actual_timestamp = timestamp_digits(record.get("actual_timestamp"))
    if not actual_timestamp:
        errors.append("actual_timestamp_missing")
    marker = _wayback_error_marker(body)
    if marker:
        errors.append(f"archive_or_origin_error:{marker}")
    kind = _body_kind(str(item.get("original") or ""), mime, body)
    if kind == "image":
        image_error = _image_decode_error(body, out_dir)
        if image_error:
            errors.append(image_error)
    return errors


def write_validated_url_map(out_dir: Path, selected_plan_path: Path, backup_dir: Path) -> dict[str, Any]:
    """Verify successful backup entries and write the future-router URL map."""
    selected_plan = load_json(selected_plan_path)
    manifest_path = backup_dir / "manifest.jsonl"
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    if manifest_path.is_file():
        for line_number, line in enumerate(manifest_path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if isinstance(record, dict) and record.get("original") and record.get("requested_timestamp"):
                latest[(str(record["original"]), str(record["requested_timestamp"]))] = record
    files: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for item in selected_plan.get("items", []):
        original = str(item.get("original") or "")
        key = (original, str(item.get("timestamp") or ""))
        record = latest.get(key)
        if not record or record.get("status") != "success":
            errors.append({"logical_url": original, "error_class": "missing_success_manifest", "requested_timestamp": key[1]})
            continue
        try:
            body, zip_info = _manifest_body_and_info(record, manifest_path)
        except (OSError, KeyError, zipfile.BadZipFile) as exc:
            errors.append({"logical_url": original, "error_class": f"body_read_error:{type(exc).__name__}", "requested_timestamp": key[1]})
            continue
        computed_sha = sha256(body)
        expected_sha = str(record.get("sha256") or "")
        expected_length = int(record.get("content_length") or -1)
        response_headers = record.get("response_headers") or {}
        mime = str(record.get("declared_mime") or response_headers.get("Content-Type") or response_headers.get("content-type") or "").split(";", 1)[0].strip()
        validation_errors = _entity_validation_errors(item, record, body, mime, out_dir)
        if expected_sha and computed_sha != expected_sha:
            validation_errors.append("sha256_mismatch")
        if expected_length >= 0 and len(body) != expected_length:
            validation_errors.append("content_length_mismatch")
        computed_crc = zlib.crc32(body) & 0xFFFFFFFF
        if computed_crc != int(zip_info.CRC):
            validation_errors.append("zip_crc_mismatch")
        if validation_errors:
            errors.append({"logical_url": original, "error_class": ",".join(validation_errors), "requested_timestamp": key[1], "sha256": computed_sha})
            continue
        attempts = record.get("attempts") or []
        redirect_chain = [str(record.get("requested_url"))] if record.get("requested_url") else []
        redirect_chain.extend(str(attempt.get("final_url")) for attempt in attempts if attempt.get("final_url"))
        indexed_timestamp = item.get("indexed_capture_timestamp") or item.get("timestamp")
        actual_timestamp = timestamp_digits(record.get("actual_timestamp"))
        cdx_original = str(item.get("cdx_original") or original)
        manifest_original = str(record.get("original") or original)
        replay_url = str(record.get("actual_url") or "")
        files.append({
            "logical_url": original,
            "source_url": cdx_original,
            "capture_original": cdx_original,
            "manifest_original": manifest_original,
            "requested_url": record.get("requested_url"),
            "actual_url": replay_url or None,
            "base_url": replay_url or cdx_original or manifest_original,
            "local_path": router_local_path(original),
            "mime": mime or None,
            "kind": _body_kind(original, mime, body),
            "role": item.get("role"),
            "sha256": computed_sha,
            "content_length": len(body),
            "actual_timestamp": actual_timestamp,
            "entity_observed_capture_timestamp": actual_timestamp,
            "indexed_capture_timestamp": indexed_timestamp,
            "timestamp_drift": bool(actual_timestamp and indexed_timestamp and actual_timestamp != indexed_timestamp),
            "cdx_digest": item.get("cdx_digest"),
            "source_parent_urls": [parent.get("url") for parent in item.get("parents", []) if parent.get("url")],
            "manifest": rel(manifest_path),
            "zip_part": record.get("zip_part"),
            "zip_entry": record.get("zip_entry"),
            "zip_crc32": f"{int(zip_info.CRC):08x}",
            "zip_crc32_computed": f"{computed_crc:08x}",
            "redirect_chain": redirect_chain,
            "error_class": None,
        })
    supplement_only = []
    active_files = []
    for file_record in files:
        if file_record.get("logical_url") in COMPARISON_ONLY_URLS:
            supplement_only.append({
                **file_record,
                "acquisition_scope": "supplement_only",
                "exclusion_reason": "outside_2008_near_window",
            })
        else:
            active_files.append(file_record)
    result = {
        "schema_version": 1,
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "network_performed": False,
        "status": "complete" if selected_plan.get("items") and not errors and len(files) == len(selected_plan.get("items", [])) else "partial",
        "active_scope": "2008_near_first_ring",
        "files": active_files,
        "supplement_only": supplement_only,
        "all_validated_count": len(files),
        "errors": errors,
        "selected_plan": rel(selected_plan_path),
        "backup_dir": rel(backup_dir),
        "interface": {
            "logical_url": "original site URL",
            "source_url": "CDX row original URL, including its scheme/trailing slash",
            "capture_original": "same CDX original URL; distinct from logical_url if normalized",
            "manifest_original": "downloader manifest original URL",
            "requested_url": "Wayback replay request URL",
            "actual_url": "final Wayback replay URL observed by downloader",
            "base_url": "actual_url when available, retaining trailing slash semantics",
            "local_path": "future router path; bytes remain in ZIP until an explicit export stage",
            "indexed_capture_timestamp": "CDX selection fact",
            "actual_timestamp": "Memento/manifest observation",
            "source_parent_urls": "first-ring provenance",
            "redirect_chain": "requested archive URL plus observed final URLs",
            "error_class": "validation/acquisition failure classification",
        },
    }
    map_path = out_dir / "validated-url-map.json"
    map_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


# ---------------------------------------------------------------------------
# Site recovery: sidebar page discovery and bounded prefix-CDX acquisition.
# This is deliberately separate from the encyclopedia first-ring output above.

RECOVERY_CATEGORY_NAMES = {
    "menuNews": "News",
    "menuAccount": "Account",
    "menuGameGuide": "Game Guide",
    "menuInteractive": "Interactive",
    "menuMedia": "Media",
    "menuForums": "Forums",
    "menuCommunity": "Community",
    "menuSupport": "Support",
}
RECOVERY_MAIN_CATEGORY_NAMES = {
    "1": "News",
    "2": "Account",
    "3": "Guide",
    "4": "Workshop",
    "5": "Forums",
    "6": "Community",
    "7": "Support",
    "8": "Media",
}
RECOVERY_SOURCE_FILES = (
    ("navtree-main", "research/site-recovery-2008/.navtree-main.js"),
    ("navtree", "research/site-recovery-2008/.navtree.js"),
    ("menu", "research/site-recovery-2008/.menu.xml"),
)
RECOVERY_ACCOUNT_MARKERS = (
    "/account/", "/loginsupport/", "/billing", "/payment", "/checkout",
    "/character-transfer", "/character-move", "/recruit-a-friend",
    "/resurrect-a-friend", "/realmstatus/", "/ptr/",
)
RECOVERY_INTERACTIVE_MARKERS = (
    "/events/calendar/", "/calendar/", "/talent-index/", "/toplist/",
    "/flashmap/", "/arenatournament/", "/battlegroups/",
)
RECOVERY_STATIC_SUFFIXES = STATIC_EXTENSIONS - {".xml", ".xsl", ".xslt"}
RECOVERY_PUBLIC_PAGE_SUFFIXES = PAGE_EXTENSIONS | {".xml", ".xsl", ".xslt"}


def _recovery_identity(url: str) -> tuple[str, str, str] | None:
    """Identity for page matching; scheme and one trailing slash are aliases."""
    logical = canonical_url(url)
    if not logical:
        return None
    parsed = urllib.parse.urlsplit(logical)
    host = (parsed.hostname or "").casefold().rstrip(".")
    port = parsed.port
    if port is not None and not (
        (parsed.scheme == "http" and port == 80)
        or (parsed.scheme == "https" and port == 443)
    ):
        host = f"{host}:{port}"
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/") or "/"
    return host, path, parsed.query


def _recovery_identity_aliases(url: str) -> set[tuple[str, str, str]]:
    identity = _recovery_identity(url)
    if not identity:
        return set()
    host, path, query = identity
    aliases = {(host, path, query)}
    if path == "/":
        return aliases
    aliases.add((host, path + "/", query))
    return aliases


def _recovery_label(expression: str) -> str:
    values = [value.strip() for value in re.findall(r'"([^"\r\n]*)"', expression) if value.strip()]
    return " ".join(values) or expression.strip()


def _recovery_sidebar_sources() -> list[tuple[str, Path]]:
    sources = [(kind, ROOT / relative) for kind, relative in RECOVERY_SOURCE_FILES]
    missing = [str(path) for _, path in sources if not path.is_file()]
    if missing:
        raise RuntimeError("missing preserved sidebar sources: " + ", ".join(missing))
    return sources


def _recovery_classify(url: str) -> dict[str, Any]:
    parsed = urllib.parse.urlsplit(url)
    host = (parsed.hostname or "").casefold().rstrip(".")
    path = parsed.path.casefold()
    suffix = Path(parsed.path).suffix.casefold()
    if host not in MAIN_HOSTS:
        return {"category": "external_or_social", "action": "exclude", "reason": "non_primary_host"}
    if host.endswith("forums.worldofwarcraft.com") or path.startswith("/forums"):
        return {"category": "social_forum", "action": "exclude", "reason": "forum_or_social"}
    if any(marker in path for marker in RECOVERY_ACCOUNT_MARKERS):
        return {"category": "dynamic_account", "action": "exclude", "reason": "account_or_dynamic"}
    if any(marker in path for marker in RECOVERY_INTERACTIVE_MARKERS):
        return {"category": "dynamic_interactive", "action": "exclude", "reason": "interactive_or_live_data"}
    if suffix in LARGE_EXTENSIONS or suffix in RECOVERY_STATIC_SUFFIXES:
        return {"category": "static_or_large", "action": "exclude", "reason": "non_page_resource"}
    if parsed.query:
        return {"category": "parameterized_page", "action": "exclude", "reason": "parameterized_or_form_endpoint"}
    if suffix in RECOVERY_PUBLIC_PAGE_SUFFIXES or not suffix:
        return {"category": "public_page", "action": "candidate", "reason": "official_sidebar_page"}
    return {"category": "unknown", "action": "review", "reason": "unrecognized_suffix"}


def _recovery_priority(url: str, categories: list[str]) -> tuple[int, int, int, str]:
    parsed = urllib.parse.urlsplit(url)
    path = parsed.path or "/"
    special = {
        "/": 0,
        "/index.xml": 1,
        "/info/index.xml": 2,
        "/info/": 3,
        "/news/": 4,
        "/downloads/": 5,
        "/community/": 6,
        "/info/story/index.html": 7,
    }
    category_rank = {
        "News": 0, "Guide": 1, "Game Guide": 1, "Story": 2,
        "Media": 3, "Community": 4, "Workshop": 5,
    }
    special_rank = special.get(path, 20)
    category_rank_value = min((category_rank.get(category, 9) for category in categories), default=9)
    return special_rank, category_rank_value, path.count("/"), url


def _recovery_existing_identities() -> set[tuple[str, str, str]]:
    identities: set[tuple[str, str, str]] = set()
    # Only active 2008-near expansion files suppress recovery work.  The
    # comparison map deliberately contains 2007/2006 captures and must not
    # make the live homepage or Game Guide look recovered.
    for relative in ("research/site-expansion-2008/validated-url-map.json",):
        path = ROOT / relative
        if not path.is_file():
            continue
        try:
            data = load_json(path)
        except (OSError, ValueError):
            continue
        # Historical comparison captures (for example the 2007 root and the
        # 2006 /info/basics page) are deliberately excluded from this set.
        # They remain visible in the expansion map but cannot suppress a
        # current recovery candidate.
        for item in data.get("files", []):
            if item.get("logical_url"):
                identities.update(_recovery_identity_aliases(str(item["logical_url"])))
    source_path = ROOT / "research/site-expansion-2008/link-inventory.json"
    if source_path.is_file():
        try:
            data = load_json(source_path)
        except (OSError, ValueError):
            data = {}
        for record in data.get("source_records", []):
            url = record.get("source_url")
            if url and record.get("locator"):
                identities.update(_recovery_identity_aliases(str(url)))
    return identities


def build_recovery_inventory(out_dir: Path, batch_size: int = RECOVERY_BATCH_ENTITIES) -> dict[str, Any]:
    """Read preserved sidebar sources and create a finite page frontier."""
    out_dir.mkdir(parents=True, exist_ok=True)
    sources = _recovery_sidebar_sources()
    rows: list[dict[str, Any]] = []
    js_pattern = re.compile(r'^\s*(Menu[0-9_]+)=new Array\((.*?),"([^"]+)"', re.M)
    for source_kind, source_path in sources:
        text = source_path.read_text(encoding="utf-8", errors="replace")
        if source_kind == "menu":
            root = ET.fromstring(text)
            for category in root.findall("category"):
                category_name = RECOVERY_CATEGORY_NAMES.get(str(category.get("name")), str(category.get("name")))
                for index, menu_item in enumerate(category.findall("menuItem"), start=1):
                    raw_url = str(menu_item.get("url") or "")
                    url = canonical_url(raw_url, "http://www.worldofwarcraft.com/")
                    if not url:
                        continue
                    rows.append({
                        "source_kind": source_kind,
                        "source_file": rel(source_path),
                        "source_id": f"{category.get('name')}:{index}",
                        "line": None,
                        "label": str(menu_item.get("name") or ""),
                        "raw_url": raw_url,
                        "url": url,
                        "category": category_name,
                        "had_fragment": bool(urllib.parse.urlsplit(raw_url).fragment),
                    })
            continue
        for match in js_pattern.finditer(text):
            menu_id = match.group(1)
            parts = menu_id.split("_")
            if source_kind == "navtree-main":
                category = RECOVERY_MAIN_CATEGORY_NAMES.get(parts[1], "Home") if len(parts) > 1 else "Home"
            else:
                category = "Game Guide"
            raw_url = match.group(3)
            url = canonical_url(raw_url, "http://www.worldofwarcraft.com/")
            if not url:
                continue
            rows.append({
                "source_kind": source_kind,
                "source_file": rel(source_path),
                "source_id": menu_id,
                "line": text[:match.start()].count("\n") + 1,
                "label": _recovery_label(match.group(2)),
                "raw_url": raw_url,
                "url": url,
                "category": category,
                "had_fragment": bool(urllib.parse.urlsplit(raw_url).fragment),
            })
    nodes: dict[str, dict[str, Any]] = {}
    for row in rows:
        node = nodes.setdefault(row["url"], {
            "url": row["url"],
            "labels": [],
            "categories": [],
            "references": [],
        })
        if row["label"] and row["label"] not in node["labels"]:
            node["labels"].append(row["label"])
        if row["category"] not in node["categories"]:
            node["categories"].append(row["category"])
        node["references"].append({
            "source_kind": row["source_kind"],
            "source_file": row["source_file"],
            "source_id": row["source_id"],
            "line": row["line"],
            "label": row["label"],
            "raw_url": row["raw_url"],
            "had_fragment": row["had_fragment"],
        })
    existing = _recovery_existing_identities()
    inventory_nodes: list[dict[str, Any]] = []
    for node in nodes.values():
        classification = _recovery_classify(node["url"])
        node["classification"] = classification
        node["priority_key"] = list(_recovery_priority(node["url"], node["categories"]))
        if classification["action"] == "candidate" and _recovery_identity(node["url"]) in existing:
            node["acquisition_state"] = "existing_verified"
            node["action"] = "skip_existing"
        else:
            node["acquisition_state"] = {
                "candidate": "pending_prefix_cdx",
                "exclude": "excluded_by_scope",
                "review": "review_required",
            }.get(classification["action"], "review_required")
            node["action"] = classification["action"]
        inventory_nodes.append(node)
    inventory_nodes.sort(key=lambda node: (tuple(node["priority_key"]), node["url"]))
    pending = [node for node in inventory_nodes if node["action"] == "candidate"]
    for index, node in enumerate(pending):
        node["batch"] = index // batch_size + 1
        node["batch_index"] = index % batch_size + 1
    for node in inventory_nodes:
        node.setdefault("batch", None)
        node.setdefault("batch_index", None)
    from collections import Counter
    summary = {
        "sidebar_source_rows": len(rows),
        "unique_sidebar_urls": len(inventory_nodes),
        "public_sidebar_pages": sum(node["classification"]["category"] == "public_page" for node in inventory_nodes),
        "pending_recovery_pages": len(pending),
        "first_batch_pages": min(batch_size, len(pending)),
        "deferred_pages": max(0, len(pending) - batch_size),
        "action_counts": dict(Counter(node["action"] for node in inventory_nodes)),
        "category_counts": dict(Counter(node["classification"]["category"] for node in inventory_nodes)),
        "pending_by_sidebar_category": dict(Counter(category for node in pending for category in node["categories"])),
    }
    inventory = {
        "schema_version": 1,
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "network_performed": False,
        "anchor_timestamp": ANCHOR,
        "source_files": [rel(path) for _, path in sources],
        "source_policy": "parse preserved menu and navtree text; never execute JavaScript",
        "summary": summary,
        "nodes": inventory_nodes,
    }
    (out_dir / "sidebar-inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Put exact homepage/guide aliases first so a short entity deadline still
    # obtains the most important public routes before the long Game Guide tail.
    plan_items = []
    for offset, alias in enumerate(RECOVERY_ALIAS_PAGES, start=1):
        alias_item = dict(alias)
        alias_item.update({
            "batch": 1,
            "batch_index": offset,
            "selection_state": "pending_exact_cdx",
        })
        plan_items.append(alias_item)
    for node in pending:
        plan_items.append({
            "original": node["url"],
            "role": "site_recovery_sidebar_page",
            "kind": "page",
            "labels": node["labels"],
            "categories": node["categories"],
            "parents": [{"url": ref["source_file"], "label": ref["label"], "line": ref["line"]} for ref in node["references"]],
            "batch": node["batch"],
            "batch_index": node["batch_index"],
            "selection_state": "pending_prefix_cdx",
        })
    first_batch = [item for item in plan_items if item["batch"] == 1]
    plan = {
        "schema_version": 1,
        "generated_utc": inventory["generated_utc"],
        "network_performed": False,
        "anchor_timestamp": ANCHOR,
        "query_to_timestamp": RECOVERY_QUERY_TO,
        "batch_size": batch_size,
        "source_inventory": "research/site-recovery-2008/sidebar-inventory.json",
        "items": plan_items,
        "first_batch_items": first_batch,
        "deferred_items": len(plan_items) - len(first_batch),
        "prefix_queries": [{"label": label, "url": url, "match_type": "prefix"} for label, url in RECOVERY_PREFIXES]
        + [{"label": label, "url": url, "match_type": "exact"} for label, url in RECOVERY_EXACT_ALIASES],
    }
    (out_dir / "recovery-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    frontier = {
        "schema_version": 1,
        "generated_utc": inventory["generated_utc"],
        "network_performed": False,
        "items": [{"original": item["original"], "batch": item["batch"], "status": "pending_prefix_cdx", "attempts": 0} for item in plan_items],
    }
    (out_dir / "frontier.json").write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    validation = {
        "schema_version": 1,
        "generated_utc": inventory["generated_utc"],
        "network_performed": False,
        "checks": {
            "source_files_present": all(path.is_file() for _, path in sources),
            "unique_urls": len(nodes) == len({node["url"] for node in inventory_nodes}),
            "candidate_is_primary_host_page": all(
                node["classification"]["category"] == "public_page" and official_main(node["url"])
                for node in inventory_nodes if node["action"] == "candidate"
            ),
            "batch_limit": len(first_batch) <= batch_size + len(RECOVERY_ALIAS_PAGES),
            "no_fragments_in_canonical_urls": all("#" not in node["url"] for node in inventory_nodes),
            "no_network": True,
        },
        "summary": summary,
    }
    (out_dir / "validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# 官网侧栏正文恢复离线盘点",
        "",
        "本阶段读取保存的 `menu.xml`、`navtree-main.js`、`navtree.js` 文本，未执行 JavaScript、未联网。",
        f"- 侧栏原始菜单行：{len(rows)}；去重 URL：{len(inventory_nodes)}。",
        f"- 公共正文候选：{summary['public_sidebar_pages']}；剔除/复核：{len(inventory_nodes) - summary['public_sidebar_pages']}。",
        f"- 已有本地证据跳过：{summary['action_counts'].get('skip_existing', 0)}；待 prefix-CDX：{len(pending)}。",
        f"- 第一批：{len(first_batch)} 页；后续批次：{summary['deferred_pages']} 页。",
        "- 排除账户、支付、Armory、论坛/社交、在线交互、静态资源、安装包及大媒体文件。",
        "- `/index.xml`、`/info/index.xml`与主栏目分别列为 exact alias/prefix 计划；晚于锚点的 2008 捕获只作 supplement。",
        "",
        f"分类：`{json.dumps(summary['category_counts'], ensure_ascii=False, sort_keys=True)}`",
        f"栏目：`{json.dumps(summary['pending_by_sidebar_category'], ensure_ascii=False, sort_keys=True)}`",
        "",
        "输出：`sidebar-inventory.json`、`recovery-plan.json`、`frontier.json`、`validation.json`。",
    ]
    (out_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return {"inventory": inventory, "plan": plan, "summary": summary}


def _recovery_read_limited(stream, limit: int = MAX_CDX_BYTES) -> tuple[bytes, bool]:
    body = stream.read(limit + 1)
    return body[:limit], len(body) > limit


def query_recovery_prefixes(
    out_dir: Path,
    *,
    timeout_seconds: float,
    deadline_seconds: float,
    max_queries: int,
    prefix_offset: int = 0,
) -> dict[str, Any]:
    """Perform bounded prefix and alias CDX queries, preserving raw evidence."""
    plan = load_json(out_dir / "recovery-plan.json")
    specs_all = list(plan.get("prefix_queries", []))
    specs = specs_all[prefix_offset:prefix_offset + max_queries]
    raw_dir = out_dir / "prefix-cdx"
    raw_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    results: list[dict[str, Any]] = []
    consecutive_failures = 0
    stop_reason: str | None = None
    for attempt, spec in enumerate(specs, start=1):
        if time.monotonic() - started >= deadline_seconds:
            stop_reason = "deadline"
            break
        raw_url = str(spec["url"])
        match_type = str(spec.get("match_type") or "prefix")
        # The CDX ``matchType=prefix`` form already denotes descendants.  An
        # appended ``/*`` is accepted by some shards but returns the null-row
        # placeholder on others; preserve that first response as evidence and
        # use the canonical prefix form for the bounded follow-up.
        query_value = raw_url if match_type == "prefix" else raw_url
        params = [
            ("url", query_value),
            ("matchType", match_type),
            ("output", "json"),
            ("fl", "timestamp,original,statuscode,digest,length,mimetype"),
            ("filter", "statuscode:200"),
            ("from", RECOVERY_QUERY_FROM),
            ("to", RECOVERY_QUERY_TO),
            ("limit", "20000"),
        ]
        # Do not request ``showNumPages`` here.  The Archive may return a
        # 102-byte null-row pagination placeholder instead of CDX rows when
        # this flag is combined with a prefix query.  We need the uncollapsed
        # rows themselves so selection can choose the latest <= anchor row.
        request_url = "https://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode(params)
        # Include the bounded-query revision and date window in the filename;
        # this keeps both earlier null-row probes and this canonical retry as
        # independently auditable raw evidence.
        query_signature = (
            f"recovery-prefix-v2|{spec.get('label')}|{query_value}|"
            f"from={RECOVERY_QUERY_FROM}|to={RECOVERY_QUERY_TO}|match={match_type}|pagination=rows-v1"
        )
        stem = f"{attempt:03d}-{sha256(query_signature.encode('utf-8'))[:16]}"
        raw_path = raw_dir / f"{stem}.json"
        meta_path = raw_dir / f"{stem}.meta.json"
        result: dict[str, Any] = {
            "attempt": attempt,
            "label": spec.get("label"),
            "query_url": raw_url,
            "query_pattern": query_value,
            "match_type": match_type,
            "request_url": request_url,
            "requested_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "status": None,
            "final_url": None,
            "response_headers": {},
            "body_bytes": 0,
            "body_sha256": None,
            "truncated": False,
            "error": None,
        }
        body = b""
        try:
            request = urllib.request.Request(
                request_url,
                headers={"Accept": "application/json", "Accept-Encoding": "identity", "User-Agent": "WOW-Encyclopedia-site-recovery/1.0"},
                method="GET",
            )
            with urllib.request.urlopen(request, timeout=min(timeout_seconds, 30.0)) as response:
                body, truncated = _recovery_read_limited(response)
                result["status"] = int(response.status)
                result["final_url"] = response.geturl()
                result["response_headers"] = {str(key): str(value) for key, value in response.headers.items()}
                result["truncated"] = truncated
        except urllib.error.HTTPError as exc:
            result["status"] = int(exc.code)
            result["final_url"] = exc.geturl()
            result["response_headers"] = {str(key): str(value) for key, value in exc.headers.items()}
            try:
                body, truncated = _recovery_read_limited(exc)
                result["truncated"] = truncated
            except Exception as body_exc:
                result["error"] = f"http_error_body:{type(body_exc).__name__}:{body_exc}"
        except Exception as exc:
            result["error"] = f"{type(exc).__name__}:{exc}"
        raw_path.write_bytes(body)
        result["raw_file"] = rel(raw_path)
        result["meta_file"] = rel(meta_path)
        result["body_bytes"] = len(body)
        result["body_sha256"] = sha256(body) if body else None
        result["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        result["duration_seconds"] = round(time.monotonic() - started, 3)
        meta_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        results.append(result)
        status = result.get("status")
        failed = bool(result.get("error")) or status is None or (status is not None and status >= 500)
        if failed:
            consecutive_failures += 1
            if consecutive_failures >= 3:
                stop_reason = "three_consecutive_site_failures"
                break
        else:
            consecutive_failures = 0
    if stop_reason is None:
        stop_reason = "plan_complete" if len(results) == len(specs) else "no_more_queries"
    summary = {
        "schema_version": 1,
        "network_performed": True,
        "anchor_timestamp": ANCHOR,
        "query_to_timestamp": RECOVERY_QUERY_TO,
        "started_at": dt.datetime.fromtimestamp(time.time() - (time.monotonic() - started), dt.timezone.utc).isoformat(),
        "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "timeout_seconds": min(timeout_seconds, 30.0),
        "deadline_seconds": deadline_seconds,
        "max_queries": max_queries,
        "attempts": len(results),
        "stop_reason": stop_reason,
        "raw_directory": rel(raw_dir),
        "retry_policy": "no automatic prefix-CDX retry; stop after three consecutive failures",
        "http_status_counts": {str(status): sum(row.get("status") == status for row in results) for status in sorted({row.get("status") for row in results}, key=lambda value: str(value))},
        "errors": [{"label": row.get("label"), "query_url": row.get("query_url"), "error": row.get("error"), "status": row.get("status")} for row in results if row.get("error") or row.get("status") not in {200, 404}],
    }
    (out_dir / "prefix-cdx-query-results.json").write_text(json.dumps({"schema_version": 1, "results": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "prefix-cdx-query-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def select_recovery_prefix_cdx(out_dir: Path, batch: int = 1) -> dict[str, Any]:
    """Select primary <=anchor rows and separately label 2008 supplements."""
    plan = load_json(out_dir / "recovery-plan.json")
    raw_paths = sorted((out_dir / "prefix-cdx").glob("*.json")) if (out_dir / "prefix-cdx").is_dir() else []
    raw_paths = [path for path in raw_paths if not path.name.endswith(".meta.json")]
    records, source_errors = load_cdx_records(raw_paths)
    by_identity: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for record in records:
        # Prefix rows commonly carry :80, an HTTPS scheme, or a trailing
        # slash even when the sidebar literal does not.  Use the recovery
        # alias identity rather than the exact-CDX identity here.
        identity = _recovery_identity(str(record.get("original") or ""))
        if identity:
            by_identity.setdefault(identity, []).append(record)
    selected: list[dict[str, Any]] = []
    supplements: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    # ``batch=0`` is an explicit finite all-candidate selection.  It is
    # useful after the bounded prefix sweep: the selected plan can then be
    # split into independent downloader shards without re-reading or
    # re-querying CDX.  Positive values retain the historical batch view.
    batch_items = (
        list(plan.get("items", []))
        if batch == 0
        else [item for item in plan.get("items", []) if item.get("batch") == batch]
    )
    for item in batch_items:
        aliases = _recovery_identity_aliases(str(item.get("original") or ""))
        matches = [record for alias in aliases for record in by_identity.get(alias, []) if record.get("statuscode") == "200"]
        unique: dict[tuple[str, str], dict[str, Any]] = {(str(r.get("timestamp")), str(r.get("original"))): r for r in matches}
        matches = list(unique.values())
        # Keep the reconstruction baseline within calendar year 2008.  Older
        # status-200 rows remain useful historical comparisons but must not
        # silently satisfy a 2008 recovery candidate (notably the 2007 root).
        primary = [
            record for record in matches
            if str(record.get("timestamp", ""))[:4] == "2008"
            and str(record.get("timestamp", "")) <= ANCHOR
        ]
        late_2008 = [record for record in matches if ANCHOR < str(record.get("timestamp", "")) <= RECOVERY_QUERY_TO and str(record.get("timestamp", ""))[:4] == "2008"]
        older = [record for record in matches if str(record.get("timestamp", ""))[:4] < "2008"]
        if primary:
            chosen = max(primary, key=lambda record: str(record.get("timestamp", "")))
            bucket = "primary_at_or_before_anchor"
        elif late_2008:
            chosen = min(late_2008, key=lambda record: str(record.get("timestamp", "")))
            bucket = "supplement_2008_after_anchor"
        elif older:
            chosen = max(older, key=lambda record: str(record.get("timestamp", "")))
            bucket = "historical_pre2008"
        else:
            missing.append({"original": item["original"], "reason": "no_status_200_cdx_in_query_window", "candidate_rows": len(matches)})
            continue
        selected_item = dict(item)
        selected_item.update({
            "timestamp": chosen["timestamp"],
            "requested_timestamp_is_capture_fact": True,
            "selection_status": bucket,
            "selection_bucket": bucket,
            "indexed_capture_timestamp": chosen["timestamp"],
            "cdx_original": chosen.get("original"),
            "cdx_digest": chosen.get("digest"),
            "cdx_length": chosen.get("length"),
            "declared_mime": chosen.get("mimetype"),
            "cdx_source_file": chosen.get("source_file"),
            "cdx_source_row": chosen.get("source_row"),
        })
        if bucket == "primary_at_or_before_anchor":
            selected.append(selected_item)
        else:
            supplements.append(selected_item)
    selected_plan = {
        "schema_version": 1,
        "network_performed": False,
        "anchor_timestamp": ANCHOR,
        "query_to_timestamp": RECOVERY_QUERY_TO,
        "batch": batch,
        "selection_policy": "latest status-200 alias-matched CDX at or before anchor; later 2008 and pre-2008 captures remain supplement-only",
        "source_files": [rel(path) for path in raw_paths],
        "items": selected,
        "supplement_only": supplements,
        "missing": missing,
        "source_errors": source_errors,
    }
    selected_path = out_dir / "wayback-plan-selected.json"
    selected_path.write_text(json.dumps(selected_plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = {
        "schema_version": 1,
        "network_performed": False,
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "anchor_timestamp": ANCHOR,
        "batch": batch,
        "cdx_record_count": len(records),
        "selected_primary_count": len(selected),
        "supplement_only_count": len(supplements),
        "missing_count": len(missing),
        "selected_plan": rel(selected_path),
        "supplements": supplements,
        "missing": missing,
        "source_errors": source_errors,
    }
    (out_dir / "prefix-cdx-selection.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"selected_plan": selected_plan, "selection": result}


def _recovery_manifest_records(backup_dir: Path) -> tuple[Path, dict[tuple[str, str], dict[str, Any]]]:
    manifest_path = backup_dir / "manifest.jsonl"
    records: dict[tuple[str, str], dict[str, Any]] = {}
    if not manifest_path.is_file():
        return manifest_path, records
    for line in manifest_path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if isinstance(record, dict) and record.get("original") and record.get("requested_timestamp"):
            records[(str(record["original"]), str(record["requested_timestamp"]))] = record
    return manifest_path, records


def _recovery_original_from_replay(replay_url: str) -> str | None:
    """Recover the final ORIGINAL URL from a Wayback replay URL.

    ``actual_url`` is intentionally retained as the observed replay URL.  A
    router base, however, must use the original URL after the archive's
    redirect, including its trailing slash.  Keep this parser conservative:
    only the standard replay modifiers are unwrapped and all other values are
    left for the CDX original fallback.
    """
    value = str(replay_url or "")
    # A replay URL has the timestamp and modifier in one path segment, for
    # example ``/web/20080402025125id_/http://...``.  Looking only for
    # ``/id_/`` misses this normal form and can accidentally derive a base
    # from the logical request URL instead of the capture's ORIGINAL link.
    match = re.search(r"/web/\d{14}(?:id_|im_|if_|oe_|js_)?/(https?://.+)$", value, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def _recovery_route_fields(source_url: str) -> dict[str, Any]:
    """Describe local router aliases without changing preserved page bytes."""
    parsed = urllib.parse.urlsplit(source_url)
    path = parsed.path or "/"
    fields: dict[str, Any] = {}
    if path == "/index.xml":
        fields["derived_route"] = "/index.xml"
        fields["route_aliases"] = ["/"]
    elif path == "/":
        fields["derived_route"] = "/index.html"
        fields["route_aliases"] = ["/"]
    elif path.endswith("/"):
        fields["derived_route"] = path + "index.html"
        fields["route_aliases"] = [path, path.rstrip("/")]
    elif Path(path).suffix == "":
        fields["derived_route"] = path + "/index.html"
        fields["route_aliases"] = [path, path + "/"]
    return fields


def write_recovery_validated_map(out_dir: Path, selected_plan_path: Path, backup_dir: Path) -> dict[str, Any]:
    """Verify page entities and export real bytes to the recovery source tree."""
    selected_plan = load_json(selected_plan_path)
    previous_map: dict[str, Any] = {}
    previous_path = out_dir / "validated-url-map.json"
    if previous_path.is_file():
        try:
            loaded = load_json(previous_path)
            if isinstance(loaded, dict):
                previous_map = loaded
        except (OSError, ValueError):
            previous_map = {}
    manifest_path, records = _recovery_manifest_records(backup_dir)
    target_root = ROOT / "offline" / "source-entities-pages-recovery"
    target_root.mkdir(parents=True, exist_ok=True)
    files: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    total_bytes = 0
    pending: list[tuple[dict[str, Any], dict[str, Any], bytes, zipfile.ZipInfo]] = []
    for item in selected_plan.get("items", []):
        # CDX original may intentionally use https or preserve a trailing
        # slash while the sidebar's logical URL uses the historical link
        # spelling.  Fetch/manifest lookup uses the exact plan original;
        # exported routing identity uses the separately preserved logical URL.
        plan_original = str(item.get("original") or "")
        logical_original = str(item.get("logical_url") or plan_original)
        key = (plan_original, str(item.get("timestamp") or ""))
        record = records.get(key)
        if not record or record.get("status") != "success":
            errors.append({"logical_url": logical_original, "manifest_original": plan_original, "requested_timestamp": key[1], "error_class": "missing_success_manifest"})
            continue
        try:
            body, zip_info = _manifest_body_and_info(record, manifest_path)
        except (OSError, KeyError, zipfile.BadZipFile) as exc:
            errors.append({"logical_url": logical_original, "manifest_original": plan_original, "requested_timestamp": key[1], "error_class": f"body_read_error:{type(exc).__name__}"})
            continue
        response_headers = record.get("response_headers") or {}
        content_type = str(response_headers.get("Content-Type") or response_headers.get("content-type") or "")
        content_type_full = content_type or str(item.get("declared_mime") or "")
        media_type = content_type_full.split(";", 1)[0].strip()
        validation_errors = _entity_validation_errors(item, record, body, media_type, out_dir)
        computed_sha = sha256(body)
        computed_crc = zlib.crc32(body) & 0xFFFFFFFF
        if record.get("sha256") and computed_sha != str(record["sha256"]):
            validation_errors.append("sha256_mismatch")
        if record.get("content_length") is not None and len(body) != int(record["content_length"]):
            validation_errors.append("content_length_mismatch")
        if computed_crc != int(zip_info.CRC):
            validation_errors.append("zip_crc_mismatch")
        kind = _body_kind(logical_original, media_type, body)
        if kind == "xml":
            try:
                ET.fromstring(body)
            except ET.ParseError as exc:
                validation_errors.append(f"xml_parse_error:{exc}")
        if not body:
            validation_errors.append("empty_body")
        if validation_errors:
            errors.append({"logical_url": logical_original, "manifest_original": plan_original, "requested_timestamp": key[1], "error_class": ",".join(validation_errors), "sha256": computed_sha})
            continue
        total_bytes += len(body)
        # MIME is derived per response.  Do not carry the last loop iteration's
        # value into a mixed HTML/XML batch.
        pending.append((item, record, body, zip_info))
    usage = shutil.disk_usage(ROOT)
    if total_bytes > MAX_WORKSPACE_BYTES or usage.free < MIN_FREE_BYTES + RESERVE_BYTES + total_bytes:
        raise RuntimeError(f"recovery export budget guard failed: bytes={total_bytes} free={usage.free}")
    for item, record, body, zip_info in pending:
        plan_original = str(item["original"])
        original = str(item.get("logical_url") or plan_original)
        computed_sha = sha256(body)
        destination = target_root / f"{computed_sha}.bin"
        if destination.exists():
            if destination.read_bytes() != body:
                raise RuntimeError(f"recovery export collision with different bytes: {destination}")
        else:
            temporary = destination.with_suffix(".partial")
            temporary.write_bytes(body)
            temporary.replace(destination)
        attempts = record.get("attempts") or []
        response_headers = record.get("response_headers") or {}
        content_type_full = str(
            response_headers.get("Content-Type")
            or response_headers.get("content-type")
            or item.get("declared_mime")
            or ""
        )
        media_type = content_type_full.split(";", 1)[0].strip()
        redirect_chain = [str(record.get("requested_url"))] if record.get("requested_url") else []
        redirect_chain.extend(str(attempt.get("final_url")) for attempt in attempts if attempt.get("final_url"))
        actual_timestamp = timestamp_digits(record.get("actual_timestamp"))
        cdx_original = str(item.get("cdx_original") or original)
        replay_url = str(record.get("actual_url") or "")
        source_base_url = _recovery_original_from_replay(replay_url) or cdx_original
        route_fields = _recovery_route_fields(source_base_url)
        files.append({
            "logical_url": original,
            "source_url": cdx_original,
            "capture_original": cdx_original,
            "manifest_original": record.get("original") or plan_original,
            "requested_url": record.get("requested_url"),
            "actual_url": replay_url or None,
            "source_base_url": source_base_url,
            "base_url": source_base_url,
            "local_path": rel(destination),
            "mime": content_type_full or None,
            "response_content_type": content_type_full or None,
            "media_type": media_type or None,
            "kind": _body_kind(original, media_type, body),
            "role": item.get("role"),
            "categories": item.get("categories", []),
            "labels": item.get("labels", []),
            "sha256": computed_sha,
            "content_length": len(body),
            "actual_timestamp": actual_timestamp,
            "entity_observed_capture_timestamp": actual_timestamp,
            "indexed_capture_timestamp": item.get("indexed_capture_timestamp") or item.get("timestamp"),
            "timestamp_drift": bool(actual_timestamp and item.get("timestamp") and actual_timestamp != item.get("timestamp")),
            "cdx_digest": item.get("cdx_digest"),
            "source_parent_urls": [parent.get("url") for parent in item.get("parents", []) if parent.get("url")],
            "manifest": rel(manifest_path),
            "zip_part": record.get("zip_part"),
            "zip_file": rel(backup_dir / str(record.get("zip_part"))) if record.get("zip_part") else None,
            "zip_entry": record.get("zip_entry"),
            "zip_crc32": f"{int(zip_info.CRC):08x}",
            "zip_crc32_computed": f"{zlib.crc32(body) & 0xFFFFFFFF:08x}",
            "redirect_chain": redirect_chain,
            "error_class": None,
            **route_fields,
        })
    # Keep one cumulative map across finite recovery batches.  A batch's
    # selected plan remains the validation scope for its new records, while
    # prior verified records stay addressable for the future router.
    merged_files: dict[tuple[str, str, str], dict[str, Any]] = {}
    for previous in previous_map.get("files", []):
        if isinstance(previous, dict) and previous.get("logical_url") and previous.get("sha256"):
            merged_files[(str(previous.get("logical_url")), str(previous.get("indexed_capture_timestamp") or previous.get("actual_timestamp") or ""), str(previous.get("sha256")))] = previous
    for current in files:
        merged_files[(str(current.get("logical_url")), str(current.get("indexed_capture_timestamp") or current.get("actual_timestamp") or ""), str(current.get("sha256")))] = current
    all_files = list(merged_files.values())
    current_success_keys = {
        (str(current.get("logical_url")), str(current.get("indexed_capture_timestamp") or current.get("actual_timestamp") or ""))
        for current in files
    }
    merged_errors: dict[tuple[str, str], dict[str, Any]] = {}
    for previous_error in previous_map.get("errors", []):
        if isinstance(previous_error, dict) and previous_error.get("logical_url"):
            key = (str(previous_error.get("logical_url")), str(previous_error.get("requested_timestamp") or ""))
            if key not in current_success_keys:
                merged_errors[key] = previous_error
    for current_error in errors:
        if isinstance(current_error, dict) and current_error.get("logical_url"):
            key = (str(current_error.get("logical_url")), str(current_error.get("requested_timestamp") or ""))
            merged_errors[key] = current_error
    result = {
        "schema_version": 1,
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "network_performed": False,
        "status": "complete" if selected_plan.get("items") and not errors and len(files) == len(selected_plan.get("items", [])) else "partial",
        "active_scope": "sidebar_public_pages_2008",
        "files": all_files,
        "errors": list(merged_errors.values()),
        "selected_plan": rel(selected_plan_path),
        "backup_dir": rel(backup_dir),
        "export_root": rel(target_root),
        "exported_bytes": sum(int(item.get("content_length") or 0) for item in all_files),
        "current_batch_files": len(files),
        "current_batch_errors": len(errors),
        "cumulative_files": len(all_files),
        "interface": {
            "source_url": "selected CDX original URL",
            "capture_original": "same CDX original, preserving scheme/trailing slash",
            "actual_url": "final Wayback replay URL from manifest",
            "source_base_url": "original URL unwrapped from final Wayback actual_url; CDX original fallback",
            "base_url": "same source_base_url, retaining final original trailing slash",
            "mime": "full response Content-Type including charset",
            "zip_file": "workspace-relative backup ZIP path",
            "derived_route": "optional local router path for directory-like entities",
            "route_aliases": "optional logical aliases such as / for index.xml",
            "local_path": "real exported entity file under offline/source-entities-pages-recovery",
        },
    }
    (out_dir / "validated-url-map.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def recovery_fetch(out_dir: Path, *, deadline_seconds: float, max_requests: int) -> dict[str, Any]:
    selected_path = out_dir / "wayback-plan-selected.json"
    if not selected_path.is_file():
        raise RuntimeError("recovery selected plan is missing; run --site-recovery query-prefix first")
    selected = load_json(selected_path)
    items = selected.get("items", [])
    invalid = [item for item in items if item.get("requested_timestamp_is_capture_fact") is not True or not re.fullmatch(r"\d{14}", str(item.get("timestamp") or ""))]
    if invalid:
        raise RuntimeError(f"recovery selected plan has {len(invalid)} items without exact CDX capture timestamps")
    if len(items) > max_requests:
        raise RuntimeError(f"recovery selected entity count {len(items)} exceeds max requests {max_requests}")
    backup_dir = ROOT / "backups" / "site-recovery-2008"
    command = [
        sys.executable,
        str(ROOT / "tools" / "wayback_backup.py"),
        "--plan", str(selected_path),
        "--out", str(backup_dir),
        "--budget-root", str(ROOT),
        "--max-bytes", str(MAX_WORKSPACE_BYTES),
        "--min-free-bytes", str(MIN_FREE_BYTES),
        "--reserve-bytes", str(RESERVE_BYTES),
        "--max-object-bytes", str(MAX_OBJECT_BYTES),
        "--max-requests", str(max_requests),
        "--deadline-seconds", str(deadline_seconds),
    ]
    (out_dir / "fetch-command.json").write_text(json.dumps({"command": command, "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "max_entities": len(items), "max_requests": max_requests, "deadline_seconds": deadline_seconds}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    completed = subprocess.run(command, cwd=ROOT, check=False)
    validated = write_recovery_validated_map(out_dir, selected_path, backup_dir)
    return {"fetch_returncode": completed.returncode, "validated": validated}


def recovery_main(args: argparse.Namespace) -> int:
    out_dir = args.recovery_out
    if args.site_recovery == "offline":
        result = build_recovery_inventory(out_dir, args.recovery_batch_size)
        print(json.dumps({"network_performed": False, "output": rel(out_dir), "summary": result["summary"]}, ensure_ascii=False, sort_keys=True))
        return 0
    # Every network mode rebuilds only the recovery inventory; it never writes
    # research/site-expansion-2008 or its CDX evidence.
    build_recovery_inventory(out_dir, args.recovery_batch_size)
    if args.site_recovery == "query-prefix":
        query = query_recovery_prefixes(
            out_dir,
            timeout_seconds=args.recovery_timeout_seconds,
            deadline_seconds=args.recovery_deadline_seconds,
            max_queries=args.recovery_max_queries,
            prefix_offset=args.recovery_prefix_offset,
        )
        selection = select_recovery_prefix_cdx(out_dir, batch=args.recovery_batch)
        print(json.dumps({"network_performed": True, "query": query, "selection": selection["selection"]}, ensure_ascii=False, sort_keys=True))
        return 0 if query.get("stop_reason") == "plan_complete" else 1
    selection = select_recovery_prefix_cdx(out_dir, batch=args.recovery_batch)
    if not selection["selected_plan"].get("items"):
        print(json.dumps({"network_performed": False, "error": "no primary selected items; see prefix-cdx-selection.json"}, ensure_ascii=False))
        return 3
    fetched = recovery_fetch(out_dir, deadline_seconds=args.recovery_entity_deadline_seconds, max_requests=args.recovery_max_requests)
    print(json.dumps({"network_performed": True, "fetch_returncode": fetched["fetch_returncode"], "validated_map": rel(out_dir / "validated-url-map.json"), "validated_files": len(fetched["validated"]["files"]), "validation_errors": len(fetched["validated"]["errors"])}, ensure_ascii=False, sort_keys=True))
    return int(fetched["fetch_returncode"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="build local inventory; this is the default")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--query-cdx", action="store_true", help="query bounded exact CDX rows, preserve raw responses, then select; requires --allow-network")
    mode.add_argument("--select", action="store_true", help="select exact CDX rows from saved responses; never performs network I/O")
    mode.add_argument("--fetch", action="store_true", help="fetch a previously selected plan through wayback_backup.py")
    parser.add_argument("--cdx", action="append", default=[], type=Path, help="saved CDX response file; repeatable with --select")
    parser.add_argument("--cdx-dir", type=Path, help="directory of saved CDX response files for --select")
    parser.add_argument("--allow-network", action="store_true", help="required with --fetch; never implied by --offline")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--max-requests", type=int, default=MAX_REQUESTS)
    parser.add_argument("--deadline-seconds", type=float, default=600.0, help="bounded downloader deadline for --fetch")
    parser.add_argument("--cdx-timeout-seconds", type=float, default=30.0, help="per-CDX request timeout, capped at 30 seconds")
    parser.add_argument("--cdx-deadline-seconds", type=float, default=600.0, help="bounded exact-CDX query deadline")
    parser.add_argument("--selected-plan", type=Path, help="selected plan path for --fetch")
    parser.add_argument("--site-recovery", choices=("offline", "query-prefix", "fetch"), help="run the separate sidebar page recovery workflow")
    parser.add_argument("--recovery-out", type=Path, default=RECOVERY_DEFAULT_OUT, help="sidebar recovery output directory")
    parser.add_argument("--recovery-batch", type=int, default=1, help="sidebar recovery batch number; 0 selects all finite candidates")
    parser.add_argument("--recovery-batch-size", type=int, default=RECOVERY_BATCH_ENTITIES, help="pages in each sidebar recovery batch")
    parser.add_argument("--recovery-max-queries", type=int, default=len(RECOVERY_PREFIXES) * 2 + len(RECOVERY_EXACT_ALIASES), help="maximum prefix/alias CDX requests")
    parser.add_argument("--recovery-prefix-offset", type=int, default=0, help="skip this many prefix/alias specs while preserving prior raw CDX evidence")
    parser.add_argument("--recovery-max-requests", type=int, default=150, help="maximum downloader requests for one sidebar batch")
    parser.add_argument("--recovery-timeout-seconds", type=float, default=25.0, help="sidebar CDX request timeout, capped at 30 seconds")
    parser.add_argument("--recovery-deadline-seconds", type=float, default=600.0, help="sidebar prefix-CDX deadline")
    parser.add_argument("--recovery-entity-deadline-seconds", type=float, default=600.0, help="sidebar entity downloader deadline")
    args = parser.parse_args(argv)
    if args.site_recovery:
        if args.recovery_batch < 0 or args.recovery_batch_size <= 0 or args.recovery_max_queries <= 0 or args.recovery_max_requests <= 0 or args.recovery_prefix_offset < 0:
            parser.error("recovery batch must be zero or positive; query and request limits must be positive")
        if args.recovery_timeout_seconds <= 0 or args.recovery_deadline_seconds <= 0 or args.recovery_entity_deadline_seconds <= 0:
            parser.error("recovery time limits must be positive")
        if args.site_recovery != "offline" and not args.allow_network:
            parser.error("networked site recovery requires explicit --allow-network")
        if args.site_recovery == "offline" and args.allow_network:
            parser.error("offline site recovery must not pass --allow-network")
        return recovery_main(args)
    if args.max_requests <= 0:
        parser.error("--max-requests must be positive")
    if args.fetch and not args.allow_network:
        parser.error("--fetch requires explicit --allow-network")
    if (args.select or args.offline) and args.allow_network and not args.query_cdx and not args.fetch:
        parser.error("--select/--offline are offline-only; do not pass --allow-network")
    if args.query_cdx and not args.allow_network:
        parser.error("--query-cdx requires explicit --allow-network")
    if args.deadline_seconds <= 0:
        parser.error("--deadline-seconds must be positive")
    if args.cdx_timeout_seconds <= 0 or args.cdx_deadline_seconds <= 0:
        parser.error("CDX timeout and deadline must be positive")
    result = build_inventory(args.out, args.max_requests)
    if args.query_cdx:
        query_summary = query_exact_cdx(
            args.out,
            max_queries=args.max_requests,
            timeout_seconds=args.cdx_timeout_seconds,
            deadline_seconds=args.cdx_deadline_seconds,
        )
        raw_paths = [
            path for path in sorted((args.out / "cdx").glob("*.json"))
            if not path.name.endswith(".meta.json")
        ]
        selection = select_exact_cdx(args.out, raw_paths)
        print(json.dumps({
            "network_performed": True,
            "query": query_summary,
            "selection": selection["selection_report"],
        }, ensure_ascii=False, sort_keys=True))
        return 0 if query_summary.get("stop_reason") == "plan_complete" else 1
    if args.select:
        cdx_paths: list[Path] = []
        for path in args.cdx:
            cdx_paths.append(path if path.is_absolute() else ROOT / path)
        if args.cdx_dir:
            cdx_dir = args.cdx_dir if args.cdx_dir.is_absolute() else ROOT / args.cdx_dir
            if not cdx_dir.is_dir():
                parser.error(f"--cdx-dir is not a directory: {cdx_dir}")
            cdx_paths.extend(
                path for path in sorted(cdx_dir.rglob("*"))
                if path.is_file() and path.suffix.casefold() not in {".meta", ".pyc"}
            )
        unique_paths: list[Path] = []
        seen_paths: set[str] = set()
        for path in cdx_paths:
            key = str(path.resolve()).casefold()
            if key not in seen_paths:
                seen_paths.add(key)
                unique_paths.append(path)
        if not unique_paths:
            parser.error("--select requires --cdx FILE or --cdx-dir DIR")
        selection = select_exact_cdx(args.out, unique_paths)
        print(json.dumps({"network_performed": False, **selection["selection_report"]}, ensure_ascii=False, sort_keys=True))
        return 0
    if args.fetch:
        plan_path = args.selected_plan or (args.out / "wayback-plan-selected.json")
        if not plan_path.is_absolute():
            plan_path = ROOT / plan_path
        if not plan_path.is_file():
            print(f"refusing fetch: selected plan is missing: {rel(plan_path)}; run --select first", file=sys.stderr)
            return 3
        selected_plan = load_json(plan_path)
        items = selected_plan.get("items", [])
        invalid = [
            item for item in items
            if item.get("requested_timestamp_is_capture_fact") is not True
            or not re.fullmatch(r"\d{14}", str(item.get("timestamp") or ""))
        ]
        if invalid:
            print(f"refusing fetch: {len(invalid)} selected items lack exact-CDX capture timestamps", file=sys.stderr)
            return 3
        if len(items) > args.max_requests:
            print(f"refusing fetch: selected entity count {len(items)} exceeds --max-requests {args.max_requests}", file=sys.stderr)
            return 3
        max_attempt_requests = max(1, len(items) * 2) if items else 0
        command = [
            sys.executable,
            str(ROOT / "tools/wayback_backup.py"),
            "--plan", str(plan_path),
            "--out", str(ROOT / "backups/site-expansion-2008"),
            "--budget-root", str(ROOT),
            "--max-bytes", str(MAX_WORKSPACE_BYTES),
            "--min-free-bytes", str(MIN_FREE_BYTES),
            "--reserve-bytes", str(RESERVE_BYTES),
            "--max-object-bytes", str(MAX_OBJECT_BYTES),
            "--max-requests", str(max_attempt_requests),
            "--deadline-seconds", str(args.deadline_seconds),
        ]
        (args.out / "fetch-command.json").write_text(json.dumps({
            "command": command,
            "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "network_gate": "explicit --allow-network",
            "max_entities": len(items),
            "max_attempt_requests": max_attempt_requests,
            "deadline_seconds": args.deadline_seconds,
            "archive_flows": MAX_ARCHIVE_FLOWS,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        completed = subprocess.run(command, cwd=ROOT, check=False)
        try:
            validated = write_validated_url_map(args.out, plan_path, ROOT / "backups/site-expansion-2008")
            print(json.dumps({
                "network_performed": True,
                "fetch_returncode": completed.returncode,
                "validated_map": rel(args.out / "validated-url-map.json"),
                "validated_files": len(validated["files"]),
                "validation_errors": len(validated["errors"]),
            }, ensure_ascii=False, sort_keys=True))
        except OSError as exc:
            print(f"validated-url-map generation failed: {type(exc).__name__}:{exc}", file=sys.stderr)
        return int(completed.returncode)
    print(json.dumps({"network_performed": False, "output": rel(args.out), "summary": result["inventory"]["summary"]}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
