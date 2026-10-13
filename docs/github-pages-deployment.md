# GitHub Pages 部署与本地补齐（2026-10-13）

本轮按用户要求，为现有公开仓库创建可直接浏览的 GitHub Pages 站点，然后在本地恢复资源补齐。归档基准仍为 2008-05-12 21:00:44 UTC，资源处理日期 2026-10-12，部署适配日期 2026-10-13。

## 静态派生层

输入是冻结的 `offline/site/` 与 `offline/build-manifest.json`，后者 SHA-256 为 `397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459`。另生成 `.scratch/pages-preview/`，不改原始下载、历史 ZIP 或冻结镜像。

GitHub Pages 不运行 Python 路由服务器，项目站点还有 `/WOW-Encyclopedia-Deployable-Archive/` 前缀。导出器将保存为 `.xml`、但实际 MIME 为 HTML 的页面另存为 `.xml.html`，按记录的字符集转为 UTF-8，同时改写站内导航、CSS/JavaScript 路径、iframe 与菜单。真实 XML 数据文件保留 XML 类型，图像等二进制保持原字节。源 SHA、派生 SHA 和路径映射另记来源清单。

根入口与目录别名单独生成静态跳转，缺失资源继续使用明确占位；查询参数在客户端以 textContent 回显。搜索保留现有本地标题跳转，Toplist 缺失数据不伪造。静态适配不恢复账号、支付、Flash 或原站服务端功能。页面包含非官方历史教育保存声明，敏感表单禁用；只加载本站已保存资源。

旧脚本还会通过 `document.write`、`innerHTML`、图片属性和背景图表达式生成地址。派生副本在这些写入发生前同步查路由表；百科父词条图标按文件名定位，标题搜索直接使用静态目标，避免先访问旧 XML 地址再跳转。真实 XML/XSL 的网址查询分隔符做 XML 转义。19 个 XML/XSL 派生文件中有 18 个可解析；`new-hp/layout/layout.xsl` 的嵌套引号错误已存在于冻结源文件，继续列为保留限制。已经生成的 HTML 页面不依赖它运行。

## 发布方式

使用独立 `gh-pages` 分支及 Pages 的 branch/legacy 发布源。既有图片可复用 Git blob，主分支继续保留源码、部署工具、工作记录与关键证据，不把500MB派生目录再复制进主分支。

```sh
python tools/export_github_pages.py --output .scratch/pages-preview --base-path /WOW-Encyclopedia-Deployable-Archive/
python tools/publish_github_pages.py --site .scratch/pages-preview --branch gh-pages
```

第二条默认仅准备本地提交；显式 `--push` 才进行普通非 force 推送。临时 Git index 独立，主分支 index/checkout 不变，分支更新使用旧 SHA lease。Pages API 配置为 `build_type=legacy`、source branch `gh-pages`、path `/`。`.nojekyll` 保留下划线支持目录。

公开网址：<https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/>；[百科直接入口](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/info/encyclopedia/index.xml.html)。仓库 About 已设置同一网站地址。

## 2026-10-13 发布回执

- `gh-pages` 部署提交：`9ee94f1bbcaf3ec819b65b7dcfb4128e3819d443`；8,399 个发布文件，共 555,433,910 字节。
- GitHub Pages 构建 `1281533117` 于 `2026-10-13 13:50:53 UTC` 成功；source 为 `gh-pages` 根目录，HTTPS 已启用。
- 最终普通静态浏览器验收：11 个代表路由、4 个 XML 探针、4 项交互、2 张截图；无外部请求、路径越界、页面脚本错误或意外资源失败。旧 XML 入口的预期 HTTP 404 随后由静态 404 页正确映射到 `.xml.html`。
- 线上另检查 6 个页面/脚本/图片对象，均 HTTP 200，响应 MIME 正确，SHA-256 与发布实体一致。
- 不可变 Git tree 验收覆盖 8,304 个来源记录；8,395 个相同 Git blob 复用已完成的完整字节扫描，只对 4 个改动 blob 重扫。没有跳过字节或未决公开内容检查项。

证据：[部署回执](../research/github-pages-20261013/deployment-receipt.json)、[线上 HTTP/SHA 核验](../research/github-pages-20261013/online-http-verification.json)、[不可变发布树验收](../research/github-pages-20261013/root-pages-tree-acceptance.json)、[最终静态浏览器验收](../research/github-pages-20261013/browser-pages-qa-final-5/browser-validation.json)。Pages 的浏览器检查覆盖代表路由；此前 917/917 文档的全量浏览检查针对本地镜像服务器，二者分别记录。

## 验收与补齐边界

先用普通静态服务器验证真实的路径前缀、HTML/XML MIME、代表栏目、菜单、搜索和资源请求；不使用原 Python 后端替静态站兜底。发布前核对二进制原 SHA、派生来源清单、主分支未被替换、1GB发布尺寸、14GB工作区和D盘保留空间。发布后再检查GitHub部署状态和公开HTTP内容。

本地补齐从当前3,358条目标SSOT重新选出有界候选，先复用已有exact索引与失败证据，避免无新依据地重试。新的查询、实体、错误和日期补充继续分开保存；任何HTTP200错误HTML均不算图片，pre2008素材仍必须有完整exact2008全年空证明。新采集不自动覆盖已发布快照。

依据：[服务器职责盘点](../research/github-pages-20261013/server-contract-inventory.md)、[本地补齐初选](../research/resource-resume-20261013/inventory.md)、[GitHub Pages限额](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)、[GitHub Pages REST API](https://docs.github.com/en/rest/pages/pages)。
