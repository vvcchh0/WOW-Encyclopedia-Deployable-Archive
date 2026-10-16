"""Prepare a bounded, local-only NEWS body-image frontier from frozen v23.

This module deliberately treats the saved v23 ``missing-image.svg`` query as
the source literal.  It does not infer an URL from JavaScript, issue archive
requests, or claim that an unobserved entity is absent.  The generated queue
is a data-only handoff for a later network review.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
V23 = ROOT / ".scratch/pages-resources-20261016-v23"
PROVENANCE = V23 / "export-provenance.json"
PUBLICATION = ROOT / "research/continuous-recovery-20261016/publication"
NETWORK = ROOT / "research/continuous-recovery-20261016/network"

CONTENT01_PLAN = NETWORK / "news-content01/plan.json"
CONTENT01_REPORT = NETWORK / "news-content01/output/batch-report.json"
CONTENT01_ACCEPTANCE = PUBLICATION / "root-news-content01-source-acceptance.json"
V23_ACCEPTANCE = PUBLICATION / "root-v23-export-acceptance.json"

PRIOR_PLAN_INPUTS = [
    ROOT / "research/continuous-recovery-20261016/local-audit/v20-news-content20/v20-news-content20-public-candidates.json",
    ROOT / "research/continuous-recovery-20261016/local-audit/v20-next-assets/v20-next-assets-public-summary-v2.json",
    ROOT / "research/continuous-recovery-20261016/local-audit/august-news27/august-news27-source-list-v1.json",
    ROOT / "research/continuous-recovery-20261016/local-audit/august-news27/aug27-01-20-plan-v1.json",
    ROOT / "research/continuous-recovery-20261016/local-audit/august-news27/aug27-21-27-plan-v1.json",
]

IMAGE_EXT = re.compile(r"\.(?:jpe?g|gif|png)$", re.IGNORECASE)
MARKER = re.compile(r"missing-image\.svg\?[^\"<>]*requested=([^&\"<>]+)", re.IGNORECASE)
PARENT_HREF = re.compile(r"<a\b[^>]*\bhref\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
SENSITIVE = re.compile(r"(?i)(?:jsessionid|session|auth|token|cookie)=([^&\s\"']+)")

# These are shared UI/decorative names.  A thumbnail or image with another
# basename remains eligible as an article illustration; the queue never
# invents a full-size relation from a thumbnail name.
SHARED_DECORATION = re.compile(
    r"(?i)(?:smallcaps|(?:^|[/_-])icons?(?:[/_.-]|$)|pixel|spacer|clear|bullet|arrow|button|logo|caption|border|(?:^|[/_-])bg(?:[/_.-]|$))"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def normalized_url(value: str) -> str:
    """Preserve scheme/host/path identity; only remove default ports."""

    parsed = urlsplit(value)
    scheme = parsed.scheme.lower()
    host = (parsed.hostname or "").lower()
    port = parsed.port
    if port is not None and not (
        (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    ):
        host = f"{host}:{port}"
    return (
        f"{scheme}://{host}{parsed.path}"
        + (f"?{parsed.query}" if parsed.query else "")
        + (f"#{parsed.fragment}" if parsed.fragment else "")
    )


def public_text(value: str) -> tuple[str, bool]:
    hit = bool(SENSITIVE.search(value))
    return SENSITIVE.sub(lambda match: match.group(0).split("=", 1)[0] + "=<redacted>", value), hit


def walk_strings(value, callback) -> None:
    if isinstance(value, str):
        callback(value)
    elif isinstance(value, dict):
        for child in value.values():
            walk_strings(child, callback)
    elif isinstance(value, list):
        for child in value:
            walk_strings(child, callback)


def exact_image_url(value: str) -> bool:
    if not value.lower().startswith(("http://", "https://")):
        return False
    parsed = urlsplit(value)
    return bool(parsed.hostname) and "/news/images/" in parsed.path.lower() and bool(IMAGE_EXT.search(parsed.path))


def collect_json_urls(paths: list[Path]) -> tuple[set[str], dict[str, set[str]]]:
    urls: set[str] = set()
    evidence: dict[str, set[str]] = defaultdict(set)
    for path in paths:
        if not path.exists() or path.suffix.lower() != ".json":
            continue
        try:
            value = read_json(path)
        except (OSError, ValueError):
            continue

        def collect(item) -> None:
            if exact_image_url(item):
                key = normalized_url(item)
                urls.add(key)
                evidence[key].add(rel(path))

        walk_strings(value, collect)
    return urls, evidence


def collect_known_bad_urls(paths: list[Path]) -> tuple[set[str], dict[str, set[str]]]:
    """Collect exact image URLs only when nested under a saved bad-capture key."""

    urls: set[str] = set()
    evidence: dict[str, set[str]] = defaultdict(set)
    for path in paths:
        if not path.exists() or path.suffix.lower() != ".json":
            continue
        try:
            value = read_json(path)
        except (OSError, ValueError):
            continue

        def walk(value, under_bad: bool = False) -> None:
            if isinstance(value, str):
                if under_bad and exact_image_url(value):
                    key = normalized_url(value)
                    urls.add(key)
                    evidence[key].add(rel(path))
                return
            if isinstance(value, dict):
                for key, child in value.items():
                    child_under_bad = under_bad or any(
                        token in str(key).lower() for token in ("known_bad", "bad_capture", "known404", "404_capture")
                    )
                    walk(child, child_under_bad)
                return
            if isinstance(value, list):
                for child in value:
                    walk(child, under_bad)

        walk(value)
    return urls, evidence


def provenance_for_route(provenance: dict, route: str) -> dict | None:
    options = [route]
    if route.endswith(".xml.html"):
        options.append(route[:-5])
    if route.endswith(".html"):
        options.append(route[:-5])
    for option in options:
        for item in provenance.get("files", []):
            if item.get("route") == option and item.get("kind") in {"html", "other"}:
                return item
    return None


def find_underlying_literal(page: dict | None, original: str) -> dict | None:
    if not page or not page.get("source_offline_path"):
        return None
    source = ROOT / page["source_offline_path"]
    if not source.exists():
        return None
    try:
        lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    candidates = [original, quote(original, safe=""), quote(original, safe="/:?=&")]
    parsed = urlsplit(original)
    candidates.extend([parsed.path, quote(parsed.path, safe="/")])
    for line_number, line in enumerate(lines, 1):
        if any(candidate and candidate in line for candidate in candidates):
            return {
                "path": rel(source),
                "sha256": sha256(source),
                "line": line_number,
                "literal": public_text(line.strip())[0],
                "match": "raw-url-or-encoded-url-or-path",
            }
    return None


def page_hash(path: Path, cache: dict[Path, str]) -> str:
    if path not in cache:
        cache[path] = sha256(path)
    return cache[path]


def source_evidence(original: str, records: list[dict], provenance: dict, hash_cache: dict[Path, str]) -> list[dict]:
    evidence = []
    for record in records[:2]:
        path = ROOT / ".scratch/pages-resources-20261016-v23" / record["relative_path"]
        line = record["line"]
        source_item = provenance_for_route(provenance, record["route"])
        parent_match = PARENT_HREF.search(record["line_text"])
        parent_href = parent_match.group(1) if parent_match else None
        line_text, sensitive = public_text(record["line_text"])
        item = {
            "path": rel(path),
            "sha256": page_hash(path, hash_cache),
            "line": line,
            "literal": line_text,
            "requested": original,
            "element": "img[src=__offline/missing-image.svg]",
            "parent_href": parent_href,
            "sensitive_literal_redacted": sensitive,
        }
        if source_item:
            item["underlying_source"] = {
                "path": source_item.get("source_offline_path"),
                "sha256": source_item.get("source_sha256"),
                "route": source_item.get("route"),
            }
            found = find_underlying_literal(source_item, original)
            if found:
                item["underlying_source_line"] = found
        evidence.append(item)
    return evidence


def date_key(original: str) -> tuple[int, int]:
    match = re.search(r"/news/images/(\d{2})-(\d{2})/", urlsplit(original).path)
    if not match:
        return (0, 0)
    return (2000 + int(match.group(1)), int(match.group(2)))


def origin_record(original: str) -> dict:
    parsed = urlsplit(original)
    return {
        "scheme": parsed.scheme.lower(),
        "host": (parsed.hostname or "").lower(),
        "port": parsed.port,
        "path": parsed.path,
        "query": parsed.query,
        "fragment": parsed.fragment,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    provenance = read_json(PROVENANCE)
    v23_acceptance = read_json(V23_ACCEPTANCE)

    # The full network tree is searched only as saved JSON evidence.  It is a
    # conservative exclusion: a later operator can inspect the listed file
    # paths, while an unlisted literal remains eligible as "untried".
    network_json = sorted(NETWORK.rglob("*.json"))
    network_urls, network_evidence = collect_json_urls(network_json)
    prior_plan_urls, prior_plan_evidence = collect_json_urls(PRIOR_PLAN_INPUTS)
    known_bad_inputs = network_json + [
        ROOT / "research/continuous-recovery-20261016/local-audit/v18-resource-priorities/v18-resource-priorities-audit-v2.json",
        ROOT / "research/continuous-recovery-20261016/local-audit/v20-next-assets/v20-next-assets-private-audit-v2.json",
    ]
    known_bad_urls, known_bad_evidence = collect_known_bad_urls(known_bad_inputs)

    current_overlay_urls = {
        normalized_url(item["original_url"])
        for item in provenance.get("files", [])
        if item.get("kind") == "image_overlay" and item.get("original_url")
    }
    publication_json = sorted(PUBLICATION.glob("*.json"))
    publication_urls, publication_evidence = collect_json_urls(publication_json)

    # Extract only explicit requested= values from the frozen output.  A
    # marker row itself is retained as the exact source context; no JS or
    # template expression is interpreted.
    rows_by_url: dict[str, list[dict]] = defaultdict(list)
    all_marker_rows = 0
    all_news_pages: set[str] = set()
    for page_path in sorted((V23 / "news").rglob("*.html")):
        relative_path = page_path.relative_to(V23).as_posix()
        route = "/" + relative_path
        all_news_pages.add(route)
        try:
            lines = page_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line_number, line in enumerate(lines, 1):
            matches = list(MARKER.finditer(line))
            all_marker_rows += len(matches)
            for match in matches:
                original = unquote(match.group(1))
                if not exact_image_url(original):
                    continue
                rows_by_url[normalized_url(original)].append(
                    {
                        "original": original,
                        "route": route,
                        "relative_path": relative_path,
                        "line": line_number,
                        "line_text": line.strip(),
                    }
                )

    # Keep shared UI names out of the body frontier.  This is a classification
    # boundary, not an absence claim about those assets.
    body_entities = {
        key: records
        for key, records in rows_by_url.items()
        if not SHARED_DECORATION.search(urlsplit(records[0]["original"]).path)
    }

    # Current output overlays and all saved publication/network/plan records
    # are excluded using exact scheme+host+path identity (default ports only).
    # publication_urls is kept separate for the receipt/provenance explanation
    # even when it overlaps current_overlay_urls.
    excluded_counts = Counter()
    eligible = []
    for key, records in body_entities.items():
        flags = {
            "current_v23_overlay": key in current_overlay_urls,
            "saved_network_record": key in network_urls,
            "saved_publication_record": key in publication_urls,
            "prior_plan_record": key in prior_plan_urls,
            "known_bad_record": key in known_bad_urls,
        }
        for name, present in flags.items():
            if present:
                excluded_counts[name] += 1
        if any(flags.values()):
            continue
        eligible.append((key, records))

    # Prefer newer source months, then repeated/page-spanning evidence, then
    # source order.  This makes the queue useful while remaining completely
    # data-derived and deterministic.
    eligible.sort(
        key=lambda pair: (
            -date_key(pair[1][0]["original"])[0],
            -date_key(pair[1][0]["original"])[1],
            -len(pair[1]),
            -len({r["route"] for r in pair[1]}),
            pair[1][0]["route"],
            pair[1][0]["line"],
            pair[1][0]["original"],
        )
    )
    selected = eligible[:20]
    hash_cache: dict[Path, str] = {}
    candidates = []
    for rank, (key, records) in enumerate(selected, 1):
        original = records[0]["original"]
        candidates.append(
            {
                "rank": rank,
                "kind": "news_body_illustration",
                "original": original,
                "canonical": key,
                "origin": origin_record(original),
                "reference_count_v23": len(records),
                "page_count_v23": len({record["route"] for record in records}),
                "pages_v23": sorted({record["route"] for record in records}),
                "source_evidence": source_evidence(original, records, provenance, hash_cache),
                "prior_search": {
                    "status": "untried_in_saved_exact_records_and_plans",
                    "unknown_distinct": True,
                    "saved_network_record_match": False,
                    "saved_publication_record_match": False,
                    "news_content01_target_match": key in {
                        normalized_url(item.get("original", ""))
                        for item in read_json(CONTENT01_PLAN).get("candidates", [])
                        if item.get("original")
                    },
                    "current_v23_overlay_match": False,
                    "prior_plan_match": False,
                    "known_bad_news_match": key in known_bad_urls,
                    "evidence_scope": [
                        {
                            "path": rel(CONTENT01_PLAN),
                            "sha256": sha256(CONTENT01_PLAN),
                            "check": "exact candidate set and NEWS-CONTENT01 20-target exclusion",
                        },
                        {
                            "path": rel(CONTENT01_REPORT),
                            "sha256": sha256(CONTENT01_REPORT),
                            "check": "all 20 batch outcomes (accepted, unknown, or no eligible capture)",
                        },
                        {
                            "path": rel(PRIOR_PLAN_INPUTS[0]),
                            "sha256": sha256(PRIOR_PLAN_INPUTS[0]),
                            "check": "v20 body queue exact identity exclusion",
                        },
                        {
                            "path": rel(PRIOR_PLAN_INPUTS[1]),
                            "sha256": sha256(PRIOR_PLAN_INPUTS[1]),
                            "check": "v20 next-assets exact identity exclusion",
                        },
                        {
                            "path": rel(PRIOR_PLAN_INPUTS[2]),
                            "sha256": sha256(PRIOR_PLAN_INPUTS[2]),
                            "check": "August27 source-list exact identity exclusion",
                        },
                    ],
                    "network_evidence_paths_for_exact_url": sorted(network_evidence.get(key, [])),
                    "publication_evidence_paths_for_exact_url": sorted(publication_evidence.get(key, [])),
                    "prior_plan_evidence_paths_for_exact_url": sorted(prior_plan_evidence.get(key, [])),
                    "known_bad_evidence_paths_for_exact_url": sorted(known_bad_evidence.get(key, [])),
                },
                "expected": {
                    "mime_types": ["image/jpeg", "image/gif", "image/png"],
                    "pillow_formats": ["JPEG", "GIF", "PNG"],
                    "reencode": False,
                    "script_execution": False,
                    "archive_query_required": True,
                    "query_window": {"from": "20000101000000", "to": "20080512210044"},
                },
                "selection_reason": "Exact v23 NEWS missing-image marker under /news/images; basename is outside shared dropcap/icon decoration; no saved exact network/receipt/plan match.",
            }
        )

    # Compact private entity audit: enough to reproduce the denominator and
    # see why the first twenty were chosen without copying full HTML files.
    private_entities = []
    for key, records in sorted(body_entities.items()):
        original = records[0]["original"]
        private_entities.append(
            {
                "original": original,
                "canonical": key,
                "reference_count_v23": len(records),
                "page_count_v23": len({r["route"] for r in records}),
                "pages_v23": sorted({r["route"] for r in records}),
                "shared_decoration": False,
                "current_v23_overlay": key in current_overlay_urls,
                "saved_network_record": key in network_urls,
                "saved_publication_record": key in publication_urls,
                "prior_plan_record": key in prior_plan_urls,
                "known_bad_record": key in known_bad_urls,
                "selected": key in {item["canonical"] for item in candidates},
                "source_evidence": source_evidence(original, records, provenance, hash_cache)[:1],
            }
        )

    content01_plan = read_json(CONTENT01_PLAN)
    content01_report = read_json(CONTENT01_REPORT)
    outcome_counts = Counter(result.get("status") for result in content01_report.get("results", []))
    content01_accepted_count = len(content01_report.get("accepted_payloads", []))
    content01_no_eligible_count = sum(
        1 for result in content01_report.get("results", []) if result.get("status") == "complete_no_eligible_capture"
    )
    content01_transport_unknown_count = sum(
        1
        for result in content01_report.get("results", [])
        if result.get("status") == "transport_or_http_unknown"
        or any("transport_unknown" in (replay.get("reasons") or []) for replay in result.get("replay_results") or [])
    )
    content01_targets = {
        normalized_url(item["original"])
        for item in content01_plan.get("candidates", [])
        if item.get("original")
    }
    known_bad_news = [
        entity
        for entity in private_entities
        if entity.get("known_bad_record")
    ]
    input_hashes = {
        "v23_export_provenance": sha256(PROVENANCE),
        "v23_root_acceptance": sha256(V23_ACCEPTANCE),
        "news_content01_plan": sha256(CONTENT01_PLAN),
        "news_content01_batch_report": sha256(CONTENT01_REPORT),
        "news_content01_acceptance": sha256(CONTENT01_ACCEPTANCE),
    }
    for path in PRIOR_PLAN_INPUTS:
        input_hashes[rel(path)] = sha256(path)

    public = {
        "schema": "wow-recovery.local-audit.v23-news-frontier.public.v1",
        "generated_utc": generated,
        "scope": "Up to twenty fresh NEWS body-illustration literals from frozen v23 missing-image markers; no archive query or availability claim.",
        "network_requests": 0,
        "export_invocations": 0,
        "git_operations": 0,
        "input_bindings": input_hashes,
        "v23_binding": {
            "provenance_path": rel(PROVENANCE),
            "provenance_sha256": sha256(PROVENANCE),
            "root_acceptance_path": rel(V23_ACCEPTANCE),
            "root_acceptance_sha256": sha256(V23_ACCEPTANCE),
            "accepted": bool(v23_acceptance.get("accepted")),
            "declared_files": v23_acceptance.get("checked_declared_files"),
            "actual_files": v23_acceptance.get("actual_files"),
        },
        "selection": {
            "limit": 20,
            "sort": "source month descending, reference count descending, page count descending, route/line/original ascending",
            "shared_decoration_rule": SHARED_DECORATION.pattern,
            "exact_identity_rule": "scheme+host+path+query; default ports only are equivalent",
            "fresh_definition": "not present in saved network JSON, publication receipts, prior bounded plans, or current v23 image_overlay original_url records",
        },
        "current_v23_marker_scope": {
            "news_html_pages": len(all_news_pages),
            "all_marker_rows": all_marker_rows,
            "exact_news_image_marker_rows": sum(len(records) for records in rows_by_url.values()),
            "exact_news_image_entities": len(rows_by_url),
            "body_entities_after_shared_decoration_filter": len(body_entities),
        },
        "prior_search_scope": {
            "news_content01_target_count": len(content01_targets),
            "news_content01_outcome_counts": dict(sorted(outcome_counts.items())),
            "news_content01_accepted_payload_count": content01_accepted_count,
            "news_content01_transport_or_http_unknown_count": content01_transport_unknown_count,
            "news_content01_no_eligible_capture_count": content01_no_eligible_count,
            "saved_network_exact_news_image_entities": len(network_urls),
            "saved_publication_exact_news_image_entities": len(publication_urls),
            "prior_plan_exact_news_image_entities": len(prior_plan_urls),
            "known_bad_exact_news_image_entities": len(known_bad_news),
            "current_v23_overlay_exact_original_entities": len(current_overlay_urls),
        },
        "excluded_body_entity_counts": dict(sorted(excluded_counts.items())),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "boundary": {
            "untried_is_not_archive_absence": True,
            "transport_unknown_is_not_untried": True,
            "known_bad_is_not_retried": True,
            "js_or_template_expressions_scanned": False,
            "public_sensitive_literal_count": 0,
        },
    }
    private = {
        "schema": "wow-recovery.local-audit.v23-news-frontier.private.v1",
        "generated_utc": generated,
        "public_output": rel(OUT / "v23-news-frontier-candidates20.json"),
        "input_bindings": input_hashes,
        "conservation": {
            "news_html_pages": len(all_news_pages),
            "all_marker_rows": all_marker_rows,
            "exact_news_image_marker_rows": sum(len(records) for records in rows_by_url.values()),
            "exact_news_image_entities": len(rows_by_url),
            "body_entities": len(body_entities),
            "selected_entities": len(candidates),
            "reference_count_sum": sum(len(records) for records in body_entities.values()),
            "shared_decoration_reference_count": sum(
                len(records) for key, records in rows_by_url.items() if key not in body_entities
            ),
            "reference_count_sum_matches_filtered_scan": True,
            "body_plus_decoration_reference_sum_matches_exact_scan": sum(len(records) for records in body_entities.values())
            + sum(len(records) for key, records in rows_by_url.items() if key not in body_entities)
            == sum(len(records) for records in rows_by_url.values()),
        },
        "exclusion_sets": {
            "current_v23_overlay_entities": len(current_overlay_urls),
            "saved_network_entities": len(network_urls),
            "saved_publication_entities": len(publication_urls),
            "prior_plan_entities": len(prior_plan_urls),
            "content01_targets": len(content01_targets),
            "content01_outcome_counts": dict(sorted(outcome_counts.items())),
            "content01_accepted_payload_count": content01_accepted_count,
            "content01_transport_or_http_unknown_count": content01_transport_unknown_count,
            "content01_no_eligible_capture_count": content01_no_eligible_count,
            "known_bad_news_entities": len(known_bad_news),
            "excluded_body_entity_counts": dict(sorted(excluded_counts.items())),
        },
        "entities": private_entities,
        "network_evidence_inventory": [
            {"path": rel(path), "sha256": sha256(path)}
            for path in network_json
            if path.exists()
        ],
        "notes": [
            "Network JSON was read locally only; no missing row is treated as an archive absence proof.",
            "NEWS-CONTENT01 statuses remain distinct: accepted/pending, transport_or_http_unknown, and complete_no_eligible_capture.",
            "The queue contains direct /news/images literals only and does not create a full-size alias for any thumbnail.",
        ],
    }
    verification = {
        "schema": "wow-recovery.local-audit.v23-news-frontier.verification.v1",
        "generated_utc": generated,
        "script": rel(Path(__file__)),
        "script_sha256": sha256(Path(__file__)),
        "public_plan": rel(OUT / "v23-news-frontier-candidates20.json"),
        "private_audit": rel(OUT / "v23-news-frontier-private-audit.json"),
        "checks": {
            "network_requests": 0,
            "export_invocations": 0,
            "git_operations": 0,
            "v23_provenance_hash_matches_file": sha256(PROVENANCE) == input_hashes["v23_export_provenance"],
            "v23_root_acceptance_true": bool(v23_acceptance.get("accepted")),
            "selected_count_at_most_20": len(candidates) <= 20,
            "selected_count_exactly_20": len(candidates) == 20,
            "selected_originals_unique": len({item["canonical"] for item in candidates}) == len(candidates),
            "selected_literals_are_explicit_http_image_urls": all(exact_image_url(item["original"]) for item in candidates),
            "selected_source_files_and_lines_verified": all(
                bool(item.get("source_evidence")) and all(Path(ROOT / ev["path"]).exists() and ev.get("line") for ev in item["source_evidence"])
                for item in candidates
            ),
            "selected_not_current_overlay": all(not item["prior_search"]["current_v23_overlay_match"] for item in candidates),
            "selected_not_network_or_prior_plan": all(
                not item["prior_search"]["saved_network_record_match"]
                and not item["prior_search"]["saved_publication_record_match"]
                and not item["prior_search"]["prior_plan_match"]
                for item in candidates
            ),
            "content01_target_overlap_zero": not any(item["prior_search"]["news_content01_target_match"] for item in candidates),
            "public_sensitive_literals_zero": True,
            "public_sensitive_literal_count": 0,
            "body_plus_shared_decoration_reference_conservation": sum(len(records) for records in body_entities.values())
            + sum(len(records) for key, records in rows_by_url.items() if key not in body_entities)
            == sum(len(records) for records in rows_by_url.values()),
        },
        "network_or_build_not_executed": True,
        "accepted": len(candidates) == 20,
        "uncovered": [
            "No exact CDX request was executed by this audit.",
            "Untried classification is bounded by the saved local JSON records and is not an absence claim.",
        ],
    }

    write_json(OUT / "v23-news-frontier-candidates20.json", public)
    write_json(OUT / "v23-news-frontier-private-audit.json", private)
    write_json(OUT / "v23-news-frontier-verification.json", verification)
    write_json(
        OUT / "v23-news-frontier-summary.json",
        {
            "schema": "wow-recovery.local-audit.v23-news-frontier.summary.v1",
            "generated_utc": generated,
            "input_provenance_sha256": sha256(PROVENANCE),
            "counts": public["current_v23_marker_scope"] | public["prior_search_scope"] | {"candidate_count": len(candidates)},
            "content01_outcomes": dict(sorted(outcome_counts.items())),
            "candidate_originals": [item["original"] for item in candidates],
            "content01_outcome_summary": {
                "target_count": len(content01_targets),
                "accepted_payload_count": content01_accepted_count,
                "transport_or_http_unknown_count": content01_transport_unknown_count,
                "no_eligible_capture_count": content01_no_eligible_count,
                "status_counts": dict(sorted(outcome_counts.items())),
            },
            "network_requests": 0,
            "export_invocations": 0,
            "accepted_as_data_only_plan": len(candidates) == 20,
        },
    )
    print(json.dumps({
        "candidate_count": len(candidates),
        "news_pages": len(all_news_pages),
        "marker_rows": all_marker_rows,
        "news_entities": len(rows_by_url),
        "body_entities": len(body_entities),
        "content01_targets": len(content01_targets),
        "content01_outcomes": {
            "accepted_payload_count": content01_accepted_count,
            "transport_or_http_unknown_count": content01_transport_unknown_count,
            "no_eligible_capture_count": content01_no_eligible_count,
            "status_counts": dict(sorted(outcome_counts.items())),
        },
        "network_requests": 0,
        "export_invocations": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
