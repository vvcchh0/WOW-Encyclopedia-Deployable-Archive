"""Build the offline-only screenshot accessibility sampling plan.

This script reads already saved provenance and gallery inventories.  It never
contacts Wayback and deliberately does not walk raw stores or archives.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[3]
V5 = ROOT / ".scratch/pages-local-maintenance-20261014-v5"
OUT = Path(__file__).resolve().parent
PLAN = OUT.parent / "plan.json"
SUMMARY = OUT.parent / "summary.md"


def read_json(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def find_header_status(metadata_path: str | None) -> tuple[int | None, str | None]:
    if not metadata_path:
        return None, None
    meta = ROOT / metadata_path
    header = meta.parent.parent / "headers" / (meta.stem + ".txt")
    if not header.exists():
        return None, None
    text = header.read_text(encoding="utf-8", errors="replace")
    status = 200 if re.search(r"HTTP/\d(?:\.\d)?\s+200\s+OK", text) else None
    mime_match = re.search(r"(?im)^content-type:\s*([^\r\n]+)", text)
    return status, mime_match.group(1).strip() if mime_match else None


def find_cdx_row(source: dict[str, Any], original: str) -> dict[str, Any] | None:
    """Read one exact, header-labelled CDX row from saved local evidence."""
    metadata = source.get("cdx_metadata")
    if not metadata:
        return None
    path = ROOT / metadata
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))

    def normalize(name: Any) -> str:
        return re.sub(r"[^a-z0-9]", "", str(name).lower())

    aliases = {
        "timestamp": {"timestamp", "capturetimestamp", "ts"},
        "original": {"original", "url", "key"},
        "status": {"statuscode", "status", "status_code", "httpstatus", "http_status"},
        "digest": {"digest", "cdxdigest"},
        "length": {"length", "contentlength", "content_length"},
        "mime": {"mimetype", "mime", "contenttype", "content_type"},
    }

    rows: list[Any]
    header: list[str] | None = None
    if isinstance(payload, list) and payload and isinstance(payload[0], list):
        header = [normalize(v) for v in payload[0]]
        rows = payload[1:]
    elif isinstance(payload, dict):
        rows = payload.get("rows", payload.get("items", []))
        if rows and isinstance(rows[0], dict):
            header = None
    else:
        rows = []

    def value(row: Any, name: str) -> Any:
        if isinstance(row, dict):
            normalized = {normalize(k): v for k, v in row.items()}
            for alias in aliases[name]:
                if normalize(alias) in normalized:
                    return normalized[normalize(alias)]
            return None
        if not isinstance(row, list) or header is None:
            return None
        for index, column in enumerate(header):
            if column in {normalize(v) for v in aliases[name]} and index < len(row):
                return row[index]
        return None

    target_timestamp = str(source.get("actual_timestamp"))
    for row in rows:
        if str(value(row, "original")) != original or str(value(row, "timestamp")) != target_timestamp:
            continue
        raw_status = value(row, "status")
        try:
            status = int(raw_status)
        except (TypeError, ValueError):
            status = None
        raw_length = value(row, "length")
        try:
            length = int(raw_length)
        except (TypeError, ValueError):
            length = None
        return {
            "status": status,
            "mime": value(row, "mime"),
            "digest": value(row, "digest"),
            "length": length,
        }
    return None


def decode_image(path: Path) -> dict[str, Any]:
    """Load the complete image through Pillow without rewriting it."""
    try:
        from PIL import Image

        with Image.open(path) as image:
            image.load()
            return {
                "valid": True,
                "format": image.format,
                "size": list(image.size),
                "frames": int(getattr(image, "n_frames", 1)),
            }
    except Exception as exc:  # pragma: no cover - the production inventory should fail loudly below
        return {"valid": False, "error": f"{type(exc).__name__}: {exc}"}


def load_maps() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]], list[dict[str, Any]]]:
    karazhan = {r["original"]: r for r in read_json("research/related-sites-20261014/integration/karazhan-late-source-map.json")["items"]}
    regional = {r["original"]: r for r in read_json("research/related-sites-20261014/integration/regional-image-source-map.json")["items"]}
    static = {}
    for r in read_json("offline/approved-static-recovery-map.json")["files"]:
        original = r.get("original") or r.get("logical_url")
        if original:
            static[original] = r
    provenance_container = read_json(".scratch/pages-local-maintenance-20261014-v5/export-provenance.json")
    provenance = provenance_container.get("files", provenance_container) if isinstance(provenance_container, dict) else provenance_container
    return karazhan, regional, static, provenance


def provenance_for(provenance: list[dict[str, Any]], original: str) -> dict[str, Any] | None:
    for r in provenance:
        if r.get("original_url") == original and r.get("kind") == "image_overlay":
            return r
    return None


def local_record(
    *,
    item_id: str,
    context: str,
    gallery: str | None,
    original: str,
    source: dict[str, Any],
    source_map_path: str,
    output_path: str,
    provenance: list[dict[str, Any]],
    source_page: str | None = None,
) -> dict[str, Any]:
    p = provenance_for(provenance, original)
    if p:
        local_path = ROOT / ".scratch/pages-local-maintenance-20261014-v5" / p["output_path"]
        output_ref = ".scratch/pages-local-maintenance-20261014-v5/" + p["output_path"]
    else:
        local_path = ROOT / "offline/site" / output_path.lstrip("/")
        output_ref = "offline/site/" + output_path.lstrip("/")
    expected_sha = source.get("sha256") or source.get("source_sha256")
    expected_length = source.get("length") or source.get("content_length") or source.get("source_length")
    actual_sha = sha256(local_path)
    actual_length = local_path.stat().st_size
    if expected_sha and actual_sha != expected_sha:
        raise RuntimeError(f"local SHA mismatch for {original}: {actual_sha} != {expected_sha}")
    if expected_length is not None and actual_length != int(expected_length):
        raise RuntimeError(f"local length mismatch for {original}: {actual_length} != {expected_length}")
    decode = decode_image(local_path)
    if not decode.get("valid"):
        raise RuntimeError(f"image decode failed for {original}: {decode}")
    saved_status, saved_header_mime = find_header_status(source.get("metadata_path"))
    saved_source_status = source.get("http_status")
    try:
        saved_source_status = int(saved_source_status) if saved_source_status is not None else None
    except (TypeError, ValueError):
        saved_source_status = None
    mime = source.get("mime") or source.get("cdx_mime") or p.get("mime") if p else source.get("mime")
    if not mime:
        mime = source.get("mime") or source.get("response_content_type")
    source_map_cdx_digest = source.get("cdx_digest")
    cdx_row = find_cdx_row(source, original)
    row_mime = cdx_row.get("mime") if cdx_row else None
    row_status = cdx_row.get("status") if cdx_row else None
    row_digest = cdx_row.get("digest") if cdx_row else None
    row_length = cdx_row.get("length") if cdx_row else None
    row_is_200_image = bool(row_status == 200 and str(row_mime or "").lower().startswith("image/"))
    cdx_state: bool | str = True if row_is_200_image else (False if cdx_row is not None else "unknown")
    saved_header_is_image = bool(saved_status == 200 and str(saved_header_mime or "").lower().startswith("image/"))
    saved_source_is_image = bool(saved_source_status == 200 and str(source.get("mime") or source.get("response_content_type") or "").lower().startswith("image/"))
    saved_payload: bool | str = True if (saved_header_is_image or saved_source_is_image) else "unknown"
    cdx_digest = source_map_cdx_digest or row_digest
    evidence = {
        "source_map_cdx_digest": source_map_cdx_digest,
        "row_matched": cdx_row is not None,
        "row_status": row_status,
        "row_mime": row_mime,
        "row_digest": row_digest,
        "row_length": row_length,
    }
    if source_page:
        evidence["source_page"] = source_page
    return {
        "id": item_id,
        "context": context,
        "gallery": gallery,
        "original_url": original,
        "probe_urls": [original],
        "local": {
            "has_real_image": True,
            "path": output_ref,
            "sha256": actual_sha,
            "bytes": actual_length,
            "mime": mime,
            "validity": "local bytes match the saved source record and Pillow.load completed",
            "decode": decode,
        },
        "capture": {
            "actual_timestamp": source.get("actual_timestamp"),
            "indexed_timestamp": source.get("indexed_capture_timestamp") or source.get("actual_timestamp"),
            "temporal_class": source.get("temporal_class"),
            "cdx_digest": cdx_digest,
            "saved_payload_http200_image": saved_payload,
            "cdx_200_image_row": cdx_state,
            "cdx_evidence": evidence,
            "cdx_length": source.get("cdx_length") or row_length,
        },
        "evidence": [source_map_path, ".scratch/pages-local-maintenance-20261014-v5/export-provenance.json" if p else "offline/build-manifest.json"],
        "source_local_path": source.get("local_path"),
        "source_page": source_page,
        "status": "known_good_control",
    }


def missing_record(item_id: str, context: str, gallery: str, original: str, route: str, shots: int) -> dict[str, Any]:
    return {
        "id": item_id,
        "context": context,
        "gallery": gallery,
        "original_url": original,
        "probe_urls": [original],
        "local": {
            "has_real_image": False,
            "path": None,
            "validity": "no local entity or v5 direct provenance record",
            "missing_reason": "the frozen 50-gallery inventory and v5 route recheck report no direct full/thumb file",
        },
        "capture": {
            "actual_timestamp": None,
            "indexed_timestamp": None,
            "temporal_class": None,
            "cdx_digest": None,
            "saved_payload_http200_image": "unknown",
            "cdx_200_image_row": "unknown",
            "cdx_evidence": "not queried in this offline pass",
            "cdx_length": None,
        },
        "gallery_source": {"page_route": route, "declared_shots": shots, "source_route": route},
        "evidence": ["research/github-pages-20261013/gallery-inventory-20261013.json", "research/local-maintenance-20261014/gallery-route-entity-recheck.json"],
        "status": "needs_wayback_probe",
    }


def main() -> None:
    karazhan, regional, static, provenance = load_maps()
    items: list[dict[str, Any]] = []

    # Existing late-2008 gallery controls (the local direct gallery directory is still incomplete).
    karazhan_urls = {
        1: "https://www.worldofwarcraft.com/info/dungeons/images/karazhan/thumbs/ss1-thumb.jpg",
        2: "http://www.worldofwarcraft.com/info/dungeons/images/karazhan/thumbs/ss2-thumb.jpg",
        3: "http://www.worldofwarcraft.com/info/dungeons/images/karazhan/thumbs/ss3-thumb.jpg",
    }
    for n in (1, 2, 3):
        original = karazhan_urls[n]
        items.append(local_record(item_id=f"karazhan-thumb-ss{n}", context="Raid gallery / TBC / local late capture", gallery="Karazhan", original=original, source=karazhan[original], source_map_path="research/related-sites-20261014/integration/karazhan-late-source-map.json", output_path=f"/info/dungeons/images/karazhan/thumbs/ss{n}-thumb.jpg", provenance=provenance))

    # Gallery targets with no local full/thumbnail entity.  Keep these explicit so the next probe can compare both forms.
    items.append(missing_record("karazhan-full-ss1", "Raid gallery / TBC / full screenshot gap", "Karazhan", "http://www.worldofwarcraft.com/info/dungeons/images/karazhan/ss1.jpg", "/info/dungeons/karazhan-gallery.html", 63))
    items.append(missing_record("blacktemple-full-ss1", "Raid gallery / TBC / full screenshot gap", "Black Temple", "http://www.worldofwarcraft.com/info/dungeons/images/blacktemple/ss1.jpg", "/info/dungeons/black-temple-gallery.html", 48))
    items.append(missing_record("blacktemple-thumb-ss1", "Raid gallery / TBC / thumbnail gap", "Black Temple", "http://www.worldofwarcraft.com/info/dungeons/images/blacktemple/ss1-thumb.jpg", "/info/dungeons/black-temple-gallery.html", 48))
    items.append(missing_record("magisters-full-ss1", "Dungeon gallery / TBC / full screenshot gap", "Magister's Terrace", "http://www.worldofwarcraft.com/info/dungeons/images/magisters/ss1.jpg", "/info/dungeons/magisters-terrace-gallery.html", 47))
    items.append(missing_record("magisters-thumb-ss1", "Dungeon gallery / TBC / thumbnail gap", "Magister's Terrace", "http://www.worldofwarcraft.com/info/dungeons/images/magisters/ss1-thumb.jpg", "/info/dungeons/magisters-terrace-gallery.html", 47))

    # Wrath screenshot gallery controls.  These are ordinary screenshot images, not UI/layout assets.
    for n in (5, 11, 41):
        original = f"http://www.worldofwarcraft.com/wrath/images/screenshots/ss{n}.jpg"
        items.append(local_record(item_id=f"wrath-screenshot-ss{n}", context="Wrath of the Lich King screenshot gallery", gallery="Wrath screenshots", original=original, source=static[original], source_map_path="offline/approved-static-recovery-map.json", output_path=f"/wrath/images/screenshots/ss{n}.jpg", provenance=provenance))

    # EU Screen of the Day captures provide the regional/media control set.
    eu = [
        ("10704-03", "2008 baseline EU daily screenshot"),
        ("10702-05", "2008 baseline EU daily screenshot"),
        ("10710-10", "2008 baseline EU daily screenshot"),
        ("10706-26", "2008 EU daily screenshot"),
        ("10704-14", "2007 EU daily screenshot"),
    ]
    for stem, context in eu:
        candidates = [u for u in regional if u.endswith(stem + ".jpg")]
        if not candidates:
            raise RuntimeError(f"regional source missing for {stem}")
        original = candidates[0]
        source = regional[original]
        items.append(local_record(item_id=f"eu-screenoftheday-{stem}", context=f"Media / {context}", gallery="EU Screen of the Day", original=original, source=source, source_map_path="research/related-sites-20261014/integration/regional-image-source-map.json", output_path="/_origins/" + urlsplit(original).netloc + urlsplit(original).path, provenance=provenance, source_page=source.get("source_page")))

    if len(items) != 16:
        raise RuntimeError(f"expected 16 selected items, got {len(items)}")
    plan = {
        "schema": "screenshot-accessibility-plan/v1",
        "generated_utc": "2026-10-14",
        "network_performed": False,
        "anchor_timestamp": "20080512210044",
        "scope": {
            "selection_count": len(items),
            "coverage": ["TBC raid/dungeon dynamic galleries", "Wrath screenshot gallery", "EU Screen of the Day media"],
            "exclusions": ["navigation/menu/border/layout/UI assets", "nested ZIPs and raw stores", "Wayback requests"],
            "next_probe": "query existing CDX/replay candidates direct first; use the configured proxy only after a direct failure",
        },
        "items": items,
        "evidence_boundary": {
            "cdx_meaning": "true only means an exact saved CDX row matched original URL and capture timestamp with statuscode 200 and image MIME; false means an exact row exists but fails that test; unknown means no exact row was available. source_map_cdx_digest is retained as a saved summary and is not treated as row validation",
            "saved_payload_meaning": "saved_payload_http200_image is separate from CDX and is true only for a saved replay header or source record explicitly carrying HTTP 200 plus image MIME",
            "local_meaning": "has_real_image only covers bytes present in the current v5 site or frozen offline site and verified against the saved source record",
            "gallery_gap_meaning": "missing dynamic gallery files are retained as probe targets; absence here is not evidence that Wayback has no capture",
        },
        "inputs": [
            "research/github-pages-20261013/gallery-inventory-20261013.json",
            "research/local-maintenance-20261014/gallery-route-entity-recheck.json",
            "research/related-sites-20261014/integration/karazhan-late-source-map.json",
            "research/related-sites-20261014/integration/regional-image-source-map.json",
            "offline/approved-static-recovery-map.json",
            ".scratch/pages-local-maintenance-20261014-v5/export-provenance.json",
        ],
    }
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    local = [r for r in items if r["local"]["has_real_image"]]
    gaps = [r for r in items if not r["local"]["has_real_image"]]
    cdx_rows = [r for r in items if r["capture"]["cdx_200_image_row"] is True]
    cdx_unknown = [r for r in items if r["capture"]["cdx_200_image_row"] == "unknown"]
    lines = [
        "# Screenshot accessibility sample",
        "",
        "This inventory was assembled from saved local manifests and source maps on 2026-10-14. No Wayback request was made, and nested ZIP/raw stores were not scanned.",
        "",
        f"The plan contains **{len(items)}** targets: **{len(local)}** local image controls and **{len(gaps)}** dynamic-gallery gaps. Exactly **{len(cdx_rows)}** have a matching saved CDX 200/image row; **{len(cdx_unknown)}** remain unknown. The gallery recheck still reports 50 gallery routes but zero direct full/thumb files; the three Karazhan thumbnails below are late related previews recorded separately.",
        "",
        "| ID | Context | Local image | Capture | Saved 200/image | CDX row |",
        "|---|---|---:|---|---|---|",
    ]
    for r in items:
        c = r["capture"]
        lines.append(f"| `{r['id']}` | {r['context']} | {'yes' if r['local']['has_real_image'] else 'no'} | {c['actual_timestamp'] or 'not locally recorded'} | {c['saved_payload_http200_image']} | {c['cdx_200_image_row']} |")
    lines += [
        "",
        "The strongest controls for the next replay check are `karazhan-thumb-ss2` (`20080512212653`), `karazhan-thumb-ss3` (`20080512212653`), and the Wrath screenshots `ss5` (`20080402054247`) and `ss11` (`20080402050117`). EU Screen of the Day controls retain their source page and capture timestamps, including `10704-03` at `20080512205334` and `10704-14` at `20070421152959`.",
        "",
        "Black Temple and Magister's Terrace remain explicit probe targets because their gallery source pages enumerate 48 and 47 shots, while the local inventory has no corresponding direct full or thumbnail entity. Their `unknown` CDX state means only that this pass did not query those individual image URLs.",
        "",
        "The next probe should record direct HTTP status, MIME, replay timestamp, response length, and image decode result for each target, then retry through the configured proxy only after direct transport fails. Preserve the original bytes and source timestamp for any accepted capture.",
    ]
    SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"plan": str(PLAN), "summary": str(SUMMARY), "selected": len(items), "local_controls": len(local), "gallery_gaps": len(gaps)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
