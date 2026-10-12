# Warcraft Encyclopedia archival acquisition

## Request and scope

Acquire the latest demonstrably usable, best-covered historical version of Blizzard's original World of Warcraft Encyclopedia from Internet Archive. User-supplied known working entry: https://web.archive.org/web/20080512210044/http://www.worldofwarcraft.com/info/encyclopedia/index.xml . This phase preserves source files and evidence; offline reconstruction and editorial organization are later work.

## Selection and acceptance

Enumerate entry captures and encyclopedia URL captures through the Wayback CDX index. Inspect actual response bodies to reject redirects, errors, empty wrappers, and soft errors even when status is 200. Compare the latest valid historical entry candidates with the known 2008 baseline. Measure coverage against the navigation's article list and recursively referenced encyclopedia resources, plus required shared XSL/CSS/JavaScript/images. Record gaps and timestamp drift; a Wayback date is an anchor, not an atomic site snapshot. Do not claim completeness when index enumeration or dependency closure is incomplete.

Reassessment after the user's 2026-10-10 correction: body integrity and browser usability are separate acceptance dimensions. A selected usable version must also pass normal replay checks with the actual response MIME, including representative linked articles. The 2010-12-03 acquisition remains preserved, but its earlier usable-version selection is withdrawn. Compare the working 2008 baseline, representative resources, and later candidates before any new whole-version claim.

## Preservation decisions

- Retain unmodified HTTP entity bytes from Wayback identity replay (`id_`), the source URL, requested and actual capture times, HTTP metadata, and SHA-256. Firecrawl output is research evidence only and cannot substitute for original source bytes.
- Compress during acquisition, deduplicate payloads by SHA-256, and keep mappings for every logical URL/capture. Avoid an additional full uncompressed copy. Archive errors separately from successful source files.
- Keep the acquisition resumable and bounded. Do not crawl unrelated Blizzard sections, external links, modern redirects, or Wayback interface assets.
- Task storage budget: 14,000,000,000 bytes, including research and compressed outputs. D: must retain at least 10,737,418,240 bytes (10 GiB), with additional write headroom. These interpretations are conservative relative to decimal GB.
- Network requests have finite timeouts, attempt counts, request ceilings and run deadlines. Back off or stop on rate limits and repeated service errors.

## Evidence locations

- `research/inventory/`: original index queries, capture probes and selection evidence.
- `research/baseline/`: user-provided anchor's original response and headers.
- `research/firecrawl-*.json`, `research/cdx-api-documentation.json`: web research results (including failed upstream responses).
- `tools/`: reusable acquisition program, its interface and limits.
- `backups/`: compressed response payloads and per-request manifests.
- A final acquisition report will record the selected anchor, measured coverage, download totals, validation and unresolved gaps.

## Primary interface reference

Internet Archive CDX API documentation: https://raw.githubusercontent.com/internetarchive/wayback/master/wayback-cdx-server/README.md . Prefix queries, date bounds, output fields and resume-key pagination are preferable to an uncontrolled recursive website download.
