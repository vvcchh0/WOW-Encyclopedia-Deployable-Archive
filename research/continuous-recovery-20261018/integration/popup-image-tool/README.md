# Historical `popUpOmega` image viewer preparation

This preparation is based on exporter SHA256 `7c3684fb777e9c21b07fe8c8a1be0418810f448e99dd582ed4c9d9c342764dea`. It adds a narrow runtime wrapper for the unique `window.popUpOmega` image helper. The wrapper is installed at startup, after the existing route-map promise, and through the existing 0/250/1000 ms retry points so a legacy script that defines the helper later is covered. A marker on the wrapper and a runtime flag make repeated installation a no-op.

For string arguments that resolve to a raster filename (`jpg`, `jpeg`, `png`, `gif`, `webp`, or `bmp`) or the current project `__offline/missing-image.svg`, the wrapper calls the existing `mapImage` function. It opens the result only when the mapped URL is same-origin and begins with the current project `PREFIX`, using `window.open(mapped, "_blank", "noopener,noreferrer")`. Unknown or external raster URLs therefore open the local missing-image exhibit; they do not navigate to the external URL. Non-image arguments retain the original helper call and receiver/argument list. No other `window.open` call or popup adapter is changed.

The focused Node VM test covers late helper definition, a collected relative image, an `_origins` image, an unknown image, an existing local missing-image placeholder, an external raster URL, non-image and `javascript:` fallback arguments, the feature string, local-prefix enforcement, and repeated scheduled installation. The test also checks that the adapter is not exposed as a new public `__WOWPages` API.

Files in this directory:

- `implementation-diff.patch`: popup-only exporter diff plus the complete new test file, with baseline/result SHA256 values.
- `focused-tests.log`: the final focused test command output, UTC timestamps, exit code, and D-drive checks.
- `verification-receipt.json`: immutable byte hashes, command/result summary, and scope limitations.

No export, network request, map change, version output, commit, or publication was performed. The v30/v31 inputs and outputs remain untouched.
