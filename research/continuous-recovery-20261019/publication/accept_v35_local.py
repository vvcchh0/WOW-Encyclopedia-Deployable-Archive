"""Accept the checked v35 tree and its real browser image delta for publication."""
import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "research/continuous-recovery-20261019"
PUB = RUN / "publication"
SITE = ROOT / ".scratch/pages-resources-20261019-v35"
V33 = ROOT / ".scratch/pages-resources-20261018-v33"
BASE = RUN / "integration/v35"
OUT = PUB / "root-v35-local-acceptance.json"
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
READ = lambda p: json.loads(p.read_bytes())


def bind(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": SHA(path), "bytes": path.stat().st_size}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser-result-sha", required=True)
    parser.add_argument("--browser-receipt-sha", required=True)
    args = parser.parse_args()
    assert not OUT.exists() and shutil.disk_usage(ROOT).free >= 11005853696
    final_path = PUB / "root-v35-finalization-r2-execution.json"
    final = READ(final_path)
    assert final["accepted"] and final["status"] == "finalized_from_checked_partial" and not final["published"]
    assert final["new_export_invocations"] == 0 and final["child_returncode"] == 0
    check_path = BASE / "finalization/v35-partial-check-receipt.json"
    assert SHA(check_path) == final["check_receipt_sha256"] == "eb05bfc5dd10fb8370ba8f806fa625abd6a5b43378196571e821c9c69d747122"
    check = READ(check_path)
    assert check["status"] == "passed" and not check["errors"]
    assert check["counts"] == {"declared_files": 9041, "actual_files": 9042, "symlinks": 0}
    prov_path = SITE / "export-provenance.json"
    assert SHA(prov_path) == final["export_provenance_sha256"] == "f37f73ba4cdd63b1190b895a2d770dd94b2b764ad5fc219a5fd34bad93a3c4d0"
    gate_path = PUB / "root-v35-input-acceptance.json"
    assert SHA(gate_path) == "1d3705381773e5040724f957512987719946e36876765f84395e804fdee655fd"
    gate = READ(gate_path)
    assert gate["accepted"] and len(gate["map_bindings"]) == 62
    for row in gate["map_bindings"]:
        assert SHA(ROOT / row["path"]) == row["sha256"], row["path"]
    v34_gate = PUB / "root-v34-local-acceptance.json"
    assert READ(v34_gate)["accepted"] and READ(v34_gate)["browser_scenarios"] == 7

    browser = BASE / "browser/results/v35-new-images-r2.json"
    run_path = BASE / "browser/v35-browser-run-receipt-r2.json"
    assert SHA(browser) == args.browser_result_sha and SHA(run_path) == args.browser_receipt_sha
    run, result = READ(run_path), READ(browser)
    assert run["status"] == "completed" and run["returncode"] == 0 and run["elapsed_seconds"] <= 300
    assert result["accepted"] and result["browser_executed"] and result["target_count"] == 24
    assert all(result["assertions"].values()) and len(result["target_results"]) == 23
    assert not any(result[k] for k in ("external_requests", "request_failures", "page_errors", "server_errors", "errors"))
    inp_path = BASE / "browser/v35-browser-input.json"
    inp = READ(inp_path)
    assert run["input"]["sha256"] == SHA(inp_path) == result["input"]["sha256"]
    targets = {r["original"]: r for r in inp["targets"]}
    for row in result["target_results"]:
        target = targets[row["original"]]
        assert row["facts"] and all(f["visible"] and f["complete"] and not f["decode_error"] and
            f["natural"] == target["dimensions"] and f["pathname"] == target["served_output_path"] for f in row["facts"])
    native = result["native_toggle"]
    assert native["id"] == "news10-15-07-904" and native["clicked"] and native["final_class"] == "news-expand"
    assert native["image_facts"] and all(f["visible"] and f["complete"] and not f["decode_error"] for f in native["image_facts"])
    assert all(r["status"] == 200 and r["mime"].startswith("text/html") for r in result["pages"])
    for target in targets.values():
        rows = [r for r in result["local_image_or_asset_requests"] if r["path"] == target["served_output_path"]]
        assert rows and all(r["exact"] and r["sha256"] == target["sha256"] and r["length"] == target["length"] for r in rows)
    screenshots = [ROOT / p for p in result["screenshots"]]
    assert len(screenshots) == 2 and all(p.is_file() for p in screenshots)

    before = {r["output_path"]: r for r in READ(V33 / "export-provenance.json")["files"]}
    provenance = READ(prov_path)
    after = {r["output_path"]: r for r in provenance["files"]}
    assert len(before) == 9017 and len(after) == 9041 and not (set(before) - set(after))
    new = set(after) - set(before)
    assert len(new) == 24 and new == {r["served_output_path"] for r in targets.values()}
    common = {p for p in before if (before[p]["derived_sha256"], before[p]["derived_length"]) !=
              (after[p]["derived_sha256"], after[p]["derived_length"])}
    assert common == {"__offline/pages_runtime.js", "__offline/route-map.json", "news/rss-10-2007.xml.html",
                      "news/wow-news2004.html", "shared/wow-com/includes-client/navtreefunctions.js"}
    assert sum(r.get("role") == "image_overlay" for r in after.values()) == 583
    assert sum(after[p]["derived_length"] for p in new) == 191943
    objects = []
    for p in sorted(new | common | {"export-provenance.json"}):
        path = SITE / p
        record = bind(path)
        record["path"] = p
        if p != "export-provenance.json":
            assert record["sha256"] == after[p]["derived_sha256"] and record["bytes"] == after[p]["derived_length"]
        suffix = path.suffix.lower()
        record["mime"] = {".js": ["text/javascript", "application/javascript"], ".json": ["application/json"],
                          ".html": ["text/html"], ".jpg": ["image/jpeg"]}[suffix]
        objects.append(record)
    assert len(objects) == 30
    pages_commit = subprocess.check_output(["git", "rev-parse", "gh-pages"], cwd=ROOT, timeout=30).decode().strip()
    assert pages_commit == "f648d3439961bd2e242f4eff588321a286ca2653"
    paths = [final_path, check_path, gate_path, v34_gate, browser, run_path, inp_path,
        PUB / "root-v35-browser-input-acceptance.json", PUB / "root-v35-browser-execute-go.json",
        BASE / "browser/check_v35_new_images_r2.cjs", BASE / "browser/execute_v35_browser_r2.py", *screenshots]
    output = {"accepted": True, "published": False, "checked_utc": datetime.now(timezone.utc).isoformat(),
        "version": "v35", "local_site": SITE.relative_to(ROOT).as_posix(), "previous_pages_commit": pages_commit,
        "declared_files": 9041, "actual_files": 9042, "tree_bytes": 594545453, "image_overlays": 583,
        "new_images": 24, "new_image_bytes": 191943, "external_requests": 0,
        "browser_targets": 24, "native_toggle": native["id"], "objects": objects,
        "bindings": [bind(p) for p in paths],
        "scope": "Reuses completed full9041-file check and unchanged promotion provenance; independently verifies source bindings, exact24 image bytes, actual DOM/decode/native-toggle observations, v34 menu acceptance and30-object delta from live v33. Root separately reviews both screenshots before running this acceptance."}
    OUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"accepted": True, "version": "v35", "new_images": 24, "objects": 30, "published": False}))


if __name__ == "__main__":
    main()
