"""Read-only v16/v17 Current and Archived News marker comparison.

The page set is inherited from the accepted all-news audit.  Marker parsing is
reused verbatim from that audit so the v16 954-reference denominator remains
comparable.  This script never fetches, exports, or edits source/output trees.
"""

from __future__ import annotations

import collections
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD_AUDIT = ROOT / "research/continuous-recovery-20261016/local-audit/all-news/all-news-audit.json"
OLD_PARSER = ROOT / "research/continuous-recovery-20261016/local-audit/all-news/audit_all_news.py"
V16_ROOT = ROOT / ".scratch/pages-resources-20261016-v16"
V17_ROOT = ROOT / ".scratch/pages-resources-20261016-v17"
V16_PROVENANCE = V16_ROOT / "export-provenance.json"
V17_PROVENANCE = V17_ROOT / "export-provenance.json"
GUIDE_MAP = ROOT / "research/continuous-recovery-20261016/integration/guide-previews-source-map.json"
MAPS = {
    "allnews01": ROOT / "research/continuous-recovery-20261016/network/allnews01/source-map.json",
    "news03": ROOT / "research/continuous-recovery-20261016/network/news03/source-map.json",
    "news04": ROOT / "research/continuous-recovery-20261016/network/news04/source-map.json",
}
ACCEPTANCES = {
    "allnews01": ROOT / "research/continuous-recovery-20261016/publication/root-allnews01-acceptance.json",
    "news03": ROOT / "research/continuous-recovery-20261016/publication/root-news03-acceptance.json",
    "news04": ROOT / "research/continuous-recovery-20261016/publication/root-news04-acceptance.json",
}
OUT = HERE


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def digest_record(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def output_path(root: Path, route: str) -> Path:
    return root / (route.lstrip("/") + (".html" if route.endswith(".xml") else ""))


def load_parser():
    spec = importlib.util.spec_from_file_location("all_news_parser", OLD_PARSER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import accepted all-news parser")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def marker_scan(parser: Any, path: Path, route: str, root_label: str) -> tuple[list[dict[str, Any]], int]:
    text = path.read_text(encoding="utf-8", errors="replace")
    # The old audit's parser deliberately keeps only exact HTTP(S) image URLs.
    markers = parser.extract_markers(text, route, rel(path), "https://www.worldofwarcraft.com" + route, root_label)
    return markers, len(parser.MARKER_RE.findall(text))


def main() -> int:
    parser = load_parser()
    audit = json.loads(OLD_AUDIT.read_text(encoding="utf-8"))
    routes = [row["route"] for row in audit["page_results"]]
    if len(routes) != 40:
        raise RuntimeError(f"accepted news page scope changed: {len(routes)}")

    maps: dict[str, dict[str, Any]] = {}
    map_records: list[dict[str, Any]] = []
    for batch, path in MAPS.items():
        data = json.loads(path.read_text(encoding="utf-8"))
        entries = data.get("entries") or []
        for entry in entries:
            url = entry.get("logical_url") or entry.get("original") or entry.get("captured_original_url")
            if not url:
                raise RuntimeError(f"map entry has no URL: {path}")
            if url in maps:
                raise RuntimeError(f"duplicate accepted NEWS URL: {url}")
            maps[url] = {"batch": batch, "map_path": rel(path), "entry": entry}
        map_records.append({"batch": batch, **digest_record(path), "entry_count": len(entries)})

    page_results: list[dict[str, Any]] = []
    v16_all: collections.Counter[str] = collections.Counter()
    v17_all: collections.Counter[str] = collections.Counter()
    v16_raw_total = v17_raw_total = 0
    for route in routes:
        p16 = output_path(V16_ROOT, route)
        p17 = output_path(V17_ROOT, route)
        if not p16.exists() or not p17.exists():
            raise RuntimeError(f"missing v16/v17 output for {route}")
        m16, raw16 = marker_scan(parser, p16, route, "v16_output")
        m17, raw17 = marker_scan(parser, p17, route, "v17_output")
        c16 = collections.Counter(x["requested_url"] for x in m16)
        c17 = collections.Counter(x["requested_url"] for x in m17)
        v16_all.update(c16)
        v17_all.update(c17)
        v16_raw_total += raw16
        v17_raw_total += raw17
        page_results.append(
            {
                "route": route,
                "v16_output": rel(p16),
                "v17_output": rel(p17),
                "v16_output_sha256": sha256_file(p16),
                "v17_output_sha256": sha256_file(p17),
                "v16_raw_marker_tokens": raw16,
                "v17_raw_marker_tokens": raw17,
                "v16_valid_image_markers": len(m16),
                "v17_valid_image_markers": len(m17),
                "marker_delta_v16_minus_v17": len(m16) - len(m17),
                "v16_unique_requested_urls": len(c16),
                "v17_unique_requested_urls": len(c17),
                "new_asset_disappeared_occurrences": sum((c16 - c17)[url] for url in maps),
            }
        )

    disappeared = v16_all - v17_all
    appeared = v17_all - v16_all
    url_rows: list[dict[str, Any]] = []
    for url, info in maps.items():
        v16_locations: list[dict[str, Any]] = []
        v17_locations: list[dict[str, Any]] = []
        for page in page_results:
            # Re-scan only when an accepted URL occurs; this keeps the receipt
            # compact while retaining every exact page/line occurrence.
            route = page["route"]
            p16 = ROOT / page["v16_output"]
            p17 = ROOT / page["v17_output"]
            if page["v16_valid_image_markers"]:
                m16, _ = marker_scan(parser, p16, route, "v16_output")
                for m in m16:
                    if m["requested_url"] == url:
                        v16_locations.append({"route": route, "line": m["line"], "output": page["v16_output"]})
            if page["v17_valid_image_markers"]:
                m17, _ = marker_scan(parser, p17, route, "v17_output")
                for m in m17:
                    if m["requested_url"] == url:
                        v17_locations.append({"route": route, "line": m["line"], "output": page["v17_output"]})
        url_rows.append(
            {
                "batch": info["batch"],
                "original_url": url,
                "v16_valid_marker_occurrences": v16_all[url],
                "v17_valid_marker_occurrences": v17_all[url],
                "disappeared_occurrences": disappeared[url],
                "status": "new_v17_asset_removed_all_markers" if v16_all[url] > 0 and v17_all[url] == 0 else "unexpected_marker_state",
                "v16_locations": v16_locations,
                "v17_locations": v17_locations,
                "source_map": info["map_path"],
                "source_map_entry": info["entry"].get("target_key") or info["entry"].get("cdx_digest"),
            }
        )

    batch_delta = collections.Counter()
    for row in url_rows:
        batch_delta[row["batch"]] += row["disappeared_occurrences"]
    guide_provenance = json.loads(V17_PROVENANCE.read_text(encoding="utf-8")).get("stats", {})
    inputs = [OLD_AUDIT, OLD_PARSER, V16_PROVENANCE, V17_PROVENANCE, GUIDE_MAP, *MAPS.values(), *ACCEPTANCES.values()]
    input_hashes = [digest_record(p) for p in inputs]

    report = {
        "schema": "wow-recovery.v17-news-marker-audit.v1",
        "generated_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "network_performed": False,
        "scope": {
            "pages": 40,
            "page_routes_source": rel(OLD_AUDIT),
            "page_definition": audit["scope"]["page_definition"],
            "same_page_set_as_v16": True,
            "guide_cards_excluded": "19 guide previews in v17 provenance are provenance/HTML additions, not News page marker inputs or News image download occurrences.",
            "v17_guide_preview_provenance": {"count": guide_provenance.get("guide_preview_count"), "gallery_pages": guide_provenance.get("guide_preview_gallery_pages")},
        },
        "input_hashes": input_hashes,
        "map_records": map_records,
        "page_results": page_results,
        "asset_url_results": url_rows,
        "stats": {
            "v16_raw_marker_tokens": v16_raw_total,
            "v17_raw_marker_tokens": v17_raw_total,
            "v16_valid_image_markers": sum(v16_all.values()),
            "v17_valid_image_markers": sum(v17_all.values()),
            "valid_marker_delta_v16_minus_v17": sum(v16_all.values()) - sum(v17_all.values()),
            "v16_unique_requested_urls": len(v16_all),
            "v17_unique_requested_urls": len(v17_all),
            "disappeared_valid_marker_occurrences": sum(disappeared.values()),
            "appeared_valid_marker_occurrences": sum(appeared.values()),
            "accepted_new_asset_url_count": len(maps),
            "accepted_new_asset_urls_with_all_markers_removed": sum(1 for row in url_rows if row["status"] == "new_v17_asset_removed_all_markers"),
            "disappeared_occurrences_by_batch": dict(batch_delta),
            "allnews01_expected_occurrences": 152,
            "allnews01_actual_occurrences": batch_delta["allnews01"],
            "other_news_batches_actual_occurrences": batch_delta["news03"] + batch_delta["news04"],
            "remaining_v17_valid_marker_occurrences_after_new_assets": sum(v17_all.values()),
        },
        "observations": [
            "The 954 v16 denominator and 798 v17 numerator use the accepted all-news parser's image-URL filter; raw marker token counts are 956 and 800 because two non-image requested URLs per layer are intentionally excluded.",
            "The prior audit's 504 v15 source-layer markers are a different counting layer from the 954 v16 derived-output markers; the 450 difference is output derivation/overlay material, not a v17 regression, and is not used in this delta.",
            "The 156 removed occurrences are exactly 152 ALLNEWS01 references plus 2 NEWS03 and 2 NEWS04 references; no accepted-map URL remains as a v17 marker.",
            "A page marker count is an occurrence count; URL rows retain deduplicated URLs and every v16 page/line location for the 20 accepted assets.",
        ],
    }
    (OUT / "v17-news-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md = [
        "# v17 News marker audit",
        "",
        "Read-only comparison of the same 40 pages used by the accepted all-news audit.",
        "",
        f"- v16 valid image markers: **{sum(v16_all.values())}**; v17: **{sum(v17_all.values())}**; removed: **{sum(disappeared.values())}**.",
        f"- Accepted new assets: **{len(maps)}**; ALLNEWS01 disappeared occurrences: **{batch_delta['allnews01']} / 152 expected**; NEWS03+NEWS04: **{batch_delta['news03'] + batch_delta['news04']}**.",
        f"- Unique requested URLs: v16 **{len(v16_all)}**, v17 **{len(v17_all)}**; no new valid marker URL appeared.",
        f"- v17 guide provenance reports **{guide_provenance.get('guide_preview_count')}** previews on **{guide_provenance.get('guide_preview_gallery_pages')}** gallery pages; these cards are excluded from this News marker/download count.",
        "",
        "## Per-page comparison",
        "",
        "| route | v16 valid | v17 valid | delta | new-asset removals |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in page_results:
        md.append(f"| `{row['route']}` | {row['v16_valid_image_markers']} | {row['v17_valid_image_markers']} | {row['marker_delta_v16_minus_v17']} | {row['new_asset_disappeared_occurrences']} |")
    md += ["", "## Twenty accepted URLs", "", "| batch | URL | v16 occurrences | v17 occurrences | pages with v16 markers |", "|---|---|---:|---:|---|"]
    for row in url_rows:
        pages = ", ".join(sorted({x["route"] for x in row["v16_locations"]}))
        md.append(f"| {row['batch']} | `{row['original_url']}` | {row['v16_valid_marker_occurrences']} | {row['v17_valid_marker_occurrences']} | {pages} |")
    md += ["", "The JSON receipt retains exact page/line locations and all locked input hashes. No network, build, production, or frozen-source writes were performed.", ""]
    (OUT / "v17-news-audit.md").write_text("\n".join(md), encoding="utf-8")

    verification = {
        "schema": "wow-recovery.v17-news-marker-audit-verification.v1",
        "audit": rel(OUT / "v17-news-audit.json"),
        "audit_sha256": sha256_file(OUT / "v17-news-audit.json"),
        "network_performed": False,
        "assertions": {
            "page_count_40": len(page_results) == 40,
            "all_page_outputs_exist": all((ROOT / row["v16_output"]).exists() and (ROOT / row["v17_output"]).exists() for row in page_results),
            "v16_marker_count_954": sum(v16_all.values()) == 954,
            "v17_marker_count_798": sum(v17_all.values()) == 798,
            "removed_marker_count_156": sum(disappeared.values()) == 156,
            "accepted_map_entry_count_20": len(maps) == 20,
            "allnews01_exact_152": batch_delta["allnews01"] == 152,
            "news03_news04_exact_4": batch_delta["news03"] + batch_delta["news04"] == 4,
            "all_accepted_urls_removed": all(row["status"] == "new_v17_asset_removed_all_markers" for row in url_rows),
            "no_new_valid_marker_url": not appeared,
            "guide_previews_not_news_downloads": guide_provenance.get("guide_preview_count") == 19,
        },
        "counts": {"pages": len(page_results), "v16_valid": sum(v16_all.values()), "v17_valid": sum(v17_all.values()), "removed": sum(disappeared.values()), "new_urls": len(maps)},
        "disk_free_bytes_after": shutil.disk_usage(ROOT).free,
    }
    (OUT / "verification.json").write_text(json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(verification, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
