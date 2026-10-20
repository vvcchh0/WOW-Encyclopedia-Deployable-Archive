# Common Crawl ARC01 offline reference comparison

This report reads the private accepted ARC range and the frozen Source15 encyclopedia page. It makes zero HTTP requests and executes no HTML or JavaScript.

- ARC payload: `52400` bytes; SHA1 base32 `J5QKGA7VRIUFZPBPEDKOT6REERJJJJXS`.
- Active literal refs: July 20 HTML `26`, Source15 `26`.
- Actual-only active URLs: `0`.
- Potential new image leads: `0`.
- Classification: **no_genuine_new_restoration_lead**.

The accepted July 20 HTML exposes no same-site image URL absent from Source15; therefore this comparison supplies no genuinely new restoration lead.

Excluded references are recorded by reason in `reference-comparison.json`; ads/social, external hosts, offline rewrites, expression URLs, placeholders, and fragments are not treated as restoration leads.
