#!/usr/bin/env python3
"""Reconcile the saved US MEDIA/SSOTD CDX rows without network access.

The input set is deliberately bounded to the two saved 1000-row prefix pages
and the NET-SSOTD-012 terminal shard (82 rows).  This script does not replay
anything.  It records index rows separately from the two already accepted
2010 payloads and excludes routes that are already present in v17 provenance.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from typing import Any


ANCHOR = "20080512210044"
START_2008 = "20080101000000"
END_2008 = "20081231235959"
DISK_FLOOR = 11005853696
MAX_CANDIDATES = 20

RAW_SOURCES = [
    {
        "id": "wayback_prefix_page_0",
        "path": "research/media-screenshots-20261015/wayback-window/raw/07-ssotd_screens_prefix_rows_all.body",
        "expected_rows": 1000,
        "role": "canonical first saved prefix page; four alias query bodies were identical and are not recounted",
    },
    {
        "id": "wayback_prefix_page_1",
        "path": "research/media-screenshots-20261015/wayback-window/raw/13-ssotd_screens_prefix_resume_page1.body",
        "expected_rows": 1000,
        "role": "saved resume page; no further resume key was requested",
    },
    {
        "id": "net_ssotd_012_terminal82",
        "path": "research/continuous-recovery-20261015/network-ssotd12/raw/02-prefix-page-1-cdx-proxy.body",
        "expected_rows": 82,
        "role": "NET-SSOTD-012 terminal no-resume-key index-only shard",
    },
]

ALIAS_SOURCES = [
    "research/media-screenshots-20261015/wayback-window/raw/08-ssotd_screens_prefix_rows_port80.body",
    "research/media-screenshots-20261015/wayback-window/raw/09-ssotd_screens_prefix_rows_bare_port80.body",
    "research/media-screenshots-20261015/wayback-window/raw/10-ssotd_screens_prefix_rows_bare.body",
]

INPUT_FILES = [
    "research/continuous-recovery-20261016/local-audit/v2/media-gap-audit-v2.json",
    "research/continuous-recovery-20261015/network-ssotd12/batch-report.json",
    "research/continuous-recovery-20261015/network-ssotd12/sanitized-summary.json",
    "research/continuous-recovery-20261015/network-ssotd12/cdx-index-pages.json",
    "research/continuous-recovery-20261015/network-ssotd12/observed-index-candidates.json",
    "research/continuous-recovery-20261015/network-ssotd12/payload-source-map.json",
    "research/continuous-recovery-20261015/network-ssotd12/redirect-evidence.json",
    "research/media-screenshots-20261015/capture-ledger.json",
    "research/media-screenshots-20261015/late-image-source-map.json",
    "research/media-screenshots-20261015/wayback-window/request-records-reconciled.json",
    "research/media-screenshots-20261015/wayback-window/extended-summary.json",
    ".scratch/offline-navigation-20261015-v15/build-manifest.json",
    ".scratch/offline-navigation-20261015-v15/site/downloads/ssotd/index.html",
    ".scratch/offline-navigation-20261015-v15/site/new-hp/js/ssotd-screenie.js",
    ".scratch/pages-resources-20261016-v17/export-provenance.json",
    "research/continuous-recovery-20261016/publication/root-v17-input-acceptance.json",
    "research/continuous-recovery-20261016/publication/root-v17-local-acceptance.json",
    "research/continuous-recovery-20261016/integration/worker-build-v17.json",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def fail(message: str) -> None:
    raise RuntimeError(message)


def input_digest(root: Path, path_text: str, role: str | None = None) -> dict[str, Any]:
    path = root / path_text
    if not path.is_file():
        fail(f"missing input: {path_text}")
    result: dict[str, Any] = {"path": path_text, "bytes": path.stat().st_size, "sha256": sha256(path)}
    if role:
        result["role"] = role
    return result


def normalize_identity(value: str) -> str:
    parsed = urlsplit(value)
    scheme = parsed.scheme.lower()
    host = (parsed.hostname or "").lower()
    try:
        port = parsed.port
    except ValueError:
        port = None
    default = (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    netloc = host if port is None or default else f"{host}:{port}"
    return f"{scheme}://{netloc}{parsed.path}?{parsed.query}#{parsed.fragment}"


def temporal_bucket(timestamp: str) -> str:
    if timestamp < START_2008:
        return "pre_2008"
    if timestamp <= ANCHOR:
        return "baseline_le_anchor"
    if timestamp <= END_2008:
        return "late_2008"
    return "post_2008"


def row_category(row: dict[str, Any]) -> str:
    status = row["statuscode"]
    mime = row["mimetype"].lower()
    if status == "200" and mime.startswith("image/"):
        return "valid_status200_image_index_row"
    if status in {"301", "302", "307"}:
        return "redirect"
    if status == "-" or mime == "warc/revisit":
        return "revisit"
    if status == "404":
        return "archive_404"
    if status == "200":
        return "status200_non_image"
    return "other"


def parse_shot_identity(original: str) -> dict[str, Any]:
    parsed = urlsplit(original)
    match = re.search(r"/ss(\d+)(-thumb)?\.(jpg|jpeg|gif|png)$", parsed.path, re.IGNORECASE)
    if not match:
        return {"is_dynamic_ss_entity": False}
    number = int(match.group(1))
    is_thumb = bool(match.group(2))
    suffix = match.group(3).lower()
    counterpart_name = f"ss{number}{'' if is_thumb is False else ''}"
    counterpart_name += "-thumb" if not is_thumb else ""
    counterpart_name += f".{suffix}"
    counterpart_path = parsed.path[: parsed.path.rfind("/k") + 1] if False else parsed.path.rsplit("/", 1)[0] + "/" + counterpart_name
    return {
        "is_dynamic_ss_entity": True,
        "shot_number": number,
        "role": "thumb" if is_thumb else "full",
        "extension": suffix,
        "pair_key": f"ss{number}",
        "counterpart_path": counterpart_path,
    }


def load_rows(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    source_receipts: list[dict[str, Any]] = []
    for spec in RAW_SOURCES:
        path = root / spec["path"]
        if not path.is_file():
            fail(f"missing CDX body: {path}")
        body = json.loads(path.read_bytes())
        if not body or body[0] != ["timestamp", "original", "statuscode", "mimetype", "digest", "length"]:
            fail(f"unexpected CDX header: {spec['path']}")
        data = [(index, value) for index, value in enumerate(body[1:], start=1) if isinstance(value, list) and len(value) == 6]
        if len(data) != spec["expected_rows"]:
            fail(f"{spec['path']} data rows {len(data)} != {spec['expected_rows']}")
        source_receipts.append(
            {
                "id": spec["id"],
                "path": spec["path"],
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "json_list_length": len(body),
                "header_present": True,
                "data_rows": len(data),
                "role": spec["role"],
            }
        )
        for body_index, value in data:
            row = {
                "source_id": spec["id"],
                "body_path": spec["path"],
                "body_sha256": source_receipts[-1]["sha256"],
                "body_index": body_index,
                "timestamp": value[0],
                "original": value[1],
                "statuscode": str(value[2]),
                "mimetype": value[3],
                "digest": value[4],
                "length": str(value[5]),
            }
            row["identity_key"] = normalize_identity(row["original"])
            row["temporal_bucket"] = temporal_bucket(row["timestamp"])
            row["row_category"] = row_category(row)
            row["shot_identity"] = parse_shot_identity(row["original"])
            rows.append(row)
    if len(rows) != 2082:
        fail(f"canonical saved CDX rows {len(rows)} != 2082")
    alias_receipts = []
    first_sha = source_receipts[0]["sha256"]
    for path_text in ALIAS_SOURCES:
        path = root / path_text
        if not path.is_file():
            fail(f"missing alias body: {path_text}")
        alias_receipts.append(
            {
                "path": path_text,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "same_as_page_0": sha256(path) == first_sha,
                "counted_in_2082": False,
            }
        )
    raw_copy = copy.deepcopy(rows)
    unique: dict[tuple[Any, ...], dict[str, Any]] = {}
    duplicate_groups: defaultdict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            row["identity_key"],
            row["timestamp"],
            row["statuscode"],
            row["mimetype"],
            row["digest"],
            row["length"],
        )
        if key in unique:
            duplicate_groups[key].append(row)
        else:
            unique[key] = row
    dedup_rows = list(unique.values())
    dedup_receipt = {
        "raw_data_rows": len(rows),
        "dedup_data_rows": len(dedup_rows),
        "duplicate_row_instances_removed": len(rows) - len(dedup_rows),
        "dedup_key": "normalized original identity (default port only), actual timestamp, statuscode, mimetype, digest, length",
        "duplicate_groups": [
            {
                "key": list(key),
                "count": len(items) + 1,
                "locations": [
                    {"source_id": unique[key]["source_id"], "body_index": unique[key]["body_index"]},
                    *[{"source_id": item["source_id"], "body_index": item["body_index"]} for item in items],
                ],
            }
            for key, items in duplicate_groups.items()
        ],
    }
    return raw_copy, dedup_rows, {"sources": source_receipts, "aliases": alias_receipts, "dedup": dedup_receipt}


def route_matches(root: Path, rows: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    v15_path = root / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
    v17_path = root / ".scratch/pages-resources-20261016-v17/export-provenance.json"
    v15 = json.loads(v15_path.read_text(encoding="utf-8"))
    v17 = json.loads(v17_path.read_text(encoding="utf-8"))
    v15_by_route: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    v17_by_route: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in v15["files"]:
        if item.get("route"):
            v15_by_route[item["route"]].append(item)
    for item in v17["files"]:
        if item.get("route"):
            v17_by_route[item["route"]].append(item)
    v15_bases = {item.get("source_base_url") for item in v15["files"] if item.get("source_base_url")}
    v17_overlay_by_route = {route: items for route, items in v17_by_route.items() if any(x.get("kind") == "image_overlay" for x in items)}
    raw_hits = []
    for row in rows:
        path = urlsplit(row["original"]).path
        v15_hits = v15_by_route.get(path, [])
        v17_hits = v17_by_route.get(path, [])
        if v15_hits or v17_hits:
            raw_hits.append(
                {
                    "source_id": row["source_id"],
                    "body_index": row["body_index"],
                    "original": row["original"],
                    "path": path,
                    "row_category": row["row_category"],
                    "v15_route_match_count": len(v15_hits),
                    "v17_route_match_count": len(v17_hits),
                    "v17_overlay_match_count": len(v17_overlay_by_route.get(path, [])),
                    "v17_provenance": [
                        {
                            "route": x.get("route"),
                            "original_url": x.get("original_url"),
                            "kind": x.get("kind"),
                            "role": x.get("role"),
                            "source_map": x.get("source_map"),
                            "source_map_sha256": x.get("source_map_sha256"),
                            "source_path": x.get("source_path"),
                            "source_offline_path": x.get("source_offline_path"),
                            "source_sha256": x.get("source_sha256"),
                            "source_length": x.get("source_length"),
                            "derived_sha256": x.get("derived_sha256"),
                            "derived_length": x.get("derived_length"),
                            "actual_capture_timestamp": x.get("actual_capture_timestamp"),
                            "temporal_class": x.get("temporal_class"),
                        }
                        for x in v17_hits
                    ],
                }
            )
    scope = {
        "v15_manifest": {
            "path": rel(root, v15_path),
            "sha256": sha256(v15_path),
            "record_count": len(v15["files"]),
            "unique_route_count": len(v15_by_route),
            "source_base_url_count": len(v15_bases),
            "ssotd_route_count": sum("/downloads/ssotd/" in str(x.get("route", "")) for x in v15["files"]),
        },
        "v17_export_provenance": {
            "path": rel(root, v17_path),
            "sha256": sha256(v17_path),
            "record_count": len(v17["files"]),
            "unique_route_count": len(v17_by_route),
            "image_overlay_count": sum(x.get("kind") == "image_overlay" for x in v17["files"]),
            "ssotd_route_count": sum("/downloads/ssotd/" in str(x.get("route", "")) for x in v17["files"]),
            "source_records_declared": v17.get("stats", {}).get("source_records"),
        },
        "v17_overlay_route_count": len(v17_overlay_by_route),
        "raw_route_match_count": len(raw_hits),
        "unique_route_match_count": len({(x["path"], x["original"]) for x in raw_hits}),
        "unique_row_match_count": len({(x["path"], x["original"], x["row_category"], x["body_index"]) for x in raw_hits}),
        "raw_route_matches": raw_hits,
    }
    return scope, {"v15": v15_by_route, "v17": v17_by_route}, {"v15_bases": v15_bases, "v17_overlay": v17_overlay_by_route}


def source_anchor(root: Path) -> dict[str, Any]:
    page_path = root / ".scratch/offline-navigation-20261015-v15/site/downloads/ssotd/index.html"
    js_path = root / ".scratch/offline-navigation-20261015-v15/site/new-hp/js/ssotd-screenie.js"
    manifest = json.loads((root / ".scratch/offline-navigation-20261015-v15/build-manifest.json").read_text(encoding="utf-8"))
    page_entry = next(x for x in manifest["files"] if x.get("route") == "/downloads/ssotd/index.html")
    page_text = page_path.read_text(encoding="utf-8", errors="replace")
    js_text = js_path.read_text(encoding="utf-8", errors="replace")
    start_match = re.search(r"startDate\s*=\s*(\d+)", page_text)
    if not start_match:
        fail("SSOTD startDate literal not found")
    start_date = int(start_match.group(1))
    timestamp = page_entry.get("actual_timestamp")
    if not timestamp:
        fail("SSOTD source actual_timestamp missing from v15 manifest")
    dt = datetime.strptime(timestamp, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    epoch_days = (dt - datetime(1970, 1, 1, tzinfo=timezone.utc)).days
    shot_number = epoch_days - start_date
    if shot_number != 1340:
        fail(f"derived anchor shot number {shot_number} != 1340")
    if 'dir + "/" + filename + (i) +".jpg"' not in js_text:
        fail("SSOTD full image rule literal not found")
    if 'replace(".jpg","-thumb.jpg")' not in js_text:
        fail("SSOTD thumbnail rule literal not found")
    return {
        "anchor_timestamp": ANCHOR,
        "source_page": {
            "path": rel(root, page_path),
            "sha256": sha256(page_path),
            "source_manifest_actual_timestamp": timestamp,
            "source_manifest_route": "/downloads/ssotd/index.html",
            "startDate": start_date,
            "derived_currentShotNumber": shot_number,
            "numeric_range": {"first": 1, "last": shot_number},
            "range_meaning": "source page runtime range derived from saved anchor server-date entity; numeric coverage is separate from temporal class",
        },
        "js_rule": {
            "path": rel(root, js_path),
            "sha256": sha256(js_path),
            "full_literal": 'dir + "/" + filename + (i) +".jpg"',
            "thumb_literal": 'replace(".jpg","-thumb.jpg")',
        },
    }


def late_map_and_payloads(root: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    map_path = root / "research/media-screenshots-20261015/late-image-source-map.json"
    source_map = json.loads(map_path.read_text(encoding="utf-8"))
    entries: dict[str, dict[str, Any]] = {}
    for entry in source_map["items"]:
        payload_path = root / entry["local_path"]
        if not payload_path.is_file():
            fail(f"missing accepted payload: {entry['local_path']}")
        actual_sha = sha256(payload_path)
        if actual_sha != entry["sha256"] or payload_path.stat().st_size != entry["length"]:
            fail(f"accepted payload changed: {entry['logical_url']}")
        entries[normalize_identity(entry["original"])] = {
            "source_map_path": rel(root, map_path),
            "source_map_sha256": sha256(map_path),
            "payload_exists": True,
            "payload_path": entry["local_path"],
            "payload_sha256": actual_sha,
            "payload_length": payload_path.stat().st_size,
            "source_map_entry": copy.deepcopy(entry),
        }
    return {
        "path": rel(root, map_path),
        "sha256": sha256(map_path),
        "entry_count": len(source_map["items"]),
        "items": copy.deepcopy(source_map["items"]),
    }, entries


def prior_controls(root: Path) -> dict[str, Any]:
    req_path = root / "research/media-screenshots-20261015/wayback-window/request-records-reconciled.json"
    records = json.loads(req_path.read_text(encoding="utf-8"))
    wanted = {
        "ssotd_capture_date_derived_ss1340_exact",
        "ssotd_capture_date_derived_ss1340_thumb_exact",
        "exact_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314-thumb.jpg",
        "replay_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1314.jpg",
        "replay_http_www.worldofwarcraft.com_downloads_ssotd_images_screens_ss1336.jpg",
    }
    controls = []
    for record in records:
        if record.get("label") not in wanted:
            continue
        body_path = record.get("body_path")
        raw_path = req_path.parent / body_path if body_path else None
        controls.append(
            {
                "label": record.get("label"),
                "kind": record.get("kind"),
                "source_status": record.get("status"),
                "body_path": (rel(root, raw_path) if raw_path and raw_path.is_file() else body_path),
                "body_sha256": (sha256(raw_path) if raw_path and raw_path.is_file() else record.get("body_sha256")),
                "body_bytes": record.get("body_bytes"),
                "rows_count": len(record.get("rows") or []),
                "replay_payload": record.get("payload_probe") or None,
                "note": "Saved control/replay evidence only; no new request made by this audit.",
            }
        )
    batch_path = root / "research/continuous-recovery-20261015/network-ssotd12/payload-source-map.json"
    batch_map = json.loads(batch_path.read_text(encoding="utf-8"))
    controls.append(
        {
            "label": "NET-SSOTD-012 payload-source-map",
            "path": rel(root, batch_path),
            "sha256": sha256(batch_path),
            "entity_count": batch_map.get("entity_count"),
            "integration_held": batch_map.get("integration_held"),
            "note": "Terminal82 shard has no valid payload entities.",
        }
    )
    return {"records": controls, "source_records_path": rel(root, req_path), "source_records_sha256": sha256(req_path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[4])
    args = parser.parse_args()
    root = args.root.resolve()
    out_dir = root / "research/continuous-recovery-20261016/local-audit/media-candidates"
    out_json = out_dir / "media-candidates-audit.json"
    out_md = out_dir / "media-candidates-audit.md"
    out_verify = out_dir / "verification.json"
    for path in (out_json, out_md, out_verify):
        if path.exists():
            fail(f"refusing to overwrite existing audit output: {path}")

    raw_rows, dedup_rows, raw_receipt = load_rows(root)
    provenance_scope, route_indexes, route_sets = route_matches(root, raw_rows)
    anchor = source_anchor(root)
    late_map, late_entries = late_map_and_payloads(root)
    controls = prior_controls(root)

    valid_rows = [row for row in dedup_rows if row["row_category"] == "valid_status200_image_index_row"]
    valid_raw_rows = [row for row in raw_rows if row["row_category"] == "valid_status200_image_index_row"]
    candidates: list[dict[str, Any]] = []
    excluded_valid_rows: list[dict[str, Any]] = []
    for row in valid_rows:
        path = urlsplit(row["original"]).path
        v17_hits = route_indexes["v17"].get(path, [])
        v15_hits = route_indexes["v15"].get(path, [])
        known = late_entries.get(row["identity_key"])
        shot = row["shot_identity"]
        counterpart = None
        if shot.get("is_dynamic_ss_entity"):
            counterpart = f"{urlsplit(row['original']).scheme}://{urlsplit(row['original']).netloc}{shot['counterpart_path']}"
        record = {
            "original_row": {
                "timestamp": row["timestamp"],
                "original": row["original"],
                "statuscode": row["statuscode"],
                "mimetype": row["mimetype"],
                "digest": row["digest"],
                "length": row["length"],
            },
            "source_evidence": {
                "body_path": row["body_path"],
                "body_sha256": row["body_sha256"],
                "body_index": row["body_index"],
                "source_id": row["source_id"],
            },
            "identity": {
                "normalized_identity": row["identity_key"],
                "temporal_bucket": row["temporal_bucket"],
                "row_category": row["row_category"],
                "shot": shot,
                "source2008_numeric_range_covers_slot": bool(shot.get("shot_number") and 1 <= shot["shot_number"] <= anchor["source_page"]["numeric_range"]["last"]),
                "counterpart_expected": counterpart,
                "counterpart_status200_image_rows_in_2082": [
                    x["original"] for x in valid_rows if counterpart and normalize_identity(x["original"]) == normalize_identity(counterpart)
                ],
            },
            "existing_route_provenance_match": {
                "v17_route_matches": len(v17_hits),
                "v15_route_matches": len(v15_hits),
                "v17_overlay_route_match": any(x.get("kind") == "image_overlay" for x in v17_hits),
                "v17_records": [
                    {
                        "route": x.get("route"),
                        "original_url": x.get("original_url"),
                        "kind": x.get("kind"),
                        "role": x.get("role"),
                        "source_map": x.get("source_map"),
                        "source_map_sha256": x.get("source_map_sha256"),
                        "source_path": x.get("source_path"),
                        "source_sha256": x.get("source_sha256"),
                        "source_length": x.get("source_length"),
                        "derived_sha256": x.get("derived_sha256"),
                        "derived_length": x.get("derived_length"),
                        "actual_capture_timestamp": x.get("actual_capture_timestamp"),
                        "temporal_class": x.get("temporal_class"),
                    }
                    for x in v17_hits
                ],
            },
            "accepted_late_payload_match": known,
        }
        if v17_hits or v15_hits or known:
            record["exclusion_reason"] = "already_present_route_with_full_v17_or_v15_provenance" if v17_hits or v15_hits else "already_accepted_late_payload_source_map"
            excluded_valid_rows.append(record)
        else:
            record["candidate_reason"] = "status200_image_row_without_existing_route_or_accepted_payload"
            candidates.append(record)

    if len(candidates) > MAX_CANDIDATES:
        fail(f"candidate queue exceeds bound: {len(candidates)}")
    if len(valid_rows) != 2 or len(valid_raw_rows) != 2:
        fail(f"expected exactly two saved status200 image rows, got raw={len(valid_raw_rows)} dedup={len(valid_rows)}")
    if len(excluded_valid_rows) != 2 or candidates:
        fail(f"expected the two known late rows to be excluded and no new candidates: excluded={len(excluded_valid_rows)}, candidates={len(candidates)}")
    if provenance_scope["v17_export_provenance"]["image_overlay_count"] != 69:
        fail("v17 image overlay count changed from accepted 69")
    if provenance_scope["v17_export_provenance"]["record_count"] != 8527:
        fail("v17 provenance record count changed from accepted 8527")
    if provenance_scope["v15_manifest"]["record_count"] != 8357:
        fail("v15 source manifest record count changed from accepted 8357")

    def counts(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
        return dict(sorted(Counter(str(row[key]) for row in rows).items()))

    raw_category_counts = counts(raw_rows, "row_category")
    raw_bucket_counts = counts(raw_rows, "temporal_bucket")
    dedup_category_counts = counts(dedup_rows, "row_category")
    dedup_bucket_counts = counts(dedup_rows, "temporal_bucket")
    cross = Counter((row["temporal_bucket"], row["row_category"]) for row in raw_rows)

    input_digests = [input_digest(root, path) for path in INPUT_FILES]
    batch_report = json.loads((root / "research/continuous-recovery-20261015/network-ssotd12/batch-report.json").read_text(encoding="utf-8"))
    batch_summary = json.loads((root / "research/continuous-recovery-20261015/network-ssotd12/sanitized-summary.json").read_text(encoding="utf-8"))
    v17_acceptance = json.loads((root / "research/continuous-recovery-20261016/publication/root-v17-input-acceptance.json").read_text(encoding="utf-8"))
    audit = {
        "schema": "wow-recovery.local-audit.media-candidates.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "network_performed_by_audit": False,
        "scope": {
            "source": "saved MEDIA/SSOTD CDX rows only",
            "canonical_raw_row_count": len(raw_rows),
            "canonical_raw_row_count_expected": 2082,
            "deduplicated_row_count": len(dedup_rows),
            "candidate_bound": MAX_CANDIDATES,
            "dedup_identity_rule": "normalized exact original identity (default port normalization only) plus actual timestamp/status/MIME/digest/length",
            "temporal_boundaries": {
                "pre_2008": f"timestamp < {START_2008}",
                "baseline_le_anchor": f"{START_2008} <= timestamp <= {ANCHOR}",
                "late_2008": f"{ANCHOR} < timestamp <= {END_2008}",
                "post_2008": f"timestamp > {END_2008}",
            },
            "index_vs_payload": "CDX rows are index evidence. A status200 image row is not called recovered unless saved payload/provenance validates it.",
        },
        "input_hashes": input_digests,
        "raw_sources": raw_receipt,
        "row_accounting": {
            "raw_rows": len(raw_rows),
            "deduplicated_rows": len(dedup_rows),
            "raw_source_counts": counts(raw_rows, "source_id"),
            "raw_status_counts": counts(raw_rows, "statuscode"),
            "raw_mime_counts": counts(raw_rows, "mimetype"),
            "raw_category_counts": raw_category_counts,
            "raw_temporal_bucket_counts": raw_bucket_counts,
            "raw_temporal_category_counts": {f"{k[0]}::{k[1]}": v for k, v in sorted(cross.items())},
            "dedup_category_counts": dedup_category_counts,
            "dedup_temporal_bucket_counts": dedup_bucket_counts,
            "conservation": {
                "raw_categories_sum": sum(raw_category_counts.values()),
                "raw_temporal_sum": sum(raw_bucket_counts.values()),
                "source_sum": sum(counts(raw_rows, "source_id").values()),
                "all_equal_2082": sum(raw_category_counts.values()) == sum(raw_bucket_counts.values()) == len(raw_rows) == 2082,
            },
            "dedup": raw_receipt["dedup"],
        },
        "source_anchor": anchor,
        "terminal_net_ssotd_012": {
            "batch_id": batch_report["batch_id"],
            "report_path": "research/continuous-recovery-20261015/network-ssotd12/batch-report.json",
            "report_sha256": sha256(root / "research/continuous-recovery-20261015/network-ssotd12/batch-report.json"),
            "new_index_rows": batch_report["cdx_index_row_count"],
            "old_plus_new_scoped_index_rows": 2082,
            "terminal_no_resume_key": True,
            "valid_payload_entities": batch_report["valid_entity_count"],
            "category_counts": batch_summary["category_counts"],
            "interpretation": "82 terminal rows are post-anchor index-only evidence; no payload entity was added.",
        },
        "existing_route_exclusion": provenance_scope,
        "known_accepted_late_payloads": late_map,
        "prior_replay_controls": controls,
        "valid_image_rows": {
            "raw_count": len(valid_raw_rows),
            "deduplicated_count": len(valid_rows),
            "new_candidate_count": len(candidates),
            "existing_or_accepted_excluded_count": len(excluded_valid_rows),
            "excluded_rows": excluded_valid_rows,
            "new_candidates": candidates,
        },
        "v17_acceptance_binding": {
            "path": "research/continuous-recovery-20261016/publication/root-v17-input-acceptance.json",
            "sha256": sha256(root / "research/continuous-recovery-20261016/publication/root-v17-input-acceptance.json"),
            "accepted": v17_acceptance.get("accepted"),
            "source_records": v17_acceptance.get("source_records"),
            "total_overlays": v17_acceptance.get("total_overlays"),
            "guide_preview_count": v17_acceptance.get("guide_preview_count"),
        },
        "notes": [
            "There are no new exact-CDX-supported image candidates after route/provenance and accepted payload exclusion.",
            "The two valid status200 image rows are ss1314.jpg and ss1336.jpg, both post_2008 payloads already present as v17 image_overlay records and in the accepted late-image source map.",
            "No pre_2008 or baseline_le_anchor status200 image row exists in the 2082 saved rows; late_2008 rows are HTML/404/redirect evidence only.",
            "The four alias query bodies 08/09/10 duplicate the first canonical body by SHA and are not recounted; NET-SSOTD-012 contributes the terminal 82 rows once.",
            "No candidate URL was guessed, downloaded, replayed, or integrated by this audit.",
        ],
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    md_lines = [
        "# MEDIA/SSOTD candidate audit",
        "",
        "- Scope: saved canonical CDX rows only; network requests by this audit: `0`.",
        "- Raw rows: `2082` (`1000 + 1000 + NET-SSOTD-012 terminal 82`); deduplicated rows: `2076` after six exact duplicate row instances.",
        f"- Status categories: `{raw_category_counts}`.",
        f"- Temporal buckets: `{raw_bucket_counts}`; pre-2008 and baseline status-200 image candidates: `0`.",
        f"- v17 exclusion scope: `8527` provenance records, `69` image overlays; v15 source manifest: `8357` records.",
        "",
        "## Candidate result",
        "",
        "**New exact-CDX-supported candidates: 0.** The only two status-200 image rows are the already accepted post-2008 `ss1314.jpg` and `ss1336.jpg`; both match complete v17 route/provenance records and are excluded.",
        "",
        "| Original | CDX timestamp/digest | Source body | Route/provenance | Temporal | Pair relation |",
        "|---|---|---|---|---|---|",
    ]
    for item in excluded_valid_rows:
        row = item["original_row"]
        v17 = item["existing_route_provenance_match"]["v17_records"][0]
        md_lines.append(
            f"| `{row['original']}` | `{row['timestamp']}` / `{row['digest']}` | `{item['source_evidence']['body_path']}#{item['source_evidence']['body_index']}` (SHA `{item['source_evidence']['body_sha256']}`) | `{v17.get('kind')}` `{v17.get('source_map')}` | `{item['identity']['temporal_bucket']}` | `{item['identity']['shot'].get('role')}` ↔ `{item['identity']['counterpart_expected']}`; counterpart status-200 image rows: 0 |"
        )
    md_lines.extend(
        [
            "",
            "## Accounting",
            "",
            f"- Raw category conservation: `{raw_category_counts}`; sum `{sum(raw_category_counts.values())}`.",
            f"- Raw temporal conservation: `{raw_bucket_counts}`; sum `{sum(raw_bucket_counts.values())}`.",
            "- Redirect/revisit/index rows are retained as evidence and are never counted as payload recovery.",
            "- NET-SSOTD-012 terminal82 has `valid_payload_entities=0`; no additional replay target is emitted.",
            "",
            "## Boundaries",
            "",
            "The source page derives a numeric SSOTD range `ss1.jpg` through `ss1340.jpg` at the saved anchor timestamp, using the frozen `startDate` and `ssotd-screenie.js` rules. Numeric slot coverage does not turn a post-2008 capture into a baseline-2008 asset.",
            "",
        ]
    )
    out_md.write_text("\n".join(md_lines), encoding="utf-8", newline="\n")

    free_bytes = shutil.disk_usage(root).free
    checks = {
        "network_performed_by_audit_false": audit["network_performed_by_audit"] is False,
        "raw_row_count_2082": len(raw_rows) == 2082,
        "source_rows_1000_1000_82": [x["data_rows"] for x in raw_receipt["sources"]] == [1000, 1000, 82],
        "dedup_row_count_2076": len(dedup_rows) == 2076,
        "raw_category_conservation": sum(raw_category_counts.values()) == 2082,
        "raw_temporal_conservation": sum(raw_bucket_counts.values()) == 2082,
        "valid_status200_image_rows_exactly_two": len(valid_rows) == 2,
        "new_candidate_count_zero": len(candidates) == 0,
        "late_existing_excluded_two": len(excluded_valid_rows) == 2,
        "v17_records_8527": provenance_scope["v17_export_provenance"]["record_count"] == 8527,
        "v17_overlays_69": provenance_scope["v17_export_provenance"]["image_overlay_count"] == 69,
        "v15_manifest_records_8357": provenance_scope["v15_manifest"]["record_count"] == 8357,
        "net012_rows_82": batch_report["cdx_index_row_count"] == 82,
        "net012_valid_payload_zero": batch_report["valid_entity_count"] == 0,
        "accepted_late_map_entries_two": late_map["entry_count"] == 2,
        "anchor_shot_number_1340": anchor["source_page"]["derived_currentShotNumber"] == 1340,
        "disk_above_floor": free_bytes >= DISK_FLOOR,
    }
    verification = {
        "schema": "wow-recovery.local-audit.media-candidates.verification.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "network_performed": False,
        "command_scope": "local-only saved CDX/provenance reconciliation; no replay or download",
        "outputs": {
            "audit": {"path": rel(root, out_json), "sha256": sha256(out_json), "bytes": out_json.stat().st_size},
            "markdown": {"path": rel(root, out_md), "sha256": sha256(out_md), "bytes": out_md.stat().st_size},
        },
        "counts": {
            "raw_rows": len(raw_rows),
            "deduplicated_rows": len(dedup_rows),
            "valid_status200_image_rows": len(valid_rows),
            "new_candidates": len(candidates),
            "excluded_existing_or_accepted": len(excluded_valid_rows),
            "v17_provenance_records": provenance_scope["v17_export_provenance"]["record_count"],
            "v17_overlays": provenance_scope["v17_export_provenance"]["image_overlay_count"],
            "v15_manifest_records": provenance_scope["v15_manifest"]["record_count"],
        },
        "disk": {"free_bytes": free_bytes, "floor_bytes": DISK_FLOOR, "above_floor": free_bytes >= DISK_FLOOR},
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }
    out_verify.write_text(json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if not verification["all_checks_pass"]:
        fail(f"verification failed: {verification['checks']}")
    print(json.dumps({
        "audit": rel(root, out_json),
        "audit_sha256": verification["outputs"]["audit"]["sha256"],
        "markdown": rel(root, out_md),
        "markdown_sha256": verification["outputs"]["markdown"]["sha256"],
        "verification": rel(root, out_verify),
        "all_checks_pass": verification["all_checks_pass"],
        "raw_rows": len(raw_rows),
        "deduplicated_rows": len(dedup_rows),
        "new_candidates": len(candidates),
        "network_performed": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
