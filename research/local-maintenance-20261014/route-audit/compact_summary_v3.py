"""Compact the saved v3 route-audit details without reading the source tree.

The v3 scan's full summary is retained byte-for-byte in a gzip archive.  This
script only reads that saved JSON, derives an exact requested-target index from
placeholder query fields, and replaces the human-facing summary with bounded
statistics and evidence examples.
"""

from __future__ import annotations

import copy
import gzip
import hashlib
import json
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_DIR = ROOT / "research/local-maintenance-20261014/route-audit"
SUMMARY_PATH = AUDIT_DIR / "summary.json"
MARKDOWN_PATH = AUDIT_DIR / "summary.md"
ARCHIVE_PATH = AUDIT_DIR / "details-v3.json.gz"
MAX_EXAMPLES_PER_CLASS = 20
MAX_TOTAL_EXAMPLES = 100


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def first_query_value(raw: str, name: str) -> str | None:
    try:
        query = urllib.parse.urlsplit(raw).query
        values = urllib.parse.parse_qs(query, keep_blank_values=True).get(name, [])
    except ValueError:
        return None
    if not values:
        return None
    return values[0]


def strip_fragment(value: str) -> str:
    # Keep the decoded requested scheme, host, path, and query exactly as
    # supplied by the saved placeholder; only the fragment is excluded.
    return value.split("#", 1)[0]


def host_scope(target: str) -> str:
    try:
        hostname = (urllib.parse.urlsplit(target).hostname or "").casefold().rstrip(".")
    except ValueError:
        hostname = ""
    if not hostname:
        return "relative_or_non_url"
    if hostname in {"www.worldofwarcraft.com", "worldofwarcraft.com"}:
        return "primary_worldofwarcraft_host"
    return "external_host"


def compact_group(group: dict[str, Any], *, include_requested: bool = True) -> dict[str, Any]:
    raw = str(group.get("raw") or "")
    requested = first_query_value(raw, "requested") if include_requested else None
    item: dict[str, Any] = {
        "classification": group.get("classification"),
        "raw": raw,
        "missing_reason": group.get("missing_reason"),
        "occurrences": int(group.get("occurrences") or 0),
        "pages": int(group.get("pages") or 0),
    }
    if requested:
        item["requested"] = strip_fragment(requested)
    examples: list[dict[str, Any]] = []
    for example in group.get("examples") or []:
        examples.append(
            {
                key: example.get(key)
                for key in ("page", "line", "context", "raw")
                if key in example
            }
        )
        if len(examples) >= 3:
            break
    if examples:
        item["examples"] = examples
    return item


def compact_summary(old: dict[str, Any], old_bytes: bytes, archive_bytes: bytes) -> dict[str, Any]:
    groups = old.get("missing_assets") or []
    target_data: dict[str, dict[str, Any]] = {}
    by_classification: dict[str, dict[str, int]] = defaultdict(lambda: {"unique": 0, "occurrences": 0})
    by_host_scope: dict[str, dict[str, int]] = defaultdict(lambda: {"unique": 0, "occurrences": 0})
    by_reason: Counter[str] = Counter()
    missing_requested_groups = 0
    missing_requested_occurrences = 0
    requested_field_occurrences = 0
    multiple_requested_field_groups = 0
    no_requested_groups = 0
    no_requested_occurrences = 0
    no_requested_by_class: dict[str, dict[str, int]] = defaultdict(lambda: {"groups": 0, "occurrences": 0})
    all_requested_refs: list[dict[str, Any]] = []

    for group in groups:
        classification = str(group.get("classification") or "unknown")
        occurrences = int(group.get("occurrences") or 0)
        raw = str(group.get("raw") or "")
        try:
            values = urllib.parse.parse_qs(urllib.parse.urlsplit(raw).query, keep_blank_values=True).get("requested", [])
        except ValueError:
            values = []
        values = [strip_fragment(value) for value in values if value]
        if len(values) > 1:
            multiple_requested_field_groups += 1
        if not values:
            no_requested_groups += 1
            no_requested_occurrences += occurrences
            no_requested_by_class[classification]["groups"] += 1
            no_requested_by_class[classification]["occurrences"] += occurrences
            continue
        # The exporter emits one requested field per placeholder.  If a saved
        # row contains several, retain each exact field while assigning the
        # row's occurrence weight to the first field and one diagnostic count
        # for the extra fields.
        requested_field_occurrences += occurrences
        for value_index, target in enumerate(values):
            record = target_data.setdefault(
                target,
                {
                    "target": target,
                    "occurrences": 0,
                    "source_group_count": 0,
                    "classifications": Counter(),
                    "host_scopes": Counter(),
                    "reasons": Counter(),
                    "references": [],
                },
            )
            weight = occurrences if value_index == 0 else 0
            record["occurrences"] += weight
            record["source_group_count"] += 1
            record["classifications"][classification] += 1
            scope = host_scope(target)
            record["host_scopes"][scope] += 1
            reason = first_query_value(raw, "reason") or str(group.get("missing_reason") or "unspecified")
            record["reasons"][reason] += 1
            if value_index == 0:
                for example in group.get("examples") or []:
                    if len(record["references"]) >= 3:
                        break
                    record["references"].append(
                        {
                            key: example.get(key)
                            for key in ("page", "line", "context", "raw")
                            if key in example
                        }
                    )
                all_requested_refs.extend(record["references"][-3:])
        # Classification/host/reason counters are target-index counters.  A
        # target that appears under two raw groups is still one exact target.

    for target, record in target_data.items():
        record["classifications"] = dict(sorted(record["classifications"].items()))
        record["host_scopes"] = dict(sorted(record["host_scopes"].items()))
        record["reasons"] = dict(sorted(record["reasons"].items()))
        record["host_scope"] = max(record["host_scopes"], key=record["host_scopes"].get)
        record["references"] = record["references"][:3]
        by_host_scope[record["host_scope"]]["unique"] += 1
        by_host_scope[record["host_scope"]]["occurrences"] += int(record["occurrences"])
        for classification, count in record["classifications"].items():
            by_classification[classification]["unique"] += 1
            by_classification[classification]["occurrences"] += int(record["occurrences"]) if count else 0
        for reason, count in record["reasons"].items():
            by_reason[reason] += int(record["occurrences"]) if count else 0
        missing_requested_groups += int(record["source_group_count"])
        missing_requested_occurrences += int(record["occurrences"])

    def target_view(record: dict[str, Any]) -> dict[str, Any]:
        return {
            "target": record["target"],
            "occurrences": record["occurrences"],
            "source_group_count": record["source_group_count"],
            "host_scope": record["host_scope"],
            "classifications": record["classifications"],
            "reasons": record["reasons"],
            "references": record["references"],
        }

    def category_target_view(record: dict[str, Any]) -> dict[str, Any]:
        # Keep the per-class examples independently auditable while avoiding a
        # second copy of the larger reference samples retained by top targets.
        return {
            "target": record["target"],
            "occurrences": record["occurrences"],
            "source_group_count": record["source_group_count"],
            "host_scope": record["host_scope"],
            "classifications": record["classifications"],
        }

    ordered_targets = sorted(target_data.values(), key=lambda item: (-int(item["occurrences"]), item["target"]))
    top_targets = [target_view(item) for item in ordered_targets[:MAX_EXAMPLES_PER_CLASS]]
    examples_by_class: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in ordered_targets:
        for classification in item["classifications"]:
            if len(examples_by_class[classification]) < MAX_EXAMPLES_PER_CLASS:
                examples_by_class[classification].append(category_target_view(item))

    old_scan = copy.deepcopy(old.get("scan") or {})
    old_scan.update(
        {
            "requested_target_unique_count": len(target_data),
            "requested_target_occurrences": requested_field_occurrences,
            "requested_target_occurrences_counted": missing_requested_occurrences,
            "requested_target_groups": missing_requested_groups,
            "requested_target_groups_without_field": no_requested_groups,
        }
    )
    # The first and second occurrence totals differ only if a malformed saved
    # row carried multiple requested fields; expose that condition explicitly.
    old_scan["requested_target_multiple_field_groups"] = multiple_requested_field_groups

    compact_missing: dict[str, Any] = {
        "group_count": len(groups),
        "occurrence_count": sum(int(group.get("occurrences") or 0) for group in groups),
        "classification_counts": {},
        "examples_by_classification": {},
    }
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for group in groups:
        classification = str(group.get("classification") or "unknown")
        compact_missing["classification_counts"].setdefault(classification, {"groups": 0, "occurrences": 0})
        compact_missing["classification_counts"][classification]["groups"] += 1
        compact_missing["classification_counts"][classification]["occurrences"] += int(group.get("occurrences") or 0)
        if len(grouped[classification]) < MAX_EXAMPLES_PER_CLASS:
            grouped[classification].append(compact_group(group))
    compact_missing["examples_by_classification"] = dict(grouped)

    archive = {
        "path": str(ARCHIVE_PATH.relative_to(ROOT).as_posix()),
        "source_bytes": len(old_bytes),
        "source_sha256": sha256_bytes(old_bytes),
        "gzip_bytes": len(archive_bytes),
        "gzip_sha256": sha256_bytes(archive_bytes),
        "decompresses_byte_exact": True,
    }

    result: dict[str, Any] = {
        "schema": "local-route-audit/v1-compact",
        "source_schema": old.get("schema"),
        "generated_at": old.get("generated_at"),
        "offline_only": old.get("offline_only"),
        "inputs": copy.deepcopy(old.get("inputs") or {}),
        "inventory": copy.deepcopy(old.get("inventory") or {}),
        "scan": old_scan,
        "details_archive": archive,
        "interpretation": {
            "requested_identity_rule": "Exact decoded requested field from saved placeholder query, with only the fragment stripped; preserve scheme, host, path, and query.",
            "host_path_rule": "Targets remain distinct by exact scheme/host/path/query identity; no basename, casefold, or cross-domain merge is performed.",
            "known_placeholder_unique_meaning": "Legacy known_placeholder_unique counts full raw placeholder strings, including source= caller identity; it is not an independent requested target count.",
            "recovery_queue_boundary": "requested target counts are an evidence inventory and are not claimed equivalent to the 3358 recovery queue.",
            "without_requested_field": "Direct external or excluded references without a requested query field are counted separately and are not forced into the requested target set.",
        },
        "requested_targets": {
            "unique_count": len(target_data),
            "occurrence_count": requested_field_occurrences,
            "occurrence_count_weighted_by_first_field": missing_requested_occurrences,
            "source_group_count": missing_requested_groups,
            "groups_without_requested": no_requested_groups,
            "occurrences_without_requested": no_requested_occurrences,
            "without_requested_by_classification": dict(sorted(no_requested_by_class.items())),
            "multiple_requested_field_groups": multiple_requested_field_groups,
            "by_classification": dict(sorted(by_classification.items())),
            "by_host_scope": dict(sorted(by_host_scope.items())),
            "occurrences_by_reason": dict(sorted(by_reason.items())),
            "external_host_unique_count": by_host_scope.get("external_host", {}).get("unique", 0),
            "external_host_occurrence_count": by_host_scope.get("external_host", {}).get("occurrences", 0),
            "top_by_occurrences": top_targets,
            "examples_by_classification": dict(examples_by_class),
        },
        "candidates": copy.deepcopy(old.get("candidates") or []),
        "missing_assets": compact_missing,
        "unproven": {
            "group_count": len(old.get("unproven") or []),
            "examples": [compact_group(group) for group in (old.get("unproven") or [])[:MAX_EXAMPLES_PER_CLASS]],
        },
        "dynamic_samples": copy.deepcopy((old.get("dynamic_samples") or [])[:MAX_EXAMPLES_PER_CLASS]),
        "representative_refs": copy.deepcopy((old.get("representative_refs") or [])[:MAX_EXAMPLES_PER_CLASS]),
        "compact_limits": {
            "max_examples_per_classification": MAX_EXAMPLES_PER_CLASS,
            "max_representative_examples": MAX_EXAMPLES_PER_CLASS,
            "max_total_human_facing_examples": MAX_TOTAL_EXAMPLES,
            "full_details": archive["path"],
        },
    }
    return result


def markdown(result: dict[str, Any]) -> str:
    scan = result["scan"]
    inventory = result["inventory"]
    requested = result["requested_targets"]
    missing = result["missing_assets"]
    lines = [
        "# Local route audit",
        "",
        "Offline static audit of all derived HTML/XML/CSS in `.scratch/pages-historical-exhibits-20261014-v3`.",
        "The v3 source tree, build manifest, provenance, and route map were read only; this compact summary was derived from the saved v3 JSON without a second scan.",
        "",
        f"Scanned {inventory['html_files_scanned']} HTML/XML files and {inventory['css_files_scanned']} CSS files, yielding {scan['static_reference_occurrences']} static reference occurrences; {scan['dynamic_reference_occurrences_skipped']} dynamic expressions were skipped.",
        f"Outcomes: {scan['outcome_counts'].get('resolved', 0)} resolved, {scan['outcome_counts'].get('candidate', 0)} proven repair candidates ({scan.get('candidate_unique_proven', 0)} unique; {scan.get('candidates_emitted', 0)} emitted), and {scan['outcome_counts'].get('missing', 0)} unresolved occurrences.",
        f"Known placeholders: {scan['known_placeholder_occurrences']} occurrences and {scan['known_placeholder_unique']} legacy raw groups (the raw value includes `source=` and is not a requested-target count).",
        f"Input hashes unchanged: {result['inputs'].get('hashes_unchanged')}. Full v3 details: `{result['details_archive']['path']}` ({result['details_archive']['source_bytes']} bytes before gzip).",
        "",
        "## Requested target aggregation",
        "",
        f"Exact requested targets after stripping only URL fragments: **{requested['unique_count']} unique**, **{requested['occurrence_count']} occurrences**. Groups without a requested field: {requested['groups_without_requested']} ({requested['occurrences_without_requested']} occurrences); these remain separate external/excluded evidence.",
        "This evidence inventory is not claimed equivalent to the 3358 recovery queue.",
        "",
        "| scope | unique targets | occurrences |",
        "| --- | ---: | ---: |",
    ]
    for scope, counts in requested["by_host_scope"].items():
        lines.append(f"| {scope} | {counts['unique']} | {counts['occurrences']} |")
    lines.extend(["", "### Highest occurrence exact targets", "", "| target | occurrences | scope | class |", "| --- | ---: | --- | --- |"])
    for target in requested["top_by_occurrences"][:MAX_EXAMPLES_PER_CLASS]:
        classes = ", ".join(target["classifications"])
        lines.append(f"| `{target['target']}` | {target['occurrences']} | {target['host_scope']} | {classes} |")
    lines.extend(["", "## Proven repair candidates", ""])
    if result["candidates"]:
        lines.extend(["| rank | impact | pages | refs | kind | current evidence | exact local target |", "| ---: | ---: | ---: | ---: | --- | --- | --- |"])
        for candidate in result["candidates"][:MAX_EXAMPLES_PER_CLASS]:
            lines.append("| {rank} | {impact} | {pages} | {refs} | {kind} | `{current}` | `{target}` |".format(
                rank=candidate.get("rank", ""), impact=candidate.get("impact", ""), pages=candidate.get("pages", ""), refs=candidate.get("references", candidate.get("refs", "")), kind=candidate.get("kind", ""), current=candidate.get("current_evidence", ""), target=candidate.get("exact_local_target", ""),
            ))
    else:
        lines.append("No proven repair candidates were emitted.")
    lines.extend(["", "## Missing and unproven evidence", "", f"There are {missing['group_count']} missing groups ({missing['occurrence_count']} occurrences); compact examples are capped at {MAX_EXAMPLES_PER_CLASS} per classification. Full rows are in the gzip archive.", ""])
    for classification, groups in missing["examples_by_classification"].items():
        counts = missing["classification_counts"][classification]
        lines.extend([f"### {classification} ({counts['groups']} groups, {counts['occurrences']} occurrences)", ""])
        for group in groups[:MAX_EXAMPLES_PER_CLASS]:
            requested_text = f"; requested={group['requested']}" if group.get("requested") else ""
            example = (group.get("examples") or [{}])[0]
            ref = f"{example.get('page', '?')}:{example.get('line', '?')}" if example else "?"
            lines.append(f"- `{ref}` `{group['raw']}` ({group['occurrences']} refs{requested_text}) — {group['missing_reason']}")
        lines.append("")
    lines.extend(["## Validation", "", f"`details-v3.json.gz` decompresses byte-exactly to the saved v3 JSON; source SHA-256 `{result['details_archive']['source_sha256']}`; gzip SHA-256 `{result['details_archive']['gzip_sha256']}`.", f"The compact JSON is intentionally bounded and contains at most {MAX_TOTAL_EXAMPLES} representative/example rows per human-facing section; `representative_refs` retains {len(result['representative_refs'])} rows.", ""])
    return "\n".join(lines)


def main() -> None:
    current_bytes = SUMMARY_PATH.read_bytes()
    current = json.loads(current_bytes.decode("utf-8"))
    if current.get("schema") == "local-route-audit/v1":
        old_bytes = current_bytes
        old = current
    elif current.get("schema") == "local-route-audit/v1-compact" and ARCHIVE_PATH.is_file():
        with gzip.open(ARCHIVE_PATH, "rb") as zipped:
            old_bytes = zipped.read()
        old = json.loads(old_bytes.decode("utf-8"))
    else:
        raise SystemExit(f"expected saved v3 summary or its archive, got {current.get('schema')!r}")
    with ARCHIVE_PATH.open("wb") as handle:
        with gzip.GzipFile(fileobj=handle, mode="wb", mtime=0) as zipped:
            zipped.write(old_bytes)
    archive_bytes = ARCHIVE_PATH.read_bytes()
    with gzip.open(ARCHIVE_PATH, "rb") as zipped:
        if zipped.read() != old_bytes:
            raise SystemExit("details archive failed byte-exact round trip")
    result = compact_summary(old, old_bytes, archive_bytes)
    SUMMARY_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MARKDOWN_PATH.write_text(markdown(result), encoding="utf-8")
    print(json.dumps({
        "source_bytes": len(old_bytes),
        "source_sha256": sha256_bytes(old_bytes),
        "archive_bytes": len(archive_bytes),
        "archive_sha256": sha256_bytes(archive_bytes),
        "summary_bytes": SUMMARY_PATH.stat().st_size,
        "markdown_bytes": MARKDOWN_PATH.stat().st_size,
        "requested_unique": result["requested_targets"]["unique_count"],
        "requested_occurrences": result["requested_targets"]["occurrence_count"],
        "requested_without_field_occurrences": result["requested_targets"]["occurrences_without_requested"],
        "static_occurrences": result["scan"]["static_reference_occurrences"],
        "outcome_sum": sum(result["scan"]["outcome_counts"].values()),
        "details_round_trip": result["details_archive"]["decompresses_byte_exact"],
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
