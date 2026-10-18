#!/usr/bin/env python3
"""Prepare the additive v33 browser input with the late 19 source-bound references.

The original ``v33-browser-input.json`` is immutable.  This preparer reuses its
accepted image/provenance closure, reads the accepted source-plan evidence for
the late navigation/static rows, verifies each row against the actual v33 HTML,
and writes only ``v33-browser-input-r2.json``.  It never launches Playwright,
performs HTTP, changes maps, or rewrites the r1 input.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import importlib.util
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[5]
R1_PATH = HERE / "prepare_v33_browser.py"
R1_INPUT = HERE / "v33-browser-input.json"
INPUT = HERE / "v33-browser-input-r2.json"
OUTPUT = ROOT / ".scratch/pages-resources-20261018-v33"
NAVIGATION_CORRECTION = ROOT / "research/continuous-recovery-20261018/local-audit/static-frontier-v32/static-frontier-v32-navigation-exclusion-correction.json"
STATIC40_PLAN = ROOT / "research/continuous-recovery-20261018/network/static40-v32/batch-04/plan.json"
STATIC40_QUEUE = ROOT / "research/continuous-recovery-20261018/network/static40-v32/static40-source-queue.json"
STATIC40_SOURCE = ROOT / "research/continuous-recovery-20261018/publication/root-static40-batch4-source-acceptance.json"
STATIC40_PUBLIC = ROOT / "research/continuous-recovery-20261018/publication/root-static40-batch4-public-copy-acceptance.json"
NEWS_BODY_PLAN = ROOT / "research/continuous-recovery-20261018/network/news-body-2008-v26/batch-02/plan.json"
NEWS_BODY_SOURCE = ROOT / "research/continuous-recovery-20261018/publication/root-transfer-pending2-v2-batch1-source-acceptance.json"
NEWS_BODY_PUBLIC = ROOT / "research/continuous-recovery-20261018/publication/root-transfer-pending2-v2-batch1-public-copy-acceptance.json"
BASE_PATH = "/WOW-Encyclopedia-Deployable-Archive/"

NAVIGATION_TARGETS = (
    "http://www.worldofwarcraft.com/news/images/07-08/ss01.jpg",
    "http://www.worldofwarcraft.com/news/images/07-08/ss02.jpg",
    "http://www.worldofwarcraft.com/news/images/07-07/comic-full.jpg",
    "http://www.worldofwarcraft.com/news/images/07-11/comic1.jpg",
    "http://www.worldofwarcraft.com/news/images/07-11/comic2.jpg",
    "http://www.worldofwarcraft.com/info/basics/images/trade/ss01.jpg",
    "http://www.worldofwarcraft.com/info/basics/images/trade/ss02.jpg",
    "http://www.worldofwarcraft.com/info/basics/images/trade/ss03.jpg",
    "http://www.worldofwarcraft.com/news/images/04-08/leipzig_02.jpg",
    "http://www.worldofwarcraft.com/news/images/04-08/leipzig_03.jpg",
    "http://www.worldofwarcraft.com/news/images/04-08/leipzig_04.jpg",
    "http://www.worldofwarcraft.com/news/images/04-08/leipzig_05.jpg",
)
STATIC_TARGETS = (
    "http://www.worldofwarcraft.com/news/images/08-02/02-06-08-3.jpg",
    "http://www.wowarmory.com/images/icons/21x21/ability_warrior_victoryrush.png",
    "http://www.wowarmory.com/images/icons/21x21/ability_hunter_pet_cat.png",
    "http://www.wowarmory.com/images/icons/21x21/inv_jewelcrafting_dawnstone_03.png",
    "http://www.wowarmory.com/images/icons/21x21/inv_jewelcrafting_nightseye_03.png",
    "http://www.wowarmory.com/images/icons/21x21/inv_jewelcrafting_nobletopaz_03.png",
    "http://www.wowarmory.com/images/icons/21x21/inv_boots_08.png",
)


def load_r1():
    spec = importlib.util.spec_from_file_location("wow_v33_browser_r1_for_r2", R1_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load r1 preparer: {R1_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


r1 = load_r1()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def binding(path: Path) -> dict:
    if not path.is_file():
        raise RuntimeError(f"missing r2 source binding: {path}")
    return {"path": rel(path), "sha256": sha256_file(path)}


def read_json(path: Path, label: str) -> dict:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} is not a JSON object: {path}")
    return value


class _NewsEntryParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() != "div":
            return
        values = {str(key).casefold(): str(value or "") for key, value in attrs}
        entry_id = values.get("id", "")
        classes = set(values.get("class", "").casefold().split())
        if entry_id.casefold().startswith("news") and ({"news-expand", "news-collapse"} & classes):
            if entry_id not in self.ids:
                self.ids.append(entry_id)


def news_toggle_ids_r2(page_output: str) -> list[str]:
    page = r1.inside(OUTPUT / page_output, "v33 r2 news page")
    if not page.is_file():
        raise RuntimeError(f"v33 r2 news page is missing: {page}")
    parser = _NewsEntryParser()
    parser.feed(page.read_text(encoding="utf-8", errors="replace"))
    return parser.ids


def relative_output(source_path: str) -> str:
    normalized = str(source_path).replace("\\", "/")
    match = re.search(r"pages-resources-[^/]+/(.+)$", normalized)
    if not match:
        raise RuntimeError(f"cannot map accepted source page to v33 output: {source_path}")
    return match.group(1)


def current_output_match(page_output: str, original: str, context: str) -> dict:
    page = r1.inside(OUTPUT / page_output, "v33 r2 current source page")
    if not page.is_file():
        raise RuntimeError(f"v33 r2 current page is missing: {page}")
    path = urlsplit(original).path
    lines = page.read_text(encoding="utf-8", errors="replace").splitlines()
    candidates: list[tuple[int, str, str]] = []
    for index, line in enumerate(lines, 1):
        decoded = html.unescape(line)
        lower = decoded.casefold()
        if path not in decoded:
            continue
        if context == "navigation" and "href" not in lower:
            continue
        if context == "image" and not any(token in lower for token in ("src=", "url(", "<img", "background")):
            continue
        match_kind = "href" if "href" in lower and context == "navigation" else "img_or_css"
        candidates.append((index, line, match_kind))
    if not candidates:
        raise RuntimeError(f"accepted target has no exact current v33 HTML match: {original} in {page_output}")
    line_number, line_text, match_kind = candidates[0]
    return {
        "page_output": page_output,
        "line": line_number,
        "page_sha256": sha256_file(page),
        "path_token": path,
        "match_kind": match_kind,
        "line_text": line_text,
    }


def plan_candidate(plan: dict, original: str) -> dict:
    for row in plan.get("candidates", []) or []:
        if isinstance(row, dict) and str(row.get("original") or "") == original:
            return row
    raise RuntimeError(f"accepted source plan has no exact target: {original}")


def navigation_identity(correction: dict, original: str) -> dict:
    for row in correction.get("corrected_navigation_queue", {}).get("identities", []) or []:
        if isinstance(row, dict) and str(row.get("original") or "") == original:
            return row
    raise RuntimeError(f"accepted navigation correction has no exact target: {original}")


def source_record(original: str, correction: dict, static_plan: dict, news_plan: dict) -> tuple[dict, str, str]:
    if original in NAVIGATION_TARGETS:
        identity = navigation_identity(correction, original)
        references = identity.get("references") or []
        if not references:
            raise RuntimeError(f"navigation target has no frozen source reference: {original}")
        evidence = dict(references[0])
        source_path = str(evidence.get("output_file") or "")
        source_page = str(evidence.get("source_page") or "")
        return {
            "plan": binding(NAVIGATION_CORRECTION),
            "candidate_key": f"navigation-rank-{identity.get('rank')}",
            "source_path": source_path,
            "source_line": evidence.get("line"),
            "source_page": source_page,
            "source_page_sha256": str(evidence.get("source_page_sha256") or ""),
            "reason": str(evidence.get("reason") or ""),
            "identity_rank": identity.get("rank"),
        }, relative_output(source_path), "navigation"
    if original.startswith("http://www.worldofwarcraft.com/news/images/08-02/"):
        candidate = plan_candidate(news_plan, original)
        evidence = dict(candidate.get("source_evidence") or {})
        source_path = str(evidence.get("path") or "")
        return {
            "plan": binding(NEWS_BODY_PLAN),
            "candidate_key": str(candidate.get("target_key") or ""),
            "source_path": source_path,
            "source_line": evidence.get("line"),
            "source_page": str(evidence.get("source_page") or ""),
            "source_page_sha256": str(evidence.get("sha256") or ""),
            "reason": str(evidence.get("reason") or ""),
            "source_marker": evidence.get("source_marker"),
        }, relative_output(source_path), "image"
    candidate = plan_candidate(static_plan, original)
    evidence = dict(candidate.get("source_evidence") or {})
    source_path = str(evidence.get("path") or "")
    return {
        "plan": binding(STATIC40_PLAN),
        "candidate_key": str(candidate.get("target_key") or ""),
        "source_path": source_path,
        "source_line": evidence.get("line"),
        "source_page": str(evidence.get("source_page") or ""),
        "source_page_sha256": str(evidence.get("sha256") or ""),
        "reason": str(evidence.get("reason") or ""),
    }, relative_output(source_path), "image"


def additional_reference(original: str, items_by_original: dict[str, dict], correction: dict, static_plan: dict, news_plan: dict) -> dict:
    if original not in items_by_original:
        raise RuntimeError(f"r2 target is not in the accepted v33 image maps: {original}")
    source, page_output, context = source_record(original, correction, static_plan, news_plan)
    current = current_output_match(page_output, original, context)
    parsed_page = urlsplit(str(source["source_page"]))
    page_route = parsed_page.path or "/"
    return {
        "original": original,
        "role": str(items_by_original[original].get("role") or ""),
        "page_route": page_route,
        "page_output": page_output,
        "page_kind": r1.page_kind(page_route),
        "source_page_sha256": source["source_page_sha256"],
        "source_base_url": source["source_page"],
        "source_line": source["source_line"],
        "literal": original,
        "resolved_url": original,
        "target": "",
        "requested": original,
        "action": "accepted_v33_r2_current_output_match",
        "context": context,
        "reason": source["reason"],
        "match_kind": f"v33_current_output_{current['match_kind']}",
        "popup_full_image": False,
        "ordinary_image_href": context == "navigation",
        "missing_image_svg_marker": False,
        "static_render_candidate": context == "image",
        "source_evidence": source,
        "current_output_match": current,
    }


def build_input() -> dict:
    correction = read_json(NAVIGATION_CORRECTION, "navigation correction")
    static_plan = read_json(STATIC40_PLAN, "static40 batch-04 plan")
    news_plan = read_json(NEWS_BODY_PLAN, "news-body batch-02 plan")
    # Build against the already accepted r1 closure.  Replacing this function
    # keeps r1's map/provenance checks and changes only the reference layer.
    r1.news_toggle_ids = news_toggle_ids_r2
    payload = r1.build_input()
    items_by_original = {str(row["original"]): row for row in payload["new_originals"]}
    targets = list(NAVIGATION_TARGETS) + list(STATIC_TARGETS)
    if len(set(targets)) != 19:
        raise RuntimeError("r2 target list is not 19 distinct originals")
    existing = {
        str(row.get("original") or "")
        for key in ("ordinary_image_hrefs", "static_render_targets", "popup_full_image_links")
        for row in payload["source_references"].get(key, [])
    }
    overlap = sorted(set(targets) & existing)
    if overlap:
        raise RuntimeError("r2 additions already present in r1 reference sets: " + ", ".join(overlap))
    additions = [additional_reference(original, items_by_original, correction, static_plan, news_plan) for original in targets]
    navigation = [row for row in additions if row["ordinary_image_href"]]
    static = [row for row in additions if row["static_render_candidate"]]
    references = payload["source_references"]
    references["ordinary_image_hrefs"].extend(navigation)
    references["new_ordinary_image_hrefs"].extend(navigation)
    references["static_render_targets"].extend(static)
    references["all_matches"].extend(additions)
    ordinary = references["ordinary_image_hrefs"]
    payload["browser_plan"]["ordinary_image_hrefs"]["required_unique_originals"] = len({row["original"] for row in ordinary})
    payload["browser_plan"]["ordinary_image_hrefs"]["new_required_unique_originals"] = len({row["original"] for row in references["new_ordinary_image_hrefs"]})
    payload["browser_plan"]["static_render_targets"]["candidate_count"] = len(references["static_render_targets"])
    pages = set(payload["browser_plan"].get("news_toggle_ids", {}))
    pages.update(row["page_output"] for row in additions if row["page_kind"] == "news")
    pages.update(row["page_output"] for row in ordinary if row["page_kind"] == "news")
    payload["browser_plan"]["news_toggle_ids"] = {page: news_toggle_ids_r2(page) for page in sorted(pages)}
    payload["schema"] = "wow-recovery.integration.v33-browser-input-r2.v1"
    payload["r1_input"] = binding(R1_INPUT)
    payload["r2_reference_additions"] = {
        "navigation_count": len(navigation),
        "static_count": len(static),
        "total_count": len(additions),
        "source_plans": [
            binding(NAVIGATION_CORRECTION),
            binding(STATIC40_PLAN),
            binding(STATIC40_QUEUE),
            binding(STATIC40_SOURCE),
            binding(STATIC40_PUBLIC),
            binding(NEWS_BODY_PLAN),
            binding(NEWS_BODY_SOURCE),
            binding(NEWS_BODY_PUBLIC),
        ],
        "targets": additions,
    }
    payload["source_bindings"].update({
        "r1_browser_input": binding(R1_INPUT),
        "r2_preparer": binding(Path(__file__).resolve()),
        "navigation_exclusion_correction": binding(NAVIGATION_CORRECTION),
        "static40_batch4_plan": binding(STATIC40_PLAN),
        "static40_source_queue": binding(STATIC40_QUEUE),
        "static40_batch4_source_acceptance": binding(STATIC40_SOURCE),
        "static40_batch4_public_copy_acceptance": binding(STATIC40_PUBLIC),
        "news_body_batch2_plan": binding(NEWS_BODY_PLAN),
        "news_body_batch2_source_acceptance": binding(NEWS_BODY_SOURCE),
        "news_body_batch2_public_copy_acceptance": binding(NEWS_BODY_PUBLIC),
    })
    return payload


def write_once(path: Path, payload: dict) -> None:
    if path.exists():
        raise RuntimeError(f"refusing to overwrite additive r2 browser input: {path}")
    path.write_bytes((json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args(argv)
    if not args.prepare:
        parser.error("r2 browser preparer requires --prepare; it never runs Playwright")
    payload = build_input()
    write_once(INPUT, payload)
    print(json.dumps({"status": payload["status"], "input": rel(INPUT), "input_sha256": sha256_file(INPUT), "new_originals": payload["new_original_count"], "ordinary_links": payload["browser_plan"]["ordinary_image_hrefs"]["required_unique_originals"], "static_targets": payload["browser_plan"]["static_render_targets"]["candidate_count"], "popup_links": payload["browser_plan"]["popup_full_image_links"]["required"], "network_requests": 0, "export_executed": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
