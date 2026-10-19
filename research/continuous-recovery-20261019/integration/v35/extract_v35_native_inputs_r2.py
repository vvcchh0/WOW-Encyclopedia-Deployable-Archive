#!/usr/bin/env python3
"""Prepare the bounded v35 native-image evidence revision.

R1 searched Source15 text for the literal image path and therefore missed the
23 news images represented by an exact ``missing-image.svg`` marker whose
``requested`` query value is percent-encoded.  R2 deliberately reads only the
two Source15 pages already bound by the accepted frontier input: the static
2004 news archive and the 2007-10 news page containing the Beowulf entry.
It matches the accepted original URI exactly, records the source line/hash and
the real enclosing news container, and never rewrites, downloads, or hashes
image payloads.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


ROOT = Path(__file__).resolve().parents[4]
if ROOT.name != "WOW_Encyclopedia":
    raise RuntimeError(f"unexpected repository root: {ROOT}")
SOURCE_SITE = ROOT / ".scratch/offline-navigation-20261015-v15/site"
PRIMARY_MAP = ROOT / "research/continuous-recovery-20261019/integration/v35/v35-primary-source-map.json"
OUTPUT = Path(__file__).resolve().parent / "v35-native-ui-inputs-r2.json"
BASE_ORIGIN = "http://www.worldofwarcraft.com"
SOURCE_PAGES = (
    ("news/wow-news2004.html", "static_2004_news_archive"),
    ("news/rss-10-2007.xml", "native_news_entry"),
)
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def line_text(text: str, line: int) -> str:
    rows = text.splitlines()
    return rows[line - 1].strip() if 0 < line <= len(rows) else ""


@dataclass
class Frame:
    tag: str
    attrs: dict[str, str]
    kind: str | None = None
    title: str | None = None


@dataclass
class Heading:
    text: list[str] = field(default_factory=list)


class SourceParser(HTMLParser):
    """Parse only enough HTML structure to identify image and news ancestors."""

    def __init__(self, text: str, page_route: str):
        super().__init__(convert_charrefs=True)
        self.text = text
        self.page_route = page_route
        self.stack: list[Frame] = []
        self.heading_stack: list[Heading] = []
        self.matches: list[dict] = []

    def _attrs(self, attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {name.casefold(): html.unescape(value or "") for name, value in attrs}

    def _container_frame(self) -> Frame | None:
        for frame in reversed(self.stack):
            if frame.kind in {"news-expand", "news-collapse", "postContainer"}:
                return frame
        return None

    def _position(self) -> tuple[int, int]:
        line, col = self.getpos()
        return line, col

    def _source_literal(self, line: int) -> str:
        return line_text(self.text, line)

    def _container_payload(self, frame: Frame | None) -> dict:
        if frame is None:
            return {"kind": "none", "toggle": False, "reason": "no_news_container_ancestor"}
        attrs = frame.attrs
        return {
            "kind": frame.kind,
            "tag": frame.tag,
            "id": attrs.get("id"),
            "class": attrs.get("class", ""),
            "title": frame.title,
            "toggle": frame.kind in {"news-expand", "news-collapse"},
        }

    def _record_image(self, attrs: dict[str, str], raw: str) -> None:
        src = html.unescape(attrs.get("src", ""))
        if not src:
            return
        line, col = self._position()
        requested: str | None = None
        match_kind: str | None = None
        marker_src: str | None = None
        parsed = urlsplit(src)
        if parsed.path.rstrip("/").casefold() == "/__offline/missing-image.svg":
            query = parse_qs(parsed.query, keep_blank_values=True)
            values = query.get("requested", [])
            if len(values) == 1:
                requested = html.unescape(values[0])
                marker_src = src
                match_kind = "missing_image_marker_requested_uri"
        elif src.startswith("http://") or src.startswith("https://"):
            requested = src
            match_kind = "direct_image_uri"
        elif src.startswith("/"):
            requested = BASE_ORIGIN + src
            match_kind = "direct_image_uri"
        if requested is None:
            return
        self.matches.append({
            "requested": requested,
            "match_kind": match_kind,
            "marker_src": marker_src,
            "line": line,
            "column": col,
            "source_line": self._source_literal(line),
            "raw_tag": raw,
            "container": self._container_payload(self._container_frame()),
        })

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        attrs_map = self._attrs(attrs)
        raw = self.get_starttag_text() or ""
        classes = attrs_map.get("class", "")
        kind: str | None = None
        if tag == "div" and "news-expand" in classes.casefold().split():
            kind = "news-expand"
        elif tag == "div" and "news-collapse" in classes.casefold().split():
            kind = "news-collapse"
        elif tag == "div" and "postcontainer" in classes.casefold().split():
            kind = "postContainer"
        frame = Frame(tag=tag, attrs=attrs_map, kind=kind)
        if tag == "h3" and "title" in classes.casefold().split():
            self.heading_stack.append(Heading())
        if tag == "img":
            self._record_image(attrs_map, raw)
        if tag not in VOID_TAGS:
            self.stack.append(frame)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_data(self, data: str) -> None:
        if self.heading_stack:
            self.heading_stack[-1].text.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if tag == "h3" and self.heading_stack:
            heading = self.heading_stack.pop()
            title = " ".join(" ".join(heading.text).split())
            for frame in reversed(self.stack):
                if frame.kind == "postContainer":
                    frame.title = title
                    break
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break


def load_items() -> list[dict]:
    payload = json.loads(PRIMARY_MAP.read_text(encoding="utf-8"))
    items = payload.get("items")
    if not isinstance(items, list) or len(items) != 24:
        raise RuntimeError(f"expected 24 v35 primary items, got {len(items) if isinstance(items, list) else None}")
    return items


def extract(items: list[dict]) -> dict:
    pages: list[dict] = []
    all_matches: list[dict] = []
    for relative, role in SOURCE_PAGES:
        path = SOURCE_SITE / relative
        if not path.is_file():
            raise RuntimeError(f"missing bound Source15 page: {path}")
        text = path.read_text(encoding="utf-8", errors="replace")
        parser = SourceParser(text, relative)
        parser.feed(text)
        parser.close()
        for match in parser.matches:
            match["source_page"] = relative
            match["source_page_sha256"] = sha256_file(path)
        all_matches.extend(parser.matches)
        pages.append({
            "path": rel(path),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
            "role": role,
            "literal_scan_only": True,
        })

    targets: list[dict] = []
    for item in items:
        original = str(item.get("original") or "")
        matches = [row for row in all_matches if row["requested"] == original]
        if len(matches) != 1:
            raise RuntimeError(f"expected exactly one exact R2 source match for {original}, got {len(matches)}")
        row = dict(matches[0])
        row.pop("requested", None)
        targets.append({
            "original": original,
            "served_output_path": urlsplit(original).path.lstrip("/"),
            "reference_count": 1,
            "references": [row],
            "native_toggle_ids": [row["container"]["id"]] if row["container"]["toggle"] and row["container"].get("id") else [],
            "display_class": "native_news_toggle" if row["container"]["toggle"] else "postContainer_static_no_toggle",
        })

    marker_count = sum(1 for target in targets if target["references"][0]["match_kind"] == "missing_image_marker_requested_uri")
    direct_count = len(targets) - marker_count
    toggle_targets = [target for target in targets if target["native_toggle_ids"]]
    static_targets = [target for target in targets if not target["native_toggle_ids"]]
    if marker_count != 23 or direct_count != 1 or len(toggle_targets) != 1 or len(static_targets) != 23:
        raise RuntimeError(f"unexpected R2 classification: markers={marker_count}, direct={direct_count}, toggles={len(toggle_targets)}, static={len(static_targets)}")
    return {
        "schema": "wow-recovery.integration.v35-native-ui-inputs-r2.v1",
        "status": "prepared_waiting_root_v35_input_acceptance",
        "revision_of": {"path": rel(Path(__file__).with_name("v35-native-ui-inputs.json")), "sha256": sha256_file(Path(__file__).with_name("v35-native-ui-inputs.json"))},
        "primary_map": {"path": rel(PRIMARY_MAP), "sha256": sha256_file(PRIMARY_MAP)},
        "source_site_manifest": {"path": ".scratch/offline-navigation-20261015-v15/build-manifest.json", "sha256": sha256_file(ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json")},
        "source_pages": pages,
        "source_page_count": len(pages),
        "target_count": len(targets),
        "reference_count": sum(target["reference_count"] for target in targets),
        "missing_marker_reference_count": marker_count,
        "direct_reference_count": direct_count,
        "native_toggle_target_count": len(toggle_targets),
        "static_postcontainer_target_count": len(static_targets),
        "native_toggle_ids": sorted({control_id for target in targets for control_id in target["native_toggle_ids"]}),
        "container_policy": "news-expand/news-collapse is a native toggle; 2004 postContainer is a static article display with no invented toggle.",
        "network_requests": 0,
        "export_executed": False,
        "targets": targets,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    if args.output.exists():
        raise RuntimeError(f"refusing existing output: {args.output}")
    payload = extract(load_items())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({
        "output": rel(args.output),
        "targets": payload["target_count"],
        "references": payload["reference_count"],
        "missing_marker_references": payload["missing_marker_reference_count"],
        "direct_references": payload["direct_reference_count"],
        "native_toggle_ids": payload["native_toggle_ids"],
        "network_requests": 0,
        "export_executed": False,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
