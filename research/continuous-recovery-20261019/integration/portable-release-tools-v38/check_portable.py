"""Validate one accepted 2026-10-19 v38 portable archive and smoke its server.

The command is intentionally a checker only. It reads an already-created ZIP;
it does not create an archive, contact GitHub, or publish a release.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import stat
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.request import ProxyHandler, Request, build_opener

from portable_release_common import (
    FLOOR,
    ROOT,
    RUN_DATE,
    TAG,
    browser_paths,
    guide_paths,
    read_json,
    rel,
    release_paths,
    safe_site_path,
    sha_bytes,
    sha_path,
    smoke_paths,
    validate_version,
)


def _assert_local_receipt(path: Path, site: Path) -> dict:
    data = read_json(path)
    assert data.get("accepted") is True, path
    assert data.get("published") is not True, path
    assert data.get("local_site") == rel(ROOT, site), (path, data.get("local_site"))
    return data


def _assert_accepted_receipt(path: Path) -> dict:
    data = read_json(path)
    assert data.get("accepted") is True, path
    return data


def _bound(receipt: dict, path: Path, digest: str) -> bool:
    wanted = rel(ROOT, path)
    return any(
        item.get("path") == wanted and item.get("sha256") == digest
        for item in receipt.get("bindings", [])
        if isinstance(item, dict)
    )


def _verify_receipts(paths: dict[str, Path]) -> tuple[dict, dict, dict, dict, bytes, dict]:
    local = _assert_local_receipt(paths["local"], paths["site"])
    export = read_json(paths["export"])
    browser = _assert_accepted_receipt(paths["browser"])
    pages_online = _assert_local_receipt(paths["pages_online"], paths["site"])
    assert export.get("accepted") is True and export.get("site") == rel(ROOT, paths["site"])
    assert browser.get("export_provenance_sha256")
    assert browser.get("external_requests") == 0
    assert browser.get("network_requests_to_external_sources") == 0
    assert pages_online.get("accepted") is True
    provenance_path = paths["site"] / "export-provenance.json"
    provenance_bytes = provenance_path.read_bytes()
    provenance = json.loads(provenance_bytes)
    provenance_sha = sha_bytes(provenance_bytes)
    assert export.get("export_provenance_sha256") == provenance_sha
    assert browser.get("export_provenance_sha256") == provenance_sha
    assert local.get("export_provenance_sha256", provenance_sha) == provenance_sha
    actual_site_files = sum(1 for item in paths["site"].rglob("*") if item.is_file())
    assert local.get("actual_files") == actual_site_files, (local.get("actual_files"), actual_site_files)
    assert export.get("actual_files") == actual_site_files, (export.get("actual_files"), actual_site_files)
    assert _bound(local, paths["export"], sha_path(paths["export"]))
    assert _bound(local, paths["browser"], sha_path(paths["browser"]))
    actual_groups = len((provenance.get("guide_image_collections") or {}).get("groups", []))
    actual_images = sum(
        len(group.get("images", []))
        for group in (provenance.get("guide_image_collections") or {}).get("groups", [])
    )
    assert local.get("guide_collection_images") == actual_images
    for item in pages_online.get("objects", []):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            continue
        path = paths["site"] / safe_site_path(item["path"])
        assert path.is_file(), path
        assert len(path.read_bytes()) == item["local_bytes"]
        assert sha_path(path) == item["local_sha256"]
    return local, export, browser, pages_online, provenance_bytes, {
        "groups": actual_groups,
        "images": actual_images,
        "provenance_sha256": provenance_sha,
    }


def _expected_members(paths: dict[str, Path], provenance: dict) -> dict[str, tuple[str, int]]:
    expected = {}
    for item in provenance.get("files", []):
        output = safe_site_path(item["output_path"]).as_posix()
        expected[f"site/{output}"] = (item["derived_sha256"], item["derived_length"])
    provenance_bytes = paths["site"].joinpath("export-provenance.json").read_bytes()
    expected["site/export-provenance.json"] = (sha_bytes(provenance_bytes), len(provenance_bytes))
    for relative in ("NOTICE.md", "tools/serve_pages_preview.py"):
        data = (ROOT / relative).read_bytes()
        expected[relative] = (sha_bytes(data), len(data))
    return expected


def _category(path: PurePosixPath) -> str:
    suffix = path.suffix.lower()
    if suffix in {".html", ".xml", ".xsl"}:
        return "markup"
    if suffix in {".js", ".css"}:
        return "scripts_and_styles"
    if suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".ico"}:
        return "images"
    return "other"


def _check_zip(paths: dict[str, Path], provenance: dict, producer: dict, before: int) -> tuple[str, int, int, dict, int]:
    archive = paths["archive"]
    with archive.open("rb") as stream:
        archive_sha = hashlib.file_digest(stream, "sha256").hexdigest()
    assert archive_sha == producer["verification"]["archive_sha256"]
    assert producer.get("archive") in {archive.name, rel(ROOT, archive)}
    expected = _expected_members(paths, provenance)
    checked_bytes = 0
    compression: dict[str, dict[str, int]] = {}
    with zipfile.ZipFile(archive) as zf:
        infos = zf.infolist()
        names = [item.filename for item in infos]
        allowed = set(expected) | {"README.md", "START_BROWSE.cmd", "archive-metadata.json", "FILE_SHA256SUMS.txt"}
        assert len(names) == len(set(names)) and set(names) == allowed
        sums = {}
        for line in zf.read("FILE_SHA256SUMS.txt").decode("utf-8").splitlines():
            if line.startswith("#") or not line:
                continue
            digest, length, relative = line.split("  ", 2)
            assert relative not in sums
            sums[relative] = (digest, int(length))
        assert set(sums) == allowed - {"FILE_SHA256SUMS.txt"}
        for item in infos:
            path = PurePosixPath(item.filename)
            assert not path.is_absolute() and ".." not in path.parts and "\\" not in item.filename
            assert path.parts and ":" not in path.parts[0]
            mode = item.external_attr >> 16
            assert not stat.S_ISLNK(mode)
            data = zf.read(item)
            actual = (sha_bytes(data), len(data))
            checked_bytes += len(data)
            totals = compression.setdefault(
                _category(path),
                {"members": 0, "uncompressed_bytes": 0, "compressed_member_bytes": 0},
            )
            totals["members"] += 1
            totals["uncompressed_bytes"] += item.file_size
            totals["compressed_member_bytes"] += item.compress_size
            if item.filename in expected:
                assert actual == expected[item.filename], item.filename
            if item.filename in sums:
                assert actual == sums[item.filename], item.filename
        assert producer.get("package_member_count") in (None, len(names))
        assert producer.get("verification", {}).get("member_count") in (None, len(names))
        assert before - checked_bytes >= FLOOR
        extract = paths["extract"]
        assert not extract.exists()
        extract.mkdir()
        assert shutil.disk_usage(ROOT).free >= FLOOR + checked_bytes
        for item in infos:
            assert shutil.disk_usage(ROOT).free >= FLOOR + item.file_size
            zf.extract(item, extract)
    return archive_sha, archive.stat().st_size, checked_bytes, compression, len(infos)


def _serve_smoke(paths: dict[str, Path], provenance: dict, local: dict, browser: dict, pages_online: dict) -> tuple[list[dict], dict]:
    smoke, guide_counts = smoke_paths(provenance, local, browser, pages_online, paths["site"])
    for relative in smoke:
        source_file = paths["site"] / safe_site_path(relative)
        assert source_file.is_file(), ("smoke source missing", relative)
    requests = []
    child = None
    try:
        with paths["server_log"].open("w", encoding="utf-8") as log:
            child = subprocess.Popen(
                [sys.executable, "-I", str(paths["extract"] / "tools/serve_pages_preview.py"),
                 "--site", str(paths["extract"] / "site"), "--port", "0"],
                cwd=paths["extract"], stdout=log, stderr=log,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            deadline = time.monotonic() + 20
            base = None
            while time.monotonic() < deadline:
                match = re.search(
                    r"Archive preview: (http://127\.0\.0\.1:\d+/\S*)",
                    paths["server_log"].read_text(encoding="utf-8"),
                )
                if match:
                    base = match.group(1)
                    break
                if child.poll() is not None:
                    raise RuntimeError("packaged server exited before startup")
                time.sleep(0.1)
            assert base
            opener = build_opener(ProxyHandler({}))
            for relative in smoke:
                local_file = paths["extract"] / "site" / safe_site_path(relative)
                data = local_file.read_bytes()
                for method in ("GET", "HEAD"):
                    with opener.open(Request(base + relative, method=method), timeout=10) as response:
                        body = response.read()
                        assert response.status == 200
                        assert int(response.headers["Content-Length"]) == len(data)
                        assert body == data if method == "GET" else body == b""
                        requests.append({"path": relative, "method": method, "status": response.status,
                                         "bytes": len(body), "content_type": response.headers.get("Content-Type")})
    finally:
        if child is not None and child.poll() is None:
            child.terminate()
            child.wait(timeout=10)
    return requests, {"paths": len(smoke), **guide_counts}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="final version such as v32")
    args = parser.parse_args()
    version = validate_version(args.version)
    paths = release_paths(version)
    assert not paths["portable"].exists(), "preserve existing portable receipt"
    assert paths["local"].is_file() and paths["export"].is_file() and paths["browser"].is_file() and paths["pages_online"].is_file()
    assert paths["package_report"].is_file() and paths["archive"].is_file()
    before = shutil.disk_usage(ROOT).free
    assert before >= FLOOR and not paths["extract"].exists()
    local, export, browser, pages_online, provenance_bytes, guide_counts = _verify_receipts(paths)
    provenance = json.loads(provenance_bytes)
    producer = read_json(paths["package_report"])
    assert producer.get("network_performed") is False
    archive_sha, archive_bytes, checked_bytes, compression, members_read = _check_zip(paths, provenance, producer, before)
    requests, smoke = _serve_smoke(paths, provenance, local, browser, pages_online)
    after = shutil.disk_usage(ROOT).free
    assert after >= FLOOR
    report = {
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "accepted": True,
        "version": version,
        "tag": TAG,
        "archive": rel(ROOT, paths["archive"]),
        "archive_sha256": archive_sha,
        "archive_bytes": archive_bytes,
        "members_read": members_read,
        "uncompressed_bytes_read": checked_bytes,
        "export_provenance_sha256": guide_counts["provenance_sha256"],
        "guide_collection": {"groups": guide_counts["groups"], "images": guide_counts["images"]},
        "smoke": smoke,
        "compression_by_suffix": compression,
        "isolated_server": True,
        "python_isolated_flag": True,
        "requests": requests,
        "external_network_requests": 0,
        "space_before": before,
        "space_after": after,
        "scope": "All ZIP members read and checked; extracted packaged server GET/HEAD smoke derived from final provenance and local acceptance. Browser rendering is reused from the accepted versioned receipts.",
    }
    paths["portable"].write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("accepted", "version", "archive_bytes", "members_read", "uncompressed_bytes_read", "space_after")}))


if __name__ == "__main__":
    main()
