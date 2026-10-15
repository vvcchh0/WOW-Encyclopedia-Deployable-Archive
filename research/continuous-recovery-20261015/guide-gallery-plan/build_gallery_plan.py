#!/usr/bin/env python3
"""Build a local, bounded plan for three previously unqueried galleries."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
INVENTORY = ROOT / "research/github-pages-20261013/gallery-inventory-20261013.json"
INSPECTION = ROOT / "research/github-pages-20261013/gallery-inspection-20261013.md"
MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v10/build-manifest.json"
PROVENANCE = ROOT / ".scratch/pages-resources-20261015-v10/export-provenance.json"
EXPORT_ROOT = ROOT / ".scratch/pages-resources-20261015-v10"
OLD_EVIDENCE = [
    ROOT / "research/gallery-recovery-20261014/karazhan/sanitized-summary.json",
    ROOT / "research/gallery-recovery-20261014/discovery-002/sanitized-summary.json",
]
TARGET_ROUTES = [
    "/info/dungeons/black-temple-gallery.html",
    "/info/dungeons/serpentshrine-gallery.html",
    "/info/dungeons/magisters-terrace-gallery.html",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> tuple[int, str]:
    h = hashlib.sha256()
    n = 0
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
            n += len(chunk)
    return n, h.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def line_number(text: str, position: int) -> int:
    return text[:position].count("\n") + 1


def line_text(text: str, number: int) -> str:
    lines = text.splitlines()
    return lines[number - 1].strip() if 0 < number <= len(lines) else ""


def extract_gallery(text: str) -> dict:
    num_match = re.search(r"\bnumShots\s*=\s*(\d+)", text, re.I)
    add_match = re.search(
        r"\baddshots\s*\(\s*(['\"])(.*?)\1\s*,\s*(['\"])(.*?)\3\s*,\s*numShots\s*\)",
        text,
        re.I | re.S,
    )
    if not num_match or not add_match:
        raise RuntimeError("gallery template fields not found")
    add_line = line_number(text, add_match.start())
    return {
        "num_shots": int(num_match.group(1)),
        "addshots_source_dir": add_match.group(2),
        "addshots_filename": add_match.group(4),
        "addshots_line": add_line,
        "addshots_markup": line_text(text, add_line),
    }


def extract_js_lines(text: str) -> dict:
    wanted = list(range(471, 488)) + [506, 507]
    lines = text.splitlines()
    return {str(n): lines[n - 1] if n <= len(lines) else "" for n in wanted}


def source_identity(url: str) -> dict[str, str]:
    p = urlsplit(url)
    return {"scheme": p.scheme.lower(), "host": (p.hostname or "").lower(), "path": p.path, "query": p.query}


def expected_url(page_source_base: str, directory: str, filename: str, n: int, thumb: bool = False) -> str:
    origin = f"{urlsplit(page_source_base).scheme}://{urlsplit(page_source_base).netloc}"
    suffix = f"{filename}{n}{'-thumb' if thumb else ''}.jpg"
    return urljoin(origin + "/", directory.lstrip("/") + suffix)


def route_for_url(url: str) -> str:
    p = urlsplit(url)
    return p.path


def direct_entity_state(prefix: str, count: int, manifest: dict, provenance: dict) -> dict:
    files = {x.get("route"): x for x in manifest.get("files", []) if x.get("route")}
    prov = {x.get("route"): x for x in provenance.get("files", []) if x.get("route")}
    origin_index = manifest.get("origin_index", {})
    full_records = []
    thumb_records = []
    missing_examples = []
    for n in range(1, count + 1):
        for is_thumb, bucket in ((False, full_records), (True, thumb_records)):
            path = f"{prefix}ss{n}{'-thumb' if is_thumb else ''}.jpg"
            row = files.get(path)
            prow = prov.get(path)
            origin_key = "www.worldofwarcraft.com" + path
            route_index = origin_index.get(origin_key)
            item = {
                "slot": n,
                "kind": "thumb" if is_thumb else "full",
                "route": path,
                "manifest_record": bool(row),
                "provenance_record": bool(prow),
                "origin_index_route": route_index,
                "manifest_output": row.get("output_path") if row else None,
                "manifest_sha256": row.get("derived_sha256") if row else None,
                "manifest_length": row.get("derived_length") if row else None,
            }
            bucket.append(item)
            if len(missing_examples) < 6 and not row and not prow and not route_index:
                missing_examples.append(item)
    return {
        "expected_slots": count,
        "expected_direct_entities": count * 2,
        "full_manifest_records": sum(1 for x in full_records if x["manifest_record"]),
        "thumb_manifest_records": sum(1 for x in thumb_records if x["manifest_record"]),
        "full_provenance_records": sum(1 for x in full_records if x["provenance_record"]),
        "thumb_provenance_records": sum(1 for x in thumb_records if x["provenance_record"]),
        "full_origin_index_records": sum(1 for x in full_records if x["origin_index_route"]),
        "thumb_origin_index_records": sum(1 for x in thumb_records if x["origin_index_route"]),
        "missing_examples": missing_examples,
        "full_records": full_records,
        "thumb_records": thumb_records,
    }


def prior_coverage(prefix: str) -> dict:
    checked = []
    hits = []
    for path in OLD_EVIDENCE:
        length, digest = sha256(path)
        data = load(path)
        checked.append({"path": rel(path), "bytes": length, "sha256": digest})
        raw = json.dumps(data, ensure_ascii=False)
        if prefix in raw:
            hits.append(rel(path))
    return {
        "status": "evidence_hit" if hits else "not_checked",
        "evidence_files": checked,
        "prefix_hits": hits,
        "reason": "Only the explicitly listed Karazhan/discovery-002 summaries were inspected; absence is not evidence that this prefix was never queried." if not hits else "The bounded evidence set contains this prefix.",
    }


def main() -> int:
    inventory = load(INVENTORY)
    manifest = load(MANIFEST)
    provenance = load(PROVENANCE)
    rows = {x["route"]: x for x in inventory["rows"]}
    mfiles = {x.get("route"): x for x in manifest.get("files", []) if x.get("route")}
    pfiles = {x.get("route"): x for x in provenance.get("files", []) if x.get("route")}
    js_route = "/new-hp/js/guidegallery-screenie.js"
    js_row = mfiles[js_route]
    js_path = ROOT / js_row["output_path"]
    js_bytes, js_sha = sha256(js_path)
    js_text = js_path.read_text(encoding="utf-8", errors="replace")
    js_evidence = {
        "route": js_route,
        "path": rel(js_path),
        "bytes": js_bytes,
        "sha256": js_sha,
        "manifest_sha256": js_row.get("derived_sha256"),
        "manifest_length": js_row.get("derived_length"),
        "lines": extract_js_lines(js_text),
        "rules": {
            "full": "sourceDirectory + filename + N + '.jpg'",
            "thumb": "full URL with '.jpg' replaced by '-thumb.jpg' (guidegallery-screenie.js:506-507)",
        },
    }
    out = {
        "schema": "wow-recovery.guide-gallery-plan.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "network_requests": 0,
        "scope": "Black Temple, Serpentshrine Cavern, Magister's Terrace only",
        "excluded_scope": ["Karazhan", "Fishing", "Zul'Aman wrapper"],
        "inputs": {},
        "shared_gallery_js": js_evidence,
        "galleries": [],
    }
    input_paths = [INVENTORY, INSPECTION, MANIFEST, PROVENANCE, js_path, *OLD_EVIDENCE]
    for path in input_paths:
        size, digest = sha256(path)
        out["inputs"][rel(path)] = {"bytes": size, "sha256": digest}

    for route in TARGET_ROUTES:
        inv = rows[route]
        mrow = mfiles[route]
        prow = pfiles[route]
        source_path = ROOT / mrow["source_local_path"]
        derived_path = ROOT / mrow["output_path"]
        export_path = EXPORT_ROOT / prow["output_path"]
        source_bytes, source_sha = sha256(source_path)
        derived_bytes, derived_sha = sha256(derived_path)
        export_bytes, export_sha = sha256(export_path)
        source_text = source_path.read_text(encoding="utf-8", errors="replace")
        derived_text = derived_path.read_text(encoding="utf-8", errors="replace")
        export_text = export_path.read_text(encoding="utf-8", errors="replace")
        source_template = extract_gallery(source_text)
        derived_template = extract_gallery(derived_text)
        export_template = extract_gallery(export_text)
        source_dir = source_template["addshots_source_dir"]
        page_source_base = mrow["source_base_url"]
        prefix_url = urljoin(f"{urlsplit(page_source_base).scheme}://{urlsplit(page_source_base).netloc}/", source_dir.lstrip("/"))
        direct = direct_entity_state(source_dir, source_template["num_shots"], manifest, provenance)
        out["galleries"].append({
            "label": inv["label"],
            "category": inv["category"],
            "route": route,
            "index_line": inv["index_line"],
            "page_source_base_url": page_source_base,
            "page_source_identity": source_identity(page_source_base),
            "inventory_observation": {
                "source_html_exists": inv.get("source_html_exists"),
                "export_html_exists": inv.get("export_html_exists"),
                "source_html_manifest": inv.get("source_html_manifest"),
                "export_html_provenance": inv.get("export_html_provenance"),
                "route_map_html": inv.get("route_map_html"),
                "source_counts": inv.get("source_counts"),
                "export_counts": inv.get("export_counts"),
                "manifest_direct_full": inv.get("manifest_direct_full"),
                "manifest_direct_thumb": inv.get("manifest_direct_thumb"),
                "provenance_direct_full": inv.get("provenance_direct_full"),
                "provenance_direct_thumb": inv.get("provenance_direct_thumb"),
            },
            "source_html": {
                "path": rel(source_path),
                "bytes": source_bytes,
                "sha256": source_sha,
                "manifest_sha256": mrow.get("source_sha256"),
                "manifest_length": mrow.get("source_length"),
                "actual_timestamp": mrow.get("actual_timestamp"),
                "template": source_template,
            },
            "v10_derived_html": {
                "path": rel(derived_path),
                "bytes": derived_bytes,
                "sha256": derived_sha,
                "manifest_sha256": mrow.get("derived_sha256"),
                "manifest_length": mrow.get("derived_length"),
                "template": derived_template,
            },
            "final_export_html": {
                "path": rel(export_path),
                "bytes": export_bytes,
                "sha256": export_sha,
                "provenance_sha256": prow.get("derived_sha256"),
                "provenance_length": prow.get("derived_length"),
                "template": export_template,
            },
            "shot_template": {
                "source_directory": source_dir,
                "filename": source_template["addshots_filename"],
                "num_shots": source_template["num_shots"],
                "first_full_url": expected_url(page_source_base, source_dir, source_template["addshots_filename"], 1),
                "first_thumb_url": expected_url(page_source_base, source_dir, source_template["addshots_filename"], 1, True),
                "last_full_url": expected_url(page_source_base, source_dir, source_template["addshots_filename"], source_template["num_shots"]),
                "last_thumb_url": expected_url(page_source_base, source_dir, source_template["addshots_filename"], source_template["num_shots"], True),
            },
            "direct_entity_state": direct,
            "prior_query_coverage": prior_coverage(source_dir),
            "derived_addshots_diagnostic": {
                "source": source_template["addshots_source_dir"],
                "v10_derived": derived_template["addshots_source_dir"],
                "final_export": export_template["addshots_source_dir"],
                "final_export_is_missing_html": "/__offline/missing.html" in export_template["addshots_source_dir"],
                "final_export_is_localized_route": "/WOW-Encyclopedia-Deployable-Archive/" in export_template["addshots_source_dir"],
                "interpretation": "static export-path diagnostic only; no production fix made",
            },
        })

    proposals = []
    for g in out["galleries"]:
        proposals.append({
            "gallery": g["label"],
            "exact_prefix_url": g["shot_template"]["first_full_url"].rsplit("ss1.jpg", 1)[0],
            "matchType": "prefix",
            "query_constraints": ["statuscode:200", "mimetype:image/*", "collapse=digest", "preserve exact origin and prefix; no basename substitution"],
            "time_window_proposal": {"from": "20060101000000", "to": "20081231235959", "reason": "bounded historical proposal around the fixed 2008 archive anchor; not a claim of existing captures"},
            "expected_slot_count": g["shot_template"]["num_shots"],
            "expected_entities": g["shot_template"]["num_shots"] * 2,
            "local_evidence": {"manifest_full": g["direct_entity_state"]["full_manifest_records"], "manifest_thumb": g["direct_entity_state"]["thumb_manifest_records"], "provenance_full": g["direct_entity_state"]["full_provenance_records"], "provenance_thumb": g["direct_entity_state"]["thumb_provenance_records"]},
            "prior_query_coverage": g["prior_query_coverage"],
            "priority": "P1",
        })
    out["summary"] = {
        "target_galleries": len(out["galleries"]),
        "total_shots": sum(g["shot_template"]["num_shots"] for g in out["galleries"]),
        "expected_direct_entities": sum(g["shot_template"]["num_shots"] * 2 for g in out["galleries"]),
        "manifest_direct_full": sum(g["direct_entity_state"]["full_manifest_records"] for g in out["galleries"]),
        "manifest_direct_thumb": sum(g["direct_entity_state"]["thumb_manifest_records"] for g in out["galleries"]),
        "provenance_direct_full": sum(g["direct_entity_state"]["full_provenance_records"] for g in out["galleries"]),
        "provenance_direct_thumb": sum(g["direct_entity_state"]["thumb_provenance_records"] for g in out["galleries"]),
        "prior_prefixes_with_explicit_evidence": sum(1 for g in out["galleries"] if g["prior_query_coverage"]["status"] == "evidence_hit"),
        "network_requests": 0,
        "final_export_missing_html_addshots": sum(1 for g in out["galleries"] if g["derived_addshots_diagnostic"]["final_export_is_missing_html"]),
        "final_export_localized_addshots": sum(1 for g in out["galleries"] if g["derived_addshots_diagnostic"]["final_export_is_localized_route"]),
    }
    out["cdx_prefix_proposals"] = proposals
    (OUT / "guide-gallery-plan.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "cdx-prefix-proposals.json").write_text(json.dumps({"schema": "wow-recovery.guide-gallery-cdx-prefix-proposals.v1", "generated_utc": out["generated_utc"], "network_requests": 0, "proposals": proposals}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Three gallery local plan",
        "",
        f"Generated `{out['generated_utc']}` with `network_requests=0`. Scope is Black Temple, Serpentshrine Cavern, and Magister's Terrace. Karazhan, Fishing, and the Zul'Aman wrapper are excluded.",
        "",
        "## Matrix",
        "",
        "| gallery | route | shots | source addshots | expected entities | manifest full/thumb | provenance full/thumb | prior prefix evidence | final addshots |",
        "|---|---|---:|---|---:|---:|---:|---|---|",
    ]
    for g in out["galleries"]:
        d = g["direct_entity_state"]
        lines.append(f"| {g['label']} | `{g['route']}` | {g['shot_template']['num_shots']} | `{g['shot_template']['source_directory']}` `{g['shot_template']['filename']}` | {g['shot_template']['num_shots']*2} | {d['full_manifest_records']}/{d['thumb_manifest_records']} | {d['full_provenance_records']}/{d['thumb_provenance_records']} | `{g['prior_query_coverage']['status']}` | `{g['derived_addshots_diagnostic']['final_export']}` |")
    lines += ["", "All three source page payloads and v10 derived/final export HTML files are hash-recorded in JSON. The source page capture timestamp and source/derived SHA are retained per row. The shared JS rule is recorded with its actual v10 file SHA and lines 471-487/506-507.", "", "## Exact prefix proposals", ""]
    for p in proposals:
        lines.append(f"- **{p['gallery']}**: `{p['exact_prefix_url']}`; `matchType=prefix`, `statuscode:200`, `mimetype=image/*`, `collapse=digest`; proposed window `{p['time_window_proposal']['from']}`–`{p['time_window_proposal']['to']}`. This is a query proposal, not capture evidence.")
    lines += ["", "## Findings and limits", "", f"The three galleries contain {out['summary']['total_shots']} slots and {out['summary']['expected_direct_entities']} expected direct full/thumb entities. Current v10 manifest and export provenance contain zero direct full and zero direct thumbnail records for all three prefixes. The explicitly inspected old evidence covers only Karazhan/Fishing, so these three prefixes remain `not_checked`; no absence claim is made.", "", f"The current final export has `{out['summary']['final_export_localized_addshots']}` localized addshots directories and `{out['summary']['final_export_missing_html_addshots']}` missing.html addshots directories for these three pages. This is a static export-path observation only. The direct screenshot entities remain absent from current manifest/provenance.", "", "No production, source, ledger, export, or frozen baseline file was changed. No full URL enumeration was performed.", ""]
    (OUT / "guide-gallery-plan.md").write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
