# v34 runner preparation

`execute_v34.py --go --root-export-go` is a one-shot wrapper. It refuses an
absent or unaccepted `research/continuous-recovery-20261019/publication/
root-v34-input-acceptance.json`, checks every prepared and frozen binding,
requires zero new image rows, checks the D: disk floor, refuses an existing
output/partial/receipt, and calls the current exporter once. It uses the
frozen source15 site and maps; it never reads v33 output as source and never
rebuilds maps or preflight.
