# MEDIA 截图、旧新闻与导航补缺（2026-10-15）

本轮按栏目检查截图入口与实际图片捕获，修复已有页面的导航问题，并补取缺少的历史页面。重建基准仍为 2008-05-12；新增文件保留各自的捕获日期。原始来源与冻结的 `offline/site` 未改写，浏览修复在派生层完成。

## MEDIA Screenshots

官网 MEDIA 菜单中的 Screenshots 指向 **Screenshot of the Day**，来源入口为 `http://www.worldofwarcraft.com/downloads/ssotd/`，本地规范路由为 `/downloads/ssotd/index.html`。这与 Game Guide 下的 50 个玩家截图分区是两套图库。

入口页面实际捕获于 **2008-05-12 20:43:28 UTC**。旧脚本用对 `anachronos.xml` 的 HEAD 请求取得日期，再减去 `startDate=12671` 计算最新截图编号。本地服务器返回当前日期，会生成超出历史范围的编号。派生版改用页面的记录捕获日期，得到 **1340**，保留翻页、每页 9/12/16 张和编号大图跳转。这是根据原脚本计算出的截止编号，尚未由完整图片目录独立核对。

### 存档点调查

- 入口全时段 CDX 返回 **648 条捕获记录**，范围为 2007-10-11 至 2026-09-23；其中 2006–2010 年查询返回 520 条。记录包含重定向、重访和 URL 变体，不等同于 648 个独立内容版本。
- 精确查询 `.../ssotd/index.html` 在 2006–2010 年返回有效空数组；实际来源为目录尾斜杠地址，因此不能据此判断入口未存档。
- 图片目录未筛选查询取得两页各 1000 条记录，第二页仍有续页标记。本轮没有遍历全部未筛选记录。
- 同一路径按 HTTP 200 和图片 MIME 筛选的查询返回 **2 条图片记录**，无续页标记；两张均已实际下载和解码。网页捕获很多，查到的有效图片捕获很少。
- `ss1340.jpg`、其缩略图以及 `ss1314-thumb.jpg` 的本轮精确查询为空；只说明这些查询范围内没有记录。
- `showNumPages=true` 返回 HTTP 200、空正文，不作为有效索引或零条结果使用。

图片由 JavaScript 按编号拼接地址，这可能使网页与图片的捕获覆盖不同。当前证据尚不能确定历史抓取器漏图的具体机制，也不能把未检索到的文件判为永久丢失。

| 文件 | 实际捕获（UTC） | 尺寸 | 本轮结果 |
| --- | --- | --- | --- |
| `ss1314.jpg` | 2010-08-10 17:30:46 | 1024×640 | 原图已补回 |
| `ss1336.jpg` | 2010-06-02 10:23:29 | 1200×750 | 原图已补回 |

这两张是晚期捕获的补充素材。原始缩略图仍未取得，列表使用已验证原图缩放显示；未知图片继续显示缺图占位。导出时须显式使用 `--allow-later-image-supplements`，默认时间限制不变。

本轮 MEDIA 获取窗口执行 18 个源请求，收到 1,183,008 字节正文。查询、范围、图片来源与验收见[捕获台账](../research/media-screenshots-20261015/capture-ledger.json)、[整理后的结果](../research/media-screenshots-20261015/sanitized-summary.json)、[图片来源表](../research/media-screenshots-20261015/late-image-source-map.json)与[独立图片验收](../research/media-screenshots-20261015/root-image-acceptance.json)。原始响应头和追踪日志保存在本地。

Game Guide 的 50 个分区仍合计声明 1,684 张截图，其 3,368 个原图与缩略图实体未因本轮 MEDIA 恢复而补齐。

## Archived News 与导航

按多代 `navtree.js`、`menu.xml` 和布局侧栏展开盘点，共 **588 条菜单记录、411 个不同本地目标**。初始状态为 563 条已有内容路由、22 条外部或动态入口、3 条缺少导出路由。多代菜单会重复引用同一页面，条目数不作为完整页面数。

Archived News 正文原已保存。本轮重新回放两份源文件，均得到 HTTP 200，正文摘要与本地原始文件一致：

| 页面 | 实际捕获（UTC） | 本轮核对 |
| --- | --- | --- |
| `/info/archivednews.html` | 2008-04-02 03:01:56 | 126,020 字节，与已保存来源一致 |
| `/news/wow-news-06-2006.html` | 2008-05-12 20:56:11 | 84,871 字节，与已保存来源一致 |

修复旧新闻中五个已确认目标的兼容地址：`dailyquests.shtml`、`titles.shtml`、`benice.shtml`、`credits.shtml`，以及重复的 `/info/info/items/armorsets/`。这些地址映射到已有的真实页面；目标未保存时不会生成假内容。

Community 菜单存在 Fan Wallpapers 与 Fan Sites 共用 `Menu1_6_10`、父节点仍声明 10 个子项的问题。派生版保留 Fan Wallpapers 的编号，将 Fan Sites 改为 11，并同步父节点数量，恢复两个独立入口。

完整条目、来源与缺口见[导航盘点](../research/navigation-gaps-20261015/inventory.md)、[旧新闻链接检查](../research/navigation-gaps-20261015/archived-links.md)、[实现验收](../research/navigation-gaps-20261015/implementation-validation.md)和[旧新闻实际回放](../research/navigation-gaps-20261015/parent-wayback/summary.json)。

### 最后三个缺页的回放

8 个源请求取得两份有效的 2008 年页面，并识别两次错误正文回放：

| 目标 | 捕获 | 结果 |
| --- | --- | --- |
| Free Trials | 2008-04-02 00:40:57 | 取得历史试用选择页；派生展示须移除追踪和报名行为 |
| WLK Wallpapers | 2008-04-02 07:08:13 | 取得 HTML 对照页；后来确认较新的页面及素材已在冻结树中 |
| PvP Minisite | 候选 2009-05-08 03:29:38、2009-08-08 01:46:38 | HTTP 200，但正文均为历史 404 页，未纳入有效来源 |

这次补页脚本直接使用进程已有代理，没有单独重测 direct，偏离了 direct 优先约定。结果已如实标注；后续获取继续采用先 direct、失败再 proxy。查询范围、实际 Memento 日期与内容分类见[补页记录](../research/navigation-gaps-20261015/wayback-missing/sanitized-summary.md)。

独立本地素材检查随后发现，WLK Wallpapers 已保存 **2008-05-09 07:29:57 UTC** 的页面，但清单路由为 `/wrath//wallpapers.xml`，菜单请求为 `/wrath/wallpapers.xml`。实际文件和四套壁纸的 **28 张原图、4 张缩略图、4 张阴影 PNG** 均在本地。修复采用已确认的规范路由别名，继续使用较新的冻结页面；4 月 2 日对照页不替代它。见[壁纸素材检查](../research/resource-repair-20261015/wrath-wallpaper-audit.md)。

PvP Minisite 随后扩展查询至 2008 年以前：先 direct 超时，再 proxy 取得 **196 条 2005–2007 年 HTTP 200 记录**。最新的 **2007-01-15 22:39:11 UTC** 回放实际取得 20,761 字节 HTML，标题为 `World of Warcraft PvP Mini Site`，Memento 和 CDX 摘要一致。该页面纳入补充层；前面的两份 2009 错误正文仍排除。见[旧捕获查询](../research/resource-repair-20261015/pvp-pre2008-control/summary.json)和[实际回放](../research/resource-repair-20261015/pvp-pre2008-control/replay/summary.md)。页面包含旧 Flash，取得入口 HTML 不等于恢复 Flash 交互。

Free Trials 的原始捕获保留不变，浏览版改为介绍当年两个选项的静态展品，移除追踪脚本、cookie 初始化及报名跳转。它所引用的面板图片和页脚素材仍缺失。

## TLS 轮询与下载判定

按用户要求由 GPT-5.6 Luna Max 执行 **4 轮有界探测**，累计 6 个源请求。目标是已知可用的 Karazhan 地下城介绍页预览图，便于把连接失败与图片未存档区分开。

- 第 1、4 轮先 direct，均在 TCP 连接阶段约 4 秒超时，尚未进入 TLS，也没有源站 HTTP 状态。
- 4 轮 proxy 均完成 TLS、源站返回 HTTP 200，取得同一份 3,347 字节、150×110 JPEG，摘要和捕获日期一致；本轮未触发 429。
- 系统 DNS 观测地址在轮次间变化。没有修改全局 DNS、代理、证书验证或浏览器安全设置。

这表明本次代理控制请求可用，直连故障发生在 TLS 之前。此前的代理 TLS 故障具有间歇性，不能据单个控制对象推定所有 URL 都已恢复。轮询已结束，没有建立后台循环或定时任务。

同日较早的[DNS 与跨客户端对照](karazhan-tls-recheck-20261015.md#tls-判断)还发现，系统 DNS 与经代理获得的 HTTPS DNS 结果不同；但指定后者地址的 direct 请求仍在 TLS 阶段被重置。因此解析异常是线索之一，不能解释全部连接故障。本轮四次成功代理控制和实际补图、补页说明代理通路在这些请求时恢复可用。

共享传输工具同步修复两项判定：忽略代理 `200 Connection established`，取真正的源响应；实际捕获时间只从有效 Memento 读取，不再用请求中的时间提示代填。见[轮询记录](../research/tls-poll-20261015/summary.md)与[完整整理结果](../research/tls-poll-20261015/summary.json)。

## 构建与验收

第一版本地派生镜像 v6 已完成：8,442 个导出文件，8,304 个冻结来源记录，38 张独立补充图片。冻结清单摘要保持 `397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459`；构建后 D 盘空余约 42.9 GB，保留 10 GiB 加 256 MiB 缓冲。

相关传输、导出和图片补充层测试通过。实际浏览器验收的 4 个场景通过：截图首屏和翻页布局、`#1314` 大图、旧新闻及五处兼容路由、Community 菜单。观测中无外部请求、非 GET 请求、请求失败或控制台错误。首屏 12 个图片槽位中仅 `ss1336` 已恢复，其余 11 项仍显示缺图；检查通过不表示图库已完整恢复。

见[构建回执](../research/resource-repair-20261015/build-v6.json)、[主代理静态验收](../research/resource-repair-20261015/root-static-acceptance.json)、[浏览器结果](../research/resource-repair-20261015/browser/browser-check.json)与[截图](../research/resource-repair-20261015/browser/ssotd-first-screen.png)。本轮修复先在本地验收，线上站点和已有 Release 不随本地构建自动更新。

补入 Trial 与 PvP 后，最终源树 v7c 包含 **8,306 个记录**，保留全部 8,304 个冻结路由和两个兼容支持文件。主代理逐文件核对长度与摘要，36 个壁纸素材均可解码。见[源树构建回执](../research/navigation-gaps-20261015/v7c-build-receipt.md)与[主代理源树验收](../research/resource-repair-20261015/root-source-acceptance.json)。

Pages v7 导出 8,444 个文件，三个已识别的菜单路由缺口均可达。七个功能场景通过，但 PvP 页仍出现四个旧菜单脚本错误和一个 Flash CSP 错误，主代理未将它视为最终验收通过。后续派生修复保留静态外框与素材，将该页旧菜单替换为本地返回链接，并把空白 Flash 区域改成可见的缺失说明；原始 HTML、Flash 引用与脚本仍保存在来源文件中。[v7 浏览记录](../research/resource-repair-20261015/browser/browser-check-v7.json)保留了修复前的实际错误。

最终 **v8 已验收**：8,444 个导出文件、38 张独立补充图片；四组相关单元测试一次运行 **55 项全部通过**。七个浏览场景通过，页面错误、控制台错误、外部请求、非 GET 请求、失败请求及观测 404 均为 0。初次 v8 检查仅有 PvP 缺失说明的句式匹配失败；修正 checker 后在相同、未修改的镜像上单独复查 PvP，并保留六个已通过场景的记录。构建完成时 D 盘余量约 32.6 GB，高于保留阈值。

最终证据：[构建](../research/resource-repair-20261015/build-v8.json)、[55 项测试](../research/resource-repair-20261015/final-unit-tests.json)、[浏览验收](../research/resource-repair-20261015/browser/browser-check-v8.json)、[PvP 复查](../research/resource-repair-20261015/browser/browser-check-v8-pvp-recheck.json)、[主代理最终验收](../research/resource-repair-20261015/root-final-acceptance.json)和[PvP 最终截图](../research/resource-repair-20261015/browser/pvp-flash-rewards-v8.png)。当前成果保存在本地，线上站点与 Release 保持此前版本。

完整工作区中可用以下通路复现新源树和 Pages 派生版：

```sh
python research/navigation-gaps-20261015/build_v7c.py
python research/resource-repair-20261015/build_pages_v7.py --output .scratch/pages-resources-20261015-v8 --receipt research/resource-repair-20261015/build-v8.json
python tools/serve_pages_preview.py --site .scratch/pages-resources-20261015-v8 --port 8766
```

导出器拒绝覆盖已存在的输出目录。完整工作区须包含此前获取的来源包和图片来源表；Git 主树的保存范围见[文档索引](README.md)。
