# Release Cookie Review

This is a bounded, value-free local review. It made no network requests and did not extract ZIP members to disk.

- Existing metadata report: `research/github-publication-20261012/publication_hygiene.json`
- Existing six-ZIP metadata total: `669842264` uncompressed bytes, `11345` Cookie fields, `0` credential-shaped values.
- Existing metadata rows marked truncated/member-error: `4` of `6`.
- Bounded name/domain sample: `97699464` bytes across `6` ZIPs.
- Existing central-directory scope: `6` ZIPs; current artifacts outside that report: `artifacts/WOW_Encyclopedia_20080512_runtime_20261013.zip`.

## Cookie classification

The bounded sample matched response `Set-Cookie` syntax only; it found no request `Cookie` syntax. `wb-p-SERVER` is consistent with Archive playback infrastructure. `wb-cdx-SERVER` and `wb-cdx-nomatch-SERVER` are consistent with Archive/CDX responses. `JSESSIONID`, `login.cookies`, and `perm` are session/preference-like names near both Archive and historical official-site domains; values were not retained and issuer cannot be proven.

Cookie names, field kinds, and nearby domain counts are recorded in the JSON without values. Nearby domains are context evidence, not a definitive issuer mapping.

The precise structured pass sampled `97699464` bytes and found `11124` target-cookie events. It records exact header key names, capture years, and only value-shape classes. Any `unknown_session_value_shape` remains unresolved; no cookie value is printed or stored.
- Header-key mapping by name: `{"JSESSIONID": {"x-archive-orig-set-cookie": 34}, "login.cookies": {"x-archive-orig-set-cookie": 18}, "perm": {"x-archive-orig-set-cookie": 22}, "wb-cdx-SERVER": {"set-cookie": 25}, "wb-cdx-nomatch-SERVER": {"set-cookie": 30}, "wb-p-SERVER": {"set-cookie": 10970, "unparsed-cookie-field": 25}}`.
- Classification by name: `{"JSESSIONID": {"unknown_session_value_shape": 34}, "login.cookies": {"unknown_session_value_shape": 18}, "perm": {"fixed_public_preference_shape": 22}, "wb-cdx-SERVER": {"archive_route_id_shape_only": 25}, "wb-cdx-nomatch-SERVER": {"archive_route_id_shape_only": 30}, "wb-p-SERVER": {"archive_route_id_shape_only": 10995}}`.

## Release scope

Keep `WOW_Encyclopedia_20080512_full_source.zip` as a separate asset for the original 437-file source backup. The offline recovery ZIP contains selected research/evidence members rather than the complete workspace research tree. Keep the 20101203 and reassessment ZIPs separately labeled as historical candidate evidence. The runtime ZIP is outside this existing six-ZIP review and needs its own hygiene scan before release.

## Limits

The report does not claim the nested ZIP or all non-metadata payloads are clean. Existing metadata rows that reached a 512 MiB/member-error boundary remain marked truncated. A value-free Set-Cookie match cannot prove anonymous replay infrastructure versus an origin session cookie; manual release review remains appropriate for those ambiguous fields.
