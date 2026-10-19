# v37 input proposal

v37 is a preparation-only delta over the locally built and byte-audited v36
closure. The frozen v36 closure is 534 primary plus 100 supplement overlays
(634 total), 39 guide images, and 22 guide previews. The current exporter is
the accepted Toplist-aware revision, with the historical-exhibit tool pinned
unchanged and the Toplist acceptance receipt bound in this preparation.

Two root-accepted original-byte source/public-copy batches add 21 primary
images totaling 167403 bytes: news20e-rank99-gif (1/27829) and frontier-news20f
(20/139574). The resulting target is 555 primary, 100 supplement, and 655
total overlays, with 9113 declared and 9114 actual files. All 21 captures are
on the canonical `www.worldofwarcraft.com` host in the 2008 baseline through
the existing anchor; no supplement date window is widened.

The map source is limited to the two accepted source/public-copy receipts and
their Git-visible `publication/accepted-images/` paths. The additive browser
ledger records 21 real `postContainer` image references on
`news/wow-news2004.html`, plus a separate Toplist page/script/CSS check. The
two `body.wide` next/previous CSS images are pending until a real visible
Toplist entry is observed; the commented `lion-top` declaration is excluded.
The ledger is evidence for a later root browser gate, not a browser acceptance
result.

`execute_v37.py --go --root-export-go` is the only export entry point. It
requires a root acceptance gate with exact bindings and post-export
expectations, checks the D: free-space floor and the 13:30Z start deadline,
and refuses an existing output, partial, or receipt. The inner export watchdog
is 600 seconds and the outer driver is 720 seconds. No export, network request,
or publication is performed by this preparation.
