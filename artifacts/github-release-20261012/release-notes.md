# WOW Encyclopedia Deployable Archive

Archive baseline: **2008-05-12 21:00:44 UTC (20080512210044)**. Processing: **2026-10-12**. Publication validation and runtime packaging: **2026-10-13**.

早期魔兽世界官方百科与部分官网镜像：8,304 条路由、917 个文档，917/917完整浏览验收通过；仍有3,358个去重缺口，Flash及部分动态/账号服务不完整。

## 下载与启动

下载 `WOW_Encyclopedia_20080512_runtime_20261013.zip`（502,151,286 B）与相邻`.sha256`。SHA-256：`49048568821e307c03764d486e76ab952b4aea460dd38ccf53f973263386c115`。解压约613,287,622 B，共8,316成员，CRC/SHA/长度/白名单全部核验。图片按原字节保存，无损DEFLATE-6。

解压到短目录，例如`D:\WoW2008`，使用Python3.11或更新版本运行`START_OFFLINE.cmd`，或：

```sh
python tools/offline_mirror.py serve --host 127.0.0.1 --port 8765
```

打开`http://127.0.0.1:8765/`或`http://127.0.0.1:8765/info/encyclopedia/index.xml`。服务器仅监听本机，不自动联网下载。

## 保存与发布范围

Git提供运行文件、工具、方法回顾及关键验收。轻量包排除完整取证/原始下载，相比2.25GB取证包减少下载约77.7%。完整取证ZIP、三卷备份及历史来源包保持不变并保留本地；原始响应元数据存在尚未确认用途的Cookie字段，本次未直接上传。

详见仓库`docs/project-history-and-methodology.md`、`docs/github-publication-20261012.md`与`docs/storage-and-compression.md`。原始素材权利归Blizzard等原权利人；兼容组件保留自己的第三方声明。
