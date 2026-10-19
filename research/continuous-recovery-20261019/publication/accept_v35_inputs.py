"""Root review of the fixed24-image v35 export inputs; no site is built here."""
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
FOLDER = RUN / "integration/v35"
OUT = RUN / "publication/root-v35-input-acceptance.json"
READ = lambda p: json.loads(p.read_bytes())
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    runner_path = FOLDER / "execute_v35.py"
    assert SHA(runner_path) == "beb62d81d7a65625c594e03625dfa78474cc12f6584462a89acd5a95e0c85ee0"
    assert SHA(FOLDER / "build_pages_v35.py") == "0fdce2a703f3e4c1f7b2e122391f89ce54093cae30ac3fc7d97d6fd24b8d7fb5"
    assert SHA(FOLDER / "v35-preflight.json") == "f8514ee2577aabab70c8adf2920962d10d0d81e6d7ea3287997de099e383ef71"
    calls = [n for n in ast.walk(ast.parse(runner_path.read_text(encoding="utf-8")))
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "export_pages"]
    assert len(calls) == 1
    kwargs = {k.arg: k.value for k in calls[0].keywords}
    assert isinstance(kwargs["max_bytes"], ast.Constant) and kwargs["max_bytes"].value is None
    spec = importlib.util.spec_from_file_location("root_v35_input_runner", runner_path)
    runner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = runner
    spec.loader.exec_module(runner)
    builder = runner.load_builder()
    preflight = runner.guard_prepared(builder)
    runner.guard_outputs()
    bindings = runner.required_bindings(builder)
    assert builder.SOURCE_SITE == ROOT / ".scratch/offline-navigation-20261015-v15/site"
    assert builder.SOURCE_MANIFEST == ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
    assert preflight["new_image_count"] == 24 and preflight["new_image_bytes"] == 191943
    expected = preflight["expected_after_export"]
    assert (expected["primary_overlays"], expected["supplement_overlays"], expected["total_overlays"],
            expected["declared_files"], expected["actual_files"]) == (483, 100, 583, 9041, 9042)
    assert READ(RUN / "publication/root-v34-local-acceptance.json")["accepted"]
    bindings[(RUN / "publication/root-v34-local-acceptance.json").relative_to(ROOT).as_posix()] = SHA(RUN / "publication/root-v34-local-acceptance.json")
    source_rows = {}
    for name in ("frontier-news04", "frontier-news20a"):
        source = READ(RUN / f"publication/root-{name}-source-acceptance.json")
        public = READ(RUN / f"publication/root-{name}-public-copy-acceptance.json")
        visual_path = RUN / f"publication/root-{name}-visual-acceptance.json"
        assert source["accepted"] and public["accepted"] and READ(visual_path)["accepted"]
        assert source["failure_streak_end"] == 0
        source_by = {r["original"]: r for r in source["accepted_images"]}
        for row in public["accepted_images"]:
            original = source_by[row["original"]]
            assert (row["sha256"], row["length"], row["actual_capture_timestamp"]) == (original["sha256"], original["length"], original["actual_capture_timestamp"])
            assert row["original"] not in source_rows
            source_rows[row["original"]] = row
        bindings[visual_path.relative_to(ROOT).as_posix()] = SHA(visual_path)
    primary = READ(FOLDER / "v35-primary-source-map.json")["items"]
    assert len(primary) == len(source_rows) == 24
    assert not READ(FOLDER / "v35-supplement-source-map.json")["items"]
    copies = []
    for row in primary:
        source = source_rows[row["original"]]
        assert row["logical_url"] == row["original"]
        assert row["actual_timestamp"] == source["actual_capture_timestamp"]
        assert "20080101000000" <= row["actual_timestamp"] <= "20080512210044"
        assert (row["sha256"], row["length"], row["public_copy_path"]) == (source["sha256"], source["length"], source["local_path"])
        public_path = ROOT / row["public_copy_path"]
        assert SHA(public_path) == row["sha256"] and public_path.stat().st_size == row["length"]
        copies.append({"path": row["public_copy_path"], "sha256": row["sha256"], "length": row["length"]})
    assert sum(r["length"] for r in copies) == 191943
    free = shutil.disk_usage(ROOT).free
    assert free >= 11005853696 + 900000000
    assert datetime.now(timezone.utc) < runner.START_DEADLINE
    report = {"accepted": True, "checked_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Frozen Source15 and accepted559-image closure plus exactly24 canonical2008 news images and the accepted contest menu repair.",
        "export_executed": False, "network_requests": 0, "new_images": 24, "image_bytes": 191943,
        "public_image_copies": copies, "preflight_sha256": SHA(FOLDER / "v35-preflight.json"),
        "map_bindings": [{"path": p, "sha256": digest} for p, digest in sorted(bindings.items())],
        "expected_after_export": expected, "workspace_total_budget": None,
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, timeout=30).strip(),
        "max_execution_wall_seconds": 900, "start_deadline_utc": "2026-10-19T13:30:00Z",
        "disk_free_before_bytes": free,
        "browser_acceptance_pending": True,
        "native_input_revision_required": "Old literal-only UI input misses23 encoded missing-marker references. Additive r2 must bind all24 exact source elements and the single real Beowulf news control before browser acceptance/publication."}
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    assert runner.validate_root_acceptance(builder)["gate"]["accepted"]
    print(json.dumps({"accepted": True, "bindings": len(bindings), "new_images": 24, "image_bytes": 191943, "browser_pending": True}))


if __name__ == "__main__":
    main()
