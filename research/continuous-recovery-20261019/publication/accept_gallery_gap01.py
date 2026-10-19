"""Root review of two exact CDX gap responses and existing gallery evidence."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "research/continuous-recovery-20261019"
BATCH = RUN / "network/gallery-late-gap01"
OUT = RUN / "publication/root-gallery-late-gap01-source-acceptance.json"
FLOOR = 11005853696


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def relative(path):
    return path.relative_to(ROOT).as_posix()


if __name__ == "__main__":
    assert not OUT.exists()
    ledger = read(RUN / "gallery-audit/coverage-ledger.json")
    for entry in ledger["evidence_files"]:
        path = (ROOT / entry["path"]).resolve()
        path.relative_to(ROOT)
        assert path.is_file() and sha(path) == entry["sha256"]
    assert len(ledger["gallery_groups"]) == 50
    native_path = ROOT / "research/continuous-recovery-20261018/publication/root-karazhan-availability-v3.json"
    native = read(native_path)
    counts = Counter((r["kind"], r["outcome"]) for r in native["rows"])
    assert len(native["rows"]) == 126
    assert counts[("full", "archive_replay_404")] == 63
    assert counts[("thumb", "archive_replay_404")] == 51
    assert len(native["late_cdx_rows"]) == 12
    assert all(r["statuscode"] == "301" and r["mimetype"] == "text/html" for r in native["late_cdx_rows"])

    report = read(BATCH / "batch-report.json")
    attempts = read(BATCH / "attempt-records.json")
    assert len(attempts) == report["network_requests"] == 4
    assert report["stop_reason"] == "completed_candidate_queue"
    assert report["failure_streak"] == 0 and report["payload_replay_count"] == 0
    assert not report["continuation_followed"]
    assert report["cadence"]["min_dispatch"] >= 5.25
    assert report["cadence"]["min_request_start"] >= 5.0
    assert all(a["disk_free_before_bytes"] >= FLOOR and a["disk_floor_passed"] for a in attempts)
    assert [a["transport"] for a in attempts] == ["direct", "proxy", "direct", "proxy"]
    assert [a["source_status"] for a in attempts] == [None, 200, None, 200]
    assert all(not a["resume_keys"] and not a["potential_truncation"] for a in attempts)

    rows_by_gallery = {}
    raw_bindings = []
    for attempt in attempts:
        if attempt["source_status"] != 200:
            continue
        body_name = attempt["raw"].get("body") or attempt["raw"].get("body_path")
        body_path = ROOT / body_name
        assert sha(body_path) == attempt["body_sha256"]
        body = body_path.read_bytes()
        assert len(body) == attempt["body_bytes"]
        payload = json.loads(body)
        assert payload[0] == ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
        assert all(isinstance(row, list) and len(row) == 7 for row in payload[1:])
        rows = [dict(zip(payload[0], row)) for row in payload[1:]]
        assert len(rows) == attempt["cdx_record_count"]
        native_rows = []
        for row in rows:
            parsed = urlsplit(row["original"])
            assert parsed.hostname in {"www.worldofwarcraft.com", "worldofwarcraft.com"}
            assert parsed.username is None and parsed.password is None and not parsed.query
            prefix = urlsplit(attempt["prefix"]).path
            assert parsed.path.startswith(prefix)
            suffix = parsed.path[len(prefix):]
            # Include HTTPS captures in the root check, even when the driver
            # conservatively labels them as a different source scheme.
            if re.fullmatch(r"ss\d+(?:-thumb)?\.jpg", suffix, re.I):
                native_rows.append(row)
        assert not native_rows
        rows_by_gallery[attempt["label"]] = {"complete": True, "rows": rows,
            "row_count": len(rows), "native_full_or_thumbnail_rows_all_schemes": 0,
            "scheme_counts": dict(Counter(urlsplit(r["original"]).scheme for r in rows)),
            "unique_original_paths": sorted({urlsplit(r["original"]).path for r in rows})}
        raw_bindings.append({"path": relative(body_path), "sha256": sha(body_path), "bytes": len(body)})
    assert {k: v["row_count"] for k, v in rows_by_gallery.items()} == {"Karazhan": 52, "Black Temple": 68}
    assert sum(a["body_bytes"] for a in attempts) == report["total_body_bytes"] == 27956
    assert shutil.disk_usage(ROOT).free >= FLOOR
    output = {"accepted": True, "checked_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Independent raw CDX parsing, source evidence hashes, cadence/disk/tail review; native replay404 ledger remains separately bound.",
        "network_requests": 4, "source_responses": 2, "body_bytes": 27956,
        "accepted_image_payloads": 0, "payload_replays": 0, "failure_streak_end": 0,
        "cooldown_not_before_utc": report["cooldown_not_before_utc"],
        "source_evidence_files_rehashed": len(ledger["evidence_files"]),
        "native_karazhan_replay_counts": {"full_404": 63, "thumb_404": 51, "late_301_html": 12},
        "redirect_scope": "Only ss1-thumb late2013 Location was observed; other11 have CDX301 evidence only.",
        "results": rows_by_gallery, "raw_body_bindings_local_only": raw_bindings,
        "bindings": [{"path": relative(p), "sha256": sha(p)} for p in [BATCH / "batch-report.json", BATCH / "attempt-records.json", BATCH / "execution-plan.json", BATCH / "execution-input-bindings.json", RUN / "gallery-audit/coverage-ledger-r2.json", native_path]],
        "decision": {"Karazhan": "park_native_gallery_pending_new_evidence", "Black Temple": "park_native_gallery_pending_new_evidence"},
        "reactivation_triggers": ["A concrete original image URL from another preserved source page", "A valid new image capture row or payload for a native target", "New archive holdings beyond these examined date windows"],
        "limits": "Karazhan native replay404 observations and complete2000–2010 prefix windows/associated-page leads support parking. BlackTemple has complete examined prefix indexes without native rows; its96 native URLs were not individually replayed. Neither conclusion asserts that every archive or later timestamp was exhausted.",
        "disk_free_after_bytes": shutil.disk_usage(ROOT).free}
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"accepted": True, "source_rows": 120, "native_rows_including_https": 0, "decision": output["decision"]}))
