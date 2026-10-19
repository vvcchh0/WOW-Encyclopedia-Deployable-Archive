# v35 input proposal

v35 is a preparation-only delta over the locally built and byte-audited v34
closure.  The accepted contest navigation compatibility repair remains bound
through the current exporter and root contest-tool receipt.  The frozen
closure is 459 primary plus 100 supplement overlays (559 total), 39 guide
images, and 22 guide previews.

Two root-accepted original-byte news batches add 24 primary images totaling
191943 bytes: frontier-news04 (4/41536) and frontier-news20a (20/150407).
The resulting target is 483 primary, 100 supplement, and 583 total overlays,
with 9041 declared and 9042 actual files.  All 24 captures are on the
canonical `www.worldofwarcraft.com` host in the 2008 baseline through anchor;
no pre-anchor or supplement policy is widened.

The map source is limited to the two accepted source/public-copy receipts and
their Git-visible `publication/accepted-images/` paths.  Native page evidence
is separately recorded in `v35-native-ui-inputs.json` from literal Source15
references and actual `news-expand`/`news-collapse` ids.  It is evidence for
the later browser gate, not a browser acceptance result.

`execute_v35.py --go --root-export-go` is the only export entry point.  It
requires a root acceptance gate with exact bindings and post-export
expectations, checks the D: free-space floor and 13:30Z start deadline, and
refuses an existing output, partial, or receipt.  No export, network request,
or publication is performed by this preparation.
