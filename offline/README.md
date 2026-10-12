# 2008 魔兽官网与百科离线镜像：资源恢复版

解压便携包，双击根目录 `START_OFFLINE.cmd`，保持启动窗口打开。浏览器入口：

- [2008 官网首页 / Current News](http://127.0.0.1:8765/)
- [Warcraft Encyclopedia](http://127.0.0.1:8765/info/encyclopedia/index.xml)
- [Game Guide](http://127.0.0.1:8765/info/)
- [Media / Downloads](http://127.0.0.1:8765/downloads/)
- [Archived News](http://127.0.0.1:8765/info/archivednews.html)

需要 Python 3。浏览服务只用标准库，无需安装额外包。在解压目录也可运行：

```powershell
python tools/offline_mirror.py serve --port 8765
```

端口占用时使用 `powershell -File tools/launch_offline_mirror.ps1 -Port 8766`，访问相应端口。服务只绑定本机；按 Ctrl+C 停止。通过 HTTP 入口浏览，直接双击 HTML/XML 文件不能完整还原相对路径、脚本与跳转。

百科以用户确认的 `20080512210044` 为基准，保留首页及51个导航词条。官网首页使用同日21:00:44之前的真实捕获，侧栏、正文链接及其图片、CSS、JS等按接近基准的实际捕获重建。原本带`.xml`后缀的许多页面实际保存HTML，离线服务按经过验证的类型提供。

本副本组合了多个捕获时刻，不能当作单次完整快照。锚点后同日图片、其他2008补充，以及仅有更早静态捕获的项目分别记录实际时间与采用理由。XML声明错误、导航标签和间隔图属性拼写错误等兼容修复只作用于派生副本；原始响应、原MIME和摘要均保留。旧日历显示基准日期，避免现代年份超出其年份表。

Toplist 的数据请求也使用基准日期。其缺失的 `effects.js` 使用官方 Scriptaculous 1.6.5 源码作兼容补充：已保存的 Prototype 与该版本逐字节相同，加载器正文也相同。此文件明确列在 `upstream-compatibility-map.json`，保留 MIT 许可证、官方提交与摘要，不计为 WoW/Wayback 捕获，也不补造统计数据。

所有浏览请求留在本机，缺失项显示明确的离线提示，不会自动到Wayback或现代官网补下载。账号登录、支付、在线状态服务、广告、遥测、社交链接及大型客户端下载不具备在线功能。现代浏览器也不能直接运行旧Flash插件；保存的原素材与可浏览HTML需区别看待。搜索提供本地百科标题匹配。

文件组织：

- `offline/site/`：可直接由本地服务浏览的派生站点。
- `offline/build-manifest.json`：路由、别名、实际捕获时间、源/派生摘要和修改记录。
- `offline/approved-*-map.json`：经独立验证后接入的来源地图，时间补充单列。
- `offline/source-entities-*-recovery/`：新增页面和资源的未改写实体，按内容摘要去重。
- `backups/*recovery-2008/`：分批原始实体ZIP、请求manifest及响应证据。
- `research/*recovery-2008/`、`research/offline-2008/full-recovery/`：CDX查询、完整性判断、缺口与浏览验收。
- `docs/resource-recovery-2008.md`：本轮范围、设计理由与验收记录；两个Sol调研报告记录查询方法和旧官网组织结构。

服务不需要此前的百科来源包即可运行。重新构建需要完整来源工作区；原437项百科/布局原件仍在此前的`full_source`来源包，便携恢复包保留浏览副本与其索引，不重复冒充新增原件。首版及历史ZIP保持不变。

`FILE_SHA256SUMS.txt`校验包内文件；相邻`.sha256`校验ZIP本身。收录数量、尚未恢复项目和是否达到完整闭包，以同一构建的浏览验收及打包报告为准，不能用占位响应HTTP 200计作恢复。

2026-10-12交付构建含8,304条路由、917个文档。本构建的一次完整浏览检查917/917通过，脚本错误、未处理加载失败和外网请求均为0；侧栏407个范围内入口有406个已取得，没有路由拒绝。此前7,903路由构建及其补测记录保留为历史证据。

最后一轮新增407个图片URL，其中70项属于选用基准资源、12项为晚期2008补充、325项为有完整2008空索引证明的更早静态补充；实际日期均在来源地图中单列。仍有缺图、缺失脚本、一个未取得的PvP侧栏入口和Toplist动态数据缺口，`restoration_complete=false`。完整浏览记录了4,581次范围内占位引用及1,127次范围外引用；重复引用次数不是缺失文件数。当前浏览报告为`research/offline-2008/full-recovery/browser-validation.json`，最终剩余目标见`research/final-gap-closure-20261012/final-build/`；请区别“页面可浏览”与“全部原资源齐全”。
