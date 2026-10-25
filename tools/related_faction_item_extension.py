"""Seven pinned item-icon associations added to the unchanged v54 bundle."""
from __future__ import annotations

from dataclasses import replace
import hashlib
import html
import io
import json
from pathlib import Path
import re
import stat
import zipfile

from PIL import Image
import related_faction_icons as legacy

MAP_RELATIVE = "artifacts/related-faction-item-icons-20261025/input-map.json"
MAP_SHA256 = "2341188c22d531b42437881823c7fda63a45d58e62e131033cfdaabc89e3d750"
ACCEPTANCE_SHA256 = "3b817bf6c814e7166680251f7619bc563fb569d20040700362b6129e5b7404e8"
ZIP_SHA256 = "61c3465c8c6aef76fad5c183714f809485afb4895af1f29427e023ba2ac55379"
ZIP_LENGTH = 15667
SOURCE_BYTES = 15498
PAGES = frozenset({
    "/info/basics/factions/hellfire/hellfire.xml",
    "/info/basics/factions/zangarmarsh/zangarpvp.xml",
})

def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def _file(root: Path, value: str | Path) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    if candidate.is_symlink():
        raise legacy.RelatedFactionIconError("item-art input is a symlink")
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise legacy.RelatedFactionIconError("item-art input is outside the workspace or missing")
    for parent in (candidate, *candidate.parents):
        if parent == root.parent:
            break
        if parent.is_symlink() or getattr(parent.lstat(), "st_file_attributes", 0) & 0x400:
            raise legacy.RelatedFactionIconError("item-art input contains a reparse point")
    return resolved

def load_additional_assets(map_path: str | Path, workspace_root: str | Path):
    """Validate only the fixed public seven-image bundle, without any writes."""
    root = Path(workspace_root).resolve()
    map_file = _file(root, map_path)
    if map_file != (root / MAP_RELATIVE).resolve():
        raise legacy.RelatedFactionIconError("item-art map path is not the accepted profile")
    raw = map_file.read_bytes()
    if _sha(raw) != MAP_SHA256:
        raise legacy.RelatedFactionIconError("item-art map SHA-256 differs from the accepted profile")
    data = json.loads(raw)
    if (
        data.get("schema") != "wow-related-faction-item-art-map/v1"
        or data.get("status") != "accepted_parent_review"
        or data.get("acceptance_sha256") != ACCEPTANCE_SHA256
        or data.get("source_manifest_sha256") != legacy.EXPECTED_SOURCE_MANIFEST_SHA256
        or data.get("base_profile") != legacy.EXPECTED_MAP_RELATIVE
    ):
        raise legacy.RelatedFactionIconError("item-art source identity differs from accepted inputs")
    receipt = _file(root, "docs/evidence/faction-item-art-20261025.json").read_bytes()
    if _sha(receipt) != ACCEPTANCE_SHA256:
        raise legacy.RelatedFactionIconError("item-art acceptance receipt SHA-256 mismatch")
    zip_path = _file(root, map_file.parent / "source-payloads.zip")
    if zip_path.stat().st_size != ZIP_LENGTH:
        raise legacy.RelatedFactionIconError("item-art ZIP length mismatch")
    zipped = zip_path.read_bytes()
    if _sha(zipped) != ZIP_SHA256:
        raise legacy.RelatedFactionIconError("item-art ZIP SHA-256 mismatch")
    entries = data["entries"]
    if len(entries) != 7 or data["source_bytes"] != SOURCE_BYTES:
        raise legacy.RelatedFactionIconError("item-art entry count or aggregate size mismatch")
    expected_names = {e["zip_member"] for e in entries}
    assets = []
    try:
        with zipfile.ZipFile(io.BytesIO(zipped)) as archive:
            infos = archive.infolist()
            if len(infos) != 7 or len(expected_names) != 7 or {i.filename for i in infos} != expected_names:
                raise legacy.RelatedFactionIconError("item-art ZIP differs from its seven-member whitelist")
            for info in infos:
                mode = info.external_attr >> 16
                if info.is_dir() or (stat.S_IFMT(mode) not in (0, stat.S_IFREG)) or info.flag_bits & 1:
                    raise legacy.RelatedFactionIconError("item-art ZIP contains an unsafe member")
                if not re.fullmatch(r"icons/[a-z0-9_]+\.(jpg|png)", info.filename) or info.file_size > 65536:
                    raise legacy.RelatedFactionIconError("item-art ZIP member exceeds accepted path/size limits")
            for entry in entries:
                payload = archive.read(entry["zip_member"])
                if len(payload) != entry["length"] or _sha(payload) != entry["sha256"]:
                    raise legacy.RelatedFactionIconError("item-art payload length/hash mismatch")
                with Image.open(io.BytesIO(payload)) as image:
                    if image.format != entry["format"] or getattr(image, "n_frames", 1) != 1:
                        raise legacy.RelatedFactionIconError("item-art payload format/frame mismatch")
                    image.load()
                    if image.size != (entry["width"], entry["height"]):
                        raise legacy.RelatedFactionIconError("item-art payload dimensions mismatch")
                if not set(entry["page_routes"]).issubset(PAGES):
                    raise legacy.RelatedFactionIconError("item-art notice page exceeds accepted scope")
                route = entry["route"]
                if not re.fullmatch(r"/__offline/related-faction-icons/[a-z0-9_]+\.(jpg|png)", route):
                    raise legacy.RelatedFactionIconError("item-art canonical route is unsafe")
                assets.append(legacy.RelatedFactionIconAsset(
                    route=route, relative=route.lstrip("/"),
                    target_route=entry["target_route"], data=payload,
                    mime="image/png" if entry["format"] == "PNG" else "image/jpeg",
                    metadata={**entry, "images_reencoded": False, "original_capture_timestamp": None,
                              "display_size": [16, 16] if entry["icon_id"] == "inv_misc_token_honorhold" else [36, 36]},
                ))
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise legacy.RelatedFactionIconError(f"item-art source bundle cannot be decoded: {exc}") from exc
    if sum(len(asset.data) for asset in assets) != SOURCE_BYTES:
        raise legacy.RelatedFactionIconError("item-art decoded aggregate differs from accepted bytes")
    return tuple(assets)

def extend_bundle(map_path: str | Path, workspace_root: str | Path, base_path: str, base_bundle):
    additional = load_additional_assets(map_path, workspace_root)
    if len(base_bundle.assets) != 3 or len(base_bundle.route_reuses) != 3:
        raise legacy.RelatedFactionIconError("item-art extension requires the three-icon v54 baseline")
    assets = (*base_bundle.assets, *additional)
    routes = dict(base_bundle.route_reuses)
    for asset in additional:
        if asset.target_route in routes or asset.route in routes.values():
            raise legacy.RelatedFactionIconError("item-art extension collides with a baseline route")
        routes[asset.target_route] = asset.route
    normalized_base = legacy._normalize_base_path(base_path)
    catalog_url = html.escape(normalized_base + legacy.EXPECTED_CATALOG_RELATIVE, quote=True)
    notice = (
        '<aside id="__offline-related-faction-icons" role="note" '
        'style="padding:6px 12px;background:#eadbb7;color:#302619;'
        'font:13px/1.5 Arial,sans-serif;text-align:center">'
        'Some reward icons use later game archives. '
        f'<a href="{catalog_url}" style="color:#174f7d;text-decoration:underline">Sources</a>.'
        '</aside>'
    )
    # The old item slot holds a 36px icon; its price line starts at y=35 in a
    # 55px row. Keep the larger JPEG/PNG sources intact and size only these
    # seven displayed substitutes. The lost GIF dimensions remain unknown.
    rules = []
    for asset in additional:
        width, height = asset.metadata["display_size"]
        rules.append(
            f'img[src$="{asset.route}"]{{width:{width}px;height:{height}px;vertical-align:middle}}'
        )
    layout = '<style id="__offline-faction-item-art-layout">' + ''.join(rules) + '</style>'
    notices = dict(base_bundle.notice_by_page)
    notices.update({page: layout + notice for page in PAGES})
    metadata = {
        "source_label": "Related faction art: coolwow2 (2015), TBC calculator (2019), Cavern of Time TBC data/art (observed 2026-10-25)",
        "source_manifest_sha256": legacy.EXPECTED_SOURCE_MANIFEST_SHA256,
        "classification": "later_related_source", "original_capture_timestamp": None,
        "original_2008_images_recovered": 0, "historical_original_images_recovered": 0,
        "images_reencoded": False, "image_count": len(assets),
        "source_bytes": sum(len(a.data) for a in assets),
        "source_acceptance_sha256": ACCEPTANCE_SHA256,
        "base_profile": dict(base_bundle.source_metadata),
        "additional_profile": {"map_sha256": MAP_SHA256, "zip_sha256": ZIP_SHA256,
                               "acceptance_sha256": ACCEPTANCE_SHA256, "image_count": 7,
                               "new_downloaded_images": 6, "existing_png_reuses": 1},
    }
    catalog = legacy._make_catalog(normalized_base, list(assets), metadata)
    return replace(
        base_bundle, assets=assets, route_reuses=routes, catalog_bytes=catalog,
        estimated_bytes=metadata["source_bytes"] + len(catalog), source_metadata=metadata,
        notice_by_page=notices, map_sha256=MAP_SHA256,
        source_acceptance_sha256=ACCEPTANCE_SHA256,
    )
