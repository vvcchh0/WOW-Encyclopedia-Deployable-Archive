#!/usr/bin/env python3
"""Offline semantic/display audit for three faction reward icon stems.

Reads the frozen Source16 site and local v53 export only. It emits curated
line-level metadata and tooltip text, never copies source HTML or image bytes.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE16 = ROOT / ".scratch/offline-non-gallery-20261021-v16/site"
V53 = ROOT / ".scratch/pages-resources-20261022-v53"
SOURCE_FACTIONS = SOURCE16 / "info/basics/factions"
V53_FACTIONS = V53 / "info/basics/factions"
OUT = Path(__file__).resolve().parent / "semantic-usage-audit.json"
SAFE_INVENTORY = ROOT / "research/continuous-recovery-20261022/network/coolwow2-item-icons01/runtime/public-inventory.json"
SOURCE_SELECTION = ROOT / "research/continuous-recovery-20261022/coolwow2-selected-source-tree.json"

TARGETS = {
    "INV_Scroll_03.gif": "INV_Scroll_03.jpg",
    "INV_Scroll_06.gif": "INV_Scroll_06.jpg",
    "INV_Wand_11.gif": "INV_Wand_11.jpg",
}
COMMIT = "09c52b7673871b8048da92e5a13ed753fc08162f"
REPO = "https://github.com/boom8866/coolwow2"
COMMIT_DATE = "2015-12-16T16:29:03Z"
IMAGE_DIR = ROOT / "research/continuous-recovery-20261022/network/coolwow2-item-icons01/runtime/private/raw"
IMAGE_FILES = {
    "INV_Scroll_03.jpg": IMAGE_DIR / "attempt-02-coolwow2-item-icon-scroll-03-proxy.body",
    "INV_Scroll_06.jpg": IMAGE_DIR / "attempt-04-coolwow2-item-icon-scroll-06-proxy.body",
    "INV_Wand_11.jpg": IMAGE_DIR / "attempt-06-coolwow2-item-icon-wand-11-proxy.body",
}
REP = {0: "friendly", 1: "honored", 2: "revered", 3: "exalted"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jpeg_size(data: bytes) -> tuple[int | None, int | None]:
    """Read JPEG SOF dimensions without a third-party decoder."""
    if not data.startswith(b"\xff\xd8"):
        return None, None
    i = 2
    while i + 4 <= len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        while i < len(data) and data[i] == 0xFF:
            i += 1
        if i >= len(data):
            break
        marker = data[i]
        i += 1
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            continue
        if i + 2 > len(data):
            break
        length = int.from_bytes(data[i:i+2], "big")
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                      0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            if i + 7 > len(data):
                break
            return int.from_bytes(data[i+5:i+7], "big"), int.from_bytes(data[i+3:i+5], "big")
        i += length
    return None, None


def line_number(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def visible_text(markup: str, limit: int = 260) -> str:
    text = re.sub(r"(?i)<br\s*/?>", " | ", markup)
    text = re.sub(r"(?s)<[^>]*>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\\[\"']", "'", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def extract_tooltips(block: str, variable: str) -> list[dict]:
    found = []
    pattern = re.compile(
        rf"{re.escape(variable)}\.itemStats\[(\d+)\]\s*=\s*\"\\\r?\n(.*?)\r?\n\";",
        re.S,
    )
    for match in pattern.finditer(block):
        index = int(match.group(1))
        raw = match.group(2)
        raw = re.sub(r"\\\r?\n", "", raw)
        raw = raw.replace(r"\"", '"').replace(r"\'", "'")
        found.append({
            "stats_index": index,
            "reputation_bracket": REP.get(index, f"unknown-index-{index}"),
            "tooltip_text_excerpt": visible_text(raw),
        })
    return found


def iter_text(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".js", ".xml", ".html", ".css"}:
            yield path


def map_page_references(site_root: Path, target_data_js: set[str]) -> dict[str, list[dict]]:
    result = {name: [] for name in target_data_js}
    pattern = re.compile(r"<script\b[^>]*\bsrc=[\"']([^\"']+)[\"'][^>]*>", re.I)
    for page in iter_text(site_root / "info/basics/factions"):
        if page.suffix.lower() not in {".xml", ".html"}:
            continue
        text = page.read_text(encoding="utf-8", errors="replace")
        route = "/" + page.relative_to(site_root).as_posix()
        rep_controls = [i for i in range(4) if f"nowThisIsHappening({i})" in text]
        side_labels = {}
        for button_id in ("allianceButton", "hordeButton"):
            button = re.search(r'<[^>]*\bid=[\"\']' + re.escape(button_id) + r'[\"\'][^>]*>(.*?)</td>', text, re.I | re.S)
            side_labels[button_id] = visible_text(button.group(1), 80) if button else ""
        for match in pattern.finditer(text):
            src = html.unescape(match.group(1))
            for data_js in target_data_js:
                if src.endswith("/" + data_js) or src == data_js:
                    result[data_js].append({
                        "page_route": route,
                        "page_line": line_number(text, match.start()),
                        "script_src": src,
                        "page_sha256": sha256(page),
                        "reputation_control_indices": rep_controls,
                        "visible_table_button_text": side_labels,
                    })
    return result


def map_renderer_references(site_root: Path, assets: dict[str, str]) -> dict[str, list[dict]]:
    result = {name: [] for name in assets}
    tag_pattern = re.compile(r"<(script|link)\b[^>]*>", re.I)
    attr_pattern = re.compile(r"\b(src|href)=[\"']([^\"']+)[\"']", re.I)
    for page in iter_text(site_root / "info/basics/factions"):
        if page.suffix.lower() not in {".xml", ".html"}:
            continue
        text = page.read_text(encoding="utf-8", errors="replace")
        route = "/" + page.relative_to(site_root).as_posix()
        for match in tag_pattern.finditer(text):
            tag = match.group(0)
            attr = attr_pattern.search(tag)
            if not attr:
                continue
            src = html.unescape(attr.group(2))
            for name, suffix in assets.items():
                if src.endswith(suffix):
                    result[name].append({
                        "page_route": route,
                        "page_line": line_number(text, match.start()),
                        "tag": match.group(1).lower(),
                        "asset_src": src,
                        "page_sha256": sha256(page),
                    })
    return result


def script_hash_rows(root: Path, script_paths: set[str]) -> list[dict]:
    rows = []
    for rel in sorted(script_paths):
        path = root / rel
        if path.exists():
            rows.append({"path": rel.replace("\\", "/"), "bytes": path.stat().st_size, "sha256": sha256(path)})
    return rows


def main() -> None:
    assert SOURCE_FACTIONS.is_dir() and V53_FACTIONS.is_dir()
    source_occurrences = []
    target_js_paths = set()
    occurrences_by_asset = {asset: [] for asset in TARGETS}
    constructor = re.compile(
        r'^\s*var\s+(\w+)\s*=\s*new RewardItem\("(alliance|horde|both)","((?:[^"\\]|\\.)*)","([^"]+)"\);'
    )
    for path in sorted(SOURCE_FACTIONS.rglob("*.js")):
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if not any(f"/icons/{asset}" in line for asset in TARGETS):
                continue
            match = constructor.match(line)
            if not match:
                continue
            variable, faction, item_name, icon_path = match.groups()
            asset = Path(icon_path).name
            target_js_paths.add(path.relative_to(SOURCE16).as_posix())
            # Keep only the containing item definition, not the complete data file.
            start = i + 1
            end = start
            while end < len(lines) and not re.match(r"\s*var\s+\w+\s*=\s*new RewardItem\(", lines[end]):
                end += 1
            block = "\n".join(lines[i:end])
            tooltips = extract_tooltips(block, variable)
            occurrence = {
                "source_script": "/" + path.relative_to(SOURCE16).as_posix(),
                "source_script_line": i + 1,
                "variable": variable,
                "player_faction": faction,
                "reward_label": item_name,
                "missing_icon_target": icon_path,
                "reputation_brackets_and_tooltip_text": tooltips,
            }
            occurrences_by_asset[asset].append(occurrence)
            source_occurrences.append(occurrence)

    data_js_names = {Path(p).name for p in target_js_paths}
    source_pages = map_page_references(SOURCE16, data_js_names)
    v53_pages = map_page_references(V53, data_js_names)
    renderer_assets = {
        "rewardstable-new.js": "/info/basics/factions/rewardstable/scripts/rewardstable-new.js",
        "rewardstable.css": "/info/basics/factions/rewardstable/rewardstable.css",
    }
    renderer_pages = {
        "source16": map_renderer_references(SOURCE16, renderer_assets),
        "v53": map_renderer_references(V53, renderer_assets),
    }

    # Dynamic references to all three target paths across markup, scripts, and CSS.
    reference_scan = {"source16": {}, "v53": {}}
    for label, root in (("source16", SOURCE16), ("v53", V53)):
        target_paths = {asset: [] for asset in TARGETS}
        for path in iter_text(root):
            text = path.read_text(encoding="utf-8", errors="replace")
            for asset in TARGETS:
                # Match plain basename or the URL-encoded basename used by v53 placeholders.
                for match in re.finditer(re.escape(asset), text, re.I):
                    target_paths[asset].append({
                        "path": "/" + path.relative_to(root).as_posix(),
                        "line": line_number(text, match.start()),
                        "source_kind": path.suffix.lower().lstrip("."),
                    })
        reference_scan[label] = target_paths

    def renderer_lines(site_root: Path) -> dict[str, list[dict]]:
        files = (
            ("info/basics/factions/rewardstable/scripts/rewardstable-new.js",
             ("itemIcon.src = rewardItem.itemIcon", 'iconStyle.nodeValue="style_icon"', "showTip(RewardItems[")),
            ("info/basics/factions/rewardstable/rewardstable.css", (".style_icon", ".style_cell", ".style_wrapper", ".style_name")),
        )
        result = {}
        for rel, needles in files:
            path = site_root / rel
            text = path.read_text(encoding="utf-8", errors="replace")
            result[rel] = [
                {"line": i + 1, "text": line.strip()}
                for i, line in enumerate(text.splitlines())
                if any(needle in line for needle in needles)
            ]
        return result

    key_lines = renderer_lines(SOURCE16)
    v53_key_lines = renderer_lines(V53)

    safe_inventory = json.loads(SAFE_INVENTORY.read_text(encoding="utf-8"))
    safe_by_path = {row["repository_path"]: row for row in safe_inventory["records"]}

    image_meta = {}
    for jpg, raw_path in IMAGE_FILES.items():
        data = raw_path.read_bytes()
        width, height = jpeg_size(data)
        image_meta[jpg] = {
            "later_source_url": f"{REPO}/blob/{COMMIT}/images/item_icons/{jpg}",
            "later_source_raw_url": f"https://raw.githubusercontent.com/boom8866/coolwow2/{COMMIT}/images/item_icons/{jpg}",
            "commit": COMMIT,
            "commit_date": COMMIT_DATE,
            "original_capture_date": None,
            "private_local_payload_bytes": len(data),
            "private_local_payload_sha256": hashlib.sha256(data).hexdigest(),
            "git_blob_sha1": safe_by_path[f"images/item_icons/{jpg}"]["git_blob_sha1"],
            "format": "JPEG" if data.startswith(b"\xff\xd8") else "unknown",
            "native_dimensions_px": [width, height],
            "frames": 1,
            "interpretation": "later-related canonical JPEG candidate; not the missing Source16 GIF bytes",
        }

    script_rel = sorted(target_js_paths)
    renderer_rel = [
        "info/basics/factions/rewardstable/scripts/rewardstable-new.js",
        "info/basics/factions/rewardstable/rewardstable.css",
    ]
    v53_data_script_paths = set(target_js_paths)
    v53_renderer_paths = set(renderer_rel)
    page_routes = {}
    for name in sorted(data_js_names):
        page_routes[name] = {
            "source16": source_pages.get(name, []),
            "v53": v53_pages.get(name, []),
        }

    routes_by_target = {}
    aggregate_usage = {}
    for asset, rows in occurrences_by_asset.items():
        script_names = {Path(row["source_script"]).name for row in rows}
        routes_by_target[asset] = sorted({
            ref["page_route"]
            for name in script_names
            for ref in source_pages.get(name, [])
        })
        counts = {"faction": {}, "reputation_bracket": {}, "label_class": {}}
        for row in rows:
            faction = row["player_faction"]
            counts["faction"][faction] = counts["faction"].get(faction, 0) + 1
            for tooltip in row["reputation_brackets_and_tooltip_text"]:
                bracket = tooltip["reputation_bracket"]
                counts["reputation_bracket"][bracket] = counts["reputation_bracket"].get(bracket, 0) + 1
            label_class = row["reward_label"].split(":", 1)[0] if ":" in row["reward_label"] else "other"
            counts["label_class"][label_class] = counts["label_class"].get(label_class, 0) + 1
        aggregate_usage[asset] = counts

    source_path_presence = {}
    for asset in TARGETS:
        p = SOURCE_FACTIONS / "images/icons" / asset
        source_path_presence[asset] = {"exists": p.exists(), "target_path": "/info/basics/factions/images/icons/" + asset}
    v53_target_presence = {}
    for asset in TARGETS:
        p = V53_FACTIONS / "images/icons" / asset
        v53_target_presence[asset] = {"exists": p.exists(), "target_path": "/info/basics/factions/images/icons/" + asset}

    result = {
        "schema": "wow-faction-related-icon-semantic-audit/v1",
        "created_local": "2026-10-22",
        "network_requests": 0,
        "scope": {
            "source16_root": str(SOURCE16),
            "v53_export_root": str(V53),
            "source16_build_manifest_sha256": sha256(ROOT / ".scratch/offline-non-gallery-20261021-v16/build-manifest.json"),
            "v53_build_receipt": "research/continuous-recovery-20261022/integration/v53-build-receipt.json",
            "v53_root_browser_acceptance": "research/continuous-recovery-20261022/root-v53-browser-acceptance.json",
            "v53_root_browser_accepted": True,
            "candidate_source_identity": {
                "repository": REPO,
                "commit": COMMIT,
                "commit_date": COMMIT_DATE,
                "original_capture_date": None,
                "source_selection": "research/continuous-recovery-20261022/coolwow2-selected-source-tree.json",
            "source_selection_sha256": sha256(SOURCE_SELECTION),
            "safe_public_inventory": "research/continuous-recovery-20261022/network/coolwow2-item-icons01/runtime/public-inventory.json",
            "safe_public_inventory_sha256": sha256(SAFE_INVENTORY),
            },
        },
        "source_images": image_meta,
        "target_presence": {"source16": source_path_presence, "v53_export": v53_target_presence},
        "usage_counts": {asset: len(rows) for asset, rows in occurrences_by_asset.items()},
        "aggregate_usage": aggregate_usage,
        "source16_routes_by_target": routes_by_target,
        "occurrences_by_target": occurrences_by_asset,
        "all_target_occurrence_count": len(source_occurrences),
        "source_data_script_hashes": script_hash_rows(SOURCE16, set(script_rel)),
        "renderer_script_and_css_hashes": script_hash_rows(SOURCE16, set(renderer_rel)),
        "v53_data_script_hashes": script_hash_rows(V53, v53_data_script_paths),
        "v53_renderer_script_and_css_hashes": script_hash_rows(V53, v53_renderer_paths),
        "page_routes_by_data_script": page_routes,
        "page_routes_by_shared_renderer_asset": renderer_pages,
        "dynamic_reference_scan": reference_scan,
        "source16_same_stem_files_anywhere": {
            asset: ["/" + p.relative_to(SOURCE16).as_posix()
                    for p in SOURCE16.rglob("*") if p.is_file() and p.name.lower() == asset.lower()]
            for asset in TARGETS
        },
        "v53_same_stem_files_anywhere": {
            asset: ["/" + p.relative_to(V53).as_posix()
                    for p in V53.rglob("*") if p.is_file() and p.name.lower() == asset.lower()]
            for asset in TARGETS
        },
        "renderer_key_lines": key_lines,
        "v53_renderer_key_lines": v53_key_lines,
        "interpretation": {
            "INV_Scroll_03.gif": "reward-table icon for many heterogeneous recipes, patterns, plans, designs, and schematics; not a unique scroll item",
            "INV_Scroll_06.gif": "reward-table icon for heterogeneous recipes, designs, and patterns; not a unique scroll item",
            "INV_Wand_11.gif": "two Alliance/Horde rows both labeled Incendic Rod; item role is evidenced, visual identity to JPEG remains unverified",
            "reputation_rule": "source renderer maps itemStats[0..3] to Friendly/Honored/Revered/Exalted and displays only the selected bracket; excerpts record all defined tiers",
            "faction_rule": "RewardItem.playerFaction is Alliance or Horde; renderer places rows into separate faction tables/tabs",
            "pixel_identity": "No byte/pixel comparison to Source16 is possible because the original GIF targets are absent; shared basename is not proof of identical artwork.",
        },
        "unknowns": [
            "Original Source16 GIF bytes, MIME/format metadata, dimensions, animation frames, and pixel appearance remain unknown.",
            "No proof that the three later JPEGs visually match the missing GIFs; any reuse must be labeled later_related_source and preserve source/format distinction.",
            "Exact rendered CSS pixel size was not explicitly set for style_icon; renderer relies on the image's intrinsic dimensions, while wrapper offsets are defined in CSS.",
        ],
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUT),
        "sha256": sha256(OUT),
        "usage_counts": result["usage_counts"],
        "all_target_occurrence_count": len(source_occurrences),
        "data_script_count": len(script_rel),
        "route_map_count": len(page_routes),
        "v53_reference_counts": {asset: len(rows) for asset, rows in reference_scan["v53"].items()},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
