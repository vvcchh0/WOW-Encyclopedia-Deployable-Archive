# WOW Encyclopedia Deployable Archive

重建早期魔兽世界官方百科与部分官网，供在线浏览和本地保存。这是一个非官方历史保存项目，以 [2008-05-12 的 Wayback Machine 快照](https://web.archive.org/web/20080512210044/http://www.worldofwarcraft.com/info/encyclopedia/index.xml)为基准。

**[浏览百科](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/encyclopedia/index.xml.html)** · **[浏览官网](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/)** · [更新记录](CHANGELOG.md)

## 已完成

- 保存百科首页与 51 个词条，共 52 页。
- 扩展至 Current News、Game Guide、Media 等官网栏目，现有镜像包含 917 个页面文档和配套资源。
- 提供在线网站与离线包，恢复菜单、分类展开和百科标题搜索。
- 在线版将旧登录与奖励入口改为历史展品，历史业务表单采用静态展示。
- 补回部分布局图片与相关截图素材，并修复 50 个玩家截图图库的目录路径。

## 当前不足

- 图片与部分静态资源仍有缺口。50 个玩家截图图库的原图与配套缩略图尚待恢复。
- Flash、账号和依赖原站服务的功能不可用。
- 已发布离线包仍为 2026-10-13 版本，本轮浏览版修复先更新在线网站。

## 本地使用

下载[离线包](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/download/archive-20080512-processed-20261012/WOW_Encyclopedia_20080512_runtime_20261013.zip)（约 502 MB，解压后约 613 MB），Windows 用户可解压后双击 `START_OFFLINE.cmd`。

也可安装 Python 3，克隆仓库并启动：

```sh
git clone https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive.git
cd WOW-Encyclopedia-Deployable-Archive
python tools/offline_mirror.py serve --host 127.0.0.1 --port 8765
```

启动后打开[本地官网](http://127.0.0.1:8765/)或[本地百科](http://127.0.0.1:8765/info/encyclopedia/index.xml)。

## 参与协作

欢迎通过 [Issues](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/issues)反馈缺图、失效链接或提供可用的 Wayback 捕获，也欢迎提交页面与兼容性修复。请附页面地址和问题描述；如有存档链接，也请一并提供。

工作进度见 [CHANGELOG](CHANGELOG.md)；获取方法、来源、校验与部署细节见[工程文档](docs/README.md)。

原站文字与美术素材归 Blizzard Entertainment 等权利人所有，详见 [NOTICE](NOTICE.md)。
