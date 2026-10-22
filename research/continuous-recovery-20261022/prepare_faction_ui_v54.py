"""Prepare a fixed three-icon later-source supplement without editing sources."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research/continuous-recovery-20261022"
DEST = BASE / "integration/related-faction-icons-v54"
SOURCE_ACCEPT = BASE / "root-coolwow2-item-source-acceptance.json"
AUDIT = BASE / "faction-related-candidates/semantic-usage-audit.json"
FLOOR = 11005853696


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write(path: Path, value: object) -> str:
    data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()
    if path.exists():
        assert path.read_bytes() == data, f"refusing to replace {path}"
    else:
        path.write_bytes(data)
    return sha(data)


def main() -> None:
    assert shutil.disk_usage(ROOT).free >= FLOOR
    assert not DEST.exists(), "prepared inputs are immutable"
    source_bytes = SOURCE_ACCEPT.read_bytes()
    audit_bytes = AUDIT.read_bytes()
    assert sha(audit_bytes) == "5a78c3f5494a0e1551d2a1f5a56983af1ab7c3f647351271eaa4b3a018410702"
    source = json.loads(source_bytes)
    audit = json.loads(audit_bytes)
    assert source["accepted_sources"] is True
    assert source["accepted_for_browser_supplement"] is False
    entries = []
    (DEST / "assets").mkdir(parents=True)
    for record in source["records"]:
        filename = Path(record["repository_path"]).name
        gifname = Path(filename).stem + ".gif"
        original = ROOT / record["curated_payload"]
        data = original.read_bytes()
        assert len(data) == record["length"] and sha(data) == record["sha256"]
        assert audit["usage_counts"][gifname] in (58, 25, 2)
        target = "/info/basics/factions/images/icons/" + gifname
        page_routes = audit["source16_routes_by_target"][gifname]
        out = DEST / "assets" / filename
        out.write_bytes(data)
        entries.append({
            **{key: record[key] for key in (
                "repository_path", "source_url", "current_observed_utc", "sha256",
                "git_blob_sha1", "length", "format", "width", "height", "frames",
                "original_capture_timestamp", "classification",
            )},
            "target_route": target,
            "route": "/__offline/related-faction-icons/" + filename,
            "payload_path": relative(out),
            "page_routes": page_routes,
            "source_occurrence_count": audit["usage_counts"][gifname],
            "role": "Incendic Rod item icon" if "Wand" in filename else "Recipe and design reward icon",
            "original_gif_pixel_identity": "unknown",
        })
    assert len(entries) == 3 and sum(e["length"] for e in entries) == 3587
    now = datetime.now(timezone.utc).isoformat()
    decision = {
        "schema": "wow-related-faction-icon-decision/v1",
        "decided_utc": now,
        "accepted_for_derived_trial": True,
        "source_acceptance": relative(SOURCE_ACCEPT),
        "source_acceptance_sha256": sha(source_bytes),
        "semantic_audit": relative(AUDIT),
        "semantic_audit_sha256": sha(audit_bytes),
        "source_manifest_sha256": audit["scope"]["source16_build_manifest_sha256"],
        "repository_url": source["repository_url"],
        "commit_sha": source["commit_sha"],
        "tree_sha": source["tree_sha"],
        "classification": "later_related_source",
        "original_capture_timestamp": None,
        "historical_original_images_recovered": 0,
        "images_reencoded": False,
        "rationale": "The historical reward scripts explicitly request these three standard icon names. The later repository provides matching named JPEG artwork; a separate route and visible source notice identify this as a related supplement. The original GIF identity and dimensions remain unknown.",
        "allowed_targets": [e["target_route"] for e in entries],
        "allowed_page_routes": sorted({r for e in entries for r in e["page_routes"]}),
        "entry_count": 3,
        "source_bytes": 3587,
        "required_browser_acceptance": [
            "All eleven affected pages load the canonical JPEGs through the real route adapter without request fulfillment.",
            "The two visible faction table tabs and all four reputation brackets remain usable; reward-name tooltips work.",
            "The icons decode at 36 by 36 pixels, fit the existing reward cells and retain original source bytes.",
            "The notice and local source catalog identify the 2015 repository supplement and unknown original capture.",
        ],
    }
    decision_sha = write(DEST / "decision.json", decision)
    source_meta = {key: source[key] for key in (
        "repository_url", "commit_sha", "tree_sha", "repository_commit_date_utc",
        "original_capture_timestamp",
    )}
    source_meta["classification"] = "later_related_source"
    image_map = {
        "schema": "wow-related-faction-icon-map/v1",
        "decision": relative(DEST / "decision.json"),
        "decision_sha256": decision_sha,
        "source_acceptance": relative(SOURCE_ACCEPT),
        "source_acceptance_sha256": sha(source_bytes),
        "semantic_audit": relative(AUDIT),
        "semantic_audit_sha256": sha(audit_bytes),
        "source_manifest_sha256": decision["source_manifest_sha256"],
        "source": source_meta,
        "entry_count": 3,
        "entries": entries,
    }
    map_sha = write(DEST / "input-map.json", image_map)
    pins = {
        "map_sha256": map_sha,
        "decision_sha256": decision_sha,
        "source_acceptance_sha256": sha(source_bytes),
        "semantic_audit_sha256": sha(audit_bytes),
        "entry_count": 3,
        "source_bytes": 3587,
        "affected_page_count": len(decision["allowed_page_routes"]),
        "source_occurrences": sum(e["source_occurrence_count"] for e in entries),
        "new_network_requests": 0,
    }
    write(DEST / "root-input-pins.json", pins)
    assert shutil.disk_usage(ROOT).free >= FLOOR
    print(json.dumps(pins))


if __name__ == "__main__":
    main()
