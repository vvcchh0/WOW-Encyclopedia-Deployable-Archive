# WOW Encyclopedia Deployable Archive

以 **2008-05-12 21:00:44 UTC** 的 Wayback Machine 快照为基准，保存并重建早期魔兽世界官方百科与部分官网。资源处理日期：**2026-10-12**；GitHub 发布验收日期：**2026-10-13**。

原始入口：[The Official Warcraft Encyclopedia](https://web.archive.org/web/20080512210044/http://www.worldofwarcraft.com/info/encyclopedia/index.xml)。各文件保留自己的实际捕获时间；较晚的 2008 素材、更早的静态补充及现代兼容文件分别记录，不把整站称为同一秒的快照。

## 在线浏览

[官网首页](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/) · [Warcraft Encyclopedia](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/encyclopedia/index.xml.html)

GitHub Pages 使用独立 `gh-pages` 分支；HTML 内容的历史 `.xml` 地址导出为 `.xml.html`，兼容项目路径、菜单与本地标题搜索。本站是非官方历史保存，仍有资源缺口，账号和原站在线服务不可用。发布方法及验收记录见[GitHub Pages 部署说明](docs/github-pages-deployment.md)。

## 本地启动

安装 Python 3，克隆仓库后在仓库目录执行：

```sh
git clone https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive.git
cd WOW-Encyclopedia-Deployable-Archive
python tools/offline_mirror.py serve --host 127.0.0.1 --port 8765
```

Windows 也可双击 `START_OFFLINE.cmd`。服务运行后打开[官网首页](http://127.0.0.1:8765/)或[官方百科](http://127.0.0.1:8765/info/encyclopedia/index.xml)。运行镜像只需要 Python 标准库，已生成的页面、资源和路由清单随 Git 提供，不需要先重新下载或构建。请使用本地服务器访问，直接打开 XML 文件不能替代服务器路由及 MIME 处理。

## 当前保存范围

| 项目 | 当前结果 |
|---|---|
| 百科核心 | 首页与 51 个词条，共 52 页 |
| 官网扩展镜像 | 8,304 条路由、917 个文档 |
| 完整浏览检查 | 917/917 文档通过；无页面脚本错误、资源请求失败或非本地请求 |
| 最后图片恢复批次 | 407 个逻辑图片 URL 全部取得并核验，跨年代补充分列 |
| 剩余缺口 | 3,358 个去重 URL，合并 HTTP/HTTPS 后 3,355 组；页面显示明确缺失提示 |

浏览检查通过代表镜像可浏览，**不代表原官网资源已全部恢复**。剩余缺口、部分动态数据及 Flash 内容仍限制完整性；登录、账号与其他线上服务不具备原站功能。源文件、改写副本、占位响应和浏览证据分开记录。

## 轻量部署包与压缩

仅浏览镜像可下载 [轻量部署 ZIP（502 MB）](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/download/archive-20080512-processed-20261012/WOW_Encyclopedia_20080512_runtime_20261013.zip)，解压约 613 MB，然后运行 `START_OFFLINE.cmd`。它包含同一份 8,304 路由镜像、来源清单和启动文件，不包含原始下载与完整研究证据。包的 CRC、成员 SHA、长度及白名单全部核验通过；原始图片未重编码。

镜像约 91% 的字节来自图片，文本 gzip 可省约 38.8 MB，图片再 gzip 仅省约 4.2 MB，精确重复内容约 2.1 MB。Git 对象已经压缩；当前采用无损 ZIP 分离“浏览部署”与“完整取证”，避免为了压缩修改冻结页面或图片。详见[空间与压缩策略](docs/storage-and-compression.md)。

## 完整取证备份（本地保留）

完整恢复 ZIP 为 **2,251,344,514 字节**，SHA-256 为 `66553fcd368ae5ee48dfb9f1b11897ac7fb3fd6a1983a0e303c2c088522c1c63`。它与原始来源包、历史版本和三份分卷保持不变，目前保留在项目维护者本地，**尚未上传到此次 Release**。

原始下载元数据包含 Archive/历史站点响应 Cookie 字段，有限扫描尚不能确认全部字段用途。首次发布选择已完成全内容检查的部署副本和关键证据，不直接公开这些未确认的原始元数据。`tools/release_archive.py` 和 `artifacts/github-release-20261012/release-assets.json` 用于维护者本地校验/合并原备份分卷。GitHub 自动 Source code 包只覆盖 Git 主树，不等同于完整取证备份。

## 工作记录与证据

- [工作回顾与方法](docs/project-history-and-methodology.md)：选版纠正、Thuum 对照、依赖发现、下载、验证、恢复与限制。
- [文档索引](docs/README.md)与[发布组织说明](docs/github-publication-20261012.md)。
- [基准复核](docs/reassessment-2008.md)、[2008 全量获取](docs/acquisition-2008.md)、[17 项缺口复核](docs/gap-review-20261011.md)。
- [离线重建](docs/offline-reconstruction-2008.md)、[官网资源恢复](docs/resource-recovery-2008.md)、[下载工具说明](tools/README.md)。
- [冻结构建来源清单](offline/build-manifest.json)、[最终缺口](research/final-gap-closure-20261012/final-build/README.md)、[完整浏览验收](research/offline-2008/full-recovery/round-108-8304-full-browser-validation.json)。
- [完整包验收](artifacts/offline-20261012-root-final-acceptance.json)与[短目录独立启动验收](artifacts/offline-20261012-recovery-portability-shortpath-check.json)。

早期 2010-12-03 候选虽然可以保存实体，但实际回放出现 XML 解析错误，已撤回其“最晚可用”结论。历史来源包保持不变，供比对；本项目重建基准是用户确认的 2008-05-12。

本站文字、美术及其他原始素材的权利归 Blizzard Entertainment 等原权利人所有。本仓库的保存与兼容修改不改变原权利归属，详见 [NOTICE](NOTICE.md)。
