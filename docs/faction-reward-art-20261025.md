# 声望与奖励图标补齐

2026-10-25 为奖励表补入111个关联图标显示，累计使用114个图片文件、115个原路径对应。新增部分包括109个Cavern of Time TBC JPEG和两个已保存的TBC计算器PNG。图片原字节保存，显示尺寸调整为物品36×36、货币16×16。

## 对应方法

七项自定义文件名先按原奖励名称核对物品记录，包括Mark of Defiance、Libram of Zeal、Mark of Conquest、Mark of Vindication、Idol of Savagery、Totem of Impact和Mark of Honor Hold。其余104个图标按原脚本中的完整游戏素材标识对应，保留大小写或扩展名不同的原路径。

来源是[Cavern of Time TBC](https://tbc.cavernoftime.com/)于2026-10-25实际提供的图像，以及[固定2019年提交的TBC计算器](https://github.com/Vampyr7878/WoW-Talent-Caluclator-TBC/tree/2a5f39aadb1c88ded12ff6389f4f0bdc4470c2a4)。这些属于后期关联素材，原2008年GIF的像素身份仍未知。页面上提供来源入口，原奖励文字、价格与效果保留。

例如Totem of Impact仍显示原页面的“46”点效果，没有采用当前数据库的“47”；Mark of Conquest只采用与原图标ArmorKit_12有依据的物品记录。`INV_Jewelry_Ring_48`和`INV_Jewelry_Ring_51`在本次Cavern路径返回404，保持待补，不据此判断Wayback是否存档。

## 动态缺图盘点

原先331项选定清单没有覆盖全部动态奖励表。补齐七项后，本地21份奖励脚本还有575条缺图构造引用、313个不同路径。本次三个标准标识素材包对应其中230条引用、105个路径，剩余345条引用、208个路径。这是指定脚本范围的静态计数，实际可见条目随声望、职业和阵营筛选变化。

另外三个PvP奖励页面使用相同图片路径，已加入来源提示和显示尺寸规则，其条目不混入上述声望脚本计数。[共享脚本检查](evidence/faction-art-shared-script-uses-20261025.json)

## 浏览与构建

22个声望、徽记和PvP页面完成原生阵营按钮、声望下拉和职业选择检查，111个补充图标均在界面实际出现。另修复共享悬浮说明在首次鼠标进入前未初始化坐标的问题，以及两张旧PvP奖励页在较晚菜单中找不到节点的问题。物品说明继续取自保存的`itemHTML`。

服装赛获奖页独立检查：2006年10月新闻展开后可跳转至静态阅读页，保留五位获奖者及作品名称，照片仍待补齐。正文来源是Common Crawl的2008-08-29官方页面记录。

v67的22页奖励检查879项、阅读页检查24项通过。v68再加入八张饰品图标，五页93项检查通过；此前素材、阅读页和兼容修复逐字节保持。最终导出10,449个文件、718,560,407字节，完整独立回读通过。v65、v66失败输出保留，v67为本地已验收中间检查点，合并发布v68。[v67验收](evidence/v67-local-acceptance-20261025.json)、[v68验收](evidence/v68-local-acceptance-20261025.json)

来源核对：[七项奖励](evidence/faction-item-art-20261025.json)、[第一组标准标识](evidence/faction-canonical-art-20261025.json)、[第二组标准标识](evidence/faction-canonical-more-art-20261025.json)、[八项饰品](evidence/faction-canonical-third-art-20261025.json)、[服装赛正文](evidence/costume-contest-source-20261025.json)。

最后一组在第三个请求返回404后停止：九次请求取得八图，计划中39项未请求，留待后续批次。

## 线上发布

v68的168个变更对象与本地逐项一致。线上浏览发现旧`.shtml`直达地址缺少静态文件，随后以独立的跳转目录及更新后的来源清单发布v68.1，保留已验收的v68目录。该入口现经301转向目录，再进入获奖正文；手机布局和五条获奖记录复核通过。最终网站10,450文件、718,562,930字节。[线上验收](evidence/v68-1-online-acceptance-20261025.json)

部分原历史声望下拉菜单的初始化档位不一致，浏览检查通过原生点击另一档后再返回第一档来覆盖这些条目；该既有行为留待后续兼容修复。
