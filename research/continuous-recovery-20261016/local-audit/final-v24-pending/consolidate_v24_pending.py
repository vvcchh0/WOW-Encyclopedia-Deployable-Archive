"""Offline v24 pending-resource consolidation.

This module reads frozen local acceptance records and the v24 export once.  It
does not make network requests, read raw response bodies, or modify any prior
batch.  The only writable location is this directory.
"""

from __future__ import annotations

import gzip
import hashlib
import importlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
RECOVERY = ROOT / "research" / "continuous-recovery-20261016"
PUB = RECOVERY / "publication"
SITE = ROOT / ".scratch" / "pages-resources-20261016-v24"
PRIVATE = OUT / "private"


EXPECTED = {
    "publication/root-v24-local-acceptance.json": "6ede038217c7e3a978dc82c2b6135580660546b9013e30883679cbae11c17282",
    "publication/root-v24-export-acceptance.json": "9f8e660e5220994a06088ca4de249ac950df49623f28a92199062b78af4b19c5",
    "publication/root-v24-static-metrics-acceptance.json": "f334d8176f8b776975394e3e9df351a0b5284858e2692e255b46df8da57f4cac",
    ".scratch/pages-resources-20261016-v24/export-provenance.json": "0d1a392e5be8f5eae71b8ca6bf73f5473331357c6f99f9ac60e79b6d07dec3d0",
    "local-audit/v2/gallery-direct-entity-audit-v2.json": "341435e62cfea8db4f1421d05c9e765e598ae4a31fb92d5702201c5308972a0a",
    "local-audit/gallery-final-v7/gallery-prefix-registry-v7.json": "2579f66841bf6102d90f5dbfe819902337bff03f6e3ac7191239ae041e2d97d6",
    "local-audit/gallery-neighbors/full-images20-candidates.json": "d7345075a288141d24bc7934a66cb4e1822c2cb0f89c80f7017d1fc4afaeb11c",
    "local-audit/gallery-neighbors/remaining20-candidates.json": "1670d7d7af8c7a9a28477469e70f7f0f3b76303ebca927164cc222e3e01aa6cf",
    "local-audit/gallery-neighbors/remaining9-candidates.json": "b9c7c9550eb65c6795803e6ada01ab55fe185d52f7dc57e7f3ddce193c64b745",
    "publication/root-gallery-neighbors-candidates-acceptance.json": "477d8b770330c57c32e7f784aad8ee2a6841376ad08e52aceaee63e1951e4a53",
    "publication/root-gallery-neighbors-remaining-candidates-acceptance.json": "eb5a2aadd7105df6335b4eb1c98445121a64a56179986955f28fd872148431f5",
    "integration/v23-neighbor-supplement-source-map-final40.json": "a41530972865b8b1d7413dd9a7d91d4555a770f0efa9848ee0ca2429ebee5030",
    "integration/v23-neighbor-supplement-catalog-map-final40.json": "ef5e6c9e4bdde5a08c248b35b3fd48849740e0714b3fb056100b4b6355b451b4",
    "publication/root-news-content02-source-acceptance.json": "01b3d1be19e1bafb60247f94a1405c41b362573889179a66a6ef4970fecc9a25",
    "publication/root-news-content03-source-acceptance.json": "cf36c2b1bfa153f47dc42b8fcfee5e1338c5a917e57902c94b72b080b9c7dd9a",
    "local-audit/v23-news-frontier/v23-news-frontier-summary.json": "b1d464cb6a9cb497970d55054e8025db4562fbb6cf86c2b3650a02fe30836109",
    "publication/root-news-content01-source-acceptance.json": "70deedfbc1cd0511c82e41dbd786f81224af8386a7bd1adb73160512bd965475",
    "local-audit/gallery-neighbor-guide-literals/gallery-neighbor-guide-literals-v1.json": "a0e76ea9fa7c9f7e4b4b5aa5f4ca3c3c0ed0e2d39f363906c8e19d18d2af026c",
    "local-audit/regional-image-supplement-map.proposal.json": "11c6e21a2e9b5a15b3ee7c10e097465c1b3ed646c24f130d8e1ea5be10d2f3c5",
    "local-audit/regional-image-supplement-plan.json": "367d0768465a42b02cfa425dde620e9f5aa9ec8dedd42b9ed6cff5c6a85d847b",
    "local-audit/regional-discovery/nested-preview-audit-v4.json": "9d35e2b2f9e60b850ee9a4344137e3d3eed779c26bcaf8adbd8459391e5c38fc",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def repo_path(relative: str) -> Path:
    # Recovery records are rooted under RECOVERY; the exported site and
    # repository-level tools use the repository root.  Keeping this explicit
    # prevents an accidental read from a similarly named root-level path.
    if relative.startswith((".scratch/", "offline/", "tools/")):
        return ROOT / Path(relative)
    return RECOVERY / Path(relative)


def load_json(relative: str) -> Any:
    return json.loads(repo_path(relative).read_text(encoding="utf-8"))


def binding(relative: str, role: str, expected: str | None = None) -> dict[str, Any]:
    path = repo_path(relative)
    assert path.is_file(), relative
    actual = sha256(path)
    if expected is not None:
        assert actual == expected, (relative, actual, expected)
    return {
        "path": relative.replace("\\", "/"),
        "sha256": actual,
        "bytes": path.stat().st_size,
        "role": role,
    }


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_scan() -> Any:
    # The accepted v24 wrapper imports the same pure scan implementation.  We
    # import it here without running either module's main function.
    sys.path.insert(0, str(PUB))
    module = importlib.import_module("accept_v23_static_metrics")
    return module.scan


def compact_neighbor_candidate(item: dict[str, Any]) -> dict[str, Any]:
    rows = item.get("positive_rows", [])
    return {
        "original": item["original"],
        "gallery_context": item.get("gallery_context"),
        "filename_class": item.get("filename_class"),
        "state": item.get("state"),
        "positive_capture_count": len(rows),
        "positive_capture_timestamps": [r.get("timestamp") for r in rows],
        "positive_digests": sorted({r.get("digest") for r in rows if r.get("digest")}),
        "relationship": item.get("relationship"),
    }


def compact_native_status(entity: dict[str, Any]) -> dict[str, Any]:
    # Keep the 3368-record ledger useful for reconciliation without copying
    # source-page quotes, HTML, headers, cookies, or payload bytes.
    return {
        "gallery": entity.get("gallery"),
        "category": entity.get("category"),
        "slot": entity.get("slot"),
        "kind": entity.get("kind"),
        "original_url": entity.get("original_url"),
        "status": entity.get("status"),
    }


def main() -> None:
    existing = [
        p for p in OUT.iterdir()
        if p.name != Path(__file__).name
        and not (p.name == "private" and p.is_dir() and not any(p.iterdir()))
    ]
    if existing:
        raise RuntimeError(f"refusing to overwrite existing output: {existing}")
    PRIVATE.mkdir(parents=False, exist_ok=True)

    # Bind the accepted v24 local result and its static/provenance evidence.
    v24_acceptance_path = "publication/root-v24-local-acceptance.json"
    v24_acceptance = load_json(v24_acceptance_path)
    assert v24_acceptance["accepted"] is True
    assert v24_acceptance["network_requests"] == 0
    v24_acceptance_binding = binding(v24_acceptance_path, "root accepted v24 local export", EXPECTED[v24_acceptance_path])
    export_acceptance_path = "publication/root-v24-export-acceptance.json"
    export_acceptance = load_json(export_acceptance_path)
    assert export_acceptance["accepted"] is True and export_acceptance["network_requests"] == 0
    export_binding = binding(export_acceptance_path, "root accepted v24 export", EXPECTED[export_acceptance_path])
    metrics_path = "publication/root-v24-static-metrics-acceptance.json"
    metrics = load_json(metrics_path)
    assert metrics["accepted"] is True
    assert metrics["static_text_files"] == 1104
    assert metrics["current_unique_missing_images"] == 1181
    assert metrics["current_missing_occurrences"] == 1942
    assert metrics["current_news_missing_occurrences"] == 557
    assert metrics["current_news_unique_missing_images"] == 551
    metrics_binding = binding(metrics_path, "root accepted static metrics", EXPECTED[metrics_path])
    provenance_path = ".scratch/pages-resources-20261016-v24/export-provenance.json"
    provenance_binding = binding(provenance_path, "v24 export provenance", EXPECTED[provenance_path])

    # Exactly one pure scan call for this consolidation run.
    scan = load_scan()
    files, counter, news, allmarkers = scan(SITE)
    assert len(files) == 1104
    assert len(counter) == 1181
    assert sum(counter.values()) == 1942
    assert sum(news.values()) == 557
    assert len(news) == 551

    counter_payload = {
        "schema": "wow-recovery.local-audit.final-v24.pending.static-counter.private.v1",
        "generated_utc": now_utc(),
        "visibility": "local-private",
        "scope": {
            "site": v24_acceptance["local_site"],
            "static_files": len(files),
            "excluded_prefixes": ["_origins/"],
            "included_suffixes": [".html", ".htm", ".xml", ".css"],
            "raw_html_copied": False,
            "raw_headers_copied": False,
            "cookies_copied": False,
        },
        "counts": {
            "static_files": len(files),
            "unique_missing_images": len(counter),
            "missing_occurrences": sum(counter.values()),
            "news_unique_missing_images": len(news),
            "news_missing_occurrences": sum(news.values()),
            "all_placeholder_markers": allmarkers,
        },
        "counter": {k: counter[k] for k in sorted(counter)},
        "news_counter": {k: news[k] for k in sorted(news)},
    }
    counter_path = PRIVATE / "static-missing-counter.json.gz"
    with counter_path.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as gz:
            gz.write(json.dumps(counter_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))

    # Keep native JavaScript gallery entities separate from static placeholder
    # counts.  The ledger has statuses only; no source-page text is copied.
    audit_path = "local-audit/v2/gallery-direct-entity-audit-v2.json"
    audit = load_json(audit_path)
    assert audit["entity_count"] == 3368
    assert audit["status_counts"] == {"archive_404": 79, "never_requested": 3242, "transport_unknown": 47}
    status_records = [compact_native_status(e) for e in audit["entities"]]
    assert len(status_records) == 3368
    status_counts = Counter(r["status"] for r in status_records)
    assert dict(status_counts) == {"archive_404": 79, "never_requested": 3242, "transport_unknown": 47}
    native_status_path = OUT / "native-gallery-statuses.json"
    write_json(native_status_path, {
        "schema": "wow-recovery.local-audit.final-v24.pending.native-gallery-statuses.v1",
        "generated_utc": now_utc(),
        "visibility": "clean-local-status-ledger",
        "source_classification": "native dynamic gallery entities; status is preserved as audited",
        "source_binding": binding(audit_path, "native gallery entity audit", EXPECTED[audit_path]),
        "entity_count": len(status_records),
        "status_counts": dict(sorted(status_counts.items())),
        "records": status_records,
    })

    # Validate the final gallery registry's index-window claims separately from
    # its payload-status ledger.  A complete CDX window remains index evidence.
    registry_path = "local-audit/gallery-final-v7/gallery-prefix-registry-v7.json"
    registry = load_json(registry_path)
    stats = registry["stats"]
    assert stats["gallery_count"] == 50
    assert stats["full_window_complete_groups"] == 50
    assert stats["full_window_incomplete_or_unknown_groups"] == 0
    assert stats["full_window_partition"]["global_complete_groups"] == 50
    assert stats["full_window_partition"]["index_rows_are_not_payloads"] is True
    registry_binding = binding(registry_path, "accepted 50 full-window CDX registry", EXPECTED[registry_path])

    # Reconcile the 49 positive neighboring originals against the 40 already
    # accepted supplement/catalog entries.  This is set arithmetic only.
    candidate_paths = [
        "local-audit/gallery-neighbors/full-images20-candidates.json",
        "local-audit/gallery-neighbors/remaining20-candidates.json",
        "local-audit/gallery-neighbors/remaining9-candidates.json",
    ]
    candidate_data = [load_json(p) for p in candidate_paths]
    candidates = [item for data in candidate_data for item in data["candidates"]]
    assert [len(data["candidates"]) for data in candidate_data] == [20, 20, 9]
    candidate_by_original = {item["original"]: item for item in candidates}
    assert len(candidate_by_original) == 49
    map_paths = [
        "integration/v23-neighbor-supplement-source-map-final40.json",
        "integration/v23-neighbor-supplement-catalog-map-final40.json",
    ]
    accepted_items = [item for path in map_paths for item in load_json(path)["items"]]
    accepted_originals = {item["original"] for item in accepted_items}
    assert len(accepted_items) == 40 and len(accepted_originals) == 40
    assert accepted_originals <= set(candidate_by_original)
    pending_neighbors = [candidate_by_original[o] for o in sorted(set(candidate_by_original) - accepted_originals)]
    assert len(pending_neighbors) == 9
    assert sum(1 for item in pending_neighbors if item.get("filename_class") == "full") == 7
    assert sum(1 for item in pending_neighbors if item.get("filename_class") != "full") == 2
    compact_pending_neighbors = [compact_neighbor_candidate(item) for item in pending_neighbors]

    neighbor_acceptance_path = "publication/root-gallery-neighbors-candidates-acceptance.json"
    neighbor_remaining_acceptance_path = "publication/root-gallery-neighbors-remaining-candidates-acceptance.json"
    neighbor_acceptance = load_json(neighbor_acceptance_path)
    neighbor_remaining_acceptance = load_json(neighbor_remaining_acceptance_path)
    assert neighbor_acceptance["accepted"] and neighbor_acceptance["positive_not_local"] == 49
    assert neighbor_acceptance["fresh_exact_candidates"] == 20
    assert neighbor_remaining_acceptance["accepted"]
    assert neighbor_remaining_acceptance["all49_distinct_originals_conserved"] is True

    # Bind news outcomes and retain only the three final transport/HTTP
    # unknowns from CONTENT03.  Cached-index rows that did not yield a payload
    # are not promoted into the remaining-unknown list.
    content02_acceptance_path = "publication/root-news-content02-source-acceptance.json"
    content03_acceptance_path = "publication/root-news-content03-source-acceptance.json"
    content02_acceptance = load_json(content02_acceptance_path)
    content03_acceptance = load_json(content03_acceptance_path)
    assert content02_acceptance["accepted"] and content03_acceptance["accepted"]
    content02_plan_path = "network/news-content02/plan.json"
    content03_plan_path = "network/news-content03/plan.json"
    content02_report_path = "network/news-content02/output/batch-report.json"
    content03_report_path = "network/news-content03/output/batch-report.json"
    content02_plan = load_json(content02_plan_path)
    content03_plan = load_json(content03_plan_path)
    content02_report = load_json(content02_report_path)
    content03_report = load_json(content03_report_path)
    assert sha256(repo_path(content02_plan_path)) == content02_acceptance["plan_sha256"]
    assert sha256(repo_path(content03_plan_path)) == content03_acceptance["plan_sha256"]
    assert sha256(repo_path(content02_report_path)) == content02_acceptance["batch_report_sha256"]
    assert sha256(repo_path(content03_report_path)) == content03_acceptance["batch_report_sha256"]
    unknown_targets = []
    for candidate, result in zip(content03_plan["candidates"], content03_report["results"]):
        if result.get("status") == "transport_or_http_unknown":
            unknown_targets.append({
                "rank": candidate["rank"],
                "target_key": candidate["target_key"],
                "original": candidate["original"],
                "classification": "transport_or_http_unknown",
                "cdx_mode": candidate["cdx_mode"],
                "retry_of": candidate["retry_of"],
            })
    assert [item["rank"] for item in unknown_targets] == [13, 14, 18]

    content01_summary_path = "local-audit/v23-news-frontier/v23-news-frontier-summary.json"
    content01_summary = load_json(content01_summary_path)
    assert content01_summary["content01_outcome_summary"]["transport_or_http_unknown_count"] == 8
    content01_acceptance_path = "publication/root-news-content01-source-acceptance.json"
    content01_acceptance = load_json(content01_acceptance_path)
    assert content01_acceptance["accepted"]
    content01_queue_path = "local-audit/v20-news-content20/v20-news-content20-public-candidates.json"
    content01_queue_sha256 = sha256(repo_path(content01_queue_path))
    assert content01_queue_sha256 == "11bbeec9ddf2b7d0f14bf0e8399d81674354c35623dbbf53d7d466d5841900c4"

    generated = now_utc()
    source_bindings = [
        v24_acceptance_binding,
        export_binding,
        metrics_binding,
        provenance_binding,
        registry_binding,
        binding(audit_path, "native gallery status source", EXPECTED[audit_path]),
        binding(neighbor_acceptance_path, "neighbor candidate acceptance", EXPECTED[neighbor_acceptance_path]),
        binding(neighbor_remaining_acceptance_path, "neighbor remaining queue acceptance", EXPECTED[neighbor_remaining_acceptance_path]),
    ]
    source_bindings.extend(
        binding(path, "neighbor positive source queue") for path in candidate_paths
    )
    source_bindings.extend(
        binding(path, "accepted neighbor payload map") for path in map_paths
    )
    source_bindings.extend([
        binding(content02_acceptance_path, "CONTENT02 accepted source receipt", EXPECTED[content02_acceptance_path]),
        binding(content03_acceptance_path, "CONTENT03 accepted source receipt", EXPECTED[content03_acceptance_path]),
        binding(content02_plan_path, "CONTENT02 frozen source queue"),
        binding(content03_plan_path, "CONTENT03 frozen retry queue"),
        binding(content02_report_path, "CONTENT02 sanitized batch report"),
        binding(content03_report_path, "CONTENT03 sanitized batch report"),
        binding(content01_summary_path, "CONTENT01 unknown-count summary", EXPECTED[content01_summary_path]),
        binding(content01_acceptance_path, "CONTENT01 accepted source receipt", EXPECTED[content01_acceptance_path]),
        binding("local-audit/v20-news-content20/v20-news-content20-public-candidates.json", "CONTENT01 source queue"),
        binding("publication/root-news-content20-candidates-acceptance.json", "CONTENT01 source queue acceptance"),
        binding("local-audit/gallery-neighbor-guide-literals/gallery-neighbor-guide-literals-v1.json", "static guide literal queue", EXPECTED["local-audit/gallery-neighbor-guide-literals/gallery-neighbor-guide-literals-v1.json"]),
        binding("local-audit/regional-image-supplement-map.proposal.json", "regional static supplement pointer", EXPECTED["local-audit/regional-image-supplement-map.proposal.json"]),
        binding("local-audit/regional-image-supplement-plan.json", "regional static supplement plan pointer", EXPECTED["local-audit/regional-image-supplement-plan.json"]),
        binding("local-audit/regional-discovery/nested-preview-audit-v4.json", "regional nested preview pointer", EXPECTED["local-audit/regional-discovery/nested-preview-audit-v4.json"]),
        binding("local-audit/eu-dependencies/eu-dependencies-public-candidates-v1.json", "EU literal queue pointer"),
        binding("local-audit/eu-dependencies/eu-dependencies-public-summary-v1.json", "EU public summary pointer"),
        binding("local-audit/eu-navigation-wave2/eu-navigation-wave2-public-summary-v1.json", "EU navigation queue pointer"),
    ])

    counter_artifact = {
        "path": "private/static-missing-counter.json.gz",
        "sha256": sha256(counter_path),
        "bytes": counter_path.stat().st_size,
        "classification": "local-private static counter; no raw source copied",
    }
    status_artifact = {
        "path": "native-gallery-statuses.json",
        "sha256": sha256(native_status_path),
        "bytes": native_status_path.stat().st_size,
        "classification": "clean status ledger for 3368 dynamic gallery entities",
    }
    script_binding = {
        "path": "local-audit/final-v24-pending/consolidate_v24_pending.py",
        "sha256": sha256(Path(__file__)),
        "bytes": Path(__file__).stat().st_size,
        "role": "reproducible offline consolidation script",
    }

    summary = {
        "schema": "wow-recovery.local-audit.final-v24.pending.summary.v1",
        "generated_utc": generated,
        "phase": "acquisition_closed_offline_consolidation",
        "network_requests": 0,
        "git_performed": False,
        "source_provenance": {
            "site": v24_acceptance["local_site"],
            "provenance_sha256": provenance_binding["sha256"],
            "root_local_acceptance_sha256": v24_acceptance_binding["sha256"],
            "root_local_acceptance_checked_utc": v24_acceptance["checked_utc"],
        },
        "file_resource_counts": {
            "site": {
                "declared_files": v24_acceptance["declared_files"],
                "actual_files": v24_acceptance["actual_files"],
                "tree_bytes": v24_acceptance["tree_bytes"],
                "source_records": export_acceptance["stats"]["source_records"],
            },
            "static": {
                "scanned_files": len(files),
                "unique_missing_image_entities": len(counter),
                "missing_image_references": sum(counter.values()),
                "news_unique_missing_image_entities": len(news),
                "news_missing_image_references": sum(news.values()),
                "placeholder_markers": allmarkers,
                "scope": "1104 HTML/HTM/XML/CSS files excluding _origins/",
            },
            "dynamic_gallery": {
                "native_entities": len(status_records),
                "status_counts": dict(sorted(status_counts.items())),
                "complete_cdx_windows": stats["full_window_complete_groups"],
                "scope": "3368 JavaScript gallery entities kept separate from static files",
            },
        },
        "accepted_v24_new_source_data": {
            "image_count": v24_acceptance["new_images"],
            "image_bytes": v24_acceptance["new_image_bytes"],
            "remaining_news_missing_references": v24_acceptance["remaining_news_missing_references"],
            "classification": "source data accepted locally; deployment claim is absent",
        },
        "classification_rules": [
            "A complete CDX window is index evidence and does not imply a recovered payload.",
            "Index absence is preserved as unknown or never_requested and is never converted to archive_404.",
            "Neighbor originals preserve exact scheme, host, port, and path; no dynamic-gallery alias is inferred.",
            "Native gallery status counts remain archive_404=79, transport_unknown=47, never_requested=3242.",
            "Public artifacts contain no source HTML, raw headers, cookies, or response-body text.",
        ],
        "pending_priorities": {
            "gallery_neighbors": {
                "classification": "positive_index_not_local",
                "count": len(compact_pending_neighbors),
                "accepted_subtracted_from": 49,
                "accepted_payloads_subtracted": 40,
                "items": compact_pending_neighbors,
                "queue_status": "deferred_after_acquisition_closure; no acquisition started",
                "source_queue_sha256": [binding(path, "neighbor source queue", EXPECTED[path])["sha256"] for path in candidate_paths],
                "acceptance_receipt_sha256": [
                    sha256(repo_path(neighbor_acceptance_path)),
                    sha256(repo_path(neighbor_remaining_acceptance_path)),
                ],
            },
            "news_content02_03": {
                "classification": "transport_or_http_unknown after frozen CONTENT02/03 runs",
                "count": len(unknown_targets),
                "items": unknown_targets,
                "queue_status": "deferred_after_acquisition_closure; no retry/control started",
                "content02_acceptance_sha256": sha256(repo_path(content02_acceptance_path)),
                "content03_acceptance_sha256": sha256(repo_path(content03_acceptance_path)),
                "content03_plan_sha256": sha256(repo_path(content03_plan_path)),
                "content03_report_sha256": sha256(repo_path(content03_report_path)),
            },
            "news_content01": {
                "classification": "transport_or_http_unknown in older CONTENT01 queue",
                "count": content01_summary["content01_outcome_summary"]["transport_or_http_unknown_count"],
                "queue_status": "pointer only; no acquisition started",
                "candidate_queue_path": "local-audit/v20-news-content20/v20-news-content20-public-candidates.json",
                "candidate_queue_sha256": content01_queue_sha256,
                "summary_sha256": sha256(repo_path(content01_summary_path)),
                "acceptance_receipt_sha256": sha256(repo_path(content01_acceptance_path)),
            },
            "static_and_eu": {
                "classification": "related static/EU literal queues; pointers only",
                "queue_status": "no acquisition started",
                "pointers": [
                    "local-audit/gallery-neighbor-guide-literals/gallery-neighbor-guide-literals-v1.json",
                    "local-audit/regional-image-supplement-map.proposal.json",
                    "local-audit/regional-image-supplement-plan.json",
                    "local-audit/regional-discovery/nested-preview-audit-v4.json",
                    "local-audit/eu-dependencies/eu-dependencies-public-candidates-v1.json",
                    "local-audit/eu-dependencies/eu-dependencies-public-summary-v1.json",
                    "local-audit/eu-navigation-wave2/eu-navigation-wave2-public-summary-v1.json",
                ],
            },
        },
        "artifacts": {
            "private_static_counter": counter_artifact,
            "native_gallery_statuses": status_artifact,
            "script": script_binding,
        },
        "source_bindings": source_bindings,
    }

    markdown = f"""# v24 pending-resource consolidation

Generated `{generated}` from accepted local evidence. This consolidation performed **0 network requests** and no Git operation.

## Counts

- Site: `{v24_acceptance['declared_files']}` declared files, `{v24_acceptance['actual_files']}` actual files, `{v24_acceptance['tree_bytes']}` bytes.
- Static scope: `{len(files)}` HTML/HTM/XML/CSS files, excluding `_origins/`; `{len(counter)}` unique missing-image entities and `{sum(counter.values())}` references. News contributes `{len(news)}` unique entities and `{sum(news.values())}` references.
- Dynamic gallery scope: `{len(status_records)}` native entities with statuses `archive_404=79`, `transport_unknown=47`, `never_requested=3242`.
- Gallery index evidence: `50` complete CDX windows; these rows remain index evidence and are not payload recovery.

The complete static counter is in the local-private artifact [`private/static-missing-counter.json.gz`](private/static-missing-counter.json.gz). The separate native status ledger is [`native-gallery-statuses.json`](native-gallery-statuses.json).

## Deferred priorities

1. **Nine positive neighboring originals remain without accepted local payloads** after subtracting 40 accepted resources from 49 exact candidates. They are seven numeric full images and two model/dress resources. Their exact origins, scheme, host, port, and path are preserved in `public-summary.json`; these are positive CDX rows only and were not acquired in this closed phase.
2. **NEWS-CONTENT02/03 retains three transport/HTTP unknowns:** ranks 13, 14, and 18, with exact originals in `public-summary.json`. They remain deferred after acquisition closure.
3. **Older CONTENT01 retains eight transport/HTTP unknowns.** The frozen queue, summary, and acceptance receipt are bound in `public-summary.json`; no raw response material is copied here.
4. Static and EU literal queues are retained as pointers only. No new acquisition is proposed or started.

The classifications preserve the evidence boundary: index absence is not converted to `archive_404`, and source-data acceptance does not make a deployment claim.
"""
    markdown_path = OUT / "public-summary.md"
    markdown_path.write_text(markdown, encoding="utf-8")
    summary_path = OUT / "public-summary.json"
    write_json(summary_path, summary)

    manifest = {
        "schema": "wow-recovery.local-audit.final-v24.pending.artifacts.v1",
        "generated_utc": now_utc(),
        "network_requests": 0,
        "artifacts": [
            {"path": p.relative_to(OUT).as_posix(), "sha256": sha256(p), "bytes": p.stat().st_size}
            for p in (Path(__file__), counter_path, native_status_path, markdown_path, summary_path)
        ],
    }
    write_json(OUT / "artifacts.json", manifest)
    print(json.dumps({
        "scan_once": True,
        "static_files": len(files),
        "static_unique": len(counter),
        "static_refs": sum(counter.values()),
        "news_unique": len(news),
        "news_refs": sum(news.values()),
        "native_entities": len(status_records),
        "native_status_counts": dict(sorted(status_counts.items())),
        "neighbor_pending": len(pending_neighbors),
        "news_unknown": [item["rank"] for item in unknown_targets],
        "output": str(OUT),
        "artifacts": manifest["artifacts"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
