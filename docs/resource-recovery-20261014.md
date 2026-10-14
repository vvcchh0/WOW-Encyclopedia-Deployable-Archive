# 本地资源补充（2026-10-14）

已完成本地首批整合与验证，未更新线上部署。归档基准仍为 2008-05-12 21:00:44 UTC。

19 张既有布局图片已接入本地浏览树，修复了 67 处图片及 CSS 背景占位。50 个玩家截图图库的目录拼接已修正；图库原图与配套缩略图仍有缺口，本轮没有取得新的完整图片对。

## 本轮处理范围

- 修复图库 `addshots` 目录被静态导出误写成缺失页的问题。
- 复核并接入上一轮取得的 19 张布局图片。
- 从 Karazhan 图库开始查询、获取原图和配套缩略图，记录每个实体的实际捕获时间。
- 增加独立图片补充层，构建时将验收通过的图片接入路由和来源记录。

原始 `offline/site`、`offline/build-manifest.json` 和历史来源包继续保留；图片补充层不覆盖这些文件。查询失败与没有捕获分别记录，缺失素材仍显示本地占位。

## 获取与整合方法

图库原图并没有全部出现在 HTML 属性里。历史脚本通过目录、`ss` 前缀和编号生成文件名，再将 `.jpg` 替换为 `-thumb.jpg` 获取缩略图。因此除页面链接外，需要按脚本生成规则建立实体清单。此前[图库盘点](../research/github-pages-20261013/gallery-inspection-20261013.md)列出了 50 个图库、1,684 个截图位置。

本轮先查询一个图库目录，只有完整索引才能用于捕获选择；分页或传输失败的结果不能作为空索引。资源优先选择基准之前最近的 2008 捕获。实体下载后比对索引摘要、实际回放日期、图片类型和解码结果，再进入图片补充清单。原始响应头和下载正文保留在本地研究目录。

浏览版导出增加可重复参数 `--image-source-map PATH`。它读取已验收图片的来源清单，将原始图片字节加入具体路由；图库目录本身只用于拼接，不据此假定所有图片都存在。历史业务表单继续使用静态展示。

## 空间安排

开始时工作区含 `.git` 占用 13,209,417,592 字节，D 盘剩余约 46.1 GB。新构建仍受 14,000,000,000 字节工作区上限和 D 盘保留空间约束，预算计算已包含 `.git`。

旧 `.scratch/pages-preview-final` 的 8,399 个文件与保留的部署提交 `9ee94f1bbcaf3ec819b65b7dcfb4128e3819d443` 全部一致。核验后清理这份重复生成目录，回收 555,433,910 字节；需要时可用 `git archive 9ee94f1bbcaf3ec819b65b7dcfb4128e3819d443` 导出恢复。当前已验证浏览版 `.scratch/pages-security-20261014-ready` 保留。

## 本地入口与验收

本地浏览树为 `.scratch/pages-resources-20261014`，包含冻结清单的 8,304 条记录和 19 张补充图片。首次验收发现 17 处 CSS 背景仍使用旧占位，修复外部样式表和页面内样式的转换后完整重建，最终 67 处占位均已恢复。

验收结果：

- 43 项镜像与导出测试通过。
- 50 个图库的目录全部与来源页对应。
- Chrome 实际检查 3 个代表图库的目录和分页、19 张图片的加载，均通过。
- 39 项浏览器回归检查通过，历史业务表单仍为静态展示，搜索与菜单正常。
- 补充图片与下载原件逐字节一致；冻结清单未改变。

[主代理验收](../research/resource-integration-20261014/root-acceptance.json)、[图片与图库浏览检查](../research/resource-integration-20261014/browser-validation.json)、[浏览器回归](../research/resource-integration-20261014/browser-security-validation.json)和[19 张图片复核](../research/resource-integration-20261014/accepted-image-audit.md)保存了结果。

维护者本地重新构建与启动：

```powershell
python tools/export_github_pages.py --output .scratch/pages-resources-new --image-source-map research/resource-resume-20261013/round002/entity-source-map.json --image-source-map research/resource-resume-20261013/round003/entity-source-map.json
python tools/serve_pages_preview.py --site .scratch/pages-resources-new --port 8766
```

上述补充清单及原始下载文件需存在于本地研究目录。构建拒绝覆盖现有输出；本地入口为 `http://127.0.0.1:8766/WOW-Encyclopedia-Deployable-Archive/`。

## 图库获取结果与后续缺口

| 查询范围 | 完整索引结果 | 动态图库原图/缩略图 |
| --- | --- | --- |
| Karazhan 目录，2008 全年 | 20 行，其中 15 行对应 3 个嵌套预览路径，其余为目录 404 | 无直接实体记录 |
| Karazhan 目录，2007 全年 | 0 行 | 未找到 |
| Fishing 目录，2008 全年 | 63 行，包含相邻攻略资源及嵌套预览 | `/fishing/ss/ssN.jpg` 和配套缩略图未找到 |

Karazhan 实际取得 5 个回放记录，按路径和内容去重后为 3 张预览图，捕获时间晚于基准约 26–82 分钟，单独留存在本地研究目录，没有加入本轮基准图片补充层。一项 curl 写出失败未取得响应头或正文，记为本地写入失败，不作为 Archive 无资源的证据。详情见[首批摘要](../research/gallery-recovery-20261014/karazhan/sanitized-summary.md)。

Fishing 的少量 exact 回退也没有找到前几张图库图片；未完成的查询保留为未完成，详情见[目录查询续批](../research/gallery-recovery-20261014/discovery-002/sanitized-summary.md)。这些结果只说明上述查询范围内的缺口，尚未完成其余分区或更广年份、其他官方区域站点的资源调查。

后续应先扩大有证据支持的捕获与官方站点范围，取得真正的图库实体，再接入同一补充层；修正目录不会自动补出原图。

本轮工具：

- `tools/export_github_pages.py`：读取冻结镜像与图片补充清单，生成新浏览树。
- `tools/serve_pages_preview.py`：在 `127.0.0.1` 下按项目路径提供本地浏览。
- `tools/validate_gallery_resources.js`：验证目录、分页、已恢复图片解码与图库原图/缩略图的实际显示。
- `tools/validate_resource_overlay.py`：验证全部图库目录、补充图片字节及剩余占位引用。

本轮完成时工作区含 `.git` 约 13.22 GB，D 盘剩余约 45.87 GB。所有下载批次已结束并保存状态；本地预览服务独立运行。

Search Console 复核另见[复核准备](search-console-review-20261014.md)。当前没有取得所有权验证或正式安全问题报告，也没有提交复核。
