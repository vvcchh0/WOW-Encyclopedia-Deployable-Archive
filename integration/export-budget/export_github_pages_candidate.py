"""Load an isolated exporter candidate with the workspace-budget patch.

This module never edits ``tools/export_github_pages.py``.  It reads that
source, applies the two-line candidate diff in memory, and executes the
result as a separately named module so the focused tests exercise the real
export pipeline and all of its current helpers.
"""

from __future__ import annotations

import hashlib
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "tools" / "export_github_pages.py"
BEFORE_WORKSPACE = "    before_workspace = workspace_size(workspace_root, output)\n"
AFTER_WORKSPACE = "        after_workspace = workspace_size(workspace_root, output)\n"
BEFORE_WORKSPACE_PATCHED = "    before_workspace = workspace_size(workspace_root, output) if max_bytes is not None else None\n"
AFTER_WORKSPACE_PATCHED = "        after_workspace = workspace_size(workspace_root, output) if max_bytes is not None else None\n"


def source_sha256() -> str:
    return hashlib.sha256(SOURCE.read_bytes()).hexdigest()


def load_candidate() -> types.ModuleType:
    source = SOURCE.read_text(encoding="utf-8")
    if source.count(BEFORE_WORKSPACE) != 1 or source.count(AFTER_WORKSPACE) != 1:
        raise RuntimeError("candidate patch context is absent or ambiguous in exporter source")
    patched = source.replace(BEFORE_WORKSPACE, BEFORE_WORKSPACE_PATCHED, 1)
    patched = patched.replace(AFTER_WORKSPACE, AFTER_WORKSPACE_PATCHED, 1)
    name = "export_github_pages_export_budget_candidate"
    module = types.ModuleType(name)
    module.__file__ = str(SOURCE)
    module.__package__ = ""
    sys.modules[name] = module
    exec(compile(patched, str(SOURCE), "exec"), module.__dict__)
    return module
