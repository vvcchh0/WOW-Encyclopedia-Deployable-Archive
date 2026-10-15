# Full tracked-tree publication hygiene scan

Pinned Git tree: `e6f558061455d60926e855f56f1b681267bfe22d` (verified expected HEAD: `True`).
The scan is byte-complete over the exact tracked Git tree, including binary files. It uses `git ls-tree` and `git cat-file --batch`; it does not inspect mutable untracked files and does not access the network.

## Coverage

- Tracked files: 8,740; scanned: 8,740; skipped: 0; read/object errors: 0
- Tracked/scanned bytes: 740,009,246 / 740,009,246
- Complete byte scan: `True`; every file record includes Git object ID, byte length and SHA256.
- Findings in 81 files; matched values are never emitted.

## Credential-shape result

Candidate value-shaped matches (excluding handling-only Authorization/Cookie fields): **6**; exact reviewed unresolved credential findings: **0**.

- `authorization_field_without_value`: 5 matches in 1 files
- `cookie_handling_field`: 2877 matches in 78 files
- `cookie_literal_assignment`: 2 matches in 2 files
- `credential_literal_assignment`: 3 matches in 1 files
- `url_userinfo_value`: 1 matches in 1 files

Cookie handling code is separated from cookie literal assignments. Historical `document.cookie` or `Set-Cookie` handling is not called a credential; any literal assignment remains a review candidate. Fixed fixtures/examples and historical public archive content are classified by path/context in the JSON without publishing values.

## Match locations

The JSON lists category, counts, byte offsets, line numbers where the file is text-like, field names, literal status, and context class. It intentionally contains no matched secret, token, password, cookie value, or line text.

### `artifacts/github-release-20261012/release-notes.md`

Context: `repository_source_or_metadata`; bytes: 1,608; SHA256: `c0744466c1cc93e37c04dd8662ac82dba049f7ef9bc6fbdc063e2fa11e9c83cc`.
- `cookie_handling_field` count=1; byte offsets=1342; lines=1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `artifacts/offline-20261012-recovery-package-verification.json`

Context: `repository_source_or_metadata`; bytes: 5,930,419; SHA256: `bcfea500b9ba4b6734c71b3a4de0452f926a1239e9cfe3b3f3529170d04f951d`.
- `cookie_handling_field` count=32; byte offsets=392794, 409516, 409715, 410504, 410704, 410905, 411106, 411307, 411508, 411709, 411910, 412111, 412312, 412513, 412713, 412913, 413114, 413315, 413516, 413717; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `artifacts/offline-20261012-recovery-portability-shortpath-check.json`

Context: `repository_source_or_metadata`; bytes: 4,638,237; SHA256: `b953c5b15862a0e6b0aec4e87fbd8bad9274675143ecea3b6a866df9891d1348`.
- `cookie_handling_field` count=32; byte offsets=262292, 274751, 274901, 275494, 275645, 275797, 275949, 276101, 276253, 276405, 276557, 276709, 276861, 277013, 277164, 277315, 277467, 277619, 277771, 277923; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `docs/github-publication-20261012.md`

Context: `repository_source_or_metadata`; bytes: 6,769; SHA256: `42cd7e77d0f29a03843b59cb06c0cd74fc07cf475b98a738e19f81de2bbae764`.
- `cookie_handling_field` count=4; byte offsets=2843, 4148, 6209, 6247; lines=1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `docs/media-and-navigation-recovery-20261015.md`

Context: `repository_source_or_metadata`; bytes: 12,607; SHA256: `1c64d16c1038c055e0b0a06f3dfd6da08d84736cd077d1fec7d944e08894a3a8`.
- `cookie_handling_field` count=1; byte offsets=7135; lines=1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `docs/resource-recovery-2008.md`

Context: `repository_source_or_metadata`; bytes: 56,308; SHA256: `9171ba22aef3595cbf6608e67f735252df0b3f9e20f35593adf31211dfea1e4a`.
- `cookie_handling_field` count=1; byte offsets=24852; lines=1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `docs/resource-resume-20261013.md`

Context: `repository_source_or_metadata`; bytes: 4,302; SHA256: `056a8e990992508af0e2ad8264181a5670a8fc7a8e323c6c4ca5e00c1dcbcdfc`.
- `cookie_handling_field` count=1; byte offsets=4261; lines=1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `offline/build-manifest.json`

Context: `repository_source_or_metadata`; bytes: 73,067,980; SHA256: `397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459`.
- `cookie_handling_field` count=514; byte offsets=202136, 202186, 202264, 202312, 202659, 202701, 396083, 396122, 403781, 403832, 403911, 403963, 404043, 404095, 404175, 404227, 404307, 404359, 404439, 404491; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `offline/site/_origins/forums.worldofwarcraft.com/js/forum.js`

Context: `historical_public_archive_content`; bytes: 20,349; SHA256: `a0bf9f2b4a4ed7574c7720aee4ab0f2df7fb7bdebfb5e0152216e07478ef72ed`.
- `cookie_handling_field` count=19; byte offsets=10596, 10626, 10990, 11082, 11183, 11294, 11356, 11410, 17462, 17589, 17869, 17914, 17923, 17999, 18042, 18051, 18591, 18697, 19162; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/contests/holiday-xmas05/cookie/honorable.html`

Context: `historical_public_archive_content`; bytes: 62,775; SHA256: `eba4c4e96c23edf6c96fd80544bb2f43b472852b1292ba2b81d78f4b3005ae38`.
- `cookie_handling_field` count=4; byte offsets=218, 37071, 37100, 37364; lines=1, 1, 1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/contests/holiday-xmas05/cookie/winners.html`

Context: `historical_public_archive_content`; bytes: 49,043; SHA256: `70b146473759a8fdd54af7b5901b0329467b01c4c8b097c131df54b9df4cb559`.
- `cookie_handling_field` count=4; byte offsets=218, 36968, 36997, 37261; lines=1, 1, 1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/contests/holiday-xmas05/screenshot/honorable.html`

Context: `historical_public_archive_content`; bytes: 66,899; SHA256: `47a5db4a3acffb51122150087cfb49a92794d4696fda2fcbd73502814c59fc29`.
- `cookie_handling_field` count=3; byte offsets=37186, 37215, 37479; lines=1, 1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/contests/holiday-xmas05/screenshot/winners.html`

Context: `historical_public_archive_content`; bytes: 49,312; SHA256: `afd1befb4eb2cfa6e986ce64e0623a03bfd51b8c1868be40ec1cc819cf759816`.
- `cookie_handling_field` count=3; byte offsets=37151, 37180, 37444; lines=1, 1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/contests/holiday06/winners-cookie.xml`

Context: `historical_public_archive_content`; bytes: 73,603; SHA256: `6144ac2511a3101f1c5d27f9a40d653b7df23c3b1d9a0b59c6c7e7dee67af15c`.
- `cookie_handling_field` count=123; byte offsets=2133, 7525, 9181, 9817, 10461, 11126, 11789, 12466, 13133, 13808, 14917, 24765, 32505, 33120, 34762, 35419, 36063, 36714, 37381, 38046; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/contests/holiday06/winners-screenshot.xml`

Context: `historical_public_archive_content`; bytes: 67,874; SHA256: `168425e389d1fa1488968f5e177aac8fe814425c8ad4fd0466bb4b39c4d24803`.
- `cookie_handling_field` count=5; byte offsets=53346, 53366, 53609, 57268, 57332; lines=1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/contests/holiday07/winners-dessert.xml`

Context: `historical_public_archive_content`; bytes: 63,485; SHA256: `46a1dc53b614b3fce84d700007392de5adf75a2f9bac6e720c83458d14e35b8d`.
- `cookie_handling_field` count=2; byte offsets=50727, 54848; lines=1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/contests/holiday07/winners-screenshot.xml`

Context: `historical_public_archive_content`; bytes: 63,611; SHA256: `4e52ba4c5cb8cc572a78a4005d081c43dbd0d6f18a264ffc3b32cd07baa76ae9`.
- `cookie_handling_field` count=2; byte offsets=50814, 54980; lines=1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/contests/index.html`

Context: `historical_public_archive_content`; bytes: 92,279; SHA256: `0b23887c75e7b06ac2f6e2c7791e0b62f539127d73bef07361da0a748aba7bf9`.
- `cookie_handling_field` count=10; byte offsets=46577, 46639, 46828, 46880, 48012, 62009, 62243, 62291, 62458, 62487; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/index.xml`

Context: `historical_public_archive_content`; bytes: 125,086; SHA256: `916f4e7a6f16eae739bd709fa0c96d5fbe41461697e902fe8ad02813af402fa5`.
- `cookie_handling_field` count=10; byte offsets=54299, 57922, 61310, 63824, 66897, 70132, 72572, 75412, 78129, 80828; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/info/basics/factions/darkmoon/buffs.html`

Context: `historical_public_archive_content`; bytes: 52,005; SHA256: `a87449eabd3e0c82abce08dd06892e4f1752b6b1d2d5a7c8407ec86ba8efa52a`.
- `cookie_handling_field` count=1; byte offsets=43499; lines=1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/info/basics/mounts/special.html`

Context: `historical_public_archive_content`; bytes: 80,857; SHA256: `5514fe417d0d5bdaa141777f9c45af734ab0b98c2df834f56361103cc4935ed1`.
- `credential_literal_assignment` count=3; byte offsets=32806, 32887, 32971; lines=1, 1, 1; fields=token; literal status=literal_candidate_requires_review; classification=historical_public_archive_content
  - Review: `resolved_noncredential`; public/default or fixture class=`fixed_historical_public_markup`; authentication privilege=`False`; reason: Three variables named avtoken/abtoken/warsongtoken hold public HTML tooltip labels for in-game battleground tokens; their literals are markup, not authentication material.

### `offline/site/info/events/winterveil/index.html`

Context: `historical_public_archive_content`; bytes: 62,607; SHA256: `65d76f15b54a68fece938e80022714af59a6a53d180256261216c1efbe269528`.
- `cookie_handling_field` count=1; byte offsets=47767; lines=1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/insider/06/interview.html`

Context: `historical_public_archive_content`; bytes: 52,349; SHA256: `b8711647af80e763e82e75b5d0833c1c29e538f9da5f167f746b412cacee90cc`.
- `cookie_handling_field` count=1; byte offsets=42625; lines=1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/new-hp/js/functions.js`

Context: `historical_public_archive_content`; bytes: 27,567; SHA256: `71841c30555a5b9caa3c1925fdf0134999f27e67e518adf2661af66d46847e5a`.
- `cookie_handling_field` count=13; byte offsets=5384, 5792, 7294, 7421, 7701, 7746, 7755, 7837, 7880, 7889, 8431, 8537, 9002; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/new-hp/layout/layout.xsl`

Context: `historical_public_archive_content`; bytes: 63,776; SHA256: `72023113f52778f0a3cb80579700ac19c62c0f1b3bc1df47b2e3c88cdffad1f1`.
- `cookie_handling_field` count=1; byte offsets=21919; lines=1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/news/wow-news-01-2006.html`

Context: `historical_public_archive_content`; bytes: 68,476; SHA256: `deb430d16b27bac663f6a8b3f6171155150bd9b3196971af8c091b93069f098f`.
- `cookie_handling_field` count=5; byte offsets=56543, 56572, 56671, 56782, 57316; lines=1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/news/wow-news-12-2005.html`

Context: `historical_public_archive_content`; bytes: 79,001; SHA256: `506eb215d8c53e02fa6478500b4a26949b4b7d85536247b8b9a99a06ea6b5ae4`.
- `cookie_handling_field` count=4; byte offsets=63241, 63687, 63891, 64035; lines=1, 1, 1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/pvp/tournament/tabcontent.js`

Context: `historical_public_archive_content`; bytes: 8,498; SHA256: `62f26f01c6e7eb868519fa6063859f8eb2a29ea6ad576c17f698b2f2ffacc49b`.
- `cookie_handling_field` count=5; byte offsets=1845, 1877, 1900, 2028, 2073; lines=1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/shared/wow-com/includes-client/detection.js`

Context: `historical_public_archive_content`; bytes: 14,163; SHA256: `da06d82c4e3c302df76fcd3160bd78e8dab293f92bde32b6f4033d30ee0125cd`.
- `cookie_handling_field` count=2; byte offsets=12197, 12250; lines=1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content
- `cookie_literal_assignment` count=1; byte offsets=12197; lines=1; fields=document.cookie; literal status=literal_candidate_requires_review; classification=historical_public_archive_content
  - Review: `resolved_noncredential`; public/default or fixture class=`fixed_historical_cookie_feature_probe`; authentication privilege=`False`; reason: document.cookie receives a fixed browser-capability probe value and is immediately read into is_cookie; it grants no authentication privilege.

### `offline/site/shared/wow-com/includes-client/wow.js`

Context: `historical_public_archive_content`; bytes: 11,510; SHA256: `2fc0bb2aac01c2067abb6c5c1b876c0a1676bf33da686a52f91b7e56e3a6f1e8`.
- `cookie_handling_field` count=2; byte offsets=7316, 7724; lines=1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/toplist/includes-client/js/logic.js`

Context: `historical_public_archive_content`; bytes: 47,479; SHA256: `1c0a50ff5fd1af19663b925e502c3a3b2dab0eb905874d95966e8bf35504eabe`.
- `cookie_handling_field` count=3; byte offsets=222, 347, 768; lines=1, 1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `offline/site/wrath/js/detection.js`

Context: `historical_public_archive_content`; bytes: 14,163; SHA256: `da06d82c4e3c302df76fcd3160bd78e8dab293f92bde32b6f4033d30ee0125cd`.
- `cookie_handling_field` count=2; byte offsets=12197, 12250; lines=1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content
- `cookie_literal_assignment` count=1; byte offsets=12197; lines=1; fields=document.cookie; literal status=literal_candidate_requires_review; classification=historical_public_archive_content
  - Review: `resolved_noncredential`; public/default or fixture class=`fixed_historical_cookie_feature_probe`; authentication privilege=`False`; reason: document.cookie receives a fixed browser-capability probe value and is immediately read into is_cookie; it grants no authentication privilege.

### `offline/site/wrath/js/functions.js`

Context: `historical_public_archive_content`; bytes: 8,896; SHA256: `fd5eb5a78a01954325107da1b905d514a4af6850fa2181f91d5e571cde28636b`.
- `cookie_handling_field` count=2; byte offsets=5123, 5716; lines=1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `research/final-gap-closure-20261012/final-build/targets.json`

Context: `repository_source_or_metadata`; bytes: 4,109,891; SHA256: `a4900bb989c3395e6ab10ef4442e4ddc591f361e8b14d29446e54a0344624345`.
- `cookie_handling_field` count=256; byte offsets=355391, 355505, 355621, 355747, 356097, 356512, 356627, 356744, 356871, 357221, 357637, 357752, 357869, 357996, 358346, 358762, 358877, 358994, 359121, 359471; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/final-gap-closure-20261012/nonimage-final-reconciliation.json`

Context: `repository_source_or_metadata`; bytes: 140,754; SHA256: `0df25d3502f9b03917b4ff4b4d6ca9fceff59bb2da7e15bdfcc344ffa1d06ce0`.
- `cookie_handling_field` count=1; byte offsets=77197; lines=1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/gallery-recovery-20261014/karazhan/sanitized-summary.md`

Context: `repository_source_or_metadata`; bytes: 1,387; SHA256: `8d9e7423660da2eb62a3e71088325352955a795250e6733b311bbbdde678ed1f`.
- `cookie_handling_field` count=1; byte offsets=1280; lines=1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-pages-20261013/browser-pages-qa-final-2/browser-validation.json`

Context: `repository_source_or_metadata`; bytes: 472,299; SHA256: `bae339b684b70ab148ecd24547d3f074cd755a058156326c185029c168395463`.
- `cookie_handling_field` count=12; byte offsets=390547, 390654, 390759, 390938, 391045, 391150, 391664, 391771, 391876, 393866, 393975, 394082; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-pages-20261013/browser-pages-qa-final-3/browser-validation.json`

Context: `repository_source_or_metadata`; bytes: 627,183; SHA256: `2081081e2e07d4cc873f568e86892d3d4dea61f1ecfbb17383f5849bf4ebcc17`.
- `cookie_handling_field` count=12; byte offsets=546277, 546384, 546489, 546668, 546775, 546880, 547394, 547501, 547606, 549596, 549705, 549812; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-pages-20261013/browser-pages-qa-final-4-retry/browser-validation.json`

Context: `repository_source_or_metadata`; bytes: 625,017; SHA256: `1b589e021679dfce7b0cc9096ff5bdea24b886f63b7b88d64c1c7c8d529c47d5`.
- `cookie_handling_field` count=12; byte offsets=546277, 546384, 546489, 546668, 546775, 546880, 547394, 547501, 547606, 549596, 549705, 549812; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-pages-20261013/browser-pages-qa-final-4/browser-validation.json`

Context: `repository_source_or_metadata`; bytes: 632,846; SHA256: `c1981260bb06d4024d376ca423f05006e176d62d312c7dfc44f68b5dd470a578`.
- `cookie_handling_field` count=12; byte offsets=546277, 546384, 546489, 546668, 546775, 546880, 547394, 547501, 547606, 549596, 549705, 549812; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-pages-20261013/browser-pages-qa-final-5/browser-validation.json`

Context: `repository_source_or_metadata`; bytes: 625,008; SHA256: `0096e783046a1d90b628f978284524acc510626e3e2af41535b4d3de9e836d44`.
- `cookie_handling_field` count=12; byte offsets=546277, 546384, 546489, 546668, 546775, 546880, 547394, 547501, 547606, 549596, 549705, 549812; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-pages-20261013/browser-pages-qa-final/browser-validation.json`

Context: `repository_source_or_metadata`; bytes: 516,311; SHA256: `ac2caf6c66caef5e35a5795ca867c26a63af7c69fca1ca91ff39e3cb753345b7`.
- `cookie_handling_field` count=12; byte offsets=390547, 390654, 390759, 390938, 391045, 391150, 391664, 391771, 391876, 393866, 393975, 394082; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-pages-20261013/checkpoint-staged-hygiene.json`

Context: `repository_source_or_metadata`; bytes: 5,927; SHA256: `4ad3b6d3408fa046f4c64904fb4c2b153c2672206b0481b2174efca4b851bad1`.
- `cookie_handling_field` count=3; byte offsets=4839, 4846, 4866; lines=1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-pages-20261013/main-staged-hygiene.json`

Context: `repository_source_or_metadata`; bytes: 35,383; SHA256: `38c201d0542b1f95f37a29e14e49bd0c0c224cab8eb4271bd6fdead473cdbc0c`.
- `cookie_handling_field` count=39; byte offsets=1373, 1380, 1400, 3907, 3914, 3934, 6104, 6111, 6131, 8307, 8314, 8334, 11441, 11448, 11468, 13638, 13645, 13665, 15833, 15840; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-pages-20261013/publish-final-prepare-report.json`

Context: `repository_source_or_metadata`; bytes: 909,074; SHA256: `50276a243c710fe2b2d8b50ea50087eaa09626964e6ddbf9112125cce07eee84`.
- `cookie_handling_field` count=32; byte offsets=125522, 134449, 134558, 134892, 135400, 135510, 135621, 135732, 135843, 135954, 136065, 136176, 136287, 136398, 136509, 136619, 136729, 136840, 136951, 137062; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-pages-20261013/publish-prepare-report.json`

Context: `repository_source_or_metadata`; bytes: 909,065; SHA256: `cbbfe3c363914e2c748a6fec36dc250803761859a8f3babf8f807c4691426d4f`.
- `cookie_handling_field` count=32; byte offsets=125522, 134449, 134558, 134892, 135400, 135510, 135621, 135732, 135843, 135954, 136065, 136176, 136287, 136398, 136509, 136619, 136729, 136840, 136951, 137062; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-pages-20261013/resource-checkpoint-hygiene.json`

Context: `repository_source_or_metadata`; bytes: 4,079; SHA256: `c05fd6028a41d6ac805e7ae0aafee3324e28a95ad9a44b4630bd2d651d585445`.
- `cookie_handling_field` count=9; byte offsets=1334, 1341, 1361, 2625, 2632, 2652, 3923, 3930, 3950; lines=1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-pages-20261013/root-export-acceptance.json`

Context: `repository_source_or_metadata`; bytes: 3,692,041; SHA256: `b322b052802266ca885e29ca3fe907c216624b7752c7662ab77f3de1870f79b8`.
- `cookie_handling_field` count=121; byte offsets=1647, 2158, 7862, 7869, 7889, 9387, 9394, 9414, 58401, 58408, 58428, 561217, 599986, 600732, 600739, 600759, 600931, 601675, 601682, 601702; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-pages-20261013/root-export-initial-check.json`

Context: `repository_source_or_metadata`; bytes: 3,691,169; SHA256: `7cf1674183498f9dd80506f13ed9f038604c99e3c54ee86d8142c838e8a39028`.
- `cookie_handling_field` count=118; byte offsets=1647, 2158, 8515, 8522, 8542, 57529, 57536, 57556, 560345, 599114, 599860, 599867, 599887, 600059, 600803, 600810, 600830, 601718, 601725, 601745; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-pages-20261013/root-export-pre-browser-fixes.json`

Context: `repository_source_or_metadata`; bytes: 3,692,041; SHA256: `b322b052802266ca885e29ca3fe907c216624b7752c7662ab77f3de1870f79b8`.
- `cookie_handling_field` count=121; byte offsets=1647, 2158, 7862, 7869, 7889, 9387, 9394, 9414, 58401, 58408, 58428, 561217, 599986, 600732, 600739, 600759, 600931, 601675, 601682, 601702; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-pages-20261013/root-pages-tree-acceptance.json`

Context: `repository_source_or_metadata`; bytes: 4,538,511; SHA256: `6237a3b583171b244984fb1b9c5d810ff4a1385a56bf32a7da2949d229b0ab0d`.
- `cookie_handling_field` count=119; byte offsets=7153, 7160, 7180, 8780, 8787, 8807, 68500, 68507, 68527, 688476, 736335, 737081, 737088, 737108, 737381, 738125, 738132, 738152, 739141, 739148; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-publication-20261012/candidate-files.json`

Context: `repository_source_or_metadata`; bytes: 952,504; SHA256: `15dfe7dcae55f25ede31010ad22963ad276afb76c57333a869d163343b501486`.
- `cookie_handling_field` count=64; byte offsets=283, 339, 406, 473, 541, 610, 679, 748, 817, 886, 955, 1024, 1093, 1162, 1231, 1299, 1368, 1437, 1506, 1575; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-publication-20261012/compression-analysis.json`

Context: `repository_source_or_metadata`; bytes: 2,854,019; SHA256: `49dec13b70b92c5c57df402e6580f2a23e9c70bac490d7c6033c3132162063e7`.
- `cookie_handling_field` count=32; byte offsets=492774, 521337, 521671, 523004, 523341, 523679, 524017, 524355, 524693, 525031, 525369, 525707, 526045, 526381, 526719, 527056, 527394, 527732, 528070, 528408; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-publication-20261012/full-tree-hygiene.json`

Context: `repository_source_or_metadata`; bytes: 8,105,282; SHA256: `6dbf5bbef0a3bd088db61e0445e15e15e3e081fa24eebfef5b8fa67ac7fcf44d`.
- `cookie_handling_field` count=159; byte offsets=434, 463, 11455, 11462, 11482, 13542, 13549, 13569, 23162, 23169, 23189, 26266, 26273, 26293, 138912, 138919, 138939, 1246924, 1330228, 1330235; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 32618, 32618, 32618; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-publication-20261012/full-tree-hygiene.md`

Context: `repository_source_or_metadata`; bytes: 20,145; SHA256: `0381023970cf1ef7ff7d7f454a260956d6625649bc37de3f18b90ba264fa9429`.
- `cookie_handling_field` count=13; byte offsets=756, 1062, 1101, 1141, 1162, 1618, 4210, 4592, 5729, 11897, 13141, 19567, 19781; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-publication-20261012/full-tree-hygiene.py`

Context: `repository_source_or_metadata`; bytes: 26,205; SHA256: `7e1805b05a065d45d663d82b4a506859e93a7695329e348a19e627ab81bf0b64`.
- `cookie_handling_field` count=18; byte offsets=2139, 2592, 5402, 5512, 5519, 5964, 5971, 5991, 6069, 6088, 20410, 20439, 22009, 22522, 22561, 22601, 22622, 23118; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-publication-20261012/git-root-acceptance.json`

Context: `repository_source_or_metadata`; bytes: 2,085; SHA256: `818bca7aca5caad99576d280ffe21258f05d378cb742676d2f4049d2c6354db9`.
- `cookie_handling_field` count=1; byte offsets=612; lines=1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-publication-20261012/publication_hygiene.json`

Context: `repository_source_or_metadata`; bytes: 17,049; SHA256: `499f6e61070f692e0ca5a8684f13d066fd79b1fa7b8fb6a3ea38e64d63c0d492`.
- `cookie_handling_field` count=28; byte offsets=3402, 3466, 3541, 3616, 3692, 3769, 3846, 3923, 4000, 4077, 4154, 4231, 4308, 4385, 4462, 4538, 4615, 4692, 4769, 4846; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-publication-20261012/publication_hygiene.md`

Context: `repository_source_or_metadata`; bytes: 2,009; SHA256: `45629ae7720e8893149fb56bd28dee282cde6fdc822af9e9a450cfdfc444d749`.
- `cookie_handling_field` count=8; byte offsets=800, 807, 860, 1000, 1011, 1078, 1184, 1526; lines=1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-publication-20261012/publication_hygiene.py`

Context: `repository_source_or_metadata`; bytes: 35,869; SHA256: `3f3986ef3efb955fde212e11c98ac96029820f5160b00185c825e43d6cbcf6d5`.
- `cookie_handling_field` count=31; byte offsets=381, 2514, 3124, 3131, 3833, 3840, 4003, 4014, 10119, 10151, 16612, 16629, 16664, 16674, 27457, 27464, 27547, 30490, 30497, 30946; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-publication-20261012/release-cookie-review.json`

Context: `repository_source_or_metadata`; bytes: 165,138; SHA256: `765f81007734169e3e8dd8455e7fc309f3b72f4dc360eee76409a1f0a9664baf`.
- `cookie_handling_field` count=491; byte offsets=1150, 9449, 9900, 13052, 14145, 15713, 22469, 25624, 28528, 28565, 28607, 28686, 28718, 28760, 28872, 28949, 29017, 29079, 29149, 29209; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-publication-20261012/release-cookie-review.md`

Context: `repository_source_or_metadata`; bytes: 3,038; SHA256: `98d6fdc6c970ee0b5618dc0477e89cecf574077e4cacf9cd0002ba56c2b1eaa1`.
- `cookie_handling_field` count=17; byte offsets=10, 311, 642, 704, 750, 1108, 1352, 1504, 1603, 1655, 1698, 1735, 1780, 1815, 1845, 2872, 2959; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-publication-20261012/release_cookie_review.py`

Context: `repository_source_or_metadata`; bytes: 36,038; SHA256: `a6708cb95784f0d80122c905885cef9698180febd6ec1001e2e2b4dfaac6cbda`.
- `cookie_handling_field` count=46; byte offsets=33, 163, 1360, 1371, 3091, 3866, 3921, 3968, 3978, 6665, 7872, 7914, 7967, 7994, 8039, 8073, 8099, 8133, 8143, 8170; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-publication-20261012/runtime-package-verification.json`

Context: `repository_source_or_metadata`; bytes: 2,814,465; SHA256: `a6ae9a8035678ab618b509a0eaa268ae31718d44d6ad10194947fbbca5de2276`.
- `cookie_handling_field` count=32; byte offsets=428329, 457232, 457571, 458921, 459262, 459604, 459946, 460288, 460630, 460972, 461314, 461656, 461998, 462339, 462679, 463020, 463362, 463704, 464046, 464388; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/historical-exhibits-20261014/publish-prepare.json`

Context: `repository_source_or_metadata`; bytes: 913,255; SHA256: `5760740b2b5bd609ed33786cf8ddb77619a5c3780fbd48fd0befd43d0d930a17`.
- `cookie_handling_field` count=32; byte offsets=125532, 134459, 134568, 134902, 135410, 135520, 135631, 135742, 135853, 135964, 136075, 136186, 136297, 136408, 136519, 136629, 136739, 136850, 136961, 137072; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/navigation-gaps-20261015/wayback-missing/query_missing.py`

Context: `repository_source_or_metadata`; bytes: 40,320; SHA256: `0122d23be6ac94b7e137ee8be0a22a2ae7c95039ad9cc3873620399ebe76b64c`.
- `cookie_handling_field` count=4; byte offsets=27511, 32746, 32758, 34736; lines=1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/navigation-gaps-20261015/wayback-missing/sanitized-summary.json`

Context: `repository_source_or_metadata`; bytes: 8,393; SHA256: `1d5b659f5a81c88188aeaf4f8454a71b74537870f3efdcd2a3ed7b2f984e67bf`.
- `cookie_handling_field` count=2; byte offsets=8323, 8335; lines=1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/navigation-gaps-20261015/wayback-missing/sanitized-summary.md`

Context: `repository_source_or_metadata`; bytes: 2,599; SHA256: `d681baefadfa83b5ac8d77f1108c90b37199170c404d1a3408a94bd24f411177`.
- `cookie_handling_field` count=1; byte offsets=2460; lines=1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/offline-2008/full-recovery/round-105-final-full-capture-map-validation.json`

Context: `repository_source_or_metadata`; bytes: 15,753,206; SHA256: `54d032f6754e466fc8bbed4480a6b04ecae3a5adcb5143b812daa70769a138dd`.
- `cookie_handling_field` count=32; byte offsets=216580, 218273, 223363, 3181507, 3294760, 3296537, 3298315, 3300093, 3301871, 3303649, 3305427, 3307205, 3308983, 3310761, 3312539, 3314314, 3316091, 3317869, 3319647, 3321425; lines=1, 1, 1, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/offline-2008/full-recovery/round-108-8304-full-browser-validation.json`

Context: `repository_source_or_metadata`; bytes: 3,282,401; SHA256: `58f680bc38167b85ad2e540b9a9be62fe14c22a975c5c4c435b12d9134c957df`.
- `cookie_handling_field` count=118; byte offsets=262048, 262595, 262672, 263586, 264134, 264209, 268199, 268741, 1712701, 1712968, 1713052, 1713243, 1713327, 1713518, 1713602, 1713793, 1713877, 1714068, 1714152, 1714343; lines=1, 1, 1, 1, 1, 1, 1, 1, 19517, 19517, 19517, 19517, 19517, 19517, 19517, 19517, 19517, 19517, 19517, 19517; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/resource-repair-20261015/browser/browser-check-v7.json`

Context: `repository_source_or_metadata`; bytes: 35,318; SHA256: `ac4615617f37ead3f833b1f63dbdde0866f465d69397c9a1779a4a7e359a492c`.
- `cookie_handling_field` count=1; byte offsets=17478; lines=1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/resource-repair-20261015/browser/browser-check-v8-initial-failed.json`

Context: `repository_source_or_metadata`; bytes: 25,398; SHA256: `04ff00c8286146c2490943c240a4d89755fdcdbe5404309c567e61db952646f7`.
- `cookie_handling_field` count=1; byte offsets=17903; lines=1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/resource-repair-20261015/browser/browser-check-v8.json`

Context: `repository_source_or_metadata`; bytes: 34,104; SHA256: `d68b9301357be01ae4ad9e823f6591a850710b66ff0d4a192795ae83dc79b86b`.
- `cookie_handling_field` count=1; byte offsets=18330; lines=1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/resource-repair-20261015/browser/browser_check.js`

Context: `repository_source_or_metadata`; bytes: 56,417; SHA256: `8adb73d76310494a8f2f4e3bcb7a62b39855dd6301132134566e63d26fd18357`.
- `cookie_handling_field` count=2; byte offsets=30748, 30756; lines=1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/resource-resume-20261013/round002/sanitized-summary.md`

Context: `repository_source_or_metadata`; bytes: 3,025; SHA256: `e0359f6dc73bedd8cd26ac1003c53dc0ad7d44b46faa550985061334e676439e`.
- `cookie_handling_field` count=1; byte offsets=142; lines=1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/resource-resume-20261013/round003/run_round003.py`

Context: `repository_source_or_metadata`; bytes: 44,056; SHA256: `d53e251586fa4fa75d388977a6f96aa7c2da5b84b2891bac6a09d5eb96519e6a`.
- `cookie_handling_field` count=1; byte offsets=32799; lines=1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/resource-resume-20261013/round003/sanitized-summary.md`

Context: `repository_source_or_metadata`; bytes: 1,362; SHA256: `a6334c515340bc18d0b605403ad50dc4a8c6de2924c14a60879187f6d596cbb1`.
- `cookie_handling_field` count=1; byte offsets=85; lines=1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `tests/test_resource_candidate_filter.py`

Context: `fixed_fixture_or_example`; bytes: 6,646; SHA256: `08adf2158a817a10140d80c60ac8d088565d3fcfa1cee2e1a209a3b5804c99c9`.
- `url_userinfo_value` count=1; byte offsets=4516; lines=1; fields=n/a; literal status=n/a; classification=fixed_fixture_or_example
  - Review: `resolved_noncredential`; public/default or fixture class=`fixed_negative_test_fixture`; authentication privilege=`False`; reason: The userinfo URL is an intentional invalid candidate in a unit test. Assertions require it to be rejected from the request list; it is not used for authentication or network access.

### `tools/historical_exhibits.py`

Context: `repository_source_or_metadata`; bytes: 38,754; SHA256: `2130986d2e76ec746c40b94a26bfabe56072feb23cab02b29947a4869b56b47e`.
- `cookie_handling_field` count=1; byte offsets=5287; lines=1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `tools/offline_mirror.py`

Context: `repository_source_or_metadata`; bytes: 100,491; SHA256: `8171683dc6b74237d3a655697c9930932fe863f8200685f16da8d4c29c1c635a`.
- `cookie_handling_field` count=2; byte offsets=30290, 30771; lines=1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `tools/wayback_pooled_transport.py`

Context: `repository_source_or_metadata`; bytes: 22,156; SHA256: `1bdb0656906134f2bd77178925f1c0215e5c2334ad22d9fb74f801c289f314e7`.
- `authorization_field_without_value` count=5; byte offsets=1681, 3363, 3680, 3779, 11130; lines=1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

## Archive-resource classification

Binary matches are still scanned in full. When a path is present in `offline/build-manifest.json`, its record contains the manifest section, kind/role and source/derived SHA samples, classifying it as a manifest-backed archive resource rather than silently treating historical bytes as repository credentials.

## Limits

Pattern matches crossing chunk boundaries use a 131,072-byte overlap; all bytes are nevertheless hashed and read. This is a shape scan, not proof that a human-readable string is an active credential. Any nonzero candidate value requires human review before upload.
