"""Review the fixed21-image v37 inputs and the bounded export runner."""
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
FOLDER = RUN / "integration/v37"
OUT = RUN / "publication/root-v37-input-acceptance.json"
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
READ = lambda p: json.loads(p.read_bytes())


def main():
    assert not OUT.exists()
    pins = {"build_pages_v37.py": "a07fa3c718862408808959a288033337a152f0245aa3624416d7bac3e2a4508b",
        "execute_v37.py": "f7d74578b795c99906bd068ff643b55c31a6f2f14439037c7e58f1102db329de",
        "execute_v37_parent_once.py": "9fd90044bd59926a284db35f26859541ea606e4b0889e8f299779066200c585d",
        "v37-primary-source-map.json": "febd24f5e2af8b17f268efe3d9f8c3239cc6d5e308298331a66f9759f470d955",
        "v37-supplement-source-map.json": "7f22f9a8817add33bdab74ec8e5a2203100fbc24a9ca0bb0cde59ee00e5fd2ee",
        "v37-preflight.json": "beab243de6d6d28c34a2f1606ca2ebb6eef229b0547a9ce29a17beb94c192e6d",
        "v37-native-ui-inputs.json": "41403b12e3e0869a358fde4434e606246bed9a8f196d0cc55eccfd4f06b83263"}
    for name, digest in pins.items():
        assert SHA(FOLDER / name) == digest, name
    runner_path = FOLDER / "execute_v37.py"
    tree = ast.parse(runner_path.read_text(encoding="utf-8"))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "export_pages"]
    assert len(calls) == 1
    kwargs = {r.arg: r.value for r in calls[0].keywords}
    assert isinstance(kwargs["max_bytes"], ast.Constant) and kwargs["max_bytes"].value is None
    assert any(isinstance(n, ast.Call) and ast.unparse(n.func) == "subprocess.run" and
        any(k.arg == "timeout" and isinstance(k.value, ast.Constant) and k.value.value == 600 for k in n.keywords) for n in ast.walk(tree))
    outer = ast.parse((FOLDER / "execute_v37_parent_once.py").read_text("utf-8"))
    assert any(isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "OUTER_TIMEOUT" for t in n.targets) and isinstance(n.value, ast.Constant) and n.value.value == 720 for n in ast.walk(outer))
    assert any(isinstance(n, ast.Call) and ast.unparse(n.func) == "subprocess.run" and any(k.arg == "timeout" and isinstance(k.value, ast.Name) and k.value.id == "OUTER_TIMEOUT" for k in n.keywords) for n in ast.walk(outer))
    spec = importlib.util.spec_from_file_location("root_v37_input_runner", runner_path)
    runner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = runner
    spec.loader.exec_module(runner)
    builder = runner.load_builder()
    preflight = runner.guard_prepared(builder)
    runner.guard_outputs()
    assert builder.SOURCE_SITE == ROOT / ".scratch/offline-navigation-20261015-v15/site"
    assert builder.SOURCE_MANIFEST == ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
    assert preflight["new_image_count"] == 21 and preflight["new_image_bytes"] == 167403
    expected = preflight["expected_after_export"]
    assert (expected["primary_overlays"], expected["supplement_overlays"], expected["total_overlays"],
        expected["declared_files"], expected["actual_files"], expected["guide_images"], expected["guide_previews"]) == (555, 100, 655, 9113, 9114, 39, 22)
    bindings = runner.required_bindings(builder)
    sources = {}
    for name in ("news20e-rank99", "frontier-news20f"):
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
    primary = READ(FOLDER / "v37-primary-source-map.json")["items"]
    assert len(primary) == len(sources) == 21 and not READ(FOLDER / "v37-supplement-source-map.json")["items"]
    copies = []
    for row in primary:
        source = sources[row["original"]]
        assert row["logical_url"] == row["original"] and row["actual_timestamp"] == source["actual_capture_timestamp"]
        assert "20080101000000" <= row["actual_timestamp"] <= "20080512210044"
        assert (row["sha256"], row["length"], row["public_copy_path"]) == (source["sha256"], source["length"], source["local_path"])
        path = ROOT / row["public_copy_path"]
        assert SHA(path) == row["sha256"] and path.stat().st_size == row["length"]
        copies.append({"path": row["public_copy_path"], "sha256": row["sha256"], "length": row["length"]})
    assert sum(r["length"] for r in copies) == 167403
    ui = READ(FOLDER / "v37-native-ui-inputs.json")
    assert ui["target_count"] == 21 and {r["original"] for r in ui["targets"]} == set(sources)
    assert ui["native_toggle_target_count"] == 0 and ui["reference_count"] == 21
    for page in ui["source_pages"]:
        assert SHA(ROOT / page["path"]) == page["sha256"]
    tool_gate = RUN / "publication/root-toplist-tools-acceptance.json"
    assert READ(tool_gate)["accepted"]
    bindings[tool_gate.relative_to(ROOT).as_posix()] = SHA(tool_gate)
    free = shutil.disk_usage(ROOT).free
    assert free >= 11005853696 + 900000000 and datetime.now(timezone.utc) < runner.START_DEADLINE
    result = {"accepted": True, "checked_utc": datetime.now(timezone.utc).isoformat(), "export_executed": False,
        "network_requests": 0, "new_images": 21, "image_bytes": 167403, "public_image_copies": copies,
        "preflight_sha256": SHA(FOLDER / "v37-preflight.json"),
        "map_bindings": [{"path": p, "sha256": h} for p, h in sorted(bindings.items())],
        "expected_after_export": expected, "workspace_total_budget": None,
        "max_child_export_seconds": 600, "max_parent_wall_seconds": 720,
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, timeout=30).decode().strip(),
        "disk_free_before_bytes": free, "browser_acceptance_pending": True,
        "scope": "Frozen Source15 and634-image v36 closure plus exactly21 new originals and the accepted two-script Toplist repair. The v36 image layer has48 actual rendered targets and3 inactive CSS assets; its full browser gate failed and is not presented as a pass. Original source, prior versions and private evidence unchanged.",
        "ui_revision_before_browser": "21 static news references plus actual Toplist runtime and two body.wide CSS buttons; retain the commented lion-top exclusion and inspect real controls without invented DOM.",
        "parent_template_sha256": pins["execute_v37_parent_once.py"],
        "parent_binding_strategy": "Keep the frozen template. Create a separate bound sibling changing only runner/gate SHA constants; root then verifies and authorizes that sibling."}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    assert runner.validate_root_acceptance(builder)["gate"]["accepted"]
    print(json.dumps({"accepted": True, "new_images": 21, "bindings": len(bindings), "browser_pending": True}))


if __name__ == "__main__":
    main()
