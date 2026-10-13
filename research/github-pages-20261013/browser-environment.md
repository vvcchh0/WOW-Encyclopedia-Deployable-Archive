# GitHub Pages preview QA environment

本文件记录 GitHub Pages 静态预览的实际 QA 环境与一次已完成的本地验收。
正式输入为 `.scratch/pages-preview-final`；`.scratch/pages-preview` 仍可作为
后续导出覆盖目标，但不应与 final 树混用。

## 已确认的本机工具

* Node：`C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe`
* Playwright：`C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\playwright`
* Chrome：`C:\Program Files\Google\Chrome\Application\chrome.exe`
* 已用 `node --check` 验证新 harness 语法；Playwright `chromium` 模块可以加载。

既有可复用审计包括 `research/offline-2008/acceptance/browser-check.js`、
`research/offline-2008/full-recovery/browser-check.js` 和
`research/runtime-page-audit-round5/diagnose_pages.js`。它们默认连接
`offline_mirror.py` loopback 服务，不能直接作为 GitHub Pages 验收，因为
它们允许后端 alias、占位和自定义 MIME。

## 本次 harness

`browser-pages-qa.js` 只访问一个普通静态 HTTP server，默认地址为：

```text
http://127.0.0.1:8879/WOW-Encyclopedia-Deployable-Archive/
```

可通过 `PAGES_PREVIEW_BASE` 指定实际 project prefix，并通过
`PAGES_QA_OUTPUT` 指定截图和 JSON 输出目录。例如：

```powershell
$env:PAGES_PREVIEW_BASE = 'http://127.0.0.1:8879/WOW-Encyclopedia-Deployable-Archive/'
$env:PAGES_QA_OUTPUT = 'D:\WOW_Encyclopedia\research\github-pages-20261013\browser-pages-qa'
& 'C:\nvm4w\nodejs\node.exe' 'D:\WOW_Encyclopedia\research\github-pages-20261013\browser-pages-qa.js'
```

静态挂载器 `browser-static-server.py` 只剥离项目 prefix 后读取真实文件；它不使用
`offline_mirror.py` 的 route backend。项目内缺失文件会读取导出树的 `404.html`
并保留 HTTP 404，让页面中的 `pages_runtime.js` 执行真实的 Pages 404 修复；服务器
本身不做 source-route 重写或 MIME 动态适配。harness 会：

1. 按 `__offline/route-map.json` 打开首页、百科首页、Elune、GameGuide、Media、
   Current News 和一个 JS；百科源 `.xml` 页面使用导出后的 `.xml.html`；
2. 另从 `offline/build-manifest.json` 选择 4 个 `kind=xml` 记录，直接检查真实
   `.xml` 响应；接受 `application/xml` 与普通静态主机的 `text/xml` 注册差异；
3. 记录 HTTP 状态、Content-Type、DOM 根节点、标题、正文长度、菜单链接和
   broken images；
4. 阻断所有非 loopback 请求，并分别记录外部请求、同源但逃出 project
   prefix 的请求、响应错误、requestfailed、console/page error；
5. 在本地 HTML DOM 上测试菜单开闭、Factions 展开、Elune 标题搜索、全站搜索
   的 `__offline/uncollected` 落点、缺失图片自然尺寸与表单作用域；旧未转换
   XML 入口先记录真实 404，再验证 runtime 是否映射到 `.xml.html`；
6. 将结果写入 `browser-pages-qa-final-2/browser-validation.json`，截图也只写入
   该目录。

前一轮结果记录在 [browser-qa-final-2.md](browser-qa-final-2.md)；第三轮会在 B
交付修复后的最终树上另写独立目录，避免覆盖历史证据。本文件、
`browser-pages-qa.js` 与静态挂载器不改动导出器或站点。
