# Related talent UI loader v54

The loader now dispatches by map schema. The existing v1 path continues to load its six PNGs with the original bundle, catalog, notice, and route behavior. The v2 path accepts only the pinned 24-target scope: those six PNGs plus 18 native-size GIF arrows across `across-left`, `across-right`, `down-1`, `down-2`, `down-4`, and `down-right`, each in grey, green, and yellow. The three `down-3` targets remain excluded.

The v2 branch binds the exact input map, decision, source acceptance record, and `root-input-pins.json`; checks the source URL, commit, tree, ZIP metadata, later-source classification, and null historical capture date; and restricts map, decision, acceptance, and payload paths to their pinned workspace locations. It checks every payload's byte length, SHA-256, Git blob SHA-1, decoded format, dimensions, and all frames. It returns the existing `RelatedTalentUIBundle` interface with 24 route reuses and a catalog whose `ui_count` is 24. Source references identify the accepted CraftedRO commit `4c8013cf40d0edf84625430eaf43b86d97880ae0` and tree `e8916c038b41c2c29144f5411f8fc6ec5cd032d5`. The supplement remains classified as later-source material; it does not claim recovery of 2008 images.

The immutable inputs checked for v2 are:

- `input-map.json` — SHA-256 `f795ed587062553831afd24d682aaba516ac07bdc6360636119a28aca2bf8355`
- `decision.json` — SHA-256 `958ae52a9bde6ff505522ba920257936971231650db0e3db1ef92241853fc304`
- `research/continuous-recovery-20261021/publication/root-talent-related-source-acceptance.json` — SHA-256 `4f05d6ab9ee61691cd6440ccd549fc756cd99424b3840ff92b0955c5bad53465`

The implementation changes are in `tools/related_talent_ui.py`, `tests/test_related_talent_ui.py`, and `tests/test_related_talent_ui_pages.py`. The exporter and its route handling were not changed.

Validation ran in PowerShell with `TEMP` and `TMP` set to `D:\WOW_Encyclopedia\.scratch\test-temp-20261022`:

```powershell
python -X utf8 -m unittest discover -s tests -p 'test_related_talent_ui.py' -v
```

Result: 14 tests passed, including the persisted v1 map, the public v2 map, exact bytes and source references, down-3 rejection after map/decision rebinding, payload hash/length/Git-blob drift, wrong-format and multi-frame rejection, source-binding drift, and unsafe payload paths.

```powershell
python -X utf8 -m unittest discover -s tests -p 'test_related_talent_ui_pages.py' -v
```

Result: 4 tests passed, including a real v2 loader bundle consumed by the exporter and all 24 target routes written to a temporary output. These checks do not replace the parent's independent production export, Chrome no-fulfill, save/reload, or release acceptance.
