# Non-gallery closeout v49-r3

Generated `2026-10-21T12:23:45.464941Z` from the local audit receipts, accepted v41/v42/v45/v46
browser receipts, the independently accepted v46 259-path target manifest, the
v49 route/provenance files, and the accepted local route-review correction. This
records observed local states and accepted missing-target observations; it is not
a site-wide crawl or a claim about unobserved dynamic states.

The final initial-browser receipt contains **7** page records although the
requested batch was described as 10 pages. The closeout keeps the seven real
records and records the discrepancy in `summary.json`; it does not invent
three pages.

`page-coverage.csv` contains one row per canonical non-gallery route after
deduplicating exact logical routes and `.xml`/`.xml.html` aliases. The accepted
v41 Flash pages, v42 five-page BlizzCast reader, v45 topic pages, and v46 nine
class pages are retained with their receipt references. The v45 contest page and
v46 talent pages whose HTTP status was not recorded are marked
`completed_by_accepted_browser_evidence` from their accepted browser receipts;
their blank status fields remain blank and no HTTP 200 is invented.

News illustrations such as `/news/images/06-10/screenshot01.jpg` and
`screenshot02.jpg` remain in scope. Exclusions use path segments for the known
player gallery and Media/screenshot/SSOTD collections. Prototype/intercept
exclusion is applied only when a receipt explicitly sets a prototype/intercept
field; an anomalous `/__offline/` or project-prefixed requested value is kept as
`url_uncertain` when it cannot be identified from evidence. The exclusion basis
is recorded in `summary.json`.

`remaining-targets.csv` distinguishes `still_missing_local` (static/CSS/404 or
accepted v46 target evidence without a v49 entity), `unknown_200_placeholder`
(only a 200 placeholder was observed), and `url_uncertain`. A 200 placeholder
never counts as recovery. `available-unrouted.csv` separately records the exact
case-verified T.gif file present in the v50 output tree while its source route has
a double slash and the output route has one slash. `malformed-navigation.csv`
separately records the accepted anniversary export transform bug; the screenshot
directory itself remains uncollected. The accepted v46 target list is an
observation inventory, not a new browser pass or network request.

`filesystem-crosscheck.csv` records the v49 output-tree case-preserving check for
every remaining `still_missing_local` target. The check does not turn an observed
placeholder into a recovered asset, and it does not claim v51 publication.

No network request was made. Raw headers/cookies/HTML/large DOM payloads were
not copied. v49 is the fixed audit baseline; the route-review evidence is used
only to correct local classification of already-existing output and malformed
navigation. This receipt does not claim v51 publication.

The retained `build_closeout.py` is the local reproducibility helper; its
inputs and output directory are confined to this audit scope.
