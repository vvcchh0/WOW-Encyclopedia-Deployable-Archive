"""Validate a 503-stopped packet while accepting only its completed CDX targets."""
import argparse
import hashlib
import json
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
READ = lambda p: json.loads(p.read_bytes())
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
FLOOR = 11005853696


def binding(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": SHA(path), "bytes": path.stat().st_size}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", required=True)
    parser.add_argument("--report-sha", required=True)
    args = parser.parse_args()
    assert re.fullmatch(r"gallery-late-rest\d+[a-z]", args.packet)
    directory = PUB.parent / "network" / args.packet
    out = PUB / f"root-{args.packet}-source-acceptance.json"
    assert not out.exists() and shutil.disk_usage(ROOT).free >= FLOOR
    gate_path = PUB / f"root-{args.packet}-execute-go.json"
    gate = READ(gate_path)
    assert gate["accepted"] and gate["root_go"] and gate["index_only"]
    assert gate["prior_failure_tail"] == 0 and gate["payload_replays_allowed"] == 0
    plan_path = directory / "plan.json"
    assert SHA(plan_path) == gate["plan_sha256"]
    plan = READ(plan_path)
    assert SHA(ROOT / gate["latest_network_source_path"]) == gate["latest_network_source_sha256"]
    assert SHA(directory / "batch-report.json") == args.report_sha
    report = READ(directory / "batch-report.json")
    execution = READ(directory / "execution-input-bindings.json")
    assert SHA(ROOT / execution["script_path"]) == execution["script_sha256"] == gate["driver_sha256"]
    assert SHA(ROOT / execution["plan_path"]) == execution["plan_sha256"] == report["plan_sha256"]
    assert SHA(ROOT / execution["fixture_path"]) == execution["fixture_sha256"]
    assert READ(ROOT / execution["fixture_path"])["all_passed"]
    source_bindings = []
    for row in execution["source_bindings"].values():
        path = ROOT / row["path"]
        assert SHA(path) == row["sha256"], row["path"]
        source_bindings.append(binding(path))
    parent = READ(directory / "parent-execution-receipt.json")
    assert parent["go_sha256"] == SHA(gate_path)
    assert parent["returncode"] == 0 and not parent["timed_out"] and parent["retry_count"] == 0
    assert parent["outer_timeout_seconds"] == 960 and parent["elapsed_seconds"] < 960
    assert all(parent["disk"][key] >= FLOOR for key in ("free_before_bytes", "free_after_bytes"))
    for row in parent["raw_evidence_files"]:
        path = ROOT / row["path"]
        assert SHA(path) == row["sha256"], row["path"]
    attempts = READ(directory / "attempt-records.json")
    dispatch = READ(directory / "dispatch-log.json")
    candidates = plan["candidates"]
    assert len(attempts) == report["network_requests"] == len(dispatch) <= gate["max_requests"]
    assert len(candidates) == gate["target_count"]
    assert report["failure_streak"] == 0 and report["prior_failure_tail"] == 0
    assert report["payload_replay_count"] == 0 and not report["continuation_followed"]
    assert report["stop_reason"] == "endpoint_status_503"
    assert report["cooldown_required_seconds"] >= 120
    assert report["cooldown_not_before_utc"]
    assert datetime.fromisoformat(report["cooldown_not_before_utc"].replace("Z", "+00:00")) >= datetime.fromisoformat(report["finished_utc"].replace("Z", "+00:00")) + __import__("datetime").timedelta(seconds=120)
    successes = []
    total_bytes = 0
    raw_bindings = []
    results = []
    previous = None
    for a, d in zip(attempts, dispatch):
        assert a["attempt"] == d["attempt"] and a["rank"] == d["rank"]
        assert a["kind"] == d["kind"] == "cdx"
        assert a["transport"] == d["transport"]
        assert a["disk_free_before_bytes"] >= FLOOR and d["disk_free_before_bytes"] >= FLOOR
        start = datetime.fromisoformat(a["started_utc"].replace("Z", "+00:00"))
        if previous:
            assert (start - previous).total_seconds() >= 5
        previous = start
        c = next(x for x in candidates if x["rank"] == a["rank"])
        assert d["query_url"] == c["query_url"] == c["cdx_query_url"]
        q = parse_qs(urlsplit(d["query_url"]).query)
        assert q["url"] == [c["prefix"]] and q["matchType"] == ["prefix"]
        assert q["from"] == ["20080512210045"] and q["to"] == ["20101207235959"]
        assert q["limit"] == ["500"] and q["showResumeKey"] == ["true"]
        assert a["source_status"] != 429
        total_bytes += a["body_bytes"]
        assert total_bytes <= gate["max_body_bytes"] and a["body_bytes"] <= 8388608
        if a["source_status"] == 503:
            assert a is attempts[-1] and a["transport"] == "proxy" and a["curl_exit"] == 0
            assert not a["cdx_json_valid"] and not a["continuation_followed"]
            body_path = ROOT / a["raw"]["body"]
            assert SHA(body_path) == a["body_sha256"] and body_path.stat().st_size == a["body_bytes"]
            headers = (ROOT / a["raw"]["headers.txt"]).read_text("utf-8", errors="replace")
            assert re.search(r"HTTP/\S+ 503(?: |\r|\n)", headers)
            raw_bindings.append(binding(body_path))
            continue
        if a["source_status"] != 200:
            assert a["transport"] == "direct" and a["transport_error"] and not a["source_status"]
            continue
        assert a["curl_exit"] == 0 and not a["transport_error"] and a["cdx_json_valid"]
        assert not a["potential_truncation"] and not a["resume_keys"]
        assert a["transport"] == "proxy"
        prior = attempts[a["attempt"] - 2]
        assert prior["rank"] == a["rank"] and prior["transport"] == "direct"
        body_path = ROOT / a["raw"]["body"]
        assert body_path.stat().st_size == a["body_bytes"] and SHA(body_path) == a["body_sha256"]
        headers = (ROOT / a["raw"]["headers.txt"]).read_text("utf-8", errors="replace")
        assert re.search(r"HTTP/\S+ 200(?: |\r|\n)", headers)
        raw = READ(body_path)
        fields = ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"]
        assert isinstance(raw, list) and raw and raw[0] == fields and len(raw) - 1 < 500
        rows = []
        scheme_counts = Counter()
        classes = Counter()
        native_rows = []
        prefix_path = urlsplit(c["prefix"]).path
        image_other_paths = set()
        for values in raw[1:]:
            assert isinstance(values, list) and len(values) == len(fields)
            r = dict(zip(fields, values))
            assert re.fullmatch(r"\d{14}", r["timestamp"])
            assert "20080512210045" <= r["timestamp"] <= "20101207235959"
            u = urlsplit(r["original"])
            assert u.scheme in ("http", "https") and u.hostname in ("www.worldofwarcraft.com", "worldofwarcraft.com")
            assert not u.username and not u.password
            scheme_counts[u.scheme] += 1
            suffix = u.path[len(prefix_path):] if u.path.startswith(prefix_path) else None
            native = bool(suffix and re.fullmatch(r"ss\d+(?:-thumb)?\.jpg", suffix, re.I))
            if native:
                native_rows.append(r)
            image = r["statuscode"] == "200" and r["mimetype"].startswith("image/")
            if native:
                kind = "native_direct_image_index" if image else "native_direct_nonimage_or_revisit"
            elif suffix is None:
                kind = "prefix_sibling_or_other_path"
            elif re.fullmatch(r"thumbs/ss\d+-thumb\.jpg", suffix, re.I):
                kind = "nested_guide_preview"
            else:
                kind = "directory_or_other"
            classes[kind] += 1
            if image and not native:
                image_other_paths.add(r["original"])
            rows.append(r)
        assert len(rows) == a["cdx_record_count"]
        evidence = c["source_evidence"]
        page = ROOT / evidence["path"]
        assert SHA(page) == evidence["sha256"]
        assert evidence["addshots_literal"] in page.read_text("utf-8").splitlines()[evidence["addshots_line"] - 1]
        assert evidence["source_directory"] == prefix_path
        results.append({"gallery": c["label"], "prefix": c["prefix"], "window": c["query_window"],
                        "complete_within_response": True, "row_count": len(rows), "scheme_counts": dict(scheme_counts),
                        "path_class_counts": dict(classes), "native_rows_all_schemes": native_rows,
                        "other_image_originals": sorted(image_other_paths),
                        "source_page": binding(page), "raw_body_local": binding(body_path), "rows": rows})
        raw_bindings.append(binding(body_path))
        successes.append(a)
    assert len(successes) == len(candidates) - 2 == report["source_responses"] - 1
    assert len(set(a["rank"] for a in successes)) == len(successes)
    assert attempts[-1]["source_status"] == 503
    incomplete = [c for c in candidates if c["rank"] not in {a["rank"] for a in successes}]
    assert len(incomplete) == 2
    assert total_bytes == report["total_body_bytes"]
    elapsed = (datetime.fromisoformat(report["finished_utc"].replace("Z", "+00:00")) -
               datetime.fromisoformat(report["window_started_utc"].replace("Z", "+00:00"))).total_seconds()
    assert elapsed < gate["max_seconds"]
    receipt = {"accepted": True, "checked_utc": datetime.now(timezone.utc).isoformat(), "is_network_batch": True,
               "scope": "Independent parsing of every completed raw CDX response, plus the terminal503 and immediate stop. Eight successful targets only; the failed and unqueried targets remain open. A fresh post-failure control is required before any new batch.",
               "network_requests": len(attempts), "source_responses": len(successes), "body_bytes": total_bytes,
               "elapsed_seconds": elapsed, "accepted_image_payloads": 0, "payload_replays": 0,
               "failure_streak_end": 0, "cooldown_not_before_utc": report["cooldown_not_before_utc"],
               "resume_gate_passed": False, "stop_reason": report["stop_reason"], "endpoint_stop_status": 503,
               "last_failure_finished_utc": report["finished_utc"],
               "http_responses": report["source_responses"],
               "incomplete_targets": [{"gallery": c["label"], "prefix": c["prefix"], "status": "source_503" if c["rank"] == attempts[-1]["rank"] else "not_queried"} for c in incomplete],
               "total_index_rows": sum(r["row_count"] for r in results),
               "native_index_rows_all_schemes": sum(len(r["native_rows_all_schemes"]) for r in results),
               "results": results, "raw_body_bindings_local_only": raw_bindings,
               "source_bindings": source_bindings,
               "bindings": [binding(directory / f) for f in ("batch-report.json", "attempt-records.json", "dispatch-log.json", "plan.json", "execution-plan.json", "execution-input-bindings.json", "parent-execution-receipt.json")],
               "summary_report_hash_erratum": "Frozen driver summary embeds a pre-final report SHA; this receipt binds the actual final report bytes.",
               "disk_free_after_bytes": shutil.disk_usage(ROOT).free}
    assert receipt["disk_free_after_bytes"] >= FLOOR
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: receipt[k] for k in ("accepted", "network_requests", "source_responses", "total_index_rows", "native_index_rows_all_schemes")}))


if __name__ == "__main__":
    main()
