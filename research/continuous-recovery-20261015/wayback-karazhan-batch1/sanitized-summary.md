# Karazhan Wayback TLS unknown recheck — batch 1

This bounded serial recheck selected the first 30 distinct original URLs whose prior category was `transport_error` and whose prior source statuses were empty.

Input report SHA-256: `31368c5ecda7a7aefb99a7736c8a7b0c58ecb04ee484897259011eada910a05a`; TLS diagnostic SHA-256: `9089af2e0e51d2590c214e8c30fbd7b7e2e4f12d0e3efc1d0843b3d52b3bbd5e`.
Request window finished: `2026-10-15T06:59:35.213520+00:00`; report updated offline: `2026-10-15T07:03:51.917024+00:00`.
Transport after the first target: `proxy`; source requests: `26`; transport attempts: `26`; failed attempts: `12`; source HTTP responses: `14`; body bytes: `65932`.
Categories: `not_archived` 14, `not_requested` 5, `transport_error` 11.
Disk free before/after: `31536787456` / `31517470720` bytes; stop reason: `five_consecutive_tls_or_transport_failures`.

Actual Memento values below come only from response `Memento-Datetime` headers. The replay request hint is never used as an actual capture timestamp.

| # | target | category | HTTP | actual Memento | bytes | decoded size | SHA-256 | unrequested reason |
|---:|---|---|---:|---|---:|---|---|---|
| 1 | `thumb-ss36` | `not_archived` | 404 | `` | 4712 | `None` | `c60331940054c5a3e8c5f4a72fe2080daf5cbd5008e92edeadbf08293bf55961` | `` |
| 2 | `thumb-ss37` | `not_archived` | 404 | `` | 4712 | `None` | `7043e8180f2bdf5ec773cb3f0031adf63b45c259fc00b270fd68bfc853cd2313` | `` |
| 3 | `full-ss38` | `not_archived` | 404 | `` | 4706 | `None` | `094105c4424851168735568f5f3a9773a4f31d30947bae9777884961a242574a` | `` |
| 4 | `thumb-ss38` | `not_archived` | 404 | `` | 4712 | `None` | `06c78a193c83f9d520094a6bd0eae9504405f5af91a1c1c741e7ba11ebaef5d6` | `` |
| 5 | `full-ss39` | `not_archived` | 404 | `` | 4706 | `None` | `cc7e76ce190c592c17fce7ab775949529b7af1cadb40a86f02285a8dea5b2c07` | `` |
| 6 | `thumb-ss39` | `not_archived` | 404 | `` | 4712 | `None` | `5fc6011808969619e11fdb7925ecd40221ebb7329b218eb05454160a10b8ec3b` | `` |
| 7 | `full-ss40` | `not_archived` | 404 | `` | 4706 | `None` | `8afa07e902a6bc2f959e02ba709076cd41995ac843527bf7d48044d27a7dc503` | `` |
| 8 | `thumb-ss40` | `not_archived` | 404 | `` | 4712 | `None` | `e70552a5082f718fa152aa8b9bce0e758119e8cb1e5e725aab76f00432dc7a85` | `` |
| 9 | `full-ss41` | `not_archived` | 404 | `` | 4706 | `None` | `3c74854bcae90fa0c0b52a45aa2286de5f121d9573d87e82d44fe58e49c63436` | `` |
| 10 | `thumb-ss41` | `not_archived` | 404 | `` | 4712 | `None` | `3834993afffcb051aa2515c4c29feb270c44041857db6e904e83c4ebbcf995e4` | `` |
| 11 | `full-ss42` | `transport_error` |  | `` | 0 | `None` | `` | `` |
| 12 | `thumb-ss42` | `transport_error` |  | `` | 0 | `None` | `` | `` |
| 13 | `full-ss43` | `not_archived` | 404 | `` | 4706 | `None` | `3fb455c3b0f6ddac599d7e78c0d6e579ea0e70269e34716449deb520f3c4a35c` | `` |
| 14 | `thumb-ss43` | `transport_error` |  | `` | 0 | `None` | `` | `` |
| 15 | `full-ss44` | `transport_error` |  | `` | 0 | `None` | `` | `` |
| 16 | `thumb-ss44` | `transport_error` |  | `` | 0 | `None` | `` | `` |
| 17 | `full-ss45` | `not_archived` | 404 | `` | 4706 | `None` | `0306cf9653812b791f2de19764e02ba155584b80d3a34f4af19f4c56d7d03761` | `` |
| 18 | `thumb-ss45` | `not_archived` | 404 | `` | 4712 | `None` | `311e7ef5de15ae4946e05b51c301ce5ba0a1c16d63e33a7c16eb260ef3eef162` | `` |
| 19 | `full-ss46` | `transport_error` |  | `` | 0 | `None` | `` | `` |
| 20 | `thumb-ss46` | `not_archived` | 404 | `` | 4712 | `None` | `04b5592d2f3025128d6e1cff18bc7c8b50e22de2aa799c571af0e0667ed61754` | `` |
| 21 | `full-ss47` | `transport_error` |  | `` | 0 | `None` | `` | `` |
| 22 | `thumb-ss47` | `transport_error` |  | `` | 0 | `None` | `` | `` |
| 23 | `full-ss48` | `transport_error` |  | `` | 0 | `None` | `` | `` |
| 24 | `thumb-ss48` | `transport_error` |  | `` | 0 | `None` | `` | `` |
| 25 | `full-ss49` | `transport_error` |  | `` | 0 | `None` | `` | `` |
| 26 | `thumb-ss49` | `not_requested` |  | `` | 0 | `None` | `` | `five_consecutive_tls_or_transport_failures` |
| 27 | `full-ss50` | `not_requested` |  | `` | 0 | `None` | `` | `five_consecutive_tls_or_transport_failures` |
| 28 | `thumb-ss50` | `not_requested` |  | `` | 0 | `None` | `` | `five_consecutive_tls_or_transport_failures` |
| 29 | `full-ss51` | `not_requested` |  | `` | 0 | `None` | `` | `five_consecutive_tls_or_transport_failures` |
| 30 | `thumb-ss51` | `not_requested` |  | `` | 0 | `None` | `` | `five_consecutive_tls_or_transport_failures` |

Valid image bodies, if any, are retained under `raw/` with their headers, trace, and digest evidence. Source mapping suggestions are recorded for review; no entity was copied into production or the offline mirror.
