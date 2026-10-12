# 原版 Warcraft Encyclopedia 的 Wayback 备份方法

> 2026-10-10 更正：下方“本次选版依据”是此前获取批次的历史决定，已撤回其中关于 2010-12-03 正常可用的判断。正常回放复现了 XML 解析错误。当前以用户提供的 2008-05-12 为复核基准，详见 [复核报告](reassessment-2008.md)。摘要、原件保存及空间控制方法仍适用。

## 本次选版依据

入口原始地址为 `http://www.worldofwarcraft.com/info/encyclopedia/index.xml`。已验证的最晚原百科入口是 [2010-12-03 21:49:58 UTC](https://web.archive.org/web/20101203214958/http://www.worldofwarcraft.com/info/encyclopedia/index.xml)。对应原始响应 46,355 字节，SHA-1 的 Base32 值 `LAOJEXSW2ZM3K7RVJ2RPVOZB22HR5H7X` 与 CDX 一致。

2011 年抽查的入口捕获返回 301，目标是 Battle.net 游戏指南；跟随后的页面已改变用途。详细状态、请求和原始证据见 `research/inventory/inventory_report.md`、`inventory_report.json`。这些证据把有效入口和重定向过渡界定在已观察的捕获之间，不能推导出精确撤站日期。

2008 与 2010 首页的主要可见文字相同。两个时期的 `topic-list.js`、`cascade.js`、百科 `stylesheet.css` 逐字节相同；51 个数字词条 ID 无增删。2010 锚点具有完整的已知核心词条捕获，因此采用较晚版本，同时逐文件记录捕获时间。

## 发现与下载

1. 通过 CDX 查询入口的时间、原 URL、状态、摘要、MIME 和记录长度，再查询百科目录前缀。原始索引和请求参数落盘保存。本次未折叠前缀查询得到 2,220 行，未达到 10,000 行上限；若达到上限，应使用 resume-key 分页。`collapse=digest` 适合发现不同内容，未折叠索引用于判断较晚的重复捕获。
2. 同时检查真实页面正文、响应 MIME 与正常回放结果。原网址的 `.xml` 扩展名可能对应 XML 或已经由旧站生成的 XHTML/HTML；按存档响应原样保存。HTML 容错解析能接受的正文可能在 XML MIME 下失败，因此正文存在、摘要一致与正常浏览必须分别验收。普通回放页面还有 Wayback 工具栏及渲染层，保存实体采用实测的 `https://web.archive.org/web/<timestamp>id_/<original-url>`。
3. 从 `topic-list.js` 解析全部核心词条，静态分析 HTML、XSL、CSS、JavaScript 的资源引用。原站的词条标题和分类子项由脚本填充，空的 `h1` 标签需要结合正文、导航数据和摘要判断。远程 JavaScript 始终作为源文件保存。
4. 以 2010-12-03 为锚选择核心页面。百科静态资源可使用同一次抓取日内稍晚的捕获。共享资源按锚点请求，保存实际 `Memento-Datetime`、最终 URL 和时间漂移，检查错误页、文件类型及异常日期。较晚回放只作补充证据，优先使用锚点之前的有效实体；从已保存的菜单 iframe 进一步提取其 9 个字面脚本依赖。
5. 将响应实体按 SHA-256 去重并直接写入压缩 ZIP 分卷；`manifest.jsonl` 保留每个原 URL、请求日期、实际日期和对象位置。研究期间已获取的共享脚本、样式和 XSL 及其元数据一起收入最终包。

CDX 的 `length` 是索引中的存档记录长度；实体文件大小使用本次实际读取的字节数。

## 空间与恢复

任务目录预算为 14,000,000,000 字节，D 盘最少保留 10 GiB。下载器还为正在处理的对象和写入预留空间，每个请求有超时、尝试上限和批次截止时间。并行补充批次使用独立目录、8 MiB 单对象上限和 256 MiB 裕量。

运行方法、清单字段与 ZIP 追加时的崩溃限制见 `tools/README.md`。重跑前会校验已有对象及清单引用，然后跳过已验证的成功项。每个批次的完成摘要分别保存，避免后续批次覆盖前次验收记录。最终便携压缩包另做 CRC 与 SHA-256 校验。

## 产物与后续使用

- `research/core-plan.json`：首页与 51 个词条的来源、日期和 CDX 摘要。
- `research/encyclopedia-assets-plan.json`：百科自己的 54 张图片和 4 个脚本、样式文件。
- `research/dependencies/`：共享依赖的原始响应、响应元数据、引用来源和研究清单。
- `backups/20101203/`：核心及补充批次的压缩对象、URL 映射和错误记录。
- `research/validation/`：独立的正文、摘要和资源闭包验收。

当前阶段完成原始文件获取和来源保存。离线镜像重建可依据清单还原 URL 路径，再处理旧站的 XSL、脚本和链接；完整视觉还原需要单独的浏览器验收。

接口资料：[Internet Archive CDX API 原始文档](https://raw.githubusercontent.com/internetarchive/wayback/master/wayback-cdx-server/README.md)。本次使用的查询和网络错误均保留在研究目录，方便复核覆盖范围。
