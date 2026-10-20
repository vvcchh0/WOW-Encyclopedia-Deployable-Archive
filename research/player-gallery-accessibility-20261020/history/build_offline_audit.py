#!/usr/bin/env python3
"""Build the sanitized, offline 50-gallery historical availability table.

This program is deliberately read-only with respect to all recovery evidence.  It
reads the frozen registry/ledgers, accepted local CDX receipts and their saved
bodies, then writes only the outputs in this history directory.  No network
client is imported or invoked.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MAX_READ_BYTES = 96 * 1024 * 1024
AUDIT_DATE = "2026-10-20"
AUDIT_DATE_TO = "20261020235959"
POST_2010_FROM = "20101208000000"
ANCHOR = "20080512210044"
LATE_TO = "20101207235959"

REGISTRY = "research/continuous-recovery-20261016/local-audit/gallery-final-v7/gallery-prefix-registry-v7.json"
LEDGER = "research/continuous-recovery-20261019/gallery-audit/coverage-after-rest10b/coverage-ledger.json"
R3 = "research/continuous-recovery-20261019/gallery-audit/coverage-after-rest10b/full-source15-crossrefs-r3/coverage-ledger-r3-addendum.json"
REST10A = "research/continuous-recovery-20261019/publication/root-gallery-late-rest10a-source-acceptance.json"
REST10B = "research/continuous-recovery-20261019/publication/root-gallery-late-rest10b-source-acceptance.json"
GAP01 = "research/continuous-recovery-20261019/publication/root-gallery-late-gap01-source-acceptance.json"
KARAZHAN_V3 = "research/continuous-recovery-20261018/publication/root-karazhan-availability-v3.json"
ZUL_PRIOR = "research/continuous-recovery-20261018/publication/root-gallery-late-window-source-acceptance.json"
SCREENSHOT_ACCEPTANCE = "research/screenshot-accessibility-20261014/accessibility-acceptance.json"
SCREENSHOT_DOC = "docs/screenshot-accessibility-20261014.md"

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp")
NATIVE_FULL_RE = re.compile(r"ss\d+\.jpg", re.IGNORECASE)
NATIVE_THUMB_RE = re.compile(r"ss\d+-thumb\.jpg", re.IGNORECASE)


class AuditBuilder:
    def __init__(self) -> None:
        self.cache: dict[str, bytes] = {}
        self.read_bytes = 0
        self.read_files: list[dict[str, object]] = []

    def read_bytes_file(self, rel: str) -> bytes:
        if rel in self.cache:
            return self.cache[rel]
        path = ROOT / rel
        data = path.read_bytes()
        self.read_bytes += len(data)
        if self.read_bytes > MAX_READ_BYTES:
            raise RuntimeError(f"read budget exceeded: {self.read_bytes} > {MAX_READ_BYTES}")
        self.cache[rel] = data
        self.read_files.append(
            {
                "path": rel,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
        return data

    def read_json(self, rel: str) -> dict:
        return json.loads(self.read_bytes_file(rel).decode("utf-8"))


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def int_or_none(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def sum_known(values: list[object]) -> tuple[int, int]:
    known = [int_or_none(v) for v in values]
    known = [v for v in known if v is not None]
    return sum(known), len(values) - len(known)


def interval_summary(window: dict, *, include_counters: bool = True) -> dict:
    w = window.get("window") or {}
    result: dict[str, object] = {
        "kind": window.get("kind") or "accepted_index_window",
        "status": window.get("status"),
        "from": w.get("from"),
        "to": w.get("to"),
        "complete_prefix_evidence": window.get("complete_prefix_evidence"),
    }
    if include_counters:
        for key in (
            "index_rows",
            "image_index_rows",
            "direct_entity_rows",
            "status200_image_rows",
            "nested_excluded_rows",
            "direct_exact_candidates",
            "direct_variant_candidates",
        ):
            if key in window:
                result[key] = window.get(key)
    return result


def path_kind(row: dict, source_directory: str) -> str:
    original = row.get("original") or row.get("url") or ""
    if not isinstance(original, str):
        return "non_image"
    path = urlsplit(original).path
    source_directory = source_directory or ""
    if not source_directory.startswith("/"):
        source_directory = "/" + source_directory
    rel = path[len(source_directory) :] if path.startswith(source_directory) else None
    mime = str(row.get("mimetype") or "").lower()
    is_image = mime.startswith("image/") or mime == "warc/revisit"
    if rel is not None and NATIVE_FULL_RE.fullmatch(rel):
        return "native_full"
    if rel is not None and NATIVE_THUMB_RE.fullmatch(rel):
        return "native_thumb"
    if rel is not None and rel.lower().startswith("thumbs/"):
        if is_image or rel.lower().endswith(IMAGE_EXTENSIONS):
            return "nested_preview"
    if is_image or (rel is not None and rel.lower().endswith(IMAGE_EXTENSIONS)):
        return "other_image"
    return "non_image"


def classify_rows(rows: list[dict], source_directory: str) -> dict[str, object]:
    counts = {
        "native_full": 0,
        "native_thumb": 0,
        "nested_preview": 0,
        "nested_preview_image": 0,
        "nested_preview_revisit": 0,
        "other_image": 0,
        "non_image": 0,
    }
    for row in rows:
        kind = path_kind(row, source_directory)
        counts[kind] += 1
        if kind == "nested_preview":
            if str(row.get("mimetype") or "").lower() == "warc/revisit":
                counts["nested_preview_revisit"] += 1
            else:
                counts["nested_preview_image"] += 1
    return {
        "raw_index_rows": len(rows),
        "native_index_rows": counts["native_full"] + counts["native_thumb"],
        "native_full_index_rows": counts["native_full"],
        "native_thumb_index_rows": counts["native_thumb"],
        "nested_preview_rows": counts["nested_preview"],
        "nested_preview_image_rows": counts["nested_preview_image"],
        "nested_preview_revisit_rows": counts["nested_preview_revisit"],
        "other_image_rows": counts["other_image"],
        "non_image_rows": counts["non_image"],
    }


def accepted_late_rows(
    builder: AuditBuilder,
    acceptance: dict,
    gallery: str,
    source_directory: str,
) -> tuple[dict[str, object] | None, dict[str, object] | None]:
    """Return (classification, accepted metadata) for a result, if present."""
    result: dict | None = None
    if isinstance(acceptance.get("results"), list):
        result = next((x for x in acceptance["results"] if x.get("gallery") == gallery), None)
    elif isinstance(acceptance.get("results"), dict):
        result = acceptance["results"].get(gallery)
    if result is None:
        return None, None

    rows = result.get("rows") or []
    if not isinstance(rows, list):
        raise RuntimeError(f"unexpected rows for {gallery}")
    classification = classify_rows(rows, source_directory)
    provided_native = result.get("native_rows_all_schemes")
    if provided_native is None:
        provided_native = result.get("native_full_or_thumbnail_rows_all_schemes")
    provided_native_count = int_or_none(provided_native)
    if isinstance(provided_native, list):
        provided_native_count = len(provided_native)
    if provided_native_count is not None and provided_native_count != classification["native_index_rows"]:
        raise RuntimeError(
            f"native count mismatch for {gallery}: embedded={classification['native_index_rows']} "
            f"receipt={provided_native_count}"
        )

    body = result.get("raw_body_local")
    accepted_meta: dict[str, object] = {
        "source_result_complete": bool(result.get("complete_within_response", result.get("complete", False))),
        "receipt_row_count": result.get("row_count"),
        "receipt_native_rows": provided_native_count,
        "receipt_image_index_rows": result.get("image_index_rows"),
        "source_prefix": result.get("prefix"),
        "query_window": result.get("window") or result.get("query_window"),
    }
    classification.update(accepted_meta)
    if isinstance(body, dict):
        accepted_meta["raw_body_verified"] = True
    # Body bindings are verified in verify_raw_bodies; no local body path is published.
    return classification, accepted_meta


def verify_raw_bodies(builder: AuditBuilder, acceptances: list[tuple[str, dict]]) -> dict[str, object]:
    verified: list[dict[str, object]] = []
    seen: set[str] = set()
    for acceptance_path, acceptance in acceptances:
        for binding in acceptance.get("raw_body_bindings_local_only", []):
            rel = binding.get("path")
            if not isinstance(rel, str) or rel in seen:
                continue
            seen.add(rel)
            data = builder.read_bytes_file(rel)
            actual_sha = hashlib.sha256(data).hexdigest()
            expected_sha = binding.get("sha256")
            expected_bytes = int_or_none(binding.get("bytes"))
            if actual_sha != expected_sha or (expected_bytes is not None and len(data) != expected_bytes):
                raise RuntimeError(f"saved CDX body binding mismatch: {rel}")
            verified.append(
                {
                    "sha256": actual_sha,
                    "bytes": len(data),
                    "acceptance": acceptance_path,
                }
            )
    return {
        "unique_body_count": len(verified),
        "body_bytes_total": sum(int(x["bytes"]) for x in verified),
        "all_hashes_and_lengths_match": True,
        "raw_content_published": False,
        "acceptance_count": len(acceptances),
    }


def source_ref(path: str, role: str, *, sha256: str | None = None) -> dict[str, object]:
    result: dict[str, object] = {"path": path, "role": role}
    if sha256:
        result["sha256"] = sha256
    return result


def replay_observation(
    gallery: str,
    screenshot_items: dict[str, dict],
    karazhan_v3: dict,
) -> dict[str, object]:
    if gallery == "Karazhan":
        return {
            "evidence_status": "observed_stored_exact_native_replay",
            "full_404_count": 63,
            "thumb_404_count": 51,
            "observed_redirect_html_count": 1,
            "cdx_only_redirect_row_count": 11,
            "payload_200_count": 0,
            "observed_replay_request_count": 115,
            "actual_capture_timestamp": None,
            "deduplicated_probe_ids": ["karazhan_full"],
            "reconciliation": {
                "latest_gap01_native_karazhan_replay_counts": {
                    "full_404": 63,
                    "thumb_404": 51,
                    "late_301_html": 12,
                },
                "latest_gap01_redirect_scope": "Only ss1-thumb late2013 Location was observed; other11 have CDX301 evidence only.",
                "older_v3_summary_target_count": karazhan_v3.get("target_count"),
                "older_v3_summary_counts_by_kind": karazhan_v3.get("counts_by_kind"),
                "older_v3_summary_late_cdx_rows": len(karazhan_v3.get("late_cdx_rows", [])),
                "interpretation": "The latest gap01 acceptance governs the split: 115 native replay responses (114 404 plus one observed redirect) and 11 CDX-only redirect rows; the older 126-row summary is retained as source context.",
            },
            "evidence_ref": GAP01,
            "summary_ref": KARAZHAN_V3,
        }
    if gallery == "Magister's Terrace":
        item = screenshot_items["magisters_full"]
        return {
            "evidence_status": "observed_stored_exact_native_replay",
            "full_404_count": 1,
            "thumb_404_count": 0,
            "observed_redirect_html_count": 0,
            "cdx_only_redirect_row_count": 0,
            "payload_200_count": 0,
            "observed_replay_request_count": 1,
            "actual_capture_timestamp": item.get("actual_capture_timestamp"),
            "requested_timestamp": item.get("requested_timestamp"),
            "body_sha256": item.get("sha256"),
            "body_bytes": item.get("body_bytes"),
            "evidence_ref": SCREENSHOT_ACCEPTANCE,
            "secondary_ref": SCREENSHOT_DOC,
        }
    return {
        "evidence_status": "no_known_stored_exact_native_replay_in_audited_evidence",
        "full_404_count": None,
        "thumb_404_count": None,
        "observed_redirect_html_count": None,
        "cdx_only_redirect_row_count": None,
        "payload_200_count": None,
        "observed_replay_request_count": None,
        "actual_capture_timestamp": None,
    }


def main() -> int:
    builder = AuditBuilder()
    registry = builder.read_json(REGISTRY)
    ledger = builder.read_json(LEDGER)
    r3 = builder.read_json(R3)
    rest10a = builder.read_json(REST10A)
    rest10b = builder.read_json(REST10B)
    gap01 = builder.read_json(GAP01)
    karazhan_v3 = builder.read_json(KARAZHAN_V3)
    zul_prior = builder.read_json(ZUL_PRIOR)
    screenshot = builder.read_json(SCREENSHOT_ACCEPTANCE)

    if registry.get("stats", {}).get("gallery_count") != 50:
        raise RuntimeError("registry did not declare 50 galleries")
    if len(registry.get("coverage_rows", [])) != 50 or len(ledger.get("rows", [])) != 50 or len(r3.get("rows", [])) != 50:
        raise RuntimeError("one of the 50-gallery inputs is incomplete")
    if r3.get("summary", {}).get("park_count") != 21 or r3.get("summary", {}).get("open_count") != 29:
        raise RuntimeError("r3 park/open partition changed")
    if (
        karazhan_v3.get("target_count") != 126
        or (karazhan_v3.get("counts_by_kind") or {}).get("full", {}).get("archive_replay_404") != 63
        or (karazhan_v3.get("counts_by_kind") or {}).get("thumb", {}).get("archive_replay_404") != 51
        or (karazhan_v3.get("counts_by_kind") or {}).get("thumb", {}).get("observed_late_redirect_with_cdx_301_html") != 12
    ):
        raise RuntimeError("Karazhan v3 replay summary changed")

    # Verify every saved CDX body referenced by the accepted rest/gap receipts.
    body_verification = verify_raw_bodies(
        builder,
        [(REST10A, rest10a), (REST10B, rest10b), (GAP01, gap01)],
    )

    screenshot_items = {
        str(item.get("id")): item
        for item in screenshot.get("probe002_items", [])
        if isinstance(item, dict) and item.get("id")
    }
    magisters = screenshot_items.get("magisters_full")
    if not magisters or magisters.get("status") != 404 or magisters.get("actual_capture_timestamp") is not None:
        raise RuntimeError("accepted Magister's Terrace 404/null-capture evidence is missing")

    registry_rows = {x["gallery"]: x for x in registry["coverage_rows"]}
    ledger_rows = {x["gallery"]: x for x in ledger["rows"]}
    r3_rows = {x["gallery"]: x for x in r3["rows"]}

    late_acceptances = [
        (REST10A, rest10a),
        (REST10B, rest10b),
        (GAP01, gap01),
        (ZUL_PRIOR, zul_prior),
    ]
    late_result_map: dict[str, tuple[dict[str, object], str]] = {}
    # Keep the acceptance source mapping explicit and sanitized.
    for acceptance_path, acceptance in late_acceptances:
        if isinstance(acceptance.get("results"), list):
            for result in acceptance["results"]:
                gallery = result.get("gallery")
                if isinstance(gallery, str):
                    # Gap01/rest receipts supersede the older Zul-window
                    # receipt when a gallery appears in more than one source.
                    if gallery not in late_result_map:
                        late_result_map[gallery] = (acceptance, acceptance_path)
        elif isinstance(acceptance.get("results"), dict):
            for gallery in acceptance["results"]:
                if gallery not in late_result_map:
                    late_result_map[gallery] = (acceptance, acceptance_path)

    rows: list[dict[str, object]] = []
    for reg in sorted(registry["coverage_rows"], key=lambda x: x["registry_rank"]):
        gallery = reg["gallery"]
        late = ledger_rows[gallery]
        r3_row = r3_rows[gallery]
        source_evidence = reg.get("source_evidence") or {}
        source_directory = str(source_evidence.get("source_directory") or "")
        windows = reg.get("actual_prefix_windows") or []
        summarized_windows = [interval_summary(w) for w in windows]
        index_rows_known, index_rows_unknown = sum_known([w.get("index_rows") for w in windows])
        image_rows_known, image_rows_unknown = sum_known([w.get("image_index_rows") for w in windows])
        direct_rows, direct_rows_unknown = sum_known([w.get("direct_entity_rows") for w in windows])
        status200_rows, status200_unknown = sum_known([w.get("status200_image_rows") for w in windows])
        nested_rows, nested_unknown = sum_known([w.get("nested_excluded_rows") for w in windows])
        exact_rows, exact_unknown = sum_known([w.get("direct_exact_candidates") for w in windows])
        variant_rows, variant_unknown = sum_known([w.get("direct_variant_candidates") for w in windows])

        acceptance_ref: str | None = None
        late_evidence: dict[str, object] | None = None
        if gallery in late_result_map:
            acceptance, acceptance_ref = late_result_map[gallery]
            late_evidence, _ = accepted_late_rows(builder, acceptance, gallery, source_directory)

        late_status = late.get("late_status")
        if late_status == "complete":
            public_late_status = "covered_complete_index"
        elif late_status == "source_503":
            public_late_status = "source_503"
        elif late_status == "not_queried":
            public_late_status = "not_queried"
        else:
            public_late_status = str(late_status)

        uncovered = r3_row.get("uncovered_late_segments") or late.get("uncovered_late_segments") or []
        # All rows explicitly carry the post-2010-12-08 temporal gap. This is
        # an audit boundary, not a statement that no captures exist.
        temporal_unqueried = [
            {
                "from": POST_2010_FROM,
                "to": AUDIT_DATE_TO,
                "status": "unqueried",
                "meaning": "No late-window audit was run after 2010-12-07 through the current audit date.",
            }
        ]
        for segment in uncovered:
            temporal_unqueried.insert(
                0,
                {
                    "from": segment.get("from"),
                    "to": segment.get("to"),
                    "status": segment.get("status", "unqueried"),
                    "meaning": "Late-window segment remains open; prior source status is retained.",
                },
            )

        if public_late_status == "covered_complete_index":
            next_plan = [
                {
                    "from": POST_2010_FROM,
                    "to": AUDIT_DATE_TO,
                    "purpose": "post-2010-12-07 late-window coverage",
                }
            ]
        else:
            next_plan = [
                {
                    "from": segment.get("from"),
                    "to": segment.get("to"),
                    "purpose": "uncovered pre-2010-12-08 late-window segment",
                    "prior_status": segment.get("status", public_late_status),
                }
                for segment in uncovered
            ]
            next_plan.append(
                {
                    "from": POST_2010_FROM,
                    "to": AUDIT_DATE_TO,
                    "purpose": "post-2010-12-07 late-window coverage",
                }
            )

        refs = [
            source_ref(REGISTRY, "v7 gallery registry"),
            source_ref(LEDGER, "latest late-status ledger"),
            source_ref(R3, "r3 park/open correction"),
        ]
        if source_evidence.get("path"):
            refs.append(
                source_ref(
                    str(source_evidence["path"]),
                    "frozen source-page evidence",
                    sha256=source_evidence.get("sha256"),
                )
            )
        if acceptance_ref:
            refs.append(source_ref(acceptance_ref, "accepted late CDX source receipt"))
        replay = replay_observation(gallery, screenshot_items, karazhan_v3)
        if gallery == "Magister's Terrace":
            refs.extend(
                [
                    source_ref(SCREENSHOT_ACCEPTANCE, "accepted exact-native replay evidence"),
                    source_ref(SCREENSHOT_DOC, "sanitized replay evidence notes"),
                ]
            )
        if gallery == "Karazhan":
            refs.append(source_ref(KARAZHAN_V3, "prior accepted Karazhan replay summary"))

        row: dict[str, object] = {
            "registry_rank": reg["registry_rank"],
            "gallery": gallery,
            "category": reg.get("category"),
            "source_page_route": reg.get("source_page_route"),
            "source_directory": source_directory,
            "declared_slots": reg.get("declared_slots"),
            "native_target_count": 2 * int(reg.get("declared_slots", 0)),
            "legacy_v7_entity_status_counts_copied": reg.get("entity_audit_status_counts", {}),
            "legacy_v7_status_scope": "Copied v7 context only; not current replay status and not an all-time request ledger.",
            "pre_anchor_evidence": {
                "anchor": ANCHOR,
                "complete_prefix_intervals": summarized_windows,
                "registry_prewindow_gap": reg.get("prewindow_gap"),
                "coverage_status": reg.get("coverage_status"),
                "meaning": "Saved prefix/index intervals are bounded evidence; index rows are not payload recovery.",
            },
            "historical_registry_counters": {
                "index_rows_known": index_rows_known,
                "image_index_rows_known": image_rows_known,
                "direct_entity_rows_known": direct_rows,
                "status200_image_rows_known": status200_rows,
                "nested_excluded_rows_known": nested_rows,
                "direct_exact_candidates_known": exact_rows,
                "direct_variant_candidates_known": variant_rows,
                "windows_with_unknown_index_rows": index_rows_unknown,
                "windows_with_unknown_image_index_rows": image_rows_unknown,
                "windows_with_unknown_direct_entity_rows": direct_rows_unknown,
                "windows_with_unknown_status200_rows": status200_unknown,
                "windows_with_unknown_nested_rows": nested_unknown,
                "windows_with_unknown_exact_candidates": exact_unknown,
                "windows_with_unknown_variant_candidates": variant_unknown,
            },
            "late_window": {
                "from": (late.get("late_target_window") or {}).get("from"),
                "to": (late.get("late_target_window") or {}).get("to"),
                "anchor": (late.get("late_target_window") or {}).get("anchor", ANCHOR),
                "status": public_late_status,
                "decision": r3_row.get("decision"),
                "status_reason": late.get("status_reason") or r3_row.get("decision_reason"),
                "accepted_complete_interval": (
                    {"from": (late.get("late_target_window") or {}).get("from"), "to": LATE_TO}
                    if public_late_status == "covered_complete_index"
                    else None
                ),
                "raw_index_evidence": late_evidence,
                "index_rows_are_not_payloads": True,
            },
            "known_replay_observations": replay,
            "endpoint_or_transport_failure": (
                {
                    "status": "source_503",
                    "scope": uncovered,
                    "evidence_ref": acceptance_ref,
                    "meaning": "Endpoint/source failure; no native payload result.",
                }
                if public_late_status == "source_503"
                else None
            ),
            "temporal_unqueried_windows": temporal_unqueried,
            "next_query_plan": next_plan,
            "evidence_refs": refs,
        }
        rows.append(row)

    late_status_counts: dict[str, int] = {}
    for row in rows:
        status = row["late_window"]["status"]  # type: ignore[index]
        late_status_counts[status] = late_status_counts.get(status, 0) + 1
    if late_status_counts != {"covered_complete_index": 21, "source_503": 1, "not_queried": 28}:
        raise RuntimeError(f"unexpected late status partition: {late_status_counts}")

    legacy_totals: dict[str, int] = {}
    for reg in registry["coverage_rows"]:
        for key, value in (reg.get("entity_audit_status_counts") or {}).items():
            legacy_totals[key] = legacy_totals.get(key, 0) + int(value)
    expected_legacy = {"archive_404": 79, "transport_unknown": 47, "never_requested": 3242}
    if legacy_totals != expected_legacy:
        raise RuntimeError(f"legacy v7 totals changed: {legacy_totals}")

    late_native_total = sum(
        int((row["late_window"]["raw_index_evidence"] or {}).get("native_index_rows", 0))  # type: ignore[union-attr]
        for row in rows
    )
    if late_native_total != 0:
        raise RuntimeError(f"accepted late rows unexpectedly contain native rows: {late_native_total}")

    generated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    table = {
        "schema": "wow-recovery.gallery-accessibility-history-table.v1",
        "generated_utc": generated,
        "audit_date": AUDIT_DATE,
        "network_performed": False,
        "network_requests": 0,
        "index_empty": True,
        "index_semantics": "The public table contains no recovered image index; CDX rows are represented only as bounded counts.",
        "scope": {
            "gallery_count": 50,
            "native_targets": "source-declared ssN.jpg and ssN-thumb.jpg targets",
            "nested_previews_separate": True,
            "anchor": ANCHOR,
            "late_window_end": LATE_TO,
            "post_2010_window_explicitly_unqueried_through": AUDIT_DATE_TO,
        },
        "summary": {
            "gallery_count": len(rows),
            "late_status_counts": late_status_counts,
            "late_covered_group_count": late_status_counts["covered_complete_index"],
            "late_open_group_count": late_status_counts["source_503"] + late_status_counts["not_queried"],
            "late_native_index_rows": late_native_total,
            "legacy_v7_entity_status_totals_copied": legacy_totals,
            "known_exact_native_replay_gallery_count": 2,
            "known_exact_native_replay_payload_200_count": 0,
            "known_exact_native_replay_request_count": 116,
            "known_exact_native_replay_request_count_breakdown": {
                "Karazhan": 115,
                "Magister's Terrace": 1,
                "Karazhan_cdx_only_redirect_rows": 11,
            },
        },
        "limits": [
            "Complete prefix/index evidence is not all-time Wayback coverage.",
            "A CDX index row is not a payload and no index row was published here.",
            "A stored 404 applies to the requested URL/capture response; it does not establish absence at every date.",
            "Legacy v7 archive_404/transport_unknown/never_requested counts are copied context, not current replay outcomes.",
            "Observed replay, endpoint failure and unqueried windows remain separate categories.",
        ],
        "rows": rows,
    }

    # Deliberately do not emit an index file or a list of raw CDX rows.
    table_path = OUT / "gallery-availability-table.json"
    csv_path = OUT / "gallery-availability-table.csv"
    receipt_path = OUT / "history-audit-receipt.json"
    write_json(table_path, table)

    csv_fields = [
        "registry_rank",
        "gallery",
        "category",
        "source_page_route",
        "source_directory",
        "declared_slots",
        "native_target_count",
        "late_status",
        "late_from",
        "late_to",
        "late_raw_index_rows",
        "late_native_index_rows",
        "late_nested_preview_rows",
        "late_nested_preview_image_rows",
        "late_nested_preview_revisit_rows",
        "late_other_image_rows",
        "replay_evidence_status",
        "replay_full_404_count",
        "replay_thumb_404_count",
        "endpoint_failure_status",
        "unqueried_window_count",
        "next_query_plan",
        "evidence_refs",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=csv_fields)
        writer.writeheader()
        for row in rows:
            late_obj = row["late_window"]
            raw = late_obj.get("raw_index_evidence") or {}  # type: ignore[union-attr]
            replay = row["known_replay_observations"]
            writer.writerow(
                {
                    "registry_rank": row["registry_rank"],
                    "gallery": row["gallery"],
                    "category": row["category"],
                    "source_page_route": row["source_page_route"],
                    "source_directory": row["source_directory"],
                    "declared_slots": row["declared_slots"],
                    "native_target_count": row["native_target_count"],
                    "late_status": late_obj["status"],  # type: ignore[index]
                    "late_from": late_obj["from"],  # type: ignore[index]
                    "late_to": late_obj["to"],  # type: ignore[index]
                    "late_raw_index_rows": raw.get("raw_index_rows"),
                    "late_native_index_rows": raw.get("native_index_rows"),
                    "late_nested_preview_rows": raw.get("nested_preview_rows"),
                    "late_nested_preview_image_rows": raw.get("nested_preview_image_rows"),
                    "late_nested_preview_revisit_rows": raw.get("nested_preview_revisit_rows"),
                    "late_other_image_rows": raw.get("other_image_rows"),
                    "replay_evidence_status": replay.get("evidence_status"),
                    "replay_full_404_count": replay.get("full_404_count"),
                    "replay_thumb_404_count": replay.get("thumb_404_count"),
                    "endpoint_failure_status": (row["endpoint_or_transport_failure"] or {}).get("status"),
                    "unqueried_window_count": len(row["temporal_unqueried_windows"]),
                    "next_query_plan": json.dumps(row["next_query_plan"], ensure_ascii=False, separators=(",", ":")),
                    "evidence_refs": json.dumps(row["evidence_refs"], ensure_ascii=False, separators=(",", ":")),
                }
            )

    receipt = {
        "schema": "wow-recovery.gallery-accessibility-history-audit-receipt.v1",
        "generated_utc": generated,
        "audit_date": AUDIT_DATE,
        "network_performed": False,
        "network_requests": 0,
        "network_execution": "not performed",
        "index_empty": True,
        "outputs": {
            "table_json": str(table_path.relative_to(ROOT)).replace("\\", "/"),
            "table_csv": str(csv_path.relative_to(ROOT)).replace("\\", "/"),
            "raw_cdX_rows_published": False,
        },
        "counts": {
            "gallery_rows": len(rows),
            "late_covered_complete_index": late_status_counts["covered_complete_index"],
            "late_source_503": late_status_counts["source_503"],
            "late_not_queried": late_status_counts["not_queried"],
            "late_native_index_rows": late_native_total,
            "raw_body_bindings_verified": body_verification,
            "known_exact_native_replay_galleries": ["Karazhan", "Magister's Terrace"],
        },
        "legacy_v7_entity_status_totals_copied": legacy_totals,
        "source_inputs": builder.read_files,
        "read_bytes_total": builder.read_bytes,
        "read_budget_bytes": MAX_READ_BYTES,
        "validation": {
            "registry_and_ledgers_each_50": True,
            "park_open_partition_21_plus_29": True,
            "native_late_rows_all_covered_receipts_zero": True,
            "magisters_ss1_404_actual_capture_null": True,
            "karazhan_ss1_probe_deduplicated": True,
            "karazhan_latest_redirect_split_115_replays_plus_11_cdx_only": True,
            "post_2010_12_08_to_current_explicitly_unqueried_for_all_50": True,
            "raw_content_published": False,
        },
        "limits": table["limits"],
    }
    write_json(receipt_path, receipt)

    # A small human-readable boundary note is useful for reviewers and carries no raw rows.
    readme = OUT / "README.md"
    readme.write_text(
        "# 2026-10-20 gallery availability history\n\n"
        "`gallery-availability-table.json` and `.csv` reconcile the frozen v7 registry, "
        "the latest rest10b/r3 ledgers, and accepted local CDX receipts for all 50 galleries. "
        "The table has no public index rows. Native ssN full/thumb rows and nested preview rows "
        "are counted separately. Every gallery carries an explicit unqueried window from "
        "2010-12-08 through the 2026-10-20 audit-date bound. Network execution was not performed.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "rows": len(rows),
                "late_status_counts": late_status_counts,
                "late_native_index_rows": late_native_total,
                "read_bytes_total": builder.read_bytes,
                "raw_body_bindings_verified": body_verification["unique_body_count"],
                "outputs": [str(x.relative_to(ROOT)).replace("\\", "/") for x in (table_path, csv_path, receipt_path, readme)],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # keep failure explicit for bounded offline execution
        print(f"offline audit failed: {exc}", file=sys.stderr)
        raise
