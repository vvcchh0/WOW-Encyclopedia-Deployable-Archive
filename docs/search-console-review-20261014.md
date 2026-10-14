# Google Search Console 复核材料（准备稿，2026-10-14）

> **状态：修复与根站点验证文件已部署；用户已提供安全问题报告，类别为“欺骗性网页”；复核尚未提交。** 正式报告未给出示例网址或首次检测日期。

## 根站点所有权文件发布（2026-10-14）

用户在 Search Console 选择了 URL-prefix `https://vvcchh0.github.io/`，并提供 `D:\GithubIO\googled4e2187611b0fbea.html`。根地址此前返回 404，账号尚无用户站点仓库；本轮创建 [vvcchh0.github.io](https://github.com/vvcchh0/vvcchh0.github.io)，将文件原样放在 `main` 根目录并发布。文件网址为：

[https://vvcchh0.github.io/googled4e2187611b0fbea.html](https://vvcchh0.github.io/googled4e2187611b0fbea.html)

Pages 提交为 `e02544be5f01291319a4bdf352c2b7630e545658`，构建于 2026-10-14 16:19:58（Asia/Shanghai）完成。公网 direct 请求返回 HTTP 200，响应字节与用户提供的文件一致。[发布核对记录](../research/github-root-verification-20261014/publication.json)保存了结果。

文件发布后，用户已提供根属性的“安全问题”报告，详见下节；所有权验证的具体操作时间未单独记录。本轮代理没有点击 Google 的验证或复核提交。该文件继续保留。Google 说明已验证父属性可用于自动验证其子属性，见[所有权验证说明](https://support.google.com/webmasters/answer/9008080)。

根验证文件发布阶段没有更改 WOW 与 Gitube 项目的内容。WOW 后续发布的历史展品改造见下节；Gitube 尚未在本轮检查。正式提交须以实际选中的属性及其报告范围为准。

## 历史展品改造已发布

源码 `c3cf6f9638c8ee6de6accc6ccc77af1b630839e7`，Pages `86dc069b4fa806388ac9a966f3d88880166d4fcd`。旧奖励与登录入口已改为明确的 2008 年历史展品；报名、兑换、投稿、软件下载页及三个账号菜单标签采用历史语境。旧业务没有可填写或提交控件，搜索和正常文献浏览保留。

32 项单元回归、29 项展品浏览检查和 39 项既有功能检查通过。展品检查覆盖桌面、390px 手机和禁用 JavaScript；意外脚本异常、非预期 CSP 错误、外部请求和提交请求为 0。2026-10-14 19:14:37 Asia/Shanghai 核对 18 个线上对象，均为 HTTP 200，字节与本地导出一致。详细证据见[改造与发布记录](historical-exhibits-20261014.md)。这些检查没有提供 Google 已解除标记的结果。

## 用户提供的正式报告（2026-10-14）

- 属性上下文：`https://vvcchh0.github.io/`。
- 检测到的问题数：1；类别原文：**欺骗性网页**。
- 示例网址：**不适用**。
- 首次检测日期、刷新时间：截图未提供。
- 状态：页面提供“申请审核”入口；本轮没有提交。

帮助说明将模仿可信实体的行为或外观、诱导用户泄露机密信息或下载软件列为社会工程情形。报告没有指出触发页面；不能据此把某个历史登录页认定为已定位的原因。[专项分析](google-deceptive-archive-analysis-20261014.md)核对 Google 官方规则和实际发布版的历史业务入口，再提出后续处理方案。

## 范围与已知观察

项目保存的是非官方的 2008 Warcraft Encyclopedia 历史教育档案。归档基准是 `20080512210044`（2008-05-12 21:00:44 UTC），首批资源处理日为 2026-10-12，浏览器安全修复处理日为 2026-10-14（Asia/Shanghai）。当前正式报告来自根属性；为定位问题，可另检查这些项目级 URL-prefix 属性：

1. `https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/`
2. `https://vvcchh0.github.io/Gitube/`（另一项目，**不在本次修复范围**，只为避免将两个项目混在一个报告中而记录）

2026-10-13 晚独立查询 Google 透明度报告的界面记录显示 `vvcchh0.github.io`、WOW 项目和本账号 Gitube 页面 处于 `unsafe/deceptive` 提示状态。对任意不存在路径观察到相同 API verdict，说明当时的观察可能按 hostname 或更大范围呈现；这不是“整个域名的每个 URL 都已确认有问题”的证明。上游 `Andy7016/Gitube` 显示 `No available data`，不作为认证或信誉结论。

分享给访问者的浏览未收到拦截反馈；手机 Chrome 正常打开，本机 Chrome 曾出现拦截；用户随后报告本机 Edge 也提示“被人举报不安全”。这些浏览器上下文不同，记录只保留为观察，不能写成所有设备都被拦截，也不能据此断定误报。

## 提交前仍需完成的范围核对

正式报告来自根属性 `https://vvcchh0.github.io/`，覆盖其下的项目路径。当前报告只有“欺骗性网页”1 项，示例网址“不适用”，原始触发 URL 未确定；首次检测日期及刷新时间未提供。不要猜测日期或把本轮修复写成已定位原始触发原因。

本轮检查和修复的是 WOW 项目，Gitube 未审计。新增项目级 URL-prefix 属性可帮助检查对应报告，但不会缩小已有根属性报告的范围。提交根属性复核前，应继续核对该属性覆盖的其他公开内容，并记录结果。Google 的处理步骤见[安全问题报告与复核](https://support.google.com/webmasters/answer/9044101?hl=zh-Hans)。

此前技术修复于 2026-10-14 10:03:30 Asia/Shanghai 发布为 Pages `97f7cf66255593c3b936d7957abcd134674de048`，10:04 完成 13 个对象对照。本节上方记录的是随后增加历史展品改造的最新发布，保留旧记录用于追溯。

| 项目 | 当前事实 |
| --- | --- |
| 报告属性 | `https://vvcchh0.github.io/` |
| 问题类型 | 欺骗性网页，1 项 |
| 示例网址 | 不适用 |
| 原始触发 URL | 未确定 |
| 首次检测 / 刷新日期 | 未提供 |
| 已检查修复范围 | WOW Encyclopedia 项目；Gitube 未审计 |
| WOW 源码提交 | `c3cf6f9638c8ee6de6accc6ccc77af1b630839e7` |
| WOW Pages 提交 | `86dc069b4fa806388ac9a966f3d88880166d4fcd` |
| 最新公网检查 | 2026-10-14 19:14:37 Asia/Shanghai；18/18 HTTP 200，与本地一致 |
| 本地验收 | 32 单元回归、29 展品检查、39 既有浏览检查通过 |
| 复核提交 | 未提交 |
| Google 结果 | 未取得解除标记结果 |

## 英文复核说明草案

以下内容记录已完成的 WOW 修复。根属性其他项目的核对完成后，再补充其结果并决定提交范围；不要把这段草稿当作根属性所有问题都已排除的声明。通过 Search Console 的“申请审核”提交；本轮代理没有点击提交。审核处于 pending 时不重复申请。

```text
The Security Issues report for https://vvcchh0.github.io/ shows one Deceptive pages issue and no example URLs. We have not identified the original triggering URL.

The WOW Encyclopedia project is an independent archive of 2008 Blizzard website material. On 14 October 2026 we replaced its old rewards and account-login pages with explicit historical exhibits. They describe the retired interfaces in the past tense and contain no editable identity, account or payment fields. Old registration, redemption, submission and software-download pages now explain their historical context. Original login artwork is presented only as captioned, non-interactive material. Local archive search, menus and browsing filters remain available.

We also removed query-string evaluation from the old screenshot pagination and retained static replacements for historical business forms. The latest Pages commit is 86dc069b4fa806388ac9a966f3d88880166d4fcd, from source commit c3cf6f9638c8ee6de6accc6ccc77af1b630839e7. Thirty-two unit tests, 29 exhibit checks and 39 existing browser checks passed. The exhibit checks included desktop, mobile and JavaScript-disabled browsing. Eighteen published objects returned HTTP 200 and matched the verified local export on 2026-10-14 19:14:37 Asia/Shanghai.

The completed work above covers https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/ .
[Before submitting for the root property, add the results of checks for other hosted projects and the final scope of this review request.]
```

复核提交时间、状态及 Google 原文回复待实际操作后记录。当前没有提交记录，也没有新的风险状态结论。2026-10-14 10:04 的公共查询风险状态仅作为当时观察保留。

## Edge 与 DNS 排查记录

本机 Edge 的“已举报为不安全”提示与 Microsoft Defender SmartScreen 的警告类别一致，具体判定仍以警告页标识为准。SmartScreen 有独立的网址信誉判定；Google 复核通过不能代替 Microsoft 的复核。如果修复部署后 Edge 仍拦截，可按 [Microsoft 官方复核说明](https://learn.microsoft.com/en-us/troubleshoot/microsoft-edge/development/unexpected-block-warning)从警告页的 More information 进入报告入口，使用本文相同的修复与部署证据。本轮仅准备材料，没有提交 Microsoft 请求。

`ipconfig /flushdns` 清理的是 DNS 解析缓存，不会移除安全服务的风险记录。它适合排查旧地址或解析失败；已有 Google 风险状态及两种浏览器警告的记录，优先完成内容修复和对应服务的复核。见 [Microsoft ipconfig 文档](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ipconfig)及 [Edge SmartScreen 工作方式](https://learn.microsoft.com/en-us/deployedge/microsoft-edge-security-smartscreen)。本轮未更改 DNS 或浏览器安全设置。
