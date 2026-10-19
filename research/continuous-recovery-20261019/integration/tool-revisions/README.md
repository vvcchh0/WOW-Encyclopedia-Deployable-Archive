# Formal tool revision record

This directory records the approved application of two narrow changes after v35
online acceptance. It does not contain an export and it does not change the
frozen v35 output.

## Applied production changes

- `tools/export_github_pages.py`: `workspace_size()` is called before and after
  export only when `max_bytes` is finite. An uncapped export reports
  `workspace_bytes: null`; disk free checks remain active. Finite workspace
  limits retain both before-export and after-export enforcement.
- `tools/historical_exhibits.py`: `/visa/index.html`, `/visa`, and `/visa/`
  render the six accepted 2008 Visa images as a static historical exhibit.
  The derived page exposes only archive home and the existing rewards exhibit
  as local links, with no form, account, application, Flash, mouseover, bank,
  or external business control.

The formal source diff and all final SHA-256 values are in
`formal-application-receipt.json` and `formal-application.diff`. The earlier
Visa candidate files under `integration/visa-exhibit/` remain unchanged and
are hashed in the receipt. No budget-candidate directory was present in this
checkout when the formal two-line budget change was applied; the final diff is
the authoritative record of that approved change.

## Validation

`run_focused_tests.py` ran each command through `subprocess.run(...,
timeout=120)`:

```text
python -X utf8 -m unittest discover -s tests -p test_github_pages_export.py -v
python -X utf8 -m unittest discover -s tests -p test_historical_exhibits.py -v
```

The exporter suite passed 34 tests in 4.643 seconds. The historical-exhibit
suite passed 15 tests in 1.135 seconds. The receipt also preserves the initial
runner-path failure before the repository-root calculation was corrected.

No network, export, commit, or push was performed.
