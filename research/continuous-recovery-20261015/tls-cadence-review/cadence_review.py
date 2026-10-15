"""Offline cadence extraction for NET013, RSS016, and RSS018.

This script reads only the three completed batch reports and dispatch journals.
It does not invoke curl or inspect response bodies.  The generated table is
deliberately limited to within-batch timing; monotonic clocks are not compared
across batches.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


BASE = Path("research/continuous-recovery-20261015")
OUT = BASE / "tls-cadence-review"

BATCHES = [
    {
        "batch_id": "NET-NEWS-ASSETS-013",
        "directory": BASE / "network-news-assets13",
        "report": BASE / "network-news-assets13" / "batch-report.json",
        "dispatch": BASE / "network-news-assets13" / "dispatch-log.json",
    },
    {
        "batch_id": "NET-RSS-016",
        "directory": BASE / "network-rss16",
        "report": BASE / "network-rss16" / "batch-report.json",
        "dispatch": BASE / "network-rss16" / "dispatch-log.json",
    },
    {
        "batch_id": "NET-RSS-018",
        "directory": BASE / "network-rss18",
        "report": BASE / "network-rss18" / "batch-report.json",
        "dispatch": BASE / "network-rss18" / "dispatch-log.json",
    },
]

GENERATOR_COMMAND = (
    "C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/"
    "dependencies/python/python.exe -X utf8 "
    "research/continuous-recovery-20261015/tls-cadence-review/cadence_review.py"
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def round_seconds(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value, 6)


def attempt_like(value: Any) -> bool:
    return isinstance(value, dict) and "started_utc" in value and "kind" in value


def collect_attempts(value: Any, output: list[dict[str, Any]]) -> None:
    """Collect both report schemas used by the three batches.

    NET013 stores a replay hop as one attempt dict. RSS016/RSS018 store replay
    hops as containers containing an ``attempts`` list.
    """

    if isinstance(value, dict):
        if attempt_like(value):
            output.append(value)
            return
        if isinstance(value.get("attempts"), list):
            for item in value["attempts"]:
                collect_attempts(item, output)
            return
        for key, child in value.items():
            if key not in {"raw", "capture_records", "selected_capture"}:
                collect_attempts(child, output)
        return
    if isinstance(value, list):
        for item in value:
            collect_attempts(item, output)


def report_attempts(report: dict[str, Any]) -> list[dict[str, Any]]:
    attempts: list[dict[str, Any]] = []
    for result in report.get("results", []):
        # The result context is attached after collection so the original
        # attempt objects remain untouched.
        collect_attempts(result.get("cdx"), attempts)
        collect_attempts(result.get("replay_hops"), attempts)
    return attempts


def target_for_attempt(attempt: dict[str, Any], result: dict[str, Any]) -> str | None:
    return attempt.get("target_key") or result.get("target")


def collect_contextual_attempts(
    report: dict[str, Any],
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    output: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for result in report.get("results", []):
        local: list[dict[str, Any]] = []
        collect_attempts(result.get("cdx"), local)
        collect_attempts(result.get("replay_hops"), local)
        output.extend((attempt, result) for attempt in local)
    return output


def source_status(value: Any) -> int | str | None:
    """Return only the driver's real source HTTP status.

    ``connect_status`` is intentionally never used here.  A CONNECT 200 with
    ``source_status`` null is therefore a non-response in this review.
    """

    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    text = str(value)
    try:
        return int(text)
    except ValueError:
        return text


def journal_match(
    attempt: dict[str, Any], journal_entry: dict[str, Any]
) -> bool:
    a_dispatch = parse_dt(attempt.get("dispatch_utc"))
    j_dispatch = parse_dt(journal_entry.get("dispatch_utc"))
    same_time = (
        a_dispatch is not None
        and j_dispatch is not None
        and abs((a_dispatch - j_dispatch).total_seconds()) <= 0.01
    )
    same_mono = abs(
        float(attempt.get("dispatch_monotonic"))
        - float(journal_entry.get("dispatch_monotonic"))
    ) <= 0.01
    same_transport = attempt.get("transport") == journal_entry.get("transport")
    return same_time and same_mono and same_transport


def extract_batch(spec: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    report = read_json(spec["report"])
    journal = read_json(spec["dispatch"])
    contextual = collect_contextual_attempts(report)
    report_count = int(report.get("transport_attempt_count", len(contextual)))
    dispatches = list(journal.get("dispatches", []))
    if len(contextual) != report_count:
        raise RuntimeError(
            f"{spec['batch_id']}: report attempts {len(contextual)} != "
            f"transport_attempt_count {report_count}"
        )
    if len(dispatches) != report_count:
        raise RuntimeError(
            f"{spec['batch_id']}: journal dispatches {len(dispatches)} != "
            f"transport_attempt_count {report_count}"
        )

    # The report and journal use the same dispatch timestamp, but sorting by
    # that field makes the cross-check resilient to nested result ordering.
    contextual.sort(key=lambda pair: parse_dt(pair[0]["dispatch_utc"]))
    dispatches.sort(key=lambda item: parse_dt(item["dispatch_utc"]))

    rows: list[dict[str, Any]] = []
    for index, ((attempt, result), journal_entry) in enumerate(
        zip(contextual, dispatches), start=1
    ):
        row = {
            "batch_id": spec["batch_id"],
            "batch_attempt_index": index,
            "resource_target": target_for_attempt(attempt, result),
            "kind": attempt.get("kind"),
            "transport": attempt.get("transport"),
            "request_url": attempt.get("url"),
            "driver_attempt_number": attempt.get("attempt"),
            "actual_request_start_utc": attempt.get("started_utc"),
            "finished_utc": attempt.get("finished_utc"),
            "dispatch_utc": attempt.get("dispatch_utc"),
            "dispatch_monotonic": attempt.get("dispatch_monotonic"),
            "curl_exit": attempt.get("curl_exit"),
            "source_http_status": source_status(attempt.get("source_status")),
            "source_http_counted": attempt.get("source_status") is not None,
            "connect_status_observed": attempt.get("connect_status"),
            "body_is_source_response": attempt.get("body_is_source_response"),
            "transport_reason": attempt.get("transport_reason"),
            "transport_error": attempt.get("transport_error"),
            "body_bytes": attempt.get("body_bytes"),
            "memento_datetime": attempt.get("memento_datetime"),
            "journal_attempt": journal_entry.get("attempt"),
            "journal_dispatch_monotonic": journal_entry.get("dispatch_monotonic"),
            "journal_interval_since_previous_dispatch_seconds": journal_entry.get(
                "interval_since_previous_dispatch_seconds"
            ),
            "dispatch_journal_match": journal_match(attempt, journal_entry),
        }
        rows.append(row)

    # The table's cadence values are intentionally recomputed from actual
    # timestamps. They are not copied from a driver's helper field.
    previous_start: datetime | None = None
    previous_dispatch_mono: float | None = None
    previous_success_finish: datetime | None = None
    for row in rows:
        current_start = parse_dt(row["actual_request_start_utc"])
        current_finished = parse_dt(row["finished_utc"])
        current_dispatch_mono = float(row["journal_dispatch_monotonic"])
        row["previous_actual_request_start_interval_seconds"] = round_seconds(
            (current_start - previous_start).total_seconds()
            if current_start is not None and previous_start is not None
            else None
        )
        row["monotonic_dispatch_interval_seconds"] = round_seconds(
            current_dispatch_mono - previous_dispatch_mono
            if previous_dispatch_mono is not None
            else None
        )
        row["previous_successful_source_http_finish_utc"] = (
            previous_success_finish.isoformat() if previous_success_finish else None
        )
        row["seconds_since_previous_successful_source_http_finish"] = round_seconds(
            (current_start - previous_success_finish).total_seconds()
            if current_start is not None and previous_success_finish is not None
            else None
        )
        if current_start is not None:
            previous_start = current_start
        previous_dispatch_mono = current_dispatch_mono
        if row["source_http_counted"] and current_finished is not None:
            previous_success_finish = current_finished

    observed_source_count = sum(1 for row in rows if row["source_http_counted"])
    report_source_count = int(report.get("source_response_count", observed_source_count))
    if observed_source_count != report_source_count:
        raise RuntimeError(
            f"{spec['batch_id']}: observed source status count "
            f"{observed_source_count} != report source_response_count {report_source_count}"
        )
    if not all(row["dispatch_journal_match"] for row in rows):
        bad = [row["batch_attempt_index"] for row in rows if not row["dispatch_journal_match"]]
        raise RuntimeError(f"{spec['batch_id']}: journal mismatch rows {bad}")

    final_success_index = max(
        (row["batch_attempt_index"] for row in rows if row["source_http_counted"]),
        default=None,
    )
    trailing_failures = (
        len(rows) - final_success_index if final_success_index is not None else len(rows)
    )
    summary = {
        "batch_id": spec["batch_id"],
        "report_path": str(spec["report"]).replace("\\", "/"),
        "dispatch_path": str(spec["dispatch"]).replace("\\", "/"),
        "report_sha256": sha256_file(spec["report"]),
        "dispatch_sha256": sha256_file(spec["dispatch"]),
        "report_transport_attempt_count": report_count,
        "journal_dispatch_count": len(dispatches),
        "table_row_count": len(rows),
        "report_source_response_count": report_source_count,
        "observed_source_http_count": observed_source_count,
        "source_http_by_kind": dict(
            Counter(row["kind"] for row in rows if row["source_http_counted"])
        ),
        "source_http_by_status": dict(
            Counter(str(row["source_http_status"]) for row in rows if row["source_http_counted"])
        ),
        "curl_exit_counts": dict(Counter(str(row["curl_exit"]) for row in rows)),
        "transport_counts": dict(Counter(str(row["transport"]) for row in rows)),
        "stop_reason": report.get("stop_reason"),
        "stop_detail": report.get("stop_detail"),
        "started_utc": report.get("started_utc"),
        "finished_utc": report.get("finished_utc"),
        "request_window_finished_utc": report.get("request_window_finished_utc"),
        "last_successful_source_http_attempt_index": final_success_index,
        "trailing_attempts_after_last_success": trailing_failures,
    }
    return summary, rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    fields = [
        "batch_id",
        "batch_attempt_index",
        "resource_target",
        "kind",
        "transport",
        "request_url",
        "driver_attempt_number",
        "actual_request_start_utc",
        "finished_utc",
        "dispatch_utc",
        "dispatch_monotonic",
        "curl_exit",
        "source_http_status",
        "source_http_counted",
        "connect_status_observed",
        "body_is_source_response",
        "transport_reason",
        "transport_error",
        "body_bytes",
        "memento_datetime",
        "previous_actual_request_start_interval_seconds",
        "monotonic_dispatch_interval_seconds",
        "seconds_since_previous_successful_source_http_finish",
        "previous_successful_source_http_finish_utc",
        "journal_attempt",
        "journal_dispatch_monotonic",
        "journal_interval_since_previous_dispatch_seconds",
        "dispatch_journal_match",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def markdown_summary(
    batch_summaries: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    input_records: list[dict[str, Any]],
) -> str:
    lines = [
        "# TLS cadence review",
        "",
        "This is an offline extraction from NET-NEWS-ASSETS-013, NET-RSS-016, and NET-RSS-018. It made 0 network requests and did not modify the original reports, journals, raw headers, traces, or bodies.",
        "",
        "The 42 rows are ordered within each batch by actual request start/dispatch order. `source_http_status` is populated only from the driver's `source_status`; CONNECT 200 is retained as an observation but is never counted as a source response. Monotonic intervals and previous-start intervals are computed within each batch only. Control 014/017 is outside this table, and monotonic clocks are not compared across batches.",
        "",
        "## Counts",
        "",
        f"- Rows: {len(rows)} (" + ", ".join(f"{s['batch_id']}={s['table_row_count']}" for s in batch_summaries) + ").",
        f"- Source HTTP rows: {sum(1 for r in rows if r['source_http_counted'])}; CONNECT-only rows remain non-source rows.",
        f"- Dispatch-journal matches: {sum(1 for r in rows if r['dispatch_journal_match'])}/{len(rows)}.",
        "",
        "## Per-batch evidence",
        "",
        "| Batch | Window (UTC) | Rows | Source HTTP | curl exits | Stop | Last source row | Tail after last source |",
        "|---|---|---:|---:|---|---|---:|---:|",
    ]
    for s in batch_summaries:
        exits = ", ".join(f"{k}:{v}" for k, v in sorted(s["curl_exit_counts"].items()))
        lines.append(
            f"| {s['batch_id']} | {s['started_utc']} → {s['finished_utc']} | "
            f"{s['table_row_count']} | {s['observed_source_http_count']} | {exits} | "
            f"{s['stop_reason']} | {s['last_successful_source_http_attempt_index']} | "
            f"{s['trailing_attempts_after_last_success']} |"
        )
    lines.extend(
        [
            "",
            "## Observed transition",
            "",
            "All three batches contain earlier proxy attempts with source HTTP 200, followed at the terminal boundary by a transport-failure streak recorded with curl exit 35 and no source HTTP status. Each batch also begins with a direct attempt that may fail before the proxy path is used. This is an observation about the recorded cadence and transport path; it does not identify whether the limiting factor was new-connection pressure, an intermediate link, or a resource-specific condition.",
            "",
            "The field `seconds_since_previous_successful_source_http_finish` is measured from the current attempt's actual `started_utc` to the immediately preceding counted source response's `finished_utc`; it is null until a previous source response exists. It is not a cross-batch elapsed time.",
            "",
            "## Inputs",
            "",
        ]
    )
    for item in input_records:
        lines.append(
            f"- {item['batch_id']}: report `{item['report_path']}` SHA256 `{item['report_sha256']}`; "
            f"dispatch `{item['dispatch_path']}` SHA256 `{item['dispatch_sha256']}`."
        )
    lines.extend(
        [
            "",
            "Generated by the local command recorded in the JSON output. No root-cause experiment or new network batch was run.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    batch_summaries: list[dict[str, Any]] = []
    all_rows: list[dict[str, Any]] = []
    input_records: list[dict[str, Any]] = []
    for spec in BATCHES:
        summary, rows = extract_batch(spec)
        batch_summaries.append(summary)
        all_rows.extend(rows)
        input_records.append(
            {
                "batch_id": spec["batch_id"],
                "report_path": str(spec["report"]).replace("\\", "/"),
                "dispatch_path": str(spec["dispatch"]).replace("\\", "/"),
                "report_sha256": summary["report_sha256"],
                "dispatch_sha256": summary["dispatch_sha256"],
            }
        )

    expected_rows = sum(s["report_transport_attempt_count"] for s in batch_summaries)
    if len(all_rows) != expected_rows or len(all_rows) != 42:
        raise RuntimeError(f"row conservation failed: rows={len(all_rows)} expected={expected_rows}/42")

    output = {
        "schema": "tls-cadence-review.v1",
        "review_id": "TLS-CADENCE-REVIEW-026",
        "mode": "offline_only",
        "network_requests": 0,
        "within_batch_only": True,
        "excluded_batches": ["NET-CONTROL-014", "NET-CONTROL-017"],
        "generator_command": GENERATOR_COMMAND,
        "generator_exit_code": 0,
        "method": {
            "actual_request_start": "attempt.started_utc",
            "dispatch_monotonic": "dispatch journal dispatch_monotonic, cross-checked to attempt record",
            "previous_start_interval": "current started_utc minus previous started_utc after within-batch chronological sort",
            "seconds_since_previous_source_finish": "current started_utc minus previous counted source_status attempt finished_utc; null before first source response",
            "source_http_rule": "count source_status when non-null; connect_status is reported separately and never counted",
            "raw_trace_read": False,
        },
        "inputs": input_records,
        "batch_summaries": batch_summaries,
        "validation": {
            "expected_rows": 42,
            "actual_rows": len(all_rows),
            "attempt_conservation": all(
                s["table_row_count"] == s["report_transport_attempt_count"] == s["journal_dispatch_count"]
                for s in batch_summaries
            ),
            "journal_matches": all(row["dispatch_journal_match"] for row in all_rows),
            "source_response_conservation": all(
                s["observed_source_http_count"] == s["report_source_response_count"]
                for s in batch_summaries
            ),
        },
        "rows": all_rows,
    }
    json_path = OUT / "tls-cadence-review.json"
    csv_path = OUT / "tls-cadence-review.csv"
    md_path = OUT / "sanitized-summary.md"
    json_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(all_rows, csv_path)
    md_path.write_text(markdown_summary(batch_summaries, all_rows, input_records), encoding="utf-8")
    print(
        json.dumps(
            {
                "mode": "offline_only",
                "network_requests": 0,
                "rows": len(all_rows),
                "batches": {s["batch_id"]: s["table_row_count"] for s in batch_summaries},
                "source_http_rows": sum(1 for row in all_rows if row["source_http_counted"]),
                "journal_matches": sum(1 for row in all_rows if row["dispatch_journal_match"]),
                "attempt_conservation": output["validation"]["attempt_conservation"],
                "source_response_conservation": output["validation"]["source_response_conservation"],
                "outputs": [str(json_path), str(csv_path), str(md_path)],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
