"""Bounded, read-only v29 static-resource frontier audit.

This audit reads the frozen v29 text output and prior JSON receipts only.  It
does not contact the network, read or hash image payloads, run an exporter, or
modify any frozen build/map/status artifact.  It writes only to the new
``local-audit/next-frontier-v29`` directory.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit


ROOT = Path(__file__).resolve().parents[4]
V29 = ROOT / ".scratch" / "pages-resources-20261018-v29"
OUT = ROOT / "research" / "continuous-recovery-20261018" / "local-audit" / "next-frontier-v29"
STATIC_BATCH = ROOT / "research" / "continuous-recovery-20261016" / "network" / "static-main01" / "output" / "batch-report.json"
STATIC_PLAN = ROOT / "research" / "continuous-recovery-20261016" / "network" / "static-main01" / "plan.json"
STATIC_MAP = ROOT / "research" / "continuous-recovery-20261016" / "network" / "static-main01" / "output" / "source-map.json"
STATIC_ACCEPT = ROOT / "research" / "continuous-recovery-20261016" / "publication" / "root-static-main01-source-acceptance.json"
V29_METRICS = ROOT / "research" / "continuous-recovery-20261018" / "publication" / "root-v29-static-metrics-acceptance.json"
SELECTED38 = ROOT / "research" / "continuous-recovery-20261018" / "publication" / "static-frontier-selected38.json"
NEWS_QUEUE = ROOT / "research" / "continuous-recovery-20261018" / "publication" / "news-remaining-v28-queue.json"
NATIVE_LEDGER = ROOT / "research" / "continuous-recovery-20261018" / "publication" / "native-gallery-late-window-ledger.json"

sys.path.insert(0, str(ROOT / "research" / "continuous-recovery-20261016" / "publication"))
from accept_static_resource_inventory import normalize  # noqa: E402


MARKER = re.compile(r"missing-image\.svg\?([^\"'<>\s\)]+)", re.I)
TAG = re.compile(r"<([A-Za-z][\w:-]*)\b[^>]*>", re.I | re.S)
ATTR = re.compile(r"([:\w-]+)\s*=\s*(['\"])(.*?)\2", re.S)
IMAGE_EXTS = {".jpg", ".jpeg", ".gif", ".png", ".bmp", ".webp", ".svg"}
FLOOR = 11_005_853_696
ARMORY_PARTS = ("wowarmory.com", "armory.wow-europe.com", "/armory/")
CONTENT_PARTS = (
    "/insider/", "/burningcrusade/", "/gameguide/", "/game-guide/", "/guides/",
    "/info/dungeons/", "/pvp/", "/battlegrounds/", "/encyclopedia/", "/gadgetzan/",
)
NON_CONTENT_STEMS = {
    "pixel", "spacer", "blank", "clear", "transparent", "shim", "dot", "b", "bg",
    "background", "border", "top", "bottom", "left", "right", "side", "sides",
    "button", "arrow", "bullet", "divider", "prodlistseperator", "prodlistseparator",
    "separator", "seperator", "captcha", "tl", "tr", "bl", "br", "day", "cell",
    "cell-big", "townhall-bar", "wow-bc", "wow-classic", "icon_o", "icon_n", "icon_u",
    "icon_h", "header", "footer", "nav", "logo", "loading",
    "hr", "line", "rule",
}
LAYOUT_WORDS = NON_CONTENT_STEMS | {
    "bevel", "dropback", "container", "circle", "splash", "title", "box", "tab",
    "parchment", "meta-mini", "orange-mini", "close", "data", "tip", "team",
}
CONTENT_TOKENS = {
    "photo": 30, "screenshot": 32, "ss": 24, "thumb": 22, "movie": 26,
    "artwork": 32, "art": 22, "concept": 30, "wallpaper": 30, "fanart": 28,
    "map": 24, "battleground": 28, "lordaeron": 26, "nagrand": 26,
    "bladesedge": 26, "magtheridon": 26, "illidan": 26, "outland": 24,
    "bestiary": 28, "encyclopedia": 28, "article": 24, "malfurion": 26,
    "small pets": 24, "cat": 20, "hugescreen": 24, "gadget": 24,
    "contest": 20, "holiday": 20, "sponsor": 18, "arena": 24, "anatomy": 24,
    "warrior": 22, "warlock": 22, "mages": 22, "interview": 24,
}
ITEM_TOKENS = {"reagent", "recipe", "socket", "reward", "mount", "item", "inv_", "icons", "icon"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def is_image_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
        return parsed.scheme in {"http", "https"} and Path(parsed.path).suffix.lower() in IMAGE_EXTS
    except ValueError:
        return False


def is_news(source: str, output_file: str, target: str) -> bool:
    low = f"{source} {output_file} {target}".lower()
    return output_file.startswith("news/") or "/news/" in low or "/rss-" in low or "news." in low


def page_class(source: str, target: str) -> str:
    low_source = source.lower()
    low_target = target.lower()
    if any(part in low_target for part in ARMORY_PARTS):
        return "armory"
    if any(part in low_source or part in low_target for part in CONTENT_PARTS):
        return "guide_bc_insider"
    return "other_static"


def marker_role(target: str, context: dict | None = None) -> str:
    path = urlsplit(target).path.lower()
    stem = Path(path).stem.lower()
    if stem in LAYOUT_WORDS or any(token in stem for token in ("pixel", "spacer", "blank", "border", "parchment")):
        return "layout_or_placeholder_candidate"
    if any(part in path for part in ARMORY_PARTS) or "/icons/" in path or stem in {"icon", "icons"} or stem.startswith(("socket_", "inv_", "reagent", "recipe")):
        return "icon_or_small_visual_candidate"
    return "content_visual_candidate"


def topic_for(source: str, target: str, category: str) -> str:
    low = f"{source} {target}".lower()
    if "insider" in low:
        return "Insider"
    if "burningcrusade" in low or "/bc/" in low:
        return "Burning Crusade"
    if "battleground" in low or "/pvp/" in low:
        return "PvP or battleground guide"
    if "gameguide" in low or "game-guide" in low or "/guides/" in low or "/info/dungeons/" in low:
        return "Game Guide"
    if "encyclopedia" in low:
        return "Encyclopedia knowledge image"
    if "contest" in low or "holiday" in low:
        return "Event or contest"
    if "gadgetzan" in low:
        return "Gadgetzan guide"
    if category == "armory":
        return "Armory item or small icon"
    return "Other static site visual"


def parse_attrs(tag: str) -> dict:
    result = {}
    for match in ATTR.finditer(tag):
        key = match.group(1).lower()
        value = " ".join(html.unescape(match.group(3)).split())
        result[key] = value[:500]
    return result


def context_for(text: str, marker_start: int) -> dict:
    line_start = text.rfind("\n", 0, marker_start) + 1
    line_end = text.find("\n", marker_start)
    if line_end < 0:
        line_end = len(text)
    line = " ".join(html.unescape(text[line_start:line_end]).split())
    window_start = max(0, marker_start - 1800)
    window_end = min(len(text), marker_start + 1800)
    nearby = text[window_start:window_end]
    containing = []
    for tag_match in TAG.finditer(nearby):
        absolute_start = window_start + tag_match.start()
        absolute_end = window_start + tag_match.end()
        if absolute_start <= marker_start <= absolute_end:
            containing.append((tag_match, absolute_start, absolute_end))
    if containing:
        tag_match, _, _ = containing[-1]
        tag = html.unescape(tag_match.group(0))
        attrs = parse_attrs(tag)
        return {
            "kind": tag_match.group(1).lower(),
            "attributes": attrs,
            "alt": attrs.get("alt"),
            "title": attrs.get("title"),
            "snippet": " ".join(tag.split())[:500],
            "line_snippet": line[:360],
        }
    # CSS url() and malformed fragments do not have an enclosing HTML tag.
    return {
        "kind": "line_or_css",
        "attributes": {},
        "alt": None,
        "title": None,
        "snippet": line[:500],
        "line_snippet": line[:360],
    }


def recursive_strings(value):
    if isinstance(value, dict):
        for nested in value.values():
            yield from recursive_strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from recursive_strings(nested)
    elif isinstance(value, str):
        yield value


def evidence_kind(path: Path) -> str:
    name = path.name.lower()
    if any(token in name for token in ("plan", "candidate", "queue")):
        return "plan_or_queue"
    if any(token in name for token in ("batch-report", "request-record", "source-map", "sanitized-summary")):
        return "execution_or_receipt"
    return "other_json"


def canonical_scan() -> tuple[dict, dict, dict, int, int, int]:
    """Return canonical v23-style file hashes, marker counters, and rows."""
    files = {}
    counter = Counter()
    news = Counter()
    rows = defaultdict(lambda: {"occurrences": 0, "originals": set(), "sources": set(), "refs": []})
    all_markers = 0
    marker_files = set()
    if not V29.exists():
        raise RuntimeError(f"missing frozen v29 output: {V29}")
    for path in V29.rglob("*"):
        if not path.is_file():
            continue
        relpath = path.relative_to(V29).as_posix()
        if relpath.startswith("_origins/") or path.suffix.lower() not in {".html", ".htm", ".xml", ".css"}:
            continue
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        files[relpath] = hashlib.sha256(raw).hexdigest()
        matches = list(MARKER.finditer(text))
        if matches:
            marker_files.add(relpath)
        for match in matches:
            all_markers += 1
            params = parse_qs(html.unescape(match.group(1)), keep_blank_values=True)
            original = unquote(params.get("requested", [""])[0])
            source = unquote(params.get("source", [""])[0])
            if not original:
                continue
            parsed = urlsplit(original)
            if parsed.scheme not in {"http", "https"} or Path(parsed.path.lower()).suffix not in IMAGE_EXTS:
                continue
            key = normalize(original)
            counter[key] += 1
            if relpath.startswith("news/"):
                news[key] += 1
            row = rows[key]
            row["occurrences"] += 1
            row["originals"].add(original)
            if source:
                row["sources"].add(source)
            if len(row["refs"]) < 8:
                line = text.count("\n", 0, match.start()) + 1
                row["refs"].append({
                    "output_file": f".scratch/pages-resources-20261018-v29/{relpath}",
                    "line": line,
                    "source_page": source,
                    "reason": params.get("reason", [""])[0],
                    "context": context_for(text, match.start()),
                })
    return files, counter, news, all_markers, len(marker_files), rows


def load_static_results():
    data = json.loads(STATIC_BATCH.read_text(encoding="utf-8")) if STATIC_BATCH.exists() else {}
    results = {}
    for entry in data.get("results", []):
        for value in (entry.get("canonical"), entry.get("requested"), entry.get("original")):
            if value:
                results[normalize(value)] = entry
        for row in (entry.get("cdx") or {}).get("rows", []):
            value = row.get("original")
            if value:
                results.setdefault(normalize(value), entry)
    accepted = set()
    if STATIC_ACCEPT.exists():
        data = json.loads(STATIC_ACCEPT.read_text(encoding="utf-8"))
        accepted.update(normalize(x.get("original", "")) for x in data.get("accepted_images", []) if x.get("original"))
    return data, results, accepted


def collect_json_evidence():
    """Index exact URL evidence without opening payloads or sending requests."""
    roots = [ROOT / "research" / directory for directory in (
        "continuous-recovery-20261015", "continuous-recovery-20261016", "continuous-recovery-20261018",
    )]
    paths = []
    for base in roots:
        if not base.exists():
            continue
        for path in base.rglob("*.json"):
            if OUT in path.parents:
                continue
            if any(token in path.name.lower() for token in (
                "batch-report", "request-record", "source-map", "sanitized-summary", "plan", "candidates", "queue", "acceptance", "receipt",
            )):
                paths.append(path)
    index = defaultdict(list)
    for path in sorted(set(paths)):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        url_values = set()
        for value in recursive_strings(data):
            if value.startswith(("http://", "https://")) and is_image_url(value):
                url_values.add(value)
        kind = evidence_kind(path)
        path_rel = rel(path)
        for value in url_values:
            index[normalize(value)].append({"path": path_rel, "kind": kind, "exact": value})

        def add_context(node):
            if isinstance(node, dict):
                node_urls = [value for value in node.values() if isinstance(value, str) and value.startswith(("http://", "https://")) and is_image_url(value)]
                details = {key: node[key] for key in (
                    "status", "category", "reason", "source_status", "transport_error", "unrequested_reason",
                    "cdx_parse_error", "selected_capture", "query_performed", "body_bytes",
                ) if key in node}
                if node_urls and details:
                    for value in node_urls:
                        index[normalize(value)].append({"path": path_rel, "kind": kind, "exact": value, "details": details})
                for nested in node.values():
                    add_context(nested)
            elif isinstance(node, list):
                for nested in node:
                    add_context(nested)

        add_context(data)
    return index, len(set(paths))


def cdx_summary(entry: dict | None) -> dict:
    if not entry:
        return {"status": "not_in_static_main01", "complete": None, "selected": [], "rows": 0, "first_timestamp": None, "accepted_payloads": 0, "statuscodes": {}}
    cdx = entry.get("cdx") or {}
    rows = cdx.get("rows") or []
    selected = cdx.get("selected") or []
    statuscodes = Counter(str(row.get("statuscode")) for row in rows if row.get("statuscode") is not None)
    return {
        "status": entry.get("status"),
        "cdx_source": entry.get("cdx_source"),
        "complete": bool(cdx.get("status", "").startswith("complete") and not cdx.get("potential_truncation", True)),
        "selected": [
            {"timestamp": item.get("timestamp"), "original": item.get("original"), "digest": item.get("digest"), "mimetype": item.get("mimetype"), "statuscode": item.get("statuscode"), "length": item.get("length"), "replay_url": item.get("replay_url")}
            for item in selected[:3]
        ],
        "rows": len(rows),
        "first_timestamp": rows[0].get("timestamp") if rows else None,
        "latest_unknown": bool(entry.get("latest_unknown")),
        "replay_count": len(entry.get("replay_results") or []),
        "accepted_payloads": len(entry.get("accepted_payloads") or []),
        "statuscodes": dict(statuscodes),
    }


def exclusion_sets() -> tuple[set[str], set[str]]:
    selected = json.loads(SELECTED38.read_text(encoding="utf-8"))
    selected_keys = {normalize(row.get("requested_url", "")) for row in selected.get("rows", []) if row.get("requested_url")}
    queue = json.loads(NEWS_QUEUE.read_text(encoding="utf-8"))
    queue_keys = {normalize(row.get("original", "")) for row in queue.get("rows", []) if row.get("original")}
    return selected_keys, queue_keys


def non_content_reason(target: str, role: str) -> str | None:
    parsed = urlsplit(target)
    stem = Path(parsed.path).stem.lower()
    if role == "layout_or_placeholder_candidate":
        return "layout_or_placeholder_visual_role"
    if stem in NON_CONTENT_STEMS:
        return "known_ui_or_non_content_stem"
    # Old pages commonly name decorative repeat-x/slice assets with a suffix
    # rather than the bare words caught by the role classifier.  Keep genuine
    # maps, photos, screenshots, and artwork, but do not promote CSS chrome,
    # title strips, corner pieces, or error panels into the content frontier.
    compact = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    if compact.endswith(("bg", "background", "-top", "-bottom", "-left", "-right", "-side", "-title", "-header", "-footer", "-box", "-error")):
        return "decorative_background_or_layout_suffix"
    if compact in {"bg", "background", "nosponsor"} or compact.startswith("bg-"):
        return "decorative_background_or_layout_name"
    if compact.startswith(("townhall-bar-", "indicator")) or compact.startswith(("wow-bc-", "wow-classic-")) or "buttonback" in compact:
        return "known_ui_or_non_content_stem"
    if "/support/" in parsed.path.lower() and stem in {"prodlistseperator", "prodlistseparator"}:
        return "support_layout_separator"
    return None


def priority_score(row: dict) -> int:
    target = row["requested_url"].lower()
    path = urlsplit(target).path.lower()
    stem = Path(path).stem.lower()
    score = 0
    if row["visual_role"] == "content_visual_candidate":
        score += 100
    elif row["visual_role"] == "icon_or_small_visual_candidate":
        score += 25
    if row["category"] == "guide_bc_insider":
        score += 12
    elif row["category"] == "other_static":
        score += 8
    if Path(path).suffix.lower() in {".jpg", ".jpeg", ".png"}:
        score += 8
    for token, value in CONTENT_TOKENS.items():
        if token == "ss":
            if re.search(r"(?:^|[-_/])ss\d+(?:[-_.]|$)", path):
                score += value
        elif token in target:
            score += value
    for token in ITEM_TOKENS:
        if token in target:
            score += 4
    score += min(row["occurrences_in_v29_missing_markers"], 20)
    if row["prior_attempt"] == "no_matching_execution_or_cdx_record_found":
        score += 3
    if row["prior_attempt"] == "prior_execution_transport_unknown":
        score += 2
    if row["category"] == "armory":
        score -= 100
    if stem.endswith("float"):
        score += 5
    return score


def next_step(prior: str) -> str:
    if prior == "prior_execution_transport_unknown":
        return "new_bounded_exact_CDX_window_then_replay_if_eligible"
    if prior == "plan_or_queue_only_no_execution_record":
        return "new_exact_CDX_window_then_replay_if_eligible; plan evidence is not execution"
    if prior == "prior_execution_record_outside_static_main01":
        return "verify outside-batch receipt, then use a new exact CDX/replay window"
    if prior == "static_main01_attempted":
        return "review the existing CDX/replay candidate before any new bounded request"
    return "new_exact_CDX_window_then_replay_if_eligible"


def prior_attempt_for(static_entry, static_status, evidence_rows):
    execution = [item for item in evidence_rows if item["kind"] == "execution_or_receipt"]
    plan = [item for item in evidence_rows if item["kind"] == "plan_or_queue"]
    details = [item.get("details", {}) for item in execution if item.get("details")]
    if static_entry:
        status = str(static_status.get("status") or "")
        if status == "complete_no_eligible_capture":
            if any(str(code) == "404" for code in static_status.get("statuscodes", {})):
                return "prior_execution_complete_404_or_no_image"
            return "complete_cdx_no_eligible_capture"
        if status.startswith("transport"):
            return "prior_execution_transport_unknown"
        if static_status.get("accepted_payloads", 0):
            return "already_accepted_static_payload"
        return "static_main01_attempted"
    if any(item.get("details", {}).get("transport_error") is True or item.get("details", {}).get("reason") in {"no_http_status", "transport_error"} for item in details):
        return "prior_execution_transport_unknown"
    if any("404" in str(item.get("details", {}).get("category", "")).lower() or "404" in str(item.get("details", {}).get("reason", "")).lower() for item in details):
        return "prior_execution_complete_404_or_no_image"
    if execution:
        return "prior_execution_record_outside_static_main01"
    if plan:
        return "plan_or_queue_only_no_execution_record"
    return "no_matching_execution_or_cdx_record_found"


def build_row(key, value, source_hash_cache, static_results, accepted, evidence_index):
    originals = sorted(value["originals"])
    requested = originals[0]
    source = sorted(value["sources"])[0] if value["sources"] else ""
    refs = list(value["refs"])
    page_file = ROOT / refs[0]["output_file"]
    if page_file not in source_hash_cache:
        source_hash_cache[page_file] = {"sha256": sha256(page_file), "bytes": page_file.stat().st_size}
    static_entry = static_results.get(key)
    status = cdx_summary(static_entry)
    evidence_rows = evidence_index.get(key, [])
    prior = prior_attempt_for(static_entry, status, evidence_rows)
    if key in accepted or status.get("accepted_payloads", 0):
        prior = "already_accepted_static_payload"
    category = page_class(source, requested)
    role = marker_role(requested, refs[0].get("context"))
    alt_values = sorted({ref.get("context", {}).get("alt") for ref in refs if ref.get("context", {}).get("alt")})
    title_values = sorted({ref.get("context", {}).get("title") for ref in refs if ref.get("context", {}).get("title")})
    first_context = refs[0].get("context", {})
    for ref in refs:
        ref["source_page_sha256"] = source_hash_cache[page_file]["sha256"] if ref["output_file"] == refs[0]["output_file"] else None
    return {
        "requested_url": requested,
        "observed_originals": originals,
        "normalized_identity": key,
        "category": category,
        "topic": topic_for(source, requested, category),
        "visual_role": role,
        "expected_visual_role": "content photo, screenshot, illustration, map, or knowledge image" if role == "content_visual_candidate" else "small/item/icon visual (lower priority)",
        "occurrences_in_v29_missing_markers": value["occurrences"],
        "source_pages_count": len(value["sources"]),
        "source_pages": sorted(value["sources"])[:8],
        "references": refs,
        "marker_context": first_context,
        "observed_alt_texts": alt_values,
        "observed_title_texts": title_values,
        "source_output_page": refs[0]["output_file"],
        "source_output_page_sha256": source_hash_cache[page_file]["sha256"],
        "source_output_page_bytes": source_hash_cache[page_file]["bytes"],
        "prior_attempt": prior,
        "static_main01_cdx": status,
        "existing_json_evidence": {
            "execution_or_receipt": [item for item in evidence_rows if item["kind"] == "execution_or_receipt"][:8],
            "plan_or_queue_only": [item for item in evidence_rows if item["kind"] == "plan_or_queue"][:8],
            "other": [item for item in evidence_rows if item["kind"] == "other_json"][:4],
        },
        "complete_cdx_cache": status.get("complete") if static_entry else None,
        "known_cdx_or_replay_date": status.get("first_timestamp"),
        "next_step": next_step(prior),
        "selection_note": "Static marker and local evidence only; this audit sent no CDX, replay, or image request.",
    }


def native_scope() -> dict:
    data = json.loads(NATIVE_LEDGER.read_text(encoding="utf-8"))
    return {
        "ledger_path": rel(NATIVE_LEDGER),
        "ledger_sha256": sha256(NATIVE_LEDGER),
        "separate_from_static_missing_counts": True,
        "scope": data.get("scope"),
        "counter_summary": "79 archive404, 47 transportunknown, 3242 not requested",
        "current_windows": data.get("rows", []),
        "followup": data.get("followup"),
        "network_requests_by_ledger": data.get("network_requests_by_ledger"),
    }


def main() -> None:
    free_before = shutil.disk_usage(ROOT).free
    if free_before < FLOOR:
        raise RuntimeError(f"D: below floor before audit: {free_before}")
    files, counter, news, all_markers, marker_file_count, marker_rows = canonical_scan()
    metrics = json.loads(V29_METRICS.read_text(encoding="utf-8"))
    expected = {
        "static_text_files": 1104,
        "unique_missing_images": 1066,
        "missing_occurrences": 1821,
        "news_unique_missing_images": 436,
        "news_missing_occurrences": 436,
        "all_placeholder_markers": 1873,
    }
    observed = {
        "static_text_files": len(files),
        "unique_missing_images": len(counter),
        "missing_occurrences": sum(counter.values()),
        "news_unique_missing_images": len(news),
        "news_missing_occurrences": sum(news.values()),
        "all_placeholder_markers": all_markers,
    }
    if not metrics.get("accepted") or any(observed[key] != value for key, value in expected.items()):
        raise RuntimeError(f"canonical v29 metric mismatch: observed={observed} expected={expected} acceptance={metrics.get('accepted')}")
    static_batch, static_results, static_accepted = load_static_results()
    evidence, evidence_file_count = collect_json_evidence()
    selected38, news_queue = exclusion_sets()
    source_hash_cache = {}
    all_rows = []
    for key, value in marker_rows.items():
        requested = sorted(value["originals"])[0]
        parsed = urlsplit(requested)
        source = sorted(value["sources"])[0] if value["sources"] else ""
        output_file = value["refs"][0]["output_file"] if value["refs"] else ""
        if parsed.scheme not in {"http", "https"} or not is_image_url(requested):
            continue
        row = build_row(key, value, source_hash_cache, static_results, static_accepted, evidence)
        row["is_news"] = is_news(source, output_file, requested)
        row["has_query_or_fragment"] = bool(parsed.query or parsed.fragment)
        row["frozen_exclusion"] = "static-frontier-selected38" if key in selected38 else ("news-remaining-v28-queue" if key in news_queue else None)
        row["non_content_reason"] = non_content_reason(requested, row["visual_role"])
        row["priority_score"] = priority_score(row)
        all_rows.append(row)

    excluded_counts = Counter()
    candidates = []
    for row in all_rows:
        if row["is_news"]:
            excluded_counts["news_marker"] += 1
            continue
        if row["has_query_or_fragment"]:
            excluded_counts["query_or_fragment"] += 1
            continue
        if row["frozen_exclusion"]:
            excluded_counts[row["frozen_exclusion"]] += 1
            continue
        if row["prior_attempt"] in {"already_accepted_static_payload", "complete_cdx_no_eligible_capture", "prior_execution_complete_404_or_no_image"}:
            excluded_counts[row["prior_attempt"]] += 1
            continue
        if row["non_content_reason"]:
            excluded_counts[row["non_content_reason"]] += 1
            continue
        candidates.append(row)

    candidates.sort(key=lambda row: (-row["priority_score"], -row["occurrences_in_v29_missing_markers"], row["requested_url"]))
    non_armory = [row for row in candidates if row["category"] != "armory"]
    armory = [row for row in candidates if row["category"] == "armory"]
    selected = non_armory[:80]
    if len(selected) < 80:
        selected.extend(armory[: min(8, 80 - len(selected))])
    for index, row in enumerate(selected, 1):
        row["priority_rank"] = index
    selected_keys = {row["normalized_identity"] for row in selected}
    for row in candidates:
        if row["normalized_identity"] not in selected_keys:
            row["not_selected_reason"] = "candidate_pool_above_80_cap"

    prior_counts = Counter(row["prior_attempt"] for row in candidates)
    all_non_news_prior_counts = Counter(row["prior_attempt"] for row in all_rows if not row["is_news"])
    category_counts = Counter(row["category"] for row in candidates)
    role_counts = Counter(row["visual_role"] for row in candidates)
    output = {
        "schema": "wow-recovery.local-audit.next-frontier-v29.v1",
        "checked_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "network_requests": 0,
        "scope": "Frozen v29 canonical HTML/HTM/XML/CSS missing-image markers excluding news and native JS gallery targets; no raw image payloads were read or hashed.",
        "inputs": {
            "v29_output": rel(V29),
            "v29_export_provenance_sha256": sha256(V29 / "export-provenance.json"),
            "v29_static_metrics_acceptance": rel(V29_METRICS),
            "v29_static_metrics_acceptance_sha256": sha256(V29_METRICS),
            "static_main01_batch_report": rel(STATIC_BATCH),
            "static_main01_batch_report_sha256": sha256(STATIC_BATCH) if STATIC_BATCH.exists() else None,
            "static_main01_plan": rel(STATIC_PLAN),
            "static_main01_plan_sha256": sha256(STATIC_PLAN) if STATIC_PLAN.exists() else None,
            "static_main01_source_map": rel(STATIC_MAP),
            "static_main01_source_map_sha256": sha256(STATIC_MAP) if STATIC_MAP.exists() else None,
            "static_main01_acceptance": rel(STATIC_ACCEPT),
            "static_main01_acceptance_sha256": sha256(STATIC_ACCEPT) if STATIC_ACCEPT.exists() else None,
            "static_frontier_selected38": rel(SELECTED38),
            "static_frontier_selected38_sha256": sha256(SELECTED38),
            "news_remaining_v28_queue": rel(NEWS_QUEUE),
            "news_remaining_v28_queue_sha256": sha256(NEWS_QUEUE),
            "native_gallery_ledger": rel(NATIVE_LEDGER),
            "native_gallery_ledger_sha256": sha256(NATIVE_LEDGER),
        },
        "canonical_scan": {
            "static_text_files": len(files),
            "marker_files": marker_file_count,
            "all_placeholder_markers": all_markers,
            "unique_missing_images": len(counter),
            "missing_occurrences": sum(counter.values()),
            "news_unique_missing_images": len(news),
            "news_missing_occurrences": sum(news.values()),
            "non_news_unique_missing_images": len(counter) - len(news),
            "non_news_missing_occurrences": sum(counter.values()) - sum(news.values()),
            "root_acceptance_match": observed == expected,
        },
        "evidence_json_files_indexed": evidence_file_count,
        "static_main01_batch_summary": {
            "batch_id": static_batch.get("batch_id"),
            "network_requests": static_batch.get("network_requests"),
            "source_responses": static_batch.get("source_responses"),
            "candidate_count": static_batch.get("candidate_count"),
            "stop_reason": static_batch.get("stop_reason"),
            "accepted_payloads": len(static_batch.get("accepted_payloads") or []),
        },
        "frozen_exclusions": {
            "static_frontier_selected38_count": len(selected38),
            "news_remaining_v28_queue_count": len(news_queue),
            "selection_rule": "Exact normalized identity exclusion; plan/queue evidence is not execution evidence.",
        },
        "candidate_pool": {
            "before_cap": len(candidates),
            "selected": len(selected),
            "available_by_category": dict(category_counts),
            "available_by_visual_role": dict(role_counts),
            "available_by_prior_attempt": dict(prior_counts),
            "selected_by_category": dict(Counter(row["category"] for row in selected)),
            "selected_by_visual_role": dict(Counter(row["visual_role"] for row in selected)),
            "excluded_counts": dict(excluded_counts),
        },
        "evidence_state_coverage": {
            "non_news_all_marker_rows_by_prior_attempt": dict(all_non_news_prior_counts),
            "candidate_pool_by_prior_attempt": dict(prior_counts),
            "state_definitions": {
                "complete_cdx_no_eligible_capture": "Explicit complete CDX window with no eligible image capture and no 404 row.",
                "prior_execution_complete_404_or_no_image": "Execution/CDX evidence contains a complete 404 or no-image result; not re-queued in this frontier.",
                "prior_execution_transport_unknown": "Execution evidence records transport or HTTP status unknown; requires a new bounded window.",
                "plan_or_queue_only_no_execution_record": "Only plan/queue evidence exists; this is not an executed request.",
                "no_matching_execution_or_cdx_record_found": "No matching local execution/CDX evidence found.",
            },
        },
        "native_dynamic_gallery": native_scope(),
        "selection_policy": {
            "maximum": 80,
            "priority": "Photos, screenshots, illustrations, maps, knowledge visuals, and event visuals first; item/resource images next; Armory icon rows only as a final remainder up to eight.",
            "layout_filter": "Pure border, pixel, spacer, UI separator, captcha, and known tab/corner assets are excluded.",
            "evidence_rule": "complete CDX empty/404 and already accepted rows are not re-queued; transport_unknown, plan-only, outside-receipt, and uncovered remain distinct.",
            "native_gallery_rule": "3368/native JS50 gallery targets stay in a separate ledger and are not counted as static candidates.",
        },
        "candidates": selected,
        "uncovered_or_excluded_summary": {
            "not_selected_after_cap": len(candidates) - len(selected),
            "known_attempts_not_requeued": dict({key: value for key, value in excluded_counts.items() if key in {"already_accepted_static_payload", "complete_cdx_no_eligible_capture", "prior_execution_complete_404_or_no_image"}}),
            "plan_only_is_not_request": True,
            "image_payload_hashing": False,
        },
        "disk_free_before_bytes": free_before,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    out_json = OUT / "next-frontier-v29-candidates.json"
    out_md = OUT / "next-frontier-v29-candidates.md"
    receipt = OUT / "next-frontier-v29-audit-receipt.json"
    out_json.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# v29 next static frontier audit",
        "",
        f"Checked `{output['checked_utc']}`; network requests: `0`; canonical static text files: `{len(files)}`; marker files: `{marker_file_count}`.",
        f"Canonical missing-image scope: `{len(counter)}` unique / `{sum(counter.values())}` occurrences; news excluded: `{len(news)}` unique / `{sum(news.values())}` occurrences.",
        f"Candidate pool after news, frozen selected38/news49, query, accepted/complete-empty, and pure-layout exclusions: `{len(candidates)}`; selected `{len(selected)}`.",
        "",
        "The table records exact literal URL, source output line and page SHA, marker context/alt, and prior local evidence. Plan-only records never count as an executed request. Native JS50/3368 gallery targets are listed separately and are not in the static count.",
        "",
        "|#|topic|visual role|occurrences|prior attempt|CDX complete|URL|source page:line|alt|",
        "|---:|---|---|---:|---|---|---|---|---|",
    ]
    for row in selected:
        reference = row["references"][0]
        alt = row["observed_alt_texts"][0] if row["observed_alt_texts"] else ""
        lines.append(
            f"|{row['priority_rank']}|{row['topic']}|{row['visual_role']}|{row['occurrences_in_v29_missing_markers']}|{row['prior_attempt']}|{row['complete_cdx_cache']}|{row['requested_url']}|{reference['output_file']}:{reference['line']}|{alt}|"
        )
    lines += [
        "",
        "## Evidence boundaries",
        "",
        "- Existing JSON plans, batch reports, source maps, and receipts were read locally only; this audit made no CDX, replay, or image request.",
        "- Page SHA values hash frozen v29 source pages, not missing image payloads. No image payload was opened or hashed.",
        "- Exact selected38 and news-remaining-v28 identities are excluded by normalized identity; duplicate complete windows and accepted/complete-empty captures are not re-queued.",
        "- `transport_unknown`, `plan_or_queue_only_no_execution_record`, and `no_matching_execution_or_cdx_record_found` remain separate evidence states.",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")
    free_after = shutil.disk_usage(ROOT).free
    if free_after < FLOOR:
        raise RuntimeError(f"D: below floor after audit writes: {free_after}")
    receipt.write_text(json.dumps({
        "schema": "wow-recovery.local-audit.next-frontier-v29.receipt.v1",
        "candidate_sha256": sha256(out_json),
        "markdown_sha256": sha256(out_md),
        "network_requests": 0,
        "image_payloads_read_or_hashed": 0,
        "disk_free_before_bytes": free_before,
        "disk_free_after_bytes": free_after,
        "selected": len(selected),
        "candidate_pool_before_cap": len(candidates),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "json": rel(out_json),
        "markdown": rel(out_md),
        "receipt": rel(receipt),
        "candidate_sha256": sha256(out_json),
        "markdown_sha256": sha256(out_md),
        "receipt_sha256": sha256(receipt),
        "selected": len(selected),
        "candidate_pool_before_cap": len(candidates),
        "counts": output["candidate_pool"],
        "disk_free_before": free_before,
        "disk_free_after": free_after,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
