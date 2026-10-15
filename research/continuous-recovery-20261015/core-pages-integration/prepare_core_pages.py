"""Prepare the next core-pages source map without building a site.

The seven pages accepted in core-pages3 are the current integration baseline.
Follow-up payload maps are observations until an independent acceptance receipt
is supplied.  With such a receipt this script can select a newer pre-anchor
body for the same target, while retaining every raw body and header path in
the provenance record.  It deliberately does not perform network I/O and it
does not invoke the frozen-site builder.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
RECOVERY = ROOT / "research" / "continuous-recovery-20261015"
BASE_MAP = RECOVERY / "network-core-pages3" / "payload-source-map.json"
BASE_ACCEPTANCE = RECOVERY / "core-pages3-acceptance.json"
CONTENT_REVIEW = RECOVERY / "root-content-review-0753.json"
CANDIDATE_MAP = RECOVERY / "network-core-pages4" / "payload-source-map.json"
REDIRECT_EVIDENCE = RECOVERY / "network-core-pages4" / "redirect-evidence.json"
FROZEN_MANIFEST = ROOT / "offline" / "build-manifest.json"
OWN_DIR = RECOVERY / "core-pages-integration"
PENDING_MAP = OWN_DIR / "core-pages-source-map.pending.json"
V9_DIR = ROOT / ".scratch" / "offline-navigation-20261015-v9"
V9_PREPARATION = V9_DIR / "PREPARATION.json"
V7C_DIR = ROOT / ".scratch" / "offline-navigation-20261015-v7c"
V7C_MANIFEST = V7C_DIR / "build-manifest.json"

EXPECTED_BASE_TARGETS = {
    "/news/wow-news2004.html",
    "/news/wow-news-07-2005.html",
    "/news/wow-news-08-2005.html",
    "/news/wow-news-09-2005.html",
    "/news/wow-news-10-2005.html",
    "/news/wow-news-11-2005.html",
    "/ptr",
}
PTR_ROUTE = "/ptr/index.html"
PTR_ALIASES = ["/ptr", "/ptr/"]
PTR_FACTS = [
    "The selected source described the Public Test Realms as a public environment for testing upcoming content patches before release to live realms.",
    "The selected source described feedback gathered from the public test and the test realm forum.",
]


class PreparationError(RuntimeError):
    """Raised when an input fails the local provenance gate."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel_to_root(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise PreparationError(f"missing JSON input: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PreparationError(f"cannot read JSON input {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PreparationError(f"JSON root is not an object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def parse_timestamp(value: Any) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise PreparationError("source has no actual_memento")
    if re.fullmatch(r"\d{14}", text):
        return datetime.strptime(text, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise PreparationError(f"invalid timestamp: {value!r}") from exc
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def manifest_timestamp(entry: dict[str, Any]) -> str:
    """Return the exporter contract's fourteen-digit UTC timestamp."""

    supplied = str(entry.get("actual_timestamp") or "").strip()
    if re.fullmatch(r"\d{14}", supplied):
        return supplied
    return parse_timestamp(entry.get("actual_memento")).astimezone(timezone.utc).strftime(
        "%Y%m%d%H%M%S"
    )


def resolve_map_file(map_path: Path, raw_value: Any) -> Path:
    """Resolve a map-relative raw path and reject paths outside its batch."""

    if not isinstance(raw_value, str) or not raw_value.strip():
        raise PreparationError(f"missing raw path in {map_path}")
    raw = Path(raw_value)
    if raw.is_absolute():
        candidate = raw.resolve()
    else:
        candidate = (map_path.parent / raw).resolve()
    batch_root = map_path.parent.resolve()
    try:
        candidate.relative_to(batch_root)
    except ValueError as exc:
        raise PreparationError(
            f"raw path escapes its source batch: {raw_value!r} from {map_path}"
        ) from exc
    return candidate


def validate_raw_entry(entry: dict[str, Any], map_path: Path) -> dict[str, Any]:
    body = resolve_map_file(map_path, entry.get("raw_body_path"))
    headers = resolve_map_file(map_path, entry.get("raw_headers_path"))
    if not body.is_file():
        raise PreparationError(f"raw body missing: {body}")
    if not headers.is_file():
        raise PreparationError(f"raw headers missing: {headers}")
    actual_bytes = body.stat().st_size
    actual_sha = sha256_file(body)
    expected_bytes = entry.get("body_bytes")
    expected_sha = entry.get("body_sha256")
    if actual_bytes != expected_bytes:
        raise PreparationError(
            f"raw body length mismatch for {entry.get('target')}: "
            f"{actual_bytes} != {expected_bytes}"
        )
    if actual_sha != expected_sha:
        raise PreparationError(
            f"raw body SHA mismatch for {entry.get('target')}: "
            f"{actual_sha} != {expected_sha}"
        )
    if entry.get("source_status") != 200:
        raise PreparationError(
            f"selected payload is not HTTP 200 for {entry.get('target')}: "
            f"{entry.get('source_status')}"
        )
    parse_timestamp(entry.get("actual_memento"))
    return {
        "body_path": body,
        "headers_path": headers,
        "body_bytes": actual_bytes,
        "body_sha256": actual_sha,
    }


def read_review_entries(review: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if review.get("accepted_content_identity") is not True:
        raise PreparationError("root content review is not accepted")
    entries = review.get("entries")
    if not isinstance(entries, list):
        raise PreparationError("root content review has no entries array")
    result: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("target"):
            raise PreparationError("malformed root content review entry")
        result[str(entry["target"])] = entry
    return result


def read_base_acceptance(path: Path) -> dict[str, Any]:
    acceptance = load_json(path)
    if acceptance.get("accepted") is not True:
        raise PreparationError(f"base acceptance is not accepted: {path}")
    if acceptance.get("network_requests_by_acceptance") != 0:
        raise PreparationError(
            f"base acceptance has unexpected network requests: {path}"
        )
    return acceptance


def extract_ptr_facts(body_path: Path) -> list[str]:
    plain = body_path.read_text(encoding="utf-8", errors="replace")
    plain = re.sub(r"<[^>]+>", " ", plain)
    plain = " ".join(plain.split())
    facts: list[str] = []
    if re.search(
        r"Public Test Realms.*?test upcoming content patches.*?live realms",
        plain,
        re.IGNORECASE,
    ):
        facts.append(PTR_FACTS[0])
    if re.search(
        r"feedback from the public test.*?test realm forum",
        plain,
        re.IGNORECASE,
    ):
        facts.append(PTR_FACTS[1])
    return facts


def verify_base_inputs(
    base_map_path: Path,
    base_acceptance_path: Path,
    review_path: Path,
    frozen_manifest_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]:
    base_map = load_json(base_map_path)
    if base_map.get("only_real_valid_entities") is not True:
        raise PreparationError("base payload map is not marked only_real_valid_entities")
    entries = base_map.get("entries")
    if not isinstance(entries, list):
        raise PreparationError("base payload map has no entries array")
    by_target = {str(item.get("target")): item for item in entries if isinstance(item, dict)}
    if set(by_target) != EXPECTED_BASE_TARGETS:
        raise PreparationError(
            "base target conservation failed: "
            f"expected {sorted(EXPECTED_BASE_TARGETS)}, got {sorted(by_target)}"
        )
    acceptance = read_base_acceptance(base_acceptance_path)
    accepted_payloads = {
        str(item.get("target")): item
        for item in acceptance.get("accepted_payloads", [])
        if isinstance(item, dict) and item.get("target")
    }
    if set(accepted_payloads) != EXPECTED_BASE_TARGETS:
        raise PreparationError("base acceptance target set does not conserve seven entries")
    review = load_json(review_path)
    review_by_target = read_review_entries(review)
    if set(review_by_target) != EXPECTED_BASE_TARGETS:
        raise PreparationError("root content review target set does not conserve seven entries")
    for target, entry in by_target.items():
        checked = validate_raw_entry(entry, base_map_path)
        accepted = accepted_payloads[target]
        review_entry = review_by_target[target]
        if accepted.get("sha256") != checked["body_sha256"]:
            raise PreparationError(f"base acceptance SHA mismatch for {target}")
        if accepted.get("bytes") != checked["body_bytes"]:
            raise PreparationError(f"base acceptance length mismatch for {target}")
        if review_entry.get("source_sha256") != checked["body_sha256"]:
            raise PreparationError(f"root review SHA mismatch for {target}")
        if review_entry.get("accepted_content_identity") is not True:
            raise PreparationError(f"root review entry is not accepted for {target}")
    frozen = load_json(frozen_manifest_path)
    if frozen.get("anchor_timestamp") != "20080512210044":
        raise PreparationError(
            "unexpected frozen anchor timestamp: "
            f"{frozen.get('anchor_timestamp')}"
        )
    return base_map, acceptance, review_by_target, frozen


def observe_candidate_map(map_path: Path | None) -> dict[str, Any] | None:
    if map_path is None:
        return None
    if not map_path.exists():
        return {
            "path": rel_to_root(map_path),
            "present": False,
            "selection": "not_observed",
        }
    data = load_json(map_path)
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise PreparationError(f"candidate map has no entries array: {map_path}")
    observed: list[dict[str, Any]] = []
    for raw in entries:
        if not isinstance(raw, dict) or not raw.get("target"):
            raise PreparationError(f"malformed candidate entry in {map_path}")
        checked = validate_raw_entry(raw, map_path)
        observed.append(
            {
                "target": raw["target"],
                "actual_memento": raw.get("actual_memento"),
                "body_bytes": checked["body_bytes"],
                "body_sha256": checked["body_sha256"],
                "raw_body_path": rel_to_root(checked["body_path"]),
                "raw_headers_path": rel_to_root(checked["headers_path"]),
                "source_status": raw.get("source_status"),
            }
        )
    return {
        "path": rel_to_root(map_path),
        "sha256": sha256_file(map_path),
        "schema": data.get("schema"),
        "present": True,
        "entry_count": len(observed),
        "entries": observed,
        "selection": "unselected_without_acceptance_receipt",
    }


def acceptance_payloads(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    acceptance = read_base_acceptance(path)
    return {
        str(item.get("target")): item
        for item in acceptance.get("accepted_payloads", [])
        if isinstance(item, dict) and item.get("target")
    }


def select_entries(
    base_map_path: Path,
    base_map: dict[str, Any],
    base_review: dict[str, dict[str, Any]],
    candidate_map_path: Path | None,
    candidate_acceptance_path: Path | None,
    anchor_timestamp: str,
) -> tuple[list[tuple[dict[str, Any], Path, dict[str, Any] | None, str]], dict[str, Any]]:
    """Select accepted entries and return (entry, map_path, review, reason)."""

    chosen: dict[str, tuple[dict[str, Any], Path, dict[str, Any] | None, str]] = {}
    for entry in base_map["entries"]:
        chosen[str(entry["target"])] = (
            entry,
            base_map_path,
            base_review.get(str(entry["target"])),
            "accepted_core_pages3_baseline",
        )
    candidate_info: dict[str, Any] = {
        "candidate_acceptance": (
            rel_to_root(candidate_acceptance_path)
            if candidate_acceptance_path is not None
            else None
        ),
        "selected_replacements": [],
        "selected_new_targets": [],
        "selection_blocked_without_acceptance": bool(candidate_map_path and not candidate_acceptance_path),
    }
    if candidate_map_path is None or not candidate_map_path.exists():
        return list(chosen.values()), candidate_info
    if candidate_acceptance_path is None:
        return list(chosen.values()), candidate_info

    candidate_map = load_json(candidate_map_path)
    accepted = acceptance_payloads(candidate_acceptance_path)
    candidate_info["candidate_acceptance_sha256"] = sha256_file(candidate_acceptance_path)
    candidate_info["accepted_payload_count"] = len(accepted)
    anchor = parse_timestamp(anchor_timestamp)
    for entry in candidate_map.get("entries", []):
        if not isinstance(entry, dict) or not entry.get("target"):
            continue
        target = str(entry["target"])
        accepted_item = accepted.get(target)
        if accepted_item is None:
            continue
        checked = validate_raw_entry(entry, candidate_map_path)
        if accepted_item.get("sha256") != checked["body_sha256"]:
            raise PreparationError(f"candidate acceptance SHA mismatch for {target}")
        if accepted_item.get("bytes") != checked["body_bytes"]:
            raise PreparationError(f"candidate acceptance length mismatch for {target}")
        memento = parse_timestamp(entry.get("actual_memento"))
        if memento >= anchor:
            raise PreparationError(f"candidate is not pre-anchor for {target}")
        previous = chosen.get(target)
        if previous is not None:
            previous_memento = parse_timestamp(previous[0].get("actual_memento"))
            if memento <= previous_memento:
                continue
            reason = "accepted_newer_pre_anchor_replacement"
            candidate_info["selected_replacements"].append(target)
        else:
            reason = "accepted_new_pre_anchor_target"
            candidate_info["selected_new_targets"].append(target)
        chosen[target] = (entry, candidate_map_path, None, reason)
    return list(chosen.values()), candidate_info


def make_file_entry(
    item: tuple[dict[str, Any], Path, dict[str, Any] | None, str],
    root_review: dict[str, dict[str, Any]],
    base_acceptance_path: Path,
    candidate_acceptance_path: Path | None,
) -> dict[str, Any]:
    entry, source_map_path, review_entry, selection_reason = item
    target = str(entry["target"])
    checked = validate_raw_entry(entry, source_map_path)
    body_path = checked["body_path"]
    route = PTR_ROUTE if target == "/ptr" else target
    aliases = PTR_ALIASES if target == "/ptr" else []
    source_url = str(entry["query_original_url"])
    result: dict[str, Any] = {
        "logical_url": source_url,
        "source_url": source_url,
        "source_base_url": source_url,
        "captured_original": str(entry.get("captured_original_url") or source_url),
        "local_path": rel_to_root(body_path),
        "sha256": checked["body_sha256"],
        "content_length": checked["body_bytes"],
        "actual_timestamp": manifest_timestamp(entry),
        "actual_memento": entry["actual_memento"],
        "derived_route": route,
        "route_aliases": aliases,
        "mime": entry.get("content_type") or "text/html",
        "kind": "html",
        "role": "historical_ptr_exhibit" if target == "/ptr" else "archived_news_html" if target.startswith("/news/") else "core_historical_html",
        "temporal_class": "pre_anchor_historical_capture",
        "source_status": entry.get("source_status"),
        "raw_body_path": rel_to_root(body_path),
        "raw_headers_path": rel_to_root(checked["headers_path"]),
        "source_batch": rel_to_root(source_map_path),
        "source_batch_schema": load_json(source_map_path).get("schema"),
        "selection_reason": selection_reason,
        "source_entities_unmodified": True,
        "source_evidence": {
            "payload_entry_target": target,
            "payload_map": rel_to_root(source_map_path),
            "payload_body_sha256": checked["body_sha256"],
            "payload_body_bytes": checked["body_bytes"],
            "raw_headers": rel_to_root(checked["headers_path"]),
        },
    }
    for optional in (
        "indexed_capture_timestamp",
        "indexed_original_url",
        "indexed_statuscode",
        "indexed_cdx_digest",
        "cdx_digest_calculated",
        "cdx_digest_match",
        "title",
    ):
        if optional in entry:
            result[optional] = entry[optional]
    if target.startswith("/news/"):
        result["article_body_preservation"] = "existing_exporter_raw_body"
        result["review_evidence"] = root_review.get(target)
    if target == "/ptr":
        facts = extract_ptr_facts(body_path)
        if not facts:
            raise PreparationError(
                "selected PTR source has no recognized source-backed facts; "
                "hold for manual review rather than inventing exhibit text"
            )
        result.update(
            {
                "historical_exhibit_required": True,
                "exhibit_title": "World of Warcraft Public Test Realm — Historical Exhibit",
                "verified_facts": facts,
                "operational_controls_rendered": False,
                "local_related_routes": [
                    "/index.html",
                    "/info/basics/guide.html",
                    "/info/faq/ptr.html",
                    "/patchnotes/test-realm-patchnotes.html",
                ],
                "excluded_operational_destinations": [
                    "character-copy",
                    "software-download",
                    "test-realm-forum",
                ],
            }
        )
    if candidate_acceptance_path is not None and source_map_path != BASE_MAP:
        result["candidate_acceptance"] = rel_to_root(candidate_acceptance_path)
    return result


def redirect_observation(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    if not path.exists():
        return {"path": rel_to_root(path), "present": False}
    data = load_json(path)
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise PreparationError(f"redirect evidence has no entries array: {path}")
    return {
        "path": rel_to_root(path),
        "present": True,
        "sha256": sha256_file(path),
        "schema": data.get("schema"),
        "entry_count": len(entries),
        "targets": [entry.get("target") for entry in entries if isinstance(entry, dict)],
        "registered_as_route_alias": False,
        "reason": "redirect-only evidence is retained separately and cannot supply an HTML body or alias",
    }


def v7c_preservation_observation() -> dict[str, Any]:
    """Record the existing v7c baseline without copying or modifying it."""

    return {
        "staging_directory": rel_to_root(V7C_DIR),
        "site_present": (V7C_DIR / "site").is_dir(),
        "build_manifest": rel_to_root(V7C_MANIFEST),
        "build_manifest_present": V7C_MANIFEST.is_file(),
        "build_manifest_sha256": sha256_file(V7C_MANIFEST)
        if V7C_MANIFEST.is_file()
        else None,
        "source_and_image_overlays_untouched": True,
        "future_builder_policy": "reuse v7c baseline and preserve its existing source/image overlays",
    }


def build_pending_map(
    *,
    generated_utc: str,
    base_map_path: Path,
    base_map: dict[str, Any],
    base_acceptance_path: Path,
    review_path: Path,
    review_by_target: dict[str, dict[str, Any]],
    frozen_manifest_path: Path,
    frozen_manifest: dict[str, Any],
    candidate_observation: dict[str, Any] | None,
    candidate_selection: dict[str, Any],
    redirect_info: dict[str, Any] | None,
    selected: list[tuple[dict[str, Any], Path, dict[str, Any] | None, str]],
    candidate_acceptance_path: Path | None,
    v7c_observation: dict[str, Any],
) -> dict[str, Any]:
    files = [
        make_file_entry(
            item,
            review_by_target,
            base_acceptance_path,
            candidate_acceptance_path,
        )
        for item in sorted(selected, key=lambda item: str(item[0]["target"]))
    ]
    return {
        "schema_version": "wow-recovery.core-pages-integration-source-map.pending.v1",
        "status": "prepared_pending_NET004_selection" if candidate_observation and candidate_observation.get("present") and not candidate_acceptance_path else "prepared",
        "generated_utc": generated_utc,
        "network_performed": False,
        "network_note": "No network request was made by this preparation run; all selected bodies and headers were already local.",
        "source_entities_unmodified": True,
        "anchor_timestamp": frozen_manifest.get("anchor_timestamp"),
        "selected_target_count": len(files),
        "selected_targets": [entry["logical_url"] for entry in files],
        "selected_route_count": len({entry["derived_route"] for entry in files}),
        "base_selection": {
            "map": rel_to_root(base_map_path),
            "map_sha256": sha256_file(base_map_path),
            "acceptance": rel_to_root(base_acceptance_path),
            "acceptance_sha256": sha256_file(base_acceptance_path),
            "root_content_review": rel_to_root(review_path),
            "root_content_review_sha256": sha256_file(review_path),
            "entry_count": len(base_map.get("entries", [])),
            "target_conserved": {
                str(entry.get("target")) for entry in base_map.get("entries", [])
            }
            == EXPECTED_BASE_TARGETS,
        },
        "candidate_observation": candidate_observation,
        "candidate_selection": candidate_selection,
        "redirect_only_observation": redirect_info,
        "v7c_preservation_baseline": v7c_observation,
        "frozen_manifest": {
            "path": rel_to_root(frozen_manifest_path),
            "sha256": sha256_file(frozen_manifest_path),
            "anchor_timestamp": frozen_manifest.get("anchor_timestamp"),
            "site_unchanged": True,
        },
        "ptr_contract": {
            "canonical_route": PTR_ROUTE,
            "aliases": PTR_ALIASES,
            "title": "World of Warcraft Public Test Realm — Historical Exhibit",
            "renderer_source": "tools/historical_exhibits.py",
            "no_active_business_anchors": True,
            "no_guessed_BC_or_battleground_aliases": True,
        },
        "files": files,
        "notes": [
            "Six news bodies remain raw source entities for the existing exporter; this map does not rewrite article HTML.",
            "PTR is rendered through an explicit static historical exhibit using only source-backed facts and confirmed local archive links.",
            "A future accepted candidate map may replace a same-target body only when its accepted Memento is newer and still pre-anchor; older raw inputs remain listed in their source batches.",
        ],
    }


def build_preparation_record(
    *,
    generated_utc: str,
    pending_map: dict[str, Any],
    base_map_path: Path,
    candidate_observation: dict[str, Any] | None,
    redirect_info: dict[str, Any] | None,
    output_map_path: Path,
    v7c_observation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema": "wow-recovery.core-pages-integration-preparation.v1",
        "generated_utc": generated_utc,
        "network_requests": 0,
        "selection_status": pending_map["status"],
        "site_built": False,
        "frozen_offline_tree_modified": False,
        "output_source_map": rel_to_root(output_map_path),
        "v9_staging_directory": rel_to_root(V9_DIR),
        "v9_site_directory_created": False,
        "base_input": {
            "path": rel_to_root(base_map_path),
            "sha256": sha256_file(base_map_path),
            "target_count": pending_map["base_selection"]["entry_count"],
        },
        "selected_target_count": pending_map["selected_target_count"],
        "selected_route_count": pending_map["selected_route_count"],
        "candidate_observation": candidate_observation,
        "redirect_only_observation": redirect_info,
        "v7c_preservation_baseline": v7c_observation,
        "no_production_files_changed": True,
        "no_network": True,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-map", type=Path, default=BASE_MAP)
    parser.add_argument("--base-acceptance", type=Path, default=BASE_ACCEPTANCE)
    parser.add_argument("--content-review", type=Path, default=CONTENT_REVIEW)
    parser.add_argument("--candidate-map", type=Path, default=CANDIDATE_MAP)
    parser.add_argument("--candidate-acceptance", type=Path, default=None)
    parser.add_argument("--redirect-evidence", type=Path, default=REDIRECT_EVIDENCE)
    parser.add_argument("--frozen-manifest", type=Path, default=FROZEN_MANIFEST)
    parser.add_argument("--output-map", type=Path, default=PENDING_MAP)
    parser.add_argument("--preparation-record", type=Path, default=V9_PREPARATION)
    parser.add_argument(
        "--prepare",
        action="store_true",
        help="write the pending source map and v9 preparation record (the default action)",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="refuse explicitly: full site construction is outside this preparation run",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.build:
        print(
            "refusing --build: wait for an accepted NET004 source map and an explicit integration run",
            file=sys.stderr,
        )
        return 2
    generated_utc = utc_now()
    try:
        base_map, _base_acceptance, review_by_target, frozen = verify_base_inputs(
            args.base_map.resolve(),
            args.base_acceptance.resolve(),
            args.content_review.resolve(),
            args.frozen_manifest.resolve(),
        )
        candidate_path = args.candidate_map.resolve() if args.candidate_map else None
        candidate_observed = observe_candidate_map(candidate_path)
        redirect_path = args.redirect_evidence.resolve() if args.redirect_evidence else None
        redirect_info = redirect_observation(redirect_path)
        v7c_info = v7c_preservation_observation()
        candidate_acceptance_path = (
            args.candidate_acceptance.resolve() if args.candidate_acceptance else None
        )
        selected, candidate_selection = select_entries(
            args.base_map.resolve(),
            base_map,
            review_by_target,
            candidate_path,
            candidate_acceptance_path,
            str(frozen["anchor_timestamp"]),
        )
        pending = build_pending_map(
            generated_utc=generated_utc,
            base_map_path=args.base_map.resolve(),
            base_map=base_map,
            base_acceptance_path=args.base_acceptance.resolve(),
            review_path=args.content_review.resolve(),
            review_by_target=review_by_target,
            frozen_manifest_path=args.frozen_manifest.resolve(),
            frozen_manifest=frozen,
            candidate_observation=candidate_observed,
            candidate_selection=candidate_selection,
            redirect_info=redirect_info,
            selected=selected,
            candidate_acceptance_path=candidate_acceptance_path,
            v7c_observation=v7c_info,
        )
        write_json(args.output_map.resolve(), pending)
        preparation = build_preparation_record(
            generated_utc=generated_utc,
            pending_map=pending,
            base_map_path=args.base_map.resolve(),
            candidate_observation=candidate_observed,
            redirect_info=redirect_info,
            output_map_path=args.output_map.resolve(),
            v7c_observation=v7c_info,
        )
        write_json(args.preparation_record.resolve(), preparation)
    except PreparationError as exc:
        print(f"PREPARATION_ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "result": "PASS",
                "generated_utc": generated_utc,
                "selected_targets": pending["selected_target_count"],
                "selected_routes": pending["selected_route_count"],
                "candidate_status": pending["status"],
                "candidate_entries_observed": (
                    candidate_observed.get("entry_count", 0)
                    if candidate_observed
                    else 0
                ),
                "redirect_only_entries": (
                    redirect_info.get("entry_count", 0) if redirect_info else 0
                ),
                "network_requests": 0,
                "site_built": False,
                "output_map": rel_to_root(args.output_map.resolve()),
                "preparation_record": rel_to_root(args.preparation_record.resolve()),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
