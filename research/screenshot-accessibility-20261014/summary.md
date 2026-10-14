# Screenshot accessibility sample

This inventory was assembled from saved local manifests and source maps on 2026-10-14. No Wayback request was made, and nested ZIP/raw stores were not scanned.

The plan contains **16** targets: **11** local image controls and **5** dynamic-gallery gaps. Exactly **5** have a matching saved CDX 200/image row; **11** remain unknown. The gallery recheck still reports 50 gallery routes but zero direct full/thumb files; the three Karazhan thumbnails below are late related previews recorded separately.

| ID | Context | Local image | Capture | Saved 200/image | CDX row |
|---|---|---:|---|---|---|
| `karazhan-thumb-ss1` | Raid gallery / TBC / local late capture | yes | 20080512222305 | True | unknown |
| `karazhan-thumb-ss2` | Raid gallery / TBC / local late capture | yes | 20080512212653 | True | unknown |
| `karazhan-thumb-ss3` | Raid gallery / TBC / local late capture | yes | 20080512212653 | True | unknown |
| `karazhan-full-ss1` | Raid gallery / TBC / full screenshot gap | no | not locally recorded | unknown | unknown |
| `blacktemple-full-ss1` | Raid gallery / TBC / full screenshot gap | no | not locally recorded | unknown | unknown |
| `blacktemple-thumb-ss1` | Raid gallery / TBC / thumbnail gap | no | not locally recorded | unknown | unknown |
| `magisters-full-ss1` | Dungeon gallery / TBC / full screenshot gap | no | not locally recorded | unknown | unknown |
| `magisters-thumb-ss1` | Dungeon gallery / TBC / thumbnail gap | no | not locally recorded | unknown | unknown |
| `wrath-screenshot-ss5` | Wrath of the Lich King screenshot gallery | yes | 20080402054247 | True | unknown |
| `wrath-screenshot-ss11` | Wrath of the Lich King screenshot gallery | yes | 20080402050117 | True | unknown |
| `wrath-screenshot-ss41` | Wrath of the Lich King screenshot gallery | yes | 20080402054459 | True | unknown |
| `eu-screenoftheday-10704-03` | Media / 2008 baseline EU daily screenshot | yes | 20080512205334 | unknown | True |
| `eu-screenoftheday-10702-05` | Media / 2008 baseline EU daily screenshot | yes | 20080512205328 | unknown | True |
| `eu-screenoftheday-10710-10` | Media / 2008 baseline EU daily screenshot | yes | 20080512205325 | unknown | True |
| `eu-screenoftheday-10706-26` | Media / 2008 EU daily screenshot | yes | 20080402003127 | unknown | True |
| `eu-screenoftheday-10704-14` | Media / 2007 EU daily screenshot | yes | 20070421152959 | unknown | True |

The strongest controls for the next replay check are `karazhan-thumb-ss2` (`20080512212653`), `karazhan-thumb-ss3` (`20080512212653`), and the Wrath screenshots `ss5` (`20080402054247`) and `ss11` (`20080402050117`). EU Screen of the Day controls retain their source page and capture timestamps, including `10704-03` at `20080512205334` and `10704-14` at `20070421152959`.

Black Temple and Magister's Terrace remain explicit probe targets because their gallery source pages enumerate 48 and 47 shots, while the local inventory has no corresponding direct full or thumbnail entity. Their `unknown` CDX state means only that this pass did not query those individual image URLs.

The next probe should record direct HTTP status, MIME, replay timestamp, response length, and image decode result for each target, then retry through the configured proxy only after direct transport fails. Preserve the original bytes and source timestamp for any accepted capture.
