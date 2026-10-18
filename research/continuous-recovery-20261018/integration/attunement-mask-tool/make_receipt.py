#!/usr/bin/env python3
"""Write immutable evidence for the narrow attunement mask repair."""

from __future__ import annotations

import difflib
import hashlib
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "research/continuous-recovery-20261018/integration/attunement-mask-tool"
TOOL = ROOT / "tools/export_github_pages.py"
TEST = ROOT / "tests/test_attunement_mask_pixel.py"
V30_PAGE = ROOT / ".scratch/pages-resources-20261018-v30/bcattunement/index.html"
PIXEL = ROOT / ".scratch/offline-navigation-20261015-v15/site/shared/wow-com/includes/images/pixel.gif"
BASELINE_SHA = "b353b0f88da385321a70b35e2bb7f9bccc7cbb371f69c7d36c3cd8d2c3af543c"
V30_PAGE_SHA = "ea23f53156738370d24354f7690bf6c21363eb0e442a01bcb99f0e55532c9c20"
PIXEL_SHA = "b1442e85b03bdcaf66dc58c7abb98745dd2687d86350be9a298a1d9382ac849b"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconstruct_b353(current: str) -> str:
    # Reapply the persisted popup-only patch to the repository HEAD (the
    # accepted 7c3684 baseline) in a temporary assigned-directory checkout.
    # This avoids guessing at whitespace around the current attunement hunk.
    source = subprocess.check_output(
        ["git", "show", "HEAD:tools/export_github_pages.py"],
        cwd=ROOT,
    )
    popup_diff = (ROOT / "research/continuous-recovery-20261018/integration/popup-image-tool/implementation-diff.patch").read_text(encoding="utf-8")
    start = popup_diff.index("--- a/tools/export_github_pages.py")
    end = popup_diff.index("--- /dev/null", start)
    tool_diff = popup_diff[start:end]
    with tempfile.TemporaryDirectory(dir=OUT) as scratch:
        scratch_root = Path(scratch)
        target = scratch_root / "tools/export_github_pages.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source)
        apply_result = subprocess.run(
            ["git", "apply", "--directory", scratch_root.relative_to(ROOT).as_posix()],
            input=(tool_diff.encode("utf-8")),
            cwd=ROOT,
            capture_output=True,
            check=False,
        )
        if apply_result.returncode != 0:
            raise RuntimeError(f"could not reconstruct popup baseline: {apply_result.stderr.decode(errors='replace')}")
        baseline_bytes = target.read_bytes()
        baseline = baseline_bytes.decode("utf-8")
    baseline_sha = hashlib.sha256(baseline_bytes).hexdigest()
    if baseline_sha != BASELINE_SHA:
        raise RuntimeError(f"reconstructed popup baseline does not match accepted b353 SHA: {baseline_sha}")
    return baseline


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    current = TOOL.read_text(encoding="utf-8")
    baseline = reconstruct_b353(current)
    current_lines = current.splitlines(keepends=True)
    baseline_lines = baseline.splitlines(keepends=True)
    patch = "".join(
        difflib.unified_diff(
            baseline_lines,
            current_lines,
            fromfile="tools/export_github_pages.py@b353b0f8",
            tofile="tools/export_github_pages.py@attunement-mask",
        )
    )
    diff_path = OUT / "attunement-mask-diff.patch"
    diff_path.write_text(patch, encoding="utf-8")

    current_v30_sha = sha256(V30_PAGE)
    pixel_sha = sha256(PIXEL)
    if current_v30_sha != V30_PAGE_SHA:
        raise RuntimeError(f"frozen v30 page changed: {current_v30_sha}")
    if pixel_sha != PIXEL_SHA:
        raise RuntimeError(f"transparent pixel changed: {pixel_sha}")

    import sys

    sys.path.insert(0, str(ROOT / "tools"))
    import export_github_pages as pages

    page = V30_PAGE.read_text(encoding="utf-8")
    transformed, changed = pages.rewrite_attunement_mask_pixel(
        page,
        route="/bcattunement/index.html",
        base_path=pages.DEFAULT_BASE_PATH,
    )
    map_pixel = 'id="mapPixel"'
    target_request = "requested=https%3A%2F%2Fwww.worldofwarcraft.com%2Fbcattunement%2Fimages%2Fpixel.gif"
    canonical = pages.DEFAULT_BASE_PATH + "shared/wow-com/includes/images/pixel.gif"
    actual_page_check = {
        "changed": changed,
        "map_pixel_count": transformed.count(map_pixel),
        "canonical_pixel_count": transformed.count(canonical),
        "target_placeholder_count_before": page.count(target_request),
        "target_placeholder_count_after": transformed.count(target_request),
        "legacy_background_image_count": transformed.count("_background-image:url"),
        "map_pixel_line": next(line for line in transformed.splitlines() if map_pixel in line),
        "coverDivStyle1_line": next(line for line in transformed.splitlines() if ".coverDivStyle1" in line),
        "coverDivStyle2_line": next(line for line in transformed.splitlines() if ".coverDivStyle2" in line),
    }

    test_log = OUT / "focused-tests.log"
    test_log_sha = sha256(test_log) if test_log.exists() else None
    receipt = {
        "schema": "wow-recovery.integration.attunement-mask-tool.v1",
        "checked_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "accepted_scope": {
            "route": "/bcattunement/index.html",
            "visible_references": ["img#mapPixel", ".coverDivStyle1 background", ".coverDivStyle2 background"],
            "requested_original": "https://www.worldofwarcraft.com/bcattunement/images/pixel.gif",
            "replacement_original": "/shared/wow-com/includes/images/pixel.gif",
            "legacy_ie_background_left_unchanged": True,
            "other_routes_and_pixel_references_left_unchanged": True,
            "payload_status": "compatibility mask only; no original bcattunement pixel payload recovered",
        },
        "previous_popup_tool_sha256": BASELINE_SHA,
        "tool_sha256": sha256(TOOL),
        "test_sha256": sha256(TEST),
        "diff_sha256": sha256(diff_path),
        "focused_test_log_sha256": test_log_sha,
        "frozen_v30_page": {"path": str(V30_PAGE.relative_to(ROOT)).replace("\\", "/"), "sha256": current_v30_sha, "length": V30_PAGE.stat().st_size},
        "transparent_pixel": {"path": str(PIXEL.relative_to(ROOT)).replace("\\", "/"), "sha256": pixel_sha, "length": PIXEL.stat().st_size},
        "actual_frozen_page_check": actual_page_check,
        "network_requests": 0,
        "export_executed": False,
        "old_outputs_modified": False,
    }
    receipt_path = OUT / "verification-receipt.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    readme = f"""# Attunement map mask tool evidence

The accepted popup-tool baseline was `{BASELINE_SHA}`. The narrow repair is
`rewrite_attunement_mask_pixel`: it runs only for `/bcattunement/index.html`,
uses `_MarkupTokenParser` source positions, and replaces exactly three visible
references whose requested original is
`https://www.worldofwarcraft.com/bcattunement/images/pixel.gif`:
`img#mapPixel`, `.coverDivStyle1` `background`, and `.coverDivStyle2`
`background`. The legacy `_background` declaration and unrelated pixel URLs
are intentionally unchanged. The replacement is the existing 43-byte
transparent `/shared/wow-com/includes/images/pixel.gif`, prefixed for Pages;
it is a compatibility mask, not recovered attunement image content.

Focused command:

```text
C:\\Users\\17630\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe -X utf8 -m unittest -v tests.test_attunement_mask_pixel tests.test_popup_image_viewer
```

The JSON receipt records exact hashes and the read-only frozen v30 page check.
No export, network request, old-output mutation, commit, or publication was
performed.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    print(json.dumps({"receipt": str(receipt_path), "diff": str(diff_path), "actual_page_check": actual_page_check}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
