# Continuous recovery 2026-10-20 local audit

This directory contains an offline-only handoff for the next authorized network executor. It does not authorize network access. Queue: recovery-queue.json (SHA256 a4f7a8fed2de23fa65864a5d949f9af112694074f87318706c6b8e3ce484f03e). The repository baseline is f84786d4820438213f0610df147fb78c3f0b2af9; published local pages are under .scratch/pages-resources-20261019-v38.

The first executable segment is news-extension ranks 121-140 (20 inputs). Every rank has an active v38 missing-image marker and no direct v38 asset. The frozen candidate manifest reports no historical execution evidence for these ranks; the prior frontier-news20f actual report is recorded only as a ranks 101-120 boundary (20 fresh CDX targets, 40 source responses, zero failure tail), not as evidence for 121-140.

The six Korea PvP URLs are retained as comment_only_historical_clue. In immutable Source15 news/wow-news2004.html they are img src attributes inside the commented A Rumble in the Desert block (lines 2010-2051), and v38 preserves that comment (lines 2015-2056). They are not active visible images and are excluded from the first queue. The original enclosing viewer pages are recorded for indexes 3, 4, 11, 21, 27, and 28; no direct image path is inferred. Three URLs have rows in two old prefix-CDX responses (ss04, ss06, ss07); all six still lack exact per-URL CDX and image replay receipts. The queue supplies pre-anchor and residual late exact windows for a future executor.

The gallery segment lists the first ten open rows in the r3 ledger order: Mechanar, Botanica, Arcatraz, Warsong Gulch, Isle of Quel'Danas, Amani War Bear, Riding Turtle, Swift White Hawkstrider, Qiraji battle tank, and Raven Mount. All use the exact source-directory prefix from the archived gallery page and the residual window 20080512210045..20101207235959. Mechanar's prior receipt is source 503; Botanica and later rows were not queried after the 10b stop. These are index-only prefix requests: no payload replay, filename expansion, resume pagination, or 404 claim.

Counts: A = 6 comment-only candidates, 0 exact-CDX requests, 0 image replays, 3 distinct historical prefix rows; B = 20 priority candidates, 20 active markers, 20 direct assets absent, 0 candidate-specific actual CDX/replay receipts; C = 50 ledger groups, 21 complete/parked, 29 open, 10 next prefixes, 1 prior source-503 group and 28 prior not-queried groups.

Offline checks used:

- git status --short; git rev-parse HEAD; git branch --show-current -> clean baseline, f84786d4820438213f0610df147fb78c3f0b2af9, main.
- Get-FileHash -Algorithm SHA256 on every queue input -> hashes are embedded in source_inputs.
- Select-String on the two news pages -> six exact koreapvp/ssNN.jpg lines and the enclosing comment ranges; no Source15 mutation.
- Bounded exact-path marker checks on v38 news pages and Test-Path for 20 direct asset paths -> 20 active markers, 20 direct files absent.
- Bounded rg -l --fixed-strings over the prior news execution/report surfaces, excluding output/raw/** -> no rank 121-140 CDX/replay evidence; no raw-tree rescan.
- JSON parsing of the addendum and base ledgers -> 50 groups, 21 complete/parked, 29 open; first ten open registry ranks emitted exactly.

Unknowns remain explicit in the queue. A network executor must create fresh request receipts before treating any candidate as available or replayable.
