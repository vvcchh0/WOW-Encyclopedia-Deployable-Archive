# MEDIA -> Screenshots local inventory

Generated from local files on 2026-10-15. This report does not make network requests; saved CDX rows are identified as index evidence and kept separate from payload validation.

## Confirmed MEDIA entry

The current MEDIA menu points to /downloads/ssotd/index.html#latest (offline/site/new-hp/layout/menu.xml:55-58). The legacy navigation tree independently points Media -> Screenshots to /downloads/ssotd/index.html (offline/site/shared/wow-com/includes-client/navtree-main.js:283-286). The page title is WorldofWarcraft.com -> Screenshot of the Day.

This is distinct from the Game Guide Player Screenshot Galleries listed in offline/site/info/index.html:539-591; those pages use /info/.../images/.../ssN.jpg and are summarized below only as a control.

## SSOTD URL and pagination rules

index.html:63-83 computes currentShotNumber from the Date response header of a HEAD anachronos.xml request, then calls addshots(/downloads/ssotd/images/screens, ss, currentShotNumber). The local anachronos.xml body is '<?xml version="1.0" encoding="UTF-8"?>\n<tag>Huh. Seems like it *IS* my time yet, after all.</tag>', so an offline file read cannot recover the server Date or the current total.

ssotd-screenie.js:432-468 constructs full URLs as /downloads/ssotd/images/screens/ssN.jpg and thumbnail URLs by replacing .jpg with -thumb.jpg. The default page size is 12; the UI can switch to 16, 12, or 9. Pagination is client-side and hash-aware; the page is one chronological stream with no category sections.

## Local coverage

Frozen baseline offline/site contains 8304 files. offline/build-manifest.json is 73067980 bytes with SHA-256 397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459. The latest derived directory exists at .scratch/pages-local-maintenance-20261014-v5.

The baseline SSOTD static asset directory contains 8 files ({'.gif': 8}) and 8 Pillow-decoded images. The dynamic screens roots in both baseline and v5 have zero ssN.jpg full images and zero ssN-thumb.jpg thumbnails. This is a local coverage result; it is not a claim that Wayback or the source server has no such objects.

| Route/system | slots or entities | valid local direct images | evidence |
|---|---:|---:|---|
| MEDIA SSOTD /downloads/ssotd/images/screens/ | date-derived, total unavailable offline | 0 full / 0 thumb | index.html:63-83; ssotd-screenie.js:432-468 |
| Game Guide galleries (49 HTML + Zul'Aman underlying page) | 1684 slots; 3368 expected full/thumb entities | 0 full / 0 thumb / 0 pairs | research/github-pages-20261013/gallery-inspection-20261013.md:5-17 |

## Existing saved CDX evidence

No pre-existing local US /downloads/ssotd CDX rows were found in the local scan. The separately authorized parent query is stored under research/media-screenshots-20261015/parent-query/; its empty exact result must remain scoped to that exact URL and range.

The available local control is the EU route /screenoftheday/screenoftheday/: the saved complete-prefix CDX table has 87 rows from 20070101000000 through 20080512210044, including 64 status-200 image rows. Its source-map contains 14 saved JPEG payloads that passed decode validation, covering 20070302101942–20080512205334 across observed host forms wow-europe.com:80, www.wow-europe.com, www.wow-europe.com:80. This related-site evidence is not merged into the US MEDIA count.

## Authorized Wayback window evidence

The parent exact query for /downloads/ssotd/index.html is retained at research/media-screenshots-20261015/parent-query/summary.json and returned valid JSON [] for its stated 2006–2010 scope. The evidence-backed trailing-slash source query returned 648 rows all-time and 520 rows for 2006–2010, including historical 200 HTML captures and later redirects; this explains why the index.html exact empty result cannot be generalized.

The canonical /downloads/ssotd/images/screens/ prefix first page has 1000 valid data rows and a resume token; its two status-200 image rows are ss1314.jpg at 2010-08-10 and ss1336.jpg at 2010-06-02. Four evidence-backed host forms returned the same first-page body and are counted once (1 canonical page). One resume page was fetched with 1000 valid data rows. Prefix pagination is therefore proven incomplete beyond the two saved pages.

Exact CDX for the real path http://www.worldofwarcraft.com/downloads/ssotd/images/screens/ss1314.jpg returned 9 rows, including the status-200 image digest 4AKYT7KIDFUKL2OD6WVGY63CXMXIHGF3 at 20100810173046. The thumb exact control returned valid JSON with 0 rows. Two full-image replay samples were then validated with HTTP 200, Pillow decode, Memento timestamps, and digest match; the filtered prefix returned 2 status-200 image rows.

The two validated 2010 payloads are listed in late-image-source-map.json with their raw replay paths, CDX identity, timestamps, dimensions, SHA-256, and digest-match evidence. sanitized-summary.json and capture-ledger.json provide compact counts while the original raw responses remain under wayback-window/raw/.

Manual inspection of the saved JPEG payloads confirms route-relevant game-scene content: ss1314 shows several blue aquatic/fish-like humanoid characters in a luminous underwater setting (1024x640), while ss1336 shows a dark cavern landscape dominated by glowing magenta-red mushroom-like formations and falling light particles (1200x750). These observations support that the two 2010 rows are real screenshot payloads rather than redirect or index artifacts; they are classified as post_2008 supplements.

## Provenance and limits

The static page, JS, navigation, manifest, existing gallery inventory, and saved regional CDX files are the source records. URL variants appear in the query plan only when a local page/script or saved index provides the path; a CDX row is not treated as a downloaded image until replay yields HTTP 200, image MIME, JPEG magic, and decode success.
