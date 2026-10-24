"""Validate and stage the accepted current-origin BlizzCast MP3 copies.

This opt-in module binds a tiny local ZIP to the accepted BlizzCast reader
inputs and the separately reviewed 2026 audio receipt. It performs no network
access and never treats the current MP3 bytes as a 2008 capture.
"""

from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ == "tools":
    from . import blizzcast_reader
else:
    import blizzcast_reader


MAP_SCHEMA = "wow-blizzcast-current-origin-audio-input/v1"
ACCEPTANCE_SCHEMA = "wow-root-blizzcast-current-origin-audio-acceptance/v1"
AUDIO_ROUTE = "/__offline/related-sites/blizzcast/audio/"
CATALOG_ROUTE = AUDIO_ROUTE + "catalog.json"
SOURCE_NOTE = "Audio from Blizzard’s current media copies, saved 24 October 2026."
RSS_URL = "http://us.blizzard.com/blizzcast/_content/en-US/rss.xml"
EXPECTED_EPISODES = (
    {
        "id": "episode1",
        "url": "http://us.media.blizzard.com/blizzcast/blizzcast_episode1.mp3",
        "route": AUDIO_ROUTE + "episode1.mp3",
        "member": "__offline/related-sites/blizzcast/audio/episode1.mp3",
    },
    {
        "id": "episode2",
        "url": "http://us.media.blizzard.com/blizzcast/blizzcast_episode2.mp3",
        "route": AUDIO_ROUTE + "episode2.mp3",
        "member": "__offline/related-sites/blizzcast/audio/episode2.mp3",
    },
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ZIP_OVERHEAD_LIMIT = 1024 * 1024


class BlizzcastAudioError(ValueError):
    """Raised when current-origin audio inputs violate the accepted contract."""


@dataclass
class BlizzcastAudioBundle:
    """Verified immutable payloads and generated catalog for the exporter."""

    assets: list[dict[str, Any]]
    catalog_path: str
    catalog_bytes: bytes
    origin_routes: dict[str, str]
    estimated_bytes: int
    map_sha256: str
    source_acceptance_sha256: str
    current_origin_acceptance_sha256: str
    payload_zip_sha256: str
    source_date: str


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _resolve_workspace_path(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise BlizzcastAudioError(f"{label} path is missing")
    candidate = Path(value)
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise BlizzcastAudioError(f"{label} path escapes the workspace") from exc
    return resolved


def _read_json(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BlizzcastAudioError(f"{label} is not readable UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise BlizzcastAudioError(f"{label} must be a JSON object")
    return value, raw


def _accepted_reader_binding(root: Path, reader_map_path: Path, expected_map_sha: str, expected_acceptance_sha: str) -> tuple[dict[str, Any], dict[str, Any]]:
    reader_map, reader_raw = _read_json(reader_map_path, "accepted BlizzCast input map")
    if reader_map.get("schema") != "wow-blizzcast-reader-input/v1" or reader_map.get("accepted") is not True:
        raise BlizzcastAudioError("current-origin audio requires the accepted BlizzCast reader map")
    if _sha256(reader_raw) != expected_map_sha:
        raise BlizzcastAudioError("audio map is bound to a different BlizzCast reader map")
    if reader_map.get("source_acceptance_sha256") != expected_acceptance_sha:
        raise BlizzcastAudioError("audio map is bound to a different BlizzCast source acceptance")
    acceptance_path = _resolve_workspace_path(root, reader_map.get("source_acceptance"), "BlizzCast source acceptance")
    acceptance, acceptance_raw = _read_json(acceptance_path, "BlizzCast source acceptance")
    if _sha256(acceptance_raw) != expected_acceptance_sha or acceptance.get("accepted") is not True:
        raise BlizzcastAudioError("BlizzCast source acceptance is not accepted or its digest differs")
    records = reader_map.get("records")
    if not isinstance(records, list) or len(records) != 5 or [item.get("entity_id") for item in records] != list(blizzcast_reader.EXPECTED_IDS):
        raise BlizzcastAudioError("audio must be paired with all five accepted BlizzCast reader sources")
    rss_record = next((item for item in records if item.get("entity_id") == "BC01"), None)
    if not isinstance(rss_record, dict) or rss_record.get("original_url") != RSS_URL:
        raise BlizzcastAudioError("accepted BlizzCast map has no fixed RSS source")
    rss_path = _resolve_workspace_path(root, rss_record.get("payload_path"), "BlizzCast RSS payload")
    try:
        rss_raw = rss_path.read_bytes()
    except OSError as exc:
        raise BlizzcastAudioError("accepted BlizzCast RSS payload is missing") from exc
    if len(rss_raw) != rss_record.get("length") or _sha256(rss_raw) != rss_record.get("sha256"):
        raise BlizzcastAudioError("accepted BlizzCast RSS bytes do not match the source map")
    if b"<!DOCTYPE" in rss_raw.upper() or b"<!ENTITY" in rss_raw.upper():
        raise BlizzcastAudioError("DTD/entity RSS input is not allowed")
    try:
        rss = ET.fromstring(rss_raw)
    except ET.ParseError as exc:
        raise BlizzcastAudioError("accepted BlizzCast RSS is not well-formed XML") from exc
    enclosures: dict[str, int] = {}
    for element in rss.iter():
        if element.tag.rsplit("}", 1)[-1].casefold() == "enclosure":
            url = element.attrib.get("url", "")
            length = element.attrib.get("length", "")
            if url and length.isdecimal():
                if url in enclosures:
                    raise BlizzcastAudioError("accepted RSS repeats an audio enclosure URL")
                enclosures[url] = int(length)
    return reader_map, {"rss_lengths": enclosures, "rss_sha256": _sha256(rss_raw)}


def load_blizzcast_audio_bundle(
    map_path: str | Path,
    workspace_root: str | Path,
    blizzcast_source_map: str | Path,
) -> BlizzcastAudioBundle:
    """Read and verify the fixed two-MP3 current-origin package.

    The supplied reader map is independently hash-bound and must also carry an
    accepted source receipt. ZIP entries are read only after all path, receipt,
    roster, and archive-hash checks pass.
    """

    root = Path(workspace_root).resolve()
    audio_map_path = _resolve_workspace_path(root, str(map_path), "audio input map")
    audio_map, map_raw = _read_json(audio_map_path, "audio input map")
    if audio_map.get("schema") != MAP_SCHEMA or audio_map.get("accepted") is not True:
        raise BlizzcastAudioError("current-origin audio input map is not accepted")
    source_date = audio_map.get("source_acquired_date")
    if source_date != "2026-10-24" or audio_map.get("classification") != "current_origin_audio_copy":
        raise BlizzcastAudioError("audio provenance must identify the accepted 2026 current-origin copies")
    if audio_map.get("historical_byte_identity") != "unknown; no original MP3 digest is present in the 2008 RSS":
        raise BlizzcastAudioError("audio map must retain the unknown historical-byte-identity boundary")
    reader_path = _resolve_workspace_path(root, str(blizzcast_source_map), "BlizzCast reader map")
    if audio_map.get("blizzcast_source_map") != reader_path.relative_to(root).as_posix():
        raise BlizzcastAudioError("audio map names a different accepted BlizzCast reader map")
    if not _SHA256_RE.fullmatch(str(audio_map.get("blizzcast_source_map_sha256", ""))):
        raise BlizzcastAudioError("audio map has an invalid BlizzCast reader-map SHA256")
    if not _SHA256_RE.fullmatch(str(audio_map.get("blizzcast_source_acceptance_sha256", ""))):
        raise BlizzcastAudioError("audio map has an invalid source-acceptance SHA256")
    reader_map, rss_data = _accepted_reader_binding(
        root,
        reader_path,
        str(audio_map["blizzcast_source_map_sha256"]),
        str(audio_map["blizzcast_source_acceptance_sha256"]),
    )
    if audio_map.get("blizzcast_rss_sha256") != rss_data["rss_sha256"]:
        raise BlizzcastAudioError("audio map is bound to a different accepted RSS payload")
    acceptance_path = _resolve_workspace_path(root, audio_map.get("current_origin_acceptance"), "current-origin audio acceptance")
    acceptance, acceptance_raw = _read_json(acceptance_path, "current-origin audio acceptance")
    acceptance_sha = _sha256(acceptance_raw)
    if acceptance_sha != audio_map.get("current_origin_acceptance_sha256"):
        raise BlizzcastAudioError("current-origin audio acceptance SHA256 mismatch")
    if acceptance.get("schema") != ACCEPTANCE_SCHEMA or acceptance.get("accepted_as_current_origin_audio") is not True:
        raise BlizzcastAudioError("current-origin audio acceptance is missing")
    if acceptance.get("accepted_as_2008_byte_identical") is not False or acceptance.get("original_bytes_unchanged") is not True:
        raise BlizzcastAudioError("historical identity or original-byte preservation boundary changed")
    accepted_records = acceptance.get("records")
    if not isinstance(accepted_records, list) or len(accepted_records) != 2:
        raise BlizzcastAudioError("current-origin acceptance must contain exactly two episodes")
    accepted_by_id = {item.get("id"): item for item in accepted_records if isinstance(item, dict)}
    if set(accepted_by_id) != {item["id"] for item in EXPECTED_EPISODES}:
        raise BlizzcastAudioError("current-origin acceptance episode IDs differ from the fixed allowlist")
    accepted_total_bytes = sum(int(accepted_by_id[item["id"]].get("bytes") or 0) for item in EXPECTED_EPISODES)
    records = audio_map.get("records")
    if not isinstance(records, list) or len(records) != 2:
        raise BlizzcastAudioError("audio map must contain exactly two episodes")
    if [item.get("id") for item in records] != [item["id"] for item in EXPECTED_EPISODES]:
        raise BlizzcastAudioError("audio map episode order or IDs differ from the fixed allowlist")
    if [item.get("original_url") for item in records] != [item["url"] for item in EXPECTED_EPISODES]:
        raise BlizzcastAudioError("audio map URLs differ from the fixed RSS enclosure allowlist")
    if [item.get("canonical_path") for item in records] != [item["route"] for item in EXPECTED_EPISODES]:
        raise BlizzcastAudioError("audio map routes differ from the fixed canonical paths")
    if [item.get("payload_zip_member") for item in records] != [item["member"] for item in EXPECTED_EPISODES]:
        raise BlizzcastAudioError("audio map ZIP members differ from the fixed allowlist")
    zip_path = _resolve_workspace_path(root, audio_map.get("payload_zip"), "audio payload ZIP")
    if not zip_path.is_file():
        raise BlizzcastAudioError("audio payload ZIP is missing")
    zip_file_bytes = zip_path.stat().st_size
    if zip_file_bytes > accepted_total_bytes + ZIP_OVERHEAD_LIMIT:
        raise BlizzcastAudioError("audio payload ZIP exceeds accepted raw bytes plus bounded ZIP overhead")
    if zip_file_bytes != audio_map.get("payload_zip_bytes"):
        raise BlizzcastAudioError("audio payload ZIP size differs from its input map")
    zip_raw_sha = hashlib.sha256()
    zip_length = 0
    try:
        with zip_path.open("rb") as source:
            while chunk := source.read(1024 * 1024):
                zip_raw_sha.update(chunk)
                zip_length += len(chunk)
    except OSError as exc:
        raise BlizzcastAudioError("audio payload ZIP is unreadable") from exc
    if zip_length != audio_map.get("payload_zip_bytes") or zip_raw_sha.hexdigest() != audio_map.get("payload_zip_sha256"):
        raise BlizzcastAudioError("audio payload ZIP size or SHA256 mismatch")
    zip_sha = zip_raw_sha.hexdigest()
    try:
        archive = zipfile.ZipFile(zip_path, "r")
    except (OSError, zipfile.BadZipFile) as exc:
        raise BlizzcastAudioError("audio payload archive is not a valid ZIP") from exc
    assets: list[dict[str, Any]] = []
    catalog_records: list[dict[str, Any]] = []
    try:
        infos = archive.infolist()
        expected_members = [item["member"] for item in EXPECTED_EPISODES]
        if [info.filename for info in infos] != expected_members or len({info.filename for info in infos}) != 2:
            raise BlizzcastAudioError("audio ZIP must contain exactly the two whitelisted MP3 members in order")
        for expected, record in zip(EXPECTED_EPISODES, records, strict=True):
            accepted = accepted_by_id.get(expected["id"])
            if not isinstance(accepted, dict) or accepted.get("url") != expected["url"]:
                raise BlizzcastAudioError(f"current-origin acceptance is missing {expected['id']}")
            if accepted.get("classification") != "current_origin_audio_copy" or accepted.get("eligible_for_derived_player") is not True:
                raise BlizzcastAudioError(f"{expected['id']} is not accepted for a local player")
            if accepted.get("historical_byte_identity") != "unknown; RSS has no MP3 hash":
                raise BlizzcastAudioError(f"{expected['id']} historical identity boundary changed")
            for key, actual in (("bytes", accepted.get("bytes")), ("sha256", accepted.get("sha256")), ("rss_enclosure_length", accepted.get("rss_length"))):
                if record.get(key) != actual:
                    raise BlizzcastAudioError(f"audio-map {expected['id']}.{key} differs from current-origin acceptance")
            if record.get("rss_enclosure_length") != rss_data["rss_lengths"].get(expected["url"]):
                raise BlizzcastAudioError(f"{expected['id']} old RSS enclosure length differs from the accepted RSS")
            if record.get("current_origin_length_delta_bytes") != int(record["bytes"]) - int(record["rss_enclosure_length"]):
                raise BlizzcastAudioError(f"{expected['id']} old RSS size comparison is inconsistent")
            if record.get("classification") != "current_origin_audio_copy" or record.get("mime") != "audio/mpeg":
                raise BlizzcastAudioError(f"{expected['id']} has an unexpected classification or MIME")
            if record.get("historical_byte_identity") != "unknown; the accepted 2008 RSS has no MP3 digest":
                raise BlizzcastAudioError(f"{expected['id']} map erases the historical-identity boundary")
            info = archive.getinfo(expected["member"])
            if info.is_dir() or info.compress_type != zipfile.ZIP_STORED or info.file_size != record["bytes"] or info.compress_size != info.file_size:
                raise BlizzcastAudioError(f"{expected['id']} ZIP member must be exact-length ZIP_STORED bytes")
            if info.flag_bits & 0x1:
                raise BlizzcastAudioError("encrypted ZIP entries are not allowed")
            body = archive.read(info)
            if len(body) != record["bytes"] or _sha256(body) != record["sha256"]:
                raise BlizzcastAudioError(f"{expected['id']} raw audio bytes differ from the accepted digest")
            if not (body.startswith(b"ID3") or (len(body) >= 2 and body[0] == 0xFF and body[1] & 0xE0 == 0xE0)):
                raise BlizzcastAudioError(f"{expected['id']} does not have an MP3/ID3 signature")
            safe_record = {
                "id": expected["id"],
                "original_url": expected["url"],
                "path": expected["route"],
                "mime": "audio/mpeg",
                "bytes": len(body),
                "sha256": record["sha256"],
                "source_acquired_date": source_date,
                "classification": "current_origin_audio_copy",
                "historical_byte_identity": "unknown; the accepted 2008 RSS has no MP3 digest",
                "rss_enclosure_length": record["rss_enclosure_length"],
                "current_origin_length_delta_bytes": record["current_origin_length_delta_bytes"],
            }
            assets.append({"path": expected["route"], "data": body, "mime": "audio/mpeg", "record": safe_record})
            catalog_records.append(safe_record)
    finally:
        archive.close()
    if set(rss_data["rss_lengths"]) & {item["url"] for item in EXPECTED_EPISODES} != {item["url"] for item in EXPECTED_EPISODES}:
        raise BlizzcastAudioError("accepted RSS is missing one or more fixed episode enclosures")
    catalog = {
        "schema": "wow-blizzcast-current-origin-audio-catalog/v1",
        "inventory": {"audio_restored": True, "classification": "current_origin_audio_copy"},
        "source_acquired_date": source_date,
        "source_note": SOURCE_NOTE,
        "blizzcast_source_map_sha256": audio_map["blizzcast_source_map_sha256"],
        "blizzcast_source_acceptance_sha256": audio_map["blizzcast_source_acceptance_sha256"],
        "blizzcast_rss_sha256": rss_data["rss_sha256"],
        "current_origin_acceptance_sha256": acceptance_sha,
        "payload_zip_sha256": zip_sha,
        "historical_byte_identity": "unknown; the 2008 RSS contains no MP3 digest",
        "records": catalog_records,
    }
    catalog_bytes = (json.dumps(catalog, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return BlizzcastAudioBundle(
        assets=assets,
        catalog_path=CATALOG_ROUTE,
        catalog_bytes=catalog_bytes,
        origin_routes={item["original_url"]: item["canonical_path"] for item in records},
        estimated_bytes=sum(len(item["data"]) for item in assets) + len(catalog_bytes),
        map_sha256=_sha256(map_raw),
        source_acceptance_sha256=str(audio_map["blizzcast_source_acceptance_sha256"]),
        current_origin_acceptance_sha256=acceptance_sha,
        payload_zip_sha256=zip_sha,
        source_date=str(source_date),
    )


def _q(tag: str) -> str:
    return f"{{{blizzcast_reader.XHTML_NS}}}{tag}"


def _has_class(element: ET.Element, name: str) -> bool:
    return name in (element.attrib.get("class") or "").split()


def _page_text(root: ET.Element, *, element_id: str) -> str:
    target = next((item for item in root.iter() if item.attrib.get("id") == element_id), None)
    return "".join(target.itertext()) if target is not None else ""


def _replace_text_nodes(root: ET.Element, old: str, new: str) -> None:
    for element in root.iter():
        if element.text:
            element.text = element.text.replace(old, new)
        if element.tail:
            element.tail = element.tail.replace(old, new)


def _static_url(base_path: str, route: str) -> str:
    return blizzcast_reader._static_url(base_path, route)


def augment_reader_bundle(reader_bundle: blizzcast_reader.BlizzcastBundle, audio_bundle: BlizzcastAudioBundle) -> None:
    """Add the current-copy notice, players, and feed downloads in-place.

    Existing transcript nodes are checked before and after serialization so
    this opt-in presentation layer cannot alter transcript text.
    """

    pages = {
        item["path"]: item
        for item in reader_bundle.generated_files
        if item.get("mime") == "application/xhtml+xml"
    }
    expected_pages = {blizzcast_reader.ROUTES_BY_ENTITY[key] for key in blizzcast_reader.EXPECTED_IDS}
    if set(pages) != expected_pages:
        raise BlizzcastAudioError("audio presentation requires the fixed five BlizzCast reader pages")
    by_url = {asset["record"]["original_url"]: asset for asset in audio_bundle.assets}
    if set(by_url) != {item["url"] for item in EXPECTED_EPISODES}:
        raise BlizzcastAudioError("audio bundle does not contain the two fixed source URLs")
    original_transcripts: dict[str, str] = {}
    roots: dict[str, ET.Element] = {}
    for route, page in pages.items():
        try:
            root = ET.fromstring(str(page["data"]).encode("utf-8"))
        except ET.ParseError as exc:
            raise BlizzcastAudioError(f"cannot parse generated reader page: {route}") from exc
        if root.tag != _q("html"):
            raise BlizzcastAudioError(f"unexpected XHTML root on {route}")
        original_transcripts[route] = _page_text(root, element_id="transcript")
        roots[route] = root
        _replace_text_nodes(
            root,
            "Images, audio, and interactive media are not restored in this offline reading view. ",
            "Images and interactive media remain unrestored in this offline reading view. ",
        )
        _replace_text_nodes(
            root,
            "Historical reading edition. Original images and audio remain to be recovered.",
            "Historical reading edition. Original images and interactive media remain to be recovered; current-origin audio copies are available in this reader.",
        )
        _replace_text_nodes(
            root,
            "This RSS capture is converted into two text entries. Audio files are referenced in the dependency inventory but are not restored here.",
            "This RSS capture is converted into two text entries with local audio downloads for the current-origin copies.",
        )
        needs_player = route in {
            blizzcast_reader.ROUTES_BY_ENTITY["BC02"],
            blizzcast_reader.ROUTES_BY_ENTITY["BC03"],
        }
        policy = next((
            element for element in root.iter()
            if element.tag == _q("meta")
            and element.attrib.get("http-equiv", "").casefold() == "content-security-policy"
        ), None)
        if policy is None:
            raise BlizzcastAudioError(f"reader page has no Content-Security-Policy meta tag: {route}")
        csp = policy.attrib.get("content", "")
        if "default-src 'none'" not in csp:
            raise BlizzcastAudioError(f"reader CSP changed outside the accepted audio opt-in contract on {route}")
        if needs_player:
            if "media-src" in csp:
                raise BlizzcastAudioError(f"reader CSP unexpectedly already declares media-src on {route}")
            policy.set("content", csp.replace("default-src 'none';", "default-src 'none'; media-src 'self';", 1))
        elif "media-src" in csp:
            raise BlizzcastAudioError(f"reader CSP unexpectedly permits media on a non-player page: {route}")
        main = next((item for item in root.iter() if item.tag == _q("main") and item.attrib.get("id") == "reader-content"), None)
        if main is None:
            raise BlizzcastAudioError(f"generated reader page has no reader-content main: {route}")
        note = ET.Element(_q("p"), {"class": "current-origin-audio-note", "role": "note"})
        note.text = SOURCE_NOTE
        main.insert(0, note)

    feed_route = blizzcast_reader.ROUTES_BY_ENTITY["BC01"]
    feed_root = roots[feed_route]
    feed_rows = [
        item for item in reader_bundle.dependency_inventory
        if item.get("source_entity_id") == "BC01"
        and item.get("kind") == "audio"
        and item.get("requested_url") in by_url
    ]
    all_audio_rows = [item for item in reader_bundle.dependency_inventory if item.get("kind") == "audio"]
    articles = [item for item in feed_root.iter() if item.tag == _q("article") and _has_class(item, "feed-entry")]
    if (
        len(feed_rows) != 2
        or len(all_audio_rows) != 2
        or {item["requested_url"] for item in feed_rows} != set(by_url)
        or len(articles) != 2
    ):
        raise BlizzcastAudioError("RSS reader output does not expose exactly the two accepted enclosure entries")
    for row, article in zip(feed_rows, articles, strict=True):
        asset = by_url[row["requested_url"]]
        row.update({
            "restored": True,
            "local_route": asset["record"]["path"],
            "missing_route": None,
            "reason": "accepted-current-origin-audio-copy",
        })
        for child in list(article):
            if child.tag == _q("p") and _has_class(child, "unrestored-notice"):
                article.remove(child)
        number = "1" if asset["record"]["id"] == "episode1" else "2"
        paragraph = ET.SubElement(article, _q("p"), {"class": "audio-copy-download"})
        link = ET.SubElement(paragraph, _q("a"), {
            "href": _static_url(reader_bundle.base_path, asset["record"]["path"]),
            "download": f"episode{number}.mp3",
        })
        link.text = f"Download Episode {number} audio (MP3 current copy)"

    for episode in EXPECTED_EPISODES:
        page_route = blizzcast_reader.ROUTES_BY_ENTITY["BC02" if episode["id"] == "episode1" else "BC03"]
        root = roots[page_route]
        main = next(item for item in root.iter() if item.tag == _q("main") and item.attrib.get("id") == "reader-content")
        audio_section = ET.Element(_q("section"), {"class": "audio-copy-player", "aria-label": f"{episode['id']} current media copy"})
        audio = ET.SubElement(audio_section, _q("audio"), {"controls": "controls", "preload": "none"})
        ET.SubElement(audio, _q("source"), {
            "src": _static_url(reader_bundle.base_path, episode["route"]),
            "type": "audio/mpeg",
        })
        audio.text = "Your browser does not support audio playback. Use the download link below."
        download = ET.SubElement(audio_section, _q("p"), {"class": "audio-copy-download"})
        link = ET.SubElement(download, _q("a"), {
            "href": _static_url(reader_bundle.base_path, episode["route"]),
            "download": f"{episode['id']}.mp3",
        })
        number = "1" if episode["id"] == "episode1" else "2"
        link.text = f"Download Episode {number} audio (MP3 current copy)"
        main.insert(2, audio_section)

    for route, root in roots.items():
        if _page_text(root, element_id="transcript") != original_transcripts[route]:
            raise BlizzcastAudioError(f"audio augmentation changed transcript text on {route}")
        page = pages[route]
        page["data"] = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode", method="xml") + "\n"
        page["bytes"] = len(str(page["data"]).encode("utf-8"))
    css = next((item for item in reader_bundle.generated_files if item.get("path") == blizzcast_reader.CSS_ROUTE), None)
    if css is None:
        raise BlizzcastAudioError("generated reader bundle has no local stylesheet")
    css["data"] = str(css["data"]) + (
        "\n.current-origin-audio-note { border-left: 4px solid #315c7d; background: #edf6fc; padding: .6rem .8rem; }\n"
        ".audio-copy-player audio { display: block; width: min(100%, 38rem); margin: 1rem 0; }\n"
        ".audio-copy-download { margin: .4rem 0 1rem; }\n"
    )
    css["bytes"] = len(str(css["data"]).encode("utf-8"))
    reader_bundle.origin_routes.update(audio_bundle.origin_routes)
    reader_bundle.estimated_bytes = sum(int(item["bytes"]) for item in reader_bundle.generated_files)


__all__ = [
    "AUDIO_ROUTE",
    "BlizzcastAudioBundle",
    "BlizzcastAudioError",
    "CATALOG_ROUTE",
    "SOURCE_NOTE",
    "augment_reader_bundle",
    "load_blizzcast_audio_bundle",
]
