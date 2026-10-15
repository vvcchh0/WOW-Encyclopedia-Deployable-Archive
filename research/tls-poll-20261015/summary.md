# Wayback TLS poll — 2026-10-15

This record covers the known JPEG control target and preserves CONNECT status separately from source HTTP status.

Target: `https://web.archive.org/web/20080512212653id_/http://www.worldofwarcraft.com/info/dungeons/images/karazhan/thumbs/ss2-thumb.jpg`
Expected payload: 3347 bytes, JPEG 150x110, SHA-256 `45936113efa432f3c8188445ae255108c2af3d06fecf902202f0611068a74a11`.
Rounds recorded: 4; source requests: 6/12; automatic redirects: 0; availability: `ready`.

## Round 1

Ready: `True`; requests: 2.
- `target` via `direct`: outcome `tcp_or_timeout_failed`, CONNECT `None`, source HTTP `None`, decode `False`, bytes `0`, ready `False`, redirects `0`. Raw evidence: `raw\round1-target-direct-curl.trace.txt`.
- `target` via `proxy`: outcome `source_http`, CONNECT `200`, source HTTP `200`, decode `True`, bytes `3347`, ready `True`, redirects `0`. Raw evidence: `raw\round1-target-proxy-curl.trace.txt`.
- DNS `web.archive.org` via `system_getaddrinfo`: addresses `['108.160.169.55']`, error `None`.
- Offline parser fixtures: `True`.

## Round 2

Ready: `True`; requests: 1.
- `target` via `proxy`: outcome `source_http`, CONNECT `200`, source HTTP `200`, decode `True`, bytes `3347`, ready `True`, redirects `0`. Raw evidence: `raw\round2-target-proxy-curl.trace.txt`.
- DNS `web.archive.org` via `system_getaddrinfo`: addresses `['108.160.169.55']`, error `None`.
- Offline parser fixtures: `True`.

## Round 3

Ready: `True`; requests: 1.
- `target` via `proxy`: outcome `source_http`, CONNECT `200`, source HTTP `200`, decode `True`, bytes `3347`, ready `True`, redirects `0`. Raw evidence: `raw\round3-target-proxy-curl.trace.txt`.
- DNS `web.archive.org` via `system_getaddrinfo`: addresses `['168.143.162.58']`, error `None`.
- Offline parser fixtures: `True`.

## Round 4

Ready: `True`; requests: 2.
- `target` via `direct`: outcome `tcp_or_timeout_failed`, CONNECT `None`, source HTTP `None`, decode `False`, bytes `0`, ready `False`, redirects `0`. Raw evidence: `raw\round4-target-direct-curl.trace.txt`.
- `target` via `proxy`: outcome `source_http`, CONNECT `200`, source HTTP `200`, decode `True`, bytes `3347`, ready `True`, redirects `0`. Raw evidence: `raw\round4-target-proxy-curl.trace.txt`.
- DNS `web.archive.org` via `system_getaddrinfo`: addresses `['185.60.216.11']`, error `None`.
- Offline parser fixtures: `True`.

Raw headers, bodies, stderr, curl traces and metrics are local ignored evidence under `raw/`; summary fields are redacted metadata.
A proxy `200 Connection established` is never counted as source HTTP 200. Only source HTTP 200 plus exact payload hash, byte length and image decode is `ready`.
