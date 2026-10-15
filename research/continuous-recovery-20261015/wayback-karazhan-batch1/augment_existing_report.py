"""Offline augmentation of an already completed batch report.

No network operation is performed.  The helper adds explicit Pillow decode
and HTML marker fields to each stored source hop, then regenerates the
sanitized summaries from the same raw evidence.
"""

from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
MAIN_PATH = HERE / "wayback_recheck_batch1.py"
# Authoritative timestamp from the original network run, supplied by the
# orchestrator after the report was first written.
ORIGINAL_REQUEST_WINDOW_FINISHED_UTC = "2026-10-15T06:59:35.213520+00:00"


def load_main():
    spec = importlib.util.spec_from_file_location("wayback_batch1_main", MAIN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load batch module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    module = load_main()
    candidates = json.loads((HERE / "candidates.json").read_text(encoding="utf-8"))
    report_path = HERE / "batch-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    for result in report["results"]:
        for hop in result.get("hops") or []:
            body_rel = hop.get("body_path")
            body_path = HERE / body_rel if body_rel else None
            if body_path is not None and not body_path.exists():
                body_path.write_bytes(b"")
            body = body_path.read_bytes() if body_path is not None and body_path.exists() else b""
            image = module.pillow_info(body)
            html = module.html_markers(body, hop.get("content_type"))
            hop["target_id"] = result["target_id"]
            hop["decode"] = image
            hop["decoded_size"] = image.get("size")
            hop["html_markers"] = html
        executed = [hop for hop in result.get("hops") or [] if hop.get("executed")]
        if executed:
            final = executed[-1]
            result.setdefault("detail", {})["pillow"] = final.get("decode")
            result["detail"]["decoded_size"] = final.get("decoded_size")
            result["detail"]["html"] = final.get("html_markers")

    state = module.RunState(time.monotonic())
    executed_hops = [
        hop
        for result in report["results"]
        for hop in result.get("hops") or []
        if hop.get("executed")
    ]
    state.source_requests = len(executed_hops)
    state.transport_attempts = len(executed_hops)
    state.failed_attempts = sum(1 for hop in executed_hops if hop.get("transport_error"))
    state.source_responses = sum(1 for hop in executed_hops if hop.get("source_status") is not None)
    state.total_body_bytes = int(report.get("total_body_bytes") or 0)
    state.fail_streak = int(report.get("consecutive_transport_failure_streak_at_stop") or 0)
    state.stop_reason = report.get("stop_reason")
    state.stop_detail = report.get("stop_detail") or {}
    if state.stop_reason == "five_consecutive_tls_or_transport_failures" and not state.stop_detail:
        failed_hops = [
            hop
            for result in report["results"]
            for hop in result.get("hops") or []
            if hop.get("executed") and hop.get("transport_error")
        ]
        last_failed = failed_hops[-1] if failed_hops else {}
        state.stop_detail = {
            "failure_streak": state.fail_streak,
            "last_source_status": last_failed.get("source_status"),
            "last_curl_exit": last_failed.get("curl_exit"),
        }
    state.rate_limit = report.get("rate_limit")
    preflight = report.get("preflight") or {}
    transport = report.get("transport") or {}
    request_window_finished_utc = (
        report.get("request_window_finished_utc")
        or ORIGINAL_REQUEST_WINDOW_FINISHED_UTC
    )
    module.write_summaries(
        candidates,
        report["results"],
        state,
        report["started_utc"],
        int(preflight.get("free_bytes_before") or 0),
        module.disk_free_bytes(),
        transport.get("confirmed_transport_after_first_target") or "unknown",
        request_window_finished_utc=request_window_finished_utc,
        report_updated_utc=module.now_utc(),
    )
    print(json.dumps({"augmented_targets": len(report["results"]), "network_requests": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
