#!/usr/bin/env python3
"""Run the one root-authorized v21 Pages export from frozen local inputs."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
SOURCE_STAGE = ROOT / ".scratch/offline-navigation-20261015-v15"
SOURCE_SITE = SOURCE_STAGE / "site"
SOURCE_MANIFEST = SOURCE_STAGE / "build-manifest.json"
OUTPUT = ROOT / ".scratch/pages-resources-20261016-v21"
ROOT_V17_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v17-input-acceptance.json"
ROOT_V18_EXPORT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v18-export-acceptance.json"
ROOT_V18_LOCAL_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v18-local-acceptance.json"
ROOT_V18_BROWSER_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v18-browser-acceptance.json"
ROOT_V2_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-city-v2-code-acceptance.json"
FOCUSED_RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v18-build/focused-guide-tests-receipt.json"
ORIGINAL_OFFLINE_MANIFEST = ROOT / "offline/build-manifest.json"
V18_PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v18/export-provenance.json"
V19_PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v19/export-provenance.json"
ROOT_V19_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v19-export-acceptance.json"
V19_RECONCILIATION = ROOT / "research/continuous-recovery-20261016/integration/v19-build/post-export-reconciliation-v19-final.json"
V18_BUILD_RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v18-build/worker-build-v18.json"
V19_PREPARATION_RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v19-build/prepare-v19-inputs.json"
V20_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261016/integration/v20-primary-news-source-map.json"
V20_PROVENANCE = ROOT / ".scratch/pages-resources-20261016-v20/export-provenance.json"
ROOT_V20_EXPORT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-v20-export-acceptance.json"
PREPARATION_RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v21-build/prepare-v21-inputs.json"
RECEIPT = ROOT / "research/continuous-recovery-20261016/integration/v21-build/worker-build-v21.json"
V1_GUIDE_MAP = ROOT / "research/continuous-recovery-20261016/integration/guide-previews-source-map.json"
V2_GUIDE_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
V19_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261016/integration/v19-primary-news-source-map.json"
V21_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261016/integration/v21-primary-news-source-map.json"
V21_LATE_MAP = ROOT / "research/continuous-recovery-20261016/integration/v21-august-late-source-map.json"
ROOT_AUG20_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-aug20-source-acceptance.json"
ROOT_AUG_REMAINING15_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-aug-remaining15-source-acceptance.json"
ROOT_AUG_FINAL3_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-aug-final3-source-acceptance.json"
ROOT_AUG_CACHED19_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-aug-cached19-source-acceptance.json"
ROOT_AUG_LATE11_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-aug-late11-source-acceptance.json"
AUG20_SOURCE_MAP = ROOT / "research/continuous-recovery-20261016/network/aug27-01-20/output/source-map.json"
AUG_REMAINING15_SOURCE_MAP = ROOT / "research/continuous-recovery-20261016/network/aug27-remaining15/output/source-map.json"
AUG_FINAL3_SOURCE_MAP = ROOT / "research/continuous-recovery-20261016/network/aug27-final3/output/source-map.json"
AUG_CACHED19_SOURCE_MAP = ROOT / "research/continuous-recovery-20261016/network/aug27-cached19/output/source-map.json"
AUG_LATE11_SOURCE_MAP = ROOT / "research/continuous-recovery-20261016/network/aug27-same-day-late11/output/source-map.json"
NEWS_SHARED10_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-news-shared10-source-acceptance.json"
NEWS_SHARED13_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-news-shared13-source-acceptance.json"
NEWS_SHARED10_SOURCE_MAP = ROOT / "research/continuous-recovery-20261016/network/news-shared10/source-map.json"
NEWS_SHARED13_SOURCE_MAP = ROOT / "research/continuous-recovery-20261016/network/news-shared13/source-map.json"
MIN_FREE_BYTES = 11_005_853_696
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"
sys.path.insert(0, str(ROOT / "tools"))
import export_github_pages

FROZEN_MANIFEST_SHA256 = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
ORIGINAL_OFFLINE_MANIFEST_SHA256 = "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"
V18_PROVENANCE_SHA256 = "5e233b4e951b15f6004a971eb5082fb77202b59234f8a4561d3d03d671daf3b5"
ROOT_V17_ACCEPTANCE_SHA256 = "d45384119fe8ba9578a0a11a25ce79653460f2a65562423a5ad66ebd17883429"
ROOT_V18_EXPORT_ACCEPTANCE_SHA256 = "1eddccd098f380566beecc5a5e0ee0dfe6e1522ac68afa87ba2a4da4414e2c4c"
ROOT_V18_LOCAL_ACCEPTANCE_SHA256 = "ef768465d6945dd3972fe60abdc201c71a913c5b60566428658402aed6fb8a5d"
ROOT_V18_BROWSER_ACCEPTANCE_SHA256 = "cf1152f27bcb73d8288afff81e344717440c8b05f2f295bc4652ca377143dfa3"
V18_BUILD_RECEIPT_SHA256 = "17ba2c060b72a08da2219a74867cf569f1e98f758996b72c22241e981f0a7c72"
ROOT_V2_ACCEPTANCE_SHA256 = "215bcca89a55bb3a5756998d428f6e62f01577ef58384e4a490b8e9049f63eb2"
V2_GUIDE_MAP_SHA256 = "9d95ce6e8a04282da1c282e80e4fde9c29c18d853d363da418ec1bb87e1c6581"
V1_GUIDE_MAP_SHA256 = "cf0da5fec45993684676d94d1cc09fad3f5a421dabbb18b56861000daa6248b2"
V19_PREPARATION_RECEIPT_SHA256 = "903bf57c53ce9b2b7bd25b6e9a3c1ab0541c407015bb9d212404c61c40b6e9c6"
PREPARATION_RECEIPT_SHA256 = "900e8afab240c30f600fd1bb6c306c06f9dbd11fae3f66f2b7e56cbebcc41979"
V19_PRIMARY_MAP_SHA256 = "7587fcb84e79f90502953d12e425af8a418916b2d4a8f6d211c7f8be24cf5df7"
V20_PRIMARY_MAP_SHA256 = "2629ac0915f933202f60a912643c830aac3c66486e28f7d42c061e5f48f9dc77"
V21_PRIMARY_MAP_SHA256 = "9a900cf93a706657c76e36f6291bd646992a94147bb48cd66b8acba6379d6c33"
V21_LATE_MAP_SHA256 = "a21faaf398e4b605a441da7ca9f23d23e75e1e1bfb59a824d59e5aa7a981d772"
V19_PROVENANCE_SHA256 = "d0359a5daeabe1854b674e3f296f37fa3d6e1417f217848b22233e45ac898631"
V20_PROVENANCE_SHA256 = "c4b741691f9ac8ad8201dfc35e6af81119c60e62afa07f08c569ec3a9e7a9f50"
ROOT_V19_ACCEPTANCE_SHA256 = "b374b7760040aaf6e998921d772540632195282cfb2cc1b193b5abeae2a1a542"
ROOT_V20_EXPORT_ACCEPTANCE_SHA256 = "8db1088841c41e2fde6c72e45b10aede1221b15e65600e19bd09eba8e0a9e92e"
V19_RECONCILIATION_SHA256 = "80198de187f027cb49036afaac816cd2e0185a17a3a9b6d8b54b4307d82a73d1"
ROOT_AUG20_ACCEPTANCE_SHA256 = "42bf3efd4ffaadf760e67dfdc86ffa359adcbcc3c6907218f48de33f66f7c2e3"
ROOT_AUG_REMAINING15_ACCEPTANCE_SHA256 = "bc99dae101f2fca429faf5c88df2c8721cca3d5cc479a0ee28c6739e1699dbb6"
ROOT_AUG_FINAL3_ACCEPTANCE_SHA256 = "16e4680d8d396ea94a2d4a17ffa7da918b8465ed723eb7be876c0c6144b7d56a"
ROOT_AUG_CACHED19_ACCEPTANCE_SHA256 = "72dfafd5d389876572d06059e6891ccc0190bb56704b2c9d4a00b3e1d7162ca2"
ROOT_AUG_LATE11_ACCEPTANCE_SHA256 = "e89571cd8e9bdbf916af9a013a9d459270ed07de09240aa1a015b24d01dbc874"
AUG20_SOURCE_MAP_SHA256 = "f427d3d672e1eebd1d94ee3fe76757c699159579d7781e1e2fb85c5d895d16f0"
AUG_REMAINING15_SOURCE_MAP_SHA256 = "fb2cc203d23c0b88f3af04d561b857a6b21f6fb09a0129e3e08ba07bf1318f72"
AUG_FINAL3_SOURCE_MAP_SHA256 = "2249ea2597e61b3407ba31e053b49b063ee32acdca1b9f832939d8f53d90bca6"
AUG_CACHED19_SOURCE_MAP_SHA256 = "77a111646fc8dae692449ddbe2035b486cc53062f5ec1f1f9cf66b09eef1e2c3"
AUG_LATE11_SOURCE_MAP_SHA256 = "61c1791a00df70236d6109ceeb7023e66a0fe4b356070918ea5d7cb21da9d59e"
NEWS_SHARED10_ACCEPTANCE_SHA256 = "65354d44666d68654a619efdc10bc8bd2cacab0cd085f3d729bdb6159309be4f"
NEWS_SHARED13_ACCEPTANCE_SHA256 = "cda6475904c67a034dbbaee20362a1b5c65f9d376e960b91f6c2918c10875ff2"
NEWS_SHARED10_SOURCE_MAP_SHA256 = "e73e0ac9e465da9dce571e55a6a4c730c02a35c68d346c5f81ad5f72220f059d"
NEWS_SHARED13_SOURCE_MAP_SHA256 = "e5148b15bb67eae6e5f24176549283ab0f021ee6502c06ed3f10e11d38ba99c6"

PRODUCTION_SHA256 = {
    "tools/guide_previews.py": "bac8334aec3e6335556912216cc5ab803186158ef602f6a82081baf046a87db1",
    "tools/export_github_pages.py": "c16647890b488f534aa7945f3333ca38a6583b8ca6dad6ce70e40a06d3685de9",
}
TEST_SHA256 = {
    "tests/test_guide_previews.py": "ec8d351347efb790cb003bff2f0e94493a85f6da75f801a26b8422a6d88b9852",
}
MAP_SHA256 = {
    "research/resource-resume-20261013/round002/entity-source-map.json": "9342b01e4f8ad683ecbceafb5d10064ea2f0eb6200d0f94f02dca3812e3cc325",
    "research/resource-resume-20261013/round003/entity-source-map.json": "17b2d0eb4c1d52d128a19c3c98d1ea15596a380cc252cac34fbeef05b34bcc57",
    "research/continuous-recovery-20261016/integration/v16-primary-news-image-source-map.json": "b978caed7b97a06eb04a3ce6fd69ef12d3b9903eef68ff8d1de00f26e51cd04b",
    "research/continuous-recovery-20261016/integration/v17-primary-news-image-source-map.json": "f4866b36d664535283baf1e5a90db0b93eea82ad81b34281cc2b94805566ca9d",
    "research/related-sites-20261014/integration/regional-image-source-map.json": "7cbad0d949749ce5fbdbdef95b65e6e95f8cd8c15546285814931c6e1b325502",
    "research/related-sites-20261014/integration/karazhan-late-source-map.json": "f7f84beac63d63ec5a0c589dcfad3209e016cd4f9acf0f39c9b313f79cb37bb4",
    "research/media-screenshots-20261015/late-image-source-map.json": "1bb8405e58eaf19999313c160b5db256a11559cbc70f8cfccf564f05c99cff03",
    "research/continuous-recovery-20261016/integration/v16-eu-image-source-map.json": "2efd473a586f155743ee18cabc2885ca489e0d03dbd58bd473a7dcb825c9c1e3",
    "research/continuous-recovery-20261016/integration/guide-previews-source-map.json": V1_GUIDE_MAP_SHA256,
    "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json": V2_GUIDE_MAP_SHA256,
    "research/continuous-recovery-20261016/integration/v19-primary-news-source-map.json": V19_PRIMARY_MAP_SHA256,
    "research/continuous-recovery-20261016/integration/v20-primary-news-source-map.json": V20_PRIMARY_MAP_SHA256,
    "research/continuous-recovery-20261016/integration/v21-primary-news-source-map.json": V21_PRIMARY_MAP_SHA256,
    "research/continuous-recovery-20261016/integration/v21-august-late-source-map.json": V21_LATE_MAP_SHA256,
}

PRIMARY_MAPS = [
    ROOT / "research/resource-resume-20261013/round002/entity-source-map.json",
    ROOT / "research/resource-resume-20261013/round003/entity-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v16-primary-news-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v17-primary-news-image-source-map.json",
    V20_PRIMARY_MAP,
    V21_PRIMARY_MAP,
]
SUPPLEMENT_MAPS = [
    ROOT / "research/related-sites-20261014/integration/regional-image-source-map.json",
    ROOT / "research/related-sites-20261014/integration/karazhan-late-source-map.json",
    ROOT / "research/media-screenshots-20261015/late-image-source-map.json",
    ROOT / "research/continuous-recovery-20261016/integration/v16-eu-image-source-map.json",
    V21_LATE_MAP,
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def require_hash(path: Path, expected: str, label: str) -> str:
    if not path.is_file():
        raise RuntimeError(f"{label} is missing: {path}")
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f"{label} SHA-256 changed: expected {expected}, got {actual}")
    return actual


def read_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"{label} is not valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{label} is not an object: {path}")
    return payload


def locked_input_hashes() -> dict[str, str]:
    paths: dict[str, tuple[Path, str]] = {
        rel(SOURCE_MANIFEST): (SOURCE_MANIFEST, FROZEN_MANIFEST_SHA256),
        rel(ORIGINAL_OFFLINE_MANIFEST): (ORIGINAL_OFFLINE_MANIFEST, ORIGINAL_OFFLINE_MANIFEST_SHA256),
        rel(ROOT_V17_ACCEPTANCE): (ROOT_V17_ACCEPTANCE, ROOT_V17_ACCEPTANCE_SHA256),
        rel(ROOT_V18_EXPORT_ACCEPTANCE): (ROOT_V18_EXPORT_ACCEPTANCE, ROOT_V18_EXPORT_ACCEPTANCE_SHA256),
        rel(ROOT_V18_LOCAL_ACCEPTANCE): (ROOT_V18_LOCAL_ACCEPTANCE, ROOT_V18_LOCAL_ACCEPTANCE_SHA256),
        rel(ROOT_V18_BROWSER_ACCEPTANCE): (ROOT_V18_BROWSER_ACCEPTANCE, ROOT_V18_BROWSER_ACCEPTANCE_SHA256),
        rel(ROOT_V2_ACCEPTANCE): (ROOT_V2_ACCEPTANCE, ROOT_V2_ACCEPTANCE_SHA256),
        rel(FOCUSED_RECEIPT): (FOCUSED_RECEIPT, "9ae29a7db52077a3c94f7a85b67a444f28cb2c2f985fc8b9242ed96601800b5f"),
        rel(V18_PROVENANCE): (V18_PROVENANCE, V18_PROVENANCE_SHA256),
        rel(V18_BUILD_RECEIPT): (V18_BUILD_RECEIPT, V18_BUILD_RECEIPT_SHA256),
        rel(V19_PREPARATION_RECEIPT): (V19_PREPARATION_RECEIPT, V19_PREPARATION_RECEIPT_SHA256),
        rel(PREPARATION_RECEIPT): (PREPARATION_RECEIPT, PREPARATION_RECEIPT_SHA256),
        rel(V19_PROVENANCE): (V19_PROVENANCE, V19_PROVENANCE_SHA256),
        rel(ROOT_V19_ACCEPTANCE): (ROOT_V19_ACCEPTANCE, ROOT_V19_ACCEPTANCE_SHA256),
        rel(V20_PROVENANCE): (V20_PROVENANCE, V20_PROVENANCE_SHA256),
        rel(ROOT_V20_EXPORT_ACCEPTANCE): (ROOT_V20_EXPORT_ACCEPTANCE, ROOT_V20_EXPORT_ACCEPTANCE_SHA256),
        rel(V19_RECONCILIATION): (V19_RECONCILIATION, V19_RECONCILIATION_SHA256),
        rel(ROOT_AUG20_ACCEPTANCE): (ROOT_AUG20_ACCEPTANCE, ROOT_AUG20_ACCEPTANCE_SHA256),
        rel(ROOT_AUG_REMAINING15_ACCEPTANCE): (ROOT_AUG_REMAINING15_ACCEPTANCE, ROOT_AUG_REMAINING15_ACCEPTANCE_SHA256),
        rel(ROOT_AUG_FINAL3_ACCEPTANCE): (ROOT_AUG_FINAL3_ACCEPTANCE, ROOT_AUG_FINAL3_ACCEPTANCE_SHA256),
        rel(ROOT_AUG_CACHED19_ACCEPTANCE): (ROOT_AUG_CACHED19_ACCEPTANCE, ROOT_AUG_CACHED19_ACCEPTANCE_SHA256),
        rel(ROOT_AUG_LATE11_ACCEPTANCE): (ROOT_AUG_LATE11_ACCEPTANCE, ROOT_AUG_LATE11_ACCEPTANCE_SHA256),
        rel(AUG20_SOURCE_MAP): (AUG20_SOURCE_MAP, AUG20_SOURCE_MAP_SHA256),
        rel(AUG_REMAINING15_SOURCE_MAP): (AUG_REMAINING15_SOURCE_MAP, AUG_REMAINING15_SOURCE_MAP_SHA256),
        rel(AUG_FINAL3_SOURCE_MAP): (AUG_FINAL3_SOURCE_MAP, AUG_FINAL3_SOURCE_MAP_SHA256),
        rel(AUG_CACHED19_SOURCE_MAP): (AUG_CACHED19_SOURCE_MAP, AUG_CACHED19_SOURCE_MAP_SHA256),
        rel(AUG_LATE11_SOURCE_MAP): (AUG_LATE11_SOURCE_MAP, AUG_LATE11_SOURCE_MAP_SHA256),
        rel(NEWS_SHARED10_ACCEPTANCE): (NEWS_SHARED10_ACCEPTANCE, NEWS_SHARED10_ACCEPTANCE_SHA256),
        rel(NEWS_SHARED13_ACCEPTANCE): (NEWS_SHARED13_ACCEPTANCE, NEWS_SHARED13_ACCEPTANCE_SHA256),
        rel(NEWS_SHARED10_SOURCE_MAP): (NEWS_SHARED10_SOURCE_MAP, NEWS_SHARED10_SOURCE_MAP_SHA256),
        rel(NEWS_SHARED13_SOURCE_MAP): (NEWS_SHARED13_SOURCE_MAP, NEWS_SHARED13_SOURCE_MAP_SHA256),
        rel(V1_GUIDE_MAP): (V1_GUIDE_MAP, V1_GUIDE_MAP_SHA256),
        rel(V2_GUIDE_MAP): (V2_GUIDE_MAP, V2_GUIDE_MAP_SHA256),
    }
    for relative, expected in {**PRODUCTION_SHA256, **TEST_SHA256, **MAP_SHA256}.items():
        paths[relative] = (ROOT / relative, expected)
    return {relative: require_hash(path, expected, relative) for relative, (path, expected) in paths.items()}


def validate_gates() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    v17 = read_object(ROOT_V17_ACCEPTANCE, "root v17 input acceptance")
    if v17.get("accepted") is not True or v17.get("export_started") is not False:
        raise RuntimeError("root v17 input acceptance is not accepted and pre-export")
    for key, expected in {
        "source_manifest_sha256": FROZEN_MANIFEST_SHA256,
        "primary_overlays": 48,
        "supplement_overlays": 21,
        "total_overlays": 69,
        "source_records": 8357,
    }.items():
        if v17.get(key) != expected:
            raise RuntimeError(f"root v17 gate differs for {key}: {v17.get(key)!r}")

    v18_export = read_object(ROOT_V18_EXPORT_ACCEPTANCE, "root v18 export acceptance")
    if v18_export.get("accepted") is not True or v18_export.get("published") is not False:
        raise RuntimeError("root v18 export acceptance is not accepted and unpublished")
    for key, expected in {
        "checked_declared_files": 8527,
        "actual_files": 8528,
        "stats": None,
    }.items():
        if key == "stats":
            stats = v18_export.get("stats") or {}
            if any(stats.get(name) != value for name, value in {
                "output_files": 8527,
                "source_records": 8357,
                "image_overlay": 69,
                "primary_image_overlay_records": 48,
                "supplement_image_overlay_records": 21,
                "guide_preview_count": 22,
                "guide_preview_gallery_pages": 6,
            }.items()):
                raise RuntimeError("root v18 export stats do not match the accepted v18 tree")
        elif v18_export.get(key) != expected:
            raise RuntimeError(f"root v18 export gate differs for {key}: {v18_export.get(key)!r}")
    v18_local = read_object(ROOT_V18_LOCAL_ACCEPTANCE, "root v18 local acceptance")
    if v18_local.get("accepted") is not True or v18_local.get("network_requests") != 0 or v18_local.get("published") is not False:
        raise RuntimeError("root v18 local acceptance is not an accepted local-only gate")
    v18_browser = read_object(ROOT_V18_BROWSER_ACCEPTANCE, "root v18 browser acceptance")
    if v18_browser.get("accepted") is not True or v18_browser.get("external_requests") != []:
        raise RuntimeError("root v18 browser acceptance is not an accepted local-only gate")
    v18_build = read_object(V18_BUILD_RECEIPT, "worker v18 build receipt")
    if v18_build.get("export_completed") is not True or v18_build.get("network_requests_by_builder") != 0:
        raise RuntimeError("worker v18 build receipt is not complete and local-only")
    v19_preparation = read_object(V19_PREPARATION_RECEIPT, "v19 input preparation receipt")
    if v19_preparation.get("asset_count") != 10 or v19_preparation.get("asset_bytes") != 33224 or v19_preparation.get("map_sha256") != V19_PRIMARY_MAP_SHA256:
        raise RuntimeError("v19 input preparation receipt does not bind the ten accepted assets")
    preparation = read_object(PREPARATION_RECEIPT, "v21 input preparation receipt")
    if (
        preparation.get("asset_count") != 3
        or preparation.get("asset_bytes") != 18793
        or preparation.get("primary_asset_bytes") != 14148
        or preparation.get("late_asset_bytes") != 4645
        or preparation.get("network_requests") != 0
        or (preparation.get("primary_map") or {}).get("sha256") != V21_PRIMARY_MAP_SHA256
        or (preparation.get("late_map") or {}).get("sha256") != V21_LATE_MAP_SHA256
    ):
        raise RuntimeError("v21 input preparation receipt does not bind the three accepted assets")
    if preparation.get("late_actual_timestamp") != "20080512231210" or preparation.get("late_temporal_class") != "late_2008" or preparation.get("pre_anchor_digest_match_preserved") is not True:
        raise RuntimeError("v21 preparation does not preserve late supplement timing/digest evidence")

    v20_export = read_object(ROOT_V20_EXPORT_ACCEPTANCE, "root v20 export acceptance")
    if v20_export.get("accepted") is not True or v20_export.get("published") is not False:
        raise RuntimeError("root v20 export acceptance is not accepted and unpublished")
    if v20_export.get("checked_declared_files") != 8561 or v20_export.get("actual_files") != 8562:
        raise RuntimeError("root v20 acceptance counts do not match the frozen v20 tree")
    v20_stats = v20_export.get("stats") or {}
    if any(v20_stats.get(name) != value for name, value in {
        "output_files": 8561,
        "source_records": 8357,
        "image_overlay": 103,
        "primary_image_overlay_records": 82,
        "supplement_image_overlay_records": 21,
        "guide_preview_count": 22,
        "guide_preview_gallery_pages": 6,
    }.items()):
        raise RuntimeError("root v20 export stats do not match the frozen v20 tree")
    v20_provenance = read_object(V20_PROVENANCE, "v20 export provenance")
    if (v20_provenance.get("stats") or {}).get("source_records") != 8357:
        raise RuntimeError("frozen v20 provenance source count changed")

    v19_acceptance = read_object(ROOT_V19_ACCEPTANCE, "root v19 export acceptance")
    if v19_acceptance.get("accepted") is not True or v19_acceptance.get("published") is not False:
        raise RuntimeError("root v19 export acceptance is not accepted and unpublished")
    if v19_acceptance.get("checked_declared_files") != 8537 or v19_acceptance.get("actual_files") != 8538:
        raise RuntimeError("root v19 acceptance counts do not match the frozen v19 tree")
    v2 = read_object(ROOT_V2_ACCEPTANCE, "root City v2 code acceptance")
    if v2.get("accepted") is not True or v2.get("network_requests") != 0:
        raise RuntimeError("root City v2 code acceptance is not accepted local-only evidence")
    if v2.get("source_manifest_sha256") != FROZEN_MANIFEST_SHA256 or v2.get("production_code_sha256") != PRODUCTION_SHA256["tools/guide_previews.py"]:
        raise RuntimeError("root City v2 code acceptance does not bind current source/code")
    if v2.get("v2_map_sha256") != V2_GUIDE_MAP_SHA256 or v2.get("v2_groups") != 6 or v2.get("v2_previews") != 22 or v2.get("city_cards") != 3:
        raise RuntimeError("root City v2 map/count gate differs")

    focused = read_object(FOCUSED_RECEIPT, "focused guide test receipt")
    if focused.get("exit_code") != 0 or focused.get("result") != "9 tests OK":
        raise RuntimeError("focused guide tests are not accepted")
    return v17, v2, focused


def output_file_count(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file())


def preflight_loader() -> dict[str, Any]:
    """Run the unchanged exporter loaders against v21 inputs without writing output."""

    sys.path.insert(0, str(ROOT / "tools"))
    
    import guide_previews

    manifest = read_object(SOURCE_MANIFEST, "source15 manifest")
    records = list(manifest.get("files") or [])
    route_records: dict[str, dict[str, Any]] = {}
    route_to_static: dict[str, str] = {}
    relative_paths: set[str] = set()
    for record in records:
        route = export_github_pages.safe_route(str(record.get("route") or ""))
        route_records[route] = record
        relative = export_github_pages.static_rel_for_route(route, record)
        relative_paths.add(relative)
        route_to_static[route] = export_github_pages.static_url(BASE_PATH, relative)
    aliases = manifest.get("route_aliases") or {}
    frozen_routes = set(route_records) | {str(alias) for alias in aliases}
    primary, primary_bytes = export_github_pages.load_image_overlays(
        tuple(PRIMARY_MAPS),
        workspace_root=ROOT,
        anchor_timestamp=str(manifest.get("anchor_timestamp") or ""),
        frozen_routes=frozen_routes,
        frozen_static_paths=set(relative_paths),
    )
    overlay_routes = frozen_routes | {str(item["route"]) for item in primary}
    overlay_static = set(relative_paths) | {str(item["relative"]) for item in primary}
    for item in primary:
        route_to_static[str(item["route"])] = export_github_pages.static_url(BASE_PATH, str(item["relative"]))
    supplement, supplement_bytes = export_github_pages.load_supplement_image_overlays(
        tuple(SUPPLEMENT_MAPS),
        workspace_root=ROOT,
        anchor_timestamp=str(manifest.get("anchor_timestamp") or ""),
        frozen_routes=overlay_routes,
        frozen_static_paths=overlay_static,
        allow_later_image_supplements=True,
    )
    for item in supplement:
        route_to_static[str(item["route"])] = export_github_pages.static_url(BASE_PATH, str(item["relative"]))
    bundle = guide_previews.load_guide_preview_map(
        V2_GUIDE_MAP,
        workspace_root=ROOT,
        source_site=SOURCE_SITE,
        manifest_path=SOURCE_MANIFEST,
        manifest=manifest,
        route_to_static=route_to_static,
    )
    if len(primary) != 84 or len(supplement) != 22:
        raise RuntimeError(f"v21 loader count mismatch: primary={len(primary)}, supplement={len(supplement)}")
    return {
        "primary_overlay_records": len(primary),
        "primary_overlay_bytes": primary_bytes,
        "supplement_overlay_records": len(supplement),
        "supplement_overlay_bytes": supplement_bytes,
        "total_overlay_records": len(primary) + len(supplement),
        "guide_preview_groups": len(bundle.groups),
        "guide_preview_count": bundle.preview_count,
        "network_requests": 0,
    }


def verify_postbuild_v21(result: dict[str, Any]) -> dict[str, Any]:
    """Verify the single v21 export against frozen v20 bytes and three new inputs."""
    if not OUTPUT.is_dir() or OUTPUT.with_name(OUTPUT.name + ".partial").exists():
        raise RuntimeError("v21 output or partial output state is invalid after export")
    provenance_path = OUTPUT / "export-provenance.json"
    provenance = read_object(provenance_path, "v21 export provenance")
    stats = provenance.get("stats") or {}
    if result.get("output_files") != 8564 or stats.get("output_files") != 8564:
        raise RuntimeError(f"v21 declared output count is not 8564: result={result.get('output_files')}, provenance={stats.get('output_files')}")
    actual_files = output_file_count(OUTPUT)
    if actual_files != 8565:
        raise RuntimeError(f"v21 actual file count is not 8565: {actual_files}")
    if provenance.get("source_manifest_sha256") != FROZEN_MANIFEST_SHA256 or stats.get("source_records") != 8357:
        raise RuntimeError("v21 provenance does not bind source15 manifest")
    expected_stats = {
        "image_overlay": 106,
        "image_overlay_records": 106,
        "primary_image_overlay_records": 84,
        "supplement_image_overlay_records": 22,
        "guide_preview_gallery_pages": 6,
        "guide_preview_count": 22,
    }
    for key, expected in expected_stats.items():
        if stats.get(key) != expected:
            raise RuntimeError(f"v21 provenance stat {key} is {stats.get(key)!r}, expected {expected}")
    guide_provenance = provenance.get("guide_previews") or {}
    if guide_provenance.get("schema") != "github-pages-guide-preview-provenance/v2" or guide_provenance.get("source_map_schema") != "wow-recovery.guide-preview-source-map.v2":
        raise RuntimeError("v21 guide preview provenance is not v2")
    if guide_provenance.get("preview_count") != 22 or guide_provenance.get("group_count") != 6:
        raise RuntimeError("v21 guide preview provenance count is wrong")
    if guide_provenance.get("source_map_sha256") != V2_GUIDE_MAP_SHA256:
        raise RuntimeError("v21 guide preview provenance does not bind v2 map")

    old_provenance = read_object(V20_PROVENANCE, "v20 export provenance")
    old_overlays = {
        str(item.get("route")): item
        for item in old_provenance.get("files", [])
        if item.get("role") == "image_overlay"
    }
    overlays = [item for item in provenance.get("files", []) if item.get("role") == "image_overlay"]
    overlay_by_route = {str(item.get("route")): item for item in overlays}
    if len(old_overlays) != 103 or len(overlays) != 106 or not set(old_overlays).issubset(set(overlay_by_route)):
        raise RuntimeError("v21 overlay route set does not retain the frozen v20 103 routes")
    stable_fields = ("derived_sha256", "derived_length", "source_sha256", "source_length", "mime", "temporal_class", "original_url", "route", "output_path", "source_map", "source_map_sha256")
    retained_mismatches: list[str] = []
    for route, old_item in old_overlays.items():
        new_item = overlay_by_route[route]
        for key in stable_fields:
            if key in old_item and new_item.get(key) != old_item.get(key):
                retained_mismatches.append(f"{route}:{key}")
                break
        output_file = OUTPUT / str(new_item.get("output_path") or "")
        if not output_file.is_file() or sha256(output_file) != str(old_item.get("derived_sha256") or ""):
            retained_mismatches.append(f"{route}:bytes")
    if retained_mismatches:
        raise RuntimeError(f"v20 retained overlay metadata/bytes changed: {retained_mismatches[:5]}")

    v20_map = read_object(V20_PRIMARY_MAP, "v20 primary map")
    v21_map = read_object(V21_PRIMARY_MAP, "v21 primary map")
    late_map = read_object(V21_LATE_MAP, "v21 late supplement map")

    def map_route(item: dict[str, Any]) -> str:
        return export_github_pages.mirror.route_path(str(item.get("original") or item.get("logical_url") or ""))

    v20_map_routes = {map_route(item) for item in v20_map.get("items", [])}
    v21_map_routes = {map_route(item) for item in v21_map.get("items", [])}
    expected_new_primary = v21_map_routes - v20_map_routes
    if len(v20_map_routes) != 34 or len(v21_map_routes) != 36 or len(expected_new_primary) != 2:
        raise RuntimeError(f"v21 primary map route delta is not 34->36: old={len(v20_map_routes)}, new={len(v21_map_routes)}, delta={len(expected_new_primary)}")
    late_items = late_map.get("items") or []
    if len(late_items) != 1:
        raise RuntimeError("v21 late map must contain exactly one supplement")
    late_route = map_route(late_items[0])
    actual_new = set(overlay_by_route) - set(old_overlays)
    if actual_new != expected_new_primary | {late_route}:
        raise RuntimeError(f"v21 new overlay routes differ from two primary plus late supplement: expected={sorted(expected_new_primary | {late_route})}, actual={sorted(actual_new)}")

    def check_map_item(route: str, item: dict[str, Any], label: str) -> None:
        output_item = overlay_by_route.get(route)
        if output_item is None:
            raise RuntimeError(f"{label} route missing from provenance: {route}")
        output_file = OUTPUT / str(output_item.get("output_path") or "")
        if not output_file.is_file() or sha256(output_file) != str(item.get("sha256") or ""):
            raise RuntimeError(f"{label} output bytes do not match map: {route}")
        for output_key, map_key in (("derived_sha256", "sha256"), ("derived_length", "length"), ("mime", "mime"), ("cdx_digest", "cdx_digest"), ("actual_capture_timestamp", "actual_timestamp"), ("indexed_capture_timestamp", "indexed_capture_timestamp")):
            if map_key in item and output_item.get(output_key) != item.get(map_key):
                raise RuntimeError(f"{label} provenance mismatch {output_key}: {route}")

    map_items_by_route = {map_route(item): item for item in v21_map.get("items", [])}
    for route in sorted(expected_new_primary):
        check_map_item(route, map_items_by_route[route], "v21 primary")
    late_item = late_items[0]
    check_map_item(late_route, late_item, "v21 late supplement")
    late_output = overlay_by_route[late_route]
    if late_item.get("actual_timestamp") != "20080512231210" or late_item.get("temporal_class") != "late_2008" or late_item.get("pre_anchor_digest_match") is not True or late_output.get("actual_capture_timestamp") != "20080512231210":
        raise RuntimeError("v21 late supplement timing/digest evidence was not retained")

    section_checks: dict[str, dict[str, Any]] = {}
    notice = "These previews survive in the original guide pages. Full-size gallery images are still incomplete."
    guide_doc = json.loads(V2_GUIDE_MAP.read_text(encoding="utf-8"))
    expected_counts = {str(group["group_id"]): len(group["previews"]) for group in guide_doc["groups"]}
    for group_id, (_label, gallery_route, _guide_route) in guide_previews.EXPECTED_GROUPS_V2.items():
        page_path = OUTPUT / export_github_pages.static_rel_for_route(gallery_route, {"kind": "html"})
        page = page_path.read_text(encoding="utf-8")
        section_id = f"offline-preserved-guide-previews-{guide_previews._slug(group_id)}"
        route_markers = page.count("data-guide-preview-route=")
        section_checks[group_id] = {
            "path": rel(page_path),
            "section_id_count": page.count(f'id="{section_id}"'),
            "title_count": page.count("Preserved guide previews"),
            "notice_count": page.count(notice),
            "view_original_guide_count": page.count("View original guide"),
            "route_marker_count": route_markers,
            "expected_cards": expected_counts[group_id],
        }
        for key in ("section_id_count", "title_count", "notice_count", "view_original_guide_count"):
            if section_checks[group_id][key] != 1:
                raise RuntimeError(f"v21 guide preview section count failed: {group_id} {key}")
        if route_markers != expected_counts[group_id]:
            raise RuntimeError(f"v21 guide preview card count failed: {group_id} {route_markers}")

    city_page_path = OUTPUT / export_github_pages.static_rel_for_route("/pvp/worldpvp/cityattacks-gallery.html", {"kind": "html"})
    city_page = city_page_path.read_text(encoding="utf-8")
    if "/pvp/worldpvp/images/city/ss1.jpg" in city_page or "dynamic_full_candidate" in city_page:
        raise RuntimeError("v21 City page contains a dynamic/full alias")
    if "addshots(" not in city_page:
        raise RuntimeError("v21 City page lost its dynamic gallery script")

    old_gallery_equal: dict[str, bool] = {}
    for group_id, (_label, gallery_route, _guide_route) in guide_previews.EXPECTED_GROUPS_V2.items():
        old_path = ROOT / ".scratch/pages-resources-20261016-v20" / export_github_pages.static_rel_for_route(gallery_route, {"kind": "html"})
        new_path = OUTPUT / export_github_pages.static_rel_for_route(gallery_route, {"kind": "html"})
        old_gallery_equal[group_id] = old_path.read_bytes() == new_path.read_bytes()
        if not old_gallery_equal[group_id]:
            raise RuntimeError(f"v21 changed existing v20 gallery output: {group_id}")

    return {
        "declared_output_files": result.get("output_files"),
        "provenance_declared_output_files": stats.get("output_files"),
        "actual_output_files": actual_files,
        "source_records": stats.get("source_records"),
        "overlay_records": len(overlays),
        "primary_overlay_records": expected_stats["primary_image_overlay_records"],
        "supplement_overlay_records": expected_stats["supplement_image_overlay_records"],
        "v20_overlay_routes_retained": len(old_overlays),
        "v20_overlay_metadata_and_bytes_verified": True,
        "v21_new_primary_routes": sorted(expected_new_primary),
        "v21_late_supplement_route": late_route,
        "v21_new_overlay_bytes_verified": True,
        "guide_preview_count": guide_provenance.get("preview_count"),
        "guide_gallery_pages": guide_provenance.get("group_count"),
        "guide_sections": section_checks,
        "city_dynamic_full_alias": False,
        "existing_v20_gallery_bytes_equal": old_gallery_equal,
    }


def verify_postbuild(result: dict[str, Any]) -> dict[str, Any]:
    if not OUTPUT.is_dir() or OUTPUT.with_name(OUTPUT.name + ".partial").exists():
        raise RuntimeError("v21 output or partial output state is invalid after export")
    provenance_path = OUTPUT / "export-provenance.json"
    provenance = read_object(provenance_path, "v21 export provenance")
    stats = provenance.get("stats") or {}
    sys.path.insert(0, str(ROOT / "tools"))
    
    import guide_previews
    if result.get("output_files") != 8561 or stats.get("output_files") != 8561:
        raise RuntimeError(f"v21 declared output count is not 8561: result={result.get('output_files')}, provenance={stats.get('output_files')}")
    actual_files = output_file_count(OUTPUT)
    if actual_files != 8562:
        raise RuntimeError(f"v21 actual file count is not 8562: {actual_files}")
    if provenance.get("source_manifest_sha256") != FROZEN_MANIFEST_SHA256 or stats.get("source_records") != 8357:
        raise RuntimeError("v19 provenance does not bind source15 manifest")
    expected_stats = {
        "image_overlay": 103,
        "image_overlay_records": 103,
        "primary_image_overlay_records": 82,
        "supplement_image_overlay_records": 21,
        "guide_preview_gallery_pages": 6,
        "guide_preview_count": 22,
    }
    for key, expected in expected_stats.items():
        if stats.get(key) != expected:
            raise RuntimeError(f"v21 provenance stat {key} is {stats.get(key)!r}, expected {expected}")
    guide_provenance = provenance.get("guide_previews") or {}
    if guide_provenance.get("schema") != "github-pages-guide-preview-provenance/v2" or guide_provenance.get("source_map_schema") != "wow-recovery.guide-preview-source-map.v2":
        raise RuntimeError("v19 guide preview provenance is not v2")
    if guide_provenance.get("preview_count") != 22 or guide_provenance.get("group_count") != 6:
        raise RuntimeError("v19 guide preview provenance count is wrong")
    if guide_provenance.get("source_map_sha256") != V2_GUIDE_MAP_SHA256:
        raise RuntimeError("v19 guide preview provenance does not bind v2 map")

    old_provenance = read_object(V19_PROVENANCE, "v19 export provenance")
    old_overlays = {
        str(item.get("route")): item
        for item in old_provenance.get("files", [])
        if item.get("role") == "image_overlay"
    }
    overlays = [item for item in provenance.get("files", []) if item.get("role") == "image_overlay"]
    new_overlays = {str(item.get("route")): item for item in overlays}
    if len(old_overlays) != 79 or len(overlays) != 103 or not set(old_overlays).issubset(set(new_overlays)):
        raise RuntimeError("v21 overlay route set does not retain v19's 79 routes plus twenty-four new routes")
    retained_mismatches: list[str] = []
    for route, old_item in old_overlays.items():
        new_item = new_overlays[route]
        output_file = OUTPUT / str(new_item.get("output_path") or "")
        if (
            str(new_item.get("derived_sha256") or "") != str(old_item.get("derived_sha256") or "")
            or not output_file.is_file()
            or sha256(output_file) != str(old_item.get("derived_sha256") or "")
        ):
            retained_mismatches.append(route)
    if retained_mismatches:
        raise RuntimeError(f"v19 retained overlay bytes changed: {retained_mismatches[:5]}")

    v21_map = read_object(V21_PRIMARY_MAP, "v21 primary map")
    map_routes = {
        export_github_pages.mirror.route_path(str(item.get("original") or item.get("logical_url") or ""))
        for item in v21_map.get("items", [])
    }
    expected_new_routes = map_routes - set(old_overlays)
    actual_new_routes = set(new_overlays) - set(old_overlays)
    if len(map_routes) != 34 or len(expected_new_routes) != 24 or actual_new_routes != expected_new_routes:
        raise RuntimeError(
            f"v21 new overlay routes differ from the 34-item derived map: expected={sorted(expected_new_routes)}, actual={sorted(actual_new_routes)}"
        )
    new_overlay_bytes_verified = True
    for route in sorted(expected_new_routes):
        item = new_overlays[route]
        output_file = OUTPUT / str(item.get("output_path") or "")
        if not output_file.is_file() or sha256(output_file) != str(item.get("derived_sha256") or ""):
            new_overlay_bytes_verified = False
            break
    if not new_overlay_bytes_verified:
        raise RuntimeError("v21 new overlay output bytes do not match provenance")

    section_checks: dict[str, dict[str, Any]] = {}
    notice = "These previews survive in the original guide pages. Full-size gallery images are still incomplete."
    expected_counts = {group[0]: len(group[1]) for group in [(g["group_id"], g["previews"]) for g in json.loads(V2_GUIDE_MAP.read_text(encoding="utf-8"))["groups"]]}
    for group_id, (_label, gallery_route, _guide_route) in guide_previews.EXPECTED_GROUPS_V2.items():
        page_path = OUTPUT / export_github_pages.static_rel_for_route(gallery_route, {"kind": "html"})
        page = page_path.read_text(encoding="utf-8")
        section_id = f"offline-preserved-guide-previews-{guide_previews._slug(group_id)}"
        route_markers = page.count('data-guide-preview-route=')
        section_checks[group_id] = {
            "path": rel(page_path),
            "section_id_count": page.count(f'id="{section_id}"'),
            "title_count": page.count("Preserved guide previews"),
            "notice_count": page.count(notice),
            "view_original_guide_count": page.count("View original guide"),
            "route_marker_count": route_markers,
            "expected_cards": expected_counts[group_id],
        }
        for key in ("section_id_count", "title_count", "notice_count", "view_original_guide_count"):
            if section_checks[group_id][key] != 1:
                raise RuntimeError(f"v21 guide preview section count failed: {group_id} {key}")
        if route_markers != expected_counts[group_id]:
            raise RuntimeError(f"v21 guide preview card count failed: {group_id} {route_markers}")

    city_page_path = OUTPUT / export_github_pages.static_rel_for_route("/pvp/worldpvp/cityattacks-gallery.html", {"kind": "html"})
    city_page = city_page_path.read_text(encoding="utf-8")
    if "/pvp/worldpvp/images/city/ss1.jpg" in city_page or "dynamic_full_candidate" in city_page:
        raise RuntimeError("v21 City page contains a dynamic/full alias")
    if "addshots(" not in city_page:
        raise RuntimeError("v21 City page lost its dynamic gallery script")

    old_gallery_equal: dict[str, bool] = {}
    for group_id, (_label, gallery_route, _guide_route) in guide_previews.EXPECTED_GROUPS_V2.items():
        old_path = Path(ROOT / ".scratch/pages-resources-20261016-v19" / export_github_pages.static_rel_for_route(gallery_route, {"kind": "html"}))
        new_path = OUTPUT / export_github_pages.static_rel_for_route(gallery_route, {"kind": "html"})
        old_gallery_equal[group_id] = old_path.read_bytes() == new_path.read_bytes()
        if not old_gallery_equal[group_id]:
            raise RuntimeError(f"v21 changed existing v19 gallery output: {group_id}")

    return {
        "declared_output_files": result.get("output_files"),
        "provenance_declared_output_files": stats.get("output_files"),
        "actual_output_files": actual_files,
        "source_records": stats.get("source_records"),
        "overlay_records": len(overlays),
        "primary_overlay_records": expected_stats["primary_image_overlay_records"],
        "supplement_overlay_records": expected_stats["supplement_image_overlay_records"],
        "v19_overlay_routes_retained": len(old_overlays),
        "v19_overlay_bytes_verified": True,
        "v21_new_overlay_routes": sorted(expected_new_routes),
        "v21_new_overlay_bytes_verified": new_overlay_bytes_verified,
        "guide_preview_count": guide_provenance.get("preview_count"),
        "guide_gallery_pages": guide_provenance.get("group_count"),
        "guide_sections": section_checks,
        "city_dynamic_full_alias": False,
        "existing_v18_gallery_bytes_equal": old_gallery_equal,
    }


def write_receipt(payload: dict[str, Any]) -> None:
    RECEIPT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    command = '"C:\\Users\\17630\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe" -X utf8 research/continuous-recovery-20261016/integration/v21-build/build_pages_v21.py'
    started = now()
    export_started = False
    result: dict[str, Any] | None = None
    preflight: dict[str, Any] | None = None
    locks_before: dict[str, str] | None = None
    free_before: int | None = None
    try:
        if RECEIPT.exists():
            raise RuntimeError(f"refusing to overwrite existing worker receipt: {RECEIPT}")
        validate_gates()
        locks_before = locked_input_hashes()
        if not SOURCE_SITE.is_dir() or not SOURCE_MANIFEST.is_file():
            raise RuntimeError("source15 source/site is missing")
        if OUTPUT.exists() or OUTPUT.with_name(OUTPUT.name + ".partial").exists():
            raise RuntimeError("refusing to overwrite existing v21 output or partial")
        free_before = shutil.disk_usage(OUTPUT.parent).free
        if free_before < MIN_FREE_BYTES:
            raise RuntimeError(f"disk free below floor before export: {free_before} < {MIN_FREE_BYTES}")

        sys.path.insert(0, str(ROOT / "tools"))
        preflight = preflight_loader()
        export_started = True
        result = export_github_pages.export_pages(
            source_site=SOURCE_SITE,
            manifest_path=SOURCE_MANIFEST,
            output=OUTPUT,
            base_path=BASE_PATH,
            workspace_root=ROOT,
            max_bytes=None,
            min_free_bytes=MIN_FREE_BYTES,
            image_source_maps=PRIMARY_MAPS,
            supplement_image_source_maps=SUPPLEMENT_MAPS,
            allow_later_image_supplements=True,
            guide_preview_map=V2_GUIDE_MAP,
        )
        postbuild = verify_postbuild_v21(result)
        locks_after = locked_input_hashes()
        if locks_before != locks_after:
            raise RuntimeError("a locked source/map/production input changed during export")
        free_after = shutil.disk_usage(OUTPUT.parent).free
        if free_after < MIN_FREE_BYTES:
            raise RuntimeError(f"disk free below floor after export: {free_after} < {MIN_FREE_BYTES}")
        receipt = {
            "schema": "wow-recovery.integration.v21.build-receipt.v1",
            "executed_by": "/root/local_recovery_20261016",
            "command": command,
            "checked_utc_start": started,
            "checked_utc_end": now(),
            "export_started": True,
            "export_completed": True,
            "network_requests_by_builder": 0,
            "published": False,
            "source_stage": rel(SOURCE_STAGE),
            "source_stage_reused": True,
            "source_site": rel(SOURCE_SITE),
            "source_manifest": rel(SOURCE_MANIFEST),
            "source_manifest_sha256": locks_after[rel(SOURCE_MANIFEST)],
            "original_offline_manifest": rel(ORIGINAL_OFFLINE_MANIFEST),
            "original_offline_manifest_sha256": locks_after[rel(ORIGINAL_OFFLINE_MANIFEST)],
            "v18_provenance": rel(V18_PROVENANCE),
            "v18_provenance_sha256": locks_after[rel(V18_PROVENANCE)],
            "v20_provenance": rel(V20_PROVENANCE),
            "v20_provenance_sha256": locks_after[rel(V20_PROVENANCE)],
            "root_v20_export_acceptance": rel(ROOT_V20_EXPORT_ACCEPTANCE),
            "root_v20_export_acceptance_sha256": locks_after[rel(ROOT_V20_EXPORT_ACCEPTANCE)],
            "root_v17_input_acceptance": rel(ROOT_V17_ACCEPTANCE),
            "root_v17_input_acceptance_sha256": locks_after[rel(ROOT_V17_ACCEPTANCE)],
            "root_v18_export_acceptance": rel(ROOT_V18_EXPORT_ACCEPTANCE),
            "root_v18_export_acceptance_sha256": locks_after[rel(ROOT_V18_EXPORT_ACCEPTANCE)],
            "root_v18_local_acceptance": rel(ROOT_V18_LOCAL_ACCEPTANCE),
            "root_v18_local_acceptance_sha256": locks_after[rel(ROOT_V18_LOCAL_ACCEPTANCE)],
            "root_v18_browser_acceptance": rel(ROOT_V18_BROWSER_ACCEPTANCE),
            "root_v18_browser_acceptance_sha256": locks_after[rel(ROOT_V18_BROWSER_ACCEPTANCE)],
            "v18_build_receipt": rel(V18_BUILD_RECEIPT),
            "v18_build_receipt_sha256": locks_after[rel(V18_BUILD_RECEIPT)],
            "root_v2_code_acceptance": rel(ROOT_V2_ACCEPTANCE),
            "root_v2_code_acceptance_sha256": locks_after[rel(ROOT_V2_ACCEPTANCE)],
            "focused_test_receipt": rel(FOCUSED_RECEIPT),
            "focused_test_receipt_sha256": locks_after[rel(FOCUSED_RECEIPT)],
            "v21_input_preparation": rel(PREPARATION_RECEIPT),
            "v21_input_preparation_sha256": locks_after[rel(PREPARATION_RECEIPT)],
            "primary_source_maps": [rel(path) for path in PRIMARY_MAPS],
            "supplement_source_maps": [rel(path) for path in SUPPLEMENT_MAPS],
            "guide_preview_map": rel(V2_GUIDE_MAP),
            "map_sha256_before": {rel(path): locks_before[rel(path)] for path in [*PRIMARY_MAPS, *SUPPLEMENT_MAPS, V1_GUIDE_MAP, V2_GUIDE_MAP]},
            "map_sha256_after": {rel(path): locks_after[rel(path)] for path in [*PRIMARY_MAPS, *SUPPLEMENT_MAPS, V1_GUIDE_MAP, V2_GUIDE_MAP]},
            "maps_unchanged_during_export": True,
            "production_sha256_before": {key: locks_before[key] for key in PRODUCTION_SHA256},
            "production_sha256_after": {key: locks_after[key] for key in PRODUCTION_SHA256},
            "production_unchanged_during_export": True,
            "test_sha256_before": {key: locks_before[key] for key in TEST_SHA256},
            "test_sha256_after": {key: locks_after[key] for key in TEST_SHA256},
            "v19_primary_source_map": rel(V19_PRIMARY_MAP),
            "v19_primary_source_map_sha256": locks_after[rel(V19_PRIMARY_MAP)],
            "v20_primary_source_map": rel(V20_PRIMARY_MAP),
            "v20_primary_source_map_sha256": locks_after[rel(V20_PRIMARY_MAP)],
            "v21_primary_source_map": rel(V21_PRIMARY_MAP),
            "v21_primary_source_map_sha256": locks_after[rel(V21_PRIMARY_MAP)],
            "v21_late_supplement_source_map": rel(V21_LATE_MAP),
            "v21_late_supplement_source_map_sha256": locks_after[rel(V21_LATE_MAP)],
            "v19_provenance": rel(V19_PROVENANCE),
            "v19_provenance_sha256": locks_after[rel(V19_PROVENANCE)],
            "root_v19_export_acceptance": rel(ROOT_V19_ACCEPTANCE),
            "root_v19_export_acceptance_sha256": locks_after[rel(ROOT_V19_ACCEPTANCE)],
            "v19_reconciliation": rel(V19_RECONCILIATION),
            "v19_reconciliation_sha256": locks_after[rel(V19_RECONCILIATION)],
            "root_aug20_acceptance": rel(ROOT_AUG20_ACCEPTANCE),
            "root_aug20_acceptance_sha256": locks_after[rel(ROOT_AUG20_ACCEPTANCE)],
            "root_aug_remaining15_acceptance": rel(ROOT_AUG_REMAINING15_ACCEPTANCE),
            "root_aug_remaining15_acceptance_sha256": locks_after[rel(ROOT_AUG_REMAINING15_ACCEPTANCE)],
            "aug20_source_map": rel(AUG20_SOURCE_MAP),
            "aug20_source_map_sha256": locks_after[rel(AUG20_SOURCE_MAP)],
            "aug_remaining15_source_map": rel(AUG_REMAINING15_SOURCE_MAP),
            "aug_remaining15_source_map_sha256": locks_after[rel(AUG_REMAINING15_SOURCE_MAP)],
            "root_aug_final3_acceptance": rel(ROOT_AUG_FINAL3_ACCEPTANCE),
            "root_aug_final3_acceptance_sha256": locks_after[rel(ROOT_AUG_FINAL3_ACCEPTANCE)],
            "root_aug_cached19_acceptance": rel(ROOT_AUG_CACHED19_ACCEPTANCE),
            "root_aug_cached19_acceptance_sha256": locks_after[rel(ROOT_AUG_CACHED19_ACCEPTANCE)],
            "root_aug_late11_acceptance": rel(ROOT_AUG_LATE11_ACCEPTANCE),
            "root_aug_late11_acceptance_sha256": locks_after[rel(ROOT_AUG_LATE11_ACCEPTANCE)],
            "aug_final3_source_map": rel(AUG_FINAL3_SOURCE_MAP),
            "aug_final3_source_map_sha256": locks_after[rel(AUG_FINAL3_SOURCE_MAP)],
            "aug_cached19_source_map": rel(AUG_CACHED19_SOURCE_MAP),
            "aug_cached19_source_map_sha256": locks_after[rel(AUG_CACHED19_SOURCE_MAP)],
            "aug_late11_source_map": rel(AUG_LATE11_SOURCE_MAP),
            "aug_late11_source_map_sha256": locks_after[rel(AUG_LATE11_SOURCE_MAP)],
            "news_shared10_acceptance": rel(NEWS_SHARED10_ACCEPTANCE),
            "news_shared13_acceptance": rel(NEWS_SHARED13_ACCEPTANCE),
            "news_shared10_source_map": rel(NEWS_SHARED10_SOURCE_MAP),
            "news_shared13_source_map": rel(NEWS_SHARED13_SOURCE_MAP),
            "preflight_loader": preflight,
            "root_expected_primary_overlay_count": 84,
            "root_expected_supplement_overlay_count": 22,
            "root_expected_total_overlay_count": 106,
            "root_expected_guide_preview_count": 22,
            "root_expected_guide_gallery_pages": 6,
            "root_expected_city_cards": 3,
            "build": result,
            "postbuild_checks": postbuild,
            "output": rel(OUTPUT),
            "output_refused_if_existing_or_partial": True,
            "disk_free_before_bytes": free_before,
            "disk_free_after_bytes": free_after,
            "disk_free_floor_bytes": MIN_FREE_BYTES,
            "input_hashes_before": locks_before,
            "input_hashes_after": locks_after,
        }
        write_receipt(receipt)
        print(json.dumps(receipt, ensure_ascii=False))
        return 0
    except Exception as exc:
        free_after = shutil.disk_usage(OUTPUT.parent).free
        failure = {
            "schema": "wow-recovery.integration.v21.build-receipt.v1",
            "executed_by": "/root/local_recovery_20261016",
            "command": command,
            "checked_utc_start": started,
            "checked_utc_end": now(),
            "export_started": export_started,
            "export_completed": False,
            "network_requests_by_builder": 0,
            "published": False,
            "error": f"{type(exc).__name__}: {exc}",
            "output": rel(OUTPUT) if OUTPUT.exists() else None,
            "partial_exists": OUTPUT.with_name(OUTPUT.name + ".partial").exists(),
            "disk_free_before_bytes": free_before,
            "disk_free_after_bytes": free_after,
            "disk_free_floor_bytes": MIN_FREE_BYTES,
        }
        if locks_before is not None:
            failure["input_hashes_before"] = locks_before
        try:
            write_receipt(failure)
        except Exception as receipt_exc:
            failure["receipt_write_error"] = f"{type(receipt_exc).__name__}: {receipt_exc}"
        print(json.dumps(failure, ensure_ascii=False), file=sys.stderr)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
