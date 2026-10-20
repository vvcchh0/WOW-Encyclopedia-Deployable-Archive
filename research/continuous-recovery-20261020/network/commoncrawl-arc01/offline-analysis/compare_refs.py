"""Compare literal active same-site resource references without executing HTML or JS."""

from __future__ import annotations

import hashlib
import html as html_lib
import json
import re
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[5]
OWN = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from tools.commoncrawl_arc import parse_arc_gzip_member
RAW_BODY = ROOT / "research/continuous-recovery-20261020/network/commoncrawl-arc01/raw/attempt01-direct.body"
SOURCE15_PAGE = ROOT / ".scratch/offline-navigation-20261015-v15/site/info/encyclopedia/index.xml"
BASE_URL = "http://www.worldofwarcraft.com/info/encyclopedia/index.xml"
EXPECTED_RAW_BYTES = 6601
EXPECTED_RAW_SHA256 = "81e766f10196f05945fa51c7be1c106ddc730b32ef93b470c2ccd51f82444d5a"
EXPECTED_SOURCE15_BYTES = 59230
EXPECTED_SOURCE15_SHA256 = "b531cbd2d6b0ef1ad37cf744d666e6559120142d230baf308baa70b53a512b1d"
EXPECTED_URL = BASE_URL
EXPECTED_TIMESTAMP = "20080720173556"
EXPECTED_DIGEST = "J5QKGA7VRIUFZPBPEDKOT6REERJJJJXS"

SAME_SITE_HOSTS = {"www.worldofwarcraft.com", "worldofwarcraft.com"}
AD_SOCIAL_TERMS = (
    "doubleclick",
    "googlesyndication",
    "google-analytics",
    "facebook",
    "twitter",
    "youtube",
    "instagram",
    "linkedin",
    "pinterest",
    "reddit",
    "addthis",
    "sharethis",
)
EXPRESSION_RE = re.compile(r"(?:javascript|data|vbscript):|expression\s*\(|\$\{|\}\s*\)", re.I)
PLACEHOLDER_RE = re.compile(r"@[A-Za-z0-9_.:-]+@")
CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
CSS_IMPORT_RE = re.compile(
    r"@import\s+(?:url\(\s*)?[\"']?([^\s\"')]+)", re.I
)
CSS_URL_RE = re.compile(r"url\(\s*([^)]+?)\s*\)", re.I)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _normalise_url(raw: str) -> tuple[str | None, str | None]:
    value = html_lib.unescape(raw).strip().strip("\"'")
    lower = value.lower()
    if not value or lower.startswith("#") or lower.startswith("?"):
        return None, "non-resource-fragment"
    if EXPRESSION_RE.search(value) or PLACEHOLDER_RE.search(value):
        return None, "expression-or-placeholder"
    absolute = urljoin(BASE_URL, value)
    parts = urlsplit(absolute)
    if parts.scheme.lower() not in {"http", "https"}:
        return None, "non-http-scheme"
    host = (parts.hostname or "").lower()
    if host not in SAME_SITE_HOSTS:
        return None, "external-host"
    path = parts.path or "/"
    normal = urlunsplit(("http", "www.worldofwarcraft.com", path, parts.query, ""))
    path_lower = path.lower()
    full_lower = normal.lower()
    if path_lower.startswith("/__offline/"):
        return normal, "offline-rewrite"
    if any(term in full_lower for term in AD_SOCIAL_TERMS):
        return normal, "ad-or-social"
    segments = {part for part in path_lower.split("/") if part}
    if segments.intersection({"ad", "ads", "advert", "advertising", "social", "share"}):
        return normal, "ad-or-social"
    return normal, None


class _ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[dict[str, object]] = []
        self.excluded: list[dict[str, object]] = []
        self._style_depth = 0
        self._style_parts: list[str] = []

    def _add(self, kind: str, raw: str, origin: str) -> None:
        line, column = self.getpos()
        normal, reason = _normalise_url(raw)
        entry: dict[str, object] = {
            "kind": kind,
            "raw": raw,
            "origin": origin,
            "line": line,
            "column": column,
        }
        if normal is not None:
            entry["url"] = normal
        if reason is not None:
            entry["excluded_reason"] = reason
            if normal is not None:
                entry["url"] = normal
            self.excluded.append(entry)
        else:
            self.references.append(entry)

    def _add_css(self, text: str, origin: str) -> None:
        clean = CSS_COMMENT_RE.sub("", text)
        for match in CSS_IMPORT_RE.finditer(clean):
            self._add("style", match.group(1), origin + ":@import")
        for match in CSS_URL_RE.finditer(clean):
            raw = match.group(1).strip().strip("\"'")
            self._add("image", raw, origin + ":url")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        pairs = [(name.lower(), value) for name, value in attrs]
        attrs_map = {name: value for name, value in pairs}
        if tag == "img" and attrs_map.get("src"):
            self._add("image", attrs_map["src"] or "", "img[src]")
        elif tag == "input" and attrs_map.get("src") and (attrs_map.get("type") or "").lower() == "image":
            self._add("image", attrs_map["src"] or "", "input[type=image][src]")
        elif tag == "script" and attrs_map.get("src"):
            self._add("script", attrs_map["src"] or "", "script[src]")
        elif tag == "link" and attrs_map.get("href"):
            rel = set((attrs_map.get("rel") or "").lower().split())
            if "stylesheet" in rel:
                self._add("style", attrs_map["href"] or "", "link[rel=stylesheet]")
        if attrs_map.get("style"):
            self._add_css(attrs_map["style"] or "", tag + "[style]")
        if tag == "style":
            self._style_depth += 1
            self._style_parts = []

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "style" and self._style_depth:
            self._add_css("".join(self._style_parts), "style-block")
            self._style_depth -= 1
            self._style_parts = []

    def handle_data(self, data: str) -> None:
        if self._style_depth:
            self._style_parts.append(data)


def extract_references(document: bytes) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    parser = _ReferenceParser()
    parser.feed(document.decode("utf-8", "replace"))
    parser.close()
    return parser.references, parser.excluded


def _unique(references: list[dict[str, object]]) -> dict[tuple[str, str], dict[str, object]]:
    grouped: dict[tuple[str, str], dict[str, object]] = {}
    for ref in references:
        key = (str(ref["kind"]), str(ref["url"]))
        item = grouped.setdefault(
            key,
            {
                "kind": key[0],
                "url": key[1],
                "occurrences": [],
            },
        )
        item["occurrences"].append(
            {
                "raw": ref["raw"],
                "origin": ref["origin"],
                "line": ref["line"],
                "column": ref["column"],
            }
        )
    return grouped


def _read_bound(path: Path, expected_bytes: int, expected_sha256: str) -> bytes:
    value = path.read_bytes()
    if len(value) != expected_bytes:
        raise RuntimeError(f"unexpected byte count for {path}: {len(value)}")
    actual = sha256_bytes(value)
    if actual != expected_sha256:
        raise RuntimeError(f"unexpected SHA-256 for {path}: {actual}")
    return value


def build_report() -> dict[str, object]:
    compressed = _read_bound(RAW_BODY, EXPECTED_RAW_BYTES, EXPECTED_RAW_SHA256)
    source15 = _read_bound(SOURCE15_PAGE, EXPECTED_SOURCE15_BYTES, EXPECTED_SOURCE15_SHA256)
    arc = parse_arc_gzip_member(
        compressed,
        expected_url=EXPECTED_URL,
        expected_timestamp=EXPECTED_TIMESTAMP,
        expected_status=200,
        expected_digest=EXPECTED_DIGEST,
    )
    actual_refs, actual_excluded = extract_references(arc.http.payload)
    source_refs, source_excluded = extract_references(source15)
    actual_unique = _unique(actual_refs)
    source_unique = _unique(source_refs)
    actual_keys = set(actual_unique)
    source_keys = set(source_unique)
    actual_only_keys = sorted(actual_keys - source_keys)
    source_only_keys = sorted(source_keys - actual_keys)
    actual_urls = {url for _, url in actual_keys}
    source_urls = {url for _, url in source_keys}
    actual_only_urls = sorted(actual_urls - source_urls)
    potential_image_leads = sorted(
        {
            url
            for kind, url in actual_only_keys
            if kind == "image"
        }
    )
    if potential_image_leads:
        classification = "potential_new_image_leads_require_independent_source_acceptance"
    else:
        classification = "no_genuine_new_restoration_lead"

    def sorted_values(grouped: dict[tuple[str, str], dict[str, object]]) -> list[dict[str, object]]:
        return [grouped[key] for key in sorted(grouped)]

    return {
        "schema": "commoncrawl-arc01-offline-reference-comparison-v1",
        "network_requests": 0,
        "javascript_executed": False,
        "html_executed": False,
        "input_reads": [
            {
                "path": RAW_BODY.relative_to(ROOT).as_posix(),
                "bytes": len(compressed),
                "sha256": sha256_bytes(compressed),
                "role": "private accepted ARC range; not copied to this output",
            },
            {
                "path": SOURCE15_PAGE.relative_to(ROOT).as_posix(),
                "bytes": len(source15),
                "sha256": sha256_bytes(source15),
                "role": "frozen Source15 encyclopedia page",
            },
        ],
        "arc": {
            "url": arc.url,
            "ip": arc.ip,
            "timestamp": arc.timestamp,
            "mime": arc.mime,
            "declared_length": arc.declared_length,
            "record_body_bytes": len(arc.record_body),
            "trailing": arc.trailing.decode("ascii"),
            "stored_http_status": arc.http.status,
            "payload_bytes": len(arc.http.payload),
            "payload_sha1_base32": arc.payload_sha1_base32,
            "expected_payload_sha1_base32": EXPECTED_DIGEST,
        },
        "active_reference_policy": {
            "kinds": ["image", "script", "style"],
            "same_site_hosts": sorted(SAME_SITE_HOSTS),
            "literal_sources": ["img[src]", "input[type=image][src]", "script[src]", "link[rel=stylesheet]", "CSS @import/url() in style attributes or blocks"],
            "excluded": ["external hosts", "ads/social terms", "offline rewrite assets", "JavaScript/data/expression URLs", "placeholders and fragments"],
        },
        "actual_july20_html": {
            "source": "ARC payload",
            "raw_reference_count": len(actual_refs) + len(actual_excluded),
            "active_unique_count": len(actual_unique),
            "active_references": sorted_values(actual_unique),
            "excluded_count": len(actual_excluded),
            "excluded_reason_counts": dict(sorted(Counter(str(item["excluded_reason"]) for item in actual_excluded).items())),
        },
        "source15_encyclopedia_page": {
            "source_path": SOURCE15_PAGE.relative_to(ROOT).as_posix(),
            "raw_reference_count": len(source_refs) + len(source_excluded),
            "active_unique_count": len(source_unique),
            "active_references": sorted_values(source_unique),
            "excluded_count": len(source_excluded),
            "excluded_reason_counts": dict(sorted(Counter(str(item["excluded_reason"]) for item in source_excluded).items())),
        },
        "comparison": {
            "active_key_intersection_count": len(actual_keys & source_keys),
            "actual_only_active_keys": [actual_unique[key] for key in actual_only_keys],
            "source15_only_active_keys": [source_unique[key] for key in source_only_keys],
            "actual_only_urls": actual_only_urls,
            "source15_only_urls": sorted(source_urls - actual_urls),
            "potential_new_image_leads": potential_image_leads,
            "classification": classification,
            "interpretation": (
                "The accepted July 20 HTML exposes no same-site image URL absent from Source15; "
                "therefore this comparison supplies no genuinely new restoration lead."
                if not potential_image_leads
                else "Image URLs present only in the accepted July 20 HTML are potential leads, not accepted restorations."
            ),
        },
    }


def write_outputs() -> dict[str, object]:
    report = build_report()
    report_path = OWN / "reference-comparison.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    comparison = report["comparison"]
    actual = report["actual_july20_html"]
    source = report["source15_encyclopedia_page"]
    lines = [
        "# Common Crawl ARC01 offline reference comparison",
        "",
        "This report reads the private accepted ARC range and the frozen Source15 encyclopedia page. It makes zero HTTP requests and executes no HTML or JavaScript.",
        "",
        f"- ARC payload: `{report['arc']['payload_bytes']}` bytes; SHA1 base32 `{report['arc']['payload_sha1_base32']}`.",
        f"- Active literal refs: July 20 HTML `{actual['active_unique_count']}`, Source15 `{source['active_unique_count']}`.",
        f"- Actual-only active URLs: `{len(comparison['actual_only_urls'])}`.",
        f"- Potential new image leads: `{len(comparison['potential_new_image_leads'])}`.",
        f"- Classification: **{comparison['classification']}**.",
        "",
        comparison["interpretation"],
        "",
        "Excluded references are recorded by reason in `reference-comparison.json`; ads/social, external hosts, offline rewrites, expression URLs, placeholders, and fragments are not treated as restoration leads.",
    ]
    summary_path = OWN / "reference-comparison.md"
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "report_path": report_path.relative_to(ROOT).as_posix(),
        "report_sha256": sha256_bytes(report_path.read_bytes()),
        "summary_path": summary_path.relative_to(ROOT).as_posix(),
        "summary_sha256": sha256_bytes(summary_path.read_bytes()),
        "classification": comparison["classification"],
        "actual_only_urls": comparison["actual_only_urls"],
        "potential_new_image_leads": comparison["potential_new_image_leads"],
    }


if __name__ == "__main__":
    print(json.dumps(write_outputs(), ensure_ascii=False, indent=2))
