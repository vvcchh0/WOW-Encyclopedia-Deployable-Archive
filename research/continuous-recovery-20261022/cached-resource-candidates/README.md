# Cached ArchiveCraft resource candidates — first offline pass

This folder records a read-only comparison of cached ArchiveCraft HTML against the v52 remaining-resource CSV. No network access occurred, no media was downloaded, and no project/site/source/Git files were changed.

The only image-source lead strong enough for a fetch-and-compare plan is the Burning Crusade Professions page-title media URL. The cached HTML uses it as the Professions page banner, while the local page at `burningcrusade/townhall/professions.html:556` asks for `/burningcrusade/townhall/images/professions/page-title.png`. The source HTML was observed on 2026-10-21 at `2026-10-21T09:17:32.158665Z` and has SHA-256 `ec244462dce8cee50b4257829b8dd064ec41853be51d0be7d754385d91cfbae7`. This timestamp describes the current HTML response, not a historical 2008 media capture. The image itself remains unfetched and unvalidated; it is a candidate for later visual/hash comparison only.

The cached Bestiary index links to `https://archivecraft.com/townhall/bestiary/dragons-of-nightmare/` at line 1524, but embeds only a generic arrow there. This is a page-acquisition lead, not evidence for any of the 13 missing Four Dragons screenshots. Numeric screenshot filename coincidences and same-basename local images are explicitly rejected in `audit.json`.

The CSV contains 391 exact-missing routes. Exact file/provenance checks found all 391 absent from the anchor tree, Source16 and v52. Semantic candidate review in this first pass focused on four Burning Crusade routes, twelve Encyclopedia icon routes, and thirteen Four Dragons screenshot routes; other families remain outside this bounded pass.

`audit.json` contains source body paths, byte lengths, SHA-256 values, observation timestamps, exact current media/page URLs, local route checks, evidence locators, explicit rejection reasons and remaining verification needs. `extract_cached_page_images.py` is a standard-library parser for the cached HTML bodies; it does not fetch media or copy raw HTML.
