# Talent calculator Source15 fixtures

These are the two reviewed, original-byte JavaScript inputs used by
`tests/test_talent_compat.py`. They are copied into the test fixture so a new
checkout does not depend on the ignored `offline/site` tree.

| Fixture | Original URL index entry | Length | SHA-256 |
| --- | --- | ---: | --- |
| `localize.js` | `http://www.worldofwarcraft.com/shared/global/talents/includes/localize.js` | 5467 | `e13769500cc7853b7c4d835f0380cf971cbec5f8fc061c3f1f83cf3dea1e6972` |
| `printOutTop.js` | `http://www.worldofwarcraft.com/shared/global/talents/includes/printOutTop.js` | 22836 | `618c92c0d00c960f651aad4364a05e93cfb785df38b2b63902febaeb06d26f04` |

The URL paths are retained from the local Source15/origin index. No HTTP
capture, cookies, or other source tree is included here.
