"""Verify all three owned GitHub assets, publish the draft, and reverify it."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone

from portable_release_common import (
    FLOOR,
    REPO,
    RUN_DATE,
    ROOT,
    TAG,
    read_json,
    release_paths,
    rel,
    run_local,
    sha_path,
    validate_version,
)


def _expected(paths: dict) -> tuple[dict[str, tuple[int, str]], str]:
    portable = read_json(paths["portable"])
    assert portable.get("accepted") is True
    archive = paths["archive"]
    assert portable.get("archive") in {archive.name, rel(ROOT, archive)}
    assert portable.get("archive_sha256") == sha_path(archive)
    assert portable.get("archive_bytes") == archive.stat().st_size
    expected = {
        archive.name: (archive.stat().st_size, portable["archive_sha256"]),
        paths["sidecar"].name: (paths["sidecar"].stat().st_size, sha_path(paths["sidecar"])),
        "NOTICE.md": ((ROOT / "NOTICE.md").stat().st_size, sha_path(ROOT / "NOTICE.md")),
    }
    return expected, sha_path(paths["portable"])


def _api(endpoint: str) -> dict:
    return json.loads(run_local(["gh", "api", endpoint], timeout=60))


def _verify(data: dict, release_id: int, target: str, expected: dict[str, tuple[int, str]]) -> list[dict]:
    assert data.get("id") == release_id
    assert data.get("tag_name") == TAG and data.get("target_commitish") == target
    assert len(data.get("assets", [])) == 3
    assert {asset.get("name") for asset in data["assets"]} == set(expected)
    checks = []
    for asset in data["assets"]:
        size, digest = expected[asset["name"]]
        assert asset.get("state") == "uploaded" and asset.get("size") == size
        assert asset.get("digest") == "sha256:" + digest
        checks.append({
            "id": asset["id"],
            "name": asset["name"],
            "state": asset["state"],
            "bytes": asset["size"],
            "digest": asset["digest"],
            "expected_sha256": digest,
            "browser_download_url": asset.get("browser_download_url"),
            "accepted": True,
        })
    return checks


def _verify_saved_published_config(config: dict, data: dict, expected: dict[str, tuple[int, str]],
                                   portable_sha: str, target: str) -> None:
    """Validate an owned saved config after a publish response was lost."""
    # The saved config can still say draft=True when GitHub published the
    # release but the edit response or subsequent verification was lost.
    # Ownership is proven by the exact saved id/tag/target and asset bindings.
    assert config.get("draft") in (True, False)
    assert data.get("draft") is False
    assert config.get("id") == data.get("id")
    assert config.get("tag") == TAG and data.get("tag_name") == TAG
    assert config.get("target_commit") == target and data.get("target_commitish") == target
    assert config.get("portable_acceptance_sha256") == portable_sha
    assert config.get("expected_assets") == {
        name: {"bytes": size, "sha256": digest}
        for name, (size, digest) in expected.items()
    }


def _recovered_report(version: str, release_id: int, target: str, tag_commit: str,
                      data: dict, before: list[dict], portable_path: str) -> dict:
    return {
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "accepted": True,
        "published": True,
        "recovered_existing_publication": True,
        "mutation_performed": False,
        "version": version,
        "release_id": release_id,
        "tag": TAG,
        "url": data.get("html_url"),
        "target_commit": target,
        "resolved_tag_commit": tag_commit,
        "assets_before_publish": before,
        "assets": before,
        "verification": "Owned saved draft=false config matched release id, tag, target and all three asset digests; publication was reverified without mutation.",
        "portable_acceptance": portable_path,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="final version such as v32")
    args = parser.parse_args()
    version = validate_version(args.version)
    assert datetime.now(timezone.utc) < datetime(2026, 10, 20, 14, 15, tzinfo=timezone.utc), "release deadline passed"
    assert shutil.disk_usage(ROOT).free >= FLOOR
    paths = release_paths(version)
    assert not paths["publication_report"].exists(), "preserve publication receipt"
    config = read_json(paths["draft"])
    expected, portable_sha = _expected(paths)
    assert config.get("tag") == TAG and config.get("portable_acceptance_sha256") == portable_sha
    assert config.get("expected_assets") == {
        name: {"bytes": size, "sha256": digest}
        for name, (size, digest) in expected.items()
    }
    target = config["target_commit"]
    assert run_local(["git", "rev-parse", "HEAD"]) == target
    assert run_local(["git", "rev-parse", "origin/main"]) == target
    release_id = config["id"]
    data = _api(f"repos/{REPO}/releases/{release_id}")
    before = _verify(data, release_id, target, expected)
    if data.get("draft") is False:
        _verify_saved_published_config(config, data, expected, portable_sha, target)
        tag_commit = _api(f"repos/{REPO}/commits/{TAG}")["sha"]
        assert tag_commit == target
        report = _recovered_report(version, release_id, target, tag_commit, data, before,
                                   rel(ROOT, paths["portable"]))
        paths["publication_report"].write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"published": True, "recovered": True, "version": version,
                          "release_id": release_id, "mutation_performed": False,
                          "target_commit": tag_commit}))
        return
    assert config.get("draft") is True
    assert data.get("draft") is True, "release is already published or unowned"
    run_local(["gh", "release", "edit", TAG, "--repo", REPO, "--draft=false", "--latest"], timeout=120)
    data = _api(f"repos/{REPO}/releases/{release_id}")
    after = _verify(data, release_id, target, expected)
    assert data.get("draft") is False
    tag_commit = _api(f"repos/{REPO}/commits/{TAG}")["sha"]
    assert tag_commit == target
    report = {
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "accepted": True,
        "published": True,
        "version": version,
        "release_id": release_id,
        "tag": TAG,
        "url": data.get("html_url"),
        "target_commit": target,
        "resolved_tag_commit": tag_commit,
        "assets_before_publish": before,
        "assets": after,
        "verification": "All three GitHub assets matched local size and SHA-256 digest before and after publication; tag resolved to the exact main/origin-main target.",
        "portable_acceptance": rel(ROOT, paths["portable"]),
        "recovered_existing_publication": False,
        "mutation_performed": True,
    }
    paths["publication_report"].write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"published": True, "version": version, "url": data.get("html_url"), "assets": len(after), "target_commit": tag_commit}))


if __name__ == "__main__":
    main()
