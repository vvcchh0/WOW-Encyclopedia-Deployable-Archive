"""Review the zero-resource-delta v34 preparation before its one-shot export."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "research/continuous-recovery-20261019"
FOLDER = RUN / "integration/v34"
TARGET = RUN / "publication/root-v34-input-acceptance.json"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    assert not TARGET.exists()
    assert sha(FOLDER / "execute_v34.py") == "032548dfe7949dd63d4b55713bb79c72a136919b4d277bac48465b455a7af2d0"
    spec = importlib.util.spec_from_file_location("root_v34_runner", FOLDER / "execute_v34.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    builder = runner.load_builder()
    preflight = runner.guard_prepared(builder)
    runner.guard_outputs()
    bindings = runner.required_bindings(builder)
    assert len(bindings) == 54 and runner.MAX_OUTPUT_BYTES == 650000000
    assert runner.START_DEADLINE == datetime(2026, 10, 19, 13, 30, tzinfo=timezone.utc)
    assert datetime.now(timezone.utc) < runner.START_DEADLINE
    assert preflight["new_image_count"] == preflight["new_image_bytes"] == 0
    assert preflight["expected_after_export"]["primary_overlays"] == 459
    assert preflight["expected_after_export"]["supplement_overlays"] == 100
    assert builder.SOURCE_SITE == ROOT / ".scratch/offline-navigation-20261015-v15/site"
    assert builder.SOURCE_MANIFEST == ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
    for role in ("primary", "supplement"):
        assert not json.loads((FOLDER / f"v34-{role}-source-map.json").read_bytes()).get("items", [])
    assert shutil.disk_usage(ROOT).free >= 11005853696 + 650000000
    report = {"accepted": True, "checked_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Source15 and acceptedv33 closure, zero newimage delta, only exact-route contest navigation fallback",
        "export_executed": False, "network_requests": 0, "new_images": 0, "image_bytes": 0,
        "public_image_copies": [], "preflight_sha256": sha(FOLDER / "v34-preflight.json"),
        "map_bindings": [{"path": p, "sha256": digest} for p, digest in sorted(bindings.items())],
        "expected_after_export": preflight["expected_after_export"],
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "max_output_bytes": 650000000, "max_execution_wall_seconds": 900,
        "start_deadline_utc": "2026-10-19T13:30:00Z", "disk_free_before_bytes": shutil.disk_usage(ROOT).free}
    TARGET.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    assert runner.validate_root_acceptance(builder, preflight)["binding_count"] == 54
    print(json.dumps({"accepted": True, "bindings": 54, "new_images": 0, "disk_free": report["disk_free_before_bytes"]}))
