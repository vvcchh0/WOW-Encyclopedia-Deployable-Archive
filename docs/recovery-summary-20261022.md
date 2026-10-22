# 2026-10-22 恢复回顾

本轮从 v52 继续，已发布 [v56 在线版](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/)与[离线浏览包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/tag/archive-20080512-browser-20261022-v56)。以2008年5月12日官网为重建基准，新增关联图片在页面来源目录中注明出处。

## 地下城与 Deadmines

ArchiveCraft 的地下城故事与本地保存的官网指南正文能够对应。19个经典副本主题和五个 Outland 区域组已有正文，未重复收录。

Deadmines 九张早期原图和十张预览也已在 v52 保存。实际检查本地 Chrome 和20个线上对象，确认均可访问，并非部署漏传；可从[地下城指南](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/basics/dungeons.html)打开。原图有2008年4月2日捕获记录，但当前证据不足以进一步确定具体 Alpha 构建号。图注、旧地址和来源对应见[地下城追溯](dungeon-source-tracing-20261022.md)。

## 本轮补充

| 内容 | 图片文件 | 获取与接入 |
| --- | ---: | --- |
| Profession Updates 标题图 | 1 | 从 ArchiveCraft 取得，v53接入 |
| 天赋连线箭头 | 18 | 复用已保存的后期计算器素材，六种几何的灰／绿／黄状态，v54接入 |
| 声望奖励图标 | 3 | 从公开 coolwow2 仓库取得，接入11页的85处引用 |
| 改名或移树天赋的明暗图标 | 20 | 十个同职业天赋，v55接入 |
| 同名天赋的明暗图标 | 18 | 九个同职业天赋，v56接入 |
| 合计 | **60** | **4个新下载、56个从现有来源包复用** |

新增图片共85,003字节，均保留来源字节；本轮没有新增确认属于2008年捕获的原图。天赋关联图片总量由986增至1,024，保留原文字、数据和加点规则。映射取舍、来源版本与未选候选见[天赋图像来源](talent-image-sources-20261022.md)。三张存在连线断口的 down-3 箭头暂未接入。

## 验收与发布

- v56共10,205个站点文件；相对v55新增18张JPEG，只更新四个资源目录／路由文件。[导出验收](../research/continuous-recovery-20261022/root-v56-export-acceptance.json)
- 九个新映射天赋完成合法加点、说明与下一级说明、模板保存和重载检查，核对18个图片响应及五职业数据。普通 Chrome 窗口中的两个补充视觉控制通过；无头模式局部绘制差异与一处报告文字更正保留在[浏览验收](../research/continuous-recovery-20261022/root-v56-browser-acceptance.json)，未据此改写产品样式。
- Pages提交 `ada74291b7f46afe3289fb2773e31449f4a5eb83` 的[部署构建](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/actions/runs/39789068533)成功；22个变化文件通过direct取得，实际响应体与本地一致。[线上验收](../research/continuous-recovery-20261022/root-v56-online-acceptance.json)
- 离线ZIP为546,446,950字节，解压635,822,442字节，10,211个成员；从新的带空格目录启动包内服务器，245项HTTP检查通过。[包内验收](../research/continuous-recovery-20261022/publication/v56-portable-acceptance.json)
- Release公开附件的长度和GitHub摘要已核对；匿名读取说明与校验文件，检查ZIP下载响应长度，未再次下载整个ZIP。[公开附件验收](../research/continuous-recovery-20261022/publication/v56-public-assets-acceptance.json)

源码与来源说明发布于主树 `7dff875e341d9d11cbfeb6417665b12059575c75`；本回顾及最终验收随后作独立文档提交。main同步、Pages构建与Release分别记录。

## 剩余缺口与接续条件

本轮v53清单中的390个非图库缺图目标接通59个，剩331个；职业标题图另计。这个范围不等于全站缺图总数，逐项目标见[剩余资源清单](../research/continuous-recovery-20261022/v56-remaining-resource-targets.json)。部分天赋背景和界面素材、指南插图、新闻配图及BlizzCast音频仍待恢复。

50个玩家截图图库所涉及的1,684张截图，其原图和缩略图仍未取得；已有指南图片单独统计。保留[逐组可及性调查](player-gallery-accessibility-20261020.md)，Karazhan、Black Temple等已暂缓窗口只有出现新捕获或关联页线索时才重启。

本轮Wayback控制在09:04 UTC直连超时、代理返回429，后续未开启Wayback批次。ArchiveCraft当前页面的上传路径或页脚年份不当作历史捕获日期；关联来源继续与原站捕获分别保存。未使用付费Firecrawl。

授权窗口为07:21:33–14:51:33 UTC；来源获取与导出按预定提前截止，发布主体在截止前完成。工作时间线与执行约定见[持续记录](continuous-recovery-20261022.md)，最终进程、空间和同步状态见[总账](../research/continuous-recovery-20261022/status.json)。原始站点、Source15/16及历史版本保持冻结。
