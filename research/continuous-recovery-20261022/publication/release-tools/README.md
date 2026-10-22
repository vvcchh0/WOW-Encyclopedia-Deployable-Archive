# GitHub release draft create/upload helper

This is a parameterized create-and-upload wrapper for a root-accepted portable archive. It does not create an archive, modify Git, replace a tag or asset, or publish a release. The public publish step remains a separate root-controlled action.

`create_upload_release.py` accepts one root-authored JSON file matching `config.schema.json`. Paths must resolve to regular, non-symlink files inside the repository. The package checker receipt must have schema `wow-portable-check-receipt/v1`, `status: "accepted"`, `network_performed: false`, the configured version, and an archive record binding the exact archive path, SHA-256, byte length, and sidecar SHA-256/length. The archive sidecar must contain the matching SHA-256 line. The helper uploads exactly the archive, its `.sha256` sidecar, and `NOTICE.md`.

Before any GitHub CLI operation, the helper requires the current branch, `HEAD`, `origin/main`, and configured `source_head` to match, requires an empty Git status, and checks that `origin` names the configured GitHub repository. A pre-existing remote tag or release is never adopted without a saved local intent whose random marker is present in the draft. The intent is written before a draft-creation request so an interrupted run can inspect and recover that same draft. Before any retry after an ambiguous write, the helper reads back the release and tag; it does not retry a create if the owned draft is visible or a tag exists. Asset uploads omit `--clobber`; a readback must show the expected asset digest, size, and uploaded state. A later run can recover only from the matching intent and verifies the current remote draft against its saved receipt.

The helper starts `gh` processes at least 5.2 seconds apart, within a hard cutoff of `2026-10-22T14:51:33Z`. Each subprocess timeout is capped to finish at least one second before that cutoff; if less than one second remains, it refuses to start another process. Each operation tries the normal direct environment first. Only a classified transport failure permits one retry through process-scoped `127.0.0.1:7890`; HTTP errors do not trigger proxy fallback. TLS certificate verification remains enabled. The spacing applies to starts of `gh` CLI processes; it cannot schedule or certify spacing between internal REST requests made by a single `gh` process. No custom API transport is used.

Run only after the root supplies a concrete config and authorization for the release operation:

```powershell
python -B research/continuous-recovery-20261022/publication/release-tools/create_upload_release.py --config <root-config.json> --execute
```

The helper writes a new `create-upload-intent.json` and, after all three remote assets pass readback, `create-upload-receipt.json` under `output_dir`. The success receipt records each `gh` invocation's UTC start, operation type, direct/proxy mode, timeout, and exit code without recording command output or credentials. Those events cover `gh` process starts only; they do not observe its internal REST subrequests. Keep the output directory ignored or outside a later clean-checkout run so the helper's local Git cleanliness guard remains true. A rejected or interrupted run preserves its intent for review. Do not delete it or issue another request automatically; compare the intent with the remote draft first. This preparation task has made no `gh` calls and has not created a release or uploaded anything.

Offline validation:

```powershell
python -B -m unittest discover -s research/continuous-recovery-20261022/publication/release-tools -p 'test_*.py' -v
```
