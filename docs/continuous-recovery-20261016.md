# 2026-10-16 持续恢复

用户授权连续推进未完成修复，窗口为 2026-10-16 10:01:49–22:01:49（Asia/Shanghai；UTC 02:01:49–14:01:49），包含获取、整合、验收和发布。延续[前次专项](focused-recovery-20261015-2303.md)，不重新下载已经验收的新闻和原图。

## 起点与目标

- main 起点 `7d0c9e6785e6e9fc0c1e6f8d1e35eada533c7cf4`；公开 Pages 与离线包为 v14，本地 v15 已通过验收。
- 先发布 v15 的 2007 年 8 月 50 条新闻，再查玩家图库、Media 和其他缺失素材；两张新取得的欧服每日截图归入关联站展品。
- 页面入口、图片实体、传输未知和存档不存在分别记录；侧栏页面已齐不表示图片已齐。

## 分工与约束

主代理负责取舍、独立验收与发布。两名 Luna 执行者分别负责只读本地审计/派生整合与单一串行网络获取，文件所有权按任务分开。任务及状态见 [tasks](../research/continuous-recovery-20261016/tasks.json)、[status](../research/continuous-recovery-20261016/status.json)。

下载 direct 优先，失败后仅在进程内用 `127.0.0.1:7890`，开启 TLS 验证，不自动跳转。每批限制请求、时长和字节，实际请求间隔至少 5 秒；429/503 或五次连续传输失败停批并冷却至少 120 秒。每批、每请求及大写入前检查 D 盘至少保留 11,005,853,696 字节。不改全局网络设置，不绕限流。

冻结原始来源、`offline/site`、`offline/build-manifest.json`、历史 ZIP 和已验收版本；新修复用新派生版本。原始 HTTP 元数据与 Cookie 留本地；公开整理后的来源与验收。旧业务界面保留为静态展品。

## 时间与检查点

复用当前聊天的自动接续，每 15 分钟检查现有任务；正在进行的工作不受这个间隔限制。无实质变化时安静，新增验收成果、重要修复、真实阻塞及最终收尾时通知。

UTC 13:00 后不启动新网络批次，13:10 后不启动新来源/导出版本，预留最终验收、离线包及发布时间。截止后只做有界收尾与累计报告。不会以未验收的下载数量替代恢复成果。

## 进度

- 02:05 UTC：确认 main 干净、D 盘约 28.7 GB 可用，无本项目下载进程；旧代理树已结束。
- 更新已有自动接续 `wow-8` 至本轮截止，启动两名执行者的只读首批审计。v15 准备从现有已验收文件直接发布。
- 02:13 UTC：重新读取 v15 的全部 8,496 声明对象及来源清单，长度与摘要和原验收一致，未修改冻结版本。
- 02:15 UTC：Pages 构建完成，发布提交 `fe60f9a8bd8249b255aa24902e31f84c06124fc0`。02:19 UTC 完成八项线上文件核对，包含八月新闻、九月回链、菜单、运行脚本、百科首页、样式和来源清单；[线上验收](../research/continuous-recovery-20261016/publication/root-pages-online-acceptance.json)。来源清单首次两条路径均因 25 秒传输时限只取得部分字节；单项有界复查后 direct 取得完整一致的文件，首次结果保留。
- 新总账继承全部 1,241 项菜单记录，仅更新已验收的页面状态：1,107 个内容入口、483 个实际页面文件、缺路由为零。图片与交互字段保留其原审计版本，尚未重算。离线 Release 仍为 v14。
- 第一批精确 CDX 调查完成：六次请求、三个真实响应。两张欧服缩略图均只有原有摘要记录；原页面引用的 `10805-10.jpg` 在查询时间窗没有记录。没有将这些索引结果计为已恢复图片。[独立复核](../research/continuous-recovery-20261016/network/root-cdx01-acceptance.json)
- NEWS01/02 取回九张 2006/2007 新闻配图，均为 2008 年 4 月有效捕获；原字节共 66,803 字节。首批一次解析异常保留独立回执并计入累计七次请求，修正后取得三图；第二批 36 次请求取得六图，四个目标留待冷却后检查。[NEWS01 验收](../research/continuous-recovery-20261016/publication/root-news01-acceptance.json)、[NEWS02 验收](../research/continuous-recovery-20261016/publication/root-news02-acceptance.json)
- 合并全部三轮 Karazhan 回执后，126 个直接图片目标中 79 项取得真实 Wayback 404，47 项仍为传输未知。其余图库实体在本次审阅回执中没有对应请求；不据此推定全局未存档。初版遗漏中间批次的 14 项，已由逐 URL 合并与原始响应头复核纠正。[独立复核](../research/continuous-recovery-20261016/publication/root-gallery-audit-acceptance.json)
- 五个指南页的 19 张嵌套预览图均已存在本地，冻结来源清单记录的捕获日期为 2008 年 4 月及 5 月。它们与动态图库的直接缩略图路径不同；父链接与文件编号也并非总是一致。早期将这组素材标为晚期或只有引用的分类已被 v4 复核替代。[预览图验收](../research/continuous-recovery-20261016/publication/root-nested-preview-acceptance.json)
- v16 已完成本地构建与主代理验收：沿用 source15，新增九张新闻配图和两张欧服原图，共 49 份图片补充；全部 8,507 声明文件通过逐字节核对，旧路由与 38 份补充均保留。12 项浏览检查通过，实际展开新闻后图片可见；已查看新闻和欧服图集画面。尚待发布。[本地验收](../research/continuous-recovery-20261016/publication/root-v16-local-acceptance.json)
- 网络只读诊断区分了直连 TCP 超时与代理 CONNECT 成功后的间歇 TLS 失败。NEWS02 未见 429/503，末尾四次传输失败保留在后续冷却记录中。冷却后 NEWS03/04 又取得四图，尚待主代理验收并进入下一版本，未改变已冻结的 v16 输入。

## 追加进度

- v17 完成本地验收：新增二十张新闻图片（100,831 字节），并在 Fishing、Hallow's End、Brewfest、Winter's Veil、Zul'Aman 五图库展示十九张已有指南预览。全部 8,527 声明文件核对通过，旧 49 项补充保留，共 69 项图片补充；91 项浏览检查通过，已查看五组预览及新闻实际画面。[本地验收](../research/continuous-recovery-20261016/publication/root-v17-local-acceptance.json)
- ALLNEWS01 二十目标取得十六图，含十四个首字母与两张新闻配图；原始响应核对、全部帧解码与摘要通过。ALLNEWS02 对四个传输未知项复查时连续五次连接失败，零源 HTTP 响应；停批并冷却 120 秒，下一次控制窗口安排在 04:30 UTC 之后。旧失败尾数保留，控制窗口成功后再决定是否恢复普通获取。[图片验收](../research/continuous-recovery-20261016/publication/root-allnews01-acceptance.json)、[停批复核](../research/continuous-recovery-20261016/publication/root-allnews02-failure-acceptance.json)

- 03:31 UTC：v16 已推送 Pages，提交 `96911e7ba7eda5e27cd5c52068cdd071a21c8c08`；03:36 UTC 完成 19 项线上文件核对，包含九张新闻图片、两张欧服原图、两页展开新闻、来源清单、路由表、运行脚本、相关图集与百科/八月新闻保留项。[线上验收](../research/continuous-recovery-20261016/publication/root-v16-pages-online-acceptance.json)
- NEWS03/04 的四张图片通过主代理来源与字节核验，共 40,877 字节，留待 v17 或之后整合；NEWS04 仅保留批次前后磁盘值，驱动具有逐请求检查，但没有记录逐请求余量，已在回执标出。新下载器将保留这些值。[NEWS03](../research/continuous-recovery-20261016/publication/root-news03-acceptance.json)、[NEWS04](../research/continuous-recovery-20261016/publication/root-news04-acceptance.json)

- 04:38 UTC：v17 Pages 构建完成，提交 `067f72e4cb313cfa9693f470814aa6a62bc92921`；随后 63 项线上对象与本地一致。相同四十页新闻中，缺图引用由 954 减至 798，二十个新增资源消除 156 处引用。[线上验收](../research/continuous-recovery-20261016/publication/root-v17-pages-online-acceptance.json)、[引用复核](../research/continuous-recovery-20261016/publication/root-v17-news-metrics-acceptance.json)
- 04:34 UTC：退避后 CONTROL01 取得合法 CDX，确认代理已恢复一次有效源响应；原 ALLNEWS02 的五次失败保持在历史记录中，另行批准新窗口。[控制验收](../research/continuous-recovery-20261016/publication/root-control01-acceptance.json)
- 04:45 UTC：十个图库目录调查用完二十次请求，九个完整 CDX 响应共 116 行，Amani War Bear 仍为传输未知；未发现直接 `ssN.jpg` 或 `ssN-thumb.jpg`，未回放图片。五次调度间隔为 5.093/5.094 秒，略低于 5.1 秒要求，实际请求开始均超过五秒。保留该执行偏离，下一驱动增加单调时钟复查和裕量。[独立复核](../research/continuous-recovery-20261016/publication/root-gallery-prefix01-acceptance.json)
- MEDIA 已保存的 2,082 行索引完成分类：仅两项有效 JPEG，均为已取得的 2010 年补充，未生成新图片候选，待主代理复核。另查欧服首页依赖与菜单路径。

- 05:10 UTC：第二轮十个副本目录全部取得 CDX，合计十九行，均无有效图片记录；未回放任何图片，当前传输失败尾数为零。修正后的实际调度间隔至少 5.25 秒。[独立复核](../research/continuous-recovery-20261016/publication/root-gallery-prefix02-acceptance.json)
- City Attacks 的三张已有预览通过原始字节、存档摘要、父链接与实际画面核对。它们在 PvP 指南中指向图库但无具体截图编号，准备作为独立指南预览加入；此前五组十九张的输入保持不变。[图片验收](../research/continuous-recovery-20261016/publication/root-city-preview-acceptance.json)
- 欧服首页发现七个菜单 iframe，以及两份脚本和一份样式的确切引用，十项来源 literal 经主代理复核；已保存的 US 同路径文件不当作 EU 来源。新批次将先查精确索引，再核验文本回放。[候选验收](../research/continuous-recovery-20261016/publication/root-eu-dependency-candidates-acceptance.json)
- MEDIA 的 2,082 行已由主代理重新分类，两张有效 JPEG 均匹配已有补充原图；本次没有新的可下载候选。[独立复核](../research/continuous-recovery-20261016/publication/root-media-inventory-acceptance.json)

## 后续取舍

优先回放已有有效索引、此前因网络失败未取回的资源，再寻找其他存档路径。已收到真实 404 的同点不反复请求。图库审计需要将每轮回执按精确 URL 与实际请求时间合并，不能从较早的汇总推导当前状态。

图库页面使用脚本拼接原图和缩略图地址。一个待验证的解释是：部分图片请求没有随页面一起被存档，因此页面保存下来而整组图片缺失。后续比较静态页面引用的嵌套缩略图、动态图库路径和地区官网镜像的捕获记录；不会用地区站的其他截图填充美服副本图库。
- 05:49 UTC：v18 本地验收完成，City Attacks 新展示三张已有预览；六组共二十二张，原五组页面字节保持一致。8,527 个声明文件与全部路由核对通过，十二项实际浏览检查和九项针对性测试通过。[导出验收](../research/continuous-recovery-20261016/publication/root-v18-export-acceptance.json)、[浏览验收](../research/continuous-recovery-20261016/publication/root-v18-browser-acceptance.json)
- 欧服菜单专项取得七份有效文本来源（30,206 字节），包含五个菜单 iframe 和两份脚本；只作本地结构研究，未执行或部署原脚本。进一步核对十个真实依赖与语言入口，优先沿菜单变量脚本寻找图库导航。[来源验收](../research/continuous-recovery-20261016/publication/root-eu-deps-source-acceptance.json)、[后续引用验收](../research/continuous-recovery-20261016/publication/root-literal-wave2-acceptance.json)
- 06:00 UTC：共享新闻批次取回 W、I 两个首字母图标，共 2,370 字节；第十一请求后达到五次连续连接失败，停批冷却，余八项目未完成。两图经源响应、存档摘要和全部图帧核对，保留给下一派生版本。[来源与停批验收](../research/continuous-recovery-20261016/publication/root-news-shared10-source-acceptance.json)
