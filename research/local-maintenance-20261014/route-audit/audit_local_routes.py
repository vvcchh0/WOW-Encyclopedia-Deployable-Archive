"""Offline-only audit of static HTML/CSS references in the v3 Pages export.

The audit is intentionally read-only for the frozen source and derived tree.  It
uses the build manifest/origin index and the export provenance as identity
evidence; basename similarity is never used to produce a repair candidate.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlsplit


ROOT = Path(__file__).resolve().parents[3]
DERIVED = ROOT / ".scratch/pages-historical-exhibits-20261014-v3"
MANIFEST_PATH = ROOT / "offline/build-manifest.json"
PROVENANCE_PATH = DERIVED / "export-provenance.json"
ROUTEMAP_PATH = DERIVED / "__offline/route-map.json"
OUT = ROOT / "research/local-maintenance-20261014/route-audit"
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
PRIMARY_HOST = "www.worldofwarcraft.com"
HTML_SUFFIXES = {".html", ".htm", ".xml"}
CSS_SUFFIXES = {".css"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_tree_digest(paths: list[Path], root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(paths, key=lambda p: p.relative_to(root).as_posix().casefold()):
        rel = path.relative_to(root).as_posix()
        data = path.read_bytes()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(str(len(data)).encode("ascii"))
        h.update(b"\0")
        h.update(hashlib.sha256(data).digest())
        h.update(b"\n")
    return h.hexdigest()


def norm_path(path: str) -> str:
    path = unquote(path or "")
    if not path.startswith("/"):
        path = "/" + path
    # urljoin has already normalised dot segments; this handles direct path
    # lookups and keeps a trailing slash meaningful for aliases.
    while "//" in path:
        path = path.replace("//", "/")
    return path


def origin_key(value: str) -> str:
    parsed = urlsplit(value)
    host = (parsed.hostname or "").casefold()
    port = parsed.port
    if port is not None and not ((parsed.scheme.casefold() == "http" and port == 80) or (parsed.scheme.casefold() == "https" and port == 443)):
        host += f":{port}"
    return host + norm_path(parsed.path or "/")


def base_name_from_static(value: str) -> str | None:
    parsed = urlsplit(value)
    path = parsed.path
    if not path.startswith(BASE_PATH):
        return None
    rel = path[len(BASE_PATH) :]
    return rel or "index.html"


def static_url(rel: str) -> str:
    return BASE_PATH + rel.lstrip("/")


def line_for(text: str, offset: int) -> int:
    return text.count("\n", 0, max(0, offset)) + 1


def looks_dynamic(value: str) -> bool:
    # Values assembled by the historical JavaScript/CSS are outside a static
    # route audit.  A URL with a query string is static unless it contains an
    # expression marker.
    return any(token in value for token in ("+", "{", "}", "<%", "%>", "${", "`"))


def is_non_network(value: str) -> bool:
    lower = value.strip().casefold()
    return not lower or lower.startswith(("#", "javascript:", "mailto:", "tel:", "data:", "about:", "blob:", "none"))


CSS_URL_RE = re.compile(r"url\(\s*(?P<quote>[\"']?)(?P<value>.*?)(?P=quote)\s*\)", re.I | re.S)
CSS_IMPORT_RE = re.compile(r"@import\s+(?P<quote>[\"'])(?P<value>.*?)(?P=quote)", re.I | re.S)


class RefParser(HTMLParser):
    ATTRS = {"src", "href", "poster", "background", "data", "codebase"}

    def __init__(self, text: str, rel: str):
        super().__init__(convert_charrefs=True)
        self.text = text
        self.rel = rel
        self._line_starts = [0]
        self._line_starts.extend(match.end() for match in re.finditer(r"\n", text))
        self.refs: list[dict] = []
        self.dynamic: list[dict] = []
        self._style_depth = 0
        self._style_start = 0
        self._style_parts: list[str] = []

    def _add(self, value: str, context: str, offset: int, attr: str | None = None):
        value = html.unescape(value).strip()
        item = {"raw": value, "context": context, "attr": attr, "offset": offset, "line": line_for(self.text, offset)}
        if is_non_network(value):
            item["skip"] = "non-network"
            return
        if looks_dynamic(value):
            item["skip"] = "dynamic-expression"
            self.dynamic.append(item)
            return
        self.refs.append(item)

    def _add_css(self, css: str, offset: int, context: str):
        for match in CSS_URL_RE.finditer(css):
            raw = html.unescape(match.group("value")).strip()
            self._add(raw, context, offset + match.start("value"), "url()")
        for match in CSS_IMPORT_RE.finditer(css):
            self._add(html.unescape(match.group("value")).strip(), "css_import", offset + match.start("value"), "@import")

    def handle_starttag(self, tag: str, attrs):
        start = self.getpos()
        # Resolve source offsets with one precomputed line index.  Rebuilding
        # splitlines() for every tag makes large historical pages quadratic.
        offset = self._line_starts[min(start[0] - 1, len(self._line_starts) - 1)] + start[1]
        tag_lower = tag.casefold()
        for name, value in attrs:
            if value is None:
                continue
            lname = name.casefold()
            if lname in self.ATTRS:
                self._add(value, f"html_{lname}", offset, lname)
            elif lname == "srcset":
                for token in re.split(r"\s*,\s*", value):
                    candidate = token.strip().split()[0] if token.strip() else ""
                    if candidate:
                        self._add(candidate, "html_srcset", offset, lname)
            elif lname == "style":
                self._add_css(value, offset, "html_style_url")
        if tag_lower == "style":
            self._style_depth += 1
            self._style_start = offset
            self._style_parts = []

    def handle_startendtag(self, tag: str, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str):
        if tag.casefold() == "style" and self._style_depth:
            self._add_css("".join(self._style_parts), self._style_start, "html_style_block")
            self._style_depth -= 1
            self._style_parts = []

    def handle_data(self, data: str):
        if self._style_depth:
            self._style_parts.append(data)

    def finish(self):
        if self._style_depth and self._style_parts:
            self._add_css("".join(self._style_parts), self._style_start, "html_style_block")


def parse_css(text: str) -> tuple[list[dict], list[dict]]:
    parser = RefParser("", "")
    parser._add_css(text, 0, "css_url")
    # The offset above is relative to the CSS body.  Replace lines accurately
    # for standalone CSS after extraction.
    for item in parser.refs + parser.dynamic:
        item["line"] = line_for(text, item["offset"])
    return parser.refs, parser.dynamic


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def route_static_maps(provenance: list[dict], route_map: dict) -> tuple[dict[str, str], dict[str, str], dict[str, dict]]:
    route_to_rel: dict[str, str] = {}
    static_to_route: dict[str, str] = {}
    by_output: dict[str, dict] = {}
    for item in provenance:
        rel = str(item.get("output_path") or "").replace("\\", "/")
        if not rel:
            continue
        by_output[rel] = item
        route = str(item.get("route") or "")
        if route and route not in route_to_rel:
            route_to_rel[route] = rel
        static_to_route.setdefault(rel.casefold(), route)
    for logical, value in (route_map.get("routes") or {}).items():
        rel = base_name_from_static(str(value))
        if rel is not None:
            static_to_route.setdefault(rel.casefold(), str(logical))
            route_to_rel.setdefault(str(logical), rel)
    for logical, value in (route_map.get("aliases") or {}).items():
        rel = base_name_from_static(str(value))
        if rel is not None:
            static_to_route.setdefault(rel.casefold(), str(logical))
            route_to_rel.setdefault(str(logical), rel)
    return route_to_rel, static_to_route, by_output


def local_target_evidence(rel: str, *, by_output: dict[str, dict], route_to_rel: dict[str, str], manifest_routes: dict[str, dict]) -> dict | None:
    item = by_output.get(rel)
    if item is None:
        return None
    route = str(item.get("route") or "")
    source = item.get("source_offline_path")
    record = manifest_routes.get(route)
    evidence = {
        "output_path": rel,
        "static_url": static_url(rel),
        "route": route,
        "source_offline_path": source,
        "derived_sha256": item.get("derived_sha256"),
        "derived_length": item.get("derived_length"),
        "kind": item.get("kind"),
        "role": item.get("role"),
    }
    if record:
        evidence["manifest_route"] = route
        evidence["manifest_sha256"] = record.get("derived_sha256")
        evidence["manifest_length"] = record.get("derived_length")
    if item.get("source_map"):
        evidence["source_map"] = item.get("source_map")
        evidence["source_path"] = item.get("source_path")
        evidence["original_url"] = item.get("original_url")
        evidence["temporal_class"] = item.get("temporal_class")
        evidence["supplement_strategy"] = item.get("supplement_strategy")
    return evidence


def resolve_original(raw: str, page_route: str) -> str:
    base = "http://" + PRIMARY_HOST + (page_route if page_route.startswith("/") else "/" + page_route)
    return urljoin(base, raw)


def requested_values(raw: str) -> list[str]:
    parsed = urlsplit(raw)
    query = parse_qs(parsed.query, keep_blank_values=True)
    values: list[str] = []
    # ``source`` identifies the page that emitted the placeholder.  It is
    # evidence about the caller, never the resource to repair.
    for key in ("requested", "target"):
        values.extend(query.get(key, []))
    return [unquote(v) for v in values if v]


def classify_ref(ref: dict, *, rel: str, page_route: str, existing: set[str], fold_map: dict[str, list[str]], route_to_rel: dict[str, str], static_to_route: dict[str, str], origin_to_route: dict[str, str], manifest_routes: dict[str, dict], by_output: dict[str, dict]):
    raw = ref["raw"]
    parsed = urlsplit(raw)
    page_path = "/" + rel
    placeholder = parsed.path.casefold().startswith(BASE_PATH.casefold() + "__offline/missing") or "/__offline/missing" in parsed.path.casefold()
    if placeholder:
        reqs = requested_values(raw)
        ref["classification"] = "known_placeholder"
        ref["requested"] = reqs[-1] if reqs else None
        for req in reversed(reqs):
            absolute = req if urlsplit(req).scheme else resolve_original(req, page_route)
            key = origin_key(absolute) if urlsplit(absolute).scheme in {"http", "https"} else ""
            route = origin_to_route.get(key)
            if route is None and req.startswith(BASE_PATH):
                req_rel = base_name_from_static(req)
                route = static_to_route.get((req_rel or "").casefold())
            if route:
                target_rel = route_to_rel.get(route)
                if target_rel and target_rel in existing:
                    ref["candidate_route"] = route
                    ref["candidate_rel"] = target_rel
                    ref["candidate_reason"] = "placeholder requested URL exact host+path matches frozen origin/route index"
                    ref["evidence"] = local_target_evidence(target_rel, by_output=by_output, route_to_rel=route_to_rel, manifest_routes=manifest_routes)
                    return "candidate"
        ref["missing_reason"] = "placeholder requested identity has no exact local origin/route evidence"
        return "missing"

    if is_non_network(raw):
        ref["classification"] = "preserved_or_non_network"
        return "skip"
    if raw.startswith(BASE_PATH):
        requested_rel = base_name_from_static(raw) or ""
        if requested_rel in existing:
            ref["classification"] = "resolved"
            return "resolved"
        folded = fold_map.get(requested_rel.casefold(), [])
        route = static_to_route.get(requested_rel.casefold())
        if len(folded) == 1 and route:
            target_rel = folded[0]
            ref.update({"classification": "case_mismatch", "candidate_route": route, "candidate_rel": target_rel, "candidate_reason": "Pages-prefixed path differs only by case and its route-map identity is unique", "evidence": local_target_evidence(target_rel, by_output=by_output, route_to_rel=route_to_rel, manifest_routes=manifest_routes)})
            return "candidate"
        ref["classification"] = "missing_local_path"
        ref["missing_reason"] = "Pages-prefixed static path has no exact output file"
        return "missing"

    # Absolute original/external URL: preserve the host+path identity.
    if parsed.scheme.casefold() in {"http", "https"}:
        route = origin_to_route.get(origin_key(raw))
        if route:
            target_rel = route_to_rel.get(route)
            if target_rel and target_rel in existing:
                ref.update({"classification": "unlocalized_existing", "candidate_route": route, "candidate_rel": target_rel, "candidate_reason": "absolute URL exact host+path matches frozen origin index", "evidence": local_target_evidence(target_rel, by_output=by_output, route_to_rel=route_to_rel, manifest_routes=manifest_routes)})
                return "candidate"
        ref["classification"] = "external_or_uncollected"
        ref["missing_reason"] = "absolute URL has no exact frozen origin identity"
        return "missing"

    # Relative/root-local reference.  First test the actual derived path.
    actual = urlsplit(urljoin("http://pages.invalid/" + rel, raw))
    actual_rel = actual.path.lstrip("/")
    if actual_rel in existing:
        ref["classification"] = "resolved"
        return "resolved"
    folded = fold_map.get(actual_rel.casefold(), [])
    original = resolve_original(raw, page_route)
    route = origin_to_route.get(origin_key(original))
    if route is None and raw.startswith("/"):
        route = static_to_route.get(norm_path(parsed.path).casefold())
    if route:
        target_rel = route_to_rel.get(route)
        if target_rel and target_rel in existing:
            kind = "alias_or_wrong_path"
            if len(folded) == 1 and folded[0] == target_rel and actual_rel.casefold() == target_rel.casefold():
                kind = "case_mismatch"
            ref.update({"classification": kind, "candidate_route": route, "candidate_rel": target_rel, "candidate_reason": "relative/root reference resolves to a frozen origin route with an existing exact local output", "evidence": local_target_evidence(target_rel, by_output=by_output, route_to_rel=route_to_rel, manifest_routes=manifest_routes)})
            return "candidate"
    if len(folded) == 1:
        ref.update({"classification": "unproven_case_similarity", "missing_reason": "casefold target exists but original host+path/route identity was not proven"})
    else:
        ref["classification"] = "missing_local_path"
        ref["missing_reason"] = "resolved local path has no exact output file or origin identity"
    return "missing"


def group_rows(rows: list[dict], key_fields: tuple[str, ...], limit: int | None = None) -> list[dict]:
    groups: dict[tuple, dict] = {}
    for row in rows:
        key = tuple(row.get(k) for k in key_fields)
        group = groups.setdefault(key, {k: row.get(k) for k in key_fields} | {"occurrences": 0, "pages": set(), "examples": []})
        group["occurrences"] += 1
        group["pages"].add(row.get("page"))
        if len(group["examples"]) < 4:
            group["examples"].append({"page": row.get("page"), "line": row.get("line"), "context": row.get("context"), "raw": row.get("raw")})
    result = []
    for group in groups.values():
        group["pages"] = len(group["pages"])
        result.append(group)
    result.sort(key=lambda x: (-x["pages"], -x["occurrences"], str(x.get(key_fields[0]) or "")))
    return result[:limit] if limit is not None else result


def main() -> int:
    manifest_data = MANIFEST_PATH.read_bytes()
    provenance_data = PROVENANCE_PATH.read_bytes()
    route_map_data = ROUTEMAP_PATH.read_bytes()
    manifest = json.loads(manifest_data)
    provenance = json.loads(provenance_data)
    route_map = json.loads(route_map_data)
    scanned_paths = [p for p in DERIVED.rglob("*") if p.is_file() and p.suffix.casefold() in HTML_SUFFIXES | CSS_SUFFIXES]
    tree_before = stable_tree_digest(scanned_paths, DERIVED)
    route_to_rel, static_to_route, by_output = route_static_maps(provenance.get("files") or [], route_map)
    existing = {p.relative_to(DERIVED).as_posix() for p in DERIVED.rglob("*") if p.is_file()}
    fold_map: dict[str, list[str]] = defaultdict(list)
    for rel in existing:
        fold_map[rel.casefold()].append(rel)
    manifest_routes = {str(item.get("route")): item for item in (manifest.get("files") or []) if item.get("route")}
    origin_to_route = {str(key): str(value) for key, value in (manifest.get("origin_index") or {}).items()}
    for item in provenance.get("files") or []:
        original = item.get("original_url")
        route = item.get("route")
        if original and route:
            origin_to_route.setdefault(origin_key(str(original)), str(route))

    refs: list[dict] = []
    dynamic: list[dict] = []
    parser_errors: list[dict] = []
    for path in sorted(scanned_paths, key=lambda p: p.as_posix().casefold()):
        rel = path.relative_to(DERIVED).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        item = by_output.get(rel, {})
        page_route = str(item.get("route") or ("/" + rel))
        if path.suffix.casefold() in CSS_SUFFIXES:
            current, current_dynamic = parse_css(text)
        else:
            parser = RefParser(text, rel)
            try:
                parser.feed(text)
                parser.close()
                parser.finish()
                current, current_dynamic = parser.refs, parser.dynamic
            except Exception as exc:  # retain scan coverage while recording malformed markup
                parser_errors.append({"page": rel, "error": repr(exc)})
                current, current_dynamic = parser.refs, parser.dynamic
        for row in current_dynamic:
            row.update({"page": rel, "route": page_route})
            dynamic.append(row)
        for row in current:
            row.update({"page": rel, "route": page_route})
            outcome = classify_ref(row, rel=rel, page_route=page_route, existing=existing, fold_map=fold_map, route_to_rel=route_to_rel, static_to_route=static_to_route, origin_to_route=origin_to_route, manifest_routes=manifest_routes, by_output=by_output)
            row["outcome"] = outcome
            refs.append(row)

    candidate_rows = [r for r in refs if r.get("outcome") == "candidate"]
    candidate_groups = group_rows(candidate_rows, ("candidate_rel", "candidate_route", "classification"))
    for row in candidate_groups:
        row["impact_score"] = row["pages"] * 10 + row["occurrences"] * 2
        matches = [r for r in candidate_rows if r.get("candidate_rel") == row.get("candidate_rel") and r.get("candidate_route") == row.get("candidate_route") and r.get("classification") == row.get("classification")]
        row["source_examples"] = [
            {"page": r["page"], "line": r["line"], "context": r["context"], "raw": r["raw"], "requested": r.get("requested"), "reason": r.get("candidate_reason")}
            for r in matches[:4]
        ]
        row["evidence"] = matches[0].get("evidence")
        row["original_identities"] = sorted({origin_key((r.get("requested") or "")) for r in matches if r.get("requested") and urlsplit(r["requested"]).scheme})[:8]
    candidate_groups.sort(key=lambda x: (-x["impact_score"], -x["pages"], -x["occurrences"], x["candidate_rel"]))
    candidates = candidate_groups[:30]
    for i, row in enumerate(candidates, 1):
        row["rank"] = i

    placeholder_rows = [r for r in refs if r.get("classification") == "known_placeholder"]
    missing_rows = [r for r in refs if r.get("outcome") == "missing"]
    missing_assets = group_rows(
        [r for r in missing_rows if r.get("classification") in {"known_placeholder", "external_or_uncollected", "missing_local_path"}],
        ("classification", "raw", "missing_reason"),
        limit=None,
    )
    unproven = group_rows(
        [r for r in missing_rows if r.get("classification") in {"unproven_case_similarity", "external_or_uncollected", "missing_local_path"}],
        ("classification", "raw", "missing_reason"),
        limit=200,
    )
    tree_after = stable_tree_digest(scanned_paths, DERIVED)
    manifest_after = sha256_bytes(MANIFEST_PATH.read_bytes())
    provenance_after = sha256_bytes(PROVENANCE_PATH.read_bytes())
    route_map_after = sha256_bytes(ROUTEMAP_PATH.read_bytes())
    counts = Counter(r.get("outcome") for r in refs)
    class_counts = Counter(r.get("classification") for r in refs)
    summary = {
        "schema": "local-route-audit/v1",
        "generated_at": "2026-10-14",
        "offline_only": True,
        "inputs": {
            "derived_root": str(DERIVED.relative_to(ROOT)).replace("\\", "/"),
            "manifest": str(MANIFEST_PATH.relative_to(ROOT)).replace("\\", "/"),
            "provenance": str(PROVENANCE_PATH.relative_to(ROOT)).replace("\\", "/"),
            "route_map": str(ROUTEMAP_PATH.relative_to(ROOT)).replace("\\", "/"),
            "manifest_sha256_before": sha256_bytes(manifest_data),
            "manifest_sha256_after": manifest_after,
            "provenance_sha256_before": sha256_bytes(provenance_data),
            "provenance_sha256_after": provenance_after,
            "route_map_sha256_before": sha256_bytes(route_map_data),
            "route_map_sha256_after": route_map_after,
            "scanned_tree_digest_before": tree_before,
            "scanned_tree_digest_after": tree_after,
            "hashes_unchanged": all(
                [sha256_bytes(manifest_data) == manifest_after, sha256_bytes(provenance_data) == provenance_after, sha256_bytes(route_map_data) == route_map_after, tree_before == tree_after]
            ),
        },
        "inventory": {
            "derived_files_total": len(existing),
            "html_files_scanned": sum(p.suffix.casefold() in HTML_SUFFIXES for p in scanned_paths),
            "css_files_scanned": sum(p.suffix.casefold() in CSS_SUFFIXES for p in scanned_paths),
            "manifest_files": len(manifest.get("files") or []),
            "manifest_origin_entries": len(manifest.get("origin_index") or {}),
            "provenance_files": len(provenance.get("files") or []),
            "provenance_overlay_entries": sum(bool(x.get("source_map")) for x in provenance.get("files") or []),
            "route_aliases": len(route_map.get("aliases") or {}),
        },
        "scan": {
            "static_reference_occurrences": len(refs),
            "dynamic_reference_occurrences_skipped": len(dynamic),
            "parser_errors": parser_errors,
            "outcome_counts": {key: counts.get(key, 0) for key in ("resolved", "candidate", "missing", "skip")},
            "classification_counts": {key: class_counts.get(key, 0) for key in ("resolved", "known_placeholder", "external_or_uncollected", "missing_local_path", "unproven_case_similarity")},
            "known_placeholder_occurrences": len(placeholder_rows),
            "known_placeholder_unique": len(group_rows(placeholder_rows, ("raw",), limit=None)),
            "candidate_occurrences": len(candidate_rows),
            "candidate_unique_proven": len(candidate_groups),
            "candidates_emitted": len(candidates),
            "missing_occurrences": len(missing_rows),
            "unproven_group_count_emitted": len(unproven),
            "missing_asset_group_count": len(missing_assets),
        },
        "candidates": candidates,
        "missing_assets": missing_assets,
        "unproven": unproven,
        "dynamic_samples": dynamic[:100],
        "representative_refs": [
            {k: row.get(k) for k in ("page", "line", "context", "raw", "classification", "outcome", "candidate_rel", "candidate_route", "requested", "missing_reason")}
            for row in (
                sorted([r for r in refs if r.get("outcome") == "candidate"], key=lambda x: (x.get("page", ""), x.get("line", 0)))[:8]
                + sorted([r for r in refs if r.get("outcome") == "missing"], key=lambda x: (x.get("page", ""), x.get("line", 0)))[:8]
                + sorted([r for r in refs if r.get("outcome") == "resolved"], key=lambda x: (x.get("page", ""), x.get("line", 0)))[:8]
            )
        ],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Local route audit",
        "",
        "Offline static audit of all derived HTML/XML/CSS in `.scratch/pages-historical-exhibits-20261014-v3`.",
        "The frozen source tree, build manifest, provenance, and route map were read only.",
        "",
        f"Scanned {summary['inventory']['html_files_scanned']} HTML/XML files and {summary['inventory']['css_files_scanned']} CSS files, yielding {len(refs)} static reference occurrences; {len(dynamic)} dynamic expressions were skipped.",
        f"Outcomes: {counts.get('resolved', 0)} resolved, {counts.get('candidate', 0)} occurrences with {len(candidate_groups)} proven repair identities ({len(candidates)} emitted), and {counts.get('missing', 0)} unresolved occurrences.",
        f"Known missing placeholders: {len(placeholder_rows)} occurrences ({summary['scan']['known_placeholder_unique']} unique). Input hashes unchanged: {summary['inputs']['hashes_unchanged']}.",
        "",
        "## Proven repair candidates",
        "",
        "| rank | impact | pages | refs | kind | current evidence | exact local target |",
        "| ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in candidates:
        evidence = row.get("evidence") or {}
        lines.append(f"| {row['rank']} | {row['impact_score']} | {row['pages']} | {row['occurrences']} | {row.get('classification')} | `{row.get('candidate_route')}` / `{evidence.get('source_offline_path')}` | `{static_url(row['candidate_rel'])}` |")
    if not candidates:
        lines.append("| — | — | — | — | none proven | — | — |")
    lines += [
        "",
        "## Unproven or missing material",
        "",
        "Grouped rows below retain unresolved identities separately. A casefold or basename match without an exact host+path/route index is deliberately not a repair candidate.",
        "",
        f"The JSON contains {len(unproven)} representative groups (up to 200), {sum(x['occurrences'] for x in unproven)} grouped occurrences, plus dynamic-expression samples.",
        "",
        "## Representative evidence",
        "",
    ]
    for row in summary["representative_refs"][:12]:
        lines.append(f"- `{row.get('page')}:{row.get('line')}` `{row.get('context')}` `{row.get('raw')}` → `{row.get('outcome')}/{row.get('classification')}`")
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"summary": str((OUT / "summary.json").relative_to(ROOT)).replace("\\", "/"), "markdown": str((OUT / "summary.md").relative_to(ROOT)).replace("\\", "/"), "counts": summary["scan"], "hashes_unchanged": summary["inputs"]["hashes_unchanged"]}, ensure_ascii=False))
    return 0 if summary["inputs"]["hashes_unchanged"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
