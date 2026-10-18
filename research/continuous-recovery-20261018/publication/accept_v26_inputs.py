"""Check public byte copies, source bindings and preserved collection records."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "research/continuous-recovery-20261018"
OUT = BASE / "publication/root-v26-input-acceptance.json"
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not OUT.exists()
    status = read(BASE / "status.json")
    for path, expected in status["frozen_bindings"].items():
        assert sha(ROOT / path) == expected
    preflight_path = BASE / "integration/v26-combined-preflight.json"
    preflight = read(preflight_path)
    loader = preflight["loader_preflight"]
    assert loader["total_overlay_records"] == 196 and loader["primary_overlay_records"] == 125
    assert loader["supplement_overlay_records"] == 71 and loader["guide_collection_images"] == 39
    assert loader["guide_preview_images"] == 22 and loader["network_requests"] == 0
    bindings = []
    for item in preflight["input_maps"].values():
        path = ROOT / item["path"]
        assert sha(path) == item["sha256"]
        bindings.append({"path": item["path"], "sha256": sha(path)})
    accepted, copied = {}, []
    for name in ["root-neighbors5-source-acceptance.json", "root-news9-source-acceptance.json"]:
        path = BASE / "publication" / name
        data = read(path)
        assert data["accepted"]
        bindings.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)})
        accepted.update({item["original"]: item for item in data["accepted_images"]})
    maps = [BASE / "integration/v26-neighbor-supplement-source-map.json", BASE / "integration/v26-news-primary-source-map.json"]
    entries = [item for path in maps for item in read(path)["items"]]
    assert len(entries) == len(accepted) == 13
    assert {item["original"] for item in entries} == set(accepted)
    for item in entries:
        source = accepted[item["original"]]
        path = (ROOT / item["local_path"]).resolve()
        path.relative_to(BASE / "integration/accepted-images")
        assert not path.is_symlink() and path.stat().st_size == source["length"] == item["length"]
        assert sha(path) == source["sha256"] == item["sha256"]
        assert path.read_bytes() == (ROOT / source["private_payload_path"]).read_bytes()
        assert item["actual_timestamp"] == item["indexed_capture_timestamp"] == source["actual_capture_timestamp"]
        assert item["mime"] == source["mime"] == "image/jpeg"
        assert item["dimensions"] == source["dimensions"] and item["cdx_digest"] == source["cdx_digest"]
        copied.append({"path": item["local_path"], "sha256": sha(path), "length": item["length"]})
    old = read(ROOT / "research/focused-recovery-20261016-2301/local/v25-guide-image-collection-map.json")
    new = read(BASE / "integration/v26-guide-image-collection-map.json")
    old_groups, new_groups = ({item["group_id"]: item for item in data["groups"]} for data in [old, new])
    assert set(old_groups) == set(new_groups)
    prior_count, current_count = 0, 0
    for key, group in old_groups.items():
        before, after = group["images"], new_groups[key]["images"]
        assert all(item in after for item in before), key
        assert len(after) == len({item["original"] for item in after})
        prior_count += len(before)
        current_count += len(after)
    assert prior_count == 35 and current_count == 39
    site = ROOT / ".scratch/pages-resources-20261018-v26"
    assert not site.exists() and not site.with_name(site.name + ".partial").exists()
    free = shutil.disk_usage(ROOT).free
    assert free >= 11005853696
    result = {"accepted": True, "checked_utc": datetime.now(timezone.utc).isoformat(),
              "map_bindings": bindings, "preflight_sha256": sha(preflight_path),
              "public_image_copies": copied, "prior_collection_images_preserved": 35,
              "guide_collection_images": 39, "new_images": 13, "image_bytes": sum(x["length"] for x in copied),
              "network_requests": 0, "export_executed": False, "disk_free_bytes": free,
              "scope": "All13public image copies match independently accepted raw bytes; prior35collection rows preserved. Frozen inputs unchanged."}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key not in ["map_bindings", "public_image_copies"]}))

if __name__ == "__main__":
    main()
