"""Root-GO-gated, bounded ArchiveCraft HTML source probe.

Preparation and ``--offline-fixtures`` never contact the network.  Only
``--execute --go PATH`` is a network entry point.  The four URLs are fixed
from an already observed main-site link set; redirects are recorded and are
never followed.  Current HTTPS observations are not historical captures.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PLAN = OUT / "plan.json"
BINDINGS = OUT / "input-bindings.json"
FIXTURE = OUT / "fixture-results.json"
RUNTIME = OUT / "runtime"

PROXY = "http://127.0.0.1:7890"
BATCH_ID = "archivecraft-dungeons01"
TARGETS: list[dict[str, str]] = [
    {"target_id": "archivecraft-dungeons", "url": "https://archivecraft.com/townhall/dungeons/"},
    {"target_id": "archivecraft-dungeons-instances", "url": "https://archivecraft.com/townhall/dungeons/instances/"},
    {"target_id": "archivecraft-dungeons-outland", "url": "https://archivecraft.com/townhall/dungeons/instances/outland/"},
    {"target_id": "archivecraft-about", "url": "https://archivecraft.com/about/"},
    {"target_id": "archivecraft-disclaimer", "url": "https://archivecraft.com/disclaimer/"},
]

MAX_LOGICAL_REQUESTS = 5
MAX_ATTEMPTS = 10
MAX_SECONDS = 600.0
PARENT_SECONDS = 660
REQUEST_SECONDS = 30.0
CONNECT_SECONDS = 10
MIN_START_SECONDS = 6.2
DISK_FLOOR = 11_005_853_696
TOTAL_BODY_CAP = 16 * 1024 * 1024
MAX_RESPONSE_BYTES = 4 * 1024 * 1024
MAX_PAGE_BYTES = 4 * 1024 * 1024
MIN_COOLDOWN = 120
MAX_TRANSPORT_FAILURES = 5
STOP_HTTP = {429, 503}
STATUS_RE = re.compile(r"^HTTP/\S+\s+(\d{3})\b", re.I)
RETRY_AFTER_RE = re.compile(r"^retry-after:\s*(.+)$", re.I | re.M)
CSS_URL_RE = re.compile(r"url\(\s*(?:['\"])?([^'\")\s]+)", re.I)
SOURCE_TEXT_RE = re.compile(r"\b(?:source|sourc(?:ed|ing)|credit|courtesy|via|archive|wayback|reddit|imgur|github|screenshot|image|photo|photograph|illustrat|artwork|material|copyright|permission|license)\b", re.I)


@dataclass(frozen=True)
class Paths:
    runtime: Path
    private: Path
    raw: Path
    journal: Path
    report: Path
    public: Path


def make_paths(runtime: Path) -> Paths:
    private = runtime / "private"
    return Paths(runtime, private, private / "raw", private / "attempt-journal.jsonl", private / "report.json", runtime / "public-inventory.json")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat().replace("+00:00", "Z")


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def disk_free() -> int:
    return shutil.disk_usage(ROOT).free


def require_disk(stage: str) -> int:
    free = disk_free()
    if free < DISK_FLOOR:
        raise RuntimeError(f"disk floor failed at {stage}: {free} < {DISK_FLOOR}")
    return free


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON object required: {path}")
    return value


def retry_after_seconds(value: str | None, *, now: datetime | None = None) -> int | None:
    if not value:
        return None
    try:
        return max(0, int(value.strip()))
    except (TypeError, ValueError):
        try:
            retry_at = parsedate_to_datetime(value.strip())
        except (TypeError, ValueError, OverflowError):
            return None
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        current = now or utc_now()
        return max(0, math.ceil((retry_at.astimezone(timezone.utc) - current.astimezone(timezone.utc)).total_seconds()))


def parse_headers(data: bytes) -> dict[str, Any]:
    text = data.decode("iso-8859-1", errors="replace")
    blocks = re.split(r"\r?\n\r?\n", text)
    for block in reversed(blocks):
        lines = block.splitlines()
        if not lines:
            continue
        match = STATUS_RE.match(lines[0].strip())
        if not match:
            continue
        values: dict[str, str] = {}
        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                values[key.strip().lower()] = value.strip()
        length = int(values["content-length"]) if values.get("content-length", "").isdigit() else None
        return {
            "status": int(match.group(1)),
            "content_type": values.get("content-type"),
            "content_length": length,
            "location": values.get("location"),
            "retry_after": values.get("retry-after") or (RETRY_AFTER_RE.search(text).group(1).strip() if RETRY_AFTER_RE.search(text) else None),
            "headers": values,
        }
    return {"status": None, "content_type": None, "content_length": None, "location": None, "retry_after": None, "headers": {}}


def clean_child_env() -> dict[str, str]:
    env = os.environ.copy()
    for key in list(env):
        if key.lower() in {"http_proxy", "https_proxy", "all_proxy", "no_proxy"}:
            env.pop(key, None)
    return env


def curl_command(target: dict[str, str], *, use_proxy: bool, headers: Path, body: Path, cookie: Path, max_time_seconds: float, remaining_body_bytes: int) -> list[str]:
    if remaining_body_bytes <= 0:
        raise RuntimeError("no remaining body budget for GET")
    cap = min(MAX_RESPONSE_BYTES, remaining_body_bytes)
    command = [
        "curl.exe", "--silent", "--show-error", "--tlsv1.2", "--proto", "=https",
        "--connect-timeout", str(CONNECT_SECONDS), "--max-time", f"{max_time_seconds:.3f}",
        "--retry", "0", "--max-redirs", "0", "--dump-header", str(headers),
        "--header", "Accept-Encoding: identity", "--cookie-jar", str(cookie),
        "--max-filesize", str(cap), "--output", str(body), "--write-out", "%{http_code}\\n%{url_effective}",
    ]
    command += ["--proxy", PROXY] if use_proxy else ["--noproxy", "*"]
    command.append(target["url"])
    return command


def append_journal(paths: Paths, event: dict[str, Any]) -> None:
    require_disk("before journal append")
    paths.journal.parent.mkdir(parents=True, exist_ok=True)
    with paths.journal.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    require_disk("after journal append")


def wait_cadence(last_start: float | None, batch_start: float, cadence_seconds: float, batch_seconds: float) -> None:
    if last_start is None or cadence_seconds <= 0:
        return
    delay = cadence_seconds - (time.monotonic() - last_start)
    if delay > 0:
        if time.monotonic() - batch_start + delay >= batch_seconds:
            raise RuntimeError("batch window exhausted before cadence wait")
        time.sleep(delay)


def as_bytes(value: bytes | str | None) -> bytes:
    if value is None:
        return b""
    return value if isinstance(value, bytes) else value.encode("utf-8", errors="replace")


def transport_failed(status: int | None, returncode: int | None, timed_out: bool, cap_exceeded: bool) -> bool:
    if cap_exceeded:
        return False
    if status is None:
        return True
    if status >= 400:
        return False
    return timed_out or returncode is None or returncode != 0


def run_attempt(target: dict[str, str], attempt_no: int, use_proxy: bool, last_start: float | None, batch_start: float, remaining_body_bytes: int, paths: Paths, *, cadence_seconds: float = MIN_START_SECONDS, batch_seconds: float = MAX_SECONDS) -> tuple[dict[str, Any], float]:
    transport = "proxy" if use_proxy else "direct"
    stem = f"attempt-{attempt_no:02d}-{target['target_id']}-{transport}"
    headers = paths.raw / f"{stem}.headers"
    body = paths.raw / f"{stem}.body"
    stderr_path = paths.raw / f"{stem}.stderr.txt"
    cookie = paths.raw / f"{stem}.cookies.txt"
    for path in (headers, body, stderr_path, cookie):
        path.parent.mkdir(parents=True, exist_ok=True)
    require_disk(f"before attempt {attempt_no} preflight")
    append_journal(paths, {"phase": "attempt_preflight", "attempt": attempt_no, "logical_request": target["target_id"], "url": target["url"], "transport": transport, "prepared_utc": iso_now(), "disk_free_before_bytes": disk_free()})
    wait_cadence(last_start, batch_start, cadence_seconds, batch_seconds)
    remaining = batch_seconds - (time.monotonic() - batch_start)
    if remaining <= 0:
        raise RuntimeError("batch window exhausted before attempt")
    timeout = min(REQUEST_SECONDS, remaining)
    require_disk(f"before attempt {attempt_no} request")
    command = curl_command(target, use_proxy=use_proxy, headers=headers, body=body, cookie=cookie, max_time_seconds=timeout, remaining_body_bytes=remaining_body_bytes)
    started_mono = time.monotonic()
    start_interval = None if last_start is None else started_mono - last_start
    started_utc = iso_now()
    timed_out = False
    returncode: int | None = None
    stdout = b""
    stderr = b""
    exception_text: str | None = None
    try:
        completed = subprocess.run(command, capture_output=True, timeout=max(1.0, timeout), check=False, env=clean_child_env())
        returncode = completed.returncode
        stdout = as_bytes(completed.stdout)
        stderr = as_bytes(completed.stderr)
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = as_bytes(exc.stdout)
        stderr = as_bytes(exc.stderr)
        exception_text = "subprocess_timeout"
    except OSError as exc:
        exception_text = f"os_error:{type(exc).__name__}"
    finally:
        for path in (headers, body, cookie):
            if not path.exists():
                path.write_bytes(b"")
        stderr_path.write_bytes(stderr)
        require_disk(f"after attempt {attempt_no} raw write")
    header_bytes = headers.read_bytes()
    body_bytes = body.read_bytes()
    parsed = parse_headers(header_bytes)
    output_lines = stdout.decode("utf-8", errors="replace").splitlines()
    status_text = output_lines[0].strip() if output_lines else ""
    effective_url = output_lines[1].strip() if len(output_lines) > 1 else target["url"]
    if parsed["status"] is None and re.fullmatch(r"\d{3}", status_text):
        parsed["status"] = int(status_text)
    if not effective_url:
        effective_url = target["url"]
    cap = min(MAX_RESPONSE_BYTES, remaining_body_bytes)
    cap_exceeded = returncode == 63 or len(body_bytes) > cap
    failed = transport_failed(parsed["status"], returncode, timed_out, cap_exceeded)
    finished_utc = iso_now()
    record: dict[str, Any] = {
        "attempt": attempt_no, "logical_request": target["target_id"], "url": target["url"], "transport": transport,
        "request_started_utc": started_utc, "request_finished_utc": finished_utc, "actual_start_interval_seconds": start_interval,
        "effective_url": effective_url, "attempt_timeout_seconds": timeout,
        "returncode": returncode, "http_status": parsed["status"], "timed_out": timed_out,
        "transport_failed": failed, "response_cap_exceeded": cap_exceeded, "request_body_cap": cap,
        "body_bytes": len(body_bytes), "body_sha256": hashlib.sha256(body_bytes).hexdigest(),
        "headers_sha256": hashlib.sha256(header_bytes).hexdigest(), "cookie_sha256": hashlib.sha256(cookie.read_bytes()).hexdigest(),
        "stderr_sha256": hashlib.sha256(stderr).hexdigest(), "retry_after": parsed.get("retry_after"),
        "body_path": safe_rel(body), "headers_path": safe_rel(headers), "cookie_path": safe_rel(cookie),
        "stderr_path": safe_rel(stderr_path), "header_parse": parsed, "command": command,
        "exception": exception_text, "disk_free_after_bytes": disk_free(), "_body_file": str(body),
    }
    append_journal(paths, {"phase": "attempt_end", "attempt": attempt_no, "logical_request": target["target_id"], "url": target["url"], "transport": transport, "request_started_utc": started_utc, "request_finished_utc": finished_utc, "actual_start_interval_seconds": start_interval, "effective_url": effective_url, "returncode": returncode, "http_status": parsed["status"], "timed_out": timed_out, "transport_failed": failed, "response_cap_exceeded": cap_exceeded, "request_body_cap": cap, "body_bytes": len(body_bytes), "headers_bytes": len(header_bytes), "stderr_bytes": len(stderr), "body_path": safe_rel(body), "headers_path": safe_rel(headers), "cookie_path": safe_rel(cookie), "stderr_path": safe_rel(stderr_path), "exception": exception_text, "disk_free_after_bytes": disk_free()})
    return record, started_mono


def css_urls(value: str) -> list[str]:
    return [match.group(1).strip() for match in CSS_URL_RE.finditer(value) if match.group(1).strip()]


def srcset_urls(value: str) -> list[str]:
    found: list[str] = []
    for candidate in value.split(","):
        item = candidate.strip()
        if not item:
            continue
        token = item.split()[0]
        if token:
            found.append(token)
    return found


def safe_public_url(raw: str | None, base_url: str) -> str | None:
    if not raw or any(ord(char) < 32 for char in raw):
        return None
    try:
        parsed = urlsplit(urljoin(base_url, raw.strip()))
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
            return None
        host = parsed.hostname.encode("idna").decode("ascii").lower()
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        try:
            port = parsed.port
        except ValueError:
            return None
        netloc = host if port is None else f"{host}:{port}"
        return urlunsplit((parsed.scheme.lower(), netloc, parsed.path or "/", "", ""))
    except (UnicodeError, ValueError):
        return None


class StaticPageParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.title_parts: list[str] = []
        self.in_title = False
        self.in_style = False
        self.style_parts: list[str] = []
        self.dependencies: list[dict[str, str]] = []
        self.image_links: list[dict[str, Any]] = []
        self.source_statements: list[dict[str, Any]] = []
        self.source_blocks: list[dict[str, Any]] = []
        self.figures: list[dict[str, Any]] = []
        self.anchor_hrefs: list[str] = []
        self.script_tags = 0
        self.form_tags = 0
        self.unsafe_embeds = 0
        self.block_tags = {"p", "li", "blockquote", "figcaption", "small", "footer", "dt", "dd", "h1", "h2", "h3", "h4", "h5", "h6"}

    def add_dependency(self, kind: str, raw: str) -> None:
        raw = raw.strip()
        if not raw or raw.lower().startswith(("data:", "javascript:", "#")):
            return
        self.dependencies.append({"kind": kind, "raw": raw, "resolved": urljoin(self.base_url, raw)})

    def add_css(self, kind: str, css: str) -> None:
        for raw in css_urls(css):
            self.add_dependency(kind, raw)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attr = {key.lower(): value or "" for key, value in attrs}
        if tag in self.block_tags:
            self.source_blocks.append({"tag": tag, "parts": [], "links": []})
        if tag == "a":
            self.anchor_hrefs.append(attr.get("href", ""))
            if self.source_blocks and attr.get("href"):
                self.source_blocks[-1]["links"].append(attr["href"])
        if tag == "figure":
            self.figures.append({"image_indexes": [], "caption_parts": [], "in_caption": False})
        if tag == "figcaption" and self.figures:
            self.figures[-1]["in_caption"] = True
        if tag == "title":
            self.in_title = True
        if tag == "style":
            self.in_style = True
            self.style_parts = []
        if tag == "img":
            src = attr.get("src", "").strip()
            srcset = srcset_urls(attr.get("srcset", "")) if attr.get("srcset") else []
            if attr.get("src"):
                self.add_dependency("img", attr["src"])
            if attr.get("srcset"):
                for raw in srcset:
                    self.add_dependency("srcset", raw)
            image = {
                "src": src or None, "srcset": srcset, "alt": attr.get("alt") or None,
                "title": attr.get("title") or None, "width": attr.get("width") or None,
                "height": attr.get("height") or None,
                "linked_image_url": (self.anchor_hrefs[-1] if self.anchor_hrefs and self.anchor_hrefs[-1] else None),
                "caption": None,
            }
            self.image_links.append(image)
            if self.figures:
                self.figures[-1]["image_indexes"].append(len(self.image_links) - 1)
        if tag == "link" and "stylesheet" in attr.get("rel", "").lower().split():
            if attr.get("href"):
                self.add_dependency("css", attr["href"])
        if attr.get("style"):
            self.add_css("style", attr["style"])
        if tag == "script":
            self.script_tags += 1
        if tag == "form":
            self.form_tags += 1
        if tag in {"iframe", "object", "embed", "input", "button"}:
            self.unsafe_embeds += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
        if tag == "a" and self.anchor_hrefs:
            self.anchor_hrefs.pop()
        if tag == "figcaption" and self.figures:
            self.figures[-1]["in_caption"] = False
        if tag == "figure" and self.figures:
            figure = self.figures.pop()
            caption = " ".join("".join(figure["caption_parts"]).split())[:1000] or None
            for index in figure["image_indexes"]:
                self.image_links[index]["caption"] = caption
        if tag == "style":
            self.add_css("style", "".join(self.style_parts))
            self.in_style = False
            self.style_parts = []
        if tag in self.block_tags:
            for index in range(len(self.source_blocks) - 1, -1, -1):
                block = self.source_blocks[index]
                if block["tag"] == tag:
                    self.source_blocks.pop(index)
                    statement = " ".join("".join(block["parts"]).split())[:1000]
                    if statement and SOURCE_TEXT_RE.search(statement):
                        key = statement.casefold()
                        if all(item["text"].casefold() != key for item in self.source_statements):
                            safe_links = []
                            for href in block["links"]:
                                safe = safe_public_url(href, self.base_url)
                                if safe and safe not in safe_links:
                                    safe_links.append(safe)
                            self.source_statements.append({"text": statement, "links": safe_links})
                    break

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_style:
            self.style_parts.append(data)
        for block in self.source_blocks:
            block["parts"].append(data)
        for figure in self.figures:
            if figure["in_caption"]:
                figure["caption_parts"].append(data)

    def finish(self) -> None:
        self.source_statements = self.source_statements[:100]
        for image in self.image_links:
            image["src"] = safe_public_url(image.get("src"), self.base_url)
            image["srcset"] = [safe for value in image.get("srcset", []) if (safe := safe_public_url(value, self.base_url))]
            image["linked_image_url"] = safe_public_url(image.get("linked_image_url"), self.base_url)


def parse_html(body: bytes, target_url: str, content_type: str | None) -> dict[str, Any]:
    lowered_type = (content_type or "").lower()
    if not ("text/html" in lowered_type or "application/xhtml+xml" in lowered_type):
        return {"valid": False, "classification": "non_html_content_type", "title": None, "dependencies": [], "security": {"script_tags": 0, "form_tags": 0, "unsafe_embeds": 0}}
    if not body:
        return {"valid": False, "classification": "empty_html_body", "title": None, "dependencies": [], "security": {"script_tags": 0, "form_tags": 0, "unsafe_embeds": 0}}
    text = body.decode("utf-8", errors="replace")
    parser = StaticPageParser(target_url)
    parser.feed(text)
    parser.close()
    parser.finish()
    title = " ".join("".join(parser.title_parts).split()) or None
    visible = re.sub(r"<[^>]+>", " ", text, flags=re.S)
    soft404 = bool(re.search(r"\b(?:404|not\s+found|page\s+does\s+not\s+exist|error\s+page)\b", f"{title or ''} {visible[:65536]}", re.I))
    security = {"script_tags": parser.script_tags, "form_tags": parser.form_tags, "unsafe_embeds": parser.unsafe_embeds, "scripts_or_forms_executed": False}
    return {"valid": not soft404, "classification": "soft404_suspect" if soft404 else "accepted_html", "title": title, "dependencies": parser.dependencies, "image_links": parser.image_links, "source_statements": parser.source_statements, "security": security}


def public_page(target: dict[str, str], record: dict[str, Any] | None, body: bytes, *, attempt_count: int, observed_utc: str, forced_reason: str | None = None) -> dict[str, Any]:
    meta = (record or {}).get("header_parse", {})
    status = (record or {}).get("http_status")
    location = meta.get("location")
    if forced_reason:
        parsed = {"valid": False, "classification": forced_reason, "title": None, "dependencies": [], "security": {"script_tags": 0, "form_tags": 0, "unsafe_embeds": 0}}
    elif status != 200:
        parsed = {"valid": False, "classification": "redirect_not_followed" if 300 <= (status or 0) < 400 and location else f"http_status_{status}", "title": None, "dependencies": [], "security": {"script_tags": 0, "form_tags": 0, "unsafe_embeds": 0}}
    elif record and (record.get("returncode") != 0 or record.get("timed_out") or record.get("response_cap_exceeded") or record.get("transport_failed")):
        parsed = {"valid": False, "classification": "truncated_or_incomplete_transfer", "title": None, "dependencies": [], "security": {"script_tags": 0, "form_tags": 0, "unsafe_embeds": 0}}
    else:
        parsed = parse_html(body, target["url"], meta.get("content_type"))
    safe_url = safe_public_url(target["url"], target["url"]) or target["url"]
    safe_location = safe_public_url(location, target["url"]) if location else None
    redirect = bool(status and 300 <= status < 400)
    effective_url = safe_public_url((record or {}).get("effective_url"), target["url"]) or safe_url
    return {
        "target_id": target["target_id"], "url": safe_url, "current_observed_utc": observed_utc,
        "current_response_is_not_historical_capture": True, "attempt_count": attempt_count,
        "http_status": status, "transport": (record or {}).get("transport"), "returncode": (record or {}).get("returncode"),
        "request_started_utc": (record or {}).get("request_started_utc"), "request_finished_utc": (record or {}).get("request_finished_utc"),
        "effective_url": effective_url, "redirect_chain": {"observed": [safe_url] + ([safe_location] if redirect and safe_location else []), "followed": False, "complete": not redirect},
        "body_bytes": len(body), "body_sha256": hashlib.sha256(body).hexdigest(),
        "content_type": meta.get("content_type"), "redirect_location": safe_location, "classification": parsed["classification"],
        "title": parsed.get("title"), "dependencies": [{"kind": item["kind"], "url": safe_public_url(item["resolved"], target["url"])} for item in parsed.get("dependencies", []) if safe_public_url(item["resolved"], target["url"])],
        "image_links": parsed.get("image_links", []), "source_statements": parsed.get("source_statements", []), "security": parsed.get("security", {}),
        "valid": bool(parsed.get("valid")),
    }


def cooldown_from_record(record: dict[str, Any], wait_seconds: int) -> str:
    finished = datetime.fromisoformat(record["request_finished_utc"].replace("Z", "+00:00"))
    return (finished + timedelta(seconds=wait_seconds)).isoformat().replace("+00:00", "Z")


def handle_status(record: dict[str, Any]) -> tuple[str | None, str | None]:
    status = record.get("http_status")
    if status in STOP_HTTP:
        wait = max(MIN_COOLDOWN, retry_after_seconds(record.get("retry_after")) or 0)
        return f"endpoint_status_{status}", cooldown_from_record(record, wait)
    return None, None


def run_core(targets: list[dict[str, str]], paths: Paths, *, max_logical: int = MAX_LOGICAL_REQUESTS, max_attempts: int = MAX_ATTEMPTS, max_seconds: float = MAX_SECONDS, cadence_seconds: float = MIN_START_SECONDS, total_cap: int = TOTAL_BODY_CAP) -> dict[str, Any]:
    paths.runtime.mkdir(parents=True, exist_ok=False)
    paths.private.mkdir(parents=True, exist_ok=True)
    paths.raw.mkdir(parents=True, exist_ok=True)
    require_disk("batch start")
    batch_start = time.monotonic()
    started_utc = iso_now()
    total_body = 0
    page_body: dict[str, int] = {}
    attempts: list[dict[str, Any]] = []
    public_records: list[dict[str, Any]] = []
    last_start: float | None = None
    transport_failures = 0
    stop_reason = "completed"
    cooldown_not_before: str | None = None
    stop_batch = False
    try:
        for target in targets[:max_logical]:
            target_attempts: list[dict[str, Any]] = []
            target_failure: str | None = None
            use_proxy = False
            while not target_attempts or (target_attempts[-1]["transport_failed"] and not target_attempts[-1]["response_cap_exceeded"] and target_attempts[-1]["transport"] == "direct"):
                if len(attempts) >= max_attempts:
                    target_failure = "maximum_attempts_reached"
                    stop_reason = "maximum_attempts_reached"
                    stop_batch = True
                    break
                if time.monotonic() - batch_start >= max_seconds:
                    target_failure = "batch_time_limit_reached"
                    stop_reason = "batch_time_limit_reached"
                    stop_batch = True
                    break
                remaining_page = MAX_PAGE_BYTES - page_body.get(target["target_id"], 0)
                remaining_total = total_cap - total_body
                remaining = min(remaining_page, remaining_total)
                if remaining <= 0:
                    target_failure = "page_or_total_body_cap_reached"
                    if remaining_total <= 0:
                        stop_reason = "total_body_cap_reached"
                        stop_batch = True
                    break
                use_proxy = bool(target_attempts and target_attempts[-1]["transport_failed"] and target_attempts[-1]["transport"] == "direct")
                try:
                    record, last_start = run_attempt(target, len(attempts) + 1, use_proxy, last_start, batch_start, remaining, paths, cadence_seconds=cadence_seconds, batch_seconds=max_seconds)
                except RuntimeError as exc:
                    target_failure = "batch_time_limit_reached" if "window exhausted" in str(exc) else "request_precondition_failed"
                    stop_reason = target_failure
                    stop_batch = True
                    break
                attempts.append(record)
                target_attempts.append(record)
                page_body[target["target_id"]] = page_body.get(target["target_id"], 0) + record["body_bytes"]
                total_body += record["body_bytes"]

                status_reason, status_cooldown = handle_status(record)
                if status_reason:
                    target_failure = status_reason
                    stop_reason = status_reason
                    cooldown_not_before = status_cooldown
                    stop_batch = True
                    break
                if record["transport_failed"]:
                    transport_failures += 1
                    if transport_failures >= MAX_TRANSPORT_FAILURES:
                        target_failure = "transport_failure_limit"
                        stop_reason = target_failure
                        cooldown_not_before = cooldown_from_record(record, MIN_COOLDOWN)
                        stop_batch = True
                        break
                    if record["response_cap_exceeded"] or record["transport"] == "proxy":
                        target_failure = "transport_failed_no_further_fallback"
                        break
                    continue
                transport_failures = 0
                if record["response_cap_exceeded"]:
                    target_failure = "response_cap_exceeded"
                break

            if target_attempts:
                record = target_attempts[-1]
                body = Path(record["_body_file"]).read_bytes()
                public_records.append(public_page(target, record, body, attempt_count=len(target_attempts), observed_utc=iso_now(), forced_reason=target_failure))
            else:
                public_records.append(public_page(target, None, b"", attempt_count=0, observed_utc=iso_now(), forced_reason=target_failure or "not_attempted"))
            if stop_batch:
                break
    finally:
        finished_utc = iso_now()
        report = {
            "schema": f"wow-recovery.{BATCH_ID}.private-report.v1", "batch_id": BATCH_ID,
            "started_utc": started_utc, "finished_utc": finished_utc, "attempt_count": len(attempts), "logical_count": len(public_records),
            "total_body_bytes": total_body, "page_body_bytes": page_body, "stop_reason": stop_reason, "cooldown_not_before_utc": cooldown_not_before,
            "attempts": attempts, "public_record_count": len(public_records), "raw_private": True, "cookies_private": True,
            "network_requests_at_prepare": 0,
        }
        require_disk("before private report")
        paths.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        public = {
            "schema": f"wow-recovery.{BATCH_ID}.public-inventory.v1", "batch_id": BATCH_ID,
            "complete": stop_reason == "completed" and len(public_records) == min(max_logical, len(targets)), "stop_reason": stop_reason,
            "cooldown_not_before_utc": cooldown_not_before, "attempt_count": len(attempts), "total_body_bytes": total_body, "records": public_records,
            "evidence_scope": "Current-origin HTTPS HTML response metadata and static page statements/image references only; no historical capture claim. XML/navigation anchors are not classified as image resources.",
            "raw_http_private": True, "network_requests_at_prepare": 0,
        }
        require_disk("before public inventory")
        paths.public.write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        require_disk("after public inventory")
    return {"stop_reason": stop_reason, "attempt_count": len(attempts), "logical_count": len(public_records), "total_body_bytes": total_body, "cooldown_not_before_utc": cooldown_not_before, "public_records": public_records}


def validate_plan() -> dict[str, Any]:
    plan = load_json(PLAN)
    if plan.get("mode") != "prepared" or plan.get("root_go_required") is not True or plan.get("batch_id") != BATCH_ID:
        raise RuntimeError("plan is not prepared/root-gated")
    if plan.get("network_requests_at_prepare") != 0:
        raise RuntimeError("preparation network count is nonzero")
    roster = plan.get("target_roster")
    planned_targets = plan.get("targets")
    roster_pairs = [{"target_id": item.get("target_id"), "url": item.get("url")} for item in roster] if isinstance(roster, list) else None
    if roster_pairs != TARGETS or not isinstance(planned_targets, list) or len(planned_targets) > MAX_LOGICAL_REQUESTS:
        raise RuntimeError("target roster or request target set changed")
    target_keys = {(item.get("target_id"), item.get("url")) for item in TARGETS}
    if any(not isinstance(item, dict) or (item.get("target_id"), item.get("url")) not in target_keys for item in planned_targets):
        raise RuntimeError("unapproved target in request target set")
    if len({item["url"] for item in planned_targets}) != len(planned_targets):
        raise RuntimeError("duplicate request URL")
    reused = plan.get("reused_sources", [])
    if not isinstance(reused, list):
        raise RuntimeError("reused_sources must be an array")
    reused_urls = {item.get("url") for item in reused if isinstance(item, dict)}
    planned_urls = {item["url"] for item in planned_targets}
    if planned_urls & reused_urls or planned_urls | reused_urls != {item["url"] for item in roster}:
        raise RuntimeError("each roster URL must be either requested or recorded as reused")
    for item in reused:
        if not isinstance(item, dict) or not all(key in item for key in ("url", "source_path", "body_bytes", "body_sha256", "observed_utc", "http_status")):
            raise RuntimeError("reused source evidence is incomplete")
        source_path = (ROOT / str(item["source_path"])).resolve()
        if not source_path.is_file() or source_path.stat().st_size != item["body_bytes"] or sha_file(source_path) != item["body_sha256"]:
            raise RuntimeError("reused source bytes or hash do not match the plan")
        if item["http_status"] != 200:
            raise RuntimeError("only HTTP 200 cache entries can be reused as page bodies")
    policy = plan.get("policy", {})
    expected = {
        "maximum_logical_requests": MAX_LOGICAL_REQUESTS,
        "maximum_http_attempts": MAX_ATTEMPTS,
        "maximum_batch_seconds": int(MAX_SECONDS),
        "parent_watchdog_seconds": PARENT_SECONDS,
        "maximum_request_seconds": int(REQUEST_SECONDS),
        "curl_connect_timeout_seconds": CONNECT_SECONDS,
        "minimum_request_start_seconds": MIN_START_SECONDS,
        "maximum_total_body_bytes": TOTAL_BODY_CAP,
        "maximum_response_bytes": MAX_RESPONSE_BYTES,
        "maximum_page_body_bytes": MAX_PAGE_BYTES,
        "disk_floor_bytes": DISK_FLOOR,
        "process_proxy": PROXY,
        "direct_first": True,
        "proxy_fallback_only_after_transport_failure": True,
        "tls_verification": True,
        "follow_redirects": False,
        "automatic_retries": 0,
        "stop_http_statuses": [429, 503],
        "cooldown_seconds_minimum": MIN_COOLDOWN,
        "consecutive_transport_failure_stop": MAX_TRANSPORT_FAILURES,
    }
    for key, value in expected.items():
        if policy.get(key) != value:
            raise RuntimeError(f"policy mismatch: {key}")
    if plan.get("preservation_constraints", {}).get("freeze_existing_sources") is not True:
        raise RuntimeError("existing-source preservation constraint missing")
    require_disk("plan validation")
    return plan


def validate_execute(go_path: Path) -> dict[str, Any]:
    plan = validate_plan()
    if plan.get("reuse_review", {}).get("complete") is not True:
        raise RuntimeError("local-cache reuse review is incomplete")
    if RUNTIME.exists():
        raise RuntimeError("refusing existing runtime/private output")
    if not BINDINGS.is_file() or not FIXTURE.is_file():
        raise RuntimeError("missing input bindings or offline fixture")
    bindings = load_json(BINDINGS)
    expected = {"plan_sha256": sha_file(PLAN), "runner_sha256": sha_file(Path(__file__)), "fixture_sha256": sha_file(FIXTURE), "targets_sha256": hashlib.sha256(json.dumps(plan["targets"], ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()}
    for key, value in expected.items():
        if bindings.get(key) != value:
            raise RuntimeError(f"binding mismatch: {key}")
    fixture = load_json(FIXTURE)
    if fixture.get("all_passed") is not True or fixture.get("network_requests") != 0:
        raise RuntimeError("offline fixture is not accepted/no-network")
    if not go_path.is_file():
        raise RuntimeError("missing root GO")
    go = load_json(go_path)
    if go.get("accepted") is not True or go.get("root_go") is not True:
        raise RuntimeError("GO is not accepted/root_go")
    for key, value in expected.items():
        if go.get(key) not in (None, value):
            raise RuntimeError(f"GO mismatch: {key}")
    if go.get("batch_id") not in (None, plan["batch_id"]):
        raise RuntimeError("GO batch mismatch")
    valid_until = go.get("valid_until")
    if valid_until and datetime.fromisoformat(str(valid_until).replace("Z", "+00:00")) <= utc_now():
        raise RuntimeError("GO expired")
    require_disk("before batch")
    return plan


def execute(go_path: Path) -> int:
    plan = validate_execute(go_path.resolve())
    result = run_core(plan["targets"], make_paths(RUNTIME))
    return 0 if result["stop_reason"] == "completed" else 2


class FixtureStub:
    def __init__(self, scenarios: dict[str, list[dict[str, Any]]], targets: list[dict[str, str]] | None = None) -> None:
        self.scenarios = scenarios
        self.url_to_id = {item["url"]: item["target_id"] for item in (targets or TARGETS)}
        self.calls: list[dict[str, Any]] = []

    def __call__(self, command: list[str], *, capture_output: bool, timeout: float, check: bool, env: dict[str, str]) -> subprocess.CompletedProcess[bytes]:
        url = command[-1]
        transport = "proxy" if "--proxy" in command else "direct"
        target_id = self.url_to_id.get(url, url)
        scenario_list = self.scenarios.setdefault(target_id, [])
        scenario = scenario_list.pop(0) if scenario_list else {"status": 200, "content_type": "text/html", "body": b"<html><title>default</title></html>"}
        headers = Path(command[command.index("--dump-header") + 1])
        body_path = Path(command[command.index("--output") + 1])
        cookie = Path(command[command.index("--cookie-jar") + 1])
        body = scenario.get("body", b"")
        if isinstance(body, str):
            body = body.encode("utf-8")
        status = scenario.get("status")
        header_lines = []
        if status is not None:
            header_lines.append(f"HTTP/1.1 {status} Fixture")
            if scenario.get("content_type"):
                header_lines.append(f"Content-Type: {scenario['content_type']}")
            if scenario.get("content_length", True) and body is not None:
                header_lines.append(f"Content-Length: {len(body)}")
            if scenario.get("location"):
                header_lines.append(f"Location: {scenario['location']}")
            if scenario.get("retry_after"):
                header_lines.append(f"Retry-After: {scenario['retry_after']}")
            headers.write_bytes(("\r\n".join(header_lines) + "\r\n\r\n").encode("iso-8859-1"))
        else:
            headers.write_bytes(b"")
        if scenario.get("write_body", True) and body is not None:
            body_path.write_bytes(body)
        cookie.write_bytes(b"")
        returncode = int(scenario.get("returncode", 0))
        stdout = str(status).encode("ascii") if status is not None else b""
        self.calls.append({"target_id": target_id, "url": url, "transport": transport, "command": command, "timeout": timeout})
        return subprocess.CompletedProcess(command, returncode, stdout=stdout, stderr=str(scenario.get("stderr", "")).encode("utf-8"))


def fixture_target(target_id: str = "fixture-page", url: str = "https://archivecraft.com/townhall/dungeons/") -> dict[str, str]:
    return {"target_id": target_id, "url": url}


def run_one_fixture(targets: list[dict[str, str]], scenarios: dict[str, list[dict[str, Any]]], *, max_attempts: int = MAX_ATTEMPTS) -> tuple[dict[str, Any], FixtureStub]:
    with tempfile.TemporaryDirectory(prefix=f"{BATCH_ID}-fixture-") as temp:
        paths = make_paths(Path(temp) / "runtime")
        stub = FixtureStub(scenarios, targets)
        original = subprocess.run
        subprocess.run = stub  # type: ignore[assignment]
        try:
            result = run_core(targets, paths, max_logical=len(targets), max_attempts=max_attempts, max_seconds=20, cadence_seconds=0)
            public = json.loads(paths.public.read_text(encoding="utf-8"))
            private = load_json(paths.report)
            private_raw_file_count = len(list(paths.raw.iterdir()))
            journal_line_count = len(paths.journal.read_text(encoding="utf-8").splitlines()) if paths.journal.exists() else 0
            request_body_caps = [item["request_body_cap"] for item in private.get("attempts", [])]
            return {"result": result, "public": public, "private_raw_file_count": private_raw_file_count, "journal_line_count": journal_line_count, "request_body_caps": request_body_caps}, stub
        finally:
            subprocess.run = original  # type: ignore[assignment]


def offline_fixtures() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    try:
        html = b'''<!doctype html><html><head><title>ArchiveCraft sample</title><link rel="stylesheet" href="/css/site.css"><style>.hero{background:url('/img/bg.png')}</style></head><body><img src="/img/hero.png" srcset="/img/hero-1.png 1x, https://cdn.example/hero-2.png 2x"><script src="/run.js"></script><form><input name="q"></form></body></html>'''
        one, stub = run_one_fixture([fixture_target()], {"fixture-page": [{"status": 200, "content_type": "text/html; charset=utf-8", "body": html}]})
        page = one["public"]["records"][0]
        assert page["valid"] is True and page["classification"] == "accepted_html"
        assert page["title"] == "ArchiveCraft sample" and len(page["dependencies"]) == 5
        assert len(page["image_links"]) == 1 and page["image_links"][0]["src"] == "https://archivecraft.com/img/hero.png"
        assert page["security"]["scripts_or_forms_executed"] is False and len(stub.calls) == 1
        assert "command" not in page and "headers_path" not in page and "cookie_path" not in page and "cookies" not in json.dumps(page)
        checks.append({"name": "static_html_dependency_inventory", "passed": True, "calls": len(stub.calls)})

        source_html = b'''<html><head><title>Dungeons source</title></head><body><figure><a href="https://imgur.com/gallery/promo?token=private"><img src="/wp-content/uploads/screenshots/alpha.jpg?download=1" alt="Alpha promo"></a><figcaption>Image source: captured by Wayback and shared via Imgur.</figcaption></figure><p>Materials sourced from Reddit and GitHub.</p><p>Source link: <a href="https://github.com/example/archive?auth=secret">repository</a>.</p><a href="/dungeons/index.xml">XML index</a></body></html>'''
        sourced, _ = run_one_fixture([fixture_target()], {"fixture-page": [{"status": 200, "content_type": "text/html", "body": source_html}]})
        source_page = sourced["public"]["records"][0]
        assert len(source_page["image_links"]) == 1
        assert source_page["image_links"][0]["src"] == "https://archivecraft.com/wp-content/uploads/screenshots/alpha.jpg"
        assert source_page["image_links"][0]["linked_image_url"] == "https://imgur.com/gallery/promo"
        assert source_page["image_links"][0]["caption"] == "Image source: captured by Wayback and shared via Imgur."
        assert any("Reddit and GitHub" in item["text"] for item in source_page["source_statements"])
        assert any("github.com/example/archive" in link for item in source_page["source_statements"] for link in item["links"])
        assert "/dungeons/index.xml" not in json.dumps(source_page["image_links"])
        checks.append({"name": "source_statements_image_links_captions_and_xml_boundary", "passed": True})

        redirect, stub = run_one_fixture([fixture_target()], {"fixture-page": [{"status": 301, "content_type": "text/html", "location": "https://www.example.invalid/next", "body": b"redirect"}]})
        assert redirect["public"]["records"][0]["classification"] == "redirect_not_followed" and len(stub.calls) == 1
        checks.append({"name": "redirect_recorded_without_follow", "passed": True, "calls": len(stub.calls)})

        plain, _ = run_one_fixture([fixture_target()], {"fixture-page": [{"status": 200, "content_type": "text/plain", "body": b"<html><title>fake</title></html>"}]})
        assert plain["public"]["records"][0]["classification"] == "non_html_content_type"
        checks.append({"name": "html_body_wrong_mime_rejected", "passed": True})

        soft, _ = run_one_fixture([fixture_target()], {"fixture-page": [{"status": 200, "content_type": "text/html", "body": b"<html><title>Not Found</title><h1>Page not found</h1></html>"}]})
        assert soft["public"]["records"][0]["classification"] == "soft404_suspect" and soft["public"]["records"][0]["valid"] is False
        checks.append({"name": "soft404_rejected", "passed": True})

        partial, stub = run_one_fixture([fixture_target()], {"fixture-page": [{"status": 200, "content_type": "text/html", "returncode": 63, "body": b"<html><title>partial prefix</title>"}]})
        assert partial["public"]["records"][0]["classification"] == "response_cap_exceeded" and partial["public"]["records"][0]["valid"] is False and len(stub.calls) == 1
        checks.append({"name": "curl63_html_prefix_rejected_as_incomplete", "passed": True, "calls": len(stub.calls)})

        fallback, stub = run_one_fixture([fixture_target()], {"fixture-page": [{"status": None, "returncode": 7, "body": b"", "write_body": False}, {"status": 200, "content_type": "text/html", "body": b"<html><title>Proxy success</title></html>"}]})
        assert fallback["public"]["records"][0]["valid"] is True and [call["transport"] for call in stub.calls] == ["direct", "proxy"]
        checks.append({"name": "transport_failure_one_process_proxy_fallback", "passed": True, "calls": len(stub.calls)})

        limited_targets = [fixture_target(f"fail-{index}", f"https://archivecraft.com/fail/{index}/") for index in range(3)]
        five_failure_scenarios = {item["target_id"]: [{"status": None, "returncode": 7, "body": b"", "write_body": False}, {"status": None, "returncode": 7, "body": b"", "write_body": False}] for item in limited_targets}
        limited, stub = run_one_fixture(limited_targets, five_failure_scenarios, max_attempts=10)
        assert limited["result"]["stop_reason"] == "transport_failure_limit" and limited["result"]["cooldown_not_before_utc"] and len(stub.calls) == 5
        assert limited["private_raw_file_count"] == 20 and limited["journal_line_count"] == 10
        checks.append({"name": "five_consecutive_transport_failures_stop_and_preserve_raw_tail", "passed": True, "calls": len(stub.calls), "private_raw_files": limited["private_raw_file_count"], "cooldown": limited["result"]["cooldown_not_before_utc"]})

        for status in (429, 503):
            throttled, stub = run_one_fixture([fixture_target()], {"fixture-page": [{"status": status, "content_type": "text/plain", "retry_after": "2", "body": b"slow"}]})
            assert throttled["result"]["stop_reason"] == f"endpoint_status_{status}" and throttled["result"]["cooldown_not_before_utc"] and len(stub.calls) == 1
            retry_record = datetime.fromisoformat(throttled["result"]["cooldown_not_before_utc"].replace("Z", "+00:00"))
            response_end = datetime.fromisoformat(throttled["public"]["records"][0]["request_finished_utc"].replace("Z", "+00:00"))
            assert (retry_record - response_end).total_seconds() >= MIN_COOLDOWN
        checks.append({"name": "429_503_immediate_stop_and_minimum_cooldown", "passed": True, "calls_each": 1})

        future = (utc_now() + timedelta(seconds=300)).strftime("%a, %d %b %Y %H:%M:%S GMT")
        parsed = retry_after_seconds(future)
        assert parsed is not None and parsed >= 298
        checks.append({"name": "retry_after_http_date_parsed", "passed": True, "seconds_at_least": parsed})

        with tempfile.TemporaryDirectory(prefix=f"{BATCH_ID}-cap-") as temp:
            paths = make_paths(Path(temp) / "runtime")
            paths.runtime.mkdir(parents=True)
            paths.private.mkdir()
            paths.raw.mkdir()
            stub = FixtureStub({"fixture-page": [{"status": 200, "content_type": "text/html", "returncode": 63, "body": b"123456789"}]}, [fixture_target()])
            original = subprocess.run
            subprocess.run = stub  # type: ignore[assignment]
            try:
                batch_start = time.monotonic()
                record, _ = run_attempt(fixture_target(), 1, False, None, batch_start, 7, paths, cadence_seconds=0, batch_seconds=20)
                assert record["response_cap_exceeded"] is True and record["transport_failed"] is False
                try:
                    curl_command(fixture_target(), use_proxy=False, headers=paths.raw / "h", body=paths.raw / "b", cookie=paths.raw / "c", max_time_seconds=1, remaining_body_bytes=0)
                except RuntimeError:
                    pass
                else:
                    raise AssertionError("zero remaining budget started a request")
            finally:
                subprocess.run = original  # type: ignore[assignment]
        checks.append({"name": "remaining_body_cap_and_zero_budget_refusal", "passed": True})
        original_page_cap = MAX_PAGE_BYTES
        try:
            globals()["MAX_PAGE_BYTES"] = 12
            target = fixture_target()
            cap_test, cap_stub = run_one_fixture([target], {"fixture-page": [{"status": None, "returncode": 7, "body": b"1234567"}, {"status": 200, "content_type": "text/html", "body": b"abcde"}]})
            assert [call["transport"] for call in cap_stub.calls] == ["direct", "proxy"]
            assert cap_test["request_body_caps"] == [12, 5]
            assert cap_test["result"]["total_body_bytes"] == 12 and cap_test["result"]["logical_count"] == 1
        finally:
            globals()["MAX_PAGE_BYTES"] = original_page_cap
        checks.append({"name": "per_page_budget_shared_with_proxy_fallback", "passed": True, "body_bytes": cap_test["result"]["total_body_bytes"]})
        result = {"schema": f"wow-recovery.{BATCH_ID}.offline-fixture.v1", "all_passed": True, "network_requests": 0, "stubbed_subprocess_calls": sum(int(item.get("calls", 0)) for item in checks), "checks": checks}
    except Exception as exc:
        result = {"schema": f"wow-recovery.{BATCH_ID}.offline-fixture.v1", "all_passed": False, "network_requests": 0, "checks": checks, "error": f"{type(exc).__name__}: {exc}"}
    require_disk("before fixture receipt")
    FIXTURE.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    require_disk("after fixture receipt")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline-fixtures", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--go", type=Path)
    args = parser.parse_args()
    if args.offline_fixtures:
        result = offline_fixtures()
        print(json.dumps({"all_passed": result.get("all_passed"), "network_requests": result.get("network_requests"), "checks": len(result.get("checks", []))}, ensure_ascii=False))
        return 0 if result.get("all_passed") else 1
    if args.execute:
        if args.go is None:
            raise SystemExit("--execute requires --go PATH")
        return execute(args.go)
    validate_plan()
    print(json.dumps({"prepared": True, "batch_id": BATCH_ID, "network_requests_at_prepare": 0}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
