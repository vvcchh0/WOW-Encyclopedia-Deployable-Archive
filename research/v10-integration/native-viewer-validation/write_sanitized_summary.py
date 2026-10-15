"""Write the bounded, sanitized NATIVE-VIEWER-VM-012 offline summary."""

from __future__ import annotations

import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OWNED = ROOT / "research" / "v10-integration" / "native-viewer-validation"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


source = json.loads((OWNED / "source-validation.json").read_text(encoding="utf-8"))
vm = json.loads((OWNED / "vm-results.json").read_text(encoding="utf-8"))
raw_path = ROOT / source["inputs"]["raw_viewer"]["path"].replace("/", "\\")
derived_path = OWNED / "derived-screeniesimplified.js"

case_rows = []
for item in vm["cases"]:
    observed = item["observed"]
    case_rows.append(
        {
            "name": item["name"],
            "search": item["search"],
            "expected_one_based": item["expectedOneBased"],
            "expected_zero_based": item["expectedZeroBased"],
            "observed_now_viewing": observed["nowViewing"],
            "observed_opened_shot": observed["openedShot"],
            "d_current": observed["dCurrent"],
            "d_total": observed["dTotal"],
            "screen_link": observed["screenLink"],
            "sentinel": observed["sentinel"],
            "image_assignment_count": observed["imageAssignmentCount"],
            "passed": item["passed"],
        }
    )

summary = {
    "schema": "native-viewer-vm-012-sanitized-summary/v1",
    "batch_id": "NATIVE-VIEWER-VM-012",
    "simulation": True,
    "network_requests": 0,
    "validation_mode": "offline Node VM; native source definitions executed; no browser or archive acquisition",
    "commands": [
        "C:\\nvm4w\\nodejs\\node.EXE --version",
        "C:\\nvm4w\\nodejs\\node.EXE research\\v10-integration\\native-viewer-validation\\vm_native_viewer_validation.js",
    ],
    "node_version": vm["node_version"],
    "vm_window": {"start_utc": vm["start_utc"], "end_utc": vm["end_utc"]},
    "inputs": {
        "raw_viewer": {
            "path": source["inputs"]["raw_viewer"]["path"],
            "bytes": source["inputs"]["raw_viewer"]["bytes"],
            "sha256": source["inputs"]["raw_viewer"]["sha256"],
            "actual_memento": source["inputs"]["raw_viewer"]["actual_memento"],
            "captured_original_url": source["inputs"]["raw_viewer"]["captured_original_url"],
            "on_disk_sha256": sha256(raw_path),
        },
        "mixed9_acceptance": source["inputs"]["mixed9_acceptance"],
        "viewer_fix_receipt": source["inputs"]["viewer_fix_receipt"],
    },
    "freeze_hash_match": source["freeze"]["match"],
    "freeze_current_digests": source["freeze"]["current_digests"],
    "source_transform": source["source_transform"],
    "derived": {
        "path": source["derived"]["path"],
        "bytes": derived_path.stat().st_size,
        "sha256": sha256(derived_path),
        "recorded_sha256": source["derived"]["sha256"],
    },
    "assertions": vm["assertions"],
    "cases": case_rows,
    "scope_not_covered": [
        "browser layout, paint, and browser navigation",
        "real image fetching or archive acquisition",
        "animation timers and interactive next/previous behavior",
        "full exporter/build/browser integration",
    ],
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "host_platform": platform.platform(),
}

if summary["inputs"]["raw_viewer"]["on_disk_sha256"] != summary["inputs"]["raw_viewer"]["sha256"]:
    raise SystemExit("raw SHA mismatch")
if summary["derived"]["sha256"] != summary["derived"]["recorded_sha256"]:
    raise SystemExit("derived SHA mismatch")
if not summary["freeze_hash_match"] or not vm["assertions"]["all_cases_passed"]:
    raise SystemExit("validation assertions are not all passing")

(OWNED / "sanitized-summary.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)

lines = [
    "# NATIVE-VIEWER-VM-012 sanitized summary",
    "",
    "Offline validation only. `simulation=true`; `network_requests=0`; no browser or archive acquisition.",
    "",
    f"- Node: `{vm['node_version']}`",
    f"- VM window: `{vm['start_utc']}` to `{vm['end_utc']}`",
    f"- Raw viewer: `{source['inputs']['raw_viewer']['bytes']} B`, SHA256 `{source['inputs']['raw_viewer']['sha256']}`",
    f"- Derived viewer: `{summary['derived']['bytes']} B`, SHA256 `{summary['derived']['sha256']}`",
    f"- Freeze hashes: exporter `{source['freeze']['match']['exporter']}`, tests `{source['freeze']['match']['tests']}`, source CSS `{source['freeze']['match']['source_css']}`",
    f"- Fresh VM cases: `{vm['assertions']['case_count']}/{vm['assertions']['expected_case_count']}` passed",
    "",
    "## Case evidence",
    "",
    "| case | query | opened index | dCurrent/dTotal | screenLink | sentinel | result |",
    "|---|---|---:|---:|---|---:|---|",
]
for row in case_rows:
    lines.append(
        f"| `{row['name']}` | `{row['search'] or '(missing)'}` | {row['observed_opened_shot']} | "
        f"{row['d_current']}/{row['d_total']} | `{row['screen_link']}` | {row['sentinel']} | "
        f"{'PASS' if row['passed'] else 'FAIL'} |"
    )
lines.extend(
    [
        "",
        "The native source built `shotList` as common `ss1..ss12` plus locale `en_us/ss1`, with matching `dirList` and `hiResList`; all cases verified one-based query input to zero-based lightbox index and `-hires.jpg` links.",
        "",
        "## Source and scope boundaries",
        "",
        f"- The helper transformed the single approved original fragment at character span `{source['source_transform']['original_fragment_span']}`; prefix/suffix and all four navigation function bodies remained unchanged.",
        "- `eval` was removed from the derived parser fragment; invalid, duplicate, unsafe, and sentinel query values all fell back to one-based shot 1.",
        "- Image and DOM objects were local stubs. The run does not establish browser layout, paint, network image loading, animation, or full exporter integration.",
        "",
        f"Generated from `source-validation.json` and `vm-results.json`; report update UTC `{summary['generated_utc']}`.",
    ]
)
(OWNED / "sanitized-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps({
    "mode": "offline_summary",
    "network_requests": 0,
    "cases": vm["assertions"]["case_count"],
    "all_cases_passed": vm["assertions"]["all_cases_passed"],
    "raw_sha256": summary["inputs"]["raw_viewer"]["on_disk_sha256"],
    "derived_sha256": summary["derived"]["sha256"],
    "freeze_hash_match": summary["freeze_hash_match"],
}, ensure_ascii=False))
