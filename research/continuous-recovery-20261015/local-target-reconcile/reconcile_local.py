from __future__ import annotations

import hashlib
import html
import json
import re
from datetime import datetime, timezone
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "research/continuous-recovery-20261015/local-target-reconcile"
AUDIT_PATH = ROOT / "research/continuous-recovery-20261015/sidebar-audit/audit.json"
FROZEN_MANIFEST = ROOT / "offline/build-manifest.json"
V7C_ROOT = ROOT / ".scratch/offline-navigation-20261015-v7c"
V7C_MANIFEST = V7C_ROOT / "build-manifest.json"
V8_ROUTE_MAP = ROOT / ".scratch/pages-resources-20261015-v8/__offline/route-map.json"
MIRROR_URL_MAP = ROOT / "mirror/20080512/url-map.json"
MIRROR_NAVTREE = ROOT / "mirror/20080512/www.worldofwarcraft.com/shared/wow-com/includes-client/navtree.js"

TARGET_PREFIXES = ("/account", "/loginsupport", "/support", "/billing")
HOSTS = {"www.worldofwarcraft.com", "worldofwarcraft.com"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_url_path(value) -> str | None:
    if not isinstance(value, str):
        return None
    value = html.unescape(value).strip()
    if not value:
        return None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        if parsed.hostname and parsed.hostname.lower() not in HOSTS:
            return None
        value = parsed.path or "/"
    else:
        value = parsed.path or value
    if not value.startswith("/"):
        value = "/" + value
    value = re.sub(r"/{2,}", "/", value)
    if value != "/":
        value = value.rstrip("/") if value.endswith("/") and "." not in value.rsplit("/", 1)[-1] else value
    return value


def relative_actual(path_value) -> Path | None:
    if not isinstance(path_value, str) or not path_value:
        return None
    path = ROOT / path_value
    try:
        path.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return None
    return path


def inspect_file(path_value, expected_sha=None, expected_length=None):
    path = relative_actual(path_value)
    result = {"path": path_value, "exists": bool(path and path.is_file())}
    if not result["exists"]:
        return result
    result["length"] = path.stat().st_size
    result["sha256"] = sha256(path)
    if expected_sha:
        result["sha256_matches_manifest"] = result["sha256"] == expected_sha
    if expected_length is not None:
        result["length_matches_manifest"] = result["length"] == expected_length
    return result


def entry_digest(e):
    return {
        "route": e.get("route"),
        "output_path": e.get("output_path"),
        "source_local_path": e.get("source_local_path"),
        "source_base_url": e.get("source_base_url"),
        "source_sha256": e.get("source_sha256"),
        "source_length": e.get("source_length"),
        "derived_sha256": e.get("derived_sha256"),
        "derived_length": e.get("derived_length"),
        "source_mime": e.get("source_mime"),
        "mime": e.get("mime"),
        "kind": e.get("kind"),
        "role": e.get("role"),
        "source_file_check": inspect_file(e.get("source_local_path"), e.get("source_sha256"), e.get("source_length")),
        "output_file_check": inspect_file(e.get("output_path"), e.get("derived_sha256"), e.get("derived_length")),
    }


def find_navtree_line(needle: str):
    if not MIRROR_NAVTREE.exists():
        return None
    for no, line in enumerate(MIRROR_NAVTREE.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if needle.lower() in line.lower():
            return {"path": "mirror/20080512/www.worldofwarcraft.com/shared/wow-com/includes-client/navtree.js", "line": no, "text": line.strip()}
    return None


def route_value(map_obj, target):
    return map_obj.get("routes", {}).get(target), map_obj.get("aliases", {}).get(target)


def original_map_hits(url_map, target):
    hits = []
    for key, value in url_map.items() if isinstance(url_map, dict) else []:
        key_path = normalize_url_path(str(key))
        if key_path == target:
            hits.append({"key": key, "value": value})
    return hits


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    audit = load(AUDIT_PATH)
    v7c = load(V7C_MANIFEST)
    v8 = load(V8_ROUTE_MAP)
    url_map = load(MIRROR_URL_MAP) if MIRROR_URL_MAP.exists() else {}

    records = [r for r in audit["records"] if r.get("current_page_status") == "missing_export_route"]
    groups = defaultdict(list)
    for record in records:
        groups[record["normalized_route"]].append(record)
    targets = sorted(groups)
    if len(records) != 40 or len(targets) != 35:
        raise AssertionError(f"expected 40 observations/35 targets, got {len(records)}/{len(targets)}")
    family_counts = Counter(
        "rss" if target.startswith("/news/rss-") else "news_html" if target.startswith("/news/wow-news") else "other"
        for target in targets
    )
    generated_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    files = v7c.get("files", [])
    files_by_route = defaultdict(list)
    files_by_source = defaultdict(list)
    for entry in files:
        route = normalize_url_path(entry.get("route"))
        source_route = normalize_url_path(entry.get("source_base_url"))
        if route:
            files_by_route[route].append(entry)
        if source_route:
            files_by_source[source_route].append(entry)

    # These are intentionally evidence candidates, not automatic aliases.  The
    # old menu URL and the current local URL must still be proved equivalent.
    alternate_routes = {
        "/pvp/battlegrounds/battlegroups.html": ["/pvp/battlegrounds/battlegroups/index.html"],
        "/burningcrusade/townhall/professions.html": ["/info/professions/index.html"],
        "/ptr": ["/info/faq/ptr.html", "/contests/ptr-contest/index.html"],
        "/wrath/artwork.xml": ["/burningcrusade/artwork.html"],
    }

    # Representative exact captures for the next network worker.  The complete
    # target list remains in reconciliation.json; these 12 are the bounded queue.
    queue_order = [
        "/news/rss-05-2008.xml",
        "/news/rss-01-2008.xml",
        "/news/rss-12-2007.xml",
        "/news/rss-01-2007.xml",
        "/news/rss-12-2006.xml",
        "/news/rss-07-2006.xml",
        "/news/wow-news2005.html",
        "/news/wow-news2004.html",
        "/news/wow-news-06-2005.html",
        "/ptr",
        "/burningcrusade/townhall/professions.html",
        "/wrath/artwork.xml",
    ]

    rows = []
    for target in targets:
        observations = groups[target]
        scope_excluded = target.startswith(TARGET_PREFIXES)
        v8_route, v8_alias = route_value(v8, target)
        v7_alias = v7c.get("route_aliases", {}).get(target)
        canonical_candidates = []
        if target.endswith(".html"):
            stem = target[:-5]
            c_route, c_alias = route_value(v8, stem)
            if c_route or c_alias or stem in v7c.get("route_aliases", {}):
                canonical_candidates.append({"key": stem, "v8_route": c_route, "v8_alias": c_alias, "v7c_route_alias": v7c.get("route_aliases", {}).get(stem)})
        exact_files = files_by_route.get(target, [])
        exact_source = files_by_source.get(target, [])
        exact_entries = exact_files + [e for e in exact_source if e not in exact_files]
        nav_evidence = []
        for r in observations:
            nav_evidence.append({
                "record_id": r.get("record_id"),
                "source_menu": r.get("source_menu"),
                "source_line": r.get("source_line"),
                "label": r.get("label"),
                "href": r.get("href"),
                "source_role": r.get("source_role"),
            })

        local_evidence = [
            {"path": "research/continuous-recovery-20261015/sidebar-audit/audit.json", "field": f"records[{observations[0].get('record_id')}]", "detail": "final audit observation"},
            {"path": ".scratch/pages-resources-20261015-v8/__offline/route-map.json", "field": f"routes[{target}] / aliases[{target}]", "detail": {"route": v8_route, "alias": v8_alias, "canonical_candidates": canonical_candidates}},
            {"path": ".scratch/offline-navigation-20261015-v7c/build-manifest.json", "field": f"files[].route/source_base_url == {target}", "detail": {"route_matches": len(exact_files), "source_matches": len(exact_source), "route_alias": v7_alias}},
            {"path": "mirror/20080512/url-map.json", "field": f"normalized source URL {target}", "detail": original_map_hits(url_map, target)},
        ]

        alternates = []
        for alt in alternate_routes.get(target, []):
            alt_route, alt_alias = route_value(v8, alt)
            alt_entries = files_by_route.get(alt, [])
            if not alt_entries:
                alt_entries = files_by_source.get(alt, [])
            for e in alt_entries[:2]:
                alternates.append({
                    "route": alt,
                    "route_map_value": alt_route,
                    "alias_map_value": alt_alias,
                    "manifest": entry_digest(e),
                    "equivalence": "candidate_only",
                })
            if alt not in [a["route"] for a in alternates]:
                alternates.append({"route": alt, "route_map_value": alt_route, "alias_map_value": alt_alias, "manifest": None, "equivalence": "candidate_only"})

        # Very narrow same-parent scan is useful as evidence for pages with a
        # known alternate, while avoiding a blind raw-content scan.
        related = []
        if target == "/ptr":
            related = [e for e in files if "/ptr" in str(e.get("route", "")).lower()][:4]
        elif target == "/wrath/artwork.xml":
            related = [e for e in files if "artwork" in str(e.get("route", "")).lower()][:4]
        elif target == "/burningcrusade/townhall/professions.html":
            related = [e for e in files if str(e.get("route", "")).startswith("/info/professions")][:4]
        elif target == "/pvp/battlegrounds/battlegroups.html":
            related = [e for e in files if str(e.get("route", "")).startswith("/pvp/battlegrounds/battlegroups")][:4]
        related_evidence = [entry_digest(e) for e in related]

        for alt in alternates:
            if alt.get("manifest"):
                local_evidence.append({"path": ".scratch/offline-navigation-20261015-v7c/build-manifest.json", "field": f"files[].route == {alt['route']}", "detail": {"source_local_path": alt["manifest"].get("source_local_path"), "source_sha256": alt["manifest"].get("source_sha256"), "source_length": alt["manifest"].get("source_length"), "output_path": alt["manifest"].get("output_path"), "source_file_check": alt["manifest"].get("source_file_check"), "output_file_check": alt["manifest"].get("output_file_check")}})

        navtree = None
        if target == "/pvp/battlegrounds/battlegroups.html":
            navtree = find_navtree_line("Battlegroups")
            if navtree:
                local_evidence.append(navtree)

        if exact_entries:
            classification = "source_present_route_present"
            next_action = "No route repair required; reconcile duplicate menu observation against the exact manifest entity."
            alias_status = "exact"
        elif scope_excluded:
            classification = "scope_excluded_business_or_sensitive"
            next_action = "Keep outside the content recovery/network queue; no form or account interaction was attempted."
            alias_status = "not_applicable"
        elif target == "/pvp/battlegrounds/battlegroups.html" and alternates:
            classification = "route_only_candidate"
            alias_status = "candidate_alias_needs_proof"
            next_action = "Existing local battlegroups entity is at the index route; verify old .html equivalence before adding a compatibility alias."
        elif target == "/burningcrusade/townhall/professions.html" and alternates:
            classification = "source_present_route_missing_candidate_alias"
            alias_status = "candidate_alias_needs_proof"
            next_action = "Prove requested URL equivalence (redirect, same source URL, or byte/content evidence) before adding an alias; otherwise capture the exact URL."
        else:
            classification = "source_missing_candidate"
            alias_status = "none_found_locally"
            next_action = "Queue exact original URL for network capture; do not infer an alias from neighboring months or expansion pages."

        if target == "/burningcrusade/townhall/professions.html":
            next_action = "The generic professions index is local, but BC Townhall source equivalence is unproven; capture the exact BC URL before aliasing."
        if target == "/wrath/artwork.xml":
            next_action = "Related Burning Crusade artwork and Wrath static art assets do not prove the Wrath XML page; capture the exact URL."
        if target == "/ptr":
            next_action = "PTR-related FAQ/contest entities are local but are not proof of a /ptr landing page; capture exact /ptr or document redirect."

        if target == "/pvp/battlegrounds/battlegroups.html" and navtree:
            local_evidence.append({"path": navtree["path"], "field": f"line {navtree['line']}", "detail": "newer navtree records /pvp/battlegrounds/battlegroups/index.html"})

        if target == "/pvp/battlegrounds/battlegroups.html" and canonical_candidates:
            alias_status = "canonical_output_present_legacy_equivalence_review"

        row = {
            "target": target,
            "observation_count": len(observations),
            "source_menu": nav_evidence,
            "exact_original_url": f"http://www.worldofwarcraft.com{target}",
            "route_map": {"v8_route": v8_route, "v8_alias": v8_alias, "v7c_route_alias": v7_alias, "canonical_candidates": canonical_candidates},
            "classification": classification,
            "source_presence": "exact_entity" if exact_entries else ("alternate_entity" if target in {"/pvp/battlegrounds/battlegroups.html", "/burningcrusade/townhall/professions.html"} and alternates else ("related_entity_only" if alternates else "no_exact_entity")),
            "resolved_path": v8_route,
            "alternate_routes": alternates,
            "related_local_entities": related_evidence,
            "alias_status": alias_status,
            "local_search_evidence": local_evidence,
            "network_queue_eligible": bool(not scope_excluded and target in queue_order),
            "priority": "P0" if target.startswith("/news/") else ("P1" if not scope_excluded else "P2"),
            "recommended_capture_constraints": [
                "Request the exact original URL without month/path substitution or query broadening.",
                "Record status, redirect chain, response MIME, byte length, SHA-256, and capture timestamp.",
                "Preserve XML versus HTML MIME/body separately; a same-month or same-label page is not an alias proof.",
            ],
            "next_action": next_action,
        }
        rows.append(row)

    # Add a compact per-target source presence check for the direct filesystem
    # path. This is supplementary evidence and never promotes an alias by itself.
    for row in rows:
        target = row["target"]
        direct_rel = ".scratch/offline-navigation-20261015-v7c/site" + target
        direct = inspect_file(direct_rel)
        row["local_search_evidence"].append({"path": direct_rel, "field": "filesystem exact target", "detail": direct})

    counts = Counter(row["classification"] for row in rows)
    queue_rows = []
    for rank, target in enumerate(queue_order, 1):
        row = next(r for r in rows if r["target"] == target)
        queue_rows.append({
            "queue_id": f"LOCAL-TARGET-RECONCILE-002-{rank:02d}",
            "target": target,
            "exact_original_url": row["exact_original_url"],
            "observation_count": row["observation_count"],
            "classification": row["classification"],
            "priority": row["priority"],
            "menu_evidence": row["source_menu"],
            "local_search_evidence": row["local_search_evidence"],
            "recommended_capture_constraints": row["recommended_capture_constraints"],
            "recommended_capture": "Capture exact URL first; if redirect, preserve the full chain and separately hash the final payload. Do not substitute a neighboring archive month.",
        })

    input_files = [AUDIT_PATH, FROZEN_MANIFEST, V7C_MANIFEST, V8_ROUTE_MAP]
    input_hashes = {str(p.relative_to(ROOT)).replace("\\", "/"): {"sha256": sha256(p), "bytes": p.stat().st_size} for p in input_files}
    reconciliation = {
        "schema": "wow-recovery.local-target-reconciliation.v1",
        "task_id": "LOCAL-TARGET-RECONCILE-002",
        "generated_utc": generated_utc,
        "network_performed": False,
        "network_request_count": 0,
        "scope": {"source": "final sidebar audit missing_export_route", "observations": len(records), "distinct_targets": len(targets), "account_or_sensitive_excluded_in_reconciled_subset": sum(r["target"].startswith(TARGET_PREFIXES) for r in rows), "account_or_sensitive_in_final_audit_outside_subset": sum(r.get("current_page_status") == "business_or_sensitive" for r in audit["records"]), "account_or_sensitive_routes_outside_subset": sorted({r.get("normalized_route") for r in audit["records"] if r.get("current_page_status") == "business_or_sensitive"})},
        "target_family_counts": dict(sorted(family_counts.items())),
        "input_hashes": input_hashes,
        "frozen_manifest_sha256_expected": "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459",
        "frozen_manifest_sha256_observed": input_hashes["offline/build-manifest.json"]["sha256"],
        "conservation": {"observations_expected": 40, "observations_reconciled": sum(r["observation_count"] for r in rows), "targets_expected": 35, "targets_reconciled": len(rows), "ok": sum(r["observation_count"] for r in rows) == 40 and len(rows) == 35},
        "classification_counts": dict(sorted(counts.items())),
        "rows": rows,
        "production_edit_suggestions": [
            {"file": "offline/approved-route-alias-overlay.json", "suggestion": "After proof only, add compatibility aliases for old battlegroups/professions paths; do not hand-edit generated route-map.json."},
            {"file": "offline/approved-pages-recovery-map.json", "suggestion": "For any captured news/PTR/artwork page, add an evidence-backed source record with exact original URL, timestamp, MIME, length, and SHA-256."},
            {"file": "offline/approved-pages-temporal-supplement-map.json", "suggestion": "Use only when a later/alternate timestamp is explicitly accepted; preserve original target and capture provenance."},
            {"file": ".scratch/offline-navigation-20261015-v9/build-manifest.json", "suggestion": "Generate a new derived staging manifest after review; keep frozen offline/build-manifest.json unchanged."},
        ],
    }

    queue = {
        "schema": "wow-recovery.network-query-queue.v1",
        "task_id": "LOCAL-TARGET-RECONCILE-002",
        "network_performed": False,
        "queue_limit": 12,
        "queue_count": len(queue_rows),
        "conservation_reference": {"all_reconciled_targets": len(rows), "queued_targets": len(queue_rows), "deferred_targets": len(rows) - len(queue_rows)},
        "entries": queue_rows,
        "deferred_targets": [r["target"] for r in rows if r["target"] not in queue_order],
        "exclusion_rule": "Account, login-support, support, and billing targets are never sent to the network queue in this local audit.",
    }

    (OUT / "reconciliation.json").write_text(json.dumps(reconciliation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "network-query-queue.json").write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Local target reconciliation — LOCAL-TARGET-RECONCILE-002",
        "",
        f"This report is local-only and was generated at `{generated_utc}`. Network requests: **0**. No production edit, Git operation, or deployment was performed.",
        "",
        "## Inputs and conservation",
        "",
        f"The final sidebar audit contributed **{len(records)} observations over {len(targets)} distinct normalized targets**. Reconciliation preserves {sum(r['observation_count'] for r in rows)} observations over {len(rows)} rows: **{family_counts['rss']} RSS**, **{family_counts['news_html']} News HTML**, and **{family_counts['other']} other targets**.",
        f"Frozen `offline/build-manifest.json` observed SHA-256: `{input_hashes['offline/build-manifest.json']['sha256']}`; expected frozen SHA-256 matches: `{input_hashes['offline/build-manifest.json']['sha256'] == '397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459'}`.",
        "",
        "## Classification counts",
        "",
        "| Classification | Targets | Observations |",
        "|---|---:|---:|",
    ]
    for classification, count in sorted(counts.items()):
        lines.append(f"| `{classification}` | {count} | {sum(r['observation_count'] for r in rows if r['classification'] == classification)} |")
    lines.extend(["", "## Target rows", "", "| Target | Obs. | Classification | Local alternate/entity | Next action |", "|---|---:|---|---|---|"])
    for row in rows:
        alts = ", ".join(a["route"] for a in row["alternate_routes"][:3]) or "none found"
        lines.append(f"| `{row['target']}` | {row['observation_count']} | `{row['classification']}` | {alts} | {row['next_action']} |")
    lines.extend([
        "",
        "## Highest-value conclusions",
        "",
        "1. The 23 RSS targets and eight old HTML news targets have no exact local `files[].route`, `source_base_url`, mirror URL-map entry, or exact staging file; same-month or neighboring archive pages were not treated as aliases.",
        "2. `/pvp/battlegrounds/battlegroups.html` is the strongest route-only candidate: v8 maps the extensionless canonical key `/pvp/battlegrounds/battlegroups` to a `.html` output, while the v7c manifest has a verified local source entity at `/pvp/battlegrounds/battlegroups/index.html` (`source_length=26271`, source SHA recorded in `reconciliation.json`) and the newer mirror navtree points to the index route. Treat legacy equivalence as a review step before adding an explicit alias.",
        "3. `/burningcrusade/townhall/professions.html` has a local generic professions index, but its source URL is `/info/professions/`; this is a candidate alias only and does not prove BC Townhall equivalence.",
        "4. `/ptr` has local PTR-related FAQ/contest pages, but no local `/ptr` entity; those related pages are not substituted.",
        "5. `/wrath/artwork.xml` has a local Burning Crusade artwork page and Wrath artwork assets, but no Wrath XML page or source URL; static assets are evidence of dependencies only.",
        "6. The bounded queue contains 12 exact original URLs. The remaining targets are listed under `deferred_targets` and remain in the complete reconciliation.",
        "",
        "## Network queue",
        "",
        "`network-query-queue.json` contains 12 entries. Capture each exact URL first, preserve redirect/MIME/body/hash/timestamp, and do not substitute neighboring months. Account/login/support targets are excluded by rule.",
        "",
        "## Suggested production files (not edited)",
        "",
        "- `offline/approved-route-alias-overlay.json`: add only proof-backed compatibility aliases for route-only candidates.",
        "- `offline/approved-pages-recovery-map.json` or `offline/approved-pages-temporal-supplement-map.json`: add exact captured pages with original URL and payload evidence.",
        "- A new derived staging manifest such as `.scratch/offline-navigation-20261015-v9/build-manifest.json`: regenerate after approved map changes; keep frozen `offline/build-manifest.json` untouched.",
        "",
        "## Validation",
        "",
        "- Python script loaded the final audit, v7c manifest, v8 route-map, and mirror URL-map; conservation assertion passed at 40/35.",
        "- Every row includes menu evidence and local route/manifest/filesystem evidence; alternate hashes and lengths are recorded when a local entity exists.",
        "- Network flag is false, recorded request count is 0, and no network libraries or calls are used by the script.",
    ])
    (OUT / "reconciliation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"targets": len(rows), "observations": sum(r["observation_count"] for r in rows), "classification_counts": dict(counts), "queue": len(queue_rows), "frozen_sha_ok": input_hashes["offline/build-manifest.json"]["sha256"] == "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
