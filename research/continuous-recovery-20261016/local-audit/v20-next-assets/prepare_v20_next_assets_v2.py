"""Prepare the next local-only image queues from frozen v18 and v20 evidence.

No network or exporter call is made.  The v20 output is scanned only for its
literal missing-image markers.  The private audit keeps the current marker
evidence and the matching v18 classifications; the public summary contains
only the selected 40 image candidates and non-sensitive evidence.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit, urlunsplit


ROOT = Path.cwd()
OUT_DIR = ROOT / "research/continuous-recovery-20261016/local-audit/v20-next-assets"
V20_ROOT = ROOT / ".scratch/pages-resources-20261016-v20"
V18_AUDIT = ROOT / "research/continuous-recovery-20261016/local-audit/v18-resource-priorities/v18-resource-priorities-audit-v2.json"
V18_BOUNDED = ROOT / "research/continuous-recovery-20261016/local-audit/v18-resource-priorities/v18-resource-priorities-bounded-data-v2.json"
V18_PUBLIC = ROOT / "research/continuous-recovery-20261016/local-audit/v18-resource-priorities/v18-resource-priorities-public-summary-v2.json"
V20_PROV = ROOT / ".scratch/pages-resources-20261016-v20/export-provenance.json"
V20_MAP = ROOT / "research/continuous-recovery-20261016/integration/v20-primary-news-source-map.json"
CACHE_INVENTORY = ROOT / "research/continuous-recovery-20261016/local-audit/v18-resource-priorities/news-images-cache-inventory-v1.json"

PRIVATE_PATH = OUT_DIR / "v20-next-assets-private-audit-v2.json"
PUBLIC_PATH = OUT_DIR / "v20-next-assets-public-summary-v2.json"
VERIFY_PATH = OUT_DIR / "v20-next-assets-verification-v2.json"

MARKER_RE = re.compile(r"missing-image\.svg\?([^\"'<>\s\)]*)", re.IGNORECASE)
TEXT_EXTENSIONS = {".html", ".htm", ".xml", ".css"}
IMAGE_EXTENSIONS = (".gif", ".jpg", ".jpeg", ".png", ".webp", ".svg", ".bmp")
MAIN_HOSTS = {"worldofwarcraft.com", "www.worldofwarcraft.com"}
RELATED_STATIC_HOSTS = {
    "www.wowarmory.com",
    "wowarmory.com",
    "armory.wow-europe.com",
    "imgs.worldofwarcraft.co.kr",
}
SENSITIVE_RE = re.compile(r"(?:jsessionid|session|auth|token|password|passwd|sig|signature|access[_-]?key)\s*=", re.IGNORECASE)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def canonical_url(raw: str) -> str:
    """Normalize only host case and default ports; retain scheme and query."""
    parsed = urlsplit(raw)
    scheme = parsed.scheme.lower()
    host = (parsed.hostname or "").lower()
    try:
        port = parsed.port
    except ValueError:
        port = None
    if port is not None and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        host = f"{host}:{port}"
    if parsed.username or parsed.password:
        host = parsed.netloc.rsplit("@", 1)[0] + "@" + host
    return urlunsplit((scheme, host, parsed.path or "/", parsed.query, ""))


def image_url(raw: str | None) -> bool:
    if not raw:
        return False
    parsed = urlsplit(raw)
    return parsed.scheme in {"http", "https"} and parsed.path.lower().endswith(IMAGE_EXTENSIONS)


def source_host(raw: str) -> str:
    return (urlsplit(raw).hostname or "").lower()


def endpoint_class(raw: str, v18_entry: dict | None) -> str:
    host = source_host(raw)
    path = urlsplit(raw).path.lower()
    if path.endswith("/captcha.jpg") or "/captcha" in path:
        return "functional_image_endpoint"
    if host in MAIN_HOSTS:
        return "official_or_other_image_endpoint"
    # The v18 audit retained a broad official class for this Korea image host;
    # preserve its source evidence but refine the queue class so static related
    # origins (including the spacer example) stay in queue B.
    if host in RELATED_STATIC_HOSTS and not urlsplit(raw).query and path.endswith(IMAGE_EXTENSIONS):
        return "related_origin_static_image"
    if v18_entry and v18_entry.get("endpoint_class"):
        return v18_entry["endpoint_class"]
    return "other_image_endpoint"


def is_sensitive(value: str) -> bool:
    return bool(SENSITIVE_RE.search(value))


def extract_marker(marker: str) -> dict | None:
    token = html.unescape(marker)
    query = token.split("?", 1)[1] if "?" in token else ""
    params = parse_qs(query, keep_blank_values=True)
    requested = params.get("requested", [None])[0]
    source = params.get("source", [None])[0]
    reason = params.get("reason", [None])[0]
    if requested:
        requested = unquote(requested)
    if source:
        source = unquote(source)
    if not image_url(requested):
        return None
    return {
        "requested": requested,
        "canonical": canonical_url(requested),
        "source": source,
        "reason": reason,
        "marker_token": token,
        "sensitive": is_sensitive(token) or is_sensitive(requested),
    }


def scan_v20_markers() -> tuple[list[dict], dict]:
    markers: list[dict] = []
    scanned_files = 0
    scanned_text_files = 0
    eligible_text_files = 0
    internal_origin_files_skipped = 0
    source_sha_mismatches = []
    provenance = load(V20_PROV)
    provenance_by_output = {row.get("output_path"): row for row in provenance.get("files", [])}
    source_sha_cache: dict[str, str] = {}
    for path in V20_ROOT.rglob("*"):
        if not path.is_file():
            continue
        scanned_files += 1
        relpath = path.relative_to(V20_ROOT).as_posix()
        if relpath == "_origins" or relpath.startswith("_origins/"):
            internal_origin_files_skipped += 1
            continue
        if path.name == "export-provenance.json":
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        eligible_text_files += 1
        scanned_text_files += 1
        raw = path.read_bytes()
        source_sha_cache[relpath] = hashlib.sha256(raw).hexdigest()
        expected = provenance_by_output.get(relpath, {}).get("derived_sha256")
        if expected and expected != source_sha_cache[relpath]:
            source_sha_mismatches.append({"path": relpath, "actual_sha256": source_sha_cache[relpath], "provenance_derived_sha256": expected})
        text = raw.decode("utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), 1):
            for match in MARKER_RE.finditer(line):
                parsed = extract_marker("missing-image.svg?" + match.group(1))
                if not parsed:
                    continue
                parsed.update(
                    {
                        "path": relpath,
                        "sha256": source_sha_cache[relpath],
                        "line": line_no,
                        "literal": line.strip(),
                    }
                )
                markers.append(parsed)
    return markers, {
        "files_seen": scanned_files,
        "text_files_eligible": eligible_text_files,
        "text_files_scanned": scanned_text_files,
        "internal_origin_files_skipped": internal_origin_files_skipped,
        "marker_occurrences": len(markers),
        "source_sha_cache_count": len(source_sha_cache),
        "source_sha_mismatches": source_sha_mismatches,
    }


def compact_cache(entry: dict) -> dict:
    result = {
        "cache_join_status": entry.get("cache_join_status", "unknown_not_in_v18_entity"),
        "cache_query": entry.get("cache_query"),
        "positive_row_count": len(entry.get("cache_positive_rows") or []),
        "positive_rows": entry.get("cache_positive_rows") or [],
    }
    return result


def safe_evidence(ev: dict) -> dict:
    sensitive = bool(ev.get("sensitive")) or is_sensitive(ev.get("literal", ""))
    requested = ev.get("requested") or (unquote(ev.get("raw_requested", "")) if ev.get("raw_requested") else None)
    if sensitive:
        return {
            "path": ev["path"],
            "sha256": ev["sha256"],
            "line": ev["line"],
            "literal": "[redacted sensitive query; see private audit]",
            "requested": "[redacted sensitive URL]",
            "source": "[redacted sensitive source]",
            "reason": ev.get("reason"),
            "redacted": True,
        }
    return {
        "path": ev["path"],
        "sha256": ev["sha256"],
        "line": ev["line"],
        "literal": ev["literal"],
        "requested": requested,
        "source": ev.get("source"),
        "reason": ev.get("reason"),
        "redacted": False,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    v18 = load(V18_AUDIT)
    bounded = load(V18_BOUNDED)
    public_v18 = load(V18_PUBLIC)
    provenance = load(V20_PROV)
    v20_map = load(V20_MAP)
    cache_inventory = load(CACHE_INVENTORY)

    markers, scan_stats = scan_v20_markers()
    v18_by_canonical = {canonical_url(item["canonical"]): item for item in v18["all_entities"]}
    overlays = [item for item in provenance["files"] if item.get("kind") == "image_overlay"]
    overlay_originals = {canonical_url(item["original_url"]) for item in overlays}
    map_originals = {canonical_url(item["original"]) for item in v20_map["items"]}
    acquired_originals = overlay_originals | map_originals

    grouped: dict[str, list[dict]] = defaultdict(list)
    for marker in markers:
        grouped[marker["canonical"]].append(marker)

    entities = []
    for canonical, rows in grouped.items():
        original = rows[0]["requested"]
        v18_entry = v18_by_canonical.get(canonical)
        current_evidence = rows[:2]
        sections = v18_entry.get("sections", {}) if v18_entry else {"UNKNOWN": len(rows)}
        state = v18_entry.get("candidate_state", "current_v20_unseen_entity") if v18_entry else "current_v20_unseen_entity"
        if canonical in acquired_originals:
            state = "excluded_current_v20_acquired_or_mapped"
        entity = {
            "canonical": canonical,
            "original": original,
            "all_observed_originals": sorted({row["requested"] for row in rows}),
            "occurrence_count_v20": len(rows),
            "page_count_v20": len({row["path"] for row in rows}),
            "pages_v20": sorted({row["path"] for row in rows}),
            "sections": sections,
            "cross_section": len(sections) > 1,
            "endpoint_class": endpoint_class(original, v18_entry),
            "candidate_state_v18": v18_entry.get("candidate_state") if v18_entry else None,
            "current_state": state,
            "v18_occurrence_count": v18_entry.get("occurrence_count") if v18_entry else None,
            "v18_page_count": v18_entry.get("page_count") if v18_entry else None,
            "v18_pages": v18_entry.get("pages") if v18_entry else [],
            "v18_prior_evidence": v18_entry.get("prior_evidence", []) if v18_entry else [],
            "v18_known_bad_capture": v18_entry.get("known_bad_capture") if v18_entry else None,
            "v18_uncovered_window": v18_entry.get("uncovered_window") if v18_entry else None,
            "cache": compact_cache(v18_entry) if v18_entry else {
                "cache_join_status": "unknown_not_in_v18_entity",
                "cache_query": None,
                "positive_row_count": 0,
                "positive_rows": [],
            },
            "current_v20_evidence": current_evidence,
            "sensitive_evidence_count_v20": sum(1 for row in rows if row.get("sensitive")),
        }
        entities.append(entity)

    # Only unplanned, literal image entities are queueable.  Existing overlays,
    # root-planned assets, and explicitly excluded business/advertising endpoints
    # remain in the private inventory but never enter either public queue.
    excluded_states = {
        "excluded_endpoint",
        "planned_root_next10",
        "acquired_pending_integration",
        "excluded_current_v20_acquired_or_mapped",
    }
    candidates = [
        item
        for item in entities
        if item["current_state"] not in excluded_states
        and item["endpoint_class"] not in {"advertising_endpoint", "business_endpoint", "functional_image_endpoint"}
    ]

    def rank(item: dict):
        return (-item["occurrence_count_v20"], -item["page_count_v20"], -int(item["cross_section"]), item["canonical"])

    main_candidates = sorted(
        [item for item in candidates if source_host(item["canonical"]) in MAIN_HOSTS], key=rank
    )
    related_candidates = sorted(
        [
            item
            for item in candidates
            if source_host(item["canonical"]) not in MAIN_HOSTS
            and item["endpoint_class"] == "related_origin_static_image"
        ],
        key=rank,
    )

    # If the v18 refinement did not label a non-main static origin, keep a
    # conservative fallback for query-free image literals only; this includes
    # Korea-like static hosts while still excluding business/query endpoints.
    if len(related_candidates) < 20:
        fallback = [
            item
            for item in candidates
            if source_host(item["canonical"]) not in MAIN_HOSTS
            and item["endpoint_class"] == "other_image_endpoint"
            and not urlsplit(item["canonical"]).query
        ]
        seen = {item["canonical"] for item in related_candidates}
        related_candidates.extend(item for item in sorted(fallback, key=rank) if item["canonical"] not in seen)
    queue_a = main_candidates[:20]
    queue_b = related_candidates[:20]
    assert len(queue_a) == 20, f"main queue has {len(queue_a)} candidates"
    assert len(queue_b) == 20, f"related queue has {len(queue_b)} candidates"

    def selected_item(item: dict, queue: str, rank_no: int) -> dict:
        return {
            "queue": queue,
            "rank": rank_no,
            "canonical": item["canonical"],
            "original": item["original"],
            "origin": {
                "scheme": urlsplit(item["canonical"]).scheme,
                "host": source_host(item["canonical"]),
                "path": urlsplit(item["canonical"]).path,
                "query_present": bool(urlsplit(item["canonical"]).query),
            },
            "endpoint_class": item["endpoint_class"],
            "occurrence_count_v20": item["occurrence_count_v20"],
            "page_count_v20": item["page_count_v20"],
            "sections": item["sections"],
            "current_state": item["current_state"],
            "candidate_state_v18": item["candidate_state_v18"],
            "cache": item["cache"],
            "prior_evidence": item["v18_prior_evidence"],
            "known_bad_capture": item["v18_known_bad_capture"],
            "uncovered_window": item["v18_uncovered_window"],
            "current_v20_evidence": [safe_evidence(ev) for ev in item["current_v20_evidence"]],
            "v18_evidence": [safe_evidence(ev) for ev in (v18_by_canonical.get(item["canonical"], {}).get("evidence", [])[:2])],
            "selection_reason": "high occurrence/page reuse among current v20 literal missing-image markers; no acquired overlay/source map match",
        }

    public_queue = [selected_item(item, "A-main-worldofwarcraft", i + 1) for i, item in enumerate(queue_a)]
    public_queue += [selected_item(item, "B-related-static", i + 1) for i, item in enumerate(queue_b)]

    public_sensitive = [
        item["canonical"]
        for item in public_queue
        if any(ev.get("redacted") for ev in item["current_v20_evidence"] + item["v18_evidence"])
    ]
    assert not public_sensitive, f"sensitive fields would enter public summary: {public_sensitive[:3]}"

    # Private inventory is intentionally more complete than the public queue:
    # it preserves current marker evidence and old classification boundaries.
    private_entities = []
    for item in entities:
        private_entities.append({
            **{key: value for key, value in item.items() if key != "current_v20_evidence"},
            "current_v20_evidence": item["current_v20_evidence"],
            "v18_evidence": v18_by_canonical.get(item["canonical"], {}).get("evidence", [])[:2],
        })

    input_hashes = {
        "v18_audit": sha256(V18_AUDIT),
        "v18_bounded_data": sha256(V18_BOUNDED),
        "v18_public_summary": sha256(V18_PUBLIC),
        "v18_cache_inventory": sha256(CACHE_INVENTORY),
        "v20_provenance": sha256(V20_PROV),
        "v20_primary_map": sha256(V20_MAP),
    }
    generated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    current_counts = Counter(item["current_state"] for item in entities)
    endpoint_counts = Counter(item["endpoint_class"] for item in entities)
    section_counts = Counter()
    for item in entities:
        for section, count in item["sections"].items():
            section_counts[section] += count

    private = {
        "schema": "wow-recovery.local-audit.v20-next-assets.private.v2",
        "generated_utc": generated,
        "network_requests": 0,
        "amendment": {
            "supersedes": [
                "research/continuous-recovery-20261016/local-audit/v20-next-assets/v20-next-assets-private-audit.json",
                "research/continuous-recovery-20261016/local-audit/v20-next-assets/v20-next-assets-public-summary.json",
                "research/continuous-recovery-20261016/local-audit/v20-next-assets/v20-next-assets-verification.json",
            ],
            "root_cause": "The v1 scanner only visited .html/.htm files. Frozen v18 scope also includes .xml and .css; v20 has 55 additional eligible files in those two extensions, contributing 59 marker occurrences across 54 entities.",
            "v1_scan": {"eligible_text_files": 1049, "marker_occurrences": 1959, "unique_entities": 1166},
            "v2_scan": {"eligible_text_files": 1104, "marker_occurrences": 2018, "unique_entities": 1220},
            "scope_alignment": "v2 matches v18 TEXT_EXTS (.html/.htm/.xml/.css), skips _origins, and includes .svg image URLs like the frozen v18 parser.",
        },
        "scope": "Current v20 literal missing-image markers joined to frozen v18 entity evidence; no network or export execution.",
        "inputs": {
            "v18_audit_path": str(V18_AUDIT.relative_to(ROOT)).replace("\\", "/"),
            "v20_output_root": ".scratch/pages-resources-20261016-v20",
            "v20_provenance_path": str(V20_PROV.relative_to(ROOT)).replace("\\", "/"),
            "v20_map_path": str(V20_MAP.relative_to(ROOT)).replace("\\", "/"),
            "sha256": input_hashes,
        },
        "scan": scan_stats,
        "conservation": {
            "current_v20_marker_occurrences": len(markers),
            "current_v20_unique_exact_image_entities": len(entities),
            "entity_occurrence_sum": sum(item["occurrence_count_v20"] for item in entities),
            "entity_occurrence_sum_matches_scan": sum(item["occurrence_count_v20"] for item in entities) == len(markers),
            "v18_entity_count": len(v18["all_entities"]),
            "current_entities_with_v18_match": sum(1 for item in entities if item["canonical"] in v18_by_canonical),
            "current_entities_unseen_in_v18": sum(1 for item in entities if item["canonical"] not in v18_by_canonical),
            "v20_overlay_original_count": len(overlay_originals),
            "v20_map_original_count": len(map_originals),
            "source_sha_mismatches": len(scan_stats["source_sha_mismatches"]),
            "current_entities_excluded_as_acquired_or_mapped": sum(1 for item in entities if item["current_state"] == "excluded_current_v20_acquired_or_mapped"),
        },
        "counts": {
            "current_state": dict(sorted(current_counts.items())),
            "endpoint_class": dict(sorted(endpoint_counts.items())),
            "section_marker_occurrences_from_v18_sections": dict(sorted(section_counts.items())),
            "queue_a_main": len(queue_a),
            "queue_b_related": len(queue_b),
        },
        "cache_scope": {
            "v18_cache_inventory_path": str(CACHE_INVENTORY.relative_to(ROOT)).replace("\\", "/"),
            "v18_cache_inventory_sha256": input_hashes["v18_cache_inventory"],
            "interpretation": "A positive cached row is reusable evidence only. No missing cached row is treated as absence, latest proof, or payload recovery.",
            "cache_inventory_summary": cache_inventory.get("conservation"),
        },
        "entities": private_entities,
        "queue_a": public_queue[:20],
        "queue_b": public_queue[20:],
        "selection_rule": "A is exact worldofwarcraft.com origin, B is exact related-origin static image; scheme/host/path/query identities remain separate except default-port canonicalization.",
        "known_boundaries": [
            "The current v20 scan is a marker-layer inventory; dynamic gallery entities are outside this queue.",
            "SentientMortals retains its v18 known 404 evidence and is not relabeled absent outside that capture.",
            "HTTP and HTTPS variants remain separate candidates and retain their own prior evidence.",
            "No candidate is a claim of valid payload, latest CDX capture, or successful replay.",
        ],
    }
    dump(PRIVATE_PATH, private)

    public = {
        "schema": "wow-recovery.local-audit.v20-next-assets.public.v2",
        "generated_utc": generated,
        "network_requests": 0,
        "summary": {
            "current_v20_marker_occurrences": len(markers),
            "current_v20_unique_exact_image_entities": len(entities),
            "current_v20_unresolved_queueable_entities": len(candidates),
            "queue_a_count": len(queue_a),
            "queue_b_count": len(queue_b),
            "queue_total": len(public_queue),
            "v20_overlay_original_count": len(overlay_originals),
            "v20_map_original_count": len(map_originals),
            "source_sha_mismatches": len(scan_stats["source_sha_mismatches"]),
            "sensitive_public_fields": 0,
        },
        "input_sha256": input_hashes,
        "queues": public_queue,
        "classification_notes": [
            "v2 corrects the superseded v1 denominator: v1 omitted .xml and .css marker surfaces; v2 follows the frozen v18 scope.",
            "Queue A keeps exact main-site scheme/host/path/query identity.",
            "Queue B keeps related static image origins such as Armory/Korea-like image hosts; query/session/business endpoints are excluded.",
            "Known bad captures and HTTP/HTTPS variants are retained as prior evidence rather than converted into absence claims.",
            "Cached positives are reusable CDX evidence only and are not payload or latest-capture proof.",
            "These are preparation candidates only; no network tail binding or download was executed.",
        ],
    }
    dump(PUBLIC_PATH, public)

    verification = {
        "schema": "wow-recovery.local-audit.v20-next-assets.verification.v2",
        "generated_utc": generated,
        "amendment": {
            "supersedes_verification": "research/continuous-recovery-20261016/local-audit/v20-next-assets/v20-next-assets-verification.json",
            "root_cause": "v1 scanned 1049 .html/.htm files; v2 scanned all 1104 frozen-scope .html/.htm/.xml/.css files. The omitted 55 files account for 59 occurrences and 54 entities.",
            "v1_counts": {"marker_occurrences": 1959, "unique_entities": 1166},
            "v2_counts": {"marker_occurrences": 2018, "unique_entities": 1220},
        },
        "script": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"),
        "script_sha256": sha256(Path(__file__)),
        "private_audit": {"path": str(PRIVATE_PATH.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(PRIVATE_PATH)},
        "public_summary": {"path": str(PUBLIC_PATH.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(PUBLIC_PATH)},
        "input_sha256": input_hashes,
        "checks": {
            "network_requests": 0,
            "export_invocations": 0,
            "current_marker_occurrence_sum_matches": sum(item["occurrence_count_v20"] for item in entities) == len(markers),
            "current_unique_entity_count": len(entities),
            "v2_scope_matches_frozen_v18": scan_stats["text_files_eligible"] == 1104 and scan_stats["internal_origin_files_skipped"] == 127,
            "v2_matches_root_expected_denominator": len(markers) == 2018 and len(entities) == 1220,
            "queue_a_exactly_20": len(queue_a) == 20,
            "queue_b_exactly_20": len(queue_b) == 20,
            "queue_unique_40": len({item["canonical"] for item in public_queue}) == 40,
            "queue_candidates_have_current_evidence": all(item["current_v20_evidence"] for item in public_queue),
            "queue_candidates_have_origin": all(item["origin"]["host"] for item in public_queue),
            "public_sensitive_fields_zero": len(public_sensitive) == 0,
            "source_sha_mismatches_zero": len(scan_stats["source_sha_mismatches"]) == 0,
            "v20_provenance_sha_bound": bool(input_hashes["v20_provenance"]),
            "v20_map_sha_bound": bool(input_hashes["v20_primary_map"]),
        },
        "uncovered": [
            "No network requests, direct CDX lookups, replay requests, payload downloads, or v21 integration were performed.",
            "A cache join is not an absence proof and current output markers do not prove historical validity.",
        ],
    }
    verification["accepted"] = all(value is True for value in verification["checks"].values() if isinstance(value, bool))
    dump(VERIFY_PATH, verification)
    verification["verification_sha256"] = sha256(VERIFY_PATH)
    print(json.dumps({
        "accepted": verification["accepted"],
        "private": str(PRIVATE_PATH.relative_to(ROOT)).replace("\\", "/"),
        "private_sha256": sha256(PRIVATE_PATH),
        "public": str(PUBLIC_PATH.relative_to(ROOT)).replace("\\", "/"),
        "public_sha256": sha256(PUBLIC_PATH),
        "verification": str(VERIFY_PATH.relative_to(ROOT)).replace("\\", "/"),
        "verification_sha256": verification["verification_sha256"],
        "current_markers": len(markers),
        "current_entities": len(entities),
        "queue_a": len(queue_a),
        "queue_b": len(queue_b),
        "network_requests": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
