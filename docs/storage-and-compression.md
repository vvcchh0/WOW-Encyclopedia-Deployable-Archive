# 空间与压缩策略（2026-10-13）

2026-10-25 更新：GitHub Release 已整理为四个阶段包，附件由约7.03GB减至2.22GB；本地历史ZIP保留。后续完整包按阶段成果发布，见[发布策略](publication-policy.md)和[整理记录](github-publication-cleanup-20261025.md)。下文中的旧Release链接现指向对应历史说明。

2026-10-14 更新：用户取消了工作区固定 14GB 上限，改为 D 盘保留至少 10GB 安全空间。当前 Pages 导出与 direct 优先下载工具默认不限制工作区总量，仍预检预计新增量及磁盘余量；可按需显式设置总量上限。下文测量和早期预算按当时记录保留。

基准、原始响应和派生文件的 SHA 保持不变。采用无损压缩与分层交付，不重新编码历史图片，不把压缩率当成资源完整性的证明。

## 实测

`offline/site/` 共 8,304 文件、539,027,834 字节，冻结清单 SHA-256 为 `397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459`。对全部部署文件只读测量：

| 范围 | 原字节 | gzip-9 字节 | 可省字节 |
|---|---:|---:|---:|
| HTML/XML/JS/CSS/JSON 文本 | 46,828,944 | 8,056,509 | 38,772,435 |
| 7,123 个图片文件 | 490,291,407 | 486,122,052 | 4,169,355 |

图片占部署文件字节约 91%。179 组精确 SHA 重复涉及 243 个冗余路径，理论最大仅省 2,066,256 字节。当前 Git 对象 pack 约 497,531,702 字节，已经使用压缩及内容寻址；再次把网页 gzip 后提交，对 Git 存储的额外收益有限，还会增加路由和摘要处理成本。

压缩分析参考了 [posh-crouton/dovahzul-archive 收录的 Thuum.org 备份包](https://github.com/posh-crouton/dovahzul-archive/blob/main/other/thuum-backup/thuumbackup.7z)，备份来源与抓取者署名见[上游说明](https://github.com/posh-crouton/dovahzul-archive/blob/main/other/thuum-backup/Index.md)。对其本地解包副本的只读扫描为 3,062,212,968 字节，其中 HTML 3,025,051,284 字节，约占 98.8%。它以文字为主，本项目镜像则以图片为主，二者的压缩收益不同。

## 已采用：轻量部署与完整取证分开

新增 `WOW_Encyclopedia_20080512_runtime_20261013.zip`：502,151,286 字节，解压总量 613,287,622 字节，8,316 成员。它包含所有 8,304 部署文件、冻结 manifest、4 个兼容支持文件、服务器与启动器、说明和逐文件校验清单。相较完整恢复包的 2,251,344,514 字节，下载体积减少约 77.7%；它通过排除研究及原始下载证据减小范围，并不声称这些证据被压成了同一份小包。

ZIP SHA-256：`49048568821e307c03764d486e76ab952b4aea460dd38ccf53f973263386c115`。所有原始图片按原字节复制，使用 DEFLATE-6；逐成员流式核 CRC、SHA、长度、白名单和 FILE_SHA256SUMS，不创建额外解压副本。此前 Git-only 全新克隆已经证明这些运行依赖可独立启动，包内字节与冻结树一致。

Git 主树继续提供可审阅、直接启动的文件；完整恢复 ZIP、原始来源包与失败记录另保留。普通浏览用户可仅下载轻量包，验证并解压后按需删除下载 ZIP，避免保留 Git 对象库或完整研究树。维护者核验历史来源时使用本地完整取证包；公开取证材料需另行处理原始响应元数据。

## 暂未改变运行存储格式

没有将站点文件改为 `.gz`，服务器仍按原路由读取原文件。预压缩文本需要服务层明确支持 Content-Encoding、回退路径和原始/压缩摘要；本轮约 39 MB 的站点文本收益不足以要求用户承担这项格式变化。图片不进行 JPEG/WebP 重编码，以免改变历史素材。

[NTFS 文件压缩](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/compact)可作为保留原字节的本机可选方案，尤其适合大 JSON/文字证据；本轮未对整个工作区启用，也未计入收益。早期的 14,000,000,000 字节预算已于 2026-10-14 取消；当前按新增量预检 D 盘余量，并保留 10GiB 加 256MiB 缓冲。

依据：[完整测量](../research/github-publication-20261012/compression-analysis.md)、[逐文件测量 JSON](../research/github-publication-20261012/compression-analysis.json)、[轻量包核验](../research/github-publication-20261012/runtime-package-verification.md)。

## 2026-10-14：当前浏览版便携包

新版浏览包直接收录当前派生站点、历史展品改造、36 张已有补充图片、本地旧地址兼容和动态图片地址修复。解压后运行 `START_BROWSE.cmd`，需要本机 Python；浏览时无需原仓库及研究目录。该包本轮保存在本地，线上下载入口仍指向此前发布的运行包。

| 范围 | 字节 |
| --- | ---: |
| 静态浏览站点 | 556,973,990 |
| 全包解压成员总量 | 560,576,253 |
| DEFLATE-6 ZIP | 501,698,432 |
| 无损压缩节省 | 58,877,821 |

包名 `WOW_Encyclopedia_20080512_browser_20261014_v5.zip`，8,442 个成员，SHA-256 为 `a3bfb85d3f8f03fe02e5dd72b1782aae5f43da2e612f7bd12941b09f81e2ced4`。图片保持原字节；完整逐成员报告保留在本地，Git 保存[简要打包记录](../research/local-maintenance-20261014/portable-package-summary.json)和独立浏览验收。

新增本轮浏览版与候选包之前的空间盘点约 15.49 GB；五份旧 Pages 派生树合计约 2.78 GB，内容与当前版存在差异，因此继续作为检查点保留。大份静态引用明细已无损压缩为约 355–359 KB 的 gzip 文件，Git 仅纳入摘要。工作区总量按用户最新约定不设固定 14GB 上限；下载、导出和打包预检继续保留 D 盘 10GiB 加 256MiB 缓冲。

旧运行包、首次候选包及来源包仍保留，版本用途与实际验收见[本地整理记录](local-maintenance-20261014.md)。

## 2026-10-15：发布浏览包（v14）

[新版离线包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/blob/main/docs/release-history/archive-20080512-browser-20261015.md)收录当前派生站点和独立启动器，解压后不需要 Git 仓库或研究目录。旧 Release 和本地历史 ZIP 继续保留。

| 文件类别 | 解压字节 | ZIP 成员压缩字节 |
| --- | ---: | ---: |
| HTML / XML / XSL | 54,337,780 | 8,634,650 |
| JavaScript / CSS | 5,414,033 | 686,465 |
| 图片 | 492,130,501 | 488,011,916 |
| 其他（含来源索引与启动文件） | 14,573,208 | 3,673,454 |

ZIP 共 502,662,461 字节，8,502 个成员，解压成员合计 566,455,522 字节；容器目录等开销另占 1,655,976 字节。图片占解压总量约 86.9%，已有压缩格式的图片仅进一步缩小约 0.84%；保留原图字节并使用 DEFLATE-6，因此本项目不会得到以 HTML 为主的备份包那样的体积降幅。

SHA-256 为 `7d13b98943180e52cc024d43f73148e8450dd5f81379b95083b9ce1f57df0c9e`。独立验收实读全部成员核对 CRC、SHA、长度与清单，再从带空格路径的解压副本以 Python `-I` 启动本地服务器，完成 44 次 GET / HEAD 检查；Windows 启动器未实际双击。详见[打包摘要](../research/v14-integration/portable-package-summary.json)、[独立验收](../research/v14-integration/root-portable-acceptance.json)与[Release 资产确认](../research/v14-integration/root-release-publication.json)。

完整取证 ZIP 及原始响应元数据继续留本地；公开浏览包只包含派生站点、来源索引和启动文件。检查后 D 盘余量为 30,550,495,232 字节，仍高于 11,005,853,696 字节安全阈值。本轮没有清理冻结副本，也未对图片重新编码。

## 2026-10-16：最终浏览包（v24）

本轮单次制作 v24 处理后离线包，收录最终派生页面与启动文件，已发布至 [GitHub Releases](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/tag/archive-20080512-browser-20261016)。此前浏览包、冻结副本与原始取证包继续保留。

| 文件类别 | 解压字节 | ZIP 成员压缩字节 |
| --- | ---: | ---: |
| HTML / XML / XSL | 54,567,680 | 8,664,423 |
| JavaScript / CSS | 5,429,702 | 687,646 |
| 图片 | 500,025,157 | 495,692,297 |
| 其他（含来源索引与启动文件） | 14,879,092 | 3,712,873 |

ZIP 510,437,875 字节，共 8,644 个成员，解压成员合计 574,901,631 字节。原始图片不重编码；DEFLATE-6 主要压缩文本及重复来源信息。

SHA-256：`2507f0fe744af971854048c711f3cba24a4e43b4bd2a78b20e93deb4ef3ba4e7`。主代理独立实读全部成员，检查 CRC、SHA、长度、路径白名单；从含空格路径的解压副本以 Python `-I` 启动包内服务器，完成 128 次 GET / HEAD 检查。实际浏览使用同字节 v24 的既有验收；Windows 启动器未实际双击。

[包摘要](../research/continuous-recovery-20261016/publication/v24-portable-package-summary.json) · [独立验收](../research/continuous-recovery-20261016/publication/root-v24-portable-acceptance.json)。验收后 D 盘余量 21,781,245,952 字节，安全阈值 11,005,853,696 字节。

## 2026-10-19：v33 浏览包

[v33 离线包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/blob/main/docs/release-history/archive-20080512-browser-20261019.md)沿用 10 月 18 日构建的原包，533 MB 下载、约 598 MB 解压，不收录研究目录和原始 HTTP 响应。独立验收重新读取全部 9,024 个成员，并从含空格的隔离目录启动包内服务器，检查 201 个路径的 GET/HEAD。

| 文件类别 | 解压字节 | ZIP 成员压缩字节 |
| --- | ---: | ---: |
| HTML / XML / XSL | 54,499,551 | 8,663,642 |
| JavaScript / CSS | 5,477,144 | 691,384 |
| 图片 | 522,550,066 | 518,028,124 |
| 其他（含来源索引与启动文件） | 15,626,910 | 3,805,752 |

ZIP 为 532,938,958 字节，解压成员合计 598,153,671 字节。文本和脚本从约 60 MB 缩至 9.36 MB；图片进一步压缩仅节省约 4.52 MB。后续继续保留原图字节和现有 ZIP 格式，避免为很小的额外压缩收益改变浏览资源格式。新版素材增加包体积属于实际图片新增，不能靠重复 HTML 压缩抵消。

[独立包验收与分项统计](../research/continuous-recovery-20261019/publication/root-v33-portable-acceptance.json) · [Release 资产确认](../research/continuous-recovery-20261019/publication/root-v33-release-publication.json)。本次检查后 D 盘余量约 45.19 GB；下载、导出与大写入仍受相同安全阈值约束。

## 2026-10-19：v38 浏览包

新处理包为534,197,885字节，共9,120成员，解压总量599,564,048字节；纯站点为595,689,284字节。新增的96个图片资源保持原字节，ZIP继续使用DEFLATE-6。

| 文件类别 | 解压字节 | ZIP成员压缩字节 |
|---|---:|---:|
| HTML/XML/XSL | 54,478,935 | 8,661,926 |
| JavaScript/CSS | 5,486,423 | 692,248 |
| 图片 | 523,783,945 | 519,247,320 |
| 其他（含来源与启动文件） | 15,814,745 | 3,828,921 |

图片占ZIP成员压缩字节约97.5%，决定了包体积；文本虽然压缩明显，继续压缩图片只能节省少量空间。继续采用原图字节、分层浏览包与来源取证分开的策略，保留D盘安全余量。本轮没有批量删除历史副本或改写原图。独立检查读取全部成员，并从新解压的包启动服务器，完成137个路径的GET/HEAD。[独立包验收](../research/continuous-recovery-20261019/publication/root-v38-portable-acceptance.json)。

[v38下载页](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/tag/archive-20080512-browser-20261019-v38)已发布，旧版资产保持可用。三项Release资产在发布前后均与本地大小和SHA匹配。

## 2026-10-20：v39 浏览包

v39 ZIP 为 534,242,751 字节，9,122 个成员，解压成员合计 599,611,852 字节；站点本身为 595,736,319 字节。相比 v38，ZIP 增加 44,866 字节，主要来自新增的两条图片路径；图片沿用已有原始文件。

| 文件类别 | 解压字节 | ZIP 成员压缩字节 |
| --- | ---: | ---: |
| HTML / XML / XSL | 54,478,123 | 8,661,972 |
| JavaScript / CSS | 5,486,633 | 692,275 |
| 图片 | 523,827,683 | 519,290,983 |
| 其他（含来源与启动文件） | 15,819,413 | 3,829,717 |

继续采用 DEFLATE-6、保留原图字节与独立浏览包。主代理读取全部成员并启动包内 Python 服务器，56 个路径的 112 次 GET/HEAD 检查通过；浏览展示复用同字节 v39 的四页验收。此次未实际双击 Windows 启动器。

[打包摘要](../research/continuous-recovery-20261020/publication/v39-portable-package-summary.json) · [独立包验收](../research/continuous-recovery-20261020/publication/root-v39-portable-acceptance.json) · [v39 下载页](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/blob/main/docs/release-history/archive-20080512-browser-20261020-v39.md)。

## 2026-10-23：历史 Pages 导出去重

57 个历史版本共 513,856 个文件、33,445,408,630 字节逻辑内容，整理为 60 个文件的共享归档，归档目录逻辑长度 665,351,745 字节。13,234 个唯一对象（未压缩共 1,456,362,754 字节）全部实读核验，三个代表版本恢复并独立验收；清理55棵旧展开目录，保留v55、v56、原始来源及完整历史ZIP。

文件级 NTFS AllocationSize 核账为净节省 32,049,445,528 字节（约32.05 GB）：删除的旧文件分配 32,714,919,104 字节，减去新归档文件分配 665,473,576 字节。此数不含目录元数据和少量审计文件，也不是D盘余量差；三份临时恢复副本的1,784,109,860字节未重复计入。浏览版和Release仍为v56，本次没有发布新网页或离线包。

[去重方法、核验与恢复命令](historical-export-deduplication.md) · [整理后的验收摘要](evidence/historical-export-deduplication-20261023.json)。

## 2026-10-22：本地空间清理

完成C、D盘的项目占用清点；通过大文本及旧会话的NTFS透明压缩、清理可重建发布分片和v55／v56验收解压副本，净节省约7.40GB。原始资料、完整历史ZIP和已验收Pages导出继续保留。后续最大机会是历史导出的集中去重归档，详见[清理报告与保留清单](storage-cleanup-20261022.md)。个人会话路径及逐文件审计材料保存在本地。
