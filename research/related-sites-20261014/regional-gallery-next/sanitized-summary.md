# Direct-first archive transport

Selected `18` entities and accepted `0` (`0` bytes) in `272.047` seconds.

Direct attempts: `18`; proxy attempts: `18`; chosen direct: `0`; chosen proxy: `0`.

The original run completed the selected batch before the final-failure stop rule was added. Its audited classes were `18` direct transport timeouts, `17` proxy HTTP 429 responses, and `1` proxy transport timeout. No image entered the source map.

CDX `length` is retained as metadata only; it is not compared with decoded JPEG body length. The corrected runner stops after three consecutive final failures of the same class, tightens each request to the remaining deadline, counts partial timeout bytes, and moves accepted raw bodies instead of copying them.
