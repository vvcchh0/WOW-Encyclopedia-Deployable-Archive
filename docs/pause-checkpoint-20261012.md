# 2026-10-12 暂停与续接状态

按用户“浏览检查结束后暂停目前工作，等待通知恢复”的指令暂停。所有下载批次与浏览检查均已结束；未启动 global wave，未开始新下载，也未生成新版发布包。保留本地浏览服务供查看。

当前冻结构建为 4558 条路由，manifest SHA-256：`134f2458c7f2ba7c75b039989b1b4eaf6214c00e6509c75a1154439917c0ceba`。2008-05-12 21:00:44 基准不变。当前地图含 5370 条捕获记录，其中 878 条为构建后新增，尚未进入当前镜像。另有 1 条明确标注的上游兼容资源，不能计为魔兽官网历史捕获。

## 浏览检查结果

[完整检查快照](../research/offline-2008/full-recovery/round-016-full-browser-validation.json)检查了全部 917 个文档，页面结构与实体对应检查均完成；整体 `accepted=false`、`restoration_complete=false`。构建与服务身份在检查期间保持不变。

- 407 个侧边栏目标中 406 个已有内容，路由拒绝 0；PvP Minisite 目标仍未取得。
- `/info/faq/pvppage.html` 与 `/info/underdev/dressingroom.html` 有 6 条去重脚本错误（原始事件 12 条），涉及 navtree/Menu 初始化。保留错误证据，暂停前不继续修复。
- 外网请求 0，意外资源请求失败 0；这不表示图片齐全，因为缺失图片有明确占位。官方范围占位引用出现 10260 次，外部范围 1129 次，均是引用次数而非独立文件数。
- Toplist 有 1 项明确缺失的历史动态数据；未伪造统计数据。

## 下载交接

B 最近两批 243 条有效资源已独立复核并合入地图。A main003/main004 下载结束并封存，执行者验证 173 条有效实体，尚未由根代理独立验收、尚未并入地图。其 426 条未完成/失败记录保留；`ptrcontestsbg.jpg` MIME 与字节类型不符，已排除于有效 map；`bg-shatar.jpg` 请求在截止时中断，未自动重试。

[运行详情](../research/site-recovery-2008/static-cdx-support/main-image-followup-003-004/main-followup-summary.json)与两张 valid map、ZIP、manifest 均保留。B 的 global selector 仅保存了代码，未运行、未生成或调度四分片；C 的 20 个严格 2008 年 CDX 查询及原始响应均保留。

## 恢复入口

以[机器可读暂停状态](../research/offline-2008/full-recovery/pause-state-20261012.json)为续接入口。收到明确恢复通知后，先复核地图/构建与任务状态，再独立验收 A 的 173 项，处理浏览暴露的脚本错误，重新冻结有界候选队列。最终构建、完整浏览验收与打包尚未进行。现有旧归档与原始证据保持保留。

并发浏览工具的本地验证已结束，默认 3 workers、15 秒 networkidle，验收证据在 `research/browser-audit-concurrency/`；它没有重复启动完整 917 页检查。当前完整报告来自原先已运行的串行检查。
