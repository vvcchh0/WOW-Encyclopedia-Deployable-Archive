# 非图库内容复原：2026-10-21

本轮从v39继续，优先恢复已有正文和交互。三处Flash兼容展示随v41上线；天赋计算器和BlizzCast阅读页随v42发布。v45进一步加入专题正文与关联图标，45个线上对象核对完成，离线包暂为v39。当前发布状态以[工作总账](../research/continuous-recovery-20261021/status.json)和[更新记录](../CHANGELOG.md)为准。

## 天赋计算器

九职业页面共用`localize.js`和`printOutTop.js`。Source15两份文件完整，通用导出把JavaScript字符串内CSS的转义引号误当作字符串边界，导致语法错误和空白天赋树。

`tools/talent_compat.py`仅接受两份精确来源摘要。前者修复职业模板链接和固定资源路径；后者保留原字节及其动态背景表达式。导出器识别后跳过这两份脚本的通用URL转换，原加点逻辑保持。公开测试携带这两份纯JavaScript来源fixture及来源说明，脱离维护者本地原始备份也能执行。

九职业初始页面合计缺1,259个图片目标，包括技能图标、树背景和布局素材。其中1,232个目标已显示为静态缺图占位；动态请求另观察到61个404目标，与前者部分重叠。61项中有27张树背景和34个技能图标地址（17组普通/暗色图标）。脚本故障、原始图片恢复和关联来源补充分别记录。

主代理核对了合并集合，每个目标均不在v42实际文件、路由及来源表中。[逐职业盘点](../research/continuous-recovery-20261021/integration/talents/full-image-scope/README.md)与[可协作缺图清单](../research/continuous-recovery-20261021/publication/talent-missing-image-targets.json)可供后续寻找素材。此计数描述本地缺口，不判断所有网络存档均已缺失；悬停后才生成的状态图尚未覆盖。

v45加入986张来自[CraftedRO的WotLK离线计算器备份](https://github.com/CraftedRO/Offline-talent-calculator-for-WotLK-3.3.5a/tree/4c8013cf40d0edf84625430eaf43b86d97880ae0)的同路径36×36图标。固定提交、源路径和原字节进入独立来源目录，页面注明后期关联来源，2008年天赋数据与脚本保持。树背景、近似技能名和跨职业图片没有自动接入。

九职业实际完成加点、重置、非零模板保存、重开和刷新；主代理逐张查看了截图。静态占位与真实404合并后仍缺273个目标，含27张背景；[集合核对](../research/continuous-recovery-20261021/local-audit/v44/v44-gap-union-reconciliation.json)保留与初始清单的对应关系。这部分已随v45部署。

## 新增主站正文

同一Common Crawl集合取得九份2008年5月9–12日的精确来源。Source16新增战场截图比赛公告、Tinfoil Hat、双头食人魔、粉丝站计划、Molten Core趣味专题、2004年9月补丁说明和吟游诗人介绍七份正文；更新内容目录，另接通六个旧地址别名。每页标出其实际捕获日期。

旧比赛和招募均用历史措辞，比赛入口为“View historical contest”，不接受提交。比赛规则页未取得，保留缺口说明；没有把原公告中的计划写成已发生的评选结果。Tinfoil Hat的九片提示框背景与Molten Core返回箭头复用已保存的站内素材，来源表标为布局兼容复用；文章插图仍有缺失。[Source16验收](../research/continuous-recovery-20261021/publication/root-source16-local-acceptance.json) · [布局复用决定](../research/continuous-recovery-20261021/publication/root-source16-layout-reuse-decision.json)

## BlizzCast

从Common Crawl的`CC-MAIN-2008-2009`静态索引定位精确ARC成员，使用Range读取并核对ARC记录URL、时间、HTTP实体摘要和XML。取得以下来源：

| 来源 | 实际捕获时间（UTC） | 内容 |
| --- | --- | --- |
| Episode 1 | 2008-05-09 12:27:09 | Sam Didier、Jeff Kaplan访谈，19个对话块 |
| Episode 2 | 2008-05-09 06:21:14 | Chris Metzen、Geoff Goodman、Andy Chambers、Tom Chilton访谈，31个对话块 |
| RSS | 2008-05-11 19:31:52 | 两期目录与音频线索 |
| 首页 | 2008-05-15 21:04:12 | 简介与节目入口，作为晚期补充 |
| 目录 | 2008-05-15 22:41:16 | 节目说明，作为晚期补充 |

精确ARC文件名、偏移、压缩成员长度与来源摘要见[来源验收](../research/continuous-recovery-20261021/publication/root-blizzcast-source-acceptance.json)。原始ARC、HTTP头和未处理XHTML留在本地；公开阅读页保留访谈原文、人物标签、段落和时间码，公开来源表保留捕获信息及ARC定位。

`tools/blizzcast_reader.py`输出五个阅读页和一份本地样式，不依赖原站服务。原有菜单或新闻中的BlizzCast入口经精确来源匹配接通；首页的无斜线和目录斜线地址只映射到已取得的首页。此接入不扩大其他关联站点或历史业务路由。

原配图和音频尚未取得。八个图片/样式原站URL经过实际301、307跳转后均为404；两个音频URL在direct与代理均报证书名称校验错误，未取得音频响应。原站支线暂告结束，后续寻找存档和其他关联来源。[可及性检查](../research/continuous-recovery-20261021/publication/root-blizzcast-current-origin-accessibility.json)。阅读页采用新的排版，原站完整布局仍待恢复。

## 验收与后续

v42已核对全部输出对象、原有657个图片覆盖地址和三处Flash资源。实际Chrome逐一完成九职业加点、重置、非零模板恢复，五个阅读页和下载页、展开后新闻中的可见入口检查通过。main为`2577dcdc`，Pages为`fdc976ed`；24个线上对象与本地一致，均由direct取得。[线上核对](../research/continuous-recovery-20261021/publication/root-v42-pages-online-acceptance.json)

本地v45包含上述Source16正文、986张关联图标和两页布局修复，共10,130个文件，约629MB。67项相关检查通过，全部输出逐项核对；五页新的实际浏览检查通过。v44候选因比赛说明后的多余闭合锚点未发布，该问题在v45修复。九职业HTML和天赋脚本与已完成九职业浏览的v44相同，因此复用这部分浏览证据。[本地发布验收](../research/continuous-recovery-20261021/publication/root-v45-local-acceptance.json)

Wayback在本轮00:49 UTC返回429后停批；Common Crawl静态数据取得成功只说明该独立端点可用。下载继续direct优先，备用代理只作用于下载进程。完整进度见[当日记录](continuous-recovery-20261021.md)。

后续诊断观察到本机解析地址与两家DoH返回地址不同；对公共解析地址能建立TCP连接，但TLS握手仍被重置，未取得证书。因此尚未证明改DNS可以修复访问，也未改系统DNS、代理或证书。[诊断记录](../research/continuous-recovery-20261021/publication/root-wayback-dns-tls-diagnosis.json)

## 界面与关联图源补充

v46补入三色天赋状态框、Reset、Reset All及Printable Version六张界面图，另复用八片已有同站点数框GIF。九职业加点和重置检查通过，天赋缺图剩259个目标；已部署，60个线上对象核对通过。

ArchiveCraft提供Alleria、塞纳里奥议会和玛法里奥三幅配图的新线索，当前JPEG已取得并查看，作为单独标注来源的关联补充准备接入。原始目标捕获仍未找到；未导入该站正文、评论、脚本或表单。

## 百科与指南关联配图

v49补入Alleria、塞纳里奥议会、玛法里奥和The Broken四幅关联来源图片。页面给出ArchiveCraft来源链接；Alleria保留该站缩放JPEG。The Broken保留一张实际237×184缩略图，菜单点击使用同一素材，尚未补回标题图和大图。

奖励表的两个阵营按钮已改为已有图片的正确本地地址。奥尔多／占星者页面说明框仍显示undefined，正在从已保存的同专题令牌页面脚本提取原始说明，单独修复。[本地验收](../research/continuous-recovery-20261021/publication/root-v49-local-acceptance.json)

## 派系说明文字

v50本地恢复奥尔多／占星者说明弹窗。两段文字来自已保存的2008-04-02同专题令牌脚本；仅补入缺失说明，按钮切换、原奖励数据和令牌页保持。实际Chrome完成两个弹窗及两次派系切换，正文与来源对应，现已合入v51上线。

## 最终本地版本与剩余素材

v51接通一张已有Wrath字母图的单斜线地址，四页恢复显示。源GIF保留原字节，未扩展为通用斜线折叠，也未推断其他字母图片。v50的派系说明随本轮最终版本发布。

分轮浏览清单覆盖177条独立路径；已观察状态仍有411个缺资源目标，包含259个天赋目标和12个百科分类头像。完整动态状态尚未遍历。周年时间线的截图目录被旧脚本拼成异常路径，已确认是导出转换问题，列入后续图库工作。

[页面覆盖与缺口](../research/continuous-recovery-20261021/local-audit/non-gallery-closeout-v49-r3/README.md)保留版本、来源和观察类型。Wayback最新控制仍为429；本轮没有通过该路径取得新原图。

## v51发布验收

最终Pages版本为v51，80个线上对象与本地一致。浏览版ZIP约546MB，解压约634MB；独立成员检查与包内服务145个对象的GET/HEAD检查完成，实际Chrome再次验证派系说明和四页Wrath字母图。离线包发布结果单独记录，避免把本地完成等同于公开可下载。

[线上核对](../research/continuous-recovery-20261021/publication/root-v51-pages-online-acceptance.json) · [离线包验收](../research/continuous-recovery-20261021/publication/root-v51-portable-acceptance.json)

## Arathi指南预览

收尾调查确认页面的22个异常地址来自目录基址转换错误，其中20张精确JPEG已在本地。v52仅对该指南页的path赋值保留目录，同页导航继续指向首页文件。全文件核对和实际Chrome检查完成，20张预览恢复显示；ss17与ss18的缩略图仍未取得。这属于已有指南素材的显示修复，没有重启玩家图库下载。

修正后分轮清单为391个真实本地资源目标，旧411条观察路径及原报告保留供追溯。[修正清单](../research/continuous-recovery-20261021/publication/v52-remaining-resource-targets.csv) · [调查](../research/continuous-recovery-20261021/local-audit/underdev-final-routing-review/README.md)
