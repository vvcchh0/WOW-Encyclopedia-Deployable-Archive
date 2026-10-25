# 发布与保留策略

2026-10-25 起，在线修复和完整离线包采用不同节奏。

## 网页更新

验收通过的页面、资源和交互修复正常提交到 `main`，并按需要更新 `gh-pages`。相关变化写入 CHANGELOG。连续的小修复可以合并部署，文档更新不触发网页重建。

GitHub 部署列表保留当前部署及最近两个已完成检查点。清理旧记录前，保存提交、状态和工作流链接；历史 Git 提交与标签仍用于追溯和回退。

## 完整离线包

仅在完成一项可明确描述的阶段成果时发布，例如补齐一个栏目、恢复一类交互、接入一批可靠的新来源，或修复影响离线使用的重大问题。运行时间达到预算、完成一个下载批次或部署编号增加，本身不要求发布完整包。

阶段发布前核对来源和新增资源，验证受影响的浏览行为，独立检查解压后的包内服务。每次提供 ZIP、SHA-256 校验文件和 NOTICE；README 默认链接最新阶段包。

保留最新完整包和少量具有不同阶段意义的版本。中间包可转为历史说明，清理前先核对维护者本地原附件与 GitHub 摘要，保存说明和附件元数据，并保留 Git 标签。保留清单见[版本索引](release-history.md)。不定时批量删除，不按每次小改动自动上传整包。

## 容量

当前 v61 站点为 717,469,401 字节。Pages 的发布站点上限为 1 GB；后续大音频、视频先评估放入离线包或独立附件的方式，再决定是否加入在线版。导出器继续检查发布大小。

Release 附件、Actions 构建产物与 Git 对象历史分别统计。删除部署记录不会减小站点文件或 Git 历史；本次不重写分支、不做 force push。Actions 的 Pages 产物当前约一天到期，继续沿用；工作流日志保留用于排错。

参考：[GitHub Pages 限制](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)、[Release 说明](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)、[Actions 产物保留](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/remove-workflow-artifacts)。
