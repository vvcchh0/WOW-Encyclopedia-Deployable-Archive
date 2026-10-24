"""Exact, provenance-checked news previews reused from linked wallpapers."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
from typing import Any, Mapping


class NewsWallpaperPreviewError(ValueError):
    """Raised when an approved news wallpaper preview no longer matches its source."""


CAPTION = "Preview from linked wallpaper"
PRESENTATION_STYLE = "max-width:165px;max-height:231px;width:auto;height:auto;"
DESIGN_PATH = "research/continuous-recovery-20261024/news-wallpaper-preview-design.json"
DESIGN_SHA256 = "ea1b8cc8bb26544a43180501ff12d75acaec479c0c06aaa10555f007c15c9afc"
SOURCE_MANIFEST_SHA256 = "e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a"


@dataclass(frozen=True)
class NewsWallpaperPreview:
    news_page_route: str
    thumbnail_route: str
    wallpaper_page_route: str
    source_image_route: str
    source_image_sha256: str
    source_image_length: int
    posted_date: str


APPROVED_PREVIEWS = (
    NewsWallpaperPreview(
        "/news/rss-10-2006.xml", "/news/images/06-10/tcg-deathdealer.jpg",
        "/downloads/wallpapers/wallpaper86.html", "/downloads/wallpapers/images/tcg2/tcg2-800x.jpg",
        "02500d09cac26f6b4e12e7f544a23c281d21a3393a2b7419ccd06dbe6340b375", 143763, "10-31-06",
    ),
    NewsWallpaperPreview(
        "/news/rss-10-2006.xml", "/news/images/06-10/tcg-zormstonefury.jpg",
        "/downloads/wallpapers/wallpaper85.html", "/downloads/wallpapers/images/tcg1/tcg1-800x.jpg",
        "a501281104c773ea4e33b451436a8943e1338c28f163890d6eb757e0015b1382", 525385, "10-26-06",
    ),
    NewsWallpaperPreview(
        "/news/rss-11-2006.xml", "/news/images/06-11/tcg-facesmash.jpg",
        "/downloads/wallpapers/wallpaper89.html", "/downloads/wallpapers/images/tcg5/tcg5-800x.jpg",
        "676e007728b90f07b62583bcb4971008c82f8c0ccc408fcb916a76217cf6e921", 258436, "11-28-06",
    ),
    NewsWallpaperPreview(
        "/news/rss-11-2006.xml", "/news/images/06-11/tcg-chromie.jpg",
        "/downloads/wallpapers/wallpaper88.html", "/downloads/wallpapers/images/tcg4/tcg4-800x.jpg",
        "ad4060d892ab39f515692cf53b51475df6f766b7f0cfcca7eeaba078644efb97", 217815, "11-21-06",
    ),
    NewsWallpaperPreview(
        "/news/rss-11-2006.xml", "/news/images/06-11/tcg-retribution.jpg",
        "/downloads/wallpapers/wallpaper87.html", "/downloads/wallpapers/images/tcg3/tcg3-800x.jpg",
        "24c02d174ecf91d0afa331a2e5dbca4a506c57ccdf8f5eb0d1fe92bab24aef59", 136889, "11-07-06",
    ),
)


def validate_preview_sources(
    *,
    route_records: Mapping[str, Mapping[str, Any]],
    route_to_static: Mapping[str, str],
    source_site: Path,
    workspace_root: Path,
    source_manifest_sha256: str | None = None,
    specs: tuple[NewsWallpaperPreview, ...] = APPROVED_PREVIEWS,
) -> dict[str, dict[str, Any]]:
    """Verify missing-thumb candidates against exact manifest and on-disk bytes.

    Only candidates whose news page is in this export and whose thumbnail route
    is still absent are eligible. A later genuine thumbnail therefore keeps the
    normal exporter path and does not depend on this wallpaper source.
    """

    site_root = source_site.resolve()
    workspace = workspace_root.resolve()
    validated: dict[str, dict[str, Any]] = {}
    eligible = [
        item for item in specs
        if item.news_page_route in route_records
        and item.news_page_route in route_to_static
        and item.thumbnail_route not in route_to_static
    ]
    if eligible and source_manifest_sha256 is not None and source_manifest_sha256 != SOURCE_MANIFEST_SHA256:
        raise NewsWallpaperPreviewError("approved source manifest SHA mismatch")
    for item in eligible:
        if item.news_page_route not in route_records or item.news_page_route not in route_to_static:
            continue
        if item.thumbnail_route in route_to_static:
            continue
        if item.wallpaper_page_route not in route_to_static:
            raise NewsWallpaperPreviewError(
                f"approved parent wallpaper page is absent: {item.wallpaper_page_route}"
            )
        static_url = route_to_static.get(item.source_image_route)
        record = route_records.get(item.source_image_route)
        if not static_url or record is None:
            raise NewsWallpaperPreviewError(
                f"approved source image is absent from the accepted route map: {item.source_image_route}"
            )
        if record.get("kind") != "image" or str(record.get("mime") or "").split(";", 1)[0].lower() != "image/jpeg":
            raise NewsWallpaperPreviewError(f"approved source is not an accepted JPEG image: {item.source_image_route}")
        if record.get("derived_sha256") != item.source_image_sha256:
            raise NewsWallpaperPreviewError(f"approved source manifest SHA mismatch: {item.source_image_route}")
        if record.get("derived_length") != item.source_image_length:
            raise NewsWallpaperPreviewError(f"approved source manifest length mismatch: {item.source_image_route}")
        output_path = str(record.get("output_path") or "")
        source_path = (workspace / output_path).resolve()
        try:
            source_path.relative_to(site_root)
        except ValueError as exc:
            raise NewsWallpaperPreviewError(f"approved source path escapes source site: {output_path}") from exc
        if not source_path.is_file():
            raise NewsWallpaperPreviewError(f"approved source file is missing: {output_path}")
        payload = source_path.read_bytes()
        actual_sha = hashlib.sha256(payload).hexdigest()
        if len(payload) != item.source_image_length or actual_sha != item.source_image_sha256:
            raise NewsWallpaperPreviewError(f"approved source bytes drifted: {item.source_image_route}")
        validated[item.thumbnail_route] = {
            "spec": item,
            "static_url": static_url,
            "sha256": actual_sha,
            "length": len(payload),
        }
    return validated


def apply_news_wallpaper_previews(
    text: str,
    *,
    page_route: str,
    route_to_static: Mapping[str, str],
    validated_sources: Mapping[str, Mapping[str, Any]],
    specs: tuple[NewsWallpaperPreview, ...] = APPROVED_PREVIEWS,
) -> tuple[str, list[dict[str, Any]]]:
    """Replace only exact missing TCG thumbnail anchors with labelled previews."""

    applicable = [item for item in specs if item.news_page_route == page_route]
    if not applicable:
        return text, []
    applied: list[dict[str, Any]] = []
    for item in applicable:
        # A collected real thumbnail always takes precedence over the fallback.
        if item.thumbnail_route in route_to_static:
            continue
        source = validated_sources.get(item.thumbnail_route)
        if source is None or source.get("spec") != item:
            raise NewsWallpaperPreviewError(f"missing validated source for preview: {item.thumbnail_route}")
        href_q = r"(?P<hq>[\"'])" + re.escape(item.wallpaper_page_route) + r"(?P=hq)"
        src_q = r"(?P<sq>[\"'])" + re.escape(item.thumbnail_route) + r"(?P=sq)"
        pattern = re.compile(
            r"(?P<open><a\b(?=[^>]*\bhref\s*=\s*" + href_q + r")[^>]*>)"
            r"(?P<space>\s*)(?P<img><img\b(?=[^>]*\bsrc\s*=\s*" + src_q + r")[^>]*>)"
            r"(?P<tail>\s*</a>)"
        )
        matches = list(pattern.finditer(text))
        if len(matches) != 1:
            raise NewsWallpaperPreviewError(
                f"expected one exact linked thumbnail for {item.thumbnail_route} on {page_route}; found {len(matches)}"
            )

        def replace(match: re.Match[str]) -> str:
            image_tag = match.group("img")
            image_tag, source_count = re.subn(
                r"(?i)(\bsrc\s*=\s*)([\"'])" + re.escape(item.thumbnail_route) + r"\2",
                lambda src_match: src_match.group(1) + '"' + str(source["static_url"]) + '"',
                image_tag,
                count=1,
            )
            if source_count != 1:
                raise NewsWallpaperPreviewError(f"thumbnail source attribute is ambiguous: {item.thumbnail_route}")
            image_tag = re.sub(r"(?i)\s+(?:width|height)\s*=\s*(?:[\"'][^\"']*[\"']|[^\s/>]+)", "", image_tag)
            image_tag = re.sub(r"(?i)\s+alt\s*=\s*(?:[\"'][^\"']*[\"']|[^\s/>]+)", "", image_tag)
            image_tag = re.sub(r"(?i)\s+style\s*=\s*(?:[\"'][^\"']*[\"']|[^\s/>]+)", "", image_tag)
            ending = "/>" if image_tag.rstrip().endswith("/>") else ">"
            image_tag = image_tag.rstrip()
            image_tag = image_tag[:-len(ending)].rstrip()
            image_tag += f' alt="{CAPTION}" style="{PRESENTATION_STYLE}"{ending}'
            caption = f'<br><small class="news-wallpaper-preview-caption">{CAPTION}</small>'
            return match.group("open") + match.group("space") + image_tag + caption + match.group("tail")

        text = pattern.sub(replace, text, count=1)
        applied.append({
            "news_page_route": item.news_page_route,
            "thumbnail_route": item.thumbnail_route,
            "wallpaper_page_route": item.wallpaper_page_route,
            "source_image_route": item.source_image_route,
            "source_static_url": str(source["static_url"]),
            "source_sha256": item.source_image_sha256,
            "source_length": item.source_image_length,
            "posted_date": item.posted_date,
            "display_fallback": True,
            "original_thumbnail_added": False,
        })
    return text, applied


def provenance(items: list[dict[str, Any]], *, source_manifest_sha256: str | None = None) -> dict[str, Any]:
    """Report image display reuse separately from original-image recovery."""

    ordered = sorted(items, key=lambda item: (item["news_page_route"], item["thumbnail_route"]))
    return {
        "schema": "github-pages-news-wallpaper-preview-fallbacks/v1",
        "design_decision": DESIGN_PATH,
        "design_decision_sha256": DESIGN_SHA256,
        "source_manifest_sha256": source_manifest_sha256,
        "display_fallback_count": len(ordered),
        "original_payloads_added": 0,
        "original_payloads_reused": len(ordered),
        "presentation": f"accepted linked wallpaper image displayed with max bounds 165x231 and auto aspect ratio; visible caption: {CAPTION}",
        "items": ordered,
    }
