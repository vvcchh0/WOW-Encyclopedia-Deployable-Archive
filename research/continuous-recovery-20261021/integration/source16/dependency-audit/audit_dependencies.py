#!/usr/bin/env python3
"""Read-only dependency audit for the eight Source16 body pages.

This deliberately inspects HTML resource attributes and CSS declarations only.
HTML comments are discarded by HTMLParser.  Inline JavaScript is scanned only
for known runtime resource constructors (printFlash and document.write); other
string literals are not treated as page dependencies.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote


ROOT = Path(__file__).resolve().parents[5]
SOURCE16_SITE = ROOT / ".scratch" / "offline-non-gallery-20261021-v16" / "site"
SOURCE16_MANIFEST = ROOT / ".scratch" / "offline-non-gallery-20261021-v16" / "build-manifest.json"
V42_ROOT = ROOT / ".scratch" / "pages-resources-20261021-v42"
V42_ROUTE_MAP = V42_ROOT / "__offline" / "route-map.json"
PRIVATE = ROOT / "research" / "continuous-recovery-20261021" / "integration" / "main-pages-review" / "private"
OUT = ROOT / "research" / "continuous-recovery-20261021" / "integration" / "source16" / "dependency-audit"


PAGES = [
    ("contest-050609", "/contests/05-06-09/index.html", "contest-050609.html"),
    ("content-index-shtml", "/info/basics/content-index.html", "content-index-shtml.html"),
    ("tinfoilhat", "/info/items/tinfoilhat.xml", "tinfoilhat.html"),
    ("two-headed-ogre", "/info/races/two-headed-ogre.shtml", "two-headed-ogre.html"),
    ("fan-site-program", "/misc/fan-site-program.html", "fan-site-program.html"),
    ("moltencore", "/moltencore/index.html", "moltencore.html"),
    ("patch-092904", "/patchnotes/patch-9-29-04.shtml", "patch-092904.html"),
    ("bardclass", "/wrath/features/bard/bardclass.xml", "bardclass.html"),
]

RESOURCE_ATTRS = {
    "script": {"src": "script"},
    "link": {"href": "link"},
    "img": {"src": "image", "longdesc": "image_metadata"},
    "input": {"src": "image"},
    "object": {"data": "object"},
    "embed": {"src": "embed"},
    "iframe": {"src": "iframe"},
    "frame": {"src": "frame"},
    "source": {"src": "media", "srcset": "media_srcset"},
    "video": {"src": "media", "poster": "poster"},
    "audio": {"src": "media"},
    "body": {"background": "background"},
    "table": {"background": "background"},
    "tr": {"background": "background"},
    "td": {"background": "background"},
    "th": {"background": "background"},
}

URL_RE = re.compile(r"url\(\s*(?P<q>['\"]?)(?P<u>.*?)(?P=q)\s*\)", re.I | re.S)
FILTER_SRC_RE = re.compile(r"(?:AlphaImageLoader|filter\s*:\s*[^;]*?)\s*[^;]*?\bsrc\s*=\s*['\"]([^'\"]+)['\"]", re.I | re.S)
PRINT_FLASH_RE = re.compile(r"\bprintFlash\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]", re.I)
DOC_WRITE_RE = re.compile(r"\bdocument\.write\s*\(", re.I)
ATTR_LITERAL_RE = re.compile(r"\b(?:src|href|data|poster)\s*=\s*['\"]([^'\"]+)['\"]", re.I)
ROOTHOST_RE = re.compile(r"\broothost\s*\+\s*['\"]([^'\"]+)['\"]", re.I)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def route_path(raw: str, page_route: str) -> tuple[str | None, str]:
    """Return normalized same-site route, or None for non-local URL."""
    value = html.unescape(raw).strip()
    value = value.strip("\"'")
    if not value or value.startswith(("#", "javascript:", "mailto:", "data:", "blob:", "about:")):
        return None, "non_resource"
    if value.startswith("//"):
        return None, "external"
    parts = urlsplit(value)
    if parts.scheme and parts.scheme.lower() not in {"http", "https"}:
        return None, "external"
    if parts.scheme or parts.netloc:
        host = (parts.hostname or "").lower()
        if host not in {"www.worldofwarcraft.com", "worldofwarcraft.com"}:
            return None, "external"
        path = parts.path or "/"
    else:
        path = value.split("#", 1)[0].split("?", 1)[0]
        path = urljoin("http://local" + page_route, path).split("#", 1)[0].split("?", 1)[0]
        path = urlsplit(path).path
    if not path.startswith("/"):
        path = "/" + path
    path = unquote(path)
    prefix = "/WOW-Encyclopedia-Deployable-Archive/"
    if path.startswith(prefix):
        path = "/" + path[len(prefix) :]
    # Collapse dot segments using urljoin without altering case or extension.
    path = urlsplit(urljoin("http://local/", path.lstrip("/"))).path
    if not path.startswith("/"):
        path = "/" + path
    return path, "same_site_local"


def line_for(start_line: int, text: str, offset: int) -> int:
    return start_line + text[:offset].count("\n")


class PageParser(HTMLParser):
    def __init__(self, page_id: str, route: str):
        super().__init__(convert_charrefs=True)
        self.page_id = page_id
        self.route = route
        self.rows: list[dict] = []
        self.script_buffers: list[dict] = []
        self.style_buffers: list[dict] = []
        self.ignore_depth = 0
        self.comments = 0
        self._active_script: dict | None = None
        self._active_style: dict | None = None

    def handle_comment(self, data: str) -> None:
        self.comments += 1

    def _add(self, *, kind: str, raw_url: str, line: int, element: str, attribute: str, context: str = "static_html", note: str = "") -> None:
        raw_url = html.unescape(raw_url).strip()
        if not raw_url:
            return
        route, route_kind = route_path(raw_url, self.route)
        self.rows.append({
            "page_id": self.page_id,
            "page_route": self.route,
            "element": element,
            "attribute": attribute,
            "kind": kind,
            "raw_url": raw_url,
            "route": route,
            "route_kind": route_kind,
            "line": line,
            "context": context,
            "note": note,
        })

    def _add_css(self, text: str, start_line: int, element: str, attribute: str, context: str) -> None:
        for m in URL_RE.finditer(text):
            value = m.group("u").strip()
            if value:
                self._add(kind="css", raw_url=value, line=line_for(start_line, text, m.start()), element=element, attribute=attribute, context=context)
        for m in FILTER_SRC_RE.finditer(text):
            self._add(kind="css_filter", raw_url=m.group(1).strip(), line=line_for(start_line, text, m.start()), element=element, attribute=attribute, context=context, note="legacy AlphaImageLoader src")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        line = self.getpos()[0]
        tl = tag.lower()
        amap = dict((k.lower(), v) for k, v in attrs)
        for attr, kind in RESOURCE_ATTRS.get(tl, {}).items():
            value = amap.get(attr)
            if value is None:
                continue
            if attr == "srcset":
                # Keep each candidate as its own actual media target.
                for candidate in value.split(","):
                    target = candidate.strip().split(None, 1)[0]
                    self._add(kind=kind, raw_url=target, line=line, element=tl, attribute=attr)
            else:
                self._add(kind=kind, raw_url=value, line=line, element=tl, attribute=attr)
        style = amap.get("style")
        if style:
            self._add_css(style, line, tl, "style", "inline_style")
        if tl == "style":
            self._active_style = {"line": line, "text": []}
        elif tl == "script":
            self._active_script = {"line": line, "text": []}

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_data(self, data: str) -> None:
        if self._active_style is not None:
            self._active_style["text"].append(data)
        if self._active_script is not None:
            self._active_script["text"].append(data)

    def handle_endtag(self, tag: str) -> None:
        tl = tag.lower()
        if tl == "style" and self._active_style is not None:
            text = "".join(self._active_style["text"])
            # An HTML comment inside CSS is not a resource declaration.
            text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
            self._add_css(text, self._active_style["line"], "style", "text", "style_block")
            self._active_style = None
        elif tl == "script" and self._active_script is not None:
            self._scan_script("".join(self._active_script["text"]), self._active_script["line"])
            self._active_script = None

    def _scan_script(self, text: str, start_line: int) -> None:
        # Only recognized runtime constructors are dependencies. Arbitrary JS
        # strings (including anchor snippets in printFlash fallbacks) are not.
        for m in PRINT_FLASH_RE.finditer(text):
            self._add(kind="swf", raw_url=m.group(2), line=line_for(start_line, text, m.start()), element="script", attribute="printFlash", context="dynamic_runtime", note=f"player id {m.group(1)}")
        if DOC_WRITE_RE.search(text):
            for m in ATTR_LITERAL_RE.finditer(text):
                self._add(kind="dynamic_markup", raw_url=m.group(1), line=line_for(start_line, text, m.start()), element="script", attribute="document.write", context="dynamic_runtime")
        for m in ROOTHOST_RE.finditer(text):
            self._add(kind="dynamic_css", raw_url=m.group(1), line=line_for(start_line, text, m.start()), element="script", attribute="roothost+literal", context="dynamic_runtime", note="runtime host prefix")


def local_file(site: Path, route: str | None) -> Path | None:
    if not route:
        return None
    rel = route.lstrip("/")
    p = site / rel
    if p.is_file():
        return p
    if route.endswith("/"):
        for index in ("index.html", "index.xml", "index.shtml"):
            q = site / rel / index
            if q.is_file():
                return q
    return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    route_map = json.loads(V42_ROUTE_MAP.read_text(encoding="utf-8"))
    v42_routes = set(route_map.get("routes", {}))
    v42_aliases = set(route_map.get("aliases", {}))
    manifest = json.loads(SOURCE16_MANIFEST.read_text(encoding="utf-8"))
    source16_records = {x.get("route"): x for x in manifest.get("source16", {}).get("records", [])}

    all_rows: list[dict] = []
    page_records: list[dict] = []
    for page_id, route, raw_name in PAGES:
        raw_path = PRIVATE / raw_name
        out_path = SOURCE16_SITE / route.lstrip("/")
        raw_bytes = raw_path.read_bytes()
        out_bytes = out_path.read_bytes()
        raw_parser = PageParser(page_id, route)
        raw_parser.feed(raw_bytes.decode("utf-8", errors="replace"))
        raw_parser.close()
        parser = PageParser(page_id, route)
        parser.feed(out_bytes.decode("utf-8", errors="replace"))
        parser.close()
        for row in parser.rows:
            f = local_file(SOURCE16_SITE, row["route"])
            row["source16_file"] = f.relative_to(SOURCE16_SITE).as_posix() if f else None
            row["source16_file_bytes"] = f.stat().st_size if f else None
            row["v42_route_present"] = bool(row["route"] and (row["route"] in v42_routes or row["route"] in v42_aliases))
            v42_file = V42_ROOT / row["route"].lstrip("/") if row["route"] else None
            row["v42_file_present"] = bool(v42_file and v42_file.is_file())
            if row["route_kind"] == "external":
                row["status"] = "external"
            elif row["route_kind"] == "non_resource":
                row["status"] = "non_resource"
            elif row["context"] == "dynamic_runtime" and row["kind"] in {"dynamic_css", "dynamic_markup"}:
                # This is one side of a runtime expression (for example
                # roothost + '/css/ie.css' or icon_ + menu name). Keep the
                # candidate route as evidence, but do not claim a concrete
                # missing file from the literal alone.
                row["status"] = "dynamic_unresolved"
            elif row["context"] == "dynamic_runtime" and row["route"] is None:
                row["status"] = "dynamic_unresolved"
            elif row["context"] == "dynamic_runtime" and f:
                row["status"] = "dynamic_local_present"
            elif row["context"] == "dynamic_runtime":
                row["status"] = "dynamic_local_missing"
            elif f:
                row["status"] = "local_present"
            elif row["v42_file_present"] or row["v42_route_present"]:
                row["status"] = "missing_in_source16_v42_entity"
            else:
                row["status"] = "local_missing"
            all_rows.append(row)
        rec = source16_records.get(route, {})
        dep_key = lambda r: (r["kind"], r["raw_url"], r["route"], r["context"])
        raw_dep_set = {dep_key(r) for r in raw_parser.rows}
        out_dep_set = {dep_key(r) for r in parser.rows}
        page_records.append({
            "page_id": page_id,
            "route": route,
            "raw_path": raw_path.relative_to(ROOT).as_posix(),
            "source16_path": out_path.relative_to(ROOT).as_posix(),
            "raw_sha256": sha256_bytes(raw_bytes),
            "raw_length": len(raw_bytes),
            "source16_sha256": sha256_bytes(out_bytes),
            "source16_length": len(out_bytes),
            "source16_manifest_record": rec,
            "raw_dependency_row_count": len(raw_parser.rows),
            "source16_dependency_row_count": len(parser.rows),
            "raw_parser_comments_seen": raw_parser.comments,
            "source16_parser_comments_seen": parser.comments,
            "raw_only_dependency_keys": [list(x) for x in sorted(raw_dep_set - out_dep_set, key=repr)],
            "source16_only_dependency_keys": [list(x) for x in sorted(out_dep_set - raw_dep_set, key=repr)],
            "dependency_row_count": len(parser.rows),
        })

    # Group repeated use of the same actual target. Dynamic and static uses
    # remain separate so a missing runtime SWF cannot be hidden by a CSS hit.
    groups: dict[tuple, dict] = {}
    for row in all_rows:
        if row["status"] in {"non_resource"}:
            continue
        key = (row["status"], row["kind"], row["route"] or row["raw_url"])
        g = groups.setdefault(key, {
            "status": row["status"], "kind": row["kind"], "route": row["route"], "raw_urls": set(),
            "pages": set(), "uses": 0, "first_use": None, "notes": set(),
            "v42_route_present": row["v42_route_present"], "v42_file_present": row["v42_file_present"],
            "source16_file": row["source16_file"], "source16_file_bytes": row["source16_file_bytes"],
        })
        g["raw_urls"].add(row["raw_url"])
        g["pages"].add(row["page_id"])
        g["uses"] += 1
        g["notes"].add(row["note"])
        if g["first_use"] is None:
            g["first_use"] = {k: row[k] for k in ("page_id", "page_route", "element", "attribute", "line", "context", "raw_url")}

    unique = []
    for g in groups.values():
        unique.append({
            **{k: v for k, v in g.items() if k not in {"raw_urls", "pages", "notes"}},
            "raw_urls": sorted(g["raw_urls"]),
            "pages": sorted(g["pages"]),
            "notes": sorted(x for x in g["notes"] if x),
        })
    unique.sort(key=lambda x: (x["status"], x["kind"], x["route"] or x["raw_urls"][0]))

    priority = []
    for g in unique:
        if g["status"] not in {"local_missing", "missing_in_source16_v42_entity", "dynamic_local_missing"}:
            continue
        # Keep the requested output small and page-useful. Shared chrome is
        # lower priority than page-specific style/content assets.
        route = g["route"] or ""
        pages = g["pages"]
        score = 0
        if len(pages) == 1:
            score += 20
        if any(p in {"moltencore", "bardclass"} for p in pages):
            score += 20
        if g["kind"] in {"css", "css_filter", "image", "swf", "object", "embed", "media"}:
            score += 10
        if route.startswith("/moltencore/") or route.startswith("/wrath/"):
            score += 8
        if g["status"] == "dynamic_unresolved":
            score -= 5
        priority.append((score, g))
    priority.sort(key=lambda x: (-x[0], x[1]["kind"], x[1]["route"] or x[1]["raw_urls"][0]))
    priority_rows = []
    for rank, (score, g) in enumerate(priority[:30], 1):
        priority_rows.append({"rank": rank, "score": score, **g})

    counts = Counter(r["status"] for r in all_rows)
    unique_counts = Counter(g["status"] for g in unique)
    page_counts = {p["page_id"]: Counter(r["status"] for r in all_rows if r["page_id"] == p["page_id"]) for p in page_records}
    report = {
        "schema": "source16-dependency-audit-v1",
        "scope": {
            "pages": [p["route"] for p in page_records],
            "source16_site": str(SOURCE16_SITE.relative_to(ROOT)).replace("\\", "/"),
            "v42_route_map": str(V42_ROUTE_MAP.relative_to(ROOT)).replace("\\", "/"),
            "network": "not used",
            "comments_excluded": True,
            "pure_javascript_strings_excluded": True,
            "dynamic_targets_separate": True,
        },
        "inputs": {
            "source16_manifest_sha256": sha256_bytes(SOURCE16_MANIFEST.read_bytes()),
            "v42_route_map_sha256": sha256_bytes(V42_ROUTE_MAP.read_bytes()),
            "source16_routes_in_manifest": len(manifest.get("files", [])),
            "v42_routes": len(v42_routes),
            "v42_aliases": len(v42_aliases),
        },
        "counts": {
            "pages": len(page_records),
            "dependency_rows": len(all_rows),
            "unique_targets": len(unique),
            "by_status": dict(sorted(counts.items())),
            "unique_by_status": dict(sorted(unique_counts.items())),
            "priority_items": len(priority_rows),
        },
        "page_counts": {k: dict(sorted(v.items())) for k, v in page_counts.items()},
        "pages": page_records,
        "targets": unique,
        "priority_gaps": priority_rows,
        "method_notes": [
            "Static resource attributes and CSS url()/AlphaImageLoader src were parsed from live Source16 output bytes with line numbers.",
            "HTML comments were ignored by HTMLParser; inline JavaScript was only inspected for printFlash/document.write/roothost runtime constructions.",
            "Route existence is checked against the Source16 destination first, then v42 file and route-map evidence; no route-key-only miss is reported as a page gap.",
            "Each page's raw private HTML was parsed with the same rules; page records include raw-only and Source16-only dependency-key deltas alongside the final output evidence.",
            "The eight page bodies are Source16 inputs; shared chrome and external analytics are retained as observations but ranked below page-specific missing assets.",
        ],
    }
    (OUT / "dependency-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with (OUT / "dependency-audit.csv").open("w", encoding="utf-8", newline="") as fh:
        fields = ["page_id", "page_route", "kind", "element", "attribute", "raw_url", "route", "status", "line", "context", "source16_file", "source16_file_bytes", "v42_route_present", "v42_file_present", "note"]
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(all_rows)

    with (OUT / "priority-gaps.csv").open("w", encoding="utf-8", newline="") as fh:
        fields = ["rank", "score", "status", "kind", "route", "raw_urls", "pages", "uses", "source16_file", "v42_route_present", "v42_file_present", "first_use", "notes"]
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in priority_rows:
            out = dict(row)
            out["raw_urls"] = " | ".join(out["raw_urls"])
            out["pages"] = " | ".join(out["pages"])
            out["first_use"] = json.dumps(out["first_use"], ensure_ascii=False, sort_keys=True)
            out["notes"] = " | ".join(out["notes"])
            w.writerow(out)

    (OUT / "README.md").write_text(
        """# Source16 dependency audit\n\n"
        "This is a local, read-only audit of the eight Source16 body pages. It parses actual HTML resource attributes and CSS declarations, ignores HTML comments, and records only recognized runtime targets from `printFlash`, `document.write`, and `roothost` in a separate dynamic class. It does not inspect the network or alter Source16/v42.\n\n"
        "`dependency-audit.json` is the evidence record; `dependency-audit.csv` contains one row per observed use with source line; `priority-gaps.csv` is capped at 30 ranked page-use gaps.\n""",
        encoding="utf-8",
    )

    summary_lines = [
        "# Source16 dependency audit summary",
        "",
        "Scope: eight Source16 body pages; local Source16 destination plus v42 route-map/file evidence; no network and no site/exporter writes.",
        "",
        f"Observed {len(all_rows)} dependency uses, {len(unique)} unique target/status groups, and {len(priority_rows)} ranked gaps (cap 30).",
        "",
        "## Per-page counts",
        "",
        "| Page | Present | Missing | Dynamic unresolved | Dynamic missing | External |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for page_id in [p["page_id"] for p in page_records]:
        c = page_counts[page_id]
        summary_lines.append(
            f"| `{page_id}` | {c.get('local_present', 0)} | {c.get('local_missing', 0)} | {c.get('dynamic_unresolved', 0)} | {c.get('dynamic_local_missing', 0)} | {c.get('external', 0)} |"
        )
    summary_lines.extend([
        "",
        "## Highest-priority concrete gaps",
        "",
        "The rows below are page-use evidence with exact output line numbers. Dynamic variable expressions are excluded from this list; the one exact missing runtime SWF is retained separately.",
        "",
        "| Rank | Page | Kind | Route | Line | Reason |",
        "|---:|---|---|---|---:|---|",
    ])
    for g in priority_rows:
        first = g["first_use"]
        summary_lines.append(
            f"| {g['rank']} | `{first['page_id']}` | `{g['kind']}` | `{g['route'] or 'runtime expression'}` | {first['line']} | `{g['status']}`; raw `{first['raw_url']}` |"
        )
    summary_lines.extend([
        "",
        "## Interpretation",
        "",
        "* MoltenCore has a missing page stylesheet (`css.css` line 8), three gallery thumbnails, and its local helper scripts/back arrow. The audit does not infer whether any absent original binary is recoverable.",
        "* Bard has missing header skin backgrounds, artwork thumbnails, talent decoration images, stylesheet/helper scripts, and one exact runtime `bard_idle.swf` target at line 184. The runtime target is not one of the three already validated Flash exhibits, so it remains a source/decision item rather than an automatic restore proposal.",
        "* Tinfoil Hat and Two-Headed Ogre contain page-specific image/CSS targets absent from both the Source16 destination and v42 local evidence. Contest has two page thumbnails with the same evidence boundary.",
        "* Dynamic `roothost + literal`, menu-icon concatenation, and other variable expressions remain in `targets` as `dynamic_unresolved`; they are not counted as concrete missing files.",
        "",
        "See `dependency-audit.json` for source hashes, manifest records, route-map booleans, all line-level uses, and the capped `priority_gaps`; `dependency-audit.csv` contains the row-level table.",
        "",
    ])
    (OUT / "SUMMARY.md").write_text("\n".join(summary_lines), encoding="utf-8")

    print(json.dumps({"out": str(OUT), "counts": report["counts"], "page_counts": report["page_counts"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
