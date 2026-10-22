"""Independently accept v54 code and export a fresh derived tree."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / ".scratch/pages-resources-20261022-v54"
PREP = HERE / "integration/v54-input-preparation.json"
FLOOR = 11005853696
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
write = lambda p, x: p.write_bytes((json.dumps(x, ensure_ascii=False, indent=2) + "\n").encode())
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))


def accept_ui():
    import related_talent_ui as new
    previous = subprocess.run(
        ["git", "show", "6e9acf13:tools/related_talent_ui.py"],
        cwd=ROOT, capture_output=True, check=True,
    ).stdout
    old = types.ModuleType("accepted_v53_talent_ui")
    sys.modules[old.__name__] = old
    exec(compile(previous, "<accepted-v53-talent-ui-loader>", "exec"), old.__dict__)
    v1map = ROOT / "research/continuous-recovery-20261021/integration/related-talent-ui/input-map.json"
    v2map = HERE / "integration/related-talent-ui-v54/input-map.json"
    base = "/WOW-Encyclopedia-Deployable-Archive/"
    v1old = old.load_related_talent_ui_bundle(v1map, ROOT, base)
    v1new = new.load_related_talent_ui_bundle(v1map, ROOT, base)
    assert asdict(v1old) == asdict(v1new), "v1 output changed"
    v2 = new.load_related_talent_ui_bundle(v2map, ROOT, base)
    assert len(v2.assets) == len(v2.route_reuses) == 24
    assert sum(len(a.data) for a in v2.assets) == 26930
    assert v1new.notice_html == v2.notice_html
    retained = {a.target_route: a for a in v1new.assets}
    for a in v2.assets:
        if a.target_route in retained:
            assert asdict(a) == asdict(retained[a.target_route]), a.target_route
        else:
            assert a.mime == "image/gif" and "/arrows/" in a.target_route
            assert "down-3" not in a.target_route
    result = {
        "schema": "wow-root-v54-talent-ui-code-acceptance/v1",
        "accepted": True,
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "compared_v1_code_commit": "6e9acf132760d35f00b9ca5b12e158978957e2de",
        "v1_bundle_exactly_unchanged": True,
        "retained_png_asset_records_exactly_unchanged": True,
        "notice_exactly_unchanged": True,
        "assets": 24, "new_cached_arrows": 18, "held_arrows": 3,
        "source_bytes": 26930, "new_downloads": 0,
        "worker_tests": {"loader": 14, "exporter_consumption": 4, "passed": True,
            "evidence": "integration/related-talent-ui-v54/implementation/README.md"},
        "production_export_and_browser_pending": True,
        "bindings": [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p)} for p in (
            ROOT / "tools/related_talent_ui.py", ROOT / "tests/test_related_talent_ui.py",
            ROOT / "tests/test_related_talent_ui_pages.py", v2map,
            v2map.parent / "decision.json", v2map.parent / "root-input-pins.json",
        )],
    }
    write(HERE / "root-v54-talent-ui-code-acceptance.json", result)
    return result


def accept_code():
    import related_faction_icons as faction
    prior_ui = read(HERE / "root-v54-talent-ui-code-acceptance.json")
    assert prior_ui["accepted"]
    for row in prior_ui["bindings"]:
        assert sha(ROOT / row["path"]) == row["sha256"], row["path"]
    bundle = faction.load_related_faction_icon_bundle(
        HERE / "integration/related-faction-icons-v54/input-map.json", ROOT,
        "/WOW-Encyclopedia-Deployable-Archive/",
    )
    assert len(bundle.assets) == len(bundle.route_reuses) == 3
    assert len(bundle.notice_by_page) == 11 and sum(len(a.data) for a in bundle.assets) == 3587
    assert bundle.source_metadata["initial_source_record_browser_acceptance"] is False
    assert bundle.source_metadata["original_2008_images_recovered"] == 0
    import tempfile
    temp = ROOT / ".scratch/test-temp-20261022"
    temp.mkdir(parents=True, exist_ok=True)
    tempfile.tempdir = str(temp)
    suite = unittest.defaultTestLoader.loadTestsFromNames([
        "tests.test_related_faction_icons.RelatedFactionIconTests",
        "tests.test_related_faction_icons_pages.RelatedFactionPagesTests",
        "tests.test_related_talent_ui_pages.RelatedTalentUIPagesTests",
    ])
    log = io.StringIO()
    outcome = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    log_path = HERE / "integration/v54-root-focused-tests.log"
    log_path.write_bytes(log.getvalue().encode())
    code_paths = [
        "tools/export_github_pages.py", "tools/related_talent_ui.py", "tools/related_faction_icons.py",
        "tests/test_related_talent_ui.py", "tests/test_related_talent_ui_pages.py",
        "tests/test_related_faction_icons.py", "tests/test_related_faction_icons_pages.py",
    ]
    result = {
        "schema": "wow-root-v54-code-acceptance/v1",
        "accepted": outcome.wasSuccessful() and not outcome.skipped,
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "new_arrow_assets": 18, "new_faction_icons": 3,
        "new_downloads_during_integration": 0,
        "source_manifest_sha256": faction.EXPECTED_SOURCE_MANIFEST_SHA256,
        "tests": {"run": outcome.testsRun, "failures": len(outcome.failures),
            "errors": len(outcome.errors), "skipped": len(outcome.skipped), "log_sha256": sha(log_path)},
        "prior_worker_regression": {
            "run": 46, "passed": True, "includes_imported_general_exporter_tests": 39,
            "evidence": "integration/related-faction-icons-v54/implementation/validation-report.json",
            "note": "Those 39 passed after the new exporter hook; the root focused run covers the later metadata naming change and real bundle boundaries.",
        },
        "bindings": [{"path": p, "sha256": sha(ROOT / p)} for p in code_paths],
        "production_browser_pending": True,
    }
    write(HERE / "root-v54-code-acceptance.json", result)
    assert result["accepted"], log.getvalue()
    return result


CONFIG_KEYS = (
    "source_site", "source_manifest", "primary_maps", "supplement_maps", "guide_preview_map",
    "guide_image_collection_map", "flash_runtime_archive", "blizzcast_source_map", "related_talent_icon_map",
    "source16_layout_map", "related_talent_ui_map", "talent_box_layout_map",
    "related_encyclopedia_image_map", "related_guide_image_map",
)


def prepare():
    assert not PREP.exists() and not OUT.exists()
    code = read(HERE / "root-v54-code-acceptance.json")
    assert code["accepted"] and read(HERE / "root-v53-online-acceptance.json")["accepted"]
    prior_path = HERE / "integration/v53-input-preparation.json"
    prior = read(prior_path)
    allowed_changed = {r["path"] for r in code["bindings"]}
    bindings = {}
    for row in prior["bindings"]:
        actual = sha(ROOT / row["path"])
        assert actual == row["sha256"] or row["path"] in allowed_changed, row["path"]
        bindings[row["path"]] = actual
    for row in code["bindings"]:
        assert sha(ROOT / row["path"]) == row["sha256"], row["path"]
        bindings[row["path"]] = row["sha256"]
    required = [Path(__file__), prior_path, HERE / "root-v54-code-acceptance.json",
        HERE / "root-v54-talent-ui-code-acceptance.json", HERE / "root-coolwow2-item-source-acceptance.json",
        HERE / "faction-related-candidates/semantic-usage-audit.json"]
    for directory in ("related-talent-ui-v54", "related-faction-icons-v54"):
        required.extend(p for p in (HERE / "integration" / directory).rglob("*")
            if p.is_file() and "implementation" not in p.parts)
    for p in required:
        bindings[p.relative_to(ROOT).as_posix()] = sha(p)
    config = {k: prior[k] for k in CONFIG_KEYS}
    config.update(
        schema="wow-v54-input-preparation/v1", prepared_utc=datetime.now(timezone.utc).isoformat(),
        related_talent_ui_map="research/continuous-recovery-20261022/integration/related-talent-ui-v54/input-map.json",
        related_faction_icon_map="research/continuous-recovery-20261022/integration/related-faction-icons-v54/input-map.json",
        output=OUT.relative_to(ROOT).as_posix(),
        bindings=[{"path": p, "sha256": h} for p, h in sorted(bindings.items())],
        restore_aldor_scryers_lore=True, prior_accepted_version="v53",
        scope="Eighteen cached later-source talent arrows and three later-source faction reward icons; no historical source edits.",
        new_original_2008_images=0, new_related_images=21, network_requests=0,
        deadline_utc="2026-10-22T13:41:33Z",
    )
    write(PREP, config)
    return {"prepared": True, "bindings": len(bindings), "sha256": sha(PREP)}


def export():
    config = read(PREP)
    assert datetime.now(timezone.utc) < datetime.fromisoformat(config["deadline_utc"].replace("Z", "+00:00"))
    assert shutil.disk_usage(ROOT).free >= FLOOR and not OUT.exists()
    for row in config["bindings"]:
        assert sha(ROOT / row["path"]) == row["sha256"], row["path"]
    import export_github_pages
    kwargs = {k: ROOT / config[k] for k in CONFIG_KEYS if k not in ("source_site", "source_manifest", "primary_maps", "supplement_maps")}
    kwargs["related_faction_icon_map"] = ROOT / config["related_faction_icon_map"]
    started = datetime.now(timezone.utc).isoformat()
    result = export_github_pages.export_pages(
        source_site=ROOT / config["source_site"], manifest_path=ROOT / config["source_manifest"], output=OUT,
        base_path="/WOW-Encyclopedia-Deployable-Archive/", workspace_root=ROOT, max_bytes=None, min_free_bytes=FLOOR,
        image_source_maps=tuple(ROOT / p for p in config["primary_maps"]),
        supplement_image_source_maps=tuple(ROOT / p for p in config["supplement_maps"]),
        allow_later_image_supplements=True, restore_aldor_scryers_lore=True, **kwargs,
    )
    receipt = {
        "schema": "wow-v54-build-receipt/v1", "status": "built_pending_independent_browser_acceptance",
        "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
        "preparation_sha256": sha(PREP), "provenance_sha256": sha(OUT / "export-provenance.json"),
        "result": result, "disk_free_after_bytes": shutil.disk_usage(ROOT).free,
        "network_requests": 0, "published": False,
    }
    write(HERE / "integration/v54-build-receipt.json", receipt)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["accept-ui", "accept-code", "prepare", "export"])
    args = parser.parse_args()
    print(json.dumps({"accept-ui": accept_ui, "accept-code": accept_code, "prepare": prepare, "export": export}[args.mode]()))
