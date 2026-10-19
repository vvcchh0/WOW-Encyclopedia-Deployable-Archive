#!/usr/bin/env python3
"""Extract source-page evidence for v35's newly accepted news images.

This is a read-only preparation helper.  It searches only the frozen Source15
HTML/XML/CSS/JS text files for each literal accepted image URL/path and records
the real page, line, snippet, and page SHA.  News pages additionally expose
the native ``news-expand``/``news-collapse`` ids found in the same source
file.  It never downloads, rewrites, or hashes image payloads.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[4]
SOURCE_SITE = ROOT / ".scratch/offline-navigation-20261015-v15/site"
R7_INPUT = ROOT / "research/continuous-recovery-20261018/integration/v33/browser/v33-browser-input-r7.json"
OUTPUT = Path(__file__).resolve().parent / "v35-native-ui-inputs.json"
TEXT_SUFFIXES = {".html", ".htm", ".xml", ".css", ".js", ".txt"}
IMAGE_SUFFIXES = (".gif", ".jpg", ".jpeg", ".png", ".webp", ".svg")
TAG_RE = re.compile(r"<(?P<tag>[A-Za-z][\w:-]*)(?P<attrs>[^>]*)>", re.I | re.S)
ATTR_RE = re.compile(r"(?P<name>[A-Za-z_:][\w:.-]*)\s*=\s*(?P<quote>[\"'])(?P<value>.*?)\2", re.I | re.S)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def snippets(text: str, needle: str) -> list[dict]:
    rows: list[dict] = []
    start = 0
    lowered = text.casefold()
    wanted = needle.casefold()
    while True:
        index = lowered.find(wanted, start)
        if index < 0:
            return rows
        line = line_number(text, index)
        begin = text.rfind("\n", 0, index) + 1
        end = text.find("\n", index)
        if end < 0:
            end = len(text)
        rows.append({"line": line, "literal": text[begin:end].strip()[:1000]})
        start = index + max(1, len(needle))


def native_controls(text: str) -> list[dict]:
    controls: list[dict] = []
    for match in TAG_RE.finditer(text):
        raw = match.group(0)
        if not re.search(r"news-(?:expand|collapse)", raw, re.I):
            continue
        attrs = {m.group("name").casefold(): html.unescape(m.group("value")) for m in ATTR_RE.finditer(match.group("attrs"))}
        control_id = attrs.get("id")
        classes = attrs.get("class", "")
        if not control_id or not re.search(r"news-(?:expand|collapse)", classes, re.I):
            continue
        controls.append({
            "tag": match.group("tag").lower(),
            "id": control_id,
            "class": classes,
            "line": line_number(text, match.start()),
        })
    unique: dict[str, dict] = {}
    for row in controls:
        unique.setdefault(row["id"], row)
    return list(unique.values())


def load_items(map_path: Path) -> list[dict]:
    payload = json.loads(map_path.read_text(encoding="utf-8"))
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        raise RuntimeError(f"map has no items: {map_path}")
    return items


def extract_items(items: list[dict], *, source_site: Path = SOURCE_SITE, prior_input: Path = R7_INPUT) -> dict:
    if not source_site.is_dir():
        raise RuntimeError(f"missing frozen Source15 site: {source_site}")
    if not prior_input.is_file():
        raise RuntimeError(f"missing v33 r7 browser input: {prior_input}")
    candidates = [p for p in source_site.rglob("*") if p.is_file() and p.suffix.casefold() in TEXT_SUFFIXES]
    targets: list[dict] = []
    for item in items:
        original = str(item.get("original") or item.get("logical_url") or "")
        parsed = urlsplit(original)
        path = parsed.path.lstrip("/")
        if not path or not path.casefold().endswith(IMAGE_SUFFIXES):
            raise RuntimeError(f"new v35 item is not a literal raster URL: {original}")
        matches: list[dict] = []
        # Full relative paths are authoritative.  A basename-only fallback is
        # deliberately omitted to avoid claiming an unrelated same-name image.
        for page in candidates:
            try:
                text = page.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            found = snippets(text, path)
            if not found:
                found = snippets(text, "/" + path)
            if not found:
                continue
            page_route = page.relative_to(source_site).as_posix()
            rows = [{"page": page_route, "page_sha256": sha256_file(page), **hit} for hit in found]
            controls = native_controls(text) if page_route.casefold().startswith("news/") else []
            matches.append({"source_page": page_route, "source_page_sha256": sha256_file(page), "references": rows, "native_news_controls": controls})
        targets.append({
            "original": original,
            "served_output_path": str(item.get("original") or "").split("/", 3)[-1],
            "actual_timestamp": item.get("actual_timestamp"),
            "reference_pages": matches,
            "reference_count": sum(len(group["references"]) for group in matches),
            "native_toggle_ids": sorted({control["id"] for group in matches for control in group["native_news_controls"]}),
        })
    prior = json.loads(prior_input.read_text(encoding="utf-8"))
    return {
        "schema": "wow-recovery.integration.v35-native-ui-inputs.v1",
        "status": "prepared_waiting_root_v35_input_acceptance",
        "source_site": {"path": rel(source_site), "sha256": sha256_file(source_site / "../build-manifest.json") if (source_site / "../build-manifest.json").is_file() else None},
        "prior_browser_input_r7": {"path": rel(prior_input), "sha256": sha256_file(prior_input)},
        "new_image_count": len(items),
        "targets": targets,
        "native_controls_scope": "Only exact news-expand/news-collapse controls in the actual source page containing a literal accepted image reference are recorded; no hidden DOM is invented.",
        "network_requests": 0,
        "export_executed": False,
        "prior_r7_counts": prior.get("counts"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    if args.output.exists():
        raise RuntimeError(f"refusing existing output: {args.output}")
    payload = extract_items(load_items(args.map))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": rel(args.output), "new_image_count": payload["new_image_count"], "reference_count": sum(item["reference_count"] for item in payload["targets"]), "network_requests": 0, "export_executed": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
