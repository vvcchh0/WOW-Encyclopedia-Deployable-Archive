# 2026-10-16 恢复回顾

最终 v24 已同时发布到[在线网站](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/)与[离线 Release](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/tag/archive-20080512-browser-20261016)。离线包约 510 MB，解压约 575 MB，需要 Python 3。

## 本轮成果

相较本轮起点 v15，新增 141 个有效图片资源地址，共 7,894,656 字节；这是文件及资源地址计数，包含装饰图标和同素材的不同路径。

| 范围 | 新增资源 | 浏览结果 |
| --- | ---: | --- |
| 新闻 | 93 | 包括正文配图、首字母和栏目图标；2007 年 8 月的五十条新闻与全部二十七张配图可浏览 |
| 指南相邻素材 | 40 | 情人节、春节和 World PvP 展示三十二张大图；六张服装/模型视图与两张缩略图保存在素材目录 |
| 其他页面 | 6 | 补回页面实际引用的静态图片 |
| 欧服 | 2 | 保存两张每日截图原图，保留地区与捕获日期 |

六个玩家图库另展示二十二张已有指南预览。这些预览沿用此前保存的字节，未计入上述新增下载。

## 获取与重建

沿页面中的实际引用、脚本拼接规则和 CDX 索引调查精确原站地址，优先 direct，连接失败后在下载进程内回退到已有代理。每批有请求、时间及字节上限，遇限流或连续失败停批；没有调整系统网络与证书设置。

来源验收核对实际图片字节、捕获日期、原站链接与存档摘要，图片逐帧解码。新增资源进入独立派生层，原始站点、旧来源与历史包保留。相邻指南原图在独立展示区提供，不填入原动态玩家图库的截图槽位。设计见[指南图片与玩家图库](guide-image-collections.md)。

最终站点有 8,637 个声明文件、8,638 个实际文件。主代理检查全部导出字节及 107 项针对性浏览行为，线上 32 项对象与本地一致。离线包共 8,644 个成员；独立读完整包并启动解压副本，完成 128 次 GET / HEAD 检查。Windows 启动器未实际双击，浏览行为使用同字节站点的验收。压缩测量见[空间策略](storage-and-compression.md)。

## 仍待恢复

固定 1,104 个 HTML/HTM/XML/CSS 文件范围内，仍有 1,181 个静态图片地址、1,942 处缺图引用；其中新闻为 551 个地址、557 处引用。

原玩家图库的 JavaScript 目标单独计数：五十分区、1,684 个截图槽位，共 3,368 个原图/缩略图地址。其中 79 项实际回放 404、47 项传输未知、3,242 项未逐图请求。五十分区的目录索引窗口已连贯查至基准时点，目录调查没有新增原动态图库图片。Karazhan 的六十三张原图与六十三张缩略图仍缺失。

后续优先取回九个已有正索引的指南相邻资源，再复查三项最新新闻未知地址和八项旧新闻未知地址；关联站静态素材及欧服菜单依赖继续沿已保存的确切引用查找。MEDIA 的两张有效晚期截图已保留，本轮索引复核未发现可增加的基准内原图。

完整后续清单与来源绑定见[资源清单](../research/continuous-recovery-20261016/local-audit/final-v24-pending/public-summary.json)；静态完整计数明细压缩保留在本地。持续过程、失败与更正见[阶段记录](continuous-recovery-20261016.md)。

## 发布与证据

- [本地导出与浏览验收](../research/continuous-recovery-20261016/publication/root-v24-local-acceptance.json)
- [线上核对](../research/continuous-recovery-20261016/publication/root-v24-pages-online-acceptance.json)
- [离线包验收](../research/continuous-recovery-20261016/publication/root-v24-portable-acceptance.json)
- [Release 确认](../research/continuous-recovery-20261016/publication/root-v24-release-publication.json)
- [新增资源累计核对](../research/continuous-recovery-20261016/publication/root-v24-cumulative-acceptance.json)
- [后续清单独立核对](../research/continuous-recovery-20261016/publication/root-final-v24-pending-acceptance.json)
