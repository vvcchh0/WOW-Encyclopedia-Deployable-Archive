# 关联站点素材与第二批本地恢复

本轮取得欧服官网的 2 份历史页面和 14 张图片，并将欧服图片及此前暂存的 3 张 Karazhan 预览图接入新的本地浏览树。线上部署未更新。

## 已保存的站点范围

| 来源 | 已有材料 | 本轮进展 |
| --- | --- | --- |
| 美服主站 `worldofwarcraft.com` | 官网与百科页面、共享资源；上一轮接入 19 张布局图片 | 接入 3 张已有的 Karazhan 晚期预览图 |
| 旧官方论坛 `forums.worldofwarcraft.com` | 1 个公开规则页面及 105 个配套资源 | 本轮没有扩展讨论帖 |
| 欧服 `wow-europe.com`、`www.wow-europe.com` | 此前仅保留导航线索 | 保存 2 份页面、14 张图片，增加可浏览的素材目录 |
| 其他暴雪与官方区域站点 | 来源清单中记录了链接与候选路径 | 尚未形成可浏览的素材集合 |

[起始覆盖盘点](../research/related-sites-20261014/inventory/sanitized-summary.md)按本轮开始时的冻结镜像与 19 张补充图片统计。`supplements` 是来源记录，不能与 `files` 相加当作独立实体；页面链接和 CDX 记录也没有计作已下载文件。

## 欧服页面与图片

入口是 [2008-05-09 的欧服英文首页](https://web.archive.org/web/20080509092828/http://www.wow-europe.com/en/index.xml)，其中链接到 [2008-05-10 的 Screenshot of the Day 页面](https://web.archive.org/web/20080510105954/http://wow-europe.com/screenoftheday/screens.html)。截图页面显示 521 个位置，图片引用指向 `/screenoftheday/screenoftheday/`。

对该目录的有限日期查询取得完整一页、87 行 CDX 记录，其中 64 行为成功状态的 JPEG 捕获。选取 20 个图片实体后，14 个通过回放日期、HTTP 状态、图片格式、解码、摘要与长度核验：

- 4 张捕获于基准之前的 2008 年；
- 10 张捕获于 2007 年；
- 包含原图与缩略图，不将文件数称为完整截图数量。

初次 3 项遇到本地输出目录缺失造成的写入失败；另 3 项响应图片的摘要与所选 CDX 不一致，均未接入。页面直接引用的 `10805-10.jpg` 没有出现在本批完整索引中，仍保留为缺口。[欧服批次摘要](../research/related-sites-20261014/regional-gallery/sanitized-summary.md)记录了查询范围和结果。

这些欧服每日截图尚未建立与美服 Game Guide 分区图库的对应关系。美服图库原图和配套缩略图的缺口继续保留，不用同名区域站图片自动替换。

## 整合方法

欧服图片使用 `/_origins/<实际域名>/...` 保存本地路由；裸域与 `www` 分开记录。导出器修复了外站同路径误落到主站文件的问题。原图字节、来源网址和实际捕获时间均保留。

新增显式参数 `--supplement-image-source-map PATH` 接收已经复核的早期或晚期素材。原 `--image-source-map` 仍接收基准前的 2008 年主站图片。时间分类写入来源记录；素材目录使用可读的 UTC 日期。

本地素材目录为 `/__offline/related-images/index.html`，列出 14 张欧服图片及 3 张 Karazhan 预览图。欧服两份原始页面保存在本地研究目录；本轮提供图片素材目录，没有重建欧服整套导航和页面依赖。

本轮构建输入：

```powershell
python tools/export_github_pages.py --output .scratch/pages-resources-20261014-next --image-source-map research/resource-resume-20261013/round002/entity-source-map.json --image-source-map research/resource-resume-20261013/round003/entity-source-map.json --supplement-image-source-map research/related-sites-20261014/integration/regional-image-source-map.json --supplement-image-source-map research/related-sites-20261014/integration/karazhan-late-source-map.json
```

冻结镜像、来源清单和历史 ZIP 均未覆盖。新浏览树总共包含 19 张前次补充图片、14 张欧服图片及 3 张 Karazhan 图片；实际构建和浏览验收见本轮 `integration` 目录记录。

## 主站队列更正

Round004 从旧新闻图片队列下载并核验了 18 个有效回放。合并前与当前冻结镜像逐项比较，发现 18 个路径和内容已经存在，因此本批主站新增唯一资源为 **0**，没有覆盖或重复计入镜像。[逐项比对](../research/related-sites-20261014/integration/news-existing-route-check.json)保留了证据。

筛选旧队列时漏掉了当前路由检查，造成重复下载；已增加请求前的当前镜像过滤。首轮本地写入错误及停批指纹未稳定归类的偏离保留在 [Round004 最终记录](../research/resource-resume-20261014/round004/final-checkpoint.md)。后续批次应先以冻结 manifest 和最新补充层过滤旧候选，再选择未取得资源。

## 本地验收与获取约定

新浏览树的来源实体为冻结镜像 8,304 条，加上 36 张图片补充；图片补充层共 1,526,500 字节，关联素材目录登记 17 张图片。当前构建的导出记录为 8,435 条，另有导出证明文件；工作区测量值为 13,229,642,187 字节，仍低于既定磁盘预算。冻结 manifest 的摘要和原始图片字节未被改写。

已保存的验收记录显示：50 个图库目录通过路由检查，36 张补充图片通过实际加载检查，关联素材目录 17 张图片全部解码，浏览器回归 39 项通过；当前 Round004 的 29 项候选全部命中已有路由，剩余可请求项为 0。图库原图与缩略图的直接成对资源仍为 0，这项缺口没有被关联站点的每日截图素材掩盖。[整合验收](../research/related-sites-20261014/integration/root-acceptance.json)、[关联目录验收](../research/related-sites-20261014/integration/catalog-browser-validation.json)、[图库验收](../research/related-sites-20261014/integration/gallery-browser-validation.json)、[当前路由过滤](../research/related-sites-20261014/integration/current-route-filter.json)。

本地复核运行了 9 个来源路由、关联图片导出和候选过滤测试，以及 12 个既有导出与图片补充回归测试，共 21 项全部通过；候选过滤复核结果为输入 29、已有路由 29、剩余 0。测试没有发起网络请求。

下一批 Wayback 获取按每个候选先尝试 direct 连接；直连失败后才进入代理路径，并在批次证据中记录所用路径和失败原因。本约定用于后续获取流程，本轮已完成的历史批次不据此重新标记。

## 空间与后续

本节早先的 14GB 总量预算于 2026-10-14 后续会话中取消。当前导出器与新下载工具的工作区总量上限为可选参数，继续按 D 盘空闲空间预检，并保留至少 10GB（工具默认采用 10GiB 加缓冲）。原 `.scratch/pages-resources-20261014` 副本继续保留；曾计划的压缩后清理没有执行。

为新构建腾出空间，核对旧 `.scratch/pages-security-20261014-ready` 的 8,399 个文件与已保留的 Git 部署提交 `97f7cf6` 完全一致后，清理这份重复派生树，回收 555,402,887 字节。当前资源浏览树和原始下载继续保留；旧部署可用 `git archive 97f7cf66255593c3b936d7957abcd134674de048` 恢复。

后续优先检查其余官方区域站点的实际页面与资源目录，并从经过当前路由过滤的缺口队列继续获取。关联站点原始素材可以独立保存；只有来源与对应关系明确后，才考虑补入现有页面。
