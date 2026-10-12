# WOW Encyclopedia Deployable Archive

Archive baseline: **2008-05-12 21:00:44 UTC (20080512210044)**. Processing date: **2026-10-12**.

可浏览的早期魔兽世界官方百科及部分官网镜像：8,304 条路由、917 个文档，917/917 完整浏览验收通过。最后恢复的 407 个图片 URL 已核验；仍保留 3,358 个去重缺口，未宣称历史官网全部资源、Flash 与动态服务完整。

## 下载与启动

- 最新恢复包：下载同名 `.zip.001`、`.zip.002`、`.zip.003`，以及 `release-assets.json`、`SHA256SUMS.txt`、`release_archive.py`。
- 三卷是连续字节段，不能分别解压。执行：

```sh
python release_archive.py verify --manifest release-assets.json
python release_archive.py join --manifest release-assets.json --output WoW2008.zip
```

合并 ZIP 长度 2,251,344,514 字节，SHA-256：`66553fcd368ae5ee48dfb9f1b11897ac7fb3fd6a1983a0e303c2c088522c1c63`。

解压到短目录（如 `D:\WoW2008`），运行 `START_OFFLINE.cmd`，或 `python tools/offline_mirror.py serve`。仅运行镜像需要 Python 3 标准库。Git 仓库也包含直接启动所需文件。

## 历史资产

`20080512_full_source.zip` 保存最初百科来源批次；`sample_and_reassessment.zip`、`gap_review_20261011.zip`、`offline_20261011.zip` 是保留的阶段成果。`20101203_source.zip` 是曾候选的来源实体，实际回放有 XML 解析错误，已经撤回其浏览基准结论，不能将它当作最新可用镜像。历史包相邻的 SHA-256 文件保持原样。

工作回顾、具体方法、时间补充规则、原件与派生文件边界和验收依据见仓库 `docs/project-history-and-methodology.md` 与 `docs/github-publication-20261012.md`。原始素材权利保留给 Blizzard 等原权利人，第三方兼容组件保留自己的声明。
