#!/usr/bin/env python3
"""Extract guide-owned screenshot literals without network or payload reads."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = ROOT / "research/continuous-recovery-20261016/local-audit/gallery-neighbor-guide-literals"
OUTPUT = OUT_DIR / "gallery-neighbor-guide-literals-v1.json"
VERIFICATION = OUT_DIR / "verification.json"
SOURCE_ROOT = ROOT / ".scratch/offline-navigation-20261015-v15/site"
MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
NEIGHBOR_AUDIT = ROOT / "research/continuous-recovery-20261016/local-audit/gallery-neighbors/audit.json"
PREFIX04_ACCEPTANCE = ROOT / "research/continuous-recovery-20261016/publication/root-gallery-prefix04-acceptance.json"
SCREENSHOT_JS = SOURCE_ROOT / "shared/wow-com/includes-client/screenshot.js"


GUIDES = {
    "love-is-in-the-air": {
        "route": "/info/events/loveisintheair/index.html",
        "source_rel": ".scratch/offline-navigation-20261015-v15/site/info/events/loveisintheair/index.html",
        "context": "Love is in the Air",
        "gallery_route": "/info/events/loveisintheair/gallery.html",
        "origin": "http://www.worldofwarcraft.com",
    },
    "lunar-festival": {
        "route": "/info/events/lunarnewyears/index.html",
        "source_rel": ".scratch/offline-navigation-20261015-v15/site/info/events/lunarnewyears/index.html",
        "context": "Lunar Festival",
        "gallery_route": "/info/events/lunarnewyears/gallery.html",
        "origin": "https://www.worldofwarcraft.com",
    },
    "world-pvp": {
        "route": "/pvp/worldpvp/index.xml",
        "source_rel": ".scratch/offline-navigation-20261015-v15/site/pvp/worldpvp/index.xml",
        "context": "World PvP",
        "gallery_route": None,
        "origin": "https://www.worldofwarcraft.com",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def source_ref(path: Path, line: int | None = None) -> dict[str, object]:
    value: dict[str, object] = {"path": rel(path), "sha256": sha256(path), "bytes": path.stat().st_size}
    if line is not None:
        value["line"] = line
    return value


def manifest_page(manifest: dict[str, object], route: str) -> dict[str, object]:
    for record in manifest.get("files", []):
        if record.get("route") == route:
            return record
    raise RuntimeError(f"manifest route missing: {route}")


def line_records(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def exact_line(lines: list[str], pattern: str) -> tuple[int, str]:
    rx = re.compile(pattern)
    for number, line in enumerate(lines, 1):
        if rx.search(line):
            return number, line
    raise RuntimeError(f"literal not found: {pattern}")


def screenshot_js_evidence() -> dict[str, object]:
    lines = line_records(SCREENSHOT_JS)
    selected = [1, 16, 38, 62, 75, 76, 78, 82, 85, 91]
    return {
        "source": source_ref(SCREENSHOT_JS),
        "selected_literals": [{"line": line, "literal": lines[line - 1]} for line in selected],
        "contract": {
            "page_directory": "path is reduced to the site-root-relative directory by lines 75-91",
            "dynamic_thumbnail": "path + theDirectory + 'ss' + number + '-thumb.jpg' (lines 16, 38, 62)",
            "dynamic_viewer": "/imageviewer.html? + path + ',' + theDirectory + ',' + number + ',' + screenshotsTotal + ',' + theURL",
            "guide_directory_literal": "theDirectory = \"images/\" in Love/Lunar pages",
        },
    }


def event_guide(config: dict[str, object], manifest: dict[str, object]) -> dict[str, object]:
    path = ROOT / str(config["source_rel"])
    lines = line_records(path)
    route = str(config["route"])
    page_manifest = manifest_page(manifest, route)
    directory_line, directory_literal = exact_line(lines, r"var\s+theDirectory\s*=\s*\"images/\"")
    total_line, total_literal = exact_line(lines, r"var\s+screenshotsTotal\s*=")
    script_line, script_literal = exact_line(lines, r"src=\"/shared/wow-com/includes-client/screenshot\.js\"")
    calls: list[dict[str, object]] = []
    call_rx = re.compile(r"\b(screenshotThinBorder|screenshot)\(\s*\"(\d+)\"")
    for number, line in enumerate(lines, 1):
        match = call_rx.search(line)
        if match:
            calls.append({"function": match.group(1), "number": int(match.group(2)), "line": number, "literal": line.strip()})
    origin = str(config["origin"])
    base_path = route.rsplit("/", 1)[0] + "/"
    unique_numbers = sorted({int(call["number"]) for call in calls})
    total_match = re.search(r"screenshotsTotal\s*=\s*(\d+)", total_literal)
    declared_total = int(total_match.group(1)) if total_match else None
    dynamic = [
        {
            "number": number,
            "full_route": f"{base_path}images/ss{number}.jpg",
            "thumbnail_route": f"{base_path}images/ss{number}-thumb.jpg",
            "full_original": f"{origin}{base_path}images/ss{number}.jpg",
            "thumbnail_original": f"{origin}{base_path}images/ss{number}-thumb.jpg",
            "derived_from": "screenshot.js lines 75-91 plus lines 16/38/62; page theDirectory literal",
            "direct_html_literal": False,
        }
        for number in unique_numbers
    ]
    gallery_links: list[dict[str, object]] = []
    gallery_rx = re.compile(r'<a\s+href="([^"]+gallery\.html)"[^>]*><img\s+src="([^"]+)"', re.I)
    for number, line in enumerate(lines, 1):
        match = gallery_rx.search(line)
        if match:
            gallery_links.append({"line": number, "literal": line.strip(), "href": match.group(1), "image": match.group(2)})
    return {
        "guide_id": config["context"],
        "route": route,
        "gallery_route": config["gallery_route"],
        "source": source_ref(path),
        "manifest": {key: page_manifest.get(key) for key in ("source_base_url", "actual_timestamp", "derived_sha256", "derived_length", "source_sha256", "source_length", "kind", "role", "transformed")},
        "script_literal": {"line": script_line, "literal": script_literal.strip()},
        "directory_literal": {"line": directory_line, "literal": directory_literal.strip()},
        "screenshots_total_literal": {"line": total_line, "literal": total_literal.strip()},
        "declared_screenshot_total": declared_total,
        "screenshot_calls": calls,
        "call_number_counts": {str(number): sum(1 for call in calls if call["number"] == number) for number in unique_numbers},
        "declared_numbers_without_a_source_call": [number for number in range(1, (declared_total or 0) + 1) if number not in unique_numbers],
        "dynamic_image_routes": dynamic,
        "parent_gallery_links": gallery_links,
        "classification": {
            "dynamic_images_are_guide_original_gallery_routes": True,
            "player_submitted_gallery_links_are_separate": True,
            "filename_or_number_is_not_proof_of_payload_or_cross_gallery_identity": True,
        },
    }


def world_pvp_guide(manifest: dict[str, object]) -> dict[str, object]:
    config = GUIDES["world-pvp"]
    path = ROOT / str(config["source_rel"])
    lines = line_records(path)
    route = str(config["route"])
    page_manifest = manifest_page(manifest, route)
    function_line, function_literal = exact_line(lines, r"function\s+popUpOmega\s*\(")
    interpolation_line, interpolation_literal = exact_line(lines, r"<img src='\" \+ screenshot")
    calls: list[dict[str, object]] = []
    current_section = None
    heading_rx = re.compile(r"<h3>(.*?)</h3>", re.I)
    call_rx = re.compile(r"popUpOmega\(&#x27;images/(ss\d+\.jpg)&#x27;,[^)]*\).*?src=\"/pvp/worldpvp/images/(ss\d+-thumb\.jpg)\"", re.I)
    for number, line in enumerate(lines, 1):
        heading = heading_rx.search(line)
        if heading:
            current_section = re.sub(r"<[^>]+>", "", heading.group(1)).strip()
        match = call_rx.search(line)
        if match:
            calls.append(
                {
                    "section": current_section,
                    "line": number,
                    "literal": line.strip(),
                    "relative_full_literal": f"images/{match.group(1)}",
                    "thumbnail_literal": f"/pvp/worldpvp/images/{match.group(2)}",
                    "resolved_full_route": f"/pvp/worldpvp/images/{match.group(1)}",
                    "resolved_thumbnail_route": f"/pvp/worldpvp/images/{match.group(2)}",
                    "resolved_full_original": f"{config['origin']}/pvp/worldpvp/images/{match.group(1)}",
                    "resolved_thumbnail_original": f"{config['origin']}/pvp/worldpvp/images/{match.group(2)}",
                    "guide_role": "WorldPvP guide illustration",
                    "not_halaa_gallery_native": True,
                }
            )
    return {
        "guide_id": config["context"],
        "route": route,
        "gallery_route": None,
        "source": source_ref(path),
        "manifest": {key: page_manifest.get(key) for key in ("source_base_url", "actual_timestamp", "derived_sha256", "derived_length", "source_sha256", "source_length", "kind", "role", "transformed")},
        "popUpOmega_interface": {
            "function": {"line": function_line, "literal": function_literal.strip()},
            "interpolation": {"line": interpolation_line, "literal": interpolation_literal.strip()},
            "relative_resolution": "page source /pvp/worldpvp/index.xml resolves images/ssN.jpg under /pvp/worldpvp/",
        },
        "screenshot_calls": calls,
        "classification": {
            "guide_images_are_not_halaa_gallery_native": True,
            "same_route_overlap_requires_context_label": True,
            "do_not_create_native_ss_aliases": True,
        },
    }


def audit_join(audit: dict[str, object]) -> dict[str, object]:
    entries = audit.get("entries", [])
    by_context: dict[str, list[dict[str, object]]] = {}
    for entry in entries:
        by_context.setdefault(str(entry.get("gallery_context")), []).append(entry)
    overlap = [
        {
            "context": entry.get("gallery_context"),
            "original": entry.get("original"),
            "state": entry.get("state"),
            "route": entry.get("route"),
            "length": entry.get("length"),
            "dimensions": entry.get("dimensions"),
            "source_evidence": entry.get("source_evidence"),
        }
        for entry in entries
        if str(entry.get("original", "")).lower().endswith(tuple(f"/ss{n}.jpg" for n in range(1, 50)))
        and str(entry.get("gallery_context")) == "Halaa PvP"
    ]
    return {
        "audit_source": source_ref(NEIGHBOR_AUDIT),
        "prefix04_acceptance": source_ref(PREFIX04_ACCEPTANCE),
        "counts": audit.get("counts"),
        "filename_counts": audit.get("filename_counts"),
        "context_counts": {context: len(rows) for context, rows in sorted(by_context.items())},
        "context_state_counts": {
            context: {
                state: sum(1 for row in rows if row.get("state") == state)
                for state in sorted({str(row.get("state")) for row in rows})
            }
            for context, rows in sorted(by_context.items())
        },
        "worldpvp_halaa_path_overlap": overlap,
        "boundary": "The 34 local rows and 49 positive-index-not-local rows are prior audit facts. Index evidence is not payload recovery; WorldPvP guide context does not relabel Halaa rows as a gallery source.",
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit = json.loads(NEIGHBOR_AUDIT.read_text(encoding="utf-8"))
    guides = [event_guide(GUIDES["love-is-in-the-air"], manifest), event_guide(GUIDES["lunar-festival"], manifest), world_pvp_guide(manifest)]
    payload = {
        "schema": "wow-recovery.gallery-neighbor-guide-literals.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "network_requests": 0,
        "payload_downloads": 0,
        "source_manifest": source_ref(MANIFEST),
        "screenshot_js": screenshot_js_evidence(),
        "guides": guides,
        "prior_neighbor_audit": audit_join(audit),
        "counts": {
            "guides": len(guides),
            "love_dynamic_unique_full": len(guides[0]["dynamic_image_routes"]),
            "lunar_dynamic_unique_full": len(guides[1]["dynamic_image_routes"]),
            "lunar_dynamic_call_occurrences": len(guides[1]["screenshot_calls"]),
            "lunar_declared_screenshots_total": guides[1]["declared_screenshot_total"],
            "lunar_declared_numbers_without_source_call": guides[1]["declared_numbers_without_a_source_call"],
            "worldpvp_guide_image_calls": len(guides[2]["screenshot_calls"]),
            "neighbor_audit_already_local": audit.get("counts", {}).get("already_local_and_published"),
            "neighbor_audit_positive_index_not_local": audit.get("counts", {}).get("positive_index_not_local"),
        },
        "relations_for_future_ui": [
            {
                "gallery_route": "/info/events/loveisintheair/gallery.html",
                "guide_route": "/info/events/loveisintheair/index.html",
                "section_label": "Guide images",
                "relationship": "Show only screenshot.js-derived ssN guide routes with a link back to the guide; keep gal01/gal02/gal03 player-submitted entry images separate.",
                "native_full_or_thumb_aliases": False,
            },
            {
                "gallery_route": "/info/events/lunarnewyears/gallery.html",
                "guide_route": "/info/events/lunarnewyears/index.html",
                "section_label": "Guide images",
                "relationship": "Keep player-submitted /images/ss/thumb/ssN-thumb.jpg entries separate from screenshot.js-derived /images/ssN.jpg and /images/ssN-thumb.jpg guide routes.",
                "native_full_or_thumb_aliases": False,
            },
            {
                "gallery_route": None,
                "guide_route": "/pvp/worldpvp/index.xml",
                "section_label": "WorldPvP guide images",
                "relationship": "Use the guide page's section context and literal parent links; do not relabel the overlapping /pvp/worldpvp/images/ssN.jpg paths as Halaa gallery originals.",
                "native_full_or_thumb_aliases": False,
            },
        ],
        "evidence_boundary": "Guide literals prove route construction and parent context. They do not prove bytes, capture validity, or that a same-number full image exists unless a separate accepted payload record says so.",
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    verification = {
        "schema": "wow-recovery.gallery-neighbor-guide-literals-verification.v1",
        "audit": {"path": rel(OUTPUT), "sha256": sha256(OUTPUT), "bytes": OUTPUT.stat().st_size},
        "checks": {
            "network_requests_zero": payload["network_requests"] == 0,
            "payload_downloads_zero": payload["payload_downloads"] == 0,
            "guide_count_three": len(guides) == 3,
            "love_unique_calls_12": len(guides[0]["dynamic_image_routes"]) == 12,
            "lunar_total_21_declared": guides[1]["screenshots_total_literal"]["literal"].endswith("21;"),
            "worldpvp_calls_16": len(guides[2]["screenshot_calls"]) == 16,
            "prior_34_local_49_not_local": audit.get("counts") == {"positive_index_not_local": 49, "already_local_and_published": 34},
            "no_dynamic_aliases_proposed": all(not relation["native_full_or_thumb_aliases"] for relation in payload["relations_for_future_ui"]),
        },
        "source_hashes": {
            "manifest": sha256(MANIFEST),
            "neighbor_audit": sha256(NEIGHBOR_AUDIT),
            "prefix04_acceptance": sha256(PREFIX04_ACCEPTANCE),
            "screenshot_js": sha256(SCREENSHOT_JS),
            **{guide["guide_id"]: guide["source"]["sha256"] for guide in guides},
        },
    }
    VERIFICATION.write_text(json.dumps(verification, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"audit": rel(OUTPUT), "audit_sha256": sha256(OUTPUT), "verification": rel(VERIFICATION), "verification_sha256": sha256(VERIFICATION), "counts": payload["counts"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
