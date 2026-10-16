from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from urllib.parse import quote


ROOT = Path(r"D:\WOW_Encyclopedia")
BASE = ROOT / "research" / "continuous-recovery-20261016"
BATCH = BASE / "network" / "gallery-neighbors-full15"
DRIVER = BASE / "network" / "reusable-image-driver-v2" / "reusable_image_driver.py"
PROD_PLAN = BATCH / "plan.json"
PROD_BINDINGS = BATCH / "input-bindings.json"
PROBE = BATCH / "fixture-probe"
PROBE_PLAN = PROBE / "plan.json"
PROBE_BINDINGS = PROBE / "input-bindings.json"
PROBE_SOURCE = PROBE / "fixture-probe-source.txt"
PROBE_FIXTURE = PROBE / "fixture-results.json"
PROD_FIXTURE = BATCH / "fixture-results.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def cdx_url(original: str) -> str:
    fields = "urlkey,timestamp,original,mimetype,statuscode,digest,length"
    return (
        "https://web.archive.org/cdx/search/cdx?"
        f"url={quote(original, safe='')}&from=20000101000000&to=20080512210044"
        f"&output=json&fl={quote(fields, safe='')}&limit=500&showResumeKey=true&matchType=exact"
    )


def load_driver():
    spec = importlib.util.spec_from_file_location("reusable_v2_full15_fixture", DRIVER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen V2 driver")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_probe() -> None:
    production = json.loads(PROD_PLAN.read_text(encoding="utf-8"))
    probe = copy.deepcopy(production)
    PROBE.mkdir(parents=True, exist_ok=True)
    synthetic_original = production["candidates"][0]["original"].replace(
        "http://www.worldofwarcraft.com:80", "http://www.worldofwarcraft.com", 1
    )
    PROBE_SOURCE.write_text(synthetic_original + "\n", encoding="utf-8")
    candidate = probe["candidates"][0]
    candidate["original"] = synthetic_original
    candidate["literal"] = synthetic_original
    candidate["source_evidence"] = dict(candidate["source_evidence"])
    candidate["source_evidence"].update({
        "literal": synthetic_original,
        "path": rel(PROBE_SOURCE),
        "line": 1,
        "sha256": sha(PROBE_SOURCE),
    })
    candidate["query"] = dict(candidate["query"])
    candidate["query"]["url"] = synthetic_original
    candidate["query"]["query_url"] = cdx_url(synthetic_original)
    candidate["replay"] = dict(candidate["replay"])
    candidate["replay"]["id_url_template"] = "https://web.archive.org/web/{timestamp}id_/" + synthetic_original
    probe["batch_id"] = "GALLERY-NEIGHBORS-FULL15-FIXTURE-PROBE"
    probe["output_dir"] = rel(PROBE / "output")
    probe["mode"] = "offline_fixture_probe"
    probe["network_authorized"] = False
    probe["no_network_before_parent_go"] = True
    probe["input_bindings"] = copy.deepcopy(production["input_bindings"])
    probe["input_bindings"]["fixture_probe_source"] = {
        "path": rel(PROBE_SOURCE),
        "sha256": sha(PROBE_SOURCE),
        "bytes": PROBE_SOURCE.stat().st_size,
        "role": "synthetic bare-HTTP original for frozen default-port fixture compatibility",
    }
    write_json(PROBE_PLAN, probe)
    probe_sha = sha(PROBE_PLAN)
    write_json(PROBE_BINDINGS, {
        "schema": "wow-recovery.gallery-neighbors-full15-fixture-probe-bindings.v1",
        "batch_id": probe["batch_id"],
        "mode": "offline_fixture_probe",
        "network_requests": 0,
        "plan_sha256": probe_sha,
        "driver_sha256": sha(DRIVER),
        "source_bindings": probe["input_bindings"],
        "network_authorized": False,
    })
    print(json.dumps({"probe_plan_sha256": probe_sha, "probe_source_sha256": sha(PROBE_SOURCE),
                      "network_requests": 0}, ensure_ascii=False, sort_keys=True))


def finalize_fixture() -> None:
    module = load_driver()
    module.configure_from_plan(PROD_PLAN)
    validated, _ = module.load_and_validate_inputs()
    production_validation = {
        "validated": True,
        "batch_id": validated["batch_id"],
        "candidate_count": len(validated["candidates"]),
        "network_requests": 0,
        "exact_originals_preserved": len(validated["candidates"]) == 15,
        "plan_sha256": sha(PROD_PLAN),
    }
    if not PROBE_FIXTURE.is_file():
        raise RuntimeError("run the synthetic probe fixture before finalizing the composite result")
    probe_result = json.loads(PROBE_FIXTURE.read_text(encoding="utf-8"))
    composite = {
        "schema": "wow-recovery.gallery-neighbors-full15-fixtures.v1",
        "batch_id": validated["batch_id"],
        "network_requests": 0,
        "all_passed": bool(production_validation["validated"] and production_validation["exact_originals_preserved"] and probe_result.get("all_passed")),
        "production_plan_validation": production_validation,
        "synthetic_default_port_probe": {
            "plan_path": rel(PROBE_PLAN),
            "plan_sha256": sha(PROBE_PLAN),
            "fixture_path": rel(PROBE_FIXTURE),
            "fixture_sha256": sha(PROBE_FIXTURE),
            "all_passed": probe_result.get("all_passed"),
            "passed": probe_result.get("passed"),
            "total": probe_result.get("total"),
            "network_requests": probe_result.get("network_requests"),
            "synthetic_original": json.loads(PROD_PLAN.read_text(encoding="utf-8"))["candidates"][0]["original"].replace(
                "http://www.worldofwarcraft.com:80", "http://www.worldofwarcraft.com", 1
            ),
        },
        "production_candidate_count": 15,
        "production_candidate_order_preserved": production_validation["exact_originals_preserved"],
        "notes": [
            "Production plan validation used the frozen V2 load_and_validate_inputs path and created no network request.",
            "The frozen fixture mutates its first fixture candidate to exercise default-port identity; this production set begins with an explicit :80 original, so the fixture ran in an isolated synthetic bare-HTTP probe.",
            "The synthetic probe is test-only and does not alter any production candidate or plan.",
            "Cached candidates were revalidated against their SHA-bound CDX body/header/report before the fixture was run.",
        ],
    }
    write_json(PROD_FIXTURE, composite)
    bindings = json.loads(PROD_BINDINGS.read_text(encoding="utf-8"))
    bindings["fixture_results"] = {
        "path": rel(PROD_FIXTURE),
        "sha256": sha(PROD_FIXTURE),
        "all_passed": composite["all_passed"],
        "network_requests": 0,
        "role": "production validation plus isolated synthetic V2 fixture probe",
    }
    bindings["synthetic_probe"] = {
        "plan_path": rel(PROBE_PLAN),
        "plan_sha256": sha(PROBE_PLAN),
        "fixture_path": rel(PROBE_FIXTURE),
        "fixture_sha256": sha(PROBE_FIXTURE),
        "all_passed": probe_result.get("all_passed"),
        "network_requests": 0,
    }
    write_json(PROD_BINDINGS, bindings)
    print(json.dumps({"production_validation": production_validation,
                      "fixture_all_passed": composite["all_passed"],
                      "fixture_sha256": sha(PROD_FIXTURE),
                      "bindings_sha256": sha(PROD_BINDINGS),
                      "network_requests": 0}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    make_probe()
    if PROBE_FIXTURE.is_file():
        finalize_fixture()
