"""Parent acceptance: reconcile final package, frozen sources and actual QA."""
import hashlib
import json
from pathlib import Path
import shutil
from datetime import datetime, timezone
import zipfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SITE = ROOT / ".scratch/pages-local-maintenance-20261014-v5"
ARCHIVE = ROOT / "artifacts/WOW_Encyclopedia_20080512_browser_20261014_v5.zip"
MIN_FREE = 10 * 1024**3 + 256 * 1024**2


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main():
    provenance = read(SITE / "export-provenance.json")
    previous = read(ROOT / ".scratch/pages-local-maintenance-20261014-v4/export-provenance.json")
    current = {r["output_path"]: (r["derived_sha256"], r["derived_length"]) for r in provenance["files"]}
    prior = {r["output_path"]: (r["derived_sha256"], r["derived_length"]) for r in previous["files"]}
    assert current.keys() == prior.keys()
    changed = sorted(p for p in current if current[p] != prior[p])
    assert changed == ["__offline/pages_runtime.js"], changed
    frozen_sha = digest(ROOT / "offline/build-manifest.json")
    assert frozen_sha == "397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459"
    assert digest(ROOT / "tools/export_github_pages.py") == "ffa158842e0197f80ceea19b81ec2cdc86506257a60bcdf5b79e6e449584174d"
    assert digest(ROOT / "tools/package_pages_archive.py") == "b9f942fd099dbefa35bdd84ceb63ce2ead5da6ffcead34382a12ce1b63302c0f"

    package_path = HERE / "portable-package-v5-report.json"
    package = read(package_path)
    verification = package["verification"]
    assert verification["crc_sha_length_all_passed"] and verification["whitelist_exact"]
    members = {m["path"]: m for m in verification["members"]}
    assert ARCHIVE.stat().st_size == verification["archive_bytes"]
    with zipfile.ZipFile(ARCHIVE) as zipped:
        actual = {info.filename: info for info in zipped.infolist()}
        assert actual.keys() == members.keys()
        assert all(actual[p].file_size == m["bytes"] and actual[p].CRC == int(m["crc32"], 16) for p, m in members.items())
    for path, (sha, length) in current.items():
        member = members["site/" + path]
        assert (member["sha256"], member["bytes"]) == (sha, length), path
    assert members["site/export-provenance.json"]["sha256"] == digest(SITE / "export-provenance.json")

    qa_path = HERE / "portable-validation/v5/portable-bundle-validation-v5.json"
    browser_path = HERE / "portable-validation/v5/portable-browser-validation-v5.json"
    qa, browser = read(qa_path), read(browser_path)
    assert qa["passed"] and not qa["failures"]
    assert qa["checks"]["receipt"]["archive_sha256"] == verification["archive_sha256"]
    assert qa["checks"]["http"]["passed"]
    assert browser["passed"] and len(browser["scenarios"]) == 6
    assert all(s["passed"] for s in browser["scenarios"])
    for key in ("externalRequests", "postAttempts", "nonGetRequests", "pageErrors", "requestFailures"):
        assert browser["counts"][key] == 0, key
    assert " " in qa["scratch_requested"]
    assert qa["scratch_cleanup"]["cleaned"]
    preview = read(HERE / "preview-validation.json")
    assert preview["passed"] and len(preview["checks"]) == 7
    resource = read(HERE / "resource-validation-v4.json")
    assert resource["passed"]
    free = shutil.disk_usage(ROOT).free
    assert free >= MIN_FREE

    summary = {k: v for k, v in package.items() if k != "verification"}
    summary["verification"] = {k: v for k, v in verification.items() if k != "members"}
    summary["verification"]["uncompressed_member_bytes"] = sum(m["bytes"] for m in members.values())
    summary["full_report"] = {"path": str(package_path.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(package_path)}
    acceptance = {
        "schema": "local-maintenance-parent-acceptance/v1",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "accepted": True,
        "code_commit": "2348cbeaea39f26f14b01acd5e35e10ff8439ef0",
        "source_manifest_sha256": frozen_sha,
        "v4_v5": {"records": len(current), "unchanged_records": len(current) - len(changed), "changed_paths": changed, "members_same": True},
        "packaged_provenance_records_matched": len(current),
        "archive": {"path": str(ARCHIVE.relative_to(ROOT)).replace("\\", "/"), "bytes": verification["archive_bytes"], "sha256": verification["archive_sha256"], "members": len(members)},
        "unit_tests": {"exporter": 15, "portable_pack": 12, "note": "Exporter rerun after runtime correction; portable-pack tests passed before the unchanged package tool was frozen."},
        "portable_qa": {"path": str(qa_path.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(qa_path), "browser_scenarios": 6, "browser_sha256": digest(browser_path), "scratch_with_spaces": True, "own_scratch_cleaned": True},
        "preview": {"url": preview["base_url"], "pid": preview["process"]["pid"], "checks": 7},
        "disk": {"free_bytes": free, "minimum_free_bytes": MIN_FREE},
        "boundaries": {"new_network_resources": 0, "gallery_original_thumbnail_pairs_added": 0, "published_this_round": False, "google_review_submitted": False, "historical_artifacts_preserved": True},
    }
    write_new(HERE / "portable-package-summary.json", summary)
    write_new(HERE / "root-acceptance.json", acceptance)
    print(json.dumps(acceptance, ensure_ascii=False))


if __name__ == "__main__":
    main()
