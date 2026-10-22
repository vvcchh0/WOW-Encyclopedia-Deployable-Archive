"""Accept ten same-class artwork correspondences and prepare twenty exact JPEGs."""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import shutil
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DEST = HERE / "integration/related-talent-icons-v55"
AUDIT = HERE / "talent-icon-reuse-audit/audit.json"
BASE_MAP = ROOT / "research/continuous-recovery-20261021/integration/related-talent-icons/input-map.json"
ACCEPTANCE = ROOT / "research/continuous-recovery-20261021/publication/root-talent-related-source-acceptance.json"
ZIP = ROOT / "research/continuous-recovery-20261021/network/talent-repo-zip01/runtime/private/raw/attempt-01-direct.body"
FLOOR = 11005853696
sha = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_bytes())
rel = lambda p: p.relative_to(ROOT).as_posix()


def write(path, value):
    assert not path.exists(), path
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()
    path.write_bytes(payload)
    return sha(payload)


def main():
    assert not DEST.exists()
    assert shutil.disk_usage(ROOT).free >= FLOOR
    audit_bytes = AUDIT.read_bytes()
    assert sha(audit_bytes) == "fe8b6dfb6229e6c63eefafef778cffaa205b40fca9e8652389f823f64f98b520"
    audit, base = json.loads(audit_bytes), read(BASE_MAP)
    assert sha(BASE_MAP.read_bytes()) == "db2295c57b336be03b1fcccdb5a86373e4e95047b4be8e56647a1c2c95970092"
    assert sha(ACCEPTANCE.read_bytes()) == "4f05d6ab9ee61691cd6440ccd549fc756cd99424b3840ff92b0955c5bad53465"
    assert sha(ZIP.read_bytes()) == "52cd20ed7509943d5a386c95888686f8ea043c051cb367d8efe779b2a191095f"
    images = {e["repository_path"]: e for e in audit["image_evidence"]}
    assert len(audit["recommendations"]) == 10
    (DEST / "assets").mkdir(parents=True)
    entries = []
    with zipfile.ZipFile(ZIP) as archive:
        for recommendation in audit["recommendations"]:
            old = recommendation["old_target"]
            evidence = old["old_data_evidence"]
            class_name = old["class"]
            class_route = "/shared/global/talents/" + class_name + "/data.js"
            current_data = ROOT / ".scratch/pages-resources-20261022-v54" / class_route.lstrip("/")
            assert sha(current_data.read_bytes()) == evidence["v52_sha256"], class_route
            source_data = ROOT / evidence["Source16_path"]
            assert sha(source_data.read_bytes()) == evidence["Source16_sha256"]
            later_evidence = recommendation["later_talent"]["data_evidence"]
            later_data = archive.read(later_evidence["zip_member"])
            assert sha(later_data) == later_evidence["sha256"]
            assert hashlib.sha1(b"blob " + str(len(later_data)).encode() + b"\0" + later_data).hexdigest() == later_evidence["git_blob_sha1"]
            old_lines = current_data.read_text(encoding="utf-8").splitlines()
            assert any(old["talent"] in old_lines[line - 1] for line in evidence["talent_assignment_lines"])
            new_lines = later_data.decode("utf-8-sig").splitlines()
            assert any(recommendation["later_talent"]["title"] in new_lines[line - 1] for line in later_evidence["talent_assignment_lines"])
            for candidate in recommendation["later_images"]:
                item = images[candidate["evidence_id"]]
                state = candidate["state"]
                target = next(r for r in old["routes"] if r.endswith("-off.jpg") == (state == "off"))
                assert target not in {e["route"] for e in base["entries"]}
                assert item["accepted_986_is_direct_exact_route"] is False
                assert item["repository_path"].startswith("shared/global/talents/" + class_name + "/images/")
                assert not (ROOT / ".scratch/offline-non-gallery-20261021-v16/site" / target.lstrip("/")).exists()
                data = archive.read(item["zip_member"])
                assert data == (ROOT / item["extracted_path"]).read_bytes()
                assert sha(data) == item["sha256"] and len(data) == item["bytes"]
                blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                assert blob == item["git_blob_sha1"]
                with Image.open(io.BytesIO(data)) as image:
                    assert image.format == "JPEG" and image.size == (36, 36) and getattr(image, "n_frames", 1) == 1
                    image.load()
                out = DEST / "assets" / (recommendation["id"] + "-" + state + ".jpg")
                out.write_bytes(data)
                entries.append({
                    "route": target, "repository_path": item["repository_path"], "payload_path": rel(out),
                    "sha256": item["sha256"], "git_blob_sha1": blob, "length": len(data),
                    "format": "JPEG", "width": 36, "height": 36, "frames": 1,
                    "class": class_name, "talent": old["talent"], "state": state,
                    "page_route": "/info/classes/" + class_name + "/talents.html",
                    "classification": "later_related_source", "original_capture_timestamp": None,
                    "original_2008_pixel_identity": "unknown",
                    "mapping_id": recommendation["id"], "mapping_reason": recommendation["reason"],
                    "old_data_route": class_route, "old_data_sha256": evidence["v52_sha256"],
                    "old_data_talent_lines": evidence["talent_assignment_lines"],
                    "later_data_repository_path": later_evidence["zip_member"].split("/", 1)[1],
                    "later_data_sha256": later_evidence["sha256"],
                    "later_data_talent_lines": later_evidence["talent_assignment_lines"],
                })
    assert len(entries) == 20 and len({e["route"] for e in entries}) == 20
    source_bytes = sum(e["length"] for e in entries)
    decision = {
        "schema": "wow-related-talent-icon-decision/v2", "decided_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for_derived_trial": True,
        "base_map": rel(BASE_MAP), "base_map_sha256": sha(BASE_MAP.read_bytes()),
        "base_icon_count": 986, "mapped_icon_count": 20, "icon_count": 1006,
        "mapped_source_bytes": source_bytes, "semantic_audit": rel(AUDIT), "semantic_audit_sha256": sha(audit_bytes),
        "source_acceptance": rel(ACCEPTANCE), "source_acceptance_sha256": sha(ACCEPTANCE.read_bytes()),
        "source": base["source"], "classification": "later_related_source", "original_capture_timestamp": None,
        "original_2008_images_recovered": 0, "images_reencoded": False,
        "allowed_targets": [e["route"] for e in entries], "allowed_source_paths": [e["repository_path"] for e in entries],
        "scope": "Ten same-class talents moved to another tree or changed spelling. Only artwork is supplied; the 2008 talent data, descriptions, ranks and behavior stay unchanged.",
        "excluded": "Cross-class same-name candidates, Druid Grasp guesses, backgrounds and all other unmapped files.",
        "entries": entries,
        "required_browser_acceptance": "Four original class calculators display all twenty active/inactive images from actual output with unchanged 2008 data and legal rank, tooltip, save/reload behavior.",
    }
    decision_sha = write(DEST / "decision.json", decision)
    image_map = {
        "schema": "wow-related-talent-icon-map/v2", "base_map": rel(BASE_MAP),
        "base_map_sha256": sha(BASE_MAP.read_bytes()), "decision": rel(DEST / "decision.json"),
        "decision_sha256": decision_sha, "source_acceptance": rel(ACCEPTANCE),
        "source_acceptance_sha256": sha(ACCEPTANCE.read_bytes()), "semantic_audit": rel(AUDIT),
        "semantic_audit_sha256": sha(audit_bytes), "source": base["source"],
        "base_icon_count": 986, "mapped_icon_count": 20, "icon_count": 1006,
        "mapped_source_bytes": source_bytes, "entries": entries,
    }
    map_sha = write(DEST / "input-map.json", image_map)
    pins = {"map_sha256": map_sha, "decision_sha256": decision_sha,
        "base_map_sha256": sha(BASE_MAP.read_bytes()), "semantic_audit_sha256": sha(audit_bytes),
        "source_acceptance_sha256": sha(ACCEPTANCE.read_bytes()), "base_icon_count": 986,
        "mapped_icon_count": 20, "icon_count": 1006, "mapped_source_bytes": source_bytes,
        "new_network_requests": 0, "images_reencoded": False}
    write(DEST / "root-input-pins.json", pins)
    assert shutil.disk_usage(ROOT).free >= FLOOR
    print(json.dumps(pins))


if __name__ == "__main__":
    main()
