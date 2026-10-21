"""Build a small, dependency-free historical BlizzCast reading bundle.

The reader consumes only the five locally accepted XML payloads named by the
input source map.  It never follows links, loads a DTD, executes script, or
copies the original site chrome.  The returned bundle is intentionally a
data object for the local exporter; this module does not write a site.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote, urljoin, urlsplit


XHTML_NS = "http://www.w3.org/1999/xhtml"
XML_NS = "http://www.w3.org/XML/1998/namespace"
ET.register_namespace("", XHTML_NS)
ET.register_namespace("xml", XML_NS)

READER_ROUTE = "/__offline/related-sites/blizzcast/"
ROUTES_BY_ENTITY = {
    "BC05": READER_ROUTE + "index.html",
    "BC04": READER_ROUTE + "archive.html",
    "BC02": READER_ROUTE + "episode1.html",
    "BC03": READER_ROUTE + "episode2.html",
    "BC01": READER_ROUTE + "feed.html",
}
CSS_ROUTE = READER_ROUTE + "reader.css"

EXPECTED_URLS = {
    "BC01": "http://us.blizzard.com/blizzcast/_content/en-US/rss.xml",
    "BC02": "http://us.blizzard.com/blizzcast/archive/episode1.xml",
    "BC03": "http://us.blizzard.com/blizzcast/archive/episode2.xml",
    "BC04": "http://us.blizzard.com/blizzcast/archive.xml",
    "BC05": "http://us.blizzard.com/blizzcast/index.xml",
}
EXPECTED_IDS = ("BC01", "BC02", "BC03", "BC04", "BC05")
FORBIDDEN_TAGS = {
    "script",
    "style",
    "form",
    "input",
    "textarea",
    "select",
    "option",
    "button",
    "iframe",
    "object",
    "embed",
    "link",
    "meta",
    "base",
}
RESOURCE_TAGS = {"img", "audio", "video", "source", "track", "object", "embed", "iframe"}
BLOCK_TAGS = {
    "address",
    "article",
    "aside",
    "blockquote",
    "caption",
    "center",
    "dd",
    "div",
    "dl",
    "dt",
    "figcaption",
    "figure",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "li",
    "main",
    "ol",
    "p",
    "pre",
    "section",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "tr",
    "ul",
}
INLINE_TAGS = {"a", "b", "br", "code", "em", "i", "q", "small", "span", "strong", "sub", "sup"}
SAFE_CLASS_MAP = {
    "highlight": "speaker",
    "timecode": "timecode",
    "block": "transcript-paragraph",
    "int": "transcript-inner",
}
TIME_ID_RE = re.compile(r"^\d{1,2}:\d{2}(?::\d{2})?$")
ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]*$")


class BlizzcastReaderError(ValueError):
    """Raised when the accepted local input contract is not met."""


@dataclass
class BlizzcastBundle:
    """Exporter-facing bundle returned by :func:`load_blizzcast_bundle`."""

    generated_files: list[dict[str, Any]]
    origin_routes: dict[str, str]
    estimated_bytes: int
    dependency_inventory: list[dict[str, Any]]
    source_records: list[dict[str, Any]]
    base_path: str

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def as_dict(self) -> dict[str, Any]:
        return {
            "generated_files": self.generated_files,
            "origin_routes": self.origin_routes,
            "estimated_bytes": self.estimated_bytes,
            "dependency_inventory": self.dependency_inventory,
            "source_records": self.source_records,
            "base_path": self.base_path,
        }


@dataclass
class _RenderContext:
    record: dict[str, Any]
    page_route: str
    base_path: str
    origin_routes: dict[str, str]
    inventory: list[dict[str, Any]]


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].casefold()


def _q(name: str) -> str:
    return f"{{{XHTML_NS}}}{name}"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalise_base_path(base_path: str | Path | None) -> str:
    if base_path is None or str(base_path) in {"", "/"}:
        return ""
    value = str(base_path)
    if any(token in value for token in ("?", "#", "\\", "\x00")):
        raise BlizzcastReaderError("base_path must not contain query, fragment, backslash, or NUL")
    if "://" in value or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value):
        raise BlizzcastReaderError("base_path must be a local URL path")
    normalised = "/" + value.strip("/") + "/"
    if ".." in normalised.split("/"):
        raise BlizzcastReaderError("base_path traversal")
    return re.sub(r"/{2,}", "/", normalised)


def _static_url(base_path: str, route: str) -> str:
    if not route.startswith("/") or ".." in route.split("/"):
        raise BlizzcastReaderError(f"unsafe local route: {route!r}")
    return base_path + route.lstrip("/") if base_path else route


def _resolve_workspace_path(workspace_root: Path, value: str | Path) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = workspace_root / candidate
    resolved = candidate.resolve()
    root = workspace_root.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise BlizzcastReaderError(f"path escapes workspace root: {value!r}") from exc
    return resolved


def _reject_external_markup(raw: bytes, path: Path) -> None:
    lowered = raw.lower()
    if b"<!entity" in lowered:
        raise BlizzcastReaderError(f"ENTITY declarations are forbidden in {path}")


def _parse_xml(path: Path) -> ET.Element:
    raw = path.read_bytes()
    _reject_external_markup(raw, path)
    # The accepted XHTML payloads carry a historical public DOCTYPE.  Remove
    # that declaration before stdlib parsing so ElementTree never attempts to
    # resolve a DTD; ENTITY declarations were rejected above.
    raw = re.sub(rb"<!DOCTYPE[^>]*>", b"", raw, flags=re.IGNORECASE | re.DOTALL)
    try:
        return ET.fromstring(raw)
    except ET.ParseError as exc:
        raise BlizzcastReaderError(f"malformed XML in {path}: {exc}") from exc


def _class_tokens(element: ET.Element) -> set[str]:
    return {token.casefold() for token in element.attrib.get("class", "").split() if token}


def _first_by_id(root: ET.Element, wanted: str) -> ET.Element | None:
    for element in root.iter():
        if element.attrib.get("id") == wanted:
            return element
    return None


def _first_by_class(root: ET.Element, wanted: str) -> ET.Element | None:
    wanted = wanted.casefold()
    for element in root.iter():
        if wanted in _class_tokens(element):
            return element
    return None


def _count_transcript_blocks(root: ET.Element) -> int:
    return sum("trans" in _class_tokens(element) for element in root.iter())


def _visible_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return re.sub(r"\s+", " ", "".join(element.itertext())).strip()


def _source_ref(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: copy.deepcopy(record[key])
        for key in (
            "entity_id",
            "original_url",
            "actual_capture_timestamp",
            "temporal_relation",
            "mime",
            "sha256",
            "length",
            "sha1_base32",
            "title",
            "transcript_blocks",
            "rss_items",
            "source_arc",
        )
        if key in record
    }


def _capture_label(timestamp: str) -> str:
    try:
        parsed = datetime.strptime(timestamp, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
        return parsed.strftime("%Y-%m-%d %H:%M:%S UTC")
    except (TypeError, ValueError):
        return str(timestamp)


def _load_inputs(map_path: Path, workspace_root: Path) -> tuple[dict[str, Any], dict[str, ET.Element]]:
    try:
        source_map = json.loads(map_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BlizzcastReaderError(f"cannot read input source map: {map_path}") from exc
    if source_map.get("schema") != "wow-blizzcast-reader-input/v1" or source_map.get("accepted") is not True:
        raise BlizzcastReaderError("input source map is not an accepted BlizzCast map")
    acceptance_path = _resolve_workspace_path(workspace_root, source_map.get("source_acceptance", ""))
    if not acceptance_path.is_file():
        raise BlizzcastReaderError("source acceptance receipt is missing")
    if _sha256_file(acceptance_path) != source_map.get("source_acceptance_sha256"):
        raise BlizzcastReaderError("source acceptance SHA256 mismatch")
    try:
        acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BlizzcastReaderError("source acceptance receipt is not valid JSON") from exc
    if acceptance.get("accepted") is not True:
        raise BlizzcastReaderError("source acceptance is not accepted")
    records = source_map.get("records")
    if not isinstance(records, list) or [item.get("entity_id") for item in records] != list(EXPECTED_IDS):
        raise BlizzcastReaderError("source map must contain BC01 through BC05 in fixed order")
    accepted_by_id = {item.get("entity_id"): item for item in acceptance.get("entities", [])}
    if set(accepted_by_id) != set(EXPECTED_IDS) or acceptance.get("actual_transcript_blocks") != sum(
        int(item.get("transcript_blocks") or 0) for item in accepted_by_id.values()
    ):
        raise BlizzcastReaderError("source acceptance transcript coverage is inconsistent")
    roots: dict[str, ET.Element] = {}
    for record in records:
        entity_id = record.get("entity_id")
        if entity_id not in EXPECTED_URLS or record.get("original_url") != EXPECTED_URLS[entity_id]:
            raise BlizzcastReaderError(f"unexpected source URL for {entity_id}")
        parsed = urlsplit(record["original_url"])
        if parsed.hostname != "us.blizzard.com" or not parsed.path.startswith("/blizzcast/"):
            raise BlizzcastReaderError(f"source is outside fixed us.blizzard.com/blizzcast scope: {entity_id}")
        accepted_record = accepted_by_id.get(entity_id)
        if not accepted_record:
            raise BlizzcastReaderError(f"source acceptance is missing {entity_id}")
        for field in (
            "original_url", "sha256", "length", "payload_path", "actual_capture_timestamp",
            "temporal_relation", "mime", "sha1_base32", "title", "transcript_blocks", "rss_items", "source_arc",
        ):
            if accepted_record.get(field) != record.get(field):
                raise BlizzcastReaderError(f"source acceptance mismatch for {entity_id}.{field}")
        payload_path = _resolve_workspace_path(workspace_root, record.get("payload_path", ""))
        if not payload_path.is_file():
            raise BlizzcastReaderError(f"payload is missing for {entity_id}")
        raw = payload_path.read_bytes()
        if len(raw) != record.get("length") or _sha256_bytes(raw) != record.get("sha256"):
            raise BlizzcastReaderError(f"payload integrity mismatch for {entity_id}")
        root = _parse_xml(payload_path)
        expected_root = "rss" if entity_id == "BC01" else "html"
        if _local_name(root.tag) != expected_root:
            raise BlizzcastReaderError(f"unexpected XML root for {entity_id}")
        expected_blocks = int(record.get("transcript_blocks") or 0)
        if _count_transcript_blocks(root) != expected_blocks:
            raise BlizzcastReaderError(f"transcript block count mismatch for {entity_id}")
        if entity_id == "BC01":
            item_count = sum(_local_name(item.tag) == "item" for item in root.iter())
            if item_count != int(record.get("rss_items") or 0):
                raise BlizzcastReaderError("RSS item count mismatch")
        roots[entity_id] = root
    return source_map, roots


def _route_for_url(url: str, origin_routes: dict[str, str]) -> str | None:
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError:
        return None
    scheme = parsed.scheme.casefold()
    if scheme not in {"http", "https"} or parsed.hostname not in {"us.blizzard.com", "www.blizzard.com"}:
        return None
    if parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment:
        return None
    if port is not None and port != (80 if scheme == "http" else 443):
        return None
    if url in origin_routes:
        return origin_routes[url]
    path = parsed.path or "/"
    # Historical pages used both www.blizzard.com and us.blizzard.com links;
    # localize only the exact BlizzCast paths represented by the accepted map.
    for original, route in origin_routes.items():
        original_parts = urlsplit(original)
        if parsed.path == original_parts.path and path.startswith("/blizzcast/"):
            return route
    if path in {"/blizzcast", "/blizzcast/"}:
        return origin_routes.get("http://us.blizzard.com/blizzcast/")
    if path == "/blizzcast/_content/en-US/rss.xml":
        return origin_routes.get(EXPECTED_URLS["BC01"])
    return None


def _missing_route(base_path: str, source_page: str, requested: str) -> str:
    query = (
        "?source="
        + quote(source_page, safe="")
        + "&requested="
        + quote(requested, safe="")
        + "&reason=not-restored-blizzcast-resource"
    )
    return _static_url(base_path, "/__offline/missing.html" + query)


def _dependency_kind(tag: str, attr: str) -> str:
    tag = tag.casefold()
    attr = attr.casefold()
    if tag in {"img", "image"} or attr in {"poster", "background"}:
        return "image"
    if tag in {"audio", "video", "source", "enclosure"} or attr in {"audio", "enclosure"}:
        return "audio"
    if tag in {"script"}:
        return "script"
    if tag in {"link"}:
        return "stylesheet" if attr == "href" else "link"
    if tag in {"iframe", "frame"}:
        return "iframe"
    if tag in {"object", "embed"}:
        return "object"
    if tag == "a":
        return "navigation"
    return "resource"


def _absolute_reference(page_url: str, raw: str) -> str:
    value = raw.strip()
    if value.startswith("#"):
        return value
    return urljoin(page_url, value)


def _add_inventory(
    inventory: list[dict[str, Any]],
    seen: set[tuple[str, str, str]],
    *,
    record: dict[str, Any],
    page_route: str,
    raw: str,
    attr: str,
    kind: str,
    base_path: str,
    origin_routes: dict[str, str],
) -> dict[str, Any] | None:
    if not raw or raw.strip().startswith("#"):
        return None
    requested = _absolute_reference(record["original_url"], raw)
    key = (record["entity_id"], kind, requested)
    route = _route_for_url(requested, origin_routes)
    if key in seen:
        for item in inventory:
            if (item["source_entity_id"], item["kind"], item["requested_url"]) == key:
                return item
        return None
    seen.add(key)
    item = {
        "source_entity_id": record["entity_id"],
        "page_route": page_route,
        "raw_reference": raw,
        "attribute": attr,
        "kind": kind,
        "requested_url": requested,
        "restored": route is not None,
        "local_route": route,
        "missing_route": None if route is not None else _missing_route(base_path, record["original_url"], requested),
        "reason": "accepted-local-route" if route is not None else "not-restored-in-reader-bundle",
    }
    inventory.append(item)
    return item


def _extract_inventory(
    records: list[dict[str, Any]],
    roots: dict[str, ET.Element],
    *,
    base_path: str,
    origin_routes: dict[str, str],
) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for record in records:
        page_route = ROUTES_BY_ENTITY[record["entity_id"]]
        for element in roots[record["entity_id"]].iter():
            tag = _local_name(element.tag)
            for attr in ("href", "src", "data", "url", "poster"):
                raw = element.attrib.get(attr)
                if raw:
                    _add_inventory(
                        inventory,
                        seen,
                        record=record,
                        page_route=page_route,
                        raw=raw,
                        attr=attr,
                        kind=_dependency_kind(tag, attr),
                        base_path=base_path,
                        origin_routes=origin_routes,
                    )
    return inventory


def _clean_fragment(value: str | None) -> str:
    if not value:
        return ""
    collapsed = re.sub(r"\s+", " ", value)
    stripped = collapsed.strip()
    if not stripped:
        return ""
    prefix = " " if collapsed[:1].isspace() else ""
    suffix = " " if collapsed[-1:].isspace() else ""
    return prefix + stripped + suffix


def _safe_class(element: ET.Element) -> str | None:
    tokens = _class_tokens(element)
    for token, safe in SAFE_CLASS_MAP.items():
        if token in tokens:
            return safe
    if "trans" in tokens:
        return "transcript-block"
    return None


def _inventory_item_for(ctx: _RenderContext, raw: str, kind: str, attr: str) -> dict[str, Any] | None:
    requested = _absolute_reference(ctx.record["original_url"], raw)
    for item in ctx.inventory:
        if (
            item["source_entity_id"] == ctx.record["entity_id"]
            and item["requested_url"] == requested
            and item["kind"] == kind
        ):
            return item
    # A link may only be discovered in a selected subtree after inventory
    # extraction. Keep the same deterministic schema if that happens.
    seen = {(item["source_entity_id"], item["kind"], item["requested_url"]) for item in ctx.inventory}
    return _add_inventory(
        ctx.inventory,
        seen,
        record=ctx.record,
        page_route=ctx.page_route,
        raw=raw,
        attr=attr,
        kind=kind,
        base_path=ctx.base_path,
        origin_routes=ctx.origin_routes,
    )


def _local_href(ctx: _RenderContext, raw: str, *, kind: str, attr: str) -> str | None:
    value = raw.strip()
    if value.startswith("#"):
        fragment = value[1:]
        return "#" + fragment if ID_RE.fullmatch(fragment) else None
    item = _inventory_item_for(ctx, value, kind, attr)
    if item is None:
        return None
    if item["restored"]:
        return _static_url(ctx.base_path, item["local_route"])
    return item["missing_route"]


def _copy_safe_node(source: ET.Element, parent: ET.Element, ctx: _RenderContext) -> ET.Element | None:
    local = _local_name(source.tag)
    if local in FORBIDDEN_TAGS:
        return None
    if local in RESOURCE_TAGS:
        for attr in ("href", "src", "data", "url", "poster"):
            raw = source.attrib.get(attr)
            if raw:
                _inventory_item_for(ctx, raw, _dependency_kind(local, attr), attr)
        return None
    if local == "span" and "timecode" in _class_tokens(source):
        target = ET.SubElement(parent, _q("span"), {"class": "timecode"})
        # Flatten the historical nested span so the complete static timecode
        # remains visible and searchable as ``[ 00:14 ]``.
        target.text = _visible_text(source)
        return target
    if local == "a" and source.attrib.get("href", "").strip().casefold().startswith("javascript:"):
        timestamp_id = source.attrib.get("id", "")
        if not (source.text or len(source)) and TIME_ID_RE.fullmatch(timestamp_id) is not None:
            # The visible timecode text is retained by the neighboring static
            # timecode span.  Do not emit an empty ``<a />``: HTML parsing
            # would treat it as an unclosed anchor and swallow the transcript.
            return None
        target = ET.SubElement(parent, _q("a")) if TIME_ID_RE.fullmatch(timestamp_id) else ET.SubElement(parent, _q("span"))
        if TIME_ID_RE.fullmatch(timestamp_id):
            target.set("id", "time-" + timestamp_id.replace(":", "-"))
        target.text = _clean_fragment(source.text)
        for child in source:
            copied = _copy_safe_node(child, target, ctx)
            if child.tail:
                tail = _clean_fragment(child.tail)
                if copied is not None:
                    copied.tail = (copied.tail or "") + tail
                elif len(target):
                    target[-1].tail = (target[-1].tail or "") + tail
                else:
                    target.text = (target.text or "") + tail
        return target
    if local == "a" and source.attrib.get("id") and not source.attrib.get("href") and TIME_ID_RE.fullmatch(source.attrib["id"]):
        if not (source.text or len(source)):
            return None
        target = ET.SubElement(parent, _q("a"), {"id": "time-" + source.attrib["id"].replace(":", "-")})
        target.text = _clean_fragment(source.text)
        return target
    if local == "a":
        tag = "a"
    elif local in BLOCK_TAGS or local in INLINE_TAGS:
        tag = local
    else:
        tag = "div" if source.text or list(source) else None
    if tag is None:
        return None
    target = ET.SubElement(parent, _q(tag))
    safe_class = _safe_class(source)
    if safe_class:
        target.set("class", safe_class)
    if local == "a":
        raw_href = source.attrib.get("href")
        if raw_href:
            href = _local_href(ctx, raw_href, kind="navigation", attr="href")
            if href:
                target.set("href", href)
            else:
                # Keep the visible label but never emit an executable or
                # external link when no local route exists.
                target.tag = _q("span")
    if local == "br":
        return target
    target.text = _clean_fragment(source.text)
    for child in source:
        copied = _copy_safe_node(child, target, ctx)
        if child.tail:
            tail = _clean_fragment(child.tail)
            if copied is not None:
                copied.tail = (copied.tail or "") + tail
            elif len(target):
                target[-1].tail = (target[-1].tail or "") + tail
            else:
                target.text = (target.text or "") + tail
    if local == "a" and not (target.text or len(target)):
        parent.remove(target)
        return None
    return target


def _append_copy(parent: ET.Element, source: ET.Element | None, ctx: _RenderContext) -> None:
    if source is not None:
        _copy_safe_node(source, parent, ctx)


def _append_text(parent: ET.Element, tag: str, text: str, *, class_name: str | None = None) -> ET.Element:
    element = ET.SubElement(parent, _q(tag))
    if class_name:
        element.set("class", class_name)
    element.text = text
    return element


def _append_link(parent: ET.Element, label: str, href: str, *, class_name: str | None = None) -> ET.Element:
    element = ET.SubElement(parent, _q("a"))
    if class_name:
        element.set("class", class_name)
    element.set("href", href)
    element.text = label
    return element


def _append_nav_separator(parent: ET.Element) -> ET.Element:
    # Give the span text so HTML parsing does not treat ``<span />`` as an
    # unclosed element when the XHTML is served by a simple text/html server.
    element = ET.SubElement(parent, _q("span"), {"class": "nav-separator"})
    element.text = "·"
    return element


def _append_nav(body: ET.Element, base_path: str, route: str) -> None:
    nav = ET.SubElement(body, _q("nav"), {"class": "archive-nav", "aria-label": "BlizzCast archive navigation"})
    _append_link(nav, "Archive home", _static_url(base_path, ROUTES_BY_ENTITY["BC04"]))
    _append_nav_separator(nav)
    _append_link(nav, "BlizzCast index", _static_url(base_path, ROUTES_BY_ENTITY["BC05"]))
    if route == ROUTES_BY_ENTITY["BC02"]:
        _append_nav_separator(nav)
        _append_link(nav, "Next: Episode 2", _static_url(base_path, ROUTES_BY_ENTITY["BC03"]))
    elif route == ROUTES_BY_ENTITY["BC03"]:
        _append_nav_separator(nav)
        _append_link(nav, "Previous: Episode 1", _static_url(base_path, ROUTES_BY_ENTITY["BC02"]))
    elif route == ROUTES_BY_ENTITY["BC04"]:
        _append_nav_separator(nav)
        _append_link(nav, "Episode 1", _static_url(base_path, ROUTES_BY_ENTITY["BC02"]))
        _append_nav_separator(nav)
        _append_link(nav, "Episode 2", _static_url(base_path, ROUTES_BY_ENTITY["BC03"]))


def _new_document(record: dict[str, Any], *, base_path: str, route: str, title: str, late_note: bool) -> tuple[ET.Element, ET.Element, _RenderContext]:
    root = ET.Element(_q("html"), {f"{{{XML_NS}}}lang": "en-US"})
    head = ET.SubElement(root, _q("head"))
    _append_text(head, "title", title)
    ET.SubElement(head, _q("meta"), {"charset": "utf-8"})
    ET.SubElement(head, _q("meta"), {"name": "viewport", "content": "width=device-width, initial-scale=1"})
    ET.SubElement(head, _q("meta"), {
        "http-equiv": "Content-Security-Policy",
        "content": "default-src 'none'; style-src 'self'; base-uri 'none'; form-action 'none'",
    })
    ET.SubElement(head, _q("link"), {"rel": "stylesheet", "href": _static_url(base_path, CSS_ROUTE)})
    body = ET.SubElement(root, _q("body"))
    shell = ET.SubElement(body, _q("div"), {"class": "reader-shell"})
    header = ET.SubElement(shell, _q("header"), {"class": "reader-header"})
    _append_text(header, "p", "Independent historical archive / BlizzCast archival reading view", class_name="reader-kicker")
    _append_text(header, "h1", title)
    _append_text(header, "p", f"Captured {_capture_label(record['actual_capture_timestamp'])} from {record['original_url']}", class_name="capture-note")
    if late_note:
        _append_text(header, "p", "Late supplement: this source was captured after the 2008-05-12 reference window.", class_name="late-supplement")
    _append_nav(shell, base_path, route)
    main = ET.SubElement(shell, _q("main"), {"id": "reader-content"})
    return root, main, _RenderContext(record, route, base_path, {}, [])


def _append_unrestored_notice(main: ET.Element, ctx: _RenderContext) -> None:
    media = [
        item
        for item in ctx.inventory
        if item["page_route"] == ctx.page_route and not item["restored"] and item["kind"] in {"image", "audio", "object", "video"}
    ]
    paragraph = ET.SubElement(main, _q("p"), {"class": "unrestored-notice"})
    paragraph.text = "Images, audio, and interactive media are not restored in this offline reading view. "
    if media:
        _append_link(paragraph, "Open a local missing-resource note", media[0]["missing_route"])
    else:
        paragraph.text += "No playable media is embedded."


def _append_footer(shell: ET.Element, record: dict[str, Any]) -> None:
    footer = ET.SubElement(shell, _q("footer"), {"class": "reader-footer"})
    _append_text(footer, "p", f"Historical source: {record['original_url']}")
    _append_text(footer, "p", "Historical reading edition. Original images and audio remain to be recovered.")


def _render_episode(record: dict[str, Any], root: ET.Element, *, base_path: str, origin_routes: dict[str, str], inventory: list[dict[str, Any]]) -> str:
    route = ROUTES_BY_ENTITY[record["entity_id"]]
    document, main, ctx = _new_document(record, base_path=base_path, route=route, title=record["title"], late_note=False)
    ctx.origin_routes = origin_routes
    ctx.inventory = inventory
    _append_text(main, "h2", "Interview transcript")
    _append_text(main, "p", "Captured transcript with speaker labels and timecodes.", class_name="reader-intro")
    transcript = ET.SubElement(main, _q("div"), {"id": "transcript", "class": "transcript"})
    blocks = [element for element in root.iter() if "trans" in _class_tokens(element)]
    for index, block in enumerate(blocks, start=1):
        section = ET.SubElement(transcript, _q("section"), {"class": "transcript-block", "id": f"transcript-{index}"})
        for child in block:
            copied = _copy_safe_node(child, section, ctx)
            if child.tail:
                tail = _clean_fragment(child.tail)
                if copied is not None:
                    copied.tail = (copied.tail or "") + tail
                elif len(section):
                    section[-1].tail = (section[-1].tail or "") + tail
                else:
                    section.text = (section.text or "") + tail
    if len(blocks) != int(record.get("transcript_blocks") or 0):
        raise BlizzcastReaderError(f"rendered transcript block count mismatch for {record['entity_id']}")
    _append_unrestored_notice(main, ctx)
    shell = document.find(_q("body"))
    assert shell is not None
    shell = shell.find(_q("div"))
    assert shell is not None
    _append_footer(shell, record)
    return _serialize(document)


def _render_index(record: dict[str, Any], root: ET.Element, *, base_path: str, origin_routes: dict[str, str], inventory: list[dict[str, Any]]) -> str:
    route = ROUTES_BY_ENTITY["BC05"]
    document, main, ctx = _new_document(record, base_path=base_path, route=route, title=record["title"], late_note=True)
    ctx.origin_routes = origin_routes
    ctx.inventory = inventory
    _append_copy(main, _first_by_class(root, "lcol"), ctx)
    _append_text(main, "h2", "Current podcast and show archives")
    _append_copy(main, _first_by_class(root, "rcol"), ctx)
    _append_unrestored_notice(main, ctx)
    shell = document.find(_q("body")); assert shell is not None
    shell = shell.find(_q("div")); assert shell is not None
    _append_footer(shell, record)
    return _serialize(document)


def _render_archive(record: dict[str, Any], root: ET.Element, *, base_path: str, origin_routes: dict[str, str], inventory: list[dict[str, Any]]) -> str:
    route = ROUTES_BY_ENTITY["BC04"]
    document, main, ctx = _new_document(record, base_path=base_path, route=route, title=record["title"], late_note=True)
    ctx.origin_routes = origin_routes
    ctx.inventory = inventory
    _append_text(main, "h2", "Archive home")
    _append_text(main, "p", "This late-supplement archive lists the captured episode descriptions and transcript routes.", class_name="reader-intro")
    _append_copy(main, _first_by_id(root, "archive"), ctx)
    _append_unrestored_notice(main, ctx)
    shell = document.find(_q("body")); assert shell is not None
    shell = shell.find(_q("div")); assert shell is not None
    _append_footer(shell, record)
    return _serialize(document)


def _rss_child(parent: ET.Element, name: str) -> ET.Element | None:
    for child in parent:
        if _local_name(child.tag) == name:
            return child
    return None


def _render_feed(record: dict[str, Any], root: ET.Element, *, base_path: str, origin_routes: dict[str, str], inventory: list[dict[str, Any]]) -> str:
    route = ROUTES_BY_ENTITY["BC01"]
    channel = next((element for element in root.iter() if _local_name(element.tag) == "channel"), root)
    document, main, ctx = _new_document(record, base_path=base_path, route=route, title="BlizzCast text feed", late_note=False)
    ctx.origin_routes = origin_routes
    ctx.inventory = inventory
    _append_text(main, "h2", _visible_text(_rss_child(channel, "title")) or record["title"])
    _append_text(main, "p", _visible_text(_rss_child(channel, "description")), class_name="reader-intro")
    _append_text(main, "p", "This RSS capture is converted into two text entries. Audio files are referenced in the dependency inventory but are not restored here.", class_name="reader-intro")
    for item in [element for element in channel if _local_name(element.tag) == "item"]:
        article = ET.SubElement(main, _q("article"), {"class": "feed-entry"})
        title = _visible_text(_rss_child(item, "title"))
        _append_text(article, "h2", title)
        pubdate = _visible_text(_rss_child(item, "pubDate"))
        if pubdate:
            _append_text(article, "p", pubdate, class_name="date-note")
        _append_text(article, "p", _visible_text(_rss_child(item, "description")))
        source_link = _visible_text(_rss_child(item, "link"))
        local_route = _route_for_url(source_link, origin_routes) if source_link else None
        if local_route:
            _append_link(article, "Read the captured transcript", _static_url(base_path, local_route))
        enclosure = _rss_child(item, "enclosure")
        if enclosure is not None and enclosure.attrib.get("url"):
            href = _local_href(ctx, enclosure.attrib["url"], kind="audio", attr="url")
            notice = ET.SubElement(article, _q("p"), {"class": "unrestored-notice"})
            notice.text = "Audio not restored offline. "
            if href:
                _append_link(notice, "Open local missing-resource note", href)
    shell = document.find(_q("body")); assert shell is not None
    shell = shell.find(_q("div")); assert shell is not None
    _append_footer(shell, record)
    return _serialize(document)


def _serialize(root: ET.Element) -> str:
    body = ET.tostring(root, encoding="unicode", method="xml")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + body + "\n"


READER_CSS = """\
:root { color-scheme: light; font-family: Georgia, 'Times New Roman', serif; background: #eef2f5; color: #1f2933; }
body { margin: 0; background: #eef2f5; line-height: 1.6; }
.reader-shell { max-width: 980px; margin: 0 auto; padding: 1rem 1.25rem 3rem; }
.reader-header, main, .reader-footer { background: #fff; border: 1px solid #cbd5df; box-shadow: 0 2px 8px rgba(31, 41, 51, .08); }
.reader-header { padding: 1.5rem 1.75rem 1rem; border-bottom: 0; }
.reader-kicker { margin: 0; color: #5b6b7a; font: 700 .75rem/1.4 system-ui, sans-serif; letter-spacing: .08em; text-transform: uppercase; }
h1, h2, h3 { color: #16324f; line-height: 1.25; }
h1 { margin: .35rem 0 .5rem; }
h2 { border-bottom: 1px solid #d6dee6; padding-bottom: .3rem; margin-top: 1.8rem; }
.capture-note, .date-note, .late-supplement, .reader-intro { color: #536574; }
.late-supplement { border-left: 4px solid #b26a00; background: #fff6df; padding: .65rem .8rem; }
.archive-nav { display: flex; flex-wrap: wrap; gap: .45rem; align-items: center; padding: .75rem 1.75rem; background: #16324f; font: 600 .9rem/1.4 system-ui, sans-serif; }
.archive-nav a { color: #fff; }
.nav-separator { color: #9bb4c9; }
main { padding: 1.25rem 1.75rem 2rem; }
.transcript-block { border-left: 3px solid #5b86a5; margin: 1rem 0; padding: .8rem 1rem; background: #f7fafc; }
.transcript-paragraph { margin: .25rem 0; }
.speaker { color: #16324f; font-weight: 700; }
.timecode { color: #6b4e71; font: 600 .9rem/1.4 system-ui, sans-serif; }
.unrestored-notice { border-left: 4px solid #8a4b08; background: #fff8ed; padding: .7rem .85rem; }
.unrestored-notice a { font-weight: 700; }
.feed-entry { border-top: 1px solid #d6dee6; padding: .75rem 0 1rem; }
.reader-footer { margin-top: 1rem; padding: .9rem 1.75rem; color: #536574; font: .82rem/1.5 system-ui, sans-serif; }
a { color: #145a8d; }
main a { margin-inline-end: .28rem; }
code { overflow-wrap: anywhere; }
"""


def _generated_file(path: str, data: str, mime: str, records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    return {
        "path": path,
        "data": data,
        "mime": mime,
        "curated_sources": [_source_ref(record) for record in records],
        "bytes": len(data.encode("utf-8")),
    }


def load_blizzcast_bundle(
    map_path: str | Path,
    workspace_root: str | Path,
    base_path: str | Path | None = "",
) -> BlizzcastBundle:
    """Validate accepted local inputs and return five sanitized reader pages.

    ``path`` values in ``generated_files`` and ``origin_routes`` are logical
    site routes.  ``base_path`` is applied only to links inside generated
    documents, leaving the fixed route keys stable for the exporter.
    """

    workspace = Path(workspace_root).resolve()
    source_map_path = _resolve_workspace_path(workspace, map_path)
    base = _normalise_base_path(base_path)
    source_map, roots = _load_inputs(source_map_path, workspace)
    records = source_map["records"]
    origin_routes = {record["original_url"]: ROUTES_BY_ENTITY[record["entity_id"]] for record in records}
    # The homepage is the only source granted directory aliases by contract.
    origin_routes["http://us.blizzard.com/blizzcast"] = ROUTES_BY_ENTITY["BC05"]
    origin_routes["http://us.blizzard.com/blizzcast/"] = ROUTES_BY_ENTITY["BC05"]
    inventory = _extract_inventory(records, roots, base_path=base, origin_routes=origin_routes)
    by_id = {record["entity_id"]: record for record in records}
    generated: list[dict[str, Any]] = []
    generated.append(
        _generated_file(
            ROUTES_BY_ENTITY["BC05"],
            _render_index(by_id["BC05"], roots["BC05"], base_path=base, origin_routes=origin_routes, inventory=inventory),
            "application/xhtml+xml",
            [by_id["BC05"], by_id["BC04"], by_id["BC01"]],
        )
    )
    generated.append(
        _generated_file(
            ROUTES_BY_ENTITY["BC04"],
            _render_archive(by_id["BC04"], roots["BC04"], base_path=base, origin_routes=origin_routes, inventory=inventory),
            "application/xhtml+xml",
            [by_id["BC04"], by_id["BC02"], by_id["BC03"]],
        )
    )
    generated.append(
        _generated_file(
            ROUTES_BY_ENTITY["BC02"],
            _render_episode(by_id["BC02"], roots["BC02"], base_path=base, origin_routes=origin_routes, inventory=inventory),
            "application/xhtml+xml",
            [by_id["BC02"]],
        )
    )
    generated.append(
        _generated_file(
            ROUTES_BY_ENTITY["BC03"],
            _render_episode(by_id["BC03"], roots["BC03"], base_path=base, origin_routes=origin_routes, inventory=inventory),
            "application/xhtml+xml",
            [by_id["BC03"]],
        )
    )
    generated.append(
        _generated_file(
            ROUTES_BY_ENTITY["BC01"],
            _render_feed(by_id["BC01"], roots["BC01"], base_path=base, origin_routes=origin_routes, inventory=inventory),
            "application/xhtml+xml",
            [by_id["BC01"]],
        )
    )
    generated.append(_generated_file(CSS_ROUTE, READER_CSS, "text/css", records))
    return BlizzcastBundle(
        generated_files=generated,
        origin_routes=origin_routes,
        estimated_bytes=sum(item["bytes"] for item in generated),
        dependency_inventory=inventory,
        source_records=[_source_ref(record) for record in records],
        base_path=base,
    )


__all__ = ["BlizzcastBundle", "BlizzcastReaderError", "load_blizzcast_bundle"]
