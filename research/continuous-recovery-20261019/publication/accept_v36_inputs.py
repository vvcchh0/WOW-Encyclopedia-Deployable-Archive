"""Review the fixed51-image v36 inputs and the bounded export runner."""
import ast
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "research/continuous-recovery-20261019"
FOLDER = RUN / "integration/v36"
OUT = RUN / "publication/root-v36-input-acceptance.json"
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
READ = lambda p: json.loads(p.read_bytes())


def main():
    assert not OUT.exists()
    pins = {"build_pages_v36.py": "21ce5f64f1b12ebfcf683681b27502b4e677967fbabef3f534cc567b8879fc9d",
        "execute_v36.py": "5f02c99f68e432f21ca2ff8c0518bd001255c5c43b935c557165790613578c29",
        "v36-primary-source-map.json": "77d14e114563c9a58763057f903d29e68d179d9ceadab4740bcb8ff132c1c6eb",
        "v36-supplement-source-map.json": "fb203be4630ffb99916c18b77e3014b7266fa33eacc026d0a479f8648125cc5a",
        "v36-preflight.json": "a69b528ead10c77a569f82f9eff191f546915ded4799ca4c5c87aa63bdf1263d",
        "v36-native-ui-inputs.json": "b945faba376f600d169b4ed798c95bbc44643d8352244d56a6e1595bae3b1bbc"}
    for name, digest in pins.items():
        assert SHA(FOLDER / name) == digest, name
    runner_path = FOLDER / "execute_v36.py"
    tree = ast.parse(runner_path.read_text(encoding="utf-8"))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "export_pages"]
    assert len(calls) == 1
    kwargs = {r.arg: r.value for r in calls[0].keywords}
    assert isinstance(kwargs["max_bytes"], ast.Constant) and kwargs["max_bytes"].value is None
    assert any(isinstance(n, ast.Call) and ast.unparse(n.func) == "subprocess.run" and
        any(k.arg == "timeout" and isinstance(k.value, ast.Constant) and k.value.value == 600 for k in n.keywords) for n in ast.walk(tree))
    spec = importlib.util.spec_from_file_location("root_v36_input_runner", runner_path)
    runner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = runner
    spec.loader.exec_module(runner)
    builder = runner.load_builder()
    preflight = runner.guard_prepared(builder)
    runner.guard_outputs()
    assert builder.SOURCE_SITE == ROOT / ".scratch/offline-navigation-20261015-v15/site"
    assert builder.SOURCE_MANIFEST == ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
    assert preflight["new_image_count"] == 51 and preflight["new_image_bytes"] == 874533
    expected = preflight["expected_after_export"]
    assert (expected["primary_overlays"], expected["supplement_overlays"], expected["total_overlays"],
        expected["declared_files"], expected["actual_files"], expected["guide_images"], expected["guide_previews"]) == (534, 100, 634, 9092, 9093, 39, 22)
    bindings = runner.required_bindings(builder)
    sources = {}
    for name in ("frontier-news16b", "frontier-static20c", "frontier-static20d", "frontier-news20e"):
        pub = RUN / "publication"
        source_path, copy_path, visual_path = [pub / f"root-{name}-{suffix}.json" for suffix in
            ("source-acceptance", "public-copy-acceptance", "visual-acceptance")]
        source, public, visual = READ(source_path), READ(copy_path), READ(visual_path)
        assert source["accepted"] and public["accepted"] and visual["accepted"] and public["copy_mode"] == "original_bytes"
        by = {r["original"]: r for r in source["accepted_images"]}
        for row in public["accepted_images"]:
            before = by[row["original"]]
            assert all(row[k] == before[k] for k in ("sha256", "length", "mime", "dimensions", "decoded_frames", "actual_capture_timestamp", "cdx_digest"))
            assert row["original"] not in sources
            sources[row["original"]] = row
        for path in (source_path, copy_path, visual_path):
            bindings[path.relative_to(ROOT).as_posix()] = SHA(path)
    primary = READ(FOLDER / "v36-primary-source-map.json")["items"]
    assert len(primary) == len(sources) == 51 and not READ(FOLDER / "v36-supplement-source-map.json")["items"]
    copies = []
    for row in primary:
        source = sources[row["original"]]
        assert row["logical_url"] == row["original"] and row["actual_timestamp"] == source["actual_capture_timestamp"]
        assert "20080101000000" <= row["actual_timestamp"] <= "20080512210044"
        assert (row["sha256"], row["length"], row["public_copy_path"]) == (source["sha256"], source["length"], source["local_path"])
        path = ROOT / row["public_copy_path"]
        assert SHA(path) == row["sha256"] and path.stat().st_size == row["length"]
        copies.append({"path": row["public_copy_path"], "sha256": row["sha256"], "length": row["length"]})
    assert sum(r["length"] for r in copies) == 874533
    ui = READ(FOLDER / "v36-native-ui-inputs.json")
    assert ui["target_count"] == 51 and {r["original"] for r in ui["targets"]} == set(sources)
    assert ui["native_toggle_ids"] == [] and ui["reference_count"] == 53
    for page in ui["source_pages"]:
        assert SHA(ROOT / page["path"]) == page["sha256"]
    tool_gate = RUN / "publication/root-export-exhibit-tools-acceptance.json"
    assert READ(tool_gate)["accepted"]
    bindings[tool_gate.relative_to(ROOT).as_posix()] = SHA(tool_gate)
    free = shutil.disk_usage(ROOT).free
    assert free >= 11005853696 + 900000000 and datetime.now(timezone.utc) < runner.START_DEADLINE
    result = {"accepted": True, "checked_utc": datetime.now(timezone.utc).isoformat(), "export_executed": False,
        "network_requests": 0, "new_images": 51, "image_bytes": 874533, "public_image_copies": copies,
        "preflight_sha256": SHA(FOLDER / "v36-preflight.json"),
        "map_bindings": [{"path": p, "sha256": h} for p, h in sorted(bindings.items())],
        "expected_after_export": expected, "workspace_total_budget": None,
        "max_child_export_seconds": 600, "max_parent_wall_seconds": 720,
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, timeout=30).decode().strip(),
        "disk_free_before_bytes": free, "browser_acceptance_pending": True,
        "scope": "Frozen Source15 and accepted583-image closure plus exactly51 new images; new optional-budget optimization and static Visa exhibit. Original source, prior versions and private evidence unchanged.",
        "ui_revision_before_browser": "Existing source references remain frozen. Several text_literal HTML entries are inline CSS backgrounds, so a separate browser plan must inspect actual properties and elements before claiming visible image coverage; no source-code edit or invented toggle is required."}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    assert runner.validate_root_acceptance(builder)["gate"]["accepted"]
    print(json.dumps({"accepted": True, "new_images": 51, "bindings": len(bindings), "browser_pending": True}))


if __name__ == "__main__":
    main()
