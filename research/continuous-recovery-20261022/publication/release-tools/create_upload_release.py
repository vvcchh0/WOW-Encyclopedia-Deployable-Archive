#!/usr/bin/env python3
"""Create an owned GitHub draft and upload its three verified assets.

Network work is disabled unless ``--execute`` is explicitly supplied. This
entrypoint never publishes a release, force-updates a tag, or replaces assets.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import quote
import uuid


ROOT = Path(__file__).resolve().parents[4]
CONFIG_SCHEMA = "wow-github-release-create-upload-config/v1"
INTENT_SCHEMA = "wow-github-release-draft-intent/v1"
RECEIPT_SCHEMA = "wow-github-release-upload-receipt/v1"
PACKAGE_ACCEPTANCE_SCHEMA = "wow-portable-check-receipt/v1"
DEADLINE_UTC = datetime(2026, 10, 22, 14, 51, 33, tzinfo=timezone.utc)
MIN_PROCESS_START_INTERVAL = 5.2
GH_READ_TIMEOUT = 60
GH_CREATE_TIMEOUT = 120
GH_UPLOAD_TIMEOUT = 600
GH_PROXY_URL = "http://127.0.0.1:7890"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
VERSION_RE = re.compile(r"^v[0-9]+$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
TAG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$")
INTENT_NAME = "create-upload-intent.json"
RECEIPT_NAME = "create-upload-receipt.json"


class ReleaseToolError(RuntimeError):
    """Input, safety, remote-state, or validation failure."""


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


@dataclass(frozen=True)
class LocalInputs:
    config: dict[str, Any]
    config_path: Path
    archive: Path
    sidecar: Path
    notice: Path
    package_acceptance: Path
    output_dir: Path
    package_acceptance_sha256: str
    expected_assets: dict[str, dict[str, Any]]
    version: str
    tag: str
    repo: str
    source_head: str


def _fail(message: str) -> ReleaseToolError:
    return ReleaseToolError(message)


def _sha256(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
                size += len(chunk)
    except OSError as exc:
        raise _fail(f"cannot read input file {path}: {exc}") from exc
    return digest.hexdigest(), size


def _regular_file(path: Path, label: str) -> None:
    if path.is_symlink():
        raise _fail(f"{label} must not be a symlink: {path}")
    try:
        mode = path.stat(follow_symlinks=False).st_mode
    except OSError as exc:
        raise _fail(f"cannot inspect {label}: {path}: {exc}") from exc
    if not path.is_file() or not mode:
        raise _fail(f"{label} is not a regular file: {path}")


def _resolve_repo_path(value: Any, label: str, *, must_exist: bool) -> Path:
    if not isinstance(value, str) or not value:
        raise _fail(f"{label} must be a path string")
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    try:
        resolved = candidate.resolve(strict=must_exist)
        resolved.relative_to(ROOT)
        lexical = candidate.absolute().relative_to(ROOT)
    except (OSError, ValueError) as exc:
        raise _fail(f"{label} must resolve inside the repository: {value}") from exc
    current = ROOT
    for part in lexical.parts:
        current /= part
        if current.exists() and current.is_symlink():
            raise _fail(f"{label} traverses a symlink: {current}")
    return resolved


def _read_json(path: Path, label: str) -> dict[str, Any]:
    _regular_file(path, label)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise _fail(f"{label} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise _fail(f"{label} must be a JSON object")
    return value


def _asset_record(path: Path) -> dict[str, Any]:
    digest, size = _sha256(path)
    return {"bytes": size, "sha256": digest}


def load_inputs(config_path: Path) -> LocalInputs:
    config_path = _resolve_repo_path(str(config_path), "config", must_exist=True)
    config = _read_json(config_path, "config")
    if config.get("schema") != CONFIG_SCHEMA:
        raise _fail(f"config schema must be {CONFIG_SCHEMA}")
    required = (
        "version", "repo", "tag", "source_head", "archive", "sidecar",
        "notice", "package_acceptance_receipt", "output_dir",
    )
    missing = [key for key in required if key not in config]
    if missing:
        raise _fail(f"config is missing required fields: {', '.join(missing)}")

    version = config["version"]
    repo = config["repo"]
    tag = config["tag"]
    source_head = config["source_head"]
    if not isinstance(version, str) or not VERSION_RE.fullmatch(version) or str(int(version[1:])) != version[1:]:
        raise _fail("version must be canonical vNN notation")
    if not isinstance(repo, str) or not REPO_RE.fullmatch(repo):
        raise _fail("repo must be a GitHub owner/name slug")
    if (not isinstance(tag, str) or not TAG_RE.fullmatch(tag) or ".." in tag
            or "//" in tag or tag.endswith(("/", ".")) or not tag.endswith("-" + version)):
        raise _fail("tag must be safe and end with the configured version")
    if not isinstance(source_head, str) or not GIT_SHA_RE.fullmatch(source_head):
        raise _fail("source_head must be a lowercase Git commit SHA")

    archive = _resolve_repo_path(config["archive"], "archive", must_exist=True)
    sidecar = _resolve_repo_path(config["sidecar"], "SHA-256 sidecar", must_exist=True)
    notice = _resolve_repo_path(config["notice"], "NOTICE", must_exist=True)
    package_acceptance = _resolve_repo_path(config["package_acceptance_receipt"], "package acceptance receipt", must_exist=True)
    output_dir = _resolve_repo_path(config["output_dir"], "output_dir", must_exist=False)
    for path, label in ((archive, "archive"), (sidecar, "SHA-256 sidecar"),
                        (notice, "NOTICE"), (package_acceptance, "package acceptance receipt")):
        _regular_file(path, label)
    if notice.name != "NOTICE.md":
        raise _fail("NOTICE asset must be named NOTICE.md")
    if sidecar.name != archive.name + ".sha256":
        raise _fail("SHA-256 sidecar basename must be <archive>.sha256")
    if not output_dir.parent.is_dir():
        raise _fail("output_dir parent must already exist")
    for path in (archive, sidecar, notice, package_acceptance):
        if output_dir == path or output_dir in path.parents:
            raise _fail("output_dir must not contain an input asset or acceptance receipt")

    archive_sha, archive_bytes = _sha256(archive)
    sidecar_sha, sidecar_bytes = _sha256(sidecar)
    notice_asset = _asset_record(notice)
    try:
        sidecar_content = sidecar.read_text(encoding="ascii")
    except (OSError, UnicodeError) as exc:
        raise _fail(f"SHA-256 sidecar is not ASCII: {exc}") from exc
    if sidecar_content != f"{archive_sha}  {archive.name}\n":
        raise _fail("SHA-256 sidecar does not match archive bytes/name")

    acceptance = _read_json(package_acceptance, "package acceptance receipt")
    if (acceptance.get("schema") != PACKAGE_ACCEPTANCE_SCHEMA or acceptance.get("status") != "accepted"
            or acceptance.get("network_performed") is not False or acceptance.get("version") != version):
        raise _fail("package acceptance receipt schema/status/version is not accepted for this release")
    archive_acceptance = acceptance.get("archive")
    if not isinstance(archive_acceptance, dict):
        raise _fail("package acceptance receipt archive object is missing")
    if any(archive_acceptance.get(key) is not True for key in
           ("whitelist_exact", "checksums_exact", "crc_sha_length_all_passed")):
        raise _fail("package acceptance receipt does not attest exact whitelist/checksums and all member checks")
    for key in ("member_inventory_sha256", "archive_metadata_sha256", "checksum_file_sha256"):
        if not isinstance(archive_acceptance.get(key), str) or not SHA256_RE.fullmatch(archive_acceptance[key]):
            raise _fail(f"package acceptance receipt has no valid {key}")
    archive_relative = archive.relative_to(ROOT).as_posix()
    if (archive_acceptance.get("path") != archive_relative
            or archive_acceptance.get("sha256") != archive_sha
            or archive_acceptance.get("bytes") != archive_bytes
            or archive_acceptance.get("sidecar_sha256") != sidecar_sha
            or archive_acceptance.get("sidecar_bytes") != sidecar_bytes):
        raise _fail("package acceptance receipt does not bind the configured archive and sidecar")

    expected_assets = {
        archive.name: {"path": archive, **_asset_record(archive)},
        sidecar.name: {"path": sidecar, **_asset_record(sidecar)},
        notice.name: {"path": notice, **notice_asset},
    }
    if len(expected_assets) != 3:
        raise _fail("archive, sidecar, and NOTICE asset names must be unique")
    return LocalInputs(
        config, config_path, archive, sidecar, notice, package_acceptance, output_dir,
        _sha256(package_acceptance)[0], expected_assets, version, tag, repo, source_head,
    )


def _default_runner(args: Sequence[str], env: Mapping[str, str], timeout: float) -> CommandResult:
    try:
        completed = subprocess.run(
            list(args), cwd=ROOT, env=dict(env), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return CommandResult(124, stdout, stderr + "\nprocess timeout")
    except OSError as exc:
        return CommandResult(127, "", f"process start failed: {exc}")
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


def _is_not_found(result: CommandResult) -> bool:
    text = (result.stdout + "\n" + result.stderr).casefold()
    return "http 404" in text or "not found" in text


def _is_transport_failure(result: CommandResult) -> bool:
    text = (result.stdout + "\n" + result.stderr).casefold()
    markers = (
        "process timeout", "timed out", "timeout", "connection reset", "connection refused",
        "connection aborted", "connection timed out", "failed to connect", "could not resolve",
        "no such host", "network is unreachable", "dial tcp", "unexpected eof", "unexpected end of",
        "context deadline exceeded", "tls handshake timeout", "socket hang up", "temporary failure",
    )
    return any(marker in text for marker in markers) and not re.search(r"http\s+[1-5][0-9]{2}", text)


def _child_env(*, use_proxy: bool) -> dict[str, str]:
    env = os.environ.copy()
    proxy_names = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy")
    for name in proxy_names:
        env.pop(name, None)
    # Keep certificate verification enabled in the GitHub CLI child process.
    env.pop("GH_INSECURE", None)
    env.pop("GIT_SSL_NO_VERIFY", None)
    # The repository guard below targets github.com; do not let an ambient
    # enterprise-host override silently redirect the explicit GitHub CLI calls.
    env.pop("GH_HOST", None)
    if use_proxy:
        for name in ("HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy"):
            env[name] = GH_PROXY_URL
        env["NO_PROXY"] = "localhost,127.0.0.1"
        env["no_proxy"] = "localhost,127.0.0.1"
    return env


def _json_object(text: str, label: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise _fail(f"{label} returned invalid JSON") from exc
    if not isinstance(value, dict):
        raise _fail(f"{label} did not return a JSON object")
    return value


def _write_json_new(path: Path, value: Mapping[str, Any]) -> None:
    payload = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        with path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise _fail(f"refusing to overwrite existing file: {path}") from exc
    except OSError as exc:
        raise _fail(f"cannot write {path}: {exc}") from exc


class ReleaseCreator:
    def __init__(
        self,
        inputs: LocalInputs,
        *,
        runner: Callable[[Sequence[str], Mapping[str, str], int], CommandResult] = _default_runner,
        monotonic: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
        utcnow: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ) -> None:
        self.inputs = inputs
        self.runner = runner
        self.monotonic = monotonic
        self.sleeper = sleeper
        self.utcnow = utcnow
        self.last_network_start: float | None = None
        self.proxy_attempts = 0
        self.create_attempts = 0
        self.upload_attempts = 0
        self.recovered_ambiguous_write = False
        self.process_events: list[dict[str, Any]] = []

    def _local_command(self, args: Sequence[str]) -> str:
        # Keep the full untracked-file guard for the large archive checkout.
        timeout = 120 if list(args[:2]) == ["git", "status"] else 30
        result = self.runner(args, os.environ.copy(), timeout)
        if result.returncode != 0:
            raise _fail(f"local command failed ({args[0]}, exit {result.returncode})")
        return result.stdout.strip()

    def _validate_git_state(self) -> None:
        branch = self._local_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        head = self._local_command(["git", "rev-parse", "HEAD"])
        origin_main = self._local_command(["git", "rev-parse", "origin/main"])
        status = self._local_command(["git", "status", "--porcelain=v1", "--untracked-files=all"])
        origin = self._local_command(["git", "remote", "get-url", "origin"])
        if branch != "main" or head != self.inputs.source_head or origin_main != self.inputs.source_head:
            raise _fail("source_head guard failed: require clean main == origin/main == configured source_head")
        if status:
            raise _fail("source checkout is not clean")
        normalized = origin.removesuffix(".git")
        if normalized.startswith("git@github.com:"):
            normalized = normalized.removeprefix("git@github.com:")
        elif normalized.startswith("https://github.com/"):
            normalized = normalized.removeprefix("https://github.com/")
        elif normalized.startswith("ssh://git@github.com/"):
            normalized = normalized.removeprefix("ssh://git@github.com/")
        if normalized.casefold() != self.inputs.repo.casefold():
            raise _fail("origin remote does not match configured GitHub repo")

    def _wait_for_network_slot(self) -> float:
        now = self.monotonic()
        if self.last_network_start is not None:
            for _ in range(5):
                delay = MIN_PROCESS_START_INTERVAL - (now - self.last_network_start)
                if delay <= 1e-9:
                    break
                # Windows clocks can observe a slightly early sleep return.
                # Recheck without starting any request; retain the hard gap.
                self.sleeper(delay + 0.01)
                now = self.monotonic()
            if now - self.last_network_start + 1e-9 < MIN_PROCESS_START_INTERVAL:
                raise _fail("network process start spacing could not be satisfied")
        remaining = (DEADLINE_UTC - self.utcnow()).total_seconds()
        if remaining <= 1.0:
            raise _fail("release operation cutoff is too near; refusing to start another gh process")
        self.last_network_start = now
        # Leave a one-second margin for process launch/termination overhead so
        # an upload started shortly before the cutoff cannot run past it.
        return remaining - 1.0

    def _gh_once(self, args: Sequence[str], *, proxy: bool, timeout: int) -> CommandResult:
        remaining_runtime = self._wait_for_network_slot()
        if proxy:
            self.proxy_attempts += 1
        started_utc = self.utcnow().isoformat().replace("+00:00", "Z")
        effective_timeout = min(float(timeout), remaining_runtime)
        result = self.runner(["gh", *args], _child_env(use_proxy=proxy), effective_timeout)
        if args[:1] == ["api"]:
            operation = "api_read"
        elif args[:2] == ["release", "create"]:
            operation = "release_create"
        elif args[:2] == ["release", "upload"]:
            operation = "release_upload"
        else:
            operation = "other"
        self.process_events.append({
            "gh_invocation_started_utc": started_utc,
            "operation": operation,
            "process_proxy": proxy,
            "timeout_seconds": round(effective_timeout, 3),
            "returncode": result.returncode,
        })
        return result

    def _gh_read(self, args: Sequence[str], *, timeout: int = GH_READ_TIMEOUT,
                 allow_not_found: bool = False) -> dict[str, Any] | None:
        result = self._gh_once(args, proxy=False, timeout=timeout)
        if result.returncode == 0:
            return _json_object(result.stdout, "gh api")
        if allow_not_found and _is_not_found(result) and not _is_transport_failure(result):
            return None
        if not _is_transport_failure(result):
            raise _fail(f"gh read failed without a transport error (exit {result.returncode})")
        proxy_result = self._gh_once(args, proxy=True, timeout=timeout)
        if proxy_result.returncode == 0:
            return _json_object(proxy_result.stdout, "gh api via process proxy")
        if allow_not_found and _is_not_found(proxy_result) and not _is_transport_failure(proxy_result):
            return None
        raise _fail(f"gh read failed on direct and proxy paths (exit {proxy_result.returncode})")

    def _release_endpoint(self) -> str:
        return f"repos/{self.inputs.repo}/releases/tags/{quote(self.inputs.tag, safe='')}"

    def _tag_endpoint(self) -> str:
        return f"repos/{self.inputs.repo}/git/ref/tags/{quote(self.inputs.tag, safe='')}"

    def _remote_release(self) -> dict[str, Any] | None:
        return self._gh_read(["api", self._release_endpoint()], allow_not_found=True)

    def _remote_tag_exists(self) -> bool:
        return self._gh_read(["api", self._tag_endpoint()], allow_not_found=True) is not None

    def _expected_assets_json(self) -> dict[str, dict[str, Any]]:
        return {
            name: {"bytes": item["bytes"], "sha256": item["sha256"]}
            for name, item in sorted(self.inputs.expected_assets.items())
        }

    def _intent_path(self) -> Path:
        return self.inputs.output_dir / INTENT_NAME

    def _receipt_path(self) -> Path:
        return self.inputs.output_dir / RECEIPT_NAME

    def _prepare_output(self) -> dict[str, Any] | None:
        output = self.inputs.output_dir
        allowed = {INTENT_NAME, RECEIPT_NAME}
        if output.exists():
            if output.is_symlink() or not output.is_dir():
                raise _fail("output_dir exists but is not a normal directory")
            entries = list(output.iterdir())
            unknown = [item.name for item in entries if item.name not in allowed]
            if unknown:
                raise _fail(f"output_dir contains unowned files: {unknown[:5]}")
            for item in entries:
                if item.is_symlink() or not item.is_file():
                    raise _fail(f"output_dir contains a non-regular item: {item.name}")
        else:
            if not output.parent.is_dir():
                raise _fail("output_dir parent disappeared")
            output.mkdir()

        intent_path, receipt_path = self._intent_path(), self._receipt_path()
        if receipt_path.exists() and not intent_path.exists():
            raise _fail("upload receipt exists without its matching draft intent")
        intent = None
        if intent_path.exists():
            intent = _read_json(intent_path, "draft intent")
            expected_binding = {
                "schema": INTENT_SCHEMA,
                "version": self.inputs.version,
                "repo": self.inputs.repo,
                "tag": self.inputs.tag,
                "target_commit": self.inputs.source_head,
                "package_acceptance_sha256": self.inputs.package_acceptance_sha256,
                "expected_assets": self._expected_assets_json(),
            }
            for key, value in expected_binding.items():
                if intent.get(key) != value:
                    raise _fail(f"saved draft intent does not match current input: {key}")
            if not isinstance(intent.get("nonce"), str) or not re.fullmatch(r"[0-9a-f]{32}", intent["nonce"]):
                raise _fail("saved draft intent nonce is invalid")
        return intent

    def _create_intent(self) -> dict[str, Any]:
        nonce = uuid.uuid4().hex
        marker = f"<!-- wow-encyclopedia-managed-draft:{nonce} -->"
        intent = {
            "schema": INTENT_SCHEMA,
            "created_utc": self.utcnow().isoformat().replace("+00:00", "Z"),
            "version": self.inputs.version,
            "repo": self.inputs.repo,
            "tag": self.inputs.tag,
            "target_commit": self.inputs.source_head,
            "package_acceptance_sha256": self.inputs.package_acceptance_sha256,
            "expected_assets": self._expected_assets_json(),
            "nonce": nonce,
            "release_body_marker": marker,
        }
        _write_json_new(self._intent_path(), intent)
        return intent

    def _verify_release(self, data: Mapping[str, Any], intent: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
        if data.get("tag_name") != self.inputs.tag or data.get("target_commitish") != self.inputs.source_head:
            raise _fail("remote release tag or target commit differs from configured source")
        if data.get("draft") is not True:
            raise _fail("remote release is not a draft; publishing is a separate operation")
        if intent.get("release_body_marker") not in str(data.get("body") or ""):
            raise _fail("remote draft lacks the saved ownership marker; refusing to adopt it")
        if not isinstance(data.get("id"), int):
            raise _fail("remote draft has no numeric release id")
        assets = data.get("assets")
        if not isinstance(assets, list):
            raise _fail("remote draft assets must be a list")
        expected = self._expected_assets_json()
        observed: dict[str, dict[str, Any]] = {}
        for asset in assets:
            if not isinstance(asset, dict) or not isinstance(asset.get("name"), str):
                raise _fail("remote draft contains a malformed asset")
            name = asset["name"]
            if name in observed or name not in expected:
                raise _fail(f"remote draft has a duplicate or unrelated asset: {name}")
            if (asset.get("state") != "uploaded" or asset.get("size") != expected[name]["bytes"]
                    or asset.get("digest") != "sha256:" + expected[name]["sha256"]):
                raise _fail(f"remote asset does not match local bytes/state: {name}")
            observed[name] = {"state": asset["state"], "size": asset["size"], "digest": asset["digest"]}
        return observed

    def _body(self, intent: Mapping[str, Any]) -> str:
        return (
            f"Portable browse-only archive {self.inputs.version}. The release assets are the archive, its SHA-256 sidecar, and NOTICE.\n\n"
            f"Package acceptance SHA-256: {self.inputs.package_acceptance_sha256}\n\n"
            f"{intent['release_body_marker']}"
        )

    def _create_draft(self, intent: Mapping[str, Any]) -> dict[str, Any]:
        title = f"World of Warcraft Encyclopedia browser archive {self.inputs.version}"
        args = [
            "release", "create", self.inputs.tag, "--repo", self.inputs.repo,
            "--target", self.inputs.source_head, "--draft", "--title", title,
            "--notes", self._body(intent),
        ]
        result = self._gh_once(args, proxy=False, timeout=GH_CREATE_TIMEOUT)
        self.create_attempts += 1
        state = self._remote_release()
        if state is not None:
            self.recovered_ambiguous_write = result.returncode != 0
            self._verify_release(state, intent)
            return state
        if result.returncode == 0:
            raise _fail("gh create succeeded but the owned draft was not visible on readback")
        tag_exists = self._remote_tag_exists()
        if tag_exists or not _is_transport_failure(result):
            raise _fail(f"draft creation failed and readback found no recoverable owned draft (exit {result.returncode})")

        # The direct create result was ambiguous. Retry only after both the
        # release and tag readbacks proved that no server-side creation landed.
        proxy_result = self._gh_once(args, proxy=True, timeout=GH_CREATE_TIMEOUT)
        self.create_attempts += 1
        state = self._remote_release()
        if state is None:
            raise _fail(f"proxy create result remains ambiguous; no release is visible (exit {proxy_result.returncode})")
        self.recovered_ambiguous_write = proxy_result.returncode != 0
        self._verify_release(state, intent)
        return state

    def _upload_one(self, release: Mapping[str, Any], intent: Mapping[str, Any], name: str) -> dict[str, Any]:
        observed = self._verify_release(release, intent)
        if name in observed:
            return observed[name]
        path = self.inputs.expected_assets[name]["path"]
        args = ["release", "upload", self.inputs.tag, str(path), "--repo", self.inputs.repo]
        result = self._gh_once(args, proxy=False, timeout=GH_UPLOAD_TIMEOUT)
        self.upload_attempts += 1
        state = self._remote_release()
        if state is not None:
            after = self._verify_release(state, intent)
            if name in after:
                self.recovered_ambiguous_write = self.recovered_ambiguous_write or result.returncode != 0
                return after[name]
        if result.returncode == 0:
            raise _fail(f"asset upload reported success but asset was not present on readback: {name}")
        if not _is_transport_failure(result):
            raise _fail(f"asset upload failed without a transport error: {name} (exit {result.returncode})")
        if state is None:
            raise _fail(f"asset upload result is ambiguous and release readback failed: {name}")

        # Readback succeeded and proved this exact asset is absent; only then
        # is a single process-proxy retry safe.
        proxy_result = self._gh_once(args, proxy=True, timeout=GH_UPLOAD_TIMEOUT)
        self.upload_attempts += 1
        state = self._remote_release()
        if state is None:
            raise _fail(f"proxy asset upload result remains ambiguous: {name} (exit {proxy_result.returncode})")
        after = self._verify_release(state, intent)
        if name not in after:
            raise _fail(f"asset is still absent after the one proxy retry: {name}")
        self.recovered_ambiguous_write = self.recovered_ambiguous_write or proxy_result.returncode != 0
        return after[name]

    def _make_receipt(self, release: Mapping[str, Any], intent: Mapping[str, Any]) -> dict[str, Any]:
        assets = self._verify_release(release, intent)
        expected = self._expected_assets_json()
        if set(assets) != set(expected):
            raise _fail("remote draft does not contain exactly the three expected assets")
        return {
            "schema": RECEIPT_SCHEMA,
            "accepted": True,
            "created_utc": self.utcnow().isoformat().replace("+00:00", "Z"),
            "version": self.inputs.version,
            "repo": self.inputs.repo,
            "tag": self.inputs.tag,
            "release_id": release["id"],
            "target_commit": self.inputs.source_head,
            "draft": True,
            "published": False,
            "package_acceptance_sha256": self.inputs.package_acceptance_sha256,
            "expected_assets": expected,
            "remote_assets": {name: assets[name] for name in sorted(assets)},
            "network_spacing_scope": "gh CLI process starts separated by at least 5.2 seconds; internal gh REST subrequests are not individually scheduled",
            "direct_first": True,
            "process_proxy_fallback": "http://127.0.0.1:7890 after classified transport failure only",
            "tls_verification": "enabled; no insecure flags or certificate overrides",
            "create_attempts": self.create_attempts,
            "upload_attempts": self.upload_attempts,
            "proxy_process_attempts": self.proxy_attempts,
            "ambiguous_write_recovered_by_readback": self.recovered_ambiguous_write,
            "operation_cutoff_utc": DEADLINE_UTC.isoformat().replace("+00:00", "Z"),
            "subprocess_timeout_capped_before_cutoff": True,
            "gh_process_events": list(self.process_events),
            "published_by_helper": False,
        }

    def create_upload(self) -> dict[str, Any]:
        if self.utcnow() >= DEADLINE_UTC:
            raise _fail("release operation cutoff 2026-10-22T14:51:33Z has passed")
        self._validate_git_state()
        intent = self._prepare_output()
        receipt_path = self._receipt_path()
        if receipt_path.exists():
            receipt = _read_json(receipt_path, "upload receipt")
            if (receipt.get("schema") != RECEIPT_SCHEMA or receipt.get("accepted") is not True
                    or receipt.get("repo") != self.inputs.repo or receipt.get("tag") != self.inputs.tag
                    or receipt.get("target_commit") != self.inputs.source_head
                    or receipt.get("package_acceptance_sha256") != self.inputs.package_acceptance_sha256
                    or receipt.get("expected_assets") != self._expected_assets_json()):
                raise _fail("saved upload receipt does not match current inputs")
            state = self._remote_release()
            if state is None or state.get("id") != receipt.get("release_id"):
                raise _fail("saved upload receipt no longer matches a visible remote draft")
            assets = self._verify_release(state, intent or {})
            if set(assets) != set(self.inputs.expected_assets):
                raise _fail("saved upload receipt's remote draft no longer has all expected assets")
            if (receipt.get("draft") is not True or receipt.get("published") is not False
                    or receipt.get("remote_assets") != {name: assets[name] for name in sorted(assets)}):
                raise _fail("saved upload receipt does not match the current owned draft asset state")
            return receipt

        release = self._remote_release()
        if release is not None:
            if intent is None:
                raise _fail("a release with this tag already exists and is not owned by this output directory")
            self._verify_release(release, intent)
        else:
            if self._remote_tag_exists():
                raise _fail("a remote tag with this name already exists; refusing to create or move it")
            if intent is None:
                intent = self._create_intent()
            release = self._create_draft(intent)

        assert intent is not None
        for name in sorted(self.inputs.expected_assets):
            release = self._remote_release() or release
            self._upload_one(release, intent, name)
            release = self._remote_release()
            if release is None:
                raise _fail("draft disappeared after asset upload")
            self._verify_release(release, intent)

        receipt = self._make_receipt(release, intent)
        _write_json_new(receipt_path, receipt)
        return receipt


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path, help="root-supplied release config JSON")
    parser.add_argument("--execute", action="store_true", required=True,
                        help="required: create/recover one draft and upload assets; never publishes")
    args = parser.parse_args(argv)
    try:
        inputs = load_inputs(args.config)
        receipt = ReleaseCreator(inputs).create_upload()
    except (ReleaseToolError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"create_upload_release: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({
        "accepted": receipt["accepted"],
        "version": receipt["version"],
        "repo": receipt["repo"],
        "tag": receipt["tag"],
        "release_id": receipt["release_id"],
        "draft": receipt["draft"],
        "published": receipt["published"],
        "assets": sorted(receipt["remote_assets"]),
        "receipt": str((inputs.output_dir / RECEIPT_NAME).relative_to(ROOT).as_posix()),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
