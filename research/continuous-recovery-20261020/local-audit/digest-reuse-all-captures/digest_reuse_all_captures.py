"""Bounded offline all-captures digest-reuse audit.

The audit reads CDX metadata and accepted local metadata only.  It does not
fetch, replay, copy, export, publish, read the Source15 manifest, or read
source maps.  Payload bytes are read only for a digest match that also has an
active v38 reference, with independent byte and Pillow checks.
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
ROUND105 = ROOT / "research/offline-2008/full-recovery/round-105-final-full-capture-map-validation.json"
V38_ROOT = ROOT / ".scratch/pages-resources-20261019-v38"
PROVENANCE = V38_ROOT / "export-provenance.json"
ACCEPTED = ROOT / "research/continuous-recovery-20261020/publication/root-digest-reuse-source-acceptance.json"
CDX_DIR = ROOT / "research/site-recovery-2008/prefix-cdx"
ANCHOR = "20080512210044"
CUTOFF = "20101207235959"
HARD_STOP = datetime(2026, 10, 20, 12, 28, tzinfo=timezone.utc)
MAX_SECONDS = 15 * 60
META_LIMIT = 64 * 1024 * 1024
PAYLOAD_LIMIT = 64 * 1024 * 1024
PAYLOAD_FILE_LIMIT = 32 * 1024 * 1024

COMMENT_ONLY = {
    "http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/ss01.jpg",
    "http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/ss02.jpg",
    "http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/ss04.jpg",
    "http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/ss05.jpg",
    "http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/ss06.jpg",
    "http://www.worldofwarcraft.com/news/images/04-09/pvp/koreapvp/ss07.jpg",
}
DORMANT_CSS_LEAD = "http://www.worldofwarcraft.com/contests/l70etc-musicvideo/images/flashbannerbg.jpg"
EXPRESSION_MARKERS = ("@", "{$", "{{", "}}", "<%", "%7b", "%7d", "javascript:")
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
            raise MetadataBudgetExceeded(f"metadata budget exceeded: {self.total} > {META_LIMIT}")
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


def expression(url: str) -> bool:
    low = url.lower()
    return any(token.lower() in low for token in EXPRESSION_MARKERS)


def source_files(row: dict) -> list[str]:
    raw: list[str] = []
    raw.extend(
        m.get("output_file")
        for m in row.get("markers", [])
        if isinstance(m, dict) and isinstance(m.get("output_file"), str)
    )
    raw.extend(
        c.get("source_file")
        for c in row.get("source_context", [])
        if isinstance(c, dict) and isinstance(c.get("source_file"), str)
    )
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
    dormant_url = normalize(DORMANT_CSS_LEAD)
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
        if norm == dormant_url:
            counts["dormant_css_lead_excluded"] += 1
            continue
        if expression(url):
            counts["expression_excluded"] += 1
            continue
        rel = urlsplit(url).path.lstrip("/")
        current = V38_ROOT / rel
        if current.is_file():
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
            "route": {"relative_path": rel, "exists": False},
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
        "dormant_css_lead": DORMANT_CSS_LEAD,
    }


def raster(mime: str) -> bool:
    value = mime.lower().split(";", 1)[0].strip()
    return value in RASTER_MIMES or (value.startswith("image/") and "svg" not in value)


def scan_cdx(targets: dict[str, dict], budget: MetadataBudget, started: float, stop: dict) -> tuple[dict[str, list[dict]], dict]:
    rows: dict[str, list[dict]] = defaultdict(list)
    reports = []
    totals = Counter()
    paths = sorted(p for p in CDX_DIR.glob("*.json") if not p.name.endswith(".meta.json"))
    for path in paths:
        if stop.get("reason"):
            break
        if time.monotonic() - started >= MAX_SECONDS:
            stop["reason"] = "15_minute_limit"
            break
        if datetime.now(timezone.utc) >= HARD_STOP:
            stop["reason"] = "hard_stop_12:28Z"
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
            if line == 0 and item == ["timestamp", "original", "statuscode", "digest", "length", "mimetype"]:
                continue
            if not isinstance(item, list) or len(item) < 6:
                report["malformed_rows"] += 1
                continue
            report["rows"] += 1
            timestamp, original, status, digest, length, mime = [str(v) if v is not None else "" for v in item[:6]]
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
            row = {
                "timestamp": timestamp,
                "original": original,
                "statuscode": status,
                "digest": digest.upper(),
                "length": length,
                "mimetype": mime,
                "source_file": path.relative_to(ROOT).as_posix(),
                "source_file_sha256": file_hash,
                "source_line_number": line + 1,
            }
            rows[norm].append(row)
            report["prior_rows" if timestamp <= ANCHOR else "later_rows"] += 1
        reports.append(report)
        for key in ("rows", "target_identity_rows", "eligible_rows", "prior_rows", "later_rows"):
            totals[key] += report[key]
    selected: dict[str, dict] = {}
    for norm, values in rows.items():
        ordered = sorted(
            values,
            key=lambda x: (0, -int(x["timestamp"])) if x["timestamp"] <= ANCHOR else (1, int(x["timestamp"])),
        )
        selected[norm] = dict(ordered[0], selection_class="latest_prior_anchor" if ordered[0]["timestamp"] <= ANCHOR else "earliest_later_to_cutoff")
    totals.update({
        "files_discovered": len(paths),
        "files_scanned": len(reports),
        "target_urls_with_eligible_rows": len(rows),
        "target_urls_with_selected_rows": len(selected),
        "target_urls_without_selected_rows": len(targets) - len(selected),
        "eligible_capture_rows_all_versions": sum(len(v) for v in rows.values()),
        "unique_eligible_digests": len({x["digest"] for values in rows.values() for x in values}),
    })
    return rows, {"totals": dict(totals), "reports": reports, "selected": selected}


def add_cache(cache: dict[str, list[dict]], digest_index: dict[str, list[dict]], record: dict) -> None:
    digest = str(record.get("cdx_digest") or "").upper()
    payload_sha = str(record.get("sha256") or "").lower()
    if not re.fullmatch(r"[A-Z2-7]+", digest) or not re.fullmatch(r"[0-9a-f]{64}", payload_sha):
        return
    compact = {
        "cdx_digest": digest,
        "sha256": payload_sha,
        "source_url": record.get("source_url"),
        "capture_timestamp": record.get("capture_timestamp"),
        "length": record.get("length"),
        "source": record.get("source"),
        "route": record.get("route"),
        "output_path": record.get("output_path"),
        "original_url": record.get("original_url"),
    }
    if compact not in cache[payload_sha]:
        cache[payload_sha].append(compact)
    if compact not in digest_index[digest]:
        digest_index[digest].append(compact)


def build_metadata_cache(round_data: dict, provenance: dict) -> tuple[dict[str, list[dict]], dict[str, list[dict]], dict]:
    cache: dict[str, list[dict]] = defaultdict(list)
    digest_index: dict[str, list[dict]] = defaultdict(list)
    stats = Counter()
    for mapping in round_data.get("maps", []):
        for item in mapping.get("item_evidence", []):
            if not item.get("accepted") or str(item.get("kind") or "").lower() != "image":
                continue
            stats["round105_accepted_images"] += 1
            add_cache(cache, digest_index, {
                "cdx_digest": item.get("calculated_cdx_digest"),
                "sha256": item.get("actual_sha256"),
                "source_url": item.get("logical_url"),
                "capture_timestamp": item.get("actual_timestamp"),
                "length": item.get("actual_length"),
                "source": "round105_accepted_item_evidence",
            })
    for row in provenance.get("files", []):
        if row.get("role") != "image_overlay":
            continue
        stats["v38_image_overlays"] += 1
        add_cache(cache, digest_index, {
            "cdx_digest": row.get("cdx_digest"),
            "sha256": row.get("source_sha256"),
            "source_url": row.get("original_url"),
            "capture_timestamp": row.get("actual_capture_timestamp") or row.get("indexed_capture_timestamp"),
            "length": row.get("source_length"),
            "source": "v38_overlay_curated_metadata",
            "route": row.get("route"),
            "output_path": row.get("output_path"),
            "original_url": row.get("original_url"),
        })
    stats["sha256_entries"] = len(cache)
    stats["cdx_digest_entries"] = len(digest_index)
    stats["sha256_records"] = sum(len(v) for v in cache.values())
    return cache, digest_index, dict(stats)


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
        text = budget.read(path, "active_v38_img_style_reference").decode("utf-8", errors="replace")
        files.append(rel)
        literal += text.count(path_part)
        img += len(re.findall(r"(?is)<(?:img|source|input)\b[^>]*(?:src|data-src)\s*=\s*['\"][^'\"]*" + re.escape(path_part), text))
        style += len(re.findall(r"(?is)\bstyle\s*=\s*['\"][^'\"]*" + re.escape(path_part), text))
        css += len(re.findall(r"(?is)url\(\s*['\"]?[^)]*" + re.escape(path_part), text))
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


def sha1_base32(data: bytes) -> str:
    return base64.b32encode(hashlib.sha1(data).digest()).decode("ascii").rstrip("=")


def pillow_report(data: bytes) -> dict:
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


def inspect_payload(path: Path, payload_budget: dict) -> dict:
    rel = path.relative_to(ROOT).as_posix()
    if not path.is_file():
        return {"status": "payload_file_missing", "path": rel}
    length = path.stat().st_size
    if length > PAYLOAD_FILE_LIMIT:
        return {"status": "payload_file_over_32MiB", "path": rel, "length": length}
    if payload_budget["bytes_read"] + length > PAYLOAD_LIMIT:
        return {"status": "payload_budget_64MiB", "path": rel, "length": length}
    data = path.read_bytes()
    payload_budget["bytes_read"] += len(data)
    payload_budget["files_read"] += 1
    return {
        "status": "checked",
        "path": rel,
        "actual_sha1_base32": sha1_base32(data),
        "actual_sha256": hashlib.sha256(data).hexdigest(),
        "actual_length": len(data),
        **pillow_report(data),
    }


def main() -> int:
    started = time.monotonic()
    generated = now_utc()
    stop: dict = {"reason": None}
    budget = MetadataBudget()
    payload_budget = {"bytes_read": 0, "files_read": 0}
    inputs = []
    cache: dict[str, list[dict]] = {}
    digest_index: dict[str, list[dict]] = {}
    target_report: dict = {}
    cdx_report: dict = {"totals": {}, "reports": [], "selected": {}}
    results: list[dict] = []
    candidates: list[dict] = []
    statuses = Counter()
    payload_checks: dict[str, dict] = {}
    try:
        ledger, rec = load_json(LEDGER, budget, "static_target_ledger")
        inputs.append(rec)
        round_data, rec = load_json(ROUND105, budget, "round105_accepted_capture_metadata")
        inputs.append(rec)
        provenance, rec = load_json(PROVENANCE, budget, "current_v38_export_provenance")
        inputs.append(rec)
        accepted, rec = load_json(ACCEPTED, budget, "accepted_two_digest_routes")
        inputs.append(rec)
        targets, target_report = build_targets(ledger, accepted)
        cache, digest_index, cache_stats = build_metadata_cache(round_data, provenance)
        (OUT_DIR / "metadata-identity-cache.json").write_text(
            json.dumps({"schema": "wow-recovery.digest-reuse.metadata-identity-cache.v1", "sha256_to_identities": cache}, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        rows, cdx_report = scan_cdx(targets, budget, started, stop)
        v38_by_sha = defaultdict(list)
        for row in provenance.get("files", []):
            if row.get("role") == "image_overlay" and row.get("source_sha256"):
                v38_by_sha[str(row["source_sha256"]).lower()].append(row)
        active_cache: dict[str, dict] = {}
        for norm, target_rows in rows.items():
            if stop.get("reason"):
                break
            ordered = sorted(target_rows, key=lambda x: (0, -int(x["timestamp"])) if x["timestamp"] <= ANCHOR else (1, int(x["timestamp"])))
            preferred = ordered[0]
            target = targets[norm]
            found = False
            had_digest_metadata = False
            had_v38_route = False
            refs = None
            for ordinal, target_row in enumerate(ordered):
                identities = digest_index.get(target_row["digest"], [])
                if identities:
                    had_digest_metadata = True
                for identity in identities:
                    payload_sha = identity["sha256"]
                    routes = v38_by_sha.get(payload_sha, [])
                    if not routes:
                        continue
                    had_v38_route = True
                    if refs is None:
                        refs = active_cache.setdefault(norm, active_refs(target, budget))
                    for route in routes:
                        result = {
                            "status": "candidate_pending_payload_check",
                            "target_url": target["requested_url"],
                            "target_normalized_url": norm,
                            "target_ledger_index": target["ledger_index"],
                            "target_route": target["route"],
                            "target_capture": target_row,
                            "preferred_capture": preferred,
                            "capture_search_ordinal": ordinal,
                            "all_eligible_capture_versions": len(ordered),
                            "payload_identity": identity,
                            "v38_route": {
                                "route": route.get("route"),
                                "output_path": route.get("output_path"),
                                "original_url": route.get("original_url"),
                                "actual_capture_timestamp": route.get("actual_capture_timestamp"),
                                "indexed_capture_timestamp": route.get("indexed_capture_timestamp"),
                                "cdx_digest": route.get("cdx_digest"),
                                "source_sha256": route.get("source_sha256"),
                                "source_length": route.get("source_length"),
                            },
                            "active_v38_reference_evidence": refs,
                            "source_chain_evidence": {
                                "source": identity.get("source"),
                                "source_url": identity.get("source_url") or route.get("original_url"),
                                "capture_timestamp": identity.get("capture_timestamp") or route.get("actual_capture_timestamp") or route.get("indexed_capture_timestamp"),
                                "source_chain_present": bool(identity.get("source_url") and identity.get("capture_timestamp")) or bool(route.get("original_url") and (route.get("actual_capture_timestamp") or route.get("indexed_capture_timestamp"))),
                            },
                        }
                        if not refs.get("active_ref_found"):
                            result["status"] = "matched_payload_but_inactive_v38_reference"
                            statuses[result["status"]] += 1
                            results.append(result)
                            continue
                        output_path = route.get("output_path")
                        if not isinstance(output_path, str):
                            result["status"] = "v38_route_missing_output_path"
                            statuses[result["status"]] += 1
                            results.append(result)
                            continue
                        payload_path = V38_ROOT / output_path
                        check = payload_checks.get(output_path)
                        if check is None:
                            check = inspect_payload(payload_path, payload_budget)
                            payload_checks[output_path] = check
                        result["payload_byte_check"] = check
                        result["same_bytes_proof"] = {
                            "target_cdx_digest": target_row["digest"],
                            "actual_sha1_base32": check.get("actual_sha1_base32"),
                            "sha1_equal": check.get("actual_sha1_base32") == target_row["digest"],
                            "payload_sha256_metadata": payload_sha,
                            "actual_sha256": check.get("actual_sha256"),
                            "sha256_equal": check.get("actual_sha256") == payload_sha,
                            "payload_length_metadata": identity.get("length"),
                            "actual_length": check.get("actual_length"),
                            "target_cdx_length": target_row.get("length"),
                            "v38_source_length": route.get("source_length"),
                            "pillow_valid": check.get("pillow_valid"),
                            "all_frames_decoded": check.get("all_frames_decoded"),
                        }
                        if check.get("status") != "checked":
                            result["status"] = check.get("status")
                        elif all(result["same_bytes_proof"].get(k) for k in ("sha1_equal", "sha256_equal", "pillow_valid", "all_frames_decoded")):
                            result["status"] = "new_reuse_candidate"
                            candidates.append(result)
                        else:
                            result["status"] = "payload_identity_validation_failed"
                        statuses[result["status"]] += 1
                        results.append(result)
                        found = True
            if not found:
                if had_v38_route and refs is not None and not refs.get("active_ref_found"):
                    statuses["matched_payload_but_inactive_v38_reference"] += 1
                elif had_v38_route:
                    statuses["matched_payload_not_read"] += 1
                elif had_digest_metadata:
                    statuses["digest_metadata_without_v38_route"] += 1
                else:
                    statuses["no_same_byte_metadata_match"] += 1
        if not stop.get("reason"):
            stop["reason"] = "completed"
    except MetadataBudgetExceeded as exc:
        stop["reason"] = "metadata_64MiB_limit"
        stop["error"] = str(exc)
    elapsed = time.monotonic() - started
    cache_path = OUT_DIR / "metadata-identity-cache.json"
    audit = {
        "schema": "wow-recovery.local-audit.digest-reuse-all-captures.v1",
        "status": stop["reason"],
        "generated_utc": generated,
        "elapsed_seconds": elapsed,
        "stop": stop,
        "network_requests": 0,
        "network_performed": False,
        "exported": False,
        "published": False,
        "new_map_generated": False,
        "runner": {"path": Path(__file__).relative_to(ROOT).as_posix(), "sha256": sha256(Path(__file__).read_bytes())},
        "inputs": inputs,
        "metadata_budget": {"limit_bytes": META_LIMIT, "bytes_read": budget.total, "within_limit": budget.total <= META_LIMIT, "read_events": budget.events},
        "payload_budget": {"limit_bytes": PAYLOAD_LIMIT, "single_file_limit_bytes": PAYLOAD_FILE_LIMIT, **payload_budget},
        "coverage": {"target_report": target_report, "source_maps_read": False, "source15_manifest_read": False, "eligible_target_cdx_rows_all_versions": cdx_report.get("totals", {}).get("eligible_capture_rows_all_versions")},
        "metadata_cache": {"path": cache_path.relative_to(ROOT).as_posix(), "sha256": sha256(cache_path.read_bytes()) if cache_path.is_file() else None, **cache_stats},
        "cdx": cdx_report,
        "match_results": {"assessments": len(results), "candidate_count": len(candidates), "by_status": dict(statuses), "payload_files_checked": len(payload_checks)},
        "candidates": candidates,
        "payload_checks": list(payload_checks.values()),
        "remaining": {"targets": len(targets), "targets_with_eligible_rows": cdx_report.get("totals", {}).get("target_urls_with_eligible_rows"), "targets_without_eligible_rows": cdx_report.get("totals", {}).get("target_urls_without_selected_rows"), "new_reuse_candidates": len(candidates)},
        "scope": [
            "All eligible status-200 raster CDX rows for the post-exclusion missing static target set were compared across all 68 non-meta prefix files through 20101207235959.",
            "Capture ordering prefers latest pre-anchor, then searches every other eligible version including later captures.",
            "The identity cache uses accepted round-105 metadata and current v38 overlay provenance; no Source15 manifest, source map, or whole-image scan was used.",
            "Payload bytes were read only after a metadata digest match had an active v38 reference; no map or export was produced.",
        ],
        "unknowns": [
            "CDX metadata without an accepted payload identity is not a payload recovery.",
            "Targets without an active v38 reference remain outside the genuine-candidate set.",
        ],
    }
    audit_path = OUT_DIR / "audit.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit_hash = sha256(audit_path.read_bytes())
    readme = "\n".join([
        "Expanded all-captures local digest-reuse audit",
        "",
        "Offline metadata comparison only; no network, export, publication, map generation, Source15 manifest, source-map read, or whole-image scan.",
        f"Generated UTC: {generated}",
        f"Targets after exclusions: {len(targets)} (dormant CSS lead excluded: {DORMANT_CSS_LEAD})",
        f"CDX files/rows/eligible rows: {cdx_report.get('totals', {}).get('files_scanned')}/{cdx_report.get('totals', {}).get('rows')}/{cdx_report.get('totals', {}).get('eligible_capture_rows_all_versions')}",
        f"Metadata cache SHA256 entries/digest entries: {cache_stats.get('sha256_entries')}/{cache_stats.get('cdx_digest_entries')}",
        f"Payload files/bytes checked: {payload_budget['files_read']}/{payload_budget['bytes_read']}",
        f"Genuine additional candidates: {len(candidates)}",
        f"Metadata bytes: {budget.total}/{META_LIMIT}",
        f"Audit SHA256: {audit_hash}",
        "",
    ])
    (OUT_DIR / "README.md").write_text(readme, encoding="utf-8")
    print(json.dumps({
        "audit": audit_path.relative_to(ROOT).as_posix(),
        "audit_sha256": audit_hash,
        "status": stop["reason"],
        "elapsed_seconds": elapsed,
        "metadata_bytes_read": budget.total,
        "cdx_files": cdx_report.get("totals", {}).get("files_scanned"),
        "eligible_capture_rows": cdx_report.get("totals", {}).get("eligible_capture_rows_all_versions"),
        "targets": len(targets),
        "payload_files_read": payload_budget["files_read"],
        "payload_bytes_read": payload_budget["bytes_read"],
        "candidates": len(candidates),
        "by_status": dict(statuses),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
