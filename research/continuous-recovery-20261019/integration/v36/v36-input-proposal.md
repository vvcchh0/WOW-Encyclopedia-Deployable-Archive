# v36 input proposal

v36 is a preparation-only delta over the locally built and byte-audited v35
closure.  The accepted contest navigation compatibility repair remains bound
through the current exporter and root contest-tool receipt.  The frozen v35
closure is 483 primary plus 100 supplement overlays (583 total), 39 guide
images, and 22 guide previews.

Four root-accepted original-byte source/public-copy batches add 51 primary images totaling
874533 bytes: news16b (16/118033), static20c (7/215352), static20d (9/337596), and news20e (19/203552).
The resulting target is 534 primary, 100 supplement, and 634 total overlays,
with 9092 declared and 9093 actual files. All 51 captures are on the
canonical `www.worldofwarcraft.com` host in the 2008 baseline through anchor;
existing v35 supplements retain their later-capture compatibility policy, while
no new supplement date window is widened.

The map source is limited to the four accepted source/public-copy receipts and
their Git-visible `publication/accepted-images/` paths.  Native page evidence
is separately recorded in `v36-native-ui-inputs.json` from literal Source15
references and actual `news-expand`/`news-collapse` ids.  It is evidence for
the later browser gate, not a browser acceptance result.

`execute_v36.py --go --root-export-go` is the only export entry point.  It
requires a root acceptance gate with exact bindings and post-export
expectations, checks the D: free-space floor and 13:30Z start deadline, and
refuses an existing output, partial, or receipt.  No export, network request,
or publication is performed by this preparation.
