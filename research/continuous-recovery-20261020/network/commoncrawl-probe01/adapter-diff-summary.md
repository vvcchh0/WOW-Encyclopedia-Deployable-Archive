# Common Crawl probe01 preparation

This packet is an independent-provider metadata probe for `CC-MAIN-2008-2009`. It keeps the accepted V3 transport policy as a frozen reference and reuses the frozen headers parser for status, proxy-connect, and `Retry-After` parsing. The new adapter only builds Common Crawl `output=json`, `limit=100`, exact/prefix URLs and parses JSON lines; it has no ARC or image replay path.

The prepared order is one `collinfo.json` request followed by five index queries: the known news image exact URL, the news image prefix, the frozen Karazhan sourceDirectory prefix, the frozen Black Temple sourceDirectory prefix, and the frozen encyclopedia `index.xml` exact URL. At most 12 actual HTTP attempts are possible, because each logical request is direct first and receives one process-proxy fallback only after a transport failure. A Common Crawl 404 or empty index response is recorded as index/query evidence and is never promoted to an original-image 404.

The package is root-GO gated. Preparation and the offline fixture made zero HTTP requests and wrote no raw response. Execution, if separately authorized, keeps raw HTTP private, enforces the D: floor before each attempt, 20-second child request limits, a 600-second parent watchdog, 5-second request-start spacing, 4 MiB total and 512 KiB per-attempt body caps, no redirects/retries/pagination, and immediate 429/503 stop with at least 120 seconds cooldown.

Pending root review: plan/input/driver/fixture/parent hashes must be copied into a new Common Crawl GO receipt. No Common Crawl or Wayback request is authorized by this preparation packet.
