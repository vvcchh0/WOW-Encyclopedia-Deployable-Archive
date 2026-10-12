# WOW Encyclopedia Deployable Archive

以 **2008-05-12 21:00:44 UTC** 的 Wayback Machine 快照为基准，保存并重建早期魔兽世界官方百科与部分官网。处理与发布整理日期：**2026-10-12**。

原始入口：[The Official Warcraft Encyclopedia](https://web.archive.org/web/20080512210044/http://www.worldofwarcraft.com/info/encyclopedia/index.xml)。各文件保留自己的实际捕获时间；较晚的 2008 素材、更早的静态补充及现代兼容文件分别记录，不把整站称为同一秒的快照。

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

## 完整备份下载

[2026-10-12 Release](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/tag/archive-20080512-processed-20261012) 提供最新恢复包的三份字节分卷、校验清单和历史来源包。三卷合计 **2,251,344,514 字节**，合并后 ZIP 的 SHA-256 为：

```text
66553fcd368ae5ee48dfb9f1b11897ac7fb3fd6a1983a0e303c2c088522c1c63
```

把 `.001`、`.002`、`.003` 和 `release-assets.json` 下载到同一目录，然后运行：

```sh
python tools/release_archive.py verify --manifest /path/to/release-assets.json
python tools/release_archive.py join --manifest /path/to/release-assets.json --output /path/to/WoW2008.zip
```

分卷是同一个 ZIP 的连续字节段，各卷不能单独解压。请解压到短目录，如 `D:\WoW2008`，然后运行其中的 `START_OFFLINE.cmd`。完整包含研究证据，解压约 5.19 GB；短目录解压和独立启动已验证。GitHub 自动生成的 Source code 压缩包仅覆盖 Git 主树，完整备份请下载上述 Release 资产。

## 工作记录与证据

- [工作回顾与方法](docs/project-history-and-methodology.md)：选版纠正、Thuum 对照、依赖发现、下载、验证、恢复与限制。
- [文档索引](docs/README.md)与[发布组织说明](docs/github-publication-20261012.md)。
- [基准复核](docs/reassessment-2008.md)、[2008 全量获取](docs/acquisition-2008.md)、[17 项缺口复核](docs/gap-review-20261011.md)。
- [离线重建](docs/offline-reconstruction-2008.md)、[官网资源恢复](docs/resource-recovery-2008.md)、[下载工具说明](tools/README.md)。
- [冻结构建来源清单](offline/build-manifest.json)、[最终缺口](research/final-gap-closure-20261012/final-build/README.md)、[完整浏览验收](research/offline-2008/full-recovery/round-108-8304-full-browser-validation.json)。
- [完整包验收](artifacts/offline-20261012-root-final-acceptance.json)与[短目录独立启动验收](artifacts/offline-20261012-recovery-portability-shortpath-check.json)。

早期 2010-12-03 候选虽然可以保存实体，但实际回放出现 XML 解析错误，已撤回其“最晚可用”结论。历史来源包保持不变，供比对；本项目重建基准是用户确认的 2008-05-12。

本站文字、美术及其他原始素材的权利归 Blizzard Entertainment 等原权利人所有。本仓库的保存与兼容修改不改变原权利归属，详见 [NOTICE](NOTICE.md)。
