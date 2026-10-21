# 非图库复原回顾：2026-10-21

本轮从v39推进到v52，[在线浏览](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/)与[离线浏览包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/tag/archive-20080512-browser-20261021-v52)已同步。以2008-05-12为重建基准，处理日期2026-10-21；各补充来源保留实际捕获日期。50个玩家图库与Media截图集合未在本轮重新获取。

## 恢复内容

- 九职业天赋计算器恢复加点、重置、非零模板保存与重载；加入986张注明后期来源的图标、6张界面图，并复用既有点数框素材。
- 通过Ruffle兼容层展示三份已有原始SWF：宝石插槽火花、男性矮人舞蹈、海象人模型；下载页悬停和共享菜单标签一并修复。
- 新增七份早期专题正文，更新内容目录并接通旧地址；BlizzCast前两期访谈及目录、RSS等形成五个本地阅读页，两期共50个对话块。
- 四幅百科／指南配图作为ArchiveCraft关联来源补充，页面给出来源链接；奥尔多／占星者说明弹窗使用已保存的原文恢复，奖励按钮地址修正。
- 已有Wrath字母图在四页恢复显示；Arathi指南的动态目录修正后，20张已保存的预览恢复显示，另外两张缩略图仍缺。

新增图片来源与已有图片的显示修复分别记录。本轮未通过Wayback取得新原图；后期天赋素材、当前关联站图片和原有历史捕获在来源表中区分。历史账号、报名、支付与促销功能继续以静态展品呈现。

## 获取与修复方法

Wayback的direct控制仍超时，代理控制返回429，按批次规则停止，没有改动全局DNS、代理或证书。Common Crawl静态次级目录可由direct取得，随后按精确域名、CDXJ记录与ARC偏移取得历史正文。原始HTTP与未处理来源留在本地，公开整理后的来源定位和派生结果。

修复进入新的派生版本：保留原始站点、Source15/16、旧版本和历史ZIP；在导出器中对精确来源脚本、页面与资源目录做兼容处理。Arathi问题尤其说明，应先核对动态拼接和本地精确文件，再决定是否需要下载：原22个异常路径中，20张图片已有实体，只有两张正确目标仍缺。

来源、方案与逐项验收见[复原记录](non-gallery-restoration-20261021.md)；执行过程与计划变更见[当日总账](continuous-recovery-20261021.md)。

## 验收与文件占用

最终站点有10,144个实际文件。主代理核对全部导出对象；v52相对v51仅修改Arathi页的一处目录赋值，所有图片、原脚本及其他页面保持字节一致。实际Chrome验证20张预览；其余功能复用对应版本的实际浏览记录和未变对象证明。v51核对80个线上对象，v52另核对25个相关对象，均成功。

处理后的ZIP约546MB、解压约634MB；全部10,150个成员独立检查，随后从含空格路径运行包内隔离服务，对来源表选出的页面与资源实际进行GET/HEAD检查。GitHub附件与本地包匹配，公开入口另作匿名检查。

图片占未压缩成员约525MB，已压缩的图片再次ZIP压缩收益很小；HTML等标记文件约55MB可压至约9MB。因此继续压缩主要能减少文本冗余，无法大幅缩小原字节图片。包内提供文件清单，公开仓库保留代码、整理后的来源与验收；原始取证包未上传。

- [v52完整导出核对](../research/continuous-recovery-20261021/publication/root-v52-export-acceptance.json)
- [实际浏览](../research/continuous-recovery-20261021/publication/root-v52-browser-acceptance.json)
- [线上对象](../research/continuous-recovery-20261021/publication/root-v52-pages-online-acceptance.json)
- [离线包与包内服务](../research/continuous-recovery-20261021/publication/root-v52-portable-acceptance.json)
- [公开Release](../research/continuous-recovery-20261021/publication/root-v52-release-publication.json)

## 剩余范围

分轮审计覆盖177条独立页面路径，修正后清单仍有391个本地资源目标，包括259个天赋素材目标、12个百科分类头像和两张Arathi缩略图。这是已检查状态的清单，尚未遍历所有动态状态；没有把本地缺图直接判为全网无存档。

BlizzCast图片与音频、部分旧新闻配图、专题插图、天赋背景和其他Flash依赖仍待取得。另有周年时间线截图目录的转换问题已单独记录，留待后续图库任务。玩家图库的范围结论继续见[此前调查](player-gallery-accessibility-20261020.md)。

后续先从[修正缺口清单](../research/continuous-recovery-20261021/publication/v52-remaining-resource-targets.csv)选择精确目标；Wayback需新的成功控制才恢复批次。有新捕获或关联来源时继续调查，已查窗口不盲目重复。
