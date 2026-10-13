"""Complete non-disclosing credential-shape scan of the tracked release tree.

The scan is deliberately pinned to one Git tree rather than the working tree.
It reads every blob listed by ``git ls-tree`` through ``git cat-file --batch``;
the bytes are hashed and pattern-scanned for every tracked file, including
binary archive resources.  Reports contain locations, field names, hashes and
classifications only.  Matched values are never written.
"""

from __future__ import annotations

import bisect
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO, Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/github-publication-20261012"
JSON_OUT = OUT / "full-tree-hygiene.json"
MD_OUT = OUT / "full-tree-hygiene.md"
EXPECTED_HEAD = "b8d655ca51c4e4f73101e8e774eb46b37bda9c4f"
CHUNK_SIZE = 1024 * 1024
OVERLAP = 128 * 1024

# These are the five candidate matches found in the pinned tree and reviewed
# against their surrounding historical source.  Keep the review tied to exact
# paths/categories, and record only non-secret reasons and locations.
MANUAL_REVIEW_RULES: dict[str, dict[str, dict[str, Any]]] = {
    "offline/site/info/basics/mounts/special.html": {
        "credential_literal_assignment": {
            "review_status": "resolved_noncredential",
            "public_default_or_fixture": "fixed_historical_public_markup",
            "reason": "Three variables named avtoken/abtoken/warsongtoken hold public HTML tooltip labels for in-game battleground tokens; their literals are markup, not authentication material.",
            "authentication_privilege": False,
            "public_symbols": ["avtoken", "abtoken", "warsongtoken"],
        },
    },
    "offline/site/shared/wow-com/includes-client/detection.js": {
        "cookie_literal_assignment": {
            "review_status": "resolved_noncredential",
            "public_default_or_fixture": "fixed_historical_cookie_feature_probe",
            "reason": "document.cookie receives a fixed browser-capability probe value and is immediately read into is_cookie; it grants no authentication privilege.",
            "authentication_privilege": False,
        },
    },
    "offline/site/wrath/js/detection.js": {
        "cookie_literal_assignment": {
            "review_status": "resolved_noncredential",
            "public_default_or_fixture": "fixed_historical_cookie_feature_probe",
            "reason": "document.cookie receives a fixed browser-capability probe value and is immediately read into is_cookie; it grants no authentication privilege.",
            "authentication_privilege": False,
        },
    },
}

TEXT_SUFFIXES = {
    ".bat", ".cmd", ".csv", ".css", ".htm", ".html", ".js", ".json",
    ".jsonl", ".log", ".md", ".py", ".ps1", ".sha1", ".sha256", ".txt",
    ".toml", ".ts", ".xhtml", ".xml", ".xsl", ".yaml", ".yml",
}
BINARY_SUFFIXES = {
    ".7z", ".bin", ".bmp", ".cur", ".gif", ".ico", ".jpeg", ".jpg",
    ".mp3", ".pdf", ".png", ".swf", ".tar", ".webp", ".zip",
}


@dataclass(frozen=True)
class PatternSpec:
    category: str
    description: str
    regex: re.Pattern[bytes]
    field_group: str | None = None
    value_group: str | None = None


PATTERNS = [
    PatternSpec(
        "github_token_shape",
        "GitHub token prefixes gh* or github_pat_ followed by a token-shaped value",
        re.compile(rb"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    ),
    PatternSpec(
        "aws_access_key_id_shape",
        "AWS access-key identifier shape AKIA/ASIA plus sixteen uppercase characters",
        re.compile(rb"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ),
    PatternSpec(
        "jwt_shape",
        "three JWT-like base64url segments beginning with eyJ",
        re.compile(rb"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
    ),
    PatternSpec(
        "private_key_pem",
        "PEM private-key begin marker",
        re.compile(rb"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    ),
    PatternSpec(
        "authorization_bearer_value",
        "Authorization field carrying a Bearer value of at least eight token characters",
        re.compile(rb"(?i)\bauthorization\b\s*[:=]\s*[\"']?\s*bearer\s+[A-Za-z0-9+/=_\-.]{8,}"),
        field_group=None,
    ),
    PatternSpec(
        "authorization_basic_value",
        "Authorization field carrying a Basic value of at least eight encoded characters",
        re.compile(rb"(?i)\bauthorization\b\s*[:=]\s*[\"']?\s*basic\s+[A-Za-z0-9+/=_\-.]{8,}"),
    ),
    PatternSpec(
        "url_userinfo_value",
        "HTTP(S) URL containing a user:password@ authority",
        re.compile(rb"(?i)\bhttps?://[^/\s:@]{1,128}:[^@\s]{1,256}@"),
    ),
    PatternSpec(
        "credential_literal_assignment",
        "token/secret/password-like field assigned a quoted literal of at least eight characters",
        re.compile(
            rb"(?i)(?P<field>access[_-]?token|api[_-]?key|client[_-]?secret|passphrase|password|passwd|private[_-]?key|secret|token)"
            rb"\s*(?:[:=]|=>)\s*(?P<quote>[\"'])(?P<value>[^\"'\r\n]{8,})(?P=quote)"
        ),
        field_group="field",
        value_group="value",
    ),
    PatternSpec(
        "cookie_literal_assignment",
        "Cookie-like field assigned a quoted literal",
        re.compile(
            rb"(?i)(?P<field>(?:document\.)?cookie|set-cookie)\s*(?:[:=])\s*"
            rb"(?P<quote>[\"'])(?P<value>[^\"'\r\n]{3,})(?P=quote)"
        ),
        field_group="field",
        value_group="value",
    ),
    PatternSpec(
        "authorization_field_without_value",
        "Authorization field occurrence; separately checked for a token value",
        re.compile(rb"(?i)(?:[\"']?authorization[\"']?)\s*[:=]"),
    ),
    PatternSpec(
        "cookie_handling_field",
        "Cookie/Set-Cookie field or document.cookie handling code",
        re.compile(rb"(?i)(?:\bcookie\b|\bset-cookie\b|document\.cookie)"),
    ),
]


def run_git(*args: str, input_bytes: bytes | None = None) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=ROOT, input=input_bytes, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=True,
    ).stdout


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_repo_path(value: str) -> str:
    return value.replace("\\", "/").lstrip("./")


def tracked_tree(head: str) -> list[dict[str, str]]:
    raw = run_git("ls-tree", "-r", "-z", "--full-tree", head)
    records: list[dict[str, str]] = []
    for item in raw.split(b"\0"):
        if not item:
            continue
        metadata, raw_path = item.split(b"\t", 1)
        mode, object_type, object_id = metadata.split()
        records.append({
            "path": raw_path.decode("utf-8", "surrogateescape"),
            "mode": mode.decode("ascii"),
            "object_type": object_type.decode("ascii"),
            "object_id": object_id.decode("ascii"),
        })
    return records


def load_manifest(head: str) -> tuple[dict[str, list[dict[str, Any]]], str]:
    raw = run_git("show", f"{head}:offline/build-manifest.json")
    manifest = json.loads(raw)
    by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for section in ("files", "supplements"):
        for entry in manifest.get(section, []):
            if not isinstance(entry, dict):
                continue
            for key in ("output_path", "source_local_path", "local_path"):
                value = entry.get(key)
                if isinstance(value, str) and value:
                    by_path[normalize_repo_path(value)].append({
                        "section": section,
                        "kind": entry.get("kind"),
                        "role": entry.get("role"),
                        "source_sha256": entry.get("source_sha256"),
                        "derived_sha256": entry.get("derived_sha256"),
                        "route": entry.get("route"),
                        "path_field": key,
                    })
    return by_path, sha256_bytes(raw)


def context_class(path: str, binary: bool, manifest_entries: list[dict[str, Any]]) -> str:
    low = path.casefold()
    parts = set(low.split("/"))
    if parts & {"test", "tests", "fixtures", "fixture", "mock", "mocks", "examples", "example"}:
        return "fixed_fixture_or_example"
    if manifest_entries and binary:
        return "manifest_backed_archive_resource"
    if low.startswith("offline/site/"):
        return "historical_public_archive_content"
    if low.startswith("offline/source-") or low.startswith("backups/"):
        return "archived_source_payload"
    if low.startswith("artifacts/") and Path(low).suffix in BINARY_SUFFIXES:
        return "release_or_archive_package"
    return "repository_source_or_metadata"


def type_hint(path: str, prefix: bytes) -> tuple[str, bool]:
    suffix = Path(path).suffix.casefold()
    if suffix in BINARY_SUFFIXES:
        return "binary", True
    if suffix in TEXT_SUFFIXES:
        return "text", False
    if b"\x00" in prefix:
        return "binary", True
    if not prefix:
        return "empty", False
    printable = sum(1 for byte in prefix if byte in (9, 10, 13) or 32 <= byte < 127)
    is_binary = printable / len(prefix) < 0.70
    return ("binary" if is_binary else "text/unknown"), is_binary


def literal_status(value: bytes) -> str:
    try:
        text = value.decode("utf-8", "replace").strip().casefold()
    except Exception:
        text = ""
    if not text:
        return "empty_or_unreadable"
    if re.fullmatch(r"(?:changeme|change_me|dummy|example|fake|foo|bar|none|null|password|replace(?:_me)?|secret|test|token|undefined|unknown|your[_ -]?[^ ]+|<[^>]+>|\$\{[^}]+\}|\{\{[^}]+\}\}|x{3,}|\.{3,})", text):
        return "placeholder_or_example"
    return "literal_candidate_requires_review"


def scan_blob(stream: BinaryIO, size: int, path: str, manifest_entries: list[dict[str, Any]]) -> dict[str, Any]:
    digest = hashlib.sha256()
    total = 0
    prefix = bytearray()
    text_hint = Path(path).suffix.casefold() in TEXT_SUFFIXES
    line_starts = [0]
    tail = b""
    seen: set[tuple[str, int]] = set()
    match_data: dict[str, dict[str, Any]] = {}

    def add_match(spec: PatternSpec, match: re.Match[bytes], global_offset: int) -> None:
        key = (spec.category, global_offset)
        if key in seen:
            return
        seen.add(key)
        item = match_data.setdefault(spec.category, {
            "count": 0, "byte_offsets": [], "line_numbers": [], "field_names": [],
            "literal_statuses": [], "description": spec.description,
        })
        item["count"] += 1
        if len(item["byte_offsets"]) < 20:
            item["byte_offsets"].append(global_offset)
        if text_hint and len(item["line_numbers"]) < 20:
            item["line_numbers"].append(bisect.bisect_right(line_starts, global_offset))
        if spec.field_group and match.groupdict().get(spec.field_group) is not None:
            field = match.group(spec.field_group).decode("ascii", "replace")
            if field not in item["field_names"]:
                item["field_names"].append(field)
        if spec.value_group and match.groupdict().get(spec.value_group) is not None:
            item["literal_statuses"].append(literal_status(match.group(spec.value_group)))

    while total < size:
        chunk = stream.read(min(CHUNK_SIZE, size - total))
        if not chunk:
            raise IOError(f"short git object for {path}: {total} of {size} bytes")
        if len(prefix) < 4096:
            prefix.extend(chunk[: 4096 - len(prefix)])
        digest.update(chunk)
        base = total - len(tail)
        window = tail + chunk
        for spec in PATTERNS:
            for match in spec.regex.finditer(window):
                add_match(spec, match, base + match.start())
        if text_hint:
            line_starts.extend(total + index + 1 for index, byte in enumerate(chunk) if byte == 10)
        total += len(chunk)
        tail = window[-OVERLAP:]

    content_type, binary = type_hint(path, bytes(prefix))
    context = context_class(path, binary, manifest_entries)
    findings = []
    for category in sorted(match_data):
        item = match_data[category]
        statuses = sorted(set(item.pop("literal_statuses", [])))
        item["field_names"] = sorted(item["field_names"])
        item["classification"] = context
        if statuses:
            item["literal_statuses"] = statuses
        findings.append({"category": category, **item})
    manifest_summary = None
    if manifest_entries:
        manifest_summary = {
            "entry_count": len(manifest_entries),
            "sections": sorted({str(item.get("section")) for item in manifest_entries}),
            "kinds": sorted({str(item.get("kind")) for item in manifest_entries if item.get("kind")}),
            "roles": sorted({str(item.get("role")) for item in manifest_entries if item.get("role")}),
            "source_sha256_samples": sorted({str(item.get("source_sha256")) for item in manifest_entries if item.get("source_sha256")})[:10],
            "derived_sha256_samples": sorted({str(item.get("derived_sha256")) for item in manifest_entries if item.get("derived_sha256")})[:10],
        }
    return {
        "path": path,
        "git_mode": None,
        "git_object_id": None,
        "git_object_type": None,
        "bytes": total,
        "sha256": digest.hexdigest(),
        "content_type": content_type,
        "binary": binary,
        "manifest": manifest_summary,
        "context_class": context,
        "findings": findings,
    }


def scan(head: str) -> dict[str, Any]:
    tree = tracked_tree(head)
    manifest_by_path, manifest_sha = load_manifest(head)
    reports: list[dict[str, Any]] = []
    object_errors: list[dict[str, str]] = []
    type_counts: Counter[str] = Counter()
    context_counts: Counter[str] = Counter()
    finding_counts: Counter[str] = Counter()
    finding_file_counts: Counter[str] = Counter()
    classification_counts: Counter[str] = Counter()
    reviewed_findings: list[dict[str, Any]] = []
    total_bytes = 0
    cat = subprocess.Popen(
        ["git", "cat-file", "--batch"], cwd=ROOT,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    assert cat.stdin is not None and cat.stdout is not None
    try:
        for entry in tree:
            path = entry["path"]
            try:
                cat.stdin.write((entry["object_id"] + "\n").encode("ascii"))
                cat.stdin.flush()
                header = cat.stdout.readline()
                if not header:
                    raise IOError("git cat-file ended before object header")
                parts = header.rstrip(b"\n").split()
                if len(parts) != 3 or parts[0].decode("ascii", "replace") != entry["object_id"]:
                    raise IOError(f"unexpected object header for {path}")
                object_type = parts[1].decode("ascii", "replace")
                size = int(parts[2])
                if object_type != "blob":
                    raise IOError(f"tracked entry is not a blob: {object_type}")
                record = scan_blob(cat.stdout, size, path, manifest_by_path.get(normalize_repo_path(path), []))
                terminator = cat.stdout.read(1)
                if terminator != b"\n":
                    raise IOError(f"missing cat-file object terminator for {path}")
                record["git_mode"] = entry["mode"]
                record["git_object_id"] = entry["object_id"]
                record["git_object_type"] = object_type
                reports.append(record)
                total_bytes += record["bytes"]
                type_counts[record["content_type"]] += 1
                context_counts[record["context_class"]] += 1
                for finding in record["findings"]:
                    category = finding["category"]
                    finding_counts[category] += finding["count"]
                    finding_file_counts[category] += 1
                    classification_counts[finding["classification"]] += finding["count"]
                    rule = MANUAL_REVIEW_RULES.get(path, {}).get(category)
                    if rule:
                        finding["review_outcome"] = dict(rule)
                        reviewed_findings.append({
                            "path": path,
                            "category": category,
                            "count": finding["count"],
                            "byte_offsets": finding.get("byte_offsets", []),
                            "line_numbers": finding.get("line_numbers", []),
                            "field_names": finding.get("field_names", []),
                            **rule,
                        })
            except Exception as exc:  # preserve a hard error; never call it clean
                object_errors.append({"path": path, "error_type": type(exc).__name__, "error_summary": str(exc)[:300]})
                # If scan_blob consumed an incomplete object, the batch stream
                # cannot be safely resynchronised.  Stop with an explicit error.
                break
    finally:
        try:
            cat.stdin.close()
        except Exception:
            pass
        cat.wait(timeout=30)
    candidate_findings = [
        (record, finding)
        for record in reports
        for finding in record["findings"]
        if finding["category"] not in {"authorization_field_without_value", "cookie_handling_field"}
    ]
    unresolved = sum(
        1 for _record, finding in candidate_findings
        if not finding.get("review_outcome") or finding["review_outcome"].get("authentication_privilege") is not False
    )
    report = {
        "schema_version": 1,
        "kind": "github_publication_full_tree_hygiene_20261012",
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "network_performed": False,
        "head": head,
        "head_verified": head == EXPECTED_HEAD,
        "tracked_file_count": len(tree),
        "scanned_file_count": len(reports),
        "total_tracked_bytes": total_bytes,
        "total_scanned_bytes": sum(item["bytes"] for item in reports),
        "skipped_file_count": 0,
        "read_error_count": len(object_errors),
        "object_errors": object_errors,
        "complete_byte_scan": not object_errors and len(reports) == len(tree),
        "overlap_bytes_for_cross_chunk_patterns": OVERLAP,
        "pattern_rules": [{"category": p.category, "description": p.description} for p in PATTERNS],
        "manifest_source": {
            "path": "offline/build-manifest.json",
            "sha256": manifest_sha,
            "mapped_path_count": len(manifest_by_path),
            "note": "Binary files with matching manifest paths are classified as manifest-backed archive resources; source and derived SHA fields are metadata only.",
        },
        "type_counts": dict(sorted(type_counts.items())),
        "context_counts": dict(sorted(context_counts.items())),
        "finding_counts": dict(sorted(finding_counts.items())),
        "finding_file_counts": dict(sorted(finding_file_counts.items())),
        "finding_classification_counts": dict(sorted(classification_counts.items())),
        "credential_value_candidate_count": sum(
            count for category, count in finding_counts.items()
            if category not in {"authorization_field_without_value", "cookie_handling_field"}
        ),
        "unresolved_credential_findings": unresolved,
        "manual_review": {
            "reviewed_candidate_count": sum(item["count"] for item in reviewed_findings),
            "unresolved_credential_findings": unresolved,
            "findings": reviewed_findings,
            "note": "Manual review is restricted to the exact five candidate matches in this pinned HEAD; values are not recorded.",
        },
        "cookie_policy": {
            "cookie_handling_code_is_not_a_credential": True,
            "cookie_literal_assignments_are_separately_reported": True,
            "values_emitted": False,
            "note": "Historical replay scripts may read or write document.cookie. Only quoted cookie literals are candidate values; handling-only occurrences are not classified as credentials.",
        },
        "files": reports,
    }
    return report


def write_outputs(report: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    finding_files = [item for item in report["files"] if item["findings"]]
    lines = [
        "# Full tracked-tree publication hygiene scan",
        "",
        f"Pinned Git tree: `{report['head']}` (verified expected HEAD: `{report['head_verified']}`).",
        "The scan is byte-complete over the exact tracked Git tree, including binary files. It uses `git ls-tree` and `git cat-file --batch`; it does not inspect mutable untracked files and does not access the network.",
        "",
        "## Coverage",
        "",
        f"- Tracked files: {report['tracked_file_count']:,}; scanned: {report['scanned_file_count']:,}; skipped: {report['skipped_file_count']}; read/object errors: {report['read_error_count']}",
        f"- Tracked/scanned bytes: {report['total_tracked_bytes']:,} / {report['total_scanned_bytes']:,}",
        f"- Complete byte scan: `{report['complete_byte_scan']}`; every file record includes Git object ID, byte length and SHA256.",
        f"- Findings in {len(finding_files):,} files; matched values are never emitted.",
        "",
        "## Credential-shape result",
        "",
        f"Candidate value-shaped matches (excluding handling-only Authorization/Cookie fields): **{report['credential_value_candidate_count']}**; exact reviewed unresolved credential findings: **{report['unresolved_credential_findings']}**.",
        "",
    ]
    if report["finding_counts"]:
        for category, count in sorted(report["finding_counts"].items()):
            lines.append(f"- `{category}`: {count} matches in {report['finding_file_counts'].get(category, 0)} files")
    else:
        lines.append("- No configured pattern matches.")
    lines.extend([
        "",
        "Cookie handling code is separated from cookie literal assignments. Historical `document.cookie` or `Set-Cookie` handling is not called a credential; any literal assignment remains a review candidate. Fixed fixtures/examples and historical public archive content are classified by path/context in the JSON without publishing values.",
        "",
        "## Match locations",
        "",
        "The JSON lists category, counts, byte offsets, line numbers where the file is text-like, field names, literal status, and context class. It intentionally contains no matched secret, token, password, cookie value, or line text.",
        "",
    ])
    for record in finding_files:
        lines.append(f"### `{record['path']}`")
        lines.append("")
        lines.append(f"Context: `{record['context_class']}`; bytes: {record['bytes']:,}; SHA256: `{record['sha256']}`.")
        for finding in record["findings"]:
            location = ", ".join(str(x) for x in finding.get("byte_offsets", [])) or "none"
            line_numbers = ", ".join(str(x) for x in finding.get("line_numbers", [])) or "n/a"
            fields = ", ".join(finding.get("field_names", [])) or "n/a"
            statuses = ", ".join(finding.get("literal_statuses", [])) or "n/a"
            lines.append(f"- `{finding['category']}` count={finding['count']}; byte offsets={location}; lines={line_numbers}; fields={fields}; literal status={statuses}; classification={finding['classification']}")
            if finding.get("review_outcome"):
                outcome = finding["review_outcome"]
                lines.append(f"  - Review: `{outcome['review_status']}`; public/default or fixture class=`{outcome['public_default_or_fixture']}`; authentication privilege=`{outcome['authentication_privilege']}`; reason: {outcome['reason']}")
        lines.append("")
    lines.extend([
        "## Archive-resource classification",
        "",
        "Binary matches are still scanned in full. When a path is present in `offline/build-manifest.json`, its record contains the manifest section, kind/role and source/derived SHA samples, classifying it as a manifest-backed archive resource rather than silently treating historical bytes as repository credentials.",
        "",
        "## Limits",
        "",
        f"Pattern matches crossing chunk boundaries use a {report['overlap_bytes_for_cross_chunk_patterns']:,}-byte overlap; all bytes are nevertheless hashed and read. This is a shape scan, not proof that a human-readable string is an active credential. Any nonzero candidate value requires human review before upload.",
    ])
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    actual_head = run_git("rev-parse", "HEAD").decode("ascii").strip()
    if actual_head != EXPECTED_HEAD:
        raise SystemExit(f"HEAD changed: expected {EXPECTED_HEAD}, got {actual_head}")
    report = scan(actual_head)
    write_outputs(report)
    print(json.dumps({
        "json": rel(JSON_OUT),
        "markdown": rel(MD_OUT),
        "head": report["head"],
        "tracked": report["tracked_file_count"],
        "scanned": report["scanned_file_count"],
        "bytes": report["total_scanned_bytes"],
        "complete": report["complete_byte_scan"],
        "read_errors": report["read_error_count"],
        "credential_value_candidates": report["credential_value_candidate_count"],
        "unresolved_credential_findings": report["unresolved_credential_findings"],
        "finding_counts": report["finding_counts"],
    }, ensure_ascii=False, sort_keys=True))
    return 0 if report["complete_byte_scan"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
