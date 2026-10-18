# 2026-10-18 资源补齐

本轮从北京时间 12:55:37 开始，按用户授权连续推进十小时，截止 22:55:37。21:35 后不启动新网络批次，21:50 后不启动新导出版本，为验收、发布与回顾保留时间。

## 起点与优先级

沿用在线 v25 与离线 v24。先处理[五项已有正索引的指南素材](../research/focused-recovery-20261016-2301/pending-neighbors5.json)，随后补查未取得的新闻、玩家图库资源和静态页面实际引用素材。指南相邻图片与原动态图库槽位分别记录。

使用已有 Python/curl 获取器和 CDX、Wayback 原始回放；本轮不调用 Firecrawl。下载先 direct，连接失败后仅在下载进程内使用代理。一个串行获取者，每批有明确请求、时长和字节上限；限流或连续失败后停批退避。保持 TLS 验证及 D 盘至少 11,005,853,696 字节余量。

冻结原始来源、历史 ZIP、既有版本和已验收的表格/回执。新增来源经过原始响应、实际捕获日期、图片解码与内容核对后进入新派生版本；历史业务界面继续作静态展品。主代理独立验收，分别记录 main、Pages 与处理后离线包。

## 工作记录

- 04:55 UTC：确认 main 工作树干净，当前提交 d62f9fba；D 盘可用约 48.1 GB，无遗留下载进程。新建本轮总账，将串行获取和本地审计分工。
- 05:11 UTC：五项指南相邻图片的地址、冻结索引行与预算通过主代理检查，批准单次四分钟获取。新获取器只调整本轮目录与旧离线夹具路径；实际传输和验收核心保持一致。旧合成夹具对显式 `:80` 重复加端口，原失败记录保留；只在内存规范化合成测试输入后，三十二项检查通过，正式计划未改变。
- 新闻十一项旧清单重新区分为九项传输未知与两项基准前完整空索引；后者为 `04-02-08-2.jpg`、`04-02-08-3.jpg`，不重复同一时间窗。主代理核对旧 source-map 的实际分类与 200 响应记录，后续优先补查九项未知。
- 首批约一分钟完成：十一请求取得五图，全部通过精确 CDX、源响应、实际捕获日期、摘要、完整解码与主代理逐张视觉核对。一个 direct 连接超时后转代理，后续十个响应全部有效，结束失败尾数为零。
- 九项新闻续批取回八张 JPEG（85,322 字节）；`04-02-08-1.jpg` 获得完整空索引。十一项旧清单现为八张取得、三项基准前完整空索引、传输未知零项。累计十三个新图片资源，准备一次整合至 v26；原动态图库的 3,368 个目标仍单列。[指南来源验收](../research/continuous-recovery-20261018/publication/root-neighbors5-source-acceptance.json) · [新闻来源验收](../research/continuous-recovery-20261018/publication/root-news9-source-acceptance.json)
- 第三批又取得八个新闻配图资源（含两份 GIF），其中四个来自暴雪旧站，实际捕获于 2005—2006 年；原图及日期单独保留，准备后续明确接入相关来源。累计二十一个新图片资源。低优先级排版占位图未用来凑本批数量。[来源验收](../research/continuous-recovery-20261018/publication/root-news8-next-source-acceptance.json)
- v26 单次导出于 05:33—05:40 UTC 完成，包含首十三张新图；主代理完成八十四项浏览检查，实际展开十处新闻配图、核对六个指南/图库入口与新增原图链接，无外部请求。8,654 个发布对象已逐文件重新核对，静态缺图为 1,173 个地址、1,932 处引用；其中新闻为 543 个地址、547 处引用，原动态图库仍另计。准备发布这个验收通过的检查点。

## 证据入口

[总账](../research/continuous-recovery-20261018/status.json) · [任务表](../research/continuous-recovery-20261018/tasks.json)

- v26 已推送源码 `74a7d70c`，Pages `3b3f49a5` 构建完成；二十八个线上对象逐一与本地字节和类型一致，构建前后提交相同。离线包仍为 v24，待本轮稳定版本统一更新。
- 第四批取回十张 2008 年 1 月新闻配图（72,137 字节），累计三十一个资源。二十一个请求中仅首次 direct 超时，其后代理响应均为 200，结束尾数零；已完成独立来源与逐图视觉核对，等待下一版本。

- v27 新输入为二十七张、264,852 字节。主代理逐页检查 v26 实际 HTML，确认可移除二十七个缺图地址、三十一处引用；旧 source-manifest 的 references 投影只记录十六处，不能拿它代替页面核查。四份暴雪旧站素材保留独立来源路径；最小导出器扩展及十三项相关测试通过，v27 正在单次构建。
- 连接诊断发现 UDP DNS 回答与 HTTPS DNS 不同；在下载进程内临时指定 HTTPS DNS 返回地址后，直连 TLS 仍被重置。同一索引请求随后经现有代理成功，真实失败尾数为 0→1→0；未修改全局 DNS、代理或证书，也未关闭 TLS 验证。原响应与解析器细节留本地。[整理后的控制验收](../research/continuous-recovery-20261018/publication/root-dns-connectivity-control-acceptance.json)
- 新一批十张新闻配图已接受，累计五十个图片资源。它们保留至后续版本，不加入正在导出的 v27。

- v27 的 8,681 个对象、固定缺图统计与一百一十七项浏览检查通过。初次浏览检查将升级按钮的两条 CSS 状态引用当作两个 img，失败回执保留；修正检查类型后确认两态图片均显示，导出文件未改。主代理随后逐张查看实际浏览截图，发现旧升级公告仍含当前操作口吻的付款步骤，按此前用户要求暂停该版本发布，转入 v28 历史展品修复。v27、原始公告和图片均保留，在线仍为 v26。[发布暂缓记录](../research/continuous-recovery-20261018/publication/root-v27-publication-hold.json)

- 累计取得八十项、1,611,261 字节图片资源。新四批四十项均在 v27 旧新闻 HTML 中找到精确缺图引用，其中包括四个小型界面图标；不把这些统称为游戏截图。v28 预期静态缺图为 1,106 个地址、1,861 处引用，新闻 476 处；待新导出实际复核。
- 历史公告修复先在独立夹具通过，主代理追加源管线核对发现新 early-return 会跳过原有全页历史账号链接处理。保留初次回执和发现记录，修订为先走原流程、再只改目标公告；主代理重新运行十五项测试通过，并用 AST 确认旧流程保留。v28 尚未开始导出。[修订工具验收](../research/continuous-recovery-20261018/publication/root-historical-news-tool-retry1-acceptance.json)

- 玩家图库另开晚期窗口：Karazhan 扣除已查完整的 2008 年区间，只查 2009—2010；Zul'Aman、Black Temple 查基准之后至 2010-12-07。六请求取得 Zul'Aman 的完整 63 行，均非原动态编号图片正候选；另两组代理等待首字节超时，保留未知。后续正索引控制经代理约两秒返回，实际尾数 2→3→0，未更改系统设置。[窗口验收](../research/continuous-recovery-20261018/publication/root-gallery-late-window-source-acceptance.json)
- v28 输入准备时发生主代理过早验收与执行者收尾重生成预检的竞态。首次 GO 在导出前被检查拒绝；两份预检只差审计时间与磁盘余量，主代理恢复与原门 SHA 完全匹配的字节，保留较晚版本并复核全部绑定，随后重新授权首次实际导出。未改变 v27 或源资料。[恢复记录](../research/continuous-recovery-20261018/publication/root-v28-preparation-race-recovery.json)
- 又取回十项六月新闻图片，累计九十项。此批留后续版本，正在导出的 v28 输入仍固定八十项本轮已接受资源。

### 07:36 UTC — v28 accepted locally

The full v28 output check accepted all 8,721 declared files (8,722 actual); browser retry 4 passed 268 checks with no errors or external requests. The 67 added images relative to online v26 include the four distinct Blizzard-source illustrations. The February 2007 account-upgrade announcement now describes retired services in the past tense and presents its original artwork as a static exhibit. News missing-image occurrences are 476; all static occurrences are 1,861 (1,106 unique addresses). The later forty source images, 318,622 bytes, are reserved for v29. Publication has not yet been claimed.

The two gallery prefix queries that previously timed out have a root-accepted, index-only retry plan with longer first-byte waits; the completed Zul’Aman interval is excluded.

### 07:46 UTC — v28 online

Source commit `6cc98dc4` is on main. Pages built `abbe7e556b0f5e28feb33233260ab11027cf821b`; all 88 selected online objects match the accepted local bytes and MIME. The run now has 120 source images accepted, 80 published including the first v26 thirteen, and forty reserved for v29.

The extended Karazhan query still had no first byte after 60 seconds; Black Temple returned 503, so NET15 stopped. The accepted receipt records a closed resume gate even though its transport-failure tail is zero. A fresh known-positive control after the recorded cooldown is required. These results do not classify missing gallery image payloads as 404.

V29 input and runner gates were independently checked. The first root input receipt had a serialized preflight-hash field error; it is retained with a finding and superseded by retry1 before export. The resource maps and original bytes did not change.

### 07:58 UTC — v29 locally accepted; Armory static resources retrieved

V29 adds forty more news resources (318,622 bytes) to v28. All 8,761 declared files were rehashed and the 8,762-file tree matches its provenance; 263 prior overlay records are unchanged. Browser retry 2 passed 159 checks, including the original mouseover caption in the July 2007 subscriber milestone announcement. The first checks incorrectly expected that caption to start visible and overlooked alternating news CSS classes; the source and exported page bytes remained unchanged. Static news missing occurrences are now 436, all-static occurrences 1,821 across 1,066 unique addresses. Publication is queued.

CONTROL03 succeeded after the recorded 503 cooldown; direct stalled before TCP and the existing TLS-verified proxy returned the known exact index in 1.924 seconds. NET16 then retrieved ten exact 21×21 Armory item PNGs. Root source, original-copy and visual checks accepted all ten (14,738 bytes). They remain associated static Armory assets pending integration; native player gallery images are still separate.

### 08:03 UTC — v29 online

Main source `81bd8e85` and Pages `8b038ea40c9a6ab316322fbe58734714fbbb170d` are synchronized with the accepted v29 tree. All 47 online objects passed exact byte/MIME checks, with the same built commit before and after. The run has published 120 additional image resources. The current processed offline release remains v24 until the final stable package is prepared.

### 08:17 UTC — static38 acquisition complete; next content frontier reviewed

NET16–19 accepted 33 of the 38 literal assets, totaling 156,857 bytes: nineteen primary-site pictures/material icons and fourteen related-origin assets (thirteen Armory icons plus one Blizzard concept image). Five additional positive Armory indexes redirected to real same-resource Wayback captures about an hour after the anchor; their exact observed locations are retained for a separate dated-supplement check. They are not accepted image payloads yet. The run now has 153 accepted images, 120 published, and 33 awaiting v30.

The root reviewed the next eighty-row local content audit against older records. Three encyclopedia illustrations and an already-empty Lordaeron map interval were excluded from re-querying; three logo items and three space-containing URI probes were deferred. The resulting seventy-target queue retains 71 actual page references, with one secondary-page hash completed against the frozen v29 provenance. Original audit files remain intact. A narrow Armory icon-origin extension passed root review and nine focused tests; v30 preparation will bind its new exporter hash. All acquisition so far used direct/proxy HTTP tools, with zero Firecrawl requests.


### 08:45 UTC — v30 inputs accepted; further news sources

The next export contains 33 accepted guide/related-site images, 156,857 bytes: 19 canonical images and 14 supplements (13 Armory icons and one Blizzard illustration). Root compared the source, original public copies and final maps, then scanned actual v29 pages: 33 missing addresses occur 142 times on five pages. The manifest-only estimate of 30 references on four routes is retained as an estimate. v30 is exporting once; it is not yet published.

News49 batches 1–4 added forty original illustrations, including the guild-bank GIF and two comic-cover thumbnails. Root independently checked each batch and viewed the actual images; these are reserved for a later export. Batch 5 is authorized for its final nine literal URLs. Acquisition remains direct-first with process-only proxy fallback, TLS verification and one serial Wayback worker; no Firecrawl requests.


### 09:00 UTC — v30 browser hold and literal image links

All 8,794 declared v30 objects were independently rehashed and the fixed static scope counted 1,033 missing addresses / 1,679 occurrences. The browser check exercised all 112 restored equipment references across ten tabs and six regional class-icon references, then found an obsolete Armory tooltip request assigning document.domain. v30 is preserved and held from publication. The profession selector checks also need to await their asynchronous javascript links.

A source-led follow-up found the archive banner inserted into a document.write string before the real body tag. An HTMLParser scan of all 1,049 HTML outputs identified five affected pages: collectors, lookingforgroup, outlandmap, story and scourgeinvasion. The exporter correction will locate actual head/body tags; a new version will retain the original scripts and put the banner in the page body. These are browser compatibility repairs, separate from downloaded image recovery.

News49 is complete: 49 original images / 480,639 bytes. The next static-content batch recovered eight arena thumbnails (70,901 bytes); two other exact indexes are complete and empty. Those index outcomes do not add payload404 results to the native-player-gallery ledger. The existing 47 Karazhan transport-unknown targets have been isolated for a later bounded replay check; all 79 already observed archive404 targets are excluded.

### 09:41 UTC — 指南配图、进度图与图片放大

七十项静态内容清单已检查完毕，取得五十四个原始图片资源，包括银月城设计稿、玛瑟里顿战斗示意图，以及燃烧远征副本进度图的底图和八层路径图。每批由主代理核对来源、完整解码与实际图片。它们属于文章和指南配图，仍与玩家动态图库的原编号图片分开统计。本轮累计接受 256 项图片，线上已发布 120 项，余下 136 项等待下一版整合。

旧 `popUpOmega` 在现代浏览器中会创建后立即关闭图片窗口。独立浏览夹具现已通过实际故事页点击：750×600 原图稳定打开，未取得的大图则打开本地缺图标记。第一次夹具检查误用了不存在的竞技场文章路径，失败记录保留；改用原页面引用的 `insider/11/arena.xml` 后八项检查通过。新工具只改变图片窗口适配，尚未代表整站导出验收。

v31 已准备的输入保持冻结，但未进行导出。后续合并到 v32，统一验证历史提示框、真实 body 中的归档横幅、图片窗口及新增资源；线上仍为 v29。进度图还有一处生成后的样式引号问题，正在沿单页处理步骤定位。

09:46 UTC 补充：单页十二阶段复现与 v29/v30 的文件逐字节一致；进度图属性中的引号始终正确保存为 `&quot;`。此前把 DOM 属性解码视图当作原文件字符，误判为样式序列化问题。此次没有改变生成器，后续直接验证新找回图片的实际背景与路径交互。[阶段证据](../research/continuous-recovery-20261018/integration/chart-style-diagnostic/stage-evidence.json)

### 10:02 UTC — 放大图来源检查完成

沿原文 `popUpOmega` 参数逐项解析的二十四个放大图链接，取得二十一个原图、2,386,986 字节：八张竞技场场景图、十三张银月城概念/建模/游戏图片。主代理逐张查看了原尺寸文件。另三个竞技场地址 `ss9.jpg`—`ss11.jpg` 在基准前为完整空索引；没有把这个结果计为原玩家图库的实际图片 404。三个批次的全部传输结束尾数为零，仍由现有代理取得，Firecrawl 请求数保持零。

当前累计接受 277 个新增图片资源；v32 固定纳入此前的 256 项，放大图二十一项留待后续版本。v32 准备还包含三处透明点击层兼容修复：`#mapPixel` 与两个锁定覆盖层复用既有透明像素，原 `bcattunement/images/pixel.gif` 仍属未取得，不能把兼容替换算作原资源恢复。两个旧浏览器专用背景声明保留原状。[工具检查](../research/continuous-recovery-20261018/publication/root-attunement-mask-tool-acceptance.json)


### 10:46 UTC — v32 本地验收完成；Karazhan 第一组复核

v32 的 8,897 个声明文件全部重新核对，实际目录 8,898 个文件。相对线上 v29 新增 136 个原始图片资源、1,891,055 字节，包括更多旧新闻配图、银月城和竞技场文章配图、玛瑟里顿插画、专业材料及副本进度图。三个生产浏览检查共通过 602 项检查，无外部请求或脚本错误；主代理查看九张页面截图。进度图连线、悬停与点击锁定、十组装备页签、七种专业与二十一项配方、稳定图片窗口均已实际操作。

全部 103 个本次新导入的原图经本地 HTTP 核对字节；其中 92 个普通资源在原元素中显示，玛瑟里顿 design.jpg 只出现在没有对应元素的 div.design 样式声明中，单独记为已保存而未显示。另九个路线图背景及一个红色插槽背景在专门场景中检查。早先浏览检查中的折叠新闻、动态定位器与未使用样式假设保留失败回执，修正检查方式后重测，未据此改写源页。固定静态范围现为 930 个缺图地址、1,573 处引用，新闻 387 处。原动态玩家图库继续单列，未把文章插画当作图库原图。

Karazhan 原有四十七项连接未决地址已复核前十二项，全部取得实际 Wayback 404；首次直连无响应后，现有代理正常取得响应。累计为九十一项已观察 archive404、三十五项仍待复核。此 404 只描述本次回放响应，不推断原站历史状态或所有存档点均不存在。尚无原图库新图片。线上仍为 v29，v32 正在进入发布；二十一张文章放大原图已保存，留待下一版接入。
