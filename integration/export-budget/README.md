# Export workspace-budget candidate

This directory contains an unapplied candidate for `tools/export_github_pages.py`.
When `max_bytes is None`, the candidate skips both recursive `workspace_size`
walks and returns `workspace_bytes: null`; the existing before/after disk-free
checks and per-write checks remain active. A finite `max_bytes` keeps the
existing workspace accounting and rejection behavior.

`export_github_pages.workspace-budget.patch` is the complete two-line diff.
`export_github_pages_candidate.py` loads the current exporter source, applies
that diff in memory, and registers a temporary module; it never writes the
production tool. The focused test uses a real minimal export fixture and
checks uncapped success, disk-floor rejection, and finite-budget rejection.

Run from the repository root:

```powershell
& 'C:\Program Files\Python311\python.exe' -X utf8 -m unittest discover -s integration/export-budget -p 'test_*.py' -v
```
