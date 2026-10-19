# Narrow Toplist compatibility fix

This directory records the approved source-aware repair. The production source tree and accepted v35/v36 outputs were not exported or rewritten.

`tools/toplist_compat.py` recognizes only these exact Source15 routes and hashes:

- `/toplist/includes-client/js/prototype.js`, source SHA `4efde4e87b2db7b8cb6b81f70ab4972c3cfbcd7d329d0752ad223abe67fa9120`: return the source text unchanged and bypass both generic JavaScript rewrite passes.
- `/toplist/includes-client/js/logic.js`, source SHA `1c0a50ff5fd1af19663b925e502c3a3b2dab0eb905874d95966e8bf35504eabe`: replace exactly five escaped `src=\"/toplist/images/pixel.gif\"` values via `localizer.localize(..., context="image")`, preserving the surrounding JavaScript/HTML escaping.

Any route outside these two remains on the existing `mirror.rewrite_script` plus `rewrite_root_literals` path. A route/hash/text drift or replacement-count mismatch raises through `PagesExportError`; there is no fallback to the unsafe generic path.

The focused tests exercise the real Source15 bytes through `export_pages`, compare the Prototype byte-for-byte, require exactly five logic replacements, run Node syntax checks on both generated scripts, and cover route/hash/count guards and unrelated-route pass-through.
