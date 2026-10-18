"""Independently read every declared export object and compare the frozen baseline.

This checker is offline. The root must supply the expected new routes from its
source acceptance; the exporter cannot choose its own acceptance target.
"""
import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[3]
FLOOR = 11005853696

def read(path):
    return json.loads(path.read_bytes())

def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

def local(value):
    path = (ROOT / value).resolve()
    path.relative_to(ROOT.resolve())
    return path

def index(data):
    result = {}
    for record in data["files"]:
        name = record["output_path"]
        pure = PurePosixPath(name)
        assert name and not pure.is_absolute() and ".." not in pure.parts
        assert "\\" not in name and ":" not in name and name not in result
        result[name] = record
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", required=True)
    parser.add_argument("--previous", required=True)
    parser.add_argument("--previous-provenance-sha256", required=True)
    parser.add_argument("--expectations", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    site, previous = local(args.site), local(args.previous)
    output = local(args.output)
    assert not output.exists(), "preserve completed acceptance"
    assert shutil.disk_usage(ROOT).free >= FLOOR
    started = datetime.now(timezone.utc)
    previous_provenance = previous / "export-provenance.json"
    assert sha(previous_provenance) == args.previous_provenance_sha256
    old, new = read(previous_provenance), read(site / "export-provenance.json")
    expected = read(local(args.expectations))
    assert expected["accepted"] is True
    before, after = index(old), index(new)
    assert set(before) <= set(after), "old export paths removed"
    new_paths = set(expected["new_output_paths"])
    assert set(after) - set(before) == new_paths
    allowed_changes = set(expected["allowed_changed_output_paths"])
    changed = []
    for name, record in after.items():
        if name not in before:
            continue
        prior = before[name]
        if prior.get("role") == "image_overlay":
            assert prior == record, ("prior overlay metadata changed", name)
        if (record["derived_sha256"], record["derived_length"]) != (prior["derived_sha256"], prior["derived_length"]):
            assert name in allowed_changes, ("unplanned old object change", name)
            changed.append(name)
    checked_bytes = 0
    for number, (name, record) in enumerate(sorted(after.items()), 1):
        path = site / name
        assert path.is_file() and not path.is_symlink()
        assert path.resolve().is_relative_to(site.resolve())
        assert path.stat().st_size == record["derived_length"], name
        assert sha(path) == record["derived_sha256"], name
        checked_bytes += path.stat().st_size
        if number % 1000 == 0:
            print(json.dumps({"checked_files": number, "total_files": len(after)}), flush=True)
    actual = {path.relative_to(site).as_posix() for path in site.rglob("*") if path.is_file()}
    assert actual == set(after) | {"export-provenance.json"}
    assert new["stats"]["source_records"] == old["stats"]["source_records"] == 8357
    assert new["stats"]["output_files"] == len(after)
    assert new["stats"]["image_overlay_records"] == old["stats"]["image_overlay_records"] + len(new_paths)
    for key, value in expected.get("stats", {}).items():
        assert new["stats"].get(key) == value, (key, new["stats"].get(key), value)
    if "guide_collection_images" in expected:
        assert new["guide_image_collections"]["image_count"] == expected["guide_collection_images"]
    assert shutil.disk_usage(ROOT).free >= FLOOR
    result = {
        "accepted": True,
        "started_utc": started.isoformat(),
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "site": site.relative_to(ROOT).as_posix(),
        "previous": previous.relative_to(ROOT).as_posix(),
        "previous_provenance_sha256": sha(previous_provenance),
        "expectations_sha256": sha(local(args.expectations)),
        "declared_files": len(after),
        "actual_files": len(actual),
        "all_declared_files_rehashed": True,
        "checked_bytes": checked_bytes,
        "new_output_paths": sorted(new_paths),
        "changed_output_paths": sorted(changed),
        "prior_overlay_metadata_preserved": True,
        "export_provenance_sha256": sha(site / "export-provenance.json"),
        "disk_free_after_bytes": shutil.disk_usage(ROOT).free,
        "network_requests": 0,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result), flush=True)

if __name__ == "__main__":
    main()
