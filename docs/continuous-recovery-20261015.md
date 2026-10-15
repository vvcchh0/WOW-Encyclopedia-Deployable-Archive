# 官网档案持续恢复总账（2026-10-15）

本轮按历史侧边栏逐项检查，时间预算截止 2026-10-15 14:44 UTC（北京时间 22:44），有证据的工作队列耗尽或出现真实外部阻塞时可提前结束。用户已明确授权自动接续，根代理已通过应用工具启用本线程 heartbeat `wow-8`，每 15 分钟检查一次，调度截止 `2026-10-15T14:44:25Z`。当前批次继续执行；heartbeat 接收时先检查运行中的代理、任务队列和网络批次状态，不中止有效任务、不重复提交批次、不启动第二名网络执行者。本总账不创建额外后台循环或新聊天。入口是[已有恢复与验收记录](media-and-navigation-recovery-20261015.md)。当前已验收并发布的派生版为 `.scratch/pages-resources-20261015-v10`（Pages `77015ca477cc8794f9014f4082f1e11635f7e3dc`，14 个线上对象字节/MIME 验收通过），冻结的 `offline/site` 与 `offline/build-manifest.json` 不改写；清单 SHA256 为 `397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459`。

## 总账结构

[初始总账](../research/continuous-recovery-20261015/ledger.initial.json)从已有多代菜单盘点生成，每条菜单观察保留独立标识、分组、名称、原始地址、菜单文件与行号。旧盘点口径为 588 条内容观察、653 条排除观察。启动时复查发现，其中 **579 条 `Legacy menu` 只是旧解析器未分组**，包含 `/news/rss-05-2008.xml` 等真实内容地址，不能据此排除。已生成[范围修正检查点](../research/continuous-recovery-20261015/ledger.scope-review.json)，将这 579 条恢复为待分类审计；原来的 588 条口径继续保留以便比较，74 条明确的结构、业务或外部观察另行记录。初始快照保留其原始状态并由修正检查点取代。

每条观察分别记录页面状态、资源状态、交互状态、来源证据、关联任务与下一动作。旧盘点针对 v5 派生版，其覆盖状态保留在 `prior_inventory_status`；当前 page 状态已按 v10 全菜单路由检查更新，发布版 v10 已完成线上抽样验收；资源和交互字段保留 v9 静态检查版本，历史快照分别保存。页面可达不等于图片、Flash 或历史交互完整，补充素材的实际捕获日期单独记录。

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

v9 源树现已完成[独立来源验收](../research/continuous-recovery-20261015/core-pages-integration-acceptance.json)：实际 8,328 条来源记录，原 8,306 条来源的摘要、长度、时间、来源 URL 与命名空间不变，180 个旧别名保留；22 份新来源和对应镜像正文均实读核验。根代理独立检查另记录两个 generated support 路径迁移，内容相同。此处只验收 source mirror；38 个图片补充层等待最终 Pages export 应用，PTR 静态展品与图库运行仍需根代理最终导出及浏览器验收。

`NET-RSS-006` 已[独立验收实际载荷](../research/continuous-recovery-20261015/rss6-acceptance.json)：15 次尝试、8 个真实源响应，取得 Jan–Apr 2008 四份 `.xml` 地址实际返回的 **expanded HTML**，正文共 452,039 字节；没有取得原始 RSS。April 旧标题仍写 March，原正文 8 条 `posted-date` 全为 April 2008，保留源站标题异常；其他三个月分别有 28、43、24 条对应月份日期。四份来源[单独保存](../research/continuous-recovery-20261015/selected-rss6-source-map.json)，不加入当前 v9 构建，避免构建中漂移。

本批另有六个目标传输未判定、两个未请求，连续五次传输失败后停止。两处记录的 UTC 开始间隔为 1.188815 与 1.195702 秒，curl trace 开始间隔约 1.184 与 1.186 秒，均低于要求的 1.2 秒；原时间不改写。载荷真实性通过，批次间隔合规未通过。至少冷却到 `2026-10-15T09:03:32.169574Z`，随后 `NET-CONTROL-007` 只检查一个已知 JPEG，新进程 wrapper 在实际派发前循环重检 monotonic 剩余等待，采用 1.25 秒保守间隔，并持久 UTC 与 monotonic 派发时间。成功或失败均返回，不自动重发 RSS。

`LOCAL-BROWSER-V9-005` 复用本地执行者准备有界浏览验收，等待根代理 29005 服务 ready。检查 12 个新菜单目标、PTR 允许链接和别名、Battlegroups 旧导航、Wrath 图库翻页/图片解码/lightbox及一个既有 SSOTD 补充层回归；仅 loopback GET，20 分钟，不修改生产文件。

`NET-CONTROL-007` 实际已在冷却结束后完成，一个已知 JPEG 的 direct 失败、proxy 源 HTTP 200；3,347 字节、150×110、摘要和实际 Memento 均[独立复核通过](../research/continuous-recovery-20261015/control7-acceptance.json)，trace 派发间隔 4.039 秒。原进程在报告组装时异常，内存中的 monotonic 与磁盘精确数值丢失，报告由原 raw 纯离线重建并保留这些 `null`，没有重发请求。新 wrapper 修复即时 journal、preflight 和 `finally` postflight 后，[独立重跑本地隔离测试](../research/continuous-recovery-20261015/control7-wrapper-acceptance.json)通过；模拟记录与真实执行分开，历史证据未改写。

根代理最终导出已完成并开放 29005 本地服务，声明 8,467 个导出文件、8,328 个来源与 38 个补充层；浏览验收现已启动，发布前仍须根代理的逐文件与公开卫生检查。图库新增发现两个独立缺口：原脚本组合的[精确查看页 `/wrath/art.xml`](../research/continuous-recovery-20261015/wrath-artwork-viewer-gap.json)没有本地来源；当前 counter 覆盖的 13 项中仅 common 1/3/6/9/12 五对已有图，47 个旧 artwork 路由包含更高编号，不能当作当前 13 项全齐。浏览验收必须真实点卡片，其他页面的 lightbox 回归不能替代图库展开结果。

`NET-WRATH-008` 因而优先精确查看页，base 无有效 HTML 才查询独立 `?s=1`；随后按 11、10、8、7、5、4 的顺序补首屏六缺项，每项缩略图和原图交错。最大 14 个不同候选、32 次尝试，保守派发间隔 1.25 秒并保存 monotonic/UTC；其余资源边界不变。第二页 common2/locale1 两对与 11 个从未请求的 RSS 留下一批，不自动扩大。

### 09:50 检查点：本地 v9 与发布状态分开

根代理已将主要来源、PTR 生产代码、37 项最终单元证据及 v9 source/export 验收推送并独立确认至 main `7a0955563ab44f8b69ba6715278b5ccf613791a4`。Pages 仍为已验收 v8（`7cfe6ac6a82137fc9df0673630e66c09adf03a49`），未推送 v9。

[正式 v9 静态侧栏验收](../research/continuous-recovery-20261015/v9-sidebar-acceptance.json)通过：1,241 条观察身份守恒，1,081 条 resolved、54 条外部/动态、6 条业务/敏感、26 条缺路由观察，对应 23 个旧 RSS 地址。460 个不同文件声明与统筹已实读摘要及额外 PTR canonical index 实读一致；此前缺失的 14 条观察、12 个地址接通，旧 resolved 路由无回归。旧审计将 `/ptr/` 规范为 `/ptr`，本轮保留原尾斜杠并检查真实 index；两种兼容入口均有已验收文件。delta 中追加元数据前的旧 audit 摘要已改为最终真实摘要。

[当前总账](../research/continuous-recovery-20261015/ledger.current.json)现明确代表 **本地未发布 v9**；此前 v8 总账逐字节保存为[独立快照](../research/continuous-recovery-20261015/ledger.v8-accepted-0725.json)。资源状态的 954 条 partial 仍是共享、重复的菜单观察，包含导航及占位引用，不是 954 张缺图。

[浏览独立复核](../research/continuous-recovery-20261015/v9-browser-independent-review.json)接受诊断证据：18 个报告 check 中 17 个实际执行、1 个跳过；新核心路由和别名可达，但图库只五对来源可用，八对缺失，真实卡片点击查看页返回 404。37 个 404 全属声明的图库缺口。Howling-Fjord 正常关闭被 banner 阻挡另留原证据，最终 skip；SSOTD 旧图解码与实际按钮/index/关闭通过，但 fixture 使用两个相同 URL，没有声称原生目录切到不同图片。

根代理发现 `roothost='/wrath/'` 被通用 URL 重写错误地 canonicalize 为 `.../wrath/index.html`，使共享 border 请求拼成 `index.htmlimages/...`。生产代码与真实 export fixture 已修，38 项测试以及全部 18 份实际 Wrath 来源的目录赋值改写通过；[修复验收](../research/continuous-recovery-20261015/wrath-directory-base-acceptance.json)明确尚未完成新的 full export/browser。v9 来源和导出树保持冻结，等待下一 fresh derivative，不发布当前有此问题的导出。

`NET-WRATH-008` 已[独立验收](../research/continuous-recovery-20261015/wrath8-acceptance.json)：15 次尝试、12 个真实源响应、4 条 CDX，实际只取得 `art.xml?s=1` 的 2008-02-19 查看页 HTML（10,622 字节），没有取得图片。10 个 scoped CDX 空、两个传输未判定；晚期存档不能由此推定不存在。原 query 来源保留，泛化成 canonical base viewer 的映射暂缓，须核对其真实 `screeniesimplified.js` API。

`NET-MIXED-009` 的 11 个声明目标由唯一网络执行者处理：pre-anchor viewer JS、pixel、此前未请求的 common4 对；独立晚期窗口 `2008-05-13–2010-12-31` 的 border 与 common11/10/8 三对。09:48 已有完成输出，未独立验收的摘要报告一个 JS、一个布局 GIF、没有晚期补充实体；仍待完整 raw/API 验收。pixel/border 是布局装饰，不算内容图。四份已验收 RSS-path HTML 及 query viewer 留下一版，未改当前 v9 或冻结 baseline。

### 10:30 检查点：v10 来源冻结与真实 viewer API

main 已由根代理推送并独立确认至 `8a7b30eb57632bf3353506c886d93d575b6afd27`。Pages 仍为 v8；当前总账仍代表本地未发布 v9，待 v10 真实导出与审计后再更新覆盖状态。

`NET-MIXED-009` 已完成[独立验收](../research/continuous-recovery-20261015/mixed9-acceptance.json)：14 次尝试、12 个真实源响应，取得 8,432 字节原生 viewer JS 与 43 字节 1×1 布局 GIF；有效载荷共 8,475 字节，含 CDX 的批次总量 8,938 字节。没有新内容图或晚期补充实体。真实 JS 证明 viewer 根据查询参数构造 common 12 项、locale 1 项的通用列表，因此允许以保留 `?s=1` 原来源的方式映射 canonical viewer。原脚本的 `eval` 只在派生导出中替换，原始字节保留。

`NET-RSS-010` 已完成[独立验收](../research/continuous-recovery-20261015/rss10-acceptance.json)：11 个此前未请求目标全部有实际结果分类，17 次尝试、8 个真实源响应，取得 May 2007、January 2007、July 2006 三份 expanded HTML，正文 428,871 字节；包括 CDX 的批次总量 438,550 字节。另八个目标为传输未判定，不能记作未存档。July 2006 原标题写 September，34 个正文日期均属 July，保留该原站异常；本批没有原始 RSS/XML。

派生 viewer 参数修复与卡片点击区兼容修复已由单一执行者完成，42 项测试通过，生产文件摘要固定。严格参数解析只接受唯一、十进制正整数、安全整数且在 1..shotList.length 范围内的 `s`；其余回到 1，保持原 one-based viewer 入口和目录/翻页逻辑。卡片修复只用于来源明确的两个 Wrath 图库，按原 CSS 243×193 设点击区；仅带 `missing-image.svg` 和 `ssborder1.png` 双标记的装饰占位隐藏。缺失 border 原图没有恢复，内容图缺口和下载数不变。见[最终实现与测试回执](../research/continuous-recovery-20261015/viewer-derived-fixes/wrath-card-hitarea-011-receipt.json)。

独立[真实完整脚本 VM 验收](../research/continuous-recovery-20261015/native-viewer-acceptance.json)执行 8,432 字节来源转换后的全部函数定义，再调用原生 `loadCheckForShot`，12 个参数样例通过。13 项列表、目录分区、当前/总数、one-based 到 zero-based 关系和 hires 链接均核对；表达式输入没有执行。仅已批准的查询片段改变，原 next/prev 函数保持相同。这是原生控制逻辑验收，浏览布局、真实图像加载与动画仍待新产物浏览。

[最终 v10 新增来源表](../research/continuous-recovery-20261015/selected-v10-final-additions.json)固定 10 条：七份 RSS-path HTML、query viewer、viewer JS 和布局 GIF，SHA256 为 `c73b02d2f9353402eb4b568640e1359031e25756604cbbc5f21552f0acd52a55`。相对于 v9 的 8,328 条，预期 8,338 条来源；以实际构建回执为准，38 个旧图片补充层留给根代理最终 export 应用。A 在独立 `research/v10-integration/source/` 和 fresh v10 source 树构建，旧 v9 与冻结 baseline 不改；根代理拥有完整 source/export 验收和后续 29006 浏览启动。

唯一网络执行者 B 独立执行 `NET-HIRES-011`，只查询真实 JS 模板举证的 common 1..12 与 locale 1 共 13 个精确 hires 地址。先按精确 URL 查既有索引，优先普通图已有的 1/3/6/9/12；pre-anchor CDX 确实为空时才在余量内查询单独晚期窗口。晚期素材若取得，会明确记录 temporal supplement，不替代基准原图。该批目录已有实际 dispatch journal，结果仍待验收；任何新增素材不追加入已冻结的 v10 选择表。

### 10:40 检查点：源树完成、高清批次没有实体

根代理已推送并独立确认 main `0208573d58f03607e674777453fd4af6713f57c8`，包括 viewer 参数/点击区实现及已验收来源证据。Pages 仍为已验收 v8；v10 未发布。

v10 source 一次构建完成，validation-only 最终退出 0；实际 **8,338 条来源/路由、183 个别名**。统筹[独立来源验收](../research/continuous-recovery-20261015/v10-source-independent-acceptance.json)核对全部 8,328 条旧来源关键元数据与别名守恒、两个 generated support 路径迁移的相同字节，以及十份新增 raw、真实 Memento 和派生文件。源 JS 仍保留原始内容，严格参数转换将在根代理 fresh Pages export 应用。根代理另实读全部 8,338 份派生文件；38 个旧图片补充层也留给最终 export。源[构建回执](../research/v10-integration/source/v10-source-receipt.json)与旧 v9、冻结 baseline 分别保存。

`NET-HIRES-011` 完成[独立逐请求验收](../research/continuous-recovery-20261015/hires11-acceptance.json)：24 次尝试、17 个真实 CDX HTTP 200 响应，共 51 字节索引正文，**0 条捕获记录、0 次回放、0 张图片**。七个地址在声明的 pre-anchor 与 2008-05-13–2010-12-31 两个窗口均为空；三个 pre-anchor 查询传输失败而未查 late，另三个 pre-anchor 为空、late 查询传输失败。空索引仅限精确地址和声明时窗，不代表全时域不存在。最小实际派发间隔 1.25 秒、最大连续传输失败 2，磁盘高于保留阈值；没有图片正文，因此没有 Pillow 图片验证样例。

A 现准备独立 `v10-integration/browser/` focused runner，等根代理 29006 ready 后才运行。只查七个月份 HTML、图库 13 卡两页、common12 卡片中心实际点击与 viewer 参数/翻页、真实图和已知缺口，不重跑无关旧场景。B 已结束网络，复用为 15 分钟纯本地 SSOTD 续页/脚本证据方案；当前不授权新网络。现有 648 条入口捕获、未筛选图片索引两页及真实续页键须先对照旧请求集合，避免重复查询。

### 10:55 检查点：v10 最终本地验收

根代理已完成 v10 全量 source/export 验收：8,338 份派生来源实读 541,216,852 字节；最终导出 **8,477 个声明文件、559,921,267 字节、38 个旧图片补充层**。与 v9 相同路径和摘要的文件复用已接受的公开卫生结论，全部新改文件另完整扫描，无未解决发现。线上仍为 v8，v10 是否发布由根代理处理并另写发布回执。

[focused 浏览独立复核](../research/continuous-recovery-20261015/v10-browser-independent-review.json)已接受。首轮实际执行五组检查，其中四组通过，RSS 组因 harness 将完整文档标题误当作正文可见文字而失败。保留首轮后只重跑 RSS：最终七页全部 HTTP 200，月份日期与两处原站标题异常核对通过；该轮是一组实际通过、四组 skip，不能称为单轮五组全通过。首轮 40 条标准 404 console 文本与 40 个已知缺图响应按 check 和数量吻合，零未知 404、页面错误、失败请求或阻止请求。原 console 未存 location，结论仅为聚合已知缺图诊断，不声称逐条 URL 绑定，也不拿 RSS-only 零 console 覆盖首轮。

原画列表实际为 9/4 卡片，每个点击区 243×193；common12 中心点击进入真实 viewer，实际背景与 screenImage 均显示已验收的 700×420 JPEG（50,533 字节，摘要和 decode 匹配）。12 个真实参数样例及 sentinel=0 通过，Next/Previous 实际从 12 变为 11/13；这两项仍缺原图，只验收索引。八对内容图、共享 border 原图及十三张 hires 仍缺，派生装饰占位隐藏没有增加原始恢复数。三张截图实读摘要和解码，统筹另目视 common12 原画。

根代理[1,241 条菜单复核](../research/v10-integration/root-sidebar-check.json)守恒，1,167 条当前范围中 **1,088 条 resolved、467 个不同文件**；七个 RSS-path HTML 新路由接通，剩余 **19 条缺路由观察、16 个地址**，无旧路由回归。[当前总账](../research/continuous-recovery-20261015/ledger.current.json)的 page 字段已更新为本地未发布 v10；[旧 v9 总账](../research/continuous-recovery-20261015/ledger.v9-accepted-0950.json)先逐字节保存。资源及交互字段逐值保留 v9 并显式标记版本，954 条旧 partial 观察未被称作新 v10 全资源审计。

SSOTD [纯本地方案独立审阅](../research/continuous-recovery-20261015/ssotd-next-plan-independent-review.json)核对真实第二页 cursor 与原查询参数。原候选中的 2008 入口已有 5,038 字节原始来源，2018 年 bare HTTPS 高编号重定向与基准图库相关性较弱，两者从下一批排除，旧方案保留。根代理批准的[独立优先级覆盖](../research/continuous-recovery-20261015/ssotd12-approved-plan.json)只续取最多三页真实新 key，并取 2010-12-27 `ss1057-thumb.jpg` 已见 301 的一个首跳。唯一 B 已派发 `NET-SSOTD-012`，不自动跟随、不回放新行、不接入当前 v10；仍受原请求、时间、字节、磁盘和停止边界限制。

### NET012 终页与下一资源队列

第二个 v10 main 检查点已由根代理推送并独立确认至 `bdba97213a8426e8b8d2220799dd35a9525e30e5`。Pages 推送与线上 14 个对象验收由根代理继续，当前没有据推送动作自动标为已发布验收。

`NET-SSOTD-012` 已[独立验收](../research/continuous-recovery-20261015/ssotd12-acceptance.json)：3 次尝试、2 个真实源响应、13,258 字节正文。真实续页仅 82 条 2016–2018 索引记录，且无下一 key；因此后两页正确未请求，同一未筛选查询累计已核对 2,082 条。新增行均为 redirect/revisit 索引，没有回放或取得图片。批准的 `ss1057-thumb.jpg` 首跳为真实 2010-12-27 301，Memento、CDX SHA1 和正文一致，指向 Battle.net 通用媒体门户；没有跟随。旧 helper 默认字段顺序与本查询 `fl` 不同，执行者已仅用真实 header 离线重算 status/MIME 分布，原响应、派发日志和请求时间不改。

网络执行者现 idle，没有自动下一批。A 继续纯本地检查七个新增新闻页面的资源与静态交互子集，去重正文图片候选；不改 current ledger，不将这七页检查冒充全站新资源审计。下一网络优先级待该队列独立验收，再由根代理确认具体有界范围。

### v10 线上发布验收完成

根代理发布的 Pages commit 为 `77015ca477cc8794f9014f4082f1e11635f7e3dc`，父版本是已接受的 v8。GitHub API 前后均确认该 commit built；[线上 14 对象验收](../research/v10-integration/root-pages-online-acceptance.json)全部 direct HTTP 200，正文长度、SHA256 与本地一致，MIME 正确，覆盖七个 RSS-path HTML、原画列表与查看页、viewer JS、pixel、路由表及旧 SSOTD 图。[发布回执](../research/v10-integration/root-pages-publication.json)另确认 main HEAD/index 在 publisher 前后不变。

当前总账的 published_accepted_preview 已更新 v10，旧 v8/v9 快照不改。页面全菜单覆盖结论来自本地 467 文件检查，线上结论限定为已实际验证的 14 个对象；资源及交互字段仍显式保留旧静态检查版本，focused 浏览与缺图边界单独记录。主分支当前已确认至 `bdba97213a8426e8b8d2220799dd35a9525e30e5`，后续发布回执提交由根代理处理。

`NET-SSOTD-012` 已验收结束，B idle；A 的七新闻页面资源子集输出已落盘，仍待独立验收，未据生成队列自动授权新网络或改变资源总账。

## 取舍与后续顺序

优先修复已有真实内容因地址规范化或客户端逻辑无法访问的问题；其次补取来源明确且过去因网络失败没有取得内容判定的对象；再沿历史脚本、菜单和 CDX 记录提取有证据的缺失资源。按编号生成的截图地址可以作为来源证据，不能凭猜测把实体记为已取得。若本地审计发现更高价值的缺口，下一批按证据与可恢复性调整，不为填满时间盲目重试。

Karazhan 复查结束后，剩余旧 TLS 未判定项是否继续，取决于本批是否取得新的有效内容判定。MEDIA SSOTD 的未筛选图片索引仅遍历了两页，尚有续页；可在后续有界批次检查重访、重定向和历史脚本线索。Game Guide 的 50 个截图分区合计声明 1,684 张图，3,368 个原图与原缩略图仍是独立缺口。PvP `intro.swf` 与 Trial 图片保留为有证据待恢复项。

## 每批边界与验收

网络由单一执行者串行处理，源请求间隔至少 1.2 秒；每批最多 32 个请求、8 分钟、64 MiB 正文，单体 16 MiB。先 direct，失败再使用现有 `127.0.0.1:7890` 代理；保持 TLS 验证。429 或 503 立即停批，保留 Retry-After；连续五次传输失败停止。不得通过换 IP、端点或全局设置绕过限制。

每批前后检查 D 盘余量至少 11,005,853,696 字节。源 HTTP 状态排除代理 CONNECT 200；实际捕获时间只从有效 Memento 读取。正文长度、SHA256、MIME 与解码独立记录，CDX 的 WARC 索引长度不当作正文长度。失败分别记录网络未判定、未存档、错误正文、未请求。原始响应头与追踪日志仅本地留存，公开记录脱敏。

接入新素材或修复后，统筹核对来源、摘要、时间与范围，根代理负责 Git、发布与最终验收。局部检查只覆盖实际运行的场景，不将静态通过或队列派发记为运行完成。
