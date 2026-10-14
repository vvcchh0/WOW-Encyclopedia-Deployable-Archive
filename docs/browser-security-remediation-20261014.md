# 浏览版安全修复（2026-10-14）

本轮更新 GitHub Pages 的可浏览派生版本：修复 WLK 截图分页的参数执行，历史业务表单改为静态展示，并准备 Search Console 复核材料。归档基准仍为 2008-05-12 21:00:44 UTC。`offline/site/`、来源清单、原始下载和历史压缩包均保留。

## 改动与理由

- **分页参数。** 原脚本把网址中的 `s` 直接交给 `eval`。导出器现在仅接受单个十进制正整数，解码一次后验证，再按实际页数约束；缺省、重复、表达式、负数、小数、指数、溢出或越界值回退到第一页。同步所有分页变量，删除该脚本中的两处 `eval`。
- **历史业务表单。** 七个页面中的登录、VISA、投稿、比赛上传、报名、兑换和反馈控件转成静态文字或图片，移除业务 form、输入、文件选择、自动填充及提交语义。提示为 “Historical form — display only. Submissions are unavailable.”，不依赖 JavaScript 取消事件。
- **保留浏览功能。** 搜索、语言选择及八条已核实的奖励/任务筛选路由继续工作。匿名筛选表单只有在路由、控件和处理函数都符合已确认用途时才保留；带业务提交属性的同类表单仍静态化。旧 HTML 的嵌套、表单外控件和 `form=` 关联由带位置的标签解析处理，避免截断页面布局。
- **iframe 备用内容。** 本机 Python 3.12.14 的 HTMLParser 将 iframe 内容视为原始文本；上一版发布结果中的这些地址已经本地化。本轮增加显式转换，保留旧广告链接和图片的离线占位行为，避免依赖隐含的解析行为。

没有全站删除 `unsafe-eval`：百科级联菜单仍有兼容依赖。本轮定向消除已确认的分页输入执行，不重写其他旧脚本。历史业务页面仍可作为文献浏览，原始文件可供对照。

实现：[导出器](../tools/export_github_pages.py)、[回归测试](../tests/test_github_pages_export.py)、[浏览器验收工具](../tools/validate_browser_security.js)。源码提交：[139f41f](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/commit/139f41f) 和 [94433b2](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/commit/94433b2)。

## 验收

| 检查 | 实际结果 |
| --- | --- |
| 单元测试 | 6/6 通过，包括外部控件关联、静态展示、保留筛选、拒绝未知 POST、分页转换和 iframe 备用地址 |
| 语法与补丁检查 | Python 编译、Node 语法、git diff whitespace 检查通过 |
| 分页浏览 | 17 类网址输入通过；测试表达式不执行，正常第 1、2、5 页的缩略图数量与前后页链接正确 |
| 业务页面 | 8 个代表页面 × JavaScript 开/关，共 16 项通过；无可提交业务 form、业务编辑控件或直接提交事件，无 POST 尝试 |
| 浏览兼容 | 6 项通过：百科菜单及 Elune 搜索、职业与等级奖励切换、Argent 任务切换、iframe 备用地址、静态 VISA 页面截图 |
| 来源保留 | 导出逐项核对 8,304 个冻结实体；来源清单与受跟踪输入无改动 |
| 发布树 | 8,399 个文件；最终远程核对见下方部署记录 |

浏览器检查使用新的本地 Chrome 上下文和普通静态服务器，拒绝外部请求、拦截 POST；没有读取个人浏览器资料或向生产服务提交测试数据。该检查验证页面行为，浏览器信誉状态另行记录。

```sh
python -m unittest discover -s tests -p test_github_pages_export.py
python -m py_compile tools/export_github_pages.py tests/test_github_pages_export.py
node --check tools/validate_browser_security.js
python tools/export_github_pages.py --output .scratch/pages-security-20261014-ready
node tools/validate_browser_security.js --site .scratch/pages-security-20261014-ready --output .scratch/browser-security-validation.json
```

最后一条需要可用的 Playwright 与 Chrome，可用 `--playwright-module`、`--browser` 指定本机安装位置。完整本地验收记录另保存在 Codex Security 的本项目修复证据集中。

## 部署记录

- 最终源码：`94433b2`。
- Pages 提交：[97f7cf66255593c3b936d7957abcd134674de048](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/commit/97f7cf66255593c3b936d7957abcd134674de048)。
- Pages 构建：`built`，2026-10-14 10:03:30（Asia/Shanghai），HTTPS 已启用。
- 远程内容核对：2026-10-14 10:04:13（Asia/Shanghai），13/13 个对象 HTTP 200，字节与最终本地导出一致，涵盖分页脚本、七个业务页面、首页、百科及 iframe 备用内容。
- 工作区与磁盘预算：14 GB 工作区限制和 D 盘至少 10 GB 保留阈值均通过导出检查；中间候选在最终验收后清理。

## 复核与剩余工作

[Search Console 复核准备](search-console-review-20261014.md)包含所有权验证步骤、报告信息表和英文说明。用户尚未验证属性，本轮只准备材料，没有提交复核或添加验证文件。10:04 的 Google 公共查询仍返回此前的风险状态，尚不能把代码修复等同于信誉标记已清除。

本机 Chrome 曾提示钓鱼风险，用户补充手机 Chrome 正常、分享访问者未反馈拦截、本机 Edge 也提示被举报不安全。此前 Google 公共报告将本账号 Pages 主机名和两个项目路径标为不安全；正式问题类别、样本网址及首次检测日期仍需所有者报告确认。Edge 的 SmartScreen 判定应另行处理，刷新 DNS 缓存不会移除这些服务的风险记录。

本轮没有审查或修改另一个 Gitube 项目，没有重新打包旧离线包，也没有启动图库专项恢复。它们各自的进度继续按原记录保存。
