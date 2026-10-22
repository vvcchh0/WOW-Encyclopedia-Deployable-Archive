# GitHub Pages v52 Dungeons 20-object comparison

This offline-prepared, root-GO-gated check compares exactly 20 current GitHub Pages objects with accepted local v52 bytes: the Dungeons HTML page, nine full-size screenshots, and ten thumbnails. It does not crawl links or request a sitemap, API list, or dependencies.

`object-manifest.json` pins all URLs, local paths, byte sizes, and SHA-256 values. The page and image references were cross-checked against local HTML and `dungeons-v52-browser-inspection.json` (10 decoded thumbnails, nine previously observed original HTTP 200 responses). The accepted v52 local gate, browser inspection, publication metadata, and existing verifier source hashes are bound in the manifest.

`verify_dungeons20.py` will be a small exact-target wrapper modeled on the object-match record structure of `research/continuous-recovery-20261021/publication/verify_v52_pages.py` and frozen `verify_pages_v32.py`; it retains raw response bytes privately and emits only sanitized object-match metadata. It makes no GitHub build API calls, so only the 20 exact object URLs are in scope.

Only `--execute --go PATH` can issue requests. The expected GO path is `research/continuous-recovery-20261022/root-pages-v52-dungeons20-go.json`. Preparation and offline fixtures make no network requests.

Bounds: 20 logical objects; at most 40 HTTP attempts; 600 seconds total; 30 seconds per attempt; 10-second connect timeout; 6.2-second minimum start spacing; 16 MiB total body bytes; 4 MiB per object. Direct first; process-local `127.0.0.1:7890` fallback only after transport failure. TLS stays enabled; redirects and automatic retries stay off. HTTP 429/503 stops immediately and records at least 120 seconds or longer `Retry-After`; five consecutive transfer failures preserve the failure tail, stop, and set a cooldown at least 120 seconds after the final response end. D: free space must stay above 11,005,853,696 bytes.

Raw bodies, response headers, cookie jars, stderr, and the attempt journal stay private in `runtime/private/`. The public `runtime/object-match-summary.json` contains only object match metadata. No request was made during preparation.
