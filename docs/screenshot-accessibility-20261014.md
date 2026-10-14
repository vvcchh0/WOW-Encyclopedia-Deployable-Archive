# 截图资源可及性检查（2026-10-14）

本轮确认 Wayback 的原始图片回放仍部分可用。WLK、TBC 截图和 Karazhan 预览图均能取回；Karazhan 与魔导师平台各一张图库原图的请求返回 404，页面提示未存档。索引接口本轮未取得有效数据，尚不能判断缺图在其他日期、协议或域名下的捕获情况。

本次工作回应用户在 Wayback 页面上也观察到截图缺失的反馈，检查对象包括 Game Guide 的玩家截图图库和更广泛的官网截图栏目。图库本地实体盘点见[资源补充记录](resource-recovery-20261014.md)，本轮聚焦源站回放能否实际返回图片。

## 实际回放结果

原始地址均为 `http://www.worldofwarcraft.com` 下列路径。成功项使用已有来源记录中的实际捕获日期；缺口项以重建基准 `20080512210044` 发起回放请求。

| 样本 | 原始路径 | 实际捕获时间（UTC） | 代理回放结果 | 图片验证 |
|---|---|---|---|---|
| Karazhan 嵌套预览图 | `/info/dungeons/images/karazhan/thumbs/ss2-thumb.jpg` | 2008-05-12 21:26:53 | 200，3,347 字节 | JPEG，150×110 |
| WLK 截图 | `/wrath/images/screenshots/ss11.jpg` | 2008-04-02 05:01:17 | 200，100,444 字节 | JPEG，700×518 |
| TBC 截图 | `/burningcrusade/images/screenshots/ss102.jpg` | 2008-04-02 04:17:47 | 200，198,273 字节 | JPEG，800×640 |
| Karazhan 图库原图 | `/info/dungeons/images/karazhan/ss1.jpg` | 无捕获时间响应头 | 404，4,705 字节 HTML | Wayback 未存档提示页 |
| 魔导师平台图库原图 | `/info/dungeons/images/magisters/ss1.jpg` | 无捕获时间响应头 | 404，4,708 字节 HTML | Wayback 未存档提示页 |

三张成功图片均完成 Pillow 解码，长度、SHA-256 与已有本地原件一致，响应的 `Memento-Datetime` 也与请求捕获日期相符。它们是可及性对照，本轮新增独立图片数为零。

两份 404 响应没有 `Memento-Datetime`，因此 `20080512210044` 只作为请求中的时间提示保留，不能将它记成已捕获的 404 时间。结果说明这两次回放没有取得原图；不据此推断所有日期或全部 50 个图库均无图片。

## 连接与索引

所有请求先走 direct，失败后使用现有代理 `127.0.0.1:7890`。本轮 direct 均超时，三张有效图片均由代理取得；本轮未遇到 429。

| 接口对照 | direct | 代理 | 可用于判断什么 |
|---|---|---|---|
| archive.org robots | 超时 | 200 | 部分站点连接可用 |
| CDX，已知预览图的单 URL 查询 | 超时 | 建立 CONNECT 后进程超时 | 未取得 JSON 索引，源站 HTTP 状态未知 |
| 官方 Availability API，已知预览图 | 超时 | 503，`Internet Archive: Temporarily Offline` HTML | API 本次不可用，不能据此判定资源不存在 |

请求分三组完成：基础对照 6 次、四张图片的 direct/代理回放 8 次、Availability API 2 次，共 16 次 HTTP 尝试，保存响应体合计 323,547 字节。API 返回 503 后停止该接口请求。TLS 验证保持开启，未改动全局代理、DNS 或 hosts。先前的 429 连接诊断保留在[历史记录](network-recovery-20261014.md)，与本轮结果分别解释。

## 离线选样与覆盖范围

[离线选样清单](../research/screenshot-accessibility-20261014/plan.json)整理了 16 个目标：3 张 Karazhan 预览图、3 张 WLK 截图、5 张欧服每日截图，以及 5 个 Raid/Dungeon 原图或缩略图缺口。11 张已有图片全部完成本地解码和来源长度、摘要比对；其中 5 项找到精确匹配的已保存 CDX `200/image` 行，其余 CDX 行状态保留为未知。来源摘要中的 CDX digest 与保存回放的 HTTP 状态分别记录。

线上实际测试上表 5 个图片 URL，其中 TBC 截图作为额外对照选入。其余选样未联网测试。本轮没有完成全部图库、日期、域名或嵌套来源包的遍历，也没有改动镜像或生成新浏览包。

已有截图能通过精确捕获日期取回，说明 Wayback 图片服务并非整体不可用。两个图库原图缺口同时存在于本地和本次 Wayback 回放，后续优先查找它们的捕获记录、其他官网主机和路径变体。待索引接口能提供有效数据后再扩大查询，不能用当前接口失败替代缺图结论。

## 证据与复现入口

- [离线选样说明](../research/screenshot-accessibility-20261014/summary.md)与[生成脚本](../research/screenshot-accessibility-20261014/inventory/build_plan.py)。
- [基础连接及已知图片回放](../research/screenshot-accessibility-20261014/probe001/sanitized-report.final.json)、[简表](../research/screenshot-accessibility-20261014/probe001/sanitized-summary.final.md)。
- [四张图片回放](../research/screenshot-accessibility-20261014/probe002/sanitized-report.final.json)、[简表](../research/screenshot-accessibility-20261014/probe002/sanitized-summary.final.md)及[请求清单](../research/screenshot-accessibility-20261014/probe002-plan.json)。
- [Availability API 记录](../research/screenshot-accessibility-20261014/availability001/summary.json)。
- [独立图片对照验证](../research/screenshot-accessibility-20261014/control-parent-validation.json)与[汇总验收](../research/screenshot-accessibility-20261014/accessibility-acceptance.json)。

原始响应头、响应体和初始报告保存在维护者本地。纳入 Git 的 `.final` 报告已离线更正日期格式、CONNECT 状态与资源新增计数的解释；更正没有重发请求。请求脚本保留以便复查方法，不应在接口不可用时循环重跑。
