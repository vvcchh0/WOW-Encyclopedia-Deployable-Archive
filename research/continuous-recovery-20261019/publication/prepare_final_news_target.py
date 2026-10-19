"""Cite the actual collapsed news entry for one remaining v33 UI check."""
from __future__ import annotations

import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "research/continuous-recovery-20261019/local-audit/browser"
SITE = ROOT / ".scratch/pages-resources-20261018-v33"
PAGE = "news/rss-02-2008.xml.html"
ORIGINAL = "http://www.worldofwarcraft.com/news/images/08-02/02-06-08-3.jpg"
IMAGE_PATH = "/WOW-Encyclopedia-Deployable-Archive/news/images/08-02/02-06-08-3.jpg"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class CitationParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.matches = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "img" and attributes.get("src") == IMAGE_PATH:
            entries = [item for item in self.stack if item[0] == "div" and
                       any(c.startswith(("news-expand", "news-collapse")) for c in (item[1].get("class") or "").split())]
            assert entries and entries[-1][1].get("id")
            self.matches.append({"entry_id": entries[-1][1]["id"], "image_line": self.getpos()[0]})
        if tag not in VOID:
            self.stack.append((tag, attributes))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                self.stack = self.stack[:i]
                break


if __name__ == "__main__":
    prior = AUDIT / "v33-ui-audit-input-r7.json"
    data = json.loads(prior.read_bytes())
    rows = [r for r in data["source_references"]["static_render_targets"] if r["original"] == ORIGINAL]
    assert len(rows) == 1 and rows[0]["page_output"] == PAGE
    parser = CitationParser()
    parser.feed((SITE / PAGE).read_text(encoding="utf-8"))
    assert len(parser.matches) == 1
    citation = parser.matches[0]
    assert citation["image_line"] == rows[0]["source_line"]
    data["source_references"] = {"ordinary_image_hrefs": [], "static_render_targets": rows}
    data["news_toggle_ids"] = {PAGE: [citation["entry_id"]]}
    data["counts"] = {"total_static": 1, "remaining_static": 1}
    data["scope_note"] = "One explicitly cited subset of frozen r7; add missing native news toggle citation, without changing site or original row."
    data["root_subset_binding"] = {"parent": prior.relative_to(ROOT).as_posix(),
        "parent_sha256": hashlib.sha256(prior.read_bytes()).hexdigest(),
        "page": (SITE / PAGE).relative_to(ROOT).as_posix(),
        "page_sha256": hashlib.sha256((SITE / PAGE).read_bytes()).hexdigest(), **citation}
    target = AUDIT / "v33-ui-final-news-target-input-r8.json"
    assert not target.exists()
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data["root_subset_binding"]))
