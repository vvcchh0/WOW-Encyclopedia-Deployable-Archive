"""Prepare a bounded, local-only queue of twenty v20 news-body image entities.

The input audit and v20 provenance are frozen.  This script only reads them and
writes the four receipts in this directory; it never fetches, builds, or edits
production/source files.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, quote


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
AUDIT = ROOT / "research/continuous-recovery-20261016/local-audit/v20-next-assets/v20-next-assets-private-audit-v2.json"
PUBLIC_V20 = ROOT / "research/continuous-recovery-20261016/local-audit/v20-next-assets/v20-next-assets-public-summary-v2.json"
V20_PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v20/export-provenance.json"
V20_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v20-asset-queues-acceptance.json"
PUB = ROOT / "research/continuous-recovery-20261016/publication"


SELECTED = [
    "http://www.worldofwarcraft.com/news/images/06-10/southpark.jpg",
    "http://www.worldofwarcraft.com/news/images/07-04/4-27-07-1.jpg",
    "http://www.worldofwarcraft.com/news/images/05-03/charactermove.jpg",
    "http://www.worldofwarcraft.com/news/images/04-12/thad.jpg",
    "http://www.worldofwarcraft.com/news/images/08-01/01-31-08.jpg",
    "http://www.worldofwarcraft.com/news/images/08-01/01-30-08-1.jpg",
    "http://www.worldofwarcraft.com/news/images/08-01/01-30-08-2.jpg",
    "http://www.worldofwarcraft.com/news/images/08-02/02-27-08-1.jpg",
    "http://www.worldofwarcraft.com/news/images/08-02/02-27-08-2.jpg",
    "http://www.worldofwarcraft.com/news/images/08-02/02-27-08-3.jpg",
    "http://www.worldofwarcraft.com/news/images/08-03/03-21-08-1.jpg",
    "http://www.worldofwarcraft.com/news/images/08-03/03-19-08-1.jpg",
    "http://www.worldofwarcraft.com/news/images/08-03/03-19-08-2.jpg",
    "http://www.worldofwarcraft.com/news/images/08-04/04-02-08-1.jpg",
    "http://www.worldofwarcraft.com/news/images/08-04/04-02-08-2.jpg",
    "http://www.worldofwarcraft.com/news/images/08-04/04-02-08-3.jpg",
    "http://www.worldofwarcraft.com/news/images/08-05/05-01-08-1.jpg",
    "http://www.worldofwarcraft.com/news/images/08-05/05-01-08-2.jpg",
    "http://www.worldofwarcraft.com/news/images/08-05/05-01-08-3.jpg",
    "http://www.worldofwarcraft.com/news/images/07-09/09-27-07-1.jpg",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_url(value: str) -> str:
    """Normalize only scheme/host case and default HTTP(S) ports.

    The path and query remain exact and www/bare hosts are kept distinct.
    """
    p = urlsplit(value)
    scheme = p.scheme.lower()
    host = (p.hostname or "").lower()
    port = p.port
    if port is not None and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        host = f"{host}:{port}"
    return f"{scheme}://{host}{p.path}" + (f"?{p.query}" if p.query else "") + (f"#{p.fragment}" if p.fragment else "")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def compact_query(cache: dict | None) -> dict:
    c = cache or {}
    q = c.get("cache_query") or {}
    return {
        "from": q.get("from"),
        "to": q.get("to"),
        "match_type": q.get("match_type"),
        "collapse": q.get("collapse"),
        "limit": q.get("limit"),
        "transport_status": q.get("transport_status"),
        "transport_complete": q.get("transport_complete"),
        "response_capped": q.get("response_capped"),
        "row_count": q.get("row_count"),
        "exact_entity_index_complete": q.get("exact_entity_index_complete"),
        "latest_capture": q.get("latest_capture"),
        "absence_proof": q.get("absence_proof"),
    }


SENSITIVE = re.compile(r"(?i)(?:jsessionid|session|auth|token|cookie)=([^&\s\"']+)")


def public_literal(value: str) -> tuple[str, bool]:
    hit = bool(SENSITIVE.search(value))
    return SENSITIVE.sub(lambda m: m.group(0).split("=", 1)[0] + "=<redacted>", value), hit


def public_evidence(e: dict) -> tuple[list[dict], int]:
    out = []
    sensitive = 0
    for ev in (e.get("current_v20_evidence") or [])[:2]:
        lit, hit = public_literal(ev.get("literal", ""))
        sensitive += int(hit or ev.get("sensitive", False))
        out.append({
            "path": ev.get("path"),
            "sha256": ev.get("sha256"),
            "line": ev.get("line"),
            "source": ev.get("source"),
            "requested": ev.get("requested"),
            "reason": ev.get("reason"),
            "literal": lit,
        })
    return out, sensitive


def public_prior(e: dict) -> dict:
    records = []
    for ev in e.get("v18_prior_evidence") or []:
        records.append({
            "path": ev.get("path"),
            "sha256": ev.get("sha256"),
            "line": ev.get("line"),
            "source": ev.get("source"),
            "status": ev.get("status"),
            "kind": ev.get("kind"),
            "capture_timestamp": ev.get("capture_timestamp") or ev.get("timestamp"),
            "note": ev.get("note") or ev.get("selection") or ev.get("reason"),
        })
    bad = e.get("v18_known_bad_capture")
    return {"count": len(records), "records": records, "known_bad_capture": bad}


def receipt_originals(name: str) -> list[dict]:
    p = PUB / name
    if not p.exists():
        return []
    d = read_json(p)
    out = []
    for item in d.get("accepted_images") or []:
        if item.get("original"):
            out.append({"original": item["original"], "receipt": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": item.get("sha256"), "capture": item.get("actual_capture_timestamp"), "status": "accepted"})
    return out


def verify_source_evidence(e: dict) -> dict:
    checks = []
    for ev in e.get("current_v20_evidence") or []:
        rel = ev.get("path")
        f = ROOT / ".scratch/pages-resources-20261016-v20" / rel
        exists = f.exists()
        hash_ok = exists and sha256(f) == ev.get("sha256")
        line_ok = False
        contains_requested = False
        if exists and ev.get("line"):
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
            idx = int(ev["line"]) - 1
            if 0 <= idx < len(lines):
                text = lines[idx]
                line_ok = text == ev.get("literal") or ev.get("literal", "") in text
                requested = ev.get("requested") or e.get("canonical")
                contains_requested = requested in text or quote(requested, safe="") in text or quote(requested, safe="/:?=&") in text
        checks.append({
            "path": rel,
            "sha256_expected": ev.get("sha256"),
            "sha256_actual": sha256(f) if exists else None,
            "exists": exists,
            "hash_match": hash_ok,
            "line": ev.get("line"),
            "literal_line_match": line_ok,
            "requested_in_line": contains_requested,
        })
    return {"all_ok": bool(checks) and all(x["exists"] and x["hash_match"] and x["line"] and x["literal_line_match"] and x["requested_in_line"] for x in checks), "checks": checks}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    generated_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    audit = read_json(AUDIT)
    provenance = read_json(V20_PROVENANCE)
    entities = {norm_url(e["canonical"]): e for e in audit["entities"]}
    overlay_records = [x for x in provenance.get("files", []) if x.get("kind") == "image_overlay" or x.get("role") == "image_overlay"]
    overlay_urls = {norm_url(x["original_url"]) for x in overlay_records if x.get("original_url")}

    pending = []
    pending.extend(receipt_originals("root-aug-cached19-source-acceptance.json"))
    pending.extend(receipt_originals("root-aug-final3-source-acceptance.json"))
    redirect = PUB / "root-aug11-redirect-observation.json"
    if redirect.exists():
        rd = read_json(redirect)
        if rd.get("original"):
            pending.append({"original": rd["original"], "receipt": str(redirect.relative_to(ROOT)).replace("\\", "/"), "sha256": rd.get("source_header_sha256"), "capture": rd.get("redirect_capture_timestamp"), "status": "later_capture_redirect_observed"})
    pending_by_url = {}
    for x in pending:
        pending_by_url.setdefault(norm_url(x["original"]), []).append(x)

    # Audit the full NEWS image pool before applying the explicit queue.
    ext_re = re.compile(r"\.(?:jpe?g|gif)$", re.I)
    noise_re = re.compile(r"(?:pixel|spacer|smallcaps|bullet|clear|arrow|button|icon|logo|caption)", re.I)
    news_pool = []
    news_path_pool = []
    news_body_pool = []
    excluded_overlay = []
    excluded_pending = []
    excluded_noise = []
    for e in audit["entities"]:
        u = e["canonical"]
        sp = urlsplit(u)
        if "NEWS" not in (e.get("sections") or {}) or not sp.path.lower().startswith("/news/images/"):
            continue
        news_path_pool.append(e)
        if not ext_re.search(sp.path):
            continue
        news_pool.append(e)
        nu = norm_url(u)
        if nu in overlay_urls:
            excluded_overlay.append(u)
        if nu in pending_by_url:
            excluded_pending.append(u)
        if noise_re.search(sp.path):
            excluded_noise.append(u)
        if not noise_re.search(sp.path) and nu not in overlay_urls and nu not in pending_by_url:
            news_body_pool.append(e)

    selected_entities = []
    missing = []
    for i, original in enumerate(SELECTED, 1):
        e = entities.get(norm_url(original))
        if e is None:
            missing.append(original)
            continue
        selected_entities.append((i, e))

    private_items = []
    public_items = []
    selected_checks = []
    sensitive_public_count = 0
    for rank, e in selected_entities:
        u = e["canonical"]
        nu = norm_url(u)
        evidence_public, sensitive = public_evidence(e)
        sensitive_public_count += sensitive
        source_check = verify_source_evidence(e)
        selected_checks.append({"rank": rank, "original": u, **source_check})
        sp = urlsplit(u)
        cache = e.get("cache") or {}
        prior = e.get("v18_prior_evidence") or []
        private_items.append({
            "rank": rank,
            "canonical": e.get("canonical"),
            "original": e.get("original"),
            "origin": {"scheme": sp.scheme, "host": sp.hostname, "port": sp.port, "path": sp.path, "query": sp.query},
            "occurrence_count_v20": e.get("occurrence_count_v20"),
            "page_count_v20": e.get("page_count_v20"),
            "pages_v20": e.get("pages_v20"),
            "sections": e.get("sections"),
            "cross_section": e.get("cross_section"),
            "endpoint_class": e.get("endpoint_class"),
            "current_state": e.get("current_state"),
            "current_v20_evidence": e.get("current_v20_evidence"),
            "v18_evidence": e.get("v18_evidence"),
            "v18_prior_evidence": e.get("v18_prior_evidence"),
            "v18_known_bad_capture": e.get("v18_known_bad_capture"),
            "v18_uncovered_window": e.get("v18_uncovered_window"),
            "cache": cache,
            "exclusion_checks": {
                "v20_overlay_match": nu in overlay_urls,
                "pending_aug19_or_tcg03_match": nu in pending_by_url,
                "noise_name_match": bool(noise_re.search(sp.path)),
                "selected_as_news_body": True,
            },
            "source_evidence_check": source_check,
        })
        public_items.append({
            "rank": rank,
            "original": e.get("original"),
            "origin": {"scheme": sp.scheme, "host": sp.hostname, "port": sp.port, "path": sp.path, "query": sp.query},
            "occurrence_count_v20": e.get("occurrence_count_v20"),
            "page_count_v20": e.get("page_count_v20"),
            "pages_v20": e.get("pages_v20"),
            "sections": e.get("sections"),
            "endpoint_class": e.get("endpoint_class"),
            "current_state": e.get("current_state"),
            "source_evidence": evidence_public,
            "prior_evidence": public_prior(e),
            "uncovered_window": {
                "status": (e.get("v18_uncovered_window") or {}).get("status"),
                "entity_specific_latest_capture": (e.get("v18_uncovered_window") or {}).get("entity_specific_latest_capture"),
                "entity_specific_absence_proof": (e.get("v18_uncovered_window") or {}).get("entity_specific_absence_proof"),
                "bounded_prefix_window": (e.get("v18_uncovered_window") or {}).get("bounded_prefix_window"),
            },
            "cache": {
                "join_status": cache.get("cache_join_status"),
                "positive_row_count": cache.get("positive_row_count"),
                "query": compact_query(cache),
                "positive_rows": cache.get("positive_rows") or [],
            },
            "selection_reason": "NEWS section exact literal; monthly /news/images/ JPG body candidate; no glyph/noise basename; not a v20 overlay or separately pending AUG target.",
            "known_bad_capture": e.get("v18_known_bad_capture"),
            "exclusion_checks": {
                "v20_overlay_match": nu in overlay_urls,
                "pending_aug19_or_tcg03_or_aug11_match": nu in pending_by_url,
                "filename_noise_match": bool(noise_re.search(sp.path)),
            },
            "source_evidence_verified": source_check["all_ok"],
        })

    input_hashes = {
        "v20_private_audit": {"path": str(AUDIT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(AUDIT), "bytes": AUDIT.stat().st_size},
        "v20_public_summary": {"path": str(PUBLIC_V20.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(PUBLIC_V20), "bytes": PUBLIC_V20.stat().st_size},
        "v20_export_provenance": {"path": str(V20_PROVENANCE.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(V20_PROVENANCE), "bytes": V20_PROVENANCE.stat().st_size},
        "root_v20_asset_queue_acceptance": {"path": str(V20_ACCEPTANCE.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(V20_ACCEPTANCE), "bytes": V20_ACCEPTANCE.stat().st_size},
    }
    pending_receipt_hashes = []
    for name in ["root-aug-cached19-source-acceptance.json", "root-aug-final3-source-acceptance.json", "root-aug11-redirect-observation.json"]:
        p = PUB / name
        if p.exists():
            pending_receipt_hashes.append({"path": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(p), "bytes": p.stat().st_size})

    private = {
        "schema": "wow-recovery.local-audit.v20-news-content20.private.v1",
        "generated_utc": generated_utc,
        "scope": "Pure-local selection of twenty unresolved v20 NEWS body-image literals. No network, export, Git, or production mutation.",
        "selection_policy": {
            "requested_count": 20,
            "selection_order": "Four multi-reference NEWS body images first, then representative 2008-01 through 2008-05 and 2007-09 monthly JPG groups.",
            "required_path": "/news/images/",
            "allowed_extensions": [".jpg", ".jpeg", ".gif"],
            "noise_basename_regex": noise_re.pattern,
            "avoid_1px_glyph": True,
        },
        "inputs": input_hashes,
        "pending_receipts": pending_receipt_hashes,
        "input_audit_totals": {
            "exact_entities": len(audit.get("entities") or []),
            "marker_occurrences": sum(int(e.get("occurrence_count_v20") or 0) for e in audit.get("entities") or []),
        },
        "exclusion_set": {
            "v20_overlay_count": len(overlay_records),
            "v20_overlay_unique_original_count": len(overlay_urls),
            "pending_originals": sorted(pending_by_url),
            "pending_evidence": pending,
        },
        "pool_counts": {
            "news_path_entities_all_extensions": len(news_path_pool),
            "news_path_occurrences_all_extensions": sum(int(e.get("occurrence_count_v20") or 0) for e in news_path_pool),
            "news_image_entities": len(news_pool),
            "news_image_occurrences": sum(int(e.get("occurrence_count_v20") or 0) for e in news_pool),
            "news_body_pool_after_overlay_pending_noise": len(news_body_pool),
            "excluded_by_v20_overlay": len(set(excluded_overlay)),
            "excluded_by_pending": len(set(excluded_pending)),
            "excluded_by_noise_name": len(set(excluded_noise)),
            "new_hp_news_body_entities_available": 0,
            "new_hp_boundary": "No unresolved /new-hp/images/news* entity remains in the v20 audit; unresolved new-hp entries are nav/credits/background assets and are outside this news-body queue.",
        },
        "selected_count": len(private_items),
        "missing_requested_originals": missing,
        "selected_items": private_items,
    }

    public = {
        "schema": "wow-recovery.local-audit.v20-news-content20.public.v1",
        "generated_utc": generated_utc,
        "scope": "Twenty unresolved exact NEWS body-image literals for a later bounded network plan; this file contains no network result or availability claim.",
        "inputs": input_hashes,
        "pending_exclusions": {
            "v20_overlay_count": len(overlay_records),
            "pending_originals": sorted(pending_by_url),
            "pending_receipt_paths": [x["path"] for x in pending_receipt_hashes],
        },
        "input_audit_totals": {
            "exact_entities": len(audit.get("entities") or []),
            "marker_occurrences": sum(int(e.get("occurrence_count_v20") or 0) for e in audit.get("entities") or []),
        },
        "candidate_count": len(public_items),
        "candidates": public_items,
        "public_sensitive_literal_count": sensitive_public_count,
        "boundary": {
            "cache_join": "The saved positive cache is a new-hp prefix query; zero rows for these /news/images/ URLs is not absence proof.",
            "prior_evidence": "Each candidate retains prior evidence count and known-bad field; no candidate is called recovered.",
            "new_hp": "No unresolved new-hp news banner was present in this v20 audit scope.",
            "network": "No network request was made by this preparation.",
        },
    }

    summary = {
        "schema": "wow-recovery.local-audit.v20-news-content20.summary.v1",
        "generated_utc": generated_utc,
        "input_sha256": {k: v["sha256"] for k, v in input_hashes.items()},
        "input_audit_exact_entities": len(audit.get("entities") or []),
        "input_audit_marker_occurrences": sum(int(e.get("occurrence_count_v20") or 0) for e in audit.get("entities") or []),
        "candidate_count": len(public_items),
        "unique_original_count": len({x["original"] for x in public_items}),
        "selected_occurrence_count_v20": sum(int(x.get("occurrence_count_v20") or 0) for x in public_items),
        "selected_page_count_sum_v20": sum(int(x.get("page_count_v20") or 0) for x in public_items),
        "news_pool_entities": len(news_pool),
        "news_pool_occurrences": sum(int(e.get("occurrence_count_v20") or 0) for e in news_pool),
        "news_path_entities_all_extensions": len(news_path_pool),
        "news_path_occurrences_all_extensions": sum(int(e.get("occurrence_count_v20") or 0) for e in news_path_pool),
        "v20_overlay_exclusions": len(overlay_records),
        "separate_pending_exclusions": len(pending_by_url),
        "source_evidence_all_verified": all(x["all_ok"] for x in selected_checks),
        "prior_evidence_counts": {"with_prior_evidence": sum(bool(e.get("v18_prior_evidence")) for _, e in selected_entities), "known_bad_capture": sum(bool(e.get("v18_known_bad_capture")) for _, e in selected_entities), "no_prior_evidence": sum(not e.get("v18_prior_evidence") for _, e in selected_entities)},
        "cache_positive_counts": {"with_positive_row": sum(bool((e.get("cache") or {}).get("positive_rows")) for _, e in selected_entities), "no_positive_row": sum(not (e.get("cache") or {}).get("positive_rows") for _, e in selected_entities)},
        "new_hp_news_body_entities_available": 0,
        "missing_requested_originals": missing,
    }

    verification = {
        "schema": "wow-recovery.local-audit.v20-news-content20.verification.v1",
        "generated_utc": generated_utc,
        "checks": {
            "requested_count_20": len(SELECTED) == 20,
            "selected_count_20": len(public_items) == 20,
            "unique_originals": len(public_items) == len({x["original"] for x in public_items}),
            "all_news_section": all("NEWS" in (e.get("sections") or {}) for _, e in selected_entities),
            "all_news_images_path": all(urlsplit(e["canonical"]).path.lower().startswith("/news/images/") for _, e in selected_entities),
            "all_real_jpg_gif": all(bool(ext_re.search(urlsplit(e["canonical"]).path)) for _, e in selected_entities),
            "no_noise_basename": all(not noise_re.search(urlsplit(e["canonical"]).path) for _, e in selected_entities),
            "no_v20_overlay_match": all(norm_url(e["canonical"]) not in overlay_urls for _, e in selected_entities),
            "no_pending_match": all(norm_url(e["canonical"]) not in pending_by_url for _, e in selected_entities),
            "source_files_and_literals_verified": all(x["all_ok"] for x in selected_checks),
            "public_sensitive_literals_zero": sensitive_public_count == 0,
        },
        "source_checks": selected_checks,
        "pending_evidence": pending,
        "no_network_or_build_executed": True,
    }

    write_json(OUT / "v20-news-content20-private-audit.json", private)
    write_json(OUT / "v20-news-content20-public-candidates.json", public)
    write_json(OUT / "v20-news-content20-summary.json", summary)
    write_json(OUT / "v20-news-content20-verification.json", verification)
    artifact_paths = [
        OUT / "v20-news-content20-private-audit.json",
        OUT / "v20-news-content20-public-candidates.json",
        OUT / "v20-news-content20-summary.json",
        OUT / "v20-news-content20-verification.json",
    ]
    artifact_manifest = {
        "schema": "wow-recovery.local-audit.v20-news-content20.artifact-manifest.v1",
        "generated_utc": generated_utc,
        "prepare_script": {
            "path": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(Path(__file__)),
            "bytes": Path(__file__).stat().st_size,
        },
        "artifacts": [
            {"path": str(x.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(x), "bytes": x.stat().st_size}
            for x in artifact_paths
        ],
    }
    write_json(OUT / "v20-news-content20-artifact-manifest.json", artifact_manifest)
    print(json.dumps({"candidate_count": len(public_items), "missing": missing, "source_evidence_all_verified": verification["checks"]["source_files_and_literals_verified"], "public_sensitive_literal_count": sensitive_public_count, "news_pool_entities": len(news_pool), "news_pool_occurrences": sum(int(e.get("occurrence_count_v20") or 0) for e in news_pool), "overlay_count": len(overlay_records), "pending_count": len(pending_by_url)}, ensure_ascii=False, sort_keys=True))
    return 0 if verification["checks"]["selected_count_20"] and verification["checks"]["source_files_and_literals_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
