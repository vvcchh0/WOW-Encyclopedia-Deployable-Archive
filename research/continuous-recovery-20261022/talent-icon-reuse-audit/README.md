# Talent icon reuse audit

This is a bounded offline review of missing talent JPG routes in the frozen v52 resource inventory. It does not add routes or alter the site. The ten positive findings are same-class moved or renamed ability candidates from the cached CraftedRO WotLK 3.3.5a snapshot. None is established as the original 2008 image.

## Candidate shortlist

| Old missing target | Related source candidate | Evidence |
|---|---|---|
| Paladin Divine Strength (Holy) | Paladin Divine Strength (Protection) | Same five-rank Strength talent; per-rank values changed. |
| Paladin Improved Concentration Aura (Protection) | Paladin Improved Concentration Aura (Holy) | Same class and aura/silence-interrupt effects; later condition changed. |
| Paladin Improved Judgement | Paladin Improved Judgements | Pluralized title; same 1/2-second Judgement cooldown reduction. |
| Hunter Scatter Shot (Marksmanship) | Hunter Scatter Shot (Survival) | Same shot/disorient ability; tree moved. |
| Hunter Readiness (Survival) | Hunter Readiness (Marksmanship) | Same cooldown-reset ability; later exception and cooldown changed. |
| Rogue Relentless Strikes (Assassination) | Rogue Relentless Strikes (Subtlety) | Same maximum 20% per combo point effect; five-rank tuning. |
| Warrior Improved Intercept (Arms) | Warrior Improved Intercept (Fury) | Identical cooldown effects; tree moved. |
| Warrior Tactical Mastery (Protection) | Warrior Tactical Mastery (Arms) | Same retained-rage and Defensive-Stance threat effects. |
| Warrior Sweeping Strikes (Fury) | Warrior Sweeping Strikes (Arms) | Same additional-nearby-opponent ability; 10 swings became 5. |
| Warrior Weapon Mastery (Fury) | Warrior Weapon Mastery (Arms) | Same two-rank dodge/disarm effect; tree moved. |

Each target is still classified `exact_local_resource_absent` in the v52 CSV and absent from the v52 and Source16 site trees. Every proposed source has exact cached ZIP member path, byte length, SHA-256, Git blob SHA-1, 36x36 JPEG dimensions, single-frame decode result, and matching private extraction/inventory hashes in `audit.json`. These moved-path assets do not appear in the accepted 986-entry exact-route map.

## Cross-class cases

The parent-designated same-name cases are not automatic mappings. Rogue and Warrior Precision active/off images are byte-identical to each other, but the missing Paladin image is unavailable, so the old Paladin icon cannot be inferred. Warrior Shield Specialization is not equivalent to old Paladin/Shaman effects; the Shaman Shield Specialization source image is absent from the ZIP. Priest Spell Warding has an overlapping effect, but the missing Paladin pixels remain unknown. Warrior Sword Specialization is related but later rank tuning and cooldown differ. Shaman Weapon Mastery has a different effect and a visibly different icon from the same-class moved Warrior Weapon Mastery candidate.

Druid Nature's Grasp and Improved Nature's Grasp have no current Druid talent/image match in the cached tree. The only ZIP image-name lead is Shaman Earth's Grasp; its different class and source data do not support reuse.

## Provenance and checks

The archived source is the pinned CraftedRO commit `4c8013cf40d0edf84625430eaf43b86d97880ae0`, downloaded 2026-10-21. Its input map records `original_capture_timestamp: null` and classifies it as a later related source. The accepted source record reports zero recovered 2008 images. Old effect descriptions come from the actual v52 class `data.js`; Source16 source hashes and `actual_timestamp` values tie those definitions to the 2008 capture records in the frozen build manifest.

Review used the v52 remaining-target CSV, the 986 input map, complete accepted image inventory, the cached ZIP payload, Source16 and v52 class data, and selected ZIP image bytes. The candidate contact sheets enlarge original 36px files with nearest-neighbor only for viewing; no source payload was re-encoded. No network access, site changes, tool changes, or Git changes were made.

See [audit.json](audit.json) for exact paths, input hashes, line references, source metadata, target status, image hashes, cross-class decisions, and unresolved limits. Review sheets: [same-class candidates](same-class-candidate-contact-sheet.png) and [cross-class/name-only checks](cross-class-refusal-contact-sheet.png).
