# Existing-payload local audit

本审计是 2026-10-20 的 **0 网络**查漏，范围只覆盖：

- `news121..160` 的 40 条可见 missing-marker 原 URL；
- `koreapvp/ss01, ss02, ss06, ss05, ss04, ss07` 六条历史线索。

结论是：46 条精确目标均没有在选定的本地 mirror、backup manifest、offline/acquisition 索引或 resource-recovery source-map 中留下同 URL/同路径 payload 记录；v38 的 46 个直达资源路径也都不存在。没有把 CDX 行、ZIP entry、HTML marker 或计划窗口算作图片 payload。六条 `koreapvp` 的唯一来源仍是 Source15 `wow-news2004.html`（SHA-256 `825a7c5b4c77d75ed10a04908c392735462b8c56135d2deb6c0450d11002c14d`），位于 `A Rumble in the Desert` HTML 注释块；它们是 comment-only 历史线索，不是 v38 可见缺图。

在扩大检查中，冻结的 `news-extension-candidates.json` 前 160 个 active-marker 候选与 7 个既有 network `source-map.json` 交叉得到 95 条已有成功回执（79 条 news、16 条 non-news）。95 个外置 payload 均实际存在，读取总量 1,206,050 bytes；每个均通过 magic MIME、Pillow 全帧解码、长度和 SHA-256 与 source-map 回执比对，且 v38 已有对应直达文件。因此新增“成功但未接入”候选数为 **0**，这些 95 条只作为已接入的历史复核，不得再次排入恢复队列。

机器可读结果在 [audit.json](audit.json)。它保留了每条 active-marker 成功记录的原 URL、source-map 路径与 SHA、capture 时间、target key、payload 路径、MIME、帧数、长度/SHA，以及 46 条主目标的来源行和 dedupe 状态。

使用的精确匹配命令（均无输出）是：

```text
rg -l --fixed-strings --file existing-payloads/target-urls.txt --glob '*.json' --glob '*.jsonl' --glob '!**/*.bin' --glob '!**/*.zip' --glob '!**/raw/**' mirror/20080512 research/acquisition-2008 offline
rg -l --fixed-strings --file existing-payloads/target-paths.txt --glob '*.json' --glob '*.jsonl' --glob '!**/*.bin' --glob '!**/*.zip' --glob '!**/raw/**' mirror/20080512 research/acquisition-2008 offline
rg -l --fixed-strings --file existing-payloads/target-urls.txt --glob '*valid-source-map*.json' --glob '*source-map*.json' research/resource-recovery-2008
rg -l --fixed-strings --file existing-payloads/target-paths.txt --glob '*valid-source-map*.json' --glob '*source-map*.json' research/resource-recovery-2008
rg -l --fixed-strings --file existing-payloads/target-urls.txt --glob 'manifest.jsonl' --glob '*manifest*.json' --glob '!**/*.zip' --glob '!**/raw/**' backups
rg -l --fixed-strings --file existing-payloads/target-paths.txt --glob 'manifest.jsonl' --glob '*manifest*.json' --glob '!**/*.zip' --glob '!**/raw/**' backups
```

复核命令为：

```text
python -X utf8 existing-payloads/run_audit.py
```

没有打开或解压 ZIP，也没有递归读取 raw body。`.scratch/offline-navigation-20261015-v15/build-manifest.json`（约 75 MiB）没有纳入证据；此前一次离线 metadata `rg` 的宽 glob 意外读到了 `offline/build-manifest.json`（73,067,980 bytes）和其它大索引，导致索引候选字节量超过原定 64 MiB 限额。该偏离已在 `audit.json` 明示；这些大索引没有命中，也没有被用作 payload 证据。payload 文件数和 payload 字节限制本身均满足（95 / 1,206,050 bytes）。

未知边界：未解包 ZIP entry、未索引的本地文件、candidate rank 161 以后的候选，以及任何未来 2010/地区 host 变体都没有被提升为恢复候选。若以后处理地区或 2010 记录，必须保留其原 host、capture 时间和 source receipt，不能冒充 2008 美服原图。
