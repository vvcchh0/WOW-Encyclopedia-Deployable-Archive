# Git-only publication clone smoke validation

- Requested commit: `b8d655ca51c4e4f73101e8e774eb46b37bda9c4f`
- Checked-out commit: `b8d655ca51c4e4f73101e8e774eb46b37bda9c4f` (clean=True)
- `core.longpaths`: `true`
- Manifest SHA-256: `397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459` (73067980 bytes)
- Manifest records/routes: 8304/8304
- File verification: 8304 hashed; missing=0, nonregular=0, unsafe/duplicate=0, hash mismatches=0, length mismatches=0; pass=True
- Clone layout: `offline/site` present; `mirror`=False; `backups`=False
- Loopback requests: 8 records, local routes only=True, status counts={'200': 8}
- Tested routes: homepage, encyclopedia index, Elune (392), GameGuide, Media, Current News, and encyclopedia cascade.js; all returned non-empty HTTP 200 bodies with the recorded MIME values.
- Server stderr bytes: 0
- Clone cleanup: removed=True; server_stopped=True; D: free before/after=17458049024/18627579904 bytes.

The two initial clone attempts were retained as setup diagnostics: Git rejected the default and source-directory-only `safe.directory` values as dubious ownership. The exact source `.git` value allowed the local clone; no repository content was changed.

See `health.json`, `routes.json`, `server-requests.jsonl`, `clone-validation.json`, and the server stdout/stderr logs for the captured evidence.
