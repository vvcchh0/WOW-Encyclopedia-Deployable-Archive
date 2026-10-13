# Round003 transport probe

This is one transport probe for the previously failed rank-2 entity. It used `curl.exe` through `http://127.0.0.1:7890` with HTTP/1.1, retry count 0, a 15-second connect timeout, a 60-second maximum time, and TLS certificate verification enabled. Headers and the response body were written to local capture files and were not printed.

The target was `https://www.worldofwarcraft.com/visa/reward/images/frame-bot-bg.gif` at Memento timestamp `20080402093145`.

The probe exited `0` with final HTTP status `200`, final MIME `image/gif`, and `4380` downloaded bytes. The Memento date was `Wed, 02 Apr 2008 09:31:45 GMT`, matching the selected timestamp. GIF magic detection and Pillow validation passed; Pillow reported `121x79`.

The observed CDX SHA-1 Base32 digest was `YYIQNSNUKJLO7OOAIWM73Z5EMII2SYXV`, exactly matching the expected CDX digest. Content-Length matched `4380` bytes. The body SHA-256 is `dd3f604b55bb2554c92d67649bb5de4164fedd64c0ec0754226a5baed4395bd5`.

The strict single-probe checks passed. The raw response remains local in `response-body.bin` and `response-headers.txt`; no Round002 files were modified and no additional Archive requests or retries were started. This result is ready for the parent to decide whether to authorize a low-concurrency batch using the proxy.
