"""Render one pinned official contest record as a static historical exhibit."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import html
import json
from pathlib import Path
import re
from typing import Any

MAP_RELATIVE = "artifacts/official-contest-results-20261025/article.json"
MAP_SHA256 = "450d4e839c794222af6bdd94b7cc2b4dd23416339bd15c28f864d3bf3cff7a76"
MANIFEST_SHA256 = "e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a"
READER_ROUTE = "/contests/06-10-costume/winners.html"
SOURCE_ROUTE = "/__offline/official-features/costume-2006-source.json"

class OfficialContestError(ValueError):
    pass

@dataclass(frozen=True)
class OfficialContestBundle:
    generated_files: tuple[dict[str, Any], ...]
    origin_routes: dict[str, str]
    source_record: dict[str, Any]
    estimated_bytes: int
    map_sha256: str

def _render(data: dict[str, Any], base: str) -> bytes:
    esc = lambda value: html.escape(str(value), quote=True)
    article = data["article"]
    cards = ''.join(
        '<li><h2>' + esc(winner["work"]) + '</h2><p>Submitted by '
        + esc(winner["submitter"]) + '</p><p class="missing">Photograph not yet recovered.</p></li>'
        for winner in data["winners"]
    )
    capture = data["source"]["capture_timestamp"]
    date = capture[:4] + '-' + capture[4:6] + '-' + capture[6:8]
    document = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>{esc(article["title"])} (2006) | WoW Archive</title>
<style>html{{background:#15100b;color:#e8dec5;font:17px/1.65 Georgia,serif}}body{{max-width:900px;margin:0 auto;padding:24px}}a{{color:#ffd376}}nav,.kicker,.source{{font:14px/1.6 Arial,sans-serif}}h1,h2{{color:#ffd376;line-height:1.3}}h1{{font-size:2.1rem}}h2{{font-size:1.2rem}}blockquote{{margin:24px 0;padding:16px 22px;border-left:3px solid #94713e;background:#21180f}}ol{{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}}li{{padding:18px;border:1px solid #6e5835;background:#23180e}}li p{{margin-bottom:0}}.missing,.source{{color:#ccbea2}}footer{{margin-top:32px;border-top:1px solid #6e5835;padding-top:18px}}.kicker{{margin-top:32px}}</style></head>
<body><nav><a href="{esc(base)}">Archive home</a> · <a href="{esc(base)}news/rss-10-2006.xml.html">October 2006 news</a></nav>
<p class="kicker">Historical exhibit · 2006 contest results · Unaffiliated archive</p>
<h1>{esc(article["title"])}</h1><p class="source">Official page preserved in Common Crawl, capture {date}.</p>
<blockquote>{esc(article["intro"])}</blockquote><ol>{cards}</ol>
<h2>Honorable mentions</h2><blockquote>{esc(article["honorable_mentions"])}</blockquote>
<p class="missing">Photographs from this gallery have not yet been recovered.</p>
<footer><a href="{esc(base + SOURCE_ROUTE.lstrip('/'))}">Source details</a></footer></body></html>'''
    return document.encode("utf-8")

def load_official_contest_bundle(map_path: str | Path, workspace_root: str | Path,
                                 base_path: str, source_manifest_sha256: str) -> OfficialContestBundle:
    root = Path(workspace_root).resolve()
    path = Path(map_path)
    if not path.is_absolute():
        path = root / path
    if path.is_symlink() or path.resolve() != (root / MAP_RELATIVE).resolve():
        raise OfficialContestError("official contest input path is not the accepted profile")
    for parent in (path, *path.parents):
        if parent == root.parent:
            break
        if parent.is_symlink() or getattr(parent.lstat(), "st_file_attributes", 0) & 0x400:
            raise OfficialContestError("official contest input contains a reparse point")
    if path.stat().st_size > 16384:
        raise OfficialContestError("official contest input exceeds its source-data bound")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != MAP_SHA256:
        raise OfficialContestError("official contest source SHA-256 differs from acceptance")
    data = json.loads(raw)
    if source_manifest_sha256 != MANIFEST_SHA256 or data["source_manifest_sha256"] != MANIFEST_SHA256:
        raise OfficialContestError("official contest Source16 manifest guard mismatch")
    if data["schema"] != "wow-official-contest-reading/v1" or len(data["winners"]) != 5 or data["image_bytes_recovered"] != 0:
        raise OfficialContestError("official contest source scope mismatch")
    base = base_path.rstrip('/') + '/'
    if not re.fullmatch(r"/(?:[A-Za-z0-9_.~-]+/)*", base) or any(part in ('.', '..') for part in base.split('/')):
        raise OfficialContestError("official contest base path is unsafe")
    source_record = {**data["source"], "classification": data["classification"],
                     "article_input_sha256": MAP_SHA256, "image_bytes_recovered": 0}
    files = []
    for route, payload, mime in (
        (READER_ROUTE, _render(data, base), "text/html; charset=UTF-8"),
        (SOURCE_ROUTE, raw, "application/json; charset=UTF-8"),
    ):
        files.append({"path": route, "data": payload, "bytes": len(payload),
                      "sha256": hashlib.sha256(payload).hexdigest(), "mime": mime})
    origins = {"http://www.worldofwarcraft.com" + route: READER_ROUTE for route in data["original_routes"]}
    return OfficialContestBundle(tuple(files), origins, source_record,
                                 sum(item["bytes"] for item in files), MAP_SHA256)
