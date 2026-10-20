# 2026-10-20 资源恢复

从已发布的 v38 继续。本轮授权六小时，开始于 **08:33:22 UTC**，截止 **14:33:22 UTC（北京时间 22:33:22）**。新网络批次截止 13:15 UTC，新导出截止 13:25 UTC；14:00 UTC 前完成发布主体，14:15 UTC 转入收尾。

优先处理已有页面引用的六条新闻原图线索、尚未覆盖的新闻候选，以及剩余 29 个玩家图库晚期目录窗口。Karazhan 与 Black Temple 保持等待新证据的暂缓状态，不重复已完成的路径和时间窗。索引、原图实体和页面展示分别记录。

主代理负责计划、取舍、独立验收和发布；两名执行者分别负责本地来源去重和唯一串行获取。下载先 direct，连接失败后才使用进程内代理 `127.0.0.1:7890`，开启 TLS 验证。每批限定请求、时间和字节数，请求起点至少间隔五秒；429/503 或五次连续传输失败停止，并遵守至少 120 秒及 Retry-After 冷却。新控制必须晚于最新失败。

每批前后、每请求和大写入前检查 D 盘余量不少于 11,005,853,696 字节。原站、Source15、已验收版本和历史压缩包保持不变，新修复进入派生版本。原始 HTTP 元数据留本地；公开整理后的来源与验收。历史业务界面继续作为静态展品。验收通过后正常 commit/push，Pages 和处理后的离线包分别验证。

起始 main：`f84786d4820438213f0610df147fb78c3f0b2af9`；Pages v38：`78dac6c55286d43dc6a4e197a2b41d13cd6a9b4f`。上轮已补入 96 个图片资源地址，v38 离线包已发布。最新 Wayback 控制在 10 月 19 日 11:54 UTC 返回 429；本轮先做一次小规模连接检查，再决定下载批次。

总账：[status.json](../research/continuous-recovery-20261020/status.json)；任务：[tasks.json](../research/continuous-recovery-20261020/tasks.json)；前次记录：[2026-10-19](continuous-recovery-20261019.md)。

## 检查点

### 08:37 UTC — 恢复前检查

本地 main 与前次收尾一致，工作树干净，没有遗留下载进程；D 盘余量约 35.69 GB。旧自动接续调度已删除。本轮建立独立记录，保留旧回执与未完成队列。

随后独立检查 GitHub 远程引用、Pages 最近构建和 Release：main 与 gh-pages 均未变化，v38 构建成功，离线包仍公开。原始清单、Source15 清单与 v38 来源表摘要一致。本轮自动接续标识为 `wow`，到截止或工作结束时删除。

### 08:45 UTC — 六条新闻线索的范围纠正

六条 `koreapvp/ss*.jpg` 是 2004 年 “A Rumble in the Desert” 新闻注释块中的 `img src`，Source15 和 v38 均没有对应的活动图片元素。旧候选表误记成 `href`，且没有区分注释；新回执保留旧表并补充纠正。它们仍可提供历史截图关联线索，但不列作可见页面的六个缺图目标。本轮优先处理真实显示的新闻缺图。[范围核对](../research/continuous-recovery-20261020/publication/root-six-alias-scope-correction.json)

### 08:54 UTC — 控制请求返回 429，转入连接归因

新控制实际执行两次请求，父进程用时 7.42 秒：direct 在 TCP 连接前超时，代理完成 TLS 后收到 HTTP 429，立即停批。没有取得新图片，也没有据此新增资源 404 结论。主代理重新读取原始状态行、主体和计时，确认没有绕过冷却或复用旧成功控制。[来源验收](../research/continuous-recovery-20261020/publication/root-control01-source-acceptance.json)

直连日志把 `web.archive.org` 解析为 `108.160.167.147`。该结果需与可信 DNS 及本机代理/TUN 配置核对；当前只能确认 TCP 未完成，不能称为 TLS 证书失败。安排一次限时只读 DNS 调查，不改变全局网络设置、不向 Wayback 发出额外 HTTP 请求。本地来源去重继续。

### 09:02 UTC — 区分解析异常、TLS 中断和接口限流

Google 与 Cloudflare 的公共 DoH 接口均返回 `207.241.237.3`；ARIN 将前述 `108.160.167.147` 划在 Dropbox 注册网段。本机再次解析得到同网段另一个地址 `108.160.163.108`。未发现该域的 hosts 覆盖。公共递归解析结果与本机结果不一致，是解析路径异常的具体证据；Cloudflare 响应另含 EDE(18) 提示，原始结果保留。

主代理只向公共 DNS 返回的同一地址做了一次 TCP/TLS 握手，没有发送 HTTP：TCP 建立成功，TLS 在取得可验证证书前被重置。未改系统 DNS、hosts、代理或证书，也未关闭校验。因此，刷新 DNS 缓存本身不足以恢复下载；代理路径的 HTTP 429 是另一个独立障碍。[握手诊断](../research/continuous-recovery-20261020/publication/root-dns-route-tls-diagnosis.json)

### 09:08 UTC — 活动图片队列验收与独立来源调查

主代理重新解析 Source15 和 v38 的实际 `img src`，确认新闻候选 121–160 的四十个地址确实仍被页面引用，未把注释文本当图片；另核对十个未完成图库目录的 `addshots` 原引用及时间窗。这个结果用于准备下载，不表示图片已取得。[输入验收](../research/continuous-recovery-20261020/publication/root-prepared-queue-acceptance.json)

开始调查独立的 Common Crawl 数据。其[当前集合清单](https://index.commoncrawl.org/collinfo.json)列有 2008-05-09 至 2009-01-09、2009-07-02 至 2010-09-10 两组旧抓取；[原始数据文档](https://commoncrawl.atlassian.net/wiki/spaces/CRWL/pages/2850886)说明旧 ARC 保留原 HTTP 响应和实体，可按文件偏移定位。首批只检查集合与有限的原 URL/目录索引，若有合适捕获，再单独审查范围下载和原始实体验证。它是另一份抓取数据，不经 Wayback 回放或替换代理出口；Wayback 的冷却状态继续保留。

同时检查本地已有成功下载记录中是否存在尚未接入的同 URL 图片。未取得新的有效实体前，线上和离线版本保持 v38。

### 09:12 UTC — 同 URL 本地实体查漏

选定的下载清单未给四十个新闻目标和六条注释线索提供本地实体；另与已执行下载交叉核对的九十五个图片资源都已接入 v38，没有发现新的“下载成功但未部署”项。该范围不包括未解包的历史 ZIP 或未索引文件。一次 metadata 搜索误读了较大的旧清单，超过原定 64 MiB 索引读取限额；偏离留在[审计记录](../research/continuous-recovery-20261020/local-audit/existing-payloads/audit.json)，未据此把索引行当作图片。

下一步使用原 URL 的历史 CDX 内容摘要，与已有图片的实际字节摘要交叉比对，寻找不同 URL 保存了相同图片的情况。只凭文件名或视觉相似不会纳入恢复。

### 10:45 UTC — 从中断处续接

09:27 后本轮被中断，10:40 恢复检查时没有下载进程，Common Crawl 仍只有准备文件，未发出请求。两名执行者从各自检查点续接；没有重跑已完成的控制或图片检查，六小时截止保持不变。

主代理复核 Common Crawl 计划和请求边界后，允许执行一次集合清单及五个有限索引查询。该批仅取得独立来源的元数据，不取 ARC 或图片实体；Wayback 的失败状态没有因此被重新开启。本地摘要复用审计并行继续。

### 11:01 UTC — 独立抓取的百科首页

Common Crawl 元数据批次完成六次直连查询：集合和百科首页查询成功，新闻相关查询收到 502、Karazhan 目录查询收到 504、Black Temple 目录查询返回索引 404。网关错误留作未知；索引无结果也没有记成原图片的 404。[元数据验收](../research/continuous-recovery-20261020/publication/root-commoncrawl-probe01-source-acceptance.json)

随后仅下载百科首页一条 ARC 范围，HTTP 206，压缩记录 6,601 字节。主代理按 ARC 首行的声明长度分离记录和行分隔符，得到 **2008-07-20 的 52,400 字节 HTML**，内容摘要与索引一致。初版解析器把 IP 字段误作日期、并多保留了记录行分隔符，原报告保留，修正及实际字节在独立验收中说明。该晚期首页仅作补充来源，不替换五月基准，也没有部署其中脚本。[原文件验收](../research/continuous-recovery-20261020/publication/root-commoncrawl-arc01-source-acceptance.json)

首个整理检查点已正常提交并推送 main：`b115184`，Pages 与完整离线包保持 v38。

### 11:08 UTC — Wayback 本轮停止；补回两处相同字节资源

距首个 429 两个多小时后，再次执行一轮两请求控制：direct 连接超时，代理完成 TLS 后仍返回 429。没有重试其它 Wayback 地址；本轮这条路径停止，等待外部连接状态变化。[第二次控制验收](../research/continuous-recovery-20261020/publication/root-control02-source-acceptance.json)

本地摘要审计找到新闻 `ordernow.jpg` 和 `trolldire.jpg` 已在其它原站路径保存。主代理分别核对目标地址的历史 CDX、实际图片字节、Source15、旧捕获验收和完整图片解码，确认可复用两个实体。目标索引日期与实际文件来源日期分别保留，不伪造新的下载或回放记录。开始准备 v39：恢复新闻页图片，并将 2004 年订购促销条目改成静态历史展品。[复用来源验收](../research/continuous-recovery-20261020/publication/root-digest-reuse-source-acceptance.json)

### 12:18 UTC — 本地相同字节素材的扩大检查

将调查从新闻、下载两个索引文件扩大到本地全部 68 份旧目录索引，再检查其中符合条件的所有捕获版本。排除已补回、动态地址与注释线索后，862 个静态目标中有 293 个目标带有候选捕获，共 10,563 行、446 个内容摘要。与已接受来源建立的图片身份表交叉比对，未找到更多相同字节的可用图片。主代理另检查身份表未覆盖的 37 个小型图片文件（约 496 KB），结果相同，没有重复扫描整套图片。[扩大检查](../research/continuous-recovery-20261020/publication/root-all-capture-digest-audit-review.json)

另有一张音乐视频比赛的 Flash 背景与本地素材摘要一致；对应页面的 Flash 横幅元素处在原有注释中，来源链仍待整理。本轮不将它算作可见页面修复，也不重新显示已注释的元素。[范围说明](../research/continuous-recovery-20261020/publication/root-expanded-digest-audit-review.json)

v39 的来源准备保留 v38 全部 655 个图片覆盖项、三十九张指南大图及二十二张预览，另加入两条复用地址。新日期字段和历史展品改写通过相关单元检查；实际导出、浏览与线上对象另行验收。

### 12:26 UTC — 独立来源的精确查询停止

最后一批 Common Crawl 原定检查五个已有新闻地址。实际前两个查询均收到 504，按连续网关失败的停批条件结束；后三个没有发送，未取得索引行或新图片。这里记录的是索引服务的网关失败，图片是否存档仍未知。本轮结束这条获取路径，进入两处已验收修复的导出与发布。[验收](../research/continuous-recovery-20261020/publication/root-commoncrawl-probe02-source-acceptance.json)

### 12:40 UTC — 两处新闻图片的浏览验收

v39 完成一次导出，主代理逐一核对 9,115 个声明文件及来源表，保留 v38 的全部既有对象。实际增加两张 JPEG、修改四个派生对象；百科首页、网站首页和两张新闻页通过浏览检查，777 次回环请求没有外部请求或页面错误。两处图片均正常解码显示，2004 年促销条目呈现为带日期说明的静态展品。[本地验收](../research/continuous-recovery-20261020/publication/root-v39-local-acceptance.json)

进入 main、Pages 和处理后离线包的发布步骤。此次没有新增下载图片，玩家原图库的恢复数量未变化。

### 12:53 UTC — v39 上线与便携包验收

main 检查点 `000a30d0` 已正常推送。Pages 首次直连推送触发低速上限；保留失败记录，核对既有本地提交的七个变化对象后，以进程内代理推送同一提交，未重建或 force push。新构建 `60104e48` 完成，七个线上对象均通过直连核对。[发布摘要](../research/continuous-recovery-20261020/publication/v39-pages-publication-summary.json)

新版便携包为 534,242,751 字节。主代理读取全部 9,122 个成员并从新解压目录启动包内服务器，56 个路径的 112 次 GET/HEAD 检查通过。此时公开离线包仍为 v38；v39 正在上传已验证的发布草稿。

### 13:05 UTC — 离线包上传改用进程内代理

直连 ZIP 上传达到 600 秒上限后停止。核对同一草稿及已上传的说明、校验文件，仅补传缺少的 ZIP；没有重建包或覆盖已成功附件。归档获取的 Wayback 与 Common Crawl 停批状态未改变。

### 13:17 UTC — 离线包发布与本轮收尾

代理补传 ZIP 成功。v39 Release 的三项附件在发布前后均与本地一致，标签指向 `000a30d0`；公开 ZIP 的 HEAD 与校验文件 GET 也通过检查，直连失败与代理成功分别保留。[Release](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/tag/archive-20080512-browser-20261020-v39) · [公开下载检查](../research/continuous-recovery-20261020/publication/root-v39-public-download-acceptance.json)

本轮补回两处新闻图片地址，未新增下载图片或玩家图库原图。已调查的二十一个图库晚期索引窗口沿用此前结论，另二十九组仍待查；这项调查数量不表示已恢复二十一个图库。准备好的四十条新闻目标仍未补齐，Common Crawl 精确查询中的三个未发送地址与十个优先图库目录一并留在后续队列。Karazhan、Black Temple 继续等待新来源线索。

Wayback 两次控制均以代理 429 停止，Common Crawl 最后一批以两次 504 停止；本轮不再发出归档请求。本地已存索引与当前图片的扩大摘要检查未发现更多可见图片候选，已验收内容均完成发布，因此在授权截止前收尾并删除 `wow` 自动接续。冻结清单与 v38、v39 来源表再次核对一致，D 盘余量 49,722,601,472 字节。

[累计结果与后续队列](../research/continuous-recovery-20261020/publication/root-run-closeout.json)记录来源、实际获取、浏览、发布和未完成项；本页、README、CHANGELOG 与验收资料随收尾提交正常推送。
