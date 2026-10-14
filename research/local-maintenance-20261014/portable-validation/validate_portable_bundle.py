#!/usr/bin/env python3
"""Run one bounded, independent QA pass over the portable browser bundle.

The runner is intentionally separate from the package producer.  It verifies
the producer receipt and ZIP safety, extracts into the one owned v5 scratch
directory, starts the packaged preview server with ``python -I``, runs a
loopback-only urllib smoke, and invokes the small Playwright companion.  It
does not access the network and does not use the source tree as the server
root.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import time
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
import zipfile


REPO_ROOT = Path(__file__).resolve().parents[3]
EXPECTED_SCRATCH = (REPO_ROOT / ".scratch" / "local bundle smoke 20261014 v5").resolve()
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "v5" / "portable-bundle-validation-v5.json"
DEFAULT_PYTHON = Path(
    r"C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
)
DEFAULT_NODE = Path(r"C:\nvm4w\nodejs\node.exe")
DEFAULT_CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
DEFAULT_PLAYWRIGHT = Path(
    r"C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\playwright"
)
MIN_FREE_BYTES = 10 * 1024**3 + 256 * 1024**2
SERVER_START_TIMEOUT = 20.0
BROWSER_TIMEOUT = 300.0
SHA256_RE = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)
SERVER_URL_RE = re.compile(r"^Archive preview: (http://127\.0\.0\.1:\d+/\S*)$")


class QAError(RuntimeError):
    """A bounded QA precondition or independent check failed."""


@dataclass
class HTTPResult:
    method: str
    path: str
    status: int
    headers: dict[str, str]
    body: bytes
    error: str | None = None

    def compact(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "method": self.method,
            "path": self.path,
            "status": self.status,
            "bytes": len(self.body),
            "content_type": self.headers.get("Content-Type"),
            "content_length": self.headers.get("Content-Length"),
        }
        if self.error:
            result["error"] = self.error
        return result


class NoRedirect(HTTPRedirectHandler):
    """Keep 3xx responses observable for route compatibility checks."""

    def redirect_request(self, *_args: Any, **_kwargs: Any) -> None:
        return None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise QAError(f"cannot read JSON: {path}: {exc}") from exc


def require_regular_file(path: Path, label: str) -> Path:
    if not path.exists() or path.is_symlink() or not path.is_file():
        raise QAError(f"{label} is not a regular file: {path}")
    return path.resolve()


def require_directory(path: Path, label: str) -> Path:
    if not path.exists() or path.is_symlink() or not path.is_dir():
        raise QAError(f"{label} is not a normal directory: {path}")
    return path.resolve()


def reparse_or_link(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        details = path.stat(follow_symlinks=False)
    except OSError:
        return True
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(getattr(details, "st_file_attributes", 0) & reparse_flag)


def safe_zip_name(name: str) -> str:
    if not isinstance(name, str) or not name or "\x00" in name:
        raise QAError(f"unsafe ZIP member name: {name!r}")
    if "\\" in name or name.startswith("/") or re.match(r"^[A-Za-z]:", name):
        raise QAError(f"unsafe ZIP member name: {name!r}")
    parts = name.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise QAError(f"unsafe ZIP member name: {name!r}")
    # PurePosixPath catches unusual rooted spellings while keeping the ZIP
    # spelling visible in the report.
    if PurePosixPath(name).is_absolute():
        raise QAError(f"unsafe ZIP member name: {name!r}")
    return name


def zip_member_mode(info: zipfile.ZipInfo) -> int:
    return (info.external_attr >> 16) & 0xFFFF


def inspect_zip(archive: Path) -> dict[str, Any]:
    required = {
        "site/export-provenance.json",
        "site/__offline/route-map.json",
        "tools/serve_pages_preview.py",
        "NOTICE.md",
        "README.md",
        "START_BROWSE.cmd",
        "archive-metadata.json",
        "FILE_SHA256SUMS.txt",
    }
    try:
        with zipfile.ZipFile(archive, "r") as zf:
            infos = zf.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                raise QAError("ZIP contains duplicate member names")
            observed: list[dict[str, Any]] = []
            total_uncompressed = 0
            total_compressed = 0
            for info in infos:
                safe_zip_name(info.filename)
                mode = zip_member_mode(info)
                if info.is_dir() or stat.S_ISDIR(mode):
                    raise QAError(f"ZIP directory member is not allowed: {info.filename}")
                if stat.S_ISLNK(mode):
                    raise QAError(f"ZIP symlink member is not allowed: {info.filename}")
                total_uncompressed += info.file_size
                total_compressed += info.compress_size
                observed.append(
                    {
                        "path": info.filename,
                        "bytes": info.file_size,
                        "compressed_bytes": info.compress_size,
                        "crc32": f"{info.CRC:08x}",
                    }
                )
            bad = zf.testzip()
            if bad is not None:
                raise QAError(f"ZIP CRC check failed: {bad}")
    except (OSError, zipfile.BadZipFile) as exc:
        raise QAError(f"cannot inspect ZIP: {archive}: {exc}") from exc

    missing = sorted(required - set(names))
    if missing:
        raise QAError(f"ZIP is missing required members: {missing}")
    return {
        "member_count": len(names),
        "required_members_present": True,
        "member_names_safe": True,
        "symlink_members": 0,
        "crc_check": True,
        "uncompressed_bytes": total_uncompressed,
        "compressed_bytes": total_compressed,
        "sample_members": sorted(observed, key=lambda item: item["path"])[:5],
    }


def extract_zip(archive: Path, target: Path) -> dict[str, Any]:
    if target.exists() or os.path.lexists(target):
        raise QAError(f"refusing to use existing extraction directory: {target}")
    if target.resolve() != EXPECTED_SCRATCH:
        raise QAError(f"scratch directory is not the owned target: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir()
    expected_files: set[str] = set()
    try:
        with zipfile.ZipFile(archive, "r") as zf:
            for info in zf.infolist():
                name = safe_zip_name(info.filename)
                mode = zip_member_mode(info)
                if info.is_dir() or stat.S_ISDIR(mode) or stat.S_ISLNK(mode):
                    raise QAError(f"non-regular ZIP member during extraction: {name}")
                expected_files.add(name)
                destination = target.joinpath(*name.split("/"))
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists() or os.path.lexists(destination):
                    raise QAError(f"duplicate extraction target: {destination}")
                with zf.open(info, "r") as source, destination.open("xb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
    except Exception:
        # The caller deliberately keeps this new directory after any failed
        # run for evidence; never remove it here.
        raise

    actual_files: set[str] = set()
    for directory, dirnames, filenames in os.walk(target, topdown=True, followlinks=False):
        directory_path = Path(directory)
        for dirname in list(dirnames):
            path = directory_path / dirname
            if reparse_or_link(path):
                raise QAError(f"extracted directory is a link or reparse point: {path}")
        for filename in filenames:
            path = directory_path / filename
            if reparse_or_link(path):
                raise QAError(f"extracted file is a link or reparse point: {path}")
            if not path.is_file():
                raise QAError(f"extracted member is not a regular file: {path}")
            actual_files.add(path.relative_to(target).as_posix())
    if actual_files != expected_files:
        raise QAError(
            "extracted member set differs from ZIP: "
            f"missing={sorted(expected_files - actual_files)[:5]}, "
            f"extra={sorted(actual_files - expected_files)[:5]}"
        )
    return {
        "resolved_root": str(target.resolve()),
        "member_count": len(actual_files),
        "member_set_exact": True,
        "regular_files_only": True,
    }


def parse_sidecar(path: Path, archive: Path) -> dict[str, Any]:
    text = path.read_text(encoding="ascii").strip()
    parts = text.split()
    if len(parts) != 2 or not SHA256_RE.fullmatch(parts[0]):
        raise QAError(f"invalid SHA-256 sidecar: {path}")
    expected_name = parts[1].lstrip("*")
    if expected_name != archive.name:
        raise QAError(f"sidecar names {expected_name!r}, expected {archive.name!r}")
    return {"path": str(path.resolve()), "sha256": parts[0].lower(), "archive_name": expected_name}


def verify_receipt(archive: Path, report_path: Path, sidecar_path: Path) -> dict[str, Any]:
    report = json_load(report_path)
    if not isinstance(report, dict):
        raise QAError("generation report must be a JSON object")
    actual_sha = sha256_file(archive)
    actual_bytes = archive.stat().st_size
    sidecar = parse_sidecar(sidecar_path, archive)
    verification = report.get("verification")
    if not isinstance(verification, dict):
        raise QAError("generation report has no verification object")
    report_sha = str(verification.get("archive_sha256", "")).lower()
    report_bytes = verification.get("archive_bytes")
    if report_sha != actual_sha or report_bytes != actual_bytes:
        raise QAError(
            "generation report does not match ZIP: "
            f"report_sha={report_sha}, actual_sha={actual_sha}, "
            f"report_bytes={report_bytes}, actual_bytes={actual_bytes}"
        )
    if sidecar["sha256"] != actual_sha:
        raise QAError("SHA-256 sidecar does not match ZIP")
    if report.get("archive") not in {archive.name, str(archive), archive.as_posix()}:
        raise QAError(f"generation report archive field is unexpected: {report.get('archive')!r}")
    return {
        "archive": str(archive.resolve()),
        "archive_bytes": actual_bytes,
        "archive_sha256": actual_sha,
        "sidecar": sidecar,
        "generation_report": str(report_path.resolve()),
        "generation_report_schema": report.get("schema"),
        "generation_report_verified": True,
        "network_performed": report.get("network_performed"),
    }


def validate_metadata(extracted: Path, zip_summary: dict[str, Any]) -> dict[str, Any]:
    site = require_directory(extracted / "site", "packaged site")
    provenance = json_load(require_regular_file(site / "export-provenance.json", "site provenance"))
    if not isinstance(provenance, dict):
        raise QAError("site/export-provenance.json is not an object")
    prefix = provenance.get("base_path")
    if not isinstance(prefix, str) or not prefix.startswith("/") or not prefix.endswith("/"):
        raise QAError("site provenance has an invalid base_path")
    route_map = json_load(require_regular_file(site / "__offline" / "route-map.json", "route map"))
    if not isinstance(route_map, dict):
        raise QAError("site route map is not an object")
    metadata = json_load(require_regular_file(extracted / "archive-metadata.json", "archive metadata"))
    if not isinstance(metadata, dict):
        raise QAError("archive-metadata.json is not an object")
    if metadata.get("project_prefix") != prefix:
        raise QAError("archive metadata and site provenance prefixes differ")
    if metadata.get("member_count") != zip_summary["member_count"]:
        raise QAError("archive metadata member count differs from ZIP")
    return {
        "site": str(site),
        "project_prefix": prefix,
        "route_map_loaded": True,
        "archive_metadata_member_count": metadata.get("member_count"),
        "archive_metadata_network_performed": metadata.get("network_performed"),
        "archive_metadata_matches_zip": True,
    }


def disk_preflight(archive: Path, scratch: Path, uncompressed_bytes: int) -> dict[str, Any]:
    try:
        usage = shutil.disk_usage(scratch.parent)
    except OSError as exc:
        raise QAError(f"cannot inspect D: free space: {exc}") from exc
    required = MIN_FREE_BYTES + uncompressed_bytes
    result = {
        "drive": "D:",
        "free_bytes_before": usage.free,
        "uncompressed_bytes_to_extract": uncompressed_bytes,
        "minimum_free_reserve_bytes": MIN_FREE_BYTES,
        "required_before_extraction_bytes": required,
        "preflight_passed": usage.free >= required,
    }
    if not result["preflight_passed"]:
        raise QAError(f"D: free-space preflight failed: {json.dumps(result, sort_keys=True)}")
    return result


def start_server(extracted: Path, python_exe: Path) -> tuple[subprocess.Popen[bytes], str, dict[str, Any], Any, Any]:
    command = [
        str(python_exe),
        "-I",
        "tools/serve_pages_preview.py",
        "--site",
        "site",
        "--port",
        "0",
    ]
    stdout_path = extracted / "server.stdout.log"
    stderr_path = extracted / "server.stderr.log"
    stdout_handle = stdout_path.open("wb")
    stderr_handle = stderr_path.open("wb")
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    env["PYTHONNOUSERSITE"] = "1"
    process = subprocess.Popen(
        command,
        cwd=str(extracted),
        stdout=stdout_handle,
        stderr=stderr_handle,
        env=env,
    )
    deadline = time.monotonic() + SERVER_START_TIMEOUT
    url: str | None = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            break
        try:
            output = stdout_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            output = ""
        for line in output.splitlines():
            match = SERVER_URL_RE.match(line.strip())
            if match:
                url = match.group(1)
                break
        if url:
            break
        time.sleep(0.1)
    if url is None:
        stdout_handle.close()
        stderr_handle.close()
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
        stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
        raise QAError(f"packaged server did not start: stdout={stdout!r}, stderr={stderr!r}")
    parsed = urlsplit(url)
    if parsed.hostname != "127.0.0.1" or parsed.scheme != "http" or not parsed.path.endswith("/"):
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        stdout_handle.close()
        stderr_handle.close()
        raise QAError(f"server bound outside loopback or has invalid prefix: {url}")
    return (
        process,
        url,
        {
            "command": command,
            "cwd": str(extracted),
            "python_isolated": True,
            "openbrowser_argument_present": "--open-browser" in command,
            "url": url,
            "stdout_log": str(stdout_path),
            "stderr_log": str(stderr_path),
        },
        stdout_handle,
        stderr_handle,
    )


def stop_server(process: subprocess.Popen[bytes] | None, stdout_handle: Any, stderr_handle: Any) -> dict[str, Any]:
    if process is None:
        for handle in (stdout_handle, stderr_handle):
            if handle is not None:
                handle.close()
        return {"stopped": True, "returncode": None}
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
    for handle in (stdout_handle, stderr_handle):
        if handle is not None:
            handle.close()
    return {"stopped": process.poll() is not None, "returncode": process.returncode}


def compact_headers(headers: Any) -> dict[str, str]:
    names = {"Location", "Content-Type", "Content-Length", "X-Content-Type-Options", "Cache-Control"}
    return {name: headers.get(name) for name in names if headers.get(name) is not None}


def http_request(opener: Any, origin: str, path: str, method: str) -> HTTPResult:
    url = origin + path
    if urlsplit(url).hostname != "127.0.0.1":
        raise QAError(f"refusing non-loopback urllib URL: {url}")
    request = Request(url, method=method, headers={"Cache-Control": "no-store"})
    try:
        with opener.open(request, timeout=20) as response:
            body = response.read()
            return HTTPResult(method, path, response.status, compact_headers(response.headers), body)
    except HTTPError as exc:
        try:
            body = exc.read()
        except OSError:
            body = b""
        return HTTPResult(method, path, exc.code, compact_headers(exc.headers), body)
    except (OSError, URLError, ValueError) as exc:
        return HTTPResult(method, path, 0, {}, b"", f"{type(exc).__name__}: {exc}")


def check_http(result: HTTPResult, expected_status: int, label: str, passed: list[dict[str, Any]], failures: list[str], **extra: Any) -> None:
    record: dict[str, Any] = {"name": label, **result.compact(), **extra}
    record["passed"] = result.status == expected_status and result.error is None
    if not record["passed"]:
        failures.append(f"{label}: expected HTTP {expected_status}, got {result.compact()}")
    passed.append(record)


def choose_binary(site: Path) -> tuple[str, Path]:
    preferred = site / "info" / "races" / "images" / "dancing" / "banner" / "background.jpg"
    if preferred.is_file() and not reparse_or_link(preferred):
        return preferred.relative_to(site).as_posix(), preferred
    candidates = sorted(
        path
        for path in site.rglob("*")
        if path.is_file() and path.suffix.casefold() in {".png", ".jpg", ".jpeg", ".gif", ".swf"} and not reparse_or_link(path)
    )
    if not candidates:
        raise QAError("no representative binary file exists in packaged site")
    return candidates[0].relative_to(site).as_posix(), candidates[0]


def choose_index_directory(site: Path) -> str:
    for candidate in ("visa/reward", "info/races", "info/items"):
        if (site / candidate / "index.html").is_file():
            return candidate
    candidates = sorted(
        path.parent.relative_to(site).as_posix()
        for path in site.rglob("index.html")
        if path.is_file() and not reparse_or_link(path) and "__offline" not in path.parts
    )
    if not candidates:
        raise QAError("no packaged directory with index.html exists")
    return candidates[0]


def run_http_checks(server_url: str, site: Path, prefix: str) -> dict[str, Any]:
    parsed = urlsplit(server_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    opener = build_opener(ProxyHandler({}), NoRedirect())
    checks: list[dict[str, Any]] = []
    failures: list[str] = []
    query = "portable=1&requested=%3Csafe%3E"
    old_path = f"{prefix}info/encyclopedia/index.xml?{query}"
    canonical_path = f"{prefix}info/encyclopedia/index.xml.html?{query}"

    old_get = http_request(opener, origin, old_path, "GET")
    old_location = old_get.headers.get("Location")
    check_http(old_get, 302, "old XML GET redirects", checks, failures, location=old_location)
    if old_location:
        resolved = urlsplit(urljoin(origin + old_path, old_location))
        if resolved.path != f"{prefix}info/encyclopedia/index.xml.html" or resolved.query != query:
            failures.append(f"old XML redirect changed route or query: {old_location!r}")
    else:
        failures.append("old XML GET has no Location header")

    canonical_get = http_request(opener, origin, canonical_path, "GET")
    check_http(canonical_get, 200, "canonical XML-page GET", checks, failures, html_bytes=len(canonical_get.body))
    if b"<html" not in canonical_get.body[:4096].lower():
        failures.append("canonical XML-page response is not HTML")
    old_head = http_request(opener, origin, old_path, "HEAD")
    check_http(old_head, 302, "old XML HEAD redirects", checks, failures, location=old_head.headers.get("Location"))
    canonical_head = http_request(opener, origin, canonical_path, "HEAD")
    check_http(canonical_head, 200, "canonical XML-page HEAD", checks, failures, body_bytes=len(canonical_head.body))
    if canonical_head.body:
        failures.append("canonical HEAD returned a response body")

    directory = choose_index_directory(site)
    directory_path = f"{prefix}{directory}?portable-directory=1"
    directory_get = http_request(opener, origin, directory_path, "GET")
    directory_location = directory_get.headers.get("Location")
    check_http(directory_get, 302, "directory URL adds slash", checks, failures, location=directory_location, directory=directory)
    if directory_location:
        resolved = urlsplit(urljoin(origin + directory_path, directory_location))
        if resolved.path != f"{prefix}{directory}/" or resolved.query != "portable-directory=1":
            failures.append(f"directory redirect changed route or query: {directory_location!r}")
        directory_follow = http_request(opener, origin, f"{prefix}{directory}/?portable-directory=1", "GET")
        check_http(directory_follow, 200, "directory slash target", checks, failures, directory=directory)

    missing_path = f"{prefix}__portable-qa-missing__.html?source=portable&requested=%2Fmissing.png"
    missing = http_request(opener, origin, missing_path, "GET")
    check_http(missing, 404, "real missing route uses archive 404", checks, failures)
    missing_text = missing.body.decode("utf-8", errors="replace")
    v4_404_markers = (
        'meta name="offline-pages-404" content="true"',
        "Page not in this archive",
        "This page was not saved in the available archive.",
    )
    if not all(marker in missing_text for marker in v4_404_markers):
        failures.append("archive 404 body lacks its historical missing-page marker")

    for label, path in (
        ("traversal plain 404", f"{prefix}../outside.html"),
        ("backslash plain 404", f"{prefix}nested%5Coutside.html"),
        ("NUL plain 404", f"{prefix}nul%00outside.html"),
    ):
        unsafe = http_request(opener, origin, path, "GET")
        check_http(unsafe, 404, label, checks, failures)
        if unsafe.headers.get("Location"):
            failures.append(f"{label} unexpectedly redirected")

    html_relative = "info/encyclopedia/index.xml.html"
    html_path = f"{prefix}{html_relative}"
    html = http_request(opener, origin, html_path, "GET")
    local_html = (site / html_relative).read_bytes()
    check_http(html, 200, "representative HTML bytes", checks, failures, relative_path=html_relative)
    if html.body != local_html:
        failures.append("representative HTML bytes differ from extracted site")

    binary_relative, local_binary_path = choose_binary(site)
    binary_path = f"{prefix}{binary_relative}"
    binary = http_request(opener, origin, binary_path, "GET")
    local_binary = local_binary_path.read_bytes()
    check_http(binary, 200, "representative binary bytes", checks, failures, relative_path=binary_relative, sha256=hashlib.sha256(local_binary).hexdigest())
    if binary.body != local_binary:
        failures.append(f"representative binary bytes differ from extracted site: {binary_relative}")
    binary_head = http_request(opener, origin, binary_path, "HEAD")
    check_http(binary_head, 200, "representative binary HEAD", checks, failures, relative_path=binary_relative)
    if binary_head.body or binary_head.headers.get("Content-Length") != str(len(local_binary)):
        failures.append("representative binary HEAD length/body is incorrect")

    return {
        "origin": origin,
        "prefix": prefix,
        "proxy_handler": "explicit empty ProxyHandler",
        "checks": checks,
        "failed_checks": failures,
        "passed": not failures,
        "representative_html": html_relative,
        "representative_binary": binary_relative,
        "expected_archive_404": missing_path,
    }


def run_browser_checks(
    *,
    node_exe: Path,
    chrome_exe: Path,
    playwright_module: Path,
    runner: Path,
    extracted: Path,
    server_url: str,
    output_path: Path,
    mobile_screenshot: Path,
    unknown_screenshot: Path,
) -> dict[str, Any]:
    command = [
        str(node_exe),
        str(runner),
        "--base-url",
        server_url,
        "--site",
        str(extracted / "site"),
        "--output",
        str(output_path),
        "--mobile-screenshot",
        str(mobile_screenshot),
        "--unknown-screenshot",
        str(unknown_screenshot),
        "--playwright-module",
        str(playwright_module),
        "--browser",
        str(chrome_exe),
    ]
    env = os.environ.copy()
    env.pop("NODE_PATH", None)
    env.pop("NODE_OPTIONS", None)
    process = subprocess.Popen(
        command,
        cwd=str(extracted),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=BROWSER_TIMEOUT)
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        if process.poll() is None:
            process.kill()
        stdout, stderr = process.communicate()
        return {
            "passed": False,
            "command": command,
            "cwd": str(extracted),
            "timeout_seconds": BROWSER_TIMEOUT,
            "error": "browser runner timed out; its process tree was stopped",
            "stdout_tail": stdout[-2000:],
            "stderr_tail": stderr[-2000:],
        }
    result: dict[str, Any] = {
        "command": command,
        "cwd": str(extracted),
        "returncode": process.returncode,
        "stdout_tail": stdout[-2000:],
        "stderr_tail": stderr[-2000:],
    }
    if output_path.is_file():
        try:
            browser_report = json_load(output_path)
        except QAError as exc:
            result["passed"] = False
            result["error"] = str(exc)
            return result
        result["report"] = browser_report
        result["passed"] = process.returncode == 0 and bool(browser_report.get("passed"))
    else:
        result["passed"] = False
        result["error"] = "browser runner did not produce its JSON report"
    return result


def companion_output_paths(output: Path) -> tuple[Path, Path, Path]:
    """Derive collision-free browser evidence names from an output run stem."""
    stem = output.stem
    base = "portable-bundle-validation"
    run_suffix = stem[len(base) :] if stem.startswith(base) else f"-{stem}"
    return (
        output.with_name(f"portable-browser-validation{run_suffix}.json"),
        output.with_name(f"portable-mobile-login-history{run_suffix}.png"),
        output.with_name(f"portable-unknown404-query{run_suffix}.png"),
    )


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--archive", type=Path, required=True)
    value.add_argument("--report", type=Path, required=True, help="package producer JSON report")
    value.add_argument("--sidecar", type=Path, help="default: <archive>.sha256")
    value.add_argument("--source-site", type=Path, required=True, help="actual v5 source directory used by packaging")
    value.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    value.add_argument("--scratch-root", type=Path, default=EXPECTED_SCRATCH)
    value.add_argument("--python-exe", type=Path, default=DEFAULT_PYTHON)
    value.add_argument("--node-exe", type=Path, default=DEFAULT_NODE)
    value.add_argument("--chrome-exe", type=Path, default=DEFAULT_CHROME)
    value.add_argument("--playwright-module", type=Path, default=DEFAULT_PLAYWRIGHT)
    value.add_argument("--keep-scratch", action="store_true", help="retain the new extraction tree after a passing run")
    return value


def write_json_new(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(path):
        raise QAError(f"refusing to overwrite evidence file: {path}")
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    archive = args.archive.resolve()
    report_path = args.report.resolve()
    sidecar = (args.sidecar or archive.with_name(archive.name + ".sha256")).resolve()
    source_site = args.source_site.resolve()
    output = args.output.resolve()
    scratch = args.scratch_root.resolve()
    browser_report, mobile_screenshot, unknown_screenshot = companion_output_paths(output)
    runner = Path(__file__).resolve().with_name("portable_browser_checks.js")

    evidence: dict[str, Any] = {
        "schema": "wow-encyclopedia-portable-bundle-validation/v1",
        "started_utc": utc_now(),
        "network_performed": False,
        "archive": str(archive),
        "source_site": str(source_site),
        "scratch_requested": str(scratch),
        "output": str(output),
        "server": None,
        "checks": {},
        "failures": [],
        "passed": False,
    }
    server_process: subprocess.Popen[bytes] | None = None
    stdout_handle = None
    stderr_handle = None
    scratch_created = False
    try:
        if not archive.is_file() or archive.is_symlink():
            raise QAError(f"archive is not ready: {archive}")
        require_regular_file(report_path, "generation report")
        require_regular_file(sidecar, "SHA-256 sidecar")
        require_directory(source_site, "source site")
        require_regular_file(args.python_exe.resolve(), "isolated Python")
        require_regular_file(args.node_exe.resolve(), "Node")
        require_regular_file(args.chrome_exe.resolve(), "Chrome")
        if not args.playwright_module.exists():
            raise QAError(f"Playwright module path is missing: {args.playwright_module}")
        require_regular_file(runner, "Playwright companion")
        if scratch != EXPECTED_SCRATCH:
            raise QAError(f"scratch path must resolve exactly to {EXPECTED_SCRATCH}")
        for path in (output, browser_report, mobile_screenshot, unknown_screenshot):
            if os.path.lexists(path):
                raise QAError(f"refusing to overwrite existing output: {path}")

        receipt = verify_receipt(archive, report_path, sidecar)
        evidence["checks"]["receipt"] = receipt
        zip_summary = inspect_zip(archive)
        evidence["checks"]["zip"] = zip_summary
        evidence["checks"]["disk_preflight"] = disk_preflight(archive, scratch, zip_summary["uncompressed_bytes"])
        evidence["checks"]["source_site"] = {
            "resolved": str(source_site),
            "exists": True,
            "recorded_only": True,
        }

        extracted_summary = extract_zip(archive, scratch)
        scratch_created = True
        evidence["checks"]["extraction"] = extracted_summary
        metadata = validate_metadata(scratch, zip_summary)
        evidence["checks"]["package_metadata"] = metadata
        server_process, server_url, server_record, stdout_handle, stderr_handle = start_server(
            scratch, args.python_exe.resolve()
        )
        evidence["server"] = server_record
        evidence["checks"]["http"] = run_http_checks(
            server_url,
            Path(metadata["site"]),
            metadata["project_prefix"],
        )
        if not evidence["checks"]["http"]["passed"]:
            evidence["failures"].extend(evidence["checks"]["http"]["failed_checks"])

        browser = run_browser_checks(
            node_exe=args.node_exe.resolve(),
            chrome_exe=args.chrome_exe.resolve(),
            playwright_module=args.playwright_module.resolve(),
            runner=runner,
            extracted=scratch,
            server_url=server_url,
            output_path=browser_report,
            mobile_screenshot=mobile_screenshot,
            unknown_screenshot=unknown_screenshot,
        )
        evidence["checks"]["browser"] = browser
        if not browser.get("passed"):
            evidence["failures"].append("Playwright browser acceptance failed")
    except (QAError, OSError, ValueError, subprocess.SubprocessError) as exc:
        evidence["failures"].append(f"{type(exc).__name__}: {exc}")
    finally:
        evidence["server_stop"] = stop_server(server_process, stdout_handle, stderr_handle)
        evidence["finished_utc"] = utc_now()
        evidence["passed"] = not evidence["failures"]
        cleaned = False
        if evidence["passed"] and scratch_created and not args.keep_scratch:
            if scratch.resolve() != EXPECTED_SCRATCH:
                evidence["failures"].append("refused cleanup because scratch path changed")
                evidence["passed"] = False
            else:
                try:
                    shutil.rmtree(scratch)
                    cleaned = True
                except OSError as exc:
                    evidence["failures"].append(f"scratch cleanup failed: {exc}")
                    evidence["passed"] = False
        evidence["scratch_cleanup"] = {"requested": not args.keep_scratch, "cleaned": cleaned}
        try:
            write_json_new(output, evidence)
        except QAError as exc:
            print(f"portable validation could not write evidence: {exc}", file=sys.stderr)
            return 2

    print(
        json.dumps(
            {
                "passed": evidence["passed"],
                "archive_sha256": evidence.get("checks", {}).get("receipt", {}).get("archive_sha256"),
                "output": str(output),
                "scratch_cleanup": evidence.get("scratch_cleanup"),
                "failures": evidence["failures"],
            },
            ensure_ascii=False,
        )
    )
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
