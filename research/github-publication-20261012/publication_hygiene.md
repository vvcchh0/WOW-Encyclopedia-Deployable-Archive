# Public publication hygiene check (2026-10-12)

Read-only, offline scan. No ZIP payload was extracted or changed; no matched secret value is printed.

Scanned 6 artifact ZIP central directories without extraction. Top-level directories, research coverage, and member-name classifications are in JSON.
Streamed bounded ZIP metadata members (JSON/headers/log/Markdown/Python-like, excluding HTML/CSS/JS/XML and CDX/prefix members): 669,842,264 bytes; bound/truncation flags are retained per ZIP.

## Metadata scan

Scanned 87 selected metadata/text files (112,355,200 bytes) under the recorded roots and key final reports. Large skipped files: 0; read errors: 0.
Credential-shaped value matches: 0 (likely fixed test-fixture subset: 0); source authorization fields without values: 5; source Cookie/Set-Cookie fields: 0; ZIP metadata value matches: 0, Cookie fields: 11345.
Absolute-path/email-shaped matches: 86. Locations and line numbers are in JSON; values are intentionally omitted.

Cookie and Set-Cookie metadata are classified as ambiguous: an Archive replay cookie can be anonymous replay infrastructure state, but this scan cannot prove it is not a login/session cookie. Human review is required for every occurrence before publication.

## ZIP member-name scan

Only central-directory names were inspected. Credential stores, browser profiles, environment files, and personal screenshot names are reported by category without payload extraction. Public historical screenshot directories and ordinary cookie/password UI assets are separated from those categories.

## Limits

Binary assets, nested ZIP payloads, and offline historical HTML/CSS/JS were not content-scanned. This report is a bounded hygiene inventory, not a proof that publication is safe; nonzero credential-shaped findings or ambiguous cookies require manual review/redaction.

See `publication_hygiene.json` for exact scan roots, counts, ZIP member-name samples, locations, hashes, skipped files, and limits.
