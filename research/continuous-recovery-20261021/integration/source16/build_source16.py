"""Prepare and (only with an explicit GO) build the Source16 derived input.

The default command is a read-only validation plus a small preparation receipt.
It does not create ``.scratch/offline-non-gallery-20261021-v16``.  The copy
path is deliberately guarded by ``--execute --go`` and is kept here so the
parent runner can use the same validated plan after review.

This module owns only the Source16 integration directory.  It deliberately
does not run the Pages exporter: Source15 is already a derived tree, and the
exporter owns the later URL/CSP/static-form transformations.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import os
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qs, urlsplit


ROOT = Path(__file__).resolve().parents[4]
OWNED_DIR = Path(__file__).resolve().parent
MAP_PATH = ROOT / "research/continuous-recovery-20261021/integration/main-pages-review/source16-input-map.json"
ACCEPTANCE_PATH = ROOT / "research/continuous-recovery-20261021/publication/root-main-pages-source-acceptance.json"
V42_PROVENANCE = ROOT / ".scratch/pages-resources-20261021-v42/export-provenance.json"
SOURCE15_MANIFEST_DEFAULT = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
SOURCE15_SITE_DEFAULT = ROOT / ".scratch/offline-navigation-20261015-v15/site"
DEST_ROOT = ROOT / ".scratch/offline-non-gallery-20261021-v16"
DEST_SITE = DEST_ROOT / "site"
DEST_MANIFEST = DEST_ROOT / "build-manifest.json"
MIN_FREE_BYTES = 11_005_853_696

EXPECTED_IDS = {
    "contest-050609",
    "content-index-shtml",
    "tinfoilhat",
    "two-headed-ogre",
    "fan-site-program",
    "moltencore",
    "patch-092904",
    "bardclass",
    "wrath-index-xml",
}
EXPECTED_ALIASES = {
    "/contests/05-06-09": "/contests/05-06-09/index.html",
    "/contests/05-06-09/": "/contests/05-06-09/index.html",
    "/info/basics/content-index.shtml": "/info/basics/content-index.html",
    "/moltencore": "/moltencore/index.html",
    "/moltencore/": "/moltencore/index.html",
    "/wrath/index.xml": "/wrath/index.html",
}

SESSION_RE = re.compile(r";jsessionid=[A-Za-z0-9._~-]+", re.IGNORECASE)
ANCHOR_RE = re.compile(
    r"<a\b(?P<attrs>[^>]*?\bhref\s*=\s*)(?P<quote>['\"])(?P<href>.*?)(?P=quote)",
    re.IGNORECASE | re.DOTALL,
)
TEXT_SUFFIXES = {".html", ".htm", ".xml", ".shtml"}
IGNORED_BLOCK_RE = re.compile(
    r"<!--.*?-->|<script\b[^>]*>.*?</script\s*>|<style\b[^>]*>.*?</style\s*>",
    re.IGNORECASE | re.DOTALL,
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel_from_root(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def assert_under(path: Path, parent: Path, *, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(parent.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} escapes {parent}: {path}") from exc
    return resolved


def free_bytes() -> int:
    return shutil.disk_usage(ROOT).free


def require_floor(*, operation: str, required_extra: int = 0) -> int:
    free = free_bytes()
    if free < MIN_FREE_BYTES:
        raise RuntimeError(f"D: free space below floor before {operation}: {free} < {MIN_FREE_BYTES}")
    if required_extra and free - required_extra < MIN_FREE_BYTES:
        raise RuntimeError(
            f"D: free space would cross floor during {operation}: free={free}, "
            f"required_extra={required_extra}, floor={MIN_FREE_BYTES}"
        )
    return free


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], Path, Path, Path]:
    for path in (MAP_PATH, ACCEPTANCE_PATH, V42_PROVENANCE, SOURCE15_MANIFEST_DEFAULT, SOURCE15_SITE_DEFAULT):
        if not path.exists():
            raise FileNotFoundError(path)

    source_map = load_json(MAP_PATH)
    acceptance = load_json(ACCEPTANCE_PATH)
    v42 = load_json(V42_PROVENANCE)

    if source_map.get("accepted") is not True:
        raise ValueError("Source16 input map is not accepted")
    acceptance_bytes = ACCEPTANCE_PATH.read_bytes()
    acceptance_sha = sha256_bytes(acceptance_bytes)
    if source_map.get("source_acceptance_sha256") != acceptance_sha:
        raise ValueError("Source16 input-map acceptance SHA does not match acceptance file")

    manifest_rel = str(v42.get("source_manifest", ""))
    site_rel = str(v42.get("source_site", ""))
    manifest = ROOT / manifest_rel
    site = ROOT / site_rel
    if manifest.resolve() != SOURCE15_MANIFEST_DEFAULT.resolve():
        raise ValueError(f"v42 provenance points at unexpected Source15 manifest: {manifest_rel}")
    if site.resolve() != SOURCE15_SITE_DEFAULT.resolve():
        raise ValueError(f"v42 provenance points at unexpected Source15 site: {site_rel}")
    if not site.is_dir() or not manifest.is_file():
        raise FileNotFoundError("Source15 site or manifest is missing")

    manifest_sha = sha256_file(manifest)
    expected_manifest_sha = acceptance.get("frozen_source15_manifest_sha256")
    if v42.get("source_manifest_sha256") != manifest_sha:
        raise ValueError("v42 provenance Source15 manifest SHA mismatch")
    if expected_manifest_sha and expected_manifest_sha != manifest_sha:
        raise ValueError("acceptance Source15 manifest SHA mismatch")

    return source_map, acceptance, v42, manifest, site, ROOT / manifest_rel


def validate_safe_tree(site: Path) -> tuple[int, int]:
    count = 0
    total = 0
    for path in site.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Source15 tree contains a symlink: {path}")
        if path.is_file():
            rel = path.relative_to(site)
            if any(part in ("", ".", "..") for part in rel.parts):
                raise ValueError(f"unsafe Source15 relative path: {rel}")
            count += 1
            total += path.stat().st_size
    return count, total


def validate_records(source_map: dict[str, Any]) -> list[dict[str, Any]]:
    records = source_map.get("records")
    if not isinstance(records, list) or len(records) != len(EXPECTED_IDS):
        raise ValueError(f"expected exactly {len(EXPECTED_IDS)} Source16 records")
    ids = {str(record.get("entity_id")) for record in records}
    if ids != EXPECTED_IDS:
        raise ValueError(f"unexpected Source16 entity IDs: {sorted(ids)}")
    aliases = source_map.get("aliases")
    if aliases != EXPECTED_ALIASES:
        raise ValueError("Source16 alias map differs from the reviewed six-alias input")

    seen_routes: set[str] = set()
    for record in records:
        route = str(record.get("proposed_route", ""))
        url = str(record.get("original_url", ""))
        payload_rel = str(record.get("private_payload_path", ""))
        if not route.startswith("/") or "?" in route or "#" in route:
            raise ValueError(f"unsafe proposed route: {route}")
        if route in seen_routes:
            raise ValueError(f"duplicate proposed route: {route}")
        seen_routes.add(route)
        if not url.startswith("http://www.worldofwarcraft.com/"):
            raise ValueError(f"unexpected Source16 original URL: {url}")
        payload = ROOT / payload_rel
        assert_under(payload, ROOT / "research/continuous-recovery-20261021/integration/main-pages-review/private", label="private payload")
        if payload.is_symlink() or not payload.is_file():
            raise FileNotFoundError(payload)
        raw = payload.read_bytes()
        if len(raw) != int(record["length"]):
            raise ValueError(f"length mismatch for {record['entity_id']}")
        if sha256_bytes(raw) != record["sha256"]:
            raise ValueError(f"SHA mismatch for {record['entity_id']}")
        if record.get("stored_http_status") != 200:
            raise ValueError(f"non-200 accepted payload: {record['entity_id']}")
        if record.get("proposed_use") == "alias_only" and record["entity_id"] != "wrath-index-xml":
            raise ValueError(f"unexpected alias-only record: {record['entity_id']}")
    return records


def replace_exact(text: str, pattern: str, replacement: str, *, label: str, flags: int = 0) -> tuple[str, int]:
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise ValueError(f"expected exactly one {label} transformation, got {count}")
    return new_text, count


def derive_payload(entity_id: str, raw: bytes) -> tuple[bytes, dict[str, Any]]:
    text = raw.decode("utf-8")
    session_count = len(SESSION_RE.findall(text))
    text, removed = SESSION_RE.subn("", text)
    if removed != session_count:
        raise AssertionError("session substitution count drift")
    if SESSION_RE.search(text):
        raise ValueError(f"session identifier remains after derivation for {entity_id}")

    business_rewrites: list[str] = []
    if entity_id == "contest-050609":
        text, _ = replace_exact(
            text,
            r"To enter the contest, take the best screen shot you can within one of the Battlegrounds Zones and submit it using the Web page link below by June 20th, 2005\.",
            "The historical contest invited players to submit their best Battlegrounds screenshot by June 20th, 2005.",
            label="contest call-to-action",
        )
        text, _ = replace_exact(
            text,
            r"We will run them through the gauntlet of dev team scrutiny, and will announce the winners soon after\. So train your photographer's eye on the Battlegrounds and good luck!",
            "The archived announcement described development-team judging and planned publication of the winners.",
            label="contest future-tense paragraph",
        )
        business_rewrites.extend(["contest call-to-action", "contest future-tense paragraph"])
    elif entity_id == "fan-site-program":
        text, _ = replace_exact(
            text,
            r"Blizzard Entertainment is looking for a few good fansites\. Web sites that are interested in participating in our\s+official fan site program are required to meet the following guidelines:",
            "Blizzard Entertainment's historical fan site program sought a few good fansites. The program's guidelines were as follows:",
            label="fan-site historical introduction",
            flags=re.DOTALL,
        )
        text, _ = replace_exact(
            text,
            r"In return, fan sites will receive regular updates and access to exclusive chat sessions with Blizzard developers\. Fan\s+site administrators will also get a heads-up on news and insider information along with some additional surprises from\s+time\s+to time\.",
            "In return, fan sites received regular updates and access to exclusive chat sessions with Blizzard developers. Fan site administrators also received advance news and insider information along with additional surprises from time to time.",
            label="fan-site historical benefits",
            flags=re.DOTALL,
        )
        text, _ = replace_exact(
            text,
            r"Think your completed site should be part of our program\? Write\s+<a\s+href=[\"']mailto:fansites@blizzard\.com[\"']>fansites@blizzard\.com</a>\s+and ask for an application\.",
            "The archived program accepted applications by email. This historical exhibit does not accept applications.",
            label="fan-site mailto application",
            flags=re.DOTALL | re.IGNORECASE,
        )
        if re.search(r"mailto:", text, re.IGNORECASE):
            raise ValueError("fan-site derived body still contains a mailto action")
        business_rewrites.extend([
            "fan-site historical introduction",
            "fan-site historical benefits",
            "fan-site mailto application",
        ])

    derived = text.encode("utf-8")
    return derived, {
        "raw_sha256": sha256_bytes(raw),
        "raw_length": len(raw),
        "derived_sha256": sha256_bytes(derived),
        "derived_length": len(derived),
        "session_suffix_removed": session_count,
        "business_rewrites": business_rewrites,
    }


def accepted_targets(records: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {record["original_url"]: record for record in records}


def ignored_spans(text: str) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    for match in IGNORED_BLOCK_RE.finditer(text):
        block = match.group(0).lstrip().lower()
        kind = "comment" if block.startswith("<!--") else ("script" if block.startswith("<script") else "style")
        spans.append((match.start(), match.end(), kind))
    return spans


def ignored_span_kind(position: int, spans: list[tuple[int, int, str]]) -> str | None:
    for start, end, kind in spans:
        if start <= position < end:
            return kind
    return None


def in_ignored_span(position: int, spans: list[tuple[int, int, str]]) -> bool:
    return ignored_span_kind(position, spans) is not None


def scan_navigation(site: Path, records: list[dict[str, Any]]) -> dict[str, Any]:
    targets = accepted_targets(records)
    matches: list[dict[str, Any]] = []
    ignored_matches: list[dict[str, Any]] = []
    scanned_files = 0
    scanned_bytes = 0
    for path in sorted(site.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        raw = path.read_bytes()
        scanned_files += 1
        scanned_bytes += len(raw)
        text = raw.decode("utf-8", errors="replace")
        ignored = ignored_spans(text)
        for match in ANCHOR_RE.finditer(text):
            href = html.unescape(match.group("href"))
            parsed = urlsplit(href)
            if parsed.path != "/__offline/missing.html":
                continue
            requested_values = parse_qs(parsed.query, keep_blank_values=True).get("requested", [])
            if len(requested_values) != 1 or requested_values[0] not in targets:
                continue
            record = targets[requested_values[0]]
            ignored_kind = ignored_span_kind(match.start(), ignored)
            if ignored_kind is not None:
                ignored_matches.append(
                    {
                        "source_path": path.relative_to(site).as_posix(),
                        "line": text.count("\n", 0, match.start()) + 1,
                        "entity_id": record["entity_id"],
                        "requested": requested_values[0],
                        "target_route": record["proposed_route"],
                        "ignored_kind": ignored_kind,
                    }
                )
                continue
            matches.append(
                {
                    "source_path": path.relative_to(site).as_posix(),
                    "line": text.count("\n", 0, match.start()) + 1,
                    "entity_id": record["entity_id"],
                    "requested": requested_values[0],
                    "target_route": record["proposed_route"],
                }
            )
    by_entity: dict[str, int] = {}
    for item in matches:
        by_entity[item["entity_id"]] = by_entity.get(item["entity_id"], 0) + 1
    ignored_by_entity: dict[str, int] = {}
    ignored_by_kind: dict[str, int] = {}
    for item in ignored_matches:
        ignored_by_entity[item["entity_id"]] = ignored_by_entity.get(item["entity_id"], 0) + 1
        ignored_by_kind[item["ignored_kind"]] = ignored_by_kind.get(item["ignored_kind"], 0) + 1
    return {
        "scanned_files": scanned_files,
        "scanned_bytes": scanned_bytes,
        "matched_anchor_markers": len(matches),
        "by_entity": dict(sorted(by_entity.items())),
        "matches": matches,
        "ignored_exact_target_markers": len(ignored_matches),
        "ignored_by_entity": dict(sorted(ignored_by_entity.items())),
        "ignored_by_kind": dict(sorted(ignored_by_kind.items())),
        "ignored_matches": ignored_matches,
    }


def navigation_delta(site: Path, navigation: dict[str, Any], records: list[dict[str, Any]]) -> int:
    """Return the exact UTF-8 byte delta for the planned anchor rewrites."""
    targets = accepted_targets(records)
    by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in navigation["matches"]:
        by_path[item["source_path"]].append(item)
    delta = 0
    for rel, expected in by_path.items():
        path = site / rel
        text = path.read_bytes().decode("utf-8")
        rewritten, changed = rewrite_navigation(text, targets)
        expected_keys = Counter((x["entity_id"], x["requested"], x["target_route"]) for x in expected)
        changed_keys = Counter((x["entity_id"], x["requested"], x["target_route"]) for x in changed)
        if expected_keys != changed_keys:
            raise ValueError(f"navigation plan drift for {rel}: expected {expected_keys}, got {changed_keys}")
        delta += len(rewritten.encode("utf-8")) - len(text.encode("utf-8"))
    return delta


def rewrite_navigation(text: str, targets: dict[str, dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    changed: list[dict[str, Any]] = []
    ignored = ignored_spans(text)

    def repl(match: re.Match[str]) -> str:
        if in_ignored_span(match.start(), ignored):
            return match.group(0)
        href = html.unescape(match.group("href"))
        parsed = urlsplit(href)
        requested_values = parse_qs(parsed.query, keep_blank_values=True).get("requested", [])
        if parsed.path != "/__offline/missing.html" or len(requested_values) != 1:
            return match.group(0)
        record = targets.get(requested_values[0])
        if record is None:
            return match.group(0)
        changed.append({"entity_id": record["entity_id"], "requested": requested_values[0], "target_route": record["proposed_route"]})
        quote = match.group("quote")
        attrs = match.group("attrs")
        return f"<a{attrs}{quote}{record['proposed_route']}{quote}"

    return ANCHOR_RE.sub(repl, text), changed


def migrate_path(path_value: str, source_site: Path, dest_site: Path) -> str:
    value = str(path_value).replace("\\", "/")
    source_abs = source_site.resolve().as_posix().rstrip("/") + "/"
    dest_abs = dest_site.resolve().as_posix().rstrip("/") + "/"
    source_rel = source_site.resolve().relative_to(ROOT.resolve()).as_posix().rstrip("/") + "/"
    dest_rel = dest_site.resolve().relative_to(ROOT.resolve()).as_posix().rstrip("/") + "/"
    if value.startswith(source_abs):
        return dest_abs + value[len(source_abs) :]
    if value.startswith(source_rel):
        return dest_rel + value[len(source_rel) :]
    return value


def build_file_plan(records: list[dict[str, Any]], source_site: Path) -> tuple[list[dict[str, Any]], dict[str, bytes]]:
    plan: list[dict[str, Any]] = []
    derived_bodies: dict[str, bytes] = {}
    for record in records:
        raw = (ROOT / record["private_payload_path"]).read_bytes()
        derived, stats = derive_payload(record["entity_id"], raw)
        route = record["proposed_route"]
        existing = source_site / route.lstrip("/")
        use = record["proposed_use"]
        body_copy = use in {"add", "update"}
        if body_copy:
            derived_bodies[route] = derived
        plan.append(
            {
                "entity_id": record["entity_id"],
                "original_url": record["original_url"],
                "capture_timestamp": record["actual_capture_timestamp"],
                "source_arc": record["source_arc"],
                "route": route,
                "proposed_use": use,
                "private_payload_path": record["private_payload_path"],
                "existing_source15_route": existing.exists(),
                "action": "replace" if use == "update" else ("add" if use == "add" else "alias_only"),
                "copy_body": body_copy,
                "source_sha256": stats["raw_sha256"],
                "source_length": stats["raw_length"],
                "derived_sha256": stats["derived_sha256"],
                "derived_length": stats["derived_length"],
                "session_suffix_removed": stats["session_suffix_removed"],
                "business_rewrites": stats["business_rewrites"],
            }
        )
    if len(derived_bodies) != 8:
        raise ValueError(f"expected 8 body-derived routes, got {len(derived_bodies)}")
    return plan, derived_bodies


def prepare() -> dict[str, Any]:
    if DEST_ROOT.exists():
        raise FileExistsError(f"refusing to prepare over existing Source16 destination: {DEST_ROOT}")
    source_map, acceptance, v42, manifest_path, site, _ = load_inputs()
    records = validate_records(source_map)
    file_count, site_bytes = validate_safe_tree(site)
    manifest_bytes = manifest_path.stat().st_size
    navigation = scan_navigation(site, records)
    file_plan, derived_bodies = build_file_plan(records, site)
    source_route = {str(item.get("route")): item for item in load_json(manifest_path).get("files", [])}

    if source_map.get("aliases"):
        source_manifest = load_json(manifest_path)
        alias_conflicts = {
            alias: source_manifest.get("route_aliases", {}).get(alias)
            for alias in source_map["aliases"]
            if alias in source_manifest.get("route_aliases", {})
        }
        origin_conflicts = {
            "www.worldofwarcraft.com" + record["original_url"].split(".com", 1)[1]: source_manifest.get("origin_index", {}).get(
                "www.worldofwarcraft.com" + record["original_url"].split(".com", 1)[1]
            )
            for record in records
            if "www.worldofwarcraft.com" + record["original_url"].split(".com", 1)[1] in source_manifest.get("origin_index", {})
        }
    else:
        alias_conflicts = {}
        origin_conflicts = {}

    replaced_record = source_route.get("/info/basics/content-index.html")
    derived_body_bytes = sum(len(body) for body in derived_bodies.values())
    old_update_bytes = int(replaced_record.get("derived_length", 0)) if replaced_record else 0
    navigation_byte_delta = navigation_delta(site, navigation, records)
    estimated_site_delta = derived_body_bytes - old_update_bytes + navigation_byte_delta

    return {
        "schema": "wow-source16-prepare/v1",
        "status": "ready_for_root_go",
        "formal_copy_executed": False,
        "network_requests": 0,
        "generated_by": rel_from_root(Path(__file__)),
        "tool_sha256": sha256_file(Path(__file__)),
        "source_acceptance": {
            "path": rel_from_root(ACCEPTANCE_PATH),
            "sha256": sha256_file(ACCEPTANCE_PATH),
            "accepted": acceptance.get("accepted"),
            "source_entities": acceptance.get("source_entities"),
            "proposed_new_pages": acceptance.get("proposed_new_pages"),
            "proposed_updated_existing_pages": acceptance.get("proposed_updated_existing_pages"),
            "proposed_alias_only": acceptance.get("proposed_alias_only"),
        },
        "input_map": {
            "path": rel_from_root(MAP_PATH),
            "sha256": sha256_file(MAP_PATH),
            "record_count": len(records),
            "alias_count": len(source_map["aliases"]),
            "aliases": source_map["aliases"],
        },
        "source15": {
            "site": rel_from_root(site),
            "manifest": rel_from_root(manifest_path),
            "manifest_sha256": sha256_file(manifest_path),
            "manifest_bytes": manifest_bytes,
            "site_file_count": file_count,
            "site_bytes": site_bytes,
            "v42_provenance": rel_from_root(V42_PROVENANCE),
            "v42_source_manifest_sha256": v42.get("source_manifest_sha256"),
        },
        "payloads": file_plan,
        "navigation_restore": navigation,
        "conflicts": {
            "alias_conflicts": alias_conflicts,
            "origin_index_conflicts": origin_conflicts,
            "existing_body_route_before_update": bool(replaced_record),
        },
        "estimated_write": {
            "body_derived_routes": len(derived_bodies),
            "body_derived_bytes": derived_body_bytes,
            "existing_update_bytes_removed": old_update_bytes,
            "navigation_anchor_rewrites": navigation.get("matched_anchor_markers", 0),
            "navigation_byte_delta": navigation_byte_delta,
            "estimated_site_delta": estimated_site_delta,
            "formal_destination": rel_from_root(DEST_ROOT),
            "floor_bytes": MIN_FREE_BYTES,
            "free_bytes_at_prepare": free_bytes(),
        },
        "execution_contract": {
            "command": "python research/continuous-recovery-20261021/integration/source16/build_source16.py --execute --go",
            "destination": rel_from_root(DEST_ROOT),
            "guard": "refuses an existing destination, checks path/symlink safety and D: free-space floor before copy and writes",
            "source15_bytes_preserved": "all unchanged files are copied byte-for-byte; only exact accepted missing-anchor hrefs and eight body-derived routes change",
            "not_run_in_prepare": True,
        },
    }


def _write_bytes_checked(path: Path, data: bytes, *, operation: str) -> None:
    require_floor(operation=operation, required_extra=len(data))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    require_floor(operation=f"after {operation}")


def execute() -> dict[str, Any]:
    if DEST_ROOT.exists():
        raise FileExistsError(f"refusing to overwrite existing Source16 destination: {DEST_ROOT}")
    source_map, acceptance, _v42, source_manifest_path, source_site, _ = load_inputs()
    records = validate_records(source_map)
    validate_safe_tree(source_site)
    navigation = scan_navigation(source_site, records)
    file_plan, derived_bodies = build_file_plan(records, source_site)
    targets = accepted_targets(records)

    source_manifest = load_json(source_manifest_path)
    source_manifest_sha = sha256_file(source_manifest_path)
    expected_free = source_site.stat().st_size if source_site.is_file() else sum(p.stat().st_size for p in source_site.rglob("*") if p.is_file())
    expected_free += source_manifest_path.stat().st_size + sum(len(body) for body in derived_bodies.values()) + 2 * 1024 * 1024
    require_floor(operation="Source16 destination preflight", required_extra=expected_free)
    DEST_SITE.mkdir(parents=True, exist_ok=False)

    copied = 0
    for src in sorted(source_site.rglob("*")):
        if src.is_symlink():
            raise ValueError(f"source symlink encountered during execute: {src}")
        rel = src.relative_to(source_site)
        dst = assert_under(DEST_SITE / rel, DEST_SITE, label="destination path")
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue
        data = src.read_bytes()
        _write_bytes_checked(dst, data, operation=f"copy {rel.as_posix()}")
        copied += 1

    nav_changed = []
    planned_by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in navigation["matches"]:
        planned_by_path[item["source_path"]].append(item)
    for rel, expected in planned_by_path.items():
        path = DEST_SITE / rel
        text = path.read_bytes().decode("utf-8")
        rewritten, changed = rewrite_navigation(text, targets)
        expected_keys = Counter((x["entity_id"], x["requested"], x["target_route"]) for x in expected)
        changed_keys = Counter((x["entity_id"], x["requested"], x["target_route"]) for x in changed)
        if expected_keys != changed_keys:
            raise RuntimeError(f"planned navigation marker disappeared or multiplied in copied file: {rel}")
        _write_bytes_checked(path, rewritten.encode("utf-8"), operation=f"rewrite navigation {rel}")
        nav_changed.extend(changed)

    for item in file_plan:
        if not item["copy_body"]:
            continue
        target = assert_under(DEST_SITE / item["route"].lstrip("/"), DEST_SITE, label="Source16 body destination")
        exists = target.exists()
        if item["action"] == "add" and exists:
            raise FileExistsError(f"new Source16 route already exists in copied Source15 tree: {item['route']}")
        if item["action"] == "replace" and not exists:
            raise FileNotFoundError(f"Source16 update route missing after copy: {item['route']}")
        _write_bytes_checked(target, derived_bodies[item["route"]], operation=f"write Source16 body {item['route']}")

    old_records = []
    file_records = source_manifest.get("files", [])
    for route in (item["route"] for item in file_plan if item["copy_body"]):
        old_records.extend(copy.deepcopy(item) for item in file_records if item.get("route") == route)
    for item in file_records:
        if "output_path" in item:
            item["output_path"] = migrate_path(item["output_path"], source_site, DEST_SITE)
    source_manifest["files"] = [item for item in file_records if item.get("route") not in {item["route"] for item in file_plan if item["copy_body"]}]
    source_manifest.setdefault("source16_superseded_source15_records", []).extend(copy.deepcopy(old_records))
    for item, record in zip((p for p in file_plan if p["copy_body"]), (r for r in records if r["proposed_use"] != "alias_only")):
        body = derived_bodies[item["route"]]
        source_manifest["files"].append(
            {
                "route": item["route"],
                "origin_namespace": "www.worldofwarcraft.com",
                "output_path": rel_from_root(DEST_SITE / item["route"].lstrip("/")),
                "source_local_path": record["private_payload_path"],
                "source_base_url": record["original_url"],
                "source_map_path": rel_from_root(MAP_PATH),
                "source_sha_inferred": False,
                "source_sha256": item["source_sha256"],
                "source_length": item["source_length"],
                "derived_sha256": item["derived_sha256"],
                "derived_length": item["derived_length"],
                "source_mime": record["mime"],
                "mime": record["mime"],
                "kind": "html",
                "role": "source16_main_page",
                "source_role": None,
                "actual_timestamp": record["actual_capture_timestamp"],
                "requested_timestamp": None,
                "transformed": True,
                "derivation_reason": "accepted Source16 body; transient session suffix removed; historical business copy adjusted where reviewed",
                "source_arc": record["source_arc"],
            }
        )
    source_manifest["site_root"] = rel_from_root(DEST_SITE)
    route_aliases = dict(source_manifest.get("route_aliases", {}))
    for alias, target in source_map["aliases"].items():
        existing = route_aliases.get(alias)
        if existing is not None and existing != target:
            raise ValueError(f"route alias collision during execute: {alias} -> {existing!r}, new {target!r}")
        route_aliases[alias] = target
    source_manifest["route_aliases"] = route_aliases
    origin_index = dict(source_manifest.get("origin_index", {}))
    for record in records:
        key = "www.worldofwarcraft.com" + urlsplit(record["original_url"]).path
        existing = origin_index.get(key)
        if existing is not None and existing != record["proposed_route"]:
            raise ValueError(f"origin index collision during execute: {key}")
        origin_index[key] = record["proposed_route"]
    source_manifest["origin_index"] = origin_index

    nav_routes = {"/" + item["source_path"] for item in navigation["matches"]}
    for item in source_manifest["files"]:
        if item.get("route") not in nav_routes:
            continue
        rendered = DEST_SITE / item["route"].lstrip("/")
        rendered_bytes = rendered.read_bytes()
        item["derived_sha256"] = sha256_bytes(rendered_bytes)
        item["derived_length"] = len(rendered_bytes)
        item["source16_navigation_anchor_rewrites"] = sum(1 for x in navigation["matches"] if "/" + x["source_path"] == item.get("route"))
        item["derivation_reason"] = str(item.get("derivation_reason", "")) + "; exact Source16 accepted navigation marker restored"
    source_manifest.setdefault("stats", {})["source16_main_page_records"] = 8
    source_manifest["stats"]["source16_navigation_anchor_rewrites"] = len(nav_changed)
    source_manifest["source16"] = {
        "input_map": rel_from_root(MAP_PATH),
        "input_map_sha256": sha256_file(MAP_PATH),
        "source_acceptance": rel_from_root(ACCEPTANCE_PATH),
        "source_acceptance_sha256": sha256_file(ACCEPTANCE_PATH),
        "source15_manifest_sha256": source_manifest_sha,
        "network_requests": 0,
        "records": [
            {
                "entity_id": r["entity_id"],
                "original_url": r["original_url"],
                "actual_capture_timestamp": r["actual_capture_timestamp"],
                "source_arc": r["source_arc"],
                "source_sha256": r["sha256"],
                "source_length": r["length"],
                "route": r["proposed_route"],
                "proposed_use": r["proposed_use"],
            }
            for r in records
        ],
    }
    manifest_data = json.dumps(source_manifest, ensure_ascii=False, indent=2, sort_keys=False).encode("utf-8") + b"\n"
    _write_bytes_checked(DEST_MANIFEST, manifest_data, operation="write Source16 build-manifest.json")
    return {
        "status": "executed",
        "destination": rel_from_root(DEST_ROOT),
        "copied_source15_files": copied,
        "navigation_rewrites": len(nav_changed),
        "body_routes": len(derived_bodies),
        "manifest_sha256": sha256_bytes(manifest_data),
        "free_bytes_after": free_bytes(),
        "source15_manifest_sha256_before": source_manifest_sha,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", help="validate inputs and write prepare.json (default)")
    parser.add_argument("--execute", action="store_true", help="perform the guarded Source16 copy")
    parser.add_argument("--go", action="store_true", help="required with --execute; not implied by prepare")
    args = parser.parse_args(argv)
    if args.execute:
        if not args.go:
            parser.error("--execute requires explicit --go")
        result = execute()
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    if args.go:
        parser.error("--go is only valid with --execute")

    result = prepare()
    out = OWNED_DIR / "prepare.json"
    if out.exists():
        raise FileExistsError(f"refusing to overwrite existing receipt: {out}")
    require_floor(operation="write Source16 prepare.json", required_extra=32 * 1024)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="")
    require_floor(operation="after write Source16 prepare.json")
    print(json.dumps({"receipt": rel_from_root(out), "tool_sha256": result["tool_sha256"], "status": result["status"], "matched_anchor_markers": result["navigation_restore"]["matched_anchor_markers"], "free_bytes": result["estimated_write"]["free_bytes_at_prepare"]}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
