# Contest winners navigation recovery

This bounded integration fixture records the narrow derived-JavaScript repair for
the frozen v33 page `contests/05-05-25/winners.html`.  The historical page calls
the shared `findNode`/`tree(result)` navigation path, but its URL is a child page
while the loaded `Menu1_6_4` node is the `Contests` parent (`/contests/`).  The
exporter therefore adds a guarded `result = "1_6_4"` assignment immediately
before the one `tree(result);` call in `navtreefunctions.js`.

The guard is deliberately narrow:

* `document.location.pathname` must equal the project-prefixed winners route;
* `result` must still be undefined;
* `Menu1_6_4` must exist and `stripId(Menu1_6_4[0])` must be exactly
  `Contests`.

The source menu, `pageId`, and `findNode` are unchanged.  Applying the helper a
second time is a no-op, and ambiguous duplicate markers or `tree(result);`
targets are rejected.  `prepare_contest_nav_fixture.py` reads the frozen v33
output without changing it and writes a derived script plus immutable bindings
under this directory.  `compare_contest_nav.cjs` serves the frozen page through
loopback only, compares the original and derived script variants, and records
the navigation result, page errors, body text, and image-link evidence.

Validation commands:

```powershell
& 'C:\Program Files\Python311\python.exe' -X utf8 -m unittest discover -s tests -p test_contest_navigation_recovery.py -v
& 'C:\Program Files\Python311\python.exe' -X utf8 research/continuous-recovery-20261019/integration/contest-nav/prepare_contest_nav_fixture.py
& 'C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node.exe' research/continuous-recovery-20261019/integration/contest-nav/compare_contest_nav.cjs
```

The comparison is local-only.  It does not write the frozen v33 output, source
maps, or release state.
