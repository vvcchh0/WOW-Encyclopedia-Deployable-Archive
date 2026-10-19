# v35 timeout receipt erratum

The historical file
`research/continuous-recovery-20261019/integration/v35/v35-build-timeout-receipt.json`
is preserved unchanged (SHA-256
`ae3445b3ac99b6530d9f30a760a2ba1ba00603682b3da9ca5e65046cbd376d5a`). Its
recorded root-input-acceptance SHA `a8cb18dfae75b0bc2203d428ce68805d698d109b30d39a536bea2438f87db775`
is stale/incorrect. The corrected v35 gate is SHA
`1d3705381773e5040724f957512987719946e36876765f84395e804fdee655fd`.

The original process started at UTC
`2026-10-19T08:10:56.1827996Z`, with an intended 900-second deadline of
`2026-10-19T08:25:56.1827996Z`. It was actually stopped at
`2026-10-19T08:27:09.5528979Z`, an elapsed 973.3700983 seconds. The execution
used the `functions.exec` session (session `53078`, Python PID `21660`) and
polling/CTRL-C stop evidence; it did not have an outer `subprocess.run`
timeout. Therefore the old receipt must not be described as a hard 900-second
watchdog success. The new check uses an independent 300-second hard
`subprocess.run(..., timeout=300)` watchdog, and future promotion runners must
use the same model.
