"""Build a compact, source-literal-backed 50-gallery prefix registry.

This is a local reconciliation only.  It records what the saved prefix
reports searched and what they returned; it never turns a missing report into
an assertion that a URL was never requested globally.
"""

from __future__ import annotations

import collections
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
V15_SITE = ROOT / ".scratch/offline-navigation-20261015-v15/site"
INVENTORY = ROOT / "research/github-pages-20261013/gallery-inventory-20261013.json"
RECHECK = ROOT / "research/local-maintenance-20261014/gallery-route-entity-recheck.json"
DIRECT_AUDIT = ROOT / "research/continuous-recovery-20261016/local-audit/v2/gallery-direct-entity-audit-v2.json"
JS = V15_SITE / "new-hp/js/guidegallery-screenie.js"
DISCOVERY = ROOT / "research/gallery-recovery-20261014/discovery-002/sanitized-summary.json"
KARAZHAN_2008_PLAN = ROOT / "research/gallery-recovery-20261014/karazhan/batch-plan.json"
KARAZHAN_2008_SUMMARY = ROOT / "research/gallery-recovery-20261014/karazhan/sanitized-summary.json"
PREFIX15_SUMMARY = ROOT / "research/continuous-recovery-20261015/network-guide-prefix15/sanitized-summary.json"
PREFIX15_PLAN = ROOT / "research/continuous-recovery-20261015/guide-prefix15-approved-plan.json"
REGIONAL01 = ROOT / "research/continuous-recovery-20261016/publication/root-regional01-acceptance.json"
OUT = HERE


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def digest(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


ADDSHOTS_RE = re.compile(r"addshots\s*\(\s*([\"'])(?P<directory>[^\"']+)\1\s*,\s*([\"'])(?P<filename>[^\"']+)\3\s*,\s*numShots\s*\)")
NUMSHOTS_RE = re.compile(r"\bnumShots\s*=\s*(?P<count>\d+)\s*;")
DIRECT_BASENAME_RE = re.compile(r"^ss\d+(?:-thumb)?\.jpg$", re.I)


def source_literal(page_route: str) -> dict[str, Any]:
    path = V15_SITE / page_route.lstrip("/")
    if not path.exists():
        raise RuntimeError(f"missing source15 gallery page: {page_route}")
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    match = None
    line_no = None
    for i, line in enumerate(lines, 1):
        match = ADDSHOTS_RE.search(line)
        if match:
            line_no = i
            break
    if match is None or line_no is None:
        raise RuntimeError(f"no literal addshots call in {path}")
    numshots = None
    num_line = None
    for i in range(line_no - 1, -1, -1):
        nm = NUMSHOTS_RE.search(lines[i])
        if nm:
            numshots = int(nm.group("count"))
            num_line = i + 1
            break
    if numshots is None:
        raise RuntimeError(f"no preceding numShots assignment in {path}:{line_no}")
    return {
        "path": rel(path),
        "exists": True,
        "sha256": sha256_file(path),
        "addshots_line": line_no,
        "addshots_quote": lines[line_no - 1].strip(),
        "source_directory": match.group("directory"),
        "filename": match.group("filename"),
        "numShots": numshots,
        "numShots_line": num_line,
        "numShots_quote": lines[num_line - 1].strip(),
    }


def origin_schemes(entities: list[dict[str, Any]]) -> tuple[str | None, list[str]]:
    origins = [urlsplit(e["original_url"]) for e in entities if e.get("original_url")]
    hosts = {x.netloc for x in origins}
    if len(hosts) > 1:
        raise RuntimeError(f"multiple direct entity hosts in one gallery: {hosts}")
    return (next(iter(hosts)) if hosts else "www.worldofwarcraft.com", sorted({x.scheme for x in origins}))


def rows_from_discovery(d: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out = {}
    for row in d["scope_counts"]:
        out[row["gallery"]] = row
    return out


def build_search_evidence() -> list[dict[str, Any]]:
    discovery = read_json(DISCOVERY)
    by_name = {row["name"]: row for row in discovery["scope_counts"]}
    out: list[dict[str, Any]] = []
    for name, label, summary_row in [
        ("KARAZHAN-2007", "Karazhan", by_name["karazhan-2007"]),
        ("FISHING-2008", "Fishing", by_name["fishing-2008"]),
    ]:
        cdx = summary_row["cdx"]
        out.append(
            {
                "evidence_id": name,
                "gallery": label,
                "status": "executed_complete_prefix",
                "origin_prefix": "http://www.worldofwarcraft.com" + summary_row["directory"],
                "origin_host": "www.worldofwarcraft.com",
                "origin_schemes_observed": ["http", "https"] if label == "Fishing" else ["http"],
                "query_host": "web.archive.org",
                "date_window": cdx["range"],
                "returned_rows": summary_row["counts"]["rows"],
                "prefix_pages": cdx["numpages"],
                "truncated": not cdx["complete_prefix_evidence"],
                "complete_prefix_evidence": cdx["complete_prefix_evidence"],
                "direct_entity_rows": summary_row["counts"]["direct"],
                "status200_image_rows": summary_row["counts"]["status200_image"],
                "nested_excluded_rows": summary_row["counts"]["nested_excluded"],
                "evidence_paths": [
                    rel(DISCOVERY),
                    cdx["prefix_json"],
                    cdx["pages_json"],
                    cdx["prefix_headers"],
                ],
                "report_quote": (
                    f"complete_prefix_evidence={cdx['complete_prefix_evidence']}; rows={summary_row['counts']['rows']}; "
                    f"direct={summary_row['counts']['direct']}; status200_image={summary_row['counts']['status200_image']}"
                ),
            }
        )

    k8_plan = read_json(KARAZHAN_2008_PLAN)
    k8_cdx = k8_plan["query_evidence"]
    k8_rows = read_json(ROOT / k8_cdx["prefix_json"])
    schemes = sorted({urlsplit(row[2]).scheme for row in k8_rows[1:] if len(row) > 2 and row[2]})
    direct_prefix = "/info/dungeons/images/karazhan/"
    direct = [
        row
        for row in k8_rows[1:]
        if len(row) > 2
        and urlsplit(row[2]).path.startswith(direct_prefix)
        and DIRECT_BASENAME_RE.fullmatch(urlsplit(row[2]).path[len(direct_prefix) :])
    ]
    out.append(
        {
            "evidence_id": "KARAZHAN-2008",
            "gallery": "Karazhan",
            "status": "executed_complete_prefix",
            "origin_prefix": "http://www.worldofwarcraft.com/info/dungeons/images/karazhan/",
            "origin_host": "www.worldofwarcraft.com",
            "origin_schemes_observed": schemes,
            "query_host": "web.archive.org",
            "date_window": k8_cdx["range"],
            "returned_rows": k8_cdx["row_count"],
            "prefix_pages": k8_cdx["numpages"],
            "truncated": not k8_cdx["complete_prefix_evidence"],
            "complete_prefix_evidence": k8_cdx["complete_prefix_evidence"],
            "direct_entity_rows": len(direct),
            "status200_image_rows": sum(1 for row in k8_rows[1:] if len(row) > 4 and row[4] == "200" and str(row[3]).startswith("image/")),
            "nested_excluded_rows": sum(1 for row in k8_rows[1:] if len(row) > 2 and "/thumbs/" in urlsplit(row[2]).path),
            "evidence_paths": [rel(KARAZHAN_2008_PLAN), rel(KARAZHAN_2008_SUMMARY), rel(ROOT / k8_cdx["prefix_json"]), rel(ROOT / k8_cdx["prefix_headers"])],
            "report_quote": "complete_prefix_evidence=true; rows=20; dynamic direct ssN.jpg/ssN-thumb.jpg rows=0; three nested thumbs paths observed",
        }
    )

    p15 = read_json(PREFIX15_SUMMARY)
    for target in p15["targets"]:
        out.append(
            {
                "evidence_id": "NET015-" + target["label"].upper().replace(" ", "_"),
                "gallery": {"Black Temple": "Black Temple", "Serpentshrine Cavern": "Serpentshrine Cavern", "Magister's Terrace": "Magister's Terrace"}[target["label"]],
                "status": "executed_prefix_only_no_valid_direct_entity",
                "origin_prefix": target["prefix"],
                "origin_host": "www.worldofwarcraft.com",
                "origin_schemes_observed": ["http"],
                "query_host": "web.archive.org",
                "date_window": {"from": "20040101000000", "to": "20080512210044"},
                "returned_rows": target["capture_index_count"],
                "prefix_pages": 1,
                "truncated": False,
                "complete_prefix_evidence": True,
                "continuation_followed": target["continuation_followed"],
                "direct_entity_rows": target["eligible_full_count"] + target["eligible_thumb_count"],
                "status200_image_rows": 0,
                "nested_excluded_rows": 0,
                "evidence_paths": [rel(PREFIX15_SUMMARY), rel(PREFIX15_PLAN)],
                "report_quote": f"category={target['category']}; capture_index_count={target['capture_index_count']}; eligible_full_count={target['eligible_full_count']}; eligible_thumb_count={target['eligible_thumb_count']}; continuation_followed={target['continuation_followed']}",
            }
        )
    return out


def main() -> int:
    inventory = read_json(INVENTORY)
    recheck = read_json(RECHECK)
    direct_audit = read_json(DIRECT_AUDIT)
    entities = direct_audit["entities"]
    if len(recheck["rows"]) != 50 or len(inventory["rows"]) != 50:
        raise RuntimeError("gallery scope is not the accepted 50 rows")
    if len(entities) != 3368 or len({e["original_url"] for e in entities}) != 3368:
        raise RuntimeError("direct entity inventory is not 3368 unique rows")

    by_gallery: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for e in entities:
        by_gallery[e["gallery"]].append(e)
    search_evidence = build_search_evidence()
    evidence_by_gallery: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for ev in search_evidence:
        evidence_by_gallery[ev["gallery"]].append(ev)

    rows: list[dict[str, Any]] = []
    for row in recheck["rows"]:
        gallery = row["label"]
        source = source_literal(row["page"])
        xs = by_gallery.get(gallery, [])
        if not xs:
            raise RuntimeError(f"no direct entity rows for {gallery}")
        host, schemes = origin_schemes(xs)
        status_counts = collections.Counter(e["status"] for e in xs)
        expected = row["shots"] * 2
        if source["numShots"] != row["shots"] or len(xs) != expected:
            raise RuntimeError(f"source/entity count mismatch for {gallery}")
        prefix_status = "prefix_not_executed_in_reviewed_evidence"
        if evidence_by_gallery.get(gallery):
            prefix_status = "prefix_reviewed_saved_evidence"
        rows.append(
            {
                "gallery": gallery,
                "category": row["category"],
                "source_page_route": row["page"],
                "source_page": source,
                "declared_slots": row["shots"],
                "expected_direct_entities": expected,
                "entity_audit_status_scope": "v2 direct-entity audit state joined from supplied reports; never_requested is report-local absence of an exact payload replay, not a global request-history claim",
                "entity_audit_status_counts": dict(sorted(status_counts.items())),
                "origin_host_from_entity_urls": host,
                "origin_schemes_from_entity_urls": schemes,
                "prefix_review_status": prefix_status,
                "prefix_evidence": evidence_by_gallery.get(gallery, []),
                "source_evidence": {
                    "path": source["path"],
                    "sha256": source["sha256"],
                    "addshots_line": source["addshots_line"],
                    "addshots_literal": source["addshots_quote"],
                    "source_directory": source["source_directory"],
                    "filename_literal": source["filename"],
                    "numShots_line": source["numShots_line"],
                    "numShots_literal": source["numShots_quote"],
                },
                "report_references": [
                    {"path": rel(DIRECT_AUDIT), "sha256": sha256_file(DIRECT_AUDIT), "role": "3368 direct-entity status join"},
                    {"path": rel(RECHECK), "sha256": sha256_file(RECHECK), "role": "50-gallery route/slot source inventory"},
                ],
            }
        )

    counts = collections.Counter()
    for row in rows:
        counts.update(row["entity_audit_status_counts"])
    regional = read_json(REGIONAL01)
    report = {
        "schema": "wow-recovery.gallery-prefix-registry.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "network_performed": False,
        "scope": {
            "gallery_count": 50,
            "direct_entity_count": 3368,
            "conservation": "50 source addshots pages; sum(declared_slots*2)=3368 exact full+thumb entities",
            "source_page_definition": "source15 rows from gallery-route-entity-recheck, each verified against one literal addshots(directory, filename, numShots) call",
            "known_scope_excluded": [
                "EU REG01 wow-europe.com prefixes: separate origin and report, excluded from the www.worldofwarcraft.com 3368 entity set",
                "nested /thumbs/ guide previews, parent directory rows, and sibling guide resources: not dynamic direct ssN.jpg/ssN-thumb.jpg entities",
                "guide-preview cards and existing overlays: not direct gallery entity search results",
            ],
            "status_boundary": "Rows without a saved prefix report are marked prefix_not_executed_in_reviewed_evidence; no global request-history assertion is made.",
            "pending_batch_B": {"count": 10, "status": "not_executed", "exact_prefix_list_in_reviewed_local_inputs": False, "no_prefix_names_invented": True},
        },
        "input_hashes": [digest(p) for p in [INVENTORY, RECHECK, DIRECT_AUDIT, JS, DISCOVERY, KARAZHAN_2008_PLAN, KARAZHAN_2008_SUMMARY, PREFIX15_SUMMARY, PREFIX15_PLAN, REGIONAL01]],
        "shared_js_evidence": {"path": rel(JS), "sha256": sha256_file(JS), "lines": {"function": 471, "full_rule": 479, "thumb_rule": 486, "replace_rule": 506}},
        "prefix_evidence_records": search_evidence,
        "regional01_exclusion": {
            "path": rel(REGIONAL01),
            "sha256": sha256_file(REGIONAL01),
            "origin_host": "www.wow-europe.com",
            "returned_rows": sum(q["returned_rows"] for q in regional["queries"]),
            "query_count": len(regional["queries"]),
            "reason": "separate EU origin; not mixed into the www.worldofwarcraft.com 50-gallery registry",
        },
        "rows": rows,
        "stats": {
            "gallery_count": len(rows),
            "declared_slots": sum(r["declared_slots"] for r in rows),
            "expected_direct_entities": sum(r["expected_direct_entities"] for r in rows),
            "entity_audit_status_counts": dict(sorted(counts.items())),
            "prefix_reviewed_gallery_count": sum(1 for r in rows if r["prefix_evidence"]),
            "prefix_not_executed_in_reviewed_evidence_count": sum(1 for r in rows if not r["prefix_evidence"]),
            "prefix_record_count": len(search_evidence),
            "net015_gallery_count": sum(1 for e in search_evidence if e["evidence_id"].startswith("NET015-")),
            "karazhan_saved_windows": 2,
            "fishing_saved_windows": 1,
            "regional01_mixed_in_rows": 0,
        },
        "notes": [
            "Karazhan 2007 and 2008 prefix reports are complete one-page windows; direct dynamic entity rows are zero in both. Karazhan 2008 rows are nested thumbs/directory rows, not dynamic full/thumbs.",
            "Fishing 2008 has a complete 63-row prefix result, but the report excludes sibling guide resources and nested thumbs from the gallery's /ss/ direct path; direct dynamic rows are zero.",
            "NET015 has three complete one-page prefix reports with 1/5/3 capture-index rows and zero valid direct image entities; this is prefix-only evidence, not payload recovery.",
            "The v2 label never_requested is preserved only as a report-local entity-audit state and is never reused as a global request-history assertion.",
        ],
    }
    out_json = OUT / "gallery-prefix-registry.json"
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md = [
        "# 50-gallery prefix registry",
        "",
        "The registry binds every row to source15's literal `addshots` call and the supplied 3368-entity audit. Prefix coverage is evidence-scoped; an unreviewed prefix is not called globally never-requested.",
        "",
        f"- Galleries: **{len(rows)}**; declared slots: **{sum(r['declared_slots'] for r in rows)}**; expected full+thumb entities: **{sum(r['expected_direct_entities'] for r in rows)}**.",
        f"- Entity audit state counts (report-local): `{dict(sorted(counts.items()))}`.",
        f"- Saved prefix evidence covers **{sum(1 for r in rows if r['prefix_evidence'])}** galleries: Karazhan (2007/2008), Fishing (2008), and NET015's three dungeon prefixes. The remaining **{sum(1 for r in rows if not r['prefix_evidence'])}** have no saved prefix execution in the reviewed local reports.",
        "- REG01 is retained as a separate EU-origin exclusion (`www.wow-europe.com`); it is not mixed into these 50 rows. B's new ten-prefix batch remains `not_executed`; no names are invented from absent local evidence.",
        "",
        "| # | gallery | slots | source addshots | entity audit state | prefix evidence |",
        "|---:|---|---:|---|---|---|",
    ]
    for i, row in enumerate(rows, 1):
        ev = ", ".join(e["evidence_id"] for e in row["prefix_evidence"]) or "not executed in reviewed evidence"
        states = ", ".join(f"{k}:{v}" for k, v in row["entity_audit_status_counts"].items())
        md.append(f"| {i} | {row['gallery']} | {row['declared_slots']} | `{row['source_evidence']['source_directory']}` (L{row['source_evidence']['addshots_line']}) | {states} | {ev} |")
    md += [
        "",
        "## Prefix evidence fields",
        "",
        "Each saved evidence record in the JSON keeps the target origin host/scheme, query host, date window, returned rows, one-page/truncation state, direct-entity row count, and exact report paths. Karazhan/Fishing use complete one-page prefix receipts; NET015 records its 1/5/3 CDX capture-index rows and zero eligible full/thumb entities.",
        "",
        "The 3368 direct-entity audit's `never_requested` state is retained as a scoped report status only. It is not a conclusion about requests absent from the reviewed reports.",
        "",
    ]
    (OUT / "gallery-prefix-registry.md").write_text("\n".join(md), encoding="utf-8")

    verification = {
        "schema": "wow-recovery.gallery-prefix-registry-verification.v1",
        "registry": rel(out_json),
        "registry_sha256": sha256_file(out_json),
        "network_performed": False,
        "assertions": {
            "gallery_count_50": len(rows) == 50,
            "every_row_has_source_addshots_literal": all(r["source_evidence"]["addshots_literal"] for r in rows),
            "declared_slots_1684": sum(r["declared_slots"] for r in rows) == 1684,
            "expected_entities_3368": sum(r["expected_direct_entities"] for r in rows) == 3368,
            "direct_audit_3368_unique": len(entities) == 3368 and len({e["original_url"] for e in entities}) == 3368,
            "entity_status_conservation": sum(counts.values()) == 3368,
            "prefix_evidence_records_6": len(search_evidence) == 6,
            "regional01_excluded_from_rows": all(all("wow-europe.com" not in x["original_url"] for x in by_gallery[row["gallery"]]) for row in rows),
            "pending_b10_not_executed": report["scope"]["pending_batch_B"]["status"] == "not_executed",
            "no_global_request_history_assertion": "no global request-history assertion is made" in report["scope"]["status_boundary"],
        },
        "counts": {
            "gallery_count": len(rows),
            "expected_entities": sum(r["expected_direct_entities"] for r in rows),
            "prefix_records": len(search_evidence),
            "prefix_reviewed_galleries": sum(1 for r in rows if r["prefix_evidence"]),
            "not_executed_in_reviewed_evidence": sum(1 for r in rows if not r["prefix_evidence"]),
        },
        "disk_free_bytes_after": shutil.disk_usage(ROOT).free,
    }
    (OUT / "verification.json").write_text(json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(verification, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
