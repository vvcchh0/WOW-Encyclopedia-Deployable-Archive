# PvP flash-rewards exact replay — 2026-10-15

Target: `http://www.worldofwarcraft.com/pvp/flash-rewards/`; requested capture `20070115223911`; original `http://www.worldofwarcraft.com:80/pvp/flash-rewards/`.
Exact CDX row: HTTP `200`, MIME `text/html`, length `4806`, digest `P5IHZI3MCNXDRAM2BVGCTXD4WXU7VXNA`.
Requests: `2/2`; automatic redirects: `0`; stop: `completed`.
Result: `ready` via `proxy`.

- `direct`: outcome `tcp_or_timeout_failed`, CONNECT `None`, source HTTP `None`, TLS `0.0`, body `0` bytes, Memento `None`, CDX digest `None`; raw body `raw\direct.body`.
- `proxy`: outcome `source_http`, CONNECT `200`, source HTTP `200`, TLS `0.917338`, body `20761` bytes, Memento `20070115223911`, CDX digest `P5IHZI3MCNXDRAM2BVGCTXD4WXU7VXNA`; raw body `raw\proxy.body`.

Content classification: `pvp_html_page`; title `World of Warcraft PvP Mini Site`; PvP markers `['pvp']`; target markers `['flash']`; soft-404 marker `None`.
Checks: `{"body_length_matches_cdx": false, "cdx_digest_matches": true, "memento_matches_requested": true, "memento_present": true, "mime_is_html": true, "no_automatic_redirect": true, "not_soft404": true, "real_http_200": true, "real_pvp_page": true}`; CDX length is retained as metadata and is not used as the content gate when the exact CDX digest matches.

Raw body is retained under `raw/`; headers, traces, stderr and metrics are local ignored evidence.
