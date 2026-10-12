# Warcraft Encyclopedia 第一阶段备份报告

> 2026-10-10 复核更正：本报告下方“最晚有效入口”“优先采用较晚版本”的选版结论已撤回。2010-12-03 正常 Wayback 回放因 `application/xhtml+xml` 与未闭合 `xml-stylesheet` 指令的组合发生解析错误；原件摘要校验通过不能证明正常访问。下文保留为原获取记录，正文/图片的“有效”指内容分类与保存完整性。新的选版依据及 2008 样本见 [复核报告](reassessment-2008.md)。原便携包保持不变。

来源：用户提供的 [2008-05-12 21:00:44 UTC 入口](https://web.archive.org/web/20080512210044/http://www.worldofwarcraft.com/info/encyclopedia/index.xml)。本阶段核查历史捕获、选择版本、下载原始响应并保留来源；文件整理与离线网站重建留待后续阶段。

## 选定版本

采用 [2010-12-03 21:49:58 UTC 入口](https://web.archive.org/web/20101203214958/http://www.worldofwarcraft.com/info/encyclopedia/index.xml)，即北京时间 2010-12-04 05:49:58。这是本次对原入口的 CDX 查询和实际正文检查找到的最晚有效原百科入口。

未折叠的入口索引与百科目录索引共同核查：2008–2011 年目录查询返回 2,220 条 HTTP 200 捕获，未达到 10,000 条查询上限。2011 年已观察到的后续入口为 HTTP 301，转向 Battle.net 游戏指南；跟随后的网页不再是原百科。因此不能只按回放页面最终的 HTTP 200 选版，也不能用这些捕获推导出精确撤站日期。

2010 年入口正文与 2008 年基准的主要文字相同，导航仍为同一组 51 个词条，`topic-list.js`、`cascade.js` 和百科样式表逐字节相同。所选版本的全部已知词条均有有效正文和对应索引摘要，因此优先采用较晚入口。每个词条选择锚点之前的最后有效捕获，并逐文件保存实际日期；这是一组有明确时间来源的文件集合，不是全站同一时刻的原子快照。

选版原始证据：[索引与探测报告](../research/inventory/inventory_report.md)、[未折叠目录索引](../research/inventory/prefix_2008_2011_raw_30ba9ec02e43a97d.json)、[2008/2010 首页比较](../research/homepage-comparison.json)。

## 已验证的核心内容

| 项目 | 验收结果 |
|---|---|
| 首页 | 1/1 有效 |
| 导航中的词条正文 | 51/51 有效 |
| 核心页面摘要与保存完整性 | 52/52 CDX SHA-1、SHA-256、ZIP CRC、实际时间戳通过 |
| 百科自己的脚本与样式 | 4/4 有效 |
| 百科目录图片候选 | 54 个地址中 52 个保存为有效图片，2 个实际是 HTML 错误页 |

部分词条原始 `h1` 为空，标题由旧站脚本填入；验收结合导航标题、初始化代码及正文容器判断，没有把空标题标签误判为缺失正文。核心词条捕获范围为 2010-02-10 至 2010-12-03。百科静态依赖可采用 12 月 3 日同次抓取中稍晚几分钟的捕获。

独立验收：[正文与资源报告](../research/validation/report.md)、[百科素材内容校验](../research/encyclopedia-assets-validation.json)。验收脚本的整体非零状态反映图片闭包缺口，52 个核心页面本身全部通过。

## 已知缺口与年代限制

- `images/articles/alleriawindrunner.jpg`、`cenarioncircle.jpg`、`malfurionstormrage.jpg`：在本次查询的原始路径索引中没有找到有效图片捕获；三者的锚点回放均转到较晚的 Battle.net 指南。后两项初次回放遇到连接错误，连接恢复后已重查。这些证据不能证明图片从未被存档。
- `images/icons/SentientMortals.jpg`：原始词条 CSS 引用的图标，本次取得的是原站 404 HTML；已观察到的索引候选也为 HTML。
- `images/closemenu.gif`、`images/minus.gif`：百科 `cascade.js` 实际引用的导航状态图。目录索引没有对应候选；补做回放后分别转到 2013 年、2011 年的 Battle.net 指南，未取得有效图片。
- `images/featured/featured_textbg.png`：本次取得的也是原站 404 HTML。它仅出现在旧样式注释中，属于额外保留的历史候选，不是当前正文的活动图片引用。
- `maievshadowsong.jpg` 已有有效 2007 年捕获，虽然不在 2008–2011 目录查询结果中，未列为缺失图片。

因此，正文文件覆盖完整；已识别的活动百科图片引用仍有 6 项缺口，另有 1 项旧样式注释候选。共享壳层素材的内容错误、日期漂移和优先使用的历史捕获详见统一来源索引。晚于 2010-12-03 的回放单独标为年代补充，不直接当作所选版本的原件。

缺口证据：[图片探测记录](../research/gaps/missing_image_probe.md)、[静态引用闭包](../research/validation/core-referenced-assets.json)。

共享壳层另有 3 个图片地址只取得原站 404 HTML：`header-quicklinks.jpg`、`menu-gameguide-off.gif`、`menu-gameguide-on.gif`。2008–2010 的补查未找到有效图片；2008 年以前的补查中，后两项无图片候选，第一项查询超时，保留为未覆盖的时间范围。没有据此断言这些图片从未存档。

## 最终获取统计

| 范围 | 逻辑 URL 覆盖 |
|---|---|
| 首页与词条 | 52/52 有效 |
| 原百科资产批次 | 58 个地址，56 有效、2 个 HTML 错误页 |
| 共享图片、菜单及新增菜单依赖 | 286 个地址均已取得响应，283 有效、3 个 HTML 错误页 |
| 研究时已保存的独立共享 XSL/CSS/JS | 23 个有效 URL，不重复计入百科批次 |
| 正文及脚本中额外发现的图片缺口 | 3 张插图和 2 张导航状态图，均未取得原图 |

统一优先映射共有 **414 个有效历史 URL 实体**，没有待下载的共享计划项。407 条压缩响应保存记录包含历史补件及错误证据；跨分卷按 SHA-256 归并为 397 个载荷对象。研究原始文件、基准版本和查询证据另外保留，不应与有效源 URL 数混算。

最终来源索引检查退出码为 0：所有分卷 CRC、SHA 命名对象、清单引用、实体长度及缓存摘要均通过。下载器的 7 个离线测试此前全部通过。网页的图片缺口仍在清单中，不因完整性校验通过而视为已补齐。

## 保存方式与恢复过程

采用 Wayback `id_` 回放保存未修改的 HTTP 响应实体，避免将工具栏、Firecrawl 提取文本或浏览器生成内容当作原件。响应按 SHA-256 命名、去重并直接压入 ZIP 分卷；每个 URL 的原始地址、请求时间、实际捕获时间、响应头和对象位置保留在 `manifest.jsonl`。研究时已下载的共享 XSL、CSS、JavaScript 原件和元数据一起收入最终包。

共享资源的初次两个批次因沙箱 TLS 连接路径异常停止，已有成功文件与失败记录均保留。同一控制 URL 在沙箱外、保持默认 TLS 验证时成功；随后仅对未完成项进行有界恢复。连接失败与 HTTP 200 的原站错误页分别记录。旧菜单 iframe 的 9 个字面脚本依赖也纳入文件获取。

较晚的共享 `menu.xml` 回放保留为证据，已成功取得 2008-09-14 的较早有效导航 XML，优先映射采用该历史候选。另有 6 张共享图片的最近回放在 12 月 4 日凌晨，比入口晚约两三个小时；已补取其 11 月 24 日或 30 日的历史捕获，6/6 与较晚实体的 SHA-256 相同，优先映射使用较早捕获。比较见 [historical-static-comparison.json](../research/historical-static-comparison.json)。没有通过关闭证书校验解决连接问题，也没有执行下载的远程脚本。

## 交付与空间

最终便携包：`artifacts/WOW_Encyclopedia_20101203_source.zip`，相邻 `.sha256` 为整个包的校验值。包内 `FILE_SHA256SUMS.txt` 保存逐文件摘要；包外 `package-verification.json` 保存最终 ZIP CRC、逐文件 SHA-256、文件数和磁盘读数。

完整下载统计与优先捕获映射以 [preservation-summary.json](../research/preservation-summary.json) 和 [preservation-index.json](../research/preservation-index.json) 为准。原始错误响应仍在包内，恢复文件时应使用内容判定与优先映射，不能把它们当成有效图片。

空间策略为整个任务目录不超过 14,000,000,000 字节，D 盘至少保留 10 GiB；下载及打包均带额外写入裕量。没有保存一份完整解压的网站副本。此阶段尚未进行浏览器离线渲染验收，不宣称已完成全站视觉还原。

复现方法及下载器参数：[archive-method.md](archive-method.md)、[tools/README.md](../tools/README.md)。
