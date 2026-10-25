# GitHub 发布整理（2026-10-25）

本次整理既有 Release 和部署记录，并改为阶段成果发布完整离线包。网页与离线内容保持 v61。

## Release

| 项目 | 整理前 | 整理后 |
| --- | ---: | ---: |
| Release | 13 | 4 |
| 附件 | 42 | 12 |
| 附件合计 | 7,025,053,863 字节 | 2,220,937,282 字节 |

远端附件减少 4,804,116,581 字节，约 4.80 GB。保留的四个阶段为 v24、v38、v52 和 v61，内容和入口见[版本索引](release-history.md)。

撤下的九个中间版本，其三十个附件均已核对长度与 GitHub SHA-256。完整 ZIP 和校验文件继续保存在本地 `artifacts/`；各版 NOTICE、早期说明附件、原 Release 元数据和发布说明保存至本地 `research/github-publication-cleanup-20261025/release-backups/`。备份核对记录同时保存实际本地路径和摘要。

全部十三份发布说明和附件摘要已保存为[历史文档](release-history.md)。旧下载入口在维护中的工程文档里已改为对应历史说明；原始验收 JSON 继续记录当时的 URL 和结果。Git 标签保留，可以查看对应源码。

## Pages 与 Actions

部署列表从 41 条整理为 3 条，保留 v61、v59、v57 三个已完成检查点：

| 版本 | 部署记录 | 状态 | 提交 |
| --- | ---: | --- | --- |
| v61（当前） | 7298869345 | 成功／当前 | `8b9b28bf97a5c86116492fe84c824acb9805d7de` |
| v59 | 7296681807 | 失效／回退检查点 | `abd68d9947d6685c25d316301906dd8fab45209f` |
| v57 | 7276833416 | 失效／回退检查点 | `70cfe4cc4def1627bacdb970c81d00c1dc7572a2` |

清理前保存了全部部署状态和工作流链接。旧记录中仍标为成功的部署先设为失效，再删除记录；当前部署、`gh-pages` 分支与站点文件不变。Git 提交和工作流运行日志继续保留。

Actions 当时只有两份 Pages 构建产物，合计 1,168,215,190 字节，分别对应 v61 和 v59，均设置为约一天到期，继续沿用。仓库的日志保留设置为 90 天，本次未调整。删除部署记录主要整理列表，不会减小发布站点或 Git 历史。

## 今后的发布方式

小修复验收后提交并按需更新 Pages；完成可描述的栏目、交互或来源恢复成果后，才制作和发布完整包。README 指向最新阶段包，中间进度写入 CHANGELOG。具体规则见[发布策略](publication-policy.md)，并写入项目 `AGENTS.md`。

## 本地恢复

被撤下的 Release 可从本地 `release-backups/<tag>/release.json`、`notes.md` 和备份核对记录重新创建；ZIP 复用 `artifacts/` 中的原文件，小附件复用备份目录。创建时使用保留的原标签，再上传已核对附件。重新发布会得到新的 GitHub Release ID 和日期。

旧部署需要回退时，使用对应已验收的 Git 提交重新部署；无需重写 Git 历史。此次仅整理发布元数据与远端中间包，本地历史文件继续保留。

最终数量、标签保留、当前 Pages 提交及公开入口核对结果见[验收摘要](evidence/github-publication-cleanup-20261025.json)。

参考：[Release API](https://docs.github.com/en/rest/releases/releases)、[部署 API](https://docs.github.com/en/rest/deployments/deployments)、[Actions 产物管理](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/remove-workflow-artifacts)。
