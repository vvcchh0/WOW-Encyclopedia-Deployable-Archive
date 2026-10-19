# gallery-late-rest10b adapter diff

- Frozen prior packet driver: `research/continuous-recovery-20261019/network/gallery-late-rest10a/gallery_late_rest10a_driver_v1.py` SHA256 `ccd1b2b9810d274545e20f99940c1cb1a32c79c07bdb95a83408ef0c07df6541` (60752 bytes).
- New packet driver: `research/continuous-recovery-20261019/network/gallery-late-rest10b/gallery_late_rest10b_driver_v1.py` SHA256 `db9370609c57715d91b98870552dbf37d86b8970ab9e0ea9abbc7ec7b91e153b` (60804 bytes).
- Full unified diff: `research/continuous-recovery-20261019/network/gallery-late-rest10b/driver-diff.patch` SHA256 `010f8c908f4aa33f43f468cfe0f634a68bf2de49357ddb1dd42f3f238be8a5b7`.

Contract changes:

- Batch identity and User-Agent are packet-local `REST10B`; the target set is exactly registry ranks 14–23.
- The latest global source binding is the accepted `root-gallery-late-rest10a-source-acceptance.json` tail-zero receipt; old news20f is not used as the latest source.
- All transport/parser/identity/row-projection helpers and all 10a caps remain unchanged: 24 attempts/requests, 900 seconds, 32 MiB total, 8 MiB/entity, direct then proxy, TLS, no redirects, no auto-pagination, 5.25s dispatch/5.0s request-start, disk floor, 429/503 and five-failure stop/cooldown.
- CDX-only remains enforced; no payload replay or image acceptance is performed in this packet.

Changed function bodies:

- `fixture` changed for packet-local target/schema/binding validation.
- `plan_for_run` changed for packet-local target/schema/binding validation.
- `validate_inputs` changed for packet-local target/schema/binding validation.

Unchanged function bodies:

- `_remaining_clamp` unchanged by AST source hash.
- `_restart_last_dispatch` unchanged by AST source hash.
- `_schedule_next` unchanged by AST source hash.
- `canonical_query_url` unchanged by AST source hash.
- `cf` unchanged by AST source hash.
- `execute` unchanged by AST source hash.
- `free_bytes` unchanged by AST source hash.
- `headers` unchanged by AST source hash.
- `iso` unchanged by AST source hash.
- `main` unchanged by AST source hash.
- `now` unchanged by AST source hash.
- `parse_cdx` unchanged by AST source hash.
- `parse_iso` unchanged by AST source hash.
- `phase` unchanged by AST source hash.
- `project_rows` unchanged by AST source hash.
- `public_attempt` unchanged by AST source hash.
- `read_json` unchanged by AST source hash.
- `rel` unchanged by AST source hash.
- `request` unchanged by AST source hash.
- `same_origin` unchanged by AST source hash.
- `sha` unchanged by AST source hash.
- `status` unchanged by AST source hash.
- `write_json` unchanged by AST source hash.

No network authorization is embedded in this prepared packet.
