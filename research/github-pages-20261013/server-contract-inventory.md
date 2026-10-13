# GitHub Pages 静态发布前的 `offline_mirror.py` 契约盘点

本报告是只读盘点，不改变 `tools/offline_mirror.py`、`offline/site` 或
`offline/build-manifest.json`，也没有发起网络请求。依据当前工作树中的
`tools/offline_mirror.py`、`offline/build-manifest.json` 和已生成的
`offline/site`。

## 当前导出快照

manifest 的 `schema_version` 为 1，`anchor_timestamp` 为
`20080512210044`，`source_entries` 为 437；载入的扩展 map 为 7,859 项，
其中 7,858 项标作 WoW 来源。最终 `files` 和 `routes` 都是 8,304，
`route_aliases` 为 180 个，`unresolved_reference_count` 为 27,700。
其中 1,158 个实体经过派生改写，7,139 个保持字节复制，1,031 个是显式
补充，5 个是生成占位资源，2 个是兼容支持资源。

`offline/site/__offline/` 目前含 7 个静态文件：

* `compat.css`、`compat.js`；
* `excluded-frame.html`、`missing.html`、`missing-image.svg`、`empty.js`、
  `empty.css`。

manifest 中对应的 5 个 `placeholder_routes` 是上述占位文件（不包括两个
兼容文件）。页面中简单文本扫描得到约 986 个 `/__offline` 引用、9 个
`/_origins` 引用、642 个 `searchCall` 引用；557 个文件含 `http://`、15
个文件含 `https://`。后两项包含占位查询字符串、历史 provenance 和
兼容脚本中的原始目标，不能直接解释为浏览器仍会发出外网请求。

manifest 的实际引用证据为：`localized` 109,616、`placeholder` 27,700、
`preserved` 2,308、`removed` 748、`patched` 19。上下文包括
`navigation` 64,671、`image` 41,319、`css_url` 16,197、`script` 7,783、
`stylesheet` 3,601、`frame` 4,988、`css_import` 1,428 和
`script_url` 330。这些数字是构建时证据，不是 Pages 运行时会动态计算的
接口。

## 函数与职责

### 路由、别名、查询串和来源命名空间

* `canonical_url`（156–175）只规范 scheme/host 大小写和默认端口，保留
  path、query、fragment 的大小写和内容；`origin_namespace_host`、
  `origin_route`、`route_path`（181–229）为 forums 等获批准的其他 host
  建立 `/_origins/<host>/...` 命名空间。
* `canonical_request_path`（232–263）处理重复斜杠、`.`、尾斜杠和空白，
  先在 manifest route、alias、special route 中找已知形式。它依赖服务器
  在请求时执行规范化；纯静态 Pages 不会自动把所有变体归并。
* `Localizer._lookup`（357–407）优先 host+path 的 `origin_index`，再用
  alias/path，同源检查防止把 forums 或 Blizzard 资源错误替换为主站首页。
  `Localizer.localize`（409–448）保留 fragment/query，并把允许来源的已
  验证资源改成站内 route；未知、无效或外部资源改成占位 route。
* `build_site` 中的 route 注册和 alias 处理在 1334–1589；manifest 的
  `route_aliases`、`origin_index`、`origin_index_conflicts` 保存了这些关系。
  根 `/` 和 `/index.html` 的默认目标在 1552–1561 设置。

### 资源引用、绝对路径和 JS 内 URL

* `rewrite_css`（462–509）分别处理 `@import` 和 CSS `url(...)`；缺失的
  stylesheet 使用 `empty.css`，普通图片/背景使用 `missing-image.svg`。
* `rewrite_generic_markup`（512–529）处理 `src`、`href`、`data`、
  `background`、`action`、`poster`、`url`，根据扩展名选择 image/script/
  stylesheet/navigation 上下文。
* `rewrite_script`（720–927）不执行 JS，只对有证据的绝对 URL、嵌入的
  HTML 属性和字符串做有限静态改写。root-relative 的 JS 字符串在 910–915
  有意保留，让它们由本地 origin 解析；字符串拼接前缀在 849–858 保留，
  避免把半个 URL 错当完整资源。未知绝对 URL 转为本地 missing/empty
  占位，analytics 在 721–730 被删除。
* `rewrite_html` 和 `LocalizingHTMLParser`（989–1136）处理 HTML、菜单和
  `.xml` 变体；`handle_pi`（1126–1130）保留 `xml-stylesheet` 标记，同时
  删除其他 processing instruction。`inject_compat_before_head`（1164–
  1193）把兼容 CSS/JS 插入真正的 head 边界，避免误命中 script/style
  字符串中的 `</head>`。
* `rewrite_text`（1196–1212）决定 HTML/menu、CSS、JS 和其他文本的改写
  分支。`ReferenceRecorder`（291–323）把 `literal`、`resolved_url`、
  `action`、`target`、`context`、`reason` 写入每个 manifest file，单文件
  记录上限为 400，完整计数保存在 `reference_counts`。

GitHub Pages 必须发布已经生成的 `offline/site`，不能只发布 source map
并期待服务器重新执行这些改写。Pages 不会运行 Python，也不会替换站内
绝对路径；若使用 project Pages 的 `/repo/` 子路径，现有大量 `/...` 根
路径还会指向域名根，因此部署必须使用根路径/custom domain，或另做有界的
前缀适配。

### MIME、XML 和派生 HTML

* `file_mime`、`mime_base`、`charset_for`（115–136）从响应 MIME、扩展名
  和 BOM 推断编码。`build_site` 对 `html`、`menu_html`、`css`、`js`、
  `xsl`、`legacy_component`、`xml` 做文本派生（1643–1661），并在每条
  file record 中保存 `source_mime`、`mime`、`source_sha256`、
  `derived_sha256`、长度、kind、时间戳和 transformed 状态（1665–1688）。
* 旧百科 `.xml` 实体的正文可能已经是 HTML；派生文件仍保留原 route 后缀，
  但 loopback server 按 manifest 的 `mime` 发 Content-Type。GitHub Pages
  只能按静态文件扩展名提供 MIME，不能复现服务器对 `.xml` 派生 HTML 的
  route-specific header。若浏览器需要 HTML 解析，Pages 发布方案必须提供
  `.html`/extensionless 副本或其他静态路由，并明确原 `.xml` route 的
  redirect/兼容策略；不能假设 Pages 会采用 loopback 的 MIME。
* `rewrite_html` 用注释标明派生源 SHA 和“XML stylesheet PI handled as
  HTML”（1148），所以静态导出可以保留派生正文和 provenance；XML/XSL
  的原始语义仍由浏览器 MIME 决定，不能通过把所有原文件改名来声称原始
  XML 被完整恢复。

### 占位资源和 `__offline` 虚拟路径

* `encoded_missing_query`（282–288）把 `source`、`requested`、`reason`
  截断到 512 字符并 URL encode；`Localizer._placeholder`（450–459）按
  上下文选择 `missing-image.svg`、`empty.js`、`empty.css` 或 `missing.html`。
* `placeholder_bytes`（1248–1280）生成五种固定内容：广告 frame 排除说明、
  未收集页面、叉号 SVG、空 JS、空 CSS。它们可以直接作为静态文件发布；
  query 中的 source/requested 说明不会自动改变固定文件正文。
* `OfflineRequestHandler._handle`（1913–2092）实现服务器侧虚拟职责：
  路径解码和 traversal 拒绝（1915–1927）、Toplist 动态 feed 的有限 404
  grammar（1928–1943）、规范化（1944–1959）、API、根 alias、带 query 的
  missing/uncollected 页面、普通 alias、manifest file、按后缀生成的未收集
  fallback 和最终 404。

### 搜索、API 和动态 feed

* server API 在 1960–1984：`/__offline/api/log` 返回当前请求日志，
  `api/health` 返回 PID、manifest SHA 和 route 数，`api/url-map` 解析
  `url`/`path` 查询并返回匹配实体与 alias，`/__offline/build-manifest.json`
  返回完整 manifest。这些都是 Python 动态响应。
* `offline/support/compat.js` 将页面 searchCall、同站绝对链接和菜单操作
  接到本地：`offlineSearchCall` 约在 180–260 行；百科精确标题可走
  `topicsArray`，普通百科/站内搜索转到 `/__offline/uncollected?...`，
  tech support、beta forum 等只保留原目标说明，不访问外部站点。
* server 的 `/__offline/uncollected`（2007–2025）根据 kind/target/query
  生成说明页；Pages 能发布一个固定说明页，但不能按 query 动态回显这三项
  值。需要客户端替代时，应由兼容 JS 解析 query，或在发布前为已知 query
  生成静态页面；不能把 GitHub Pages 当搜索/API 后端。
* Toplist 的日期和 feed 选择在 `rewrite_script` 749–759 被固定到
  `2008-05-12 21:00:44`；缺失 feed 的 URL grammar 在 1935–1943 返回
  明确 404。首页 Screenshot-of-the-Day 的 live `Date` 在 790–802 被改成
  snapshot clock，calendar 的 `new Date()` 在 734–741 也被固定。已有静态
  feed 文件可以直接发布；任意日期生成、查询日志、健康状态和未收集 feed
  解释页需要静态 JSON/HTML 或客户端代码。

### 服务器边界和 manifest

`OfflineRequestHandler`（1795–2092）按 manifest 查文件并用
`_headers`（1825–1851）发送 `Content-Type`、长度、CSP、`nosniff`、
`X-Offline-Entity-Kind`、source/derived/served SHA。`OfflineHTTPServer`
（2095–2119）从 manifest 建 `manifest_routes`；`run_server`（2122–2137）
只允许 `127.0.0.1`、`localhost` 或 `::1`，绝不抓取缺失资源。Pages 不支持
这些自定义 response headers、动态 request log 或 loopback health；可保留
manifest 字段作为静态 provenance，但若产品依赖 header 分类，需在页面内
使用 manifest/生成的 JSON，而不是等待 HTTP header。

manifest 的关键发布字段是：`files[]`（route、output_path、source_local_path、
source/source-derived SHA 和长度、mime、kind、role、时间戳、references）、
`route_aliases`、`origin_index`、`placeholder_routes`、`unresolved_references`、
`stats`、`security` 和 `notes`。`security.external_fetches=false`、
`path_traversal_protection=true`、`serve_default_host=127.0.0.1` 是服务器
行为声明；静态托管环境不会自动继承实现，只能通过已生成内容和部署配置保持
等价边界。

## 静态导出与客户端替代清单

可以直接静态发布：

1. `offline/site` 中已生成的 8,304 个实体、两个兼容 helper、五个固定
   placeholder 以及 `_origins` 命名空间文件；
2. manifest 记录的派生 HTML/CSS/JS/XSL/图片/字体/Flash 文件和已保存的
   source/derived hash provenance；
3. 180 个已知 alias 的静态副本或明确 redirect 文件；
4. 固定的 `build-manifest.json` 快照、固定 health 摘要、已知 route 的
   url-map JSON，以及已知 Toplist/SSOTD 数据文件。

必须由构建阶段生成静态变体或由客户端替代：

1. 根 `/`、尾斜杠、重复斜杠和未知 route 的服务器规范化/alias 选择；
2. `/__offline/api/log`、带任意 query 的 `api/url-map`、health PID 和
   动态 manifest 服务；
3. `/__offline/missing.html`、`/uncollected` 对每个 query 的 source/
   requested/target 回显；
4. Toplist 任意日期 feed grammar、未收集的动态数据和原站搜索接口；
5. 依赖 response MIME 的 `.xml` HTML 解析，以及 server 注入的
   `X-Offline-*` headers；
6. 未收集 JS/CSS/图片/页面的“按后缀自动生成 200 占位”行为。Pages 的
   `404.html` 可以作为统一兜底，但不能等价替代当前按类型返回 200、MIME
   和 entity-kind 的逻辑。

结论是：GitHub Pages 的最小可行输入应是已经派生完成的 `offline/site`，
配套静态 manifest 和一个有限的客户端 route/search 适配层。不能只上传
`mirror/`、运行 `offline_mirror.py`，或把 loopback server 的动态 API 当作
静态站点能力。上述清单没有修改任何实现，也没有验证 GitHub Pages 的实际
部署配置。
