from __future__ import annotations

import hashlib
import html
import json
import os
import posixpath
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(r"D:\WOW_Encyclopedia")
OUT = ROOT / "research/continuous-recovery-20261015/sidebar-audit"
INVENTORY_PATH = ROOT / "research/navigation-gaps-20261015/inventory.json"
INVENTORY_MD = ROOT / "research/navigation-gaps-20261015/inventory.md"
V7_RECEIPT = ROOT / "research/navigation-gaps-20261015/v7c-build-receipt.json"
V8 = ROOT / ".scratch/pages-resources-20261015-v8"
V8_ROUTE_MAP = V8 / "__offline/route-map.json"
V8_PROVENANCE = V8 / "export-provenance.json"
V8_BUILD = ROOT / "research/resource-repair-20261015/build-v8.json"
FINAL_ACCEPTANCE = ROOT / "research/resource-repair-20261015/root-final-acceptance.json"
FROZEN_MANIFEST = ROOT / "offline/build-manifest.json"
DOC_PATH = ROOT / "docs/media-and-navigation-recovery-20261015.md"
CHANGELOG = ROOT / "CHANGELOG.md"

ATTR_RE = re.compile(
    r"(?P<attr>src|href|action|poster|data|background)\s*=\s*['\"](?P<url>[^'\"]+)['\"]",
    re.IGNORECASE,
)
CSS_URL_RE = re.compile(r"url\(\s*['\"]?(?P<url>[^'\")]+)['\"]?\s*\)", re.IGNORECASE)
SCRIPT_RE = re.compile(r"<script\b", re.IGNORECASE)
FORM_RE = re.compile(r"<form\b", re.IGNORECASE)
OBJECT_RE = re.compile(r"<(?:object|embed|applet)\b|\.swf(?:[\"'?#\s<]|$)|application/x-shockwave-flash|shockwave\.flash", re.IGNORECASE)
FRAME_RE = re.compile(r"<(?:iframe|frame|frameset)\b", re.IGNORECASE)
EVENT_RE = re.compile(r"\bon(?:click|submit|change|load|error|mouseover)\s*=|javascript:", re.IGNORECASE)
V8_ABS = os.path.normcase(os.path.abspath(str(V8)))
BUSINESS_PATH_PREFIXES = ("/account", "/loginsupport", "/billing", "/support")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path).replace("\\", "/")


def evidence(path: str, locator: str, detail: str) -> str:
    return f"{path}:{locator} — {detail}"


def safe_relative(path: Path, base: Path) -> bool:
    # Path.resolve() performs filesystem work on Windows.  Dependency scans
    # can visit tens of thousands of references, so use lexical absolute
    # paths after normalizing the candidate instead.
    path_abs = os.path.normcase(os.path.abspath(os.fspath(path)))
    base_abs = os.path.normcase(os.path.abspath(os.fspath(base)))
    try:
        return os.path.commonpath((path_abs, base_abs)) == base_abs
    except ValueError:
        return False


def static_relative(static_url: str, base_path: str) -> str:
    value = urlsplit(static_url).path
    if value.startswith(base_path):
        value = value[len(base_path) :]
    return unquote(value.lstrip("/")).replace("/", os.sep)


def normalize_ref(raw: str) -> str:
    value = unquote(urlsplit(raw).path)
    return value.replace("\\", "/")


def main() -> None:
    inventory = load_json(INVENTORY_PATH)
    route_map = load_json(V8_ROUTE_MAP)
    provenance = load_json(V8_PROVENANCE)
    final_acceptance = load_json(FINAL_ACCEPTANCE)
    v8_build = load_json(V8_BUILD)
    v7_receipt = load_json(V7_RECEIPT)

    routes = route_map.get("routes", {})
    aliases = route_map.get("aliases", {})
    base_path = route_map["base_path"]
    output_by_route = {}
    for key, value in routes.items():
        output_by_route[key] = value
    for key, value in aliases.items():
        output_by_route.setdefault(key, value)

    provenance_by_output = {
        str(record.get("output_path", "")).replace("\\", "/"): record
        for record in provenance.get("files", [])
        if record.get("output_path")
    }

    # Do not retain every page body: the v8 image tree is large and a few
    # historical HTML/XML exports are also sizeable.  The audit only needs a
    # page body while classifying that record.
    hash_cache: dict[Path, str | None] = {}

    def get_hash(path: Path) -> str | None:
        if path not in hash_cache:
            hash_cache[path] = sha256(path)
        return hash_cache[path]

    def page_for_route(route: str | None):
        if not route or route not in output_by_route:
            return None, None, None, None
        static_url = output_by_route[route]
        relative = static_relative(static_url, base_path)
        candidate = Path(os.path.abspath(os.fspath(V8 / relative)))
        if not safe_relative(candidate, V8):
            return static_url, relative, candidate, None
        record = provenance_by_output.get(relative.replace("\\", "/"))
        return static_url, relative, candidate, record

    def infer_route(entry: dict, coverage: dict):
        """Recover a route when the first inventory parser left it null.

        Legacy menu lines commonly carry a trailing space in the href.  Use
        only the local path component and preserve the route-map evidence; no
        network or content inference is performed here.
        """
        recorded = coverage.get("normalized_route")
        if recorded:
            return recorded, "inventory"
        raw = html.unescape(str(entry.get("href") or "").strip())
        parsed = urlsplit(raw)
        host = (parsed.hostname or "").lower()
        first_party_hosts = {"www.worldofwarcraft.com", "worldofwarcraft.com"}
        if (parsed.scheme or parsed.netloc) and host not in first_party_hosts:
            return None, "external_host"
        if not parsed.path.startswith("/"):
            return None, "unavailable"
        path = parsed.path
        normalized = posixpath.normpath(path)
        if not normalized.startswith("/"):
            normalized = "/" + normalized
        candidates = [normalized]
        if path.endswith("/"):
            candidates.insert(0, normalized.rstrip("/") + "/")
        elif normalized != "/":
            candidates.append(normalized.rstrip("/") + "/")
        for candidate in candidates:
            if candidate in output_by_route:
                return candidate, "href_fallback_first_party" if host in first_party_hosts else "href_fallback_route_map"
        return normalized, "href_fallback_unmapped"

    def page_text(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    def resolve_local_ref(raw: str, page_path: Path, attr: str):
        parsed = urlsplit(raw)
        path_part = normalize_ref(raw)
        if not path_part or raw.startswith("#"):
            return None, False, False
        if parsed.scheme or parsed.netloc:
            return None, False, False
        lowered = raw.lower()
        if lowered.startswith(("data:", "mailto:", "javascript:", "about:", "tel:")):
            return None, False, False
        if path_part.startswith(base_path.rstrip("/")):
            route_candidate = "/" + path_part[len(base_path.rstrip("/")) :].lstrip("/")
            candidate_static = base_path + path_part[len(base_path.rstrip("/")) :].lstrip("/")
        elif path_part.startswith("/"):
            route_candidate = posixpath.normpath(path_part)
            candidate_static = output_by_route.get(route_candidate)
            if candidate_static is None:
                candidate_static = base_path + route_candidate.lstrip("/")
        else:
            page_rel = page_path.relative_to(V8).as_posix()
            route_candidate = "/" + posixpath.normpath(posixpath.join(posixpath.dirname(page_rel), path_part)).lstrip("/")
            candidate_static = output_by_route.get(route_candidate)
            if candidate_static is None:
                candidate_static = base_path + route_candidate.lstrip("/")
        relative = static_relative(candidate_static, base_path)
        target = Path(os.path.abspath(os.fspath(V8 / relative)))
        exists = safe_relative(target, V8) and target.is_file()
        critical = attr.lower() in {"src", "poster", "data", "background"}
        return target, exists, critical

    def scan_dependencies(path: Path):
        if not path.is_file() or path.suffix.lower() not in {".html", ".htm", ".xml", ".js", ".css"}:
            return {"reference_count": 0, "local_unresolved_count": 0, "critical_unresolved_count": 0, "unresolved_samples": []}
        text = page_text(path)
        refs = [(m.group("attr"), m.group("url")) for m in ATTR_RE.finditer(text)]
        refs.extend(("css-url", m.group("url")) for m in CSS_URL_RE.finditer(text))
        # Provenance's placeholder count is the authoritative missing-resource
        # signal for transformed pages.  Keep the cheap textual scan for
        # context, but avoid filesystem resolution for every historical href;
        # many pages contain thousands of old article links.
        marker_matches = list(re.finditer(r"(?:__offline/)?(?:missing(?:\.html|-image\.svg)|placeholder)", text, re.IGNORECASE))
        image_marker_matches = list(re.finditer(r"missing-image\.svg", text, re.IGNORECASE))
        unresolved = [{"attr": "derived-marker", "raw": text[max(0, m.start() - 60) : m.end() + 60]} for m in marker_matches[:20]]
        return {
            "reference_count": len(refs),
            "local_unresolved_count": len(marker_matches),
            "critical_unresolved_count": len(image_marker_matches),
            "unresolved_samples": unresolved,
        }

    duplicate_keys = Counter(
        (entry.get("source_role"), entry.get("menu_id"))
        for entry in inventory.get("entries", []) + inventory.get("excluded_entries", [])
        if entry.get("menu_id")
    )
    duplicate_ids = {key for key, count in duplicate_keys.items() if count > 1}
    scope_reasons = inventory.get("scope", {}).get("excluded_sections", {})
    legacy_reclassification_reason = "parser_unclassified_legacy"

    source_paths = [
        INVENTORY_PATH,
        INVENTORY_MD,
        FINAL_ACCEPTANCE,
        V8_BUILD,
        V7_RECEIPT,
        FROZEN_MANIFEST,
        DOC_PATH,
        CHANGELOG,
        V8_ROUTE_MAP,
        V8_PROVENANCE,
        ROOT / ".scratch/offline-navigation-20261015-v7c/build-manifest.json",
    ]
    input_hashes = []
    for path in source_paths:
        input_hashes.append(
            {
                "path": rel(path),
                "exists": path.is_file(),
                "bytes": path.stat().st_size if path.is_file() else None,
                "sha256": sha256(path),
            }
        )

    def classify(entry: dict, index: int, scope: str):
        coverage = entry.get("coverage") or {}
        old_status = coverage.get("status")
        inventory_route = coverage.get("normalized_route")
        old_route, route_source = infer_route(entry, coverage)
        source_path = entry.get("source_path", "")
        source_line = entry.get("source_line")
        menu_id = entry.get("menu_id")
        label = entry.get("label")
        href = entry.get("href") or ""
        route = old_route
        static_url, output_relative, page_path, prov = page_for_route(route)
        current_route_kind = None
        if route in routes:
            current_route_kind = "route"
        elif route in aliases:
            current_route_kind = "alias"

        page_exists = bool(page_path and page_path.is_file())
        current_page_status = "scope_excluded" if scope == "scope_excluded" else "missing_export_route"
        if scope == "scope_excluded":
            current_page_status = "scope_excluded"
        elif route not in output_by_route:
            if route_source in {"external_host", "unavailable"} or old_status == "external_or_dynamic":
                current_page_status = "external_or_dynamic"
            elif route and any(route == prefix or route.startswith(prefix + "/") for prefix in BUSINESS_PATH_PREFIXES):
                current_page_status = "business_or_sensitive"
            else:
                current_page_status = "missing_export_route"
        elif not page_exists:
            current_page_status = "missing_page_file"
        elif old_status in {"external_or_dynamic", "missing_export_route"}:
            current_page_status = "resolved_recovered"
        elif current_route_kind == "alias":
            current_page_status = "resolved_via_alias"
        else:
            current_page_status = "resolved"

        dependency = {"reference_count": 0, "local_unresolved_count": 0, "critical_unresolved_count": 0, "unresolved_samples": []}
        page_record = None
        page_sha = None
        page_bytes = None
        if page_exists:
            dependency = scan_dependencies(page_path)
            page_sha = get_hash(page_path)
            page_bytes = page_path.stat().st_size
        if prov:
            page_record = {
                "role": prov.get("role"),
                "kind": prov.get("kind"),
                "source_offline_path": prov.get("source_offline_path"),
                "source_sha256": prov.get("source_sha256"),
                "source_length": prov.get("source_length"),
                "derived_sha256": prov.get("derived_sha256"),
                "derived_length": prov.get("derived_length"),
                "reference_counts": prov.get("reference_counts", {}),
                "derivation_reason": prov.get("derivation_reason"),
            }

        placeholder_count = int((page_record or {}).get("reference_counts", {}).get("placeholder", 0) or 0)
        if current_page_status in {"scope_excluded", "business_or_sensitive", "external_or_dynamic", "missing_export_route", "missing_page_file"}:
            asset_status = "not_available"
        elif placeholder_count or dependency["critical_unresolved_count"]:
            asset_status = "partial_missing_assets"
        else:
            asset_status = "local_dependencies_resolved"

        if current_page_status in {"scope_excluded", "business_or_sensitive", "external_or_dynamic", "missing_export_route", "missing_page_file"}:
            interaction_status = "not_available"
            interaction_evidence = []
        else:
            body = page_text(page_path)
            scripts = len(SCRIPT_RE.findall(body))
            forms = len(FORM_RE.findall(body))
            objects = len(OBJECT_RE.findall(body))
            frames = len(FRAME_RE.findall(body))
            events = len(EVENT_RE.findall(body))
            if objects:
                interaction_status = "legacy_plugin_static_indication"
            elif forms:
                interaction_status = "localized_form_static_indication"
            elif events or scripts > 2:
                interaction_status = "localized_script_static_indication"
            else:
                interaction_status = "static_surface_static_indication"
            interaction_evidence = [
                f"{rel(page_path)}:html — static source scan only; scripts={scripts}, forms={forms}, plugin_refs={objects}, frames={frames}, event_refs={events}"
            ]

        duplicate = (entry.get("source_role"), menu_id) in duplicate_ids
        gap_types = []
        if current_page_status in {"missing_export_route", "missing_page_file"}:
            gap_types.append("missing_page_or_route")
        if current_page_status == "business_or_sensitive":
            gap_types.append("business_or_sensitive_entry")
        if current_page_status == "external_or_dynamic":
            gap_types.append("external_or_dynamic_entry")
        if asset_status == "partial_missing_assets":
            gap_types.append("missing_key_assets")
        if interaction_status == "legacy_plugin_static_indication":
            gap_types.append("legacy_plugin_static_indication")
        if current_page_status in {"resolved_via_alias", "resolved_recovered"}:
            gap_types.append("route_alias_or_recovered")
        if duplicate:
            gap_types.append("source_menu_id_collision")

        if current_page_status in {"scope_excluded", "business_or_sensitive"}:
            next_action = "保留为范围外历史/外部入口；不作为缺页，不扩展敏感或社交交互。"
            priority = "P4"
        elif current_page_status == "external_or_dynamic":
            next_action = "若要恢复，先为该历史入口找到本地捕获并建立静态展品映射；当前不执行网络获取。"
            priority = "P2"
        elif current_page_status in {"missing_export_route", "missing_page_file"}:
            next_action = "补充已验证历史页面或路由映射；保留当前缺口占位，不生成假内容。"
            priority = "P0"
        elif asset_status == "partial_missing_assets":
            next_action = "按页面来源记录补齐缺失原始资源或保留可见占位，并在派生构建中登记来源。"
            priority = "P1"
        elif interaction_status == "legacy_plugin_static_indication":
            next_action = "保留静态替代说明；仅在找到本地旧插件素材时评估交互恢复。"
            priority = "P1"
        elif duplicate:
            next_action = "在下一次导航生成中保持唯一菜单 ID，并核对两个标签的独立路由。"
            priority = "P2"
        elif current_page_status in {"resolved_via_alias", "resolved_recovered"}:
            next_action = "当前路由可达；保留来源和别名证据，后续构建继续回归检查。"
            priority = "P3"
        else:
            next_action = "当前本地页面、依赖和交互外框均可用；无需修复。"
            priority = "P3"

        inventory_bucket = "entries" if scope == "in_scope" else "excluded_entries"
        ev = [
            evidence(source_path, f"line {source_line}", f"menu_id={menu_id}, label={label!r}, href={href!r}"),
            evidence("research/navigation-gaps-20261015/inventory.json", f"{inventory_bucket}[{index}]", f"inventory_status={old_status}, inventory_normalized_route={inventory_route!r}, audit_route={old_route!r}, route_source={route_source}"),
        ]
        if route in output_by_route:
            route_bucket = "routes" if current_route_kind == "route" else "aliases"
            ev.append(evidence(".scratch/pages-resources-20261015-v8/__offline/route-map.json", f"{route_bucket}[{route}]", f"maps_to={static_url}"))
        else:
            ev.append(evidence(".scratch/pages-resources-20261015-v8/__offline/route-map.json", "routes/aliases", f"no current mapping for {route or href!r}"))
        if page_exists:
            ev.append(evidence(rel(page_path), "file", f"bytes={page_bytes}, sha256={page_sha}"))
        if page_record:
            counts = page_record.get("reference_counts", {})
            ev.append(evidence(".scratch/pages-resources-20261015-v8/export-provenance.json", f"files[output_path={output_relative}]", f"role={page_record.get('role')}, reference_counts={counts}"))
        if dependency["critical_unresolved_count"]:
            ev.append(evidence(rel(page_path), "dependency-scan", f"critical unresolved refs={dependency['critical_unresolved_count']}; samples={dependency['unresolved_samples'][:3]}"))
        if scope == "legacy_reclassified":
            ev.append(evidence("research/navigation-gaps-20261015/inventory.json", f"excluded_entries[{index}].section", f"prior_scope_excluded_reason={legacy_reclassification_reason}; legacy source/menu record is re-audited against v8"))
        if scope == "scope_excluded":
            ev.append(evidence("research/navigation-gaps-20261015/inventory.json", "scope.excluded_sections", scope_reasons.get(entry.get("section"), "outside target sections")))
        if current_page_status == "business_or_sensitive":
            ev.append(evidence("research/continuous-recovery-20261015/sidebar-audit/audit_local.py", "BUSINESS_PATH_PREFIXES", f"route={route!r} classified as business_or_sensitive; no form or credential recovery"))
        if duplicate:
            ev.append(evidence(source_path, f"line {source_line}", f"duplicate source-role/menu-id={entry.get('source_role')}:{menu_id}"))

        return {
            "record_id": f"{scope}:{index}:{menu_id}",
            "scope": scope,
            "in_scope": scope == "in_scope",
            "effective_in_scope": scope != "scope_excluded",
            "prior_scope_excluded_reason": legacy_reclassification_reason if scope == "legacy_reclassified" else None,
            "source_menu": f"{source_path}:{source_line}",
            "source_path": source_path,
            "source_line": source_line,
            "source_role": entry.get("source_role"),
            "menu_id": menu_id,
            "label": label,
            "href": href,
            "section": entry.get("section"),
            "raw_line": entry.get("raw_line"),
            "inventory_status": old_status,
            "inventory_normalized_route": inventory_route,
            "route_source": route_source,
            "inventory_route_exists": coverage.get("route_exists"),
            "normalized_route": route,
            "current_route_kind": current_route_kind,
            "current_page_status": current_page_status,
            "resolved_path": rel(page_path) if page_exists else None,
            "resolved_static_url": static_url,
            "page_bytes": page_bytes,
            "page_sha256": page_sha,
            "page_provenance": page_record,
            "dependency_scan": dependency,
            "asset_status": asset_status,
            "asset_placeholder_count": placeholder_count,
            "interaction_status": interaction_status,
            "interaction_validation": "static_indication_only" if interaction_status != "not_available" else "not_available",
            "interaction_evidence": interaction_evidence,
            "gap_types": gap_types,
            "evidence": ev,
            "next_action": next_action,
            "priority": priority,
        }

    records = []
    for i, entry in enumerate(inventory.get("entries", [])):
        records.append(classify(entry, i, "in_scope"))
    excluded_start = len(inventory.get("entries", []))
    for i, entry in enumerate(inventory.get("excluded_entries", [])):
        # The original parser placed all legacy-menu observations in
        # excluded_entries.  They are now effective audit scope; only the
        # four explicit business/social sections remain genuinely excluded.
        scope_kind = "legacy_reclassified" if entry.get("section") == "Legacy menu" else "scope_excluded"
        records.append(classify(entry, i, scope_kind))

    original_in_scope_records = [r for r in records if r["scope"] == "in_scope"]
    legacy_records = [r for r in records if r["scope"] == "legacy_reclassified"]
    in_scope_records = [r for r in records if r["effective_in_scope"]]
    excluded_records = [r for r in records if not r["effective_in_scope"]]

    def counts_by(records_to_count, field):
        return dict(sorted(Counter(r.get(field) for r in records_to_count).items(), key=lambda item: str(item[0])))

    section_expected = inventory.get("summary", {}).get("sections", {})
    original_section_actual = dict(sorted(Counter(r.get("section") for r in original_in_scope_records).items(), key=lambda item: str(item[0])))
    section_actual = dict(sorted(Counter(r.get("section") for r in in_scope_records).items(), key=lambda item: str(item[0])))
    excluded_section_counts = dict(sorted(Counter(r.get("section") for r in excluded_records).items(), key=lambda item: str(item[0])))
    latest_status_by_section = {
        section: dict(sorted(Counter(r["current_page_status"] for r in in_scope_records if r.get("section") == section).items()))
        for section in sorted(section_actual)
    }
    asset_by_section = {
        section: dict(sorted(Counter(r["asset_status"] for r in in_scope_records if r.get("section") == section).items()))
        for section in sorted(section_actual)
    }

    active = [r for r in in_scope_records if r["gap_types"] and r["current_page_status"] not in {"resolved_recovered", "business_or_sensitive", "scope_excluded"}]
    historical_resolved = [r for r in in_scope_records if r["current_page_status"] == "resolved_recovered"]

    groups = defaultdict(list)
    for record in active:
        if "missing_page_or_route" in record["gap_types"]:
            target_value = record.get("normalized_route") or record.get("href")
            if isinstance(target_value, str) and target_value.startswith("/news/rss-"):
                target_value = "legacy_news_rss_archives"
            elif isinstance(target_value, str) and target_value.startswith("/news/wow-news"):
                target_value = "legacy_news_html_archives"
            key = ("missing_page_or_route", target_value)
        elif "missing_key_assets" in record["gap_types"]:
            key = ("missing_key_assets", record.get("resolved_path") or record.get("normalized_route"))
        elif "legacy_plugin_static_indication" in record["gap_types"]:
            key = ("legacy_plugin_static_indication", record.get("resolved_path") or record.get("normalized_route"))
        elif "external_or_dynamic_entry" in record["gap_types"]:
            key = ("external_or_dynamic_entry", record.get("href"))
        elif "source_menu_id_collision" in record["gap_types"]:
            key = ("source_menu_id_collision", f"{record.get('source_role')}:{record.get('menu_id')}" )
        else:
            key = ("route_alias_or_recovered", record.get("normalized_route"))
        groups[key].append(record)

    def suggestion_files(kind: str):
        if kind == "missing_key_assets":
            return [
                "research/resource-repair-20261015/build_pages_v7.py",
                "research/related-sites-20261014/integration/regional-image-source-map.json",
                "research/media-screenshots-20261015/late-image-source-map.json",
                "offline/approved-static-temporal-supplement-map.json",
            ]
        if kind == "legacy_plugin_static_indication":
            return [
                "research/resource-repair-20261015/build_pages_v7.py",
                "offline/approved-static-pre2008-supplement-map.json",
                "research/navigation-gaps-20261015/wayback-missing/effective-source-map-v7c.json",
            ]
        if kind == "external_or_dynamic_entry":
            return [
                "research/navigation-gaps-20261015/inventory.json",
                "offline/approved-expansion-map.json",
                "offline/approved-static-recovery-map.json",
            ]
        if kind == "missing_page_or_route":
            return [
                "research/navigation-gaps-20261015/build_v7c.py",
                "offline/approved-route-alias-overlay.json",
                "offline/approved-expansion-map.json",
            ]
        return [
            "research/navigation-gaps-20261015/build_v7c.py",
            "offline/approved-route-alias-overlay.json",
        ]

    proposals = []
    for number, ((kind, target), members) in enumerate(groups.items(), start=1):
        placeholder_observations = sum(r.get("asset_placeholder_count", 0) for r in members)
        # Repeated menu labels often point to the same page.  Rank a resource
        # gap by the unique page's maximum placeholder count and retain the
        # summed observation count separately.
        placeholder_total = max((r.get("asset_placeholder_count", 0) for r in members), default=0)
        priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
        priority = min((r["priority"] for r in members), key=lambda value: priority_order[value])
        labels = sorted({r.get("label") for r in members if r.get("label")})
        sections = sorted({r.get("section") for r in members if r.get("section")})
        if kind == "missing_key_assets":
            rationale = f"最新 v8 已有页面，但 provenance 标记 {placeholder_total} 个 placeholder；这是可验证的本地资源缺口。"
        elif kind == "legacy_plugin_static_indication":
            rationale = "页面仍含旧 Flash/插件依赖或替代外框；恢复 HTML 不等于恢复原交互。"
        elif kind == "external_or_dynamic_entry":
            rationale = "纳入恢复范围的菜单仍没有本地页面，href 是外部或动态入口；需要历史来源决策。"
        elif kind == "missing_page_or_route":
            rationale = "最新派生路由索引没有页面映射或文件，不能用假页面填充。"
        else:
            rationale = "源导航记录存在菜单 ID 或路由别名问题，需要下一次导航构建回归。"
        proposals.append(
            {
                "proposal_id": f"sidebar-{number:03d}",
                "status": "open",
                "priority": priority,
                "kind": kind,
                "target": target,
                "targets": sorted({r.get("normalized_route") or r.get("href") for r in members}),
                "menu_record_count": len(members),
                "menu_ids": sorted({r.get("menu_id") for r in members}),
                "labels": labels,
                "sections": sections,
                "placeholder_count": placeholder_total,
                "placeholder_observations": placeholder_observations,
                "rationale": rationale,
                "evidence": [ev for member in members[:3] for ev in member["evidence"][:4]],
                "suggested_files_only": suggestion_files(kind),
                "member_record_ids": [r["record_id"] for r in members],
            }
        )

    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
    proposals.sort(key=lambda p: (priority_order[p["priority"]], -p["placeholder_count"], -p["menu_record_count"], p["proposal_id"]))
    for i, proposal in enumerate(proposals, start=1):
        proposal["queue_rank"] = i

    historical_resolution_records = []
    for record in historical_resolved:
        historical_resolution_records.append(
            {
                "record_id": record["record_id"],
                "label": record["label"],
                "href": record["href"],
                "section": record["section"],
                "inventory_status": record["inventory_status"],
                "current_page_status": record["current_page_status"],
                "resolved_path": record["resolved_path"],
                "evidence": record["evidence"][:5],
            }
        )

    baseline_expected = final_acceptance.get("baseline_sha256")
    baseline_actual = sha256(FROZEN_MANIFEST)
    legacy_expected = sum(1 for entry in inventory.get("excluded_entries", []) if entry.get("section") == "Legacy menu")
    true_excluded_expected = (inventory.get("summary", {}).get("excluded_entry_count") or 0) - legacy_expected
    menu_conservation = {
        "original_in_scope_expected": inventory.get("summary", {}).get("entry_count"),
        "original_in_scope_observed": len(original_in_scope_records),
        "original_in_scope_conserved": len(original_in_scope_records) == inventory.get("summary", {}).get("entry_count"),
        "legacy_reclassified_expected": legacy_expected,
        "legacy_reclassified_observed": len(legacy_records),
        "legacy_reclassified_conserved": len(legacy_records) == legacy_expected,
        "effective_auditable_expected": (inventory.get("summary", {}).get("entry_count") or 0) + legacy_expected,
        "effective_auditable_observed": len(in_scope_records),
        "effective_auditable_conserved": len(in_scope_records) == (inventory.get("summary", {}).get("entry_count") or 0) + legacy_expected,
        "true_excluded_expected": true_excluded_expected,
        "true_excluded_observed": len(excluded_records),
        "true_excluded_conserved": len(excluded_records) == true_excluded_expected,
        "total_observed": len(records),
        "total_expected": (inventory.get("summary", {}).get("entry_count") or 0) + (inventory.get("summary", {}).get("excluded_entry_count") or 0),
        "total_conserved": len(records) == (inventory.get("summary", {}).get("entry_count") or 0) + (inventory.get("summary", {}).get("excluded_entry_count") or 0),
        "original_in_scope_by_section_expected": section_expected,
        "original_in_scope_by_section_observed": original_section_actual,
        "original_in_scope_by_section_conserved": section_expected == original_section_actual,
        "effective_auditable_by_section_observed": section_actual,
        "excluded_by_section_observed": excluded_section_counts,
    }

    audit = {
        "schema": "sidebar-local-audit/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "network_performed": False,
        "scope": {
            "inventory": rel(INVENTORY_PATH),
            "target_sections": inventory.get("scope", {}).get("target_sections", []),
            "excluded_sections": inventory.get("scope", {}).get("excluded_sections", {}),
            "legacy_reclassification": {
                "source_section": "Legacy menu",
                "prior_scope_excluded_reason": legacy_reclassification_reason,
                "observed_count": len(legacy_records),
                "treatment": "effective audit scope; compare against latest v8 route/page/resource evidence",
            },
            "latest_derived_site": rel(V8),
            "source_staging": ".scratch/offline-navigation-20261015-v7c",
        },
        "input_hashes": input_hashes,
        "frozen_baseline": {
            "manifest": rel(FROZEN_MANIFEST),
            "expected_sha256_from_acceptance": baseline_expected,
            "actual_sha256": baseline_actual,
            "unchanged": baseline_expected == baseline_actual,
        },
        "latest_build": {
            "final_acceptance": rel(FINAL_ACCEPTANCE),
            "accepted": final_acceptance.get("accepted"),
            "output_files": final_acceptance.get("output_files"),
            "source_records": final_acceptance.get("source_records"),
            "browser_counts": final_acceptance.get("browser_counts"),
            "unit_tests": final_acceptance.get("unit_tests"),
            "known_gaps": final_acceptance.get("known_gaps", []),
            "build_v8": v8_build,
            "v7c_receipt_stats": v7_receipt.get("stats", {}),
        },
        "menu_conservation": menu_conservation,
        "summary": {
            "effective_scope_counts": {
                "original_in_scope": len(original_in_scope_records),
                "legacy_reclassified": len(legacy_records),
                "effective_auditable": len(in_scope_records),
                "true_scope_excluded": len(excluded_records),
            },
            "current_page_status_counts": counts_by(in_scope_records, "current_page_status"),
            "inventory_status_counts": counts_by(in_scope_records, "inventory_status"),
            "asset_status_counts": counts_by(in_scope_records, "asset_status"),
            "interaction_status_counts": counts_by(in_scope_records, "interaction_status"),
            "gap_type_counts": dict(sorted(Counter(gap for r in in_scope_records for gap in r["gap_types"]).items())),
            "active_gap_record_count": len(active),
            "historical_resolved_record_count": len(historical_resolved),
            "open_proposal_count": len(proposals),
            "top_10_proposals": [p["proposal_id"] for p in proposals[:10]],
            "latest_status_by_section": latest_status_by_section,
            "asset_status_by_section": asset_by_section,
        },
        "records": records,
        "historical_resolutions": historical_resolution_records,
        "open_proposals": proposals,
    }

    audit_path = OUT / "audit.json"
    proposals_path = OUT / "repair-proposals.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    proposals_path.write_text(
        json.dumps(
            {
                "schema": "sidebar-repair-proposals/v1",
                "generated_from": rel(audit_path),
                "network_performed": False,
                "proposals": proposals,
                "top_10": proposals[:10],
                "historical_resolutions": historical_resolution_records,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    top_lines = []
    for p in proposals[:10]:
        top_lines.append(
            f"- `{p['proposal_id']}` {p['priority']} `{p['kind']}` {p['target']}；菜单 {p['menu_record_count']} 条；placeholder {p['placeholder_count']}；{p['rationale']}"
        )
    md = f"""# Sidebar local audit (2026-10-15)\n\n本审计只读取本地输入，未执行网络请求。逐条记录来自 `{rel(INVENTORY_PATH)}`；原始纳入范围 588 条，原始排除 653 条，总账 1241 条。其中 `Legacy menu` 的 579 条被标记为 `{legacy_reclassification_reason}` 并重新纳入有效审计；真正范围外记录为 74 条。当前页面与资源判定按 `.scratch/pages-resources-20261015-v8` 及其 `__offline/route-map.json`、`export-provenance.json` 计算。\n\n## Conservation and inputs\n\n- Menu conservation: original in-scope {menu_conservation['original_in_scope_observed']}/{menu_conservation['original_in_scope_expected']}; legacy reclassified {menu_conservation['legacy_reclassified_observed']}/{menu_conservation['legacy_reclassified_expected']}; effective auditable {menu_conservation['effective_auditable_observed']}/{menu_conservation['effective_auditable_expected']}; true excluded {menu_conservation['true_excluded_observed']}/{menu_conservation['true_excluded_expected']}; total {menu_conservation['total_observed']}/{menu_conservation['total_expected']}.\n- Original section conservation: {menu_conservation['original_in_scope_by_section_observed']} == {menu_conservation['original_in_scope_by_section_expected']}.\n- Effective auditable section counts: {menu_conservation['effective_auditable_by_section_observed']}.\n- True excluded section counts: {excluded_section_counts}.\n- Frozen `offline/build-manifest.json`: `{baseline_actual}`; acceptance expected `{baseline_expected}`; unchanged={baseline_actual == baseline_expected}.\n- Latest v8 acceptance: accepted={final_acceptance.get('accepted')}, output_files={final_acceptance.get('output_files')}, browser scenarios={final_acceptance.get('browser_counts', {}).get('scenarios')}, passed={final_acceptance.get('browser_counts', {}).get('passedScenarios')}, unit tests={final_acceptance.get('unit_tests', {}).get('tests_run')} with failures={final_acceptance.get('unit_tests', {}).get('failures')}.\n\n## Current effective audit status\n\n- Page status: `{counts_by(in_scope_records, 'current_page_status')}`\n- Asset status: `{counts_by(in_scope_records, 'asset_status')}`\n- Interaction status: `{counts_by(in_scope_records, 'interaction_status')}`\n- Inventory status retained for history: `{counts_by(in_scope_records, 'inventory_status')}`\n- Open gap records: {len(active)}; historical records recovered by v8: {len(historical_resolved)}.\n\n`resolved_recovered` means the old inventory marked the entry external/dynamic or missing, while the current v8 route and page are present. It is retained in `historical_resolutions` and is not counted as an open gap. `scope_excluded` records are accounted for but are not treated as missing pages.\n\n## Highest-value open proposals\n\n{chr(10).join(top_lines) if top_lines else '- None.'}\n\n## Group status by section\n\n"""
    for section in sorted(section_actual):
        md += f"- `{section}`: {section_actual[section]} records; page `{latest_status_by_section[section]}`; assets `{asset_by_section[section]}`.\n"
    md += f"""\n## Evidence and use\n\nEvery record in `audit.json` carries the source menu path and line, the inventory index, current route-map result, resolved file hash when present, and provenance/dependency evidence when available. `repair-proposals.json` contains suggestions only; no production map, frozen source, build script, test, or deployment file was edited.\n\nKnown v8 acceptance gaps retained as context: {final_acceptance.get('known_gaps', [])}.\n"""
    (OUT / "audit.md").write_text(md, encoding="utf-8")

    print(json.dumps({
        "audit": rel(audit_path),
        "audit_bytes": audit_path.stat().st_size,
        "proposals": rel(proposals_path),
        "proposals_count": len(proposals),
        "records": len(records),
        "in_scope": len(in_scope_records),
        "excluded": len(excluded_records),
        "active_gap_records": len(active),
        "historical_resolved": len(historical_resolved),
        "top_10": [
            {"id": p["proposal_id"], "priority": p["priority"], "kind": p["kind"], "target": p["target"], "menu_record_count": p["menu_record_count"], "placeholder_count": p["placeholder_count"]}
            for p in proposals[:10]
        ],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
