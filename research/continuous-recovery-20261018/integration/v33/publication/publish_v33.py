#!/usr/bin/env python3
"""Prepare the root-local publication gate for the accepted v33 site.

This module is preparation-only in the local role.  It compares the completed
v33 provenance with the actual frozen v32 provenance, binds every new/changed
site object, and writes an immutable local receipt for a later root-owned
Pages publication.  It never calls GitHub, ``gh``, curl, or the publisher.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
EXPECTED_ROOT = "d:/wow_encyclopedia"
if ROOT.as_posix().casefold().rstrip("/") != EXPECTED_ROOT:
    raise RuntimeError(f"nested v33 publication root must be D:/WOW_Encyclopedia, got {ROOT}")

INTEGRATION = ROOT / "research/continuous-recovery-20261018/integration/v33"
PUB = INTEGRATION / "publication"
ROOT_PUBLICATION = ROOT / "research/continuous-recovery-20261018/publication"
SITE = ROOT / ".scratch/pages-resources-20261018-v33"
V33_PROVENANCE = SITE / "export-provenance.json"
V32_SITE = ROOT / ".scratch/pages-resources-20261018-v32"
V32_PROVENANCE = V32_SITE / "export-provenance.json"
SOURCE_MANIFEST = ROOT_PUBLICATION / "root-v33-source-receipts-manifest-r2.json"
LOCAL_GATE = ROOT_PUBLICATION / "root-v33-local-acceptance.json"
MIN_FREE_BYTES = 11_005_853_696
EXPECTED_V32_PAGES_COMMIT = "0bcb961f64ea3527bfed41bacf21e670d47a6c3c"
EXPECTED_V32_PROVENANCE_SHA256 = "a071d47b65232f723c2e74112adab521eb124d22b57aa430437646f06f50d356"
EXPECTED_EXPORTER_SHA256 = "2a6fa4256ad0853797ae10748ef7842896614d419bdb7ad208d9b258dc8e6488"
EXPECTED_HISTORICAL_EXHIBITS_SHA256 = "35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011"

V33_RECEIPTS = {
    "input": ROOT_PUBLICATION / "root-v33-input-acceptance.json",
    "export": ROOT_PUBLICATION / "root-v33-export-acceptance.json",
    "browser": ROOT_PUBLICATION / "root-v33-browser-acceptance.json",
    "static_metrics": ROOT_PUBLICATION / "root-v33-static-metrics-acceptance.json",
}
V32_RECEIPTS = {
    "local": ROOT_PUBLICATION / "root-v32-local-acceptance.json",
    "online": ROOT_PUBLICATION / "root-v32-pages-online-acceptance.json",
}
V33_INPUTS = {
    "source_manifest": SOURCE_MANIFEST,
    "primary_map": INTEGRATION / "v33-primary-source-map.json",
    "supplement_map": INTEGRATION / "v33-supplement-source-map.json",
    "impact": INTEGRATION / "v33-impact-estimate.json",
    "source_audit": INTEGRATION / "v33-source-byte-audit.json",
    "preparation": INTEGRATION / "v33-input-preparation.json",
    "preflight": INTEGRATION / "v33-preflight.json",
    "builder": INTEGRATION / "build_pages_v33.py",
    "runner": INTEGRATION / "execute_v33.py",
    "build_receipt": INTEGRATION / "v33-build-receipt.json",
    "exporter": ROOT / "tools/export_github_pages.py",
    "historical_exhibits": ROOT / "tools/historical_exhibits.py",
    "v32_provenance": V32_PROVENANCE,
    "v32_primary_map": ROOT / "research/continuous-recovery-20261018/integration/v32/v32-primary-source-map.json",
    "v32_supplement_map": ROOT / "research/continuous-recovery-20261018/integration/v32/v32-supplement-source-map.json",
    "v32_local": V32_RECEIPTS["local"],
    "v32_online": V32_RECEIPTS["online"],
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def inside(path: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"{label} escapes D:/WOW_Encyclopedia: {path}") from exc
    return resolved


def read_json(path: Path, label: str) -> dict[str, Any]:
    path = inside(path, label)
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"invalid JSON for {label}: {path}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} is not an object: {path}")
    return value


def binding(path: Path) -> dict[str, Any]:
    path = inside(path, "publication binding")
    if not path.is_file():
        raise RuntimeError(f"missing publication binding: {path}")
    return {"path": rel(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}


def verify_accepted_receipt(path: Path, label: str, provenance_sha: str) -> dict[str, Any]:
    receipt = read_json(path, label)
    if receipt.get("accepted") is not True:
        raise RuntimeError(f"{label} is not accepted")
    for key in ("export_provenance_sha256", "v33_provenance_sha256", "provenance_sha256"):
        value = receipt.get(key)
        if value not in {None, ""} and str(value).casefold() != provenance_sha.casefold():
            raise RuntimeError(f"{label} {key} differs from v33 provenance")
    return receipt


def record_fingerprint(record: dict[str, Any]) -> str:
    """Return a stable fingerprint of the complete provenance record.

    The v32 image-overlay closure is frozen as metadata as well as bytes.  A
    six-field projection would miss changes to source/origin/reference fields,
    so every record field participates in the comparison.
    """
    return json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def provenance_delta(before: dict[str, Any], after: dict[str, Any], source_manifest: dict[str, Any]) -> dict[str, Any]:
    before_rows = {str(row.get("output_path")): row for row in before.get("files", []) if isinstance(row, dict) and row.get("output_path")}
    after_rows = {str(row.get("output_path")): row for row in after.get("files", []) if isinstance(row, dict) and row.get("output_path")}
    if not before_rows or not after_rows:
        raise RuntimeError("v32/v33 provenance has no output records")
    missing = sorted(set(before_rows) - set(after_rows))
    if missing:
        raise RuntimeError(f"v33 removed frozen v32 output paths: {missing[:5]}")
    for path, old in before_rows.items():
        if old.get("role") == "image_overlay" and record_fingerprint(old) != record_fingerprint(after_rows[path]):
            raise RuntimeError(f"v33 changed frozen image-overlay metadata: {path}")
    new_paths = set(after_rows) - set(before_rows)
    changed_paths = {path for path in before_rows if record_fingerprint(before_rows[path]) != record_fingerprint(after_rows[path])}
    new_image_paths = {
        path for path in new_paths
        if after_rows[path].get("kind") == "image_overlay" and after_rows[path].get("role") == "image_overlay"
    }
    manifest_count = source_manifest.get("new_images")
    manifest_bytes = source_manifest.get("image_bytes")
    if not isinstance(manifest_count, int) or not isinstance(manifest_bytes, int):
        raise RuntimeError("v33 source manifest must declare integer new_images and image_bytes")
    if len(new_image_paths) != manifest_count:
        raise RuntimeError(f"v33 new image count differs from source manifest: {len(new_image_paths)} != {manifest_count}")
    new_image_bytes = sum(int(after_rows[path].get("derived_length", -1)) for path in new_image_paths)
    if new_image_bytes != manifest_bytes:
        raise RuntimeError(f"v33 new image bytes differ from source manifest: {new_image_bytes} != {manifest_bytes}")
    return {
        "before_rows": before_rows,
        "after_rows": after_rows,
        "new_paths": sorted(new_paths),
        "changed_paths": sorted(changed_paths),
        "new_image_paths": sorted(new_image_paths),
        "new_image_count": len(new_image_paths),
        "new_image_bytes": new_image_bytes,
        "previous_image_overlay_count": sum(row.get("kind") == "image_overlay" and row.get("role") == "image_overlay" for row in before_rows.values()),
        "new_non_image_paths": sorted(new_paths - new_image_paths),
    }


def mime_for_path(path: str, record: dict[str, Any] | None = None) -> list[str]:
    suffix = Path(path).suffix.casefold()
    by_suffix = {
        ".html": ["text/html"], ".htm": ["text/html"], ".json": ["application/json"],
        ".js": ["text/javascript", "application/javascript", "application/x-javascript"],
        ".css": ["text/css"], ".jpg": ["image/jpeg"], ".jpeg": ["image/jpeg"],
        ".gif": ["image/gif"], ".png": ["image/png"], ".webp": ["image/webp"],
        ".bmp": ["image/bmp"], ".svg": ["image/svg+xml"],
    }
    if suffix in by_suffix:
        return by_suffix[suffix]
    value = str((record or {}).get("mime") or "").split(";", 1)[0].strip().casefold()
    return [value] if value else ["application/octet-stream"]


def site_object_bindings(site: Path, delta: dict[str, Any]) -> list[dict[str, Any]]:
    site = inside(site, "v33 local site")
    paths = set(delta["new_paths"]) | set(delta["changed_paths"]) | {"export-provenance.json"}
    objects: list[dict[str, Any]] = []
    for relative in sorted(paths):
        path = inside(site / relative, f"v33 object {relative}")
        if not path.is_file():
            raise RuntimeError(f"missing v33 changed/new object: {relative}")
        row = delta["after_rows"].get(relative, {})
        data = path.read_bytes()
        objects.append({
            "path": relative,
            "sha256": sha256_bytes(data),
            "bytes": len(data),
            "source_list": relative == "export-provenance.json",
            "mime": mime_for_path(relative, row),
        })
    if not 1 <= len(objects) <= 256:
        raise RuntimeError(f"v33 publication object count outside bound: {len(objects)}")
    return objects


def actual_file_count(site: Path) -> int:
    return sum(1 for path in inside(site, "v33 local site").rglob("*") if path.is_file())


def guide_counts(provenance: dict[str, Any]) -> dict[str, int]:
    stats = provenance.get("stats") or {}
    collections = provenance.get("guide_image_collections") or {}
    previews = provenance.get("guide_previews") or {}
    return {
        "guide_collection_images": int(stats.get("guide_image_collection_images", collections.get("image_count", 0))),
        "guide_collection_groups": int(collections.get("group_count", 0)),
        "guide_previews": int(stats.get("guide_preview_count", previews.get("preview_count", 0))),
    }


def previous_online_commit(receipt: dict[str, Any]) -> str:
    commit = str(receipt.get("expected_pages_commit") or "").casefold()
    if not commit:
        commit = str((receipt.get("build_after") or {}).get("commit") or "").casefold()
    if len(commit) != 40:
        raise RuntimeError("v32 online receipt has no exact Pages commit")
    return commit


def build_local_receipt() -> dict[str, Any]:
    if shutil.disk_usage(ROOT).free < MIN_FREE_BYTES:
        raise RuntimeError("D disk floor reached before v33 publication preparation")
    required = [SOURCE_MANIFEST, V32_PROVENANCE, V33_PROVENANCE, *V33_RECEIPTS.values(), *V32_RECEIPTS.values(), *V33_INPUTS.values()]
    missing = sorted({str(path) for path in required if not path.is_file()})
    if missing:
        raise RuntimeError("v33 publication gate is not ready; missing: " + ", ".join(missing))
    source_manifest = read_json(SOURCE_MANIFEST, "root v33 source manifest")
    if source_manifest.get("accepted") is not True or source_manifest.get("network_requests") not in {0, None} or source_manifest.get("export_executed") not in {False, None}:
        raise RuntimeError("root v33 source manifest is not an accepted offline input")
    previous = read_json(V32_PROVENANCE, "v32 provenance")
    current = read_json(V33_PROVENANCE, "v33 provenance")
    previous_sha = sha256_file(V32_PROVENANCE)
    if previous_sha.casefold() != EXPECTED_V32_PROVENANCE_SHA256:
        raise RuntimeError(f"frozen v32 provenance SHA changed: {previous_sha} != {EXPECTED_V32_PROVENANCE_SHA256}")
    exporter_sha = sha256_file(V33_INPUTS["exporter"])
    if exporter_sha.casefold() != EXPECTED_EXPORTER_SHA256:
        raise RuntimeError(f"accepted exporter SHA changed: {exporter_sha} != {EXPECTED_EXPORTER_SHA256}")
    historical_sha = sha256_file(V33_INPUTS["historical_exhibits"])
    if historical_sha.casefold() != EXPECTED_HISTORICAL_EXHIBITS_SHA256:
        raise RuntimeError(f"accepted historical-exhibits SHA changed: {historical_sha} != {EXPECTED_HISTORICAL_EXHIBITS_SHA256}")
    current_sha = sha256_file(V33_PROVENANCE)
    receipts = {name: verify_accepted_receipt(path, f"v33 {name} acceptance", current_sha) for name, path in V33_RECEIPTS.items()}
    delta = provenance_delta(previous, current, source_manifest)
    objects = site_object_bindings(SITE, delta)
    v32_online = read_json(V32_RECEIPTS["online"], "v32 Pages online acceptance")
    v32_commit = previous_online_commit(v32_online)
    if v32_commit != EXPECTED_V32_PAGES_COMMIT:
        raise RuntimeError(f"v32 Pages commit changed: {v32_commit} != {EXPECTED_V32_PAGES_COMMIT}")
    counts = guide_counts(current)
    declared_files = len(delta["after_rows"])
    actual_files = actual_file_count(SITE)
    bindings = [binding(path) for path in required]
    bindings.extend(binding(path) for path in V33_RECEIPTS.values())
    bindings = {entry["path"]: entry for entry in bindings}
    return {
        "schema": "wow-recovery.root.v33-local-acceptance.v1",
        "accepted": True,
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "published": False,
        "local_site": rel(SITE),
        "export_provenance_sha256": current_sha,
        "objects": objects,
        "bindings": [bindings[key] for key in sorted(bindings)],
        "actual_previous_online_version": "v32",
        "actual_previous_pages_commit": v32_commit,
        "previous_online_provenance_sha256": previous_sha,
        "current_v33_provenance_sha256": current_sha,
        "new_images_since_live_v32": delta["new_image_count"],
        "new_image_bytes_since_live_v32": delta["new_image_bytes"],
        "changed_since_live_v32": delta["changed_paths"],
        "new_paths_since_live_v32": delta["new_paths"],
        "declared_files": declared_files,
        "actual_files": actual_files,
        **counts,
        "previous_image_overlay_records": delta["previous_image_overlay_count"],
        "v33_acceptance_receipts": {name: binding(path) for name, path in V33_RECEIPTS.items()},
        "verification_scope": "All v33 new and changed objects versus the actual accepted v32 Pages baseline; max256 objects/512 HTTP attempts/900 seconds/256MiB. Root owns publication and online execution.",
        "root_acceptances": {name: {"accepted": value.get("accepted"), "provenance_sha256": current_sha} for name, value in receipts.items()},
    }


def write_once(path: Path, payload: dict[str, Any]) -> None:
    path = inside(path, "v33 local acceptance output")
    if path.exists():
        raise RuntimeError(f"refusing to overwrite v33 local acceptance: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args(argv)
    if not args.prepare:
        parser.error("v33 publication preparation requires --prepare; it never publishes or checks HTTP")
    if LOCAL_GATE.exists():
        raise RuntimeError(f"refusing existing v33 local acceptance: {LOCAL_GATE}")
    receipt = build_local_receipt()
    write_once(LOCAL_GATE, receipt)
    print(json.dumps({"accepted": True, "local_gate": rel(LOCAL_GATE), "objects": len(receipt["objects"]), "new_images_since_live_v32": receipt["new_images_since_live_v32"], "network_requests": 0, "published": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
