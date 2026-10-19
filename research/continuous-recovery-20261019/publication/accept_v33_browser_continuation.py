"""Join immutable v33 image checks with the newly executed UI continuation."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "research/continuous-recovery-20261019"
AUDIT = RUN / "local-audit/browser"
PRIOR = ROOT / "research/continuous-recovery-20261018/integration/v33/browser"
SITE = ROOT / ".scratch/pages-resources-20261018-v33"
OUT = RUN / "publication/root-v33-browser-continuation-acceptance.json"
PROVENANCE_SHA = "99ac5b0a2bc7d257b2fe3c4b18a0bb74023c3c57051be3a4f4efe20258f4c8f5"


def read(p): return json.loads(p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


if __name__ == "__main__":
    assert not OUT.exists() and sha(SITE / "export-provenance.json") == PROVENANCE_SHA
    summary_path = AUDIT / "audit-summary-r1.json"
    summary = read(summary_path)
    for b in summary["frozen_bindings"].values():
        assert sha(ROOT / b["path"]) == b["sha256"]
    original_input = read(PRIOR / "v33-browser-input-r7.json")
    current_input = read(AUDIT / "v33-ui-audit-input-r7.json")
    assert set(current_input["source_references"]) == {"ordinary_image_hrefs", "static_render_targets"}
    for key, rows in current_input["source_references"].items():
        assert rows == original_input["source_references"][key]
    prior = read(PRIOR / "results/v33-browser-result-r5.json")
    bindings = [{"path": summary_path.relative_to(ROOT).as_posix(), "sha256": sha(summary_path)}]
    passed = {"ordinary": set(), "static": set()}
    actual_pages = set()
    for item in summary["final_results"]:
        p = ROOT / item["path"]
        assert sha(p) == item["sha256"]
        report = read(p)
        assert not report["external_requests"] and not report["request_failures"] and not report["page_errors"]
        assert report["output"]["provenance_sha256"] == PROVENANCE_SHA
        assert sha(ROOT / report["input"]["path"]) == report["input"]["sha256"]
        scope = "static" if report["scope"] == "static" else "ordinary"
        for result in report["target_results"]:
            actual_pages.add(result["page_output"])
            if result["status"] == "passed":
                assert result["original"] not in passed[scope]
                passed[scope].add(result["original"])
            else:
                assert result["original"].endswith("/news/images/08-02/02-06-08-3.jpg") and result["status"] == "not_visible"
        bindings.append({"path": item["path"], "sha256": sha(p)})
    final_path = AUDIT / "results/final-news-target-r8.json"
    final = read(final_path)
    assert final["accepted"] and not final["external_requests"] and not final["request_failures"] and not final["page_errors"]
    assert len(final["target_results"]) == 1
    result = final["target_results"][0]
    assert result["status"] == "passed" and result["news_actions"] == ["news2-6-08-270"]
    assert result["visible"][0]["natural"] == [130, 100]
    passed["static"].add(result["original"])
    assert len(passed["ordinary"]) == 46 and len(passed["static"]) == 30
    prior_ordinary = {r["original"] for r in prior["checks"] if r.get("accepted") and r.get("name") == "ordinary image href navigates locally"}
    inactive = {r["original"] for r in prior["inactive_image_maps"]}
    assert len(prior_ordinary) == 21 and len(inactive) == 1
    css_viewer = "http://www.worldofwarcraft.com/pvp/tournament/images/ss5.jpg"
    assert (prior_ordinary | inactive | {css_viewer} | passed["ordinary"]) == {r["original"] for r in original_input["source_references"]["ordinary_image_hrefs"]}
    assert passed["static"] == {r["original"] for r in original_input["source_references"]["static_render_targets"]}
    files = {f["output_path"]: f for f in read(SITE / "export-provenance.json")["files"]}
    checked = set(actual_pages)
    checked.update(item["served_output_path"] for item in original_input["new_originals"])
    for relative in checked:
        assert sha(SITE / relative) == files[relative]["derived_sha256"]
    bindings.extend({"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p)} for p in [final_path, AUDIT / "v33-ui-final-news-target-input-r8.json", PRIOR / "results/tournament-viewer-baseline.json"])
    output = {"accepted": True, "checked_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "All planned v33 image-delta UI targets; not an exhaustive audit of the full historical website.",
        "export_provenance_sha256": PROVENANCE_SHA, "planned_delta_coverage_complete": True,
        "reused_new_original_bytes_and_decode_checks": 120, "reused_native_popup_links": 21,
        "ordinary_targets": 69, "active_ordinary_targets_passed": 68, "inactive_source_map_declarations": 1,
        "static_targets_passed": 30, "new_continuation_targets_passed": 76,
        "frozen_output_files_rehashed": len(checked), "external_requests": 0,
        "news_target_correction": "The original r7 lacked the native toggle citation for February6. The image exists as an IMG; a one-target check clicked its real news control and verified130x100 pixels without changing site bytes.",
        "remaining_known_issue": "Four pre-existing menu exceptions on the Vintage Poster winners page are isolated for a new derived compatibility repair.",
        "bindings": bindings}
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: output[k] for k in ["accepted", "planned_delta_coverage_complete", "new_continuation_targets_passed", "frozen_output_files_rehashed"]}))
