"""Read-only local review of the two saved rank-99 GIF replay bodies.

This module deliberately has no HTTP client or subprocess transport. It reads the
already-saved news20e report/state/CDX body and replay bodies, then writes a
sanitized evidence report without copying private headers or cookies.
"""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[4]
PACKET = ROOT / "research" / "continuous-recovery-20261019" / "network" / "frontier-news20e"
OUTPUT = ROOT / "research" / "continuous-recovery-20261019" / "network" / "frontier-news20e-rank99-local-review"
REPORT_PATH = PACKET / "output" / "batch-report.json"
STATE_PATH = PACKET / "output" / "state.json"
SOURCE_MAP_PATH = PACKET / "output" / "source-map.json"
CDX_BODY_PATH = PACKET / "output" / "raw" / "attempt-038-proxy-body.bin"
REPLAY_BODY_PATHS = {
    "20080402082404": PACKET / "output" / "raw" / "attempt-039-proxy-body.bin",
    "20051221010011": PACKET / "output" / "raw" / "attempt-040-proxy-body.bin",
}
ORIGINAL = "http://www.worldofwarcraft.com/news/images/04-09/wallpaper/wallpaper.gif"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha1_hex(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def sha1_base32(data: bytes) -> str:
    return base64.b32encode(hashlib.sha1(data).digest()).decode("ascii").rstrip("=")


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def binding(path: Path, role: str) -> dict[str, Any]:
    return {"path": rel(path), "sha256": sha256(path), "bytes": path.stat().st_size, "role": role}


def frame_evidence(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    frames: list[dict[str, Any]] = []
    with Image.open(path) as image:
        image_format = str(image.format or "").upper()
        n_frames = int(getattr(image, "n_frames", 1))
        for index in range(n_frames):
            image.seek(index)
            frames.append({
                "index": index,
                "format": str(image.format or "").upper(),
                "size": [int(image.size[0]), int(image.size[1])],
                "mode": str(image.mode),
            })
        is_animated = bool(getattr(image, "is_animated", False))
    with Image.open(path) as image:
        image.verify()
    return {
        "path": rel(path),
        "bytes": len(payload),
        "sha1_hex": sha1_hex(payload),
        "sha1_base32": sha1_base32(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "pillow_format": image_format,
        "frame_count": n_frames,
        "is_animated": is_animated,
        "frames": frames,
        "verify": "ok",
    }


def main() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    source_map = json.loads(SOURCE_MAP_PATH.read_text(encoding="utf-8"))
    result = next(item for item in report["results"] if item.get("target_key") == "FRONTIER-NEWS20E-99")
    cdx_rows = result["cdx"]["rows"]
    exact_rows = [row for row in cdx_rows if row.get("identity") == "exact"]
    variant_rows = [row for row in cdx_rows if row.get("identity") != "exact"]
    replay_by_timestamp = {
        item["actual_memento_timestamp"]: item
        for item in result["replay_results"]
    }
    attempts_by_label = {item["label"]: item for item in state["attempts"]}
    replay_evidence = []
    for timestamp, body_path in REPLAY_BODY_PATHS.items():
        replay = replay_by_timestamp[timestamp]
        attempt = attempts_by_label[f"FRONTIER-NEWS20E-99:replay:{timestamp}"]
        body = frame_evidence(body_path)
        cdx_row = next(row for row in exact_rows if row.get("timestamp") == timestamp)
        replay_evidence.append({
            "timestamp": timestamp,
            "memento_url": f"https://web.archive.org/web/{timestamp}id_/{ORIGINAL}",
            "memento_datetime": replay.get("memento_datetime"),
            "link_original": replay.get("link_original"),
            "link_identity": replay.get("link_identity"),
            "http_status": replay.get("http_status"),
            "curl_exit": replay.get("curl_exit"),
            "transport": attempt.get("transport"),
            "started_utc": attempt.get("started_utc"),
            "finished_utc": attempt.get("finished_utc"),
            "cdx_digest": cdx_row.get("digest"),
            "cdx_length": cdx_row.get("length"),
            "body": body,
            "content_type_observed": replay.get("actual_content_type"),
            "expected_contract_for_corrected_source": {
                "mime_types": ["image/gif"],
                "pillow_formats": ["GIF"],
                "all_gif_frames": True,
            },
            "content_type_matches_corrected_gif_contract": replay.get("actual_content_type") == "image/gif",
            "pillow_and_magic_valid": body["pillow_format"] == "GIF" and body["verify"] == "ok",
            "cdx_digest_matches_saved_body": cdx_row.get("digest") == body["sha1_base32"],
            "old_news20e_rejection_reasons": replay.get("reasons", []),
            "private_http_evidence": {
                "headers_and_cookie_text_retained_in_original_output": True,
                "header_text_copied_here": False,
            },
        })

    source_files = [
        binding(REPORT_PATH, "news20e batch report; rank99 result and replay metadata"),
        binding(STATE_PATH, "news20e state; attempt transport/body paths"),
        binding(SOURCE_MAP_PATH, "news20e source map; rank99 source classification"),
        binding(CDX_BODY_PATH, "saved exact-CDX response body; parsed locally"),
    ]
    report_out = {
        "schema": "wow-recovery.frontier-news20e-rank99-local-review.v1",
        "status": "offline_local_review_only",
        "network_requests": 0,
        "source_packet": "research/continuous-recovery-20261019/network/frontier-news20e",
        "candidate": {
            "rank": 99,
            "target_key": "FRONTIER-NEWS20E-99",
            "original": ORIGINAL,
            "corrected_expected": {
                "mime_types": ["image/gif"],
                "pillow_formats": ["GIF"],
                "all_gif_frames": True,
            },
        },
        "source_files": source_files,
        "cdx": {
            "saved_body": binding(CDX_BODY_PATH, "raw CDX JSON body only; no headers copied"),
            "row_count": len(cdx_rows),
            "exact_rows": exact_rows,
            "identity_variant_rows": variant_rows,
            "resume_keys": result["cdx"].get("resume_keys", []),
            "complete": result["cdx"].get("potential_truncation") is False,
        },
        "replays": replay_evidence,
        "conclusion": {
            "20080402082404": "candidate_valid_for_corrected_GIF_contract_and_CDX_digest; old news20e JPEG contract alone caused rejection",
            "20051221010011": "saved body is a valid GIF and same bytes, but does not match its PD63 CDX digest; do not accept this capture",
            "source_candidate": "Only the exact 20080402082404 replay is a locally supported source candidate; this review creates no accepted/public copy and sends no HTTP.",
        },
        "source_map_rank99_status": next(item for item in source_map["entries"] if item.get("target_key") == "FRONTIER-NEWS20E-99").get("status"),
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    out = OUTPUT / "rank99-local-review.json"
    out.write_text(json.dumps(report_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "report": rel(out),
        "report_sha256": sha256(out),
        "network_requests": 0,
        "replays_reviewed": len(replay_evidence),
        "pillow_valid": all(item["body"]["verify"] == "ok" for item in replay_evidence),
        "digest_matches": [item["timestamp"] for item in replay_evidence if item["cdx_digest_matches_saved_body"]],
        "digest_mismatches": [item["timestamp"] for item in replay_evidence if not item["cdx_digest_matches_saved_body"]],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
