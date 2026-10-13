"""Accept an immutable Pages commit, reusing scans only for identical Git blobs.

The earlier full-byte scan is bound by the old commit's provenance hash. Only
new blobs need another content scan; all output paths, lengths, source hashes,
and the complete new tree are still checked. This avoids re-reading thousands
of unchanged archive images after a JavaScript-only repair.
"""
from __future__ import annotations
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "research/github-pages-20261013"
OLD = "64677b5ca816aa998288c5c039b98c2cf5522229"

def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout

def tree(commit: str) -> dict[str, str]:
    result = {}
    for row in git("ls-tree", "-r", "-z", commit).split(b"\0"):
        if row:
            metadata, path = row.split(b"\t", 1)
            mode, kind, oid = metadata.split()
            if mode != b"100644" or kind != b"blob":
                raise ValueError("non-regular Git tree entry")
            result[path.decode("utf-8")] = oid.decode("ascii")
    return result

def main() -> int:
    commit = git("rev-parse", "gh-pages").decode().strip()
    prior_path = OUT / "root-export-pre-browser-fixes.json"
    prior_bytes = prior_path.read_bytes()
    prior = json.loads(prior_bytes)
    old_tree = tree(OLD)
    current = tree(commit)
    old_prov = git("cat-file", "blob", old_tree["export-provenance.json"])
    assert hashlib.sha256(old_prov).hexdigest() == prior["provenance_sha256"]
    # The prior scan had one classification error: a text/html generated
    # placeholder was treated as binary. SHA, provenance and hygiene passed.
    assert prior["failures"] == [{"kind": "provenance", "path": "__offline/excluded-frame.html", "error": "binary bytes changed"}]
    manifest_data = (ROOT / "offline/build-manifest.json").read_bytes()
    assert hashlib.sha256(manifest_data).hexdigest() == prior["source_manifest_sha256"]
    manifest = json.loads(manifest_data)
    source = {x["output_path"]: x for x in manifest["files"]}
    prov = json.loads(git("cat-file", "blob", current["export-provenance.json"]))
    outputs = {x["output_path"]: x for x in prov["files"]}
    assert len(outputs) == len(prov["files"])
    assert set(current) == set(outputs) | {"export-provenance.json"}
    previous = {x["path"]: x for x in prior["files"]}
    spec = importlib.util.spec_from_file_location("publication_scan", ROOT / "research/github-publication-20261012/full-tree-hygiene.py")
    scanner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = scanner
    spec.loader.exec_module(scanner)
    failures = []
    records = []
    reused = 0
    source_paths = set()
    for path, oid in current.items():
        if old_tree.get(path) == oid and path in previous:
            record = dict(previous[path])
            record["scan_reused_same_blob"] = True
            reused += 1
        else:
            data = git("cat-file", "blob", oid)
            record = scanner.scan_blob(io.BytesIO(data), len(data), "offline/site/" + path, [])
            record["path"] = path
            record["scan_reused_same_blob"] = False
            for finding in record["findings"]:
                if finding["category"] in {"cookie_handling_field", "authorization_field_without_value"}:
                    continue
                rule = scanner.MANUAL_REVIEW_RULES.get("offline/site/" + path, {}).get(finding["category"])
                if rule:
                    finding["review_outcome"] = rule
                else:
                    failures.append({"kind": "unresolved_publication_candidate", "path": path, "category": finding["category"]})
        record["git_blob"] = oid
        item = outputs.get(path)
        if item:
            if (record["sha256"], record["bytes"]) != (item["derived_sha256"], item["derived_length"]):
                failures.append({"kind": "output_provenance", "path": path})
            src = item.get("source_offline_path")
            if src:
                expected = source[src]
                source_paths.add(src)
                if (item["source_sha256"], item["source_length"]) != (expected["derived_sha256"], expected["derived_length"]):
                    failures.append({"kind": "source_provenance", "path": path})
        records.append(record)
    if set(source) != source_paths:
        failures.append({"kind": "source_coverage", "count": len(source_paths)})
    published_bytes = sum(x["bytes"] for x in records)
    workspace = sum((Path(folder) / name).stat().st_size for folder, dirs, files in os.walk(ROOT) for name in files)
    free = shutil.disk_usage(ROOT).free
    if published_bytes >= 1_000_000_000 or workspace >= 14_000_000_000 or free < 11_005_853_696:
        failures.append({"kind": "budget", "published_bytes": published_bytes, "workspace_bytes": workspace, "D_free_bytes": free})
    report = {"generated_utc": datetime.now(timezone.utc).isoformat(), "accepted": not failures, "commit": commit, "previous_commit": OLD, "previous_scan_sha256": hashlib.sha256(prior_bytes).hexdigest(), "previous_scan": str(prior_path.relative_to(ROOT)), "previous_classification_correction": "excluded-frame.html is manifest text/html; derived textual changes are permitted. Its output SHA and full byte scan were already verified.", "source_manifest_sha256": hashlib.sha256(manifest_data).hexdigest(), "files": records, "output_file_count": len(records), "output_bytes": published_bytes, "source_records_covered": len(source_paths), "reused_identical_git_blob_scans": reused, "new_blob_scans": len(records)-reused, "workspace_bytes_including_git": workspace, "D_free_bytes": free, "skipped_bytes": 0, "failures": failures}
    (OUT / "root-pages-tree-acceptance.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k != "files"}, ensure_ascii=False, indent=2))
    return int(bool(failures))

if __name__ == "__main__":
    raise SystemExit(main())
