from __future__ import annotations

import hashlib
import io
import json
import pathlib
import subprocess
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urlsplit

from PIL import Image


ROOT = pathlib.Path(__file__).resolve().parents[4]
AUDIT_DIR = pathlib.Path(__file__).resolve().parent
QUEUE = ROOT / "research/continuous-recovery-20261020/local-audit/recovery-queue.json"
TAIL = ROOT / "research/continuous-recovery-20261020/local-audit/news-extension-141-160.json"
CANDIDATE = ROOT / "research/continuous-recovery-20261019/local-audit/news-extension/news-extension-candidates.json"
V38 = ROOT / ".scratch/pages-resources-20261019-v38"
NETWORK = ROOT / "research/continuous-recovery-20261019/network"


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: pathlib.Path) -> str:
    return path.relative_to(ROOT).as_posix()


def json_load(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def magic_mime(data: bytes) -> str:
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    if data.lstrip().lower().startswith((b"<!doctype html", b"<html", b"<head", b"<body")):
        return "text/html"
    return "application/octet-stream"


def validate_image(path: pathlib.Path, expected: dict) -> dict:
    data = path.read_bytes()
    result = {
        "path": rel(path),
        "exists": True,
        "length": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "magic_mime": magic_mime(data),
        "declared_mime": expected.get("actual_content_type"),
        "expected_length": expected.get("decoded_body_bytes"),
        "expected_sha256": expected.get("decoded_body_sha256"),
        "format": None,
        "frame_count": None,
        "size": None,
        "mode": None,
        "decode_status": "failed",
        "hash_length_match": False,
    }
    try:
        with Image.open(io.BytesIO(data)) as im:
            result["format"] = im.format
            result["size"] = list(im.size)
            result["mode"] = im.mode
            frames = 0
            while True:
                im.seek(frames)
                im.copy().load()
                frames += 1
    except EOFError:
        result["frame_count"] = frames
        result["decode_status"] = "valid"
    except Exception as exc:  # validation evidence, never a control path
        result["decode_error"] = f"{type(exc).__name__}: {exc}"
    else:
        result["frame_count"] = frames
        result["decode_status"] = "valid"
    result["hash_length_match"] = (
        result["length"] == result["expected_length"]
        and result["sha256"] == result["expected_sha256"]
    )
    result["mime_match"] = result["magic_mime"] == result["declared_mime"]
    return result


def target_record(group: str, item: dict) -> dict:
    url = item.get("original_url") or item.get("requested_url")
    source = item.get("source") or item.get("source_reference") or {}
    v38 = item.get("v38") or item.get("v38_local") or {}
    direct = ROOT / (v38.get("local_direct_path") or v38.get("direct_asset_path") or (".scratch/pages-resources-20261019-v38/" + urlsplit(url).path.lstrip("/")))
    historical = item.get("historical_execution_evidence_in_manifest", [])
    if not isinstance(historical, list):
        historical = []
    exact_replay = item.get("image_replay_receipts") or item.get("actual_exact_cdx_or_replay_evidence") or []
    if not isinstance(exact_replay, list):
        exact_replay = []
    return {
        "group": group,
        "rank": item.get("candidate_rank"),
        "item_id": item.get("item_id"),
        "original_url": url,
        "original_host": urlsplit(url).netloc,
        "source_class": item.get("source_class") or item.get("role"),
        "comment_only": group == "koreapvp_comment_only",
        "source_location": {
            "path": source.get("path") or source.get("source_file"),
            "line": source.get("line") or source.get("v33_marker", {}).get("line"),
            "sha256": source.get("sha256") or source.get("source_page_sha256"),
            "attribute_kind": source.get("attribute_kind") or source.get("v33_marker", {}).get("attribute_kind"),
            "context_kind": source.get("context_kind_corrected") or source.get("context_kind"),
        },
        "candidate_manifest": source.get("candidate_manifest"),
        "candidate_manifest_sha256": source.get("candidate_manifest_sha256"),
        "v38_marker": {
            "path": v38.get("path"),
            "line": v38.get("line"),
            "active_missing_marker": v38.get("active_missing_marker"),
            "direct_asset_path": v38.get("local_direct_path") or v38.get("direct_asset_path"),
            "direct_asset_exists_recorded": v38.get("local_direct_exists") if "local_direct_exists" in v38 else v38.get("direct_asset_exists"),
        },
        "direct_asset_exists_now": direct.exists(),
        "direct_asset_path_now": rel(direct),
        "historical_plan_or_queue_evidence_count": len(historical),
        "actual_exact_cdx_or_replay_evidence_count": len(exact_replay),
        "index_exact_hits": [],
        "index_path_hits": [],
        "status": "no_local_payload_evidence",
    }


def main() -> None:
    queue = json_load(QUEUE)
    tail = json_load(TAIL)
    candidate = json_load(CANDIDATE)

    targets = []
    targets.extend(target_record("koreapvp_comment_only", x) for x in queue["a_koreapvp_comment_only"]["items"])
    targets.extend(target_record("news_121_140", x) for x in queue["b_news_extension_priority"]["items"])
    targets.extend(target_record("news_141_160", x) for x in tail["items"])

    candidate_by_url = {x["requested_url"]: x for x in candidate["candidates"]}
    rank_by_url = {x["requested_url"]: x["rank"] for x in candidate["candidate_shortlist"]}

    source_maps = []
    active_hits = {}
    for path in sorted(NETWORK.glob("*/output/source-map.json")):
        d = json_load(path)
        source_maps.append({"path": rel(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
        for payload in d.get("accepted_payloads", []):
            url = payload.get("original")
            if url not in rank_by_url:
                continue
            active_hits.setdefault(url, (path, payload))

    payload_records = []
    counters = Counter()
    payload_bytes = 0
    for url, (source_map_path, payload) in sorted(active_hits.items(), key=lambda kv: (rank_by_url[kv[0]], kv[0])):
        payload_path = ROOT / payload["private_decoded_payload_path"]
        verification = payload.get("verification") or {}
        if payload_path.exists():
            validated = validate_image(payload_path, {
                "actual_content_type": verification.get("actual_content_type"),
                "decoded_body_bytes": payload.get("decoded_body_bytes"),
                "decoded_body_sha256": payload.get("decoded_body_sha256"),
            })
            payload_bytes += validated["length"]
            counters[validated["decode_status"]] += 1
            if validated["decode_status"] == "valid" and validated["hash_length_match"] and validated["mime_match"]:
                classification = "already_integrated_v38"
            else:
                classification = "validation_failed"
        else:
            validated = {"path": rel(payload_path), "exists": False, "decode_status": "missing"}
            counters["missing"] += 1
            classification = "payload_missing"
        direct = V38 / urlsplit(url).path.lstrip("/")
        c = candidate_by_url[url]
        marker = (c.get("markers") or [{}])[0]
        payload_records.append({
            "candidate_rank": rank_by_url[url],
            "requested_url": url,
            "original_host": urlsplit(url).netloc,
            "scheme": urlsplit(url).scheme,
            "candidate_state": c.get("state"),
            "is_news": c.get("is_news"),
            "marker_count": c.get("marker_count"),
            "active_marker": {
                "output_file": marker.get("output_file"),
                "line": marker.get("line"),
                "source_url": marker.get("source_url"),
                "reason": marker.get("reason"),
            },
            "source_map": {
                "path": rel(source_map_path),
                "sha256": sha256(source_map_path),
                "target_key": payload.get("target_key"),
                "selected_capture_timestamp": payload.get("selected_capture_timestamp"),
                "actual_memento_timestamp": payload.get("actual_memento_timestamp"),
                "original": payload.get("original"),
                "actual_link_original": payload.get("actual_link_original"),
                "cdx_digest": payload.get("cdx_digest"),
                "declared_content_type": (payload.get("verification") or {}).get("actual_content_type"),
                "declared_image_format": (payload.get("verification") or {}).get("image_format"),
                "declared_frame_count": (payload.get("verification") or {}).get("image_frame_count"),
                "declared_body_bytes": payload.get("decoded_body_bytes"),
                "declared_body_sha256": payload.get("decoded_body_sha256"),
            },
            "payload": validated,
            "v38_direct_asset_path": rel(direct),
            "v38_direct_asset_exists": direct.exists(),
            "classification": classification,
        })

    input_hashes = []
    for path in [QUEUE, TAIL, CANDIDATE]:
        input_hashes.append({"path": rel(path), "bytes": path.stat().st_size, "sha256": sha256(path)})

    # These are the exact bounded commands already run in this audit. Their empty
    # output is retained as evidence; the broad historical index sweeps are not
    # treated as payload evidence.
    target_file = AUDIT_DIR / "target-urls.txt"
    path_file = AUDIT_DIR / "target-paths.txt"
    scopes = [
        {"id": "mirror_url_map", "root": "mirror/20080512/url-map.json", "file_count": 1, "candidate_bytes": 626585, "exact_result": "no_match", "path_result": "no_match"},
        {"id": "resource_recovery_source_maps", "root": "research/resource-recovery-2008", "glob": ["*valid-source-map*.json", "*source-map*.json"], "file_count": 114, "candidate_bytes": 54306961, "exact_result": "no_match", "path_result": "no_match"},
        {"id": "backup_manifests", "root": "backups", "glob": ["manifest.jsonl", "*manifest*.json"], "file_count": 150, "candidate_bytes": 51985654, "exact_result": "no_match", "path_result": "no_match"},
        {"id": "acquisition_catalogs", "root": "research/acquisition-2008", "glob": ["*.json", "*.jsonl"], "selection": "catalog/mapping/url-map filenames", "file_count": 13, "candidate_bytes": 2348002, "exact_result": "no_match", "path_result": "no_match"},
        {"id": "offline_metadata", "root": "offline", "glob": ["*.json", "*.jsonl"], "selection": "manifest/catalog/map/index/receipt filenames", "file_count": 18, "candidate_bytes": 118920802, "exact_result": "no_match", "path_result": "no_match"},
    ]
    commands = [
        f"rg -l --fixed-strings --file {rel(target_file)} --glob '*.json' --glob '*.jsonl' --glob '!**/*.bin' --glob '!**/*.zip' --glob '!**/raw/**' mirror/20080512 research/acquisition-2008 offline",
        f"rg -l --fixed-strings --file {rel(path_file)} --glob '*.json' --glob '*.jsonl' --glob '!**/*.bin' --glob '!**/*.zip' --glob '!**/raw/**' mirror/20080512 research/acquisition-2008 offline",
        f"rg -l --fixed-strings --file {rel(target_file)} --glob '*valid-source-map*.json' --glob '*source-map*.json' research/resource-recovery-2008",
        f"rg -l --fixed-strings --file {rel(path_file)} --glob '*valid-source-map*.json' --glob '*source-map*.json' research/resource-recovery-2008",
        f"rg -l --fixed-strings --file {rel(target_file)} --glob 'manifest.jsonl' --glob '*manifest*.json' --glob '!**/*.zip' --glob '!**/raw/**' backups",
        f"rg -l --fixed-strings --file {rel(path_file)} --glob 'manifest.jsonl' --glob '*manifest*.json' --glob '!**/*.zip' --glob '!**/raw/**' backups",
    ]

    report = {
        "schema": "wow-encyclopedia-existing-payload-audit/v1",
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "network_performed": False,
        "repository_head": "f84786d4820438213f0610df147fb78c3f0b2af9",
        "scope": {
            "target_groups": {"koreapvp_comment_only": 6, "news_121_140": 20, "news_141_160": 20, "total": 46},
            "source15_comment_only_rule": "The six koreapvp img-src strings are in the commented A Rumble in the Desert block; they remain historical clues, not active v38 missing images.",
            "current_overlay_root_excluded_from_new_payload_count": ".scratch/pages-resources-20261019-v38",
            "source15_and_old_acceptance_immutable": True,
        },
        "input_hashes": input_hashes,
        "target_input_files": {
            "urls_file": {"path": rel(target_file), "bytes": target_file.stat().st_size, "sha256": sha256(target_file)},
            "paths_file": {"path": rel(path_file), "bytes": path_file.stat().st_size, "sha256": sha256(path_file)},
        },
        "index_search": {
            "commands": commands,
            "scope_summaries": scopes,
            "all_exact_and_path_results_empty": True,
            "interpretation": "No selected mirror/manifest/catalog/source-map index recorded an exact URL or path for the 46 primary targets. ZIP-only references were not converted into payload evidence.",
        },
        "active_marker_expansion": {
            "candidate_manifest": {"path": rel(CANDIDATE), "bytes": CANDIDATE.stat().st_size, "sha256": sha256(CANDIDATE)},
            "candidate_shortlist_count": len(candidate.get("candidate_shortlist", [])),
            "network_source_maps_scanned": source_maps,
            "unique_successful_active_marker_urls": len(payload_records),
            "successful_urls_by_kind": dict(Counter("news" if x["is_news"] else "nonnews" for x in payload_records)),
            "source_map_overlap_rank_range": [min((x["candidate_rank"] for x in payload_records), default=None), max((x["candidate_rank"] for x in payload_records), default=None)],
            "payload_validation_counts": dict(counters),
            "payload_bytes_checked": payload_bytes,
            "payload_files_checked": len(payload_records),
            "new_not_integrated_count": sum(x["classification"] not in ("already_integrated_v38",) for x in payload_records),
            "records": payload_records,
        },
        "targets": targets,
        "findings": {
            "primary_exact_target_actual_payloads": 0,
            "primary_exact_target_index_only_zip_refs": 0,
            "primary_exact_target_wrong_content_rejected": 0,
            "active_marker_payloads_found": len(payload_records),
            "active_marker_payloads_already_in_v38": sum(x["classification"] == "already_integrated_v38" for x in payload_records),
            "new_payload_candidates_for_root": [x for x in payload_records if x["classification"] != "already_integrated_v38"],
        },
        "limits_and_deviations": {
            "requested_payload_file_limit": 100,
            "requested_payload_bytes_limit": 67108864,
            "requested_elapsed_limit_minutes": 15,
            "payload_file_limit_observed": len(payload_records) <= 100,
            "payload_bytes_limit_observed": payload_bytes <= 67108864,
            "index_sweeps_note": "The prior exact/path rg passes were restricted to metadata globs and no payload bytes were used, but their candidate index-file sizes exceeded the nominal 64 MiB reading budget. The offline glob also included offline/build-manifest.json (73,067,980 bytes) and approved-static-recovery-map.json (29,791,895 bytes); neither produced a match and neither is used as payload evidence. This is recorded as a procedure deviation.",
            "zip_and_raw_policy": "No ZIP was opened or extracted; no raw body tree was recursively scanned for payload bytes.",
        },
        "unknowns": [
            "No exact target URL/path receipt exists in the selected local indexes; absence does not prove the remote archive has no capture.",
            "ZIP entries, CDX rows without local body bytes, and unindexed files were not promoted to payload candidates.",
            "The 75 MiB .scratch/offline-navigation-20261015-v15/build-manifest.json was excluded from evidence; the separate offline/build-manifest.json was incidentally read by the broad offline rg pass and is explicitly treated as non-evidence.",
            "Candidate ranks 161..240 and any later candidate manifest were outside this bounded expansion.",
            "No 2010 or regional-host payload was found in this pass; such a host would require separate host/time labeling before reuse as a 2008 US asset.",
        ],
    }
    (AUDIT_DIR / "audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"targets": len(targets), "active_payload_records": len(payload_records), "payload_files_checked": len(payload_records), "payload_bytes_checked": payload_bytes, "audit": rel(AUDIT_DIR / 'audit.json')}, ensure_ascii=False))


if __name__ == "__main__":
    main()
