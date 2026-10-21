#!/usr/bin/env python3
"""Audit the exact talent image 404s against frozen local records.

This is deliberately a read-only audit of the browser receipt, the v41 route
map/provenance, the frozen Source15 site, and the tracked offline site.  It
does not inspect archive ZIP contents or alter site/build inputs.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit


HERE = Path(__file__).resolve()
ROOT = next(parent for parent in HERE.parents if (parent / ".git").exists())
OUT = HERE.parent
RECEIPT_PATH = ROOT / "research/continuous-recovery-20261021/integration/talents/browser-receipt.json"
ROUTE_MAP_PATH = ROOT / ".scratch/pages-resources-20261021-v41/__offline/route-map.json"
V41_PROVENANCE_PATH = ROOT / ".scratch/pages-resources-20261021-v41/export-provenance.json"
SOURCE15_MANIFEST_PATH = ROOT / ".scratch/offline-navigation-20261015-v15/build-manifest.json"
OFFLINE_MANIFEST_PATH = ROOT / "offline/build-manifest.json"
V41_ROOT = ROOT / ".scratch/pages-resources-20261021-v41"
SOURCE15_ROOT = ROOT / ".scratch/offline-navigation-20261015-v15/site"
OFFLINE_ROOT = ROOT / "offline/site"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def norm_component(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", unquote(value).lower())


def route_variants(route: str) -> list[str]:
    values = [route]
    encoded = route.replace("'", "%27")
    double_encoded = route.replace("'", "%2527")
    lower = route.lower()
    for value in (encoded, double_encoded, lower):
        if value not in values:
            values.append(value)
    return values


def file_record(entry: dict, *, label: str) -> dict:
    keys = (
        "route",
        "output_path",
        "source_local_path",
        "source_offline_path",
        "source_sha256",
        "source_length",
        "derived_sha256",
        "derived_length",
        "mime",
        "kind",
        "role",
        "transformed",
    )
    return {"manifest": label, **{key: entry.get(key) for key in keys if key in entry}}


def index_manifest(manifest: dict, label: str) -> tuple[dict[str, list[dict]], dict]:
    by_route: dict[str, list[dict]] = defaultdict(list)
    for entry in manifest.get("files", []):
        route = entry.get("route")
        if isinstance(route, str):
            by_route[route].append(file_record(entry, label=label))
    return by_route, manifest


def source_file_record(path: Path, route: str, line: int, text: str, manifest_by_route: dict[str, list[dict]]) -> dict:
    record = {
        "path": path.relative_to(ROOT).as_posix(),
        "route": route,
        "line": line,
        "text": text.strip(),
        "length": path.stat().st_size,
        "sha256": sha256(path),
    }
    if route in manifest_by_route:
        record["manifest_records"] = manifest_by_route[route]
    return record


def find_source_references(cls: str, tree: str, basename: str, source15_manifest_by_route: dict[str, list[dict]]) -> dict:
    """Return the exact Source15 script lines that generate this request."""
    class_root = SOURCE15_ROOT / "shared/global/talents" / cls
    data_path = class_root / "data.js"
    donot_path = class_root / "donotlocalize.js"
    print_path = SOURCE15_ROOT / "shared/global/talents/includes/printOutTop.js"
    result = {"image_payload_manifest_records": [], "script_lines": []}

    target_stem = Path(basename).stem
    if target_stem.endswith("-off"):
        target_stem = target_stem[:-4]
    target_norm = norm_component(target_stem)
    tree_norm = norm_component(tree)

    # Exact title rows in the non-localized and data source files.
    def js_string_values(line: str, marker: str) -> list[str]:
        # These files use double-quoted JS strings with apostrophes escaped as
        # \\' inside the title.  A generic quote matcher would split at that
        # apostrophe and lose the exact source row.
        if marker == "nltalent":
            match = re.search(r'nltalent\[i\]\s*=\s*\["((?:\\.|[^"])*)"\]', line)
        else:
            match = re.search(r'talent\[i\]\s*=\s*\[\s*\d+\s*,\s*"((?:\\.|[^"])*)"', line)
        if not match:
            return []
        return [match.group(1).replace(r"\'", "'").replace(r'\"', '"')]

    for path, route, marker in (
        (donot_path, f"/shared/global/talents/{cls}/donotlocalize.js", "nltalent"),
        (data_path, f"/shared/global/talents/{cls}/data.js", "talent"),
    ):
        if not path.exists():
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if marker not in line:
                continue
            quoted = js_string_values(line, marker)
            if any(norm_component(value) == target_norm for value in quoted):
                result["script_lines"].append(
                    source_file_record(path, route, line_no, line, source15_manifest_by_route)
                    | {"purpose": "talent-name-source"}
                )

    # Exact tree row for background requests.
    if target_stem.lower() == "background":
        if donot_path.exists():
            for line_no, line in enumerate(donot_path.read_text(encoding="utf-8").splitlines(), 1):
                if "nltree" not in line:
                    continue
                quoted = re.findall(r"[\"']([^\"']+)[\"']", line)
                if any(norm_component(value) == tree_norm for value in quoted):
                    result["script_lines"].append(
                        source_file_record(
                            donot_path,
                            f"/shared/global/talents/{cls}/donotlocalize.js",
                            line_no,
                            line,
                            source15_manifest_by_route,
                        )
                        | {"purpose": "tree-name-source"}
                    )

    if print_path.exists():
        lines = print_path.read_text(encoding="utf-8").splitlines()
        for line_no, line in enumerate(lines, 1):
            if target_stem.lower() == "background" and "background.jpg" in line and "treeName" in line:
                result["script_lines"].append(
                    source_file_record(
                        print_path,
                        "/shared/global/talents/includes/printOutTop.js",
                        line_no,
                        line,
                        source15_manifest_by_route,
                    )
                    | {"purpose": "background-runtime-constructor"}
                )
            elif target_stem.lower() != "background" and "imageName" in line and "'+ imgPath +'/'+ nlclass" in line:
                result["script_lines"].append(
                    source_file_record(
                        print_path,
                        "/shared/global/talents/includes/printOutTop.js",
                        line_no,
                        line,
                        source15_manifest_by_route,
                    )
                    | {"purpose": "talent-image-runtime-constructor"}
                )
    return result


def manifest_matches(route: str, by_route: dict[str, list[dict]]) -> dict:
    matches = {}
    for variant in route_variants(route):
        if variant in by_route:
            matches[variant] = by_route[variant]
    return matches


def manifest_url_index_matches(route: str, manifest: dict) -> dict:
    """Check original URL and alias indexes without treating nearby names as hits."""
    variants = route_variants(route)
    original_keys = []
    for variant in variants:
        original_keys.extend(
            [
                variant,
                variant.lstrip("/"),
                f"www.worldofwarcraft.com{variant}",
                f"http://www.worldofwarcraft.com{variant}",
                f"https://www.worldofwarcraft.com{variant}",
            ]
        )
    key_matches = {}
    value_matches = {}
    origin_index = manifest.get("origin_index", {})
    if isinstance(origin_index, dict):
        for candidate in original_keys:
            if candidate in origin_index:
                key_matches[candidate] = origin_index[candidate]
        for key, value in origin_index.items():
            if value in variants:
                value_matches[key] = value

    alias_matches = {}
    aliases = manifest.get("route_aliases", {})
    if isinstance(aliases, dict):
        for candidate in variants:
            if candidate in aliases:
                alias_matches[candidate] = aliases[candidate]

    supplement_matches = []
    for entry in manifest.get("supplements", []):
        if not isinstance(entry, dict):
            continue
        entry_route = entry.get("route")
        if entry_route in variants:
            supplement_matches.append(entry)
    return {
        "origin_index_key_matches": key_matches,
        "origin_index_value_matches": value_matches,
        "route_aliases": alias_matches,
        "supplements": supplement_matches,
    }


def route_map_matches(route: str, route_map: dict) -> dict:
    result = {}
    for container_name in ("routes", "aliases"):
        container = route_map.get(container_name, {})
        for variant in route_variants(route):
            if variant in container:
                result.setdefault(container_name, {})[variant] = container[variant]
    return result


def build_talent_file_index(root: Path) -> tuple[dict[str, list[dict]], int]:
    """Index only the three class-specific talent subtrees, never the whole workspace."""
    base = root / "shared/global/talents"
    by_norm: dict[str, list[dict]] = defaultdict(list)
    count = 0
    if not base.exists():
        return by_norm, count
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        count += 1
        rel = path.relative_to(root).as_posix()
        by_norm[norm_component(path.name)].append(
            {
                "path": rel,
                "length": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    return by_norm, count


def physical_evidence(route: str, roots: dict[str, Path], indexes: dict[str, dict[str, list[dict]]]) -> dict:
    decoded_route = unquote(route).lstrip("/")
    exact = {}
    for label, root in roots.items():
        matches = []
        for candidate in (route.lstrip("/"), decoded_route, *[unquote(x).lstrip("/") for x in route_variants(route)]):
            path = root / candidate
            if path.is_file():
                rel = path.relative_to(root).as_posix()
                if rel not in {m["path"] for m in matches}:
                    matches.append({"path": rel, "length": path.stat().st_size, "sha256": sha256(path)})
        exact[label] = matches

    basename = Path(decoded_route).name
    name_norm = norm_component(Path(basename).stem)
    candidates = {}
    # Candidate aliases are restricted to the same class talent subtree.  A
    # generic background.jpg elsewhere in the site is not evidence for this
    # class/tree request.
    for label, index in indexes.items():
        candidates[label] = index.get(name_norm, [])
    return {"exact_route_files": exact, "same_normalized_name_candidates": candidates}


def extract_targets(receipt: dict) -> list[dict]:
    base = "/WOW-Encyclopedia-Deployable-Archive"
    grouped = {}
    for page in receipt.get("pages", []):
        cls = page.get("className")
        for failure in page.get("httpFailures", []):
            url = failure.get("url", "")
            parsed = urlsplit(url)
            route_path = parsed.path
            if base in route_path:
                route = route_path.split(base, 1)[1] or "/"
            else:
                route = route_path
            key = route
            row = grouped.setdefault(
                key,
                {
                    "route": route,
                    "classes": [],
                    "failure_count": 0,
                    "statuses": [],
                    "raw_urls": [],
                    "query_strings": [],
                },
            )
            if cls not in row["classes"]:
                row["classes"].append(cls)
            row["failure_count"] += 1
            row["statuses"].append(failure.get("status"))
            row["raw_urls"].append(url)
            row["query_strings"].append(parsed.query)
    return [grouped[key] for key in sorted(grouped)]


def target_kind(route: str) -> str:
    return "background" if route.endswith("/background.jpg") else "talent_icon"


def classify(target: dict, route_matches: dict, manifests: dict, physical: dict) -> str:
    exact = physical["exact_route_files"]
    if exact["v41_output"]:
        if route_matches:
            return "exact-local-file"
        return "exact-local-file-route-map-omission"
    if exact["source15_site"] or exact["offline_site"]:
        return "exact-source-file-export-omission"
    if any(physical["same_normalized_name_candidates"].values()):
        return "same-name-alias-candidate"
    if route_matches:
        return "route-map-or-alias-to-missing-file"
    if any(manifests.values()):
        return "manifest-record-to-missing-file"
    return "source-script-only-no-image-record"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    receipt = read_json(RECEIPT_PATH)
    route_map = read_json(ROUTE_MAP_PATH)
    v41_provenance = read_json(V41_PROVENANCE_PATH)
    source15_manifest = read_json(SOURCE15_MANIFEST_PATH)
    offline_manifest = read_json(OFFLINE_MANIFEST_PATH)

    v41_by_route, _ = index_manifest(v41_provenance, "v41_provenance")
    source15_by_route, _ = index_manifest(source15_manifest, "source15_manifest")
    offline_by_route, _ = index_manifest(offline_manifest, "offline_manifest")
    manifest_indexes = {
        "v41_provenance": v41_by_route,
        "source15_manifest": source15_by_route,
        "offline_manifest": offline_by_route,
    }
    roots = {"v41_output": V41_ROOT, "source15_site": SOURCE15_ROOT, "offline_site": OFFLINE_ROOT}
    talent_indexes = {}
    scanned_counts = {}
    for label, root in roots.items():
        talent_indexes[label], scanned_counts[label] = build_talent_file_index(root)

    targets = extract_targets(receipt)
    rows = []
    for base in targets:
        route = base["route"]
        parts = route.split("/")
        cls = parts[4] if len(parts) > 4 else None
        tree = parts[-2] if len(parts) >= 2 else None
        basename = parts[-1] if parts else None
        route_matches = route_map_matches(route, route_map)
        manifests = {label: manifest_matches(route, by_route) for label, by_route in manifest_indexes.items()}
        manifest_url_indexes = {
            "source15_manifest": manifest_url_index_matches(route, source15_manifest),
            "offline_manifest": manifest_url_index_matches(route, offline_manifest),
        }
        physical = physical_evidence(route, roots, talent_indexes)
        refs = find_source_references(cls, tree, basename, source15_by_route)
        classification = classify(base, route_matches, manifests, physical)
        if classification in {"source-script-only-no-image-record", "same-name-alias-candidate"}:
            minimal_fix = (
                "No exact payload is available locally; preserve the missing-image behavior until an exact Source15/original byte record is supplied. "
                "Do not substitute a similarly named icon."
            )
        elif classification == "exact-source-file-export-omission":
            minimal_fix = "Register the exact existing file in the exporter route/provenance maps; do not alter the runtime URL or bytes."
        elif classification == "exact-local-file-route-map-omission":
            minimal_fix = "Add the exact existing v41 file to route-map/provenance registration; do not rename or substitute it."
        else:
            minimal_fix = "Investigate the stale route/manifest record before changing production output."

        row = {
            **base,
            "class": cls,
            "tree_or_group": tree,
            "basename": basename,
            "kind": target_kind(route),
            "status_observed": sorted(set(base["statuses"])),
            "route_variants_checked": route_variants(route),
            "route_map_matches": route_matches,
            "manifest_matches": manifests,
            "manifest_url_index_matches": manifest_url_indexes,
            "physical": physical,
            "source_reference": refs,
            "image_payload_source_record": None,
            "image_payload_status": "not found in v41 provenance, Source15 manifest, or offline manifest",
            "classification": classification,
            "minimal_fix": minimal_fix,
        }
        rows.append(row)

    receipt_hash = sha256(RECEIPT_PATH)
    generated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    counts = Counter(row["classification"] for row in rows)
    kinds = Counter(row["kind"] for row in rows)
    classes = Counter(row["class"] for row in rows)
    summary = {
        "schema": "talent-resource-audit/v1",
        "generatedUtc": generated,
        "scope": {
            "receipt": RECEIPT_PATH.relative_to(ROOT).as_posix(),
            "receipt_sha256": receipt_hash,
            "route_map": ROUTE_MAP_PATH.relative_to(ROOT).as_posix(),
            "v41_provenance": V41_PROVENANCE_PATH.relative_to(ROOT).as_posix(),
            "source15_manifest": SOURCE15_MANIFEST_PATH.relative_to(ROOT).as_posix(),
            "offline_manifest": OFFLINE_MANIFEST_PATH.relative_to(ROOT).as_posix(),
            "roots_checked": {label: root.relative_to(ROOT).as_posix() for label, root in roots.items()},
            "archive_zip_contents_scanned": False,
            "network_used": False,
        },
        "input_sizes": {
            "receipt_bytes": RECEIPT_PATH.stat().st_size,
            "route_map_bytes": ROUTE_MAP_PATH.stat().st_size,
            "v41_provenance_bytes": V41_PROVENANCE_PATH.stat().st_size,
            "source15_manifest_bytes": SOURCE15_MANIFEST_PATH.stat().st_size,
            "offline_manifest_bytes": OFFLINE_MANIFEST_PATH.stat().st_size,
        },
        "counts": {
            "browser_404_events": sum(row["failure_count"] for row in rows),
            "unique_routes": len(rows),
            "by_kind": dict(kinds),
            "by_class": dict(classes),
            "by_classification": dict(counts),
            "route_map_or_alias_matches": sum(bool(row["route_map_matches"]) for row in rows),
            "manifest_image_route_matches": sum(any(row["manifest_matches"].values()) for row in rows),
            "manifest_original_url_or_alias_matches": sum(
                any(any(section.values()) for section in row["manifest_url_index_matches"].values())
                for row in rows
            ),
            "exact_v41_files": sum(bool(row["physical"]["exact_route_files"]["v41_output"]) for row in rows),
            "exact_source_files": sum(
                bool(row["physical"]["exact_route_files"]["source15_site"] or row["physical"]["exact_route_files"]["offline_site"])
                for row in rows
            ),
            "same_normalized_name_candidates": sum(
                any(row["physical"]["same_normalized_name_candidates"].values()) for row in rows
            ),
        },
        "talent_subtree_files_scanned": scanned_counts,
        "targets": rows,
    }
    (OUT / "resource-audit.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "class",
        "tree_or_group",
        "basename",
        "kind",
        "route",
        "failure_count",
        "status_observed",
        "classification",
        "route_map_matches",
        "manifest_matches",
        "manifest_url_index_matches",
        "v41_exact_local_file",
        "source15_exact_local_file",
        "offline_exact_local_file",
        "same_normalized_name_candidates",
        "source_script_evidence",
        "image_payload_source_record",
        "image_payload_status",
        "minimal_fix",
    ]
    with (OUT / "resource-audit.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            physical = row["physical"]["exact_route_files"]
            writer.writerow(
                {
                    "class": row["class"],
                    "tree_or_group": row["tree_or_group"],
                    "basename": row["basename"],
                    "kind": row["kind"],
                    "route": row["route"],
                    "failure_count": row["failure_count"],
                    "status_observed": json.dumps(row["status_observed"]),
                    "classification": row["classification"],
                    "route_map_matches": json.dumps(row["route_map_matches"], ensure_ascii=False),
                    "manifest_matches": json.dumps(row["manifest_matches"], ensure_ascii=False),
                    "manifest_url_index_matches": json.dumps(row["manifest_url_index_matches"], ensure_ascii=False),
                    "v41_exact_local_file": json.dumps(physical["v41_output"], ensure_ascii=False),
                    "source15_exact_local_file": json.dumps(physical["source15_site"], ensure_ascii=False),
                    "offline_exact_local_file": json.dumps(physical["offline_site"], ensure_ascii=False),
                    "same_normalized_name_candidates": json.dumps(
                        row["physical"]["same_normalized_name_candidates"], ensure_ascii=False
                    ),
                    "source_script_evidence": json.dumps(row["source_reference"]["script_lines"], ensure_ascii=False),
                    "image_payload_source_record": "",
                    "image_payload_status": row["image_payload_status"],
                    "minimal_fix": row["minimal_fix"],
                }
            )

    readme = f"""# Talent resource audit\n\nGenerated `{generated}` from the existing talent browser receipt. The receipt contains **{len(rows)} unique HTTP 404 routes from {sum(row['failure_count'] for row in rows)} events**: {kinds['background']} dynamic tree backgrounds and {kinds['talent_icon']} dynamic talent icon requests across {len(classes)} classes.\n\nThe audit checked the exact URL, `%27` and `%2527` apostrophe forms, lowercase route form, v41 `route-map.json`, v41 `export-provenance.json`, both manifests' original URL indexes/aliases, the Source15 build manifest/site, and the tracked `offline` manifest/site. It scanned only the three `shared/global/talents` subtrees for local files. It did not use the network or inspect historical ZIP contents.\n\nResults are in `resource-audit.json` (full evidence) and `resource-audit.csv` (one row per unique route). Each row separates the missing image payload record from the Source15 script lines that construct the request. A `source-script-only-no-image-record` row has no exact image bytes or manifest row available locally; the script evidence is not an image source record.\n\nCounts: `{dict(counts)}`. Exact v41 files: `{summary['counts']['exact_v41_files']}`. Exact Source15/offline files: `{summary['counts']['exact_source_files']}`. Route-map/alias matches: `{summary['counts']['route_map_or_alias_matches']}`. Manifest original URL/alias matches: `{summary['counts']['manifest_original_url_or_alias_matches']}`. Same-normalized-name candidates in the same talent subtree: `{summary['counts']['same_normalized_name_candidates']}`.\n\nThe minimum repair for missing payloads is to retain the original dynamic route and wait for exact original/Source15 bytes before registering a route. Similar spell icons and unrelated `background.jpg` files are not accepted as substitutes.\n"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")

    print(json.dumps({"counts": summary["counts"], "classification": dict(counts), "outputs": [p.name for p in (OUT / "resource-audit.json", OUT / "resource-audit.csv", OUT / "README.md")]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
