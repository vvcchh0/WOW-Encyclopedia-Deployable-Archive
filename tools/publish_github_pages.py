#!/usr/bin/env python3
"""Prepare a GitHub Pages branch from a validated static site.

The default operation is local and transactional: it builds a commit with a
temporary index, then updates only the requested local branch with an expected
old SHA.  Network push is opt-in via ``--push`` and is never forced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
MAX_PUBLISHED_BYTES = 1_000_000_000
ZERO_SHA = "0" * 40
FORBIDDEN_COMPONENTS = {".git", ".env", "rawresearch", "privateprofile"}
REDACT_URL = re.compile(r"(https?://)([^/@\s]+):([^/@\s]+)@", re.I)


class PublishError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def redacted(text: str) -> str:
    return REDACT_URL.sub(r"\1***:***@", text)


def reparse_point(path: Path) -> bool:
    try:
        attributes = os.lstat(path).st_file_attributes  # type: ignore[attr-defined]
    except AttributeError:
        return stat.S_ISLNK(os.lstat(path).st_mode)
    return bool(attributes & 0x400) or stat.S_ISLNK(os.lstat(path).st_mode)


def git_command(
    git_dir: Path,
    work_tree: Path,
    args: list[str],
    *,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    # Exact per-command safe.directory entries avoid changing global Git trust.
    command = [
        "git",
        "-c",
        f"safe.directory={git_dir}",
        "-c",
        f"safe.directory={work_tree}",
        "-c",
        "core.autocrlf=false",
        "--git-dir",
        str(git_dir),
        "--work-tree",
        str(work_tree),
        *args,
    ]
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    return subprocess.run(
        command,
        cwd=str(work_tree),
        env=process_env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def git_output(git_dir: Path, work_tree: Path, args: list[str], *, env: dict[str, str] | None = None) -> str:
    result = git_command(git_dir, work_tree, args, env=env)
    return result.stdout.strip()


def validate_site(site: Path, root: Path) -> dict[str, Any]:
    scratch = (root / ".scratch").resolve()
    site = site.resolve()
    try:
        site.relative_to(scratch)
    except ValueError as exc:
        raise PublishError(f"site must be below {scratch}: {site}") from exc
    if not site.is_dir() or reparse_point(site):
        raise PublishError(f"site must be a regular directory without reparse point: {site}")

    required = [site / "index.html", site / "404.html", site / ".nojekyll"]
    missing_required = [str(path.relative_to(site)) for path in required if not path.is_file()]
    if missing_required:
        raise PublishError(f"missing required Pages files: {', '.join(missing_required)}")

    total_bytes = 0
    file_count = 0
    forbidden: list[str] = []
    reparse: list[str] = []
    nonregular: list[str] = []
    records: list[dict[str, Any]] = []
    for current, directories, files in os.walk(site, topdown=True, followlinks=False):
        current_path = Path(current)
        kept_dirs: list[str] = []
        for name in directories:
            path = current_path / name
            rel = path.relative_to(site).as_posix()
            if name.casefold() in FORBIDDEN_COMPONENTS:
                forbidden.append(rel)
            if reparse_point(path):
                reparse.append(rel)
            else:
                kept_dirs.append(name)
        directories[:] = kept_dirs
        for name in files:
            path = current_path / name
            rel = path.relative_to(site).as_posix()
            parts = {part.casefold() for part in Path(rel).parts}
            if parts & FORBIDDEN_COMPONENTS:
                forbidden.append(rel)
            if reparse_point(path):
                reparse.append(rel)
                continue
            if not path.is_file():
                nonregular.append(rel)
                continue
            size = path.stat().st_size
            total_bytes += size
            file_count += 1
            records.append({"path": rel, "bytes": size})

    if forbidden:
        raise PublishError(f"forbidden publication names: {forbidden[:8]}")
    if reparse:
        raise PublishError(f"symlink/reparse paths are not publishable: {reparse[:8]}")
    if nonregular:
        raise PublishError(f"non-regular files are not publishable: {nonregular[:8]}")
    if total_bytes >= MAX_PUBLISHED_BYTES:
        raise PublishError(f"published files exceed 1GB: {total_bytes} bytes")
    return {
        "site": str(site),
        "required_files": [str(path.relative_to(site)).replace("\\", "/") for path in required],
        "file_count": file_count,
        "total_bytes": total_bytes,
        "max_bytes": MAX_PUBLISHED_BYTES,
        "files": records,
    }


def ref_sha(git_dir: Path, work_tree: Path, ref: str, *, env: dict[str, str]) -> str:
    result = git_command(git_dir, work_tree, ["rev-parse", "--verify", ref], env=env, check=False)
    if result.returncode == 0:
        value = result.stdout.strip()
        if re.fullmatch(r"[0-9a-fA-F]{40}", value):
            return value.lower()
    return ZERO_SHA


def build_commit(
    *,
    root: Path,
    site: Path,
    branch: str,
    message: str,
    report_path: Path,
    push: bool,
) -> dict[str, Any]:
    git_dir = (root / ".git").resolve()
    if not git_dir.is_dir():
        raise PublishError(f"Git directory not found: {git_dir}")
    site_info = validate_site(site, root)
    source_head = git_output(git_dir, root, ["rev-parse", "HEAD"])
    index_path = root / ".scratch" / f".publish-index-{os.getpid()}"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    if index_path.exists():
        index_path.unlink()
    env = {"GIT_INDEX_FILE": str(index_path)}
    main_index = git_dir / "index"
    main_index_before = sha256_file(main_index)
    branch_ref = f"refs/heads/{branch}"
    old_sha = ref_sha(git_dir, root, branch_ref, env=env)
    parent_sha = old_sha if old_sha != ZERO_SHA else source_head
    parent_source = "existing local branch" if old_sha != ZERO_SHA else "current HEAD"
    result: dict[str, Any] = {
        "started_utc": utc_now(),
        "root": str(root),
        "site": site_info,
        "branch": branch,
        "branch_ref": branch_ref,
        "old_branch_sha": old_sha,
        "parent_sha": parent_sha,
        "parent_source": parent_source,
        "source_head_before": source_head,
        "main_index_sha_before": main_index_before,
        "push_requested": push,
        "network_push_performed": False,
        "commands": [
            "git read-tree --empty",
            "git add --all --force .",
            "git write-tree",
            "git commit-tree <tree> -p <parent>",
            "git update-ref <branch-ref> <new-sha> <old-sha>",
        ],
    }
    try:
        git_command(git_dir, site, ["read-tree", "--empty"], env=env)
        git_command(git_dir, site, ["add", "--all", "--force", "."], env=env)
        tree_sha = git_output(git_dir, site, ["write-tree"], env=env)
        if not message:
            raise PublishError("commit message must not be empty")
        # commit-tree takes the message on stdin; use the same isolated index
        # and exact safe.directory options as the other commands.
        command = [
            "git", "-c", f"safe.directory={git_dir}", "-c", f"safe.directory={site}",
            "-c", "core.autocrlf=false", "--git-dir", str(git_dir), "--work-tree", str(site),
            "commit-tree", tree_sha, "-p", parent_sha,
        ]
        commit_result = subprocess.run(
            command,
            cwd=str(site),
            env={**os.environ, **env},
            input=message + "\n",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        new_sha = commit_result.stdout.strip()
        git_command(git_dir, site, ["update-ref", branch_ref, new_sha, old_sha], env=env)
        result.update({"tree_sha": tree_sha, "new_commit_sha": new_sha, "local_ref_updated": True})
        if push:
            push_result = git_command(
                git_dir,
                site,
                ["push", "--porcelain", "origin", f"{branch_ref}:{branch_ref}"],
                env=env,
            )
            result.update({
                "network_push_performed": True,
                "push_returncode": push_result.returncode,
                "push_stdout": redacted(push_result.stdout),
                "push_stderr": redacted(push_result.stderr),
            })
        source_after = git_output(git_dir, root, ["rev-parse", "HEAD"])
        result.update({
            "source_head_after": source_after,
            "source_head_unchanged": source_after == source_head,
            "main_index_sha_after": sha256_file(main_index),
            "main_index_unchanged": sha256_file(main_index) == main_index_before,
            "status": "success",
            "finished_utc": utc_now(),
        })
    except (subprocess.CalledProcessError, OSError, PublishError) as exc:
        detail = str(exc)
        if isinstance(exc, subprocess.CalledProcessError):
            detail = f"returncode={exc.returncode}; stdout={redacted(exc.stdout or '')}; stderr={redacted(exc.stderr or '')}"
        result.update({"status": "failed", "error": detail, "finished_utc": utc_now()})
        raise PublishError(detail) from exc
    finally:
        try:
            if index_path.exists():
                index_path.unlink()
        except OSError:
            result["temporary_index_cleanup_error"] = str(index_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, required=True, help="validated static output below <repo>/.scratch")
    parser.add_argument("--branch", default="gh-pages", help="local/remote branch to prepare")
    parser.add_argument("--message", default="Publish static GitHub Pages site", help="commit message")
    parser.add_argument("--report", type=Path, help="JSON report path")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--push", action="store_true", help="explicitly push the prepared branch without force")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.repo_root.resolve()
    report = (args.report or root / "research/github-pages-20261013/publish-prepare-report.json").resolve()
    try:
        if not re.fullmatch(r"[A-Za-z0-9._/-]+", args.branch) or args.branch.startswith("/") or args.branch.endswith("/"):
            raise PublishError(f"invalid branch name: {args.branch}")
        result = build_commit(
            root=root,
            site=(root / args.site).resolve() if not args.site.is_absolute() else args.site.resolve(),
            branch=args.branch,
            message=args.message,
            report_path=report,
            push=args.push,
        )
        print(json.dumps({
            "status": result["status"],
            "branch": result["branch"],
            "new_commit_sha": result.get("new_commit_sha"),
            "parent_sha": result.get("parent_sha"),
            "network_push_performed": result.get("network_push_performed"),
            "report": str(report),
        }, ensure_ascii=False))
        return 0
    except PublishError as exc:
        if not report.exists():
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(json.dumps({"status": "failed", "error": str(exc), "finished_utc": utc_now()}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"publish_github_pages: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
