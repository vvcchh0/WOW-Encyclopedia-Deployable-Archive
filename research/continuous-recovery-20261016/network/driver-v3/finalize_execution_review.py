from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "research/continuous-recovery-20261016/network/driver-v3"
PREPARED_PLAN = ROOT / "research/continuous-recovery-20261016/network/gallery-prefix02-plan/plan.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def clean_row(row: dict) -> dict:
    return {
        "record_index": row.get("record_index"),
        "timestamp": row.get("timestamp"),
        "original": row.get("original"),
        "mimetype": row.get("mimetype"),
        "statuscode": row.get("statuscode"),
        "digest": row.get("digest"),
        "length": row.get("length"),
        "identity": row.get("identity"),
        "literal_kind": row.get("literal_kind"),
        "number": row.get("number"),
        "strict_image_candidate": row.get("strict_image_candidate"),
        "direct_origin_variant": row.get("direct_origin_variant"),
    }


def main() -> None:
    report_path = OUT / "batch-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    plan = json.loads(PREPARED_PLAN.read_text(encoding="utf-8"))
    attempts = json.loads((OUT / "attempt-records.json").read_text(encoding="utf-8"))
    dispatches = json.loads((OUT / "dispatch-log.json").read_text(encoding="utf-8"))
    by_rank = {int(c["rank"]): c for c in plan["candidates"]}
    candidate_reviews = []
    for result in report.get("candidate_results", []):
        rank = int(result["rank"])
        expected = by_rank[rank]
        strict_full = [clean_row(x) for x in result.get("strict_literal_full_candidates", [])]
        strict_thumb = [clean_row(x) for x in result.get("strict_literal_thumb_candidates", [])]
        variants = [clean_row(x) for x in result.get("direct_identity_variant_candidates", [])]
        nested = [clean_row(x) for x in result.get("nested_preview_or_other_rows", [])]
        other = [clean_row(x) for x in result.get("other_rows", [])]
        raw_attempts = []
        for attempt in result.get("attempts", []):
            raw_attempts.append({
                "attempt": attempt.get("attempt"), "transport": attempt.get("transport"),
                "source_status": attempt.get("source_status"), "curl_exit": attempt.get("curl_exit"),
                "phase_boundary": attempt.get("phase_boundary"), "body_bytes": attempt.get("body_bytes"),
                "body_sha256": attempt.get("body_sha256"), "raw": attempt.get("raw"),
            })
        candidate_reviews.append({
            "rank": rank, "registry_rank": expected.get("registry_rank"),
            "target_key": expected.get("target_key"), "label": result.get("label"),
            "prefix": result.get("prefix"), "expected_full_count": expected.get("expected_full_count"),
            "expected_thumb_count": expected.get("expected_thumb_count"),
            "expected_direct_entities": expected.get("expected_direct_entities"),
            "index_row_count": result.get("capture_index_count", 0),
            "index_status": result.get("status"), "cdx_json_valid": result.get("cdx_json_valid"),
            "resume_keys": result.get("resume_keys", []),
            "potential_truncation": result.get("potential_truncation", False),
            "direct_exact_full_candidates": strict_full,
            "direct_exact_thumb_candidates": strict_thumb,
            "direct_identity_variant_candidates": variants,
            "nested_preview_rows": nested,
            "other_rows": other,
            "missing_expected_full_count": int(expected.get("expected_full_count", 0)) - len(strict_full),
            "missing_expected_thumb_count": int(expected.get("expected_thumb_count", 0)) - len(strict_thumb),
            "raw_attempts": raw_attempts,
        })
    transport_counts = {}
    for attempt in attempts:
        key = f"{attempt.get('transport')}:{attempt.get('source_status') or 'no_http'}:{attempt.get('phase_boundary')}"
        transport_counts[key] = transport_counts.get(key, 0) + 1
    output = {
        "schema": "wow-recovery.gallery-prefix02-execution-review.v1",
        "batch_id": report.get("batch_id"), "mode": "cleaned_index_review", "network_requests": report.get("network_requests"),
        "prepared_plan_path": rel(PREPARED_PLAN), "prepared_plan_sha256": sha(PREPARED_PLAN),
        "execution_plan_path": rel(OUT / "execution-plan.json"), "execution_plan_sha256": sha(OUT / "execution-plan.json"),
        "driver_path": rel(OUT / "gallery_prefix_driver_v3.py"), "driver_sha256": sha(OUT / "gallery_prefix_driver_v3.py"),
        "fixture_path": rel(OUT / "fixture-results.json"), "fixture_sha256": sha(OUT / "fixture-results.json"),
        "batch_report_path": rel(report_path), "batch_report_sha256": sha(report_path),
        "attempt_records_path": rel(OUT / "attempt-records.json"), "attempt_records_sha256": sha(OUT / "attempt-records.json"),
        "dispatch_log_path": rel(OUT / "dispatch-log.json"), "dispatch_log_sha256": sha(OUT / "dispatch-log.json"),
        "source_map_path": rel(OUT / "source-map.json"), "source_map_sha256": sha(OUT / "source-map.json"),
        "raw_root": rel(OUT / "raw"), "raw_file_count": len(list((OUT / "raw").glob("*"))),
        "transport_counts": transport_counts,
        "source_responses": report.get("source_responses"), "total_body_bytes": report.get("total_body_bytes"),
        "stop_reason": report.get("stop_reason"), "failure_streak_start": report.get("failure_streak_start"),
        "failure_streak_final": report.get("failure_streak"), "prior_gallery_prefix01_tail_preserved": 2,
        "historical_allnews02_tail_preserved": 5,
        "cooldown_required_seconds": report.get("cooldown_required_seconds"),
        "cooldown_not_before_utc": report.get("cooldown_not_before_utc"),
        "payload_replay_count": report.get("payload_replay_count"), "continuation_followed": report.get("continuation_followed"),
        "cadence": report.get("cadence"), "dispatch_count": len(dispatches), "attempt_count": len(attempts),
        "candidate_reviews": candidate_reviews,
    }
    path = OUT / "execution-review.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": rel(path), "sha256": sha(path), "candidate_count": len(candidate_reviews), "network_requests": output["network_requests"], "raw_file_count": output["raw_file_count"], "min_dispatch": output["cadence"].get("min_dispatch"), "min_request_start": output["cadence"].get("min_request_start"), "transport_counts": transport_counts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
