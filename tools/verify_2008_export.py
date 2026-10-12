"""Verify the exported 2008 tree against its raw sources and selection index."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
HOME_SHA = "4951546ef139ac64d93f1811dec06ef2b84dea22cd9d278fac9262070b079ec3"


def main() -> int:
    mapping_path = ROOT / "mirror/20080512/url-map.json"
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    index = json.loads((ROOT / "research/acquisition-2008/integration/index.json").read_text(encoding="utf-8"))
    errors = []
    paths = {}
    archives = {}
    for item in mapping["files"]:
        try:
            path = (ROOT / item["local_path"]).resolve()
            path.relative_to(mapping_path.parent.resolve())
            body = path.read_bytes()
            assert hashlib.sha256(body).hexdigest() == item["sha256"], "export SHA256"
            assert len(body) == item["content_length"], "export length"
            key = path.relative_to(mapping_path.parent).as_posix().casefold()
            assert key not in paths or paths[key] == item["sha256"], "case collision"
            paths[key] = item["sha256"]
            assert item["temporal_class"] in {"anchor_consistent", "same_day_static"}, "date selection"
            if item["actual_timestamp"] > "20080512235959":
                assert item["cdx_verified_payload_reuse"] and item["cdx_digest_matches"], "unproven late payload"
                assert item["indexed_capture_timestamp"] <= "20080512210044", "late CDX proof"
            if item.get("zip_file"):
                source = (ROOT / item["zip_file"]).resolve()
                source.relative_to(ROOT)
                if source not in archives:
                    archives[source] = zipfile.ZipFile(source)
                original = archives[source].read(item["zip_entry"])
            else:
                source = (ROOT / item["source_file"]).resolve()
                source.relative_to(ROOT)
                original = source.read_bytes()
            assert body == original, "source/export byte difference"
        except Exception as error:
            errors.append({"url": item["logical_url"], "error": str(error)})
    for archive in archives.values():
        archive.close()
    core = [item for item in mapping["files"] if item["role"] == "core_page"]
    core_checks = {
        "core_pages_52": len(core) == 52,
        "numeric_articles_51": sum(Path(item["local_path"]).stem.isdigit() for item in core) == 51,
        "core_html_mime": all(item["mime"].lower().startswith("text/html") for item in core),
        "exact_homepage": any(item["logical_url"].endswith("/index.xml") and item["actual_timestamp"] == "20080512210044" and item["sha256"] == HOME_SHA for item in core),
        "mapping_matches_all_preferred": {item["logical_url"] for item in mapping["files"]} == {item["logical_url"] for item in index["logical_urls"] if item["state"] == "preferred"},
    }
    errors.extend({"check": key, "error": "failed"} for key, passed in core_checks.items() if not passed)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "passed": not errors,
        "files_checked": len(mapping["files"]),
        "unique_casefold_paths": len(paths),
        "entity_bytes": sum(item["content_length"] for item in mapping["files"]),
        "source_zip_volumes_read": len(archives),
        "core_checks": core_checks,
        "errors": errors,
        "workspace_bytes_before_package": sum(path.stat().st_size for path in ROOT.rglob("*") if path.is_file()),
        "disk_free_bytes_before_package": shutil.disk_usage(ROOT).free,
    }
    output = ROOT / "research/acquisition-2008/acceptance/export-validation.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
