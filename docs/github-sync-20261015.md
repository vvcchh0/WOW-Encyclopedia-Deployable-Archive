# GitHub 同步与持续恢复（2026-10-15）

本次将 9 个本地提交推送至 `main`，内容提交为 `e6f558061455d60926e855f56f1b681267bfe22d`。随后发布已验收的 v8 派生站点，`gh-pages` 提交为 `7cfe6ac6a82137fc9df0673630e66c09adf03a49`。

## 已发布内容

- MEDIA Screenshot of the Day 补入两张原图，修复日期计算与缺失缩略图的显示。
- 修复 Archived News 的五处旧地址及 Community 菜单分组。
- 恢复试用选择页和 PvP Mini Site 的静态历史展示，修复 WLK 壁纸入口。
- 同步此前的离线地址、脚本兼容和资源检查改动。

详细来源与缺口见 [MEDIA 截图与导航恢复](media-and-navigation-recovery-20261015.md)。Game Guide 的 50 个玩家截图分区仍有 1,684 组原图与缩略图待获取；本次两张 MEDIA 图片属于另一个栏目。

## 验收与发布证据

发布前的 [v8 本地验收](../research/resource-repair-20261015/root-final-acceptance.json)包括 55 项单元测试与 7 个浏览场景。原始 `offline/site` 和冻结清单保持不变。

GitHub Pages 构建报告确认上述 `gh-pages` 提交已构建。2026-10-15 07:16 UTC 完成 [线上核对](../research/github-sync-20261015/pages-acceptance.json)：首页、两张图片、截图脚本、新闻页、两个旧地址、壁纸页、试用页、PvP 页及路由表共 12 个对象均直连取得 HTTP 200，字节与本地 v8 一致，响应类型符合对应内容。

[发布回执](../research/github-sync-20261015/pages-publication.json)保存分支、提交、文件数及推送结果；[核对脚本](../research/github-sync-20261015/verify_pages.py)限定对象数、超时、体积和重定向。验证范围是这 12 个线上对象，不等同于逐页复验全站。

推送前对 `e6f5580` 的全部 8,740 个 Git 文件进行了字节扫描，共 740,009,246 字节。6 个候选匹配经上下文审阅，分别为游戏物品说明、浏览器 Cookie 能力检测和负向测试数据。[扫描报告](../research/github-sync-20261015/full-tree-hygiene.reviewed.md)与[验收回执](../research/github-sync-20261015/hygiene-root-acceptance.json)记录范围和判断，不保存匹配值。

## 原始包与浏览包

已公开的约 502 MB 浏览包保存页面和图片。它的完整性口径是当时已恢复的文件，未取得的图库图片仍是缺口；本次 Pages 更新没有自动替换 Release 中的 ZIP。

约 2.25 GB 的原始恢复包保留了 HTTP 响应与研究证据。之前检查发现响应 Cookie 和历史会话形态字段，尚未完成嵌套内容审阅，也未确认它们是有效凭据。公开原始包需要先处理响应元数据并记录转换过程；Warcraft 图片与网页内容本身不是本次暂缓公开的原因。原包继续按原字节留存。此前检查与压缩安排见 [发布说明](github-publication-20261012.md)和[空间策略](storage-and-compression.md)。

## 后续工作

[持续恢复总账](continuous-recovery-20261015.md)由 GPT-6.1 Sol xhigh 统筹，本地侧栏审计和串行网络批次交给两个执行者。旧盘点中 579 条未分组菜单观察已重新纳入分类，避免把解析器缺少分组误判为无需恢复的页面。

本线程已启用 `wow-8` 自动接续，每 15 分钟检查一次，到北京时间 22:44 截止。检查先读取正在运行的代理和批次，避免重复请求；下载批次按自己的时间和请求上限执行。只有取得新资源、完成修复、出现阻塞或结束时才通知。已验收且适合公开的变更正常提交并推送；原始响应头与未处理恢复包保留在本地。
