#!/usr/bin/env python3
"""Prepare exact Source15 evidence for the v37 browser gate.

The 21 new images are known to be literal missing-image markers on the 2004
news page. This reader parses that page only, records the exact source line and
postContainer context, and adds a separate read-only Toplist page/script/CSS
ledger. It does not make requests, alter the source tree, or infer a toggle.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[4]
if ROOT.name != "WOW_Encyclopedia":
    raise RuntimeError(f"unexpected repository root: {ROOT}")
SOURCE_SITE = ROOT / ".scratch/offline-navigation-20261015-v15/site"
SOURCE_MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
NEWS_PAGE = SOURCE_SITE / "news/wow-news2004.html"
TOPLIST_PAGE = SOURCE_SITE / "toplist/index.html"
TOPLIST_PROTOTYPE = SOURCE_SITE / "toplist/includes-client/js/prototype.js"
TOPLIST_LOGIC = SOURCE_SITE / "toplist/includes-client/js/logic.js"
TOPLIST_CSS = SOURCE_SITE / "toplist/includes-client/css/styles-en.css"
BASE_ORIGIN = "http://www.worldofwarcraft.com"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def line_text(text: str, line: int) -> str:
    rows = text.splitlines()
    return rows[line - 1].strip() if 0 < line <= len(rows) else ""


def normalize_requested(value: str) -> str:
    value = html.unescape(value.strip())
    for _ in range(3):
        decoded = unquote(value)
        if decoded == value:
            break
        value = decoded
    if value.startswith("/"):
        value = BASE_ORIGIN + value
    return value


def variants(original: str) -> set[str]:
    path = urlsplit(original).path
    values = {original, path, path.lstrip("/")}
    for value in (original, path):
        values.update({
            value.replace("/", "%2F"),
            value.replace("/", "%2f"),
            value.replace("/", "%252F"),
        })
    return values


class NewsParser(HTMLParser):
    def __init__(self, text: str, targets: dict[str, set[str]]) -> None:
        super().__init__(convert_charrefs=True)
        self.text = text
        self.targets = targets
        self.reverse = {variant: original for original, values in targets.items() for variant in values}
        self.stack: list[dict[str, object]] = []
        self.records: list[dict[str, object]] = []

    @staticmethod
    def attrs_map(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {str(name).casefold(): html.unescape(value or "") for name, value in attrs}

    def container(self) -> dict[str, object]:
        for frame in reversed(self.stack):
            if frame.get("kind") == "postContainer":
                attrs = frame["attrs"]
                assert isinstance(attrs, dict)
                return {
                    "kind": "postContainer",
                    "tag": frame["tag"],
                    "id": attrs.get("id"),
                    "class": attrs.get("class", ""),
                    "toggle": False,
                }
        return {"kind": "none", "toggle": False}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        amap = self.attrs_map(attrs)
        raw = self.get_starttag_text() or ""
        if tag == "img":
            for name, value in attrs:
                if not value:
                    continue
                value = html.unescape(value)
                requested = re.search(r"(?:^|[?&])requested=([^&\"']+)", value, flags=re.I)
                candidate = normalize_requested(requested.group(1)) if requested else self.reverse.get(value)
                if candidate not in self.targets:
                    continue
                line, column = self.getpos()
                self.records.append({
                    "original": candidate,
                    "source_page": "news/wow-news2004.html",
                    "line": line,
                    "column": column,
                    "source_line": line_text(self.text, line),
                    "raw_reference": raw,
                    "match_kind": "missing_image_marker_requested_uri" if requested else "direct_image_uri",
                    "reference_kind": "html_attribute",
                    "attribute": name,
                    "container": self.container(),
                })
        kind = "postContainer" if tag == "div" and "postcontainer" in amap.get("class", "").casefold().split() else None
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.stack.append({"tag": tag, "attrs": amap, "kind": kind})

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] == tag:
                del self.stack[index:]
                break


def source_binding(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    return {"path": rel(path), "sha256": sha256(raw), "bytes": len(raw)}


def toplist_ledger() -> dict[str, object]:
    page_raw = TOPLIST_PAGE.read_bytes()
    page_text = page_raw.decode("utf-8", errors="replace")
    lines = page_text.splitlines()
    refs = []
    for line_number, needle, purpose in (
        (7, "/toplist/includes-client/js/prototype.js", "prototype script"),
        (56, "/toplist/includes-client/css/styles-en.css", "Toplist stylesheet"),
        (97, "/toplist/includes-client/js/logic.js", "logic script"),
        (312, "window.onload = init", "real init entry"),
        (313, 'className = (topList_conf_vars[0] != "") ? topList_conf_vars[0] : "wide"', "default wide assignment"),
    ):
        if line_number > len(lines) or needle not in lines[line_number - 1]:
            raise RuntimeError(f"Toplist source line changed: {line_number} {needle}")
        refs.append({"line": line_number, "text": lines[line_number - 1].strip(), "purpose": purpose})
    css_raw = TOPLIST_CSS.read_bytes()
    css_lines = css_raw.decode("utf-8", errors="replace").splitlines()
    css_targets = []
    for original, line_numbers, selectors in (
        ("http://www.worldofwarcraft.com/toplist/images/en/next-wide.gif", [55, 57], ["body.wide a.next", "body.wide a.next:hover"]),
        ("http://www.worldofwarcraft.com/toplist/images/en/prev-wide.gif", [56, 58], ["body.wide a.prev", "body.wide a.prev:hover"]),
    ):
        rows = []
        for line_number, selector in zip(line_numbers, selectors):
            if line_number > len(css_lines) or original.rsplit("/", 1)[-1] not in css_lines[line_number - 1]:
                raise RuntimeError(f"Toplist CSS source line changed: {line_number} {original}")
            rows.append({"line": line_number, "selector": selector, "source_line": css_lines[line_number - 1].strip()})
        css_targets.append({"original": original, "source_page": "toplist/includes-client/css/styles-en.css", "source_page_sha256": sha256(css_raw), "references": rows, "status": "pending_real_visible_wide_entry"})
    return {
        "route": "toplist/index.html",
        "source_page": source_binding(TOPLIST_PAGE),
        "source_references": refs,
        "scripts": [
            {"route": "toplist/includes-client/js/prototype.js", "source": source_binding(TOPLIST_PROTOTYPE), "expected": "Node syntax and byte-preserving Prototype guard; no generic rewrite"},
            {"route": "toplist/includes-client/js/logic.js", "source": source_binding(TOPLIST_LOGIC), "expected": "Node syntax and five local pixel substitutions"},
        ],
        "css_targets": css_targets,
        "execution_policy": "Only count next/previous CSS backgrounds after a real body.wide Toplist entry exposes a visible matching element; do not count the commented lion-top declaration or a CSS declaration alone.",
    }


def extract_items(items: list[dict]) -> dict[str, object]:
    if len(items) != 21 or len({str(item.get("original") or "") for item in items}) != 21:
        raise RuntimeError(f"v37 native input expects 21 unique originals, got {len(items)}")
    if not SOURCE_MANIFEST.is_file() or not NEWS_PAGE.is_file():
        raise RuntimeError("missing frozen Source15 manifest or news source page")
    raw = NEWS_PAGE.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    targets = {str(item["original"]): variants(str(item["original"])) for item in items}
    parser = NewsParser(text, targets)
    parser.feed(text)
    parser.close()
    target_rows = []
    for item in items:
        original = str(item["original"])
        rows = [row for row in parser.records if row["original"] == original]
        if len(rows) != 1:
            raise RuntimeError(f"expected one exact Source15 news reference for {original}, got {len(rows)}")
        row = dict(rows[0])
        row["source_page_sha256"] = sha256(raw)
        target_rows.append({
            "original": original,
            "served_output_path": urlsplit(original).path.lstrip("/"),
            "length": int(item["length"]),
            "mime": item.get("mime"),
            "dimensions": item.get("dimensions"),
            "reference_count": 1,
            "references": [row],
            "native_toggle_ids": [],
            "display_class": "static_news_postcontainer",
            "derived_display": {"route": "news/wow-news2004.html", "rendering": "postContainer_image", "interactive": False},
            "status": "pending_root_browser_go",
        })
    return {
        "schema": "wow-recovery.integration.v37-native-ui-inputs.v1",
        "status": "prepared_waiting_root_v37_browser_go",
        "source_site_manifest": source_binding(SOURCE_MANIFEST),
        "source_pages": [source_binding(NEWS_PAGE)],
        "target_count": len(target_rows),
        "reference_count": len(target_rows),
        "native_toggle_target_count": 0,
        "display_class_counts": {"static_news_postcontainer": len(target_rows)},
        "container_policy": "The 21 accepted originals have exact Source15 postContainer image references and no native toggle IDs. The Toplist ledger is separate and only promotes real body.wide visibility.",
        "network_requests": 0,
        "export_executed": False,
        "targets": target_rows,
        "toplist": toplist_ledger(),
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--items", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.items.read_text(encoding="utf-8"))
    result = extract_items(payload.get("items") or [])
    if args.output.exists():
        raise RuntimeError(f"refusing existing output: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": rel(args.output), "targets": result["target_count"], "references": result["reference_count"], "toplist_css_targets": len(result["toplist"]["css_targets"]), "network_requests": 0, "export_executed": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
