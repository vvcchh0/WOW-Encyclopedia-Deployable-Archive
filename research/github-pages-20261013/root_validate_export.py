"""Independent byte, provenance, budget and non-disclosing publication check."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import copy
from collections import Counter
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_MANIFEST = "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, default=ROOT / ".scratch/pages-preview")
    parser.add_argument("--reuse", type=Path, help="reuse completed per-file byte scans only when SHA and length are identical")
    args = parser.parse_args()
    if args.reuse:
        args.reuse = args.reuse.resolve()
    prior = json.loads(args.reuse.read_text(encoding="utf-8")) if args.reuse else None
    prior_records = {x["path"]: x for x in prior["files"]} if prior else {}
    reused_count = 0
    site = args.site.resolve()
    site.relative_to((ROOT / ".scratch").resolve())
    spec = importlib.util.spec_from_file_location("publication_scan", ROOT / "research/github-publication-20261012/full-tree-hygiene.py")
    scanner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = scanner
    spec.loader.exec_module(scanner)
    manifest_path = ROOT / "offline/build-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    provenance_path = site / "export-provenance.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    source = {x["output_path"]: x for x in manifest["files"]}
    failures = []
    records = []
    reviewed = []
    paths = Counter(x["output_path"] for x in provenance["files"])
    duplicates = [p for p, n in paths.items() if n != 1]
    if duplicates:
        failures.append({"kind": "duplicate_provenance_paths", "paths": duplicates})
    source_checked = set()
    output_digests = {}
    binary_count = 0
    for item in provenance["files"]:
        path = site / item["output_path"]
        try:
            path.resolve().relative_to(site)
            if not path.is_file():
                raise ValueError("missing output")
            observed_output_sha = digest(path)
            output_digests[item["output_path"]] = observed_output_sha
            if observed_output_sha != item["derived_sha256"] or path.stat().st_size != item["derived_length"]:
                raise ValueError("output SHA/length mismatch")
            src = item.get("source_offline_path")
            if src:
                expected = source[src]
                frozen = ROOT / src
                frozen_sha = digest(frozen)
                if frozen_sha != expected["derived_sha256"] or frozen.stat().st_size != expected["derived_length"]:
                    raise ValueError("frozen source SHA/length mismatch")
                if frozen_sha != item["source_sha256"]:
                    raise ValueError("source provenance mismatch")
                source_checked.add(src)
                is_text_html = str(expected.get("mime", "")).lower().startswith("text/html")
                if not is_text_html and item["kind"] not in {"html", "menu_html", "js", "css", "xsl", "xml", "support", "legacy_component", "pages_missing"}:
                    if item["derived_sha256"] != frozen_sha:
                        raise ValueError("binary bytes changed")
                    binary_count += 1
        except Exception as exc:
            failures.append({"kind": "provenance", "path": item["output_path"], "error": str(exc)})
    all_files = sorted(p for p in site.rglob("*") if p.is_file())
    actual_paths = {p.relative_to(site).as_posix() for p in all_files}
    expected_paths = set(paths) | {"export-provenance.json"}
    if actual_paths != expected_paths:
        failures.append({"kind": "file_set", "extra": sorted(actual_paths-expected_paths), "missing": sorted(expected_paths-actual_paths)})
    if digest(manifest_path) != EXPECTED_MANIFEST:
        failures.append({"kind": "source_manifest_changed"})
    if set(source) != source_checked:
        failures.append({"kind": "unrepresented_source", "paths": sorted(set(source)-source_checked)})
    for path in all_files:
        rel = path.relative_to(site).as_posix()
        review_path = "offline/site/" + rel
        old = prior_records.get(rel)
        output_sha = output_digests.get(rel) or digest(path)
        if old and old["sha256"] == output_sha and old["bytes"] == path.stat().st_size:
            record = copy.deepcopy(old)
            reused_count += 1
        else:
            with path.open("rb") as f:
                record = scanner.scan_blob(f, path.stat().st_size, review_path, [])
        record["path"] = rel
        for finding in record["findings"]:
            if finding["category"] in {"authorization_field_without_value", "cookie_handling_field"}:
                continue
            rule = scanner.MANUAL_REVIEW_RULES.get(review_path, {}).get(finding["category"])
            if rule:
                finding["review_outcome"] = rule
                reviewed.append({"path": rel, "category": finding["category"], "count": finding["count"], "review": rule})
            else:
                failures.append({"kind": "unresolved_publication_candidate", "path": rel, "category": finding["category"], "count": finding["count"]})
        records.append(record)
    workspace_bytes = 0
    for folder, dirs, files in os.walk(ROOT):
        for name in files:
            workspace_bytes += (Path(folder) / name).stat().st_size
    free = shutil.disk_usage(ROOT).free
    total = sum(p.stat().st_size for p in all_files)
    if total >= 1_000_000_000 or workspace_bytes >= 14_000_000_000 or free < 11_005_853_696:
        failures.append({"kind": "budget", "site_bytes": total, "workspace_bytes": workspace_bytes, "D_free_bytes": free})
    report = {"generated_utc": datetime.now(timezone.utc).isoformat(), "accepted": not failures, "site": str(site.relative_to(ROOT)), "source_manifest_sha256": digest(manifest_path), "provenance_sha256": digest(provenance_path), "output_files": len(all_files), "output_bytes": total, "source_files_checked": len(source_checked), "binary_files_byte_identical": binary_count, "workspace_bytes_including_git": workspace_bytes, "D_free_bytes": free, "publication_scan": {"full_bytes": True, "skipped_files": 0, "values_emitted": False, "reviewed_candidates": reviewed, "reused_sha_bound_file_scans": reused_count, "new_file_scans": len(all_files) - reused_count, "reuse_report_sha256": digest(args.reuse) if args.reuse else None, "reuse_report": str(args.reuse.relative_to(ROOT)) if args.reuse else None}, "failures": failures, "files": records}
    out = ROOT / "research/github-pages-20261013/root-export-acceptance.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k not in {"files", "publication_scan"}}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1

if __name__ == "__main__":
    raise SystemExit(main())
