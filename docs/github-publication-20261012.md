# GitHub 发布记录：2026-10-12

项目显示名称：WOW Encyclopedia Deployable Archive。仓库路径：`vvcchh0/WOW-Encyclopedia-Deployable-Archive`。归档基准为 **2008-05-12 21:00:44 UTC / 20080512210044**，处理日期为 **2026-10-12**。

## 发布边界与理由

Git 主树包含冻结的 `offline/site/`、`offline/build-manifest.json`、兼容支持、启动器、源码、测试、工作回顾和关键验收报告。克隆后可直接用 Python 标准库启动，不依赖本机原始下载目录。构建来源清单和部署字节保持不变；Git 属性关闭换行转换，以免破坏冻结摘要。

完整恢复 ZIP 长度为 2,251,344,514 字节，SHA-256 为 `66553fcd368ae5ee48dfb9f1b11897ac7fb3fd6a1983a0e303c2c088522c1c63`。它通过 Release 发布为三个连续字节分卷，保留逐卷与整体摘要；不在 Git 对象库中存放大 ZIP。分卷与原 ZIP 的整体流式校验通过，不为验证再生成一份完整 ZIP。清单见 [`release-assets.json`](../artifacts/github-release-20261012/release-assets.json)。

恢复包提供可浏览镜像、恢复期来源和研究证据。最初百科采集的原始批次另保存在 `WOW_Encyclopedia_20080512_full_source.zip`；历史样本、17 项复核、首版镜像及被否定为浏览基准的 2010 来源包一并保留在 Release，名称与内容不变。它们记录不同阶段，不应替换为“当前最新完整官网”。

## 验证

- 冻结构建：8,304 路由、917 文档；清单 SHA-256 `397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459`。
- 917/917 完整浏览检查；407 个最后批次图片 URL 与剩余 3,358 个缺口互斥。
- 完整 ZIP CRC、成员 SHA、短路径全新解压和独立启动均有保留报告。
- 发布前检查文件规模、磁盘预算、凭据和本机私有资料；仅白名单文件进入 Git。
- 新增分卷工具的 4 项验证覆盖正常合并、损坏分卷、覆盖拒绝和路径逃逸。
- Git 提交后另做仅含提交文件的独立启动检查，结果和 GitHub 上传核对见相邻发布证据。

GitHub 自动 Source code 包仅代表 Git 主树。历史文档可能引用完整包内的证据路径。保存原始报告及失败记录，回顾文档负责说明更正；没有改写旧 ZIP 来制造一致的历史。

实际仓库、提交、Release 与上传资产核对完成后，追加机器可读发布回执，不在准备阶段虚构成功。

## Git 主树复核（2026-10-13）

首次推送因初步卫生扫描未覆盖 HTML/CSS/JS 和二进制内容而被自动审批拒绝，实际未执行。随后对固定提交的 8,408 个受跟踪文件、652,421,785 字节完成全字节扫描，零跳过、零读取错误；5 处字面量候选经复核为游戏代币提示文字与固定 Cookie 能力探针，没有未解决的凭据发现。新的完整扫描覆盖并替代初步报告对 Git 主树的内容扫描边界。

仅含 Git 文件的全新克隆对 8,304 个部署文件逐项验证 SHA/长度/路径全部通过，首页、百科、Elune、GameGuide、Media、Current News、JS 共 7 个 HTTP 检查通过，所有请求均为 loopback，且无原始 mirror/backups 目录依赖。自己的临时服务已停止，验证克隆已清理。见[主代理验收](../research/github-publication-20261012/git-root-acceptance.json)、[完整内容扫描](../research/github-publication-20261012/full-tree-hygiene.md)及[独立启动报告](../research/github-publication-20261012/git-checkout-smoke/smoke-report.md)。原定处理日期仍记为 2026-10-12，跨日发布验收的实际日期另列。
