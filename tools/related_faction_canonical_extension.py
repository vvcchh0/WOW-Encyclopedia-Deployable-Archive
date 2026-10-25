"""Pinned reward artwork matched by the original game asset identifier."""
from __future__ import annotations

from dataclasses import dataclass, replace
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
import related_faction_item_extension as items

MAP_RELATIVE = "artifacts/related-faction-canonical-art-20261025/input-map.json"
MAP_SHA256 = "23bd4eae0e9c2dd395665ab6ff8ea1c0888995ff1cd059b5e01af404d6a76f6f"
ACCEPTANCE_RELATIVE = "docs/evidence/faction-canonical-art-20261025.json"
ACCEPTANCE_SHA256 = "b2393f5843b6b1ed53bd746620c3f2552a773f1b4f311db56ad21d61fc9b3b53"
ZIP_SHA256 = "6e334e1b0b4259b40bef37948dc40c80fd203815a5161e3b367cfa5b2622b22e"
ZIP_LENGTH = 83448
SOURCE_BYTES = 83743
PREFIX = "/info/basics/factions/images/icons/"
MORE_MAP_RELATIVE = "artifacts/related-faction-canonical-more-20261025/input-map.json"
THIRD_MAP_RELATIVE = "artifacts/related-faction-canonical-third-20261025/input-map.json"

@dataclass(frozen=True)
class _Profile:
    map_relative: str
    map_sha: str
    receipt_relative: str
    receipt_sha: str
    zip_sha: str
    zip_length: int
    source_bytes: int
    aliases: int
    base_profile: str
    base_assets: int
    base_aliases: int
    downloads: int
    local_pngs: int
    images: int = 48

_PROFILES = (
    _Profile(MAP_RELATIVE, MAP_SHA256, ACCEPTANCE_RELATIVE, ACCEPTANCE_SHA256,
             ZIP_SHA256, ZIP_LENGTH, SOURCE_BYTES, 49, items.MAP_RELATIVE, 10, 10, 47, 1),
    _Profile(MORE_MAP_RELATIVE, "8e19f8dd041e52bf6de56feaf1fa5936b0fff0a0441fcec954a562d1578b461f",
             "docs/evidence/faction-canonical-more-art-20261025.json",
             "adeb07b20d82af0aad6fa2053f6e48bbecd836748dd802a28dc921cd7032de0b",
             "ee52dd53488fb9174d25e57935706b8a20785c03f429c6480794192d2edda16c",
             78061, 78665, 48, MAP_RELATIVE, 58, 59, 48, 0),
    _Profile(THIRD_MAP_RELATIVE, "25020410e64e998480c55cb9d55c4855995cf2b16cc868c7e11e93bfac5d9059",
             "docs/evidence/faction-canonical-third-art-20261025.json",
             "d124f3fc57e66f15370a8208c3e17930275678f7149d8b92173d6527db0e8441",
             "dfc1a85dbbfb408a4948357e4dd7242033f26b863bcd32446a73f2441b0712cb",
             13649, 13620, 8, MORE_MAP_RELATIVE, 106, 107, 8, 0, 8),
)

def _profile(map_file, root):
    for profile in _PROFILES:
        if map_file == (root / profile.map_relative).resolve():
            return profile
    raise _fail("map path differs from the accepted profiles")

def _fail(message):
    return legacy.RelatedFactionIconError("canonical faction art: " + message)

def load_additional_assets(map_path: str | Path, workspace_root: str | Path):
    """Read a fixed, accepted artwork profile; never extract to disk."""
    root = Path(workspace_root).resolve()
    map_file = items._file(root, map_path)
    profile = _profile(map_file, root)
    raw = map_file.read_bytes()
    if items._sha(raw) != profile.map_sha:
        raise _fail("map SHA-256 mismatch")
    data = json.loads(raw)
    if (data.get("schema") != "wow-related-faction-canonical-art-map/v1"
            or data.get("status") != "accepted_parent_review"
            or data.get("acceptance_sha256") != profile.receipt_sha
            or data.get("source_manifest_sha256") != legacy.EXPECTED_SOURCE_MANIFEST_SHA256
            or data.get("base_profile") != profile.base_profile):
        raise _fail("source identity differs from acceptance")
    receipt = items._file(root, profile.receipt_relative).read_bytes()
    if items._sha(receipt) != profile.receipt_sha:
        raise _fail("acceptance receipt SHA-256 mismatch")
    zip_path = items._file(root, map_file.parent / "source-payloads.zip")
    if zip_path.stat().st_size != profile.zip_length:
        raise _fail("ZIP length mismatch")
    zipped = zip_path.read_bytes()
    if items._sha(zipped) != profile.zip_sha:
        raise _fail("ZIP SHA-256 mismatch")
    entries = data["entries"]
    if len(entries) != profile.images or data["source_bytes"] != profile.source_bytes:
        raise _fail("entry count or source byte count mismatch")
    names = {e["zip_member"] for e in entries}
    assets = []
    targets_seen = set()
    routes_seen = set()
    try:
        with zipfile.ZipFile(io.BytesIO(zipped)) as archive:
            infos = archive.infolist()
            if len(infos) != profile.images or len(names) != profile.images or {i.filename for i in infos} != names:
                raise _fail("ZIP differs from its member whitelist")
            for info in infos:
                mode = stat.S_IFMT(info.external_attr >> 16)
                if (info.is_dir() or mode not in (0, stat.S_IFREG) or info.flag_bits & 1
                        or not re.fullmatch(r"icons/[a-z0-9_]+\.(jpg|png)", info.filename)
                        or info.file_size > 65536):
                    raise _fail("unsafe ZIP member")
            for entry in entries:
                icon = entry["icon_id"]
                if not re.fullmatch(r"(?:inv|spell)_[a-z0-9_]+", icon):
                    raise _fail("unsafe game asset identifier")
                targets = entry["target_routes"]
                if not targets or targets[0] != entry["target_route"]:
                    raise _fail("primary target differs from alias list")
                for target in targets:
                    if (not re.fullmatch(re.escape(PREFIX) + r"[A-Za-z0-9_]+\.(gif|jpg)", target)
                            or Path(target).stem.lower() != icon or target in targets_seen):
                        raise _fail("unsafe or duplicate original target")
                    targets_seen.add(target)
                route = entry["route"]
                extension = "png" if entry["format"] == "PNG" else "jpg"
                if route != f"/__offline/related-faction-icons/canonical_{icon}.{extension}" or route in routes_seen:
                    raise _fail("unsafe or duplicate generated route")
                routes_seen.add(route)
                payload = archive.read(entry["zip_member"])
                if len(payload) != entry["length"] or items._sha(payload) != entry["sha256"]:
                    raise _fail("payload length/hash mismatch")
                with Image.open(io.BytesIO(payload)) as image:
                    if image.format != entry["format"] or getattr(image, "n_frames", 1) != 1:
                        raise _fail("payload format/frame mismatch")
                    image.load()
                    if image.size != (entry["width"], entry["height"]):
                        raise _fail("payload dimensions mismatch")
                if entry["format"] == "PNG":
                    blob = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
                    if icon != "spell_fire_sealoffire" or blob != "3411dd64a8c7556afffcd3f77bdee5670613d11e":
                        raise _fail("local PNG differs from the accepted Git object")
                elif entry["source_url"] != f"https://cdn.cavernoftime.com/tbc/icons/large/{icon}.jpg":
                    raise _fail("source URL differs from the inspected game asset rule")
                for page in entry["page_routes"]:
                    if not re.fullmatch(r"/info/basics/factions/[a-z0-9]+/[a-z0-9-]+\.(xml|html)", page):
                        raise _fail("notice page outside accepted faction scope")
                assets.append(legacy.RelatedFactionIconAsset(
                    route=route, relative=route.lstrip("/"), target_route=targets[0], data=payload,
                    mime="image/png" if entry["format"] == "PNG" else "image/jpeg",
                    metadata={**entry, "images_reencoded": False, "original_capture_timestamp": None,
                              "display_size": [36, 36]},
                ))
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise _fail(f"source archive cannot be read: {exc}") from exc
    if (len(targets_seen) != profile.aliases or sum(len(a.data) for a in assets) != profile.source_bytes
            or sum(a.mime == "image/png" for a in assets) != profile.local_pngs
            or sum(a.mime == "image/jpeg" for a in assets) != profile.downloads):
        raise _fail("decoded targets or aggregate bytes mismatch")
    return tuple(assets)

def extend_bundle(map_path, workspace_root, base_path, base_bundle):
    root = Path(workspace_root).resolve()
    profile = _profile(items._file(root, map_path), root)
    additional = load_additional_assets(map_path, workspace_root)
    if len(base_bundle.assets) != profile.base_assets or len(base_bundle.route_reuses) != profile.base_aliases:
        raise _fail("requires the accepted preceding faction profile")
    assets = (*base_bundle.assets, *additional)
    routes = dict(base_bundle.route_reuses)
    generated = {a.route for a in base_bundle.assets}
    for asset in additional:
        if asset.route in generated:
            raise _fail("generated route collides with a baseline asset")
        generated.add(asset.route)
        for target in asset.metadata["target_routes"]:
            if target in routes:
                raise _fail("original target collides with a baseline alias")
            routes[target] = asset.route
    base = legacy._normalize_base_path(base_path)
    catalog_url = html.escape(base + legacy.EXPECTED_CATALOG_RELATIVE, quote=True)
    notice = ('<aside id="__offline-related-faction-icons" role="note" '
              'style="padding:6px 12px;background:#eadbb7;color:#302619;'
              'font:13px/1.5 Arial,sans-serif;text-align:center">'
              'Some reward icons use later game archives. '
              f'<a href="{catalog_url}" style="color:#174f7d;text-decoration:underline">Sources</a>.</aside>')
    rules = []
    for asset in assets:
        width, height = asset.metadata.get("display_size", [36, 36])
        rules.append(f'img[src$="{asset.route}"]{{width:{width}px;height:{height}px;vertical-align:middle}}')
    layout = '<style id="__offline-faction-item-art-layout">' + ''.join(rules) + '</style>'
    shared_reward_pages = {
        "/pvp/rewards-general-armor.html", "/pvp/rewards-veterans-armor.html",
        "/pvp/rewards-vindicators-armor.html",
    }
    pages = set(base_bundle.notice_by_page) | {p for a in additional for p in a.metadata["page_routes"]} | shared_reward_pages
    notices = {p: layout + notice for p in pages}
    metadata = {
        "source_label": "Related faction art: coolwow2 (2015), TBC calculator (2019), Cavern of Time TBC data/art (observed 2026-10-25)",
        "source_manifest_sha256": legacy.EXPECTED_SOURCE_MANIFEST_SHA256,
        "classification": "later_related_source", "original_capture_timestamp": None,
        "original_2008_images_recovered": 0, "historical_original_images_recovered": 0,
        "images_reencoded": False, "image_count": len(assets), "target_count": len(routes),
        "source_bytes": sum(len(a.data) for a in assets),
        "source_acceptance_sha256": profile.receipt_sha,
        "additional_notice_pages_for_shared_reward_scripts": sorted(shared_reward_pages),
        "base_profile": dict(base_bundle.source_metadata),
        "additional_profile": {"map_sha256": profile.map_sha, "zip_sha256": profile.zip_sha,
                               "acceptance_sha256": profile.receipt_sha, "image_count": profile.images,
                               "new_downloaded_images": profile.downloads, "existing_png_reuses": profile.local_pngs},
    }
    catalog = legacy._make_catalog(base, list(assets), metadata)
    return replace(base_bundle, assets=assets, route_reuses=routes, catalog_bytes=catalog,
                   estimated_bytes=metadata["source_bytes"] + len(catalog), source_metadata=metadata,
                   notice_by_page=notices, map_sha256=profile.map_sha, source_acceptance_sha256=profile.receipt_sha)
