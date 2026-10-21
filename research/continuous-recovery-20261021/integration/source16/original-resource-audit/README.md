# Source16 original-resource audit

审计时间 `2026-10-21T05:31:07+00:00`–`2026-10-21T05:31:16+00:00`；输入为 Source16 dependency-audit 的 `58` 个静态 `local_missing` 和 `1` 个动态 `bard_idle.swf`。本批只读本地 acquisition metadata、命名 backup manifests、两个 direct raw roots、四个小 Source ZIP 及九个历史备份根的 ZIP 中央目录；没有联网、没有解压历史 ZIP、没有改 Source16/v42/v43。

分类计数：`{'not_found_in_scanned_layers': 32, 'different_path_candidate_only': 27}`。本批没有 exact-route 可恢复实体；`candidate-summary.json` 中有 `269` 个跨路径同 basename 候选对（涉及 `26` 个目标），其中图片候选已用实际字节和 PIL 解码核验。它们只作为地区/同主题来源线索，不替代精确目标。

`curated-inventory.json` 保留每个目标的来源页、原始使用行、证据层、长度/SHA/CRC/图片验证和候选；`curated-inventory.csv` 为精简索引。结果是已列本地层的范围性审计，不推断未查网络来源。
