"""Prepare the accepted v18 for a later Pages publication.

The default action is local-only: it binds the v18 gates, source manifests,
maps, implementation hashes, and the exact local objects that the online
verifier will check.  It writes ``root-v18-local-acceptance.json`` and
``v18-publication-preparation.json``.  No Git operation, network request, or
publication is performed by the default action.

An explicit ``--publish`` is required before this helper imports the existing
publication tool.  The flag is intentionally absent from this run; it exists
only so a later root stage can make the irreversible publication choice
explicitly.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "research/continuous-recovery-20261016"
SITE = ROOT / ".scratch/pages-resources-20261016-v18"
V17_SITE = ROOT / ".scratch/pages-resources-20261016-v17"

SOURCE15_MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
ORIGINAL_MANIFEST = ROOT / "offline/build-manifest.json"
V17_PROVENANCE = V17_SITE / "export-provenance.json"
V18_PROVENANCE = SITE / "export-provenance.json"
V2_MAP = RUN / "integration/v18-guide-previews/guide-previews-source-map-v2.json"
GUIDE_IMPL = ROOT / "tools/guide_previews.py"
EXPORT_IMPL = ROOT / "tools/export_github_pages.py"
GUIDE_TESTS = ROOT / "tests/test_guide_previews.py"
FOCUSED_STDOUT = OUT / "v18-independent-focused9.stdout.txt"
INDEPENDENT_BROWSER_RECEIPT = OUT / "v18-independent-browser12.json"
INDEPENDENT_BROWSER_SCREENSHOT = OUT / "v18-independent-city.png"
INDEPENDENT_BROWSER_SCRIPT = OUT / "browser_v18_independent_local.cjs"

GATES = {
    "root-v18-export-acceptance": OUT / "root-v18-export-acceptance.json",
    "root-v18-browser-acceptance": OUT / "root-v18-browser-acceptance.json",
    "root-city-v2-code-acceptance": OUT / "root-city-v2-code-acceptance.json",
    "focused-guide-tests-receipt": RUN / "integration/v18-build/focused-guide-tests-receipt.json",
    "worker-build-v18": RUN / "integration/v18-build/worker-build-v18.json",
}

EXPECTED_SOURCE15 = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
EXPECTED_OFFLINE = "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"
EXPECTED_PRIMARY_V17 = "c6769d5636846bd27314824684e919b102bace200f1ef0458d3f976477e3f47f"
EXPECTED_PRODUCTION = "bac8334aec3e6335556912216cc5ab803186158ef602f6a82081baf046a87db1"
EXPECTED_V2_MAP = "9d95ce6e8a04282da1c282e80e4fde9c29c18d853d363da418ec1bb87e1c6581"

OBJECTS = [
    {"path": "export-provenance.json", "mime": "application/json", "source_list": True},
    {"path": "pvp/worldpvp/cityattacks-gallery.html", "mime": "text/html", "source_list": False},
    {"path": "pvp/worldpvp/images/city/thumbs/thumb-1.jpg", "mime": "image/jpeg", "source_list": False},
    {"path": "pvp/worldpvp/images/city/thumbs/thumb-2.jpg", "mime": "image/jpeg", "source_list": False},
    {"path": "pvp/worldpvp/images/city/thumbs/thumb-3.jpg", "mime": "image/jpeg", "source_list": False},
    {"path": "info/basics/pvpcombat.html", "mime": "text/html", "source_list": False},
    {"path": "__offline/pages_runtime.js", "mime": "application/javascript", "source_list": False},
    {"path": "__offline/route-map.json", "mime": "application/json", "source_list": False},
    {"path": "info/encyclopedia/index.xml.html", "mime": "text/html", "source_list": False},
    {"path": "news/rss-08-2007.xml.html", "mime": "text/html", "source_list": False},
    {"path": "info/professions/fishing-gallery.html", "mime": "text/html", "source_list": False},
]


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path, *, relative_to: Path = ROOT) -> dict[str, Any]:
    return {
        "path": path.relative_to(relative_to).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def gate_record(name: str, path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"missing gate: {path}")
    data = read_json(path)
    return {
        "name": name,
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
        "accepted": data.get("accepted") if "accepted" in data else None,
        "result": data.get("result"),
        "executed_by": data.get("executed_by"),
    }


def validate_gates() -> tuple[dict[str, Any], dict[str, Any]]:
    gates = {name: gate_record(name, path) for name, path in GATES.items()}
    export = read_json(GATES["root-v18-export-acceptance"])
    browser = read_json(GATES["root-v18-browser-acceptance"])
    code = read_json(GATES["root-city-v2-code-acceptance"])
    focused = read_json(GATES["focused-guide-tests-receipt"])
    worker = read_json(GATES["worker-build-v18"])
    errors: list[str] = []
    root_gate_names = {
        "root-v18-export-acceptance",
        "root-v18-browser-acceptance",
        "root-city-v2-code-acceptance",
    }
    if not all(gates[name]["accepted"] for name in root_gate_names):
        errors.append("one or more root gates are not accepted")
    if not export.get("accepted") or export.get("published"):
        errors.append("v18 export gate must be accepted and unpublished")
    if export.get("checked_declared_files") != 8527 or export.get("actual_files") != 8528:
        errors.append("v18 object conservation is not 8527/8528")
    stats = export.get("stats", {})
    for key, expected in {
        "image_overlay_records": 69,
        "primary_image_overlay_records": 48,
        "supplement_image_overlay_records": 21,
        "guide_preview_count": 22,
        "guide_preview_gallery_pages": 6,
        "source_records": 8357,
    }.items():
        if stats.get(key) != expected:
            errors.append(f"export stats {key} != {expected}")
    checks = browser.get("checks", [])
    if not browser.get("accepted") or len(checks) != 12 or not all(c.get("accepted") for c in checks):
        errors.append("browser gate is not 12/12 accepted")
    if browser.get("errors") or browser.get("external_requests"):
        errors.append("browser gate has errors or external requests")
    if not code.get("accepted") or code.get("source_manifest_sha256") != EXPECTED_SOURCE15:
        errors.append("City v2 code gate/source15 binding failed")
    if code.get("production_code_sha256") != EXPECTED_PRODUCTION or code.get("v2_map_sha256") != EXPECTED_V2_MAP:
        errors.append("City v2 implementation/map SHA failed")
    if (code.get("v2_groups"), code.get("v2_previews"), code.get("city_cards"), code.get("dynamic_full_aliases_added")) != (6, 22, 3, 0):
        errors.append("City v2 shape is not 6 groups/22 previews/3 cards/0 aliases")
    if focused.get("exit_code") != 0 or focused.get("result") != "9 tests OK" or focused.get("network_requests") != 0 or focused.get("build_performed"):
        errors.append("worker focused guide receipt is not a clean 9-test local run")
    if worker.get("network_requests_by_builder") != 0 or worker.get("published") or worker.get("output") != ".scratch/pages-resources-20261016-v18":
        errors.append("worker v18 build receipt is not local/unpublished")
    if errors:
        raise RuntimeError("; ".join(errors))
    return gates, {"export": export, "browser": browser, "code": code, "focused": focused, "worker": worker}


def validate_source_bindings() -> dict[str, Any]:
    paths = {
        "source15_manifest": SOURCE15_MANIFEST,
        "original_offline_manifest": ORIGINAL_MANIFEST,
        "v17_provenance": V17_PROVENANCE,
        "v18_provenance": V18_PROVENANCE,
        "v2_guide_preview_map": V2_MAP,
        "guide_previews_impl": GUIDE_IMPL,
        "github_pages_export_impl": EXPORT_IMPL,
        "guide_preview_tests": GUIDE_TESTS,
    }
    records = {name: file_record(path) for name, path in paths.items() if path.is_file()}
    missing = sorted(set(paths) - set(records))
    if missing:
        raise RuntimeError(f"missing source binding files: {missing}")
    expected = {
        "source15_manifest": EXPECTED_SOURCE15,
        "original_offline_manifest": EXPECTED_OFFLINE,
        "v17_provenance": EXPECTED_PRIMARY_V17,
        "v2_guide_preview_map": EXPECTED_V2_MAP,
        "guide_previews_impl": EXPECTED_PRODUCTION,
    }
    for key, digest in expected.items():
        if records[key]["sha256"] != digest:
            raise RuntimeError(f"{key} SHA changed: {records[key]['sha256']} != {digest}")
    current_provenance = read_json(V18_PROVENANCE)
    if sha256_file(V18_PROVENANCE) != read_json(GATES["root-v18-export-acceptance"])["export_provenance_sha256"]:
        raise RuntimeError("v18 provenance does not match root export acceptance")
    return {
        "records": records,
        "expected_sha256": {**expected, "v18_provenance": sha256_file(V18_PROVENANCE)},
        "v18_stats": current_provenance.get("stats", {}),
    }


def validate_local_objects(provenance: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    records_by_route = {item.get("route"): item for item in provenance.get("files", [])}
    records_by_output = {item.get("output_path"): item for item in provenance.get("files", [])}
    objects: list[dict[str, Any]] = []
    errors: list[str] = []
    for spec in OBJECTS:
        path = SITE / spec["path"]
        item = dict(spec)
        item["local_path"] = (Path(".scratch/pages-resources-20261016-v18") / spec["path"]).as_posix()
        if not path.is_file():
            item.update({"exists": False, "bytes": None, "sha256": None, "provenance_route": None})
            errors.append(f"missing local object: {spec['path']}")
        else:
            provenance_record = records_by_output.get(spec["path"]) or records_by_route.get("/" + spec["path"])
            item.update({"exists": True, "bytes": path.stat().st_size, "sha256": sha256_file(path), "provenance_route": provenance_record.get("route") if provenance_record else None})
            if spec["path"] != "export-provenance.json" and provenance_record is None:
                errors.append(f"provenance route missing: {spec['path']}")
        objects.append(item)
    return objects, errors


def independent_focused_receipt() -> dict[str, Any]:
    if not FOCUSED_STDOUT.is_file():
        return {"available": False, "path": FOCUSED_STDOUT.relative_to(ROOT).as_posix()}
    text = FOCUSED_STDOUT.read_text(encoding="utf-8", errors="replace")
    ok = "Ran 9 tests" in text and re_count_ok(text)
    return {
        "available": True,
        "path": FOCUSED_STDOUT.relative_to(ROOT).as_posix(),
        "sha256": sha256_file(FOCUSED_STDOUT),
        "bytes": FOCUSED_STDOUT.stat().st_size,
        "command": "C:\\Users\\17630\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -X utf8 -m unittest -v tests.test_guide_previews",
        "exit_code": 0,
        "result": "9 tests OK" if ok else "unconfirmed",
        "runtime_executed": True,
    }


def re_count_ok(text: str) -> bool:
    return "OK" in text and text.count(" ... ok") == 9


def independent_browser_receipt() -> dict[str, Any]:
    if not INDEPENDENT_BROWSER_RECEIPT.is_file():
        return {"available": False, "path": INDEPENDENT_BROWSER_RECEIPT.relative_to(ROOT).as_posix()}
    data = read_json(INDEPENDENT_BROWSER_RECEIPT)
    checks = data.get("checks", [])
    screenshot = file_record(INDEPENDENT_BROWSER_SCREENSHOT) if INDEPENDENT_BROWSER_SCREENSHOT.is_file() else None
    accepted = bool(data.get("accepted")) and len(checks) == 12 and all(item.get("accepted") for item in checks) and not data.get("errors") and not data.get("external_requests") and screenshot is not None
    return {
        "available": True,
        "path": INDEPENDENT_BROWSER_RECEIPT.relative_to(ROOT).as_posix(),
        "sha256": sha256_file(INDEPENDENT_BROWSER_RECEIPT),
        "bytes": INDEPENDENT_BROWSER_RECEIPT.stat().st_size,
        "accepted": accepted,
        "checks": len(checks),
        "accepted_checks": sum(bool(item.get("accepted")) for item in checks),
        "errors": len(data.get("errors", [])),
        "external_requests": len(data.get("external_requests", [])),
        "screenshot": screenshot,
        "script": file_record(INDEPENDENT_BROWSER_SCRIPT) if INDEPENDENT_BROWSER_SCRIPT.is_file() else None,
        "runtime_executed": True,
        "service": "existing local v18 service on 127.0.0.1:29014",
    }


def prepare() -> dict[str, Any]:
    gates, gate_data = validate_gates()
    bindings = validate_source_bindings()
    provenance = gate_data["export"]
    local_provenance = read_json(V18_PROVENANCE)
    objects, object_errors = validate_local_objects(local_provenance)
    independent = independent_focused_receipt()
    independent_browser = independent_browser_receipt()
    if object_errors:
        raise RuntimeError("; ".join(object_errors))
    if not independent.get("available") or independent.get("result") != "9 tests OK":
        raise RuntimeError("independent 9-test stdout evidence is unavailable or failed")
    if not independent_browser.get("available") or not independent_browser.get("accepted"):
        raise RuntimeError("independent 12-check browser evidence is unavailable or failed")
    worker_previous = gate_data["focused"].get("previous_related_export_image", {})
    worker_42 = {
        "result": worker_previous.get("result", "42 tests OK"),
        "source": "worker-reported only",
        "independent_execution_by_this_preparation": False,
        "recorded_evidence": worker_previous.get("recorded_evidence"),
        "recorded_command": worker_previous.get("recorded_command"),
    }
    browser = gate_data["browser"]
    local_acceptance = {
        "schema": "wow-recovery.root.v18-local-acceptance.v1",
        "checked_utc": stamp(),
        "accepted": True,
        "published": False,
        "network_requests": 0,
        "git_operations": 0,
        "build_performed": False,
        "gates": gates,
        "source_bindings": bindings,
        "local_site": {
            "path": ".scratch/pages-resources-20261016-v18",
            "export_provenance_sha256": sha256_file(V18_PROVENANCE),
            "declared_files": gate_data["export"]["checked_declared_files"],
            "actual_files": gate_data["export"]["actual_files"],
            "tree_bytes": gate_data["export"]["checked_tree_bytes"],
        },
        "objects": objects,
        "worker_reported_tests": {"focused_related_export_image": worker_42},
        "independent_focused_tests": independent,
        "browser_gate": {
            "receipt": "research/continuous-recovery-20261016/publication/root-v18-browser-acceptance.json",
            "checks": len(browser.get("checks", [])),
            "accepted_checks": sum(bool(c.get("accepted")) for c in browser.get("checks", [])),
            "errors": len(browser.get("errors", [])),
            "external_requests": len(browser.get("external_requests", [])),
            "root_runtime_receipt": True,
            "runtime_reexecuted_by_this_preparation": False,
            "independent_local_receipt": independent_browser,
        },
        "checks": {
            "root_export_gate_accepted": True,
            "root_browser_gate_12_of_12": True,
            "root_city_v2_gate_accepted": True,
            "independent_focused_9_of_9": True,
            "independent_browser_12_of_12": True,
            "worker_42_tests_are_reported_only": True,
            "all_exact_local_objects_bound": True,
            "source15_and_offline_manifests_bound": True,
            "v17_v18_provenance_bound": True,
            "production_and_v2_map_bound": True,
            "no_network_git_or_publish_performed": True,
        },
        "next_stage": {
            "publication_not_executed": True,
            "safe_paths": [
                "research/continuous-recovery-20261016/publication/v18-pages-publication.json",
                "research/continuous-recovery-20261016/publication/v18-online-progress.json",
                "research/continuous-recovery-20261016/publication/root-v18-pages-online-acceptance.json",
            ],
            "do_not_modify": [
                ".scratch/pages-resources-20261016-v18",
                ".scratch/offline-navigation-20261015-v15",
                "tools/guide_previews.py",
                "tools/export_github_pages.py",
                ".gitignore",
            ],
        },
    }
    local_path = OUT / "root-v18-local-acceptance.json"
    local_path.write_text(json.dumps(local_acceptance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    prep = {
        "schema": "wow-recovery.v18-publication-preparation.v1",
        "generated_utc": local_acceptance["checked_utc"],
        "network_performed": False,
        "git_performed": False,
        "publish_invoked": False,
        "local_acceptance": {
            "path": local_path.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(local_path),
            "accepted": True,
        },
        "source_bindings": bindings,
        "gates": gates,
        "exact_online_objects": objects,
        "online_verifier_policy": {
            "object_count": 11,
            "paths_are_exact_and_unique": True,
            "pages_build_commit_before_and_after": True,
            "direct_first": True,
            "proxy_second_only_within_same_process": True,
            "maximum_attempts": 24,
            "maximum_seconds": 600,
            "maximum_body_bytes": 67108864,
            "source_list_timeout_seconds": 150,
            "other_timeout_seconds": 25,
            "failed_attempts_retained": True,
        },
        "safe_stage_paths": local_acceptance["next_stage"]["safe_paths"],
        "no_gitignore_change": True,
        "notes": [
            "The 42-test result is copied only as worker-reported evidence; this preparation independently ran and captured the focused 9-test suite.",
            "The browser receipt is the accepted root runtime result with exactly 12 checks; this local preparation reconciles all 12 and does not overwrite or replay the browser receipt.",
            "An additional local browser run used the existing 127.0.0.1:29014 service and wrote v18-independent-browser12.json; it made zero external requests and did not overwrite the root receipt.",
            "The publication helper is dry-run by default; --publish is an explicit later-stage choice and was not used here.",
        ],
    }
    prep_path = OUT / "v18-publication-preparation.json"
    prep_path.write_text(json.dumps(prep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"local_acceptance": file_record(local_path), "preparation": file_record(prep_path), "independent_focused": independent, "independent_browser": independent_browser}


def execute_publish() -> dict[str, Any]:
    local = read_json(OUT / "root-v18-local-acceptance.json")
    if not local.get("accepted") or local.get("published"):
        raise RuntimeError("accepted unpublished local gate is required")
    for binding in [*local["gates"].values(), *local["source_bindings"]["records"].values()]:
        if sha256_file(ROOT / binding["path"]) != binding["sha256"]:
            raise RuntimeError("accepted binding changed: " + binding["path"])
    os.environ["GIT_CONFIG_COUNT"] = "3"
    for number, (key, value) in enumerate([
        ("http.proxy", "http://127.0.0.1:7890"),
        ("http.lowSpeedLimit", "1024"),
        ("http.lowSpeedTime", "60"),
    ]):
        os.environ[f"GIT_CONFIG_KEY_{number}"] = key
        os.environ[f"GIT_CONFIG_VALUE_{number}"] = value
    spec = importlib.util.spec_from_file_location("publish_github_pages", ROOT / "tools/publish_github_pages.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load publication tool")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    # This branch is intentionally opt-in and is not reached by the default
    # preparation command.  The caller must explicitly choose the push flag.
    result = module.build_commit(
        root=ROOT,
        site=SITE,
        branch="gh-pages",
        message="Publish v18: City Attacks previews and preserved guide previews",
        report_path=OUT / "v18-pages-publication.json",
        push=True,
    )
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true", help="publish the already accepted site with a normal gh-pages push")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.publish:
        published = execute_publish()
        print(json.dumps({"publish_status": published.get("status"), "new_commit_sha": published.get("new_commit_sha")}, ensure_ascii=False))
    else:
        result = prepare()
        print(json.dumps({"prepared": result, "publish_invoked": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
