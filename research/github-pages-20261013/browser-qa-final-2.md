# GitHub Pages preview QA: final static tree

本次验收使用普通静态挂载器 `browser-static-server.py`，没有启动
`offline_mirror.py`，也没有对外网发请求。服务器只把
`/WOW-Encyclopedia-Deployable-Archive/` 前缀剥掉后映射到
`.scratch/pages-preview-final` 的真实文件；前缀外请求返回普通 404。

脚本和输入：

* [browser-pages-qa.js](browser-pages-qa.js)，SHA-256 为
  `eebbdeda0264e99fa83109c8b7d931d4efbdad881a9d50199fce5fa60142612f`。
* route-map SHA-256：
  `7db5b2e99320d8d038e8aa3cdc7593f6084cefd60ccf192f15d5bacdcdb4c485`。
* `offline/build-manifest.json` SHA-256：
  `397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459`。
* 原始结果：[browser-validation.json](browser-pages-qa-final-2/browser-validation.json)。

脚本访问了 7 个代表路由，并另外按 manifest `kind=xml` 访问了 4 个真实 XML
记录。百科 XML 页面使用导出后的 `.xml.html` 路径；XML 探针仍访问原始
`.xml` 文件并接受 `application/xml` 或 `text/xml`。首页根别名先经过真实静态
meta refresh，再截取 canonical `index.xml.html`；截图为
[homepage.png](browser-pages-qa-final-2/homepage.png) 和
[encyclopedia.png](browser-pages-qa-final-2/encyclopedia.png)。

成功的行为检查包括菜单开闭、Factions 展开、Elune 标题搜索、全站搜索落到
项目内 `__offline/uncollected/index.html`、缺失图片 16×16 自然尺寸，以及表单
作用域检查。没有外部请求、没有 page error，旧的未转换百科 XML 入口保持 404。

结果摘要：11 个页面、4 个 XML 探针、4 个交互检查、2 张截图；0 个外网请求、
0 个 page error、0 个 harness 自身断言失败。预览仍真实暴露 3 个同源但逃出
项目 prefix 的旧资源链接和 6 个资源 404（包括 `ss1340-thumb.jpg`、Elune
图标、两个共享 subnav 图标）；因此本轮 `accepted=false`。这些是静态树/页面
资源缺口证据，QA 没有把它们改写成占位成功。控制台另记录 9 项与这些资源及
历史 `status.xml` XML 解析错误相关的真实浏览器消息。

本地服务器在报告写入后已停止；运行期间未修改 exporter、publisher、冻结站点
或原始证据。
