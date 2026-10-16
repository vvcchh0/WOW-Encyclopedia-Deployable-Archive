from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[3]
OWN_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import export_github_pages  # noqa: E402
import offline_mirror  # noqa: E402


SOURCE_STAGE = ROOT / ".scratch/offline-navigation-20261015-v15"
SOURCE_SITE = SOURCE_STAGE / "site"
MANIFEST = SOURCE_STAGE / "build-manifest.json"
PRIMARY_MAPS = [
    ROOT / "research/resource-resume-20261013/round002/entity-source-map.json",
    ROOT / "research/resource-resume-20261013/round003/entity-source-map.json",
]
EXISTING_SUPPLEMENT_MAPS = [
    ROOT / "research/related-sites-20261014/integration/regional-image-source-map.json",
    ROOT / "research/related-sites-20261014/integration/karazhan-late-source-map.json",
    ROOT / "research/media-screenshots-20261015/late-image-source-map.json",
]
EU2_MAP = ROOT / "research/continuous-recovery-20261016/integration/v16-eu-image-source-map.json"
LEGACY_EU2_MAP = ROOT / "research/continuous-recovery-20261016/local-audit/regional-image-supplement-map.proposal.json"
NEWS01_MAP = ROOT / "research/continuous-recovery-20261016/integration/v16-primary-news-image-source-map.json"
LEGACY_NEWS01_MAP = ROOT / "research/continuous-recovery-20261016/integration/news01-primary-image-source-map.json"
NEWS01_FINAL_MAX_ITEMS = 13
PRODUCTION_FILES = [ROOT / "tools/export_github_pages.py", ROOT / "tools/offline_mirror.py"]


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def file_evidence(path: Path) -> dict:
    return {"path": rel(path), "exists": path.is_file(), "sha256": sha256(path)}


def load_map(path: Path) -> dict:
    if not path.is_file():
        raise AssertionError(f"map missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise AssertionError(f"map has no items list: {path}")
    return payload


def map_item_count(paths: list[Path]) -> int:
    return sum(len(load_map(path)["items"]) for path in paths)


def frozen_sets(manifest: dict) -> tuple[set[str], set[str]]:
    records = list(manifest.get("files") or [])
    if not records:
        raise AssertionError("frozen v15 manifest has no files")
    routes = {str(record.get("route") or "") for record in records}
    routes.update(str(alias) for alias in (manifest.get("route_aliases") or {}))
    static_paths = {
        export_github_pages.static_rel_for_route(str(record["route"]), record)
        for record in records
    }
    return routes, static_paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only v16 overlay loader precheck")
    parser.add_argument(
        "--news-primary-map",
        type=Path,
        default=NEWS01_MAP,
        help="Root-accepted final NEWS primary map; current map has nine items, future additions may contain up to thirteen",
    )
    parser.add_argument(
        "--eu2-map",
        type=Path,
        default=EU2_MAP,
        help="Root-accepted EU2 supplement map",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OWN_DIR / "loader-precheck-v16-final.json",
        help="Final receipt path; legacy loader-precheck-v16.json remains preserved",
    )
    args = parser.parse_args()

    if not SOURCE_SITE.is_dir() or not MANIFEST.is_file():
        raise AssertionError("frozen v15 source site or manifest missing")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    routes, static_paths = frozen_sets(manifest)
    anchor = str(manifest.get("anchor_timestamp") or "")
    if anchor != "20080512210044":
        raise AssertionError(f"unexpected frozen v15 anchor: {anchor}")

    eu2_path = args.eu2_map.resolve()
    for path in PRIMARY_MAPS + EXISTING_SUPPLEMENT_MAPS + [eu2_path] + PRODUCTION_FILES:
        if not path.is_file():
            raise AssertionError(f"required precheck input missing: {path}")

    primary_items = map_item_count(PRIMARY_MAPS)
    existing_supplement_items = map_item_count(EXISTING_SUPPLEMENT_MAPS)
    eu2_items = map_item_count([EU2_MAP])
    if primary_items != 19 or existing_supplement_items != 19 or eu2_items != 2:
        raise AssertionError(f"unexpected map counts: primary={primary_items}, existing={existing_supplement_items}, eu2={eu2_items}")

    primary, primary_bytes = export_github_pages.load_image_overlays(
        tuple(PRIMARY_MAPS),
        workspace_root=ROOT,
        anchor_timestamp=anchor,
        frozen_routes=routes,
        frozen_static_paths=static_paths,
    )
    supplements, supplement_bytes = export_github_pages.load_supplement_image_overlays(
        tuple(EXISTING_SUPPLEMENT_MAPS + [eu2_path]),
        workspace_root=ROOT,
        anchor_timestamp=anchor,
        frozen_routes=routes | {str(item["route"]) for item in primary},
        frozen_static_paths=static_paths | {str(item["relative"]) for item in primary},
        allow_later_image_supplements=True,
    )
    if len(primary) != 19:
        raise AssertionError(f"primary loader count: {len(primary)}")
    if len(supplements) != 21:
        raise AssertionError(f"supplement loader count: {len(supplements)}")
    if sum(1 for x in supplements if "wow-europe.com" in urlsplit(str(x["logical_url"])).hostname.casefold()) != 16:
        raise AssertionError("expected 16 EU-related supplement routes after adding EU2")
    if any(str(x["logical_url"]).casefold().startswith(("http://www.wow-europe.com:80/", "http://wow-europe.com:80/")) and str(x["logical_url"]) != str(x["original_url"]) for x in supplements):
        raise AssertionError("loader retained a default-port logical/original mismatch")

    news_status = "pending_root_acceptance"
    news_evidence = None
    news_count = 0
    primary_with_news_count = None
    primary_with_news_bytes = None
    if args.news_primary_map is not None:
        news_path = args.news_primary_map.resolve()
        news_payload = load_map(news_path)
        news_count = len(news_payload["items"])
        if news_count < 1 or news_count > NEWS01_FINAL_MAX_ITEMS:
            raise AssertionError(f"NEWS01 primary map must contain 1..{NEWS01_FINAL_MAX_ITEMS} items, got {news_count}")
        news, news_bytes = export_github_pages.load_image_overlays(
            tuple(PRIMARY_MAPS + [news_path]),
            workspace_root=ROOT,
            anchor_timestamp=anchor,
            frozen_routes=routes,
            frozen_static_paths=static_paths,
        )
        if len(news) - len(primary) != news_count:
            raise AssertionError("NEWS01 map contains a duplicate route or origin key")
        news_status = "provided_and_loader_validated"
        news_evidence = file_evidence(news_path)
        primary_with_news_count = len(news)
        primary_with_news_bytes = news_bytes

    input_hashes = {
        "frozen_manifest": sha256(MANIFEST),
        "v15_build_script": sha256(ROOT / "research/focused-recovery-20261015-2303/integration/build_pages_v15.py"),
        "primary_maps": [file_evidence(x) for x in PRIMARY_MAPS],
        "existing_supplement_maps": [file_evidence(x) for x in EXISTING_SUPPLEMENT_MAPS],
        "eu2_supplement_map": file_evidence(eu2_path),
        "legacy_eu2_proposal": file_evidence(LEGACY_EU2_MAP),
        "legacy_news01_map": file_evidence(LEGACY_NEWS01_MAP),
        "production_loader": [file_evidence(x) for x in PRODUCTION_FILES],
    }
    final_primary_count = primary_with_news_count or len(primary)
    final_primary_bytes = primary_with_news_bytes or primary_bytes
    result = {
        "schema": "wow-recovery.integration.v16.loader-precheck",
        "network_requests_performed": 0,
        "export_started": False,
        "assertions": {
            "frozen_v15_stage_present": SOURCE_SITE.is_dir() and MANIFEST.is_file(),
            "frozen_anchor_matches_v15": anchor == "20080512210044",
            "existing_primary_loader_19_records": len(primary) == 19,
            "current_or_final_primary_loader_count_valid": 19 <= final_primary_count <= 19 + NEWS01_FINAL_MAX_ITEMS,
            "existing_supplement_map_records_19": existing_supplement_items == 19,
            "eu2_map_records_2": eu2_items == 2,
            "supplement_loader_21_records": len(supplements) == 21,
            "eu2_has_16_related_records_after_merge": sum(1 for x in supplements if "wow-europe.com" in urlsplit(str(x["logical_url"])).hostname.casefold()) == 16,
            "news01_pending_or_validated": news_status in {"pending_root_acceptance", "provided_and_loader_validated"},
            "no_export_started": True,
            "no_network_requests": True,
        },
        "source_policy": {
            "source_stage": rel(SOURCE_STAGE),
            "source_stage_reused": True,
            "new_source_version_created": False,
            "manifest": file_evidence(MANIFEST),
            "anchor_timestamp": anchor,
            "source_site_exists": SOURCE_SITE.is_dir(),
            "source_site_file_count": sum(1 for x in SOURCE_SITE.rglob("*") if x.is_file()),
        },
        "loader_contract": {
            "production_module": rel(ROOT / "tools/export_github_pages.py"),
            "primary_loader": "load_image_overlays",
            "supplement_loader": "load_supplement_image_overlays",
            "default_port_normalization": "mirror.origin_key/origin_namespace_host strips http:80 and https:443 for keying; logical/original URLs may retain accepted original :80 spelling",
            "supplement_later_policy": True,
        },
        "accepted_inputs": {
            "existing_primary_map_count": len(primary),
            "current_or_final_primary_loader_count": final_primary_count,
            "current_or_final_primary_source_bytes": final_primary_bytes,
            "existing_supplement_map_count": existing_supplement_items,
            "eu2_supplement_map_count": eu2_items,
            "supplement_loader_count": len(supplements),
            "supplement_source_bytes": supplement_bytes,
            "supplement_host_namespace_counts": dict(Counter(offline_mirror.origin_namespace_host(str(x["logical_url"])) for x in supplements)),
            "eu2_urls": [str(x["logical_url"]) for x in supplements if "10702-01.jpg" in str(x["logical_url"]) or "10703-14.jpg" in str(x["logical_url"])],
        },
        "news_primary_overlay": {
            "status": news_status,
            "map": news_evidence,
            "current_accepted_items": news_count,
            "future_final_items_max": NEWS01_FINAL_MAX_ITEMS,
            "count_if_provided": news_count,
            "primary_count_if_provided": primary_with_news_count,
            "primary_source_bytes_if_provided": primary_with_news_bytes,
            "must_be_passed_as": "image_source_maps / primary loader, not supplement_image_source_maps",
            "pending_reason": "No root-accepted NEWS map was present during this precheck" if news_status == "pending_root_acceptance" else None,
        },
        "input_hashes": input_hashes,
        "next_action_gate": "Final nine-image NEWS map and two-image EU2 supplement map are loader-valid. Export remains gated on root GO; the frozen v15 source is reused and no source version is copied.",
    }
    out = args.output.resolve()
    if out.exists() and out.name == "loader-precheck-v16-final.json":
        # A final receipt is a single-run artifact; refuse silent replacement.
        raise RuntimeError(f"refusing to overwrite final loader receipt: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
