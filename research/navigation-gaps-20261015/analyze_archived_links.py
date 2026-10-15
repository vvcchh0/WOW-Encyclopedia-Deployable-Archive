#!/usr/bin/env python3
"""Classify every explicit ``__offline/missing`` link in Archived News.

No URL is fetched.  The requested URL is decoded from the existing local HTML,
then compared with the existing local route map so an already-present same
origin page is not mistaken for a missing capture.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXPORT = ROOT / ".scratch/pages-local-maintenance-20261014-v5"
WOW_HOSTS = {"worldofwarcraft.com", "www.worldofwarcraft.com"}
SOCIAL_HOSTS = {
    "forums.worldofwarcraft.com",
    "www.penny-arcade.com",
    "pc.gamespy.com",
    "www.gamespy.com",
    "www.wowhead.com",
}
BUSINESS_WORDS = {
    "account",
    "billing",
    "character-move",
    "character-transfer",
    "signup",
    "subscription",
    "payment",
    "shop.",
    "support",
}
SENSITIVE_LOCAL_PREFIXES = (
    "/account",
    "/loginsupport",
    "/community/submission",
    "/ptr",
)


def route_candidates(path: str) -> list[str]:
    values = [path]
    if path.endswith("/"):
        values.append(path[:-1] or "/")
    else:
        values.append(path + "/")
    return list(dict.fromkeys(values))


def normalize_link_route(href: str, base_path: str) -> str:
    parsed = urlsplit(href)
    path = unquote(parsed.path or "/")
    prefix = base_path.rstrip("/") + "/"
    if path.startswith(prefix):
        path = "/" + path[len(prefix) :].lstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    return path


def month_route_row(
    href: str,
    count: int,
    routes: dict[str, str],
    base_path: str,
    export_root: Path,
) -> dict[str, object]:
    route = normalize_link_route(href, base_path)
    route_key = next((candidate for candidate in route_candidates(route) if candidate in routes), None)
    target = routes.get(route_key) if route_key else None
    export_file = None
    export_exists = False
    if target:
        prefix = base_path.rstrip("/") + "/"
        relative = target[len(prefix) :] if target.startswith(prefix) else target.lstrip("/")
        export_file = relative
        export_exists = (export_root / relative).is_file()
    source_candidates: list[str] = []
    for base in (ROOT / "offline/site", ROOT / "mirror/20080512/www.worldofwarcraft.com"):
        for candidate in (base / route.lstrip("/"), base / route.lstrip("/") / "index.html"):
            if candidate.is_file():
                source_candidates.append(candidate.relative_to(ROOT).as_posix())
    if route_key and export_exists:
        status = "content_route"
    elif route_key:
        status = "broken_export_route"
    elif source_candidates:
        status = "local_source_but_route_missing"
    else:
        status = "missing_export_route"
    return {
        "href": href,
        "route": route,
        "occurrences": count,
        "status": status,
        "route_key": route_key,
        "export_target": target,
        "export_file": export_file,
        "source_candidates": list(dict.fromkeys(source_candidates)),
    }


def classify_requested(requested: str, routes: dict[str, str], base_path: str, root: Path) -> dict[str, object]:
    parsed = urlsplit(requested)
    host = (parsed.hostname or "").casefold()
    path = parsed.path or "/"
    if host in WOW_HOSTS:
        route_key = next((candidate for candidate in route_candidates(path) if candidate in routes), None)
        target = routes.get(route_key) if route_key else None
        route_variants = [
            re.sub(r"/{2,}", "/", path),
            path.replace(".shtml", ".html"),
            path.replace("/info/info/", "/info/"),
            path.replace("/classes/druids/", "/classes/druid/"),
        ]
        near_key = next(
            (candidate for candidate in route_variants if candidate != path and candidate in routes),
            None,
        )
        local_candidates: list[str] = []
        for base in (root / "offline/site", root / "mirror/20080512/www.worldofwarcraft.com"):
            for candidate in (base / path.lstrip("/"), base / path.lstrip("/") / "index.html"):
                if candidate.is_file():
                    local_candidates.append(candidate.relative_to(root).as_posix())
        if near_key:
            prefix = base_path.rstrip("/") + "/"
            near_target = routes.get(near_key, "")
            near_rel = near_target[len(prefix) :] if near_target.startswith(prefix) else near_target.lstrip("/")
            return {
                "requested_host": host,
                "requested_path": path,
                "requested_route": path,
                "route_key": near_key,
                "route_exists": True,
                "route_near_match": True,
                "export_target": near_target,
                "export_relative_path": unquote(near_rel),
                "local_source_candidates": local_candidates,
                "classification": "local_route_near_match",
            }
        if route_key:
            prefix = base_path.rstrip("/") + "/"
            target_rel = target[len(prefix) :] if target.startswith(prefix) else target.lstrip("/")
            return {
                "requested_host": host,
                "requested_path": path,
                "requested_route": path,
                "route_key": route_key,
                "route_exists": True,
                "export_target": target,
                "export_relative_path": unquote(target_rel),
                "local_source_candidates": local_candidates,
                "classification": "local_route_but_placeholder",
            }
        if any(path == prefix or path.startswith(prefix + "/") for prefix in SENSITIVE_LOCAL_PREFIXES):
            classification = "security_staticized_business"
        elif local_candidates:
            classification = "local_source_but_route_missing"
        else:
            classification = "local_source_gap_or_unresolved"
        return {
            "requested_host": host,
            "requested_path": path,
            "requested_route": path,
            "route_key": None,
            "route_exists": False,
            "export_target": None,
            "export_relative_path": None,
            "local_source_candidates": local_candidates,
            "classification": classification,
        }
    lowered = f"{host}{path}".casefold()
    if host in SOCIAL_HOSTS or any(token in lowered for token in ("forum", "penny-arcade", "gamespy")):
        classification = "external_social_or_forum_staticized"
    elif any(token in lowered for token in BUSINESS_WORDS):
        classification = "security_staticized_business"
    else:
        classification = "external_uncollected_staticized"
    return {
        "requested_host": host,
        "requested_path": path,
        "requested_route": None,
        "route_key": None,
        "route_exists": False,
        "export_target": None,
        "export_relative_path": None,
        "local_source_candidates": [],
        "classification": classification,
    }


def analyze_page(
    page: Path,
    route_map: dict[str, object],
    source_label: str,
    export_root: Path,
) -> dict[str, object]:
    text = page.read_text(encoding="utf-8", errors="replace")
    # Count links plus the two historical JS guard strings that carry the
    # same requested URLs.  They are still page-local references and should
    # not disappear from the evidence count.
    pattern = re.compile(r"(?P<quote>[\"'])(?P<url>[^\"']*__offline/missing\.html\?[^\"']*)(?P=quote)", re.I)
    routes = route_map.get("routes", {}) if isinstance(route_map, dict) else {}
    base_path = str(route_map.get("base_path") or "/") if isinstance(route_map, dict) else "/"
    links: list[dict[str, object]] = []
    for index, match in enumerate(pattern.finditer(text), 1):
        raw = html.unescape(match.group("url"))
        query = parse_qs(urlsplit(raw).query)
        requested = unquote(query.get("requested", [""])[0])
        source = unquote(query.get("source", [""])[0])
        reason = query.get("reason", [""])[0]
        prefix = text[max(0, match.start() - 16) : match.start()].lower()
        attribute = "href" if "href" in prefix else "src" if "src" in prefix else "script_string"
        row = {
            "occurrence": index,
            "attribute": attribute,
            "raw_placeholder": raw,
            "source_url": source,
            "requested_url": requested,
            "reason": reason,
        }
        row.update(classify_requested(requested, routes if isinstance(routes, dict) else {}, base_path, ROOT))
        links.append(row)
    groups: dict[tuple[str, str, str], dict[str, object]] = {}
    for row in links:
        key = (str(row.get("classification")), str(row.get("requested_host")), str(row.get("requested_path")))
        group = groups.setdefault(
            key,
            {
                "classification": row.get("classification"),
                "requested_host": row.get("requested_host"),
                "requested_path": row.get("requested_path"),
                "requested_url_examples": [],
                "occurrences": [],
                "reasons": [],
                "route_key": row.get("route_key"),
                "export_target": row.get("export_target"),
            },
        )
        if row["requested_url"] not in group["requested_url_examples"]:
            group["requested_url_examples"].append(row["requested_url"])
        group["occurrences"].append(row["occurrence"])
        if row["reason"] not in group["reasons"]:
            group["reasons"].append(row["reason"])
    month_matches = re.findall(
        r"href\s*=\s*([\"'])(?P<href>[^\"']*?/news/wow-news-[^\"']+?\.html(?:#[^\"']*)?)\1",
        text,
        re.I,
    )
    month_counts = Counter(str(match[1]) for match in month_matches)
    routes_dict = routes if isinstance(routes, dict) else {}
    news_months = [
        month_route_row(href, count, routes_dict, base_path, export_root)
        for href, count in sorted(month_counts.items())
    ]
    return {
        "source": source_label,
        "page": page.relative_to(ROOT).as_posix(),
        "placeholder_occurrences": len(links),
        "classification_counts": dict(Counter(str(row["classification"]) for row in links)),
        "links": links,
        "deduplicated_targets": sorted(groups.values(), key=lambda item: (str(item["classification"]), str(item["requested_host"]), str(item["requested_path"]))),
        "news_months": news_months,
    }


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Archived News missing-link analysis (local-only)",
        "",
        "No URLs were fetched. Each row decodes the existing `requested=` query from an `__offline/missing.html` link and compares same-origin paths with the existing route map.",
        "",
    ]
    for page in report["pages"]:
        lines.extend(
            [
                f"## {page['source']}",
                "",
                f"Page: `{page['page']}`; placeholder occurrences: **{page['placeholder_occurrences']}**.",
                "",
                "| Classification | Count | Meaning |",
                "| --- | ---: | --- |",
            ]
        )
        meanings = {
            "local_route_but_placeholder": "same-origin target already has an export route; candidate for local-link rewrite review",
            "local_route_near_match": "same-origin target has a close route variant in the export; candidate URL rewrite/alias bug",
            "local_source_but_route_missing": "local source file exists but no exact export route; candidate route integration bug",
            "local_source_gap_or_unresolved": "same-origin target has no current route; queue exact baseline capture or source review",
            "security_staticized_business": "account/support/payment/business target kept as a static historical exhibit",
            "external_social_or_forum_staticized": "external social/forum target intentionally left uncollected",
            "external_uncollected_staticized": "other external or uncollected target retained as explicit missing link",
        }
        for key, count in sorted(page["classification_counts"].items()):
            lines.append(f"| `{key}` | {count} | {meanings.get(key, '')} |")
        lines.extend(["", "| # | Classification | Requested host/path | Reason | Export route |", "| ---: | --- | --- | --- | --- |"])
        for row in page["links"]:
            route = row.get("route_key") or "—"
            lines.append(
                f"| {row['occurrence']} | `{row['classification']}` | `{row['requested_host']}{row['requested_path']}` | `{row['reason']}` | `{route}` |"
            )
        lines.extend(["", "Deduplicated targets:", ""])
        for target in page["deduplicated_targets"]:
            lines.append(
                f"- `{target['classification']}` `{target['requested_host']}{target['requested_path']}` — {len(target['occurrences'])} occurrence(s); route `{target.get('route_key') or '—'}`."
            )
        lines.extend(["", "Internal monthly news links:", ""])
        lines.extend(
            [
                "| Href | Normalized route | Occurrences | Status | Export file | Local source candidates |",
                "| --- | --- | ---: | --- | --- | --- |",
            ]
        )
        for month in page.get("news_months", []):
            lines.append(
                f"| `{month['href']}` | `{month['route']}` | {month['occurrences']} | `{month['status']}` | `{month.get('export_file') or '—'}` | `{', '.join(month.get('source_candidates', [])) or '—'}` |"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--export", type=Path, default=DEFAULT_EXPORT)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    root = args.root.resolve()
    export_root = args.export.resolve()
    route_map_path = export_root / "__offline/route-map.json"
    route_map = json.loads(route_map_path.read_text(encoding="utf-8"))
    pages = [
        analyze_page(root / "offline/site/info/archivednews.html", route_map, "frozen offline/site", export_root),
        analyze_page(export_root / "info/archivednews.html", route_map, "v5 GitHub Pages preview", export_root),
    ]
    report = {
        "schema": "archived-news-missing-links/v1",
        "network_performed": False,
        "route_map": route_map_path.relative_to(root).as_posix(),
        "pages": pages,
    }
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "archived-links.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "archived-links.md").write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"pages": [(p["source"], p["placeholder_occurrences"], p["classification_counts"]) for p in pages]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
