#!/usr/bin/env python3
"""Extract exact Source15 references for the 51 accepted v36 image overlays.

This is a read-only source-led browser-input preparer.  It scans Source15 text
assets only, matches every accepted original URI or its URL-encoded
missing-image marker exactly, and records line/source hashes and the actual
HTML/CSS context.  It never reads image payloads, performs HTTP, or invents a
news toggle for a static post/CSS reference.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[4]
if ROOT.name != "WOW_Encyclopedia":
    raise RuntimeError(f"unexpected repository root: {ROOT}")
SOURCE_SITE = ROOT / ".scratch/offline-navigation-20261015-v15/site"
OUTPUT = Path(__file__).resolve().parent / "v36-native-ui-inputs.json"
SOURCE_MANIFEST = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
BASE_ORIGIN = "http://www.worldofwarcraft.com"
TEXT_SUFFIXES = {".html", ".htm", ".xml", ".css", ".js", ".txt", ".json"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
VISA_ORIGINALS = {
    "http://www.worldofwarcraft.com/visa/images/credit_back_1.jpg",
    "http://www.worldofwarcraft.com/visa/images/credit_back_2.jpg",
    "http://www.worldofwarcraft.com/visa/images/credit_back_3-2.jpg",
    "http://www.worldofwarcraft.com/visa/images/credit_back_3.jpg",
    "http://www.worldofwarcraft.com/visa/images/title_1.png",
    "http://www.worldofwarcraft.com/visa/images/title_2.png",
}


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
    result = {original, path, path.lstrip("/")}
    for value in (original, path):
        result.add(quote(value, safe=":/"))
        result.add(quote(value, safe="/"))
        result.add(quote(value, safe=""))
        result.add(quote(quote(value, safe=""), safe=""))
    return {item for item in result if item}


class ContextParser(HTMLParser):
    """Record exact image attributes and the actual enclosing news container."""

    def __init__(self, text: str, page: str, target_variants: dict[str, set[str]], variant_to_original: dict[str, str], needle_re: re.Pattern[str]):
        super().__init__(convert_charrefs=True)
        self.text = text
        self.page = page
        self.target_variants = target_variants
        self.variant_to_original = variant_to_original
        self.needle_re = needle_re
        self.stack: list[dict] = []
        self.records: list[dict] = []

    @staticmethod
    def attrs_map(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {str(k).casefold(): html.unescape(v or "") for k, v in attrs}

    def container(self) -> dict:
        for frame in reversed(self.stack):
            if frame.get("kind") in {"news-expand", "news-collapse", "postContainer"}:
                attrs = frame["attrs"]
                return {
                    "kind": frame["kind"],
                    "tag": frame["tag"],
                    "id": attrs.get("id"),
                    "class": attrs.get("class", ""),
                    "toggle": frame["kind"] in {"news-expand", "news-collapse"},
                }
        return {"kind": "none", "toggle": False}

    def add_attr(self, raw: str, attr: str, value: str) -> None:
        value = html.unescape(value)
        found = self.needle_re.search(value)
        original = self.variant_to_original.get(found.group(0)) if found else None
        if original is None:
            # The missing marker's requested query is often encoded separately.
            match = re.search(r"(?:^|[?&])requested=([^&\"']+)", value, flags=re.I)
            original = normalize_requested(match.group(1)) if match else None
            if original not in self.target_variants:
                return
        line, column = self.getpos()
        self.records.append({
            "original": original,
            "source_page": self.page,
            "line": line,
            "column": column,
            "source_line": line_text(self.text, line),
            "raw_reference": raw,
            "match_kind": "missing_image_marker_requested_uri" if "missing-image.svg" in value.lower() or "requested=" in value.lower() else "direct_image_uri",
            "reference_kind": "html_attribute",
            "attribute": attr,
            "container": self.container(),
        })

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        amap = self.attrs_map(attrs)
        raw = self.get_starttag_text() or ""
        classes = set(amap.get("class", "").casefold().split())
        kind = None
        if tag == "div" and "news-expand" in classes:
            kind = "news-expand"
        elif tag == "div" and "news-collapse" in classes:
            kind = "news-collapse"
        elif tag == "div" and "postcontainer" in classes:
            kind = "postContainer"
        if tag in {"img", "source", "input"}:
            for name, value in attrs:
                if value:
                    self.add_attr(raw, name, value)
        frame = {"tag": tag, "attrs": amap, "kind": kind}
        if tag not in VOID_TAGS:
            self.stack.append(frame)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] == tag:
                del self.stack[index:]
                break


def css_property(line: str) -> str | None:
    # Keep the property evidence small and literal; this is not a CSS parser.
    before = line.split("{", 1)[-1]
    match = re.search(r"([\w-]+)\s*:\s*[^;{}]*$", before)
    return match.group(1) if match else None


def line_matches(line: str, original: str, target_variants: dict[str, set[str]]) -> bool:
    if any(item in line for item in target_variants[original]):
        return True
    for match in re.finditer(r"requested=([^&\"')\s]+)", line, flags=re.I):
        if normalize_requested(match.group(1)) == original:
            return True
    return False


def scan_source(targets: list[str]) -> tuple[dict[str, list[dict]], list[dict]]:
    target_variants = {original: variants(original) for original in targets}
    variant_to_original = {variant: original for original in targets for variant in target_variants[original]}
    needle_re = re.compile("|".join(re.escape(value) for value in sorted(variant_to_original, key=len, reverse=True)), flags=re.I)
    hits = {original: [] for original in targets}
    pages: list[dict] = []
    for path in SOURCE_SITE.rglob("*"):
        if not path.is_file() or path.suffix.casefold() not in TEXT_SUFFIXES:
            continue
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        if len(raw) > 20_000_000:
            continue
        text = raw.decode("utf-8", errors="replace")
        relative = path.relative_to(SOURCE_SITE).as_posix()
        page_hash = sha256(raw)
        file_matches = list(needle_re.finditer(text))
        if not file_matches:
            continue
        parser_records: list[dict] = []
        if path.suffix.casefold() in {".html", ".htm", ".xml"}:
            parser = ContextParser(text, relative, target_variants, variant_to_original, needle_re)
            parser.feed(text)
            parser.close()
            parser_records = parser.records
        for original, rows in ((k, [r for r in parser_records if r["original"] == k]) for k in targets):
            for row in rows:
                row = dict(row)
                row["source_page_sha256"] = page_hash
                hits[original].append(row)
        lines = text.splitlines()
        matched_lines = sorted({text.count("\n", 0, match.start()) + 1 for match in file_matches})
        for number in matched_lines:
            line = lines[number - 1] if 0 < number <= len(lines) else ""
            for original in targets:
                if not line_matches(line, original, target_variants):
                    continue
                # HTML img/source records already carry the stronger container evidence.
                if any(r["line"] == number and r["original"] == original for r in hits[original] if r.get("source_page") == relative):
                    continue
                kind = "css_url" if path.suffix.casefold() == ".css" and "url(" in line.casefold() else "script_literal" if path.suffix.casefold() == ".js" else "text_literal"
                marker = "missing-image.svg" in line.casefold() or "requested=" in line.casefold()
                hits[original].append({
                    "original": original,
                    "source_page": relative,
                    "source_page_sha256": page_hash,
                    "line": number,
                    "column": max(0, line.find(urlsplit(original).path)),
                    "source_line": line.strip(),
                    "raw_reference": line.strip(),
                    "match_kind": "missing_image_marker_requested_uri" if marker else "direct_image_uri",
                    "reference_kind": kind,
                    "attribute": "css_url" if kind == "css_url" else None,
                    "property": css_property(line) if kind == "css_url" else None,
                    "container": {"kind": "none", "toggle": False},
                })
        if any(row[0] if False else False for row in []):
            pass
        if any(any(r.get("source_page") == relative for r in rows) for rows in hits.values()):
            pages.append({"path": rel(path), "sha256": page_hash, "bytes": len(raw)})
    return hits, pages


def extract_items(items: list[dict]) -> dict:
    targets = [str(item.get("original") or "") for item in items]
    if len(targets) != 51 or len(set(targets)) != 51:
        raise RuntimeError(f"v36 native input expects 51 unique originals, got {len(targets)}")
    hits, pages = scan_source(targets)
    target_rows: list[dict] = []
    for original in targets:
        refs = hits[original]
        # A CSS sprite may declare the same URL twice; preserve each real source line.
        if not refs:
            raise RuntimeError(f"no exact Source15 reference for {original}")
        refs.sort(key=lambda row: (row["source_page"], int(row["line"]), int(row.get("column", 0))))
        source_pages = sorted({row["source_page"] for row in refs})
        if len(source_pages) != 1:
            raise RuntimeError(f"ambiguous exact Source15 pages for {original}: {source_pages}")
        containers = [row.get("container") or {} for row in refs]
        toggle_ids = sorted({str(c.get("id")) for c in containers if c.get("toggle") and c.get("id")})
        if original in VISA_ORIGINALS:
            display_class = "visa_exhibit_figure"
            derived = {"route": "/visa/index.html", "rendering": "historical_exhibit_figure", "interactive": False}
        elif toggle_ids:
            display_class = "native_news_toggle"
            derived = {"route": source_pages[0], "rendering": "native_news_entry", "interactive": True}
        elif any(r.get("reference_kind") == "css_url" for r in refs):
            display_class = "css_static_reference"
            derived = {"route": source_pages[0], "rendering": "source_css_context", "interactive": False}
        else:
            display_class = "static_source_reference"
            derived = {"route": source_pages[0], "rendering": "source_page_image", "interactive": False}
        target_rows.append({
            "original": original,
            "served_output_path": urlsplit(original).path.lstrip("/"),
            "reference_count": len(refs),
            "references": refs,
            "native_toggle_ids": toggle_ids,
            "display_class": display_class,
            "derived_display": derived,
        })
    classes = {row["display_class"] for row in target_rows}
    return {
        "schema": "wow-recovery.integration.v36-native-ui-inputs.v1",
        "status": "prepared_waiting_root_v36_input_acceptance",
        "source_site_manifest": {"path": rel(SOURCE_MANIFEST), "sha256": sha256(SOURCE_MANIFEST.read_bytes())},
        "source_page_count": len(pages),
        "target_count": len(target_rows),
        "reference_count": sum(row["reference_count"] for row in target_rows),
        "native_toggle_target_count": sum(bool(row["native_toggle_ids"]) for row in target_rows),
        "native_toggle_ids": sorted({control_id for row in target_rows for control_id in row["native_toggle_ids"]}),
        "display_class_counts": {name: sum(row["display_class"] == name for row in target_rows) for name in sorted(classes)},
        "container_policy": "Only actual news-expand/news-collapse ancestors provide native toggle IDs; postContainer and CSS references remain static; Visa six use the accepted historical exhibit figure route.",
        "network_requests": 0,
        "export_executed": False,
        "targets": target_rows,
        "source_pages": pages,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--items", type=Path, required=True, help="v36 primary map containing the 51 new items")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    if args.output.exists():
        raise RuntimeError(f"refusing existing output: {args.output}")
    payload = json.loads(args.items.read_text(encoding="utf-8"))
    items = payload.get("items")
    if not isinstance(items, list):
        raise RuntimeError("v36 primary map has no item list")
    result = extract_items(items)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": rel(args.output), "targets": result["target_count"], "references": result["reference_count"], "native_toggle_ids": result["native_toggle_ids"], "display_class_counts": result["display_class_counts"], "network_requests": 0, "export_executed": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
