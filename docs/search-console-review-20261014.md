# Google Search Console 复核材料（准备稿，2026-10-14）

> **状态：修复已部署；根站点的所有权验证文件已发布，待在 Search Console 点击验证；复核尚未提交。** 已填入本轮代码、测试与部署结果；方括号中的正式问题类型、检测日期和样本网址待 Search Console 报告补齐。

## 根站点所有权文件发布（2026-10-14）

用户在 Search Console 选择了 URL-prefix `https://vvcchh0.github.io/`，并提供 `D:\GithubIO\googled4e2187611b0fbea.html`。根地址此前返回 404，账号尚无用户站点仓库；本轮创建 [vvcchh0.github.io](https://github.com/vvcchh0/vvcchh0.github.io)，将文件原样放在 `main` 根目录并发布。文件网址为：

[https://vvcchh0.github.io/googled4e2187611b0fbea.html](https://vvcchh0.github.io/googled4e2187611b0fbea.html)

Pages 提交为 `e02544be5f01291319a4bdf352c2b7630e545658`，构建于 2026-10-14 16:19:58（Asia/Shanghai）完成。公网 direct 请求返回 HTTP 200，响应字节与用户提供的文件一致。[发布核对记录](../research/github-root-verification-20261014/publication.json)保存了结果。

接下来在 Search Console 点击“验证”，读取根属性的“安全问题”报告，再按报告范围补充本文的复核材料。发布文件不等于 Google 已确认所有权或完成安全复核；本轮未操作这两个提交。验证成功后仍保留该文件。Google 说明已验证父属性可用于自动验证其子属性，见[所有权验证说明](https://support.google.com/webmasters/answer/9008080)。

WOW 与 Gitube 项目的发布内容本轮没有更改。下文原先按项目分别准备的复核草稿继续保留，正式提交时以实际选中的属性及其报告为准。

## 范围与已知观察

项目保存的是非官方的 2008 Warcraft Encyclopedia 历史教育档案。归档基准是 `20080512210044`（2008-05-12 21:00:44 UTC），资源处理日为 2026-10-12，浏览器安全修复处理日为 2026-10-14（Asia/Shanghai）。本次拟复核的 URL-prefix 属性优先是：

1. `https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/`
2. `https://vvcchh0.github.io/Gitube/`（另一项目，**不在本次修复范围**，只为避免将两个项目混在一个报告中而记录）

2026-10-13 晚独立查询 Google 透明度报告的界面记录显示 `vvcchh0.github.io`、WOW 项目和本账号 Gitube 页面 处于 `unsafe/deceptive` 提示状态。对任意不存在路径观察到相同 API verdict，说明当时的观察可能按 hostname 或更大范围呈现；这不是“整个域名的每个 URL 都已确认有问题”的证明。上游 `Andy7016/Gitube` 显示 `No available data`，不作为认证或信誉结论。

分享给访问者的浏览未收到拦截反馈；手机 Chrome 正常打开，本机 Chrome 曾出现拦截；用户随后报告本机 Edge 也提示“被人举报不安全”。这些浏览器上下文不同，记录只保留为观察，不能写成所有设备都被拦截，也不能据此断定误报。

## 复核前步骤

1. **先确认报告对象。** 在 Search Console 中打开实际 owner 报告，记录 issue type、`first detected`、最近刷新时间和所有返回的 sample URLs。Google 明确说明报告中的 sample URLs 不是完整清单，复核对象应是属性报告所覆盖的全部问题；流程、测试和 Request review 规则见 [Search Console 安全问题报告与复核](https://support.google.com/webmasters/answer/9044101?hl=zh-Hans)。
2. **确认属性和权限。** 优先分别使用上面的两个 URL-prefix 属性。URL-prefix 可以包含项目路径；验证说明见 [URL-prefix 属性](https://support.google.com/webmasters/answer/10432366?hl=en)。`github.io` 的 DNS 不归本项目控制，因此不要把 Domain property 的 DNS 验证当作现成方案。若选择 HTML 文件验证，必须将 Google 给出的完整原样文件名和字节放在该 URL-prefix 的属性根，并在验证成功后保留它；规则见 [Google 网站所有权验证](https://support.google.com/webmasters/answer/9008080?hl=en)。
3. **核对已部署版本。** 本轮最终部署为 `97f7cf6`，Pages 于 2026-10-14 10:03:30（Asia/Shanghai）构建成功，13 个远程对象与最终本地导出一致。详细方法与结果见[修复记录](browser-security-remediation-20261014.md)。Gitube 的状态另记。
4. **核对报告列出的全部可复现范围。** 对 sample URL、入口页和代表性不存在路径分别记录 HTTP/浏览器结果、浏览器上下文和检查时间。报告没有足够信息时，应把“触发项目/原始 URL 未确定”作为事实保留，不猜测触发源。
5. **先 Test，再 Request review。** Google 的复核说明要求先解决报告问题并测试整个报告范围，再提交复核；提交时说明问题、采取的行动和结果。一次复核处于 pending 时不重复提交。复核提交时间、状态和 Google 回复要写回下表。

## 报告信息记录表

| 字段 | WOW Encyclopedia URL-prefix | Gitube URL-prefix（范围外） | 记录规则 |
| --- | --- | --- | --- |
| Search Console property | `https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/` | `https://vvcchh0.github.io/Gitube/` | `[待填：实际 property 名称及权限确认时间]` |
| Issue type / category | `[待填：报告原文]` | `[待填：若有独立报告]` | 原样抄录，勿用 `unsafe/deceptive` 替代正式 issue 名称 |
| First detected | `[待填：YYYY-MM-DD HH:mm 时区]` | `[待填]` | 以报告字段为准，不用本地观察日期替代 |
| Last refreshed | `[待填]` | `[待填]` | 保留报告显示的时区 |
| Sample URLs | `[待填：逐条列出全部返回样本；注明样本不完整]` | `[待填]` | 不写成全站 URL 清单 |
| Trigger project / original URL | `[待填：目前未确定]` | `[待填]` | 只有报告或证据确认后才能填具体值 |
| Ownership method | `[待填：URL-prefix + HTML file / 其他]` | `[待填]` | 记录验证 URL 和保留文件名 |
| Fix scope | WOW Pages exporter 的生成树 | 本次不修复 | 不把 Gitube 的状态并入 WOW 结论 |
| Final source commit | `94433b2e2e5d0dfdf07214ca252b4da9a0ae5df6` | `[待填：若另有]` | 以实际 review 对应的提交为准 |
| Final Pages deployment commit | `97f7cf66255593c3b936d7957abcd134674de048` | `[待填]` | 不填旧发布 `9ee94f1bbcaf3ec819b65b7dcfb4128e3819d443`，除非报告明确复核该版本 |
| Published URL check | `2026-10-14 10:04 Asia/Shanghai；13/13 HTTP 200，与本地一致；HTTPS 启用` | `[待填]` | 记录浏览器上下文 |
| Test result | `6 单元测试、39 本地 Chrome 检查通过；详见修复记录；网址检查工具待需要时补充` | `[待填]` | 本地与远程检查分别记录；可另补网址检查工具结果 |
| Request review | `[待填：提交时间、状态、review ID]` | `[待填]` | pending 期间不再次提交 |
| Google outcome | `[待填：原样回复]` | `[待填]` | 不自行解释为“信誉已恢复” |

## 英文 review body 草案

以下文字标为“完成报告核对后使用”。提交前必须把方括号替换为事实，并删除不适用的段落；先核对正式报告列出的全部问题；本地与线上测试已记录，必要时再用网址检查工具补充。

```text
This URL-prefix hosts an unofficial educational archive of the 2008 Warcraft Encyclopedia and related historical pages. It is not affiliated with Blizzard and does not provide account, payment, registration or submission services.

The Security Issues report identifies [EXACT ISSUE TYPE], first detected [FIRST DETECTED], with these sample URLs: [SAMPLE URLS].

On 14 October 2026 we deployed browser fixes in Pages commit 97f7cf66255593c3b936d7957abcd134674de048. We removed query-string evaluation from the Wrath screenshot pagination and replaced historical business forms with non-interactive text and images. Those pages no longer provide business data-entry, autofill, file upload or submission controls. Local archive search, menus and reward/quest filters remain available. We also preserved local placeholders for old advertisement URLs inside iframe fallback content.

Validation passed six unit tests and 39 local Chrome checks, including JavaScript-enabled and JavaScript-disabled contexts. Thirteen published objects returned HTTP 200 and matched the verified local export on 14 October 2026 at 10:04 Asia/Shanghai. Source changes are recorded in commits 139f41f and 94433b2 of https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive .

Please recrawl and review this URL-prefix after the fixes. This request covers https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/ .
```

## 待取得的正式报告信息

- 实际 issue type、`first detected`、刷新时间、返回的 sample URLs 及报告 property；
- owner 权限和 URL-prefix 验证结果（含验证方式和保留文件）；
- 已完成：源码、Pages 提交、构建/HTTPS 和线上对象对照，见上表；
- 已完成：本地与远程测试；网址检查工具结果可作为补充；
- 已完成：13 个远程对象对照；
- review 提交时间、review ID、pending 状态和最终 Google 回复。

取得所有权验证和正式报告后，核对问题类别与样本网址，再使用草稿提交复核。当前没有提交记录，Gitube 的检查与修复另行记录。

2026-10-14 10:04 的 Google 公共查询仍返回风险状态。本材料用于核对并申请复核，未取得 Google 的解除标记结果。

## Edge 与 DNS 排查记录

本机 Edge 的“已举报为不安全”提示与 Microsoft Defender SmartScreen 的警告类别一致，具体判定仍以警告页标识为准。SmartScreen 有独立的网址信誉判定；Google 复核通过不能代替 Microsoft 的复核。如果修复部署后 Edge 仍拦截，可按 [Microsoft 官方复核说明](https://learn.microsoft.com/en-us/troubleshoot/microsoft-edge/development/unexpected-block-warning)从警告页的 More information 进入报告入口，使用本文相同的修复与部署证据。本轮仅准备材料，没有提交 Microsoft 请求。

`ipconfig /flushdns` 清理的是 DNS 解析缓存，不会移除安全服务的风险记录。它适合排查旧地址或解析失败；当前有 Google 公共风险状态及两种浏览器的警告，优先完成内容修复和对应服务的复核。见 [Microsoft ipconfig 文档](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ipconfig)及 [Edge SmartScreen 工作方式](https://learn.microsoft.com/en-us/deployedge/microsoft-edge-security-smartscreen)。本轮未更改 DNS 或浏览器安全设置。
