# v28 acceptance addendum

The proposal records preparation, before export. The accepted build completed on 2026-10-18 with 8,721 declared files and 8,722 actual files. The full output check and browser retry 4 accepted the build; its 67 additional resources are measured against the online v26 baseline. Static missing-image occurrences fell from 1,901 in v27 to 1,861 in v28; the news subset contains 476 remaining occurrences.

The preparation overlap and recovery are recorded in `../../publication/root-v28-preparation-race-recovery.json`. The original preflight bound by root was restored by its exact prior hash before export. The later preparation receipt and preserved preflight copy describe the same resource inputs with later audit metadata. Neither record grants publication on its own.

Browser retries corrected the verifier's handling of four CSS background icons, asynchronous news-toggle clicks, and the actual page containing the Armory announcement. Exported site bytes were unchanged during those checks. The final browser receipt is `../../publication/root-v28-browser-retry4-acceptance.json` (268 checks passed, no page errors or external requests). The original upgrade artwork remains a noninteractive historical exhibit with a visible caption.
