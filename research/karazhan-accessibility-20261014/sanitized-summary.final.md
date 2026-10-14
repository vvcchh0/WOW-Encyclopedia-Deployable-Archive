# Karazhan gallery accessibility (final reconciled report)

- Logical curl calls: `56/128` (preflight + target invocations; not the total source HTTP request count).
- Observed source HTTP response blocks: `63`; CONNECT blocks: `55`; redirect blocks: `30`. Timed-out/incomplete chains may have unknown additional source requests.
- Unique targets: `126`; completed `54`; unexecuted `72`; completed+unexecuted `126`; duplicate target requests: `1`.
- Counts: valid_image `0`, 404_wayback_not_archived `32`, other_html `8`, transport_error `14`, unexecuted `72`.
- Groups: full `{'valid_image': 0, '404_wayback_not_archived': 22, 'other_html': 0, 'transport_error': 5, 'unexecuted': 36}`; thumb `{'valid_image': 0, '404_wayback_not_archived': 10, 'other_html': 8, 'transport_error': 9, 'unexecuted': 36}`.
- Stop: `five consecutive transport errors/5xx stop batch`; raw body bytes `155348/67108864`.

## Scope

- Initial cumulative-stop evidence, continuation evidence, and the one duplicate ss8 request are retained and disclosed in JSON.
- `redirect_not_image` is a subtype of `other_html`; guide locations are recorded from saved headers; initial automatic chains requested guide replay URLs, but no completed guide-page body was obtained. Later checks stopped at the image URL capture redirect.
- `actual_capture_timestamp` comes only from Memento-Datetime; requested URL timestamps are hints.
- A 404 or guide redirect applies to that requested URL/capture only and does not establish absence across all dates or the full gallery.
- Raw headers and bodies remain local under `raw/`, `raw-continuation/`, and `raw-continuation2/`.
