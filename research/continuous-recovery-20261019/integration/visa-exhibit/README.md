# Visa historical-exhibit candidate

This directory contains an unapplied candidate for `tools/historical_exhibits.py`.
It promotes only the manifest-backed `/visa/index.html` route and the exact
`/visa` and `/visa/` aliases into a static historical exhibit. The six
root-accepted `www.worldofwarcraft.com/visa/images/` images are rendered as
local, non-anchor figures with captions. The candidate does not alter source
HTML or image bytes and does not touch the existing `/visa/reward/*` exhibits.

The candidate removes the source page's form, SignUpLink, apply/FAQ/business
anchors, mouseover handlers, Flash object/embed, and external targets by
replacing the derived landing page with the existing historical-exhibit visual
style. It leaves only local archive-home and `/visa/reward/index.html`
navigation.

`export_historical_exhibits_candidate.py` applies the candidate in memory to a
fresh module. `test_visa_exhibit_candidate.py` is an isolated fixture test; no
production module or test is modified. Source and accepted-copy evidence is in
`source-evidence.json`.

Run from the repository root:

```powershell
& 'C:\Program Files\Python311\python.exe' -X utf8 -m unittest discover -s research/continuous-recovery-20261019/integration/visa-exhibit -p 'test_*.py' -v
```
