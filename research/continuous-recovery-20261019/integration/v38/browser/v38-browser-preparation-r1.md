# v38 browser preparation r1

This directory contains an offline preparation copied from the accepted v37 browser harness/runner. No browser was started and no external request was sent.

## Owned files

- `check_v38_images_toplist_r1.cjs`: v38 loopback harness.
- `execute_v38_browser_r1.py`: 300-second, root-gated runner; it requires a later executable plan and GO receipt.
- `v38-browser-plan-template-r1.json`: non-executable template with the 21 news targets, two CSS targets, and one Toplist target. It deliberately has `output_provenance.sha256: null`; root must create the final plan after `export_v38_once.py` produces the real provenance.

## v38 observation changes

- The loopback server records every URL and status, including requests outside the archive base path and unsupported methods.
- Console records include Playwright locations; errors remain separately counted.
- Toplist date data counts only own eight-digit keys. Prototype members and `emptyTable` rows are excluded, while the zero-date-data and historical missing notice remain explicit pending evidence.
- The exact `#numTablesSelect` `onchange="initLayoutChange(this.value);"` source is bound to the frozen source line. A real visible selector is exercised as `1 -> 2 -> 1` only after the source match; no data is injected.
- CSS rows without a visible `body.wide a.next`/`a.prev` DOM entry are `no_entry`; computed backgrounds are not used to fabricate an entry.
- The mandatory assertions include zero external requests, zero unexpected unrecorded local requests, zero Toplist data HTTP requests, exact news image HTTP/MIME/dimensions, and zero page/console errors.

## Offline validation

```text
node.exe --check check_v38_images_toplist_r1.cjs
python -X utf8 -c "compile(...)"
node.exe check_v38_images_toplist_r1.cjs --preflight --input v38-browser-plan-template-r1.json --result results/preflight-v38-template.json --screenshots screenshots-r1/preflight
```

The preflight must report `browser_started:false`, `server_started:false`, `network_requests:0`, and `template_waiting_for_export:true`.
