# digest-reuse/r2 源链与本地 map 草案

本目录是 `digest-reuse/audit.json` 冻结后的只读补充。按授权读取 Source15 build manifest 一次，只解析 `files` 数组中的两个 exact route；用 manifest 的 `source_base_url`、`source_local_path`、`source_map_path`、source SHA256、时间字段与初版 audit 的 CDX/复用证据完成双来源链。

- Source15 manifest：`.scratch/offline-navigation-20261015-v15/build-manifest.json`，75650378 bytes，SHA256 `d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002`；与 receipt 期望值匹配：`True`。
- 目标记录：2 / 2；files 记录扫描 8357，manifest 只读一次。
- 名义链（初版输入 + 一次 manifest + 小型缓存）metadata bytes：111449583 / 134217728，在预算内：`True`。早期 finalizer 曾重复 hash 同一 source-map 6 次（178751370 bytes），累计读取若计入则超预算；修正后只 stat，不再重复读取。
- 两个 staged payload 是 v38 现有实体的字节副本，放在本地 audit 目录；没有解压或复制历史 ZIP，没有发布或导出。
- `target_cdx_timestamp` 是缺失原 URL 的历史 CDX 行日期；`payload_source_actual_timestamp` 是已保存复用 payload 的原来源捕获日期，二者分开记录。
- `ordernow.jpg` 是历史广告图。后续页面处理由 root 决定；原字节不改。

输出：`source-chain.json` 为完整证据链，`map-draft.json` 为 `method=payload_digest_reuse` 的本地草案，未接入生产映射。
