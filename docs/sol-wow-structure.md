# 2008-05 官网结构专项调研

> 主任务后续状态（2026-10-11）：下文是首份调研时的本地证据快照。其后已取得并批准`/index.xml`真正官网首页（20080512205648）及`/info/` Guide入口（20080512205037），并完成基准前850项正文恢复增量；下文“当前没有获准首页原件”等描述保留为当时的发现，不能用作最新缺口结论。最新进展见[资源恢复记录](resource-recovery-2008.md)及对应浏览报告。

任务来源：研究 2008 年 5 月附近 worldofwarcraft.com 的目录、页面和资源组织，为 [资源恢复任务](resource-recovery-2008.md) 提供线索。只读既有原件；本报告与 `research/sol-wow-structure/` 是本次唯一写入范围。首份报告于 2026-10-11 形成，后续补充以本文件为准。本次未联网、未启动 Archive 请求。

## 首轮实质结论

1. **Game Guide 334 是待恢复队列计数，不是特殊目录或 334 份已确认正文。** `sidebar-inventory.json` 中含 Game Guide 分类的去重 URL 共 354，动作分为 334 candidate、15 exclude、5 skip_existing。来源 `navtree.js` 有 464 个真实 Menu 定义（另一个匹配行只是注释示例），包含首页锚点、重复天赋/职业入口、FAQ、声望、交通、PvP、历史和资料片宣传页，规模有真实导航结构依据。
2. **两份导航脚本没有显示后期数据被替换的证据。** `.navtree.js` 与 mirror 原件逐字节一致，原件实际捕获于 `20080512204446`；`.navtree-main.js` 也一致，捕获于 `20080512204753`。`WoW Classic` 在该脚本中指向 `/misc/features.html`，与 Burning Crusade、Wrath 并列，不能仅凭名称判定为 2019 Classic 污染。Wrath 宣传路径本身已出现在上述 2008 捕获脚本中。以上证明的是当时导航含有这些链接，不证明每个目标正文已取得或内容属于相同日期。
3. **`.menu.xml` 应单列来源时间。** 项目现有说明记录它是 `2008-09-14` 补充，不应与两份 5 月导航脚本合称同日原件。尤其侧栏菜单与浮动导航并不完全同步，应保留多来源证据。
4. **`.xml` 后缀不等于需要浏览器再执行 XSL。** 已读百科 `index.xml` 先有 `xml-stylesheet` PI，却紧接 `<html>`、完整 head/body 和展开侧栏；map 把其列为 html。真正布局模板 `/new-hp/layout/layout.xsl` 的 `page` 模板会调用 `document('/new-hp/layout/menu.xml')`、构建新闻和导航。应先检查实体根标签与 MIME，再决定按 HTML 服务还是构建 XML+XSL 闭包，避免对已展开 HTML 再转换。
5. **官网首页当前没有获准 2008 原件。** 已有扩展全量 map 的 `/` 实际为 `20071207185956`；`/info/basics` 为 `20060209042121`。它们不在 14 项 `offline/approved-expansion-map.json` 中，仅可比较结构。侧栏清单仍把两者标成 skip_existing，建议主任务重新核对 skip_existing 与时间批准状态的交集。现有 `/` 离线别名也不能证明 Current News 原件已恢复。
6. **Media 的真实菜单入口是 `/downloads/`。** `.menu.xml` 的 Overview、Screenshots、Movies、Music、Wallpapers 和 Other Downloads 分别指向 `/downloads/`、`/downloads/ssotd/#latest`、`/downloads/movies.html`、`/downloads/sounds.html`、`/downloads/wallpapers.html`、`/downloads/other-downloads.html`。`/media/` 暂无这份菜单的真实链接证据，应作为可能别名核验，不能替代真实入口。

## 恢复顺序

- P0：确认 `/`、`/index.xml`、`/info/`、`/info/index.xml` 的同时间窗口实体及真实跳转；先解决首页/Guide 是否缺正文。
- P0：确认 `layout.xsl`、`/new-hp/layout/menu.xml`、共享 CSS/JS 与动态图片拼接。XML 源页需模板闭包；已展开 HTML 以实体中实际资源为准。
- P1：恢复真实侧栏入口和 Current News 内容区实际图片，再继续下载子页；电影列表正文可恢复，客户端和大视频保持排除。
- P2：按 12 个 Guide 分支恢复正文；同页片段不增加独立请求，账号/Armory/论坛和提交端点不扩展。

## 来源证据与时效

| 来源 | 实际时间 | 本次核验 | 用途 |
| --- | --- | --- | --- |
| [navtree.js](../mirror/20080512/www.worldofwarcraft.com/shared/wow-com/includes-client/navtree.js) | 2008-05-12 20:44:46 UTC | 与 `.navtree.js` 逐字节一致 | Guide 深层目录 |
| [navtree-main.js](../mirror/20080512/www.worldofwarcraft.com/shared/wow-com/includes-client/navtree-main.js) | 2008-05-12 20:47:53 UTC | 与 `.navtree-main.js` 逐字节一致 | 主站浮动导航 |
| [layout.xsl](../mirror/20080512/www.worldofwarcraft.com/new-hp/layout/layout.xsl) | 2008-02-24 09:43:26 UTC | 与 map SHA-256 一致 | 布局、新闻、XML 页面模板 |
| [.menu.xml](../research/site-recovery-2008/.menu.xml) | 2008-09-14 05:50:20 UTC | 与晚期 ZIP 的对象完全一致；SHA-256 `b17f55397b566f5a5f60be6dd4d9939169d1cfb31f9cea196493dd5bd37f51d7` | 有日期标注的侧栏补充 |
| [获准扩展 map](../offline/approved-expansion-map.json) | 2008-04-02 至 2008-05-12 | 14 个实体摘要一致 | Downloads、故事、社区等真实页面 |
| [2007 首页比较件](../research/sol-wow-structure/reference-homepage-20071207185956.html) | 2007-12-07 18:59:56 UTC | 从既有备份 ZIP 读取，摘要一致 | 仅用于理解首页结构；不批准并入锚点 |

454 项源记录包括 437 个 mirror 原件、14 个获准扩展实体、2 个较早比较件和 1 个晚期菜单补充。本次读取原件的 SHA-256 均与其索引一致，没有修改原件。`sources.json` 同时保存原 map 的时间分类、索引时间和已验证的 payload reuse 字段。部分图片实际实体时间晚于锚点，应继续遵循原 map 已有的摘要复用证据，不能仅按本报告的实际捕获日期布尔字段重新批准或否定它们。

## 首页与 Guide 的可执行线索

本次复用了主任务已经保存的 prefix-CDX 文件，没有发网络请求。以下索引行可交回现有下载流，**CDX 200 不是正文验证**：

| priority | 逻辑目标 | 本地索引中的真实 original | 捕获时间 | 原始证据 |
| --- | --- | --- | --- | --- |
| P0 | `/index.xml`，Current News 首页首选候选 | `https://www.worldofwarcraft.com/index.xml` | `20080512205648` | [015-b0aa1ba25127c96f.json](../research/site-recovery-2008/prefix-cdx/015-b0aa1ba25127c96f.json)，JSON 数组第 480 行，摘要 `FEGEUCTBIRVWSDNVMG3T7D574B4IJWWS` |
| P0 | `/info/`，Guide 入口 | `https://www.worldofwarcraft.com/info/` | `20080512205037` | [001-43e85457972488fa.json](../research/site-recovery-2008/prefix-cdx/001-43e85457972488fa.json)，JSON 数组第 587 行，摘要 `UMCDSLGANU52BCPLZI26AVO73TO7JSI2` |
| P1 | `/downloads/`，Media 入口 | `https://www.worldofwarcraft.com/downloads/` | `20080512205924` | [002-5270118aef6000f1.json](../research/site-recovery-2008/prefix-cdx/002-5270118aef6000f1.json)，JSON 数组第 183 行；获准本地实体已存在 |

这里“数组第 N 行”指展开后的 CDX 记录序号，包含首行字段名，不是文件编辑器的物理文本行；原始证据 JSON 另外保留来源文件和 `row_1based`。首页候选依然需要内容核验和离线路由别名确认。`/info/index.xml`、`/info/index.html`、`/index.html` 和 `/media/` 在本报告中都是待证实的 alias probe，不因拼写相近而自动合并。

`/` 的本地 2007 比较件不能代替上述 2008 `/index.xml` 候选；`skip_existing` 应至少分别记录“存在原件”“时间允许”“正文有效”。对保存下来的有限 CDX 查询未命中的路径，只能说该批记录未命中，不能说从未存档。

## Game Guide 的实际规模与内容类型

334 个待恢复目标分为 **259 个 `.html`、38 个 `.xml`、37 个目录 URL**。这是请求候选的扩展名分类；38 个 XML 后缀目标尚不能全部判定为原始 XML。目录 URL 也需要保留最终尾斜杠，以正确解析正文中的相对链接。

Guide 的 12 个分支如下。数量是每一分支内部去除片段与重复链接后的 URL 数，含记录但不获取的服务链接；分支间有重叠，不能相加当作总页数。

| 分支 | 分支内去重 URL | 代表路径 |
| --- | ---: | --- |
| Introduction | 15 | `/info/beginners/index.html`、`/features/index.html` |
| Getting Started | 35 | `/info/basics/gettingstarted.html`、`/info/basics/chat-*.html` |
| Character | 74 | `/info/races/`、`/info/classes/`、天赋与专业 |
| Reputations | 40 | `/info/basics/factions/`、外域声望、Armory 外链 |
| Items | 16 | `/info/items/`、物品数据库外链 |
| The World | 47 | `/info/basics/worlddungeons.html#…`、副本、事件 |
| Transportation | 18 | 飞行、坐骑、船、飞艇等子页 |
| Player Interaction | 30 | 组队、公会、交易、邮件等子页 |
| Player vs Player | 46 | `/pvp/`、战场、竞技场、奖励 |
| FAQ | 30 | `/info/faq/`、资料片 FAQ、账户支持外链 |
| Story | 31 | `/info/story/`、6 章历史、巨魔 13 项、百科 |
| About Game Guide | 5 | `/info/faq/guide.html`、内容索引、归档新闻 |

大量条目来自合理的深层展开：同一职业有法术、提示、天赋等子页；同一副本有地图、任务、敌人、提示等子页。另一方面，`worlddungeons.html#Blackrock Depths` 等是同页片段，不能逐片段发请求；天赋同时出现在 Classes 和 Talents 分支，FAQ、Story 也跨分支重复。464 个真实 Menu 定义经过去重、排除和既有状态筛选后得到 334 待恢复目标，规模本身没有混入其他游戏的证据。

三份指定菜单文本中未找到 StarCraft、Diablo、Cataclysm、Pandaria 或 2010 年代资料片标记。`WoW Classic`、Classic Dungeons 和 Classic Credits 与 BC 并列，且实际脚本捕获时间为 2008。故事页面内的 Warcraft I/II/III 书籍、游戏盒与历史链接是当时魔兽世界的内容背景；外部官网链接保持记录，不沿外链展开其他游戏网站。此结论限于已检查的导航和原件，不能替代未取得目标页的日期核验。

## 正文、XML 与模板组件

| 实体形态 | 本地实例与证据 | 恢复处理 |
| --- | --- | --- |
| 完整 HTML，URL 以 `.xml` 结束 | 52 个百科 `.xml` 源实体的首个元素全部是 `html`；`index.xml` 有完整 head/body、侧栏、正文 | 保留 HTML MIME 和实际内容；仅有 stylesheet PI 不能作为二次 XSL 转换依据 |
| 原始 XML 页面 | 布局 XSL 定义 `page`、`newsposts`、`encyclopediacontent` 等模板；其他 38 个 Guide XML 后缀目标待读取 | 若取得 `<page>` 等原始 XML，沿 PI 获取 XSL，再处理 `document()` 与输出资源 |
| XSL 模板 | `layout.xsl:197` 读取 `/new-hp/layout/menu.xml`；`:388` 可读取 `document($xmlfeed)`；`:805` 是 realmstatus 组件 | 菜单是布局依赖；新闻 feed 必须从源 XML 的 `xmlfeed` 属性确认，不能直接假设一定是 `/rss.xml`；Realmstatus 属在线状态功能，单列 |
| 菜单 iframe 容器 | `/new-hp/menus/menu1.htm` 至 `menu8.htm` 只有空 head、Go 占位函数、`menuN_var.js` 和 `menu132_com.js` | 是组件，不作为 8 篇正文验收；继续核对脚本及 iframe 加载 |
| 浮动导航与子导航 | `XmlSubnavTag` 模板加载 navtree、navtreefunctions、xmlnavassist 及 CSS | 共享脚本组成一个组件闭包；脚本内 URL 是导航证据，不是正文存在证明 |
| legacy HTC、Flash | PNG behavior、`png.htc`、SWF 等 | 按实际依赖与有限体积处理；不按正文统计。Flash 列表的 HTML、缩略图与大媒体下载分开 |

一个重要路径陷阱：XSL 生成的 `styles/stylesheet.css` 与 `images/icons/SentientMortals.jpg` 应相对于**输出页面**解析；不能因为字符串位于 `layout.xsl` 就生成 `/new-hp/layout/styles/…`。JS 用 `document.write` 或 `innerHTML` 生成的相对路径也应以承载它的页面为基准。清单已把这些未决表达式放入 `unresolved-templates.json`，没有把表达式原样提交为可下载 URL。

## 图片与 shared 目录

- `/new-hp/` 保存新站外壳：布局 XSL、侧栏 XML、8 个菜单 iframe、`menuN_var.js`、`menu132_com.js`、配色与图片。`loader_screen.css` 实际导入 `newhp_basic.css`、`newhp_layout.css`、`newhp_icons.css`、`newhp.css`，必须继续沿 CSS `@import` 和 `url()` 提取。
- `/shared/wow-com/` 保存跨页面的检测、wow.js、导航、羊皮纸、边框、图标和字母装饰。旧的 wow.js 预载 `/shared/wow-com/images/menu/mainmenu/*`，新 CSS 同时引用 `/new-hp/images/menu/leftMenu/*`，两套路径共存不是单凭目录名可以判定的污染。
- `/shared/global/menu/topnav/` 是地区站、Armory、论坛的全局栏。`buildtopnav.js` 的 fr/de/es/en/ko/zh/ru 等分支属于区域选择逻辑，不是目标站别名关系。
- 新闻布局的真实规则是 `/new-hp/images/icons/{icon}.gif`，缺省 `/new-hp/images/icons/news-wow.gif`，证据为 `layout.xsl:450-453`。应从取得的新闻 item 的 icon 值生成具体 URL；不能只搜 `<img>` 后就认为新闻依赖已闭合。
- 新闻正文图片另有 `/news/images/YY-MM/…`。2007 比较首页中确实存在 `/news/images/07-11/11-28-07-1.jpg` 等，但这些只能作为目录规则比较；2008 Current News 的具体文件必须从 2008 首页或 feed 再提取。
- `xmlnavassist.js:6-8` 拼接 `/shared/wow-com/images/subnav/icon_`、菜单标题小写和 `.jpg`；不能下载包含 `+ Menu1[0] +` 的字符串。应结合所选菜单分支或实际生成 DOM 确定文件名。
- `screenie.js:308` 从 shotList 图片名把 `.jpg` 换成 `-thumb.jpg`。图库页需同时提取 shotList、缩略图和展示原图；`:301` 的 `images/photos/test.jpg` 位于注释中，是示例，不是下载线索。

## 域名与别名边界

| 域/变体 | 本地证据 | 建议 |
| --- | --- | --- |
| `www.worldofwarcraft.com` 的 HTTP、HTTPS、`:80`、有无尾斜杠 | CDX 和获准实体实际包含这些变体；2008 `/index.xml`、`/info/`、`/downloads/` 的 CDX original 是 HTTPS | 用逻辑请求键去重，同时保留真实 original、捕获日期和跳转链；不要因 HTTPS 字样便判现代污染 |
| `worldofwarcraft.com` 裸域 | 保存的 CDX 中存在同路径记录 | 可作为有限别名查询线索；同一时间、同一实体需靠摘要/跳转确认 |
| `media.worldofwarcraft.com` | Movies 原件链接到 video_loader、AVI、MP3，旧菜单也有 BC minisite | 资源/宣传子站，不能一概重写为主站；视频与客户端不抓取，有限静态图按真实引用另评估 |
| `armory.worldofwarcraft.com`、`www.wowarmory.com`、论坛域、signup | 导航内真实存在 | 明确排除在线服务和社交展开 |
| `wow-europe.com`、韩国/台湾等官方地区站 | global topnav 的语言分支 | 记录为地区站参考，不证明美国页面的镜像等价 |
| `www.blizzard.com`、`us.blizzard.com` | Press、Support、Fan Art、Store 等外链 | 按用途记录；不扩展账号、商店和其他游戏网站 |

## 输出与验收

- [candidate-urls.json](../research/sol-wow-structure/candidate-urls.json)：每个逻辑 URL 只有一条，保留所有来源文件、实际物理行号、原始 URL、日期、标签、优先级、排除理由和已知实体。目录尾斜杠、HTTP/HTTPS 与裸域仅在逻辑键上规范化；原始证据没有丢弃。索引页别名没有自动合并。
- [candidate-urls.csv](../research/sol-wow-structure/candidate-urls.csv)：便于浏览的精简清单；完整证据以 JSON 为准。
- [sources.json](../research/sol-wow-structure/sources.json)、[analysis.json](../research/sol-wow-structure/analysis.json)：输入摘要、字节核验、Guide 统计和 skip_existing 时间问题。
- [local-cdx-alias-evidence.json](../research/sol-wow-structure/local-cdx-alias-evidence.json)：复用的本地索引证据；不表示本任务新增下载或完成正文验收。
- [unresolved-templates.json](../research/sol-wow-structure/unresolved-templates.json)：动态拼接、XSL 输出相对路径与注释示例；须结合真实输出页面解析。
- [analyze_local.py](../research/sol-wow-structure/analyze_local.py)：离线复现入口，仅读现有来源，只写本目录。
- [validation.json](../research/sol-wow-structure/validation.json)：本次最终检查结果。

最终清单共有 **1,750 个去重 URL**：419 项有已知本地实体，787 项为本次未获取的候选，59 项仅由较早比较首页提供线索，485 项排除或按用途人工复核。优先级计数为 P0 306、P1 390、P2 510、C 59、X 485；这些计数包含已知实体，不能当成新增下载量。454 项源记录的摘要核验无失败，6 个输入索引/导航文件摘要未变，URL 唯一性与报告链接检查通过。47 项未决模板/生成标记表达式另列，未当作具体下载地址。

P0 表示入口、共用外壳与模板依赖优先核验；P1 表示栏目入口、页面静态资源；P2 表示后续公开正文；C 表示仅较早比较材料的链接；X 表示明确排除或必须人工按用途复核。`local_entity_known` 只代表本地有可核对实体，不代表本次新批准、视觉验收或恢复闭包已完成。候选 URL 只说明来源可追踪，不能等同存档存在、内容有效或已完成恢复。

本次不修改主工具、manifest、approved map 或其他报告，不向其他任务发送消息。剩余实际获取和浏览验证由已授权的主恢复任务继续在现有两个 Archive 请求流内执行。
