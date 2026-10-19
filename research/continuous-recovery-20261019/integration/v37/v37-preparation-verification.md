# v37 preparation verification

The v37 input, loader preflight, and additive Toplist/browser plan are frozen and waiting for the root input gate and explicit export/browser GO. The verification JSON records the final file bindings and the two preparation commands. No export, browser run, network request, or publication was performed.

The v37 delta is 21 primary images / 167403 bytes over the accepted v36 closure (534 primary + 100 supplement), producing the expected 555 primary / 100 supplement / 655 total overlay closure and 9113 declared / 9114 actual files. The loader preflight independently returned 555 / 100 / 655, 39 guide images, 22 previews, network 0, and `export_executed: false`; old overlay payloads were byte-checked by the loader.

The browser plan covers the 21 exact news `postContainer` references, Toplist initialization and default-wide navigation/ranking behavior, and two CSS background candidates only after visible local decode. It records zero native toggles and preserves unresolved rows. The outer wrapper remains a draft until root writes `root-v37-input-acceptance.json`; its gate/hash placeholders are intentional and must be bound before any GO.
