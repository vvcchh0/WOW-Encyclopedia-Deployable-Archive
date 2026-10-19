# 2026-10-19 持续恢复

本轮从已上线的 v33 继续。用户授权九小时，起点 05:52:06 UTC，硬截止 **14:52:06 UTC（北京时间 22:52:06）**。上一轮收尾超时，因此本轮采用提前截止和每个长进程的独立墙钟限制。

## 优先事项与停止条件

1. 补完 v33 尚未覆盖的 46 个普通图片入口、30 个新增静态展示目标。复用已绑定同一来源清单的原图字节检查和 21 个真实弹窗结果；实际页面交互另外验收。
2. 独立验证现有 v33 便携包的全部成员、隔离解压和所带本地服务器，随后发布处理后的离线包。后续版本另行记录，不覆盖历史包。
3. 以现有页面、索引和回放证据调查 Karazhan 及其它玩家图库。将实际 404、301/302、空索引和传输失败分开。若已覆盖相关路径、时间和关联页的具体线索，仍没有可用图片，则记录调查范围并暂缓追查；获得新捕获或新引用时才重新开启。
4. 继续补回有来源线索的新闻、指南与 Media 素材，并处理实际复现的兼容问题。

网络新批次截止 **13:15 UTC**；新导出截止 **13:30 UTC**；发布主体目标 **14:15 UTC**；**14:35 UTC** 转入最终收尾。若工具或网络阻塞，保留真实状态，不用等待跨越预算来凑齐验收。

## 分工和边界

主代理负责取舍、下载计划审查、来源与输出独立验收、提交和发布。两名既有执行者分别负责本地浏览审计和图库调查/唯一串行获取，不再委派。首轮图库工作只读取已有资料，网络计划经主代理审查后执行。

沿用 direct 优先、进程内代理回退的获取方式；TLS 验证开启，实际请求起点至少间隔五秒。每批明确请求、时长和字节上限；429/503 或五次连续传输失败停止并冷却。每批前后、每请求和大写入前检查 D 盘安全余量 11,005,853,696 字节。

原始站点、历史包、已验收版本与回执保持不变。修复写入新派生版本；原始 HTTP 元数据留本地，公开整理后的来源和验收结果。登录、报名和付款界面继续作为静态历史展品。正常提交与推送，不强制推送；源码同步、Pages 构建、线上响应和 Release 分别记录。

## 起始检查点

- main：`a7ffef6479f8c2a862febeaa76d6e4a949047c98`。
- Pages：v33，构建 `f648d3439961bd2e242f4eff588321a286ca2653`，前次新增/变化的 153 个对象已核对。
- 上一轮接受 376 个图片资源地址，均已接入 v33。动态玩家图库原编号截图仍与指南插画分计。
- 公开离线包为 v24；本地 v33 ZIP 已生成，独立验收和 Release 尚未执行。
- Karazhan 126 个目标：114 个实际回放 404、12 个跳转；后者的确切晚期日期索引均是 301 HTML。没有可接受的原编号图片，仍需关联页及覆盖范围调查后决定暂缓范围。
- 旧调度 wow-8 已删除；本轮调度为 wow-9，结束时删除。

总账：[status.json](../research/continuous-recovery-20261019/status.json)；任务：[tasks.json](../research/continuous-recovery-20261019/tasks.json)。前次记录：[2026-10-18](continuous-recovery-20261018.md)。

## 检查点

### 06:00 UTC — v33 便携包独立验收

保留上一轮 ZIP 原字节，重新读取并核对全部 9,024 个成员，再解压到独立目录，启动包内服务器。201 个页面与资源路径的 GET/HEAD 均通过，检查包括百科、新闻、指南大图、图库入口及部署变化对象。压缩包 532,938,958 字节，成员解压合计 598,153,671 字节；检查后 D 盘余量约 45.19 GB。

这项验收覆盖包内容和本地服务，浏览覆盖沿用明确限定范围的 v33 回执。未完成的真实 UI 检查仍由本轮单独推进，不因包检查通过而改写为整站交互通过。[独立包验收](../research/continuous-recovery-20261019/publication/root-v33-portable-acceptance.json)

离线发布工具在旧版基础上只调整来源日期与发布日期分离、输出位置和本轮截止；九项离线测试及路径断言通过。拟发布的包仍为 10 月 18 日构建的 v33，发布日期和标签使用 10 月 19 日。

### 06:11 UTC — v33 离线包发布

main 检查点 `d45b8a89` 已正常推送；随后创建并发布 [2026-10-19 Release](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/tag/archive-20080512-browser-20261019)。发布前后，三个 GitHub 附件的状态、大小和平台 SHA-256 均与本地一致，标签解析到同一源码提交。README 已更新下载入口。Pages 没有重复发布，仍为已验收的 v33 构建。[发布回执](../research/continuous-recovery-20261019/publication/root-v33-release-publication.json)

### 06:31 UTC — 两个图库晚期缺口关闭，原编号图片暂缓

唯一网络执行者按有限计划补查了两段此前因连接失败未取得的索引：Karazhan 的 2009–2010 年、Black Temple 的基准后至 2010 年。四次请求均先 direct，直连在 TCP 连接阶段超时，随后进程内代理各取得一次完整 CDX JSON。Karazhan 返回 52 行、Black Temple 返回 68 行，无续页或截断。主代理重新解析全部 120 行，包括驱动保守排除的八条 HTTPS 记录；它们仍只涉及目录和既有指南缩略图，没有原图库 `ssN.jpg` / `ssN-thumb.jpg` 的捕获。

现有 50 个图库的基准前目录调查、Karazhan 126 个确切回放目标、晚期索引以及保存下来的指南页和地区页面线索已汇总。Karazhan 仍是 114 个实际回放 404、十二条晚期 301 HTML，后者仅第一条实际读取过 Location；不能把其余十一条目标写成已观察事实。Black Temple 没有找到原编号图片索引，但其 96 个地址没有逐一回放，不能计作 96 个 404。

据此，将 Karazhan 与 Black Temple 原玩家图库标为“等待新证据，暂缓查询”。已有指南预览继续展示。其它图库保持各自的索引与未请求状态，不把这两组结论扩大到全体 3,368 个动态目标。新图片地址、不同关联页原引用或新的有效捕获可重新开启调查。

源页用 `addshots` 动态组装原图库地址，指南预览则直接出现在页面中。这与两类资源的保存差异一致，可能是历史爬虫发现动态资源不足造成；这是机制推断，不是已证实的抓取原因。[关联页审计](../research/continuous-recovery-20261019/gallery-audit/coverage-ledger-r2.md) · [主代理来源验收与暂缓决定](../research/continuous-recovery-20261019/publication/root-gallery-late-gap01-source-acceptance.json)

### 06:34 UTC — v33 计划内图片浏览覆盖补完

本轮实际补查的 76 个目标全部通过：Dragon Hunt 的隐藏图片先点击原始展开控件，另外 45 个普通图片入口、30 个静态展示目标分别验证。最后一张二月新闻图片的旧清单缺少对应新闻条目的展开 ID；主代理从原页面定位 `news2-6-08-270`，点击真实控件后确认 130×100 图片显示。此次仅纠正检查输入，没有修改站点文件。

结合前次 120 个新增原始文件与 21 个弹窗检查，v33 计划内的图片变化已覆盖；69 个普通目标中 68 个有实际入口，一个 Outpost map 声明没有关联图片元素，单独保留。主代理重核 133 个相关站点文件的来源摘要，所有新检查均无外部请求、失败请求或新脚本错误。比赛结果页四条旧菜单异常仍是独立待修项，不把本次图片验收称为整站全部交互验收。[浏览续查验收](../research/continuous-recovery-20261019/publication/root-v33-browser-continuation-acceptance.json)

### 07:15 UTC — 比赛菜单修复构建

Vintage Poster 结果页使用旧 `Contests` 页面 ID，但菜单查找同时要求 URL 与栏目首页一致，导致找不到节点。派生脚本只在该结果页使用已经存在的 Contests 节点；原页面和栏目结构保留。六项针对性测试与十一项既有图片链接测试通过，隔离页面中的四条脚本错误消失。v34 只包含这一兼容修复，实际生产树的浏览验收继续进行，尚未发布。

第一次构建把 650 MB 的输出预估误传给工具的“工作区总预算”参数，在生成输出前停止。错误记录保留；检查参数含义后，以用户已取消总预算、保留 D 盘安全余量的配置进行一次显式重试，07:15:45 完成，输出 9,018 个文件、594,318,472 字节，没有增加图片。原始站点和 v33 均未改写。

### 07:23 UTC — 四张新闻配图取得，八月新闻缺图标记复核

沿 v33 实际页面引用检查四个此前没有执行记录的确切地址，找回 Legendary Tales 比赛、欧服测试报名公告和两张旧同人画配图。四张图片均为 2008 年 4 月的捕获，合计 41,536 字节。主代理重新解析完整索引、核对回放来源与原始字节并读取图片全部帧，再查看实际图像；原字节已复制到整理后的素材层，尚未接入新部署。

本批九次请求、45.12 秒，首次 direct 在 TCP 阶段超时，随后八次进程内代理请求成功；尾数为零，无限流响应。单独的 300 秒父进程限制没有触发。[来源验收](../research/continuous-recovery-20261019/publication/root-frontier-news04-source-acceptance.json)

另复核 v33 的 `news/rss-08-2007.xml.html`：缺图占位引用为零，复用既有图片浏览验收。该结果只说明这张新闻页的缺图标记已清空，原玩家图库仍单独计数。[八月新闻复核](../research/continuous-recovery-20261019/publication/root-august-2007-news-coverage.json)

### 07:49 UTC — 再取得二十张旧新闻配图

第二批二十个确切地址均找到有效捕获并取回，包括同人画、早期 PvP 截图和测试公告配图。主代理独立核验完整索引、回放来源、捕获时间、原始字节和全部图片帧，随后查看二十张图的联系表。新增 150,407 字节，均为 2008 年 4 月捕获，本轮累计取得二十四个图片资源地址。四十一次请求历时 221.90 秒，尾数零，无冷却或限流响应。[来源验收](../research/continuous-recovery-20261019/publication/root-frontier-news20a-source-acceptance.json)

v35 将只整合这两批二十四张图和比赛菜单修复，继续从冻结的 Source15 生成。后续网络素材进入下一派生版本，避免在构建途中更换输入。当前公开站点和离线包仍为 v33。

### 08:51 UTC — 四十七个素材已取得，v35 完成中断收尾

新增十六张旧新闻配图和七张指南、比赛、竞技场与 PvP 页面装饰素材，本轮累计四十七个原始图片地址、525,328 字节，均已完成来源与图片验收。最近静态素材批次检查十七个地址，二十五次实际请求，找到七图；另外十项没有符合条件的图片捕获，保持缺失，未把 HTML 或地址变体作为成功图片。

v34 的比赛菜单与指南图片浏览检查通过，暂不单独发布。v35 冻结整合前二十四张新闻图；后续二十三图进入下一版。构建生成完整站点和来源清单后，末尾工作区总量扫描耗时，原执行流程在 973.37 秒手动停止。旧记录中声称的 900 秒硬限制和一处来源 gate 摘要已在独立勘误中纠正。

对现有中间目录的 9,041 个声明文件逐个检查长度和摘要，9,042 个实际文件全部吻合；无额外或缺失文件。受控收尾第一次因动态模块加载缺少注册而在改名之前失败；只修正加载助手后，于 08:51 完成正式目录改名，原站点字节未改写。浏览验收尚待执行，Pages 与下载包仍为 v33。后续构建将使用真实父进程截止，并避免没有总量上限时遍历全工作区。

[静态素材验收](../research/continuous-recovery-20261019/publication/root-frontier-static20c-source-acceptance.json) · [v35 收尾回执](../research/continuous-recovery-20261019/publication/root-v35-finalization-r2-execution.json)

### 09:07 UTC — v35 本地验收通过

二十三张静态新闻图片与一张原生展开新闻图片全部通过 HTTP 原字节、图片解码、自然尺寸和页面可见性检查；Beowulf 条目用原有控件从折叠状态展开。无外部请求、页面脚本错误或失败请求，主代理查看两张页面截图。首轮截图检查自身的定位错误保留在失败记录中，修正后的独立第二轮在 4.77 秒完成。

主代理核对 v35 相对线上 v33 的三十个变化对象：二十四张新图、两张新闻页、两份离线脚本或路由文件、一份比赛菜单脚本及来源清单。复用此前完整文件检查和 v34 菜单验收，未重复全站测试。当前进入 main 同步与 Pages 发布步骤，公开离线包继续保留 v33。[本地验收](../research/continuous-recovery-20261019/publication/root-v35-local-acceptance.json)

### 09:27 UTC — v35 发布并核对线上文件

main `d258e903` 已正常推送；随后以原 v33 的 gh-pages 提交为父版本发布 v35，Pages 提交 `1eea9aae3cbb0c29a5097e409f32461e1aec39d5` 已完成构建。三十个变化对象均通过 HTTPS 取得，全部直连成功，内容长度、摘要和 MIME 与本地一致；核对前后 Pages 提交相同。首次核对助手缺少来源清单超时分类字段，在对象请求前停止；补齐适配字段后完成独立第二轮，未修改站点或验收对象。

本轮公开新增二十四个图片地址；本地另有三十二图已验收，下一版继续整合。其间找到的六张旧 Visa 促销图片先保存原文件，等待该页进一步改为静态展品后再上线。离线下载仍为 v33。

[Pages 发布](../research/continuous-recovery-20261019/publication/v35-pages-publication.json) · [线上核对](../research/continuous-recovery-20261019/publication/root-v35-pages-online-acceptance.json)

### 09:40 UTC — 后续素材与派生工具修复

本轮累计取得七十五个图片地址、1,066,476 字节，公开 v35 含其中二十四个。最近一批二十个新闻地址取得十九图；另一个 wallpaper.gif 的旧计划错误地期待 JPEG，原始响应已经保存，正在本地复核，不把这项记作图片缺失或重复向 Wayback 请求。后续输入校验会同时核对 MIME、图片格式和 GIF 全帧设置。

新派生工具仅在设置工作区总上限时遍历统计总占用；取消总上限时保留前后磁盘安全余量检查，并返回未统计的总占用。Visa 促销页及原有两个别名改为六图静态展品，只提供本地档案导航。原始页面和图片不改写。三十四个导出测试与十五个历史展品测试通过，包括有限预算和磁盘余量在导出前后的拒绝行为。首轮测试运行器目录错误的失败记录保留。

v36 输入准备冻结为 Source15、既有来源闭包和五十一张新增图；待复核 GIF 与后续网络批次留下一版，不在构建中更换来源。[工具验收](../research/continuous-recovery-20261019/publication/root-export-exhibit-tools-acceptance.json)

### 09:59 UTC — 工具与七十五图来源提交，GIF 本地勘误完成

派生工具修复和七十五图来源检查点 `62372b14` 已正常推送至 main；Pages 仍是已验收的 v35，不将源码推送称为站点部署。保存的候选补丁含标准 unified diff 的空白上下文行，发布整理使用仅适用于该补丁的 whitespace 属性保留其原字节，第二轮内容与 Git 检查均通过。

主代理对 wallpaper.gif 已保存的完整 CDX、HTTP 回放与全部图片帧独立重验：2008-04-02 捕获的来源地址、Memento 与摘要均匹配，260×200 单帧 GIF、27,829 字节有效；2005 捕获返回的相同字节不匹配其索引摘要，仍拒绝。只修正文件类型预期，旧计划、失败观察和图片原字节均保留，没有新增网络请求。已复制为独立素材，本轮累计七十六图；v36 仍固定五十一图增量，这张 GIF 放入后续版本。

[GIF 来源勘误](../research/continuous-recovery-20261019/publication/root-news20e-rank99-source-acceptance.json)

### 10:34 UTC — v36 文件检查通过，图库晚期目录继续补查

v36 以冻结来源一次导出成功，父进程720秒、导出子进程600秒限制均未触发，实际约144秒。主代理逐个读取9092个声明文件并核对实际9093文件目录，51个新增图、874,533字节与来源相符；既有583个图片来源记录不变。浏览检查待执行，当前线上仍为v35。旧准备模板关于未重读既有图片的字段已另存勘误；当前工具实际会校验它们的原始长度和摘要，未修改冻结输入。

十个此前未覆盖的图库晚期目录补查完成，20次请求取得十份完整CDX、677行。主代理重新解析所有HTTP/HTTPS与跨前缀路径，未找到原图库直接ssN.jpg或ssN-thumb.jpg记录；指南thumbs预览不混计为原图。直连均未获得HTTP响应，随后进程内代理成功，无限流，尾数零。50组中已有13组完成所列晚期窗口，余37组按新目录继续；Karazhan、Black Temple及Zul’Aman已完成的窗口不重发。

[完整文件检查](../research/continuous-recovery-20261019/publication/root-v36-tree-acceptance.json) · [十组图库索引验收](../research/continuous-recovery-20261019/publication/root-gallery-late-rest10a-source-acceptance.json)

### 10:43 UTC — v36 图片层验收，保留排行榜问题

51个新增图片均经本地HTTP取得，原字节、MIME与自然解码通过；其中48个有真实页面元素或computed background显示，主代理查看六张截图。三张装饰图仅保留素材：PvP lion-top在原HTML注释中，Top List的next/prev宽版按钮在本次真实DOM无可见匹配，未为检查注入元素或class。Visa六幅历史图均以无链接figure展示，仅有两条档案导航。

浏览总门槛仍返回失败，原因是上述三项无实际入口，以及Top List的四条脚本错误。该栏目的HTML和JS与v35字节相同；尚未复跑旧版运行对照，不能把字节一致写成旧版运行已验证。图片层单独验收，v36暂不发布；下一步定位脚本原因并在后续派生版本修复。原结果、失败门槛和截图均保留，不改写成全通过。

[图片层范围验收](../research/continuous-recovery-20261019/publication/root-v36-image-layer-acceptance.json) · [真实浏览记录](../research/continuous-recovery-20261019/integration/v36/browser/results/v36-browser-r2.json)

### 11:03 UTC — 九十六图来源提交与两项派生脚本缺陷

main检查点3ff3c706正常推送，含本轮96个已验收素材、v36冻结构建及失败门槛的原始浏览记录；没有部署v36。Top List的两个源脚本均能通过Node语法检查，旧派生工具将Prototype正则误识别为路径，又消耗logic.js内嵌HTML引号的转义，造成两条语法错误和两条后继异常。修复设计限定两份实际Source15脚本，以源摘要保护，保留Prototype文本，并仅替换logic中的五个已知像素src值；其它脚本、HTML、CSS的既有流程保持原设计。

图库第二批取得八份完整索引、507行，仍无原编号图片；Mechanar请求503后立即停批，Botanica尚未请求。主代理分别验收八份CDX和末次503，记录尾数虽为零但连接恢复门槛未通过。等待冷却后的新控制回执，不用旧成功覆盖503。至此50组中21组已完成所列晚期窗口，剩余29组仍待查。

[排行榜诊断](../research/continuous-recovery-20261019/integration/toplist-diagnosis/toplist-diagnosis-report.md) · [503停批与部分来源验收](../research/continuous-recovery-20261019/publication/root-gallery-late-rest10b-source-acceptance.json)

### 11:14 UTC — 控制探测429，转向本地整合

冷却后单次已知小CDX控制请求仍收到429：direct未获HTTP，随后TLS验证开启的进程内代理取得162字节429响应。两次实际请求间隔5.25秒，探测约7.11秒结束，未回放图片或继续查询。主代理独立核验响应字节、末次HTTP状态、源绑定和停止行为；该429成为最新网络状态，恢复门槛保持关闭。冷却至少延长至11:45 UTC，届时也须另有明确批准的新控制，不能自动恢复或变换路径绕限流。执行者转为本地关联页和50组覆盖总账整理。

Top List窄修复通过34项导出回归和3项针对性测试；后者使用已复制的两个原始脚本夹具，可在新克隆中运行，未改变原字节。主代理完成实现与测试证据审阅；生产浏览仍须新版本验收。v37正准备在v36来源基础上加入已取得的21图与该修复，尚未执行导出。

[最新429验收](../research/continuous-recovery-20261019/publication/root-control-after-rest10b-source-acceptance.json) · [脚本修复验收](../research/continuous-recovery-20261019/publication/root-toplist-tools-acceptance.json)

### 11:35 UTC — v37 构建与文件变化验收

Top List工具修复与网络停批证据检查点c981de81已推送。v37以独立绑定的父进程脚本单次生成，11:23:46至11:26:27完成；21图、167,403字节加入既有闭包，合计655个图片覆盖、9,114个实际文件。所有9,113个声明文件逐个读取校验通过，既有634个图片来源记录保持不变。原父脚本模板未改，执行的是只替换两个摘要常量的单独副本。

主代理核对页面变化：21处新闻缺图引用改为实际图片，路由字典仅追加这21个路径；Prototype完全保留原始脚本，logic仅替换五个像素src值。其它v36页面及样式字节一致，可复用此前48项真实显示结果。新Top List运行与21图浏览尚待执行。完整文件检查的首份报告有三个从上版复制的统计字段；实际检查条件和路径集合已是21/655/634，单独r2勘误更正报告，保留首份与原检查器，没有修改站点或重复整个文件检查。

[完整文件验收及统计勘误](../research/continuous-recovery-20261019/publication/root-v37-tree-acceptance-r2.json) · [派生变化验收](../research/continuous-recovery-20261019/publication/root-v37-derived-delta-acceptance.json)

### 11:54 UTC — cross-reference review and final browser run

Root independently checked all1,205 selected Source15 text files (51,328,725B) and all93 gallery-reference rows. The65 Hallow's End shotList entries are concrete original-image literals already covered by the65-slot registry; they are not calculated guesses. The28 other rows are nested /thumb/ or /thumbs/ previews. No new Karazhan/Black Temple URL or new target-gallery address was found. The original scanner classification is preserved with a qualified root acceptance in `publication/root-source15-crossref-acceptance.json`. Other literal aliases remain separate candidate scope.

v37 browser r3 is root-gated for one300s run after correcting stylesheet/computed-background exact-target matching in the unexecuted r2 harness. A single fresh small CDX control after the extended429 cooldown is also root-gated; another429 ends Wayback acquisition for this run. Distinct v37 portable-release helpers are prepared without any upload or package execution.

### 11:57 UTC — second429 control; acquisition stopped

The11:53:54Z control attempted direct once (curl28/noHTTP) then the unchanged process proxy once (HTTP429/162B), with5.25s between starts. Root independently verified the raw final status, exact body and current failure chain. Wayback acquisition is stopped for this run. Remaining late prefix windows are open questions, not missing-image404 outcomes. No settings were changed and Firecrawl calls remain0.

Browser r3 stopped in argument parsing before any server/browser startup because a JavaScript string was incorrectly read through a `.parent` property. Its failed1.625s receipt is preserved. A new r4 corrects that path initialization and adds a real, offline parseArgs preflight before root review; site bytes are unchanged.

### 12:10 UTC — v37 real browser result and bounded v38 design

v37 r5 completed actual browser execution:21/21 new news images passed exact local HTTP/MIME/length/hash/dimensions and real visible DOM/decode; all four former Toplist JavaScript errors are gone. Both CSS image assets resolve and decode locally, but no native next/prev nodes exist for the empty ranking table; visibility/navigation remain pending. The full v37 browser gate remains false because3console404 responses were observed. r3/r4 harness failures are preserved; r5 only corrects a missing page.evaluate argument and does not change the site. Root reviewed both real screenshots.

A separate3.125s,90s-bounded read-only diagnostic identified `/toplist/data/en/killedby_10052008.js` and two root-relative table-border JPGs. No Toplist data record exists in the Source15/v37 catalog or output. The previously reported34 data keys are inherited Prototype methods, not ranking data. No source archive availability conclusion is drawn from these local404s.

Frozen v38 design: retain Source15 hash guards and Prototype, extend the narrow logic rewrite to its2CSS image URLs through the existing localizer, and supply an exact local-route map from the accepted catalog for historical ranking data. Unknown feeds take the existing empty-table path without a network request and state that historical ranking data has not been recovered. Captured feeds, if later supplied, use only their exact local route. No dataset or ranking rows are invented; old sites and receipts remain frozen. Export uses the same655 accepted overlay assets and Source15 closure; new datafix receives behavior/guard checks and actual browser validation before publication.

### 12:36 UTC — v38 local acceptance; publication and package

v38 exported once in158.17s from the same Source15/655-overlay closure. Root checked all9,113 declared files (9,114 actual;595,689,284B) and confirmed onlyToplist logic bytes differ from frozenv37. The first checker timed out at240s; an explicit scandir path/reparse walk plus8local read/hash workers completed the same byte checks in10.375s. The old checker and timeout are preserved. No sources or prior outputs changed.

The7.047s real browser run served406local requests, all200, with0external/unknown-data/unknown-local requests and0page/console/server errors.21news images passed realDOM/decode and exactbytes. The actual day selector1→2→1 produced1/2/1empty tables and0historical date datasets, each with the unrecovered-data notice. Two pagination CSS files decode, but no native pagination controls exist for the missing dataset; these and dataset0 remain four explicit pending observations. Root reviewed both screenshots. The source MIME of two old scripts is application/x-javascript; the preview serves executabletext/javascript with exactbytes, so the root checker accepts that explicit MIME conversion rather than legacy-header equality. The first local checker stopped before writing a receipt; its original is retained.

`root-v38-local-acceptance.json` binds the87-object delta from livev35, including72additional image files. Current-run total remains96 accepted images. main2e09e3a5 was pushed with the tool fix,39test results and qualified gallery audit; this is not yet a Pages deployment. A distinctv38 processed ZIP is being built; oldv33Release remains the public offline download until independent ZIP/server acceptance and release publication.

### 12:48 UTC — online and portable acceptance

main7751a187 pushed the accepted v38 scope. Pages78dac6c5 built at12:42:31Z. Independent direct-first HTTPS validation checked all87changed objects in87attempts (13,182,953response bytes); every object matched local bytes/MIME, and the exact deployment commit remained built before and after. All96current-run accepted image files are now in the published tree.

The processed v38ZIP was built once in71.892s. Root independently read and checked all9,120members and extracted a fresh isolated copy, then served137paths withGET/HEAD (274requests) using packaged Python -I server. The independent42.359s check passed:534,197,885B ZIP,599,564,048B total unpacked, original image bytes preserved. No rawHTTP/source payload evidence is included. Release preparation uses a distinctv38 tag and does not replace the earlier v33 assets. Dafter root package check38,403,313,664B.

### 12:57 UTC — v38 Release published

[处理后v38离线包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/tag/archive-20080512-browser-20261019-v38)已公开，Release417287196/tag`archive-20080512-browser-20261019-v38`精确指向main`4a169367892a05d9ca0120e544080e939fb5f13d`。上传ZIP、SHA侧车与NOTICE共三项资产，277.578s上传后逐项核对，发布前后平台大小/摘要匹配；10.125s发布过程完成。旧v33资产保持不变。

本轮累计新增96个图片资源（1,233,879B），在线/离线均为v38。玩家图库的原图/缩略图未新增；Karazhan/Black Temple保留有新来源再重启的暂缓结论。50组图库晚期窗口21组完整调查、29组尚未闭合（其中Mechanar曾返回503）。21组仅停止重复同一已查时间窗，不作为21组原图全部缺失的结论。全量Source15文字检查未找到新的目标图库地址；其他页面的417个URL变体中411个已对应本地同host资源，6个韩国PVP图片引用需后续检查。下次使用[源属性纠正后的六项清单](../research/continuous-recovery-20261019/publication/next-media-aliases-source-corrected.json)，不使用正则截断的旧队列；正式请求前仍需核对既有精确URL/时间窗。

Wayback在503后两次独立控制窗口仍返回429，本轮已停止获取，不再启动相同请求。可验收的本地修改、部署与处理后离线包已交付；剩余来源调查清单保留。Firecrawl调用0，没有购买套餐或修改全局网络设置。

### 本轮收尾

在线版和处理后离线包均为v38，README下载入口已更新。匿名下载检查验证ZIP的HEAD完整长度与117B摘要文件GET：direct未通后，经同进程代理取得200且摘要文件匹配，未再次下载534MB ZIP；签名跳转查询与Cookie未保留。完整包内容由本地全成员校验和GitHub资产digest双重核对。

本轮自动接续`wow-9`已删除：当前可验收的本地修复、部署和发布均已完成，重复429后的来源获取已停批。未用满9小时预算；未解决的图库、历史统计数据和精确来源队列作为后续工作保留。后续恢复须先读取本轮总账和[最终回顾](../research/continuous-recovery-20261019/publication/root-v38-run-closeout.json)，区分来源不存在、本地尚缺、索引查询完成和传输失败；不重跑已完成的相同查询。最终文档提交后单独核对main与origin/main。
