# 官网档案持续恢复总账（2026-10-15）

本轮按历史侧边栏逐项检查，时间预算截止 2026-10-15 14:44 UTC（北京时间 22:44），有证据的工作队列耗尽或出现真实外部阻塞时可提前结束。用户已明确授权自动接续，根代理已通过应用工具启用本线程 heartbeat `wow-8`，每 15 分钟检查一次，调度截止 `2026-10-15T14:44:25Z`。当前批次继续执行；heartbeat 接收时先检查运行中的代理、任务队列和网络批次状态，不中止有效任务、不重复提交批次、不启动第二名网络执行者。本总账不创建额外后台循环或新聊天。入口是[已有恢复与验收记录](media-and-navigation-recovery-20261015.md)。当前已验收的派生版为 `.scratch/pages-resources-20261015-v8`，冻结的 `offline/site` 与 `offline/build-manifest.json` 不改写；清单 SHA256 为 `397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459`。

## 总账结构

[初始总账](../research/continuous-recovery-20261015/ledger.initial.json)从已有多代菜单盘点生成，每条菜单观察保留独立标识、分组、名称、原始地址、菜单文件与行号。旧盘点口径为 588 条内容观察、653 条排除观察。启动时复查发现，其中 **579 条 `Legacy menu` 只是旧解析器未分组**，包含 `/news/rss-05-2008.xml` 等真实内容地址，不能据此排除。已生成[范围修正检查点](../research/continuous-recovery-20261015/ledger.scope-review.json)，将这 579 条恢复为待分类审计；原来的 588 条口径继续保留以便比较，74 条明确的结构、业务或外部观察另行记录。初始快照保留其原始状态并由修正检查点取代。

每条观察分别记录页面状态、资源状态、交互状态、来源证据、关联任务与下一动作。旧盘点针对 v5 派生版，其覆盖状态保留在 `prior_inventory_status`；当前状态须核对 v8 后更新。页面可达不等于图片、Flash 或历史交互完整，补充素材的实际捕获日期单独记录。

07:25 UTC 已完成[独立侧栏验收](../research/continuous-recovery-20261015/sidebar-acceptance.json)并生成[当前总账](../research/continuous-recovery-20261015/ledger.current.json)。旧 `Legacy menu` 按真实源文件分组：`menu1_var.js` 的 44 条归 News，`menu3_var.js` 的 511 条归 Game Guide，晚期 XML 的 24 条归其 Account、Forums、Support 类目。保留 `prior_group` 和分组理由，不改写旧盘点。

当前任务和验收条件保存在[任务队列](../research/continuous-recovery-20261015/tasks.json)。各批次在独立目录保存候选队列、逐请求结果、原始响应与脱敏回执；新增有效实体先验证，再决定是否接入派生版。旧原始包、失败记录与检查点保留。

## 第一批

- `LOCAL-SIDEBAR-001`：纯本地检查 Community、Game Guide、Media、News、Workshop，关联全部菜单目标到 v8 路由，并抽取旧新闻、媒体和指南页面的依赖缺口。业务、支持、论坛记录范围理由，保留历史展品语义。
- `NET-KARAZHAN-001`：从此前 67 项没有源站 HTTP 响应的 Karazhan 目标中，按旧报告顺序选择前 30 个不同地址，重查其真实存档内容状态；此前 59 项明确未存档的地址不在本批复查范围。

本地执行者只写 `research/continuous-recovery-20261015/sidebar-audit/`；网络执行者只写 `research/continuous-recovery-20261015/wayback-karazhan-batch1/`。统筹拥有本文件及持续总账。生产工具、测试或导出器如需修改，先给出具体方案，再分配单一文件所有者。

### 首批网络结果

`NET-KARAZHAN-001` 在 06:53:28–06:59:35 UTC 执行，30 个候选中 25 个已尝试：14 个收到真实 Wayback HTTP 404 与未存档提示，11 个仍在 TLS 阶段失败，5 个因连续五次传输失败而未请求。包括首个 direct 失败在内共 26 次请求尝试，真实源 HTTP 响应 **14 次**，正文合计 65,932 字节，没有取得有效图片。原始汇总曾将尝试数误计为源响应数，已经仅凭保存证据离线更正；报告更新时间与原请求窗口分别保存。

统筹[独立验收](../research/continuous-recovery-20261015/network-batch1-acceptance.json)逐一重读全部原始响应头、长度与 SHA256，核对未存档提示、图片解码和冻结清单；验收没有发起网络请求。Karazhan 126 个目标当前累计 73 个取得未存档内容判定，53 个仍未获得内容判定。本批[脱敏逐项回执](../research/continuous-recovery-20261015/wayback-karazhan-batch1/sanitized-summary.md)保留未请求项及停止原因。

网络进入至少 15 分钟冷却，最早 `2026-10-15T07:14:35.213520Z` 才检查一个已知可解码 JPEG 控制对象。若控制失败，不重发本批目标；继续本地审计，留到下一检查点再评估。控制对象来源为[此前控制回执](../research/tls-poll-20261015/summary.json)，预期 3,347 字节、150×110 JPEG，摘要和实际捕获日期须重新核对。

`NET-CONTROL-002` 随后在 07:15:13–07:15:20 UTC 执行：direct 在约四秒连接超时，proxy 返回真实源 HTTP 200。独立重读原始响应与正文后，确认 3,347 字节、SHA256、150×110 JPEG 与实际 Memento `2008-05-12T21:26:53Z` 均匹配。[控制验收](../research/continuous-recovery-20261015/control2-acceptance.json)为 ready；这是一份已有对象的连接控制，没有新增恢复素材，也不推定所有目标均可访问。

### 侧栏结果与第二批本地工作

修正后的[逐项审计](../research/continuous-recovery-20261015/sidebar-audit/audit.md)包含全部 1,241 条菜单观察。1,167 条纳入当前本地状态检查，其中 1,067 条解析为真实页面或别名，对应 **449 个不同文件**；54 条为外部或动态入口，6 条为新识别的账号或登录支持入口，40 条缺路由观察对应 **35 个不同地址**。另有原始明示范围排除的 74 条保留排除记录。

独立验收核对全部菜单身份与索引、全部已解析页面的路由、长度和 SHA256、全部缺失路由键以及六个规范化误报样例。交互结论仅为静态引用迹象；资源扫描与 Flash 引用不当作浏览器运行验收或独立缺页数。根代理并发更新的 `CHANGELOG.md` 仅作为上下文摘要漂移记录，关键输入和冻结清单摘要未变化。

35 个地址以 2006–2008 年 RSS 月份、2005 年旧新闻月页和年页为主，另有 BC professions、PTR、Battlegroups 与 WLK artwork。`LOCAL-TARGET-RECONCILE-002` 先在本地核对它们是否已有原始实体或可证明的规范路由，输出精确网络查询队列；在这一步验收前不扩大网络批次。RSS XML 和新闻 HTML 不能仅因月份相同就互相映射。生产文件尚未修改。

该轮已完成[本地核对与独立验收](../research/continuous-recovery-20261015/local-target-reconcile-acceptance.json)：35 个目标为 **23 个 RSS、8 个新闻 HTML、4 个其他页面**。33 个目标未找到精确来源；BC professions 只有通用 professions 页面，Battlegroups 只有已保存的 index 与规范路径候选，都尚无旧地址等价证明，未添加别名。验收实读 52 次声明实体的长度与摘要，并保留查找范围，未宣称所有可能档案中均不存在。

根代理指定 `NET-CORE-PAGES-003` 先检查 8 个新闻 HTML，再查旧 Battlegroups、BC、PTR 与 WLK artwork。已有[RSS 优先队列](../research/continuous-recovery-20261015/local-target-reconcile/network-query-queue.json)作为验收历史保留，新批次在 `network-core-pages3/` 单独生成候选和优先级覆盖理由。CDX 记录与实际有效正文分开统计；PTR 查询保留源菜单中的尾斜杠。RSS 留待后续有界批次。

并行的 `LOCAL-RESOURCE-DEDUP-003` 只做本地工作，检查 Zandalar quests、EU regionals、Insider 11 arena 与 high-level options 四个页面，将资源引用按精确来源 URL 去重，记录引用次数和覆盖页面。940 条部分缺资源菜单观察可能共享同一资源，不能当作 940 个独立缺图。现有实体须实读校验；不按文件名跨域替代，也不把动态脚本表达式当作原始资源地址。

### 核心页面的实际恢复

`NET-CORE-PAGES-003` 在 07:40:44–07:42:40 UTC 执行 21 次尝试，取得 18 个真实源 HTTP 响应；CDX 返回 292 条捕获索引记录，实际取回并独立验收 **7 份 HTML**：2004 年新闻、2005 年 7–11 月新闻和 PTR 入口。有效正文合计 **889,708 字节**；包括 CDX 索引正文的批次总量为 **930,077 字节**。见[逐请求独立验收](../research/continuous-recovery-20261015/core-pages3-acceptance.json)、[来源表](../research/continuous-recovery-20261015/network-core-pages3/payload-source-map.json)和[根代理正文身份检查](../research/continuous-recovery-20261015/root-content-review-0753.json)。这些实体尚未因下载自动接入或发布。

首次候选判断把 URL 中显式 `:80` 当成不同地址，误将三页标为没有有效候选；离线复查确认 June News、BC professions 与旧 Battlegroups 均有捕获记录，已改为“已索引、尚未回放”。HTTP 默认端口 `:80` 与省略端口、HTTPS `:443` 与省略端口可正规化；bare host 与 `www`、HTTP 与 HTTPS 继续分开。七份已回放的原始实体、实际 Memento 和摘要保留；它们有效，但部分选中日期较早，不能宣称已选中全部默认端口变体中的最新捕获。

`NET-CORE-PAGES-004` 从已保存 CDX 生成[新候选表](../research/continuous-recovery-20261015/core-pages4-candidates.json)，先处理三页漏选候选、Wrath 回放失败与 2005 年年页查询失败，再在余量内取更近基准日期的同源捕获。2004 年年页已是最新合格候选，跳过重复回放。此批继续沿单一网络执行者和原有请求边界执行。

本地执行者同步准备 `CORE-PAGES-INTEGRATION-004`：新 v9 派生源树保留全部此前 8,306 个来源记录和 38 个图片补充层，等待下一批改进来源表再完整构建。PTR 原始 2006 年页面包含角色复制与下载入口，派生版须成为静态历史展品；标题中性、日期来自所选来源，不复活账号、复制、下载动作或脚本。根代理负责最终源选择、浏览验收与发布。

`NET-CORE-PAGES-004` 已完成[独立验收](../research/continuous-recovery-20261015/core-pages4-acceptance.json)：15 次尝试、14 个真实源响应，9 份有效 HTML 的正文合计 592,852 字节，含一次新 CDX 查询的批次总量为 603,399 字节。新增四个不同来源目标（June News、2005 年年页、BC professions、Wrath artwork），并把五个已保存月页升级为更近基准日期的 2008 年捕获；旧来源完整保留。

[合并选择表](../research/continuous-recovery-20261015/selected-core-pages-source-map.json)当前含 **11 个不同页面来源**：8 个新闻 HTML、BC professions、Wrath artwork 与 PTR。2004 年年页沿用前批最新合格捕获；PTR 的 2008 年记录只有到 test 子域及登录页的重定向，因此保留真实的 2006 年 HTML，派生展品不启用该动作链。所有选择按有时区的实际 Memento 比较并归一到 UTC。

旧 Battlegroups 首跳有真实 302、匹配捕获的 Memento 和到目录入口的历史 Location；第二跳没有 Memento，只作为 Wayback 调度记录。根代理对照已有目录别名、真实 index 正文及导航证据，批准[旧 `.html` 到既有 index 的兼容别名](../research/continuous-recovery-20261015/battlegroups-alias-decision.json)。仅在 v9 派生清单加别名，不替换来源，也不计作新增恢复实体。

### 资源队列与图库依赖

四页资源去重现已[独立验收](../research/continuous-recovery-20261015/resource-dedup-acceptance.json)：623 次占位文字出现对应 217 个不同 URL，分别为 102 个静态资源、113 个导航或页脚地址，以及两个仅用于脚本条件判断的 URL（四次出现）。232 次 `b.gif` 引用有真实 1×1 标签尺寸，属于共享布局 spacer。旧 HTML 的八处 `td background` 引用补齐了属性元数据。首次失败检查快照留在本地；未观察的布局损坏与未取得的原始资源没有记为已验证。

精确查找五份既有来源表和 v7c 清单，未发现可直接复用的本地实体；这只是声明范围内的查找结论。主[静态资源队列](../research/continuous-recovery-20261015/local-resource-dedup/network-asset-queue.json)优先正文图和图标，不按 spacer 的重复次数提升优先级。

新 Wrath artwork HTML 的[文字依赖检查](../research/continuous-recovery-20261015/wrath-artwork-dependencies.json)发现两个缺失的图库计数脚本：`/wrath/images/artwork/artworkcounter.js` 与 `/wrath/images/artwork/en_us/artworkcounter.js`。根代理同时确认 47 个 artwork 图片路由以及图库布局、函数脚本已存在；两个计数脚本可能阻断已有素材的展示。`NET-ASSETS-005` 因而先精确查询这两个脚本，再处理四个 Arena 图和九个 EU 图标。脚本只取回并离线检查，不执行；没有原脚本时不能编造计数或声称恢复了原始图库脚本。

`NET-ASSETS-005` 已完成[独立验收](../research/continuous-recovery-20261015/assets5-acceptance.json)：27 次尝试、23 个真实源 HTTP 响应，取得 **2 份真实计数脚本与 9 张图片**。有效载荷合计 50,010 字节，含 CDX 的批次总量 52,398 字节。脚本原文字面赋值分别为 `screenshotsCommonTotal = 12;` 与 `screenshotsLocTotal = 1;`，仅静态核对，未执行。九张图片均独立通过 Pillow verify 和 load，实际 Memento、正文 SHA256 与 CDX SHA1 均一致。另一个 Arena 图的本次精确范围 CDX 为空；三个图标的查询在传输阶段失败，继续保留未判定状态。

[已验收静态来源表](../research/continuous-recovery-20261015/selected-static-source-map.json)已交 v9 builder；六个 armory 图标保留其原始 foreign origin 与 `_origins/armory.wow-europe.com/` 命名空间，不按同名文件跨站替换。核心页面与本批静态资源若全部为不同新增记录，来源数预期为 8,328，38 个原补充层保留，最终以实际构建和根代理浏览验收为准。下载和静态脚本检查尚不等于图库运行通过。

`NET-RSS-006` 复用唯一网络执行者，从已验收的 23 个 RSS 目标按年月倒序选择最新 12 个精确来源，另存 `network-rss6/` 候选与回执。按正文判断 raw RSS/XML、扩展 HTML 或重定向，不因 `.xml` 扩展重用 XSL，也不把 RSS 和同月新闻 HTML 等价。其余 11 个 RSS 留待本批结果后另行安排。

## 取舍与后续顺序

优先修复已有真实内容因地址规范化或客户端逻辑无法访问的问题；其次补取来源明确且过去因网络失败没有取得内容判定的对象；再沿历史脚本、菜单和 CDX 记录提取有证据的缺失资源。按编号生成的截图地址可以作为来源证据，不能凭猜测把实体记为已取得。若本地审计发现更高价值的缺口，下一批按证据与可恢复性调整，不为填满时间盲目重试。

Karazhan 复查结束后，剩余旧 TLS 未判定项是否继续，取决于本批是否取得新的有效内容判定。MEDIA SSOTD 的未筛选图片索引仅遍历了两页，尚有续页；可在后续有界批次检查重访、重定向和历史脚本线索。Game Guide 的 50 个截图分区合计声明 1,684 张图，3,368 个原图与原缩略图仍是独立缺口。PvP `intro.swf` 与 Trial 图片保留为有证据待恢复项。

## 每批边界与验收

网络由单一执行者串行处理，源请求间隔至少 1.2 秒；每批最多 32 个请求、8 分钟、64 MiB 正文，单体 16 MiB。先 direct，失败再使用现有 `127.0.0.1:7890` 代理；保持 TLS 验证。429 或 503 立即停批，保留 Retry-After；连续五次传输失败停止。不得通过换 IP、端点或全局设置绕过限制。

每批前后检查 D 盘余量至少 11,005,853,696 字节。源 HTTP 状态排除代理 CONNECT 200；实际捕获时间只从有效 Memento 读取。正文长度、SHA256、MIME 与解码独立记录，CDX 的 WARC 索引长度不当作正文长度。失败分别记录网络未判定、未存档、错误正文、未请求。原始响应头与追踪日志仅本地留存，公开记录脱敏。

接入新素材或修复后，统筹核对来源、摘要、时间与范围，根代理负责 Git、发布与最终验收。局部检查只覆盖实际运行的场景，不将静态通过或队列派发记为运行完成。
