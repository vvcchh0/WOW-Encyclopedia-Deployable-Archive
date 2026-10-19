# Rank 99 local GIF review

This directory contains a read-only review of the two already-saved rank-99
replay bodies from `frontier-news20e`. It does not copy raw headers or cookies,
create a public copy, alter the old plan/output, or make HTTP requests.

Run locally with:

```text
python -X utf8 research/continuous-recovery-20261019/network/frontier-news20e-rank99-local-review/review_rank99.py
```

The report parses the saved exact CDX response, binds each replay to its exact
timestamp/digest/Memento/Link, computes SHA-1/SHA-256, and checks every Pillow
frame plus `Image.verify()`. The corrected source contract is `image/gif`,
Pillow `GIF`, with `all_gif_frames=true`. The 20080402082404 body is valid and
matches its `CEULE...` CDX digest. The 20051221010011 body is also a valid GIF
with the same bytes, but does not match its `PD63...` CDX digest and is not a
candidate for acceptance.
