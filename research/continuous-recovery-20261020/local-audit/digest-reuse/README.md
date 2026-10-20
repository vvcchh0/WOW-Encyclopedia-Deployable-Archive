# digest-reuse 本地专项

本目录记录一次 0 网络、只读的本地 SHA1 复用审计。目标是把冻结历史 CDX 中的 exact original + HTTP 200 + 图片 MIME + 明确 digest，与 v38 当前已经存在的图片实体做字节级交叉匹配；命中只作为候选，不表示已经执行新的 CDX、Memento 或下载。

运行时间：`2026-10-20T10:59:38.102885+00:00`；网络请求：`0`；CDX 时间上限：`20080512210044`。

输入边界：

- 首批 news121..160：40 个；随后扩大到冻结 R2 ledger 中 host 为 `www.worldofwarcraft.com`、state=`uncovered`、非 dynamic 的静态/新闻 URL：432 个。六个 koreapvp comment-only URL 已排除。
- 读取两个 prefix-CDX：2 个文件、37698 行；其中目标 identity 行 11066，符合时间窗/200/图片 MIME/有 digest 的行 10028。
- v38 provenance 选择了 7135 个 `kind=image` 且 MIME 为 image/* 的实体，实际读 7135 个，SHA1 首轮读取 490376500 bytes；未读 75 MB build manifest，也没有解压 ZIP。
- v38 来源 URL 回溯使用冻结 v38 export gate 列出的 source-map 文件；这些 map 总体约 17008514 bytes，按 source SHA256 绑定 `original`/`logical_url` 与 local path。

结果：

- digest 命中评估 2 条；状态计数：`{"new_reuse_candidate": 2}`。
- 可直接交给 root 复核的 `new_reuse_candidate`：2 条。每条保留目标原 URL、CDX 文件 SHA256/行号/日期/digest、复用 payload 路径、v38 provenance SHA256、已验收 source-map URL/路径，以及 computed SHA1/完整帧验证。
- `audit.json` 中的 `matched_payload_without_accepted_source_url`、`invalid_or_unverified_payload`、`already_present_route` 只作覆盖记录，不作为可整合候选。

复现命令：

```powershell
python -X utf8 research/continuous-recovery-20261020/local-audit/digest-reuse/run_audit.py
```

未知范围：只检查了指定的两个 prefix-CDX 响应；没有把未读的 CDX、raw/ZIP、75 MB build manifest 或网络状态当作 absence 证据。没有修改旧 ledger、Source15、accepted、v38 export 或生产映射。
