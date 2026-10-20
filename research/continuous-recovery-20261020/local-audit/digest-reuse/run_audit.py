"""Bounded, offline CDX-digest to v38-payload reuse audit.

This script only reads frozen ledgers, two local prefix-CDX responses, the v38
export provenance, and the source maps listed by the frozen v38 export gate.
It never performs a network request, extracts an archive, or changes a
production/export file.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import mimetypes
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

try:
    from PIL import Image
except Exception:  # pragma: no cover - recorded in the audit if unavailable
    Image = None


ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = Path(__file__).resolve().parent
ANCHOR = "20080512210044"
MAX_IMAGE_BYTES = 1_073_741_824
MAX_IMAGE_FILES = 7_200
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_METADATA_BYTES = 128 * 1024 * 1024

R2 = ROOT / "research/continuous-recovery-20261019/local-audit/resource-frontier-v33-r2/resource-frontier-candidates.json"
QUEUE = ROOT / "research/continuous-recovery-20261020/local-audit/recovery-queue.json"
TAIL_QUEUE = ROOT / "research/continuous-recovery-20261020/local-audit/news-extension-141-160.json"
PROVENANCE = ROOT / ".scratch/local bundle smoke 20261019 v38/site/export-provenance.json"
V38_ROOT = ROOT / ".scratch/pages-resources-20261019-v38"
V38_ALT_ROOT = ROOT / ".scratch/local bundle smoke 20261019 v38/site"
V38_GATE = ROOT / "research/continuous-recovery-20261019/publication/root-v38-export-go.json"
ACCEPTED_CAPTURE_MAP = ROOT / "research/offline-2008/full-recovery/round-105-final-full-capture-map-validation.json"
CDX_PATHS = [
    ROOT / "research/site-recovery-2008/prefix-cdx/003-08c5d92edd079b20.json",
    ROOT / "research/site-recovery-2008/prefix-cdx/005-e77c67293c435d69.json",
]

COMMENT_ONLY = {
    "http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/ss01.jpg",
    "http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/ss02.jpg",
    "http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/ss06.jpg",
    "http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/ss05.jpg",
    "http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/ss04.jpg",
    "http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/ss07.jpg",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def input_record(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def load_json(path: Path):
    return json.loads(path.read_bytes())


def normalize_url(value: str) -> str:
    """Normalize only URL identity details allowed by the queue contract."""
    parts = urlsplit(str(value).strip())
    scheme = parts.scheme.lower()
    host = (parts.hostname or "").lower()
    if not scheme or not host:
        return str(value).strip()
    port = parts.port
    if port is not None and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        host = f"{host}:{port}"
    path = parts.path or "/"
    return urlunsplit((scheme, host, path, parts.query, ""))


def url_host(value: str) -> str:
    return (urlsplit(value).hostname or "").lower()


def digest_sha1_base32(data: bytes) -> str:
    return base64.b32encode(hashlib.sha1(data).digest()).decode("ascii").rstrip("=")


def sha1_file_base32(path: Path) -> tuple[str, int]:
    h = hashlib.sha1()
    length = 0
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            length += len(block)
            h.update(block)
    return base64.b32encode(h.digest()).decode("ascii").rstrip("="), length


def magic_mime(data: bytes) -> str:
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"
    if data.startswith(b"BM"):
        return "image/bmp"
    if data.startswith(b"II*\x00") or data.startswith(b"MM\x00*"):
        return "image/tiff"
    return "application/octet-stream"


def full_validate(path: Path, expected_digest: str) -> dict:
    data = path.read_bytes()
    sha1 = digest_sha1_base32(data)
    sha256 = hashlib.sha256(data).hexdigest()
    result = {
        "path": path.relative_to(ROOT).as_posix(),
        "length": len(data),
        "sha256": sha256,
        "computed_sha1_base32": sha1,
        "sha1_equals_cdx": sha1 == expected_digest,
        "magic_mime": magic_mime(data),
        "pillow_available": Image is not None,
        "pillow_valid": False,
        "image_format": None,
        "image_frame_count": None,
        "image_size": None,
        "image_mode": None,
        "all_frames_decoded": False,
    }
    if Image is None:
        return result
    frames = 0
    try:
        with Image.open(io.BytesIO(data)) as image:
            result["image_format"] = image.format
            result["image_size"] = list(image.size)
            result["image_mode"] = image.mode
            while True:
                image.seek(frames)
                image.copy().load()
                frames += 1
    except EOFError:
        result["image_frame_count"] = frames
        result["pillow_valid"] = frames > 0
        result["all_frames_decoded"] = frames > 0
    except Exception as exc:
        result["pillow_error"] = f"{type(exc).__name__}: {exc}"
    return result


def route_status(url: str) -> dict:
    rel = urlsplit(url).path.lstrip("/")
    primary = V38_ROOT / rel
    alternate = V38_ALT_ROOT / rel
    return {
        "relative_path": rel,
        "v38_primary_root": V38_ROOT.relative_to(ROOT).as_posix(),
        "v38_primary_exists": primary.is_file(),
        "v38_primary_bytes": primary.stat().st_size if primary.is_file() else None,
        "v38_alternate_exists": alternate.is_file(),
        "v38_alternate_bytes": alternate.stat().st_size if alternate.is_file() else None,
    }


def compact_source_ref(row: dict, source_path: Path, map_path: Path) -> dict:
    url = row.get("original") or row.get("logical_url") or row.get("source_url") or row.get("url")
    paths = []
    for key in ("local_path", "public_copy_path", "source_local_path_prior", "private_payload_path", "path"):
        value = row.get(key)
        if isinstance(value, str) and value and value not in paths:
            paths.append(value)
    return {
        "source_url": url,
        "source_map": map_path.relative_to(ROOT).as_posix(),
        "source_map_row_path": source_path,
        "payload_path": paths,
        "sha256": row.get("sha256") or row.get("actual_sha256") or row.get("expected_sha256"),
        "source_relationship": row.get("source_relationship"),
        "actual_timestamp": row.get("actual_timestamp") or row.get("actual_capture_timestamp"),
        "indexed_capture_timestamp": row.get("indexed_capture_timestamp"),
        "mime": row.get("mime"),
        "length": row.get("length") or row.get("actual_length") or row.get("expected_length"),
        "zip_provenance": row.get("zip_provenance"),
        "zip_file": row.get("zip_file"),
        "zip_entry": row.get("zip_entry"),
        "content": row.get("content"),
    }


def collect_source_refs(obj, map_path: Path, path: str = "root") -> list[dict]:
    """Find accepted map rows that bind a URL and payload SHA256."""
    found: list[dict] = []
    if isinstance(obj, dict):
        sha = obj.get("sha256") or obj.get("actual_sha256") or obj.get("expected_sha256")
        url = obj.get("original") or obj.get("logical_url") or obj.get("source_url") or obj.get("url")
        if isinstance(sha, str) and len(sha) == 64 and isinstance(url, str) and url:
            found.append(compact_source_ref(obj, path, map_path))
        for key, value in obj.items():
            found.extend(collect_source_refs(value, map_path, f"{path}.{key}"))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            found.extend(collect_source_refs(value, map_path, f"{path}[{idx}]"))
    return found


def load_gate_source_refs(gate: dict, input_hashes: list[dict]) -> tuple[dict[str, list[dict]], list[dict]]:
    refs: dict[str, list[dict]] = defaultdict(list)
    maps = []
    paths = [ROOT / x for key in ("primary_maps", "supplement_maps") for x in gate.get(key, [])]
    for key in ("guide_preview_map", "guide_image_collection_map"):
        value = gate.get(key)
        if value:
            paths.append(ROOT / value)
    seen = set()
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        if not path.is_file():
            maps.append({"path": path.relative_to(ROOT).as_posix(), "missing": True})
            continue
        input_hashes.append(input_record(path))
        data = load_json(path)
        rows = collect_source_refs(data, path)
        unique = {}
        for row in rows:
            payload_paths = row.get("payload_path") or []
            key = (row.get("sha256"), row.get("source_url"), payload_paths[0] if payload_paths else None)
            unique[key] = row
        for row in unique.values():
            refs[row["sha256"]].append(row)
        maps.append({"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "rows_with_url_sha256": len(unique)})
    return refs, maps


def load_additional_capture_refs(input_hashes: list[dict]) -> tuple[dict[str, list[dict]], dict]:
    """Load one explicit accepted capture index; never open its ZIP members."""
    path = ACCEPTED_CAPTURE_MAP
    input_hashes.append(input_record(path))
    data = load_json(path)
    rows = collect_source_refs(data, path)
    unique = {}
    for row in rows:
        payload_paths = row.get("payload_path") or []
        key = (row.get("sha256"), row.get("source_url"), payload_paths[0] if payload_paths else None)
        unique[key] = row
    refs: dict[str, list[dict]] = defaultdict(list)
    for row in unique.values():
        refs[row["sha256"]].append(row)
    return refs, {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "rows_with_url_sha256": len(unique),
        "zip_members_read": False,
    }


def build_targets(r2: dict, queue: dict, tail: dict, r2_hash: str, queue_hash: str, tail_hash: str) -> tuple[dict[str, dict], dict]:
    targets: dict[str, dict] = {}
    primary_items = list(queue.get("b_news_extension_priority", {}).get("items", []))
    primary_items += list(tail.get("items", []))
    primary_items.sort(key=lambda row: int(row.get("candidate_rank", 10**9)))
    for item in primary_items:
        url = item["requested_url"]
        norm = normalize_url(url)
        if norm in COMMENT_ONLY:
            continue
        targets[norm] = {
            "requested_url": url,
            "group": "news121-160",
            "candidate_rank": item.get("candidate_rank"),
            "priority_score": item.get("priority_score"),
            "source_class": item.get("source_class"),
            "source_reference": item.get("source_reference"),
            "v38_local": item.get("v38_local"),
            "direct_route": route_status(url),
        }

    excluded = Counter()
    expansion_rows = 0
    for idx, row in enumerate(r2.get("ledger", [])):
        if row.get("state") != "uncovered":
            excluded["non_uncovered_state"] += 1
            continue
        if row.get("is_dynamic"):
            excluded["dynamic"] += 1
            continue
        url = row.get("requested_url")
        if not isinstance(url, str):
            excluded["no_url"] += 1
            continue
        if url_host(url) != "www.worldofwarcraft.com":
            excluded["other_host"] += 1
            continue
        if normalize_url(url) in {normalize_url(x) for x in COMMENT_ONLY}:
            excluded["comment_only"] += 1
            continue
        low_path = urlsplit(url).path.lower()
        if "karazhan" in low_path or "blacktemple" in low_path or "black-temple" in low_path:
            excluded["kara_bt_park"] += 1
            continue
        norm = normalize_url(url)
        expansion_rows += 1
        if norm in targets:
            continue
        targets[norm] = {
            "requested_url": url,
            "group": "r2-www-static-news-expansion",
            "candidate_rank": None,
            "priority_score": None,
            "source_class": "r2_uncovered_missing_marker",
            "source_reference": {
                "ledger_path": R2.relative_to(ROOT).as_posix(),
                "ledger_sha256": r2_hash,
                "ledger_index": idx,
                "state": row.get("state"),
                "marker_count": row.get("marker_count"),
                "markers": row.get("markers"),
                "source_context": row.get("source_context"),
                "historical_execution_evidence": row.get("historical_execution_evidence"),
                "historical_plan_or_queue_evidence": row.get("historical_plan_or_queue_evidence"),
                "next_step": row.get("next_step"),
            },
            "v38_local": None,
            "direct_route": route_status(url),
        }
    # Primary is always first; expansion is deterministic and URL-stable.
    ordered = sorted(targets.items(), key=lambda item: (0 if item[1]["group"] == "news121-160" else 1, item[1].get("candidate_rank") or 10**9, item[0]))
    return dict(ordered), {
        "primary_items_loaded": len(primary_items),
        "primary_targets": sum(v["group"] == "news121-160" for v in targets.values()),
        "expansion_rows_considered": expansion_rows,
        "expansion_targets": sum(v["group"] == "r2-www-static-news-expansion" for v in targets.values()),
        "r2_filter_exclusions": dict(excluded),
        "comment_only_excluded": sorted(COMMENT_ONLY),
        "input_queue_sha256": queue_hash,
        "input_tail_sha256": tail_hash,
    }


def scan_cdx(targets: dict[str, dict], input_hashes: list[dict]) -> tuple[dict[str, list[dict]], list[dict], dict]:
    wanted = set(targets)
    hits: dict[str, list[dict]] = defaultdict(list)
    reports = []
    for path in CDX_PATHS:
        source_hash = sha256_file(path)
        size = path.stat().st_size
        input_hashes.append({"path": path.relative_to(ROOT).as_posix(), "bytes": size, "sha256": source_hash})
        total_rows = 0
        identity_rows = 0
        eligible_rows = 0
        parse_errors = 0
        try:
            rows = json.loads(path.read_bytes())
        except Exception:
            rows = []
            parse_errors += 1
        if not isinstance(rows, list):
            rows = []
            parse_errors += 1
        for row_index, row in enumerate(rows):
            # The frozen prefix files are one JSON row per physical line,
            # preceded by the header and followed by a closing bracket.
            line_no = row_index + 1
            if row_index == 0 and row == ["timestamp", "original", "statuscode", "digest", "length", "mimetype"]:
                continue
            if not isinstance(row, list) or len(row) < 6:
                parse_errors += 1
                continue
            total_rows += 1
            timestamp, original, status, digest, length, mime = [str(x) if x is not None else "" for x in row[:6]]
            norm = normalize_url(original)
            if norm not in wanted:
                continue
            identity_rows += 1
            if timestamp <= ANCHOR and status == "200" and mime.lower().startswith("image/") and digest:
                eligible_rows += 1
                hits[norm].append({
                    "source_file": path.relative_to(ROOT).as_posix(),
                    "source_file_sha256": source_hash,
                    "source_line_number": line_no,
                    "timestamp": timestamp,
                    "original": original,
                    "statuscode": status,
                    "digest": digest,
                    "length": length,
                    "mimetype": mime,
                    "normalized_identity": norm,
                })
        reports.append({
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": size,
            "sha256": source_hash,
            "rows": total_rows,
            "target_identity_rows": identity_rows,
            "eligible_rows": eligible_rows,
            "parse_errors": parse_errors,
        })
    totals = {
        "files": len(reports),
        "rows": sum(x["rows"] for x in reports),
        "target_identity_rows": sum(x["target_identity_rows"] for x in reports),
        "eligible_rows": sum(x["eligible_rows"] for x in reports),
        "urls_with_eligible_rows": len(hits),
        "unique_eligible_digests": len({row["digest"] for rows in hits.values() for row in rows}),
    }
    return hits, reports, totals


def build_sha1_index(provenance: dict, input_hashes: list[dict]) -> tuple[dict[str, list[dict]], dict]:
    entries = [row for row in provenance.get("files", []) if row.get("kind") == "image" and str(row.get("mime", "")).lower().startswith("image/")]
    index: dict[str, list[dict]] = defaultdict(list)
    missing = []
    skipped = []
    bytes_read = 0
    files_read = 0
    max_file = 0
    for row in entries:
        rel = str(row.get("output_path", ""))
        path = V38_ROOT / rel
        if not path.is_file():
            alternate = V38_ALT_ROOT / rel
            if alternate.is_file():
                path = alternate
            else:
                missing.append(rel)
                continue
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            skipped.append({"path": rel, "reason": "over_8MiB", "bytes": size})
            continue
        if files_read >= MAX_IMAGE_FILES or bytes_read + size > MAX_IMAGE_BYTES:
            skipped.append({"path": rel, "reason": "budget", "bytes": size})
            continue
        digest, actual_length = sha1_file_base32(path)
        files_read += 1
        bytes_read += actual_length
        max_file = max(max_file, actual_length)
        index[digest].append({
            "output_path": rel,
            "local_path": path.relative_to(ROOT).as_posix(),
            "provenance_mime": row.get("mime"),
            "provenance_source_sha256": row.get("source_sha256"),
            "provenance_derived_sha256": row.get("derived_sha256"),
            "provenance_source_length": row.get("source_length"),
            "provenance_derived_length": row.get("derived_length"),
            "provenance_route": row.get("route"),
            "provenance_static_url": row.get("static_url"),
            "provenance_source_offline_path": row.get("source_offline_path"),
            "provenance_role": row.get("role"),
            "computed_sha1_base32": digest,
            "actual_length": actual_length,
        })
    return index, {
        "provenance_selected_image_entries": len(entries),
        "files_read": files_read,
        "missing_files": len(missing),
        "missing_sample": missing[:20],
        "skipped_files": len(skipped),
        "skipped_sample": skipped[:20],
        "image_bytes_read": bytes_read,
        "max_file_bytes": max_file,
        "unique_sha1_digests": len(index),
        "sha1_collision_groups": sum(1 for v in index.values() if len(v) > 1),
        "budget_image_bytes": MAX_IMAGE_BYTES,
        "budget_image_files": MAX_IMAGE_FILES,
        "budget_single_file_bytes": MAX_FILE_BYTES,
    }


def representative_cdx_rows(rows: list[dict]) -> list[dict]:
    by_digest: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_digest[row["digest"]].append(row)
    out = []
    for digest, group in sorted(by_digest.items()):
        representative = max(group, key=lambda row: row["timestamp"])
        item = dict(representative)
        item["same_digest_row_count"] = len(group)
        item["same_digest_source_lines"] = [row["source_line_number"] for row in group]
        out.append(item)
    return out


def assess_matches(targets: dict[str, dict], hits: dict[str, list[dict]], sha1_index: dict[str, list[dict]], source_refs: dict[str, list[dict]], image_budget: dict) -> tuple[list[dict], dict]:
    full_cache: dict[tuple[str, str], dict] = {}
    assessments = []
    counts = Counter()
    bytes_after_index = image_budget["image_bytes_read"]
    for norm, rows in hits.items():
        target = targets[norm]
        for cdx in representative_cdx_rows(rows):
            digest = cdx["digest"]
            payloads = sha1_index.get(digest, [])
            if not payloads:
                continue
            for payload in payloads:
                cache_key = (payload["local_path"], digest)
                if cache_key not in full_cache:
                    path = ROOT / payload["local_path"]
                    if bytes_after_index + path.stat().st_size > MAX_IMAGE_BYTES:
                        full_cache[cache_key] = {"validation_skipped": "image_byte_budget"}
                    else:
                        validation = full_validate(path, digest)
                        full_cache[cache_key] = validation
                        bytes_after_index += validation["length"]
                validation = full_cache[cache_key]
                accepted_refs = []
                for sha in (payload.get("provenance_derived_sha256"), payload.get("provenance_source_sha256")):
                    if sha:
                        accepted_refs.extend(source_refs.get(sha, []))
                dedup_refs = {}
                for ref in accepted_refs:
                    key = (ref.get("sha256"), ref.get("source_url"), ref.get("source_map"), ref.get("source_map_row_path"))
                    dedup_refs[key] = ref
                accepted_refs = list(dedup_refs.values())
                route = target["direct_route"]
                valid_image = bool(validation.get("sha1_equals_cdx") and validation.get("pillow_valid") and validation.get("all_frames_decoded") and validation.get("magic_mime", "").startswith("image/"))
                if validation.get("validation_skipped"):
                    status = "validation_budget_exhausted"
                elif not valid_image:
                    status = "invalid_or_unverified_payload"
                elif route.get("v38_primary_exists"):
                    status = "already_present_route"
                elif not accepted_refs:
                    status = "matched_payload_without_accepted_source_url"
                else:
                    status = "new_reuse_candidate"
                counts[status] += 1
                assessments.append({
                    "status": status,
                    "target_url": target["requested_url"],
                    "target_normalized_url": norm,
                    "target_group": target["group"],
                    "candidate_rank": target.get("candidate_rank"),
                    "target_source_reference": target.get("source_reference"),
                    "target_v38_local": target.get("v38_local"),
                    "target_route": route,
                    "cdx_evidence": cdx,
                    "reuse_payload": payload,
                    "reuse_payload_validation": validation,
                    "accepted_source_evidence": accepted_refs[:20],
                    "accepted_source_evidence_count": len(accepted_refs),
                    "same_bytes_proof": {
                        "cdx_digest": digest,
                        "computed_sha1_base32": validation.get("computed_sha1_base32"),
                        "sha1_equal": validation.get("sha1_equals_cdx"),
                        "local_payload_sha256": validation.get("sha256"),
                        "provenance_derived_sha256": payload.get("provenance_derived_sha256"),
                        "provenance_source_sha256": payload.get("provenance_source_sha256"),
                        "local_length": validation.get("length"),
                        "cdx_length": cdx.get("length"),
                    },
                })
    return assessments, {
        "total_assessments": len(assessments),
        "by_status": dict(counts),
        "image_bytes_read_including_full_validation": bytes_after_index,
        "image_budget_remaining": MAX_IMAGE_BYTES - bytes_after_index,
        "full_validations": len(full_cache),
    }


def write_readme(audit: dict) -> None:
    c = audit["coverage"]
    m = audit["match_results"]
    lines = [
        "# digest-reuse 本地专项",
        "",
        "本目录记录一次 0 网络、只读的本地 SHA1 复用审计。目标是把冻结历史 CDX 中的 exact original + HTTP 200 + 图片 MIME + 明确 digest，与 v38 当前已经存在的图片实体做字节级交叉匹配；命中只作为候选，不表示已经执行新的 CDX、Memento 或下载。",
        "",
        f"运行时间：`{audit['generated_utc']}`；网络请求：`{audit['network_requests']}`；CDX 时间上限：`{ANCHOR}`。",
        "",
        "输入边界：",
        "",
        f"- 首批 news121..160：{c['targets']['primary_targets']} 个；随后扩大到冻结 R2 ledger 中 host 为 `www.worldofwarcraft.com`、state=`uncovered`、非 dynamic 的静态/新闻 URL：{c['targets']['expansion_targets']} 个。六个 koreapvp comment-only URL 已排除。",
        f"- 读取两个 prefix-CDX：{c['cdx']['files']} 个文件、{c['cdx']['rows']} 行；其中目标 identity 行 {c['cdx']['target_identity_rows']}，符合时间窗/200/图片 MIME/有 digest 的行 {c['cdx']['eligible_rows']}。",
        f"- v38 provenance 选择了 {c['provenance']['provenance_selected_image_entries']} 个 `kind=image` 且 MIME 为 image/* 的实体，实际读 {c['provenance']['files_read']} 个，SHA1 首轮读取 {c['provenance']['image_bytes_read']} bytes；未读 75 MB build manifest，也没有解压 ZIP。",
        f"- v38 来源 URL 回溯使用冻结 v38 export gate 列出的 source-map 文件；这些 map 总体约 {c['source_maps']['total_bytes']} bytes，按 source SHA256 绑定 `original`/`logical_url` 与 local path。",
        "",
        "结果：",
        "",
        f"- digest 命中评估 {m['total_assessments']} 条；状态计数：`{json.dumps(m['by_status'], ensure_ascii=False, sort_keys=True)}`。",
        f"- 可直接交给 root 复核的 `new_reuse_candidate`：{len(audit['candidates'])} 条。每条保留目标原 URL、CDX 文件 SHA256/行号/日期/digest、复用 payload 路径、v38 provenance SHA256、已验收 source-map URL/路径，以及 computed SHA1/完整帧验证。",
        "- `audit.json` 中的 `matched_payload_without_accepted_source_url`、`invalid_or_unverified_payload`、`already_present_route` 只作覆盖记录，不作为可整合候选。",
        "",
        "复现命令：",
        "",
        "```powershell",
        "python -X utf8 research/continuous-recovery-20261020/local-audit/digest-reuse/run_audit.py",
        "```",
        "",
        "未知范围：只检查了指定的两个 prefix-CDX 响应；没有把未读的 CDX、raw/ZIP、75 MB build manifest 或网络状态当作 absence 证据。没有修改旧 ledger、Source15、accepted、v38 export 或生产映射。",
        "",
    ]
    (OUT_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    generated = utc_now()
    input_hashes: list[dict] = []
    for path in (R2, QUEUE, TAIL_QUEUE, PROVENANCE, V38_GATE):
        input_hashes.append(input_record(path))
    r2 = load_json(R2)
    queue = load_json(QUEUE)
    tail = load_json(TAIL_QUEUE)
    provenance = load_json(PROVENANCE)
    gate = load_json(V38_GATE)
    source_refs, source_maps = load_gate_source_refs(gate, input_hashes)
    additional_refs, additional_map = load_additional_capture_refs(input_hashes)
    for sha, rows in additional_refs.items():
        source_refs[sha].extend(rows)
    targets, target_report = build_targets(
        r2,
        queue,
        tail,
        next(x["sha256"] for x in input_hashes if x["path"] == R2.relative_to(ROOT).as_posix()),
        next(x["sha256"] for x in input_hashes if x["path"] == QUEUE.relative_to(ROOT).as_posix()),
        next(x["sha256"] for x in input_hashes if x["path"] == TAIL_QUEUE.relative_to(ROOT).as_posix()),
    )
    hits, cdx_reports, cdx_total = scan_cdx(targets, input_hashes)
    sha1_index, provenance_report = build_sha1_index(provenance, input_hashes)
    assessments, match_results = assess_matches(targets, hits, sha1_index, source_refs, provenance_report)
    candidates = [row for row in assessments if row["status"] == "new_reuse_candidate"]
    input_bytes = sum(row["bytes"] for row in input_hashes)
    source_map_bytes = sum(row.get("bytes", 0) for row in source_maps)
    coverage = {
        "targets": target_report,
        "cdx": {**cdx_total, "reports": cdx_reports},
        "provenance": provenance_report,
        "source_maps": {"files": len(source_maps) + 1, "total_bytes": source_map_bytes + additional_map["bytes"], "records_by_sha256": len(source_refs), "maps": source_maps, "additional_accepted_capture_map": additional_map},
        "metadata_bytes_hashed_or_loaded": input_bytes,
        "metadata_budget_bytes": MAX_METADATA_BYTES,
        "metadata_budget_ok": input_bytes <= MAX_METADATA_BYTES,
        "image_budget_ok": match_results["image_bytes_read_including_full_validation"] <= MAX_IMAGE_BYTES,
        "time_budget_minutes": 15,
    }
    audit = {
        "schema": "wow-recovery.local-audit.digest-reuse.v1",
        "generated_utc": generated,
        "network_requests": 0,
        "network_performed": False,
        "repository": {"root": str(ROOT), "expected_v38_head": "f84786d4820438213f0610df147fb78c3f0b2af9"},
        "contract": {
            "anchor_timestamp": ANCHOR,
            "url_identity": "exact URL after lowercasing scheme/host and removing explicit default :80/:443 only",
            "positive_cdx_row": "timestamp <= anchor, statuscode=200, image/* MIME, nonempty digest",
            "comment_only_excluded": sorted(COMMENT_ONLY),
            "source_map_policy": "v38 export gate primary/supplement maps only; source URL required for a new candidate",
            "raw_or_zip_scan": False,
            "build_manifest_75mb_read": False,
        },
        "inputs": input_hashes,
        "coverage": coverage,
        "match_results": match_results,
        "assessments": assessments,
        "candidates": candidates,
        "unknowns": [
            "Only the two specified local prefix-CDX responses were scanned; unscanned CDX responses are not absence evidence.",
            "No network request, Memento replay, or new download was performed.",
            "The 75 MiB source build-manifest and raw/ZIP payloads were intentionally not read or extracted.",
            "A payload without a frozen v38 source-map URL is retained as an assessment but excluded from candidates.",
        ],
    }
    (OUT_DIR / "audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_readme(audit)
    print(json.dumps({
        "audit": str((OUT_DIR / "audit.json").relative_to(ROOT)),
        "audit_sha256": sha256_file(OUT_DIR / "audit.json"),
        "readme": str((OUT_DIR / "README.md").relative_to(ROOT)),
        "readme_sha256": sha256_file(OUT_DIR / "README.md"),
        "target_count": len(targets),
        "cdx_eligible_rows": cdx_total["eligible_rows"],
        "provenance_files_read": provenance_report["files_read"],
        "image_bytes_read": match_results["image_bytes_read_including_full_validation"],
        "assessment_count": match_results["total_assessments"],
        "candidates": len(candidates),
        "by_status": match_results["by_status"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
