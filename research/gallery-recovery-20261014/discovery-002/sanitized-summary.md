# Gallery recovery discovery-002 (local)

Anchor: `20080512210044`.

Two directory prefix scopes were checked. Karazhan 2007 returned a complete one-page empty prefix (`0 rows`), so there is no pre-2008 direct entity in that directory. Fishing 2008 returned a complete one-page prefix with `63` rows; its direct-looking `/fishing/ssN.jpg` rows are sibling guide resources, while the gallery's real paths would be `/fishing/ss/ssN.jpg`. Nested `thumbs/` previews and sibling guide resources were excluded.

Direct candidate accounting: Karazhan direct `0`; Fishing direct `0`. Pair selection found `0` complete pairs and selected `0` entities. Downloads attempted `0`, accepted `0`, validation failures `0`, transport failures `0`. This batch added no direct gallery entities.

No entity GET was issued. A small exact fallback sampled Fishing `ss/ss1.jpg`, `ss/ss1-thumb.jpg`, and `ss/ss2.jpg`; all three exact CDX responses were empty. The fourth planned `ss/ss2-thumb.jpg` exact request was stopped before a response and is not treated as an empty result. No Karazhan direct entity was found. Files remain local and were not merged or deployed.

The prefix completeness evidence is the one-page `showNumPages=1` response paired with the full prefix table; no second page exists. The earlier generic `page=1` probe returned `400 page must be smaller than numpages`, which is consistent with that one-page result and was not used as an empty-resource proof. Raw CDX responses are retained only locally; see `entity-source-map.json` and `batch-state.json`.
