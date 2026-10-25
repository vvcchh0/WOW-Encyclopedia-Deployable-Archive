# 声望与奖励图标补齐

2026-10-25 为奖励表补入103个关联图标显示，累计使用106个图片文件、107个原路径对应。新增部分包括101个Cavern of Time TBC JPEG和两个已保存的TBC计算器PNG。图片原字节保存，显示尺寸调整为物品36×36、货币16×16。

## 对应方法

七项自定义文件名先按原奖励名称核对物品记录，包括Mark of Defiance、Libram of Zeal、Mark of Conquest、Mark of Vindication、Idol of Savagery、Totem of Impact和Mark of Honor Hold。其余96个图标按原脚本中的完整游戏素材标识对应，保留大小写或扩展名不同的原路径。

来源是[Cavern of Time TBC](https://tbc.cavernoftime.com/)于2026-10-25实际提供的图像，以及[固定2019年提交的TBC计算器](https://github.com/Vampyr7878/WoW-Talent-Caluclator-TBC/tree/2a5f39aadb1c88ded12ff6389f4f0bdc4470c2a4)。这些属于后期关联素材，原2008年GIF的像素身份仍未知。页面上提供来源入口，原奖励文字、价格与效果保留。

例如Totem of Impact仍显示原页面的“46”点效果，没有采用当前数据库的“47”；Mark of Conquest只采用与原图标ArmorKit_12有依据的物品记录。`INV_Jewelry_Ring_48`在本次Cavern路径返回404，保持待补，不据此判断Wayback是否存档。

## 动态缺图盘点

原先331项选定清单没有覆盖全部动态奖励表。补齐七项后，本地21份奖励脚本还有575条缺图构造引用、313个不同路径。本次两个标准标识素材包对应其中222条引用、97个路径，剩余353条引用、216个路径。这是指定脚本范围的静态计数，实际可见条目随声望、职业和阵营筛选变化。

另外三个PvP奖励页面使用相同图片路径，已加入来源提示和显示尺寸规则，其条目不混入上述声望脚本计数。[共享脚本检查](evidence/faction-art-shared-script-uses-20261025.json)

## 浏览与构建

22个声望、徽记和PvP页面完成原生阵营按钮、声望下拉和职业选择检查，103个补充图标均在界面实际出现。另修复共享悬浮说明在首次鼠标进入前未初始化坐标的问题，以及两张旧PvP奖励页在较晚菜单中找不到节点的问题。物品说明继续取自保存的`itemHTML`。

服装赛获奖页独立检查：2006年10月新闻展开后可跳转至静态阅读页，保留五位获奖者及作品名称，照片仍待补齐。正文来源是Common Crawl的2008-08-29官方页面记录。

v67本地导出10,441个文件、718,484,189字节，逐文件回读通过。奖励页面879项检查、阅读页24项检查通过。v65、v66试验输出和失败回执保留，未部署；验收以v67为准。[本地验收](evidence/v67-local-acceptance-20261025.json)

来源核对：[七项奖励](evidence/faction-item-art-20261025.json)、[第一组标准标识](evidence/faction-canonical-art-20261025.json)、[第二组标准标识](evidence/faction-canonical-more-art-20261025.json)、[服装赛正文](evidence/costume-contest-source-20261025.json)。
