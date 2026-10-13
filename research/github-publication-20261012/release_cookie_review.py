"""Bounded, value-free review of Cookie fields in existing release ZIP metadata.

This deliberately samples metadata-like members only.  It never prints or stores
cookie values, never extracts a member to disk, and does not make network calls.
The complete field count is read from the already generated publication hygiene
report; the per-name/domain details are explicitly marked as bounded evidence.
"""

from __future__ import annotations

import json
import re
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research" / "github-publication-20261012"
PUB = OUT / "publication_hygiene.json"
MAX_SAMPLE_BYTES_PER_ZIP = 32 * 1024 * 1024
MAX_SAMPLE_MEMBERS_PER_ZIP = 1000
READ_LIMIT_PER_MEMBER = 2 * 1024 * 1024
PRECISE_MAX_BYTES_PER_ZIP = 32 * 1024 * 1024
PRECISE_MAX_MEMBERS_PER_ZIP = 1000
TARGET_COOKIE_NAMES = {"JSESSIONID", "login.cookies", "perm", "wb-p-SERVER", "wb-cdx-SERVER", "wb-cdx-nomatch-SERVER"}
MEMENTO_KEY_MARKERS = (
    "memento",
    "actual_timestamp",
    "capture",
    "x-archive-orig-date",
    "x-archive-orig-client-date",
)
TEXT_SUFFIXES = {
    ".json",
    ".jsonl",
    ".meta",
    ".txt",
    ".log",
    ".md",
    ".csv",
    ".yaml",
    ".yml",
    ".toml",
    ".headers",
}
COOKIE_NAME = re.compile(
    rb"(?i)(?:set-cookie|cookie)\s*[\"']?\s*[:=]\s*[\"']?"
    rb"([A-Za-z0-9_.-]{1,80})\s*="
)
DOMAIN = re.compile(
    rb"(?i)\b(?:[a-z0-9-]+\.)+"
    rb"(?:web\.archive\.org|archive\.org|worldofwarcraft\.com|"
    rb"wow-europe\.com|blizzard\.com)\b"
)
COOKIE_ASSIGNMENT = re.compile(
    r"(?i)(?:^|[;\s\"'])"
    r"(JSESSIONID|login\.cookies|perm|wb-p-SERVER|wb-cdx-SERVER|wb-cdx-nomatch-SERVER)"
    r"\s*=\s*([^;\r\n\"']*)"
)
YEAR = re.compile(r"(?<!\d)(?:19|20)\d{2}(?!\d)")
TIMESTAMP = re.compile(r"(?<!\d)(?:19|20)\d{10}(?!\d)")


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def family(domain: str) -> str:
    low = domain.casefold()
    if low.endswith("worldofwarcraft.com") or low.endswith("wow-europe.com") or low.endswith("blizzard.com"):
        return "historical_origin_or_official_site"
    if (
        low.endswith("archive.org")
        or low.endswith("us.archive.org")
        or low.endswith("web.archive.org")
    ):
        return "archive_infrastructure"
    return "unclassified"


def bounded_zip_sample(path: Path) -> dict[str, Any]:
    names: Counter[str] = Counter()
    kinds: Counter[str] = Counter()
    domains: Counter[str] = Counter()
    families: Counter[str] = Counter()
    members = 0
    scanned = 0
    errors = 0
    with zipfile.ZipFile(path, "r") as archive:
        for info in archive.infolist():
            if members >= MAX_SAMPLE_MEMBERS_PER_ZIP or scanned >= MAX_SAMPLE_BYTES_PER_ZIP:
                break
            name = info.filename
            low = name.casefold()
            suffix = Path(name).suffix.casefold()
            if suffix not in TEXT_SUFFIXES and not any(
                marker in low for marker in ("header", "cookie", "meta", "response")
            ):
                continue
            if "cdx" in low or "prefix" in low:
                continue
            try:
                with archive.open(info, "r") as handle:
                    data = handle.read(min(info.file_size, READ_LIMIT_PER_MEMBER))
                scanned += len(data)
                members += 1
            except (OSError, RuntimeError, EOFError, zipfile.BadZipFile):
                errors += 1
                continue
            for match in COOKIE_NAME.finditer(data):
                cookie_name = match.group(1).decode("ascii", errors="replace")
                names[cookie_name] += 1
                marker = match.group(0).lstrip().lower()
                kind = (
                    "response-set-cookie"
                    if marker.startswith(b"set-cookie")
                    else "request-cookie-or-cookie-field"
                )
                kinds[kind] += 1
                near = data[
                    max(0, match.start() - 512) : min(len(data), match.end() + 512)
                ]
                found = {
                    item.decode("ascii", errors="replace").casefold()
                    for item in DOMAIN.findall(near)
                }
                if not found:
                    families["unclassified"] += 1
                for domain in found:
                    domains[domain] += 1
                    families[family(domain)] += 1
    return {
        "path": rel(path),
        "sample_members": members,
        "sample_uncompressed_bytes": scanned,
        "sample_read_errors": errors,
        "cookie_name_counts": dict(sorted(names.items())),
        "field_kind_counts": dict(sorted(kinds.items())),
        "nearby_domain_counts": dict(sorted(domains.items())),
        "nearby_domain_family_counts": dict(sorted(families.items())),
        "values_emitted": False,
    }


def _safe_years_from_mapping(mapping: dict[str, Any], *, allow_generic_date: bool = False) -> set[str]:
    """Extract years only from timestamp/date/capture-like keys, never values."""
    details = _safe_year_details(mapping, allow_generic_date=allow_generic_date)
    return set(details)


def _safe_year_details(mapping: dict[str, Any], *, allow_generic_date: bool = False) -> dict[str, set[str]]:
    """Return year-to-key names for timestamp/date/capture-like fields."""
    details: dict[str, set[str]] = {}
    for key, value in mapping.items():
        key_low = str(key).casefold()
        if any(marker in key_low for marker in ("generated", "processed", "report", "build")):
            continue
        if not any(
            marker in key_low
            for marker in (
                "timestamp",
                "memento",
                "capture",
                "actual_date",
                "requested_date",
                "selected_date",
                "archive_date",
                "header_date",
                "date",
            )
        ) and not (allow_generic_date and key_low == "date"):
            continue
        if isinstance(value, (str, int, float)):
            text = str(value)
            found_years = set(YEAR.findall(text))
            for stamp in TIMESTAMP.findall(text):
                found_years.add(stamp[:4])
            for year in found_years:
                details.setdefault(year, set()).add(str(key))
    return details


def _classify_cookie_assignment(name: str, raw_value: str, context: str) -> tuple[str, list[str], dict[str, str]]:
    """Classify without retaining or emitting the actual cookie value."""
    value = raw_value.strip()
    years = sorted(set(YEAR.findall(context)))
    if not value:
        category = "empty_assignment"
    elif re.search(r"(?i)max-age\s*=\s*0", context) or re.search(
        r"(?i)expires\s*=[^;\r\n]*?(?:19|20)\d{2}", context
    ):
        category = "deletion_or_expired_marker"
    elif name == "perm" and re.fullmatch(r"(?i)(?:0|1|true|false|yes|no)", value):
        category = "fixed_public_preference_shape"
    elif name.casefold().startswith("wb-") and re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", value):
        category = "archive_route_id_shape_only"
    else:
        category = "unknown_session_value_shape"
    if len(value) == 0:
        size_bucket = "empty"
    elif len(value) <= 8:
        size_bucket = "1-8"
    elif len(value) <= 32:
        size_bucket = "9-32"
    elif len(value) <= 128:
        size_bucket = "33-128"
    else:
        size_bucket = "over-128"
    shape = {
        "length_bucket": size_bucket,
        "ascii_alnum_dash_shape": "yes" if re.fullmatch(r"[A-Za-z0-9_.:-]*", value) else "no",
    }
    return category, years, shape


def _header_class(key: str) -> str:
    low = key.casefold()
    if "x-archive-orig-set-cookie" in low or "x-archive-original-set-cookie" in low:
        return "archive-original-set-cookie-header"
    if "set-cookie" in low:
        return "response-set-cookie-header"
    if low == "cookie" or low.endswith("-cookie"):
        return "request-cookie-or-cookie-header"
    return "cookie-named-field"


def _record_precise_cookie(
    *,
    value: str,
    key: str,
    archive_path: str,
    member_name: str,
    base_years: set[str],
    base_year_keys: dict[str, set[str]],
    output: dict[str, Any],
) -> None:
    for match in COOKIE_ASSIGNMENT.finditer(value):
        name = match.group(1)
        raw_value = match.group(2)
        category, years, shape = _classify_cookie_assignment(name, raw_value, value)
        all_years = sorted(set(base_years).union(years))
        header_kind = _header_class(key)
        output["events"] += 1
        output["name_counts"][name] += 1
        output["classification_counts"][name][category] += 1
        output["header_key_counts"][key] += 1
        output["header_class_counts"][header_kind] += 1
        output["header_keys_by_name"][name][key] += 1
        output["header_classes_by_name"][name][header_kind] += 1
        output["shape_counts"][name][shape["length_bucket"]] += 1
        output["capture_years_by_name"][name].update(all_years)
        for year, keys in base_year_keys.items():
            if any(
                marker in key.casefold()
                for key in keys
                for marker in MEMENTO_KEY_MARKERS
            ):
                output["memento_capture_years_by_name"][name].add(year)
        if category == "deletion_or_expired_marker":
            output["deletion_years_by_name"][name].update(all_years)
        refs = output["member_refs_by_name"].setdefault(name, [])
        if len(refs) < 50:
            refs.append(
                {
                    "archive": archive_path,
                    "member": member_name,
                    "header_key": key,
                    "header_class": header_kind,
                    "classification": category,
                    "capture_years": all_years,
                    "value_shape": shape,
                }
            )


def _walk_precise_json(
    obj: Any,
    *,
    archive_path: str,
    member_name: str,
    parent_key: str,
    base_years: set[str],
    base_year_keys: dict[str, set[str]],
    output: dict[str, Any],
) -> None:
    if isinstance(obj, dict):
        year_details = _safe_year_details(
            obj,
            allow_generic_date=("header" in parent_key.casefold() or "response" in parent_key.casefold()),
        )
        local_years = set(base_years).union(year_details)
        combined_year_keys = {year: set(keys) for year, keys in base_year_keys.items()}
        for year, keys in year_details.items():
            combined_year_keys.setdefault(year, set()).update(keys)
        for year, keys in year_details.items():
            output["year_context_keys_by_year"].setdefault(year, set()).update(keys)
        for key, value in obj.items():
            key_text = str(key)
            low = key_text.casefold()
            if "cookie" in low and isinstance(value, str):
                _record_precise_cookie(
                    value=value,
                    key=key_text,
                    archive_path=archive_path,
                    member_name=member_name,
                    base_years=local_years,
                    base_year_keys=combined_year_keys,
                    output=output,
                )
            elif "cookie" in low and isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        _record_precise_cookie(
                            value=item,
                            key=key_text,
                            archive_path=archive_path,
                            member_name=member_name,
                            base_years=local_years,
                            base_year_keys=combined_year_keys,
                            output=output,
                        )
            _walk_precise_json(
                value,
                archive_path=archive_path,
                member_name=member_name,
                parent_key=key_text,
                base_years=local_years,
                base_year_keys=combined_year_keys,
                output=output,
            )
    elif isinstance(obj, list):
        for value in obj:
            _walk_precise_json(
                value,
                archive_path=archive_path,
                member_name=member_name,
                parent_key=parent_key,
                base_years=base_years,
                base_year_keys=base_year_keys,
                output=output,
            )


def precise_zip_sample(path: Path) -> dict[str, Any]:
    output: dict[str, Any] = {
        "events": 0,
        "name_counts": Counter(),
        "classification_counts": {},
        "header_key_counts": Counter(),
        "header_class_counts": Counter(),
        "header_keys_by_name": {name: Counter() for name in TARGET_COOKIE_NAMES},
        "header_classes_by_name": {name: Counter() for name in TARGET_COOKIE_NAMES},
        "year_context_keys_by_year": {},
        "shape_counts": {},
        "capture_years_by_name": {},
        "deletion_years_by_name": {},
        "member_refs_by_name": {},
        "sample_members": 0,
        "sample_uncompressed_bytes": 0,
        "sample_read_errors": 0,
        "json_parse_failures": 0,
    }
    for name in TARGET_COOKIE_NAMES:
        output["classification_counts"][name] = Counter()
        output["shape_counts"][name] = Counter()
        output["capture_years_by_name"][name] = set()
        output["deletion_years_by_name"][name] = set()
    with zipfile.ZipFile(path, "r") as archive:
        for info in archive.infolist():
            if (
                output["sample_members"] >= PRECISE_MAX_MEMBERS_PER_ZIP
                or output["sample_uncompressed_bytes"] >= PRECISE_MAX_BYTES_PER_ZIP
            ):
                break
            name = info.filename
            low = name.casefold()
            suffix = Path(name).suffix.casefold()
            if suffix not in TEXT_SUFFIXES and not any(
                marker in low for marker in ("header", "cookie", "meta", "response")
            ):
                continue
            if "cdx" in low or "prefix" in low:
                continue
            try:
                with archive.open(info, "r") as handle:
                    data = handle.read(min(info.file_size, READ_LIMIT_PER_MEMBER))
                output["sample_uncompressed_bytes"] += len(data)
                output["sample_members"] += 1
            except (OSError, RuntimeError, EOFError, zipfile.BadZipFile):
                output["sample_read_errors"] += 1
                continue
            text = data.decode("utf-8", errors="replace")
            parsed = False
            if suffix in {".json", ".meta"}:
                try:
                    obj = json.loads(text)
                except (TypeError, ValueError):
                    output["json_parse_failures"] += 1
                else:
                    parsed = True
                    _walk_precise_json(
                        obj,
                        archive_path=rel(path),
                        member_name=name,
                        parent_key="",
                        base_years=set(),
                        output=output,
                    )
            elif suffix == ".jsonl":
                parsed = True
                for line in text.splitlines():
                    if not line.strip():
                        continue
                    try:
                        obj = json.loads(line)
                    except (TypeError, ValueError):
                        output["json_parse_failures"] += 1
                        continue
                    _walk_precise_json(
                        obj,
                        archive_path=rel(path),
                        member_name=name,
                        parent_key="",
                        base_years=set(),
                        output=output,
                    )
            if not parsed and any(token.lower() in data.lower() for token in (b"cookie", b"set-cookie")):
                for match in COOKIE_NAME.finditer(data):
                    name_found = match.group(1).decode("ascii", errors="replace")
                    if name_found not in TARGET_COOKIE_NAMES:
                        continue
                    left = max(0, match.start() - 256)
                    right = min(len(data), match.end() + 768)
                    context = data[left:right].decode("utf-8", errors="replace")
                    _record_precise_cookie(
                        value=context,
                        key="unparsed-cookie-field",
                        archive_path=rel(path),
                        member_name=name,
                        base_years=set(),
                        output=output,
                    )
    return {
        "path": rel(path),
        "sample_members": output["sample_members"],
        "sample_uncompressed_bytes": output["sample_uncompressed_bytes"],
        "sample_read_errors": output["sample_read_errors"],
        "json_parse_failures": output["json_parse_failures"],
        "events": output["events"],
        "name_counts": dict(sorted(output["name_counts"].items())),
        "classification_counts": {
            name: dict(sorted(counts.items()))
            for name, counts in sorted(output["classification_counts"].items())
            if counts
        },
        "header_key_counts": dict(sorted(output["header_key_counts"].items())),
        "header_class_counts": dict(sorted(output["header_class_counts"].items())),
        "header_keys_by_name": {
            name: dict(sorted(counts.items()))
            for name, counts in sorted(output["header_keys_by_name"].items())
            if counts
        },
        "header_classes_by_name": {
            name: dict(sorted(counts.items()))
            for name, counts in sorted(output["header_classes_by_name"].items())
            if counts
        },
        "year_context_keys_by_year": {
            year: sorted(keys)
            for year, keys in sorted(output["year_context_keys_by_year"].items())
        },
        "shape_counts": {
            name: dict(sorted(counts.items()))
            for name, counts in sorted(output["shape_counts"].items())
            if counts
        },
        "capture_years_by_name": {
            name: sorted(years)
            for name, years in sorted(output["capture_years_by_name"].items())
            if years
        },
        "deletion_years_by_name": {
            name: sorted(years)
            for name, years in sorted(output["deletion_years_by_name"].items())
            if years
        },
        "member_refs_by_name": output["member_refs_by_name"],
        "values_emitted": False,
    }


def main() -> int:
    report = json.loads(PUB.read_text(encoding="utf-8"))
    metadata = report.get("zip_metadata_content_scan", [])
    rows = []
    total_scanned = 0
    total_cookie_fields = 0
    total_value_shapes = 0
    truncated = 0
    for row in metadata:
        scanned = int(row.get("scanned_uncompressed_bytes", 0))
        fields = int(row.get("field_counts", {}).get("cookie_field", 0))
        values = sum(int(v) for v in row.get("value_shape_counts", {}).values())
        is_truncated = bool(row.get("truncated_by_bound_or_member_error"))
        total_scanned += scanned
        total_cookie_fields += fields
        total_value_shapes += values
        truncated += int(is_truncated)
        rows.append(
            {
                "path": row.get("path"),
                "scanned_uncompressed_bytes": scanned,
                "cookie_field_occurrences": fields,
                "credential_value_shape_occurrences": values,
                "truncated_or_member_error": is_truncated,
            }
        )
    paths = [ROOT / row["path"] for row in rows if isinstance(row.get("path"), str)]
    samples = [bounded_zip_sample(path) for path in paths if path.is_file()]
    precise_samples = [precise_zip_sample(path) for path in paths if path.is_file()]
    zip_scope = []
    for row in report.get("zip_central_directory", []):
        if not isinstance(row, dict):
            continue
        zip_scope.append(
            {
                "path": row.get("path"),
                "bytes": row.get("bytes"),
                "sha256": row.get("sha256"),
                "member_count": row.get("member_count"),
                "top_level_counts": row.get("top_level_counts", {}),
                "research_member_count": row.get("research_member_count", 0),
                "backups_member_count": row.get("backups_member_count", 0),
                "offline_member_count": row.get("offline_member_count", 0),
                "payload_extracted": row.get("payload_extracted", False),
            }
        )
    existing_zip_paths = {row.get("path") for row in zip_scope}
    current_artifacts = sorted(
        rel(path) for path in (ROOT / "artifacts").glob("*.zip") if path.is_file()
    )
    artifact_paths_outside_existing_report = [
        path for path in current_artifacts if path not in existing_zip_paths
    ]
    sample_names: Counter[str] = Counter()
    sample_kinds: Counter[str] = Counter()
    sample_domains: Counter[str] = Counter()
    sample_families: Counter[str] = Counter()
    for sample in samples:
        sample_names.update(sample.get("cookie_name_counts", {}))
        sample_kinds.update(sample.get("field_kind_counts", {}))
        sample_domains.update(sample.get("nearby_domain_counts", {}))
        sample_families.update(sample.get("nearby_domain_family_counts", {}))
    precise_names: Counter[str] = Counter()
    precise_header_keys: Counter[str] = Counter()
    precise_header_classes: Counter[str] = Counter()
    precise_header_keys_by_name: dict[str, Counter[str]] = {
        name: Counter() for name in TARGET_COOKIE_NAMES
    }
    precise_header_classes_by_name: dict[str, Counter[str]] = {
        name: Counter() for name in TARGET_COOKIE_NAMES
    }
    precise_year_context_keys_by_year: dict[str, set[str]] = {}
    precise_classifications: dict[str, Counter[str]] = {
        name: Counter() for name in TARGET_COOKIE_NAMES
    }
    precise_years: dict[str, set[str]] = {name: set() for name in TARGET_COOKIE_NAMES}
    precise_deletion_years: dict[str, set[str]] = {name: set() for name in TARGET_COOKIE_NAMES}
    precise_refs: dict[str, list[dict[str, Any]]] = {name: [] for name in TARGET_COOKIE_NAMES}
    precise_events = 0
    precise_bytes = 0
    precise_read_errors = 0
    precise_parse_failures = 0
    for sample in precise_samples:
        precise_events += int(sample.get("events", 0))
        precise_bytes += int(sample.get("sample_uncompressed_bytes", 0))
        precise_read_errors += int(sample.get("sample_read_errors", 0))
        precise_parse_failures += int(sample.get("json_parse_failures", 0))
        precise_names.update(sample.get("name_counts", {}))
        precise_header_keys.update(sample.get("header_key_counts", {}))
        precise_header_classes.update(sample.get("header_class_counts", {}))
        for name, counts in sample.get("header_keys_by_name", {}).items():
            precise_header_keys_by_name.setdefault(name, Counter()).update(counts)
        for name, counts in sample.get("header_classes_by_name", {}).items():
            precise_header_classes_by_name.setdefault(name, Counter()).update(counts)
        for year, keys in sample.get("year_context_keys_by_year", {}).items():
            precise_year_context_keys_by_year.setdefault(year, set()).update(keys)
        for name, counts in sample.get("classification_counts", {}).items():
            precise_classifications.setdefault(name, Counter()).update(counts)
        for name, years in sample.get("capture_years_by_name", {}).items():
            precise_years.setdefault(name, set()).update(years)
        for name, years in sample.get("deletion_years_by_name", {}).items():
            precise_deletion_years.setdefault(name, set()).update(years)
        for name, refs in sample.get("member_refs_by_name", {}).items():
            bucket = precise_refs.setdefault(name, [])
            if len(bucket) < 100:
                bucket.extend(refs[: 100 - len(bucket)])
    classification = report.get("classification", {})
    out = {
        "schema_version": 1,
        "kind": "github_publication_cookie_review_20261013",
        "network_performed": False,
        "source_publication_hygiene": rel(PUB),
        "source_publication_hygiene_generated_utc": report.get("generated_utc"),
        "complete_metadata_scan_from_existing_report": {
            "zip_count": len(rows),
            "scanned_uncompressed_bytes": total_scanned,
            "cookie_field_occurrences": total_cookie_fields,
            "credential_value_shape_occurrences": total_value_shapes,
            "truncated_or_member_error_zip_count": truncated,
            "scope_note": (
                "These totals are copied from the existing metadata-only report. "
                "They exclude HTML/CSS/JS/XML and CDX/prefix members and are not a "
                "complete payload scan."
            ),
        },
        "bounded_name_domain_sample": {
            "zip_count": len(samples),
            "max_uncompressed_bytes_per_zip": MAX_SAMPLE_BYTES_PER_ZIP,
            "max_members_per_zip": MAX_SAMPLE_MEMBERS_PER_ZIP,
            "sample_uncompressed_bytes": sum(
                int(sample["sample_uncompressed_bytes"]) for sample in samples
            ),
            "cookie_name_counts": dict(sorted(sample_names.items())),
            "field_kind_counts": dict(sorted(sample_kinds.items())),
            "nearby_domain_family_counts": dict(sorted(sample_families.items())),
            "nearby_domain_counts": dict(sorted(sample_domains.items())),
            "values_emitted": False,
            "scope_note": (
                "Names and nearby domains are bounded evidence only; context windows "
                "can contain both replay and origin URLs. No cookie value is retained."
            ),
            "per_zip": samples,
        },
        "precise_structured_cookie_sample": {
            "zip_count": len(precise_samples),
            "max_uncompressed_bytes_per_zip": PRECISE_MAX_BYTES_PER_ZIP,
            "max_members_per_zip": PRECISE_MAX_MEMBERS_PER_ZIP,
            "sample_uncompressed_bytes": precise_bytes,
            "events": precise_events,
            "sample_read_errors": precise_read_errors,
            "json_parse_failures": precise_parse_failures,
            "cookie_name_counts": dict(sorted(precise_names.items())),
            "header_key_counts": dict(sorted(precise_header_keys.items())),
            "header_class_counts": dict(sorted(precise_header_classes.items())),
            "header_keys_by_name": {
                name: dict(sorted(counts.items()))
                for name, counts in sorted(precise_header_keys_by_name.items())
                if counts
            },
            "header_classes_by_name": {
                name: dict(sorted(counts.items()))
                for name, counts in sorted(precise_header_classes_by_name.items())
                if counts
            },
            "year_context_keys_by_year": {
                year: sorted(keys)
                for year, keys in sorted(precise_year_context_keys_by_year.items())
            },
            "classification_counts_by_name": {
                name: dict(sorted(counts.items()))
                for name, counts in sorted(precise_classifications.items())
                if counts
            },
            "capture_years_by_name": {
                name: sorted(years)
                for name, years in sorted(precise_years.items())
                if years
            },
            "deletion_or_expiry_years_by_name": {
                name: sorted(years)
                for name, years in sorted(precise_deletion_years.items())
                if years
            },
            "member_refs_by_name": precise_refs,
            "values_emitted": False,
            "scope_note": (
                "This second bounded pass parses only structured JSON/.meta members "
                "and small header-like samples. It records exact header key names, "
                "capture years, and value-shape classifications without storing any "
                "cookie value. Unknown means the value was not proven public or deleted."
            ),
        },
        "zip_scope_from_existing_report": {
            "covered_zip_count": len(zip_scope),
            "covered_zips": zip_scope,
            "current_artifacts_zip_count": len(current_artifacts),
            "current_artifacts_outside_existing_report": artifact_paths_outside_existing_report,
            "scope_note": (
                "Central-directory and metadata totals below describe the six ZIPs in "
                "the existing publication hygiene report. Any artifact created after "
                "that report is listed as outside this review rather than silently "
                "treated as scanned."
            ),
        },
        "credential_classification": {
            "credential_value_findings_in_existing_metadata": classification.get(
                "zip_metadata_credential_value_findings", 0
            ),
            "authorization_fields_without_values_in_existing_metadata": classification.get(
                "zip_metadata_authorization_field_occurrences", 0
            ),
            "cookie_fields_in_existing_metadata": classification.get(
                "zip_metadata_cookie_field_occurrences", total_cookie_fields
            ),
            "interpretation": (
                "The bounded sample matched response Set-Cookie syntax only; it found "
                "no request Cookie syntax. wb-p-SERVER is consistent with Archive "
                "playback infrastructure. wb-cdx-SERVER and wb-cdx-nomatch-SERVER "
                "are consistent with Archive/CDX responses. JSESSIONID, login.cookies, "
                "and perm are session/preference-like names near both Archive and "
                "historical official-site domains; their values and exact issuer are "
                "not retained, so treat them as ambiguous public replay metadata, not "
                "proof of authenticated credentials."
            ),
            "values_emitted": False,
        },
        "zip_release_scope": {
            "full_source_recommendation": (
                "Keep WOW_Encyclopedia_20080512_full_source.zip as a separate release "
                "asset for the original 437-file source backup."
            ),
            "recovery_recommendation": (
                "The offline_recovery ZIP contains selected research/evidence members; "
                "it is not a complete copy of the workspace research tree."
            ),
            "historical_candidate_recommendation": (
                "Keep 20101203 and reassessment ZIPs separately labeled as historical "
                "candidate evidence, not baseline source."
            ),
        },
        "coverage_limits": [
            "No network calls and no member extraction to disk.",
            "This review does not rescan ZIP payloads; nested ZIP payloads and non-metadata members remain outside the existing complete metadata totals.",
            "Several existing metadata ZIP scans reached their 512 MiB/member-error boundary; those are explicitly marked truncated.",
            "A value-free field match cannot prove whether a replay Set-Cookie was anonymous infrastructure state or an origin session cookie.",
            "The runtime ZIP created after the existing six-ZIP report is listed as outside this review and was not included in the 11,345-field total.",
        ],
    }
    (OUT / "release-cookie-review.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Release Cookie Review",
        "",
        "This is a bounded, value-free local review. It made no network requests and did not extract ZIP members to disk.",
        "",
        f"- Existing metadata report: `{rel(PUB)}`",
        f"- Existing six-ZIP metadata total: `{total_scanned}` uncompressed bytes, `{total_cookie_fields}` Cookie fields, `{total_value_shapes}` credential-shaped values.",
        f"- Existing metadata rows marked truncated/member-error: `{truncated}` of `{len(rows)}`.",
        f"- Bounded name/domain sample: `{sum(int(s['sample_uncompressed_bytes']) for s in samples)}` bytes across `{len(samples)}` ZIPs.",
        f"- Existing central-directory scope: `{len(zip_scope)}` ZIPs; current artifacts outside that report: `{', '.join(artifact_paths_outside_existing_report) if artifact_paths_outside_existing_report else 'none'}`.",
        "",
        "## Cookie classification",
        "",
        "The bounded sample matched response `Set-Cookie` syntax only; it found no request `Cookie` syntax. `wb-p-SERVER` is consistent with Archive playback infrastructure. `wb-cdx-SERVER` and `wb-cdx-nomatch-SERVER` are consistent with Archive/CDX responses. `JSESSIONID`, `login.cookies`, and `perm` are session/preference-like names near both Archive and historical official-site domains; values were not retained and issuer cannot be proven.",
        "",
        "Cookie names, field kinds, and nearby domain counts are recorded in the JSON without values. Nearby domains are context evidence, not a definitive issuer mapping.",
        "",
        f"The precise structured pass sampled `{precise_bytes}` bytes and found `{precise_events}` target-cookie events. It records exact header key names, capture years, and only value-shape classes. Any `unknown_session_value_shape` remains unresolved; no cookie value is printed or stored.",
        f"- Header-key mapping by name: `{json.dumps({name: dict(sorted(counts.items())) for name, counts in sorted(precise_header_keys_by_name.items()) if counts}, ensure_ascii=False, sort_keys=True)}`.",
        f"- Classification by name: `{json.dumps({name: dict(sorted(counts.items())) for name, counts in sorted(precise_classifications.items()) if counts}, ensure_ascii=False, sort_keys=True)}`.",
        "",
        "## Release scope",
        "",
        "Keep `WOW_Encyclopedia_20080512_full_source.zip` as a separate asset for the original 437-file source backup. The offline recovery ZIP contains selected research/evidence members rather than the complete workspace research tree. Keep the 20101203 and reassessment ZIPs separately labeled as historical candidate evidence. The runtime ZIP is outside this existing six-ZIP review and needs its own hygiene scan before release.",
        "",
        "## Limits",
        "",
        "The report does not claim the nested ZIP or all non-metadata payloads are clean. Existing metadata rows that reached a 512 MiB/member-error boundary remain marked truncated. A value-free Set-Cookie match cannot prove anonymous replay infrastructure versus an origin session cookie; manual release review remains appropriate for those ambiguous fields.",
    ]
    (OUT / "release-cookie-review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "output_json": rel(OUT / "release-cookie-review.json"),
        "output_md": rel(OUT / "release-cookie-review.md"),
        "metadata_zip_count": len(rows),
        "metadata_scanned_bytes": total_scanned,
        "metadata_cookie_fields": total_cookie_fields,
        "metadata_truncated_zip_count": truncated,
        "sample_bytes": sum(int(s["sample_uncompressed_bytes"]) for s in samples),
        "sample_cookie_names": dict(sorted(sample_names.items())),
        "sample_field_kinds": dict(sorted(sample_kinds.items())),
        "values_emitted": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
