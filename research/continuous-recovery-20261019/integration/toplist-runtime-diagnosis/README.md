# v37 Toplist runtime diagnosis

This is a single bounded read-only diagnosis of the local v37 Toplist page.
It records every browser request/response URL and status, including requests
outside the project prefix, console locations, page errors, `document.spells`
keys and missing/error fields, and actual `/toplist/data/` manifest/filesystem
entries. External requests are aborted and recorded; no data or controls are
injected. The runner has a 90-second hard subprocess timeout and does not
retry.

Preparation/syntax command:

```text
C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe --check research/continuous-recovery-20261019/integration/toplist-runtime-diagnosis/diagnose_toplist_runtime.cjs
C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 -m py_compile research/continuous-recovery-20261019/integration/toplist-runtime-diagnosis/execute_toplist_runtime_diagnosis.py
```

Authorized one-shot command:

```text
C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -X utf8 research/continuous-recovery-20261019/integration/toplist-runtime-diagnosis/execute_toplist_runtime_diagnosis.py --run
```
