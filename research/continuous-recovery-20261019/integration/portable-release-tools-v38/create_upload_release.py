"""Create or recover one owned GitHub draft and upload its three assets.

This script is parameterized by ``--version`` but is intentionally not run as
part of preparation. It never overwrites an asset, force-updates a tag, or
adopts a draft without the matching saved local configuration.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone

from portable_release_common import (
    FLOOR,
    REPO,
    ROOT,
    RUN_DATE,
    TAG,
    read_json,
    release_paths,
    rel,
    run_local,
    sha_path,
    validate_version,
)


DEADLINE = datetime(2026, 10, 19, 14, 15, tzinfo=timezone.utc)


def _assets(paths: dict) -> tuple[dict[str, tuple[int, str]], str]:
    portable = read_json(paths["portable"])
    assert portable.get("accepted") is True
    archive = paths["archive"]
    assert portable.get("archive") in {archive.name, rel(ROOT, archive)}
    assert portable.get("archive_sha256") == sha_path(archive)
    assert portable.get("archive_bytes") == archive.stat().st_size
    sidecar = paths["sidecar"]
    notice = ROOT / "NOTICE.md"
    assert sidecar.is_file() and notice.is_file()
    sidecar_tokens = sidecar.read_text(encoding="utf-8").strip().split()
    assert sidecar_tokens and sidecar_tokens[0] == portable["archive_sha256"]
    assert sidecar_tokens[-1] == archive.name
    expected = {
        archive.name: (archive.stat().st_size, portable["archive_sha256"]),
        sidecar.name: (sidecar.stat().st_size, sha_path(sidecar)),
        notice.name: (notice.stat().st_size, sha_path(notice)),
    }
    return expected, sha_path(paths["portable"])


def _release(releases: list[dict], tag: str) -> list[dict]:
    found = [item for item in releases if item.get("tag_name") == tag]
    assert len(found) <= 1
    return found


def _verify_owned_draft(data: dict, config: dict | None, expected: dict, portable_sha: str, target: str) -> None:
    assert data.get("tag_name") == TAG
    assert data.get("target_commitish") == target
    if config is None:
        raise RuntimeError("existing draft is unowned; saved release config is required")
    assert config.get("id") == data.get("id")
    assert config.get("tag") == TAG and config.get("target_commit") == target
    assert config.get("portable_acceptance_sha256") == portable_sha
    assert config.get("expected_assets") == {
        name: {"bytes": size, "sha256": digest}
        for name, (size, digest) in expected.items()
    }
    assert data.get("draft") is True, "owned draft is already published; use publisher"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="final version such as v32")
    args = parser.parse_args()
    version = validate_version(args.version)
    assert datetime.now(timezone.utc) < DEADLINE, "release deadline passed"
    paths = release_paths(version)
    assert shutil.disk_usage(ROOT).free >= FLOOR
    assert not paths["publication_report"].exists(), "preserve publication receipt"
    expected, portable_sha = _assets(paths)
    target = run_local(["git", "rev-parse", "HEAD"])
    assert run_local(["git", "rev-parse", "origin/main"]) == target, "main must equal origin/main"
    assert paths["notes"].is_file(), paths["notes"]
    endpoint = f"repos/{REPO}/releases?per_page=100"
    releases = json.loads(run_local(["gh", "api", endpoint], timeout=60))
    found = _release(releases, TAG)
    config = read_json(paths["draft"]) if paths["draft"].exists() else None
    if found:
        data = found[0]
        _verify_owned_draft(data, config, expected, portable_sha, target)
    else:
        assert config is None, "saved config without its release cannot be adopted"
        run_local([
            "gh", "release", "create", TAG, "--repo", REPO, "--target", target,
            "--draft", "--title", f"2008-05-12 archive · 2026-10-19 browser {version}",
            "--notes-file", str(paths["notes"]),
        ], timeout=120)
        releases = json.loads(run_local(["gh", "api", endpoint], timeout=60))
        found = _release(releases, TAG)
        assert found and found[0].get("draft") is True
        data = found[0]
        assert data.get("target_commitish") == target
        config_data = {
            "created_or_recovered_utc": datetime.now(timezone.utc).isoformat(),
            "version": version,
            "id": data["id"],
            "tag": TAG,
            "target_commit": target,
            "portable_acceptance_sha256": portable_sha,
            "expected_assets": {
                name: {"bytes": size, "sha256": digest}
                for name, (size, digest) in expected.items()
            },
            "draft": True,
        }
        paths["draft"].write_text(json.dumps(config_data, indent=2) + "\n", encoding="utf-8")
        config = config_data
    uploaded = {asset["name"]: asset for asset in data.get("assets", [])}
    assert set(uploaded) <= set(expected), "refusing unrelated pre-existing asset"
    pending = []
    for name, (size, digest) in expected.items():
        if name in uploaded:
            asset = uploaded[name]
            assert asset.get("state") == "uploaded" and asset.get("size") == size
            assert asset.get("digest") == "sha256:" + digest, name
        else:
            pending.append(name)
    if pending:
        run_local(["gh", "release", "upload", TAG, "--repo", REPO, *[str(ROOT / name) if name == "NOTICE.md" else str(paths["archive"].with_name(name)) for name in pending]], timeout=600)
        releases = json.loads(run_local(["gh", "api", endpoint], timeout=60))
        found = _release(releases, TAG)
        assert found and found[0].get("draft") is True
        data = found[0]
        _verify_owned_draft(data, config, expected, portable_sha, target)
        uploaded = {asset["name"]: asset for asset in data.get("assets", [])}
    assert set(uploaded) == set(expected)
    for name, (size, digest) in expected.items():
        asset = uploaded[name]
        assert asset.get("state") == "uploaded" and asset.get("size") == size
        assert asset.get("digest") == "sha256:" + digest, name
    print(json.dumps({"version": version, "draft_release_id": data["id"], "target": target, "uploaded_assets_requested": len(pending), "published": False}))


if __name__ == "__main__":
    main()
