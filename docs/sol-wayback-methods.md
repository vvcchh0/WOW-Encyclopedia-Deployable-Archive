# 2008 魔兽旧官网 Wayback 查询与原始实体恢复方法

首份报告：2026-10-11 15:38（Asia/Shanghai）。基准捕获 `20080512210044`。本专项只读取既有恢复证据、官方文档和开源源码；未向 Wayback 捕获或 CDX 接口提交实测请求，未新增 Archive 下载流，未修改主工具或镜像。来源快照、离线审计及候选探针在 [research/sol-wayback-methods](../research/sol-wayback-methods/)。

## 可以立即采用的结论

1. **捕获查询中移除 `showNumPages=true`。** 它请求分页元数据，不请求捕获行；`HTTP 200 + 表头 + 全 null 行` 应记为响应形状错误/元数据响应，绝不能记为无捕获。主任务已在本次调研期间取得移除此参数后的有效捕获行，见下方离线证据。
2. **发现 URL 与选取版本分开。** prefix 用于枚举；最终选版用 exact、明确时间窗、无 digest collapse。目录入口 `/info` 与后代 `/info/…` 分别检查。
3. **达到 `limit` 就标记覆盖范围未闭合。** 当前页面流的 downloads/news 各有 20,000 行，刚好等于请求上限；有效数据不代表枚举完整。优先窄时间窗或子路径分片，其次使用经过形状验证的 resume/page。
4. **`collapse=digest` 不是“基准前最近捕获”。** 它保留相邻同 digest 序列中的第一条，可能丢掉最近日期；prefix 跨 URL 边界也可能压掉内容相同的 URL。静态计划中的 5 项 `no_cdx_capture` 只能解释为“现有已折叠结果中未找到”，须保留暂定状态。
5. **继续使用 `id_`，同时验证真实实体与实际捕获日期。** `id_` 避免内容重写，不保证原始网络报文字节、原始响应头或无跳转。gzip/deflate 错误属于取得/解码失败，不证明存档不存在。

## 已核对的本地证据

可复现审计：`python research/sol-wayback-methods/audit_existing_evidence.py`，仅本地读取，输出 [existing-evidence-audit.json](../research/sol-wayback-methods/existing-evidence-audit.json)。输入文件 SHA-256 写入审计结果；共享目录仍在更新，下面数字来自 15:34—15:39 的读取，最终审计时间以 JSON 内 `generated_utc` 为准。

| 证据 | 实际观察 | 可得结论与边界 |
| --- | --- | --- |
| 最初读取的 `prefix-cdx-query-summary.json` / `prefix-cdx-query-results.json` | 13 次 HTTP 200；每次 102 bytes，相同 SHA-256 `6c205d…18c265`；原始 JSON 为字段表头加 `[null,null,null,null,null,null]` | 这些请求设置了 `showNumPages=true`。HTTP 成功，但没有可解析捕获行；不是无捕获证据 |
| `prefix-cdx/001-52126aa107473d12.json` 及其 metadata | 仍保留上述 null 响应。全目录审计找到 52 份同 SHA 的历史响应 metadata | 不将 52 份误说成 52 个独立 URL；它们来自多个批次/请求。审计保留各请求 URL 与时间 |
| 调研期间更新后的页面 prefix 结果 | 12 个结果记录，共 103,204 条有效 14 位 timestamp 行，0 条 null 行；请求已不含 `showNumPages` | 已有运行证据支持修正方向。本专项没有重发这些请求。downloads/news 各 20,000 行，需检查上限截断 |
| `research/resource-recovery-2008/cdx-discovery.json` | 8 个 prefix HTTP 200、无解析错误，共 9,771 行；community 711、downloads 1388、info 4384、misc 318、new-hp 416、news 955、pvp 711、shared 888；均用了 `collapse=digest` | 明确证明这些 prefix 有捕获。行数不足 5000 只证明没有达到该显式上限，不证明所有后端分页/过滤风险已排除 |
| `selected-download-plan.json` | 269 项：264 项 `pre_anchor_90_day`、5 项 `no_cdx_capture`；后者 `cdx_proof_available=false` | 这 5 项不能升级为“从未捕获”。应做无 collapse 的 exact 查询，必要时再拓宽时间窗 |
| `backups/site-expansion-2008/errors.jsonl` | battlegrounds (`20080509135201`) 与 ingameevents (`20080509084338`) 均报 `incorrect header check`；旧错误记录无状态/响应头 | 只能确认为解码失败；无法由旧记录区分错误 Content-Encoding、二次解压、截断或捕获异常 |
| `backups/resource-recovery-2008/batch-001/manifest.jsonl` | 已有 JPEG `id_` replay 成功，记录实际 timestamp、Memento-Datetime、原响应头及 SHA-256 | 说明 identity replay 路径在现有流中可用；这不替代完整图片解码验收 |

`tools/wayback_backup.py` 当前已请求 `Accept-Encoding: identity`、校验 gzip/deflate EOF，并在解码错误时保留 HTTP 元数据；`tools/expand_wayback_site.py` 当前已有不带 `showNumPages` 的查询。这里记录观察，未改动这些文件，也未重复跑其测试。

## 查询参数与边界

| 用途 | 请求参数方案 | 判定规则 |
| --- | --- | --- |
| 已知页面/资源选版 | `url=<原URL>&matchType=exact&from=20080212210044&to=20080512210044&output=json&fl=timestamp,original,statuscode,digest,length,mimetype&gzip=false` | 不用 collapse；按实际 timestamp 降序取候选，内容校验失败才转下一候选。90 日精确起点为 2 月 12 日 21:00:44 UTC |
| 一个栏目后代 | `url=http://www.worldofwarcraft.com/info/&matchType=prefix` 加相同时间窗和字段 | `/info/` 的 prefix 不是 `/info` 入口的充分覆盖；入口另做 exact。也可用末尾 `/*` 隐式 prefix，但不要同时构造不明多重通配 |
| 域名历史 URL 发现 | `url=worldofwarcraft.com&matchType=domain` 加时间窗、上限 | 包含子域；不保留路径边界。先限制输出/分片，再按任务允许的 host/path 筛选，不能自动扩大到账号等功能 |
| 单 host 发现 | `matchType=host` | 忽略给定路径；与栏目 prefix 不同。保留 returned `original`，不要把 canonical key 当历史 URL 字符串 |
| 轻量 URL 名单 | prefix/domain 加 `collapse=urlkey`（若部署支持） | 只用于发现 URL；保留的是代表记录，不能直接用于最终选版。仍需上限/分页证明 |
| 紧邻基准前最新一条 | exact + 上述 `from/to` + `limit=-1`（IA CDX），或部署已验证的 `sort=reverse&limit=1` | IA 与 pywb 原生接口参数/返回格式有差别；保守方案是取有界 exact 全候选后本地排序 |

matchType 的四种范围和 SURT 搜索边界均由官方实现支持。`domain` 依赖 SURT；exact 是索引规范化后的匹配，不能假设它与 URL 字符串逐字相同。pywb `calc_search_range()` 对 prefix 明确保留尾斜杠，对 host/domain 明确忽略路径。[IA CDX 官方说明](https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server#url-match-scope)、[pywb 搜索边界源码](https://github.com/webrecorder/pywb/blob/main/pywb/utils/canonicalize.py)。

`from/to` 为闭区间，短时间戳分别向下/向上补齐。先使用基准前 90 日；无合适候选再查 2008 年更早记录；2008 基准之后与 2006/2007 捕获另列，按主任务策略决定是否采用。不要将当前页面枚举的 `from=2006&to=20081231235959` 原样当作自动混合选版规则。[pywb CDX API](https://pywb.readthedocs.io/en/latest/manual/cdxserver_api.html#from-to)、[pywb `cdx_clamp` 源码](https://github.com/webrecorder/pywb/blob/main/pywb/warcserver/index/cdxops.py)。

### showNumPages、分页和空结果

IA Java CDX 的 `createPagedCdxIterator()` 在 `showNumPages` 分支打印页数后直接返回 null，不进入捕获输出；pywb `ZipNumIndexSource` 返回带 `pages/pageSize/blocks` 的 `AlwaysJsonResponse`，`cdx_load()` 对 page_count 跳过普通后处理。因此计页响应不能套用捕获的 `fl=timestamp,…` 行解析。当前 null 行很可能是部署适配层把计页对象投影为捕获字段；**“适配层投影导致 null”是推断，未经部署源码确认**。参数请求本身不一定语法非法，错误是将元数据结果当捕获清单。[IA Java CDXServer 源码](https://github.com/internetarchive/wayback/blob/master/wayback-cdx-server/src/main/java/org/archive/cdxserver/CDXServer.java)、[pywb ZipNum 源码](https://github.com/webrecorder/pywb/blob/main/pywb/warcserver/index/zipnum.py)、[pywb CDX 处理源码](https://github.com/webrecorder/pywb/blob/main/pywb/warcserver/index/cdxops.py)。

推荐小范围查询不带 page/showNumPages。结果达到 limit 或单响应字节上限，记 `coverage_incomplete`，使用更窄时间窗/路径；大范围需要分页时将计页与取页分开，计页不设捕获字段投影，验证整数或 `{pages,…}` 形状，再用固定 pageSize 取 `page=0..N-1`。页数按压缩块估计，不能当最终过滤后的捕获数；某页为空也未必后续页为空。优先用 IA `showResumeKey=true`/`resumeKey` 顺序续传，但应先验证实际响应的尾部 token 格式，不把尾部 token 当捕获行。[IA 官方分页/续传说明](https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server#pagination-api)、[pywb 分页说明](https://pywb.readthedocs.io/en/latest/manual/cdxserver_api.html#pagination-api)。

结果分类建议：网络超时/TLS/429/5xx → `query_failed`；JSON 无法解析/全 null/错误对象 → `query_response_invalid`；达到 limit/字节上限/未闭合 resume → `coverage_incomplete`；成功、形状正确、覆盖明确且目标窗口确实零行 → `no_capture_in_queried_window`。最后一种仍不等于“历来无捕获”。日志必须写出 URL、时间窗、过滤、collapse、截断标志及原始响应。

### collapse、digest 与 3xx

官方 IA CDX 的 collapse 只折叠相邻记录，保留第一条；它不是全局 digest 去重，也不是最近日期选择器。若同 URL 2 月/5 月实体相同，先 collapse 后排序可能只剩 2 月时间。prefix 中跨 urlkey 相邻且 digest 相同也有遗漏 URL 的可能。因此先无折叠选版，之后可把相同 digest 的实体候选作为内容复用线索，仍保留每个 URL/捕获时间及实际下载哈希。不要把 CDX digest 直接当本地 SHA-256；公共 `length` 也不能直接当解码后实体长度。[IA collapse 定义](https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server#collapsing)。

发现阶段保留 3xx 状态，用于找到旧站目录别名、迁移和尾斜杠。200 过滤可用于“内容候选”查询，但不应是唯一存在性查询。回放时将 archive 调度重定向与历史原站重定向分别记录：每一跳 URL、状态、Location、最终 replay timestamp、`Memento-Datetime`、`Link rel=original`。只跟随允许的 Archive 回放域名；原站 Location 需要转换成独立的存档目标并遵守页面范围，不能因重定向落到现代 live web。最终日期超窗的实体另列，不因请求 URL 含基准日期就视为基准实体。这是本项目的证据/范围策略，依赖现有 manifest 已保存的 replay 元数据，不声称从 CDX 状态即可得到完整 Location 链。

## 原始实体、压缩异常与校验

获取形式为 `https://web.archive.org/web/<已选择14位timestamp>id_/<CDX original>`。pywb 官方说明 identity modifier 关闭内容重写，但部分 HTTP 头仍可能调整；源码 `should_rw_content()/is_identity()` 与这一点一致。它返回适合保存的未重写内容，不是 WARC/ARC 整条记录，也不是 byte-for-byte 原始 HTTP 传输。[pywb identity 文档](https://pywb.readthedocs.io/en/latest/manual/rewriter.html#identity-modifier-id)、[content_rewriter 源码](https://github.com/webrecorder/pywb/blob/main/pywb/rewrite/content_rewriter.py)。

诊断 gzip/deflate 时保留：实际状态/最终 URL、`Content-Encoding` 与 `x-archive-orig-content-encoding`、响应 `Content-Length`/原长度、原始实体前 32 bytes 的 hex、压缩前后长度、客户端是否自动解码、解压器 EOF。CDX 的 `gzip=false` 控制 CDX 响应，不控制 `id_` 原件传输。请求 `Accept-Encoding: identity` 有助于排除额外协商压缩，但不能取代实际头/字节检查；客户端已经解码时不得再按旧头解一次。[IA CDX gzip 参数](https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server#output-format-json)、[HTTP Accept-Encoding 定义](https://www.rfc-editor.org/rfc/rfc9110.html#name-accept-encoding)。

pywb 上游 `content_rewriter.py` 还会在原记录有 Content-Encoding、客户端 Accept-Encoding 不接受该编码时启用内容解码，即使未启用文本重写。因而 `id_` 与“无需解压”不是同义词，`identity` 请求也可能使回放服务器解码历史压缩。这提供了检查头/bytes 是否一致的源码依据；不能据此断言两个目标在线错误的根因。[pywb 内容传输处理源码](https://github.com/webrecorder/pywb/blob/main/pywb/rewrite/content_rewriter.py)。

建议保留有限大小的失败原始 bytes 到隔离证据文件。只有确认“头写 gzip、实体实际是完整 HTML/JPEG”等矛盾，才实现带显式标记的兼容分支；真正 gzip 校验失败/EOF 未到不能作为成功实体导入。deflate 的 raw/zlib 兼容亦须有证据和完整内容校验，不盲目吞掉异常。现有两条旧错误缺头，尚不能确定哪个机制所致。

验收分层：HTTP 200 → 不是 Wayback 错误壳 → 实际 timestamp/原 URL 合规 → MIME 与 magic/content 相符 → 图片完整解码或文本内容检查 → 本地 SHA-256 和来源记录。3xx、HTTP 200 错误页、截断图、HTML 冒充图片分别保留为不同失败。原始传输 bytes 与导出实体 bytes 如不同，应各自记录哈希和转换原因。

## 替代接口与第三方下载器

| 接口/实现 | 可用之处 | 证据等级和限制 |
| --- | --- | --- |
| IA Availability API `archive.org/wayback/available`，参数 `url`、`timestamp` | 一个已知 URL 的最近可访问候选，适合作为 CDX 失败后的候选线索 | 官方文档已验证，目标 URL 本次未实测。只给 closest，不枚举，不保证基准前；空 snapshots 同时可能表示未存档或当前不可访问 |
| Memento TimeMap/TimeGate | 借成功 replay 的 Link 头取得 timemap/相邻 memento 线索，再验证候选 | IA 官方声明支持 Memento；现有成功 manifest 已出现 `/web/timemap/link/<original>`。目标 TimeMap 本次未请求，不保证完整性/可访问性 |
| `/cdx/search/xd` | 旧下载器使用过的索引入口，可作为明确计划下的有限备选 | 只验证了工具源码确有此 URL，未验证当前服务契约/可用性；不是额外档案库，也不据此绕过主流数量限制 |
| 公开 ARC/WARC 文件定位 | 有文件标识、offset/length 且确实有公开访问权限时，才考虑取归档记录 | 当前 replay 的 `x-archive-src` 可标来源，但不是公开下载授权或可直接 Range 的承诺；公共 CDX 通常不保证公开 filename/offset。此路线待验证 |

IA 官方 Availability 文档明确将“未存档或当前不可访问”并列解释空结果，因此不得把备用接口的空响应作为零捕获证明。[IA 官方 API 文档](https://archive.org/help/wayback_api.php)。

已读取 hartator `wayback-machine-downloader` 原始源码：`archive_api.rb` 使用 `xd`、`collapse=digest`、`gzip=false` 和可选 200 过滤；**JSON 解析失败直接返回空数组**。主文件按 path 归并、默认挑最大 timestamp，下载用 `id_` 并设 `Accept-Encoding: plain`。可借鉴其 identity replay 和显式时间参数；不可照搬“解析失败即空”“页为空即结束”及路径归并当成严谨恢复证明。本项目应使用标准 `identity`，保留完整 URL/host/query 和错误类型。以上只是源码行为，未运行此工具。[下载器 API 源码](https://github.com/hartator/wayback-machine-downloader/blob/master/lib/wayback_machine_downloader/archive_api.rb)、[下载器主源码](https://github.com/hartator/wayback-machine-downloader/blob/master/lib/wayback_machine_downloader.rb)。

## 交主任务的最多三个探针

完整、可执行 URL 见 [proposed-probes.json](../research/sol-wayback-methods/proposed-probes.json)。**本专项未执行。** 由主任务复用已有页面请求流，不能同时增加第三流；若已取得相同成功证据，则跳过对应探针。

| ID | 目标 | 预期/判定 |
| --- | --- | --- |
| Q1 | battlegrounds exact CDX，基准前 90 日，无 collapse、无 status 过滤、无 showNumPages | 验证捕获字段形状；预期能观察既有候选 `20080509135201` 或其它候选/3xx。有效零行只记当前窗口无返回；null/错误/超时记查询失败 |
| R1 | `20080509135201id_/…/pvp/battlegrounds` | 以 identity 请求，保留状态/头/失败 bytes；预期得到可解析正文，或可诊断的编码失败；实际日期漂移另列 |
| R2 | `20080509084338id_/…/community/ingameevents.html` | 与 R1 相同；用于核对第二项旧解码失败。若 R1/R2 已被新工具成功恢复不再重复 |

## 状态与未验证项

**已验证（本地证据/上游来源）**：null 原始响应、移除 showNumPages 后已有有效结果、两个精确 decode 错误、静态 CDX 行数与五项暂定缺口；IA Java 和 pywb 上游的计页分支、匹配边界/时间范围、identity 重写开关；下载器上述源码行为。

**推断**：当前 null 与计页对象字段投影有关；当前 digest collapse 可能导致日期或 URL 遗漏；达到 20,000 的结果可能被限制截断。最后两项是覆盖风险，尚未量化遗漏多少。

**待验证**：当前 Wayback 部署是否与所读上游版本一致；真实 resume/page 响应形状；五项暂定缺口的 exact 查询；两项 gzip 问题的新响应；Availability/TimeMap/xd 的目标服务行为；直接 ARC/WARC 公开访问。未验证项不能写成恢复成功或确定无捕获。

源码快照保存在 `research/sol-wayback-methods/sources/`。路径 `code-2.json` 是曾猜测的 `rewrite_content.py` 404，随后已用文档和正确 `content_rewriter.py` 核对，不作为技术结论来源。上游文档包含旧部署默认值，本文不把其历史 pageSize/限制数字当当前线上保证。
