# Portable archive checker

`portable_check.py` independently verifies a root-accepted portable archive and then starts the packaged preview server from a fresh extraction. It does not create or modify the ZIP, package report, accepted export, or browser acceptance. Its only production writes are a new extraction under `.scratch/portable smoke 20261022 <version>` and the new receipt named by the root-supplied config. Existing paths are never replaced.

## Config contract

The config has schema `wow-portable-check-config/v1` and these required fields:

```json
{
  "schema": "wow-portable-check-config/v1",
  "version": "v54",
  "accepted_site": "<repo-relative accepted static site>",
  "archive": "<repo-relative ZIP path>",
  "package_report": "<repo-relative package report path>",
  "export": {"path": "<repo-relative export acceptance JSON>"},
  "root_browser_acceptance": {"path": "<repo-relative final browser acceptance JSON>"},
  "output_receipt": "<new repo-relative receipt path>",
  "smoke_paths": [
    {
      "url_path": "<project-prefix plus URL-encoded site_relative>",
      "site_relative": "<path relative to accepted_site>",
      "expected_mime": "text/html; charset=utf-8",
      "methods": ["GET", "HEAD"]
    }
  ]
}
```

All input and output paths must resolve inside this repository. `accepted_site` must equal each acceptance record's `local_site` after repository-relative normalization. The export acceptance must have `accepted: true`, `actual_files` equal to the complete accepted-site file count, and `export_provenance_sha256` equal to the SHA-256 of `accepted_site/export-provenance.json`. Its listed `objects` (the export receipt may list only added/changed objects) are each checked against the accepted site; independently, the helper enumerates the complete accepted site and checks every packaged site member. Export object paths are relative to `accepted_site` and use canonical slash separators.

The root record must use schema `wow-root-final-browser-acceptance/v1`, have `accepted: true`, the same `local_site` and provenance SHA, empty `external_requests` and `page_errors`, `asset_fulfillments: 0`, and `pages`/`evidence` arrays. Each evidence entry's path and SHA-256 are checked against a regular local file.

Each `smoke_paths` item must map exactly from `url_path` to `site_relative` under the project's `base_path`, with no query, fragment, or external origin. Both GET and HEAD are required. The helper checks bytes, SHA-256, content length, MIME, and project-prefix handling. The root should select every changed/new object plus representative existing encyclopedia pages, Deadmines resources, Flash/Ruffle fallback, talent data, and launch entry points; the helper does not infer that list.

The ZIP must exactly contain all accepted site files under `site/`, current `tools/serve_pages_preview.py` and `NOTICE.md`, and the four packager-generated files. Every member is streamed for CRC/SHA/length and compared with the accepted source, `FILE_SHA256SUMS.txt`, package metadata, and package report. The sidecar `<archive>.sha256` is checked too. Traversal, absolute paths, case collisions, duplicate members, directory entries, symlinks/reparse entries, encrypted members, and known private/raw evidence paths are rejected.

The checker requires at least 11,005,853,696 free bytes on D: before the batch, before extraction and any member of at least 16 MiB, after the loopback smoke, before the receipt write, and after that write. It extracts only to the fixed versioned path when that path does not already exist. The packaged server is launched as a child process on 127.0.0.1 with a random port, must announce readiness within 60 seconds, and is always terminated by this helper. No external network access is used.

## Offline validation

Run `python -B -m unittest discover -s research/continuous-recovery-20261022/publication/portable-check -p 'test_*.py' -v` from the repository root. The service fixture creates no ZIP and only uses a temporary directory and loopback HTTP. Unit tests use synthetic receipt-shaped JSON in a temporary directory; they do not create or consume a production acceptance receipt.

For the eventual authorized local check, use `python research/continuous-recovery-20261022/publication/portable-check/portable_check.py --config <root-supplied-config.json>` only after the root supplies the real final ZIP, package report, acceptance records, and exact smoke list.

The first production check exposed a list/index mismatch at extraction: the independently verified member records were a JSON list, while the extraction helper expected a dictionary. The root corrected that interface, retained the first partial extraction, and added an actual small-ZIP extraction test with a changed-hash rejection. All seven local tests then passed. The archive and accepted site were unchanged; the production check was restarted with the corrected helper.
