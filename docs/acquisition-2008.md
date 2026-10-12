# 2008-05-12 全量文件获取

**后续更正：** 本文保留首轮全量获取时的 5 未取得 / 8 错误 / 4 晚期分类。用户要求逐项复核后，合并此前已存响应与精确 CDX 证据，当前应为 **13 错误响应 / 4 晚期有效补充**；有效 2008 原件未增加。详见 [17 项复核报告](gap-review-20261011.md) 和独立覆盖清单，原索引、文件树映射及全量 ZIP 未修改。

用户在复核报告之后确认以 `20080512210044` 为基准，并授权全量获取文件。本轮承接 [复核结论](reassessment-2008.md)，保存原始文件及来源，不将回放可用性与本地实体校验混为一谈。

## 获取范围与选择理由

- 精确基准首页与导航中的全部 51 个词条；同时检查百科目录索引中是否存在未入导航的历史文件。
- 词条实际引用的百科图片、脚本、样式，以及 2008 Burning Crusade 外壳所需的共享 CSS、JS、XSL、菜单文档和静态资源。旧 CSS 中非活动候选单列。
- 沿静态引用递归发现依赖，包括 HTML 属性、CSS url/import、XSL import/include/document 和有明确证据的 JS 字面路径/数组组合。其他栏目正文、第三方广告跟踪和 Wayback 自身资源不属于镜像范围。

核心页面优先选锚点之前最近且表示有效的捕获；首页使用用户指定的精确捕获。百科同次抓取日内稍后静态资源可单列实际日期，其他晚期素材不自动当成 2008 原件。原始 HTTP 200 错误实体也保存为证据，但不计有效资源。

已有 2008 样本和已验证的原件复用以减少重复请求。另一种优化是对照 2008 CDX 的原始摘要：若已保存实体的 SHA-1 Base32 与该捕获摘要相同，可复用字节，但必须同时记录“2008 索引日期”和“实体实际观察日期”，不得伪造 2008 响应头或 Memento。每份实体仍保留 SHA-256。

## 执行与验收

正文、依赖闭包和缺口恢复分别由有边界的执行任务负责，最终整合独立验收。最多两个 Archive 请求流；CDX 与实体获取分批、有请求和截止时间上限，连续站点失败时停止该批次，不无限重试。原件按 SHA-256 压缩去重，原 URL 的文件树在下载完成后按有效映射导出。

整个 `D:\WOW_Encyclopedia` 不超过 14,000,000,000 字节，D 盘至少保留 10 GiB 空闲，另留 256 MiB 写入裕量。旧的 2010 包与本轮之前的复核包保持不变。

验收覆盖实体 CRC/SHA/长度、已有 CDX 摘要、页面 MIME 与正文、图片/字体等文件签名、捕获日期、依赖引用闭包与有限正常回放。完整获取的完成情况以“已发现 URL 全部有明确取得或缺口状态”为准；没有足够捕获证据的资源不能用现代替代文件掩盖。

## 当前证据位置

- `research/acquisition-2008/core/`：52 页计划、缓存复用来源与正文验收。
- `research/acquisition-2008/dependencies/`：依赖图、有限批次计划、内容分类与闭包。
- `research/acquisition-2008/recovery/`：缺口变体、恢复证据与未覆盖范围。
- `backups/20080512/`：本轮原始响应 ZIP 与 HTTP 清单。

以下为 2026-10-11 实际验收结果；计划数量与有效取得数量分别列出。


## 最终取得结果（2026-10-11）

本轮获取阶段结束，状态为 `completed_with_archive_gaps`。454 个已发现逻辑 URL 均有已保存响应或有边界的恢复证据，未尝试项为 0；资源覆盖仍有以下明确缺口，不能称为零缺失镜像。

| 范围 | 实际结果 |
|---|---|
| 核心正文 | 首页 + 51 个词条，52/52 有效 HTML；正文、长度、SHA-256、既有 CDX 摘要通过 |
| 依赖计划 | 402 项，其中 401 项活动依赖、1 个历史 `index.html` 跳转入口 |
| 活动依赖 | 384 有效基准资源；5 未取得实体；8 错误内容；4 仅晚期有效捕获 |
| 导出文件树 | 437 个文件 = 52 核心 + 384 活动依赖 + 1 历史入口，4,653,310 bytes（4.44 MiB） |
| 图像完整解码 | 335/335 通过：GIF 211、JPEG 120、PNG 4；不是只检查扩展名或魔数 |
| 静态引用交叉验收 | 52 页及百科 CSS 的 90 个唯一 URL 全部纳入；28 个 JS/HTC 源的 49 个具体静态 URL 全部纳入 |
| 历史字节复用 | 337 条 CDX/本地摘要匹配证据，256 个唯一 URL；原始获取时间与早期索引日期分别保留 |

文件树位于 `mirror/20080512/`。本轮正文体量约数 MiB，不能以 Thuum 的 100,722 个 HTML/查询变体和 3 GB 解压体量推断本百科应该同样巨大；本次 51 个词条已经按官方导航逐项核对，来源包还包含共享模板、原始 ZIP、索引与研究证据。

437 个选用实体的时间分类为 `{"anchor_consistent": 368, "same_day_static": 69}`；其中 201 个选用实体依靠早期 CDX 摘要证明其较晚观察到的字节已经存在。2008-05-12 同日稍后静态捕获按已声明策略选用，并未伪称抓取于精确锚点。首页仍严格为 `20080512210044`，SHA-256 为 `4951546ef139ac64d93f1811dec06ef2b84dea22cd9d278fac9262070b079ec3`。

## 缺口与晚期补充

表中路径均属原 `www.worldofwarcraft.com`。晚期有效实体、HTTP 200 错误实体及失败请求证据均保留在来源 ZIP/索引中；它们没有进入基准文件树。未取得项的有限查询结果不能证明 Archive 从未存过该文件。

| 状态 | 原始路径 | 实际捕获时间（UTC） | 证据分类 |
|---|---|---|---|
| 未取得实体 | `/info/encyclopedia/images/closemenu.gif` | `—` | 有限查询未找到可用早期图片捕获 |
| 未取得实体 | `/info/encyclopedia/images/minus.gif` | `—` | 有限查询未找到可用早期图片捕获 |
| 未取得实体 | `/new-hp/images/header-quicklinks.jpg` | `—` | 有限查询未找到可用早期图片捕获 |
| 未取得实体 | `/new-hp/images/menu/leftMenu/menu-gameguide-off.gif` | `—` | 有限查询未找到可用早期图片捕获 |
| 未取得实体 | `/new-hp/images/menu/leftMenu/menu-gameguide-on.gif` | `—` | 有限查询未找到可用早期图片捕获 |
| 错误内容 | `/info/encyclopedia/images/articles/alleriawindrunner.jpg` | `20120913173326` | 跳转到后来的游戏指南 HTML |
| 错误内容 | `/info/encyclopedia/images/articles/cenarioncircle.jpg` | `20120722010627` | 跳转到后来的游戏指南 HTML |
| 错误内容 | `/info/encyclopedia/images/articles/malfurionstormrage.jpg` | `20120722010627` | 跳转到后来的游戏指南 HTML |
| 错误内容 | `/info/encyclopedia/images/icons/SentientMortals.jpg` | `20080402034834` | 原站 404 HTML |
| 错误内容 | `/new-hp/images/menu/backGif.gif` | `20080512210528` | 原站 404 HTML |
| 错误内容 | `/new-hp/images/menu/fwdGif.gif` | `20080512210531` | 原站 404 HTML |
| 错误内容 | `/new-hp/js/blank.html` | `20130414034902` | 晚期 XHTML 错误/站点迁移页面 |
| 错误内容 | `/shared/wow-com/images/subnav/dot.gif` | `20130718223807` | 晚期 XHTML 错误页，非图片 |
| 仅晚期有效捕获 | `/new-hp/images/back.png` | `20111219133846` | 图片有效；未证明属于基准时期 |
| 仅晚期有效捕获 | `/new-hp/images/countrymenu-bg.gif` | `20110330035817` | 图片有效；未证明属于基准时期 |
| 仅晚期有效捕获 | `/new-hp/images/menu/mainmenu/back.png` | `20111219133846` | 图片有效；未证明属于基准时期 |
| 仅晚期有效捕获 | `/new-hp/layout/menu.xml` | `20080914055020` | 菜单 XML 有效；捕获晚于基准 |

百科自身的六项图片缺口是三幅文章插图、`SentientMortals.jpg`、`closemenu.gif` 与 `minus.gif`；其余属于共享外壳。旧 CSS 注释中的 `featured_textbg.png` 另保留为非活动历史证据，不计入本轮活动依赖缺口。

恢复研究先后保留了错误前缀查询与修正查询。最初含多余通配符的 16 次查询不能作为无存档证据；修正后的美国百科图片/官网图片前缀查询分别返回 55/592 行，并有正对照。该研究批次实际网络尝试 22 次，超过原 20 次规划预算的两次偏离已在 `recovery-catalog.json` 中记录；没有隐藏或无限重复。玛法里奥图片的旧连接失败后来以正常连接取得实体，确认是晚期指南 HTML，而非图片。

## 验收与使用边界

- 原件 ZIP CRC 与按对象名的 SHA-256 无错误；437/437 导出文件与来源字节、长度、SHA-256 完全一致，Windows 路径与大小写碰撞检查通过。
- 独立页面引用检查没有解析错误或未计划 URL；JS/HTC 审计修复了 `url(images/...)`、嵌入 HTML 图片、两个域名根目录 pixel 及 `.htc` 引用的漏项。31 个通用 XSL 动态表达式已经审阅，未为这 52 个核心页实例化其他具体资源；8 条 JS 动态/分隔表达式的边界保留在独立报告中。
- 最终来源映射区分逻辑角色与原下载批次角色，并完整提升嵌套 ZIP 条目字段；请求时的回退锚点不再误记为 CDX 捕获日期。修正前的试导出及映射保留在 `integration/`，原件字节没有改动。
- 所有批次已终结。旧失败行保留，并对后续成功取得的请求标记 superseded。IE 五项合并摘要不具有原下载器 `finished_at` 字段；另用绑定清单、摘要及 ZIP 哈希的 `completion.json` 记录实际本地终结验证，没有补造旧时间。
- 正文 `.xml` 文件实际为 `text/html`。后续重建须使用映射记录的 MIME，处理绝对链接和旧脚本；本轮尚未进行本地网站渲染、视觉还原或 IE/Flash 执行验证。
- 导出前整个工作区约 98.1 MiB，D 盘约 22.10 GiB 空闲；打包仍执行 14 GB 总预算和 10 GiB 空闲加 256 MiB 写入余量检查。

最终包为 `artifacts/WOW_Encyclopedia_20080512_full_source.zip`；包内含 `FILE_SHA256SUMS.txt`。包外 `.sha256` 与 `full-2008-package-verification.json` 给出实际包大小、全包哈希、逐成员 CRC/SHA 验收及旧包不变校验。

可复核入口：

- [最终选择与缺口索引](../research/acquisition-2008/integration/index.json)、[统计](../research/acquisition-2008/integration/summary.json)、[原 URL 映射](../mirror/20080512/url-map.json)。
- [导出字节验收](../research/acquisition-2008/acceptance/export-validation.json)、[图片解码验收](../research/acquisition-2008/acceptance/image-decode-validation.json)。
- [页面引用验收](../research/acquisition-2008/acceptance/audit.zh.md)、[JS/HTC 审计](../research/acquisition-2008/acceptance/js-static-reference-audit.md)、[XSL 分支审阅](../research/acquisition-2008/acceptance/xsl-conditional-review.md)。
- [最终依赖闭包](../research/acquisition-2008/dependencies/closure-report.md)、[早期摘要复用](../research/acquisition-2008/reuse/verified-reuse-summary.zh.md)。
