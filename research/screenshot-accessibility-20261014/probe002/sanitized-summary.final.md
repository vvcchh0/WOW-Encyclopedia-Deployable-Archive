# Wayback replay probe002 (semantic correction)

- Network requests added by this correction: `0`; original network attempts remain `8/8`.
- Known-good items retrieved from already-present mirror resources: `2`; new unique resources: `0`.
- Raw body bytes: `308130/33554432`; D preflight `True`.

## Items

### `wrath_control` — Wrath screenshot

- Original: `http://www.worldofwarcraft.com/wrath/images/screenshots/ss11.jpg`; requested capture: `20080402050117`; known good: `True`.
- Outcome: `known_good_retrieved`; image retrieved: `True`; new unique resources: `0`.
- Actual capture: `20080402050117`; requested URL timestamp hint: `20080402050117`.
- `direct` status `0`, bytes `0`, elapsed `8.063`, failures `curl_exit_28,validation_failed`.
- `proxy` status `200`, bytes `100444`, elapsed `5.516`, failures `none`.

### `tbc_control` — Burning Crusade screenshot

- Original: `http://www.worldofwarcraft.com/burningcrusade/images/screenshots/ss102.jpg`; requested capture: `20080402041747`; known good: `True`.
- Outcome: `known_good_retrieved`; image retrieved: `True`; new unique resources: `0`.
- Actual capture: `20080402041747`; requested URL timestamp hint: `20080402041747`.
- `direct` status `0`, bytes `0`, elapsed `8.078`, failures `curl_exit_28,validation_failed`.
- `proxy` status `200`, bytes `198273`, elapsed `6.703`, failures `none`.

### `karazhan_full` — Raid gallery full image

- Original: `http://www.worldofwarcraft.com/info/dungeons/images/karazhan/ss1.jpg`; requested capture: `20080512210044`; known good: `False`.
- Outcome: `expected_missing_404`; image retrieved: `False`; new unique resources: `0`.
- Actual capture: `None`; requested URL timestamp hint: `20080512210044`.
- Interpretation: current replay returned HTTP 404/page indication for this requested capture only; this does not establish that all dates or all 50 galleries are absent.
- `direct` status `0`, bytes `0`, elapsed `8.047`, failures `curl_exit_28,validation_failed`.
- `proxy` status `404`, bytes `4705`, elapsed `6.453`, failures `validation_failed`.

### `magisters_full` — Dungeon gallery full image

- Original: `http://www.worldofwarcraft.com/info/dungeons/images/magisters/ss1.jpg`; requested capture: `20080512210044`; known good: `False`.
- Outcome: `expected_missing_404`; image retrieved: `False`; new unique resources: `0`.
- Actual capture: `None`; requested URL timestamp hint: `20080512210044`.
- Interpretation: current replay returned HTTP 404/page indication for this requested capture only; this does not establish that all dates or all 50 galleries are absent.
- `direct` status `0`, bytes `0`, elapsed `8.078`, failures `curl_exit_28,validation_failed`.
- `proxy` status `404`, bytes `4708`, elapsed `4.406`, failures `validation_failed`.

## Scope

- Original `sanitized-report.json` is preserved; this report is an offline semantic correction from its saved raw evidence.
- Raw response headers and bodies remain local under `raw/`; this summary contains no raw header text.
