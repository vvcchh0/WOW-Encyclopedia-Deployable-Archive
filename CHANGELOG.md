# 更新记录

按工作日期记录已完成的改动与已发现的问题。获取和校验细节见[工程文档](docs/README.md)。

## 2026-10-25

- 发布v68.1网页：111个补充奖励图标、服装赛获奖阅读页及旧PvP导航／悬浮说明修复上线。168个变更对象逐项核对通过；补充历史`.shtml`入口的静态跳转，两个补丁对象和真实浏览跳转核对通过。完整离线包保留v61。[线上验收](docs/evidence/v68-1-online-acceptance-20261025.json)

- 完成v68本地验收：补入111个奖励图标显示，累计114个素材；恢复2006年服装赛获奖正文的静态阅读页，照片仍待补。修复首次悬浮说明和两张旧PvP奖励页的导航，22个奖励页面与手机阅读布局检查通过。[来源与范围](docs/faction-reward-art-20261025.md)
- 核对ArchiveCraft百科的十个页面和五张图片，五图均与已有官方素材原字节一致；十二张数字分类头像仍未取得新来源。[对照记录](docs/archivecraft-encyclopedia-crosscheck-20261025.md)

- 完成本地v62验收：为萨满“Improved Fire Nova Totem”补入一张关联图标及灰度状态，累计覆盖66项天赋。13项测试、24项Chrome检查和10,336个文件回读通过；线上与最新完整包暂为v61。[对应依据](docs/shaman-talent-art-20261025.md)、[本地验收](docs/evidence/v62-local-acceptance-20261025.json)
- 从Common Crawl保存官方万圣节服装赛获奖页的2008-08-29记录，取得五张赢家截图的路径；该集合现存索引未包含图片，尚未恢复新闻配图。[本轮恢复总账](docs/continuous-recovery-20261025.md)
- 整理 GitHub 发布：保留 v24、v38、v52、v61 四个阶段包，中间版本转为[历史说明](docs/release-history.md)，原附件已核验并留存本地，Git 标签保留。
- 部署记录保留当前版与最近两个检查点，历史工作流与 Git 提交继续可查；在线版及最新离线包保持 v61。
- 更新[发布策略](docs/publication-policy.md)：网页随修复更新，完整离线包在取得阶段成果后发布。[本次整理记录](docs/github-publication-cleanup-20261025.md)

## 2026-10-24

- 发布v61网页：补入58张TBC关联图标，覆盖65项天赋；接入BlizzCast前两期现存媒体副本与本地播放器，保留访谈和时间码。138个线上文件与两个线上播放器检查通过；同步发布[v61离线包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/tag/archive-20080512-browser-20261024-v61)（约630MB）。[图标来源](docs/tbc-talent-art-20261024.md)、[音频说明](docs/blizzcast-audio-20261024.md)
- 发布v59网页与[离线包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/blob/main/docs/release-history/archive-20080512-browser-20261024-v59.md)：恢复五条2006年TCG壁纸公告的预览，接入三组时光之穴图库的八张法语指南缩略图，注明Coolwow2来源；原玩家图库缺图继续保留。线上17个变更文件与离线启动检查通过。[修复与来源说明](docs/news-and-related-gallery-previews-20261024.md)
- 逐项核对331个已选非图库原文件缺口，另核对十二张百科分类头像对45个子页的引用关系。直连TCP连接失败，代理Wayback仍返回429，继续查找其他来源。[本轮记录](docs/continuous-recovery-20261024.md)

## 2026-10-23

- 发布v57网页及[离线包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/blob/main/docs/release-history/archive-20080512-browser-20261023-v57.md)，修复情人节指南页面12处截图显示与原图链接，复用已保存原图；独立图库的34张投稿截图仍待补齐。浏览、线上文件及包内启动检查通过。[修复说明](docs/love-guide-preview-repair-20261023.md)
- 将57份历史Pages导出（513,856个文件、33.45 GB逻辑内容）整理为60文件共享归档；13,234个唯一对象实读核验通过，三个版本实际恢复并独立验收。删除55棵旧展开目录和三份临时恢复副本，保留v55/v56、原始来源及完整历史ZIP；按文件AllocationSize核账净节省约32.05 GB。去重保持历史版本内容不变。[去重记录与整理后验收摘要](docs/historical-export-deduplication.md)
- 09:00 UTC的Wayback控制请求直连超时，进程内代理返回429，没有取得新图片；该次连接结果不作为资源缺失结论。[本轮持续恢复记录](docs/continuous-recovery-20261023.md)
- 核对四份关联地下城源页，记录八个欧服缩略图路径及其图库链接；图片尚未获取，既有50组图库的缺失计数保持不变。12:30 UTC再次检查Wayback，代理仍返回429，本轮停止后续获取。[来源调查](docs/related-source-leads-20261023.md)

## 待完成

- 按分区寻找并恢复玩家截图图库的原图与缩略图。
- 继续补齐其他缺图与静态资源。

## 2026-10-22

- 发布 v56 网页与离线包，再补入九个同名天赋的18张明暗图标；本轮累计补入60个关联来源图片文件。原有天赋文字、数值和加点规则保留，线上22个变更文件与包内启动核对通过。[本轮回顾](docs/recovery-summary-20261022.md)
- v55网页与离线包发布：补入18张天赋连线箭头、3张声望奖励图标及20张改名／移树天赋图标，附关联来源说明；保留原天赋规则和文字。
- 复核Deadmines九张早期原图与十张预览，确认本地和线上均可访问；地下城正文已有，不重复收录。

- 发布v53：补入职业专题的Profession Updates标题图，注明ArchiveCraft来源；六个线上变更文件核对通过。继续核对天赋连线箭头和声望奖励图标。[工作记录](docs/continuous-recovery-20261022.md)
- 完成地下城来源对照：Deadmines九张早期截图及预览已在v52保存并可线上浏览；19个经典副本主题和五个Outland区域组均有本地正文。整理[入口、图注对应与来源追溯](docs/dungeon-source-tracing-20261022.md)，继续调查Four Dragons等实际缺图。

## 2026-10-21

- 同步发布[v52 离线浏览包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/tag/archive-20080512-browser-20261021-v52)（约 546 MB，解压约 634 MB），完成本轮非图库复原。内容、来源方法和剩余缺口见[本轮回顾](docs/recovery-summary-20261021.md)。

- 发布 v52：修复 Arathi 指南的动态目录，恢复 20 张已有预览的显示，25 个线上对象核对通过；两张缩略图仍缺。修正分轮清单为 391 个本地资源目标。[复原记录](docs/non-gallery-restoration-20261021.md)

- 发布 v51：恢复奥尔多／占星者说明弹窗与派系切换，接通四页 Wrath 字母图；80 个线上对象核对通过，离线包完成本地启动检查。整理 177 个页面路径的分轮浏览记录与剩余素材清单。[复原记录](docs/non-gallery-restoration-20261021.md)

- 完成本地 v50：用已保存的原文恢复奥尔多／占星者介绍弹窗与派系切换，已合入 v51。[复原记录](docs/non-gallery-restoration-20261021.md)

- 发布 v49：补入三幅百科人物／组织配图及 The Broken 指南缩略图，页面注明 ArchiveCraft 来源；修复奥尔多／占星者奖励按钮的图片路径，74个线上对象核对通过。[复原记录](docs/non-gallery-restoration-20261021.md)

- 发布 v46：补齐天赋状态边框、重置与打印按钮，恢复点数框布局；九职业实际操作检查通过，剩余 259 个缺图目标。[复原记录](docs/non-gallery-restoration-20261021.md)
- 发布 v45：新增七份早期专题正文及内容目录更新，接通旧地址；天赋页加入 986 张标明后期关联来源的图标，Tinfoil Hat 提示框和 Molten Core 返回箭头恢复显示。专题插图及部分天赋素材仍缺。[复原记录](docs/non-gallery-restoration-20261021.md)
- 发布 v41：恢复宝石插槽火花、男性矮人舞蹈与海象人模型三处 Flash 展示，修复下载页悬停错误和共享菜单标签。其他舞蹈模型仍待取得。[兼容范围](docs/flash-compatibility-20261021.md)
- 发布 v42：修复九职业天赋计算器的共享脚本，恢复加点、重置及非零模板保存和重载；新增 BlizzCast 前两期访谈、节目目录等五个阅读页，接通下载页和旧新闻中的入口。[复原记录](docs/non-gallery-restoration-20261021.md)
- 逐职业盘点天赋计算器的图标、背景和布局缺口，共 1,259 个本地缺失目标。BlizzCast 图片与音频仍待取得；继续调查其他来源。[本轮记录](docs/continuous-recovery-20261021.md)

## 2026-10-20

- 全面复核 50 个玩家图库：1,684 张截图的原图和缩略图均未取得；另有 22 张指南预览与 39 张指南大图。完成全部页面浏览检查，整理逐组缺失和存档时间窗，纠正“仅 Karazhan、Black Temple 缺图”的理解。[调查报告](docs/player-gallery-accessibility-20261020.md)
- 发布 v39：补回 2004 年商店公告与 2005 年祖尔格拉布影片公告的两处配图，商店促销条目改为静态历史展品。同步发布[v39 离线包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/blob/main/docs/release-history/archive-20080512-browser-20261020-v39.md)（约 534 MB，解压约 600 MB）。
- 扩大本地索引与图片摘要调查，核对新闻缺图和待查图库目录；Common Crawl 取得一份 2008 年 7 月百科首页，未发现新增图片线索。Wayback 429 与 Common Crawl 504 限制进一步获取，玩家图库原图仍有缺口。[工作记录](docs/continuous-recovery-20261020.md)

## 2026-10-19

- 发布 v38：本轮累计补回九十六个图片资源，修复排行榜脚本和日期切换，旧信用卡宣传页改为历史展品。历史排行榜数据仍未取得，页面已明确说明；同步发布[v38 离线包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/tag/archive-20080512-browser-20261019-v38)（约 534 MB，解压约 600 MB）。
- 发布 [v33 离线包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/blob/main/docs/release-history/archive-20080512-browser-20261019.md)（约 533 MB，解压约 598 MB），保留对应版本供本地浏览。继续复核旧页面交互，并整理玩家图库的调查结论与剩余线索。[工作记录](docs/continuous-recovery-20261019.md)
- 补完 v33 剩余 76 个图片入口与展示目标的浏览检查，包括 Dragon Hunt 展开和新闻内图片；比赛结果页的旧菜单错误另行修复。
- 完成 Karazhan、Black Temple 的晚期存档缺口调查，未发现原玩家截图的新来源，暂缓这两组图库的重复查询。有新捕获或关联页线索时继续恢复。
- 发布 v35：补回二十四张旧新闻配图，修复比赛结果页的菜单跳转。新增图片的浏览检查和三十个线上变化文件核对通过；该阶段离线包为 v33，后续素材现已整合至上方 v38。

## 2026-10-18

- 发布 v33：新增 120 个图片资源地址，补回文章原图、旧新闻大图、壁纸与专业素材；本轮累计新增 376 项。153 个线上文件核对通过。部分旧页面的隐藏链接与交互继续复核，公开离线包仍为 v24。[工作记录](docs/continuous-recovery-20261018.md)

- 发布 v32：新增一百三十六个图片资源，补回旧新闻与指南插画，恢复副本进度图的路径交互、专业配方图标和原画放大查看。玩家图库原图继续查找。[线上核对](research/continuous-recovery-20261018/publication/root-v32-pages-online-acceptance.json)
- 发布 v29：补回四十张新闻配图，保留 2007 年订阅人数公告的原有鼠标悬停图注。玩家图库原图继续查找。[工作记录](docs/continuous-recovery-20261018.md)
- 发布 v28：再补回六十七张新闻配图与相关素材，将 2007 年旧账号升级公告改为历史展品。
- 发布 v26：补回八张新闻配图与五张指南相关图片，情人节、春节及 World PvP 指南大图增至三十九张。

## 2026-10-16

- 发布 v25，补回情人节两张大图、World PvP 一张大图及春节的一张服装视图；三组指南大图增至三十五张。原有九个邻接素材缺口剩五个，离线包保持 v24。[限时修复记录](docs/focused-recovery-20261016-2301.md)

- 发布 v24，再补回十七个新闻图片资源，在线版与[新版离线包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/tag/archive-20080512-browser-20261016)同步（约 510 MB，解压约 575 MB）。本轮累计补回 141 个图片资源地址，图库与其他缺图的后续清单已保留。[本轮回顾](docs/recovery-summary-20261016.md) · [线上核对](research/continuous-recovery-20261016/publication/root-v24-pages-online-acceptance.json)

- 发布 v23，补回四十张指南相关素材；情人节、春节和 World PvP 新增三十二张可打开原尺寸的指南图片，原玩家图库继续查找。[线上核对](research/continuous-recovery-20261016/publication/root-v23-pages-online-acceptance.json)

- 发布 v22，补齐八月新闻的全部二十七张配图，并新增十张其他新闻配图和六张页面素材。相同四十页新闻减少十六处缺图引用。[线上核对](research/continuous-recovery-20261016/publication/root-v22-pages-online-acceptance.json)

- 发布 v20，补回二十四张 2007 年 8 月新闻配图；剩余图片继续寻找。[线上核对](research/continuous-recovery-20261016/publication/root-v20-pages-online-acceptance.json)

- 发布 v19，补回十张共享新闻图片，修复 184 处缺图引用。[线上核对](research/continuous-recovery-20261016/publication/root-v19-pages-online-acceptance.json)

- 发布 v18，在 City Attacks 中加入三张已有指南预览，六个图库共展示二十二张；完整截图继续查找。[线上核对](research/continuous-recovery-20261016/publication/root-v18-pages-online-acceptance.json)
- 发布 v17，补回二十张新闻图片，修复 156 处缺图引用；五个玩家图库新增十九张原指南预览，完整截图继续查找。线上 63 项文件核对通过，离线包暂为 v14。[线上核对](research/continuous-recovery-20261016/publication/root-v17-pages-online-acceptance.json)
- 发布 v16，补回九张历史新闻配图和两张欧服每日截图；线上 19 项文件核对通过。新闻及图库仍有缺图，离线包暂为 v14。[线上核对](research/continuous-recovery-20261016/publication/root-v16-pages-online-acceptance.json)
- 发布 v15，补回 2007 年 8 月的 50 条新闻；现有侧栏的历史内容入口已接通，图库与新闻配图继续补齐。离线包暂为 v14。[线上核对](research/continuous-recovery-20261016/publication/root-pages-online-acceptance.json)
- 启动本轮持续恢复，核对玩家图库未完成项，并调查欧服缩略图与新闻配图的可用存档。[工作记录](docs/continuous-recovery-20261016.md)

## 2026-10-15

- 夜间专项取回 2007 年 8 月的 50 条新闻并完成本地 v15 浏览验收，另保存两张欧服每日截图原图；Karazhan 六项图片检查仍未取得素材。线上及离线包暂保持 v14。[专项记录](docs/focused-recovery-20261015-2303.md)

- 发布 [2026-10-15 浏览版离线包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/blob/main/docs/release-history/archive-20080512-browser-20261015.md)（约 503 MB，解压约 566 MB），包含当前页面与素材；更新 README 的使用入口，并保留旧版供历史对照。

- 发布 v14，新增九页、350 条历史新闻；侧栏仅余 2007 年 8 月新闻待取得，图片缺口继续保留。[线上验收](research/v14-integration/root-pages-online-acceptance.json)

- 发布 v13，补回 2006 年 9 月、2007 年 12 月和 2008 年 5 月旧新闻，侧栏剩余 10 个缺失地址；修复新闻加号点击和回车展开。5 月页保留原存档截至 5 月 8 日的内容。[线上验收](research/v13-integration/root-pages-online-acceptance.json)

- 发布 v12，恢复 2007 年 4、6、7 月旧新闻及相关回链；侧栏剩余 13 个缺失地址，新增页面可展开浏览。[线上验收](research/v12-integration/root-pages-online-acceptance.json)

- 发布 v11，补回 BlizzCast 与 2008 年竞技场新闻的两张配图，以及旧新闻共享样式；实际展开文章后确认图片正常显示。[线上验收](research/v11-integration/root-pages-online-acceptance.json)
- 取回 2007 年 4、6、7 月旧新闻，准备接入下一版；检查三个副本图库目录的基准前存档，尚未找到图片捕获。[持续恢复记录](docs/continuous-recovery-20261015.md)

- 发布 v10 浏览镜像，接通旧新闻、BC 专业、PTR 历史展品及原画目录等 19 个原缺失入口，修复原画查看器和卡片点击。侧栏剩余 16 个缺失地址，原画仍缺八组图片。[发布验收](research/v10-integration/root-pages-online-acceptance.json)
- 复查本地 v9 的全部侧栏入口，缺路由地址由 35 个减至 23 个；新补的新闻、BC、PTR 和 Battlegroups 入口可浏览。原画目录仍缺八组图片及共享边框；查看器 HTML 已取回，正在补齐并修复其依赖。线上仍为 v8。[侧栏与浏览复核](docs/continuous-recovery-20261015.md)
- 新增 PTR 历史展品，保留捕获日期及相关档案链接；浏览版横幅注明以 2008-05-12 为重建基准。[本地镜像验收](research/continuous-recovery-20261015/root-v9-export-acceptance.json)
- 补回 BC 专业介绍、WLK 原画入口及另外两页旧新闻，更新五个新闻月页的来源；取得两份原画计数脚本和九张竞技场、欧服页面素材，已纳入本地 v9 镜像，等待浏览验收。根据历史重定向确认 Battlegroups 旧入口可映射至已有页面。[持续恢复总账](docs/continuous-recovery-20261015.md)
- 本地取回 2004 年旧新闻、2005 年 7–11 月新闻共六页及一页 PTR 资料，核对正文与实际捕获日期后准备接入镜像；修正索引候选筛选对 HTTP 默认端口 `:80` 的处理，继续检查其余捕获。[持续恢复总账](docs/continuous-recovery-20261015.md)
- 完成 1,241 条菜单观察的本地审计，确认 35 个不同内容地址缺少路由，主要涉及旧新闻与 RSS；启动原始实体及别名核对。冷却后的 JPEG 控制测试通过，代理可取得有效图片，直连仍超时。[持续恢复总账](docs/continuous-recovery-20261015.md)
- 将九个本地提交推送至 GitHub，并发布新版 Pages；12 个线上对象与本地一致。启动按侧栏逐项检查的持续恢复，旧菜单中 579 条未分组观察重新纳入审计。[发布与后续安排](docs/github-sync-20261015.md)
- Karazhan 新一批检查确认 14 个未存档资源，累计 73/126 个目标已取得内容判定，53 个仍受连接故障影响；本轮未取得新图片。[持续恢复总账](docs/continuous-recovery-20261015.md)
- 本地补回 MEDIA Screenshot of the Day 的两张原图，修复历史日期计算、缩略显示与 Community 菜单分组，并恢复 Archived News 的五处旧地址跳转。[截图与导航恢复](docs/media-and-navigation-recovery-20261015.md)
- 调查 MEDIA 入口及图片目录的存档点；大部分截图及原始缩略图仍待恢复。
- 本地恢复 2008 年试用选择页和 2007 年 PvP Mini Site，试用页以静态历史展品呈现，PvP 页恢复本地导航并展示 Flash 缺口；修复 WLK 壁纸菜单路由，确认已有 28 张壁纸原图及配套素材。
- 由 Luna 完成四轮 TLS 对照探测：代理控制图均可获取，直连两次在 TCP 阶段超时；修复下载工具对代理响应和实际捕获时间的判定。

- 复查 Karazhan 全部 126 个图片地址：59 项返回未存档、67 项 TLS 失败，未取得有效图片。对照确认连接故障具有间歇性；指定解析地址、切换 TLS 客户端和 TLS 1.2 均未恢复后续握手。[复查与诊断](docs/karazhan-tls-recheck-20261015.md)

## 2026-10-14

- 限时检查 Karazhan 玩家图库：覆盖 54/126 个图片地址，32 项返回未存档、8 项仅取得历史重定向，未取得有效图片；代理连续 TLS 错误后停止，72 项待检查。[检查记录](docs/karazhan-gallery-accessibility-20261014.md)

- 抽样检查 Wayback 截图资源：3 张已有图片可回放，2 张图库原图返回 404；本轮未遇到 429，CDX 超时、Availability API 返回 503，暂无新增图片。[可及性报告](docs/screenshot-accessibility-20261014.md)

- 本地修复旧百科 XML 地址跳转及含空格的动态图片地址，停用 7 处旧 Flash 安装属性；整理静态缺口与空间清单，生成含历史展品改造的新版便携浏览包。[本地整理记录](docs/local-maintenance-20261014.md)

- 发布历史展品改造、36 张此前验收的补充图片及素材目录、50 个图库目录修复；32 项单元测试、29 项展品检查与 39 项原功能检查通过，18 个线上对象与本地一致。[发布验收](docs/historical-exhibits-20261014.md#线上发布)

- 将奖励和两个旧登录入口改为独立历史展品；报名、兑换、投稿、软件下载及账号菜单使用历史语境。[改造记录](docs/historical-exhibits-20261014.md)
- 继续资源连接诊断，尝试进程内 HTTPS DNS 与指定地址直连；仍受连接重置和代理回放 429 影响，本轮无新增图片。[网络诊断](docs/network-recovery-20261014.md)
- direct 优先续传 18 个图片实体，直连超时、代理主要返回 HTTP 429，本批无新增；停止请求并修正下载器停批和验收逻辑，10 项离线模拟测试通过。[批次记录](docs/related-sites-recovery-20261014.md#网络恢复后的-direct-优先批次)
- 取得 Search Console 正式问题类别“欺骗性网页”（1 项，示例网址不适用），启动归档站敏感业务入口专项分析。
- 按新空间约定取消固定 14GB 工作区上限，保留 D 盘至少 10GB 安全空间；旧派生副本未清理。
- 创建根站点并发布 Search Console HTML 验证文件，公网核对通过；之后用户提供了根属性的安全问题报告。[所有权文件发布](docs/search-console-review-20261014.md#根站点所有权文件发布2026-10-14)
- 取得欧服官网 2 份历史页面和 14 张图片，接入独立本地素材目录，并整合此前的 3 张 Karazhan 预览图。[关联站点恢复](docs/related-sites-recovery-20261014.md)
- 修复跨域同路径误配；核对旧新闻队列中的重复文件，增加请求前的当前镜像过滤。
- 本地接入 19 张布局图片，恢复 67 处图片和 CSS 背景引用；修正全部 50 个玩家截图图库的目录拼接。[本地补充记录](docs/resource-recovery-20261014.md)
- 查询 Karazhan 和 Fishing 的相关索引，单独保存 3 张晚期预览图；图库原图与配套缩略图仍待获取。该批最初只作本地保存，随后纳入上方发布。
- 修复 WLK 截图分页对网址参数的执行，保留正常分页。
- 历史登录、报名、投稿、兑换与反馈表单改为静态展示，保留搜索、奖励筛选和任务切换。
- 补回 iframe 备用内容的离线地址转换，并完成浏览器回归验收。[修复记录](docs/browser-security-remediation-20261014.md)
- 整理 Search Console 验证和复核材料；后续取得根属性的“欺骗性网页”报告，报告未提供示例网址。[复核准备](docs/search-console-review-20261014.md)
- 约定后续 Wayback 获取先走 direct，直连失败后再走代理路径，并在批次记录中保留传输路径与失败原因。

## 2026-10-13

- 公开 GitHub 仓库，发布约 502 MB 的离线包。
- 上线 [GitHub Pages](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/)，适配旧页面地址、菜单和百科搜索。
- 续传取得 19 张 2008 年图片，暂存于本地，等待整合。[批次记录](docs/resource-resume-20261013.md)
- 盘点 50 个玩家截图图库：当前页面声明 1,684 张截图，原图与配套缩略图尚待获取；同时发现图库目录在静态导出时被误改写。[图库盘点](research/github-pages-20261013/gallery-inspection-20261013.md)
- 精简 README，增加协作入口，将工程说明归入专门文档，并补全参考资料来源。

## 2026-10-12

- 扩展官网镜像至 917 个页面文档，连同静态资源共 8,304 个文件。
- 完成一批 407 个图片 URL 的恢复与镜像整合，生成离线恢复包。[恢复记录](docs/resource-recovery-2008.md)

## 2026-10-11

- 保存百科首页与全部 51 个词条及其依赖，提供首版本地浏览服务。
- 复核早期缺口，整理为 13 项错误响应与 4 项晚期有效补充。[缺口复核](docs/gap-review-20261011.md)
- 沿百科页面与官网导航扩展内容获取。[离线重建](docs/offline-reconstruction-2008.md)

## 2026-10-10

- 对照 2010 与 2008 回放，确认 2010 候选存在 XML 解析错误。
- 确定用户提供的 **2008-05-12 21:00:44 UTC** 快照为重建基准，保存样本与依赖结构。[基准复核](docs/reassessment-2008.md)
