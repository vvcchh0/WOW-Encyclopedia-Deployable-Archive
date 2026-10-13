# 2026-10-13 部署后的资源补齐

GitHub Pages 发布并在线验收后，按用户要求继续本地资源获取。已发布站点使用冻结的 8,304 条路由与来源清单；新增实体先独立保留、核验，尚未合并进该快照，站点的 3,358 条缺口统计因此仍对应原冻结版本。

## 候选与证据复用

从当前缺口 SSOT 检查既有精确索引和失败证据，先排除已经完成、已知错误内容及没有新依据的旧失败。首批 50 项经去重后没有新请求需求；继续向后筛出 50 个没有完整 exact-2008 证据的官方图片 URL，保留在 [Round002 计划](../research/resource-resume-20261013/round002-plan.md)。HTTP 与 HTTPS 逻辑 URL 保留原样，比较与重复检查使用 host/path/query。

CDX 查询覆盖 2008 全年、exact、所有 status/MIME，不使用 collapse 或只取成功行的过滤。完整索引取得后才选择图片实体，优先基准之前最近的 2008 捕获；晚于基准的素材单列。请求失败不作为空索引证明，本轮没有获取 pre-2008 素材。

## Round002 实际获取

50 个索引查询取得 20 个完整结果，其中 19 个有记录、1 个为空；另 30 个发生 TLS EOF。19 个实体尝试中 1 个通过全部核验、18 个 TLS EOF。成功文件为 `visa/reward/images/border-bot.gif`，捕获时间 `20080402093136`，1,235 字节、124×17 GIF；CDX 摘要、Memento、MIME/magic、Pillow 和 SHA-256 均匹配。

证据 ZIP 共 97 个成员、112,410 字节，已独立核验 CRC 与成员 SHA。原始响应头、CDX 与实体仅存本地，公开仓库提交[不含响应头或正文的运行摘要](../research/resource-resume-20261013/round002/sanitized-summary.md)。已有来源包、镜像文件及历史 ZIP 均未覆盖。

旧 runner 的普通 FetchError 分支没有实现连续三错自动 stop，且预先提交了全部待执行 futures，因此没有按该停批约束提前中止。这个偏离已保留在摘要中。后续续传改用串行调度，并在第三个连续同类错误后不再启动待执行项。

## 传输复核与续传

48 个失败均为 `SSL: UNEXPECTED_EOF_WHILE_READING`，没有 HTTP 状态，不能据此判定 Archive 缺少文件。换用 curl、HTTP/1.1 与本机已有代理完成单项实验：原失败的 `frame-bot-bg.gif` 得到 HTTP 200，捕获 `20080402093145`，4,380 字节、121×79 GIF，严格核验全部通过。[探针记录](../research/resource-resume-20261013/round003-transport-probe/probe-validation.md)提供独立证据。

据此，Round003 只对上述失败项换传输方式续传，复用已成功的探针实体、既有完整索引及已下载文件。采用单并发、每项本轮最多一次请求、1 秒间隔、60 秒请求超时、20 分钟截止及连续三错停批；每实体 16 MiB、索引 4 MiB、累计响应 128 MiB。工作区上限 14,000,000,000 字节，D 盘保留 11,000,000,000 字节加 256 MiB 余量。

## 本轮结束结果

Round003 在 `2026-10-13 14:15:35 UTC` 结束，共发出 47 个 curl 请求：30 个 CDX 查询中 29 个得到完整全年空结果、1 个超时；17 个实体 GET 全部通过严格核验，另复用已成功的 probe 1 个。Round003 的 18 张图片加上 Round002 的 1 张，共取得 **19 个去重图片 URL**，捕获时间均为基准之前的 2008 年。没有进行第四轮或 pre-2008 下载。

原 50 个候选的最终状态为：19 个图片 URL 已取得、30 个具有完整 exact-2008 全年空证明、1 个仍为查询超时。空证明不表示更早年份也没有捕获；超时也不作为空证明。

Round003 证据 ZIP 共 261 个成员、466,043 字节，CRC、成员 SHA 与原始实体摘要通过核验。新增图片尚未写入冻结镜像或上线快照；可从本地 `round002/entity-source-map.json` 与 `round003/entity-source-map.json` 继续进行整合。

参见 [Round003 脱敏运行摘要](../research/resource-resume-20261013/round003/sanitized-summary.md)、[串行续传工具](../research/resource-resume-20261013/round003/run_round003.py)及[主代理独立核验](../research/github-pages-20261013/resource-root-acceptance.json)。全部 raw CDX、响应头、实体和两个证据 ZIP 留在本地，不公开含 Cookie 字段的原始响应元数据。
