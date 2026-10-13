# Full tracked-tree publication hygiene scan

Pinned Git tree: `b8d655ca51c4e4f73101e8e774eb46b37bda9c4f` (verified expected HEAD: `True`).
The scan is byte-complete over the exact tracked Git tree, including binary files. It uses `git ls-tree` and `git cat-file --batch`; it does not inspect mutable untracked files and does not access the network.

## Coverage

- Tracked files: 8,408; scanned: 8,408; skipped: 0; read/object errors: 0
- Tracked/scanned bytes: 652,421,785 / 652,421,785
- Complete byte scan: `True`; every file record includes Git object ID, byte length and SHA256.
- Findings in 39 files; matched values are never emitted.

## Credential-shape result

Candidate value-shaped matches (excluding handling-only Authorization/Cookie fields): **5**; exact reviewed unresolved credential findings: **0**.

- `authorization_field_without_value`: 5 matches in 1 files
- `cookie_handling_field`: 1333 matches in 37 files
- `cookie_literal_assignment`: 2 matches in 2 files
- `credential_literal_assignment`: 3 matches in 1 files

Cookie handling code is separated from cookie literal assignments. Historical `document.cookie` or `Set-Cookie` handling is not called a credential; any literal assignment remains a review candidate. Fixed fixtures/examples and historical public archive content are classified by path/context in the JSON without publishing values.

## Match locations

The JSON lists category, counts, byte offsets, line numbers where the file is text-like, field names, literal status, and context class. It intentionally contains no matched secret, token, password, cookie value, or line text.

### `artifacts/offline-20261012-recovery-package-verification.json`

Context: `repository_source_or_metadata`; bytes: 5,930,419; SHA256: `bcfea500b9ba4b6734c71b3a4de0452f926a1239e9cfe3b3f3529170d04f951d`.
- `cookie_handling_field` count=32; byte offsets=392794, 409516, 409715, 410504, 410704, 410905, 411106, 411307, 411508, 411709, 411910, 412111, 412312, 412513, 412713, 412913, 413114, 413315, 413516, 413717; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `artifacts/offline-20261012-recovery-portability-shortpath-check.json`

Context: `repository_source_or_metadata`; bytes: 4,638,237; SHA256: `b953c5b15862a0e6b0aec4e87fbd8bad9274675143ecea3b6a866df9891d1348`.
- `cookie_handling_field` count=32; byte offsets=262292, 274751, 274901, 275494, 275645, 275797, 275949, 276101, 276253, 276405, 276557, 276709, 276861, 277013, 277164, 277315, 277467, 277619, 277771, 277923; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `docs/resource-recovery-2008.md`

Context: `repository_source_or_metadata`; bytes: 56,308; SHA256: `9171ba22aef3595cbf6608e67f735252df0b3f9e20f35593adf31211dfea1e4a`.
- `cookie_handling_field` count=1; byte offsets=24852; lines=1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

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

### `offline/site/wrath/js/functions.js`

Context: `historical_public_archive_content`; bytes: 8,896; SHA256: `fd5eb5a78a01954325107da1b905d514a4af6850fa2181f91d5e571cde28636b`.
- `cookie_handling_field` count=2; byte offsets=5123, 5716; lines=1, 1; fields=n/a; literal status=n/a; classification=historical_public_archive_content

### `research/final-gap-closure-20261012/final-build/targets.json`

Context: `repository_source_or_metadata`; bytes: 4,109,891; SHA256: `a4900bb989c3395e6ab10ef4442e4ddc591f361e8b14d29446e54a0344624345`.
- `cookie_handling_field` count=256; byte offsets=355391, 355505, 355621, 355747, 356097, 356512, 356627, 356744, 356871, 357221, 357637, 357752, 357869, 357996, 358346, 358762, 358877, 358994, 359121, 359471; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/final-gap-closure-20261012/nonimage-final-reconciliation.json`

Context: `repository_source_or_metadata`; bytes: 140,754; SHA256: `0df25d3502f9b03917b4ff4b4d6ca9fceff59bb2da7e15bdfcc344ffa1d06ce0`.
- `cookie_handling_field` count=1; byte offsets=77197; lines=1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-publication-20261012/candidate-files.json`

Context: `repository_source_or_metadata`; bytes: 952,504; SHA256: `15dfe7dcae55f25ede31010ad22963ad276afb76c57333a869d163343b501486`.
- `cookie_handling_field` count=64; byte offsets=283, 339, 406, 473, 541, 610, 679, 748, 817, 886, 955, 1024, 1093, 1162, 1231, 1299, 1368, 1437, 1506, 1575; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-publication-20261012/publication_hygiene.json`

Context: `repository_source_or_metadata`; bytes: 11,863; SHA256: `4d351d4713e01843e0ad169018ef21e979cc229282bd9eaf9ba70fdd764f9683`.
- `cookie_handling_field` count=26; byte offsets=3402, 3466, 3541, 3616, 3692, 3769, 3846, 3923, 4000, 4077, 4154, 4231, 4308, 4385, 4462, 4538, 4615, 4692, 4769, 4846; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-publication-20261012/publication_hygiene.md`

Context: `repository_source_or_metadata`; bytes: 1,733; SHA256: `34ac880165fc021f32ee28e7d322553cfba748b840851dc1f8fc3ebbce3546d1`.
- `cookie_handling_field` count=7; byte offsets=577, 584, 724, 735, 802, 908, 1250; lines=1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/github-publication-20261012/publication_hygiene.py`

Context: `repository_source_or_metadata`; bytes: 21,214; SHA256: `3b36478d02f6609f5c5ee2ebc9a9b124727396d06bdf1ed2a8945c3185140806`.
- `cookie_handling_field` count=21; byte offsets=381, 2395, 3005, 3012, 9028, 9060, 15750, 15757, 15840, 16921, 16928, 17377, 17784, 17791, 19067, 19074, 19354, 19365, 19432, 19538; lines=1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/offline-2008/full-recovery/round-105-final-full-capture-map-validation.json`

Context: `repository_source_or_metadata`; bytes: 15,753,206; SHA256: `54d032f6754e466fc8bbed4480a6b04ecae3a5adcb5143b812daa70769a138dd`.
- `cookie_handling_field` count=32; byte offsets=216580, 218273, 223363, 3181507, 3294760, 3296537, 3298315, 3300093, 3301871, 3303649, 3305427, 3307205, 3308983, 3310761, 3312539, 3314314, 3316091, 3317869, 3319647, 3321425; lines=1, 1, 1, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344, 58344; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `research/offline-2008/full-recovery/round-108-8304-full-browser-validation.json`

Context: `repository_source_or_metadata`; bytes: 3,282,401; SHA256: `58f680bc38167b85ad2e540b9a9be62fe14c22a975c5c4c435b12d9134c957df`.
- `cookie_handling_field` count=118; byte offsets=262048, 262595, 262672, 263586, 264134, 264209, 268199, 268741, 1712701, 1712968, 1713052, 1713243, 1713327, 1713518, 1713602, 1713793, 1713877, 1714068, 1714152, 1714343; lines=1, 1, 1, 1, 1, 1, 1, 1, 19517, 19517, 19517, 19517, 19517, 19517, 19517, 19517, 19517, 19517, 19517, 19517; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `tools/offline_mirror.py`

Context: `repository_source_or_metadata`; bytes: 99,637; SHA256: `0c538db90b2e3bb444ebe93013b10b77c56df83b6eb485396025763ab6f85482`.
- `cookie_handling_field` count=2; byte offsets=29436, 29917; lines=1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

### `tools/wayback_pooled_transport.py`

Context: `repository_source_or_metadata`; bytes: 22,156; SHA256: `1bdb0656906134f2bd77178925f1c0215e5c2334ad22d9fb74f801c289f314e7`.
- `authorization_field_without_value` count=5; byte offsets=1681, 3363, 3680, 3779, 11130; lines=1, 1, 1, 1, 1; fields=n/a; literal status=n/a; classification=repository_source_or_metadata

## Archive-resource classification

Binary matches are still scanned in full. When a path is present in `offline/build-manifest.json`, its record contains the manifest section, kind/role and source/derived SHA samples, classifying it as a manifest-backed archive resource rather than silently treating historical bytes as repository credentials.

## Limits

Pattern matches crossing chunk boundaries use a 131,072-byte overlap; all bytes are nevertheless hashed and read. This is a shape scan, not proof that a human-readable string is an active credential. Any nonzero candidate value requires human review before upload.

## Manual classification of all five candidate values

- `offline/site/info/basics/mounts/special.html`, `credential_literal_assignment`, lines 330-332 / offsets 32806, 32887, 32971: fixed historical public HTML tooltip markup for game-token labels (`avtoken`, `abtoken`, `warsongtoken`); no authentication privilege.
- `offline/site/shared/wow-com/includes-client/detection.js`, `cookie_literal_assignment`, line 251 / offset 12197: fixed historical browser-cookie capability probe, immediately read into `is_cookie`; no authentication privilege.
- `offline/site/wrath/js/detection.js`, `cookie_literal_assignment`, line 251 / offset 12197: same fixed historical browser-cookie capability probe; no authentication privilege.

All five candidates are classified as resolved non-credentials. No test fixture was used for these findings; the first is historical public markup and the latter two are historical feature-detection defaults. Values are intentionally omitted. Machine-readable status is `unresolved_credential_findings=0`.
