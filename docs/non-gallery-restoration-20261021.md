# 非图库内容复原：2026-10-21

本轮从v39继续，优先恢复已有正文和交互。三处Flash兼容展示已随v41上线；天赋计算器和BlizzCast阅读页进入v42派生导出，尚待整站浏览和发布验收。当前发布状态以[工作总账](../research/continuous-recovery-20261021/status.json)和[更新记录](../CHANGELOG.md)为准。

## 天赋计算器

九职业页面共用`localize.js`和`printOutTop.js`。Source15两份文件完整，通用导出把JavaScript字符串内CSS的转义引号误当作字符串边界，导致语法错误和空白天赋树。

`tools/talent_compat.py`仅接受两份精确来源摘要。前者修复职业模板链接和固定资源路径；后者保留原字节及其动态背景表达式。导出器识别后跳过这两份脚本的通用URL转换，原加点逻辑保持。公开测试携带这两份纯JavaScript来源fixture及来源说明，脱离维护者本地原始备份也能执行。

九职业初始页面合计缺1,259个图片目标，包括技能图标、树背景和布局素材。其中1,232个目标已显示为静态缺图占位；动态请求另观察到61个404目标，与前者部分重叠。61项中有27张树背景和34个技能图标地址（17组普通/暗色图标）。这与脚本故障分别记录，不用其他年代或同名近似图标替代。

主代理核对了合并集合，每个目标均不在v42实际文件、路由及来源表中。[逐职业盘点](../research/continuous-recovery-20261021/integration/talents/full-image-scope/README.md)与[可协作缺图清单](../research/continuous-recovery-20261021/publication/talent-missing-image-targets.json)可供后续寻找素材。此计数描述本地缺口，不判断所有网络存档均已缺失；悬停后才生成的状态图尚未覆盖。

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

代码检查和预览结果不能代替发布验收。新版本需核对全部输出对象、原有657个图片覆盖地址和三处Flash资源，实际浏览九职业加点、重置、非零模板恢复，以及五个阅读页和原站入口。通过后分别记录main同步、Pages构建、线上对象和离线包。

Wayback在本轮00:49 UTC返回429后停批；Common Crawl静态数据取得成功只说明该独立端点可用。下载继续direct优先，备用代理只作用于下载进程。完整进度见[当日记录](continuous-recovery-20261021.md)。
