"""Root acceptance of the local, compatibility-only v34 checkpoint."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "research/continuous-recovery-20261019"
V33 = ROOT / ".scratch/pages-resources-20261018-v33"
SITE = ROOT / ".scratch/pages-resources-20261019-v34"
OUT = RUN / "publication/root-v34-local-acceptance.json"
READ = lambda p: json.loads(p.read_bytes())
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def bind(p):
    return {"path": p.relative_to(ROOT).as_posix(), "sha256": SHA(p), "bytes": p.stat().st_size}


def main():
    assert not OUT.exists()
    base = RUN / "integration/v34"
    build_path = base / "v34-build-receipt-retry1.json"
    build = READ(build_path)
    assert SHA(build_path) == "00c28092e683d106cbeb8baad54f7660f2eb259a0f215b3938561e466d4a84f2"
    assert build["export_completed"] and not build["published"] and build["network_requests_by_builder"] == 0
    assert build["postbuild"]["actual_files"] == 9018
    assert build["postbuild"]["tree_bytes"] == 594318472
    old_prov, new_prov = V33 / "export-provenance.json", SITE / "export-provenance.json"
    assert SHA(old_prov) == "99ac5b0a2bc7d257b2fe3c4b18a0bb74023c3c57051be3a4f4efe20258f4c8f5"
    assert SHA(new_prov) == "3946f504260aec576087207399ad692eef9f7fac938fac439474a2c540d85447"
    before = {r["output_path"]: r for r in READ(old_prov)["files"]}
    after = {r["output_path"]: r for r in READ(new_prov)["files"]}
    assert len(before) == len(after) == 9017 and set(before) == set(after)
    changed = [p for p in before if (before[p]["derived_sha256"], before[p]["derived_length"]) !=
               (after[p]["derived_sha256"], after[p]["derived_length"])]
    nav = "shared/wow-com/includes-client/navtreefunctions.js"
    assert changed == [nav]
    for p in before:
        if before[p].get("role") == "image_overlay":
            assert before[p] == after[p]
    assert sum(r.get("role") == "image_overlay" for r in after.values()) == 559
    assert SHA(SITE / nav) == after[nav]["derived_sha256"] == "4158e14fbb38e12a2d3f668f29c1762c2763fb2c78730845bce6fd29f57fe493"
    diff_path = base / "v33-v34-readonly-diff.json"
    assert SHA(diff_path) == "82f896c85b671886b32461cd6812f6b467928def0e2275ec3a869b0035688156"
    diff = READ(diff_path)
    assert not diff["tree"]["only_v33"] and not diff["tree"]["only_v34"]
    assert {r["path"] for r in diff["tree"]["changed_files"]} == {nav, "export-provenance.json"}
    assert not diff["provenance"]["overlay_metadata_changes"] and not diff["provenance"]["overlay_byte_mismatches"]
    browser_path = base / "browser/v33-v34-three-pages-r2.json"
    assert SHA(browser_path) == "e126088c573f8b48d02c44784962c827043b3e8141931eb9604648ab909b2d9b"
    browser = READ(browser_path)
    assert len(browser["results"]) == 6 and browser["network_requests"] == 0
    for row in browser["results"]:
        assert not row["goto_error"] and not row["external_requests"]
        menus = row["menu_iframes"]
        assert len(menus["responses"]) == len(menus["finished"]) == 8 and not menus["failed"]
        assert all(r["status"] == 200 and r["content_type"].startswith("text/html") for r in menus["responses"])
        assert len(row["page_errors"]) == (4 if row["variant"] == "v33" and row["page"]["name"] == "contest-winners" else 0)
    assert browser["assertions"]["v34_winners_result"] == "1_6_4"
    viewer = browser["assertions"]["v34_guide_image_click"]["viewer"]
    assert viewer["dumpster"] and viewer["screenie"] and viewer["screenie_width"] == "750px"
    assert "/info/basics/images/guide/ss01.jpg" in viewer["background_image"]
    nav_path = base / "browser/v34-winners-navigation-r3b.json"
    followup = READ(nav_path)
    assert not followup["goto_error"] and not followup["click_error"]
    assert not followup["page_errors"] and not followup["external_requests"]
    destination = followup["destination"]
    assert urlsplit(destination["url"]).path.endswith("/contests/index.html")
    assert destination["title"] == "WoW -> Contests" and destination["body_text_length"] > 15000
    assert "World of Warcraft Contests" in destination["body_text"] and destination["result"] == "1_6_4"
    assert any(r["status"] == 200 and r["content_type"].startswith("text/html") for r in followup["target_responses"])
    menus = followup["menu_iframes"]
    assert len(menus["responses"]) == len(menus["finished"]) == 16 and not menus["failed"]
    assert all(r["status"] == 200 and r["content_type"].startswith("text/html") for r in menus["responses"])
    pictures = [base / "browser/screenshots-r2/winners-v34-r2.png", base / "browser/screenshots-r2/guide-viewer-v34-r2.png"]
    assert [SHA(p) for p in pictures] == ["f5661729d50efa809ff39414a4d4ccc42e932e4dcf10bad9c8892350097c2aac", "6a42e83cf154a464db65483cd099e618f760bf96e4b2ddf691b7ca1fb8195bd9"]
    result = {"accepted": True, "published": False, "checked_utc": datetime.now(timezone.utc).isoformat(),
        "version": "v34", "declared_files": 9017, "actual_files": 9018, "tree_bytes": 594318472,
        "image_overlays": 559, "new_images": 0, "changed_output_paths": [nav, "export-provenance.json"],
        "browser_scenarios": 7, "external_requests": 0,
        "scope": "Exact output delta, all existing image overlay metadata and byte-audit results, six page comparisons, native guide viewer and completed winners-to-Contests navigation; root reviewed two screenshots.",
        "navigation_observation": "One canceled request is retained; a subsequent HTTP200 target response, title and15597-character body establish completed navigation.",
        "test_harness_corrections": ["R2 adds .htm text/html; all eight menu frames load on each page.",
             "R3b has16 completed menu frames across source and destination. Its two fixed-eight-count summary flags are false, but every response is200HTML and none failed; root checks the raw16 records."],
        "publication_decision": "Hold local; combine with24 accepted news images in v35 before Pages publication.",
        "bindings": [bind(p) for p in [build_path, old_prov, new_prov, diff_path, browser_path, nav_path,
            RUN / "publication/root-v34-input-acceptance-retry1.json", RUN / "publication/root-contest-nav-tool-acceptance.json", *pictures]]}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"accepted": True, "version": "v34", "new_images": 0, "published": False}))


if __name__ == "__main__":
    main()
