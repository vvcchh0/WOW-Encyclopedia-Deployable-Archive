# Google“欺骗性网页”与 WOW 历史归档专项分析

记录日：2026-10-14（Asia/Shanghai）。范围是已发布 WOW 浏览派生层的身份、旧业务入口和软件下载语义；不审计 Gitube，不作全仓库漏洞扫描。本轮只读取和记录，没有改导出器、发布内容、Search Console 或 Safe Browsing 状态。

## 结论

**归档站仍可能被归类为欺骗性网页。** 所查 Google 官方规则没有列出 archive / education 豁免；归档目的和免责声明有助于说明身份，仍需看用户面对页面时会理解什么、被要求做什么。不能由“这是历史镜像”推出 Safe Browsing 必须放行，也不能由这次无样本报告推出旧登录页已经被 Google 确认为触发源。[G1][G2]

本站的技术处置有实质作用：七个业务页面的表单已静态化。本次直接取得的 20 个线上页面全部 HTTP 200，且字节与 Pages 提交 `97f7cf66255593c3b936d7957abcd134674de048` 一致。最应继续处理的是 **VISA 奖励入口 → 两个历史登录页**：入口仍显示两个可点击的大幅登录按钮，登录页仍使用当前时态索取账号密码或身份信息的措辞。静态控件降低收集风险，但视觉和文字还没有充分变成“正在查看一件历史展品”。这是有证据的优先整改判断，尚不是 Google 触发原因的鉴定。

推荐只在公开浏览派生层把这条业务链改成明确的历史展品：入口改为“查看 2008 年登录界面”，直接访问登录 URL 也先看到历史说明；原业务画面可作为有说明的静态展品保存。冻结原件、来源哈希、原始素材和离线历史包继续保留。

## 已知与未知

| 项目 | 当前证据 |
| --- | --- |
| 用户提供的正式报告 | 根 URL-prefix 属性 `https://vvcchh0.github.io/`；检测到 1 项；类别“欺骗性网页”；示例网址“不适用” |
| 报告未显示的字段 | 首次检测日期、样本 URL、原始触发 URL；均不补猜 |
| 报告解释 | 无样本不代表没有受影响页面；Google 可能无法生成样本。[G1] |
| 发布版 | `97f7cf6`，本次 20 页线上字节核对通过 |
| 本地源码 | 开始检查时 `a34b8c5`，包含未部署资源更新；不能用本地新构建冒充当前线上内容 |
| 既有验证 | 项目修复记录记载 6 个单元测试和 39 项本地 Chrome 检查通过；本轮没有重复运行它们 |
| 本轮验证 | 20 页直接 HTTP 读取、6 个新浏览器渲染场景、2 个等图片加载完成后的重点页面复查；没有提交业务数据 |
| 仍未知 | Google 检测的时间与页面、人工或自动触发路径、是否由另一项目引起、重新抓取/复核结果；不推断内部算法 |

报告类别来自用户截图转述，不来自本轮登录 Search Console。本轮未取得账户报告的更多字段。

## 官方规则及其适用边界

以下均于 2026-10-14 访问，来源是 Google 官方文档或官方表单。可机器核对的 URL、抓取标识、页面状态、摘要及本次页面检查保存在[来源账本](../research/google-deceptive-archive-20261014/source-ledger.json)。

| 来源 | 官方说明的要点 | 对本归档的判断 |
| --- | --- | --- |
| [G1：Search Console 安全问题报告](https://support.google.com/webmasters/answer/9044101?hl=en) | 欺骗性页包括冒充可信实体的行为/外观，或诱使用户交出敏感资料、下载软件；无样本也可能存在问题。修复整个报告范围、测试后再复核；pending 期间不要重复提交。 | “控件不能提交”是重要证据，但无法单独回答身份和行动暗示问题。 |
| [G2：Social engineering](https://developers.google.com/search/docs/monitor-debug/security/social-engineering) | 包括钓鱼、欺骗性内容、未充分标识的第三方服务；示例含假登录页。嵌入内容、广告或跳转也需检查。 | 旧品牌 shell、登录按钮、申请卡和安装提示值得定向检查；品牌素材本身不等于违规证据。 |
| G2 的第三方服务标识建议 | 强调每页说明运营方及与品牌方关系，并以“单独看该页能否理解身份”作为可用性尺度。 | 本站是独立归档，不能冒称代表 Blizzard 运营业务；借用这个可用性尺度是本报告的类比，不是 Google 专门针对归档的条款。 |
| [G3：Safe Browsing 错误警告反馈](https://safebrowsing.google.com/safebrowsing/report_error/?hl=en) | 官方提供合法页面被错误警告的反馈入口，当前表单接受 URL、补充说明并要求 reCAPTCHA。 | 可在有依据时反馈误判；表单存在不证明本次是误判。本轮没有填写或提交。 |
| [G4：URL-prefix 定义](https://support.google.com/webmasters/answer/10432366?hl=en)、[G5：属性范围](https://support.google.com/webmasters/answer/34592?hl=en) | 属性按指定协议和 URL 前缀包含页面。 | 根属性范围可包含 WOW 和 `/Gitube/`。这是报告范围，不能写成每个子页均已确认有害。 |

**豁免查找结果：** 在 G1、G2、G3 及针对 Google 官方域名的定向搜索中，未找到明确的归档、教育、博物馆或历史镜像豁免。这是所查资料的有限结论。没有证据支持“只加 archive 字样即可通过”，也没有证据支持“任何历史登录画面都必须删除”。Google 最终如何评价本次修改仍需复核结果。

## 已发布页面的定向检查清单

下列路径均相对于 [WOW 浏览版](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/)。每一页均已直接 GET、取得 HTTP 200，并与 `97f7cf6` 的对应 Git blob 逐字节比较。完整哈希和链接目标见来源账本。

| 页面 | 已修复或已确认 | 剩余可见语义与优先级 |
| --- | --- | --- |
| `visa/reward/index.html` | 无输入/业务 form；两个链接均在本项目内 | **P0。** 稳定渲染可见两个大按钮：用 WoW 账号登录、用信用卡信息登录；入口没有局部静态表单提示，继续导向两个登录页。 |
| `visa/reward/login.html` | 0 form、0 控件；有静态展示提示 | **P0。** 仍要求填写姓名、邮编、出生日期和 SSN 后四位，原说明把此步骤描述为账号安全措施。 |
| `visa/reward/wow-login.html` | 0 form、0 控件；有静态展示提示 | **P0。** 仍要求输入 WoW 账号信息，并显示 Account Name / Password 标签。 |
| `visa/index.html` | 无 form；申请卡/条款外链已转成本地缺失说明 | **P1。** 仍以在售信用卡方式描述利率、奖励、申请资格；可进入 Rewards Site。 |
| `misc/deals.html` | 申请卡和网络服务营销外链已本地化 | **P1。** 保留“立即申请”、当期优惠口吻，导向上述信用卡页面。 |
| `misc/beta-signup.html` | 业务字段静态；保留的是搜索控件 | **P1。** 仍欢迎输入邀请码、邮箱、地址等，声明将发送确认邮件；应明确活动已结束。 |
| `misc/promotion.html` | 兑换字段静态；搜索与语言选择保留 | **P1。** 仍称可在此生成游戏兑换码，继续给出输入/提交指令。 |
| `community/stories/submit.html` | 投稿控件静态；搜索保留 | **P1。** 必填、邮件/账号、接受协议等说明仍用当前业务口吻；显示为历史投稿规则更清楚。 |
| `contests/l70etc-musicvideo/submit.html` | 上传/报名字段静态；搜索保留 | **P1。** 姓名、地址、账号和上传说明仍在；可加赛事年份及停办说明。 |
| `policy/index.html` | 反馈部分静态；保留本地化搜索 | **P2。** 仍出现发送反馈及发送成功的历史文字；不是本次最强疑似入口。 |
| `contests/05-12-giveaway/contest.html` | 无业务 form；只有搜索 | **P2。** 正文明确 2005 年名单且无需报名，历史语境较强；不建议因“contest”一词批量移除。 |
| `downloads/index.html` | 客户端业务链接本地化 | **P1/P2。** 仍称点击下载客户端并要求 WoW 账号；与壁纸、音乐等正常档案并列。 |
| `downloads/other-downloads.html` | 客户端、桌面主题等目标均已本地化 | **P1。** 仍邀请下载旧软件、升级账号；应区分历史软件目录与可正常浏览的媒体。 |
| `downloads/languagepack-en.xml.html` | EXE/DMG 目标进入本地缺失说明 | **P1。** 仍有下载安装、登录触发补丁等操作指令。 |
| `downloads/languagepack-es.xml.html` | 同上 | **P1。** 西语版本应同步标识历史状态，不只改英语版。 |
| `ui/index.html` | PC/Mac 工具包、EditingUI.zip 等目标进入本地缺失说明 | **P1。** 保留下载工具、Repair Utility 的当前服务口吻。 |
| `info/faq/blizzarddownloader.html` | 本次未见直接软件载荷链接；导航已本地化 | **P2。** 是旧下载机制解释，应保留文献内容，加时间语境即可。 |
| `index.xml.html` | 账号创建、管理、取回密码等目标为本地缺失说明 | **P1。** 仍以“Community Site”标题及原账号服务菜单呈现，需给旧业务项清楚的历史标识。 |
| `info/encyclopedia/index.xml.html` | 同上；搜索保留 | **P1/P2。** 历史正文含“OFFICIAL”及品牌 shell，宜在派生页 title/抬头明确非官方归档身份。 |
| `index.html` | 本地静态入口跳转到历史首页 | **P2。** 当前跳转页不足以作为登录等敏感页面的唯一说明；深链访问会绕过它。 |

补充只读核对：`visa.html`、`visa/reward.html` 是本地跳转别名，后续整改必须覆盖；`__offline/missing.html` 把原始 URL 作为文字解释，没有“去原站办理”的可点击出口。本次 20 个代表页的 HTML 锚点没有直接外链。这个结果不扩张为对全站每种动态行为的证明。

对发布树作有界文件名盘点，未发现 `.exe/.dmg/.msi/.zip/.bat/.cmd/.pkg/.scr/.com/.jar` 载荷。它支持“当前没有这些扩展名的软件下载实体”，不替代对任意格式文件的安全分析，也不表示旧软件安装指令已经充分解释。

## 归档标识的真实可见性

新建直接连接的 headless Chrome 上下文检查了桌面 1440×1000 的两个登录页、奖励入口、首页，以及 390×844 的登录页和首页；随后等 `load` 和 `networkidle` 重点复查奖励入口与身份信息登录页。没有跨过警告页、关闭 TLS/安全功能或输入业务数据。该环境成功渲染不能用来判定其他 Chrome 上下文的信誉提示已经消失。

顶部横幅确实可见，内容包含非官方、与 Blizzard 无关联、快照时间和不收集用户数据。计算样式为 12px Arial，桌面高约 28.8px，390px 视口高约 62.4px；位置是 relative，随滚动离开视野。横幅已经做对了身份说明的基础工作。

仍有两个具体缺口：

- 奖励入口的两张登录按钮比横幅更醒目，而且按钮文字没有历史限定。两张图在稳定加载后确实显示，不能把初次加载时图片空白当作整改。
- 390px 登录页文档宽 775px，局部静态表单提示宽 460px、起点 x=149，首屏只显示其一部分；当前业务措辞和历史说明均有裁切。直接进入该页的用户不应依赖横向滚动才能理解它已停用。

所以，**单独再加一条免责声明不是本报告推荐的完整处置**。更强的界面证据是：浏览者在任意深链、移动视口和关闭 JavaScript 时，都能先理解“这是旧页面的展示，没有当前登录/办卡/兑换/报名服务”。这是一项可验证的设计目标，不能承诺自动解除 Google 标记。

## 最小后续方案与验收

**P0：历史化 VISA 登录链。** 在派生层为奖励入口及两个登录 URL 提供紧凑的历史展品抬头，写清 2008 年原用途、独立归档身份、业务已停用；公开 title 加 `2008 archive`。把两个主动登录按钮替换为“查看 2008 年 WoW 账号登录界面 / 信用卡奖励登录界面”的入口，原按钮图像只作为带说明的历史画面。登录画面前增加“以下为当年页面文字，请勿提供真实身份或账号信息”的语境。静态表单转换继续保留，直接访问旧别名也得到相同说明。

优先采用清楚的历史展品页而不是重写原件。如果项目定位只需要百科且不需要公开展示金融/凭据页面，最保守而改动较小的选择是：这些公共 URL 显示目录说明与历史用途摘要，完整画面保留在离线档案；它不是 Google 明文强制要求。不要只在首页加封面、让原登录 URL 继续独立显示旧业务页。

**P1：统一旧业务与软件下载语境。** 对申请卡、报名、兑换、投稿页面补上停用/活动年份说明；在旧菜单上把账号服务标成历史入口。软件下载部分明确“2008 年安装说明，下载实体未收入本浏览版”，保留缺失说明而不恢复旧可执行文件外链。壁纸、音乐、截图等文献浏览不必因此整体移除。新增资源恢复部署前复核这些入口，因为恢复图片会提高原品牌界面的完整度。

**验收标准：**

1. 任意 P0 深链和别名在桌面及 390px 视口第一屏完整显示独立归档身份、旧业务已停用，且在原登录口吻前出现；JavaScript 开/关均成立。
2. P0 入口没有以当前登录/办卡语气呈现的可操作按钮。原按钮若留作史料，处于明确的历史展品说明内；没有可编辑凭据、自动填充、业务上传或提交控件。
3. P1 业务说明和软件页面按语言同步标识；旧业务链接只进入本地历史展品或缺失说明，不恢复银行、登录、软件安装外联。
4. 搜索、百科菜单、奖励/任务筛选等既有功能通过对应回归检查；冻结原件及来源哈希无变化。
5. 保存实际新 Pages 提交、远程字节对照、桌面/移动截图和行为检查结果，再更新复核稿。当前 20 页检查只是基线，不可改写为后续方案已实施。

## 复核材料需要怎样改

原[复核准备稿](search-console-review-20261014.md)应更新正式事实：实际选中的是根属性；报告只有“欺骗性网页”1 项、样本“不适用”，未提供首次日期。不要继续要求填一个不存在的样本列表或猜日期；不要写成已定位分页 `eval` 导致社会工程分类。

复核说明把“历史身份与业务入口的处理”放在前面，把参数执行修复、单元测试作为技术验证背景。对于当前已完成部分，可以写：

> The Security Issues report for https://vvcchh0.github.io/ shows one Deceptive pages issue and no example URLs. We have not identified the original triggering URL. The WOW project is an independent archive of 2008 Blizzard website material. Its historical account, identity, registration, redemption and upload controls have been replaced with non-editable display content. The published files were checked against Pages commit 97f7cf66255593c3b936d7957abcd134674de048.

只有后续历史展品整改真正部署后，才增加相应 URL、说明/按钮改动、移动端和禁用 JavaScript 的验证结果。不要提前宣称它们已完成，也不要以“教育用途理应豁免”作为复核理由。

**根属性边界：** 按 G4/G5，`https://vvcchh0.github.io/` 覆盖这个前缀下的 WOW、Gitube 等路径。本报告没有审计 Gitube，因此不能据此声明根属性所有问题均已解决。可查看项目级 URL-prefix 报告帮助定位；新增子属性不会自动改变已有根报告的复核范围。提交根属性复核前须对其范围有充分依据，或在材料中如实标明已检查项目及未确定触发范围。没有证据要求把两个项目都认定为有害。

若全面检查后有理由认为安全页面被误判，可使用 G3 官方错误警告表单说明归档身份和具体证据；若问题已实际修复，优先按 G1 的 Search Console 安全复核流程处理。两条路径都不是保证放行的捷径。本轮没有提交任何复核、误报反馈或外发消息。

## 证据与方法限制

[来源账本](../research/google-deceptive-archive-20261014/source-ledger.json)记录官方来源访问日、抓取标识、20 页直接 HTTP 响应哈希与发布字节相等结果、6 个渲染场景和 2 个稳定加载复查。临时截图只用于本轮视觉判断，账本中的临时路径不作为长期可下载成果；未来实施验收应另存正式截图。核心发现和验收要求已经写入本文。

Google 文档由已装 Firecrawl 连接器实时读取。Google 文档主机 direct 连接诊断失败后通过连接器 basic proxy 取得；最早两份官方读取先于本地 direct 诊断，未完全遵循要求的初始 direct-first 顺序，故在账本中明确记录。本地 CLI 不存在，没有为此安装或修改全局工具。WOW 页面读取全部 direct 成功；浏览器在修正无效的 direct proxy 参数后以 `--no-proxy-server` 成功，未关闭安全保护。

整合时已为来源账本与两张关键截图设置单文件白名单。主代理复看并保留了[桌面奖励入口](../research/google-deceptive-archive-20261014/screenshots/reward-entry-desktop.png)与[移动端身份登录页](../research/google-deceptive-archive-20261014/screenshots/identity-login-mobile.png)，摘要写入账本；其他临时截图仅作本轮辅助。

[G1]: https://support.google.com/webmasters/answer/9044101?hl=en
[G2]: https://developers.google.com/search/docs/monitor-debug/security/social-engineering
[G3]: https://safebrowsing.google.com/safebrowsing/report_error/?hl=en
[G4]: https://support.google.com/webmasters/answer/10432366?hl=en
[G5]: https://support.google.com/webmasters/answer/34592?hl=en
