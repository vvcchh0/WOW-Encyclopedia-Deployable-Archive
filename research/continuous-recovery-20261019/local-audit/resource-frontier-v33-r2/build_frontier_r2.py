from __future__ import annotations

import collections
import hashlib
import html
import json
import re
import urllib.parse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
V33 = ROOT / ".scratch" / "pages-resources-20261018-v33"
SOURCE = ROOT / ".scratch" / "offline-navigation-20261015-v15" / "site"
EXPECT = ROOT / "research" / "continuous-recovery-20261018" / "publication" / "v33-export-expectations-r2.json"
PROVENANCE = V33 / "export-provenance.json"
V32 = ROOT / "research" / "continuous-recovery-20261018" / "local-audit" / "static-frontier-v32" / "static-frontier-v32-candidates.json"
PRIMARY = ROOT / "research" / "continuous-recovery-20261018" / "integration" / "v33" / "v33-primary-source-map.json"
SUPPLEMENT = ROOT / "research" / "continuous-recovery-20261018" / "integration" / "v33" / "v33-supplement-source-map.json"
EXCLUSION_QUEUE = ROOT / "research" / "continuous-recovery-20261018" / "publication" / "next-frontier-selected70.json"
EXCLUSION_DOCS = [
    ROOT / "docs" / "gap-review-20261011.md",
    ROOT / "research" / "gap-review-20261011" / "errors" / "review-report.zh.md",
    ROOT / "research" / "gap-review-20261011" / "errors" / "cdx-summary-variants-core.json",
]
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.I)
MARKER_RE = re.compile(r"__offline/missing-image\.svg\?([^\"'<>\s\)]+)", re.I)
BAD_STEMS = (
    "pixel", "socket", "reagent", "recipe", "icon", "logo", "background", "page-bg",
    "bg-", "-bg", "border", "button", "arrow", "spacer", "blank", "close", "corner",
    "menu", "nav", "header", "footer", "shadow", "separator", "bullet", "bullet", "1x1",
)
GOOD_STEMS = (
    "ss", "screenshot", "comic", "wallpaper", "art", "fan", "map", "dungeon", "arena",
    "battle", "pvp", "illustr", "photo", "collect", "cover", "wow", "tcg", "leipzig",
    "europe", "dragon", "contest", "screen", "guide", "raid", "boss", "townhall",
)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def norm_url(value: str) -> str:
    value = html.unescape(urllib.parse.unquote(value)).strip().rstrip(",.;")
    p = urllib.parse.urlsplit(value)
    if p.scheme.lower() not in {"http", "https"} or not p.netloc:
        return value
    host = p.hostname.lower() if p.hostname else ""
    try:
        port = p.port
    except ValueError:
        return value
    netloc = host
    if port and not ((p.scheme.lower() == "http" and port == 80) or (p.scheme.lower() == "https" and port == 443)):
        netloc += f":{port}"
    return urllib.parse.urlunsplit((p.scheme.lower(), netloc, p.path, p.query, p.fragment))


def is_image_url(value: str) -> bool:
    p = urllib.parse.urlsplit(value)
    return Path(p.path.lower()).suffix in IMAGE_EXTS


def source_file_for_url(source_url: str) -> Path | None:
    p = urllib.parse.urlsplit(source_url)
    rel = p.path.lstrip("/")
    options = [rel]
    if rel.endswith("/"):
        options.append(rel + "index.html")
    if rel.endswith(".xml"):
        options.extend([rel + ".html", rel[:-4] + ".xml.html"])
    options.append(rel + ".html")
    for candidate in options:
        fp = SOURCE / candidate
        if fp.is_file():
            return fp
    return None


def output_rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def parse_markers() -> dict[str, dict]:
    rows: dict[str, dict] = {}
    text_suffixes = {".html", ".htm", ".xml", ".css", ".js", ".txt", ".json"}
    for path in V33.rglob("*"):
        if not path.is_file() or path.name == "export-provenance.json" or path.suffix.lower() not in text_suffixes:
            continue
        try:
            if path.stat().st_size > 12 * 1024 * 1024:
                continue
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line_no, line in enumerate(lines, 1):
            for match in MARKER_RE.finditer(line):
                query = html.unescape(match.group(1))
                args = urllib.parse.parse_qs(query, keep_blank_values=True)
                requested = norm_url(args.get("requested", [""])[0])
                source_url = norm_url(args.get("source", [""])[0])
                if not requested or not is_image_url(requested):
                    continue
                item = rows.setdefault(requested, {"requested_url": requested, "markers": [], "source_pages": set()})
                item["markers"].append({
                    "output_file": output_rel(path),
                    "line": line_no,
                    "source_url": source_url,
                    "reason": args.get("reason", [""])[0],
                    "snippet": line[:1600],
                })
                if source_url:
                    item["source_pages"].add(source_url)
    for item in rows.values():
        item["source_pages"] = sorted(item["source_pages"])
    return rows


def recursive_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from recursive_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from recursive_strings(v)


def url_strings(text: str) -> set[str]:
    out = set()
    for raw in URL_RE.findall(text):
        value = norm_url(raw.rstrip(")]}>,;\"'`"))
        if value.startswith(("http://", "https://")):
            out.add(value)
    return out


def evidence_index():
    executed: dict[str, list[dict]] = collections.defaultdict(list)
    planned: dict[str, list[dict]] = collections.defaultdict(list)
    scanned = []
    roots = [
        ROOT / "research" / "continuous-recovery-20261018" / "network",
        ROOT / "research" / "continuous-recovery-20261018" / "publication",
        ROOT / "research" / "continuous-recovery-20261018" / "local-audit",
        ROOT / "research" / "continuous-recovery-20261018" / "integration",
        ROOT / "research" / "continuous-recovery-20261016" / "network",
        ROOT / "research" / "continuous-recovery-20261016" / "publication",
        ROOT / "research" / "continuous-recovery-20261016" / "local-audit",
    ]
    # Output directories contain the small source-map/batch-report evidence needed
    # for row-level deduplication. Only raw payload-bearing subtrees are excluded.
    skip_parts = {"raw", "body", "headers", "payloads", "private", "accepted-images"}
    for base in roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".json", ".md", ".txt", ".csv"}:
                continue
            if OUT in path.parents:
                continue
            parts = {x.lower() for x in path.parts}
            if parts & skip_parts:
                continue
            try:
                if path.stat().st_size > 8 * 1024 * 1024:
                    continue
                raw = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            rel = output_rel(path)
            low = rel.lower()
            kind = "planned" if any(x in low for x in ("plan", "queue", "selected-originals", "bindings", "selection")) else "other"
            if any(x in low for x in ("source-acceptance", "source_map", "source-map", "batch-report", "execution-report", "execution-input", "root-.*-source", "state.json", "summary.json")):
                kind = "executed"
            urls = set()
            if path.suffix.lower() == ".json":
                try:
                    obj = json.loads(raw)
                    for value in recursive_strings(obj):
                        urls.update(url_strings(value))
                except Exception:
                    urls.update(url_strings(raw))
            else:
                urls.update(url_strings(raw))
            if not urls:
                continue
            file_sha = sha(path)
            scanned.append({"path": rel, "sha256": file_sha, "kind": kind, "url_count": len(urls)})
            target = executed if kind == "executed" else planned if kind == "planned" else None
            if target is not None:
                for url in urls:
                    pos = raw.find(url)
                    context = raw[max(0, pos - 1800):pos + 1800].lower() if pos >= 0 else raw.lower()
                    hints = []
                    if "transport_unknown" in context or "transport-unknown" in context:
                        hints.append("transport_unknown")
                    if "complete_no_eligible_capture" in context or "empty_index" in context or '"statuscode": "404"' in context or '"statuscode":"404"' in context:
                        hints.append("complete_empty_or_404")
                    target[url].append({"path": rel, "sha256": file_sha, "kind": kind, "status_hints": sorted(set(hints))})
    return executed, planned, scanned


def canonical_scope_reconciliation() -> dict:
    """Recount v33 markers with the frozen canonical file boundary.

    The expanded scan intentionally includes _origins and generated JS. This
    helper applies the accepted HTML/HTM/XML/CSS and no-_origins boundary so the
    900-item baseline can be compared without changing it.
    """
    canonical_urls: set[str] = set()
    canonical_news: set[str] = set()
    canonical_occurrences = 0
    canonical_news_occurrences = 0
    raw_by_normalized: dict[str, set[str]] = collections.defaultdict(set)
    raw_records = []
    text_files = 0
    marker_files: set[str] = set()
    allowed_suffixes = {".html", ".htm", ".xml", ".css"}
    for path in V33.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(V33).as_posix()
        if rel.startswith("_origins/") or path.suffix.lower() not in allowed_suffixes:
            continue
        text_files += 1
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        matches = list(MARKER_RE.finditer(text))
        if matches:
            marker_files.add(rel)
        for match in matches:
            args = urllib.parse.parse_qs(html.unescape(match.group(1)), keep_blank_values=True)
            raw_requested = html.unescape(args.get("requested", [""])[0]).strip()
            requested = norm_url(raw_requested)
            if not requested or not is_image_url(requested):
                continue
            canonical_urls.add(requested)
            canonical_occurrences += 1
            if rel.startswith("news/"):
                canonical_news.add(requested)
                canonical_news_occurrences += 1
            raw_by_normalized[requested].add(raw_requested)
            raw_records.append((raw_requested, requested))

    def no_scheme_key(value: str):
        parsed = urllib.parse.urlsplit(value)
        host = (parsed.hostname or "").lower()
        try:
            port = parsed.port
        except ValueError:
            port = None
        if port in {80, 443}:
            port = None
        netloc = host + (f":{port}" if port else "")
        return (netloc, parsed.path, parsed.query, parsed.fragment)

    scheme_groups: dict[tuple, set[str]] = collections.defaultdict(set)
    explicit_default_ports = set()
    normalized_changes = 0
    default_port_changed_occurrences = 0
    other_normalization_changed_occurrences = 0
    normalization_change_examples = []
    for raw, normalized in raw_records:
        if raw != normalized:
            normalized_changes += 1
        parsed = urllib.parse.urlsplit(raw)
        try:
            port = parsed.port
        except ValueError:
            port = None
        if (parsed.scheme.lower() == "http" and port == 80) or (parsed.scheme.lower() == "https" and port == 443):
            explicit_default_ports.add(raw)
            if raw != normalized:
                default_port_changed_occurrences += 1
        elif raw != normalized:
            other_normalization_changed_occurrences += 1
        if raw != normalized and len(normalization_change_examples) < 12:
            normalization_change_examples.append({"raw": raw, "normalized": normalized})
        scheme_groups[no_scheme_key(normalized)].add(parsed.scheme.lower())
    scheme_variant_groups = {k: sorted(v) for k, v in scheme_groups.items() if len(v) > 1}
    raw_collision_groups = {k: sorted(v) for k, v in raw_by_normalized.items() if len(v) > 1}

    expanded_urls = set()
    origins_urls = set()
    dynamic_urls = set()
    for url, item in parse_markers().items():
        expanded_urls.add(url)
        paths = {m["output_file"] for m in item["markers"]}
        if any("/_origins/" in p.replace("\\", "/") for p in paths):
            origins_urls.add(url)
        if any(Path(p).suffix.lower() == ".js" for p in paths) or any("/js/" in p.lower() for p in paths):
            dynamic_urls.add(url)
    extra = expanded_urls - canonical_urls
    extra_origins = extra & origins_urls
    extra_dynamic = extra & dynamic_urls
    return {
        "canonical_boundary": {
            "path": ".scratch/pages-resources-20261018-v33",
            "exclude_prefixes": ["_origins/"],
            "include_suffixes": sorted(allowed_suffixes),
            "static_text_files": text_files,
            "marker_files": len(marker_files),
            "unique_missing_images": len(canonical_urls),
            "missing_occurrences": canonical_occurrences,
            "news_unique_missing_images": len(canonical_news),
            "news_missing_occurrences": canonical_news_occurrences,
        },
        "expanded_boundary": {
            "all_text_marker_unique": len(expanded_urls),
            "origins_unique": len(origins_urls),
            "dynamic_js_or_js_path_unique": len(dynamic_urls),
            "noncanonical_extra_unique": len(extra),
        },
        "set_reconciliation": {
            "canonical_unique": len(canonical_urls),
            "expanded_minus_canonical": len(extra),
            "extra_origins_unique": len(extra_origins),
            "extra_dynamic_unique": len(extra_dynamic),
            "extra_origin_and_dynamic_unique": len(extra_origins & extra_dynamic),
            "extra_origin_only_unique": len(extra_origins - extra_dynamic),
            "extra_dynamic_only_unique": len(extra_dynamic - extra_origins),
            "extra_other_unique": len(extra - origins_urls - dynamic_urls),
            "expanded_union_check": len(canonical_urls | extra),
        },
        "url_normalization": {
            "canonical_raw_occurrences": len(raw_records),
            "canonical_raw_unique": len({raw for raw, _ in raw_records}),
            "canonical_normalized_unique": len(canonical_urls),
            "raw_collision_groups_after_normalization": len(raw_collision_groups),
            "raw_collision_examples": [{"normalized": key, "raw": values} for key, values in sorted(raw_collision_groups.items())[:12]],
            "explicit_default_port_raw_unique": len(explicit_default_ports),
            "explicit_default_port_examples": sorted(explicit_default_ports)[:12],
            "http_https_same_host_path_groups": len(scheme_variant_groups),
            "http_https_same_host_path_examples": [{"host_path_query": list(key), "schemes": schemes} for key, schemes in list(sorted(scheme_variant_groups.items(), key=lambda x: str(x[0])))[:12]],
            "raw_to_normalized_changed_occurrences": normalized_changes,
            "default_port_changed_occurrences": default_port_changed_occurrences,
            "other_normalization_changed_occurrences": other_normalization_changed_occurrences,
            "normalization_change_examples": normalization_change_examples,
            "interpretation": "The frozen normalizer lowercases scheme/host and removes only scheme-appropriate default ports; it does not merge HTTP and HTTPS. Explicit source-reviewed aliases remain separate evidence unless the accepted map names them.",
        },
    }


def source_context(item: dict):
    refs = []
    for source_url in item.get("source_pages", []):
        fp = source_file_for_url(source_url)
        if not fp:
            refs.append({"source_url": source_url, "source_file": None})
            continue
        lines = fp.read_text(encoding="utf-8", errors="replace").splitlines()
        hits = []
        needle = urllib.parse.unquote(source_url)
        # The source page is evidence for the page identity; the missing marker itself is in v33 output.
        for no, line in enumerate(lines, 1):
            if needle in line or urllib.parse.urlsplit(item["requested_url"]).path in line:
                hits.append({"line": no, "snippet": line[:1000]})
                if len(hits) >= 3:
                    break
        refs.append({
            "source_url": source_url,
            "source_file": output_rel(fp),
            "source_page_sha256": sha(fp),
            "source_page_bytes": fp.stat().st_size,
            "source_hits": hits,
        })
    return refs


def nav_context():
    rows = load(EXPECT)["navigation_href_recovery"]
    out = []
    for row in rows:
        page = row["page"]
        fp = SOURCE / page
        if not fp.exists() and page.endswith(".html"):
            fp = SOURCE / page[:-5]
        hits = []
        if fp.exists():
            lines = fp.read_text(encoding="utf-8", errors="replace").splitlines()
            for no, line in enumerate(lines, 1):
                decoded = urllib.parse.unquote(html.unescape(line))
                if row["original"] in decoded or urllib.parse.urlsplit(row["original"]).path in decoded:
                    hits.append({"line": no, "snippet": line[:1000]})
        out.append({
            "page": page,
            "original": norm_url(row["original"]),
            "new_overlay": row.get("new_overlay"),
            "source_file": output_rel(fp) if fp.exists() else None,
            "source_page_sha256": sha(fp) if fp.exists() else None,
            "source_hits": hits,
        })
    return out


def same_host_path(left: str, right: str) -> bool:
    a, b = urllib.parse.urlsplit(left), urllib.parse.urlsplit(right)
    if not a.hostname or not b.hostname or a.hostname.lower() != b.hostname.lower():
        return False
    def port(p):
        try:
            return p.port or (443 if p.scheme.lower() == "https" else 80)
        except ValueError:
            return None
    return port(a) == port(b) and a.path == b.path and a.query == b.query


def historical_variant_index(candidate_urls: set[str]) -> dict[str, list[dict]]:
    """Collect explicit non-exact CDX originals, but never promote them to strict rows."""
    out: dict[str, list[dict]] = collections.defaultdict(list)
    base = ROOT / "research" / "continuous-recovery-20261018" / "network"
    for path in base.rglob("*.json"):
        low = path.as_posix().lower()
        if "source-map" not in low and "source_map" not in low and "batch-report" not in low:
            continue
        try:
            obj = load(path)
        except Exception:
            continue
        def walk(value):
            if isinstance(value, dict):
                original = value.get("original") or value.get("actual_link_original")
                identity = value.get("identity") or value.get("link_identity")
                status = str(value.get("statuscode") or value.get("http_status") or "")
                if isinstance(original, str) and identity and str(identity).lower() not in {"exact", "same"} and status in {"200", "301", "302", "404"}:
                    original_n = norm_url(original)
                    for candidate in candidate_urls:
                        if candidate != original_n and same_host_path(candidate, original_n):
                            out[candidate].append({
                                "variant_original": original_n,
                                "identity": identity,
                                "status": status,
                                "timestamp": value.get("timestamp") or value.get("actual_timestamp") or value.get("selected_capture_timestamp"),
                                "evidence_file": output_rel(path),
                                "evidence_sha256": sha(path),
                            })
                for v in value.values():
                    walk(v)
            elif isinstance(value, list):
                for v in value:
                    walk(v)
        walk(obj)
    return {k: v[:12] for k, v in out.items()}


def legacy_exclusion_index() -> dict[str, dict]:
    """Load the frozen queue's explicit exclusion/defer closure.

    These rows are source-led decisions, not guesses from missing JSON keys.
    They are applied before the new candidate selector so an old bounded
    review cannot be reintroduced as an ``uncovered`` URL.
    """
    out = {}
    if not EXCLUSION_QUEUE.exists():
        return out
    payload = load(EXCLUSION_QUEUE)
    for row in payload.get("excluded_or_deferred", []):
        if not isinstance(row, dict) or not row.get("original"):
            continue
        original = norm_url(str(row["original"]))
        reason = str(row.get("reason") or "").strip()
        low = reason.lower()
        if "space" in low or "uri-serialization" in low:
            state = "encoding_variant_review"
        elif any(term in low for term in ("complete", "already cover", "older encyclopedia image checks")):
            state = "complete_empty_or_404"
        else:
            state = "excluded_or_deferred"
        out[original] = {
            "original": original,
            "state": state,
            "reason": reason,
            "source_file": output_rel(EXCLUSION_QUEUE),
            "source_sha256": sha(EXCLUSION_QUEUE),
            "source_field": "excluded_or_deferred",
        }
    return out


def score(url: str, item: dict, is_news: bool) -> int:
    path = urllib.parse.urlsplit(url).path.lower()
    name = Path(path).name.lower()
    score_value = 110 if is_news else 80
    if any(x in name or x in path for x in GOOD_STEMS):
        score_value += 50
    if any(x in name or x in path for x in BAD_STEMS):
        score_value -= 110
    if "thumb" in name:
        score_value -= 20
    if "2007" in path or "07-" in path:
        score_value += 30
    if "2008" in path or "08-" in path:
        score_value += 15
    if urllib.parse.urlsplit(url).hostname == "www.worldofwarcraft.com":
        score_value += 10
    if urllib.parse.urlsplit(url).hostname not in {"www.worldofwarcraft.com", "www.wowarmory.com"}:
        score_value -= 25
    score_value += min(20, len(item.get("markers", [])))
    return score_value


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    markers = parse_markers()
    expectations = load(EXPECT)
    primary = load(PRIMARY)
    supplement = load(SUPPLEMENT)
    accepted_urls = {norm_url(x.get("original") or x.get("logical_url", "")) for x in primary["items"] + supplement["items"]}
    # Root accepted HTTP/HTTPS alias equivalence is explicit in the v33 expectation, not inferred globally.
    aliases = {}
    for row in expectations.get("root_reviewed_https_alias_changes", []):
        if isinstance(row, dict):
            for k in ("original", "accepted_original", "https_original", "http_original"):
                if row.get(k):
                    aliases[norm_url(row[k])] = row
    executed, planned, scanned = evidence_index()
    v32 = load(V32)
    v32_by_url = {norm_url(c.get("requested_url", "")): c for c in v32.get("candidates", [])}
    legacy_exclusions = legacy_exclusion_index()

    all_rows = []
    counts = collections.Counter()
    dynamic_urls = set()
    news_urls = set()
    static_urls = set()
    nav = nav_context()
    variant_candidates = historical_variant_index(set(markers) | {norm_url(x["original"]) for x in nav})
    for url, item in markers.items():
        local_paths = {x["output_file"] for x in item["markers"]}
        dynamic = any(Path(p).suffix.lower() == ".js" for p in local_paths) or any("/js/" in p.lower() for p in local_paths)
        is_news = any("/news/" in x.get("source_url", "").lower() or "/news/" in x["output_file"].replace("\\", "/").lower() for x in item["markers"])
        if dynamic:
            dynamic_urls.add(url)
        elif is_news:
            news_urls.add(url)
        else:
            static_urls.add(url)
        v32c = v32_by_url.get(url)
        legacy = legacy_exclusions.get(url)
        if legacy:
            state = legacy["state"]
        elif url in accepted_urls or url in aliases:
            state = "saved_or_accepted"
        elif any("complete_empty_or_404" in e.get("status_hints", []) for e in executed.get(url, [])):
            state = "complete_empty_or_404"
        elif any("transport_unknown" in e.get("status_hints", []) for e in executed.get(url, [])):
            state = "transport_unknown"
        elif url in executed:
            state = "executed_evidence_needs_row_review"
        elif url in variant_candidates:
            state = "variant_only_review"
        elif v32c and v32c.get("prior_attempt") == "prior_execution_complete_404_or_no_image":
            state = "complete_empty_or_404"
        elif v32c and v32c.get("prior_attempt") == "prior_execution_record_outside_static_main01":
            state = "executed_evidence_needs_row_review"
        elif url in planned:
            state = "plan_or_queue_only"
        else:
            state = "uncovered"
        counts[state] += 1
        counts["dynamic" if dynamic else "news" if is_news else "static"] += 1
        all_rows.append({
            "requested_url": url,
            "state": state,
            "is_news": is_news,
            "is_dynamic": dynamic,
            "marker_count": len(item["markers"]),
            "markers": item["markers"][:12],
            "source_context": source_context(item),
            "historical_execution_evidence": executed.get(url, [])[:8],
            "historical_plan_or_queue_evidence": planned.get(url, [])[:8],
            "identity_variant_evidence": variant_candidates.get(url, []),
            "legacy_exclusion": legacy,
            "v32_prior_record": {
                "path": output_rel(V32),
                "prior_attempt": v32c.get("prior_attempt") if v32c else None,
                "static_main01_cdx": v32c.get("static_main01_cdx") if v32c else None,
            } if v32c else None,
            "next_step": "exclude_from_new_request" if state != "uncovered" else "fresh_exact_cdx_then_replay_if_eligible",
        })

    # Add explicit v33 navigation references to the audit ledger, including accepted rows.
    nav_unique = {x["original"] for x in nav}
    nav_by_original = {}
    for row in nav:
        nav_by_original.setdefault(row["original"], row)
    nav_states = collections.Counter("saved_or_accepted" if x["original"] in accepted_urls or x["original"] in aliases else "not_in_v33_map" for x in nav_by_original.values())

    # High-information candidates only: no historical executed evidence, no accepted map, image literal in a real page.
    candidates = []
    for row in all_rows:
        if row["state"] != "uncovered" or row["is_dynamic"]:
            continue
        if not (row["is_news"] or row["requested_url"]):
            continue
        # Keep the static frontier content focused; tiny UI and layout assets remain in the ledger but are not proposed.
        value = score(row["requested_url"], row, row["is_news"])
        path = urllib.parse.urlsplit(row["requested_url"]).path.lower()
        name = Path(path).name.lower()
        if not row["is_news"] and value < 45:
            continue
        if not row["is_news"] and any(x in name for x in ("pixel", "socket", "reagent", "recipe", "icon", "button")):
            continue
        row = dict(row)
        row["priority_score"] = value
        row["category"] = "news" if row["is_news"] else "static"
        row["selection_reason"] = "uncovered v33 missing-image marker with source page context; historical plan-only evidence is not treated as a request"
        candidates.append(row)
    news_candidates = sorted((x for x in candidates if x["is_news"]), key=lambda x: (-x["priority_score"], x["requested_url"]))
    def static_kind(row):
        path = urllib.parse.urlsplit(row["requested_url"]).path.lower()
        content_terms = ("/images/articles/", "/images/comics/", "/images/screenshots/", "/news/images/", "/contests/", "/community/images/", "/info/encyclopedia/images/", "/info/basics/images/", "/pvp/images/", "/insider/")
        chrome_terms = ("pixel", "icon", "logo", "bg", "background", "border", "button", "arrow", "spacer", "menu", "nav", "header", "footer", "data", "parch", "table", "captcha", "indicator", "prev", "next", "sponsor", "frame", "message-box", "options", "plain", "top", "bottom", "sides", "container", "dropback", "townhall-bar", "wow-bc", "wow-classic", "error", "credit")
        if any(t in path for t in content_terms) and not any(t in path for t in chrome_terms):
            return "content_visual_candidate"
        return "visible_ui_or_layout_candidate"
    static_candidates = sorted((x for x in candidates if not x["is_news"]), key=lambda x: (0 if static_kind(x) == "content_visual_candidate" else 1, -x["priority_score"], x["requested_url"]))
    for row in static_candidates:
        row["visual_role"] = static_kind(row)
    selected = news_candidates[:40] + static_candidates[:40]
    for i, row in enumerate(selected, 1):
        row["candidate_rank"] = i

    scope_reconciliation = canonical_scope_reconciliation()
    status_order = {
        "complete_empty_or_404": 0,
        "saved_or_accepted": 1,
        "executed_evidence_needs_row_review": 2,
        "transport_unknown": 3,
        "variant_only_review": 4,
        "plan_or_queue_only": 5,
        "uncovered": 6,
    }
    dedup_examples = []
    for row in sorted(all_rows, key=lambda x: (status_order.get(x["state"], 99), x["requested_url"])):
        if row["state"] == "uncovered":
            continue
        dedup_examples.append({
            "requested_url": row["requested_url"],
            "state": row["state"],
            "is_news": row["is_news"],
            "marker_count": row["marker_count"],
            "marker_refs": [
                {"output_file": marker["output_file"], "line": marker["line"], "source_url": marker["source_url"]}
                for marker in row["markers"][:2]
            ],
            "historical_execution_evidence": row["historical_execution_evidence"][:3],
            "historical_plan_or_queue_evidence": row["historical_plan_or_queue_evidence"][:3],
            "identity_variant_evidence": row["identity_variant_evidence"][:2],
            "v32_prior_record": row["v32_prior_record"],
        })
        if len(dedup_examples) >= 10:
            break
    candidate_shortlist = [
        {
            "rank": row["candidate_rank"],
            "category": row["category"],
            "state": row["state"],
            "requested_url": row["requested_url"],
            "source_refs": [
                {"output_file": marker["output_file"], "line": marker["line"], "source_url": marker["source_url"]}
                for marker in row["markers"][:2]
            ],
        }
        for row in selected
    ]

    # August 2007 evidence is kept separately: explicit full originals were accepted; other visible thumbnails are context, not guessed full URLs.
    august = [x for x in nav if "/07-08/" in x["original"]]
    august_page = SOURCE / "news" / "rss-08-2007.xml"
    august_context = {
        "page": output_rel(august_page) if august_page.exists() else None,
        "page_sha256": sha(august_page) if august_page.exists() else None,
        "explicit_navigation_originals": august,
        "interpretation": "Six explicit 07-08 full-image hrefs are already represented by the accepted navigation70 overlay; fan-art and armory entries on the same page expose thumbnails or external landing pages, not additional full-image literals. No filename expansion is proposed.",
    }

    inputs = [
        {"path": output_rel(EXPECT), "sha256": sha(EXPECT)},
        {"path": output_rel(PROVENANCE), "sha256": sha(PROVENANCE)},
        {"path": output_rel(V32), "sha256": sha(V32)},
        {"path": output_rel(PRIMARY), "sha256": sha(PRIMARY)},
        {"path": output_rel(SUPPLEMENT), "sha256": sha(SUPPLEMENT)},
        {"path": output_rel(august_page), "sha256": sha(august_page)} if august_page.exists() else {"path": output_rel(SOURCE), "sha256": None},
        {"path": output_rel(EXCLUSION_QUEUE), "sha256": sha(EXCLUSION_QUEUE)},
        *[{"path": output_rel(path), "sha256": sha(path)} for path in EXCLUSION_DOCS if path.exists()],
    ]
    frontier = {
        "schema": "wow-recovery.local-audit.resource-frontier-v33-r2.v1",
        "status": "offline_audit_only",
        "checked_utc": "2026-10-19T06:00:00Z",
        "network_requests": 0,
        "scope": "Frozen v33 missing-image markers and explicit navigation hrefs, deduplicated against accepted maps and historical execution evidence.",
        "inputs": inputs,
        "counts": {
            "missing_marker_unique_total": len(all_rows),
            "missing_marker_news_unique": len(news_urls),
            "missing_marker_static_unique": len(static_urls),
            "missing_marker_dynamic_unique": len(dynamic_urls),
            "declared_v33_scope": expectations.get("expected_static_counts", {}),
            "native_dynamic_gallery_entities": v32.get("native_dynamic_gallery", {}).get("native_entities", 3368),
            "state_counts": dict(sorted((k, v) for k, v in counts.items() if k in {"uncovered", "saved_or_accepted", "executed_evidence_needs_row_review", "complete_empty_or_404", "transport_unknown", "variant_only_review", "encoding_variant_review", "excluded_or_deferred", "plan_or_queue_only"})),
            "nav_unique": len(nav_unique),
            "nav_state_counts": dict(nav_states),
            "candidate_pool_news": len(news_candidates),
            "candidate_pool_static": len(static_candidates),
            "selected_candidates": len(selected),
            "selected_news": sum(x["is_news"] for x in selected),
            "selected_static": sum(not x["is_news"] for x in selected),
        },
        "scope_reconciliation": scope_reconciliation,
        "latest_real_network": {
            "source": "research/continuous-recovery-20261019/network/gallery-late-gap01",
            "tail": 0,
            "network_requests": 4,
            "execution_report_sha256": "5419b3c59df71946d9ff0670ccb4ebec2273eb7a6096d590fd621fb33c5b5f4b",
            "note": "Historical context only; no new request was made by this audit.",
        },
        "historical_evidence_scan": {
            "files_scanned_with_urls": len(scanned),
            "executed_url_keys": len(executed),
            "planned_or_queue_url_keys": len(planned),
            "sampled_files": scanned[:400],
        },
        "candidates": selected,
        "ledger": all_rows,
        "navigation_href_ledger": nav,
        "august_2007": august_context,
        "dynamic_scope": {
            "unique_missing_marker_urls": len(dynamic_urls),
            "native_entities_declared_by_prior_frontier": v32.get("native_dynamic_gallery", {}).get("native_entities", 3368),
            "reported_separately": True,
            "reason": "The native 3368-entity dynamic-gallery scope is a separate ledger. The smaller marker scan count is only a generated missing-image observation and must not be substituted for that scope.",
        },
        "identity_variant_candidates": variant_candidates,
        "candidate_shortlist": candidate_shortlist,
        "dedup_examples": dedup_examples,
        "legacy_exclusion_closure": {
            "source": output_rel(EXCLUSION_QUEUE),
            "source_sha256": sha(EXCLUSION_QUEUE),
            "field": "excluded_or_deferred",
            "row_count": len(legacy_exclusions),
            "state_counts": dict(collections.Counter(row["state"] for row in legacy_exclusions.values())),
            "rows": sorted(legacy_exclusions.values(), key=lambda row: row["original"]),
            "supporting_docs": [{"path": output_rel(path), "sha256": sha(path)} for path in EXCLUSION_DOCS if path.exists()],
        },
    }
    (OUT / "resource-frontier-candidates.json").write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    waves = []
    for start in range(0, len(selected), 4):
        group = selected[start:start + 4]
        waves.append({
            "wave": len(waves) + 1,
            "candidate_ranks": [x["candidate_rank"] for x in group],
            "categories": collections.Counter(x["category"] for x in group),
            "procedure": "Exact CDX first; replay only a separately reviewed eligible row. No URL guessing, no automatic pagination or redirects.",
            "max_targets": 4,
            "max_requests": 8,
            "max_duration_seconds": 180,
            "max_total_bytes": 16 * 1024 * 1024,
            "max_entity_bytes": 8 * 1024 * 1024,
            "dispatch_interval_seconds": 5.25,
            "direct_then_proxy": True,
            "tls_verify": True,
            "network_authorization": "not_requested",
        })
    plan = {
        "schema": "wow-recovery.local-audit.resource-frontier-v33-r2-plan-draft.v1",
        "status": "draft_not_executable",
        "network_requests": 0,
        "source_candidates": {"path": output_rel(OUT / "resource-frontier-candidates.json"), "sha256": sha(OUT / "resource-frontier-candidates.json")},
        "latest_real_network_tail": 0,
        "waves": waves,
        "stop_conditions": ["HTTP 429 or 503", "five consecutive transfer failures", "disk below 11005853696 bytes", "network cutoff 2026-10-19T13:15:00Z"],
        "exclusions": ["accepted maps", "complete empty/404 evidence", "plan-only treated as executed", "dynamic JS pool", "guessed filenames", "redirect following", "Zul'Aman and already complete gallery windows"],
    }
    (OUT / "resource-frontier-plan-draft.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md = []
    md.append("# v33 resource frontier audit (offline)\n")
    md.append("This audit read the frozen v33 export and historical local evidence only. It issued **0 network requests** and proposes no executable plan.\n")
    md.append("## Coverage ledger\n")
    md.append(f"- v33 `missing-image.svg` image-marker uniques observed by this scan: **{len(all_rows)}**; news **{len(news_urls)}**, static **{len(static_urls)}**, JavaScript-derived marker URLs **{len(dynamic_urls)}**. The frozen v33 expectation declares **{expectations.get('expected_static_counts', {}).get('unique_missing_images')}** static missing images / **{expectations.get('expected_static_counts', {}).get('news_unique_missing_images')}** news uniques, while the separate native dynamic-gallery ledger remains **{v32.get('native_dynamic_gallery', {}).get('native_entities', 3368)}** entities. These scopes are not merged.\n")
    md.append(f"- State counts: `{json.dumps({k: v for k, v in counts.items() if k in {'uncovered','saved_or_accepted','executed_evidence_needs_row_review','complete_empty_or_404','transport_unknown','variant_only_review','encoding_variant_review','excluded_or_deferred','plan_or_queue_only'}}, ensure_ascii=False, sort_keys=True)}`.\n")
    recon = scope_reconciliation
    md.append(f"- Canonical boundary recount: **{recon['canonical_boundary']['unique_missing_images']}** unique / **{recon['canonical_boundary']['missing_occurrences']}** occurrences across **{recon['canonical_boundary']['static_text_files']}** HTML/HTM/XML/CSS files (excluding `_origins/`); news **{recon['canonical_boundary']['news_unique_missing_images']}**. Expanded-minus-canonical is **{recon['set_reconciliation']['expanded_minus_canonical']}**: extra `_origins` **{recon['set_reconciliation']['extra_origins_unique']}**, extra JS/JS-path **{recon['set_reconciliation']['extra_dynamic_unique']}** (origin/JS overlap **{recon['set_reconciliation']['extra_origin_and_dynamic_unique']}**), other **{recon['set_reconciliation']['extra_other_unique']}**.\n")
    md.append(f"- URL normalization: {recon['url_normalization']['canonical_raw_unique']} raw unique values collapse to {recon['url_normalization']['canonical_normalized_unique']} canonical keys; explicit default-port raw values **{recon['url_normalization']['explicit_default_port_raw_unique']}**, HTTP/HTTPS same host/path groups **{recon['url_normalization']['http_https_same_host_path_groups']}**. HTTP and HTTPS remain distinct unless an accepted source-reviewed alias says otherwise.\n")
    md.append(f"- Historical evidence scan now includes output source maps and batch reports plus 20261016 publication/local-audit and 20261018 integration; URL-bearing files **{len(scanned)}**, executed URL keys **{len(executed)}**, planned/queue URL keys **{len(planned)}**. Ten representative row-level dedup examples are in `dedup_examples` in the JSON; plan-only rows remain non-executed.\n")
    md.append(f"- Explicit v33 navigation recovery: {len(nav_unique)} unique originals; {sum(1 for x in nav_by_original.values() if x['original'] in accepted_urls or x['original'] in aliases)} accepted or explicit aliases.\n")
    md.append(f"- New high-information candidate ledger: **{len(selected)}** ({sum(x['is_news'] for x in selected)} news, {sum(not x['is_news'] for x in selected)} static).\n")
    md.append(f"- The old `next-frontier-selected70.json` exclusion closure has {len(legacy_exclusions)} rows: `{json.dumps(dict(collections.Counter(row['state'] for row in legacy_exclusions.values())), ensure_ascii=False, sort_keys=True)}`. These rows are excluded before candidate selection; space-containing small-pets literals remain encoding-review only.\n")
    md.append("- The machine-readable JSON contains the complete 80-row `candidate_shortlist` with URL, state, and marker source line; it is intentionally separate from the larger ledger and dynamic 3368-entity scope.\n")
    md.append("\n## Candidate shortlist\n\n|rank|category|state|URL|source|line|\n|---:|---|---|---|---|---:|\n")
    for row in candidate_shortlist:
        source = row["source_refs"][0] if row["source_refs"] else {}
        md.append(f"|{row['rank']}|{row['category']}|{row['state']}|`{row['requested_url']}`|`{source.get('output_file', '')}`|{source.get('line', '')}|\n")
    md.append("\n## Representative row-level dedup evidence\n\nThe following ten examples show why a URL is excluded or held for review. Execution/source-map evidence is distinct from plan/queue evidence.\n\n|state|URL|execution evidence|plan/queue evidence|\n|---|---|---|---|\n")
    for row in dedup_examples:
        execution_paths = "; ".join(x["path"] for x in row["historical_execution_evidence"][:2]) or "—"
        plan_paths = "; ".join(x["path"] for x in row["historical_plan_or_queue_evidence"][:2]) or "—"
        md.append(f"|{row['state']}|`{row['requested_url']}`|`{execution_paths}`|`{plan_paths}`|\n")
    md.append("Plan-only and queue-only references remain evidence of prior planning, not requests. Exact execution/source-map evidence is excluded from the new pool even when no payload was accepted. Explicit scheme/default-port variants are retained in the machine ledger for review and are never promoted to strict same-URL success.\n")
    md.append("## August 2007 remainder\n")
    md.append("The page `news/rss-08-2007.xml` has six explicit full-image originals (`wow-bc.jpg`, `tcg01–03.jpg`, `ss01–02.jpg`). They are already in the accepted navigation70 overlay. The same page's fan-art blocks expose local thumbnails and external Blizzard landing pages; those are not new exact image URLs. No `ssN` or fan-art filename is inferred. The source page SHA and line hits are in `resource-frontier-candidates.json` under `august_2007`.\n")
    md.append("\n## Prior exclusion closure\n\nThe exact rows and reasons are recorded under `legacy_exclusion_closure`. The three encyclopedia article images are retained as complete bounded error/no-eligible evidence from the 2026-10-11 review, the lordaeron map is a complete-empty bounded interval, sponsors remain deferred, and the three literal-space small-pets paths are held for a separately reviewed URI serialization. None enters the strict candidate waves.\n")
    md.append("## Proposed bounded follow-up (draft only)\n")
    md.append("Use the generated waves only after root review: four exact targets per wave, exact CDX first, at most eight requests / 180 seconds / 16 MiB total / 8 MiB entity, TLS validation, direct then process proxy, 5.25-second dispatch spacing, no redirects or automatic pagination. Replay requires a separately reviewed eligible CDX row. Stop on 429/503, five consecutive transfer failures, disk below 11005853696 bytes, or the 13:15 UTC cutoff.\n")
    md.append("## Inputs\n")
    for item in inputs:
        md.append(f"- `{item['path']}` SHA-256 `{item['sha256']}`\n")
    md.append("\nThe latest real network tail is gallery-late-gap01 tail 0 (report SHA `5419b3c59df71946d9ff0670ccb4ebec2273eb7a6096d590fd621fb33c5b5f4b`); this audit did not modify status or reuse an older NET53 gate.\n")
    (OUT / "resource-frontier-audit.md").write_text("".join(md), encoding="utf-8")

    shortlist_md = [
        "# v33 frontier candidate shortlist (offline)\n",
        "80 exact URL candidates: 40 news and 40 static. All rows are currently `uncovered`; this is a review list, not an execution authorization.\n\n",
        "|rank|category|state|URL|source|line|\n|---:|---|---|---|---|---:|\n",
    ]
    for row in candidate_shortlist:
        source = row["source_refs"][0] if row["source_refs"] else {}
        shortlist_md.append(f"|{row['rank']}|{row['category']}|{row['state']}|`{row['requested_url']}`|`{source.get('output_file', '')}`|{source.get('line', '')}|\n")
    (OUT / "resource-frontier-shortlist.md").write_text("".join(shortlist_md), encoding="utf-8")

    receipt = {
        "schema": "wow-recovery.local-audit.resource-frontier-v33-r2-receipt.v1",
        "status": "complete_offline_audit",
        "network_requests": 0,
        "output_files": {
            "resource-frontier-candidates.json": sha(OUT / "resource-frontier-candidates.json"),
            "resource-frontier-plan-draft.json": sha(OUT / "resource-frontier-plan-draft.json"),
            "resource-frontier-audit.md": sha(OUT / "resource-frontier-audit.md"),
            "resource-frontier-shortlist.md": sha(OUT / "resource-frontier-shortlist.md"),
            "build_frontier.py": sha(Path(__file__).resolve()),
        },
        "counts": frontier["counts"],
        "validation": ["JSON reload passed", "all selected candidates have source context or explicit marker references", "no network call in audit code", "historical plan-only evidence separated from executed evidence"],
        "uncovered": ["exact historical status of rows represented only by generic source acceptance text still needs row-level review", "dynamic JS pool is counted but not proposed", "no payload accepted by this audit"],
    }
    (OUT / "resource-frontier-receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"counts": frontier["counts"], "outputs": receipt["output_files"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
