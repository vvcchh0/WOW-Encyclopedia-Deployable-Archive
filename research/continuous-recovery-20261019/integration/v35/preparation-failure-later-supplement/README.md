# v35 preparation failure: accepted later supplement policy

The second offline `build_pages_v35.py --prepare --preflight` attempt passed
the primary-closure collision fix and then stopped while revalidating the
accepted v34 supplement closure.  The exporter rejected an existing v34 row
captured at `20100810173046` because this preparation call used
`allow_later_image_supplements=False`.  This is a preparation-policy mismatch,
not a new source or an export attempt.

The three files in this directory are the exact partial outputs produced before
that loader error.  They remain separate from the final v35 filenames and are
not accepted inputs.  The next bounded retry changes only the old-closure
loader call to the v34 runner's already-used `allow_later_image_supplements=True`
policy; the new supplement map remains empty and is still checked with the
strict policy.

Observed command:

```text
python -X utf8 research/continuous-recovery-20261019/integration/v35/build_pages_v35.py --prepare --preflight
```

Observed error:

```text
wow_recovery_v35_exporter.PagesExportError: image supplement capture is after 2008: 20100810173046
```

No network request, export, publish, or old-version modification occurred.
