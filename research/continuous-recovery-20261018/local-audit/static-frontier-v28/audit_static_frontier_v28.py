"""Bounded, read-only v27 missing-marker frontier audit.

This audit reads only the frozen v27 HTML marker surface and existing JSON
receipts/plans.  It does not contact the network, inspect or hash binary image
payloads, or mutate any frozen build.  Its outputs are intentionally limited
to the new local-audit/static-frontier-v28 directory.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shutil
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit


ROOT = Path(r"D:\WOW_Encyclopedia")
V27 = ROOT / ".scratch" / "pages-resources-20261018-v27"
OUT = ROOT / "research" / "continuous-recovery-20261018" / "local-audit" / "static-frontier-v28"
STATIC_BATCH = ROOT / "research" / "continuous-recovery-20261016" / "network" / "static-main01" / "output" / "batch-report.json"
STATIC_PLAN = ROOT / "research" / "continuous-recovery-20261016" / "network" / "static-main01" / "plan.json"
STATIC_MAP = ROOT / "research" / "continuous-recovery-20261016" / "network" / "static-main01" / "output" / "source-map.json"
STATIC_ACCEPT = ROOT / "research" / "continuous-recovery-20261016" / "publication" / "root-static-main01-source-acceptance.json"
MARKER = re.compile(r"missing-image\.svg\?([^\"<>]+)", re.I)
IMAGE_EXTS = {".jpg", ".jpeg", ".gif", ".png", ".bmp", ".webp"}
LAYOUT_WORDS = {
    "pixel", "spacer", "blank", "clear", "transparent", "shim", "dot", "b", "bg",
    "background", "border", "top", "bottom", "left", "right", "side", "sides",
    "button", "arrow", "bullet", "divider", "meta-mini", "orange-mini", "close",
}
NEWS_PARTS = ("/news/", "/rss-", "news.")
ARMORY_PARTS = ("wowarmory.com", "armory.wow-europe.com", "/armory/")
CONTENT_PARTS = ("/insider/", "/burningcrusade/", "/gameguide/", "/game-guide/", "/guides/")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def norm_url(value: str) -> str:
    try:
        p = urlsplit(value)
        host = (p.hostname or "").lower()
        scheme = p.scheme.lower()
        port = p.port
        if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
            host = f"{host}:{port}"
        return f"{scheme}://{host}{p.path or '/'}"
    except ValueError:
        return value.lower()


def is_image_url(value: str) -> bool:
    try:
        p = urlsplit(value)
        return p.scheme in {"http", "https"} and Path(p.path).suffix.lower() in IMAGE_EXTS
    except ValueError:
        return False


def page_class(source: str, target: str) -> str:
    low_s = source.lower()
    low_t = target.lower()
    if any(x in low_t for x in ARMORY_PARTS):
        return "armory"
    if any(x in low_s for x in CONTENT_PARTS) or any(x in low_t for x in CONTENT_PARTS):
        return "guide_bc_insider"
    return "other_static"


def is_news(source: str, target: str) -> bool:
    low = (source + " " + target).lower()
    return any(x in low for x in NEWS_PARTS)


def visual_role(target: str) -> str:
    path = urlsplit(target).path.lower()
    base = Path(path).stem.lower()
    layout_tokens = ("bg", "data", "tip", "team", "parch", "bevel", "head", "border", "top", "bot", "bottom", "left", "right", "side", "dropback", "container", "circle", "splash", "title", "box", "nav", "tab", "pixel", "spacer", "blank", "shim")
    if base in LAYOUT_WORDS or any(token in base for token in layout_tokens):
        return "layout_or_placeholder_candidate"
    if base in {"icon", "icons"} or "/icons/" in path:
        return "icon_or_small_visual_candidate"
    return "content_visual_candidate"


def recursive_strings(value):
    if isinstance(value, dict):
        for k, v in value.items():
            yield from recursive_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from recursive_strings(v)
    elif isinstance(value, str):
        yield value


def evidence_kind(path: Path) -> str:
    name = path.name.lower()
    if "plan" in name or "candidate" in name or "queue" in name:
        return "plan_or_queue"
    if "batch-report" in name or "request-record" in name or "source-map" in name or "sanitized-summary" in name:
        return "execution_or_receipt"
    return "other_json"


def load_marker_rows():
    rows = defaultdict(lambda: {"occurrences": 0, "refs": [], "sources": set()})
    html_files = 0
    marker_files = 0
    if not V27.exists():
        raise RuntimeError(f"missing v27 output: {V27}")
    for path in V27.rglob("*.html"):
        html_files += 1
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        found = list(MARKER.finditer(text))
        if not found:
            continue
        marker_files += 1
        lines = text.splitlines()
        rel_file = str(path.relative_to(ROOT)).replace("\\", "/")
        for match in found:
            query = html.unescape(match.group(1))
            params = parse_qs(query, keep_blank_values=True)
            source = unquote(params.get("source", [""])[0])
            target = unquote(params.get("requested", [""])[0])
            if not source or not target:
                continue
            try:
                line = text.count("\n", 0, match.start()) + 1
            except Exception:
                line = 0
            row = rows[target]
            row["occurrences"] += 1
            row["sources"].add(source)
            if len(row["refs"]) < 8:
                row["refs"].append({
                    "output_file": rel_file,
                    "line": line,
                    "source_page": source,
                    "reason": params.get("reason", [""])[0],
                })
    return rows, {"html_files_read": html_files, "marker_files": marker_files}


def load_static_results():
    d = json.loads(STATIC_BATCH.read_text(encoding="utf-8")) if STATIC_BATCH.exists() else {}
    results = {}
    for entry in d.get("results", []):
        for key in (entry.get("canonical"), entry.get("requested"), entry.get("original")):
            if key:
                results[norm_url(key)] = entry
        cdx = entry.get("cdx") or {}
        for row in cdx.get("rows", []):
            original = row.get("original")
            if original:
                results.setdefault(norm_url(original), entry)
    accepted = set()
    if STATIC_ACCEPT.exists():
        a = json.loads(STATIC_ACCEPT.read_text(encoding="utf-8"))
        accepted.update(norm_url(x.get("original", "")) for x in a.get("accepted_images", []) if x.get("original"))
    return d, results, accepted


def collect_json_evidence():
    """Index URL-bearing JSON evidence without reading raw payloads."""
    roots = [ROOT / "research" / d for d in ("continuous-recovery-20261015", "continuous-recovery-20261016", "continuous-recovery-20261018")]
    files = []
    for base in roots:
        if not base.exists():
            continue
        for path in base.rglob("*.json"):
            if OUT in path.parents:
                continue
            if any(token in path.name.lower() for token in ("batch-report", "request-record", "source-map", "sanitized-summary", "plan", "candidates", "queue", "acceptance", "receipt")):
                files.append(path)
    index = defaultdict(list)
    for path in sorted(set(files)):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        urls = set()
        for value in recursive_strings(data):
            if value.startswith(("http://", "https://")) and is_image_url(value):
                urls.add(value)
        kind = evidence_kind(path)
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        for value in urls:
            index[norm_url(value)].append({"path": rel, "kind": kind, "exact": value})

        # Keep the nearest execution record's disposition so transport errors,
        # complete 404s, and accepted payloads are not collapsed into a single
        # "requested" label.  This remains JSON-only and never reads payloads.
        def add_context(node):
            if isinstance(node, dict):
                node_urls = [v for v in node.values() if isinstance(v, str) and v.startswith(("http://", "https://")) and is_image_url(v)]
                details = {k: node[k] for k in ("status", "category", "reason", "source_status", "transport_error", "unrequested_reason", "cdx_parse_error", "selected_capture", "query_performed", "body_bytes") if k in node}
                if node_urls and details:
                    for value in node_urls:
                        index[norm_url(value)].append({"path": rel, "kind": kind, "exact": value, "details": details})
                for value in node.values():
                    add_context(value)
            elif isinstance(node, list):
                for value in node:
                    add_context(value)
        add_context(data)
    return index, len(files)


def cdx_summary(entry):
    if not entry:
        return {"status": "not_in_static_main01", "complete": None, "selected": [], "rows": 0, "first_timestamp": None, "accepted_payloads": 0}
    cdx = entry.get("cdx") or {}
    rows = cdx.get("rows") or []
    selected = cdx.get("selected") or []
    return {
        "status": entry.get("status"),
        "cdx_source": entry.get("cdx_source"),
        "complete": bool(cdx.get("status", "").startswith("complete") and not cdx.get("potential_truncation", True)),
        "selected": [
            {"timestamp": x.get("timestamp"), "original": x.get("original"), "digest": x.get("digest"), "mimetype": x.get("mimetype"), "statuscode": x.get("statuscode"), "length": x.get("length"), "replay_url": x.get("replay_url")}
            for x in selected[:3]
        ],
        "rows": len(rows),
        "first_timestamp": rows[0].get("timestamp") if rows else None,
        "latest_unknown": bool(entry.get("latest_unknown")),
        "replay_count": len(entry.get("replay_results") or []),
        "accepted_payloads": len(entry.get("accepted_payloads") or []),
    }


def main():
    free_before = shutil.disk_usage(ROOT).free
    if free_before < 11_005_853_696:
        raise RuntimeError(f"D: below floor before audit: {free_before}")
    rows, scan_stats = load_marker_rows()
    static_batch, static_results, static_accepted = load_static_results()
    evidence, evidence_file_count = collect_json_evidence()
    source_hash_cache = {}
    all_rows = []
    for target, row in rows.items():
        parts = urlsplit(target)
        if parts.scheme not in {"http", "https"} or parts.query or parts.fragment or not is_image_url(target):
            continue
        source = sorted(row["sources"])[0]
        if is_news(source, target):
            continue
        cls = page_class(source, target)
        if cls not in {"armory", "guide_bc_insider", "other_static"}:
            continue
        norm = norm_url(target)
        static_entry = static_results.get(norm)
        static_status = cdx_summary(static_entry)
        ev = evidence.get(norm, [])
        accepted = norm in static_accepted or static_status["accepted_payloads"] > 0
        execution_records = [x for x in ev if x["kind"] == "execution_or_receipt"]
        plan_records = [x for x in ev if x["kind"] == "plan_or_queue"]
        all_evidence = execution_records + plan_records + [x for x in ev if x["kind"] == "other_json"]
        details = [x.get("details", {}) for x in all_evidence if x.get("details")]
        detail_text = " ".join(json.dumps(x, ensure_ascii=False).lower() for x in details)
        if accepted:
            prior = "already_accepted_static_payload"
        elif static_entry and static_status["status"] == "complete_no_eligible_capture":
            prior = "complete_cdx_no_eligible_capture"
        elif any(d.get("transport_error") is True or d.get("reason") in {"no_http_status", "transport_error"} for d in details):
            prior = "prior_execution_transport_unknown"
        elif any("404" in str(d.get("category", "")).lower() or "404" in str(d.get("reason", "")).lower() for d in details):
            prior = "prior_execution_complete_404_or_no_image"
        elif static_entry:
            prior = "static_main01_attempted"
        elif execution_records:
            prior = "prior_execution_record_outside_static_main01"
        elif plan_records:
            prior = "plan_or_queue_only_no_execution_record"
        else:
            prior = "no_matching_execution_or_cdx_record_found"
        page_file = ROOT / row["refs"][0]["output_file"]
        if page_file not in source_hash_cache:
            source_hash_cache[page_file] = {"sha256": sha256(page_file), "bytes": page_file.stat().st_size}
        first_cdx = static_status.get("first_timestamp")
        all_rows.append({
            "requested_url": target,
            "normalized_identity": norm,
            "category": cls,
            "visual_role": visual_role(target),
            "occurrences_in_v27_missing_markers": row["occurrences"],
            "source_pages_count": len(row["sources"]),
            "source_pages": sorted(row["sources"])[:8],
            "references": row["refs"],
            "source_output_page": row["refs"][0]["output_file"],
            "source_output_page_sha256": source_hash_cache[page_file]["sha256"],
            "source_output_page_bytes": source_hash_cache[page_file]["bytes"],
            "prior_attempt": prior,
            "static_main01_cdx": static_status,
            "existing_json_evidence": {
                "execution_or_receipt": execution_records[:8],
                "plan_or_queue_only": plan_records[:8],
                "other": [x for x in ev if x["kind"] == "other_json"][:4],
            },
            "complete_cdx_cache": static_status.get("complete") if static_entry else None,
            "known_cdx_or_replay_date": first_cdx,
            "selection_note": "Static marker and source evidence only; no new request made by this audit.",
        })

    # Keep the frontier useful for the next network wave: accepted/known full
    # empty captures are retained in excluded rows but are not re-queued.
    excluded = [r for r in all_rows if r["prior_attempt"] in {"already_accepted_static_payload", "complete_cdx_no_eligible_capture", "prior_execution_complete_404_or_no_image"}]
    candidates = [r for r in all_rows if r not in excluded]
    category_order = {"armory": 0, "guide_bc_insider": 1, "other_static": 2}
    visual_order = {"content_visual_candidate": 0, "icon_or_small_visual_candidate": 1, "layout_or_placeholder_candidate": 2}
    def rank_key(r):
        return (category_order.get(r["category"], 9), visual_order.get(r["visual_role"], 9), -r["occurrences_in_v27_missing_markers"], r["requested_url"])
    armory = sorted([r for r in candidates if r["category"] == "armory"], key=rank_key)[:20]
    content = sorted([r for r in candidates if r["category"] == "guide_bc_insider"], key=rank_key)[:20]
    selected = armory + content
    selected_keys = {r["requested_url"] for r in selected}
    if len(selected) < 40:
        for r in sorted([r for r in candidates if r["requested_url"] not in selected_keys], key=rank_key):
            selected.append(r)
            selected_keys.add(r["requested_url"])
            if len(selected) >= 40:
                break
    for i, r in enumerate(selected, 1):
        r["priority_rank"] = i
    selected.sort(key=lambda r: r["priority_rank"])
    output = {
        "schema": "wow-recovery.local-audit.static-frontier-v28.v1",
        "checked_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat().replace("+00:00", "Z"),
        "network_requests": 0,
        "scope": "Frozen v27 non-news missing-image markers; no raw image hashing, no network, no export mutation.",
        "inputs": {
            "v27_output": str(V27.relative_to(ROOT)).replace("\\", "/"),
            "v27_export_provenance_sha256": sha256(V27 / "export-provenance.json"),
            "static_main01_batch_report": str(STATIC_BATCH.relative_to(ROOT)).replace("\\", "/"),
            "static_main01_batch_report_sha256": sha256(STATIC_BATCH) if STATIC_BATCH.exists() else None,
            "static_main01_plan": str(STATIC_PLAN.relative_to(ROOT)).replace("\\", "/"),
            "static_main01_plan_sha256": sha256(STATIC_PLAN) if STATIC_PLAN.exists() else None,
            "static_main01_source_map": str(STATIC_MAP.relative_to(ROOT)).replace("\\", "/"),
            "static_main01_source_map_sha256": sha256(STATIC_MAP) if STATIC_MAP.exists() else None,
            "static_main01_acceptance": str(STATIC_ACCEPT.relative_to(ROOT)).replace("\\", "/"),
            "static_main01_acceptance_sha256": sha256(STATIC_ACCEPT) if STATIC_ACCEPT.exists() else None,
        },
        "scan": scan_stats,
        "evidence_json_files_indexed": evidence_file_count,
        "marker_targets": len(all_rows),
        "excluded_known_attempts": excluded,
        "candidates": selected,
        "candidate_counts": {
            "armory_available": len([r for r in candidates if r["category"] == "armory"]),
            "guide_bc_insider_available": len([r for r in candidates if r["category"] == "guide_bc_insider"]),
            "other_static_available": len([r for r in candidates if r["category"] == "other_static"]),
            "selected": len(selected),
            "excluded_known_attempts": len(excluded),
        },
        "selection_policy": {
            "first": "up to 20 armory/wowarmory/armory.wow-europe static image/icon targets",
            "second": "up to 20 Game Guide/BC/Insider content-image targets",
            "excluded": "news targets, query/account endpoints, accepted static payloads, and exact complete no-eligible-capture rows",
            "status_rule": "plan-only evidence is never reported as an executed request; complete CDX requires explicit complete status and no potential truncation",
        },
        "static_main01_batch_summary": {
            "batch_id": static_batch.get("batch_id"),
            "network_requests": static_batch.get("network_requests"),
            "source_responses": static_batch.get("source_responses"),
            "candidate_count": static_batch.get("candidate_count"),
            "stop_reason": static_batch.get("stop_reason"),
            "accepted_payloads": len(static_batch.get("accepted_payloads") or []),
        },
        "disk_free_before_bytes": free_before,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    out_json = OUT / "static-frontier-v28-candidates.json"
    out_json.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# v28 static frontier audit",
        "",
        f"Checked `{output['checked_utc']}`; network requests: `0`; v27 HTML files read: `{scan_stats['html_files_read']}`; files with markers: `{scan_stats['marker_files']}`.",
        f"Candidate pool after news/query/accepted/complete-empty exclusions: `{len(candidates)}`; selected: `{len(selected)}` (armory `{len(armory)}`, guide/BC/Insider `{len(content)}`).",
        "",
        "The table records exact marker URL, source-page/output line, source-page SHA, and prior evidence. `plan_or_queue_only` never counts as an executed request; `complete_cdx_cache` is true only for explicit complete CDX with no truncation.",
        "",
        "|#|class|occurrences|visual role|requested URL|prior attempt|CDX complete|source page:line|",
        "|---:|---|---:|---|---|---|---|---|",
    ]
    for r in selected:
        ref = r["references"][0]
        lines.append(f"|{r['priority_rank']}|{r['category']}|{r['occurrences_in_v27_missing_markers']}|{r['visual_role']}|`{r['requested_url']}`|{r['prior_attempt']}|{r['complete_cdx_cache']}|`{ref['output_file']}:{ref['line']}`|")
    lines += ["", "## Evidence boundaries", "", "- Existing receipts/plans were read locally only; this audit did not send CDX/replay/image requests.", "- Source-page SHA values hash the frozen v27 HTML source page, not the missing target image.", "- Exact complete-no-eligible-capture and already-accepted static-main rows are retained under `excluded_known_attempts` and are not re-queued.", ""]
    (OUT / "static-frontier-v28-candidates.md").write_text("\n".join(lines), encoding="utf-8")
    (OUT / "static-frontier-v28-audit-receipt.json").write_text(json.dumps({"schema": "wow-recovery.local-audit.static-frontier-v28.receipt.v1", "candidate_sha256": sha256(out_json), "markdown_sha256": sha256(OUT / "static-frontier-v28-candidates.md"), "network_requests": 0, "disk_free_before_bytes": free_before, "disk_free_after_bytes": shutil.disk_usage(ROOT).free}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"json": str(out_json.relative_to(ROOT)).replace("\\", "/"), "candidate_sha256": sha256(out_json), "selected": len(selected), "counts": output["candidate_counts"], "disk_free_after": shutil.disk_usage(ROOT).free}, ensure_ascii=False))


if __name__ == "__main__":
    main()
