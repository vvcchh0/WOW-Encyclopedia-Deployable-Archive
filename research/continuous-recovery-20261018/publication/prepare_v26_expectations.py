"""Set root's independently selected v26 export expectations from source receipts."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "research/continuous-recovery-20261018"
SITE = ROOT / ".scratch/pages-resources-20261016-v25"
OUT = BASE / "publication/v26-export-expectations.json"
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not OUT.exists()
    previous_path = SITE / "export-provenance.json"
    assert sha(previous_path) == "e0f6d3d631091d091ed4e515030e64136eda6b17368236f8e815453a141d579e"
    prior = read(previous_path)
    by_route = {item["route"]: item for item in prior["files"]}
    old_paths = {item["output_path"] for item in prior["files"]}
    receipts = [BASE / "publication/root-neighbors5-source-acceptance.json", BASE / "publication/root-news9-source-acceptance.json"]
    accepted = []
    for path in receipts:
        data = read(path)
        assert data["accepted"]
        accepted.extend(data["accepted_images"])
    assert len(accepted) == 13
    new_paths = {urlsplit(item["original"]).path.lstrip("/") for item in accepted}
    assert len(new_paths) == 13 and not (new_paths & old_paths)
    allowed = {"__offline/route-map.json", "__offline/pages_runtime.js", "__offline/related-images/index.html"}
    for group in prior["guide_image_collections"]["groups"]:
        for key in ["guide_route", "gallery_route"]:
            allowed.add(by_route[group[key]]["output_path"])
    news = read(receipts[1])["accepted_images"]
    news_rows = {item["original"]: item for item in read(BASE / "local-audit/news-transport-unknowns-v25.json")["rows"]}
    references = {}
    for item in news:
        original = item["original"]
        refs = news_rows[original]["v25_missing_marker_refs"]
        for ref in refs:
            page = ref["page"]
            assert page in old_paths and ".." not in Path(page).parts
            text = (SITE / page).read_text(encoding="utf-8")
            line = text.splitlines()[ref["line"] - 1]
            assert quote(original, safe="") in line and "missing-image.svg" in line
            allowed.add(page)
        references[original] = len(refs)
    assert sum(references.values()) == 10
    result = {"accepted": True, "checked_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Expected input set and allowed differences; this is not export acceptance.",
              "new_output_paths": sorted(new_paths), "allowed_changed_output_paths": sorted(allowed),
              "stats": {"source_records": 8357, "image_overlay_records": 196, "primary_image_overlay_records": 125,
                        "supplement_image_overlay_records": 71, "output_files": 8654},
              "guide_collection_images": 39, "new_news_marker_references": references,
              "expected_static_counts": {"static_text_files": 1104, "unique_missing_images": 1173,
                                         "missing_occurrences": 1932, "news_unique_missing_images": 543,
                                         "news_missing_occurrences": 547},
              "source_receipts": [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p)} for p in receipts],
              "network_requests": 0, "export_executed": False}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"new_images": len(new_paths), "allowed_changed_paths": len(allowed), "news_references": sum(references.values())}))

if __name__ == "__main__":
    main()
