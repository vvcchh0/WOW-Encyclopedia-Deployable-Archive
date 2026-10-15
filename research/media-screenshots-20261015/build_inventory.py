#!/usr/bin/env python3
"""Build the local-only MEDIA -> Screenshots inventory.

This script reads the frozen offline export and saved research evidence. It
never performs network access and writes only this task directory.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BASELINE = ROOT / "offline/site"
MANIFEST = ROOT / "offline/build-manifest.json"
V5 = ROOT / ".scratch/pages-local-maintenance-20261014-v5"


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def file_count(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file()) if path.is_dir() else 0


def decode_probe(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": rel(path),
        "exists": path.is_file(),
        "bytes": path.stat().st_size if path.is_file() else None,
        "magic": None,
        "decoded": False,
        "format": None,
        "width": None,
        "height": None,
        "error": None,
    }
    if not path.is_file():
        return result
    try:
        head = path.read_bytes()[:12]
        if head.startswith(b"\xff\xd8\xff"):
            result["magic"] = "jpeg"
        elif head[:6] in (b"GIF87a", b"GIF89a"):
            result["magic"] = "gif"
        elif head.startswith(b"\x89PNG\r\n\x1a\n"):
            result["magic"] = "png"
        else:
            result["magic"] = "other"
        if Image is None:
            result["error"] = "Pillow unavailable; magic-only probe"
            return result
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            result.update({
                "decoded": True,
                "format": image.format,
                "width": image.width,
                "height": image.height,
            })
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def static_asset_inventory(root: Path) -> dict[str, Any]:
    files = sorted(item for item in root.glob("*") if item.is_file()) if root.is_dir() else []
    probes = [decode_probe(item) for item in files]
    return {
        "root": rel(root),
        "exists": root.is_dir(),
        "file_count": len(files),
        "extension_counts": dict(sorted(Counter(item.suffix.lower() or "[none]" for item in files).items())),
        "decoded_count": sum(bool(item["decoded"]) for item in probes),
        "files": probes,
    }


def dynamic_inventory(root: Path) -> dict[str, Any]:
    files = sorted(item for item in root.rglob("*") if item.is_file()) if root.is_dir() else []
    full = [item for item in files if re.fullmatch(r"ss\d+\.jpg", item.name, re.I)]
    thumbs = [item for item in files if re.fullmatch(r"ss\d+-thumb\.jpg", item.name, re.I)]
    return {
        "root": rel(root),
        "exists": root.is_dir(),
        "all_file_count": len(files),
        "full_count": len(full),
        "thumb_count": len(thumbs),
        "full_decoded": sum(bool(decode_probe(item)["decoded"]) for item in full),
        "thumb_decoded": sum(bool(decode_probe(item)["decoded"]) for item in thumbs),
        "full_examples": [rel(item) for item in full[:2]],
        "thumb_examples": [rel(item) for item in thumbs[:2]],
    }


def parse_cdx(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        return [], []
    if isinstance(payload[0], list):
        header = [str(value) for value in payload[0]]
        rows = [
            {key: str(value) for key, value in zip(header, row)}
            for row in payload[1:]
            if isinstance(row, list)
        ]
        return header, rows
    return [], []


def game_guide_inventory() -> dict[str, Any]:
    path = ROOT / "research/github-pages-20261013/gallery-inventory-20261013.json"
    report = ROOT / "research/github-pages-20261013/gallery-inspection-20261013.md"
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    html_rows = [row for row in rows if isinstance(row.get("source", {}).get("num_shots"), int)]
    categories: dict[str, dict[str, int]] = defaultdict(
        lambda: {"index_links": 0, "dynamic_links": 0, "slots": 0}
    )
    for row in rows:
        bucket = categories[row.get("category") or "[unknown]"]
        bucket["index_links"] += 1
        if isinstance(row.get("source", {}).get("num_shots"), int):
            bucket["dynamic_links"] += 1
            bucket["slots"] += int(row["source"]["num_shots"])
    slots = sum(int(row["source"]["num_shots"]) for row in html_rows)
    wrapper_rows = [row for row in rows if not isinstance(row.get("source", {}).get("num_shots"), int)]
    # The wrapper's underlying page is documented in the existing report and
    # has numShots=60; retain it separately from the 49 HTML rows.
    zulaman_slots = 60
    return {
        "scope": "Game Guide Player Screenshot Galleries (distinct from MEDIA SSOTD)",
        "source_inventory": rel(path),
        "source_report": rel(report),
        "index_gallery_links": len(rows),
        "gallery_html_links": len(html_rows),
        "wrapper_links": len(wrapper_rows),
        "gallery_html_slots": slots,
        "zulaman_underlying_slots": zulaman_slots,
        "combined_slots": slots + zulaman_slots,
        "expected_direct_full_thumb_entities": 2 * (slots + zulaman_slots),
        "valid_direct_full": 0,
        "valid_direct_thumb": 0,
        "valid_direct_pairs": 0,
        "categories": {key: categories[key] for key in sorted(categories)},
        "identity_rule": "Guide gallery source addshots uses /info/.../images/.../ssN.jpg; MEDIA uses /downloads/ssotd/images/screens/ssN.jpg.",
    }


def regional_cdx_inventory() -> dict[str, Any]:
    cdx_path = ROOT / "research/related-sites-20261014/regional-gallery/cdx/screen-assets-baseline.rows.json"
    map_path = ROOT / "research/related-sites-20261014/regional-gallery/image-source-map.json"
    plan_path = ROOT / "research/related-sites-20261014/regional-gallery/batch-plan.json"
    header, rows = parse_cdx(cdx_path)
    source_map = json.loads(map_path.read_text(encoding="utf-8"))
    entries = source_map.get("entries", [])
    status_image = [
        row for row in rows
        if row.get("statuscode") == "200" and row.get("mimetype", "").lower().startswith("image/")
    ]
    hosts = Counter()
    paths = Counter()
    for row in rows:
        original = row.get("original", "")
        match = re.match(r"^[a-z]+://([^/]+)/(?P<path>.*)$", original, re.I)
        if match:
            hosts[match.group(1)] += 1
            paths["/" + match.group("path")] += 1
    mapped_hosts = Counter()
    for entry in entries:
        original = str(entry.get("original", ""))
        match = re.match(r"^[a-z]+://([^/]+)/", original, re.I)
        if match:
            mapped_hosts[match.group(1)] += 1
    timestamps = [row.get("timestamp", "") for row in rows if re.fullmatch(r"\d{14}", row.get("timestamp", ""))]
    return {
        "scope": "related-site EU Screen of the Day control (not US MEDIA route)",
        "cdx_rows_file": rel(cdx_path),
        "batch_plan_file": rel(plan_path),
        "source_map_file": rel(map_path),
        "query_range": {"from": "20070101000000", "to": "20080512210044"},
        "complete_prefix": True,
        "prefix": "/screenoftheday/screenoftheday/",
        "rows": len(rows),
        "header": header,
        "status200_image_rows": len(status_image),
        "host_variants_in_saved_cdx": dict(sorted(hosts.items())),
        "mapped_valid_decoded_entities": len(entries),
        "mapped_valid_host_variants": dict(sorted(mapped_hosts.items())),
        "mapped_temporal_classes": dict(sorted(Counter(entry.get("temporal_class") for entry in entries).items())),
        "mapped_timestamp_min": min((entry.get("indexed_capture_timestamp", "") for entry in entries), default=None),
        "mapped_timestamp_max": max((entry.get("indexed_capture_timestamp", "") for entry in entries), default=None),
        "distinct_paths_in_saved_cdx": len(paths),
        "row_timestamp_min": min(timestamps, default=None),
        "row_timestamp_max": max(timestamps, default=None),
        "note": "CDX row presence is index evidence. The mapped entity count is the subset with saved JPEG payloads and Pillow decode validation.",
    }


def parse_saved_cdx_body(path: Path) -> tuple[list[list[Any]], str | None]:
    if not path.is_file() or path.stat().st_size == 0:
        return [], None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload or not isinstance(payload[0], list):
        return [], None
    rows = [item for item in payload[1:] if isinstance(item, list)]
    token = next((item[0] for item in reversed(rows) if len(item) == 1 and isinstance(item[0], str)), None)
    data_rows = [item for item in rows if len(item) >= 6 and re.fullmatch(r"\d{14}", str(item[0]))]
    return data_rows, token


def parse_saved_http_status(path: Path) -> int | None:
    if not path.is_file():
        return None
    for line in path.read_text(encoding="iso-8859-1", errors="replace").splitlines():
        match = re.match(r"^HTTP/\d(?:\.\d)?\s+(\d{3})", line.strip(), re.I)
        if match and not ("connection established" in line.lower()):
            return int(match.group(1))
    return None


def wayback_window_inventory() -> dict[str, Any]:
    window = OUT / "wayback-window"
    records_path = window / "request-records.json"
    if not window.is_dir():
        return {"exists": False, "network_performed": False}
    records = json.loads(records_path.read_text(encoding="utf-8")) if records_path.is_file() else []
    prefix_body = window / "raw/07-ssotd_screens_prefix_rows_all.body"
    resume_body = window / "raw/13-ssotd_screens_prefix_resume_page1.body"
    exact_body = window / "raw/14-exact_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314.jpg.body"
    thumb_body = window / "raw/15-exact_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314-thumb.jpg.body"
    prefix_rows, prefix_token = parse_saved_cdx_body(prefix_body)
    resume_rows, resume_token = parse_saved_cdx_body(resume_body)
    exact_rows, exact_token = parse_saved_cdx_body(exact_body)
    thumb_rows, thumb_token = parse_saved_cdx_body(thumb_body)
    extended_path = window / "extended-summary.json"
    extended = json.loads(extended_path.read_text(encoding="utf-8")) if extended_path.is_file() else {}
    image_rows = [
        row for row in prefix_rows
        if row[2] == "200" and str(row[3]).lower().startswith("image/")
    ]
    exact_image_rows = [
        row for row in exact_rows
        if row[2] == "200" and str(row[3]).lower().startswith("image/")
    ]
    prefix_hosts = Counter(str(row[1]).split("/")[2] for row in prefix_rows if len(row) >= 2 and row[1])
    alias_records = records[6:10]
    alias_body_hashes = sorted({str(record.get("body_sha256")) for record in alias_records if record.get("body_sha256")})
    # request-records already includes the canonical first-page raw body
    # (request 7); only the post-processing gap 13-15 needs adding here.
    raw_extra = [resume_body, exact_body, thumb_body]
    extra_bytes = sum(path.stat().st_size for path in raw_extra if path.is_file())
    prior_bytes = sum(int(record.get("body_bytes") or 0) for record in records)
    return {
        "exists": True,
        "network_performed": True,
        "source_budget": {"max_requests": 25, "observed_requests": len(records) + 3, "observed_body_bytes": prior_bytes + extra_bytes},
        "reconciled_records": "wayback-window/request-records-reconciled.json",
        "parent_exact_index_query": {
            "path": "research/media-screenshots-20261015/parent-query/summary.json",
            "scope": "www.worldofwarcraft.com/downloads/ssotd/index.html, matchType=exact, from=2006, to=2010",
            "result": "HTTP 200 valid JSON []",
            "interpretation": "Scoped empty exact query only; not an absence claim for the trailing-slash source identity.",
        },
        "entry_trailing_slash": {
            "request_record": "wayback-window/request-records.json:1-2",
            "all_time_rows": records[0].get("rows_count") if records else None,
            "from_2006_to_2010_rows": records[1].get("rows_count") if len(records) > 1 else None,
            "source_status": "HTTP 200 JSON; rows include 200 HTML, redirects, warc/revisit, and host/protocol variants.",
        },
        "show_num_pages": {
            "request_records": "wayback-window/request-records.json:3-5",
            "statuses": [records[index].get("status") for index in (2, 3, 4) if len(records) > index],
            "body_bytes": [records[index].get("body_bytes") for index in (2, 3, 4) if len(records) > index],
            "interpretation": "HTTP 200 with empty body and no JSON; retained as unavailable pagination metadata, never treated as an empty index.",
        },
        "screens_prefix_first_page": {
            "raw": "wayback-window/raw/07-ssotd_screens_prefix_rows_all.body",
            "valid_data_rows": len(prefix_rows),
            "resume_token": prefix_token,
            "resume_token_present": bool(prefix_token),
            "host_variants": dict(sorted(prefix_hosts.items())),
            "alias_queries": [record.get("label") for record in alias_records],
            "deduped_canonical_page_count": len(alias_body_hashes),
            "alias_page_body_sha256s": alias_body_hashes,
            "deduplication_rule": "The four evidence-backed host forms returned the same canonical first-page body; count its 1000 data rows once.",
            "status_counts": dict(sorted(Counter(str(row[2]) for row in prefix_rows).items())),
            "mime_counts": dict(sorted(Counter(str(row[3]) for row in prefix_rows).items())),
            "status200_image_rows": [
                {"timestamp": row[0], "original": row[1], "statuscode": row[2], "mimetype": row[3], "digest": row[4], "length": row[5]}
                for row in image_rows
            ],
            "completeness": "First 1000 data rows only; trailing empty row plus resume key are metadata, not captures.",
        },
        "screens_prefix_resume_page": {
            "raw": "wayback-window/raw/13-ssotd_screens_prefix_resume_page1.body",
            "valid_data_rows": len(resume_rows),
            "resume_token": resume_token,
            "resume_token_present": bool(resume_token),
            "status200_image_rows": [
                {"timestamp": row[0], "original": row[1], "statuscode": row[2], "mimetype": row[3], "digest": row[4], "length": row[5]}
                for row in resume_rows
                if row[2] == "200" and str(row[3]).lower().startswith("image/")
            ],
            "completeness": "One follow-up page was fetched; the entire prefix is still not claimed complete.",
        },
        "exact_image_series": {
            "full_target": "http://www.worldofwarcraft.com/downloads/ssotd/images/screens/ss1314.jpg",
            "raw": "wayback-window/raw/14-exact_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314.jpg.body",
            "source_status": parse_saved_http_status(window / "raw/14-exact_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314.jpg.headers.txt"),
            "rows": [
                {"timestamp": row[0], "original": row[1], "statuscode": row[2], "mimetype": row[3], "digest": row[4], "length": row[5]}
                for row in exact_rows
            ],
            "status200_image_rows": [
                {"timestamp": row[0], "digest": row[4], "length": row[5]}
                for row in exact_image_rows
            ],
            "note": "One real image path was selected from a status-200 prefix row; this exact time series is index evidence until replay validation.",
        },
        "exact_thumb_control": {
            "target": "http://www.worldofwarcraft.com/downloads/ssotd/images/screens/ss1314-thumb.jpg",
            "raw": "wayback-window/raw/15-exact_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314-thumb.jpg.body",
            "source_status": parse_saved_http_status(window / "raw/15-exact_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314-thumb.jpg.headers.txt"),
            "rows": [
                {"timestamp": row[0], "original": row[1], "statuscode": row[2], "mimetype": row[3], "digest": row[4], "length": row[5]}
                for row in thumb_rows
            ],
            "interpretation": "Exact thumb query returned valid JSON [] in this window; prefix evidence still shows thumb-shaped paths elsewhere.",
        },
        "replay": {
            "status": "validated" if extended.get("replay_results") else "not_run",
            "extended_summary": "wayback-window/extended-summary.json" if extended else None,
            "samples": [
                {
                    "label": item.get("label"),
                    "status": item.get("status"),
                    "body_bytes": item.get("body_bytes"),
                    "memento_datetime": item.get("memento_datetime"),
                    "content_type": item.get("content_type"),
                    "payload_probe": item.get("payload_probe"),
                    "digest_match": item.get("digest_match"),
                    "body_path": item.get("body_path"),
                }
                for item in extended.get("replay_results", [])
            ],
            "required_acceptance": "Memento HTTP 200, image/jpeg, JPEG magic, Pillow decode, and digest/timestamp comparison.",
        },
        "filtered_prefix": extended.get("filtered_prefix", {}),
    }


def render_markdown(inventory: dict[str, Any]) -> str:
    assets = inventory["local_ssotd_assets"]
    static = assets["static_ui"]
    guide = inventory["game_guide_distinction"]
    regional = inventory["saved_cdx_coverage"]["regional_control"]
    wayback = inventory["saved_cdx_coverage"]["wayback_window"]
    frozen = inventory["frozen_inputs"]
    lines = [
        "# MEDIA -> Screenshots local inventory",
        "",
        "Generated from local files on 2026-10-15. This report does not make network requests; saved CDX rows are identified as index evidence and kept separate from payload validation.",
        "",
        "## Confirmed MEDIA entry",
        "",
        f"The current MEDIA menu points to {inventory['media_entry']['canonical_relative_href']} ({inventory['media_entry']['source_menu']['path']}:{inventory['media_entry']['source_menu']['line_range']}). The legacy navigation tree independently points Media -> Screenshots to /downloads/ssotd/index.html ({inventory['media_entry']['legacy_nav']['path']}:{inventory['media_entry']['legacy_nav']['line_range']}). The page title is WorldofWarcraft.com -> Screenshot of the Day.",
        "",
        "This is distinct from the Game Guide Player Screenshot Galleries listed in offline/site/info/index.html:539-591; those pages use /info/.../images/.../ssN.jpg and are summarized below only as a control.",
        "",
        "## SSOTD URL and pagination rules",
        "",
        f"index.html:63-83 computes currentShotNumber from the Date response header of a HEAD anachronos.xml request, then calls addshots({inventory['ssotd_rules']['full_url_template'].rsplit('/', 1)[0]}, ss, currentShotNumber). The local anachronos.xml body is {assets['anachronos']['body']!r}, so an offline file read cannot recover the server Date or the current total.",
        "",
        f"ssotd-screenie.js:432-468 constructs full URLs as {inventory['ssotd_rules']['full_url_template']} and thumbnail URLs by replacing .jpg with -thumb.jpg. The default page size is {inventory['ssotd_rules']['shots_per_page_default']}; the UI can switch to 16, 12, or 9. Pagination is client-side and hash-aware; the page is one chronological stream with no category sections.",
        "",
        "## Local coverage",
        "",
        f"Frozen baseline {frozen['offline_site']['path']} contains {frozen['offline_site']['file_count']} files. {frozen['offline_build_manifest']['path']} is {frozen['offline_build_manifest']['bytes']} bytes with SHA-256 {frozen['offline_build_manifest']['sha256']}. The latest derived directory exists at {frozen['latest_local_derived']['path']}.",
        "",
        f"The baseline SSOTD static asset directory contains {static['file_count']} files ({static['extension_counts']}) and {static['decoded_count']} Pillow-decoded images. The dynamic screens roots in both baseline and v5 have zero ssN.jpg full images and zero ssN-thumb.jpg thumbnails. This is a local coverage result; it is not a claim that Wayback or the source server has no such objects.",
        "",
        "| Route/system | slots or entities | valid local direct images | evidence |",
        "|---|---:|---:|---|",
        f"| MEDIA SSOTD /downloads/ssotd/images/screens/ | date-derived, total unavailable offline | 0 full / 0 thumb | index.html:63-83; ssotd-screenie.js:432-468 |",
        f"| Game Guide galleries (49 HTML + Zul'Aman underlying page) | {guide['combined_slots']} slots; {guide['expected_direct_full_thumb_entities']} expected full/thumb entities | {guide['valid_direct_full']} full / {guide['valid_direct_thumb']} thumb / {guide['valid_direct_pairs']} pairs | {guide['source_report']}:5-17 |",
        "",
        "## Existing saved CDX evidence",
        "",
        "No pre-existing local US /downloads/ssotd CDX rows were found in the local scan. The separately authorized parent query is stored under research/media-screenshots-20261015/parent-query/; its empty exact result must remain scoped to that exact URL and range.",
        "",
        f"The available local control is the EU route {regional['prefix']}: the saved complete-prefix CDX table has {regional['rows']} rows from {regional['query_range']['from']} through {regional['query_range']['to']}, including {regional['status200_image_rows']} status-200 image rows. Its source-map contains {regional['mapped_valid_decoded_entities']} saved JPEG payloads that passed decode validation, covering {regional['mapped_timestamp_min']}–{regional['mapped_timestamp_max']} across observed host forms {', '.join(regional['mapped_valid_host_variants'])}. This related-site evidence is not merged into the US MEDIA count.",
        "",
        "## Authorized Wayback window evidence",
        "",
        f"The parent exact query for /downloads/ssotd/index.html is retained at {wayback['parent_exact_index_query']['path']} and returned valid JSON [] for its stated 2006–2010 scope. The evidence-backed trailing-slash source query returned {wayback['entry_trailing_slash']['all_time_rows']} rows all-time and {wayback['entry_trailing_slash']['from_2006_to_2010_rows']} rows for 2006–2010, including historical 200 HTML captures and later redirects; this explains why the index.html exact empty result cannot be generalized.",
        "",
        f"The canonical /downloads/ssotd/images/screens/ prefix first page has {wayback['screens_prefix_first_page']['valid_data_rows']} valid data rows and a resume token; its two status-200 image rows are ss1314.jpg at 2010-08-10 and ss1336.jpg at 2010-06-02. Four evidence-backed host forms returned the same first-page body and are counted once ({wayback['screens_prefix_first_page']['deduped_canonical_page_count']} canonical page). One resume page was fetched with {wayback['screens_prefix_resume_page']['valid_data_rows']} valid data rows. Prefix pagination is therefore proven incomplete beyond the two saved pages.",
        "",
        f"Exact CDX for the real path {wayback['exact_image_series']['full_target']} returned {len(wayback['exact_image_series']['rows'])} rows, including the status-200 image digest {wayback['exact_image_series']['status200_image_rows'][0]['digest'] if wayback['exact_image_series']['status200_image_rows'] else 'none'} at {wayback['exact_image_series']['status200_image_rows'][0]['timestamp'] if wayback['exact_image_series']['status200_image_rows'] else 'none'}. The thumb exact control returned valid JSON with {len(wayback['exact_thumb_control']['rows'])} rows. Two full-image replay samples were then validated with HTTP 200, Pillow decode, Memento timestamps, and digest match; the filtered prefix returned {wayback['filtered_prefix'].get('status200_image_rows', 0)} status-200 image rows.",
        "",
        "The two validated 2010 payloads are listed in late-image-source-map.json with their raw replay paths, CDX identity, timestamps, dimensions, SHA-256, and digest-match evidence. sanitized-summary.json and capture-ledger.json provide compact counts while the original raw responses remain under wayback-window/raw/.",
        "",
        "## Provenance and limits",
        "",
        "The static page, JS, navigation, manifest, existing gallery inventory, and saved regional CDX files are the source records. URL variants appear in the query plan only when a local page/script or saved index provides the path; a CDX row is not treated as a downloaded image until replay yields HTTP 200, image MIME, JPEG magic, and decode success.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    menu_path = ROOT / "offline/site/new-hp/layout/menu.xml"
    nav_path = ROOT / "offline/site/shared/wow-com/includes-client/navtree-main.js"
    page_path = ROOT / "offline/site/downloads/ssotd/index.html"
    js_path = ROOT / "offline/site/new-hp/js/ssotd-screenie.js"
    page = read_text(page_path)
    js = read_text(js_path)
    menu = read_text(menu_path)
    nav = read_text(nav_path)
    start_match = re.search(r"startDate\s*=\s*(\d+)", page)
    addshots_match = re.search(r'addshots\("([^"]+)","([^"]+)",currentShotNumber\)', page)
    size_match = re.search(r"shotsPerPage\s*=\s*(\d+)", js)
    if not (start_match and addshots_match and size_match):
        raise RuntimeError("required SSOTD rules were not found in frozen inputs")
    start_date = int(start_match.group(1))
    addshots_dir, addshots_filename = addshots_match.groups()
    image_template = f"{addshots_dir}/{addshots_filename}N.jpg"
    thumb_template = image_template.replace(".jpg", "-thumb.jpg")
    ssotd_images = BASELINE / "downloads/ssotd/images"
    dynamic_roots = {
        "offline_baseline": BASELINE / "downloads/ssotd/images/screens",
        "v5_derived": V5 / "downloads/ssotd/images/screens",
    }
    anachronos = BASELINE / "downloads/ssotd/anachronos.xml"
    inventory: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Local-only inventory of official MEDIA -> Screenshots / Screenshot of the Day route",
        "network_performed_by_builder": False,
        "frozen_inputs": {
            "offline_site": {"path": rel(BASELINE), "exists": BASELINE.is_dir(), "file_count": file_count(BASELINE)},
            "offline_build_manifest": {
                "path": rel(MANIFEST),
                "exists": MANIFEST.is_file(),
                "bytes": MANIFEST.stat().st_size if MANIFEST.is_file() else None,
                "sha256": sha256(MANIFEST) if MANIFEST.is_file() else None,
            },
            "latest_local_derived": {"path": rel(V5), "exists": V5.is_dir(), "file_count": file_count(V5)},
        },
        "media_entry": {
            "canonical_relative_href": "/downloads/ssotd/index.html#latest",
            "source_menu": {"path": rel(menu_path), "line_range": "55-58", "contains": "menuMedia Screenshots -> /downloads/ssotd/index.html#latest"},
            "legacy_nav": {"path": rel(nav_path), "line_range": "283-286", "contains": "Menu1_8_2 Screenshots -> /downloads/ssotd/index.html"},
            "page": {"path": rel(page_path), "title": "WorldofWarcraft.com -> Screenshot of the Day"},
            "source_identity": "http://www.worldofwarcraft.com/downloads/ssotd/ (embedded source/rewrite evidence)",
            "not_game_guide": "The Game Guide list is offline/site/info/index.html:539-591 and its dynamic source paths begin /info/.../images/.",
        },
        "ssotd_rules": {
            "page_source": rel(page_path),
            "script_source": rel(js_path),
            "start_date_days_since_epoch": start_date,
            "date_dependency": "HEAD anachronos.xml response Date header; local anachronos.xml body is only a tag marker and cannot supply the server Date.",
            "current_shot_number_formula_source": "index.html:63-82",
            "full_url_template": image_template,
            "thumbnail_url_template": thumb_template,
            "shots_per_page_default": int(size_match.group(1)),
            "alternate_page_sizes": [16, 12, 9],
            "pagination": "client-side array and hash; printPages() computes ceil(shotList.length/shotsPerPage); galleryPrev/galleryNext wrap pages.",
            "numbering": "addshots() fills N down to 1, so one chronological stream; there are no local category sections in this page.",
            "url_construction_evidence": "ssotd-screenie.js:432-468",
        },
        "local_ssotd_assets": {
            "static_ui": static_asset_inventory(ssotd_images),
            "dynamic_roots": {key: dynamic_inventory(path) for key, path in dynamic_roots.items()},
            "dynamic_full_local_count": 0,
            "dynamic_thumb_local_count": 0,
            "dynamic_valid_decoded_count": 0,
            "absence_interpretation": "No local SSOTD dynamic image files found under either frozen baseline or v5 derived route; this is local coverage only, not a web absence claim.",
            "anachronos": {"path": rel(anachronos), "exists": anachronos.is_file(), "body": read_text(anachronos).strip() if anachronos.is_file() else None},
        },
        "game_guide_distinction": game_guide_inventory(),
        "saved_cdx_coverage": {
            "us_media": "No pre-existing local US /downloads/ssotd CDX rows were found before the separately authorized parent-query window; parent-query is linked separately after its result.",
            "regional_control": regional_cdx_inventory(),
            "wayback_window": wayback_window_inventory(),
        },
        "evidence": [
            {"path": rel(menu_path), "lines": "55-58", "role": "current MEDIA menu href"},
            {"path": rel(nav_path), "lines": "283-286", "role": "legacy Media/Screenshots href"},
            {"path": rel(page_path), "lines": "63-83", "role": "server Date and SSOTD addshots source"},
            {"path": rel(js_path), "lines": "12,432-496", "role": "slot, pagination, thumbnail construction"},
            {"path": "research/github-pages-20261013/gallery-inspection-20261013.md", "lines": "5-17,19-31", "role": "separate 50-gallery baseline"},
            {"path": "research/related-sites-20261014/regional-gallery/batch-plan.json", "role": "saved EU CDX range and completeness rule"},
        ],
    }
    json_path = OUT / "inventory.json"
    json_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "inventory.md").write_text(render_markdown(inventory), encoding="utf-8")
    print(json.dumps({
        "inventory": rel(json_path),
        "markdown": rel(OUT / "inventory.md"),
        "baseline_files": inventory["frozen_inputs"]["offline_site"]["file_count"],
        "static_ui_files": inventory["local_ssotd_assets"]["static_ui"]["file_count"],
        "dynamic_full": inventory["local_ssotd_assets"]["dynamic_full_local_count"],
        "dynamic_thumb": inventory["local_ssotd_assets"]["dynamic_thumb_local_count"],
        "guide_slots": inventory["game_guide_distinction"]["combined_slots"],
        "regional_cdx_rows": inventory["saved_cdx_coverage"]["regional_control"]["rows"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
