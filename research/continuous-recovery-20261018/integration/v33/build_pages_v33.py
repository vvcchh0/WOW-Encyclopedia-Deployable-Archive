#!/usr/bin/env python3
"""Prepare the v33 image closure after an explicit root source manifest.

This module is deliberately preparation-only.  It does not inspect pending
network folders and it has no exporter call.  Root must provide a frozen
``root-v33-source-receipts-manifest.json`` that names every accepted public
copy, its source/public receipts, role, and aggregate counts.  Once that
manifest is accepted, this script can produce the two v33 delta maps, a
source-byte audit, the manifest-only impact estimate, and preflight evidence.

The v32 closure is passed to the future exporter as its original map list;
the v33 maps contain only the explicitly accepted delta.  The impact estimate
uses every old v32 overlay origin together with the new rows when separating
navigation ``missing.html`` recoveries from ``missing-image.svg`` markers.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit


ROOT = Path(__file__).resolve().parents[4]
INTEGRATION = Path(__file__).resolve().parent
SOURCE_SITE = ROOT / ".scratch/offline-navigation-20261015-v15/site"
SOURCE_MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
ORIGINAL_MANIFEST = ROOT / "offline/build-manifest.json"
GUIDE_PREVIEW_MAP = ROOT / "research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json"
GUIDE_COLLECTION_MAP = ROOT / "research/continuous-recovery-20261018/integration/v26-guide-image-collection-map.json"

V28_BUILDER = ROOT / "research/continuous-recovery-20261018/integration/v28/build_pages_v28.py"
V29_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v29/v29-primary-source-map.json"
V30_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v30/v30-primary-source-map.json"
V30_SUPPLEMENT_MAP = ROOT / "research/continuous-recovery-20261018/integration/v30/v30-supplement-source-map.json"
V30_PROVENANCE = ROOT / ".scratch/pages-resources-20261018-v30/export-provenance.json"
V30_BUILD_RECEIPT = ROOT / "research/continuous-recovery-20261018/integration/v30/v30-build-receipt.json"
V32_PRIMARY_MAP = ROOT / "research/continuous-recovery-20261018/integration/v32/v32-primary-source-map.json"
V32_SUPPLEMENT_MAP = ROOT / "research/continuous-recovery-20261018/integration/v32/v32-supplement-source-map.json"
V32_PROVENANCE = ROOT / ".scratch/pages-resources-20261018-v32/export-provenance.json"
V32_BUILD_RECEIPT = ROOT / "research/continuous-recovery-20261018/integration/v32/v32-build-receipt.json"
V32_INPUT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-v32-input-acceptance.json"
V32_EXPORT_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-v32-export-acceptance.json"

EXPORTER = ROOT / "tools/export_github_pages.py"
HISTORICAL_EXHIBITS = ROOT / "tools/historical_exhibits.py"
ROOT_POPUP_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-popup-tool-acceptance.json"
ROOT_NAVIGATION_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-navigation-image-tool-acceptance.json"
ROOT_RETIRED_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-retired-armory-tool-acceptance.json"
ROOT_MASK_ACCEPTANCE = ROOT / "research/continuous-recovery-20261018/publication/root-attunement-mask-tool-acceptance.json"

ROOT_SOURCE_INPUT_MANIFEST = ROOT / "research/continuous-recovery-20261018/publication/root-v33-source-receipts-manifest-r2.json"
V33_PRIMARY_MAP = INTEGRATION / "v33-primary-source-map.json"
V33_SUPPLEMENT_MAP = INTEGRATION / "v33-supplement-source-map.json"
V33_IMPACT = INTEGRATION / "v33-impact-estimate.json"
V33_SOURCE_AUDIT = INTEGRATION / "v33-source-byte-audit.json"
V33_PREPARATION = INTEGRATION / "v33-input-preparation.json"
V33_PREFLIGHT = INTEGRATION / "v33-preflight.json"
V33_PROPOSAL = INTEGRATION / "v33-input-proposal.md"
V33_RUNNER_NOTE = INTEGRATION / "v33-runner-preparation.md"
V33_OUTPUT = ROOT / ".scratch/pages-resources-20261018-v33"
V33_BUILD_RECEIPT = INTEGRATION / "v33-build-receipt.json"

ANCHOR = "20080512210044"
MIN_FREE_BYTES = 11_005_853_696
PRIMARY_HOSTS = frozenset({"www.worldofwarcraft.com", "worldofwarcraft.com"})
SUPPLEMENT_HOSTS = frozenset({"www.wowarmory.com", "armory.wow-europe.com", "www.blizzard.com"})
EXPECTED_SOURCE_MANIFEST_SHA256 = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
EXPECTED_ROOT_SOURCE_INPUT_MANIFEST_SHA256 = "d167a3a6fb79cea2a2b6226238f6b42de3cf80fbd873ce1f32ecd1fe240f2e7d"
EXPECTED_ORIGINAL_MANIFEST_SHA256 = "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"
EXPECTED_V28_BUILDER_SHA256 = "e9ba376dec05ac5443a3f2264a5c6b9321780d9921dc0a72f3fac83343d9f7e4"
EXPECTED_V29_PRIMARY_MAP_SHA256 = "fc1e9f4e5da090fd22c6f8eea6d333f6899b01dedfc2dec2b106be98411d58ed"
EXPECTED_V30_PRIMARY_MAP_SHA256 = "8f204f7ec9e07afa27f66a45ee5a0536f187aad141eac633e3a78d9b42a1274e"
EXPECTED_V30_SUPPLEMENT_MAP_SHA256 = "53f84e21888dbc1ede9320ec9a177fde4bc73d993848f8a26d48da0531f02ce0"
EXPECTED_V30_PROVENANCE_SHA256 = "b04eb866bd7d21aa23ce8ad064eeb55b8b263e84147bb3755f4af7df84825d85"
EXPECTED_V30_BUILD_RECEIPT_SHA256 = "87a5edd7075a339d15da1532ebc630f36e31fae48db1bbafcaa5b15982d9623c"
EXPECTED_V32_PRIMARY_MAP_SHA256 = "939af6242b1e8cc9e62e09decd055b104cad7db4dcf17f42b9d002a4ed059318"
EXPECTED_V32_SUPPLEMENT_MAP_SHA256 = "aeb391ba14f7debfbaf0a557a69bac693120ce2471da2d7162f5260602da6966"
EXPECTED_V32_PROVENANCE_SHA256 = "a071d47b65232f723c2e74112adab521eb124d22b57aa430437646f06f50d356"
EXPECTED_V32_BUILD_RECEIPT_SHA256 = "21aeaefe6b46f7115ff246378e9fd798981ed1088d05f85e91372523f4854105"
EXPECTED_V32_INPUT_ACCEPTANCE_SHA256 = "ba49a361f853d8e3a60b2ade818898895908cdce268437d08752313a38434c1c"
EXPECTED_V32_EXPORT_ACCEPTANCE_SHA256 = "980b92c508b2b6bea8972682bac6aaaba080e27f0b8a61d1e823dff13c516c46"
EXPECTED_EXPORTER_SHA256 = "2a6fa4256ad0853797ae10748ef7842896614d419bdb7ad208d9b258dc8e6488"
EXPECTED_HISTORICAL_EXHIBITS_SHA256 = "35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011"
EXPECTED_NAVIGATION_TOOL_RECEIPT_SHA256 = "f2fbe11eeb71367f2f74fae8b321d31a33aa29fd98b0a3376b77489906f7e3d0"
EXPECTED_POPUP_TOOL_RECEIPT_SHA256 = "6e7d0afd979161fd98b996e6256d4ce39359017c5a1428b5e0d7589fe596f8bf"
EXPECTED_RETIRED_TOOL_RECEIPT_SHA256 = "46058b7e23cfa317949f42945196b40be77a6e6485834147e8e32a62c6643e6b"
EXPECTED_MASK_TOOL_RECEIPT_SHA256 = "8c295a243993353de30ea8173ef5e8530656c65acdbbf0785855eadb14eefa24"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cdx_digest(data: bytes) -> str:
    return base64.b32encode(hashlib.sha1(data).digest()).decode("ascii").rstrip("=")


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def inside(path: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"{label} escapes workspace: {path}") from exc
    return resolved


def read_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"invalid JSON for {label}: {path}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} is not an object: {path}")
    return value


def host(url: str) -> str:
    try:
        return (urlsplit(url).hostname or "").casefold().rstrip(".")
    except ValueError:
        return ""


def canonical_url(url: str) -> str:
    parsed = urlsplit(str(url))
    h = (parsed.hostname or "").casefold().rstrip(".")
    return f"{parsed.scheme.casefold()}://{h}{parsed.path}"


def origin_key(url: str) -> str:
    """Match the accepted exporter key: normalized host plus route path."""

    parsed = urlsplit(str(url))
    h = (parsed.hostname or "").casefold().rstrip(".")
    if h in PRIMARY_HOSTS:
        h = "www.worldofwarcraft.com"
    return f"{h}{parsed.path or '/'}"


def role_for_url(url: str) -> str:
    h = host(url)
    if h in PRIMARY_HOSTS:
        return "primary"
    if h in SUPPLEMENT_HOSTS:
        return "supplement"
    raise RuntimeError(f"new v33 image has an unapproved host: {url!r}")


def role_for_capture(url: str, actual_capture_timestamp: str) -> str:
    """Derive primary/supplement from the approved host and capture date.

    Canonical Blizzard-host images are primary only in the baseline 2008
    capture bucket.  The same approved host before 2008 (or after the anchor)
    is retained as a dated supplement, while Armory/Blizzard-origin hosts are
    always supplements.  Keeping ``role_for_url`` host-only preserves its
    public allowlist contract for callers that lack capture metadata.
    """
    host_role = role_for_url(url)
    if host_role == "supplement":
        return "supplement"
    return "primary" if temporal_class(actual_capture_timestamp) == "baseline_2008" else "supplement"


def temporal_class(actual: str) -> str:
    if not re.fullmatch(r"\d{14}", actual):
        raise RuntimeError(f"invalid image timestamp: {actual!r}")
    try:
        moment = datetime.strptime(actual, "%Y%m%d%H%M%S")
    except ValueError as exc:
        raise RuntimeError(f"image timestamp is not a real date: {actual!r}") from exc
    anchor = datetime.strptime(ANCHOR, "%Y%m%d%H%M%S")
    if moment < datetime(2008, 1, 1):
        return "pre_2008"
    if moment <= anchor:
        return "baseline_2008"
    if moment <= datetime(2008, 12, 31, 23, 59, 59):
        return "late_2008"
    return "post_2008"


def import_exporter():
    actual = sha256_file(EXPORTER)
    if actual != EXPECTED_EXPORTER_SHA256:
        raise RuntimeError(f"current exporter SHA changed: {actual} != {EXPECTED_EXPORTER_SHA256}")
    if str(ROOT / "tools") not in sys.path:
        sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location("wow_recovery_v33_exporter", EXPORTER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load accepted exporter")
    module = importlib.util.module_from_spec(spec)
    # Dataclasses and related decorators resolve ``cls.__module__`` through
    # sys.modules while the dynamically loaded exporter is being executed.
    # Register the module first so a clean-process import follows normal
    # importlib semantics.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_v28_builder():
    actual = sha256_file(V28_BUILDER)
    if actual != EXPECTED_V28_BUILDER_SHA256:
        raise RuntimeError(f"frozen v28 builder SHA changed: {actual} != {EXPECTED_V28_BUILDER_SHA256}")
    spec = importlib.util.spec_from_file_location("wow_recovery_v28_for_v33", V28_BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load frozen v28 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def binding(path: Path, expected: str | None = None) -> dict:
    path = inside(path, "binding")
    actual = sha256_file(path)
    if expected is not None and actual.casefold() != expected.casefold():
        raise RuntimeError(f"frozen binding SHA mismatch for {rel(path)}: {actual} != {expected}")
    return {"path": rel(path), "sha256": actual}


def verify_declared_binding(raw: object, label: str) -> Path:
    if not isinstance(raw, dict) or not raw.get("path") or not raw.get("sha256"):
        raise RuntimeError(f"{label} must contain path and sha256")
    path = inside(ROOT / str(raw["path"]), label)
    actual = sha256_file(path)
    if actual.casefold() != str(raw["sha256"]).casefold():
        raise RuntimeError(f"{label} SHA mismatch: {actual} != {raw['sha256']}")
    return path


def verify_payload(data: bytes, mime: str, label: str) -> None:
    normalized = mime.split(";", 1)[0].strip().casefold()
    if normalized == "image/jpeg":
        valid = data.startswith(b"\xff\xd8\xff")
    elif normalized == "image/png":
        valid = data.startswith(b"\x89PNG\r\n\x1a\n")
    elif normalized == "image/gif":
        valid = data[:6] in {b"GIF87a", b"GIF89a"}
    else:
        raise RuntimeError(f"{label} has unsupported image MIME {mime!r}")
    if not valid:
        raise RuntimeError(f"{label} has image magic inconsistent with {mime!r}")
    try:
        from PIL import Image
        import io

        with Image.open(io.BytesIO(data)) as image:
            image.verify()
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError(f"{label} failed image verification") from exc


def _receipt_path(raw: dict, *names: str) -> dict:
    for name in names:
        value = raw.get(name)
        if isinstance(value, dict):
            return value
    raise RuntimeError(f"batch is missing {' or '.join(names)} binding")


def _same_metadata(source: dict, public: dict, original: str, label: str) -> None:
    for key in ("actual_capture_timestamp", "mime", "dimensions", "decoded_frames", "length", "sha256", "cdx_digest"):
        if source.get(key) != public.get(key):
            raise RuntimeError(f"{label} metadata differs for {original}: {key}")


def validate_batch(batch: dict, batch_index: int) -> tuple[list[dict], dict, dict]:
    label = str(batch.get("id") or batch.get("label") or f"batch-{batch_index:02d}")
    role = str(batch.get("role") or "")
    if role not in {"primary", "supplement", "mixed"}:
        raise RuntimeError(f"{label} must declare role primary, supplement, or mixed")
    source_binding = _receipt_path(batch, "source_acceptance", "source_receipt")
    public_binding = _receipt_path(batch, "public_copy_acceptance", "public_copy_receipt")
    source_path = verify_declared_binding(source_binding, f"{label} source receipt")
    public_path = verify_declared_binding(public_binding, f"{label} public-copy receipt")
    source_receipt = read_json(source_path, f"{label} source receipt")
    public_receipt = read_json(public_path, f"{label} public-copy receipt")
    if source_receipt.get("accepted") is not True:
        raise RuntimeError(f"{label} source receipt is not accepted")
    if public_receipt.get("accepted") is not True or public_receipt.get("copy_mode") != "original_bytes":
        raise RuntimeError(f"{label} public-copy receipt is not an accepted original-byte copy")
    public_source = public_receipt.get("source_acceptance") or public_receipt.get("source_receipt")
    if not isinstance(public_source, dict) or str(public_source.get("path")) != rel(source_path) or str(public_source.get("sha256")).casefold() != sha256_file(source_path):
        raise RuntimeError(f"{label} public-copy receipt source binding differs")
    source_rows = {str(row.get("original")): row for row in source_receipt.get("accepted_images", []) if isinstance(row, dict)}
    public_rows = public_receipt.get("accepted_images")
    if not isinstance(public_rows, list) or not public_rows:
        raise RuntimeError(f"{label} public-copy receipt has no accepted_images")
    expected_count = batch.get("expected_count")
    expected_bytes = batch.get("expected_bytes")
    if not isinstance(expected_count, int) or not isinstance(expected_bytes, int):
        raise RuntimeError(f"{label} must explicitly declare expected_count and expected_bytes")
    if len(public_rows) != expected_count:
        raise RuntimeError(f"{label} count differs: {len(public_rows)} != {expected_count}")
    if role == "mixed":
        expected_primary_count = batch.get("expected_primary_count")
        expected_supplement_count = batch.get("expected_supplement_count")
        if not isinstance(expected_primary_count, int) or not isinstance(expected_supplement_count, int):
            raise RuntimeError(f"{label} mixed batch must declare expected_primary_count and expected_supplement_count")
        if expected_primary_count + expected_supplement_count != expected_count:
            raise RuntimeError(f"{label} mixed role counts do not sum to expected_count")
    else:
        expected_primary_count = expected_count if role == "primary" else 0
        expected_supplement_count = expected_count if role == "supplement" else 0
    rows: list[dict] = []
    seen: set[str] = set()
    for index, public in enumerate(public_rows):
        if not isinstance(public, dict) or public.get("accepted") is not True or public.get("deployed") not in {False, None}:
            raise RuntimeError(f"{label}[{index}] is not accepted and undeployed")
        original = str(public.get("original") or "")
        if not original or original in seen:
            raise RuntimeError(f"{label} duplicate or missing original: {original!r}")
        seen.add(original)
        source = source_rows.get(original)
        if source is None or source.get("accepted") is not True:
            raise RuntimeError(f"{label} source row missing or unaccepted: {original}")
        _same_metadata(source, public, original, label)
        derived_role = role_for_capture(original, str(public.get("actual_capture_timestamp") or ""))
        if role != "mixed" and derived_role != role:
            raise RuntimeError(f"{label} role {role!r} disagrees with host role {derived_role!r}: {original}")
        local_path = str(public.get("local_path") or "")
        if not local_path.startswith("research/continuous-recovery-20261018/publication/accepted-images/") or "private-payloads" in local_path:
            raise RuntimeError(f"{label} does not use a public accepted-image path: {local_path}")
        source_path_local = inside(ROOT / local_path, f"{label} public image")
        if not source_path_local.is_file():
            raise RuntimeError(f"{label} public image is missing: {source_path_local}")
        data = source_path_local.read_bytes()
        if len(data) != int(public.get("length", -1)) or sha256_bytes(data) != str(public.get("sha256") or "").casefold():
            raise RuntimeError(f"{label} public image bytes differ: {original}")
        if cdx_digest(data) != str(public.get("cdx_digest") or "").upper():
            raise RuntimeError(f"{label} public image CDX differs: {original}")
        verify_payload(data, str(public.get("mime") or ""), f"{label}[{index}]")
        actual = str(public.get("actual_capture_timestamp") or "")
        temporal = temporal_class(actual)
        rows.append({
            **public,
            "_batch_label": label,
            "_role": derived_role,
            "_destination": source_path_local,
            "_source_path": source_path,
            "_public_receipt_path": public_path,
            "_source_receipt_binding": binding(source_path),
            "_public_receipt_binding": binding(public_path),
            "_temporal_class": temporal,
        })
    actual_primary_count = sum(row["_role"] == "primary" for row in rows)
    actual_supplement_count = sum(row["_role"] == "supplement" for row in rows)
    if actual_primary_count != expected_primary_count or actual_supplement_count != expected_supplement_count:
        raise RuntimeError(f"{label} host-role counts differ: {actual_primary_count}/{actual_supplement_count}")
    total = sum(int(row["length"]) for row in rows)
    if total != expected_bytes or int(public_receipt.get("image_bytes", -1)) != total:
        raise RuntimeError(f"{label} byte total differs: {total} != {expected_bytes}")
    return rows, binding(source_path), binding(public_path)


def load_source_input_manifest(path: Path) -> tuple[dict, list[dict], list[dict]]:
    manifest = read_json(path, "root v33 source-receipts manifest")
    if manifest.get("accepted") is not True:
        raise RuntimeError("root v33 source-receipts manifest is not accepted")
    if manifest.get("network_requests") not in {0, None} or manifest.get("export_executed") not in {False, None}:
        raise RuntimeError("v33 source manifest records network or export activity")
    if str(manifest.get("schema") or manifest.get("schema_version") or "") != "wow-recovery.integration.v33-source-receipts-manifest.v1":
        raise RuntimeError("v33 source manifest schema is not v1")
    source15 = manifest.get("source15_manifest") or manifest.get("source_manifest")
    original = manifest.get("original_manifest") or manifest.get("frozen_original_manifest")
    if not isinstance(source15, dict) or str(source15.get("path")) != rel(SOURCE_MANIFEST) or str(source15.get("sha256")).casefold() != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise RuntimeError("v33 source manifest does not bind source15 manifest")
    if not isinstance(original, dict) or str(original.get("path")) != rel(ORIGINAL_MANIFEST) or str(original.get("sha256")).casefold() != EXPECTED_ORIGINAL_MANIFEST_SHA256:
        raise RuntimeError("v33 source manifest does not bind original offline manifest")
    verify_declared_binding(source15, "source15 manifest")
    verify_declared_binding(original, "original offline manifest")
    batches = manifest.get("batches")
    if not isinstance(batches, list) or not batches:
        raise RuntimeError("v33 source manifest must explicitly list batches")
    rows: list[dict] = []
    batch_bindings: list[dict] = []
    seen_batches: set[str] = set()
    for index, raw_batch in enumerate(batches, 1):
        if not isinstance(raw_batch, dict):
            raise RuntimeError(f"v33 source manifest batch {index} is not an object")
        label = str(raw_batch.get("id") or raw_batch.get("label") or f"batch-{index:02d}")
        if label in seen_batches:
            raise RuntimeError(f"duplicate v33 batch id: {label}")
        seen_batches.add(label)
        batch_rows, source_binding, public_binding = validate_batch(raw_batch, index)
        rows.extend(batch_rows)
        batch_bindings.append({"id": label, "role": raw_batch.get("role"), "source_acceptance": source_binding, "public_copy_acceptance": public_binding, "count": len(batch_rows), "bytes": sum(int(row["length"]) for row in batch_rows), "primary_count": sum(row["_role"] == "primary" for row in batch_rows), "supplement_count": sum(row["_role"] == "supplement" for row in batch_rows)})
    if len({str(row["original"]) for row in rows}) != len(rows):
        raise RuntimeError("v33 source manifest contains duplicate original URLs")
    expected = {
        "new_images": len(rows),
        "image_bytes": sum(int(row["length"]) for row in rows),
        "new_primary_images": sum(row["_role"] == "primary" for row in rows),
        "new_supplement_images": sum(row["_role"] == "supplement" for row in rows),
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise RuntimeError(f"v33 source manifest {key} differs: {manifest.get(key)!r} != {value}")
    return manifest, rows, batch_bindings


def frozen_maps() -> tuple[object, tuple[Path, ...], tuple[Path, ...], dict]:
    frozen = load_v28_builder()
    primary = tuple(frozen.PRIMARY_MAPS) + (V29_PRIMARY_MAP, V30_PRIMARY_MAP, V32_PRIMARY_MAP)
    supplement = tuple(frozen.SUPPLEMENT_MAPS) + (V30_SUPPLEMENT_MAP, V32_SUPPLEMENT_MAP)
    pinned = {
        "v28_builder": binding(V28_BUILDER, EXPECTED_V28_BUILDER_SHA256),
        "v29_primary_map": binding(V29_PRIMARY_MAP, EXPECTED_V29_PRIMARY_MAP_SHA256),
        "v30_primary_map": binding(V30_PRIMARY_MAP, EXPECTED_V30_PRIMARY_MAP_SHA256),
        "v30_supplement_map": binding(V30_SUPPLEMENT_MAP, EXPECTED_V30_SUPPLEMENT_MAP_SHA256),
        "v30_provenance": binding(V30_PROVENANCE, EXPECTED_V30_PROVENANCE_SHA256),
        "v30_build_receipt": binding(V30_BUILD_RECEIPT, EXPECTED_V30_BUILD_RECEIPT_SHA256),
        "v32_primary_map": binding(V32_PRIMARY_MAP, EXPECTED_V32_PRIMARY_MAP_SHA256),
        "v32_supplement_map": binding(V32_SUPPLEMENT_MAP, EXPECTED_V32_SUPPLEMENT_MAP_SHA256),
        "v32_provenance": binding(V32_PROVENANCE, EXPECTED_V32_PROVENANCE_SHA256),
        "v32_build_receipt": binding(V32_BUILD_RECEIPT, EXPECTED_V32_BUILD_RECEIPT_SHA256),
        "v32_input_acceptance": binding(V32_INPUT_ACCEPTANCE, EXPECTED_V32_INPUT_ACCEPTANCE_SHA256),
        "v32_export_acceptance": binding(V32_EXPORT_ACCEPTANCE, EXPECTED_V32_EXPORT_ACCEPTANCE_SHA256),
        "source15_manifest": binding(SOURCE_MANIFEST, EXPECTED_SOURCE_MANIFEST_SHA256),
        "original_manifest": binding(ORIGINAL_MANIFEST, EXPECTED_ORIGINAL_MANIFEST_SHA256),
        "exporter": binding(EXPORTER, EXPECTED_EXPORTER_SHA256),
        "historical_exhibits": binding(HISTORICAL_EXHIBITS, EXPECTED_HISTORICAL_EXHIBITS_SHA256),
        "popup_tool_acceptance": binding(ROOT_POPUP_ACCEPTANCE, EXPECTED_POPUP_TOOL_RECEIPT_SHA256),
        "navigation_tool_acceptance": binding(ROOT_NAVIGATION_ACCEPTANCE, EXPECTED_NAVIGATION_TOOL_RECEIPT_SHA256),
        "retired_tool_acceptance": binding(ROOT_RETIRED_ACCEPTANCE, EXPECTED_RETIRED_TOOL_RECEIPT_SHA256),
        "attunement_mask_tool_acceptance": binding(ROOT_MASK_ACCEPTANCE, EXPECTED_MASK_TOOL_RECEIPT_SHA256),
    }
    for path in primary + supplement:
        pinned.setdefault(rel(path), binding(path))
    return frozen, primary, supplement, pinned


def map_route_sets(paths: tuple[Path, ...], exporter) -> tuple[set[str], set[str]]:
    routes: set[str] = set()
    static_paths: set[str] = set()
    for path in paths:
        payload = read_json(path, path.name)
        for index, item in enumerate(payload.get("items") or []):
            logical = str(item.get("logical_url") or item.get("original") or "")
            if not logical:
                raise RuntimeError(f"map item has no logical URL: {path}[{index}]")
            route = exporter.mirror.route_path(logical) if exporter.mirror.is_primary_origin(logical) else exporter.mirror.origin_route(logical)
            routes.add(route)
            static_paths.add(exporter.static_rel_for_route(route))
    return routes, static_paths


def make_map_item(row: dict, relationship: str) -> dict:
    actual = str(row["actual_capture_timestamp"])
    role = str(row["_role"])
    return {
        "kind": "image",
        "logical_url": str(row["original"]),
        "original": str(row["original"]),
        "actual_timestamp": actual,
        "indexed_capture_timestamp": actual,
        "mime": str(row["mime"]),
        "dimensions": row.get("dimensions"),
        "decoded_frames": row.get("decoded_frames"),
        "length": int(row["length"]),
        "sha256": str(row["sha256"]).casefold(),
        "cdx_digest": str(row["cdx_digest"]).upper(),
        "local_path": rel(row["_destination"]),
        "temporal_class": row["_temporal_class"],
        "source_acceptance_path": row["_source_receipt_binding"]["path"],
        "public_copy_acceptance_path": row["_public_receipt_binding"]["path"],
        "public_copy_path": str(row["local_path"]),
        "source_relationship": relationship,
        "overlay_role": f"{role}_image_overlay",
    }


def collect_bindings(rows: list[dict], key: str) -> list[dict]:
    seen: set[str] = set()
    result: list[dict] = []
    for row in rows:
        path = str(row[key]["path"])
        if path not in seen:
            seen.add(path)
            result.append(dict(row[key]))
    return result


def validate_new_map(payload: dict, expected_items: list[dict], role: str) -> dict:
    items = payload.get("items")
    if not isinstance(items, list) or len(items) != len(expected_items):
        raise RuntimeError(f"v33 {role} map count differs")
    expected_by_original = {str(item["original"]): item for item in expected_items}
    total = 0
    for index, item in enumerate(items):
        original = str(item.get("original") or "")
        expected = expected_by_original.get(original)
        if expected is None or str(item.get("overlay_role")) != f"{role}_image_overlay":
            raise RuntimeError(f"v33 {role} map item {index} is unexpected")
        source = inside(ROOT / str(item.get("local_path") or ""), f"v33 {role} map source")
        data = source.read_bytes()
        if len(data) != int(item.get("length", -1)) or sha256_bytes(data) != str(item.get("sha256") or "").casefold() or cdx_digest(data) != str(item.get("cdx_digest") or "").upper():
            raise RuntimeError(f"v33 {role} map bytes differ: {original}")
        total += len(data)
    return {"role": f"{role}_image_overlay", "items": len(items), "bytes": total, "hosts": sorted({host(str(item["original"])) for item in items})}


def _requested_from_target(target: str) -> str:
    try:
        values = parse_qs(urlsplit(target).query, keep_blank_values=True).get("requested", [])
        return unquote(values[-1]) if values else ""
    except (TypeError, ValueError):
        return ""


def build_impact(all_old_items: list[dict], new_items: list[dict]) -> dict:
    manifest = read_json(SOURCE_MANIFEST, "source15 manifest")
    validated: dict[str, dict] = {}
    for item in all_old_items + new_items:
        original = str(item.get("original") or item.get("logical_url") or "")
        if original:
            validated[origin_key(original)] = {"original": original, "role": item.get("overlay_role", "frozen"), "new": item in new_items}
    navigation: list[dict] = []
    missing_svg: list[dict] = []
    for record in manifest.get("files", []):
        if not isinstance(record, dict):
            continue
        for reference in record.get("references", []) or []:
            if not isinstance(reference, dict):
                continue
            target = str(reference.get("target") or "")
            requested = _requested_from_target(target)
            match = validated.get(origin_key(requested)) if requested else None
            if match is None:
                continue
            target_path = urlsplit(target).path.casefold()
            entry = {
                "source_page": str(record.get("route") or ""),
                "manifest_route": str(record.get("route") or ""),
                "target": target,
                "requested": requested,
                "resolved_url": str(reference.get("resolved_url") or ""),
                "action": str(reference.get("action") or ""),
                "context": str(reference.get("context") or ""),
                "original": match["original"],
                "new_overlay": bool(match["new"]),
            }
            if target_path == "/__offline/missing.html" and str(reference.get("context") or "") == "navigation":
                navigation.append(entry)
            elif target_path == "/__offline/missing-image.svg":
                missing_svg.append(entry)
    return {
        "schema": "wow-recovery.integration.v33-impact-estimate.v1",
        "status": "static_manifest_estimate_only",
        "source_manifest": binding(SOURCE_MANIFEST, EXPECTED_SOURCE_MANIFEST_SHA256),
        "validated_origins": {
            "old_v32_count": len({origin_key(str(item.get("original") or item.get("logical_url") or "")) for item in all_old_items}),
            "new_v33_count": len({origin_key(str(item.get("original") or item.get("logical_url") or "")) for item in new_items}),
            "scope": "all frozen v32 overlays plus every explicit v33 manifest row; no pending-folder inference",
        },
        "navigation_href_recovery": {"count": len(navigation), "references": navigation},
        "missing_image_svg_marker_recovery": {"count": len(missing_svg), "references": missing_svg},
        "affected_page_routes": sorted({row["source_page"] for row in navigation + missing_svg}),
        "network_requests": 0,
        "export_executed": False,
    }


def build_source_audit(rows: list[dict]) -> dict:
    entries: list[dict] = []
    for row in rows:
        path = row["_destination"]
        data = path.read_bytes()
        entries.append({
            "original": row["original"],
            "host": host(str(row["original"])),
            "role": row["_role"],
            "actual_capture_timestamp": row["actual_capture_timestamp"],
            "temporal_class": row["_temporal_class"],
            "mime": row["mime"],
            "dimensions": row.get("dimensions"),
            "public_copy_path": row["local_path"],
            "public_copy_acceptance_path": row["_public_receipt_binding"]["path"],
            "source_acceptance_path": row["_source_receipt_binding"]["path"],
            "source_acceptance_sha256": row["_source_receipt_binding"]["sha256"],
            "declared_length": int(row["length"]),
            "actual_length": len(data),
            "declared_sha256": row["sha256"],
            "actual_sha256": sha256_bytes(data),
            "declared_cdx_digest": row["cdx_digest"],
            "actual_cdx_digest": cdx_digest(data),
            "byte_match": len(data) == int(row["length"]) and sha256_bytes(data) == str(row["sha256"]).casefold() and cdx_digest(data) == str(row["cdx_digest"]).upper(),
        })
    if not all(row["byte_match"] for row in entries):
        raise RuntimeError("v33 source byte audit mismatch")
    primary = [row for row in entries if row["role"] == "primary"]
    supplement = [row for row in entries if row["role"] == "supplement"]
    return {
        "schema": "wow-recovery.integration.v33-source-byte-audit.v1",
        "status": "actual_public_copy_bytes_checked",
        "source_count": len(entries),
        "primary_count": len(primary),
        "supplement_count": len(supplement),
        "primary_bytes": sum(row["actual_length"] for row in primary),
        "supplement_bytes": sum(row["actual_length"] for row in supplement),
        "total_bytes": sum(row["actual_length"] for row in entries),
        "all_byte_match": True,
        "network_requests": 0,
        "export_executed": False,
        "entries": entries,
    }


def json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_once(path: Path, payload: object, label: str) -> None:
    if path.exists():
        raise RuntimeError(f"refusing to overwrite {label}: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, bytes):
        data = payload
    elif isinstance(payload, str):
        data = payload.encode("utf-8")
    else:
        data = json_bytes(payload)
    path.write_bytes(data)


def build_proposal(new_count: int, new_bytes: int, new_primary: int, new_supplement: int, primary_total: int, supplement_total: int, source_manifest_sha: str) -> str:
    return f"""# v33 input proposal

v33 is a preparation-only delta over the accepted v32 closure. The frozen
v32 closure remains 350 primary, 89 supplement, and 439 total overlays. The
root source-receipts manifest names {new_count} new public-copy images ({new_bytes}
bytes): {new_primary} official `www.worldofwarcraft.com` primary images and
{new_supplement} explicit Armory/Blizzard supplement images. The planned
closure is {primary_total} primary, {supplement_total} supplement, and
{primary_total + supplement_total} total overlays.

The source manifest is `{rel(ROOT_SOURCE_INPUT_MANIFEST)}` with SHA
`{source_manifest_sha}`. No pending directory, unaccepted receipt, or private
payload path is inspected. Each batch must bind an accepted original source
receipt and an accepted original-byte public-copy receipt, and each public
copy is checked for exact length, SHA-256, CDX digest, MIME/magic, and image
decodability before a map can be written.

The impact estimate separates navigation `missing.html` href recoveries from
`missing-image.svg` static markers using every frozen v32 overlay origin plus
all explicit v33 origins. It does not claim those counts are post-export
browser results. The existing exporter route healing is pinned to
`{EXPECTED_EXPORTER_SHA256}`, historical exhibits to
`{EXPECTED_HISTORICAL_EXHIBITS_SHA256}`, and the v32 popup/navigation/retired
Armory/attunement acceptance receipts are bound in preparation evidence.

`execute_v33.py` is export-only and requires a separately accepted
`root-v33-input-acceptance.json` plus the explicit `--go --root-export-go`
pair. Until that gate is accepted, no v33 output, partial output, build
receipt, network request, or publication is permitted.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--source-receipts-manifest", type=Path, default=ROOT_SOURCE_INPUT_MANIFEST)
    args = parser.parse_args(argv)
    if not (args.prepare and args.preflight):
        parser.error("v33 preparation requires both --prepare and --preflight; export is execute_v33.py only")
    for path, label in ((V33_PRIMARY_MAP, "v33 primary map"), (V33_SUPPLEMENT_MAP, "v33 supplement map"), (V33_IMPACT, "v33 impact"), (V33_SOURCE_AUDIT, "v33 source audit"), (V33_PREPARATION, "v33 preparation"), (V33_PREFLIGHT, "v33 preflight"), (V33_PROPOSAL, "v33 proposal")):
        if path.exists():
            raise RuntimeError(f"refusing existing {label}: {path}")
    free_before = shutil.disk_usage(ROOT).free
    if free_before < MIN_FREE_BYTES:
        raise RuntimeError(f"D below v33 preparation floor: {free_before}")
    manifest_path = inside(args.source_receipts_manifest, "v33 source-receipts manifest")
    if manifest_path != ROOT_SOURCE_INPUT_MANIFEST:
        raise RuntimeError(f"v33 source manifest must use the frozen root path: {rel(ROOT_SOURCE_INPUT_MANIFEST)}")
    manifest_sha = sha256_file(manifest_path)
    if manifest_sha.casefold() != EXPECTED_ROOT_SOURCE_INPUT_MANIFEST_SHA256:
        raise RuntimeError(f"v33 source manifest SHA differs: {manifest_sha} != {EXPECTED_ROOT_SOURCE_INPUT_MANIFEST_SHA256}")
    source_manifest, rows, batch_bindings = load_source_input_manifest(manifest_path)
    frozen, old_primary_maps, old_supplement_maps, frozen_pins = frozen_maps()
    exporter = import_exporter()
    old_primary_routes, old_primary_paths = map_route_sets(old_primary_maps, exporter)
    old_supplement_routes, old_supplement_paths = map_route_sets(old_supplement_maps, exporter)
    old_items: list[dict] = []
    for path in old_primary_maps + old_supplement_maps:
        old_items.extend(read_json(path, path.name).get("items") or [])
    new_items = [make_map_item(row, "Root-accepted source/public-copy bytes; v33 delta overlay; no deployment implied.") for row in rows]
    old_originals = {origin_key(str(item.get("original") or item.get("logical_url") or "")) for item in old_items}
    new_originals = {origin_key(str(item["original"])) for item in new_items}
    overlap = old_originals & new_originals
    if overlap:
        raise RuntimeError(f"v33 new originals overlap frozen v32 closure: {sorted(overlap)}")
    primary_items = [item for item in new_items if item["overlay_role"] == "primary_image_overlay"]
    supplement_items = [item for item in new_items if item["overlay_role"] == "supplement_image_overlay"]
    primary_map = {
        "schema_version": "wow-recovery.integration.v33.primary-source-map.v1",
        "kind": "wow_static_v33_primary_image_source_map",
        "role": "primary_image_overlay",
        "accepted": False,
        "status": "prepared_waiting_root_v33_input_acceptance",
        "anchor_timestamp": ANCHOR,
        "copy_rule": "Only rows explicitly listed by the root-frozen v33 source-receipts manifest are added; all v32 maps and accepted bytes remain unchanged.",
        "relative_to_v32": {"new_items": len(primary_items), "new_bytes": sum(int(item["length"]) for item in primary_items), "frozen_primary_overlays": len(old_primary_routes), "frozen_supplement_overlays": len(old_supplement_routes), "v32_primary_map": binding(V32_PRIMARY_MAP, EXPECTED_V32_PRIMARY_MAP_SHA256), "v32_supplement_map": binding(V32_SUPPLEMENT_MAP, EXPECTED_V32_SUPPLEMENT_MAP_SHA256), "v32_provenance": binding(V32_PROVENANCE, EXPECTED_V32_PROVENANCE_SHA256)},
        "source_input_manifest": binding(manifest_path),
        "source_acceptance": collect_bindings(rows, "_source_receipt_binding"),
        "public_copy_acceptance": collect_bindings(rows, "_public_receipt_binding"),
        "items": primary_items,
    }
    supplement_map = {
        "schema_version": "wow-recovery.integration.v33.supplement-source-map.v1",
        "kind": "wow_static_v33_supplement_image_source_map",
        "role": "supplement_image_overlay",
        "accepted": False,
        "status": "prepared_waiting_root_v33_input_acceptance",
        "anchor_timestamp": ANCHOR,
        "copy_rule": "Only explicit Armory/Blizzard rows named by the root-frozen v33 source-receipts manifest are supplements; no other host or path is inferred.",
        "relative_to_v32": {"new_items": len(supplement_items), "new_bytes": sum(int(item["length"]) for item in supplement_items), "frozen_primary_overlays": len(old_primary_routes), "frozen_supplement_overlays": len(old_supplement_routes), "v32_primary_map": binding(V32_PRIMARY_MAP, EXPECTED_V32_PRIMARY_MAP_SHA256), "v32_supplement_map": binding(V32_SUPPLEMENT_MAP, EXPECTED_V32_SUPPLEMENT_MAP_SHA256), "v32_provenance": binding(V32_PROVENANCE, EXPECTED_V32_PROVENANCE_SHA256)},
        "source_input_manifest": binding(manifest_path),
        "source_acceptance": collect_bindings(rows, "_source_receipt_binding"),
        "public_copy_acceptance": collect_bindings(rows, "_public_receipt_binding"),
        "items": supplement_items,
    }
    primary_check = validate_new_map(primary_map, primary_items, "primary")
    supplement_check = validate_new_map(supplement_map, supplement_items, "supplement")
    new_primary_routes, new_primary_paths = map_route_sets((V33_PRIMARY_MAP,), exporter) if V33_PRIMARY_MAP.exists() else (set(), set())
    # Validate new route collisions directly before maps are written.
    for item in new_items:
        logical = str(item["logical_url"])
        route = exporter.mirror.route_path(logical) if exporter.mirror.is_primary_origin(logical) else exporter.mirror.origin_route(logical)
        if route in old_primary_routes | old_supplement_routes or route.startswith("/__offline/"):
            raise RuntimeError(f"v33 new image route collides with frozen/generated route: {route}")
    new_primary_routes = {exporter.mirror.route_path(str(item["logical_url"])) for item in primary_items}
    new_supplement_routes = {exporter.mirror.origin_route(str(item["logical_url"])) for item in supplement_items}
    if new_primary_routes & new_supplement_routes:
        raise RuntimeError("v33 primary and supplement routes overlap")
    primary_total = len(old_primary_routes | new_primary_routes)
    supplement_total = len(old_supplement_routes | new_supplement_routes)
    impact = build_impact(old_items, new_items)
    source_audit = build_source_audit(rows)
    v32_provenance = read_json(V32_PROVENANCE, V32_PROVENANCE.name)
    v32_stats = v32_provenance.get("stats") or {}
    expected_after_export = {
        "source_records": int(v32_stats.get("source_records", 8357)),
        "primary_overlays": primary_total,
        "supplement_overlays": supplement_total,
        "total_overlays": primary_total + supplement_total,
        "declared_files": None,
        "actual_files": None,
        "root_expectation_required": True,
        "runtime_allowed_changes": {
            "historical_body_banner_pages": 5,
            "retired_armory_script": "/new-hp/js/enhancedtip.js",
            "popup_runtime": "__offline/pages_runtime.js",
            "attunement_mask_page": "/bcattunement/index.html",
            "navigation_href_recovery": impact["navigation_href_recovery"]["count"],
            "missing_image_svg_marker_recovery": impact["missing_image_svg_marker_recovery"]["count"],
            "note": "Navigation recovery count uses all frozen v32 plus explicit v33 validated origins; SVG marker count is separate and neither is a browser acceptance result.",
        },
    }
    map_meta = {"primary": {"path": rel(V33_PRIMARY_MAP), "sha256": sha256_bytes(json_bytes(primary_map)), "items": len(primary_items), "bytes": sum(int(item["length"]) for item in primary_items)}, "supplement": {"path": rel(V33_SUPPLEMENT_MAP), "sha256": sha256_bytes(json_bytes(supplement_map)), "items": len(supplement_items), "bytes": sum(int(item["length"]) for item in supplement_items)}}
    prep = {
        "schema": "wow-recovery.integration.v33-input-preparation.v1",
        "status": "prepared_waiting_root_v33_input_acceptance",
        "checked_utc": datetime.utcnow().isoformat() + "Z",
        "builder": {"path": rel(Path(__file__)), "sha256": sha256_file(Path(__file__))},
        "source_input_manifest": binding(manifest_path),
        "source_input_counts": {key: source_manifest[key] for key in ("new_images", "image_bytes", "new_primary_images", "new_supplement_images")},
        "source_batches": batch_bindings,
        "frozen_v32_closure": {"primary_overlays": len(old_primary_routes), "supplement_overlays": len(old_supplement_routes), "total_overlays": len(old_primary_routes) + len(old_supplement_routes), "maps": [binding(path) for path in old_primary_maps + old_supplement_maps], "provenance": binding(V32_PROVENANCE, EXPECTED_V32_PROVENANCE_SHA256)},
        "new_maps": map_meta,
        "source_byte_audit": {"path": rel(V33_SOURCE_AUDIT), "sha256": sha256_bytes(json_bytes(source_audit)), "items": len(rows), "bytes": sum(int(row["length"]) for row in rows)},
        "tool_bindings": {"exporter": frozen_pins["exporter"], "historical_exhibits": frozen_pins["historical_exhibits"], "popup_tool_acceptance": frozen_pins["popup_tool_acceptance"], "navigation_tool_acceptance": frozen_pins["navigation_tool_acceptance"], "retired_tool_acceptance": frozen_pins["retired_tool_acceptance"], "attunement_mask_tool_acceptance": frozen_pins["attunement_mask_tool_acceptance"]},
        "network_requests": 0,
        "export_executed": False,
        "old_image_payloads_rehashed": False,
        "disk_free_bytes": free_before,
        "disk_free_floor_bytes": MIN_FREE_BYTES,
    }
    preflight = {
        "schema": "wow-recovery.integration.v33-preflight.v1",
        "status": "preflight_passed_waiting_root_v33_input_acceptance",
        "checked_utc": prep["checked_utc"],
        "source_input_manifest": prep["source_input_manifest"],
        "new_image_count": len(rows),
        "new_image_bytes": sum(int(row["length"]) for row in rows),
        "new_primary_count": len(primary_items),
        "new_supplement_count": len(supplement_items),
        "map_validation": {"primary": primary_check, "supplement": supplement_check},
        "loader_preflight": {"primary_overlay_records": primary_total, "supplement_overlay_records": supplement_total, "total_overlay_records": primary_total + supplement_total, "new_primary_records": len(primary_items), "new_supplement_records": len(supplement_items), "guide_collection_groups": 3, "guide_collection_images": 39, "guide_previews": 22, "network_requests": 0, "export_executed": False, "old_image_payloads_rehashed": False},
        "expected_after_export": expected_after_export,
        "frozen_pins": frozen_pins,
        "impact": {"path": rel(V33_IMPACT), "sha256": sha256_bytes(json_bytes(impact))},
        "source_byte_audit": {"path": rel(V33_SOURCE_AUDIT), "sha256": sha256_bytes(json_bytes(source_audit))},
        "root_input_acceptance_required": True,
        "disk_free_bytes": free_before,
        "disk_free_floor_bytes": MIN_FREE_BYTES,
    }
    proposal = build_proposal(len(rows), sum(int(row["length"]) for row in rows), len(primary_items), len(supplement_items), primary_total, supplement_total, sha256_file(manifest_path))
    runner_note = """# v33 runner preparation

`execute_v33.py` is a one-shot export wrapper. It never regenerates maps or
preflight, refuses an existing output/partial/receipt, checks the accepted
root input gate's exact `map_bindings` and public-copy list, and requires
`--go --root-export-go`. The exporter receives the frozen v28 primary and
supplement closure plus v29, v30, v32, and the two v33 delta maps. The source
manifest is the only authority for the new image count; pending folders are
never scanned. Root must supply post-export declared/actual file expectations
before authorizing the run.
"""
    # Validate payloads in memory and then write all new artifacts once. No
    # output, receipt, or root status file is touched by this preparation.
    write_once(V33_PRIMARY_MAP, primary_map, "v33 primary map")
    write_once(V33_SUPPLEMENT_MAP, supplement_map, "v33 supplement map")
    write_once(V33_IMPACT, impact, "v33 impact")
    write_once(V33_SOURCE_AUDIT, source_audit, "v33 source audit")
    write_once(V33_PREPARATION, prep, "v33 preparation")
    write_once(V33_PREFLIGHT, preflight, "v33 preflight")
    write_once(V33_PROPOSAL, proposal, "v33 proposal")
    write_once(V33_RUNNER_NOTE, runner_note, "v33 runner note")
    print(json.dumps({"status": preflight["status"], "new_images": len(rows), "new_primary": len(primary_items), "new_supplement": len(supplement_items), "new_bytes": sum(int(row["length"]) for row in rows), "primary_map": rel(V33_PRIMARY_MAP), "supplement_map": rel(V33_SUPPLEMENT_MAP), "preflight": rel(V33_PREFLIGHT), "network_requests": 0, "export_executed": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
