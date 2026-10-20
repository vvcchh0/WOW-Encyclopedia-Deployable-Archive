"""One-shot offline v39 preparation runner; requires a later explicit --go."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PUB = ROOT / "research/continuous-recovery-20261020/publication"
GATE = PUB / "root-v39-export-go.json"
V38_GATE = ROOT / "research/continuous-recovery-20261019/publication/root-v38-export-go.json"
DIGEST_ACCEPTANCE = PUB / "root-digest-reuse-source-acceptance.json"
PREP = HERE / "v39-input-preparation.json"
MAP = HERE / "payload-digest-reuse-image-source-map.json"
OUT = ROOT / ".scratch/pages-resources-20261020-v39"
RECEIPT = HERE / "v39-build-receipt.json"
FLOOR = 11_005_853_696
CUTOFF = datetime(2026, 10, 20, 13, 25, tzinfo=timezone.utc)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def count_files(root: Path) -> int:
    """Count regular output files without resolving every parent path."""

    count = 0
    pending = [root]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_symlink():
                    raise AssertionError(f"output contains a symlink: {entry.path}")
                if entry.is_dir(follow_symlinks=False):
                    pending.append(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    count += 1
    return count


def verify_bindings(gate: dict, *, label: str, exclude: set[str] = frozenset()) -> dict[str, str]:
    bindings = gate.get("bindings")
    assert isinstance(bindings, list) and bindings, f"{label} has no bindings"
    seen: set[str] = set()
    verified: dict[str, str] = {}
    for row in bindings:
        assert isinstance(row, dict), f"{label} binding is not an object"
        relative = row.get("path")
        expected = row.get("sha256")
        assert isinstance(relative, str) and relative and not Path(relative).is_absolute(), (
            f"{label} binding path is invalid: {relative!r}"
        )
        assert isinstance(expected, str) and len(expected) == 64, (
            f"{label} binding hash is invalid: {relative!r}"
        )
        assert relative not in seen, f"{label} binding is duplicated: {relative}"
        seen.add(relative)
        if relative in exclude:
            continue
        path = ROOT / relative
        assert path.is_file(), f"{label} bound file is missing: {relative}"
        assert sha256(path) == expected, f"{label} bound file hash changed: {relative}"
        verified[relative] = expected
    return verified


def require_bound_hashes(bound: dict[str, str], paths: set[str], *, label: str) -> None:
    for relative in sorted(paths):
        assert relative in bound, f"{label} is not bound: {relative}"


def v39_inputs(gate: dict, v38_gate: dict) -> tuple[tuple[Path, ...], tuple[Path, ...], Path, Path]:
    old_primary = v38_gate.get("primary_maps")
    old_supplements = v38_gate.get("supplement_maps")
    preview = v38_gate.get("guide_preview_map")
    collection = v38_gate.get("guide_image_collection_map")
    assert isinstance(old_primary, list) and len(old_primary) == 19
    assert isinstance(old_supplements, list) and len(old_supplements) == 17
    assert isinstance(preview, str) and preview
    assert isinstance(collection, str) and collection
    primary = tuple(ROOT / item for item in [*old_primary, MAP.relative_to(ROOT).as_posix()])
    supplements = tuple(ROOT / item for item in old_supplements)
    declared_primary = gate.get("primary_maps")
    declared_supplements = gate.get("supplement_maps")
    assert declared_primary == [path.relative_to(ROOT).as_posix() for path in primary]
    assert declared_supplements == [path.relative_to(ROOT).as_posix() for path in supplements]
    assert gate.get("guide_preview_map") == preview
    assert gate.get("guide_image_collection_map") == collection
    return primary, supplements, ROOT / preview, ROOT / collection


def validate_inputs() -> dict:
    assert GATE.is_file(), f"v39 export gate is missing: {GATE}"
    gate = read_json(GATE)
    assert gate.get("accepted") is True and gate.get("export_go") is True
    assert gate.get("output") == OUT.relative_to(ROOT).as_posix()
    assert datetime.now(timezone.utc) < CUTOFF, f"v39 export cutoff passed: {CUTOFF.isoformat()}"
    v39_bound = verify_bindings(gate, label="v39 gate")
    assert V38_GATE.is_file(), f"v38 export gate is missing: {V38_GATE}"
    v38_gate = read_json(V38_GATE)
    assert v38_gate.get("accepted") is True and v38_gate.get("export_go") is True
    # The v38 closure pins the pre-v39 exporter and historical transformer.
    # Those two files are intentionally superseded by the reviewed v39 code;
    # every other old bound input remains frozen and hash-checked here.
    v38_bound = verify_bindings(
        v38_gate,
        label="v38 gate",
        exclude={"tools/export_github_pages.py", "tools/historical_exhibits.py"},
    )
    assert DIGEST_ACCEPTANCE.is_file()
    digest_acceptance = read_json(DIGEST_ACCEPTANCE)
    assert digest_acceptance.get("accepted") is True
    assert digest_acceptance.get("accepted_images") == 2
    prep = read_json(PREP)
    assert prep["status"] == "prepared_local_only"
    assert prep["network_requests"] == 0
    assert prep["published"] is False and prep["exported"] is False
    assert sha256(ROOT / prep["source_manifest"]) == prep["source_manifest_sha256"]
    assert prep["source_manifest_sha256"] == v38_gate["source_manifest_sha256"]
    accepted = prep["accepted_v38_closure"]
    assert sha256(ROOT / accepted["path"]) == accepted["sha256"]
    new2 = prep["new2_map"]
    assert sha256(ROOT / new2["path"]) == new2["sha256"]
    assert sha256(ROOT / new2["source_chain_path"]) == new2["source_chain_sha256"]
    test_receipt = prep["test_execution_receipt"]
    assert sha256(ROOT / test_receipt["path"]) == test_receipt["sha256"]
    test_receipt_data = read_json(ROOT / test_receipt["path"])
    assert test_receipt_data["status"] == "executed_local_only"
    assert test_receipt_data["network_requests"] == 0
    assert test_receipt_data["exported"] is False
    assert sha256(MAP) == prep["image_source_map"]["sha256"]
    items = read_json(MAP)["items"]
    assert len(items) == 2
    assert all(item.get("recovery_method") == "payload_digest_reuse" for item in items)
    assert all("actual_timestamp" not in item for item in items)
    accepted_routes = {
        row["target_route"]: row for row in digest_acceptance.get("routes", [])
    }
    assert set(accepted_routes) == {
        "/news/images/04-12/ordernow.jpg",
        "/news/images/05-10/trolldire.jpg",
    }
    for item in items:
        route = str(item["logical_url"]).split(".com", 1)[-1]
        accepted_row = accepted_routes[route]
        assert item["original"] == accepted_row["target_original_url"]
        assert item["indexed_capture_timestamp"] == accepted_row["target_indexed_capture_timestamp"]
        assert item["cdx_digest"] == accepted_row["target_cdx_digest"]
        payload = item["payload_source"]
        accepted_payload = accepted_row["payload_source"]
        for field in ("original_url", "actual_capture_timestamp", "sha256", "length"):
            assert payload[field] == accepted_payload[field]
    primary, supplements, guide_preview, guide_collection = v39_inputs(gate, v38_gate)
    for path in [*primary, *supplements, guide_preview, guide_collection]:
        assert path.is_file(), f"v39 input is missing: {path}"
    assert prep["source_site"] == ".scratch/offline-navigation-20261015-v15/site"
    assert prep["source_manifest"] == ".scratch/offline-navigation-20261015-v15/build-manifest.json"
    assert gate.get("source_manifest_sha256") == prep["source_manifest_sha256"]
    required_v38 = {
        *v38_gate["primary_maps"],
        *v38_gate["supplement_maps"],
        v38_gate["guide_preview_map"],
        v38_gate["guide_image_collection_map"],
    }
    required_v39 = {
        "tools/export_github_pages.py",
        "tools/historical_exhibits.py",
        ".scratch/offline-navigation-20261015-v15/build-manifest.json",
        MAP.relative_to(ROOT).as_posix(),
        new2["path"],
        new2["source_chain_path"],
        test_receipt["path"],
        DIGEST_ACCEPTANCE.relative_to(ROOT).as_posix(),
        V38_GATE.relative_to(ROOT).as_posix(),
        *required_v38,
    }
    require_bound_hashes(v38_bound, required_v38 - {"tools/export_github_pages.py", "tools/historical_exhibits.py"}, label="v38 closure")
    require_bound_hashes(v39_bound, required_v39, label="v39 gate")
    return {
        "prep": prep,
        "gate": gate,
        "v38_gate": v38_gate,
        "primary_maps": primary,
        "supplement_maps": supplements,
        "guide_preview_map": guide_preview,
        "guide_image_collection_map": guide_collection,
    }


def child_run() -> None:
    assert os.environ.get("WOW_V39_CHILD") == "1"
    assert not OUT.exists() and not OUT.with_name(OUT.name + ".partial").exists()
    sys.path.insert(0, str(ROOT / "tools"))
    import export_github_pages as exporter

    inputs = validate_inputs()
    prep = inputs["prep"]
    result = exporter.export_pages(
        source_site=ROOT / prep["source_site"],
        manifest_path=ROOT / prep["source_manifest"],
        output=OUT,
        base_path=prep["base_path"],
        workspace_root=ROOT,
        max_bytes=None,
        min_free_bytes=FLOOR,
        image_source_maps=inputs["primary_maps"],
        supplement_image_source_maps=inputs["supplement_maps"],
        allow_later_image_supplements=True,
        guide_preview_map=inputs["guide_preview_map"],
        guide_image_collection_map=inputs["guide_image_collection_map"],
    )
    print(json.dumps(result, ensure_ascii=False, default=str))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--go", action="store_true")
    parser.add_argument("--child", action="store_true")
    args = parser.parse_args()
    validate_inputs()
    if args.child:
        child_run()
        return
    assert args.go, "preparation only; pass --go after root review"
    assert not RECEIPT.exists()
    assert not OUT.exists() and not OUT.with_name(OUT.name + ".partial").exists()
    before = shutil.disk_usage(ROOT).free
    assert before >= FLOOR
    started = datetime.now(timezone.utc)
    stdout = HERE / "export.stdout.log"
    stderr = HERE / "export.stderr.log"
    timed_out = False
    with stdout.open("xb") as outlog, stderr.open("xb") as errlog:
        try:
            child = subprocess.run(
                [sys.executable, "-B", "-X", "utf8", str(Path(__file__).resolve()), "--child"],
                cwd=ROOT,
                env=dict(os.environ, WOW_V39_CHILD="1"),
                stdout=outlog,
                stderr=errlog,
                timeout=600,
                check=False,
            )
            returncode = child.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            returncode = None
    finished = datetime.now(timezone.utc)
    receipt = {
        "executed": True,
        "started_utc": started.isoformat(),
        "finished_utc": finished.isoformat(),
        "elapsed_seconds": (finished - started).total_seconds(),
        "timeout_seconds": 600,
        "timed_out": timed_out,
        "returncode": returncode,
        "published": False,
        "network_requests": 0,
        "output": OUT.relative_to(ROOT).as_posix(),
        "root_gate_sha256": sha256(GATE),
        "input_preparation_sha256": sha256(PREP),
        "image_source_map_sha256": sha256(MAP),
        "disk_free_before_bytes": before,
        "disk_free_after_bytes": shutil.disk_usage(ROOT).free,
        "export_completed": returncode == 0 and not timed_out and OUT.is_dir(),
    }
    if receipt["export_completed"]:
        provenance = read_json(OUT / "export-provenance.json")
        receipt["export_provenance_sha256"] = sha256(OUT / "export-provenance.json")
        receipt["declared_files"] = len(provenance["files"])
        receipt["actual_files"] = count_files(OUT)
        receipt["stats"] = provenance["stats"]
    with RECEIPT.open("x", encoding="utf-8") as handle:
        json.dump(receipt, handle, indent=2)
        handle.write("\n")
    if timed_out:
        raise SystemExit("v39 export timed out; receipt recorded without retry")
    assert receipt["export_completed"], receipt
    assert receipt["disk_free_after_bytes"] >= FLOOR, receipt
    assert receipt["declared_files"] == 9115
    assert receipt["actual_files"] == 9116
    assert receipt["stats"]["image_overlay_records"] == 657
    assert receipt["stats"]["primary_image_overlay_records"] == 557
    assert receipt["stats"]["supplement_image_overlay_records"] == 100


if __name__ == "__main__":
    main()
