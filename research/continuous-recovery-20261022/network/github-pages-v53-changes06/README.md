# GitHub Pages v53 six-object verification

This batch is prepared for the six fixed objects in `object-manifest.json`, from Pages commit `f068318efedc86b6e7572213482f702b308ae362` / Actions run `39758597461`. The local expected bodies are under `.scratch/pages-resources-20261022-v53/` and are pinned by exact byte length and SHA-256.

Preparation and offline validation:

```powershell
python -X utf8 research/continuous-recovery-20261022/network/github-pages-v53-changes06/verify_pages_v53_changes06.py --offline-validate
```

This writes `offline-validation.json` and `input-bindings.json` and makes no network requests. The only network entry point is a single invocation after root reviews and writes a matching GO:

```powershell
python -X utf8 research/continuous-recovery-20261022/network/github-pages-v53-changes06/verify_pages_v53_changes06.py --execute --go <root-GO-json-path>
```

The GO must contain `accepted: true`, `root_go: true`, `batch_id`, future `valid_until`, and exact values for `plan_sha256`, `wrapper_sha256`, `object_manifest_sha256`, `offline_validation_sha256`, `input_bindings_sha256`, `transport_runner_sha256`, `source_build_receipt_sha256`, and `object_set_sha256`. A failed or expired binding creates no runtime and sends no request.

The authorized runner is bounded to 6 logical objects, 12 HTTP attempts, 400 seconds, 32 MiB total response bodies, 16 MiB per object, 6.2-second start spacing, and a disk free-space floor of 11,005,853,696 bytes. It reuses the hash-pinned `archivecraft_dungeons01.py` transport, direct first; only a transfer failure permits one process-local proxy fallback. TLS stays enabled, redirects and automatic retries stay off. HTTP 429/503 and five consecutive transfer failures stop the batch with a cooldown of at least 120 seconds. Raw HTTP headers, response bodies, and cookie jars are private under `runtime/private/raw/`; only curated size/hash/status match metadata goes in `runtime/object-match-summary.json`.
