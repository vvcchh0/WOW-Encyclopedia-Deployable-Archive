"""Bounded offline digest-reuse audit for the current v38 site.

No network, replay, copying, map generation, or publication is performed.
Source maps and the Source15 build manifest are deliberately not read.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None

ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = Path(__file__).resolve().parent
LEDGER = ROOT / "research/continuous-recovery-20261019/local-audit/resource-frontier-v33-r2/resource-frontier-candidates.json"
V38_ROOT = ROOT / ".scratch/pages-resources-20261019-v38"
PROVENANCE = V38_ROOT / "export-provenance.json"
V38_GATE = ROOT / "research/continuous-recovery-20261019/publication/root-v38-export-go.json"
ACCEPTED = ROOT / "research/continuous-recovery-20261020/publication/root-digest-reuse-source-acceptance.json"
CDX_DIR = ROOT / "research/site-recovery-2008/prefix-cdx"
ANCHOR = "20080512210044"
CUTOFF = "20101207235959"
HARD_STOP = datetime(2026, 10, 20, 12, 15, tzinfo=timezone.utc)
MAX_SECONDS = 20 * 60
MAX_NEW = 64
META_LIMIT = 64 * 1024 * 1024
IMAGE_LIMIT = 1024 * 1024 * 1024
IMAGE_FILES_LIMIT = 7200
IMAGE_FILE_LIMIT = 8 * 1024 * 1024

COMMENT_ONLY = {
    "http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/ss01.jpg",
    "http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/ss02.jpg",
    "http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/ss06.jpg",
    "http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/ss05.jpg",
    "http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/ss04.jpg",
    "http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/ss07.jpg",
}
EXPRESSION_MARKERS = ("@", "{" + "$", "{{", "}}", "<%", "%7b", "%7d", "javascript:")
RASTER_MIMES = {
    "image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp",
    "image/bmp", "image/tiff", "image/x-icon",
}


class MetadataBudgetExceeded(RuntimeError):
    pass


class MetadataBudget:
    def __init__(self) -> None:
        self.total = 0
        self.events: list[dict] = []

    def read(self, path: Path, purpose: str) -> bytes:
        data = path.read_bytes()
        self.total += len(data)
        self.events.append({
            "path": path.relative_to(ROOT).as_posix(),
            "purpose": purpose,
            "bytes": len(data),
            "cumulative_bytes": self.total,
        })
        if self.total > META_LIMIT:
            raise MetadataBudgetExceeded(
                f"metadata budget exceeded: {self.total} > {META_LIMIT}"
            )
        return data


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize(value: str) -> str:
    parts = urlsplit(str(value).strip())
    scheme = parts.scheme.lower()
    host = (parts.hostname or "").lower()
    if not scheme or not host:
        return str(value).strip()
    port = parts.port
    if port is not None and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        host = f"{host}:{port}"
    return urlunsplit((scheme, host, parts.path or "/", parts.query, ""))


def load_json(path: Path, budget: MetadataBudget, purpose: str) -> tuple[object, dict]:
    raw = budget.read(path, purpose)
    return json.loads(raw), {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(raw),
        "sha256": sha256(raw),
    }


def route(url: str) -> dict:
    rel = urlsplit(url).path.lstrip("/")
    path = V38_ROOT / rel
    return {
        "relative_path": rel,
        "exists": path.is_file(),
        "bytes": path.stat().st_size if path.is_file() else None,
    }


def expression(url: str) -> bool:
    low = url.lower()
    return any(token.lower() in low for token in EXPRESSION_MARKERS)


def source_files(row: dict) -> list[str]:
    raw: list[str] = []
    raw += [
        m.get("output_file")
        for m in row.get("markers", [])
        if isinstance(m, dict) and isinstance(m.get("output_file"), str)
    ]
    raw += [
        c.get("source_file")
        for c in row.get("source_context", [])
        if isinstance(c, dict) and isinstance(c.get("source_file"), str)
    ]
    result: list[str] = []
    for value in raw:
        value = value.replace("\\", "/")
        match = re.search(r"pages-resources-[^/]+-v\d+/(.+)$", value)
        if not match:
            match = re.search(r"offline-navigation-[^/]+/site/(.+)$", value)
        if match:
            rel = (V38_ROOT / match.group(1)).relative_to(ROOT).as_posix()
            if rel not in result:
                result.append(rel)
    return result


def build_targets(ledger: dict, accepted: dict) -> tuple[dict[str, dict], dict]:
    accepted_urls = {
        normalize(row["target_original_url"])
        for row in accepted.get("routes", [])
        if isinstance(row, dict) and row.get("target_original_url")
    }
    comment_urls = {normalize(x) for x in COMMENT_ONLY}
    counts = Counter()
    states = Counter()
    targets: dict[str, dict] = {}
    for index, item in enumerate(ledger.get("ledger", [])):
        states[item.get("state", "missing_state")] += 1
        if item.get("state") != "uncovered":
            counts["not_uncovered"] += 1
            continue
        if item.get("is_dynamic"):
            counts["dynamic_excluded"] += 1
            continue
        counts["static_uncovered"] += 1
        url = item.get("requested_url")
        if not isinstance(url, str) or not url:
            counts["missing_url"] += 1
            continue
        norm = normalize(url)
        if norm in comment_urls:
            counts["comment_only_excluded"] += 1
            continue
        if expression(url):
            counts["expression_excluded"] += 1
            continue
        current = route(url)
        if current["exists"]:
            counts["already_available_excluded"] += 1
            continue
        if norm in accepted_urls:
            counts["accepted_digest_routes_excluded"] += 1
            continue
        targets[norm] = {
            "requested_url": url,
            "normalized_url": norm,
            "ledger_index": index,
            "is_news": bool(item.get("is_news")),
            "route": current,
            "source_files": source_files(item),
            "marker_count": item.get("marker_count"),
        }
    counts["target_count"] = len(targets)
    return targets, {
        "ledger_rows": len(ledger.get("ledger", [])),
        "state_counts": dict(states),
        "counts": dict(counts),
        "accepted_routes": sorted(accepted_urls),
        "comment_only_urls": sorted(COMMENT_ONLY),
    }


def raster(mime: str) -> bool:
    value = mime.lower().split(";", 1)[0].strip()
    return value in RASTER_MIMES or (value.startswith("image/") and "svg" not in value)


def scan_cdx(
    targets: dict[str, dict],
    budget: MetadataBudget,
    start: float,
    stop: dict,
) -> tuple[dict[str, dict], dict]:
    rows: dict[str, list[dict]] = defaultdict(list)
    reports = []
    totals = Counter()
    paths = sorted(
        p for p in CDX_DIR.glob("*.json") if not p.name.endswith(".meta.json")
    )
    for path in paths:
        if stop.get("reason"):
            break
        if time.monotonic() - start >= MAX_SECONDS:
            stop["reason"] = "20_minute_limit"
            break
        if datetime.now(timezone.utc) >= HARD_STOP:
            stop["reason"] = "hard_stop_12:15Z"
            break
        raw = budget.read(path, "non_meta_cdx_json")
        file_hash = sha256(raw)
        report = {
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": len(raw),
            "sha256": file_hash,
            "rows": 0,
            "target_identity_rows": 0,
            "eligible_rows": 0,
            "prior_rows": 0,
            "later_rows": 0,
            "malformed_rows": 0,
        }
        try:
            decoded = json.loads(raw)
        except Exception:
            decoded = []
            report["malformed_rows"] += 1
        if not isinstance(decoded, list):
            decoded = []
            report["malformed_rows"] += 1
        for line, item in enumerate(decoded):
            if line == 0 and item == [
                "timestamp", "original", "statuscode", "digest", "length", "mimetype"
            ]:
                continue
            if not isinstance(item, list) or len(item) < 6:
                report["malformed_rows"] += 1
                continue
            report["rows"] += 1
            timestamp, original, status, digest, length, mime = [
                str(v) if v is not None else "" for v in item[:6]
            ]
            norm = normalize(original)
            if norm not in targets:
                continue
            report["target_identity_rows"] += 1
            if (
                not re.fullmatch(r"\d{14}", timestamp)
                or timestamp > CUTOFF
                or status != "200"
                or not raster(mime)
                or not digest
            ):
                continue
            report["eligible_rows"] += 1
            rows[norm].append({
                "timestamp": timestamp,
                "original": original,
                "statuscode": status,
                "digest": digest,
                "length": length,
                "mimetype": mime,
                "source_file": path.relative_to(ROOT).as_posix(),
                "source_file_sha256": file_hash,
                "source_line_number": line + 1,
            })
            report["prior_rows" if timestamp <= ANCHOR else "later_rows"] += 1
        reports.append(report)
        for key in ("rows", "target_identity_rows", "eligible_rows", "prior_rows", "later_rows"):
            totals[key] += report[key]
    chosen: dict[str, dict] = {}
    for norm, values in rows.items():
        prior = [x for x in values if x["timestamp"] <= ANCHOR]
        later = [x for x in values if x["timestamp"] > ANCHOR]
        if prior:
            row = max(
                prior,
                key=lambda x: (x["timestamp"], x["source_file"], x["source_line_number"]),
            )
            chosen[norm] = dict(row, selection_class="latest_prior_anchor")
        elif later:
            row = min(
                later,
                key=lambda x: (x["timestamp"], x["source_file"], x["source_line_number"]),
            )
            chosen[norm] = dict(row, selection_class="earliest_later_to_cutoff")
    totals.update({
        "files_discovered": len(paths),
        "files_scanned": len(reports),
        "target_urls_with_eligible_rows": len(rows),
        "target_urls_with_selected_rows": len(chosen),
        "target_urls_without_selected_rows": len(targets) - len(chosen),
        "unique_selected_digests": len({x["digest"] for x in chosen.values()}),
    })
    return chosen, {"totals": dict(totals), "reports": reports}


def sha1_base32(data: bytes) -> str:
    return base64.b32encode(hashlib.sha1(data).digest()).decode("ascii").rstrip("=")


def magic(data: bytes) -> str:
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


def pillow(data: bytes) -> dict:
    result = {
        "pillow_available": Image is not None,
        "pillow_valid": False,
        "all_frames_decoded": False,
        "image_frame_count": None,
        "image_format": None,
        "image_size": None,
        "image_mode": None,
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


def image_index(
    provenance: dict,
    start: float,
    stop: dict,
) -> tuple[dict[str, list[dict]], dict]:
    entries = [
        row for row in provenance.get("files", [])
        if row.get("kind") == "image"
        and str(row.get("mime", "")).lower().startswith("image/")
    ]
    index: dict[str, list[dict]] = defaultdict(list)
    stats = Counter()
    missing = []
    skipped = []
    for row in entries:
        if stop.get("reason"):
            break
        if time.monotonic() - start >= MAX_SECONDS:
            stop["reason"] = "20_minute_limit"
            break
        if datetime.now(timezone.utc) >= HARD_STOP:
            stop["reason"] = "hard_stop_12:15Z"
            break
        rel = str(row.get("output_path", ""))
        path = V38_ROOT / rel
        if not path.is_file():
            missing.append(rel)
            continue
        size = path.stat().st_size
        if size > IMAGE_FILE_LIMIT:
            skipped.append({"path": rel, "reason": "over_8MiB", "bytes": size})
            continue
        if (
            stats["files_read"] >= IMAGE_FILES_LIMIT
            or stats["image_bytes_read"] + size > IMAGE_LIMIT
        ):
            skipped.append({"path": rel, "reason": "image_budget", "bytes": size})
            continue
        data = path.read_bytes()
        stats["files_read"] += 1
        stats["image_bytes_read"] += len(data)
        stats["max_file_bytes"] = max(stats["max_file_bytes"], len(data))
        digest = sha1_base32(data)
        index[digest].append({
            "output_path": rel,
            "local_path": path.relative_to(ROOT).as_posix(),
            "route": row.get("route"),
            "provenance_role": row.get("role"),
            "provenance_mime": row.get("mime"),
            "provenance_source_sha256": row.get("source_sha256"),
            "provenance_derived_sha256": row.get("derived_sha256"),
            "provenance_source_length": row.get("source_length"),
            "provenance_derived_length": row.get("derived_length"),
            "provenance_source_offline_path": row.get("source_offline_path"),
            "provenance_source_url": row.get("source_url"),
            "provenance_original_url": row.get("original_url"),
            "provenance_actual_capture_timestamp": row.get("actual_capture_timestamp"),
            "provenance_capture_timestamp": row.get("capture_timestamp"),
            "computed_sha1_base32": digest,
            "actual_sha256": hashlib.sha256(data).hexdigest(),
            "actual_length": len(data),
            "magic_mime": magic(data),
            **pillow(data),
        })
    stats.update({
        "provenance_image_entries": len(entries),
        "missing_files": len(missing),
        "skipped_files": len(skipped),
        "unique_sha1_digests": len(index),
        "sha1_collision_groups": sum(1 for v in index.values() if len(v) > 1),
        "one_pass_payload_reads": True,
        "budget_image_bytes": IMAGE_LIMIT,
        "budget_image_files": IMAGE_FILES_LIMIT,
        "budget_single_file_bytes": IMAGE_FILE_LIMIT,
    })
    stats["missing_sample"] = missing[:20]
    stats["skipped_sample"] = skipped[:20]
    return index, dict(stats)


def active_refs(target: dict, budget: MetadataBudget) -> dict:
    path_part = urlsplit(target["requested_url"]).path.lstrip("/")
    encoded_url = quote(target["requested_url"], safe="")
    encoded_path = quote("/" + path_part, safe="/")
    files = []
    literal = img = style = css = markers = 0
    for rel in target.get("source_files", []):
        path = ROOT / rel
        if not path.is_file() or rel in files:
            continue
        text = budget.read(
            path, "active_v38_img_style_reference"
        ).decode("utf-8", errors="replace")
        files.append(rel)
        literal += text.count(path_part)
        img += len(re.findall(
            r"(?is)<(?:img|source|input)\b[^>]*(?:src|data-src)\s*=\s*['\"][^'\"]*"
            + re.escape(path_part), text
        ))
        style += len(re.findall(
            r"(?is)\bstyle\s*=\s*['\"][^'\"]*" + re.escape(path_part), text
        ))
        css += len(re.findall(
            r"(?is)url\(\s*['\"]?[^)]*" + re.escape(path_part), text
        ))
        markers += text.count(encoded_url) + text.count(encoded_path)
    return {
        "files_examined": files,
        "files_examined_count": len(files),
        "literal_path_hits": literal,
        "active_img_refs": img,
        "active_style_refs": style,
        "active_css_url_refs": css,
        "missing_marker_hits": markers,
        "active_ref_found": bool(img or style or css),
        "source_files_resolved": bool(files),
    }


def assess(
    targets: dict[str, dict],
    chosen: dict[str, dict],
    index: dict[str, list[dict]],
    budget: MetadataBudget,
    start: float,
    stop: dict,
) -> tuple[list[dict], dict, list[dict]]:
    results = []
    candidates = []
    counts = Counter()
    ref_cache = {}
    for norm, target in targets.items():
        if stop.get("reason"):
            break
        if time.monotonic() - start >= MAX_SECONDS:
            stop["reason"] = "20_minute_limit"
            break
        if datetime.now(timezone.utc) >= HARD_STOP:
            stop["reason"] = "hard_stop_12:15Z"
            break
        cdx = chosen.get(norm)
        if not cdx:
            counts["no_cdx_match"] += 1
            continue
        payloads = index.get(cdx["digest"], [])
        if not payloads:
            counts["cdx_digest_not_in_current_v38"] += 1
            continue
        ref_cache.setdefault(norm, active_refs(target, budget))
        refs = ref_cache[norm]
        for payload in payloads:
            source_url = payload.get("provenance_source_url") or payload.get("provenance_original_url")
            capture = payload.get("provenance_actual_capture_timestamp") or payload.get("provenance_capture_timestamp")
            chain = {
                "source_url_present": bool(source_url),
                "capture_timestamp_present": bool(capture),
                "source_chain_present": bool(source_url and capture),
                "source_url": source_url,
                "capture_timestamp": capture,
            }
            if not chain["source_chain_present"]:
                status = "pending_source_chain"
            elif not refs["active_ref_found"]:
                status = "pending_active_reference"
            else:
                status = "new_reuse_candidate"
            counts[status] += 1
            result = {
                "status": status,
                "target_url": target["requested_url"],
                "target_normalized_url": norm,
                "target_ledger_index": target["ledger_index"],
                "target_route": target["route"],
                "target_is_news": target["is_news"],
                "cdx_evidence": cdx,
                "reuse_payload": payload,
                "active_v38_reference_evidence": refs,
                "source_chain_evidence": chain,
                "same_bytes_proof": {
                    "cdx_digest": cdx["digest"],
                    "computed_sha1_base32": payload["computed_sha1_base32"],
                    "sha1_equal": payload["computed_sha1_base32"] == cdx["digest"],
                    "local_sha256": payload["actual_sha256"],
                    "local_length": payload["actual_length"],
                    "cdx_length": cdx["length"],
                    "pillow_valid": payload["pillow_valid"],
                    "all_frames_decoded": payload["all_frames_decoded"],
                },
            }
            results.append(result)
            if status == "new_reuse_candidate":
                candidates.append(result)
                if len(candidates) >= MAX_NEW:
                    stop["reason"] = "64_new_matches"
                    break
        if stop.get("reason"):
            break
    return results, dict(counts), candidates


def main() -> int:
    start = time.monotonic()
    generated = now_utc()
    stop: dict = {"reason": None}
    budget = MetadataBudget()
    runner = budget.read(Path(__file__), "runner_hash")
    inputs = []
    targets: dict[str, dict] = {}
    target_report: dict = {}
    chosen: dict[str, dict] = {}
    cdx_report = {"totals": {}, "reports": []}
    image_report: dict = {}
    results: list[dict] = []
    by_status: dict = {}
    candidates: list[dict] = []
    try:
        ledger, rec = load_json(LEDGER, budget, "static_target_ledger")
        inputs.append(rec)
        provenance, rec = load_json(PROVENANCE, budget, "current_v38_export_provenance")
        inputs.append(rec)
        _gate, rec = load_json(V38_GATE, budget, "current_v38_export_gate")
        inputs.append(rec)
        accepted, rec = load_json(ACCEPTED, budget, "accepted_two_digest_routes")
        inputs.append(rec)
        targets, target_report = build_targets(ledger, accepted)
        chosen, cdx_report = scan_cdx(targets, budget, start, stop)
        index, image_report = image_index(provenance, start, stop)
        results, by_status, candidates = assess(
            targets, chosen, index, budget, start, stop
        )
        if not stop.get("reason"):
            stop["reason"] = "completed"
    except MetadataBudgetExceeded as exc:
        stop["reason"] = "metadata_64MiB_limit"
        stop["error"] = str(exc)
    elapsed = time.monotonic() - start
    audit = {
        "schema": "wow-recovery.local-audit.digest-reuse-expanded.v2",
        "status": stop["reason"],
        "generated_utc": generated,
        "elapsed_seconds": elapsed,
        "stop": stop,
        "network_requests": 0,
        "network_performed": False,
        "runner": {
            "path": Path(__file__).relative_to(ROOT).as_posix(),
            "sha256": sha256(runner),
        },
        "inputs": inputs,
        "metadata_budget": {
            "limit_bytes": META_LIMIT,
            "bytes_read": budget.total,
            "within_limit": budget.total <= META_LIMIT,
            "read_events": budget.events,
        },
        "coverage": {
            "target_report": target_report,
            "current_v38_provenance": PROVENANCE.relative_to(ROOT).as_posix(),
            "source_maps_read": False,
            "source15_manifest_read": False,
        },
        "cdx": cdx_report,
        "image_scan": image_report,
        "match_results": {
            "total_assessments": len(results),
            "by_status": by_status,
            "selected_target_count": len(chosen),
        },
        "assessments": results,
        "candidates": candidates,
        "remaining": {
            "targets_not_selected_cdx": max(0, len(targets) - len(chosen)),
            "status_counts": by_status,
            "pending_source_chain": by_status.get("pending_source_chain", 0),
            "no_cdx_match": by_status.get("no_cdx_match", 0),
            "cdx_digest_not_in_current_v38": by_status.get(
                "cdx_digest_not_in_current_v38", 0
            ),
            "new_reuse_candidates": len(candidates),
        },
        "deviations": [
            "Corrected the prepared two-CDX/128MiB procedure to all non-meta CDX JSON files and a cumulative 64MiB metadata budget.",
            "Queue/tail and source-map inputs were omitted; this continuation is ledger-wide and source maps are outside the allowed metadata read.",
            "No payload was copied and no public map was generated.",
        ],
        "unknowns": [
            "Unscanned source maps and the Source15 build manifest are not absence evidence.",
            "pending_source_chain is not a negative result; root may read Source15 once afterward.",
            "A CDX row is metadata evidence only; no new payload download was performed.",
        ],
    }
    audit_path = OUT_DIR / "audit.json"
    audit_path.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    audit_hash = sha256(audit_path.read_bytes())
    readme_lines = [
        "Expanded local digest reuse audit",
        "",
        "Bounded offline read-only comparison. Every non-meta JSON CDX file is scanned against uncovered non-dynamic literal static ledger targets. No network, replay, copying, map generation, or publication.",
        f"Generated UTC: {generated}",
        f"Runner SHA256: {audit['runner']['sha256']}",
        f"Targets after exclusions: {target_report.get('counts', {}).get('target_count')}",
        f"CDX files/rows/eligible/selected: {cdx_report.get('totals', {}).get('files_scanned')}/{cdx_report.get('totals', {}).get('rows')}/{cdx_report.get('totals', {}).get('eligible_rows')}/{cdx_report.get('totals', {}).get('target_urls_with_selected_rows')}",
        f"Image one-pass files/bytes: {image_report.get('files_read')}/{image_report.get('image_bytes_read')}",
        f"Assessments/statuses: {len(results)}/{json.dumps(by_status, sort_keys=True)}",
        f"Metadata bytes: {budget.total}/{META_LIMIT}; source maps and Source15 manifest read: false",
        "Missing source URL or capture chain remains pending_source_chain.",
        f"Audit SHA256: {audit_hash}",
        "",
    ]
    (OUT_DIR / "README.md").write_text("\n".join(readme_lines), encoding="utf-8")
    print(json.dumps({
        "audit": audit_path.relative_to(ROOT).as_posix(),
        "audit_sha256": audit_hash,
        "readme": (OUT_DIR / "README.md").relative_to(ROOT).as_posix(),
        "readme_sha256": sha256((OUT_DIR / "README.md").read_bytes()),
        "status": stop["reason"],
        "elapsed_seconds": elapsed,
        "metadata_bytes_read": budget.total,
        "cdx_files": cdx_report.get("totals", {}).get("files_scanned"),
        "cdx_rows": cdx_report.get("totals", {}).get("rows"),
        "targets": target_report.get("counts", {}).get("target_count"),
        "image_files_read": image_report.get("files_read"),
        "image_bytes_read": image_report.get("image_bytes_read"),
        "assessments": len(results),
        "candidates": len(candidates),
        "by_status": by_status,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
