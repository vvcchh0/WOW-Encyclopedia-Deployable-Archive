# WOW Encyclopedia Deployable Archive

重建早期魔兽世界官方百科与部分官网，供在线浏览和本地保存。这是一个非官方历史保存项目，以 [2008-05-12 的 Wayback Machine 快照](https://web.archive.org/web/20080512210044/http://www.worldofwarcraft.com/info/encyclopedia/index.xml)为基准。

**[浏览百科](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/encyclopedia/index.xml.html)** · **[浏览官网](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/)** · [更新记录](CHANGELOG.md)

## 已完成

- 保存百科首页与 51 个词条，共 52 页。
- 扩展至 Current News、Game Guide、Media 等官网栏目，保存历史页面文档及配套资源。
- 提供在线网站与离线包，恢复菜单、分类展开和百科标题搜索。
- 在线版将旧登录与奖励入口改为历史展品，历史业务表单采用静态展示。
- 补回部分布局图片与相关截图素材，并修复 50 个玩家截图图库的目录路径。
- 补回 Archived News 的 2007 年 8 月新闻，已接通现有侧栏的历史内容入口。
- 补齐 2007 年 8 月新闻的二十七张配图，并在六个玩家图库中展示二十二张保存下来的指南预览。
- 恢复情人节、春节与 World PvP 的三十九张指南大图，提供捕获日期和原尺寸查看。
- 补回更多 2007–2008 年新闻配图；旧账号升级公告改为静态历史展品。
- 补回银月城、竞技场和玛瑟里顿文章配图，恢复副本进度图与旧专业配方的查看。
- 补回 2004–2005 年两处旧新闻配图，商店促销条目以历史展品呈现。

## 当前不足

- 50 个玩家截图图库的原图与缩略图均未恢复，共涉及 1,684 张截图；9 组页面另有已保存的指南图片。[缺失范围与存档调查](docs/player-gallery-accessibility-20261020.md)列出逐组情况，欢迎提供新线索。
- Flash、账号和依赖原站服务的功能不可用。
- 部分新闻配图和历史排行榜数据仍待补齐。

## 本地使用

安装 Python 3 后，下载 [2026-10-20 离线包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/download/archive-20080512-browser-20261020-v39/WOW_Encyclopedia_20080512_browser_20261020_v39.zip)（约 534 MB，解压后约 600 MB）。Windows 用户解压后双击 `START_BROWSE.cmd`。

macOS / Linux 用户在解压目录运行：

```sh
python3 tools/serve_pages_preview.py --site site --port 0 --open-browser
```

启动后会打开本地浏览页面。在线版与离线包均为 v39，本轮补回两处旧新闻配图，并将 2004 年商店促销条目改为静态历史展品。后续进度见[更新记录](CHANGELOG.md)。

## 参与协作

欢迎通过 [Issues](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/issues)反馈缺图、失效链接或提供可用的 Wayback 捕获，也欢迎提交页面与兼容性修复。请附页面地址和问题描述；如有存档链接，也请一并提供。

工作进度见 [CHANGELOG](CHANGELOG.md)；获取方法、来源、校验与部署细节见[工程文档](docs/README.md)。

原站文字与美术素材归 Blizzard Entertainment 等权利人所有，详见 [NOTICE](NOTICE.md)。
