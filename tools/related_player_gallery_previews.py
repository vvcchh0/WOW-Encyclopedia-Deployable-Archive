"""Validate and render a separate namespace for related player-gallery previews."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Any, Mapping
import zipfile

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - test/runtime dependency is installed
    Image = None  # type: ignore[assignment]
    _PIL_IMPORT_ERROR = exc
else:
    _PIL_IMPORT_ERROR = None


class RelatedPlayerGalleryPreviewError(ValueError):
    """Raised when the optional related-preview map or payload is unsafe or drifted."""


EXPECTED_MAP_SCHEMA = "wow-related-player-gallery-preview-map/v1"
EXPECTED_DESIGN_SHA256 = "5a54df01a5955eeba87cd14b7575c7b46f6a853a494382c9377a512dffe555db"
EXPECTED_SOURCE_ACCEPTANCE_SHA256 = "f8523f0f70639fd82d3df6dc40c97835d904234bf9a5a4b6943eb08f05bf4efd"
EXPECTED_REPOSITORY = "boom8866/coolwow2"
EXPECTED_COMMIT = "09c52b7673871b8048da92e5a13ed753fc08162f"
EXPECTED_SOURCE_CLASSIFICATION = "later_related_source_2015"
EXPECTED_SOURCE_URL = f"https://github.com/{EXPECTED_REPOSITORY}/tree/{EXPECTED_COMMIT}"
EXPECTED_CATALOG_RELATIVE = "__offline/related-player-gallery-previews.json"
EXPECTED_ASSET_DIRECTORY = "__offline/related-player-gallery-previews"
EXPECTED_PAGE_COUNTS = {
    "/info/dungeons/cot-hyjal-gallery.html": 3,
    "/info/dungeons/cot-escape-gallery.html": 2,
    "/info/dungeons/cot-opening-gallery.html": 3,
}
EXPECTED_PAYLOAD_BYTES = 42922
MAX_MAP_BYTES = 65536
MAX_ARCHIVE_BYTES = 100000
CAPTION = "French guide previews"
SECTION_ID = "offline-related-player-gallery-previews"


EXPECTED_ITEMS: tuple[dict[str, Any], ...] = (
    {
        "archive_member": "payloads/01.jpg", "route": f"/{EXPECTED_ASSET_DIRECTORY}/01.jpg", "relative": f"{EXPECTED_ASSET_DIRECTORY}/01.jpg",
        "git_path": "instance/images/ss1-thumb_002.jpg", "git_blob_sha1": "ad4d998debbe66d971bc3e2e6f992bb72bf4afbd",
        "sha256": "b8743367a871f7937b8476cc84919ecc8a8fc9a1a234c09930f39fa96db31810", "length": 5261,
        "frames": [[150, 110]], "european_gallery_anchor": "http://www.wow-europe.com/fr/info/basics/dungeons/bc/cot-escape-gallery.html#37",
        "existing_player_gallery_row": 15, "target_page_route": "/info/dungeons/cot-escape-gallery.html",
        "group_label": "Escape from Durnholde", "image_role": "Related French guide thumbnail; full screenshot and US sequence identity unknown",
    },
    {
        "archive_member": "payloads/02.jpg", "route": f"/{EXPECTED_ASSET_DIRECTORY}/02.jpg", "relative": f"{EXPECTED_ASSET_DIRECTORY}/02.jpg",
        "git_path": "instance/images/ss2-thumb_002.jpg", "git_blob_sha1": "5bf9d4dfb16558e9aa9ca25b28ccc771eda40a7a",
        "sha256": "15ae264a209476dc64f27708400f1ff6130f912bb45ba003e4e44ca9e692b153", "length": 4652,
        "frames": [[150, 110]], "european_gallery_anchor": "http://www.wow-europe.com/fr/info/basics/dungeons/bc/cot-escape-gallery.html#26",
        "existing_player_gallery_row": 15, "target_page_route": "/info/dungeons/cot-escape-gallery.html",
        "group_label": "Escape from Durnholde", "image_role": "Related French guide thumbnail; full screenshot and US sequence identity unknown",
    },
    {
        "archive_member": "payloads/03.jpg", "route": f"/{EXPECTED_ASSET_DIRECTORY}/03.jpg", "relative": f"{EXPECTED_ASSET_DIRECTORY}/03.jpg",
        "git_path": "instance/images/ss1-thumb_003.jpg", "git_blob_sha1": "a1da6e788564ddb807ef39e2526c837e3a80e9b5",
        "sha256": "22769e167607dcdd04ead6c100811d7229a6ee002f732302d9adfc45ce217a8c", "length": 5320,
        "frames": [[150, 110]], "european_gallery_anchor": "http://www.wow-europe.com/fr/info/basics/dungeons/bc/cot-opening-gallery.html#22",
        "existing_player_gallery_row": 16, "target_page_route": "/info/dungeons/cot-opening-gallery.html",
        "group_label": "Opening of the Dark Portal", "image_role": "Related French guide thumbnail; full screenshot and US sequence identity unknown",
    },
    {
        "archive_member": "payloads/04.jpg", "route": f"/{EXPECTED_ASSET_DIRECTORY}/04.jpg", "relative": f"{EXPECTED_ASSET_DIRECTORY}/04.jpg",
        "git_path": "instance/images/ss2-thumb_003.jpg", "git_blob_sha1": "dbac1988822b009f3a1f8862b98e1a17c566c1a5",
        "sha256": "db44102c7f33b841a8cd9c2527934ffb7278a3791b4fb67077ae9700cbd69be5", "length": 6497,
        "frames": [[150, 110]], "european_gallery_anchor": "http://www.wow-europe.com/fr/info/basics/dungeons/bc/cot-opening-gallery.html#17",
        "existing_player_gallery_row": 16, "target_page_route": "/info/dungeons/cot-opening-gallery.html",
        "group_label": "Opening of the Dark Portal", "image_role": "Related French guide thumbnail; full screenshot and US sequence identity unknown",
    },
    {
        "archive_member": "payloads/05.jpg", "route": f"/{EXPECTED_ASSET_DIRECTORY}/05.jpg", "relative": f"{EXPECTED_ASSET_DIRECTORY}/05.jpg",
        "git_path": "instance/images/ss3-thumb.jpg", "git_blob_sha1": "180f827454e09bfc4275a67aea06b6ba1913c6e8",
        "sha256": "be12c909529850905463412d98ce14345dda158bada213e844b493d4b3c8ee2f", "length": 4685,
        "frames": [[150, 110]], "european_gallery_anchor": "http://www.wow-europe.com/fr/info/basics/dungeons/bc/cot-opening-gallery.html#5",
        "existing_player_gallery_row": 16, "target_page_route": "/info/dungeons/cot-opening-gallery.html",
        "group_label": "Opening of the Dark Portal", "image_role": "Related French guide thumbnail; full screenshot and US sequence identity unknown",
    },
    {
        "archive_member": "payloads/06.jpg", "route": f"/{EXPECTED_ASSET_DIRECTORY}/06.jpg", "relative": f"{EXPECTED_ASSET_DIRECTORY}/06.jpg",
        "git_path": "instance/images/ss1-thumb.jpg", "git_blob_sha1": "58edaa1fdc96995fb879315cac29547b57dc02e6",
        "sha256": "c1ac564fa3b64b04b8f44c970472d708d7acc81743bb561e6ba2136b45619eaa", "length": 5308,
        "frames": [[150, 110]], "european_gallery_anchor": "http://www.wow-europe.com/fr/info/basics/dungeons/bc/cot-mounthyjal-gallery.html#42",
        "existing_player_gallery_row": 6, "target_page_route": "/info/dungeons/cot-hyjal-gallery.html",
        "group_label": "Battle for Mount Hyjal", "image_role": "Related French guide thumbnail; full screenshot and US sequence identity unknown",
    },
    {
        "archive_member": "payloads/07.jpg", "route": f"/{EXPECTED_ASSET_DIRECTORY}/07.jpg", "relative": f"{EXPECTED_ASSET_DIRECTORY}/07.jpg",
        "git_path": "instance/images/ss2-thumb.jpg", "git_blob_sha1": "6ff2ae39cf03e5860a56dc24132e3474e889c538",
        "sha256": "729ff9855ece68efe91bcb795b5cd47d0c8895cf5f272966cfceff29e362a56b", "length": 7095,
        "frames": [[150, 110]], "european_gallery_anchor": "http://www.wow-europe.com/fr/info/basics/dungeons/bc/cot-mounthyjal-gallery.html#25",
        "existing_player_gallery_row": 6, "target_page_route": "/info/dungeons/cot-hyjal-gallery.html",
        "group_label": "Battle for Mount Hyjal", "image_role": "Related French guide thumbnail; full screenshot and US sequence identity unknown",
    },
    {
        "archive_member": "payloads/08.jpg", "route": f"/{EXPECTED_ASSET_DIRECTORY}/08.jpg", "relative": f"{EXPECTED_ASSET_DIRECTORY}/08.jpg",
        "git_path": "instance/images/ss3-thumb_002.jpg", "git_blob_sha1": "e8fa283435a0393507820e6bb4200a893e7a3fd8",
        "sha256": "46c2da01f1b747ba4b418350e23f2aff1b0883cfbca7859d298ab479ab76d1ae", "length": 4104,
        "frames": [[150, 110]], "european_gallery_anchor": "http://www.wow-europe.com/fr/info/basics/dungeons/bc/cot-mounthyjal-gallery.html#7",
        "existing_player_gallery_row": 6, "target_page_route": "/info/dungeons/cot-hyjal-gallery.html",
        "group_label": "Battle for Mount Hyjal", "image_role": "Related French guide thumbnail; full screenshot and US sequence identity unknown",
    },
)


@dataclass(frozen=True)
class RelatedPlayerGalleryPreviewAsset:
    route: str
    relative: str
    data: bytes
    mime: str
    metadata: Mapping[str, Any]


@dataclass(frozen=True)
class RelatedPlayerGalleryPreviewBundle:
    assets: tuple[RelatedPlayerGalleryPreviewAsset, ...]
    assets_by_page: Mapping[str, tuple[RelatedPlayerGalleryPreviewAsset, ...]]
    catalog_relative: str
    catalog_bytes: bytes
    estimated_bytes: int
    source_metadata: Mapping[str, Any]
    map_sha256: str
    archive_sha256: str
    archive_length: int


def _fail(message: str) -> RelatedPlayerGalleryPreviewError:
    return RelatedPlayerGalleryPreviewError(message)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_map(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        if path.stat().st_size > MAX_MAP_BYTES:
            raise _fail("related player-gallery preview map exceeds its size limit")
        raw = path.read_bytes()
        if len(raw) > MAX_MAP_BYTES:
            raise _fail("related player-gallery preview map exceeds its size limit")
        payload = json.loads(raw.decode("utf-8"))
    except RelatedPlayerGalleryPreviewError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _fail(f"cannot read related player-gallery preview map: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise _fail("related player-gallery preview map must be a JSON object")
    return payload, raw


def _resolve_workspace_file(root: Path, path_value: Any, label: str) -> Path:
    if not isinstance(path_value, str) or not path_value:
        raise _fail(f"{label} path must be a non-empty string")
    pure = PurePosixPath(path_value)
    if pure.is_absolute() or "\\" in path_value or any(part in {"", ".", ".."} for part in pure.parts):
        raise _fail(f"{label} path is unsafe")
    candidate = (root / Path(*pure.parts)).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise _fail(f"{label} path escapes workspace") from exc
    if not candidate.is_file():
        raise _fail(f"{label} file does not exist: {path_value}")
    return candidate


def _validate_source_metadata(payload: Mapping[str, Any]) -> dict[str, Any]:
    expected = {
        "repository": EXPECTED_REPOSITORY,
        "commit": EXPECTED_COMMIT,
        "commit_url": EXPECTED_SOURCE_URL,
        "classification": EXPECTED_SOURCE_CLASSIFICATION,
        "design_decision_sha256": EXPECTED_DESIGN_SHA256,
        "source_acceptance_sha256": EXPECTED_SOURCE_ACCEPTANCE_SHA256,
    }
    source = payload.get("source")
    if source != expected:
        raise _fail("source metadata does not match the accepted repository, commit, design, and source-acceptance hashes")
    return dict(expected) | {
        "payload_count": len(EXPECTED_ITEMS),
        "payload_bytes": EXPECTED_PAYLOAD_BYTES,
        "original_us_gallery_images_added": 0,
        "source_page_link": EXPECTED_SOURCE_URL,
    }


def _validate_jpeg(data: bytes, item: Mapping[str, Any]) -> tuple[int, int, int]:
    if Image is None:  # pragma: no cover
        raise _fail(f"Pillow is required for full JPEG validation: {_PIL_IMPORT_ERROR}")
    try:
        with Image.open(io.BytesIO(data)) as image:
            image_format = image.format
            width, height = image.size
            frame_count = int(getattr(image, "n_frames", 1))
            if image_format != "JPEG":
                raise _fail(f"{item['git_path']} decodes as {image_format}, not JPEG")
            if frame_count != 1:
                raise _fail(f"{item['git_path']} has {frame_count} frames, expected one")
            for frame_index in range(frame_count):
                image.seek(frame_index)
                image.load()
                image.convert("RGB").tobytes()
    except RelatedPlayerGalleryPreviewError:
        raise
    except Exception as exc:
        raise _fail(f"{item['git_path']} is not fully decodable: {exc}") from exc
    expected_size = item["frames"][0]
    if [width, height] != expected_size or frame_count != 1:
        raise _fail(f"{item['git_path']} dimensions/frames differ from the accepted 150x110 JPEG")
    return width, height, frame_count


def _make_catalog(
    *,
    base_path: str,
    source_metadata: Mapping[str, Any],
    map_sha256: str,
    archive_sha256: str,
    assets: tuple[RelatedPlayerGalleryPreviewAsset, ...],
) -> bytes:
    payload = {
        "schema": "wow-related-player-gallery-preview-catalog/v1",
        "catalog_relative": EXPECTED_CATALOG_RELATIVE,
        "base_path": base_path,
        "source": dict(source_metadata),
        "map_sha256": map_sha256,
        "source_archive_sha256": archive_sha256,
        "image_count": len(assets),
        "page_counts": dict(EXPECTED_PAGE_COUNTS),
        "original_us_gallery_images_added": 0,
        "images": [
            {
                **dict(asset.metadata),
                "route": asset.route,
                "static_path": f"{base_path}{asset.relative}" if base_path else "/" + asset.relative,
                "mime": asset.mime,
            }
            for asset in assets
        ],
    }
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def load_related_player_gallery_preview_bundle(
    map_path: str | Path,
    workspace_root: str | Path,
    base_path: str,
) -> RelatedPlayerGalleryPreviewBundle:
    """Load a map-pinned ZIP containing exactly the eight accepted JPEG blobs."""

    root = Path(workspace_root).resolve()
    if not root.is_dir():
        raise _fail(f"workspace_root is not a directory: {workspace_root}")
    candidate = Path(map_path)
    map_file = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        map_file.relative_to(root)
    except ValueError as exc:
        raise _fail("related player-gallery preview map is outside workspace") from exc
    payload, map_raw = _read_map(map_file)
    if payload.get("schema") != EXPECTED_MAP_SCHEMA:
        raise _fail("related player-gallery preview map schema is not accepted")
    source_metadata = _validate_source_metadata(payload)
    if payload.get("page_counts") != EXPECTED_PAGE_COUNTS:
        raise _fail("related player-gallery preview map page counts differ from the accepted 3/2/3 grouping")
    if payload.get("expected_image_count") != len(EXPECTED_ITEMS) or payload.get("expected_payload_bytes") != EXPECTED_PAYLOAD_BYTES:
        raise _fail("related player-gallery preview map scope totals differ from the accepted eight images")
    entries = payload.get("items")
    if not isinstance(entries, list) or entries != list(EXPECTED_ITEMS):
        raise _fail("related player-gallery preview map items differ from the exact accepted Git blobs/routes")

    archive = payload.get("archive")
    if not isinstance(archive, dict) or set(archive) != {"path", "sha256", "length"}:
        raise _fail("related player-gallery preview archive record is malformed")
    if (
        not isinstance(archive["length"], int)
        or isinstance(archive["length"], bool)
        or archive["length"] < EXPECTED_PAYLOAD_BYTES
        or archive["length"] > MAX_ARCHIVE_BYTES
    ):
        raise _fail("related player-gallery preview archive length is outside the accepted bound")
    if PurePosixPath(str(archive["path"])).name != "source-payloads.zip":
        raise _fail("related player-gallery preview archive must be the sibling source-payloads.zip")
    archive_path = _resolve_workspace_file(map_file.parent, archive["path"], "source archive")
    try:
        archive_bytes = archive_path.read_bytes()
    except OSError as exc:
        raise _fail(f"cannot read related player-gallery preview archive: {exc}") from exc
    archive_sha = _sha256(archive_bytes)
    if len(archive_bytes) != archive["length"] or archive_sha != archive["sha256"]:
        raise _fail("related player-gallery preview archive length or SHA mismatch")

    try:
        zip_file = zipfile.ZipFile(io.BytesIO(archive_bytes), "r")
    except (OSError, zipfile.BadZipFile) as exc:
        raise _fail(f"related player-gallery preview archive is not a valid ZIP: {exc}") from exc
    with zip_file:
        infos = zip_file.infolist()
        expected_members = [str(item["archive_member"]) for item in EXPECTED_ITEMS]
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or names != expected_members:
            raise _fail("related player-gallery ZIP members do not exactly match the ordered allowlist")
        if zip_file.comment:
            raise _fail("related player-gallery ZIP comments are not accepted")
        assets: list[RelatedPlayerGalleryPreviewAsset] = []
        assets_by_page: dict[str, list[RelatedPlayerGalleryPreviewAsset]] = {}
        total_bytes = 0
        for info, item in zip(infos, EXPECTED_ITEMS, strict=True):
            member_path = PurePosixPath(info.filename)
            mode = (info.external_attr >> 16) & 0xFFFF
            if (
                member_path.is_absolute()
                or "\\" in info.filename
                or any(part in {"", ".", ".."} for part in member_path.parts)
                or info.is_dir()
                or stat.S_ISLNK(mode)
                or info.flag_bits & 0x1
                or info.compress_type != zipfile.ZIP_STORED
                or info.file_size != item["length"]
            ):
                raise _fail(f"unsafe or unexpected ZIP entry: {info.filename}")
            try:
                data = zip_file.read(info)
            except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
                raise _fail(f"cannot read ZIP member {info.filename}: {exc}") from exc
            if len(data) != item["length"] or _sha256(data) != item["sha256"]:
                raise _fail(f"{item['git_path']} payload length or SHA mismatch")
            git_blob_sha = hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()
            if git_blob_sha != item["git_blob_sha1"]:
                raise _fail(f"{item['git_path']} Git blob SHA-1 mismatch")
            width, height, frames = _validate_jpeg(data, item)
            metadata = dict(item) | {
                "repository": EXPECTED_REPOSITORY,
                "commit": EXPECTED_COMMIT,
                "classification": EXPECTED_SOURCE_CLASSIFICATION,
                "source_url": EXPECTED_SOURCE_URL,
                "mime": "image/jpeg",
                "width": width,
                "height": height,
                "decoded_frames": frames,
                "original_us_gallery_image": False,
            }
            asset = RelatedPlayerGalleryPreviewAsset(
                route=str(item["route"]), relative=str(item["relative"]), data=data,
                mime="image/jpeg", metadata=metadata,
            )
            assets.append(asset)
            assets_by_page.setdefault(str(item["target_page_route"]), []).append(asset)
            total_bytes += len(data)
    if total_bytes != EXPECTED_PAYLOAD_BYTES:
        raise _fail(f"related player-gallery payload total is {total_bytes}, expected {EXPECTED_PAYLOAD_BYTES}")
    actual_page_counts = {route: len(items) for route, items in assets_by_page.items()}
    if actual_page_counts != EXPECTED_PAGE_COUNTS:
        raise _fail("related player-gallery asset groups differ from the accepted three-page 3/2/3 split")

    map_sha = _sha256(map_raw)
    final_source_metadata = dict(source_metadata) | {
        "map_sha256": map_sha,
        "source_archive_sha256": archive_sha,
        "source_archive_length": len(archive_bytes),
        "payload_bytes": total_bytes,
        "image_count": len(assets),
        "page_counts": actual_page_counts,
        "original_us_gallery_images_added": 0,
    }
    frozen_assets = tuple(assets)
    frozen_groups = {route: tuple(items) for route, items in assets_by_page.items()}
    catalog_bytes = _make_catalog(
        base_path=base_path,
        source_metadata=final_source_metadata,
        map_sha256=map_sha,
        archive_sha256=archive_sha,
        assets=frozen_assets,
    )
    return RelatedPlayerGalleryPreviewBundle(
        assets=frozen_assets,
        assets_by_page=frozen_groups,
        catalog_relative=EXPECTED_CATALOG_RELATIVE,
        catalog_bytes=catalog_bytes,
        estimated_bytes=total_bytes + len(catalog_bytes),
        source_metadata=final_source_metadata,
        map_sha256=map_sha,
        archive_sha256=archive_sha,
        archive_length=len(archive_bytes),
    )


def insert_preview_section(
    text: str,
    *,
    page_route: str,
    bundle: RelatedPlayerGalleryPreviewBundle,
    route_to_static: Mapping[str, str],
) -> tuple[str, bool, int]:
    """Insert one independent related-preview section before the page's unique contentBlock span."""

    assets = bundle.assets_by_page.get(page_route)
    if assets is None:
        return text, False, 0
    if f'id="{SECTION_ID}"' in text:
        raise _fail(f"source page already contains the related preview section: {page_route}")
    source_link = escape(EXPECTED_SOURCE_URL, quote=True)
    figures: list[str] = []
    for asset in assets:
        static_url = route_to_static.get(asset.route)
        if not static_url:
            raise _fail(f"related preview has no output route: {asset.route}")
        safe_url = escape(static_url, quote=True)
        label = escape(str(asset.metadata["group_label"]))
        alt = escape(f"French guide preview: {label}", quote=True)
        figures.append(
            '<li style="width:150px;flex:0 0 150px;margin:0">'
            '<figure class="related-player-gallery-preview" style="margin:0">'
            f'<a href="{safe_url}"><img src="{safe_url}" width="150" height="110" alt="{alt}" style="display:block;width:150px;height:110px"></a>'
            f'<figcaption style="font-size:12px;color:#f7e7b0;margin-top:4px">{label} — French guide preview</figcaption>'
            "</figure></li>"
        )
    section = (
        f'<section id="{SECTION_ID}" class="related-player-gallery-previews" aria-labelledby="{SECTION_ID}-title" style="max-width:730px;width:calc(100% - 32px);box-sizing:border-box;margin:16px auto;padding:16px;background:#241b0b;color:#f7e7b0;border:1px solid #a8863d">'
        f'<h2 id="{SECTION_ID}-title" style="font-size:20px;color:inherit;margin:0 0 8px">Related guide previews</h2>'
        f'<p style="font-size:14px;color:inherit;margin:0 0 16px">{CAPTION} preserved in '
        f'<a href="{source_link}" target="_blank" rel="noopener noreferrer" style="color:#ffbf46;text-decoration:underline">Coolwow2</a>.</p>'
        '<ul class="related-player-gallery-preview-list" style="list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;justify-content:center;gap:16px">'
        + "".join(figures)
        + "</ul></section>"
    )
    content_block_openings = list(re.finditer(r"<span\b[^>]*>", text, flags=re.IGNORECASE))
    content_block_markers: list[re.Match[str]] = []
    for opening in content_block_openings:
        class_attribute = re.search(r"\bclass\s*=\s*([\"'])(.*?)\1", opening.group(0), flags=re.IGNORECASE)
        if class_attribute and "contentBlock" in class_attribute.group(2).split():
            content_block_markers.append(opening)
    if len(content_block_markers) != 1:
        raise _fail(
            f"expected exactly one span with class token contentBlock on {page_route}; "
            f"found {len(content_block_markers)}"
        )
    marker = content_block_markers[0]
    rewritten = text[:marker.start()] + section + text[marker.start():]
    if rewritten.count(f'id="{SECTION_ID}"') != 1:
        raise _fail(f"related preview section insertion is not unique on {page_route}")
    return rewritten, True, len(assets)


__all__ = [
    "CAPTION",
    "EXPECTED_ASSET_DIRECTORY",
    "EXPECTED_CATALOG_RELATIVE",
    "EXPECTED_COMMIT",
    "EXPECTED_DESIGN_SHA256",
    "EXPECTED_ITEMS",
    "EXPECTED_MAP_SCHEMA",
    "EXPECTED_PAGE_COUNTS",
    "EXPECTED_PAYLOAD_BYTES",
    "EXPECTED_REPOSITORY",
    "EXPECTED_SOURCE_ACCEPTANCE_SHA256",
    "EXPECTED_SOURCE_CLASSIFICATION",
    "EXPECTED_SOURCE_URL",
    "RelatedPlayerGalleryPreviewAsset",
    "RelatedPlayerGalleryPreviewBundle",
    "RelatedPlayerGalleryPreviewError",
    "insert_preview_section",
    "load_related_player_gallery_preview_bundle",
]
