# 玩家截图图库：缺失范围与存档可及性

核查日期：2026-10-20；浏览镜像：v39。范围为 Game Guide → **Player Screenshot Galleries (50)** 的全部分区。

## 结论

**全部50个玩家图库都缺少原图库图片，范围远大于 Karazhan 和 Black Temple。** 原页面声明1,684张截图，分别需要1,684张原图和1,684张同目录缩略图，共3,368个文件目标。原始本地站点、冻结 Source15 和当前 v39 中，这些精确目标均为0个；没有发现已经下载、却在部署时漏掉的这批文件。

50个图库页面及 Zul’Aman 的入口包装页均能打开。浏览器实际执行后，50个页面首屏共580个原图库图片格全部显示缺图 SVG；原始图片路径和截图数量仍被保留。SVG 返回 HTTP 200，因此“没有图片404请求”不能用作原图已恢复的判断。

目前能看到的图片来自另行保存的指南层：6组共22张预览，另3组共39张指南大图。本轮浏览记录确认这61张图片均可解码；它们与原图库的3,368个目标使用不同路径，不能计入原图库恢复数。

## 按类别统计

“原图 / 缩略图已取得”按原页面脚本生成的精确路径统计。

| 类别 | 图库数 | 应有原图 | 应有缩略图 | 原图 / 缩略图已取得 |
|---|---:|---:|---:|---:|
| Raid | 9 | 332 | 332 | 0 / 0 |
| Dungeon | 15 | 537 | 537 | 0 / 0 |
| PvP | 4 | 175 | 175 | 0 / 0 |
| Region | 1 | 49 | 49 | 0 / 0 |
| Mount | 7 | 83 | 83 | 0 / 0 |
| Flying Mount | 4 | 64 | 64 | 0 / 0 |
| Profession | 1 | 66 | 66 | 0 / 0 |
| Event | 6 | 242 | 242 | 0 / 0 |
| TCG Gallery | 1 | 47 | 47 | 0 / 0 |
| TCG Mount | 1 | 47 | 47 | 0 / 0 |
| TCG Picnic Basket | 1 | 42 | 42 | 0 / 0 |
| **合计** | **50** | **1,684** | **1,684** | **0 / 0** |

## Wayback 的调查覆盖

| 时间范围 | 已覆盖 | 结果与剩余工作 |
|---|---:|---|
| 2000-01-01 至重建基准 2008-05-12 21:00:44 UTC | 50组 | 现有已验收的目录索引窗口未找到原图库图片；部分目录有另一路径的指南预览。 |
| 基准之后至 2010-12-07 | 21组 | 索引窗口已覆盖，未找到原图库图片。其余29组中，Mechanar 遇503停止，28组尚未覆盖。 |
| 2010-12-08 至本次核查 | 0组完成全窗口调查 | 仍保留为未覆盖。Karazhan 的少数2013重定向记录不等于这一整个窗口已查完。 |

本轮重新检查了已保存的索引正文：20个成功的 CDX 响应共1,304行，没有命中3,368个精确目标；另一个 Mechanar 响应是503错误页，不能当成空索引。Zul’Aman 的较早验收记录另行沿用。索引查询的原始主机、目录前缀、时间窗和回执保留在下方资料中。

实际逐图回放与目录索引分开统计。现有可核对记录包含116个不同原图库目标的实际回放：Karazhan 114次404及1次已观察重定向，Magister’s Terrace 1次404，均未取得 JPEG。Karazhan 另11个目标只有重定向索引记录；不能写成12次都已实际访问重定向。这里的404是 Wayback 回放所返回的未存档页面，不能据此断言2008年原服务器也返回404。其他目标不因目录索引为空而自动记成逐图404。

北京时间22:20进行了新的两请求连接控制：直连超时（curl 28，无响应正文），进程内代理返回429，随即停止。未绕过限流，也未对50组发起新的逐图请求。**目前可以确认本地缺失范围；尚不能认定这些图片在 Wayback 的所有年份都不存在。**

## 全部50组清单

每组应有同样数量的原图和缩略图；表中取得数均为原图 / 缩略图。基准之前的索引覆盖见上表；所有组的2010-12-08以后仍待补查。

| # | 图库 | 声明截图数 | 已取得原图 / 缩略图 | 另外保存的指南图片 | 基准后至2010-12-07 |
|---:|---|---:|---:|---|---|
| 1 | [Karazhan](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/karazhan-gallery.html) | 63 | 0 / 0 | — | 已查，未见原图库索引 |
| 2 | [Zul'Aman](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/zulaman-gallery.html) | 60 | 0 / 0 | 预览 3 | 已查，未见原图库索引 |
| 3 | [Magtheridon's Lair](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/mag-gallery.html) | 15 | 0 / 0 | — | 已查，未见原图库索引 |
| 4 | [Gruul's Lair](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/gruul-gallery.html) | 21 | 0 / 0 | — | 已查，未见原图库索引 |
| 5 | [Serpentshrine Cavern](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/serpentshrine-gallery.html) | 29 | 0 / 0 | — | 已查，未见原图库索引 |
| 6 | [The Battle for Mount Hyjal - Caverns of Time](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/cot-hyjal-gallery.html) | 44 | 0 / 0 | — | 已查，未见原图库索引 |
| 7 | [Tempest Keep - The Eye](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/tk-the-eye-gallery.html) | 43 | 0 / 0 | — | 已查，未见原图库索引 |
| 8 | [Black Temple](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/black-temple-gallery.html) | 48 | 0 / 0 | — | 已查，未见原图库索引 |
| 9 | [Doom Lord Kazzak](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/doom-lord-kazzak-gallery.html) | 9 | 0 / 0 | — | 已查，未见原图库索引 |
| 10 | [Magister's Terrace](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/magisters-terrace-gallery.html) | 47 | 0 / 0 | — | 已查，未见原图库索引 |
| 11 | [Hellfire Citadel - Hellfire Ramparts](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/hc-hellfire-ramparts-gallery.html) | 32 | 0 / 0 | — | 已查，未见原图库索引 |
| 12 | [Hellfire Citadel - The Blood Furnace](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/hc-blood-furnace-gallery.html) | 39 | 0 / 0 | — | 已查，未见原图库索引 |
| 13 | [Hellfire Citadel - The Shattered Halls](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/hc-shatteredhalls-gallery.html) | 50 | 0 / 0 | — | 已查，未见原图库索引 |
| 14 | [Coilfang Reservoir - The Underbog](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/cr-underbog-gallery.html) | 40 | 0 / 0 | — | 已查，未见原图库索引 |
| 15 | [Caverns of Time - Escape from Durnholde](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/cot-escape-gallery.html) | 38 | 0 / 0 | — | 已查，未见原图库索引 |
| 16 | [Caverns of Time - Opening of the Dark Portal](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/cot-opening-gallery.html) | 30 | 0 / 0 | — | 已查，未见原图库索引 |
| 17 | [Coilfang Reservoir - The Steam Vaults](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/cr-steamvaults-gallery.html) | 30 | 0 / 0 | — | 已查，未见原图库索引 |
| 18 | [Auchindoun - Mana-Tombs](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/auc-mana-tombs-gallery.html) | 30 | 0 / 0 | — | 已查，未见原图库索引 |
| 19 | [Auchindoun - Auchenai Crypts](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/auc-crypts-gallery.html) | 37 | 0 / 0 | — | 已查，未见原图库索引 |
| 20 | [Auchindoun - Sethekk Halls](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/auc-sethek-halls-gallery.html) | 38 | 0 / 0 | — | 已查，未见原图库索引 |
| 21 | [Auchindoun - Shadow Labyrinth](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/auc-shadow-lab-gallery.html) | 23 | 0 / 0 | — | 已查，未见原图库索引 |
| 22 | [Tempest Keep - The Mechanar](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/tk-mech-gallery.html) | 35 | 0 / 0 | — | 503，中断 |
| 23 | [Tempest Keep - The Botanica](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/tk-botanica-gallery.html) | 19 | 0 / 0 | — | 未覆盖 |
| 24 | [Tempest Keep - The Arcatraz](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/dungeons/tk-arcatraz-gallery.html) | 49 | 0 / 0 | — | 未覆盖 |
| 25 | [Warsong Gulch](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/pvp/battlegrounds/warsong-gulch-gallery.html) | 29 | 0 / 0 | — | 未覆盖 |
| 26 | [Isle of Quel'Danas](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/regions/isle-of-queldanas-gallery.html) | 49 | 0 / 0 | — | 未覆盖 |
| 27 | [Amani War Bear](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/bear-gallery.html) | 24 | 0 / 0 | — | 未覆盖 |
| 28 | [Riding Turtle](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/turtle-gallery.html) | 12 | 0 / 0 | — | 未覆盖 |
| 29 | [Swift White Hawkstrider](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/swiftwhitehawkstrider-gallery.html) | 15 | 0 / 0 | — | 未覆盖 |
| 30 | [Qiraji battle tank](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/aq-battletank-gallery.html) | 4 | 0 / 0 | — | 未覆盖 |
| 31 | [Raven Mount](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/raven-mount-gallery.html) | 9 | 0 / 0 | — | 未覆盖 |
| 32 | [Black War Elekk](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/black-war-elekk-gallery.html) | 6 | 0 / 0 | — | 未覆盖 |
| 33 | [Fiery Warhorse](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/fiery-warhorse-gallery.html) | 13 | 0 / 0 | — | 未覆盖 |
| 34 | [Cenarion War Mount](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/cenarion-gallery.html) | 13 | 0 / 0 | — | 未覆盖 |
| 35 | [Flying Machine](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/flyingmachine-gallery.html) | 22 | 0 / 0 | — | 未覆盖 |
| 36 | [Phoenix](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/phoenix-gallery.html) | 15 | 0 / 0 | — | 未覆盖 |
| 37 | [X-51 Nether-Rocket](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/rocket-mount-gallery.html) | 14 | 0 / 0 | — | 未覆盖 |
| 38 | [Fishing](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/professions/fishing-gallery.html) | 66 | 0 / 0 | 预览 4 | 未覆盖 |
| 39 | [Lunar Festival](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/events/lunarnewyears/gallery.html) | 35 | 0 / 0 | 指南大图 11 | 未覆盖 |
| 40 | [Love is in the Air](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/events/loveisintheair/gallery.html) | 34 | 0 / 0 | 指南大图 12 | 未覆盖 |
| 41 | [Hallow's End](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/events/hallowsend/gallery.html) | 65 | 0 / 0 | 预览 4 | 未覆盖 |
| 42 | [Brewfest](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/events/brewfest/gallery.html) | 51 | 0 / 0 | 预览 4 | 未覆盖 |
| 43 | [Winter's Veil](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/events/winterveil/gallery.html) | 37 | 0 / 0 | 预览 4 | 未覆盖 |
| 44 | [Darkmoon Faire: Level 70 Elite Tauren Chieftain](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/events/darkmoon/gallery.html) | 20 | 0 / 0 | — | 未覆盖 |
| 45 | [TCG Gallery](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/items/tcg-gallery.html) | 47 | 0 / 0 | — | 未覆盖 |
| 46 | [TCG Spectral Tiger](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/basics/mounts/spectral-gallery.html) | 47 | 0 / 0 | — | 未覆盖 |
| 47 | [TCG Picnic Basket](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/items/tcg-picnic-gallery.html) | 42 | 0 / 0 | — | 未覆盖 |
| 48 | [City Attacks](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/pvp/worldpvp/cityattacks-gallery.html) | 102 | 0 / 0 | 预览 3 | 未覆盖 |
| 49 | [Halaa PvP](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/pvp/worldpvp/halaa-gallery.html) | 14 | 0 / 0 | — | 未覆盖 |
| 50 | [World PvP](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/pvp/worldpvp/worldpvp-gallery.html) | 30 | 0 / 0 | 指南大图 16 | 未覆盖 |

## 为什么页面有、图片却没有

原图库通过 `numShots`、`addshots()` 和 `shotList` 在 JavaScript 中生成 `ss1.jpg`、`ss1-thumb.jpg` 等路径，并非在 HTML 中逐张列出图片。当前浏览版已修复部署目录前缀；运行时生成的1,684个原图路径与来源脚本一致，文件仍未取得。

较合理的工作假设是：当年的抓取保存了页面和静态引用的指南预览，却没有发现或取得动态生成的全部图片。Internet Archive 的[使用说明](https://archivesupport.zendesk.com/hc/en-us/articles/360004651732-Using-The-Wayback-Machine)也说明，JavaScript 生成且未在原始 HTML 中写明的链接可能难以归档；缺图常与图片未被保存有关。这个机制能解释现有文件分布，但现有证据还不能确定当年每次抓取失败的具体原因。

CDX 是捕获索引，不是图片文件。查询结果的范围与是否分页需要按[官方 CDX 文档](https://github.com/internetarchive/wayback/blob/master/wayback-cdx-server/README.md)解释；索引空、网络失败、回放404和有效 JPEG 在本清单中分别记录。

## 后续查询顺序

1. 网络恢复后，先补29组尚未覆盖的2008–2010窗口；Mechanar 从失败处续接。
2. 再调查2010-12-08以后的捕获、来源页面给出的别名及关联图片路径；只对新线索取回正文并验证图片。
3. Karazhan、Black Temple 在已查时间窗内继续暂缓重复请求；出现新捕获、镜像或关联页线索后再启动。没有把这一暂缓规则扩大成“其它48组已经完整”。

MEDIA → Screenshots、Screenshot of the Day 和资料片截图是另一些图片集合，不包含在本报告的50组和1,684张中。它们已有部分素材，但不能用来补算这50个玩家图库的恢复率。

## 可复核资料

- [50组汇总 CSV](../research/player-gallery-accessibility-20261020/root/gallery-scope-50.csv)：本地缺失、指南图片和时间窗状态。
- [3,368个精确图片目标 CSV](../research/player-gallery-accessibility-20261020/local/gallery-targets-3368.csv)：每个地址在原始层、Source15及v39的存在情况。
- [50组来源与文件审计](../research/player-gallery-accessibility-20261020/local/gallery-accessibility-50.json)与[历史可及性总表](../research/player-gallery-accessibility-20261020/history/gallery-availability-table.json)。
- [浏览检查说明](../research/player-gallery-accessibility-20261020/local/browser/browser-audit-report.md)与[浏览汇总](../research/player-gallery-accessibility-20261020/local/browser/browser-audit-summary.json)。
- [来源独立核对](../research/player-gallery-accessibility-20261020/root/local-source-acceptance.json)、[索引与浏览核对](../research/player-gallery-accessibility-20261020/root/history-browser-acceptance.json)、[本轮连接核对](../research/player-gallery-accessibility-20261020/root/network-source-acceptance.json)。

本次新增调查文档与清单，未重新导出网站或离线包；在线版及离线包继续使用 v39。
