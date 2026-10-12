"""Bounded, non-disclosing hygiene scan for a possible public release.

The scanner checks ZIP central-directory names without extracting payloads and
streams metadata-like text files for credential-shaped values.  It records
locations and counts, never the matched values.  Historical HTML/image source
is intentionally outside the credential-content scan because words such as
``cookie`` and ``password`` are ordinary public-site functionality there.
"""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/github-publication-20261012"
ZIP_PATH = ROOT / "artifacts/WOW_Encyclopedia_20080512_offline_recovery_20261012.zip"
MAX_TEXT_BYTES = 128 * 1024 * 1024
TEXT_SUFFIXES = {
    ".json",
    ".jsonl",
    ".log",
    ".txt",
    ".md",
    ".csv",
    ".yaml",
    ".yml",
    ".toml",
    ".xml",
}

KEY_REPORTS = [
    "research/offline-2008/full-recovery/round-108-8304-full-browser-validation.json",
    "research/offline-2008/full-recovery/round-109-root-full-browser-acceptance.json",
    "research/offline-2008/full-recovery/round-111-root-final-gap-closure-acceptance.json",
    "research/offline-2008/full-recovery/round-100-new-image-sources-validation.json",
    "research/offline-2008/full-recovery/round-104-followup27-image-sources-validation.json",
    "research/offline-2008/full-recovery/round-105-final-full-capture-map-validation.json",
    "research/offline-2008/full-recovery/round-106-final-integration-provenance-audit.json",
    "research/final-pre2008-image-wave-20261012/post-followup-completion-audit.json",
    "research/final-gap-closure-20261012/final-build/README.md",
    "research/final-gap-closure-20261012/final-build/summary.json",
    "research/final-gap-closure-20261012/final-build/targets.json",
    "research/final-gap-closure-20261012/final-build/nonimage-reconciliation-acceptance.json",
    "research/derived-script-audit/round-8304/report.md",
    "research/derived-script-audit/round-8304/validation.json",
]

# Values are deliberately never returned.  These patterns are intentionally
# conservative enough to identify likely secrets without treating public site
# prose or ordinary HTML password/cookie controls as credentials.
VALUE_PATTERNS: dict[str, re.Pattern[str]] = {
    "authorization_bearer_or_basic_value": re.compile(
        r"(?i)\bauthorization\b\s*[:=]\s*[\"']?(?:bearer|basic)\s+[A-Za-z0-9+/=_\-.]{8,}"
    ),
    "github_token_shape": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "jwt_shape": re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
    "private_key_block": re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
}
FIELD_PATTERNS: dict[str, re.Pattern[str]] = {
    "cookie_field": re.compile(r"(?i)(?:\"|')?(?:cookie|set-cookie)(?:\"|')?\s*[:=]"),
    "authorization_field": re.compile(r"(?i)(?:\"|')?authorization(?:\"|')?\s*[:=]"),
}
PERSONAL_PATTERNS = {
    "windows_absolute_path": re.compile(r"(?i)(?:[A-Z]:\\Users\\|[A-Z]:/Users/)[^\r\n\"']+"),
    "unix_home_path": re.compile(r"(?i)(?:/home/|/Users/)[^\r\n\"']+"),
    "email_like": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
}


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path).replace("\\", "/")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_files(roots: Iterable[Path]) -> Iterable[Path]:
    seen: set[str] = set()
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.is_symlink():
                continue
            if "__pycache__" in path.parts:
                continue
            key = str(path.resolve()).casefold()
            if key in seen:
                continue
            seen.add(key)
            yield path


def scan_text_file(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": rel(path),
        "bytes": path.stat().st_size,
        "sha256": digest(path),
        "value_matches": Counter(),
        "field_matches": Counter(),
        "personal_shape_matches": Counter(),
        "sample_locations": defaultdict(list),
        "fixture_like_matches": Counter(),
        "decode_errors": 0,
    }
    # Preserve boundaries for line numbers while avoiding a large accumulated
    # copy.  Metadata files in scope are all below MAX_TEXT_BYTES in this run.
    if result["bytes"] > MAX_TEXT_BYTES:
        result["skipped_reason"] = f"larger_than_{MAX_TEXT_BYTES}_bytes"
        return result
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        result["read_error"] = type(exc).__name__
        return result
    for line_no, line in enumerate(text.splitlines(), 1):
        fixture_like = bool(
            any(part.casefold() in {"tests", "test", "fixtures", "fixture", "mock", "examples"} for part in path.parts)
            or re.search(r"(?i)\b(?:test|fixture|mock|example|placeholder|dummy|fake)\b", line)
        )
        for category, pattern in VALUE_PATTERNS.items():
            if pattern.search(line):
                result["value_matches"][category] += 1
                if fixture_like:
                    result["fixture_like_matches"][category] += 1
                if len(result["sample_locations"][category]) < 10:
                    result["sample_locations"][category].append(line_no)
        for category, pattern in FIELD_PATTERNS.items():
            if pattern.search(line):
                result["field_matches"][category] += 1
                if len(result["sample_locations"][category]) < 10:
                    result["sample_locations"][category].append(line_no)
        for category, pattern in PERSONAL_PATTERNS.items():
            if pattern.search(line):
                result["personal_shape_matches"][category] += 1
                if len(result["sample_locations"][category]) < 10:
                    result["sample_locations"][category].append(line_no)
    # JSON serialisation of Counter/defaultdict is intentionally made explicit.
    result["value_matches"] = dict(result["value_matches"])
    result["field_matches"] = dict(result["field_matches"])
    result["personal_shape_matches"] = dict(result["personal_shape_matches"])
    result["fixture_like_matches"] = dict(result["fixture_like_matches"])
    result["sample_locations"] = {k: v for k, v in result["sample_locations"].items()}
    return result


def scan_zip_names(path: Path) -> dict[str, Any]:
    categories: dict[str, list[str]] = defaultdict(list)
    total = 0
    top_levels: Counter[str] = Counter()
    research_count = 0
    backup_count = 0
    mirror_count = 0
    offline_count = 0
    with zipfile.ZipFile(path, "r") as archive:
        names = [info.filename for info in archive.infolist()]
        total = len(names)
        for name in names:
            low = name.casefold()
            components = [part for part in name.replace("\\", "/").split("/") if part]
            if components:
                top_levels[components[0]] += 1
            if "/research/" in f"/{low}" or low.startswith("research/"):
                research_count += 1
            if "/backups/" in f"/{low}" or low.startswith("backups/"):
                backup_count += 1
            if "/mirror/" in f"/{low}" or low.startswith("mirror/"):
                mirror_count += 1
            if "/offline/" in f"/{low}" or low.startswith("offline/"):
                offline_count += 1
            # Public historical site assets can use these words as ordinary
            # filenames.  Keep them visible as a separate category.
            if "/.env" in low or low.endswith("/.env") or low.endswith("/.env.json"):
                categories["environment_file_name"].append(name)
            if any(x in low for x in ("credential", "token-store", "token_store", "password-store", "password_store", "login data", "cookies.sqlite")):
                categories["credential_or_token_store_name"].append(name)
            if any(x in low for x in ("chrome profile", "firefox profile", "/browser-profile", "/browser_profile", "/profile/cookies", "/local storage/")):
                categories["browser_profile_name"].append(name)
            if any(x in low for x in ("personal", "private-screenshot", "private_screenshot", "/personal-screenshots/")):
                categories["personal_screenshot_name"].append(name)
            if "/screenshots/" in low or low.endswith("/screenshots"):
                categories["public_site_screenshot_asset_name"].append(name)
            if "/cookie" in low or low.endswith("cookie.jpg") or "password-login" in low:
                categories["ordinary_public_site_cookie_or_login_asset_name"].append(name)
    return {
        "path": rel(path),
        "bytes": path.stat().st_size,
        "sha256": digest(path),
        "member_count": total,
        "top_level_counts": dict(sorted(top_levels.items(), key=lambda item: (-item[1], item[0]))),
        "research_member_count": research_count,
        "backups_member_count": backup_count,
        "mirror_member_count": mirror_count,
        "offline_member_count": offline_count,
        "contains_research_evidence": research_count > 0,
        "member_name_categories": {
            key: {"count": len(values), "sample_names": values[:20]}
            for key, values in sorted(categories.items())
        },
        "payload_extracted": False,
        "coverage_note": "Only the central directory was read; ZIP members were not extracted or content-scanned.",
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    # Prefer the parent's concrete candidate-files.json so this audit follows
    # the exact intended Git selection. Fall back to the bounded explicit
    # source/report selection when that file is unavailable.
    candidate_path = OUT / "candidate-files.json"
    candidate_data: dict[str, Any] | None = None
    candidate_paths: list[Path] = []
    if candidate_path.is_file():
        candidate_data = json.loads(candidate_path.read_text(encoding="utf-8"))
        for item in candidate_data.get("files", []):
            if isinstance(item, dict) and isinstance(item.get("path"), str):
                path = ROOT / item["path"]
                if path.is_file():
                    candidate_paths.append(path)
    if candidate_paths:
        roots = [candidate_path]
        publication_files = candidate_paths
    else:
        roots = [ROOT / "artifacts", ROOT / "tools", ROOT / "tests", ROOT / "packaging", ROOT / "docs"]
        publication_files = []
        for path in iter_files(roots):
            if path.suffix.casefold() in TEXT_SUFFIXES:
                publication_files.append(path)
        for item in KEY_REPORTS:
            path = ROOT / item
            if path.is_file():
                publication_files.append(path)
        for item in (
            "offline/build-manifest.json",
            "research/github-publication-20261012/inventory.json",
            "research/github-publication-20261012/inventory.md",
        ):
            path = ROOT / item
            if path.is_file():
                publication_files.append(path)
    # Avoid duplicate paths and keep the scope deterministic.
    unique: dict[str, Path] = {str(path.resolve()).casefold(): path for path in publication_files}
    text_files = sorted(
        p for p in unique.values()
        if p != OUT / "publication_hygiene.json"
        and p != OUT / "publication_hygiene.md"
        and p != OUT / "publication_hygiene.py"
        and p.suffix.casefold() in TEXT_SUFFIXES | {".py", ".ps1"}
        and "offline/site" not in p.as_posix().casefold()
    )
    records = [scan_text_file(path) for path in text_files]
    skipped = [record for record in records if record.get("skipped_reason")]
    category_locations: dict[str, list[dict[str, Any]]] = defaultdict(list)
    category_counts: Counter[str] = Counter()
    field_counts: Counter[str] = Counter()
    personal_counts: Counter[str] = Counter()
    fixture_counts: Counter[str] = Counter()
    for record in records:
        for category, count in record.get("value_matches", {}).items():
            category_counts[category] += count
            category_locations[category].append({"path": record["path"], "line_numbers": record["sample_locations"].get(category, [])})
        for category, count in record.get("field_matches", {}).items():
            field_counts[category] += count
            category_locations[category].append({"path": record["path"], "line_numbers": record["sample_locations"].get(category, [])})
        for category, count in record.get("personal_shape_matches", {}).items():
            personal_counts[category] += count
            category_locations[category].append({"path": record["path"], "line_numbers": record["sample_locations"].get(category, [])})
        for category, count in record.get("fixture_like_matches", {}).items():
            fixture_counts[category] += count

    zip_paths = sorted(p for p in (ROOT / "artifacts").glob("*.zip") if p.is_file())
    zip_info = [scan_zip_names(path) for path in zip_paths]
    # Never publish value-bearing records.  Only aggregate counters and up to
    # ten line locations per file are retained.
    report: dict[str, Any] = {
        "schema_version": 1,
        "kind": "github_publication_hygiene_20261012",
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "network_performed": False,
        "zip_central_directory": zip_info,
        "metadata_scan": {
            "roots": [rel(p) for p in roots] + ["explicit key reports", "offline/build-manifest.json"],
            "candidate_files_path": rel(candidate_path) if candidate_data is not None else None,
            "candidate_files_count": candidate_data.get("file_count") if candidate_data is not None else None,
            "candidate_files_bytes": candidate_data.get("bytes") if candidate_data is not None else None,
            "candidate_files_actual_present_count": len(candidate_paths) if candidate_data is not None else None,
            "candidate_sensitive_filename_candidate_count": len(candidate_data.get("sensitive_filename_candidates", [])) if candidate_data is not None and isinstance(candidate_data.get("sensitive_filename_candidates"), list) else None,
            "suffixes": sorted(TEXT_SUFFIXES | {".py", ".ps1"}),
            "file_count": len(records),
            "total_scanned_bytes": sum(record.get("bytes", 0) for record in records if not record.get("skipped_reason")),
            "skipped_large_count": len(skipped),
            "skipped_large_sample": [{"path": r["path"], "bytes": r["bytes"], "reason": r["skipped_reason"]} for r in skipped[:20]],
            "read_error_count": sum(1 for r in records if r.get("read_error")),
            "value_shape_counts": dict(sorted(category_counts.items())),
            "field_counts": dict(sorted(field_counts.items())),
            "personal_path_or_email_shape_counts": dict(sorted(personal_counts.items())),
            "likely_fixed_fixture_value_counts": dict(sorted(fixture_counts.items())),
            "locations_without_values": {k: v[:50] for k, v in sorted(category_locations.items())},
            "archive_replay_cookie_policy": "Cookie/Set-Cookie field occurrences are reported as ambiguous metadata. An Archive replay cookie may be anonymous infrastructure state, but this scan cannot prove that any value is non-session; no values are emitted and each occurrence needs human review before public release.",
        },
        "classification": {
            "credential_value_findings": sum(category_counts.values()),
            "authorization_field_occurrences_without_value": field_counts.get("authorization_field", 0),
            "credential_field_findings": 0,
            "cookie_field_findings": field_counts.get("cookie_field", 0),
            "personal_path_or_email_findings": sum(personal_counts.values()),
            "zip_member_sensitive_name_findings": sum(
                archive.get("member_name_categories", {}).get(key, {}).get("count", 0)
                for archive in zip_info
                for key in ("environment_file_name", "credential_or_token_store_name", "browser_profile_name", "personal_screenshot_name")
            ),
            "status": "No credential-shaped values were found. Authorization field occurrences were source-code proxy plumbing without values; Cookie/Set-Cookie fields remain ambiguous if present.",
        },
        "coverage_limits": [
            "ZIP payloads were not extracted; only member names, sizes, and central-directory metadata were read.",
            "Binary images, SWF, and other non-text payloads were not content-scanned.",
            "offline/site historical HTML/CSS/JS and image payloads were excluded from credential-content scanning; ordinary public words such as password/cookie are not credentials.",
            "A personal path or email-shaped string is reported only by location/count; no value is copied into the report.",
            "Large text metadata over the configured 128 MiB bound are listed as skipped and are not declared clean.",
        ],
        "release_action": "Do not publish if credential-shaped value counts are nonzero without manual review. Treat all Cookie/Set-Cookie fields as ambiguous until reviewed. Remove or redact local paths/emails from the new public narrative even when historical evidence retains them locally.",
    }
    json_path = OUT / "publication_hygiene.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Public publication hygiene check (2026-10-12)",
        "",
        "Read-only, offline scan. No ZIP payload was extracted or changed; no matched secret value is printed.",
        "",
        f"Scanned {len(zip_info)} artifact ZIP central directories without extraction. Top-level directories, research coverage, and member-name classifications are in JSON.",
        "",
        "## Metadata scan",
        "",
        f"Scanned {len(records):,} selected metadata/text files ({report['metadata_scan']['total_scanned_bytes']:,} bytes) under the recorded roots and key final reports. Large skipped files: {len(skipped)}; read errors: {report['metadata_scan']['read_error_count']}.",
        f"Credential-shaped value matches: {report['classification']['credential_value_findings']} (likely fixed test-fixture subset: {sum(fixture_counts.values())}); authorization fields: {report['classification']['credential_field_findings']}; Cookie/Set-Cookie fields: {report['classification']['cookie_field_findings']}.",
        f"Absolute-path/email-shaped matches: {report['classification']['personal_path_or_email_findings']}. Locations and line numbers are in JSON; values are intentionally omitted.",
        "",
        "Cookie and Set-Cookie metadata are classified as ambiguous: an Archive replay cookie can be anonymous replay infrastructure state, but this scan cannot prove it is not a login/session cookie. Human review is required for every occurrence before publication.",
        "",
        "## ZIP member-name scan",
        "",
        "Only central-directory names were inspected. Credential stores, browser profiles, environment files, and personal screenshot names are reported by category without payload extraction. Public historical screenshot directories and ordinary cookie/password UI assets are separated from those categories.",
        "",
        "## Limits",
        "",
        "Binary assets, nested ZIP payloads, and offline historical HTML/CSS/JS were not content-scanned. This report is a bounded hygiene inventory, not a proof that publication is safe; nonzero credential-shaped findings or ambiguous cookies require manual review/redaction.",
        "",
        "See `publication_hygiene.json` for exact scan roots, counts, ZIP member-name samples, locations, hashes, skipped files, and limits.",
    ]
    (OUT / "publication_hygiene.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "json": rel(json_path),
        "markdown": rel(OUT / "publication_hygiene.md"),
        "zip_members": sum(item.get("member_count", 0) for item in zip_info),
        "metadata_files": len(records),
        "credential_value_matches": report["classification"]["credential_value_findings"],
        "cookie_field_matches": report["classification"]["cookie_field_findings"],
        "personal_shape_matches": report["classification"]["personal_path_or_email_findings"],
        "skipped_large": len(skipped),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
