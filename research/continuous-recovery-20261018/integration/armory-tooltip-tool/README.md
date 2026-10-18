# Retired Armory tooltip and runtime injection preparation

Scope is limited to `tools/export_github_pages.py`, `tests/test_retired_armory_tooltip.py`, and this directory. No v30 file, source archive, accepted map, exporter output, Git state, or network resource was modified.

The exact route `/new-hp/js/enhancedtip.js` now has a guarded derived pass that replaces the one complete `requestHTML(thisID)` iframe/document.domain request with the historical exhibit caption. The cached `enhancedXmlTTip` path and all bytes outside that function remain unchanged. A second pass is idempotent; wrong routes, duplicate signatures, and altered guard signatures fail or remain unchanged as specified. The exporter records `retired_armory_tooltip_repaired` and a derivation reason after the existing mirror/script and root-literal passes.

`inject_html_runtime` now uses `_MarkupTokenParser` for actual `head` and `body` start tags. It reparses after head insertion before locating body, so `<head>`/`<body>` text in JavaScript raw text or comments cannot receive the runtime or banner. Existing fallback behavior for documents without a real head/body is retained.

Validation used the bundled Python runtime and Node.js. The focused class ran five tests in 0.405 seconds with exit 0. The earlier module discovery run also completed 37/37 tests with exit 0 after correcting a token `.end` property call. The immutable source `offline/site/burningcrusade/townhall/story.html` was read-only checked: source SHA-256 `47eaa5ff151b32e38f63e7302420c5378aef00740b9b3ac1da8e027cf2627c19`; parsed real body preserved; derived banner/runtime counts were 1/1; banner followed the real body; all six original script blocks were preserved (derived parser count 7 because of the injected runtime script).

This is a tool/test preparation only. No v31 pinning or export was performed; root acceptance is still required before using the new tool SHA.
