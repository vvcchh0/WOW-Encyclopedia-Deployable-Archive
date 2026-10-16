#!/usr/bin/env python3
"""Build the independently accepted six-group guide-preview map.

This helper deliberately leaves the frozen v1 map in place.  It copies the
five accepted v1 group identities and preview records, checks them against the
root22 receipt, and appends the three root-accepted City Attacks previews.
The resulting map contains only local route/hash/length/capture fields; guide
relationship evidence remains in the bound audit and acceptance receipts.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
OLD_MAP = ROOT / "research/continuous-recovery-20261016/integration/guide-previews-source-map.json"
ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-guide-preview-22-acceptance.json"
AUDIT = ROOT / "research/continuous-recovery-20261016/publication/guide-preview-22-audit.json"
MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
OUTPUT = Path(__file__).resolve().parent / "guide-previews-source-map-v2.json"
RECEIPT = Path(__file__).resolve().parent / "v2-map-build-verification.json"

V1_SCHEMA = "wow-recovery.guide-preview-source-map.v1"
V2_SCHEMA = "wow-recovery.guide-preview-source-map.v2"
CITY_ROUTES = {
    "/pvp/worldpvp/images/city/thumbs/thumb-1.jpg",
    "/pvp/worldpvp/images/city/thumbs/thumb-2.jpg",
    "/pvp/worldpvp/images/city/thumbs/thumb-3.jpg",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def accepted_by_route(acceptance: dict[str, Any]) -> dict[str, dict[str, Any]]:
    checked = acceptance.get("checked")
    if acceptance.get("accepted") is not True or acceptance.get("network_requests") != 0:
        raise ValueError("root22 acceptance is not accepted local-only evidence")
    if not isinstance(checked, list) or len(checked) != 22:
        raise ValueError("root22 acceptance must contain exactly 22 records")
    result: dict[str, dict[str, Any]] = {}
    for item in checked:
        if not isinstance(item, dict) or not isinstance(item.get("route"), str):
            raise ValueError("root22 acceptance contains an invalid checked record")
        route = item["route"]
        if route in result:
            raise ValueError(f"root22 acceptance repeats route: {route}")
        if item.get("accepted") is not True:
            raise ValueError(f"root22 acceptance rejects route: {route}")
        result[route] = item
    if set(result) & CITY_ROUTES != CITY_ROUTES:
        raise ValueError("root22 acceptance does not contain all City Attacks routes")
    if len(set(result) - CITY_ROUTES) != 19:
        raise ValueError("root22 acceptance does not contain exactly 19 prior routes")
    return result


def preview_from_acceptance(route: str, accepted: dict[str, Any]) -> dict[str, Any]:
    if accepted.get("route") != route:
        raise ValueError(f"acceptance route mismatch: {route}")
    return {
        "route": route,
        "sha256": str(accepted.get("sha256") or "").casefold(),
        "length": int(accepted.get("length")),
        "capture_timestamp": str(accepted.get("capture_from_frozen_manifest") or ""),
    }


def main() -> int:
    for path in (OLD_MAP, ACCEPTANCE, AUDIT, MANIFEST):
        if not path.is_file():
            raise FileNotFoundError(path)
    if OUTPUT.exists() or RECEIPT.exists():
        raise FileExistsError("v2 map or verification receipt already exists; refusing overwrite")

    old_map = read_json(OLD_MAP)
    acceptance = read_json(ACCEPTANCE)
    audit = read_json(AUDIT)
    manifest = read_json(MANIFEST)
    if old_map.get("schema") != V1_SCHEMA:
        raise ValueError("frozen input map is not the v1 map")
    if audit.get("schema") != "wow-recovery.guide-preview-union-audit.v1":
        raise ValueError("union audit schema is unexpected")
    counts = audit.get("counts")
    if not isinstance(counts, dict) or counts.get("target_count") != 22 or counts.get("groups") != 6:
        raise ValueError("union audit counts are not 6 groups / 22 previews")
    if acceptance.get("audit_sha256") != sha256(AUDIT):
        raise ValueError("root22 acceptance does not bind the union audit")
    accepted = accepted_by_route(acceptance)
    audit_routes = {item.get("route") for item in audit.get("items", []) if isinstance(item, dict)}
    if audit_routes != set(accepted):
        raise ValueError("union audit and root22 acceptance route sets differ")

    raw_old_groups = old_map.get("groups")
    if not isinstance(raw_old_groups, list) or len(raw_old_groups) != 5:
        raise ValueError("frozen v1 map must contain exactly five groups")
    groups: list[dict[str, Any]] = []
    seen_routes: set[str] = set()
    for raw_group in raw_old_groups:
        if not isinstance(raw_group, dict):
            raise ValueError("frozen v1 group is invalid")
        for key in ("group_id", "label", "gallery_route", "guide_route"):
            if not isinstance(raw_group.get(key), str) or not raw_group[key]:
                raise ValueError(f"frozen v1 group lacks {key}")
        raw_previews = raw_group.get("previews")
        if not isinstance(raw_previews, list) or not raw_previews:
            raise ValueError(f"frozen v1 group has no previews: {raw_group['group_id']}")
        previews: list[dict[str, Any]] = []
        for raw_preview in raw_previews:
            if not isinstance(raw_preview, dict):
                raise ValueError("frozen v1 preview is invalid")
            route = raw_preview.get("route")
            if not isinstance(route, str) or route in seen_routes:
                raise ValueError(f"frozen v1 preview route is invalid or repeated: {route}")
            seen_routes.add(route)
            item = accepted.get(route)
            if item is None:
                raise ValueError(f"frozen v1 route missing from root22 acceptance: {route}")
            old_preview = preview_from_acceptance(route, item)
            # Require the five old records to remain byte/date identical.
            for field in ("sha256", "length", "capture_timestamp"):
                if str(raw_preview.get(field)) != str(old_preview[field]):
                    raise ValueError(f"frozen v1 preview changed in v2 map: {route} {field}")
            previews.append(old_preview)
        groups.append(
            {
                "group_id": raw_group["group_id"],
                "label": raw_group["label"],
                "gallery_route": raw_group["gallery_route"],
                "guide_route": raw_group["guide_route"],
                "previews": previews,
            }
        )

    city_items = [accepted[route] for route in sorted(CITY_ROUTES)]
    for item in city_items:
        if item.get("source_link") != "/pvp/worldpvp/cityattacks-gallery.html":
            raise ValueError("City preview does not bind to the fixed gallery source link")
        if item.get("source_guide_route") != "/info/basics/pvpcombat.html":
            raise ValueError("City preview does not bind to the fixed guide route")
    groups.append(
        {
            "group_id": "city-attacks",
            "label": "City Attacks",
            "gallery_route": "/pvp/worldpvp/cityattacks-gallery.html",
            "guide_route": "/info/basics/pvpcombat.html",
            "previews": [preview_from_acceptance(item["route"], item) for item in city_items],
        }
    )
    if len(seen_routes) != 19 or len({item["route"] for item in groups[-1]["previews"]}) != 3:
        raise ValueError("v2 route conservation failed before write")

    manifest_sha = sha256(MANIFEST)
    payload = {
        "schema": V2_SCHEMA,
        "purpose": "Accepted local guide-page preview bytes shown in six gallery pages; City Attacks remains guide-group related and has no dynamic full-image alias.",
        "source_acceptance": {"path": rel(ACCEPTANCE), "sha256": sha256(ACCEPTANCE)},
        "source_acceptance_sha256": sha256(ACCEPTANCE),
        "source_audit": {"path": rel(AUDIT), "sha256": sha256(AUDIT)},
        "source_audit_sha256": sha256(AUDIT),
        "source_manifest": {"path": rel(MANIFEST), "sha256": manifest_sha},
        "source_manifest_sha256": manifest_sha,
        "anchor_timestamp": str(manifest.get("anchor_timestamp") or ""),
        "groups": groups,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_sha = sha256(OUTPUT)
    receipt = {
        "schema": "wow-recovery.guide-preview-v2-map-build-verification.v1",
        "executed_by": "local_recovery_20261016",
        "network_requests": 0,
        "output": {"path": rel(OUTPUT), "sha256": output_sha, "group_count": 6, "preview_count": 22},
        "inputs": {
            rel(OLD_MAP): sha256(OLD_MAP),
            rel(ACCEPTANCE): sha256(ACCEPTANCE),
            rel(AUDIT): sha256(AUDIT),
            rel(MANIFEST): manifest_sha,
        },
        "route_conservation": {"prior_v1": 19, "city_attacks": 3, "total_v2": 22},
        "city_route_policy": "fixed three guide-preview routes only; no dynamic_full_candidate, ssN alias, or slot numbering",
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
