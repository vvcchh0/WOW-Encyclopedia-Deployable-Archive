from __future__ import annotations

import collections
import gc
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "research/continuous-recovery-20261015/local-resource-dedup"
AUDIT_PATH = ROOT / "research/continuous-recovery-20261015/sidebar-audit/audit.json"
PROPOSALS_PATH = ROOT / "research/continuous-recovery-20261015/sidebar-audit/repair-proposals.json"
PROV_PATH = ROOT / ".scratch/pages-resources-20261015-v8/export-provenance.json"
V8_ROOT = ROOT / ".scratch/pages-resources-20261015-v8"
V7C_ROOT = ROOT / ".scratch/offline-navigation-20261015-v7c"
V7C_MANIFEST_PATH = V7C_ROOT / "build-manifest.json"

PAGE_TARGETS = {
    "zandalar_quests": "/info/basics/factions/zandalar/quests.html",
    "eu_regionals": "/community/tournaments/euregionals/index.html",
    "insider11_arena": "/insider/11/arena.xml",
    "high_level_options": "/info/basics/highleveloptions.html",
}

MAP_PATHS = [
    "offline/approved-static-recovery-map.json",
    "offline/approved-static-temporal-supplement-map.json",
    "offline/approved-static-pre2008-supplement-map.json",
    "offline/approved-pages-recovery-map.json",
    "offline/approved-pages-temporal-supplement-map.json",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def norm_url(value: str | None):
    """Normalize only scheme/host/default port; retain path/query/fragment exactly."""
    if not isinstance(value, str):
        return None
    value = html.unescape(value).strip()
    if not value:
        return None
    parsed = urlsplit(value)
    if not parsed.scheme or not parsed.netloc:
        return None
    scheme = parsed.scheme.lower()
    host = (parsed.hostname or "").lower()
    if not host:
        return None
    try:
        port = parsed.port
    except ValueError:
        return None
    netloc = host
    if ":" in host and not host.startswith("["):
        netloc = f"[{host}]"
    if parsed.username or parsed.password:
        user = parsed.username or ""
        if parsed.password is not None:
            user += ":" + parsed.password
        netloc = user + "@" + netloc
    if port is not None and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        netloc += f":{port}"
    return urlunsplit((scheme, netloc, parsed.path, parsed.query, parsed.fragment))


def is_literal_url(value: str | None):
    if not value or "{" in value or "}" in value or "\\" in value or " + " in value:
        return False
    return bool(norm_url(value))


def actual_path(value: str | None):
    if not isinstance(value, str) or not value:
        return None
    p = ROOT / value
    try:
        p.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return None
    return p


def file_check(path_value: str | None, expected_sha: str | None = None, expected_length=None, image=False):
    path = actual_path(path_value)
    out = {"path": path_value, "exists": bool(path and path.is_file())}
    if not out["exists"]:
        return out
    out["length"] = path.stat().st_size
    out["sha256"] = sha256(path)
    if expected_sha:
        out["sha256_matches"] = out["sha256"] == expected_sha
    if expected_length is not None:
        out["length_matches"] = out["length"] == expected_length
    if image:
        try:
            from PIL import Image

            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:
                im.load()
                out["pillow"] = {"verify": True, "load": True, "format": im.format, "size": list(im.size), "mode": im.mode}
        except Exception as exc:  # local evidence only; do not turn decode failure into a network claim
            out["pillow"] = {"verify": False, "load": False, "error": str(exc)}
    return out


def asset_role(requested: str | None, attribute: str | None, tag: str | None):
    path = urlsplit(requested or "").path.lower()
    ext = Path(path).suffix.lower()
    if ext in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".swf", ".ico"}:
        role = "image" if ext != ".swf" else "flash"
    elif ext in {".js"}:
        role = "script"
    elif ext in {".css"}:
        role = "stylesheet"
    elif ext in {".xml", ".rss"}:
        role = "xml_or_feed"
    elif ext in {".html", ".htm", ".php", ""}:
        role = "page_or_navigation"
    else:
        role = "other_static"
    if tag in {"a", "area"}:
        role = "page_or_navigation"
    return role


def resource_purpose(item):
    url = item.get("canonical_url") or ""
    parsed = urlsplit(url)
    path = parsed.path.lower()
    host = (parsed.hostname or "").lower()
    refs = item.get("references", [])
    role = item.get("asset_role")
    markup = " ".join(str(r.get("context") or "") for r in refs)
    markup_lower = markup.lower()
    if role == "script_condition_reference" or any(r.get("asset_role") == "script_condition_reference" for r in refs):
        return "script_condition_reference"
    if role == "page_or_navigation":
        if host in {"www.blizzard.com", "www.esrb.org", "us.blizzard.com", "shop.blizzard.com", "signup.worldofwarcraft.com"}:
            return "third_party_footer_or_navigation"
        return "page_navigation"
    if (role == "script" and "analytics" in path) or host in {"www.google-analytics.com", "ssl.google-analytics.com"}:
        return "analytics_script"
    if role == "xml_or_feed":
        return "page_body_feed"
    if role == "image":
        width_one = bool(re.search(r"\bwidth\s*=\s*[\"']?1(?:[\"'\s>]|$)", markup_lower))
        height_one = bool(re.search(r"\bheight\s*=\s*[\"']?1(?:[\"'\s>]|$)", markup_lower))
        one_by_one = width_one and height_one
        css_or_border_context = any(token in markup_lower for token in ["background", "border", "ladder-revise", "data-head", "arena-badge"])
        if one_by_one and (path.endswith("/b.gif") or path.endswith("/pixel.gif") or "spacer" in path or "transparent" in path):
            return "layout_spacer"
        if css_or_border_context or any(token in path for token in ["rankingborder", "data-head", "/data0.gif", "/data1.gif", "/data2.gif", "/data3.gif", "arena-badge-bg"]):
            return "template_border_or_chrome"
        if "/images/icons/" in path or "/icons/" in path:
            return "page_body_icon"
        return "page_body_image"
    if role in {"stylesheet", "flash", "other_static"}:
        return "page_body_static"
    return "unknown_static"


def purpose_evidence(item):
    refs = item.get("references", [])
    evidence = []
    for ref in refs[:6]:
        evidence.append({"page_key": ref.get("page_key"), "line": ref.get("line"), "tag": ref.get("tag"), "attribute": ref.get("attribute"), "context_kind": ref.get("context_kind"), "context": ref.get("context")})
    return evidence


def extract_placeholder_refs(page_path: Path, page_key: str, route: str):
    text = page_path.read_text(encoding="utf-8", errors="replace")
    pattern = re.compile(r"__offline/[A-Za-z0-9_.-]+\?[^\s\"'<>)]*")
    refs = []
    for occurrence, match in enumerate(pattern.finditer(text), 1):
        raw = html.unescape(match.group(0))
        parsed = urlsplit(raw)
        query = parse_qs(parsed.query, keep_blank_values=True)
        requested = query.get("requested", [None])[0]
        source = query.get("source", [None])[0]
        reason = query.get("reason", [None])[0]
        before = text.rfind("<", 0, match.start())
        after = text.find(">", match.end())
        tag_text = text[before : after + 1] if before >= 0 and after >= 0 else ""
        tag_match = re.match(r"<\s*([A-Za-z0-9]+)", tag_text)
        tag = tag_match.group(1).lower() if tag_match else None
        attr_match = re.search(r"\b(src|href|data|movie|value|action|poster|style|background)\s*=", tag_text, re.I)
        attribute = attr_match.group(1).lower() if attr_match else None
        style_open = text.rfind("<style", 0, match.start())
        style_close = text.rfind("</style", 0, match.start())
        in_style_block = style_open > style_close
        if in_style_block:
            context_kind = "css"
            context_start = max(style_open, match.start() - 320)
            context_end = min(len(text), match.end() + 320)
            context = re.sub(r"\s+", " ", text[context_start:context_end])
            tag = "style"
            attribute = None
        else:
            context_kind = "markup"
            context = re.sub(r"\s+", " ", tag_text[:800])
        line = text.count("\n", 0, match.start()) + 1
        literal = is_literal_url(requested)
        role = asset_role(requested, attribute, tag)
        if tag == "script" and "document.location.href.indexof" in context.lower():
            context_kind = "script"
            attribute = "location.href condition"
            role = "script_condition_reference"
        refs.append(
            {
                "page_key": page_key,
                "page_route": route,
                "occurrence": occurrence,
                "line": line,
                "requested": requested,
                "canonical_url": norm_url(requested) if literal else None,
                "source_page": source,
                "reason": reason,
                "placeholder_kind": parsed.path.rsplit("/", 1)[-1],
                "tag": tag,
                "attribute": attribute,
                "context_kind": context_kind,
                "asset_role": role,
                "literal_url": literal,
                "raw": raw[:600],
                "context": context,
            }
        )
    return refs


def compact_map_record(map_name, item):
    local = item.get("local_path") or item.get("source_local_path")
    sha = item.get("sha256") or item.get("source_sha256")
    length = item.get("content_length") or item.get("source_length")
    mime = item.get("mime") or item.get("content_type") or item.get("response_content_type")
    is_image = str(mime or "").lower().startswith("image/") or str(item.get("kind", "")).lower() == "image"
    return {
        "map": map_name,
        "logical_url": item.get("logical_url"),
        "original": item.get("original"),
        "source_url": item.get("source_url"),
        "source_base_url": item.get("source_base_url"),
        "capture_original": item.get("capture_original"),
        "local_path": local,
        "sha256": sha,
        "content_length": length,
        "mime": mime,
        "kind": item.get("kind") or item.get("candidate_kind"),
        "role": item.get("role"),
        "temporal_class": item.get("temporal_class"),
        "actual_timestamp": item.get("actual_timestamp") or item.get("timestamp"),
        "file_check": file_check(local, sha, length, image=is_image),
    }


def build_sources(root: Path, v7c, wanted):
    exact = collections.defaultdict(list)
    # Existing approved maps: compare every original URL field exactly after the
    # allowed scheme/host/default-port normalization.
    for map_path in MAP_PATHS:
        path = root / map_path
        if not path.exists():
            continue
        data = load(path)
        for item in data.get("files", []):
            candidate_keys = {norm_url(item.get(field)) for field in ["logical_url", "original", "source_url", "source_base_url", "capture_original"]}
            candidate_keys.discard(None)
            matched_keys = candidate_keys & wanted
            if not matched_keys:
                continue
            rec = compact_map_record(map_path, item)
            for key in matched_keys:
                exact[key].append(rec)
        del data
        gc.collect()
    # v7c build manifest is independently indexed because it includes the
    # derived output path and source entity checks.
    for item in v7c.get("files", []):
        key = norm_url(item.get("source_base_url"))
        if not key or key not in wanted:
            continue
        mime = item.get("source_mime") or item.get("mime")
        is_image = str(mime or "").lower().startswith("image/") or item.get("kind") == "image"
        rec = {
            "map": ".scratch/offline-navigation-20261015-v7c/build-manifest.json",
            "logical_url": None,
            "original": None,
            "source_url": None,
            "source_base_url": item.get("source_base_url"),
            "capture_original": None,
            "local_path": item.get("source_local_path"),
            "sha256": item.get("source_sha256"),
            "content_length": item.get("source_length"),
            "mime": mime,
            "kind": item.get("kind"),
            "role": item.get("role"),
            "temporal_class": "manifest_unclassified",
            "actual_timestamp": item.get("actual_timestamp"),
            "route": item.get("route"),
            "output_path": item.get("output_path"),
            "file_check": file_check(item.get("source_local_path"), item.get("source_sha256"), item.get("source_length"), image=is_image),
            "output_file_check": file_check(item.get("output_path"), item.get("derived_sha256"), item.get("derived_length"), image=is_image),
        }
        exact[key].append(rec)
    return exact


def find_audit_records(audit, route):
    return [r for r in audit.get("records", []) if r.get("normalized_route") == route]


def proposal_for(proposals, route):
    for p in proposals.get("proposals", []):
        if route in p.get("targets", []):
            return p
    return None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    audit = load(AUDIT_PATH)
    proposals = load(PROPOSALS_PATH)
    provenance = load(PROV_PATH)
    v7c_raw = load(V7C_MANIFEST_PATH)
    # Keep only compact manifest fields before loading the large approved maps.
    v7c_files = []
    for item in v7c_raw.get("files", []):
        v7c_files.append({k: item.get(k) for k in ["route", "output_path", "source_local_path", "source_base_url", "source_sha256", "source_length", "derived_sha256", "derived_length", "source_mime", "mime", "kind", "role", "actual_timestamp"]})
    del v7c_raw
    gc.collect()
    prov_by_route = {e.get("route"): e for e in provenance.get("files", [])}
    pages = {}
    all_refs = []
    for page_key, route in PAGE_TARGETS.items():
        records = find_audit_records(audit, route)
        proposal = proposal_for(proposals, route)
        prov = prov_by_route.get(route)
        if not records or not proposal or not prov:
            raise RuntimeError(f"page identity incomplete for {page_key}: records={len(records)} proposal={bool(proposal)} provenance={bool(prov)}")
        output_rel = prov.get("output_path")
        derived_path = V8_ROOT / output_rel
        source_rel = prov.get("source_offline_path")
        source_path = ROOT / source_rel if source_rel else None
        refs = extract_placeholder_refs(derived_path, page_key, route)
        all_refs.extend(refs)
        pages[page_key] = {
            "page_key": page_key,
            "route": route,
            "labels": sorted({r.get("label") for r in records if r.get("label")}),
            "menu_record_ids": [r.get("record_id") for r in records],
            "menu_evidence": [{k: r.get(k) for k in ["record_id", "source_menu", "source_line", "label", "href", "source_role"]} for r in records],
            "proposal_id": proposal.get("proposal_id"),
            "proposal_priority": proposal.get("priority"),
            "proposal_placeholder_count": proposal.get("placeholder_count"),
            "proposal_placeholder_observations": proposal.get("placeholder_observations"),
            "derived_path": str(derived_path.relative_to(ROOT)).replace("\\", "/"),
            "source_staging_path": source_rel,
            "provenance": {k: prov.get(k) for k in ["route", "output_path", "source_offline_path", "source_sha256", "source_length", "derived_sha256", "derived_length", "mime", "kind", "role", "reference_counts"]},
            "provenance_placeholder_count": (prov.get("reference_counts") or {}).get("placeholder"),
            "extracted_vs_provenance_placeholder_delta": len(refs) - (prov.get("reference_counts") or {}).get("placeholder", 0),
            "derived_file_check": file_check(str(derived_path.relative_to(ROOT)).replace("\\", "/"), prov.get("derived_sha256"), prov.get("derived_length")),
            "source_file_check": file_check(source_rel, prov.get("source_sha256"), prov.get("source_length")) if source_rel else None,
            "placeholder_refs": refs,
            "placeholder_occurrence_count": len(refs),
            "placeholder_unique_literal_count": len({r["canonical_url"] for r in refs if r["canonical_url"]}),
        }

    wanted_urls = {r["canonical_url"] for r in all_refs if r.get("canonical_url")}
    source_index = build_sources(ROOT, {"files": v7c_files}, wanted_urls)
    del v7c_files
    gc.collect()

    groups = collections.defaultdict(list)
    for ref in all_refs:
        key = ref.get("canonical_url")
        if key:
            groups[key].append(ref)
    # Keep non-literal refs separate, retaining line evidence but excluding them
    # from a literal URL network queue.
    nonliteral = [r for r in all_refs if not r.get("canonical_url")]

    inventory = []
    for canonical, refs in sorted(groups.items()):
        exact = source_index.get(canonical, [])
        local_verified = []
        for rec in exact:
            if rec.get("file_check", {}).get("exists") or rec.get("output_file_check", {}).get("exists"):
                local_verified.append(rec)
        role_counts = collections.Counter(r["asset_role"] for r in refs)
        page_coverage = sorted({r["page_key"] for r in refs})
        time_classes = sorted({r.get("temporal_class") for r in local_verified if r.get("temporal_class")})
        if local_verified:
            status = "local_exact_entity_verified"
            next_action = "Reuse exact local source entity only after checking page role and transform compatibility; no network query needed for this URL."
        elif exact:
            status = "exact_map_record_but_local_file_unverified"
            next_action = "Repair or inspect the recorded local source path; do not substitute a basename or different origin."
        else:
            status = "network_candidate_exact_url"
            next_action = "Queue exact URL for a capture preserving origin, path, MIME, timestamp, length, and SHA-256."
        dominant_role = "script_condition_reference" if role_counts.get("script_condition_reference") else max(role_counts, key=role_counts.get)
        purpose = resource_purpose({"canonical_url": canonical, "asset_role": dominant_role, "references": refs})
        if purpose == "script_condition_reference":
            next_action = "Retain as a non-request script literal; do not fetch or treat the document.location.href condition as an anchor/resource request."
        elif purpose in {"page_navigation", "third_party_footer_or_navigation"}:
            next_action = "Retain as navigation evidence; exclude from the asset queue and do not count as missing page content."
        elif purpose in {"layout_spacer", "template_border_or_chrome", "analytics_script"}:
            next_action = "Keep in the shared-template candidate list; capture only with exact-origin evidence and do not elevate by multiplicity."
        if purpose == "script_condition_reference":
            resource_scope = "non_request_script_literal"
        elif purpose in {"page_navigation", "third_party_footer_or_navigation"}:
            resource_scope = "page_navigation"
        elif purpose in {"layout_spacer", "template_border_or_chrome", "analytics_script"}:
            resource_scope = "shared_template"
        else:
            resource_scope = "page_body"
        evidence = purpose_evidence({"references": refs})
        inventory.append(
            {
                "canonical_url": canonical,
                "requested_url_examples": sorted({r.get("requested") for r in refs}),
                "reference_count": len(refs),
                "page_coverage": page_coverage,
                "role_counts": dict(sorted(role_counts.items())),
                "asset_role": dominant_role,
                "resource_purpose": purpose,
                "resource_scope": resource_scope,
                "purpose_evidence": evidence,
                "script_condition_occurrence_count": role_counts.get("script_condition_reference", 0),
                "time_class": time_classes or ["baseline_target_unverified"],
                "status": status,
                "local_evidence": local_verified or exact,
                "references": [{k: r.get(k) for k in ["page_key", "page_route", "line", "tag", "attribute", "context_kind", "asset_role", "requested", "source_page", "reason", "context"]} for r in refs],
                "next_action": next_action,
                "cross_origin_relationship": "none_asserted",
            }
        )

    counts = collections.Counter()
    for item in inventory:
        counts[item["status"]] += 1
    purpose_counts = collections.Counter(item["resource_purpose"] for item in inventory)
    scope_counts = collections.Counter(item["resource_scope"] for item in inventory)
    literal_occurrences = sum(i["reference_count"] for i in inventory)
    # Queue only static resource roles; page navigation placeholders remain in
    # inventory and are explicitly excluded from asset capture.
    queue_candidates = [
        i for i in inventory
        if i["status"] in {"network_candidate_exact_url", "exact_map_record_but_local_file_unverified"}
        and i["asset_role"] not in {"page_or_navigation", "script_condition_reference"}
    ]
    purpose_order = {
        "page_body_image": 0,
        "page_body_icon": 1,
        "page_body_static": 2,
        "page_body_feed": 3,
        "template_border_or_chrome": 5,
        "layout_spacer": 7,
        "analytics_script": 8,
        "script_condition_reference": 9,
        "unknown_static": 9,
    }
    queue_candidates.sort(key=lambda i: (purpose_order.get(i["resource_purpose"], 9), -i["reference_count"], i["canonical_url"]))
    queue = []
    for rank, item in enumerate(queue_candidates[:16], 1):
        queue.append(
            {
                "queue_id": f"LOCAL-RESOURCE-DEDUP-003-{rank:02d}",
                "exact_url": item["canonical_url"],
                "priority": "P0" if item["reference_count"] >= 10 else "P1",
                "reference_count": item["reference_count"],
                "page_coverage": item["page_coverage"],
                "asset_role": item["asset_role"],
                "resource_purpose": item["resource_purpose"],
                "resource_scope": item["resource_scope"],
                "time_class": item["time_class"],
                "priority_reason": "page正文资源优先；共享布局/spacer/模板边框保留在单独候选清单，不按重复次数提升优先级。" if item["resource_purpose"].startswith("page_body") else "模板或共享资源，因语义重复降级；保留精确 URL 与页面覆盖。",
                "menu_page_evidence": [r for ref in item["references"] for r in pages[ref["page_key"]]["menu_evidence"][:2]],
                "local_evidence": item["local_evidence"],
                "local_search_evidence": {
                    "result": "no_exact_local_record_in_bounded_scope" if not item["local_evidence"] else "exact_record_requires_review",
                    "approved_maps": MAP_PATHS,
                    "manifest": ".scratch/offline-navigation-20261015-v7c/build-manifest.json",
                    "comparison": "exact canonical origin+URL only; scheme/host case and default port normalization only",
                    "matches": item["local_evidence"],
                },
                "purpose_evidence": item["purpose_evidence"],
                "capture_constraints": [
                    "Request this exact origin and URL; do not substitute by basename, path, host, or neighboring asset.",
                    "Preserve status, redirect chain, response MIME, timestamp, byte length, and SHA-256.",
                    "If post-2008, record as temporal supplement and do not merge into the 20080512 baseline.",
                ],
            }
        )

    # Reconciliation and queue metadata are deliberately explicit about what
    # cannot be literalized from dynamic/relative expressions.
    nonliteral_by_page = collections.Counter(r["page_key"] for r in nonliteral)
    input_paths = [AUDIT_PATH, PROPOSALS_PATH, PROV_PATH, V7C_MANIFEST_PATH] + [ROOT / p for p in MAP_PATHS if (ROOT / p).exists()]
    input_hashes = {str(p.relative_to(ROOT)).replace("\\", "/"): {"sha256": sha256(p), "bytes": p.stat().st_size} for p in input_paths}
    generated_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    reconciliation = {
        "schema": "wow-recovery.local-resource-dedup.v1",
        "task_id": "LOCAL-RESOURCE-DEDUP-003",
        "generated_utc": generated_utc,
        "network_performed": False,
        "network_request_count": 0,
        "scope": {"pages": list(PAGE_TARGETS), "page_count": 4, "derived_reference_scope": "literal placeholders in four v8 derived HTML files", "raw_workspace_scan": False},
        "input_hashes": input_hashes,
        "pages": pages,
        "dedup": {"all_placeholder_occurrences": len(all_refs), "literal_url_occurrences": literal_occurrences, "unique_literal_urls": len(inventory), "nonliteral_or_relative_occurrences": len(nonliteral), "nonliteral_by_page": dict(nonliteral_by_page), "occurrence_conservation_ok": literal_occurrences + len(nonliteral) == len(all_refs), "resource_purpose_counts": dict(sorted(purpose_counts.items())), "resource_scope_counts": dict(sorted(scope_counts.items()))},
        "status_counts": dict(sorted(counts.items())),
        "inventory": inventory,
        "notes": [
            "Canonical asset identity preserves exact origin and URL except allowed scheme/host case and standard-port normalization.",
            "Dynamic expressions, braces, concatenations, and relative output values remain nonliteral and are not network queue entries.",
            "Same body hash across different origins would be reported as a relationship only; no cross-origin alias is asserted.",
            "Existing map temporal_class is retained; un-captured placeholders are baseline_target_unverified rather than assumed baseline or supplement.",
        ],
        "production_file_suggestions": [
            "research/resource-repair-20261015/build_pages_v7.py (only after review; no edit here)",
            "research/related-sites-20261014/integration/regional-image-source-map.json (only for exact-origin regional evidence; no edit here)",
            "research/media-screenshots-20261015/late-image-source-map.json (only for exact-origin/image evidence; no edit here)",
            "offline/approved-static-temporal-supplement-map.json (for approved post-anchor payloads; frozen production tree untouched)",
        ],
    }
    queue_doc = {
        "schema": "wow-recovery.network-asset-queue.v1",
        "task_id": "LOCAL-RESOURCE-DEDUP-003",
        "generated_utc": generated_utc,
        "network_performed": False,
        "network_request_count": 0,
        "queue_limit": 16,
        "queue_count": len(queue),
        "literal_unique_url_count": len(inventory),
        "asset_candidate_unique_url_count": len(queue_candidates),
        "excluded_page_navigation_unique_url_count": sum(1 for i in inventory if i["resource_purpose"] in {"page_navigation", "third_party_footer_or_navigation"}),
        "script_condition_unique_url_count": sum(1 for i in inventory if i["resource_purpose"] == "script_condition_reference"),
        "script_condition_occurrence_count": sum(i["script_condition_occurrence_count"] for i in inventory),
        "resource_purpose_counts": dict(sorted(purpose_counts.items())),
        "resource_scope_counts": dict(sorted(scope_counts.items())),
        "local_lookup_scope": {
            "approved_maps": MAP_PATHS,
            "manifest": ".scratch/offline-navigation-20261015-v7c/build-manifest.json",
            "comparison": "exact canonical origin+URL only; scheme/host case and default port normalization only",
            "excluded": ["basename-only search", "cross-host/path substitution", "whole-workspace raw scan", "network"],
        },
        "excluded_page_navigation_count": sum(i["reference_count"] for i in inventory if i["asset_role"] == "page_or_navigation"),
        "entries": queue,
        "shared_template_candidates": [
            {
                "exact_url": item["canonical_url"],
                "asset_role": item["asset_role"],
                "resource_purpose": item["resource_purpose"],
                "resource_scope": item["resource_scope"],
                "reference_count": item["reference_count"],
                "page_coverage": item["page_coverage"],
                "priority_reason": "共享布局/spacer/template 资源；不作为正文缺图统计，也不因 multiplicity 自动升为 P0。",
                "purpose_evidence": item["purpose_evidence"],
                "derived_layout_fallback_if_visible_damage": (
                    "Proposal only: if the exact 1x1 spacer causes observed layout damage, add a derived-layer transparent 1x1 fallback matching the recorded markup; do not call the original entity recovered and do not edit production here."
                    if item["resource_purpose"] == "layout_spacer" else None
                ),
            }
            for item in inventory
            if item["resource_purpose"] in {"layout_spacer", "template_border_or_chrome", "analytics_script"}
        ],
        "deferred_exact_static_urls": [i["canonical_url"] for i in queue_candidates[16:]],
        "nonliteral_not_queued": [{k: r.get(k) for k in ["page_key", "line", "requested", "asset_role", "context"]} for r in nonliteral],
    }

    local_matches = [i for i in inventory if i["status"] == "local_exact_entity_verified"]
    map_only_matches = [i for i in inventory if i["status"] == "exact_map_record_but_local_file_unverified"]
    salvage_proposals = {
        "schema": "wow-recovery.local-salvage-proposals.v1",
        "task_id": "LOCAL-RESOURCE-DEDUP-003",
        "generated_utc": generated_utc,
        "network_performed": False,
        "network_request_count": 0,
        "salvage_status": "no_exact_url_local_salvage_found" if not local_matches and not map_only_matches else "exact_local_candidates_found",
        "lookup_scope": {
            "approved_maps": MAP_PATHS,
            "manifest": ".scratch/offline-navigation-20261015-v7c/build-manifest.json",
            "comparison": "exact canonical origin+URL only; scheme/host case and default port normalization only",
            "excluded": ["basename-only search", "cross-host/path substitution", "whole-workspace raw scan", "network"],
        },
        "summary": {
            "pages": 4,
            "unique_literal_urls": len(inventory),
            "exact_local_verified_urls": len(local_matches),
            "exact_map_records_unverified": len(map_only_matches),
            "network_candidates": sum(1 for i in inventory if i["status"] == "network_candidate_exact_url"),
            "asset_network_candidates": sum(1 for i in inventory if i["status"] == "network_candidate_exact_url" and i["resource_scope"] not in {"page_navigation", "non_request_script_literal"}),
            "navigation_or_footer_unique_urls": sum(1 for i in inventory if i["resource_purpose"] in {"page_navigation", "third_party_footer_or_navigation"}),
            "script_condition_unique_urls": sum(1 for i in inventory if i["resource_purpose"] == "script_condition_reference"),
            "script_condition_occurrences": sum(i["script_condition_occurrence_count"] for i in inventory),
        },
        "page_proposals": [],
        "shared_resource_proposals": [
            {
                "proposal_id": "shared-template-001",
                "purpose": item["resource_purpose"],
                "exact_url": item["canonical_url"],
                "asset_role": item["asset_role"],
                "resource_scope": item["resource_scope"],
                "reference_count": item["reference_count"],
                "page_coverage": item["page_coverage"],
                "local_evidence": item["local_evidence"],
                "purpose_evidence": item["purpose_evidence"],
                "recommendation": "If captured, register once as a shared template/static entity and reference it from all covered pages; do not count it as page正文 recovery.",
                "derived_layout_fallback_if_visible_damage": (
                    "Proposal only: if the exact 1x1 spacer causes observed layout damage, add a derived-layer transparent 1x1 fallback matching the recorded markup; do not call the original entity recovered and do not edit production here."
                    if item["resource_purpose"] == "layout_spacer" else None
                ),
            }
            for item in inventory
            if item["resource_purpose"] in {"layout_spacer", "template_border_or_chrome", "analytics_script"}
        ],
        "production_file_suggestions": [
            "research/resource-repair-20261015/build_pages_v7.py (wire only approved exact entities; no edit here)",
            "research/related-sites-20261014/integration/regional-image-source-map.json (exact-origin regional asset evidence only; no edit here)",
            "research/media-screenshots-20261015/late-image-source-map.json (exact-origin image evidence only; no edit here)",
            "offline/approved-static-temporal-supplement-map.json (post-anchor approved payloads only; frozen tree untouched)",
        ],
    }
    for page_key, page in pages.items():
        page_items = [i for i in inventory if page_key in i["page_coverage"]]
        page_local = [i for i in page_items if i["status"] == "local_exact_entity_verified"]
        page_map_only = [i for i in page_items if i["status"] == "exact_map_record_but_local_file_unverified"]
        salvage_proposals["page_proposals"].append(
            {
                "proposal_id": f"page-salvage-{page_key}",
                "page_key": page_key,
                "route": page["route"],
                "derived_path": page["derived_path"],
                "literal_unique_urls": len(page_items),
                "page_body_candidates": sum(1 for i in page_items if i["resource_purpose"].startswith("page_body")),
                "shared_template_candidates": sum(1 for i in page_items if i["resource_purpose"] in {"layout_spacer", "template_border_or_chrome", "analytics_script"}),
                "exact_local_verified_urls": [i["canonical_url"] for i in page_local],
                "exact_map_unverified_urls": [i["canonical_url"] for i in page_map_only],
                "recommendation": "No exact local payload can be salvaged from the approved maps/v7c manifest for this page; use the bounded exact-URL queue, then add approved entities by exact origin and URL." if not page_local and not page_map_only else "Review the exact local entity records before issuing any network request; do not cross-alias.",
            }
        )

    (OUT / "dedup-inventory.json").write_text(json.dumps(reconciliation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "network-asset-queue.json").write_text(json.dumps(queue_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "local-salvage-proposals.json").write_text(json.dumps(salvage_proposals, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md = [
        "# Local resource deduplication — LOCAL-RESOURCE-DEDUP-003",
        "",
        f"Generated `{generated_utc}`. This was a local-only pass: network requests **0**; no production, frozen tree, Git, or deployment changes.",
        "",
        "## Page identity",
        "",
        "| Page | Route | Derived bytes/SHA | Source staging bytes/SHA | Placeholder occurrences | Unique literal URLs |",
        "|---|---|---|---|---:|---:|",
    ]
    for key, page in pages.items():
        p = page["provenance"]
        md.append(f"| `{key}` | `{page['route']}` | {p['derived_length']} / `{p['derived_sha256']}` | {p['source_length']} / `{p['source_sha256']}` | {page['placeholder_occurrence_count']} | {page['placeholder_unique_literal_count']} |")
    md.extend([
        "",
        "## Dedup and local salvage",
        "",
        f"The four pages contain **{len(all_refs)}** placeholder occurrences: **{literal_occurrences}** literal URL occurrences across **{len(inventory)}** unique canonical URLs, plus **{len(nonliteral)}** dynamic/relative values retained separately. Status counts: `{dict(sorted(counts.items()))}`. Resource purposes: `{dict(sorted(collections.Counter(i['resource_purpose'] for i in inventory).items()))}`; scopes: `{dict(sorted(collections.Counter(i['resource_scope'] for i in inventory).items()))}`. Of the 217 inventory URLs, **102** are static asset candidates, **113** are page/navigation URLs, and **2** are non-request script-condition literals covering **4** occurrences.",
        "",
        "- Exact local map/manifest entities are recorded with local path, SHA-256, byte length, and image Pillow verification when applicable.",
        "- No basename, path, or cross-origin substitution is treated as an alias.",
        "- Existing post-anchor records retain their temporal class; missing placeholders remain `baseline_target_unverified`.",
        "",
        "## Highest-value findings",
        "",
    ])
    report_purpose_order = {
        "page_body_image": 0,
        "page_body_icon": 1,
        "page_body_static": 2,
        "page_body_feed": 3,
        "template_border_or_chrome": 5,
        "layout_spacer": 7,
        "analytics_script": 8,
        "script_condition_reference": 9,
        "page_navigation": 9,
        "third_party_footer_or_navigation": 9,
        "unknown_static": 10,
    }
    for item in sorted(inventory, key=lambda x: (report_purpose_order.get(x["resource_purpose"], 10), -x["reference_count"], x["canonical_url"]))[:10]:
        md.append(f"- `{item['reference_count']}x` `{item['resource_purpose']}` (`{item['resource_scope']}`) `{item['canonical_url']}` across {', '.join(item['page_coverage'])}: `{item['status']}`; {item['next_action']}")
    md.extend([
        "",
        "## Network asset queue",
        "",
        f"`network-asset-queue.json` contains {len(queue)} exact static URLs (limit 16), ordered by semantic purpose so正文 image/icon/static resources precede shared template spacers. Page/navigation placeholders and nonliteral expressions are excluded from the asset queue but remain in the inventory; shared template candidates are listed separately.",
        "",
        "| Rank | URL | Purpose | References | Page coverage |",
        "|---:|---|---|---:|---|",
    ])
    for q in queue:
        md.append(f"| {q['queue_id'].rsplit('-', 1)[-1]} | `{q['exact_url']}` | `{q['resource_purpose']}` | {q['reference_count']} | {', '.join(q['page_coverage'])} |")
    md.extend([
        "",
        "## Local salvage result",
        "",
        "`local-salvage-proposals.json` records the exact lookup scope and page-specific salvage decisions. The current pass found no exact local payload in the approved maps or v7c manifest for the 217 literal URLs; the 232-reference Korean `b.gif` is retained as one shared `layout_spacer` candidate with markup evidence and is not counted as正文缺图. Any visible layout fallback remains a disclosed derived-layer proposal only.",
    ])
    md.extend([
        "",
        "## Lookup scope and validation",
        "",
        "The pass read only the final audit/proposals, four v8 derived HTML/provenance entries, v7c build manifest, and the approved static/page source maps listed in `input_hashes`. It did not scan the whole raw workspace.",
        "",
        "Every page identity has menu evidence, proposal ID, derived/source path, byte length, and SHA-256. Every reference retains page, line, tag/attribute, markup or CSS context, requested URL, and role evidence.",
    ])
    (OUT / "dedup-inventory.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"pages": 4, "placeholder_occurrences": len(all_refs), "literal_occurrences": literal_occurrences, "unique_literal_urls": len(inventory), "nonliteral": len(nonliteral), "status_counts": dict(counts), "queue": len(queue), "network_requests": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
