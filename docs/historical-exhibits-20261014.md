# 旧业务页面的历史展品改造

2026-10-14，用户要求继续本地资源补齐、分析连接故障，并把敏感信息索取措辞改为明确的历史展品。本记录承接[欺骗性网页专项分析](google-deceptive-archive-analysis-20261014.md)及[资源恢复记录](related-sites-recovery-20261014.md)。

## 改造范围

VISA 奖励入口及两个登录 URL 改为独立历史展品，说明 2008 年用途，以过去时介绍当年界面的字段；不再向访客发出登录或身份信息索取指令。旧 URL 与别名仍能访问对应展品。

办卡、报名、兑换、投稿、反馈与软件下载页采用定向的历史语境处理，保留文献正文及正常浏览功能。原始页面、图片和冻结来源清单继续保存；浏览派生层承担界面修改。

展品需要在桌面及 390px 视口的第一屏清楚说明年份、独立归档身份和旧服务状态。说明不依赖 JavaScript；历史业务没有可编辑或提交控件。搜索、百科菜单、奖励筛选与截图分页继续工作。

## 资源获取与连接诊断

后续请求继续采用 direct 优先、失败后代理，按小批次记录 DNS、连接、TLS、首字节、HTTP 和实际回放结果。诊断先区分本机连接失败、代理响应和归档端响应，再尝试进程内可逆调整；不更改系统 DNS、hosts、防火墙或浏览器保护。

工作区总量不再固定为 14GB，D 盘保留至少 10GB 安全空间。通过验证的图片以原字节作为来源独立保存，再决定整合；错误页及限流响应不计为图片。

## 验收记录

实现覆盖三个核心奖励/登录页面、相关旧地址别名、12 个业务与下载页面，以及全站三个账号菜单标签。核心页面改为独立展品；其余页面采用定向的历史说明，保留搜索、百科菜单、奖励筛选、任务切换和截图分页。

首次浏览器检查发现账号菜单前缀匹配、投稿页退休控件初始化，以及文档头部 BOM 导致 CSP 未采用的问题，均已修正。历史语句跨越标签时只替换文字片段；原始标签、链接目标和正文中的 BOM 保留。冻结来源不作修改。

最终导出、浏览器验收与发布结果将在下文补充。Search Console 的原始触发 URL 仍未知；本轮没有提交 Google 或 Microsoft 复核。

### 最终本地验收

- 32 项单元回归通过，覆盖历史展品、导出、图片覆盖及来源路由。
- 29 项历史展品检查通过，包含桌面、390px 手机视口、禁用 JavaScript、别名、跨页链接及账号菜单。页面脚本异常、非预期 CSP 错误、外部请求和业务提交均为 0。旧 SWF 的两次 CSP 阻止作为预期结果保留。
- 39 项既有浏览功能检查通过：分页 17、静态业务显示 16、搜索/菜单/筛选等浏览检查 6。
- 36 张覆盖图片的原字节不变，50 个图库目录正确，已接入图片对应的 67 处旧占位引用均已替换。图库原图与缩略图的完整配对仍为 0。
- 冻结来源清单不变。验收时 D 盘可用约 43.37 GB，高于空间保留阈值。

主代理复看了[桌面奖励入口](../research/historical-exhibits-20261014/browser/desktop-js-visa_reward_index_html.png)、[手机账号展品](../research/historical-exhibits-20261014/browser/mobile-js-visa_reward_wow_login_html.png)和[禁用脚本的身份展品](../research/historical-exhibits-20261014/browser/desktop-no-js-visa_reward_login_html.png)。身份及历史说明清晰，原按钮图片以带说明的非交互展品保存。

实际检查结果见[历史展品浏览检查](../research/historical-exhibits-20261014/browser/validation.json)、[原功能回归](../research/historical-exhibits-20261014/browser-security-validation.json)、[资源验收](../research/historical-exhibits-20261014/resource-validation.json)和[整合验收](../research/historical-exhibits-20261014/root-acceptance.json)。
