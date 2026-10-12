#!/usr/bin/env python3
"""Run a one-shot portability smoke check for the packaged offline mirror.

The check intentionally starts the packaged ``offline_mirror.py`` through the
current Python interpreter after extracting into a fresh scratch directory.
It never deletes an existing extraction directory and only terminates the
server process created by this invocation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "artifacts/WOW_Encyclopedia_20080512_offline_20261011.zip"
REPORT = ROOT / "artifacts/offline-20261011-portability-check.json"
EXTRACTION = ROOT / ".scratch/offline-package-smoke-20261011"
MAX_WORKSPACE_BYTES = 14_000_000_000
MIN_FREE_BYTES = 10 * 1024**3 + 256 * 1024**2
PORT = 8877
POLL_SECONDS = 15.0
PLACEHOLDER_KINDS = {
    "generated_placeholder",
    "missing-placeholder",
    "uncollected-feature",
    "uncollected-page-placeholder",
    "uncollected-script-placeholder",
    "uncollected-stylesheet-placeholder",
    "uncollected-image-placeholder",
    "not-found",
}


class SmokeError(RuntimeError):
    """A portability check failed with an actionable reason."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def workspace_bytes() -> int:
    total = 0
    for path in ROOT.rglob("*"):
        if path.is_file() and not path.is_symlink():
            total += path.stat().st_size
    return total


def budget_snapshot() -> dict[str, int]:
    usage = shutil.disk_usage(ROOT)
    return {
        "workspace_bytes": workspace_bytes(),
        "max_workspace_bytes": MAX_WORKSPACE_BYTES,
        "disk_free_bytes": usage.free,
        "minimum_free_bytes": MIN_FREE_BYTES,
    }


def check_budget(stage: str) -> dict[str, Any]:
    snapshot = budget_snapshot()
    snapshot["stage"] = stage
    snapshot["within_workspace_limit"] = snapshot["workspace_bytes"] < MAX_WORKSPACE_BYTES
    snapshot["within_free_space_limit"] = snapshot["disk_free_bytes"] >= MIN_FREE_BYTES
    if not snapshot["within_workspace_limit"] or not snapshot["within_free_space_limit"]:
        raise SmokeError(f"budget guard failed at {stage}: {snapshot}")
    return snapshot


def validate_member_name(name: str) -> None:
    """Reject absolute, traversal, drive-qualified, and malformed ZIP paths."""

    if not name or "\x00" in name:
        raise SmokeError(f"invalid empty/NUL ZIP member path: {name!r}")
    normalized = name.replace("\\", "/")
    if normalized.startswith("/") or PureWindowsPath(name).is_absolute() or PureWindowsPath(name).drive:
        raise SmokeError(f"absolute ZIP member path: {name!r}")
    if any(part == ".." for part in PurePosixPath(normalized).parts):
        raise SmokeError(f"ZIP member contains '..': {name!r}")


def extract_archive(archive: Path, destination: Path) -> dict[str, Any]:
    if destination.exists():
        raise SmokeError(f"refusing to reuse existing extraction directory: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    members: list[dict[str, Any]] = []
    seen: set[str] = set()
    with zipfile.ZipFile(archive) as package:
        bad_crc = package.testzip()
        if bad_crc:
            raise SmokeError(f"ZIP CRC check failed before extraction: {bad_crc}")
        for info in package.infolist():
            validate_member_name(info.filename)
            normalized = info.filename.replace("\\", "/")
            if normalized in seen:
                raise SmokeError(f"duplicate ZIP member path: {info.filename!r}")
            seen.add(normalized)
            # ZIP symlinks could escape the extraction root on platforms that
            # materialize them.  Package members are expected to be regular
            # files or directories only.
            mode = (info.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                raise SmokeError(f"symlink ZIP member is not allowed: {info.filename!r}")
            members.append({"path": normalized, "bytes": info.file_size, "crc": f"{info.CRC:08x}"})
        package.extractall(destination)

    destination_resolved = destination.resolve()
    for member in members:
        extracted = (destination / member["path"]).resolve()
        try:
            extracted.relative_to(destination_resolved)
        except ValueError as exc:
            raise SmokeError(f"extracted path escapes scratch root: {member['path']}") from exc
    return {"member_count": len(members), "members": members}


def content_type(response: Any) -> str:
    return str(response.headers.get("Content-Type", ""))


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def request_local(base: str, path: str, timeout: float = 5.0, *, include_body: bool = True) -> dict[str, Any]:
    if not path.startswith("/"):
        raise SmokeError(f"smoke request must be local-rooted: {path}")
    started = time.perf_counter()
    request = urllib.request.Request(base + path, headers={"User-Agent": "offline-package-smoke/1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            result: dict[str, Any] = {
                "path": path,
                "status": response.status,
                "content_type": content_type(response),
                "entity_kind": str(response.headers.get("X-Offline-Entity-Kind", "")),
                "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(),
                "elapsed_seconds": round(time.perf_counter() - started, 6),
            }
            if include_body:
                result["body"] = body
            return result
    except urllib.error.HTTPError as exc:
        body = exc.read()
        result = {
            "path": path,
            "status": exc.code,
            "content_type": content_type(exc),
            "entity_kind": str(exc.headers.get("X-Offline-Entity-Kind", "")),
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
            "elapsed_seconds": round(time.perf_counter() - started, 6),
            "error": f"HTTP {exc.code}",
        }
        if include_body:
            result["body"] = body
        return result


def start_server(extraction: Path, port: int) -> tuple[subprocess.Popen[str], Path]:
    server_script = extraction / "tools/offline_mirror.py"
    manifest = extraction / "offline/build-manifest.json"
    site = extraction / "offline/site"
    if not server_script.is_file() or not manifest.is_file() or not site.is_dir():
        raise SmokeError("portable package lacks tools/offline_mirror.py, manifest, or offline/site")
    log_file = extraction / "offline/smoke-request-log.jsonl"
    command = [
        sys.executable,
        str(server_script),
        "serve",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--log-file",
        str(log_file),
    ]
    kwargs: dict[str, Any] = {
        "cwd": str(extraction),
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        "text": True,
    }
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
        kwargs["startupinfo"] = startup
    return subprocess.Popen(command, **kwargs), log_file


def wait_for_server(process: subprocess.Popen[str], base: str, port: int) -> dict[str, Any]:
    startup_lines: list[str] = []
    startup_read = threading.Event()

    def read_startup_line() -> None:
        if process.stdout is None:
            startup_read.set()
            return
        try:
            line = process.stdout.readline()
            if line:
                startup_lines.append(line)
        finally:
            startup_read.set()

    startup_reader = threading.Thread(target=read_startup_line, name="offline-smoke-startup", daemon=True)
    startup_reader.start()
    deadline = time.monotonic() + POLL_SECONDS
    attempts = 0
    last_error = ""
    while time.monotonic() < deadline:
        attempts += 1
        if process.poll() is not None:
            startup_reader.join(timeout=0.1)
            output = process.stdout.read() if process.stdout else ""
            captured = "".join(startup_lines) + output
            raise SmokeError(f"portable server exited before readiness ({process.returncode}): {captured[-2000:]}")
        if not startup_read.wait(timeout=min(0.05, max(0.0, deadline - time.monotonic()))):
            last_error = "waiting for packaged server startup line"
            continue
        startup_output = "".join(startup_lines)
        expected_line = f"offline mirror serving http://127.0.0.1:{port}/"
        if expected_line not in startup_output:
            output = process.stdout.read() if process.stdout else ""
            raise SmokeError(f"portable server did not identify its loopback listener: {(startup_output + output)[-2000:]}")
        try:
            result = request_local(base, "/info/encyclopedia/index.xml", timeout=1.0, include_body=False)
            if result["status"] == 200:
                # A pre-existing listener can answer before a just-started
                # process notices that the port is occupied.  Give the child
                # a brief chance to finish binding and reject that false
                # readiness signal if it has already exited.
                time.sleep(0.05)
                if process.poll() is not None:
                    output = process.stdout.read() if process.stdout else ""
                    raise SmokeError(
                        f"portable server exited after readiness ({process.returncode}): {output[-2000:]}"
                    )
                return {"ready": True, "attempts": attempts, "startup_output": startup_output, "result": result}
            last_error = f"status {result['status']}"
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
            last_error = str(exc)
        time.sleep(0.2)
    raise SmokeError(f"portable server did not become ready within {POLL_SECONDS}s: {last_error}")


def stop_server(process: subprocess.Popen[str]) -> dict[str, Any]:
    if process.poll() is None:
        process.terminate()
    try:
        output, _ = process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        output, _ = process.communicate(timeout=5)
    return {"pid": process.pid, "returncode": process.returncode, "output_tail": (output or "")[-2000:]}


def _route_text(item: dict[str, Any]) -> str:
    return " ".join(
        str(item.get(key, ""))
        for key in ("route", "logical_url", "original", "title", "sidebar_category", "category", "role")
    ).casefold()


def select_smoke_routes(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Select real packaged pages for the portability check.

    The route labels are inferred from manifest metadata and historical URL
    shape.  This keeps v1 useful while allowing a recovery package to expose
    its actual Guide/Media/News pages without hard-coded missing paths.
    """

    files = [
        item for item in manifest.get("files", [])
        if isinstance(item, dict)
        and str(item.get("mime", "")).casefold().split(";", 1)[0] in {"text/html", "application/xhtml+xml"}
        and str(item.get("kind", "")) not in PLACEHOLDER_KINDS
        and item.get("route")
    ]
    by_route = {str(item["route"]): item for item in files}
    root_route = str(manifest.get("route_aliases", {}).get("/", ""))
    homepage = by_route.get(root_route)
    if homepage is None:
        homepage = by_route.get("/info/encyclopedia/index.xml")
    if homepage is None:
        homepage = next((item for item in files if item.get("role") == "core_page"), None)
    if homepage is None:
        raise SmokeError("portable manifest has no real HTML homepage route")

    elune = by_route.get("/info/encyclopedia/392.xml")
    if elune is None:
        elune = next((item for item in files if "elune" in _route_text(item)), None)
    if elune is None:
        elune = next((item for item in files if item.get("role") == "core_page" and item is not homepage), None)
    if elune is None:
        raise SmokeError("portable manifest has no second real HTML page")

    def choose(label: str, predicates: tuple[str, ...], fallback: tuple[str, ...]) -> dict[str, Any]:
        candidate = next((item for item in files if any(token in _route_text(item) for token in predicates)), None)
        if candidate is None:
            candidate = next((by_route.get(route) for route in fallback if by_route.get(route)), None)
        if candidate is None:
            raise SmokeError(f"portable manifest has no real {label} page")
        return candidate

    return {
        "homepage": homepage,
        "elune": elune,
        "guide": choose("Guide", ("guide", "game guide", "/info/story", "/info/basics"), ("/info/story/index.html",)),
        "media": choose("Media", ("media", "downloads", "machinima"), ("/downloads/index.html",)),
        "news": choose("News", ("news", "archivednews"), ("/news/wow-news-06-2006.html", "/info/archivednews.html")),
    }


def _is_real_entity(result: dict[str, Any]) -> bool:
    kind = str(result.get("entity_kind", ""))
    return not kind or kind not in PLACEHOLDER_KINDS


def _html_page_check(result: dict[str, Any], *, require_text: bool = True) -> bool:
    return (
        result["status"] == 200
        and result["content_type"].casefold().startswith("text/html")
        and result["bytes"] > 100
        and _is_real_entity(result)
        and (not require_text or result.get("body_present", bool(result.get("body", b"").strip())))
    )


def run_smoke(
    *,
    archive: Path = ARCHIVE,
    report: Path = REPORT,
    extraction: Path = EXTRACTION,
    port: int = PORT,
) -> dict[str, Any]:
    archive = archive.resolve()
    report = report.resolve()
    extraction = extraction.resolve()
    result: dict[str, Any] = {
        "started_utc": utc_now(),
        "archive": display_path(archive),
        "report": display_path(report),
        "interpreter": sys.executable,
        "method": "extract ZIP into fresh scratch root, then invoke packaged tools/offline_mirror.py through sys.executable; loopback HTTP smoke only, not a double-click GUI test",
        "port": port,
        "requested_extraction_root": display_path(extraction),
        "accepted": False,
    }
    process: subprocess.Popen[str] | None = None
    try:
        if not archive.is_file():
            result.update({"status": "missing_archive", "reason": "portable ZIP has not been generated yet"})
            return result
        result["archive_bytes"] = archive.stat().st_size
        result["archive_sha256"] = sha256_file(archive)
        result["budget_before"] = check_budget("before-extraction")
        if extraction.exists():
            raise SmokeError(f"refusing to reuse existing extraction directory: {extraction}")
        result["zip"] = extract_archive(archive, extraction)
        result["extraction_root"] = display_path(extraction)
        result["budget_after_extraction"] = check_budget("after-extraction")

        manifest_path = extraction / "offline/build-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        result["build_manifest_sha256"] = sha256_file(manifest_path)
        js_item = next((item for item in manifest.get("files", []) if str(item.get("kind")) == "js" and item.get("kind") != "generated_placeholder"), None)
        if not js_item:
            raise SmokeError("portable manifest has no JavaScript file record")
        result["manifest_js_route"] = js_item.get("route")
        smoke_routes = select_smoke_routes(manifest)
        result["selected_routes"] = {label: item["route"] for label, item in smoke_routes.items()}

        process, log_file = start_server(extraction, port)
        result["server_pid"] = process.pid
        base = f"http://127.0.0.1:{port}"
        result["readiness"] = wait_for_server(process, base, port)
        recovery_browser_path = extraction / "research/offline-2008/full-recovery/browser-validation.json"
        if recovery_browser_path.is_file():
            recovery_browser = json.loads(recovery_browser_path.read_text(encoding="utf-8"))
            if recovery_browser.get("server_manifest_sha256"):
                health_response = request_local(base, "/__offline/api/health")
                health = json.loads(health_response["body"])
                result["server_identity"] = health
                if health.get("server_pid") != process.pid or health.get("build_manifest_sha256") != result["build_manifest_sha256"]:
                    raise SmokeError("portable server PID or serving manifest differs from the extracted package")
        home = request_local(base, str(smoke_routes["homepage"]["route"]))
        home_body = home.get("body", b"")
        elune = request_local(base, str(smoke_routes["elune"]["route"]))
        elune_body = elune.get("body", b"")
        js = request_local(base, str(js_item["route"]))
        guide = request_local(base, str(smoke_routes["guide"]["route"]))
        media = request_local(base, str(smoke_routes["media"]["route"]))
        news = request_local(base, str(smoke_routes["news"]["route"]))
        missing = request_local(base, "/__offline/missing.html?source=smoke&requested=%2Fmissing.png")
        for item in (home, elune, js, guide, media, news, missing):
            item["body_present"] = bool(item.get("body", b"").strip())
            item.pop("body", None)
        result["requests"] = {"homepage": home, "elune": elune, "guide": guide, "media": media, "news": news, "manifest_js": js, "missing_notice": missing}
        expected_js_mime = str(js_item.get("mime", "")).split(";", 1)[0].strip().casefold()
        observed_js_mime = js["content_type"].split(";", 1)[0].strip().casefold()
        result["checks"] = {
            "homepage_html": _html_page_check(home) and len(home_body) > 500,
            "elune_html_with_body": _html_page_check(elune) and len(elune_body) > 500 and b"Elune" in elune_body,
            "guide_html": _html_page_check(guide),
            "media_html": _html_page_check(media),
            "news_html": _html_page_check(news),
            "manifest_js_mime": js["status"] == 200 and bool(observed_js_mime) and (observed_js_mime == expected_js_mime if expected_js_mime else "javascript" in observed_js_mime),
            "manifest_js_sha": js["sha256"] == js_item.get("derived_sha256"),
            "local_missing_notice": missing["status"] == 200 and missing["content_type"].casefold().startswith("text/html") and missing.get("entity_kind", "") in {"", "generated_placeholder", "missing-placeholder"},
            "all_smoke_urls_loopback": True,
        }
        if log_file.is_file():
            log_entries = [json.loads(line) for line in log_file.read_text(encoding="utf-8").splitlines() if line.strip()]
            result["server_log"] = {"path": log_file.relative_to(extraction).as_posix(), "count": len(log_entries), "all_requests_rooted": all(str(entry.get("request", "")).startswith("/") for entry in log_entries)}
            result["checks"]["server_log_local_only"] = result["server_log"]["all_requests_rooted"]
        else:
            result["server_log"] = {"path": log_file.relative_to(extraction).as_posix(), "count": 0, "all_requests_rooted": False}
            result["checks"]["server_log_local_only"] = False
        result["accepted"] = all(result["checks"].values())
        result["status"] = "accepted" if result["accepted"] else "failed_checks"
    except Exception as exc:  # noqa: BLE001 - report all smoke failures structurally
        result["status"] = "error"
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if process is not None:
            result["server_stop"] = stop_server(process)
        result["finished_utc"] = utc_now()
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=ARCHIVE, help="package ZIP to inspect")
    parser.add_argument("--report", type=Path, default=REPORT, help="JSON report output path")
    parser.add_argument("--port", type=int, default=PORT, help=f"loopback port for the child server (default: {PORT})")
    parser.add_argument(
        "--extraction",
        "--extraction-dir",
        dest="extraction",
        type=Path,
        default=EXTRACTION,
        help="fresh extraction directory; defaults to the required portability-check path",
    )
    args = parser.parse_args()
    archive = args.archive if args.archive.is_absolute() else ROOT / args.archive
    report = args.report if args.report.is_absolute() else ROOT / args.report
    extraction = args.extraction if args.extraction.is_absolute() else ROOT / args.extraction
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    result = run_smoke(archive=archive, report=report, extraction=extraction, port=args.port)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("accepted") else 2 if result.get("status") == "missing_archive" else 1


if __name__ == "__main__":
    raise SystemExit(main())
