#!/usr/bin/env python3
"""Bounded validation and (root-authorized) promotion of the v35 partial tree.

The normal v35 exporter already produced a complete partial tree before its
workspace-size tail work timed out.  This helper deliberately validates that
tree in place and never calls the exporter in ``--check`` mode.  Promotion is
kept behind two explicit flags and reuses the frozen exporter's narrow rename
helper; it is not used by the recovery check.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


EXPECTED_ROOT = Path(r"D:\WOW_Encyclopedia")
EXPECTED_GATE_SHA256 = "1d3705381773e5040724f957512987719946e36876765f84395e804fdee655fd"
EXPECTED_PARTIAL_PROVENANCE_SHA256 = "f37f73ba4cdd63b1190b895a2d770dd94b2b764ad5fc219a5fd34bad93a3c4d0"
EXPECTED_V34_PROVENANCE_SHA256 = "3946f504260aec576087207399ad692eef9f7fac938fac439474a2c540d85447"
EXPECTED_EXPORTER_SHA256 = "e5b3a53381ddcf0b5037a726d328c7dd99fa5d2f8e24e047e474a3853305643a"
EXPECTED_V35_PRIMARY_MAP_SHA256 = "ceef4526a696c5685f65893c1cd8d45937615bb5aabc6f45c3c77d47163ca0d0"
EXPECTED_V35_SUPPLEMENT_MAP_SHA256 = "5e2c1d2887b8b5936c7d8f51b0c316624280bf5a2473b6902f884e8c1ec5eff6"
EXPECTED_V35_PREPARATION_SHA256 = "a40a488506d7269b7f3e6964b399085746d1f895b4af7c5f51cd10d4fb2c0683"
EXPECTED_V35_PREFLIGHT_SHA256 = "f8514ee2577aabab70c8adf2920962d10d0d81e6d7ea3287997de099e383ef71"
EXPECTED_V35_BUILDER_SHA256 = "0fdce2a703f3e4c1f7b2e122391f89ce54093cae30ac3fc7d97d6fd24b8d7fb5"
EXPECTED_V35_RUNNER_SHA256 = "beb62d81d7a65625c594e03625dfa78474cc12f6584462a89acd5a95e0c85ee0"
EXPECTED_DISK_FLOOR = 11_005_853_696
EXPECTED_SOURCE_RECORDS = 8_357
EXPECTED_OLD_OVERLAYS = 559
EXPECTED_NEW_OVERLAYS = 24
EXPECTED_TOTAL_OVERLAYS = 583
EXPECTED_DECLARED_FILES = 9_041
EXPECTED_ACTUAL_FILES = 9_042
EXPECTED_NEW_IMAGE_BYTES = 191_943
EXPECTED_GATE_BINDINGS = 62

ROOT = next(
    (candidate.resolve() for candidate in Path(__file__).resolve().parents if candidate.name == EXPECTED_ROOT.name),
    EXPECTED_ROOT.resolve(),
)
if os.path.normcase(os.fspath(ROOT)) != os.path.normcase(os.fspath(EXPECTED_ROOT.resolve())):
    raise RuntimeError(f"unexpected workspace root: {ROOT}")

SCRATCH = ROOT / ".scratch"
PARTIAL = SCRATCH / "pages-resources-20261019-v35.partial"
OUTPUT = SCRATCH / "pages-resources-20261019-v35"
PARTIAL_PROVENANCE = PARTIAL / "export-provenance.json"
V34_PROVENANCE = SCRATCH / "pages-resources-20261019-v34" / "export-provenance.json"
GATE = ROOT / "research/continuous-recovery-20261019/publication/root-v35-input-acceptance.json"
V35_DIR = ROOT / "research/continuous-recovery-20261019/integration/v35"
PRIMARY_MAP = V35_DIR / "v35-primary-source-map.json"
SUPPLEMENT_MAP = V35_DIR / "v35-supplement-source-map.json"
PREPARATION = V35_DIR / "v35-input-preparation.json"
PREFLIGHT = V35_DIR / "v35-preflight.json"
BUILDER = V35_DIR / "build_pages_v35.py"
RUNNER = V35_DIR / "execute_v35.py"
EXPORTER = ROOT / "tools/export_github_pages.py"
FINALIZATION_DIR = Path(__file__).resolve().parent
CHECK_RECEIPT = FINALIZATION_DIR / "v35-partial-check-receipt.json"
PROMOTION_RECEIPT = FINALIZATION_DIR / "v35-partial-promotion-receipt.json"

EXPECTED_COMMON_CHANGED = {
    "__offline/pages_runtime.js",
    "__offline/route-map.json",
    "news/rss-10-2007.xml.html",
    "news/wow-news2004.html",
}


class ValidationError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def path_under(path: Path, base: Path, *, label: str) -> Path:
    candidate = path.resolve(strict=False)
    base_resolved = base.resolve(strict=False)
    try:
        candidate.relative_to(base_resolved)
    except ValueError as exc:
        raise ValidationError(f"{label} escapes {base_resolved}: {candidate}") from exc
    return candidate


def repo_path(relative: str, *, label: str) -> Path:
    path = path_under(ROOT / relative, ROOT, label=label)
    if not path.exists() or not path.is_file():
        raise ValidationError(f"missing bound file for {label}: {relative}")
    return path


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValidationError(f"missing JSON: {path}")
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValidationError(f"expected JSON object: {path}")
    return value


def json_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False, separators=(",", ": ")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path = path_under(path, FINALIZATION_DIR, label="receipt")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        path_under(temporary, FINALIZATION_DIR, label="receipt temporary")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def verify_file_record(record: dict[str, Any]) -> tuple[str, str | None]:
    rel = record.get("output_path")
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        return str(rel), "invalid output_path"
    candidate = path_under(PARTIAL / rel, PARTIAL, label="provenance output")
    if not candidate.is_file() or candidate.is_symlink():
        return rel, "missing or symlink"
    expected_length = record.get("derived_length")
    expected_sha = record.get("derived_sha256")
    if not isinstance(expected_length, int) or not isinstance(expected_sha, str):
        return rel, "missing derived length/sha256"
    digest = hashlib.sha256()
    actual_length = 0
    try:
        with candidate.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                actual_length += len(chunk)
                digest.update(chunk)
    except OSError as exc:
        return rel, f"read failed: {exc}"
    actual_sha = digest.hexdigest()
    if actual_length != expected_length:
        return rel, f"length {actual_length} != {expected_length}"
    if actual_sha != expected_sha:
        return rel, f"sha256 {actual_sha} != {expected_sha}"
    return rel, None


def actual_relative_files() -> tuple[set[str], list[str]]:
    actual: set[str] = set()
    symlinks: list[str] = []
    for dirpath, dirnames, filenames in os.walk(PARTIAL, topdown=True, followlinks=False):
        base = Path(dirpath)
        for dirname in list(dirnames):
            child = base / dirname
            if child.is_symlink():
                symlinks.append(child.relative_to(PARTIAL).as_posix())
                dirnames.remove(dirname)
        for filename in filenames:
            child = base / filename
            rel = child.relative_to(PARTIAL).as_posix()
            if child.is_symlink():
                symlinks.append(rel)
            else:
                actual.add(rel)
    return actual, symlinks


def verify_input_gate() -> dict[str, Any]:
    gate_digest = sha256_file(GATE)
    if gate_digest != EXPECTED_GATE_SHA256:
        raise ValidationError(f"root v35 gate SHA mismatch: {gate_digest} != {EXPECTED_GATE_SHA256}")
    gate = load_json(GATE)
    if gate.get("accepted") is not True:
        raise ValidationError("root v35 input gate is not accepted")
    if gate.get("export_executed") is not False:
        raise ValidationError("root v35 gate unexpectedly records export_executed")
    if gate.get("network_requests") != 0:
        raise ValidationError("root v35 gate records network requests")
    if gate.get("new_images") != EXPECTED_NEW_OVERLAYS or gate.get("image_bytes") != EXPECTED_NEW_IMAGE_BYTES:
        raise ValidationError("root v35 gate new-image count/bytes mismatch")
    if gate.get("preflight_sha256") != EXPECTED_V35_PREFLIGHT_SHA256:
        raise ValidationError("root v35 gate preflight SHA mismatch")
    bindings = gate.get("map_bindings")
    if not isinstance(bindings, list) or len(bindings) != EXPECTED_GATE_BINDINGS:
        raise ValidationError(f"expected {EXPECTED_GATE_BINDINGS} root bindings, got {len(bindings) if isinstance(bindings, list) else None}")
    mismatches: list[dict[str, str]] = []
    for binding in bindings:
        if not isinstance(binding, dict) or not isinstance(binding.get("path"), str) or not isinstance(binding.get("sha256"), str):
            mismatches.append({"path": str(binding), "reason": "malformed binding"})
            continue
        try:
            bound_path = repo_path(binding["path"], label="root gate binding")
            actual = sha256_file(bound_path)
        except ValidationError as exc:
            mismatches.append({"path": binding["path"], "reason": str(exc)})
            continue
        if actual != binding["sha256"]:
            mismatches.append({"path": binding["path"], "reason": f"{actual} != {binding['sha256']}"})
    if mismatches:
        raise ValidationError("root binding mismatches: " + json.dumps(mismatches, ensure_ascii=False))
    return {"sha256": gate_digest, "binding_count": len(bindings), "checked": True}


def verify_paths_and_provenance() -> tuple[dict[str, Any], dict[str, Any], list[str], list[str], list[str]]:
    path_under(PARTIAL, SCRATCH, label="partial")
    path_under(OUTPUT, SCRATCH, label="output")
    if not PARTIAL.is_dir() or PARTIAL.is_symlink():
        raise ValidationError(f"partial is not a real directory: {PARTIAL}")
    if os.path.lexists(OUTPUT):
        raise ValidationError(f"refusing to inspect with output already present: {OUTPUT}")
    if sha256_file(PARTIAL_PROVENANCE) != EXPECTED_PARTIAL_PROVENANCE_SHA256:
        raise ValidationError("partial provenance SHA mismatch")
    provenance = load_json(PARTIAL_PROVENANCE)
    files = provenance.get("files")
    if not isinstance(files, list) or len(files) != EXPECTED_DECLARED_FILES:
        raise ValidationError(f"expected {EXPECTED_DECLARED_FILES} provenance file records")
    records: list[dict[str, Any]] = []
    for record in files:
        if not isinstance(record, dict):
            raise ValidationError("non-object provenance file record")
        records.append(record)
    paths = [record.get("output_path") for record in records]
    if any(not isinstance(path, str) for path in paths) or len(set(paths)) != len(paths):
        raise ValidationError("provenance output paths are missing or duplicated")
    actual, symlinks = actual_relative_files()
    declared = set(paths)
    expected_actual = declared | {"export-provenance.json"}
    if actual != expected_actual:
        missing = sorted(expected_actual - actual)
        unexpected = sorted(actual - expected_actual)
        raise ValidationError(f"partial file set mismatch: missing={missing[:10]} unexpected={unexpected[:10]}")
    if symlinks:
        raise ValidationError(f"partial contains symlinks: {symlinks[:10]}")
    failures: list[tuple[str, str | None]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8, thread_name_prefix="v35-check") as pool:
        for result in pool.map(verify_file_record, records, chunksize=16):
            if result[1] is not None:
                failures.append(result)
    if failures:
        raise ValidationError("declared file mismatches: " + json.dumps(failures[:20], ensure_ascii=False))
    stats = provenance.get("stats")
    expected_stats = {
        "source_records": EXPECTED_SOURCE_RECORDS,
        "primary_image_overlay_records": 483,
        "supplement_image_overlay_records": 100,
        "image_overlay_records": EXPECTED_TOTAL_OVERLAYS,
        "output_files": EXPECTED_DECLARED_FILES,
        "guide_image_collection_images": 39,
        "guide_preview_count": 22,
    }
    if not isinstance(stats, dict):
        raise ValidationError("provenance stats missing")
    stat_mismatches = {key: (stats.get(key), value) for key, value in expected_stats.items() if stats.get(key) != value}
    if stat_mismatches:
        raise ValidationError("provenance stats mismatch: " + json.dumps(stat_mismatches))
    return provenance, {"declared_files": len(declared), "actual_files": len(actual), "symlinks": 0}, [], [], []


def verify_old_and_new_deltas(provenance: dict[str, Any]) -> dict[str, Any]:
    if sha256_file(V34_PROVENANCE) != EXPECTED_V34_PROVENANCE_SHA256:
        raise ValidationError("v34 provenance SHA mismatch")
    v34 = load_json(V34_PROVENANCE)
    v34_files = {record["output_path"]: record for record in v34.get("files", []) if isinstance(record, dict) and isinstance(record.get("output_path"), str)}
    v35_files = {record["output_path"]: record for record in provenance["files"]}
    v34_overlays = {path: record for path, record in v34_files.items() if record.get("role") == "image_overlay"}
    v35_overlays = {path: record for path, record in v35_files.items() if record.get("role") == "image_overlay"}
    if len(v34_overlays) != EXPECTED_OLD_OVERLAYS:
        raise ValidationError(f"v34 overlay count mismatch: {len(v34_overlays)}")
    old_mismatches = [path for path in sorted(v34_overlays) if v35_overlays.get(path) != v34_overlays[path]]
    if old_mismatches:
        raise ValidationError("old overlay metadata changed: " + json.dumps(old_mismatches[:20]))
    new_overlay_paths = sorted(set(v35_overlays) - set(v34_overlays))
    if len(new_overlay_paths) != EXPECTED_NEW_OVERLAYS:
        raise ValidationError(f"new overlay path count mismatch: {len(new_overlay_paths)}")
    common_changed = sorted(path for path in set(v34_files) & set(v35_files) if v34_files[path] != v35_files[path])
    if set(common_changed) != EXPECTED_COMMON_CHANGED:
        raise ValidationError(f"unexpected common provenance changes: {json.dumps(common_changed)}")
    return {
        "v34_overlay_count": len(v34_overlays),
        "new_overlay_paths": new_overlay_paths,
        "old_overlay_metadata_mismatches": old_mismatches,
        "common_changed_paths": common_changed,
        "new_file_paths": sorted(set(v35_files) - set(v34_files)),
    }


def verify_new_public_copies(provenance: dict[str, Any]) -> dict[str, Any]:
    primary_map = load_json(PRIMARY_MAP)
    items = primary_map.get("items")
    if not isinstance(items, list) or len(items) != EXPECTED_NEW_OVERLAYS:
        raise ValidationError("v35 primary map does not contain 24 items")
    map_digest = sha256_file(PRIMARY_MAP)
    if map_digest != EXPECTED_V35_PRIMARY_MAP_SHA256:
        raise ValidationError("v35 primary map SHA mismatch")
    if sha256_file(SUPPLEMENT_MAP) != EXPECTED_V35_SUPPLEMENT_MAP_SHA256:
        raise ValidationError("v35 supplement map SHA mismatch")
    copy_failures: list[dict[str, Any]] = []
    provenance_by_original: dict[str, list[dict[str, Any]]] = {}
    for record in provenance.get("files", []):
        if record.get("role") == "image_overlay":
            provenance_by_original.setdefault(record.get("original_url"), []).append(record)
    total = 0
    outputs: list[str] = []
    for item in items:
        original = item.get("original")
        expected_sha = item.get("sha256")
        expected_length = item.get("length")
        public_path = item.get("public_copy_path") or item.get("local_path")
        if not all(isinstance(value, str) for value in (original, expected_sha, public_path)) or not isinstance(expected_length, int):
            copy_failures.append({"original": original, "reason": "malformed map item"})
            continue
        source = repo_path(public_path, label="v35 public image copy")
        actual_length = source.stat().st_size
        actual_sha = sha256_file(source)
        if actual_length != expected_length or actual_sha != expected_sha:
            copy_failures.append({"original": original, "reason": f"copy {actual_length}/{actual_sha} != {expected_length}/{expected_sha}"})
        total += expected_length
        matched = provenance_by_original.get(original, [])
        if len(matched) != 1:
            copy_failures.append({"original": original, "reason": f"provenance original matches={len(matched)}"})
            continue
        record = matched[0]
        if record.get("derived_length") != expected_length or record.get("derived_sha256") != expected_sha:
            copy_failures.append({"original": original, "reason": "partial overlay bytes differ from public copy"})
        outputs.append(record["output_path"])
    if total != EXPECTED_NEW_IMAGE_BYTES:
        copy_failures.append({"reason": f"new image bytes total {total} != {EXPECTED_NEW_IMAGE_BYTES}"})
    if copy_failures:
        raise ValidationError("new image/public-copy failures: " + json.dumps(copy_failures[:20], ensure_ascii=False))
    return {"count": len(items), "bytes": total, "output_paths": sorted(outputs), "map_sha256": map_digest}


def check() -> dict[str, Any]:
    started = time.monotonic()
    checked_utc = utc_now()
    errors: list[str] = []
    gate_info: dict[str, Any] = {}
    counts: dict[str, Any] = {}
    delta: dict[str, Any] = {}
    new_info: dict[str, Any] = {}
    try:
        gate_info = verify_input_gate()
        provenance, counts, _, _, _ = verify_paths_and_provenance()
        delta = verify_old_and_new_deltas(provenance)
        new_info = verify_new_public_copies(provenance)
        if sha256_file(PREPARATION) != EXPECTED_V35_PREPARATION_SHA256:
            raise ValidationError("v35 preparation SHA mismatch")
        if sha256_file(PREFLIGHT) != EXPECTED_V35_PREFLIGHT_SHA256:
            raise ValidationError("v35 preflight SHA mismatch")
        if sha256_file(BUILDER) != EXPECTED_V35_BUILDER_SHA256:
            raise ValidationError("v35 builder SHA mismatch")
        if sha256_file(RUNNER) != EXPECTED_V35_RUNNER_SHA256:
            raise ValidationError("v35 runner SHA mismatch")
    except (ValidationError, OSError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
    disk_free = shutil.disk_usage(ROOT).free
    elapsed = time.monotonic() - started
    receipt: dict[str, Any] = {
        "schema": "v35_partial_finalization_check_v1",
        "status": "passed" if not errors else "failed",
        "mode": "check",
        "checked_utc": checked_utc,
        "completed_utc": utc_now(),
        "elapsed_seconds": round(elapsed, 6),
        "root": str(ROOT),
        "partial": str(PARTIAL),
        "output": str(OUTPUT),
        "partial_provenance_sha256": EXPECTED_PARTIAL_PROVENANCE_SHA256,
        "root_input_gate_sha256": EXPECTED_GATE_SHA256,
        "input_gate": gate_info,
        "counts": counts,
        "new_images": new_info,
        "delta": delta,
        "disk_free_bytes": disk_free,
        "disk_floor_bytes": EXPECTED_DISK_FLOOR,
        "disk_floor_passed": disk_free >= EXPECTED_DISK_FLOOR,
        "network_requests": 0,
        "export_executed": False,
        "workspace_scan": False,
        "max_workers": 8,
        "errors": errors,
        "old_timeout_receipt_preserved": True,
    }
    if disk_free < EXPECTED_DISK_FLOOR:
        receipt["status"] = "failed"
        receipt["errors"].append(f"disk free {disk_free} below floor {EXPECTED_DISK_FLOOR}")
    write_json_atomic(CHECK_RECEIPT, receipt)
    print(json.dumps({"status": receipt["status"], "receipt": str(CHECK_RECEIPT), "elapsed_seconds": receipt["elapsed_seconds"], "disk_free_bytes": disk_free}, ensure_ascii=False))
    return receipt


def promote(check_receipt_path: Path, check_receipt_sha256: str) -> None:
    path_under(PARTIAL, SCRATCH, label="partial")
    path_under(OUTPUT, SCRATCH, label="output")
    if os.path.lexists(OUTPUT):
        raise ValidationError(f"refusing to overwrite existing output: {OUTPUT}")
    check_receipt_path = path_under(check_receipt_path, FINALIZATION_DIR, label="check receipt")
    if sha256_file(check_receipt_path) != check_receipt_sha256:
        raise ValidationError("check receipt SHA does not match --check-receipt-sha256")
    receipt = load_json(check_receipt_path)
    if receipt.get("status") != "passed" or receipt.get("mode") != "check":
        raise ValidationError("promotion requires a passed check receipt")
    if receipt.get("partial_provenance_sha256") != EXPECTED_PARTIAL_PROVENANCE_SHA256:
        raise ValidationError("check receipt partial provenance mismatch")
    if receipt.get("root_input_gate_sha256") != EXPECTED_GATE_SHA256:
        raise ValidationError("check receipt root gate mismatch")
    if sha256_file(EXPORTER) != EXPECTED_EXPORTER_SHA256:
        raise ValidationError("frozen exporter SHA mismatch")
    spec = importlib.util.spec_from_file_location("frozen_exporter_v35", EXPORTER)
    if spec is None or spec.loader is None:
        raise ValidationError("unable to load frozen exporter")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    promoter = getattr(module, "_promote_partial_output", None)
    if not callable(promoter):
        raise ValidationError("frozen exporter has no _promote_partial_output")
    started = time.monotonic()
    promoter(PARTIAL, OUTPUT)
    elapsed = time.monotonic() - started
    promotion = {
        "schema": "v35_partial_finalization_promotion_v1",
        "status": "promoted",
        "mode": "promote",
        "completed_utc": utc_now(),
        "elapsed_seconds": round(elapsed, 6),
        "partial": str(PARTIAL),
        "output": str(OUTPUT),
        "check_receipt": str(check_receipt_path),
        "check_receipt_sha256": check_receipt_sha256,
        "partial_provenance_sha256": EXPECTED_PARTIAL_PROVENANCE_SHA256,
        "exporter_sha256": EXPECTED_EXPORTER_SHA256,
        "network_requests": 0,
        "export_executed": False,
    }
    write_json_atomic(PROMOTION_RECEIPT, promotion)
    print(json.dumps(promotion, ensure_ascii=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true", help="validate the existing partial tree only")
    modes.add_argument("--promote", action="store_true", help="root-authorized rename of the validated partial tree")
    parser.add_argument("--root-go", action="store_true", help="explicit promotion authorization")
    parser.add_argument("--check-receipt", type=Path, default=CHECK_RECEIPT)
    parser.add_argument("--check-receipt-sha256")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check:
        if args.root_go or args.check_receipt_sha256:
            raise SystemExit("--check does not accept promotion authorization")
        receipt = check()
        return 0 if receipt["status"] == "passed" else 2
    if not args.root_go:
        raise SystemExit("--promote requires --root-go")
    if not args.check_receipt_sha256:
        raise SystemExit("--promote requires --check-receipt-sha256")
    try:
        promote(args.check_receipt, args.check_receipt_sha256)
    except (ValidationError, OSError, ImportError) as exc:
        print(f"promotion refused: {exc}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
