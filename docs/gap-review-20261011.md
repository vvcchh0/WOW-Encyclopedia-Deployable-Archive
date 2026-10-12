# 17 项资源缺口复核（2026-10-11）

本次逐项复核原来的 **5 项未取得、8 项错误内容、4 项仅晚期有效文件**。结论是：**没有恢复出新的有效 2008 原件；合并已有各批次响应后，应记为 13 项错误响应、4 项晚期有效补充。** 52 个核心页面和 437 个已选用基准文件保持不变。

这里的“未取得 0 项”仅表示这 17 个 URL 均已有可追溯的响应或错误实体证据，不表示缺图已经补齐。13 个错误实体仍不能用于还原对应图片或功能文件；4 个有效晚期文件仍不能作为 2008-05-12 的原件。

## 分类更正的依据

原来五项 `missing` 是 2008 候选目录没有纳入实体，并非全部备份中从未取得响应。此前 2010 下载批次已保存这五个请求的最终 HTML：两个百科按钮地址跳转到晚期游戏指南，三个共享图片地址跳转到 404 页面。本轮重新读取对应清单行和 ZIP，长度、SHA-256、CRC 均通过。

三个共享地址还查到了各自 2008-04-02 的精确 CDX 行，摘要均为 `ESCAKPP7M4OJDVRYD2BXP7KLBKPT2RNS`。它们与已保存的 27,977-byte 404 HTML 完全匹配，SHA-256 为 `f662...`（完整值及原始来源见机器清单）。这是目标 URL 的早期错误内容证据，可以复用保存的错误字节，无须再下载同一 404。目标 URL 的索引时间与供复用实体的实际观察时间、URL 和响应头分别保留。

旧前缀结果已经包含 `header-quicklinks.jpg`、`menu-gameguide-off.gif` 的 HTML 行；问题在于旧候选筛选和跨批次合并没有把这些错误实体纳入五项缺口。不能把“没有有效图片候选”表述为“没有任何捕获”，也不能仅凭前缀查询缺行判断一个准确 URL 没有存档。

## 逐项结论

以下路径均属于原 `www.worldofwarcraft.com`。日期为 UTC。表中的晚期指南日期是最终响应的实际捕获日期，不是原图片 URL 的捕获日期。

| 原始路径 | 复核后的证据和状态 | 对百科重建的用途 |
|---|---|---|
| `/info/encyclopedia/images/closemenu.gif` | 旧批次已保存 2013-01-15 的游戏指南 HTML；本轮到 2011 年末的精确 CDX 返回空。错误响应。 | 百科菜单开关的活动交互图片，仍缺有效原图。 |
| `/info/encyclopedia/images/minus.gif` | 旧批次已保存 2011-07-26 的游戏指南 HTML；新 CDX 仅有当日 301 HTML。错误响应。 | 百科展开分类的活动交互图片，仍缺有效原图。 |
| `/new-hp/images/header-quicklinks.jpg` | 2008-04-02 07:08:44 的精确 CDX 摘要匹配已存 404；另有旧批次晚期 404。错误响应。 | 共享 CSS 的 `#container-quicklinks h3`，52 核心页中未证实匹配 DOM。 |
| `/new-hp/images/menu/leftMenu/menu-gameguide-off.gif` | 2008-04-02 07:09:01 的精确 CDX 摘要匹配已存 404。错误响应。 | 共享 CSS 的 `.leftMenu-gameGuide-off`；核心页实际使用另一组 `menuGameGuide-*` 类，未证实调用该候选。 |
| `/new-hp/images/menu/leftMenu/menu-gameguide-on.gif` | 2008-04-02 07:08:18 的精确 CDX 摘要匹配已存 404。错误响应。 | 共享 CSS 的 `.leftMenu-gameGuide-on`，未证实匹配核心页 DOM。 |
| `/info/encyclopedia/images/articles/alleriawindrunner.jpg` | 实际最终捕获 2012-09-13，游戏指南 HTML；到 2010 年末的精确补查没有图片候选。错误响应。 | 词条 315 的直接插图，仍缺有效原图。 |
| `/info/encyclopedia/images/articles/cenarioncircle.jpg` | 实际最终捕获 2012-07-22，游戏指南 HTML；补查没有图片候选。错误响应。 | 词条 349 的直接插图，仍缺有效原图。 |
| `/info/encyclopedia/images/articles/malfurionstormrage.jpg` | 实际最终捕获 2012-07-22，游戏指南 HTML；补查没有图片候选。错误响应。 | 词条 474 的直接插图，仍缺有效原图。 |
| `/info/encyclopedia/images/icons/SentientMortals.jpg` | 2008-04-02 捕获已经是原站 404 HTML；CDX 摘要匹配保存的实体。错误响应。 | 51 个数字词条直接引用的背景图片，仍缺有效原图。 |
| `/new-hp/images/menu/backGif.gif` | 已保存的 2008-05-12 21:05:28 实体为原站 404 HTML。错误响应。 | 共享 `screenie.js` 的交互赋值；另一路径 `lightbox/backGif.gif` 不能冒充该 URL。 |
| `/new-hp/images/menu/fwdGif.gif` | 已保存的 2008-05-12 21:05:31 实体为原站 404 HTML。错误响应。 | 同上；`lightbox/fwdGif.gif` 属于不同路径。 |
| `/new-hp/js/blank.html` | 2013-04-14 的站点迁移/错误 XHTML，不能作为原来的空白页。错误响应。 | 通用首页分支旧菜单脚本的条件 iframe 依赖。 |
| `/shared/wow-com/images/subnav/dot.gif` | 2013-07-18 的错误 XHTML，无法解码成 GIF。错误响应。 | 通用菜单脚本生成的条件菜单图片。 |
| `/new-hp/images/back.png` | 本次精确查询范围内最早有效记录仍为 2011-12-19 13:38:46；128-byte、2×1 PNG 完整解码通过。晚期补充。 | IE `AlphaImageLoader` 样式分支。 |
| `/new-hp/images/menu/mainmenu/back.png` | 同上，与另一 `back.png` 完全相同；未发现早期字节证据。晚期补充。 | IE 样式分支；相同字节不能制造早期 URL 捕获。 |
| `/new-hp/images/countrymenu-bg.gif` | 最早有效记录仍为 2011-03-30 03:58:17；571-byte、149×21 GIF 完整解码通过。晚期补充。 | 通用首页分支国家菜单脚本。 |
| `/new-hp/layout/menu.xml` | 最早有效记录仍为 2008-09-14 05:50:20；重新下载的 5,820-byte XML 与已存实体完全相同，严格解析通过。晚期补充。 | `layout.xsl` 实际加载的共享菜单文档，捕获晚于基准。 |

百科自身需要关注的仍是六项图片：三幅词条插图、`SentientMortals.jpg`、`closemenu.gif`、`minus.gif`。另外十一项属于共享外壳候选或依赖，影响须按实际分支判断；其中三个共享 CSS 选择器尚未证实在核心页实例化，不能把 17 项全部说成页面上必然可见的破损。

## 查询、验收和边界

本轮有限查询共 **31 次精确 CDX**，30 次 HTTP 200，1 次 Cenarion HTTPS 等价形式读超时；失败未作为空结果，也未重复请求。另下载 1 次已知晚期 `menu.xml`，与原件摘要相同。两个文件名检索没有提供可用恢复线索。所有网络工作已停止，没有启动定时任务。

错误组查至 2010 年末；未取得组和晚期组查至 2011 年末。查询不用多余通配符，原始响应及请求参数逐次保存。部分 scheme/default-port 别名返回等价结果，没有形成独立的历史版本证据。空结果只能描述本次准确查询的返回，不能证明 Archive 永久没有该文件。

独立验收覆盖原 17 项的 29 条候选记录、来源 ZIP CRC、响应体长度/SHA-256、图像完整解码、菜单严格 XML 解析；另外核对五项遗漏的旧响应清单、ZIP 和字节。原全量包、原 2008 索引及文件映射均保持不变。CDX `length` 是存档记录长度，不按本地响应体长度相等来验收；字节复用依据是 CDX 摘要与响应体 SHA-1 Base32 匹配。

机器结果采用单独的 [复核覆盖清单](../research/gap-review-20261011/reviewed-index-overlay.json)，绑定原索引 SHA-256；没有静默改写首轮取得记录。按全部既存证据，454 个逻辑 URL 为 **437 个选用原件 + 13 个错误响应 + 4 个晚期有效补充**；有效资源覆盖没有增加。

## 文件入口

- [原 17 项分类快照](../research/gap-review-20261011/baseline-17.json)、[原实体独立验收](../research/gap-review-20261011/baseline-entity-validation.json)。
- [8 项错误内容复查](../research/gap-review-20261011/errors/review-report.zh.md)、[17 项用途审阅](../research/gap-review-20261011/applicability/applicability-review.md)、[4 项晚期资源复查](../research/gap-review-20261011/late/report.md)。
- [原始查询与新增证据验收](../research/gap-review-20261011/evidence-validation.json)。
- [本次复核证据增量包](../artifacts/WOW_Encyclopedia_20080512_gap_review_20261011.zip)，配套 `.sha256` 和 `gap-review-20261011-package-verification.json`。

增量包收录本轮逐项报告、原始 CDX、响应元数据和用于复核的去重实体；与原全量来源包配合使用。错误 HTML 始终保留为证据，没有放入基准图片文件树。后续离线重建仍应显式记录未恢复原图、晚期补充及兼容改动。
