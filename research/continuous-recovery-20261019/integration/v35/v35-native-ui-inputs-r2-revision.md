# v35 native UI input R2 revision

R1 (`v35-native-ui-inputs.json`, SHA
`645f3c98a5c7dbc94bfb3d79b6da05eef697bf9d88e5a1fe7f9528dbaa5a4502`) searched
only for literal image paths.  That left 23 accepted news images without a
source-page reference because Source15 stores them as
`missing-image.svg` markers whose `requested` value is percent-encoded.

R2 is additive and reads exactly these already-bound Source15 pages:

* `news/wow-news2004.html` — 23 exact marker references in static
  `postContainer` articles; these are classified as static displays with no
  invented toggle.
* `news/rss-10-2007.xml` — the direct Beowulf image reference at line 2244,
  inside `div.news-expand#news10-15-07-904`.

The R2 extractor matches each accepted original URI exactly after HTML/query
decoding.  It produced 24/24 references: 23 marker references, one direct
reference, 23 static postContainer displays, and one native toggle target
(`news10-15-07-904`).  It performed zero network requests and no export.

Files and hashes:

* `extract_v35_native_inputs_r2.py` — generated extractor.
* `v35-native-ui-inputs-r2.json` — 49,832 bytes, SHA
  `bce40e2d16d86bfd0a1c90c4d57c98b94ebff3255d85bc0b60a4a0b211f15d3d`.

The frozen proposal's phrase `pre-anchor policy` refers to the primary-image
window `2008-01-01..2008-05-12T21:00:44Z`.  The already accepted supplement
closure separately permits its explicit pre-2008 captures, anchor-after-2008
captures, and the recorded 2010 supplement entries; the new v35 supplement
map is empty.  This date-range clarification is recorded here without
rewriting the frozen proposal.

Two preparation failures remain preserved separately:

* `preparation-failure-loader-collision/`: the first retry passed the entire
  old closure as its own collision baseline.  The correction validates the
  old closure with empty baselines and checks only the new delta against old
  routes/static paths.
* `preparation-failure-later-supplement/`: the next retry applied the primary
  `2008-01-01..anchor` restriction while revalidating an accepted v34
  supplement captured at `20100810173046`.  The correction uses the already
  accepted v34 later-supplement policy for the old closure and keeps the new
  empty supplement map unchanged.

Neither failure performed network access or export, and neither changed the
frozen v35 maps/preflight/proposal.
