from __future__ import annotations

import hashlib
import html
import json
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
MANIFEST_REL = Path(".scratch/offline-navigation-20261015-v15/build-manifest.json")
SITE_ROOT = ROOT / ".scratch/offline-navigation-20261015-v15/site"
BASE_LEDGER_REL = Path("research/continuous-recovery-20261019/gallery-audit/coverage-after-rest10b/coverage-ledger.json")
PRIOR_JS_AUDIT_REL = Path("research/acquisition-2008/acceptance/js-static-reference-audit.json")
PRIOR_V20_AUDIT_REL = Path("research/continuous-recovery-20261016/local-audit/v20-next-assets/v20-next-assets-private-audit.json")
HARD_LIMIT_SECONDS = 180.0
EXPECTED_MANIFEST_SHA = "d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002"
EXPECTED_RECORDS = 8357

TEXT_EXTENSIONS = {".html", ".htm", ".xml", ".xsl", ".css", ".js", ".htc"}
TEXT_MIMES = {
    "text/html",
    "application/xhtml+xml",
    "application/xml",
    "text/xml",
    "text/css",
    "application/x-javascript",
    "application/javascript",
    "text/plain",
}
TEXT_KINDS = {"html", "menu_html", "js", "css", "xsl", "xml", "legacy_component", "support"}
URL_TOKEN_RE = re.compile(r"(?:(?:https?:)?//|/)[^\s<>'\"()]+", re.I)
SHOT_RE = re.compile(r"(?i)(?:^|[/_%.-])ss(?P<number>\d+)(?P<thumb>-thumb)?\.jpg(?:$|[?#&])")
ANY_SHOT_RE = re.compile(r"(?i)ss(?P<number>\d+)(?P<thumb>-thumb)?\.jpg")
HOST_RE = re.compile(r"(?i)https?://([^/:'\"<>\s]+)")
DYNAMIC_MARKERS = (
    "sourcedirectory",
    "shotlist",
    "filename",
    "numshots",
    "addshots",
    "replace(",
    "for(",
    "for (",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def binding(rel: str | Path, role: str | None = None) -> dict:
    p = ROOT / Path(rel)
    out = {"path": str(Path(rel).as_posix()), "exists": p.exists()}
    if p.exists() and p.is_file():
        b = p.read_bytes()
        out.update({"bytes": len(b), "sha256": sha256_bytes(b)})
    if role:
        out["role"] = role
    return out


def load_json(rel: str | Path):
    return json.loads((ROOT / Path(rel)).read_text(encoding="utf-8"))


def normalize_line(line: str) -> str:
    value = html.unescape(line)
    value = value.replace("\\/", "/")
    value = value.replace("\\x2F", "/").replace("\\x2f", "/")
    value = value.replace("\\u002F", "/").replace("\\u002f", "/")
    # Decode repeatedly only while the value changes. This handles %2F in
    # URL-list JSON without turning an ordinary literal into a new guess.
    for _ in range(2):
        new_value = unquote(value)
        if new_value == value:
            break
        value = new_value
    return value


def origin_for_token(token: str, manifest_record: dict) -> tuple[str | None, str]:
    try:
        if token.startswith("//"):
            parsed = urlsplit("http:" + token)
            return parsed.hostname, "absolute_scheme_relative"
        if token.lower().startswith("http://") or token.lower().startswith("https://"):
            return urlsplit(token).hostname, "absolute_url"
    except ValueError:
        # Old JS occasionally contains malformed bracketed strings. Preserve
        # the literal and use a best-effort host marker instead of losing the
        # whole text file from the scan.
        match = HOST_RE.search(token)
        return (match.group(1) if match else None), "malformed_absolute_literal"
    return manifest_record.get("origin_namespace"), "relative_path"


def clean_token(token: str) -> str:
    return token.rstrip(".,;:!?]}")


def path_for_token(token: str) -> str:
    try:
        if token.startswith("//"):
            return urlsplit("http:" + token).path
        if token.lower().startswith("http://") or token.lower().startswith("https://"):
            return urlsplit(token).path
    except ValueError:
        return token.split("?", 1)[0].split("#", 1)[0]
    return token.split("?", 1)[0].split("#", 1)[0]


def context_kind(line: str) -> str:
    lower = line.lower()
    if "popupomega" in lower or "javascript:" in lower:
        return "js_or_href_literal"
    if "href" in lower:
        return "href"
    if "<img" in lower and "src" in lower:
        return "img_src"
    if "url(" in lower:
        return "css_url"
    if any(marker in lower for marker in ("sourcedirectory", "shotlist", "filename", "numshots", "addshots")):
        return "js_generated_rule"
    return "literal_text_or_other"


def manifest_kind(record: dict) -> str:
    route = str(record.get("route") or "")
    role = str(record.get("role") or "")
    kind = str(record.get("kind") or "")
    if kind == "generated_placeholder" or route.startswith("/__offline/") or "placeholder" in role.lower():
        return "generated_placeholder"
    if record.get("transformed"):
        return "derived_transformed"
    if route.startswith("/_origins/"):
        return "origin_overlay"
    return "source_or_copied_text"


def text_record(record: dict, actual_bytes: bytes) -> dict:
    route = str(record.get("route") or "")
    output_path = str(record.get("output_path") or "")
    ext = Path(route).suffix.lower()
    mime = str(record.get("mime") or "").split(";", 1)[0].lower()
    return {
        "route": route,
        "output_path": output_path,
        "origin_namespace": record.get("origin_namespace"),
        "source_base_url": record.get("source_base_url"),
        "source_local_path": record.get("source_local_path"),
        "source_map_path": record.get("source_map_path"),
        "kind": record.get("kind"),
        "role": record.get("role"),
        "mime": mime,
        "extension": ext,
        "bytes": len(actual_bytes),
        "sha256": sha256_bytes(actual_bytes),
        "manifest_derived_sha256": record.get("derived_sha256"),
        "manifest_derived_length": record.get("derived_length"),
        "actual_timestamp": record.get("actual_timestamp"),
        "requested_timestamp": record.get("requested_timestamp"),
        "supplement": bool(record.get("supplement")),
        "transformed": bool(record.get("transformed")),
        "origin_overlay": route.startswith("/_origins/") or "/_origins/" in output_path,
        "derivation_class": manifest_kind(record),
    }


def is_text_record(record: dict) -> bool:
    route = str(record.get("route") or "")
    ext = Path(route).suffix.lower()
    mime = str(record.get("mime") or "").split(";", 1)[0].lower()
    return ext in TEXT_EXTENSIONS or mime in TEXT_MIMES or record.get("kind") in TEXT_KINDS


def find_target_matches(normalized: str, raw_line: str, line_no: int, record: dict, targets: dict[str, dict]) -> list[dict]:
    hits: list[dict] = []
    lower = normalized.lower()
    if "ss" not in lower:
        return hits
    dynamic = any(marker in lower for marker in DYNAMIC_MARKERS)
    tokens = [clean_token(m.group(0)) for m in URL_TOKEN_RE.finditer(normalized)]
    for directory, target in targets.items():
        if directory.lower() not in lower:
            continue
        local_tokens = [token for token in tokens if directory.lower() in token.lower()]
        if not local_tokens:
            # HTML entities or JS escaping can leave a path embedded in a
            # quoted string. Retain the exact source line and a bounded context.
            local_tokens = [normalized[max(0, lower.index(directory.lower()) - 80): lower.index(directory.lower()) + len(directory) + 160]]
        for token in local_tokens:
            token_path = path_for_token(token)
            shots = list(ANY_SHOT_RE.finditer(token_path))
            if not shots:
                continue
            shot = shots[-1]
            is_thumb = bool(shot.group("thumb")) or "/thumbs/" in token_path.lower()
            derivation = manifest_kind(record)
            origin_host, token_kind = origin_for_token(token, record)
            if dynamic:
                classification = "generated_or_dynamic_rule"
            elif derivation == "generated_placeholder":
                classification = "local_placeholder_or_repair_generated"
            elif is_thumb:
                classification = "nested_preview_or_thumb"
            else:
                classification = "concrete_native_literal"
            if origin_host == "www.worldofwarcraft.com":
                host_class = "canonical_www_worldofwarcraft"
            elif origin_host:
                host_class = "noncanonical_or_related_origin"
            else:
                host_class = "relative_unresolved_host"
            hits.append({
                "target_gallery": target["gallery"],
                "target_source_directory": directory,
                "shot_number": int(shot.group("number")),
                "thumb": is_thumb,
                "token": token,
                "decoded_line": normalized.strip(),
                "raw_line": raw_line.rstrip("\r\n"),
                "line": line_no,
                "context_kind": context_kind(normalized),
                "token_kind": token_kind,
                "origin_host": origin_host,
                "host_class": host_class,
                "classification": classification,
                "source_file": {
                    "route": record.get("route"),
                    "output_path": record.get("output_path"),
                    "origin_namespace": record.get("origin_namespace"),
                    "role": record.get("role"),
                    "kind": record.get("kind"),
                    "derivation_class": derivation,
                    "transformed": bool(record.get("transformed")),
                    "origin_overlay": bool(record.get("origin_overlay")),
                },
            })
    return hits


def find_alias_matches(normalized: str, raw_line: str, line_no: int, record: dict, target_dirs: set[str]) -> list[dict]:
    hits: list[dict] = []
    if "ss" not in normalized.lower():
        return hits
    dynamic = any(marker in normalized.lower() for marker in DYNAMIC_MARKERS)
    for m in URL_TOKEN_RE.finditer(normalized):
        token = clean_token(m.group(0))
        token_path = path_for_token(token)
        if not ANY_SHOT_RE.search(token_path):
            continue
        if "/images/" not in token_path.lower() and "/pvp/" not in token_path.lower():
            continue
        lower_path = token_path.lower()
        known = any(directory.lower() in lower_path for directory in target_dirs)
        if known:
            continue
        shot = list(ANY_SHOT_RE.finditer(token_path))[-1]
        origin_host, token_kind = origin_for_token(token, record)
        prefix = token_path[: shot.start()]
        derivation = manifest_kind(record)
        if dynamic:
            classification = "generated_or_dynamic_alias_rule"
        elif derivation == "generated_placeholder":
            classification = "local_placeholder_or_repair_generated_alias"
        elif shot.group("thumb") or "/thumbs/" in lower_path:
            classification = "nested_preview_or_alias"
        else:
            classification = "concrete_unmapped_alias_literal"
        hits.append({
            "alias_directory": prefix,
            "token": token,
            "decoded_line": normalized.strip(),
            "raw_line": raw_line.rstrip("\r\n"),
            "line": line_no,
            "shot_number": int(shot.group("number")),
            "thumb": bool(shot.group("thumb")) or "/thumbs/" in lower_path,
            "context_kind": context_kind(normalized),
            "token_kind": token_kind,
            "origin_host": origin_host,
            "origin_namespace": record.get("origin_namespace"),
            "classification": classification,
            "source_file": {
                "route": record.get("route"),
                "output_path": record.get("output_path"),
                "role": record.get("role"),
                "kind": record.get("kind"),
                "derivation_class": derivation,
                "transformed": bool(record.get("transformed")),
                "origin_overlay": bool(record.get("origin_overlay")),
            },
        })
    return hits


def stable_dedupe(items: list[dict], keys: tuple[str, ...]) -> list[dict]:
    seen = set()
    output = []
    for item in items:
        key = tuple(item.get(k) if k in item else json.dumps(item.get("source_file"), sort_keys=True) for k in keys)
        if key not in seen:
            seen.add(key)
            output.append(item)
    return output


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    started = time.monotonic()
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = ROOT / MANIFEST_REL
    manifest_bytes = manifest_path.read_bytes()
    manifest_sha = sha256_bytes(manifest_bytes)
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    if manifest_sha != EXPECTED_MANIFEST_SHA:
        raise RuntimeError(f"Source15 manifest SHA changed: {manifest_sha}")
    if len(manifest.get("files", [])) != EXPECTED_RECORDS:
        raise RuntimeError(f"Source15 manifest records changed: {len(manifest.get('files', []))}")
    base = load_json(BASE_LEDGER_REL)
    targets = {
        row["source_evidence"]["source_directory"]: {
            "gallery": row["gallery"],
            "registry_rank": row["registry_rank"],
            "source_page_route": row["source_page_route"],
        }
        for row in base["rows"]
    }
    target_dirs = set(targets)
    selected = [record for record in manifest["files"] if is_text_record(record)]
    text_inventory: list[dict] = []
    known_hits: list[dict] = []
    alias_hits: list[dict] = []
    errors: list[dict] = []
    manifest_mismatches: list[dict] = []
    replacements = 0
    total_text_bytes = 0
    scanned = 0
    timed_out = False
    for record in selected:
        if time.monotonic() - started >= HARD_LIMIT_SECONDS:
            timed_out = True
            break
        output_rel = Path(record["output_path"])
        p = ROOT / output_rel
        try:
            raw = p.read_bytes()
            total_text_bytes += len(raw)
            scanned += 1
            actual = text_record(record, raw)
            text_inventory.append(actual)
            if actual["manifest_derived_length"] is not None and actual["manifest_derived_length"] != len(raw):
                manifest_mismatches.append({"path": str(output_rel.as_posix()), "kind": "length", "manifest": actual["manifest_derived_length"], "actual": len(raw)})
            if actual["manifest_derived_sha256"] and actual["manifest_derived_sha256"] != actual["sha256"]:
                manifest_mismatches.append({"path": str(output_rel.as_posix()), "kind": "sha256", "manifest": actual["manifest_derived_sha256"], "actual": actual["sha256"]})
            text = raw.decode("utf-8", errors="replace")
            replacements += text.count("\ufffd")
            for line_no, raw_line in enumerate(text.splitlines(), 1):
                normalized = normalize_line(raw_line)
                if not normalized.strip():
                    continue
                known_hits.extend(find_target_matches(normalized, raw_line, line_no, actual, targets))
                alias_hits.extend(find_alias_matches(normalized, raw_line, line_no, actual, target_dirs))
        except Exception as exc:
            errors.append({"path": str(output_rel.as_posix()), "error_type": type(exc).__name__, "error": str(exc)})
    elapsed = time.monotonic() - started
    if scanned < len(selected) and elapsed < HARD_LIMIT_SECONDS:
        timed_out = True

    known_hits = stable_dedupe(known_hits, ("target_gallery", "token", "line", "classification", "raw_line"))
    alias_hits = stable_dedupe(alias_hits, ("alias_directory", "token", "line", "classification", "raw_line"))
    concrete_native = [h for h in known_hits if h["classification"] == "concrete_native_literal"]
    nested_preview = [h for h in known_hits if h["classification"] == "nested_preview_or_thumb"]
    generated_rules = [h for h in known_hits if h["classification"] == "generated_or_dynamic_rule"]
    generated_placeholders = [h for h in known_hits if h["classification"] == "local_placeholder_or_repair_generated"]
    alias_concrete = [h for h in alias_hits if h["classification"] == "concrete_unmapped_alias_literal"]
    alias_nested = [h for h in alias_hits if h["classification"] == "nested_preview_or_alias"]
    by_gallery = defaultdict(lambda: {"native": 0, "nested": 0, "dynamic": 0, "placeholder": 0})
    for hit in known_hits:
        gallery = hit["target_gallery"]
        if hit["classification"] == "concrete_native_literal":
            by_gallery[gallery]["native"] += 1
        elif hit["classification"] == "nested_preview_or_thumb":
            by_gallery[gallery]["nested"] += 1
        elif hit["classification"] == "generated_or_dynamic_rule":
            by_gallery[gallery]["dynamic"] += 1
        elif hit["classification"] == "local_placeholder_or_repair_generated":
            by_gallery[gallery]["placeholder"] += 1

    manifest_hosts = Counter(record.get("origin_namespace") for record in selected)
    manifest_roles = Counter(record.get("role") for record in selected)
    manifest_kinds = Counter(record.get("kind") for record in selected)
    manifest_derivations = Counter(item.get("derivation_class") for item in text_inventory)
    manifest_origin_overlays = sum(1 for item in text_inventory if item.get("origin_overlay"))
    source15_files = {
        "manifest": binding(MANIFEST_REL, "frozen Source15 8,357-record manifest"),
        "base_gallery_ledger": binding(BASE_LEDGER_REL, "known 50 gallery target directories"),
    }
    prior_scans = [
        {
            "path": str(PRIOR_JS_AUDIT_REL.as_posix()),
            "binding": binding(PRIOR_JS_AUDIT_REL, "prior 28-source JS/HTC static audit"),
            "reused_as_full_manifest_scan": False,
            "reason": "Its declared scope is 28 JS/HTC sources and excludes ordinary HTML/XML/HTM navigation links; it is not a full 8,357-record text scan.",
        },
        {
            "path": str(PRIOR_V20_AUDIT_REL.as_posix()),
            "binding": binding(PRIOR_V20_AUDIT_REL, "prior v20 missing-marker audit"),
            "reused_as_full_manifest_scan": False,
            "reason": "Its scope is v20 missing-image markers and 1,049 text files, not all Source15 manifest text records or cross-references.",
        },
    ]
    scan = {
        "schema": "wow-recovery.source15-full-text-crossrefs.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "network_requests": 0,
        "network_performed": False,
        "hard_limit_seconds": HARD_LIMIT_SECONDS,
        "elapsed_seconds": round(elapsed, 6),
        "timed_out": timed_out,
        "scope": {
            "manifest_records": EXPECTED_RECORDS,
            "manifest_text_records_selected": len(selected),
            "manifest_text_records_scanned": scanned,
            "text_bytes_scanned": total_text_bytes,
            "selected_types": ["HTML", "XML", "XSL", "CSS", "JS", "HTM", "HTC"],
            "derived_site_root": ".scratch/offline-navigation-20261015-v15/site",
            "includes_origin_overlays": True,
            "excludes": ["binary image/SWF/SVG records", "source-local .bin payloads", "network requests", "redirect/replay", "full-site paths outside the manifest"],
        },
        "input_bindings": source15_files,
        "prior_scan_reconciliation": prior_scans,
        "selection_counts": {
            "text_records_selected": len(selected),
            "text_records_scanned": scanned,
            "read_errors": len(errors),
            "manifest_byte_or_sha_mismatches": len(manifest_mismatches),
            "utf8_replacement_character_count": replacements,
            "origin_overlay_text_records": manifest_origin_overlays,
            "generated_placeholder_text_records": manifest_derivations.get("generated_placeholder", 0),
            "derived_transformed_text_records": manifest_derivations.get("derived_transformed", 0),
            "source_or_copied_text_records": manifest_derivations.get("source_or_copied_text", 0),
        },
        "manifest_text_host_counts": dict(manifest_hosts),
        "manifest_text_kind_counts": dict(manifest_kinds),
        "manifest_text_role_counts": dict(manifest_roles),
        "text_inventory": text_inventory,
        "known_gallery_reference_summary": {
            "concrete_native_literal_count": len(concrete_native),
            "nested_preview_or_thumb_count": len(nested_preview),
            "generated_or_dynamic_rule_count": len(generated_rules),
            "placeholder_or_repair_generated_count": len(generated_placeholders),
            "by_gallery": dict(by_gallery),
        },
        "known_gallery_reference_hits": known_hits,
        "concrete_native_candidates": concrete_native,
        "nested_preview_hits": nested_preview,
        "generated_rule_hits": generated_rules,
        "placeholder_or_repair_hits": generated_placeholders,
        "unmapped_alias_summary": {
            "concrete_alias_count": len(alias_concrete),
            "nested_alias_count": len(alias_nested),
            "dynamic_alias_count": sum(1 for h in alias_hits if h["classification"] == "generated_or_dynamic_alias_rule"),
            "placeholder_alias_count": sum(1 for h in alias_hits if h["classification"] == "local_placeholder_or_repair_generated_alias"),
            "unique_alias_directories": sorted({h["alias_directory"] for h in alias_hits}),
        },
        "unmapped_alias_hits": alias_hits,
        "errors": errors,
        "manifest_mismatches": manifest_mismatches,
        "interpretation": {
            "native_rule": "Only literal ssN.jpg references under one of the 50 frozen source directories, from a non-generated file, count as concrete native candidates; ssN-thumb.jpg and /thumbs/ are nested previews.",
            "generated_rule": "sourceDirectory/shotList/filename/numShots/replace/loop lines are retained as dynamic rules and do not become concrete URLs.",
            "host_rule": "www.worldofwarcraft.com is canonical; forums.worldofwarcraft.com, armory.wow-europe.com, and other origins remain separate related-origin evidence.",
            "placeholder_rule": "Files marked generated_placeholder, __offline routes, or repair-derived output remain separate and cannot create native candidates.",
            "encoding_rule": "HTML entities, slash escapes, and URL percent encoding are decoded for matching while the original source line and token are preserved.",
        },
    }
    scan_path = OUT / "crossref-scan.json"
    write_json(scan_path, scan)

    grouped_native = defaultdict(list)
    for hit in concrete_native:
        grouped_native[hit["target_gallery"]].append(hit)
    grouped_alias = defaultdict(list)
    for hit in alias_concrete:
        grouped_alias[hit["alias_directory"]].append(hit)
    md_lines = [
        "# Source15 full text cross-reference audit",
        "",
        "This bounded audit read only manifest-selected text files and sent zero network requests.",
        "",
        f"- Frozen manifest: `{MANIFEST_REL.as_posix()}` SHA256 `{manifest_sha}`; records `{EXPECTED_RECORDS}`.",
        f"- Selected/scanned text files: `{len(selected)}` / `{scanned}`; bytes read `{total_text_bytes}`; elapsed `{elapsed:.3f}s` of `{HARD_LIMIT_SECONDS:.0f}s` hard limit.",
        f"- Origin overlay text files: `{manifest_origin_overlays}`; UTF-8 replacement characters: `{replacements}`; manifest mismatches: `{len(manifest_mismatches)}`.",
        f"- Network requests: `0`; timeout: `{timed_out}`.",
        "",
        "## Reference result",
        "",
        f"- Concrete literal native references under the 50 frozen directories: `{len(concrete_native)}`.",
        f"- Nested `/thumbs/` or `ssN-thumb.jpg` references: `{len(nested_preview)}`; retained separately and not promoted.",
        f"- Dynamic/generated builder rules: `{len(generated_rules)}`; not treated as concrete URLs.",
        f"- Placeholder/repair-generated hits: `{len(generated_placeholders)}`; excluded from native evidence.",
        f"- Concrete unmapped alias literals: `{len(alias_concrete)}`.",
        "",
        "## Concrete native candidates",
        "",
    ]
    if concrete_native:
        for gallery in sorted(grouped_native):
            md_lines.append(f"### {gallery}")
            for hit in grouped_native[gallery][:50]:
                sf = hit["source_file"]
                md_lines.append(f"- `{sf['route']}:{hit['line']}` `{hit['token']}` host={hit['origin_host'] or 'relative'} context={hit['context_kind']} class={hit['classification']}")
    else:
        md_lines.append("No concrete native literal was found under the 50 frozen source directories.")
    md_lines += [
        "",
        "## Unmapped alias clues",
        "",
    ]
    if alias_concrete:
        for alias in sorted(grouped_alias):
            md_lines.append(f"### `{alias}`")
            for hit in grouped_alias[alias][:50]:
                sf = hit["source_file"]
                md_lines.append(f"- `{sf['route']}:{hit['line']}` `{hit['token']}` host={hit['origin_host'] or 'relative'}")
    else:
        md_lines.append("No concrete unmapped native alias literal was found. Any dynamic or nested alias remains in crossref-scan.json with its classification.")
    md_lines += [
        "",
        "## Boundaries",
        "",
        "The scan includes `_origins` files but preserves their source host and overlay status. It does not treat forums, armory, guide previews, nested `/thumbs/`, placeholders, transformed repair output, or generated arrays as canonical native image evidence. A source-directory builder without a numeric literal remains a dynamic rule only.",
        "",
        "Prior JS/static and v20 audits were recorded but not reused as a full-manifest scan because their declared scopes are narrower than the frozen 8,357-record text subset.",
        "",
    ]
    md_path = OUT / "crossref-scan.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    receipt = {
        "schema": "wow-recovery.source15-full-text-crossrefs.receipt.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "network_requests": 0,
        "network_performed": False,
        "hard_limit_seconds": HARD_LIMIT_SECONDS,
        "elapsed_seconds": round(elapsed, 6),
        "timed_out": timed_out,
        "inputs": {
            "manifest": binding(MANIFEST_REL, "frozen 8,357-record Source15 manifest"),
            "base_gallery_ledger": binding(BASE_LEDGER_REL, "50 frozen gallery directories"),
            "prior_js_audit": binding(PRIOR_JS_AUDIT_REL, "prior narrower audit; not reused as complete"),
            "prior_v20_audit": binding(PRIOR_V20_AUDIT_REL, "prior narrower audit; not reused as complete"),
            "script": binding(Path(__file__).resolve().relative_to(ROOT), "cross-reference scanner"),
        },
        "outputs": {
            "scan": binding(scan_path.relative_to(ROOT), "full text cross-reference results"),
            "markdown": binding(md_path.relative_to(ROOT), "human-readable summary"),
        },
        "counts": scan["selection_counts"],
        "reference_summary": scan["known_gallery_reference_summary"],
        "alias_summary": scan["unmapped_alias_summary"],
        "validation": {
            "manifest_sha_expected": manifest_sha == EXPECTED_MANIFEST_SHA,
            "manifest_records_expected": len(manifest.get("files", [])) == EXPECTED_RECORDS,
            "all_selected_scanned": scanned == len(selected),
            "hard_limit_passed": elapsed <= HARD_LIMIT_SECONDS,
            "network_requests_zero": True,
            "no_read_errors": not errors,
            "no_manifest_mismatch": not manifest_mismatches,
        },
        "uncovered_or_decision_points": [
            "Concrete native candidates, if any, require root review of their source host, role, and page context; this scan does not create a download plan.",
            "A complete absence of literal native refs does not prove archive absence; it only bounds the local Source15 text evidence.",
            "No Wayback query, replay, redirect follow, or image acceptance was performed.",
        ],
    }
    receipt_path = OUT / "crossref-scan-receipt.json"
    write_json(receipt_path, receipt)

    # Reload generated JSON and assert the bounded result. This is local-only.
    json.loads(scan_path.read_text(encoding="utf-8"))
    json.loads(receipt_path.read_text(encoding="utf-8"))
    assert manifest_sha == EXPECTED_MANIFEST_SHA
    assert len(manifest.get("files", [])) == EXPECTED_RECORDS
    assert scanned == len(selected)
    assert elapsed <= HARD_LIMIT_SECONDS
    print(json.dumps({
        "manifest_sha256": manifest_sha,
        "manifest_records": len(manifest.get("files", [])),
        "selected_text_files": len(selected),
        "scanned_text_files": scanned,
        "text_bytes": total_text_bytes,
        "elapsed_seconds": round(elapsed, 6),
        "network_requests": 0,
        "concrete_native_count": len(concrete_native),
        "nested_preview_count": len(nested_preview),
        "dynamic_rule_count": len(generated_rules),
        "placeholder_count": len(generated_placeholders),
        "concrete_alias_count": len(alias_concrete),
        "outputs": {
            "scan": binding(scan_path.relative_to(ROOT)),
            "markdown": binding(md_path.relative_to(ROOT)),
            "receipt": binding(receipt_path.relative_to(ROOT)),
        },
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
