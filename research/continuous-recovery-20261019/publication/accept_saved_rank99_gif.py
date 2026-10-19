"""Revalidate the saved wallpaper GIF after correcting its JPEG input contract."""
import copy
import hashlib
import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
PACKET = ROOT / "research/continuous-recovery-20261019/network/frontier-news20e"
RAW = PACKET / "output/raw"
OUT = PUB / "root-news20e-rank99-source-acceptance.json"
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
READ = lambda p: json.loads(p.read_bytes())


def main():
    assert not OUT.exists() and shutil.disk_usage(ROOT).free >= 11005853696
    driver = ROOT / "research/continuous-recovery-20261018/network/reusable-image-driver-v3/reusable_image_driver.py"
    assert SHA(driver) == "4a19422f0dd8e2f7e1ffdd088836c7ab80450afb91aeedc6cdb94fa4c6bfe955"
    plan_path = PACKET / "plan.json"
    assert SHA(plan_path) == "8a05c2b69bc0f8f4d360f26df7e2d5276d1494009b0429011016a99f80a8997a"
    prior = PUB / "root-frontier-news20e-source-acceptance.json"
    assert SHA(prior) == "046bcaef8972e44d23d9301cb08e747b8a41465321d78079557a5820aff8f8f1" and READ(prior)["accepted"]
    original_candidate = next(r for r in READ(plan_path)["candidates"] if r["priority"] == 99)
    candidate = copy.deepcopy(original_candidate)
    assert candidate["original"] == "http://www.worldofwarcraft.com/news/images/04-09/wallpaper/wallpaper.gif"
    candidate["expected_mime"] = ["image/gif"]
    candidate["expected"].update(mime_types=["image/gif"], pillow_formats=["GIF"], all_gif_frames=True)
    spec = importlib.util.spec_from_file_location("root_saved_rank99_validator", driver)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    cdx_path = RAW / "attempt-038-proxy-body.bin"
    parsed = module.parse_cdx(cdx_path.read_bytes())
    assert parsed["valid"] and parsed["complete"] and not parsed["resume_keys"] and len(parsed["rows"]) == 4
    row = next(r for r in parsed["rows"] if r["timestamp"] == "20080402082404" and r["original"] == candidate["original"])
    assert row["mimetype"] == "image/gif" and row["statuscode"] == "200" and row["digest"] == "CEULEW4OBEBNZR7TOFNFPQTT7ER7QLE4"
    body_path = RAW / "attempt-039-proxy-body.bin"
    headers_path = RAW / "attempt-039-proxy-headers.txt"
    body = body_path.read_bytes()
    assert len(body) == 27829 and SHA(body_path) == "9d4e2bf53b978a9790ba8c35d3dc0fd3cdc7fdec4ea15313fadded6668e6d883"
    validation = module.validate_replay(candidate, row, headers_path.read_bytes(), body, curl_exit=0)
    assert validation["accepted"] and not validation["reasons"] and validation["image_format"] == "GIF"
    assert validation["image_size"] == [260, 200] and validation["image_frame_count"] == 1
    older = next(r for r in parsed["rows"] if r["timestamp"] == "20051221010011")
    old_validation = module.validate_replay(candidate, older, (RAW / "attempt-040-proxy-headers.txt").read_bytes(),
        (RAW / "attempt-040-proxy-body.bin").read_bytes(), curl_exit=0)
    assert not old_validation["accepted"] and "cdx_digest_mismatch" in old_validation["reasons"]
    item = {"accepted": True, "original": candidate["original"], "actual_capture_timestamp": row["timestamp"],
        "mime": "image/gif", "dimensions": [260, 200], "decoded_frames": 1, "length": len(body),
        "sha256": SHA(body_path), "cdx_digest": row["digest"],
        "private_payload_path": body_path.relative_to(ROOT).as_posix(),
        "archive_memento": f'https://web.archive.org/web/{row["timestamp"]}id_/{candidate["original"]}'}
    result = {"accepted": True, "checked_utc": datetime.now(timezone.utc).isoformat(), "network_requests": 0,
        "is_network_batch": False, "accepted_images": [item], "image_bytes": len(body),
        "validation": validation, "older_capture_rejected": {"timestamp": "20051221010011", "reasons": old_validation["reasons"]},
        "bindings": [{"path": p.relative_to(ROOT).as_posix(), "sha256": SHA(p)} for p in (driver, plan_path, prior, cdx_path, body_path, headers_path)],
        "correction": "The saved request was successful, but the old JPEG expectation rejected a GIF. Only MIME/Pillow/all-frame input expectations were corrected. Exact URL, capture, CDX digest, Memento, byte limits and full frame decode remain required.",
        "scope": "Original plan and all failed observations remain unchanged. This local-only source revalidation cannot authorize a new network batch or replace its latest failure tail."}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"accepted": True, "images": 1, "bytes": len(body), "network_requests": 0, "source_sha256": SHA(OUT)}))


if __name__ == "__main__":
    main()
