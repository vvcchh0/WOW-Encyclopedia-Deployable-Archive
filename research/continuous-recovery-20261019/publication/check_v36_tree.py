"""Read and hash the complete new tree, preserving the accepted v35 baseline."""
import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
SITE = ROOT / ".scratch/pages-resources-20261019-v36"
BASE = ROOT / ".scratch/pages-resources-20261019-v35"
INPUT = PUB / "root-v36-input-acceptance.json"
OUT = PUB / "root-v36-tree-acceptance.json"
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
READ = lambda p: json.loads(p.read_bytes())


def check_record(row):
    relative = row["output_path"]
    path = SITE / relative
    path.resolve().relative_to(SITE.resolve())
    assert path.is_file() and not path.is_symlink(), relative
    assert path.stat().st_size == row["derived_length"], relative
    assert SHA(path) == row["derived_sha256"], relative
    return path.stat().st_size


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provenance-sha", required=True)
    parser.add_argument("--worker", action="store_true")
    args = parser.parse_args()
    assert not OUT.exists()
    if not args.worker:
        with (PUB / "v36-tree-check.stdout.log").open("xb") as stdout, (PUB / "v36-tree-check.stderr.log").open("xb") as stderr:
            p = subprocess.run([sys.executable, "-B", "-X", "utf8", str(Path(__file__).resolve()),
                "--provenance-sha", args.provenance_sha, "--worker"], cwd=ROOT, stdout=stdout, stderr=stderr,
                check=False, timeout=240)
        assert p.returncode == 0 and READ(OUT)["accepted"]
        print(json.dumps({k: READ(OUT)[k] for k in ("accepted", "declared_files", "actual_files", "tree_bytes", "new_images", "elapsed_seconds")}))
        return
    started = time.monotonic()
    assert shutil.disk_usage(ROOT).free >= 11005853696
    gate = READ(INPUT)
    assert gate["accepted"] and gate["new_images"] == 51
    for row in gate["map_bindings"]:
        assert SHA(ROOT / row["path"]) == row["sha256"], row["path"]
    provenance_path = SITE / "export-provenance.json"
    assert SHA(provenance_path) == args.provenance_sha
    prov = READ(provenance_path)
    assert prov["source_manifest_sha256"] == "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
    rows = prov["files"]
    assert len(rows) == len({r["output_path"] for r in rows}) == 9092
    actual = set()
    for current, dirs, names in os.walk(SITE, followlinks=False):
        directory = Path(current)
        assert all(not (directory / d).is_symlink() for d in dirs)
        for name in names:
            path = directory / name
            assert not path.is_symlink()
            actual.add(path.relative_to(SITE).as_posix())
    assert len(actual) == 9093 and actual == {r["output_path"] for r in rows} | {"export-provenance.json"}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        sizes = list(pool.map(check_record, rows))
    assert SHA(BASE / "export-provenance.json") == "f37f73ba4cdd63b1190b895a2d770dd94b2b764ad5fc219a5fd34bad93a3c4d0"
    before = {r["output_path"]: r for r in READ(BASE / "export-provenance.json")["files"]}
    after = {r["output_path"]: r for r in rows}
    added = set(after) - set(before)
    assert not (set(before) - set(after))
    items = READ(ROOT / "research/continuous-recovery-20261019/integration/v36/v36-primary-source-map.json")["items"]
    expected_new = {urlsplit(r["original"]).path.lstrip("/"): r for r in items}
    assert len(added) == len(expected_new) == 51 and added == set(expected_new)
    for path, item in expected_new.items():
        assert after[path]["role"] == "image_overlay"
        assert (after[path]["derived_sha256"], after[path]["derived_length"]) == (item["sha256"], item["length"])
    old = {p: r for p, r in before.items() if r.get("role") == "image_overlay"}
    assert len(old) == 583 and all(after[p] == row for p, row in old.items())
    assert sum(r.get("role") == "image_overlay" for r in rows) == 634
    common_changed = sorted(p for p in before if (before[p]["derived_sha256"], before[p]["derived_length"]) !=
                            (after[p]["derived_sha256"], after[p]["derived_length"]))
    stats = prov["stats"]
    assert stats["source_records"] == 8357 and stats["output_files"] == 9092
    assert (stats["guide_image_collection_images"], stats["guide_preview_count"]) == (39, 22)
    assert shutil.disk_usage(ROOT).free >= 11005853696
    result = {"accepted": True, "checked_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": time.monotonic() - started, "hard_parent_timeout_seconds": 240,
        "local_site": SITE.relative_to(ROOT).as_posix(), "input_gate_sha256": SHA(INPUT),
        "provenance_sha256": SHA(provenance_path), "declared_files": 9092, "actual_files": 9093,
        "tree_bytes": sum(sizes) + provenance_path.stat().st_size, "new_images": 51,
        "new_image_bytes": sum(r["length"] for r in items), "image_overlays": 634,
        "old_overlay_metadata_unchanged": 583, "new_paths": sorted(added),
        "common_changed_paths": common_changed, "removed_paths": [], "stats": stats,
        "disk_free_bytes": shutil.disk_usage(ROOT).free, "network_requests": 0, "published": False,
        "scope": "Every declared output file was independently read and checked against exact length/digest, actual path set and accepted51-image delta. Browser behavior and review of common HTML/CSS changes remain separate."}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
