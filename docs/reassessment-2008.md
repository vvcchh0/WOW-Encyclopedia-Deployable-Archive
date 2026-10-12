# 2008 基准与版本选择复核

2026-10-10：用户提供了 2010-12-03 的 XML 解析错误截图与 2008-05-12 的正常页面截图，并要求先下载样本、对照结构再判断。本报告记录该复核，替代此前关于 2010-12-03“最晚有效入口”的结论；原下载和原压缩包保留。

## 已确认的回放差异

2008-05-12 首页原件为 51,686 字节，以 `text/html;charset=UTF-8` 返回；2010-12-03 原件为 46,355 字节，以 `application/xhtml+xml;charset=UTF-8` 返回。两者第一行均为：

```text
<?xml-stylesheet type="text/xsl" href="/new-hp/layout/layout.xsl">
```

这一行没有 XML 处理指令需要的 `?>`。HTML 解析容错可以接受这类序列，而严格 XML 解析失败。正常 Wayback 回放的独立 Firecrawl 浏览器提取在 2008 页面取得百科主内容，在 2010 页面仅取得 `ParsePI: PI xml-stylesheet never end` 错误，复现用户发现。错误页虽返回 HTTP 200，仍然不可按正常页面判定。

原始实体的摘要与 CDX 一致，因此现有证据不支持“本次下载截断了文件”；也没有足够证据将 MIME 差异的责任归于原服务器或 Archive 的某一层。用户截图的 873 行与远端回放的 981 行属于各自回放后的文档，不能直接套在只有 841 行的 2010 原件上。

证据：[2008 回放](../research/reassessment-2008/evidence/firecrawl-replay-2008.json)、[2010 回放](../research/reassessment-2008/evidence/firecrawl-replay-2010.json)、[本地结构复核](../research/reassessment-2008/structure/structure-analysis.md)。浏览器提取证明主内容出现或解析失败，不等于全页面像素和全部依赖的完整验收。

2010-11-24 首页以 `text/html` 返回，正常回放能取得主内容，是一个需要继续核查的较晚候选；尚不能据首页推断整套词条均可正常访问。[该次观察](../research/reassessment-2008/evidence/firecrawl-replay-20101124-observation.json)。

## 正常回放与较晚候选

| 请求锚点 | 已观察结果 | 判断范围 |
|---|---|---|
| 2008-05-12 21:00:44 | 首页有主内容；400、339、346 三个代表词条回放到当日 21:39 左右，均为 HTML、取得预期正文、没有 ParsePI | 有正常访问证据，尚未验收全部 51 个词条的视觉与依赖 |
| 2008-07-20 17:35:56 | 首页提取只有 Wayback 外壳；两个词条实际跳到 2008-08-10 HTTPS 捕获，均出现 ParsePI | 本次没有得到一套比五月更晚且正常可导航的页面集合 |
| 2008-08-29 17:38:53 | 已保存原件是 5,518 字节、严格 XML 可解析的 `<page>` 文档；正常回放提取只有 Wayback 外壳 | 原始 XML 值得保存，但 XSL 转换及完整页面可用性尚未证实，不能将小文件直接当作完整 HTML |
| 2010-11-24 17:33:13 | 首页有主内容；该锚点之前最近的 51 个词条 CDX MIME 全为 `application/xhtml+xml` | 首页可提取不能证明整套词条正常 |
| 2010-12-03 21:49:58 | 首页、400、346 均出现 ParsePI；339 的工具响应因本地序列化失败未保存 | 已有足够反例撤回“正常可用版本”；未保存响应不作为缺失证据 |

[代表词条的更正后完整证据](../research/reassessment-2008/browser/reassessment-summary-corrected.json)、[较晚候选报告](../research/reassessment-2008/later-candidates/later-candidates-report.md)、[离线 CDX MIME 对照](../research/reassessment-2008/evidence/anchor-mime-index-comparison.json)。CDX 对照是“锚点之前最近捕获”，普通 Wayback 回放则可能选择距离最近的后续捕获；两种策略不能混用。初次六次词条提取中有本地命令长度导致的保存缺口，随后仅重新取得三个 2008 响应，原失败证据保留；更正后的 JSON 已验证可解析。

## 原始文件下载与逐项比较

2008 样本已下载 **24/24 项**：首页和 7 篇代表词条、3 个百科 JS/CSS、1 个共享 XSL、12 张图片。包括 Factions、High Elves and Blood Elves、Blood Elves、Burning Legion、Cenarion Circle、Alleria Windrunner、Malfurion Stormrage。下载器实际发出 24 次请求，退出码 0，无下载失败；原始实体合计 **564,537 字节**，ZIP 内压缩载荷 **119,525 字节**，分卷文件为 125,019 字节。

独立导出验收核对全部 24 个实体的 SHA-256 与长度，22 项具有明确 CDX 摘要并全部匹配；另两项按锚点最近回放取得。12 张图片均通过对应 JPEG/GIF 文件签名检查，未将 HTML 错误页算作图片。ZIP CRC 校验通过。下载时的通用内容验证器没有对 `sample_resource` 角色计图片数，因此其图片计数为零；本报告的 12 张来自对照脚本及独立导出的实际签名检查。

与已有 2010 原件对照，**15/24 项 SHA-256 相同**：三个百科脚本/样式以及十二张图片；九项不同为八个 HTML 页面和共享 `layout.xsl`。七篇词条按 `articleContentContainer` 提取并规范空白后的正文 **7/7 相同**，不是仅比较标题或全站导航。2008 共享 XSL 带 Burning Crusade 主题，2010 共享 XSL 带 Wrath 主题。这说明 2010 实体有保存价值，但主要正文未因时间更晚而产生本次可见更新，外壳与回放方式反而影响了可用性。

详细对照：[逐项中文报告](../research/reassessment-2008/downloads/comparison.zh.md)、[机器可读比较](../research/reassessment-2008/downloads/comparison.json)、[下载摘要](../backups/20080512-sample/summary.json)。

样本不是单秒原子快照。共享 XSL 实际回退至 2008-02-24；羊皮纸背景实际为 2008-05-12 21:13:21，比锚点晚约 13 分钟，已明确记录。下载计划中的首页取得同日 20:46:42 捕获；它与用户指定 21:00:44 原件逐字节相同。导出目录的首页使用已保存的**精确 21:00:44 原件**，并分别保留两次捕获的来源，未篡改时间戳。

## Thuum 对照与可检查的目录

对 `D:\Thuum\thuum-backup\thuumbackup` 只读扫描得到 **101,089 个文件、3,062,212,968 字节**，其中 **100,722 个 HTML、3,025,051,284 字节**。文件名中有 6,766 个 `_page=` 变体、496 个字典 `letter` 参数变体；有限样本中五个页面共享相同外壳前缀。其大体积来自十万级页面和查询参数组合；目前百科导航只有首页与 51 个词条，不能据 Thuum 的 3 GB 推导百科也必须达到 GB 级才完整。用户所述约 40 MB 压缩包未另行打开验证。

Thuum 的“URL 对应本地文件”结构适合后续恢复。先前百科使用的内容寻址 ZIP 也保存了文件，但肉眼难以检查。本轮额外导出未修改实体，按原 URL 路径排列：

```text
samples/20080512/
  url-map.json
  www.worldofwarcraft.com/
    info/encyclopedia/
      index.xml
      315.xml ... 474.xml
      scripts/ styles/ images/
    new-hp/layout/layout.xsl
    shared/wow-com/images/parchment/plain/dark.jpg
```

[URL、MIME、日期与摘要映射](../samples/20080512/url-map.json)。文件扩展名仍忠实保留 `.xml`，实际内容可能是 HTML；后续本地服务应按映射处理 MIME。这里只导出样本原件，还没有补齐全部依赖或重写绝对链接，因此直接双击文件不代表离线镜像已还原。[Thuum 结构报告](../research/reassessment-2008/structure/structure-analysis.md)。

## 修正后的决定与交付

**采用用户提供的 2008-05-12 21:00:44 作为下一阶段完整获取和重建的基准锚点。** 它具备首页与代表词条正常回放、足够的资源原件及一致的百科正文证据。2010 原件作为补充保存，不能继续标为正常可用版本。现有检查没有证明五月是全档案中绝对最晚或资源零缺口的版本；七月、八月与十一月的局部观察不足以替代整套验证。

本轮完成的是用户要求的结构复核、有限样本下载和比较，不是全量 2008 镜像或完整离线网站。下一阶段应按该锚点逐项获取全部导航正文与活动依赖，区分核心百科和全站共享主题，保留实际日期与缺口；完整性同时验收正文、资源闭包、MIME 和浏览器表现。

样本及本轮证据包：[WOW_Encyclopedia_20080512_sample_and_reassessment.zip](../artifacts/WOW_Encyclopedia_20080512_sample_and_reassessment.zip)。包中含 URL 目录、下载原始 ZIP/清单、比较报告、截图证据及已有 2010 对照原件，便于离线复核。2008 与 2010 原件分别保留在命名目录中，附带 2010 文件不表示该版本可正常回放。包内有逐文件 SHA-256，外部附整个 ZIP 的校验值与 [打包验证记录](../artifacts/reassessment-package-verification.json)。此前 2010 原包不会被重写。

复现导出与打包：`python packaging/package_reassessment.py --materialize-only` 只导出并校验样本；省略该参数会创建新的复核包，若同名包已存在则停止，避免覆盖历史产物。下载与打包继续执行整个目录 14,000,000,000 字节上限、D 盘至少 10 GiB 空闲和额外写入裕量。
