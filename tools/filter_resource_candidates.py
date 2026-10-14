#!/usr/bin/env python3
"""Filter resource candidates against the current origin-aware offline routes.

The filter is deliberately local-only.  It does not inspect or delete source
files and it never treats a same-path asset from another host as equivalent to
the primary World of Warcraft origin.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import offline_mirror


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "offline/build-manifest.json"


class CandidateFilterError(ValueError):
    """Raised when an input or manifest cannot be safely interpreted."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CandidateFilterError(f"{label} does not exist: {path}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CandidateFilterError(f"cannot read {label}: {path}: {exc}") from exc


def _mime_base(value: Any) -> str:
    return str(value or "").split(";", 1)[0].strip().casefold()


def _is_valid_image_record(record: Any) -> bool:
    if not isinstance(record, dict):
        return False
    return str(record.get("kind", "")).casefold() == "image" and _mime_base(record.get("mime")).startswith("image/")


def _candidate_url(item: Any) -> tuple[str | None, str | None, str | None]:
    if not isinstance(item, dict):
        return None, None, "candidate is not an object"
    for field in ("logical_url", "url", "original"):
        value = item.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip(), field, None
    return None, None, "missing logical_url/url/original"


def _validate_url(value: str) -> str | None:
    """Return an error string for an unsafe URL, or None when it is usable."""

    try:
        parsed = urllib.parse.urlsplit(value)
    except ValueError as exc:
        return f"malformed URL: {exc}"
    if parsed.scheme.casefold() not in {"http", "https"}:
        return "URL scheme must be http or https"
    if not parsed.netloc or not parsed.hostname:
        return "URL must have a host"
    if parsed.username is not None or parsed.password is not None:
        return "URL credentials are not allowed"
    try:
        port = parsed.port
    except ValueError as exc:
        return f"invalid URL port: {exc}"
    if port is not None and not 1 <= port <= 65535:
        return "URL port is outside 1..65535"
    if any(ord(char) < 0x20 or ord(char) == 0x7F for char in value):
        return "URL contains a control character"
    if "\\" in parsed.path:
        return "URL path contains a backslash"
    path = parsed.path or "/"
    decoded_path = urllib.parse.unquote(path)
    if "\\" in decoded_path or any(ord(char) < 0x20 or ord(char) == 0x7F for char in decoded_path):
        return "URL path contains an unsafe decoded character"
    if path.startswith("//") or decoded_path.startswith("//"):
        return "URL path has a double leading slash"
    if any(segment in {".", ".."} for segment in path.split("/") + decoded_path.split("/")):
        return "URL path contains a dot segment"
    host = parsed.hostname
    if any(char.isspace() for char in host):
        return "URL host contains whitespace"
    return None


def candidate_route(value: str) -> str:
    error = _validate_url(value)
    if error:
        raise CandidateFilterError(error)
    try:
        # The primary origin uses the site-root route namespace; origin_route
        # is intentionally reserved for non-primary hosts so a foreign host
        # can never borrow the primary site's same-path asset.
        route = (
            offline_mirror.route_path(value)
            if offline_mirror.is_primary_origin(value)
            else offline_mirror.origin_route(value)
        )
    except (TypeError, ValueError) as exc:
        raise CandidateFilterError(f"cannot derive origin route: {exc}") from exc
    if not route.startswith("/") or "\\" in route or "\x00" in route:
        raise CandidateFilterError("derived origin route is unsafe")
    return route


def _known_route_record(record: dict[str, Any], *, source: str) -> dict[str, Any]:
    known_hash = record.get("derived_sha256") or record.get("source_sha256")
    return {
        "source": source,
        "known_route": record.get("route"),
        "known_kind": record.get("kind"),
        "known_mime": record.get("mime"),
        "known_sha256": known_hash,
        "known_derived_sha256": record.get("derived_sha256"),
    }


def _load_known_routes(manifest: dict[str, Any], *, source: str) -> dict[str, dict[str, Any]]:
    known: dict[str, dict[str, Any]] = {}
    for record in manifest.get("files", []):
        if not _is_valid_image_record(record):
            continue
        route = record.get("route")
        if not isinstance(route, str) or not route.startswith("/"):
            continue
        known.setdefault(route, _known_route_record(record, source=source))
    return known


def _load_candidates(payload: Any) -> tuple[list[Any], str]:
    if isinstance(payload, list):
        return payload, "list"
    if not isinstance(payload, dict):
        raise CandidateFilterError("candidate input must be a JSON object or array")
    for key in ("items", "candidates"):
        if isinstance(payload.get(key), list):
            return payload[key], key
    raise CandidateFilterError("candidate input must contain an items or candidates list")


def filter_candidates(
    *,
    input_path: Path,
    manifest_path: Path = DEFAULT_MANIFEST,
    preview_provenance_path: Path | None = None,
    output_path: Path | None = None,
) -> dict[str, Any]:
    input_path = input_path.resolve()
    manifest_path = manifest_path.resolve()
    if output_path is not None:
        output_path = output_path.resolve()
        if output_path == input_path:
            raise CandidateFilterError("output must not overwrite candidate input")
    if not input_path.is_file():
        raise CandidateFilterError(f"candidate input does not exist: {input_path}")
    payload = _read_json(input_path, "candidate input")
    candidates, input_key = _load_candidates(payload)
    manifest = _read_json(manifest_path, "manifest")
    if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), list):
        raise CandidateFilterError("manifest must contain a files list")
    input_hash = sha256_file(input_path)
    manifest_hash = sha256_file(manifest_path)

    known_routes = _load_known_routes(manifest, source="offline/build-manifest.json")
    preview_meta: dict[str, Any] | None = None
    if preview_provenance_path is not None:
        preview_provenance_path = preview_provenance_path.resolve()
        preview = _read_json(preview_provenance_path, "preview provenance")
        if not isinstance(preview, dict) or not isinstance(preview.get("files"), list):
            raise CandidateFilterError("preview provenance must contain a files list")
        preview_meta = {"path": str(preview_provenance_path), "sha256": sha256_file(preview_provenance_path)}
        for record in preview["files"]:
            if not _is_valid_image_record(record):
                continue
            route = record.get("route")
            if not isinstance(route, str) or not route.startswith("/"):
                continue
            known_routes.setdefault(route, _known_route_record(record, source="preview_provenance"))

    remaining: list[dict[str, Any]] = []
    existing: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    seen_routes: dict[str, int] = {}
    for index, item in enumerate(candidates):
        value, field, url_error = _candidate_url(item)
        base = {"index": index, "candidate": item, "url_field": field, "url": value}
        if url_error or value is None:
            invalid.append({**base, "reason": url_error or "invalid URL"})
            continue
        try:
            route = candidate_route(value)
        except CandidateFilterError as exc:
            invalid.append({**base, "reason": str(exc)})
            continue
        base["route"] = route
        known = known_routes.get(route)
        if known is not None:
            existing.append({**base, "reason": "existing_route", **known})
            continue
        if route in seen_routes:
            duplicates.append({**base, "reason": "duplicate_route", "first_index": seen_routes[route]})
            continue
        seen_routes[route] = index
        remaining.append({**base, "reason": "request_candidate"})

    result = {
        "schema_version": 1,
        "kind": "resource_candidate_route_filter",
        "generated_utc": utc_now(),
        "input": {"path": str(input_path), "sha256": input_hash, "list_key": input_key, "count": len(candidates)},
        "manifest": {"path": str(manifest_path), "sha256": manifest_hash},
        "preview_provenance": preview_meta,
        "stats": {
            "input": len(candidates),
            "existing_route": len(existing),
            "duplicate_route": len(duplicates),
            "invalid": len(invalid),
            "remaining": len(remaining),
            "known_image_routes": len(known_routes),
        },
        "remaining_candidates": remaining,
        "requests": remaining,
        "excluded": {"existing_route": existing, "duplicate_route": duplicates, "invalid": invalid},
    }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="candidate JSON containing items or candidates")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--preview-provenance", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    try:
        result = filter_candidates(
            input_path=args.input,
            manifest_path=args.manifest,
            preview_provenance_path=args.preview_provenance,
            output_path=args.output,
        )
    except (CandidateFilterError, OSError, json.JSONDecodeError) as exc:
        print(f"filter_resource_candidates: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result["stats"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
