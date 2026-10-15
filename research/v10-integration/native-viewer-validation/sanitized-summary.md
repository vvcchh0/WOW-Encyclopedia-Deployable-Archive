# NATIVE-VIEWER-VM-012 sanitized summary

Offline validation only. `simulation=true`; `network_requests=0`; no browser or archive acquisition.

- Node: `v22.22.0`
- VM window: `2026-10-15T10:15:34.794Z` to `2026-10-15T10:15:34.808Z`
- Raw viewer: `8432 B`, SHA256 `43fe3ee08d5006620a34bb06dcb752e639d0c2fcbe156cdc92c1cb456d209f69`
- Derived viewer: `8692 B`, SHA256 `30942827950a0952102a598e39590044398d4f9b0be81f4d58ddd86e4ae9c35e`
- Freeze hashes: exporter `True`, tests `True`, source CSS `True`
- Fresh VM cases: `12/12` passed

## Case evidence

| case | query | opened index | dCurrent/dTotal | screenLink | sentinel | result |
|---|---|---:|---:|---|---:|---|
| `one` | `?s=1` | 0 | 1/13 | `./images/artwork/ss1-hires.jpg` | 0 | PASS |
| `three` | `?s=3` | 2 | 3/13 | `./images/artwork/ss3-hires.jpg` | 0 | PASS |
| `thirteen` | `?s=13` | 12 | 13/13 | `./images/artwork/en_us/ss1-hires.jpg` | 0 | PASS |
| `encoded-three` | `?s=%33` | 2 | 3/13 | `./images/artwork/ss3-hires.jpg` | 0 | PASS |
| `missing` | `(missing)` | 0 | 1/13 | `./images/artwork/ss1-hires.jpg` | 0 | PASS |
| `empty` | `?s=` | 0 | 1/13 | `./images/artwork/ss1-hires.jpg` | 0 | PASS |
| `zero` | `?s=0` | 0 | 1/13 | `./images/artwork/ss1-hires.jpg` | 0 | PASS |
| `negative` | `?s=-1` | 0 | 1/13 | `./images/artwork/ss1-hires.jpg` | 0 | PASS |
| `fourteen` | `?s=14` | 0 | 1/13 | `./images/artwork/ss1-hires.jpg` | 0 | PASS |
| `duplicate` | `?s=3&s=4` | 0 | 1/13 | `./images/artwork/ss1-hires.jpg` | 0 | PASS |
| `unsafe-integer` | `?s=9007199254740992` | 0 | 1/13 | `./images/artwork/ss1-hires.jpg` | 0 | PASS |
| `encoded-sentinel` | `?s=sentinel%3D99` | 0 | 1/13 | `./images/artwork/ss1-hires.jpg` | 0 | PASS |

The native source built `shotList` as common `ss1..ss12` plus locale `en_us/ss1`, with matching `dirList` and `hiResList`; all cases verified one-based query input to zero-based lightbox index and `-hires.jpg` links.

## Source and scope boundaries

- The helper transformed the single approved original fragment at character span `[831, 968]`; prefix/suffix and all four navigation function bodies remained unchanged.
- `eval` was removed from the derived parser fragment; invalid, duplicate, unsafe, and sentinel query values all fell back to one-based shot 1.
- Image and DOM objects were local stubs. The run does not establish browser layout, paint, network image loading, animation, or full exporter integration.

Generated from `source-validation.json` and `vm-results.json`; report update UTC `2026-10-15T10:16:45.985357+00:00`.
