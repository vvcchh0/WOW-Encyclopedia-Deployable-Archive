#!/usr/bin/env python3
"""Serve an exported archive locally under its recorded project prefix."""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
import webbrowser


def _audio_range(value: str, size: int) -> tuple[int, int] | None:
    """Parse one satisfiable byte range for a local media response."""

    match = re.fullmatch(r"bytes=(\d*)-(\d*)", value.strip())
    if match is None or size <= 0:
        return None
    first, last = match.groups()
    if len(first) > 20 or len(last) > 20:
        return None
    if not first:
        if not last or int(last) == 0:
            return None
        return max(0, size - int(last)), size - 1
    start = int(first)
    end = min(int(last), size - 1) if last else size - 1
    return (start, end) if start <= end and start < size else None


def _safe_route_path(value: object, prefix: str) -> str | None:
    """Return a local route path only when it stays inside ``prefix``."""

    if not isinstance(value, str) or not value:
        return None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        return None
    path = parsed.path
    if "\\" in path or "\x00" in path or not path.startswith(prefix):
        return None
    relative = path[len(prefix):]
    parts = relative.split("/") if relative else []
    if parts and parts[-1] == "":
        parts.pop()
    if any(part in {".", "..", ""} for part in parts):
        return None
    return path


def _safe_logical_path(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        return None
    path = parsed.path
    if "\\" in path or "\x00" in path or not path.startswith("/"):
        return None
    parts = path[1:].split("/") if path != "/" else []
    if parts and parts[-1] == "":
        parts.pop()
    if any(part in {".", "..", ""} for part in parts):
        return None
    return path


def _load_route_map(root: Path, prefix: str) -> dict[str, str]:
    """Load only exact, existing, same-prefix route-map targets."""

    route_map_path = root / "__offline" / "route-map.json"
    try:
        data = json.loads(route_map_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict) or data.get("base_path") != prefix:
        return {}
    result: dict[str, str] = {}
    for section in ("routes", "aliases"):
        entries = data.get(section)
        if not isinstance(entries, dict):
            continue
        for source, target in entries.items():
            logical = _safe_logical_path(source)
            target_path = _safe_route_path(target, prefix)
            if logical is None or target_path is None:
                continue
            relative = target_path[len(prefix):] or "index.html"
            candidate = (root / relative).resolve()
            if not candidate.is_relative_to(root) or not candidate.is_file():
                continue
            result.setdefault(logical, target_path)
    return result


def _safe_target(root: Path, relative: str) -> Path | None:
    if not relative or relative.startswith("/") or "\\" in relative or "\x00" in relative:
        return None
    parts = relative.split("/")
    if parts and parts[-1] == "":
        parts.pop()
    if any(part in {".", "..", ""} for part in parts):
        return None
    if not parts:
        return None
    candidate = (root / "/".join(parts)).resolve()
    if not candidate.is_relative_to(root) or candidate.is_symlink():
        return None
    return candidate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="open the bound loopback URL in the default browser",
    )
    args = parser.parse_args()
    root = args.site.resolve(strict=True)
    provenance = json.loads((root / "export-provenance.json").read_text(encoding="utf-8"))
    prefix = provenance["base_path"]
    if not prefix.startswith("/") or not prefix.endswith("/") or ".." in prefix:
        parser.error("invalid project prefix in export provenance")
    route_map = _load_route_map(root, prefix)

    class Handler(BaseHTTPRequestHandler):
        def _redirect(self, path: str, query: str) -> None:
            location = path + (("?" + query) if query else "")
            self.send_response(302)
            self.send_header("Location", location)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def _serve_file(self, target: Path, *, status: int, send_body: bool) -> None:
            try:
                size = target.stat().st_size
            except (OSError, ValueError):
                self.send_error(404)
                return
            mime = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            is_audio = target.suffix.lower() == ".mp3" and status == 200
            if is_audio:
                mime = "audio/mpeg"
            if mime.startswith("text/") or target.suffix in {".js", ".json"}:
                mime += "; charset=utf-8"
            start, end = 0, size - 1
            range_header = self.headers.get("Range") if is_audio and send_body else None
            if range_header:
                selected = _audio_range(range_header, size)
                if selected is None:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                start, end = selected
                status = 206
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(end - start + 1))
            if is_audio:
                self.send_header("Accept-Ranges", "bytes")
            if status == 206:
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if send_body:
                try:
                    with target.open("rb") as source:
                        source.seek(start)
                        remaining = end - start + 1
                        while remaining:
                            chunk = source.read(min(256 * 1024, remaining))
                            if not chunk:
                                break
                            self.wfile.write(chunk)
                            remaining -= len(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    pass  # Browsers cancel earlier media ranges when seeking.

        def do_GET(self) -> None:
            self.respond(send_body=True)

        def do_HEAD(self) -> None:
            self.respond(send_body=False)

        def respond(self, *, send_body: bool) -> None:
            parsed = urlsplit(self.path)
            path = unquote(parsed.path)
            query = parsed.query
            if path == "/":
                self._redirect(prefix, query)
                return
            prefix_without_slash = prefix.rstrip("/")
            if path == prefix_without_slash:
                self._redirect(prefix, query)
                return
            if not path.startswith(prefix) or "\\" in path or "\x00" in path:
                self.send_error(404)
                return
            relative = path[len(prefix):] or "index.html"
            target = _safe_target(root, relative)
            if target is None:
                self.send_error(404)
                return
            if target.is_dir():
                if not path.endswith("/"):
                    self._redirect(path + "/", query)
                    return
                target = target / "index.html"
            if target.is_file():
                self._serve_file(target, status=200, send_body=send_body)
                return

            logical = "/" + relative
            mapped = route_map.get(logical)
            if mapped is not None:
                self._redirect(mapped, query)
                return

            missing = root / "404.html"
            if missing.is_file() and not missing.is_symlink():
                self._serve_file(missing, status=404, send_body=send_body)
                return
            self.send_error(404)

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    browser_url = f"http://127.0.0.1:{server.server_port}{prefix}"
    print(f"Archive preview: {browser_url}", flush=True)
    print(f"Site: {root}", flush=True)
    if args.open_browser:
        webbrowser.open(browser_url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
