#!/usr/bin/env python3
"""Plain static project-prefix server for GitHub Pages browser QA.

It only strips the configured hosting prefix before delegating to
SimpleHTTPRequestHandler.  It does not implement source-route aliases,
custom MIME selection, or offline_mirror behavior.
"""
from __future__ import annotations

import argparse
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


class PrefixHandler(SimpleHTTPRequestHandler):
    root: Path
    prefix: str

    def _relative(self, request_path: str) -> str | None:
        path = urlsplit(request_path).path
        if path == self.prefix[:-1]:
            path += "/"
        if not path.startswith(self.prefix):
            return None
        return unquote(path[len(self.prefix) :]).lstrip("/")

    def translate_path(self, path: str) -> str:
        relative = self._relative(path)
        if relative is None:
            return str(self.root / "__outside_project_prefix__")
        candidate = (self.root / relative).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError:
            return str(self.root / "__outside_project_prefix__")
        return str(candidate)

    def do_GET(self) -> None:  # noqa: N802
        if self._relative(self.path) is None:
            self.send_error(404, "outside project prefix")
            return
        super().do_GET()

    def do_HEAD(self) -> None:  # noqa: N802
        if self._relative(self.path) is None:
            self.send_error(404, "outside project prefix")
            return
        super().do_HEAD()

    def send_error(self, code: int, message: str | None = None, explain: str | None = None) -> None:
        """Serve the exported Pages 404 body while retaining HTTP 404.

        GitHub Pages supplies the static ``404.html`` body for an unknown
        project file.  The body contains the route-map client marker; the
        browser can then repair a source URL while the initial response still
        remains an honest 404.  No source-route or MIME lookup is performed
        here.
        """
        if code == 404 and self._relative(self.path) is not None:
            error_page = self.root / "404.html"
            if error_page.is_file():
                body = error_page.read_bytes()
                self.send_response(404, message or "File not found")
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(body)
                return
        super().send_error(code, message, explain)

    def log_message(self, format: str, *args: object) -> None:
        print("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format % args), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--prefix", default="/WOW-Encyclopedia-Deployable-Archive/")
    parser.add_argument("--port", type=int, default=8879)
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        raise SystemExit(f"static root is not a directory: {root}")
    prefix = "/" + args.prefix.strip("/") + "/"
    PrefixHandler.root = root
    PrefixHandler.prefix = prefix
    server = ThreadingHTTPServer(("127.0.0.1", args.port), PrefixHandler)
    print(f"READY root={root} prefix={prefix} port={args.port} pid={os.getpid()}", flush=True)
    try:
        server.serve_forever(poll_interval=0.2)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
