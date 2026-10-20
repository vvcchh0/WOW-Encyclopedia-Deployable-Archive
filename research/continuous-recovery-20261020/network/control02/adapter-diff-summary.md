# control02 preparation summary

Prepared 2026-10-20 in the current recovery window. This package made zero network requests and has no raw or execution output.

## Package

- plan: `plan.json` — SHA-256 `926ef4fb6f10c44d29ef5f88cee808ec91e4c95b87445f6dcfba61acc6f38bd0`, 5130 bytes
- driver: `control02_driver.py` — SHA-256 `0105adc16cbfade33cd4f619557d9ebeb7b5df6a695edfaa0ce5480976e78274`, 25354 bytes
- parent watchdog: `parent-execute-once.py` — SHA-256 `7109d742dd07acdb744ce87ede34b6985f7548cb85d07acd0c7aa6af8031b3e3`, 5281 bytes
- offline fixture: `fixture-results.json` — SHA-256 `7292ff85da9a16e28911029e03b7b2cc057e17b67adcba9a9dff17fe565f0a31`, 831 bytes
- input bindings: `input-bindings.json` — SHA-256 `9ef353cba468f1350cd71c86333cdce76212c2d47f54f6326a1ac9e4bebcafb0`, 2795 bytes
- offline validation: `offline-validation.json` — SHA-256 `d791d00fbcac319ab55e276ba89485090030880ed5e98d96b0da7f76b76bc8b3`, 1924 bytes

## Scope changes from control01

- New identity `CONTROL-02-20261020`, target key `CONTROL-02-known-news-image-exact-cdx`, current-day output paths, and future GO path `research/continuous-recovery-20261020/publication/root-control02-execute-go.json`.
- Reused the accepted bounded control01 transport/parser behavior and preserved the 180-second parent watchdog, 120-second child cap, 1 MiB caps, direct-first order, 5-second cadence, stop codes, disk floor, no pagination, no redirects, and no image replay.
- Rebound the latest failure to control01's private report SHA `c10060a5484e4f0092660087c15d72f04f13928efde4f1181b864f31083a93f3`, root source-acceptance SHA `2420341b37eff901ecbe0288a12f738cd5380067e35a5c7f32268874730fd372`, and parent receipt SHA `155f817b421446cb99af007a27e9687371cd1737d0439eb7d5c918c88b1371f9`; the observed stop remains proxy HTTP 429.

## Offline evidence and pending gate

The reused driver's fixture passed 14/14 cases with zero network requests and no raw writes. Python compilation passed. `input-bindings.json` intentionally does not self-bind the fixture; root GO must bind the final fixture hash, driver, plan, and bindings hashes. The package remains unexecuted pending a separate root GO.
