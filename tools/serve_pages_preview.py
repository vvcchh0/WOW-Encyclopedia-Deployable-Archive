#!/usr/bin/env python3
"""Serve an exported archive locally under its recorded project prefix."""

from __future__ import annotations

import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    root = args.site.resolve(strict=True)
    provenance = json.loads((root / "export-provenance.json").read_text(encoding="utf-8"))
    prefix = provenance["base_path"]
    if not prefix.startswith("/") or not prefix.endswith("/") or ".." in prefix:
        parser.error("invalid project prefix in export provenance")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.respond(send_body=True)

        def do_HEAD(self) -> None:
            self.respond(send_body=False)

        def respond(self, *, send_body: bool) -> None:
            path = unquote(urlsplit(self.path).path)
            if path == "/":
                self.send_response(302)
                self.send_header("Location", prefix)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            if not path.startswith(prefix) or "\\" in path or "\x00" in path:
                self.send_error(404)
                return
            relative = path[len(prefix):] or "index.html"
            if ".." in relative.split("/"):
                self.send_error(404)
                return
            target = (root / relative).resolve()
            if not target.is_relative_to(root):
                self.send_error(404)
                return
            if target.is_dir():
                target = target / "index.html"
            try:
                body = target.read_bytes()
            except (OSError, ValueError):
                self.send_error(404)
                return
            mime = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            if mime.startswith("text/") or target.suffix in {".js", ".json"}:
                mime += "; charset=utf-8"
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if send_body:
                self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Archive preview: http://127.0.0.1:{server.server_port}{prefix}", flush=True)
    print(f"Site: {root}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
