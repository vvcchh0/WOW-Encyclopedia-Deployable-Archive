#!/usr/bin/env python3
"""Offline resource review for the seven newly connected RSS HTML pages.

This script intentionally reads only the selected RSS additions, their raw
payloads, the v10 manifest/provenance, and the seven exported pages. It does
not make network requests and writes only beside this script.
"""

from __future__ import annotations

import hashlib
import html as html_mod
import json
import mimetypes
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urljoin, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SELECTED = ROOT / "research/continuous-recovery-20261015/selected-v10-final-additions.json"
MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v10/build-manifest.json"
PROVENANCE = ROOT / ".scratch/pages-resources-20261015-v10/export-provenance.json"
ADDITIONS_MAP = ROOT / "research/v10-integration/source/v10-additions-source-map.json"
EXPORT_ROOT = ROOT / ".scratch/pages-resources-20261015-v10"
PRIOR_REQUEST_FILES = [
    ROOT / "research/continuous-recovery-20261015/assets5-acceptance.json",
    ROOT / "research/continuous-recovery-20261015/mixed9-acceptance.json",
    ROOT / "research/continuous-recovery-20261015/wrath8-acceptance.json",
    ROOT / "research/continuous-recovery-20261015/rss6-acceptance.json",
    ROOT / "research/continuous-recovery-20261015/rss10-acceptance.json",
    ROOT / "research/continuous-recovery-20261015/network-batch1-acceptance.json",
    ROOT / "research/continuous-recovery-20261015/resource-dedup-acceptance.json",
]


def sha256(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    n = 0
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
            n += len(chunk)
    return h.hexdigest(), n


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def compact(value: str, limit: int = 300) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value if len(value) <= limit else value[: limit - 1] + "…"


def canonical_url(value: str, base: str) -> tuple[str | None, str | None]:
    """Return an exact-origin canonical URL and a skip reason when nonliteral."""
    if value is None:
        return None, "missing"
    raw = html_mod.unescape(str(value)).strip()
    if not raw:
        return None, "empty"
    low = raw.lower()
    if low.startswith(("javascript:", "data:", "mailto:", "tel:", "#")):
        return None, "non_request_scheme_or_fragment"
    if any(token in raw for token in ("${", "}", "document.", "window.", "location", " + ", " +", "+ ")):
        return None, "dynamic_expression"
    try:
        absolute = urljoin(base, raw)
        parts = urlsplit(absolute)
    except ValueError:
        return None, "invalid_url"
    if parts.scheme.lower() not in {"http", "https"} or not parts.netloc:
        return None, "non_http_origin"
    hostname = (parts.hostname or "").lower()
    if not hostname:
        return None, "missing_host"
    port = parts.port
    if port and not ((parts.scheme.lower() == "http" and port == 80) or (parts.scheme.lower() == "https" and port == 443)):
        host = f"{hostname}:{port}"
    else:
        host = hostname
    # Keep path and query exactly after HTML entity decoding, drop only fragment.
    return urlunsplit((parts.scheme.lower(), host, parts.path or "/", parts.query, "")), None


def origin_key(url: str) -> str:
    p = urlsplit(url)
    return p.netloc.lower() + (p.path or "/") + (("?" + p.query) if p.query else "")


def identity_parts(url: str) -> dict[str, str]:
    p = urlsplit(url)
    hostname = (p.hostname or "").lower()
    port = p.port
    if port and not ((p.scheme.lower() == "http" and port == 80) or (p.scheme.lower() == "https" and port == 443)):
        host = f"{hostname}:{port}"
    else:
        host = hostname
    return {
        "scheme": p.scheme.lower(),
        "host": host,
        "path": p.path or "/",
        "query": p.query,
    }


def compare_source_identity(requested_url: str, source_base_url: str | None) -> tuple[bool | None, list[str], dict[str, str] | None, dict[str, str] | None]:
    if not source_base_url:
        return None, ["source_base_url_missing"], identity_parts(requested_url), None
    requested = identity_parts(requested_url)
    source = identity_parts(source_base_url)
    mismatches = [key for key in ("scheme", "host", "path", "query") if requested[key] != source[key]]
    return not mismatches, mismatches, requested, source


def raw_line(text: str, line: int) -> str:
    lines = text.splitlines()
    return compact(lines[line - 1] if 0 < line <= len(lines) else "")


class ResourceParser(HTMLParser):
    """Collect literal request-bearing markup with source line evidence."""

    def __init__(self, text: str, base_url: str, source_name: str) -> None:
        super().__init__(convert_charrefs=True)
        self.text = text
        self.base_url = base_url
        self.source_name = source_name
        self.records: list[dict[str, Any]] = []
        self.interactions: list[dict[str, Any]] = []
        self.stack: list[str] = []
        self._style_depth = 0
        self._style_chunks: list[tuple[str, int]] = []
        self._script_depth = 0
        self._script_chunks: list[tuple[str, int]] = []

    def _attrs(self, attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {str(k).lower(): (v or "") for k, v in attrs}

    def _context(self, tag: str, attrs: dict[str, str], line: int, value: str, attribute: str, kind: str, purpose: str, reason: str) -> None:
        resolved, skip = canonical_url(value, self.base_url)
        record = {
            "source": self.source_name,
            "line": line,
            "tag": tag,
            "attribute": attribute,
            "raw_value": value,
            "resolved_url": resolved,
            "skip_reason": skip,
            "context_kind": kind,
            "resource_purpose": purpose,
            "purpose_reason": reason,
            "parent_stack": self.stack[-6:],
            "id": attrs.get("id", ""),
            "class": attrs.get("class", ""),
            "alt": attrs.get("alt", ""),
            "width": attrs.get("width", ""),
            "height": attrs.get("height", ""),
            "evidence": raw_line(self.text, line),
        }
        self.records.append(record)

    def _img_purpose(self, attrs: dict[str, str]) -> tuple[str, str]:
        hint = " ".join((attrs.get(k, "") for k in ("id", "class", "alt", "title"))).lower()
        src = attrs.get("src", "").lower()
        size = f"{attrs.get('width','')}x{attrs.get('height','')}"
        if "/smallcaps/" in src:
            return "layout_or_navigation_image", f"32px drop-cap asset under /smallcaps/; repeated article-initial markup, size={size}"
        if "news-sc2" in src:
            return "navigation_or_third_party_promo", "article markup links image to external StarCraft II promotion"
        layout_words = ("spacer", "pixel", "border", "bg", "background", "header", "footer", "nav", "menu", "icon", "arrow", "bullet", "logo", "button")
        if (attrs.get("width") in {"1", "0"} or attrs.get("height") in {"1", "0"}) and ("layout" in src or "pixel" in src or "spacer" in src):
            return "layout_spacer_or_border", f"markup size {size} and layout/pixel path"
        if any(w in hint for w in layout_words) or any(w in src for w in layout_words):
            return "layout_or_navigation_image", f"markup/path layout hint; class/id/alt={compact(hint, 120)}"
        if attrs.get("alt") or re.search(r"\.(?:jpe?g|png|gif|webp)(?:$|[?#])", src, re.I):
            return "body_illustration_candidate", f"img in document body with alt={compact(attrs.get('alt',''), 80)!r}, size={size}"
        return "image_reference_unknown", f"img markup without sufficient semantic label; size={size}"

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attrs = self._attrs(attrs_list)
        line = self.getpos()[0]
        if tag == "img" and "src" in attrs:
            purpose, reason = self._img_purpose(attrs)
            self._context(tag, attrs, line, attrs["src"], "src", "markup", purpose, reason)
        elif tag == "script" and "src" in attrs:
            self._context(tag, attrs, line, attrs["src"], "src", "markup", "script_dependency", "static script src attribute")
        elif tag == "link" and "href" in attrs:
            rel = attrs.get("rel", "").lower()
            purpose = "shared_stylesheet" if "stylesheet" in rel else "metadata_or_navigation_link"
            self._context(tag, attrs, line, attrs["href"], "href", "markup", purpose, f"link rel={rel!r}")
        elif tag in {"object", "embed", "iframe", "video", "audio", "source"}:
            attr = "data" if tag == "object" and "data" in attrs else "src"
            if attr in attrs:
                self._context(tag, attrs, line, attrs[attr], attr, "markup", "embedded_or_media", f"{tag} request attribute")
        elif tag in {"body", "table", "tr", "td", "th", "div", "span"} and "background" in attrs:
            self._context(tag, attrs, line, attrs["background"], "background", "markup", "layout_or_background_image", f"legacy {tag}[background] attribute")
        if tag == "a" and "href" in attrs:
            resolved, skip = canonical_url(attrs["href"], self.base_url)
            self.interactions.append({
                "kind": "navigation_anchor",
                "line": line,
                "raw_value": attrs["href"],
                "resolved_url": resolved,
                "skip_reason": skip,
                "text_hint": compact(attrs.get("title", ""), 120),
                "evidence": raw_line(self.text, line),
            })
        if tag == "form":
            self.interactions.append({"kind": "form", "line": line, "action": attrs.get("action", ""), "method": attrs.get("method", "get"), "evidence": raw_line(self.text, line)})
        event_attrs = [k for k in attrs if k.lower().startswith("on")]
        if event_attrs:
            self.interactions.append({"kind": "inline_event_handler", "line": line, "attributes": event_attrs, "evidence": raw_line(self.text, line)})
        if tag == "style":
            self._style_depth += 1
        if "style" in attrs:
            self._parse_css_chunks([(attrs["style"], line)])
        if tag == "script":
            self._script_depth += 1
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.stack.append(tag)

    def handle_startendtag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs_list)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "style" and self._style_depth:
            self._style_depth -= 1
            self._parse_css_chunks(self._style_chunks)
            self._style_chunks = []
        if tag == "script" and self._script_depth:
            self._script_depth -= 1
            self._parse_script_literals(self._script_chunks)
            self._script_chunks = []
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data: str) -> None:
        line = self.getpos()[0]
        if self._style_depth:
            self._style_chunks.append((data, line))
        if self._script_depth:
            self._script_chunks.append((data, line))

    def _parse_css_chunks(self, chunks: list[tuple[str, int]]) -> None:
        css = "".join(x[0] for x in chunks)
        line0 = chunks[0][1] if chunks else 1
        for m in re.finditer(r"url\(\s*(['\"]?)(.*?)\1\s*\)", css, re.I | re.S):
            value = m.group(2).strip()
            line = line0 + css[: m.start()].count("\n")
            self._context("style", {}, line, value, "url()", "css", "css_background_or_import_asset", "literal CSS url() in inline style block")
        for m in re.finditer(r"@import\s+(?:url\(\s*)?['\"]([^'\"]+)['\"]", css, re.I):
            value = m.group(1).strip()
            line = line0 + css[: m.start()].count("\n")
            self._context("style", {}, line, value, "@import", "css", "shared_stylesheet", "literal CSS @import in inline style block")

    def _parse_script_literals(self, chunks: list[tuple[str, int]]) -> None:
        # Record only clear literal URL strings in static script text. Dynamic
        # expressions are kept as interaction evidence elsewhere and are never
        # promoted to request candidates.
        script = "".join(x[0] for x in chunks)
        line0 = chunks[0][1] if chunks else 1
        for m in re.finditer(r"(?:src|href)\s*=\s*['\"](\/[^'\"]+)['\"]", script, re.I):
            value = m.group(1)
            line = line0 + script[: m.start()].count("\n")
            self._context("script", {}, line, value, "literal-src-or-href", "script", "script_literal_reference", "literal path in inline script")


def find_record(records: Iterable[dict[str, Any]], predicate) -> dict[str, Any] | None:
    return next((x for x in records if predicate(x)), None)


def mime_for(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or "application/octet-stream"


def byte_signature_mime(path: Path) -> str | None:
    head = path.read_bytes()[:16]
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if head.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if head.startswith(b"RIFF") and b"WEBP" in head:
        return "image/webp"
    return None


def prior_request_file_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in PRIOR_REQUEST_FILES:
        if not path.exists():
            records.append({"path": str(path.relative_to(ROOT)).replace("\\", "/"), "exists": False, "sha256": None})
            continue
        digest, length = sha256(path)
        records.append({"path": str(path.relative_to(ROOT)).replace("\\", "/"), "exists": True, "bytes": length, "sha256": digest})
    return records


def prior_request_for_url(url: str, file_records: list[dict[str, Any]]) -> dict[str, Any]:
    """Use only the explicitly named old acceptance ledgers; absence is not a negative claim."""
    candidates = {url}
    if url.startswith("http://"):
        candidates.add("https://" + url[len("http://"):])
    elif url.startswith("https://"):
        candidates.add("http://" + url[len("https://"):])
    hits: list[dict[str, str]] = []
    for record in file_records:
        if not record.get("exists"):
            continue
        path = ROOT / record["path"]
        text = path.read_text(encoding="utf-8", errors="replace")
        matched = sorted(value for value in candidates if value in text)
        if matched:
            hits.append({"path": record["path"], "matched_urls": matched})
    if hits:
        return {
            "status": "evidence_hit",
            "checked_scope": "explicit acceptance/request ledger files only",
            "evidence": hits,
            "absence_claim": False,
        }
    return {
        "status": "not_checked",
        "checked_scope": "explicit acceptance/request ledger files only",
        "checked_files": [record["path"] for record in file_records if record.get("exists")],
        "reason": "No exact full URL hit in the bounded ledger set; absence is not interpreted as no prior request.",
        "absence_claim": False,
    }


def classify_status(url: str, manifest: dict[str, Any], files_by_route: dict[str, dict[str, Any]], route_aliases: dict[str, str], export_root: Path) -> dict[str, Any]:
    key = origin_key(url)
    mapped_route = manifest.get("origin_index", {}).get(key)
    alias_target = route_aliases.get(key) or route_aliases.get(mapped_route or "")
    route = mapped_route or alias_target
    row = files_by_route.get(route or "")
    result: dict[str, Any] = {
        "origin_index_key": key,
        "mapped_route": mapped_route,
        "alias_target": alias_target,
        "status": "not_mapped",
        "local_path": None,
        "local_length": None,
        "local_sha256": None,
        "local_mime": None,
        "source_base_url": None,
        "source_identity_match": None,
        "identity_mismatch_fields": [],
        "requested_identity": identity_parts(url),
        "source_identity": None,
    }
    if not route:
        return result
    if row:
        p = ROOT / row.get("output_path", "")
        result["local_path"] = row.get("output_path")
        result["manifest_role"] = row.get("role")
        result["manifest_kind"] = row.get("kind")
        source_base_url = row.get("source_base_url")
        identity_match, mismatch_fields, requested_identity, source_identity = compare_source_identity(url, source_base_url)
        result["source_base_url"] = source_base_url
        result["source_identity_match"] = identity_match
        result["identity_mismatch_fields"] = mismatch_fields
        result["requested_identity"] = requested_identity
        result["source_identity"] = source_identity
        if p.exists() and p.is_file():
            digest, length = sha256(p)
            manifest_mime = row.get("mime")
            byte_mime = byte_signature_mime(p)
            result.update({
                "local_length": length,
                "local_sha256": digest,
                "local_mime": manifest_mime or mime_for(p),
                "manifest_mime": manifest_mime,
                "byte_signature_mime": byte_mime,
                "mime_evidence": "manifest_mime plus byte signature when image magic is available",
            })
            expected = row.get("derived_sha256")
            if expected and expected != digest:
                result["status"] = "local_hash_mismatch"
            elif identity_match is False:
                result["status"] = "source_scheme_mismatch_unproven" if mismatch_fields == ["scheme"] else "source_identity_mismatch_unproven"
            elif identity_match is None:
                result["status"] = "source_identity_not_recorded"
            else:
                result["status"] = "local_available"
        else:
            result["status"] = "mapped_missing_file"
        return result
    result["status"] = "mapped_route_without_manifest_file"
    return result


def purpose_rank(purpose: str, status: str) -> tuple[int, int]:
    base = {
        "body_illustration_candidate": 0,
        "image_reference_unknown": 1,
        "shared_stylesheet": 2,
        "css_background_or_import_asset": 3,
        "script_dependency": 4,
        "layout_or_navigation_image": 7,
        "layout_spacer_or_border": 9,
        "navigation_or_third_party_promo": 8,
        "embedded_or_media": 2,
        "metadata_or_navigation_link": 10,
    }.get(purpose, 5)
    return (base, 0 if status in {"not_mapped", "mapped_missing_file", "local_hash_mismatch"} else 1)


def read_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    return load_json(SELECTED), load_json(MANIFEST), load_json(PROVENANCE), load_json(ADDITIONS_MAP)


def main() -> int:
    selected, manifest, provenance, additions_map = read_inputs()
    selected_entries = [e for e in selected["entries"] if str(e.get("target", "")).startswith("/news/rss-")]
    if len(selected_entries) != 7:
        raise RuntimeError(f"expected seven RSS additions, found {len(selected_entries)}")
    files_by_route = {str(x.get("route")): x for x in manifest.get("files", []) if x.get("route")}
    prov_by_route = {str(x.get("route")): x for x in provenance.get("files", []) if x.get("route")}
    aliases = manifest.get("route_aliases", {}) or {}
    out: dict[str, Any] = {
        "schema": "wow-recovery.rss7-resource-review.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "network_requests": 0,
        "scope": "seven selected v10 RSS-path HTML additions only",
        "inputs": {},
        "prior_request_evidence_files": [],
        "pages": [],
        "unique_resources": [],
        "navigation_summary": {},
        "static_interaction_summary": {},
        "summary": {},
    }
    input_paths = [SELECTED, MANIFEST, PROVENANCE, ADDITIONS_MAP]
    for p in input_paths:
        digest, length = sha256(p)
        out["inputs"][str(p.relative_to(ROOT)).replace("\\", "/")] = {"bytes": length, "sha256": digest}
    prior_files = prior_request_file_records()
    out["prior_request_evidence_files"] = prior_files

    unique: dict[str, dict[str, Any]] = {}
    nav_unique: dict[str, dict[str, Any]] = {}
    total_refs = Counter()
    total_interaction = Counter()

    for entry in selected_entries:
        target = entry["target"]
        mrow = files_by_route.get(target)
        prow = prov_by_route.get(target)
        if not mrow or not prow:
            raise RuntimeError(f"missing manifest/provenance row for {target}")
        raw_path = ROOT / entry["local_path"]
        raw_digest, raw_len = sha256(raw_path)
        if raw_digest != entry["body_sha256"] or raw_len != entry["body_bytes"]:
            raise RuntimeError(f"raw source mismatch for {target}: {raw_len}/{raw_digest}")
        page_path = EXPORT_ROOT / prow["output_path"]
        page_digest, page_len = sha256(page_path)
        if page_digest != prow["derived_sha256"] or page_len != prow["derived_length"]:
            raise RuntimeError(f"export page mismatch for {target}: {page_len}/{page_digest}")
        raw_text = raw_path.read_text(encoding="utf-8", errors="replace")
        page_text = page_path.read_text(encoding="utf-8", errors="replace")
        base_url = entry.get("query_original_url") or f"http://www.worldofwarcraft.com{target}"
        parser = ResourceParser(raw_text, base_url, str(raw_path.relative_to(ROOT)).replace("\\", "/"))
        parser.feed(raw_text)
        parser.close()
        # Parse the derived page too, but use it only to prove the rendered
        # export still contains the original-resource evidence marker/path.
        derived_parser = ResourceParser(page_text, f"http://www.worldofwarcraft.com{target}", str(page_path.relative_to(ROOT)).replace("\\", "/"))
        derived_parser.feed(page_text)
        derived_parser.close()
        page_resources: list[dict[str, Any]] = []
        for rec in parser.records:
            if not rec.get("resolved_url"):
                total_refs["nonliteral_or_skipped"] += 1
                continue
            url = rec["resolved_url"]
            status = classify_status(url, manifest, files_by_route, aliases, EXPORT_ROOT)
            rec = dict(rec)
            rec["status"] = status["status"]
            rec["local_path"] = status["local_path"]
            rec["local_length"] = status["local_length"]
            rec["local_sha256"] = status["local_sha256"]
            rec["local_mime"] = status["local_mime"]
            rec["manifest_mime"] = status.get("manifest_mime")
            rec["byte_signature_mime"] = status.get("byte_signature_mime")
            rec["mime_evidence"] = status.get("mime_evidence")
            rec["source_base_url"] = status.get("source_base_url")
            rec["source_identity_match"] = status.get("source_identity_match")
            rec["identity_mismatch_fields"] = status.get("identity_mismatch_fields", [])
            rec["requested_identity"] = status.get("requested_identity")
            rec["source_identity"] = status.get("source_identity")
            rec["mapped_route"] = status["mapped_route"]
            rec["alias_target"] = status["alias_target"]
            page_resources.append(rec)
            total_refs[rec["resource_purpose"]] += 1
            u = unique.setdefault(url, {
                "exact_original_url": url,
                "origin_index_key": status["origin_index_key"],
                "reference_count": 0,
                "page_coverage": [],
                "resource_types": [],
                "resource_purposes": [],
                "statuses": [],
                "mapped_routes": [],
                "alias_targets": [],
                "local_evidence": [],
                "contexts": [],
            })
            u["reference_count"] += 1
            if target not in u["page_coverage"]:
                u["page_coverage"].append(target)
            for key, value in (("resource_types", rec["tag"]), ("resource_purposes", rec["resource_purpose"]), ("statuses", rec["status"]), ("mapped_routes", rec.get("mapped_route")), ("alias_targets", rec.get("alias_target"))):
                if value and value not in u[key]:
                    u[key].append(value)
            if rec.get("local_path") and rec.get("local_sha256") and len(u["local_evidence"]) < 8:
                evidence = {
                    "local_path": rec["local_path"],
                    "length": rec.get("local_length"),
                    "sha256": rec.get("local_sha256"),
                    "mime": rec.get("local_mime"),
                    "manifest_mime": rec.get("manifest_mime"),
                    "byte_signature_mime": rec.get("byte_signature_mime"),
                    "mime_evidence": rec.get("mime_evidence"),
                    "mapped_route": rec.get("mapped_route"),
                    "status": rec.get("status"),
                    "source_base_url": rec.get("source_base_url"),
                    "source_identity_match": rec.get("source_identity_match"),
                    "identity_mismatch_fields": rec.get("identity_mismatch_fields"),
                }
                if evidence not in u["local_evidence"]:
                    u["local_evidence"].append(evidence)
            if len(u["contexts"]) < 12:
                u["contexts"].append({k: rec[k] for k in ("source", "line", "tag", "attribute", "resource_purpose", "purpose_reason", "evidence")})
        for nav in parser.interactions:
            total_interaction[nav["kind"]] += 1
            if nav.get("resolved_url"):
                u = nav_unique.setdefault(nav["resolved_url"], {"exact_original_url": nav["resolved_url"], "reference_count": 0, "page_coverage": [], "contexts": []})
                u["reference_count"] += 1
                if target not in u["page_coverage"]:
                    u["page_coverage"].append(target)
                if len(u["contexts"]) < 8:
                    u["contexts"].append({k: nav.get(k) for k in ("kind", "line", "evidence")})
        out["pages"].append({
            "target": target,
            "query_original_url": entry.get("query_original_url"),
            "title_from_selection": entry.get("title"),
            "actual_timestamp": entry.get("actual_timestamp"),
            "source_raw_path": str(raw_path.relative_to(ROOT)).replace("\\", "/"),
            "source_raw_bytes": raw_len,
            "source_raw_sha256": raw_digest,
            "export_path": str(page_path.relative_to(ROOT)).replace("\\", "/"),
            "export_bytes": page_len,
            "export_sha256": page_digest,
            "manifest_route": mrow.get("route"),
            "provenance_role": prow.get("role"),
            "resource_reference_count": len(page_resources),
            "resource_references": page_resources,
            "navigation_reference_count": len(parser.interactions),
            "navigation_evidence": parser.interactions[:80],
            "static_interaction": {
                "script_src_count": sum(1 for x in page_resources if x["resource_purpose"] == "script_dependency"),
                "inline_script_literal_count": sum(1 for x in page_resources if x["resource_purpose"] == "script_literal_reference"),
                "forms": sum(1 for x in parser.interactions if x["kind"] == "form"),
                "inline_event_handlers": sum(1 for x in parser.interactions if x["kind"] == "inline_event_handler"),
                "claim": "static markup/script presence only; no interaction execution",
            },
            "derived_parse_resource_count": len(derived_parser.records),
        })

    # Add status and purpose summaries to each exact URL after all page refs.
    resources = list(unique.values())
    for u in resources:
        statuses = set(u["statuses"])
        purposes = set(u["resource_purposes"])
        if "body_illustration_candidate" in purposes:
            u["resource_scope"] = "page_body_candidate"
        elif purposes & {"shared_stylesheet", "script_dependency", "css_background_or_import_asset"}:
            u["resource_scope"] = "shared_template_or_style"
        else:
            u["resource_scope"] = "layout_or_metadata"
        if "local_hash_mismatch" in statuses:
            u["overall_status"] = "local_hash_mismatch"
        elif "source_scheme_mismatch_unproven" in statuses:
            u["overall_status"] = "source_scheme_mismatch_unproven"
        elif "source_identity_mismatch_unproven" in statuses:
            u["overall_status"] = "source_identity_mismatch_unproven"
        elif "source_identity_not_recorded" in statuses:
            u["overall_status"] = "source_identity_not_recorded"
        elif "local_available" in statuses:
            u["overall_status"] = "local_available"
        elif "mapped_missing_file" in statuses:
            u["overall_status"] = "mapped_missing_file"
        else:
            u["overall_status"] = "not_mapped_or_unknown"
        u["prior_request"] = prior_request_for_url(u["exact_original_url"], prior_files)
        if "navigation_or_third_party_promo" in purposes:
            u["resource_scope"] = "navigation_or_third_party"
            if u["overall_status"] == "local_available":
                u["priority"] = "local"
                u["priority_reason"] = "third-party/navigation promo is locally mapped and hash-verified"
            else:
                u["priority"] = "P3"
                u["priority_reason"] = "linked third-party/navigation promotion kept separate from正文素材队列"
        elif u["resource_scope"] == "page_body_candidate" and u["overall_status"] == "source_scheme_mismatch_unproven":
            u["priority"] = "P2"
            u["priority_reason"] = "实体字节可读但请求 scheme 与 manifest source_base_url 不同，缺少 exact scheme 证明"
        elif u["resource_scope"] == "page_body_candidate" and u["overall_status"] != "local_available":
            u["priority"] = "P1"
            u["priority_reason"] = "正文插图/截图候选，精确 origin 尚未由 v10 manifest 映射到可读实体"
        elif "shared_stylesheet" in purposes and u["overall_status"] != "local_available":
            u["priority"] = "P1"
            u["priority_reason"] = "七页共享样式依赖，影响整组页面"
        elif u["overall_status"] != "local_available":
            u["priority"] = "P2"
            u["priority_reason"] = "静态依赖或未知图片，需保留上下文后再核对"
        else:
            u["priority"] = "local"
            u["priority_reason"] = "manifest origin 映射与实体 SHA/长度可实读"

    candidates = [u for u in resources if u["overall_status"] != "local_available" and u["resource_scope"] in {"page_body_candidate", "shared_template_or_style"}]
    candidates.sort(key=lambda u: (0 if u["priority"] == "P1" and u["resource_scope"] == "page_body_candidate" else 1, purpose_rank(next(iter(u["resource_purposes"]), ""), u["overall_status"]), -u["reference_count"], u["exact_original_url"]))
    for i, u in enumerate(candidates[:16], 1):
        u["queue_rank"] = i
    out["unique_resources"] = sorted(resources, key=lambda u: (u["priority"] == "local", u["priority"], -u["reference_count"], u["exact_original_url"]))
    out["network_candidates"] = candidates[:16]
    mismatch_resources = [u for u in resources if u["overall_status"] in {"source_scheme_mismatch_unproven", "source_identity_mismatch_unproven", "source_identity_not_recorded"}]
    out["source_identity_mismatch_resources"] = mismatch_resources
    out["navigation_summary"] = {
        "unique_navigation_urls": len(nav_unique),
        "navigation_reference_count": sum(x["reference_count"] for x in nav_unique.values()),
        "examples": sorted(nav_unique.values(), key=lambda x: (-x["reference_count"], x["exact_original_url"]))[:40],
        "rule": "a[href] retained as navigation evidence and excluded from resource/image queue",
    }
    out["static_interaction_summary"] = {
        "by_kind": dict(total_interaction),
        "claim": "static source evidence only; no form, script, or navigation execution",
    }
    out["summary"] = {
        "selected_rss_pages": len(out["pages"]),
        "source_payloads_verified": sum(1 for x in out["pages"] if x["source_raw_bytes"] and x["source_raw_sha256"]),
        "export_pages_verified": sum(1 for x in out["pages"] if x["export_bytes"] and x["export_sha256"]),
        "resource_reference_count": sum(x["reference_count"] for x in resources),
        "unique_exact_original_resource_urls": len(resources),
        "local_readable_unique_resources": sum(1 for x in resources if x.get("local_evidence")),
        "local_available_unique_resources": sum(1 for x in resources if x["overall_status"] == "local_available"),
        "source_scheme_mismatch_unproven_unique_resources": sum(1 for x in resources if x["overall_status"] == "source_scheme_mismatch_unproven"),
        "source_identity_mismatch_unproven_unique_resources": sum(1 for x in resources if x["overall_status"] == "source_identity_mismatch_unproven"),
        "source_identity_not_recorded_unique_resources": sum(1 for x in resources if x["overall_status"] == "source_identity_not_recorded"),
        "not_locally_available_or_unknown_unique_resources": sum(1 for x in resources if x["overall_status"] == "not_mapped_or_unknown"),
        "body_candidate_unique": sum(1 for x in resources if x["resource_scope"] == "page_body_candidate"),
        "network_candidate_count_capped": min(16, len(candidates)),
        "nonliteral_or_skipped_references": total_refs["nonliteral_or_skipped"],
        "network_requests": 0,
        "page_hash_method": "SHA-256 of exact exported HTML bytes; raw source SHA/length compared to selected additions",
    }
    (OUT / "rss7-resource-review.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    queue = {
        "schema": "wow-recovery.rss7-resource-network-candidates.v1",
        "generated_utc": out["generated_utc"],
        "network_requests": 0,
        "scope": out["scope"],
        "input_hashes": out["inputs"],
        "selection_rule": "exact original origin+URL; navigation anchors excluded; body candidates and shared styles prioritized; layout/drop-cap/spacer and third-party promo remain separate",
        "candidate_count": len(out["network_candidates"]),
        "candidates": out["network_candidates"],
    }
    (OUT / "network-resource-candidates.json").write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# RSS7 resource review",
        "",
        f"Generated `{out['generated_utc']}`. This is a local static review of the seven selected v10 RSS-path HTML pages; `network_requests=0`. Navigation anchors are recorded separately and are not promoted to the image/resource queue.",
        "",
        "## Verified scope",
        "",
        f"The seven selected raw payloads and seven exported HTML pages each matched their selected/provenance SHA-256 and byte length. The review found **{out['summary']['resource_reference_count']}** exact request-bearing resource references and **{out['summary']['unique_exact_original_resource_urls']}** unique original URLs. **{out['summary']['local_readable_unique_resources']}** entities are byte-readable locally; **{out['summary']['local_available_unique_resources']}** have exact scheme/host/path/query identity, while **{out['summary']['source_scheme_mismatch_unproven_unique_resources']}** readable entities are HTTP-request/HTTPS-source scheme mismatches and are not counted as exact recovery. A further **{out['summary']['not_locally_available_or_unknown_unique_resources']}** are not mapped or otherwise unresolved locally. There are **{out['summary']['body_candidate_unique']}** unique body-image candidates after separating small-cap/layout assets and third-party promotion.",
        "",
        f"Navigation evidence contains {out['navigation_summary']['navigation_reference_count']} anchor references across {out['navigation_summary']['unique_navigation_urls']} unique URLs. Static markup evidence contains {total_interaction['form']} forms, {total_interaction['inline_event_handler']} inline event attributes, and six shared script-src dependencies per page; none was executed.",
        "",
        "## Input hashes",
        "",
        "| input | bytes | SHA-256 |",
        "|---|---:|---|",
    ]
    for path, item in out["inputs"].items():
        lines.append(f"| `{path}` | {item['bytes']} | `{item['sha256']}` |")
    lines += ["", "## Page verification", "", "| target | raw bytes/SHA prefix | exported bytes/SHA prefix | refs | nav refs |", "|---|---:|---:|---:|---:|"]
    for page in out["pages"]:
        lines.append(f"| `{page['target']}` | {page['source_raw_bytes']} / `{page['source_raw_sha256'][:12]}…` | {page['export_bytes']} / `{page['export_sha256'][:12]}…` | {page['resource_reference_count']} | {page['navigation_reference_count']} |")
    lines += ["", "## Source identity correction", "", "The manifest origin index is host/path based, so this pass additionally compared each requested scheme/host/path/query with the row's `source_base_url`. The three readable-but-non-exact rows are listed explicitly below; their bytes remain evidence, but they are not exact HTTP-source recovery.", ""]
    for item in out["source_identity_mismatch_resources"]:
        ev = item.get("local_evidence", [{}])[0]
        lines.append(f"- `{item['exact_original_url']}` → requested identity `{ev.get('source_identity_match')}`; source `{ev.get('source_base_url')}`; fields `{','.join(ev.get('identity_mismatch_fields') or [])}`; local `{ev.get('local_path')}`, {ev.get('length')} bytes, `{ev.get('sha256')}`.")
    lines += ["", "## Prior-request evidence boundary", "", "The candidate `prior_request` field checks only the explicitly bounded acceptance/request-ledger files recorded in the JSON. `not_checked` means no exact full URL hit was found there; it does not claim that the URL was never requested.", ""]
    for record in out["prior_request_evidence_files"]:
        lines.append(f"- `{record['path']}` — `{record.get('sha256')}`")
    lines += [""]
    local_samples = [x for x in resources if x.get("local_evidence") and x.get("overall_status") == "local_available" and x.get("resource_scope") == "page_body_candidate"]
    local_samples.sort(key=lambda x: (-x["reference_count"], x["exact_original_url"]))
    lines += ["", "## Local salvage evidence samples", "", "These are locally readable manifest-mapped entities with real byte length/SHA/MIME evidence; the full set is in `rss7-resource-review.json`.", ""]
    for item in local_samples[:12]:
        ev = item["local_evidence"][0]
        mime_note = ev.get("manifest_mime") or ev.get("mime") or "unknown"
        sig_note = f", byte signature `{ev['byte_signature_mime']}`" if ev.get("byte_signature_mime") else ""
        lines.append(f"- `{item['exact_original_url']}` → `{ev['local_path']}`; {ev['length']} bytes, `{ev['sha256']}`, manifest MIME `{mime_note}`{sig_note}; {item['reference_count']} reference(s).")
    lines += ["", "## Priority exact-URL candidates", "", "The queue is capped at 16 unique URLs. Each entry retains source line/context evidence in both the JSON review and queue. `not_mapped_or_unknown` means no local v10 origin-index entity was found; it is not a claim that an external capture exists.", ""]
    for item in out["network_candidates"]:
        pages = ", ".join(item["page_coverage"])
        ctx = item["contexts"][0] if item.get("contexts") else {}
        lines += [
            f"{item.get('queue_rank', '?')}. `{item['exact_original_url']}` — **{item['priority']}**, {item['overall_status']}, {item['reference_count']} reference(s), pages: `{pages}`.",
            f"   Purpose: {', '.join(item['resource_purposes'])}; evidence: `{ctx.get('source','')}` line {ctx.get('line','?')}: {ctx.get('evidence','')}",
        ]
    lines += ["", "## Boundaries", "", "- `a[href]` is navigation evidence, not an image or asset candidate.", "- `/new-hp/images/smallcaps/*.gif` is classified as repeated 32px drop-cap/layout markup from its path, dimensions, and adjacent text; it is not ranked as正文素材.", "- `news-sc2.jpg` is kept as a linked third-party promotion and excluded from the正文 queue.", "- Static forms, inline handlers, and scripts show only source presence. No interaction, MIME fetch, payload decode, or network request was performed by this review.", "- No basename substitution or cross-origin alias was made; exact origin and URL are retained.", ""]
    (OUT / "rss7-resource-review.md").write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
