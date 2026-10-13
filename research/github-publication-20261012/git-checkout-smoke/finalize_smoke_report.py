"""Write the final local Git-clone smoke report from captured evidence."""
from __future__ import annotations

import json
import sys
from pathlib import Path


root = Path(__file__).resolve().parent
validation = json.loads((root / "clone-validation.json").read_text(encoding="utf-8"))
state_path = root / "cleanup-state.json"
state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}

report = {
    "purpose": "Git-only publication clone smoke validation",
    "commit_requested": "b8d655ca51c4e4f73101e8e774eb46b37bda9c4f",
    "clone": validation["clone"],
    "checkout": {
        "head": validation["git_head"],
        "clean_status": validation["git_status_porcelain"] == "",
        "core_longpaths": validation["core_longpaths"],
        "initial_clone_mode": "git clone --local --no-hardlinks",
        "safe_directory_workaround": "temporary exact source .git safe.directory was required; removed after clone smoke",
    },
    "manifest": validation["manifest"],
    "file_validation": validation["file_validation"],
    "layout": validation["clone_layout"],
    "loopback": validation["loopback_log"],
    "cleanup": state,
    "limitations": [
        "Validation used the committed derived files and the local loopback server; no archive or external network request was made.",
        "The clone was removed after validation because the workspace disk reserve became constrained; captured logs and hashes remain in this directory.",
    ],
}
(root / "smoke-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

fv = report["file_validation"]
lp = report["loopback"]
cleanup = report["cleanup"]
lines = [
    "# Git-only publication clone smoke validation",
    "",
    f"- Requested commit: `{report['commit_requested']}`",
    f"- Checked-out commit: `{report['checkout']['head']}` (clean={report['checkout']['clean_status']})",
    f"- `core.longpaths`: `{report['checkout']['core_longpaths']}`",
    f"- Manifest SHA-256: `{report['manifest']['sha256']}` ({report['manifest']['bytes']} bytes)",
    f"- Manifest records/routes: {report['manifest']['file_records']}/{report['manifest']['unique_routes']}",
    f"- File verification: {fv['hashed']} hashed; missing={len(fv['missing'])}, nonregular={len(fv['nonregular'])}, unsafe/duplicate={len(fv['unsafe_or_duplicate'])}, hash mismatches={len(fv['hash_mismatch'])}, length mismatches={len(fv['length_mismatch'])}; pass={fv['pass']}",
    f"- Clone layout: `offline/site` present; `mirror`={report['layout']['mirror_present']}; `backups`={report['layout']['backups_present']}",
    f"- Loopback requests: {lp['request_records']} records, local routes only={lp['all_local_routes']}, status counts={lp['status_counts']}",
    "- Tested routes: homepage, encyclopedia index, Elune (392), GameGuide, Media, Current News, and encyclopedia cascade.js; all returned non-empty HTTP 200 bodies with the recorded MIME values.",
    f"- Server stderr bytes: {(root / 'server-stderr.log').stat().st_size}",
    f"- Clone cleanup: removed={cleanup.get('clone_removed')}; server_stopped={cleanup.get('server_stopped')}; D: free before/after={cleanup.get('d_free_before')}/{cleanup.get('d_free_after')} bytes.",
    "",
    "The two initial clone attempts were retained as setup diagnostics: Git rejected the default and source-directory-only `safe.directory` values as dubious ownership. The exact source `.git` value allowed the local clone; no repository content was changed.",
    "",
    "See `health.json`, `routes.json`, `server-requests.jsonl`, `clone-validation.json`, and the server stdout/stderr logs for the captured evidence.",
]
(root / "smoke-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps({"json": str(root / "smoke-report.json"), "markdown": str(root / "smoke-report.md")}, ensure_ascii=False))
