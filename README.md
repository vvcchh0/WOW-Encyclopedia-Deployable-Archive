# WOW Encyclopedia Deployable Archive

重建早期魔兽世界官方百科与部分官网，供在线浏览和本地保存。这是一个非官方历史保存项目，以 [2008-05-12 的 Wayback Machine 快照](https://web.archive.org/web/20080512210044/http://www.worldofwarcraft.com/info/encyclopedia/index.xml)为基准。

**[浏览百科](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/encyclopedia/index.xml.html)** · **[浏览官网](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/)** · [更新记录](CHANGELOG.md)

## 已完成

- 保存百科首页与 51 个词条，共 52 页。
- 扩展至 Current News、Game Guide、Media 等官网栏目，提供在线网站与离线包，恢复菜单、分类展开和百科标题搜索。
- 接通 Archived News 的历史新闻入口，补回 2007 年 8 月新闻及其二十七张配图，并补充其他年份的新闻与文章图片。
- 恢复副本进度图、旧专业配方与部分原画查看；保存二十二张指南预览及三十九张指南大图。
- 将旧登录、奖励、报名和促销入口改为历史展品。
- 恢复宝石插槽火花、男性矮人舞蹈与海象人模型三处 Flash 展示，修复下载页悬停。
- 修复九职业天赋计算器的加点、重置和模板保存；提供 BlizzCast 前两期访谈及节目目录的本地阅读页。
- 补入七份早期专题正文，为天赋页加入 1,024 张注明后期关联来源的图标。
- 补齐天赋计算器的状态边框、重置和打印按钮、18张连线箭头，并恢复点数框布局；补充部分声望奖励图标。
- 补充百科、指南与职业专题的五幅配图，页面注明 ArchiveCraft 来源。
- 恢复奥尔多／占星者说明弹窗与派系切换，修复四页 Wrath 字母图的显示。
- 修复 Arathi 指南的图片目录，恢复二十张已有预览的显示。
- 核对地下城正文与 Deadmines 的九张早期原图、十张预览，可从[地下城指南](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/basics/dungeons.html)浏览。

## 当前不足

- 50 个玩家截图图库的原图与缩略图均未恢复，共涉及 1,684 张截图；9 组页面另有已保存的指南图片。[缺失范围与存档调查](docs/player-gallery-accessibility-20261020.md)列出逐组情况，欢迎提供新线索。
- 其他 Flash 内容仍有缺口；账号和依赖原站服务的功能不提供。
- 天赋计算器仍缺部分图标、背景和界面素材；BlizzCast 的图片与音频待恢复。
- 部分新闻配图和历史排行榜数据仍待补齐。

## 本地使用

安装 Python 3 后，下载 [2026-10-22 离线包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/download/archive-20080512-browser-20261022-v56/WOW_Encyclopedia_20080512_browser_20261022_v56.zip)（约 546 MB，解压后约 636 MB）。Windows 用户解压后双击 `START_BROWSE.cmd`。

macOS / Linux 用户在解压目录运行：

```sh
python3 tools/serve_pages_preview.py --site site --port 0 --open-browser
```

启动后会打开本地浏览页面。在线版与离线包均为 v56。后续进度见[更新记录](CHANGELOG.md)。

## 参与协作

欢迎通过 [Issues](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/issues)反馈缺图、失效链接或提供可用的 Wayback 捕获，也欢迎提交页面与兼容性修复。请附页面地址和问题描述；如有存档链接，也请一并提供。

工作进度见 [CHANGELOG](CHANGELOG.md)；获取方法、来源、校验与部署细节见[工程文档](docs/README.md)。

原站文字与美术素材归 Blizzard Entertainment 等权利人所有，详见 [NOTICE](NOTICE.md)。
