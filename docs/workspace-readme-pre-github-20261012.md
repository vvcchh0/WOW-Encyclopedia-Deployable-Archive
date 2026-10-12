# Warcraft Encyclopedia 原始文件备份

用户确认的重建基准：[2008-05-12 21:00:44 UTC 的官方百科存档](https://web.archive.org/web/20080512210044/http://www.worldofwarcraft.com/info/encyclopedia/index.xml)。本轮全量获取覆盖首页、导航中全部 51 个词条，以及正文、样式、脚本和菜单可发现的静态依赖。取得情况、实际日期和未恢复缺口见 [2008 全量获取报告](docs/acquisition-2008.md)。

最新[官网与百科离线资源恢复包](artifacts/WOW_Encyclopedia_20080512_offline_recovery_20261012.zip)约2.25 GB，含8,304条路由、917个文档，917/917通过一次完整浏览验收。本轮最后407个图片URL已全部取得并验证；跨时间补充单列。仍有3,358个去重占位目标，不等同于全站原资源齐全，见[最终缺口审计](research/final-gap-closure-20261012/final-build/README.md)。

请将新包解压到短目录（例如`D:\WoW2008`），再运行`START_OFFLINE.cmd`，避免研究证据长文件名触发Windows 260字符路径限制。入口为[官网首页](http://127.0.0.1:8765/)和[百科](http://127.0.0.1:8765/info/encyclopedia/index.xml)；[解压与启动说明](artifacts/README-offline-recovery-20261012.md)、[ZIP校验报告](artifacts/offline-20261012-recovery-package-verification.json)及相邻`.sha256`保留完整验证依据。所有历史来源包及首版离线包保持不变。

新包的[短目录全新解压与独立启动验证](artifacts/offline-20261012-recovery-portability-shortpath-check.json)已通过；较深目录触发的Windows路径限制及修复过程也保留。最终验收见[交付记录](artifacts/offline-20261012-root-final-acceptance.json)，临时验证副本已清理，最终工作区约8.73 GB，D盘可用约21.57 GB。

已完成文件获取、来源归档与百科离线重建：52/52 核心页、437 个选用原件、335/335 图片完整解码通过。离线页面、分类、菜单、词条跳转与本地标题搜索已通过 Chrome 实际浏览检查。双击 [START_OFFLINE.cmd](START_OFFLINE.cmd)，访问 <http://127.0.0.1:8765/info/encyclopedia/index.xml>；启动与范围说明见 [离线镜像说明](offline/README.md)。

[17 项缺口复核](docs/gap-review-20261011.md) 将原来的 5 项未取得、8 项错误响应、4 项晚期文件更正为 **13 项已有错误响应、4 项晚期有效补充**：五项遗漏在旧批次已有错误实体，三项另取得精确 2008 CDX 错误摘要证据，没有新增有效 2008 原件。重建以缺失提示及兼容样式处理这些缺口，错误 HTML 不冒充图片。

用户指出 2010-12-03 回放报错后，正常回放检查已复现其 XML 解析错误。此前将 2010-12-03 称为“最晚有效入口”的结论撤回；已下载原件保留作为内容和历史证据，不能据此认定浏览器可用。

2010 批次的首页和导航中的全部 51 个词条已保存，逐页通过 CDX 摘要、SHA-256 和 ZIP CRC 校验。这些检查证明保存的实体与存档一致，不证明页面正常渲染。每个文件保留自己的实际捕获时间；Wayback 的入口时间不代表全站在同一秒完成抓取。

`mirror/` 与历史来源包保存原件；`offline/site/` 是独立改写的工作副本。来源校验与浏览可用性分别记录，不能相互替代。官网扩展已恢复首页和主要栏目，当前并不等同于完整魔兽官网。完整资源恢复过程见 [资源恢复记录](docs/resource-recovery-2008.md)；本轮固定的 2,032 项图片清单已经全部通过来源摘要和完整图像核验，见 [逐项核对清单](research/resource-recovery-2008/global-image-wave/wave002-completion-audit.json)。

历史 [首版离线便携包](artifacts/WOW_Encyclopedia_20080512_offline_20261011.zip) 包含百科、启动器和首批 14 个额外官网页面；解压后运行 `START_OFFLINE.cmd`。该首版发布时官网首页尚未恢复，其内容及哈希保持不变。首版获取证据见 [扩展首批报告](research/site-expansion-2008/acquisition-report.md)。后续恢复在独立工作副本和新的便携包中交付，不把占位响应算作原资源恢复。

## 阅读入口

- [离线镜像与官网扩展记录](docs/offline-reconstruction-2008.md)、[真实浏览器验收](research/offline-2008/acceptance/browser-validation.json) 和 [派生文件来源清单](offline/build-manifest.json)。
- [17 项缺口复核](docs/gap-review-20261011.md) 与 [复核覆盖清单](research/gap-review-20261011/reviewed-index-overlay.json)：当前分类、来源证明、实际用途与查询范围；原首轮索引保留历史状态。
- [2008 全量文件获取](docs/acquisition-2008.md)：范围、下载结果、日期与缺口，后续重建从这里开始。
- [2008 完整来源索引](research/acquisition-2008/integration/index.json) 与 [统计](research/acquisition-2008/integration/summary.json)。
- [2008 原 URL 文件树映射](mirror/20080512/url-map.json)：未修改原件的本地路径、MIME、实际日期及 SHA-256。
- [2008 基准与选版复核](docs/reassessment-2008.md)：正常回放、原件结构、样本下载和 Thuum 对照。
- [此前下载与验收报告](docs/acquisition-report.md)：2010 内容获取的覆盖范围、缺口、统计和限制，选版结论已撤回。
- [方法与选版依据](docs/archive-method.md)：CDX、原始回放、日期选择和空间控制。
- [此前 2010 来源索引](research/preservation-index.json) 与 [统计](research/preservation-summary.json)。
- [下载器说明](tools/README.md)：有限计划、断点恢复和压缩对象格式。

## 文件结构

`backups/20080512/` 保存本轮正文、依赖及补充批次的原始响应 ZIP、请求清单和有限批次结果。`research/acquisition-2008/` 保存选择依据、引用图、恢复研究与验收。`mirror/20080512/` 按原 URL 路径导出有效的基准资源；文件未经改写，跨年代补充及错误实体仍在来源包与索引中单独保留。`offline/site/` 另行处理本地链接、MIME 和旧脚本兼容性，浏览时不会自动抓取外部文件。

`backups/20101203/` 内的 `objects-*.zip` 保存未修改的响应实体，按 SHA-256 命名。相邻 `manifest.jsonl` 将原始 URL 和捕获日期映射到 ZIP 分卷及对象；共享素材和补充依赖位于子目录。下载成功与内容有效性分别记录，原站 404 页面也保留为证据。

`research/dependencies/raw/` 保存研究时已取得的共享 XSL、CSS、JavaScript 及响应元数据。`research/inventory/` 保存索引和选版证据，`research/baseline/` 保留用户提供的 2008 年基准文件，`research/validation/` 保存独立验收结果。

本轮 `samples/20080512/` 按原 URL 路径导出 24 个未修改的 2008 样本文件，`url-map.json` 保留 MIME、日期与摘要；它仍是样本，尚未完成离线网站重建。`backups/20080512-sample/` 保存本次下载 ZIP 和请求清单，`research/reassessment-2008/` 保存结构、资源比较、正常回放与较晚候选证据。

此前的 2010 便携包位于 `artifacts/`，附 SHA-256 校验文件，作为当次获取记录保持不变。包内旧版报告的可用性结论已由本目录中的复核说明更正；包内 `FILE_SHA256SUMS.txt` 与包外 `package-verification.json` 仍用于核对当次打包内容。

新的样本与复核包为 `artifacts/WOW_Encyclopedia_20080512_sample_and_reassessment.zip`，相邻 `.sha256` 与 `reassessment-package-verification.json` 记录本次打包验收。

全量来源包为 `artifacts/WOW_Encyclopedia_20080512_full_source.zip`，相邻 `.sha256` 与 `full-2008-package-verification.json` 记录打包验收；旧包保持不变。

已知缺口与跨年代补充必须依据报告处理；不要把返回 HTTP 200 的 HTML 错误页还原成图片，也不要把较晚的共享素材当成 2008 年原件。
