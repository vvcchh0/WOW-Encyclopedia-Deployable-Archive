# v33 preparation boundary

This directory owns the v33 preparation code only. It does not contain an
accepted map or an export output yet. `build_pages_v33.py` refuses to prepare
until the root-owned
`research/continuous-recovery-20261018/publication/root-v33-source-receipts-manifest-r2.json`
exists and is accepted.

The manifest contract is intentionally explicit:

```json
{
  "schema": "wow-recovery.integration.v33-source-receipts-manifest.v1",
  "accepted": true,
  "source15_manifest": {"path": ".scratch/offline-navigation-20261015-v15/build-manifest.json", "sha256": "..."},
  "original_manifest": {"path": "offline/build-manifest.json", "sha256": "..."},
  "new_images": 0,
  "image_bytes": 0,
  "new_primary_images": 0,
  "new_supplement_images": 0,
  "network_requests": 0,
  "export_executed": false,
  "batches": [
    {
      "id": "popup24-batch1",
      "role": "primary",
      "expected_count": 0,
      "expected_bytes": 0,
      "source_acceptance": {"path": "research/.../root-...-source-acceptance.json", "sha256": "..."},
      "public_copy_acceptance": {"path": "research/.../root-...-public-copy-acceptance.json", "sha256": "..."}
    }
  ]
}
```

The root manifest must list every batch and exact aggregate count. A batch is
classified by its declared role, then checked against its URL host: the two
canonical WoW hosts are primary; `www.wowarmory.com`,
`armory.wow-europe.com`, and `www.blizzard.com` are explicit supplements.
Every public copy is checked against both receipts and its exact bytes, CDX
digest, MIME/magic, and image decoding. Pending network folders are never
searched.

The old v32 primary/supplement map closure (439 overlays) is passed through
unchanged. The v33 maps contain only the manifest delta. The impact estimate
uses all old and new validated origins and reports navigation `missing.html`
href recovery separately from `missing-image.svg` marker recovery. Neither is
a browser acceptance result.

After the root source manifest is accepted, prepare once with:

```powershell
& "$env:CODEX_PRIMARY_PYTHON" -X utf8 research/continuous-recovery-20261018/integration/v33/build_pages_v33.py --prepare --preflight
```

The runner is a separate one-shot path. It requires root's accepted input
gate and explicit `--go --root-export-go`; no v33 export is authorized by this
directory's preparation code alone.
