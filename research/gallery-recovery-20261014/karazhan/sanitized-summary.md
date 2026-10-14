# Karazhan gallery recovery batch (local)

Anchor: `20080512210044`. Query range: `20080101000000` through `20081231235959`.

The complete prefix query reported one page and 20 rows. Five rows are directory 404 captures; the remaining 15 rows are five captures each for three `thumbs/ssN-thumb.jpg` previews. The dynamic source directory `/info/dungeons/images/karazhan/` has no direct `ssN.jpg` or `ssN-thumb.jpg` row in this prefix result. An exact probe for `ss1.jpg` also returned an empty CDX result.

Downloaded 6 related preview entities; 5 passed replay validation. The accepted files remain under this research directory and have not been merged into `offline/site` or deployed.

Those five accepted records represent three canonical paths and three distinct image contents. Their actual captures are 26–82 minutes after the anchor. The excluded attempt is a local curl output-write failure (exit 23), with no saved response headers or body; it is not evidence of a missing Archive capture or an invalid image.

Validation required HTTP 200, image MIME, JPEG magic, Pillow decode, matching CDX digest, matching replay timestamp, and matching response Content-Length when present. Raw response headers and bodies are retained locally; this summary contains no header or cookie values.

See `entity-source-map.json` for source metadata and `batch-state.json` for every attempt.
