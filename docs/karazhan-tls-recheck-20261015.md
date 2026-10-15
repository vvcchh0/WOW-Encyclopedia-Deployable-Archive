# Karazhan 图库复查与 TLS 诊断（2026-10-15）

本轮实际请求全部 126 个唯一图片地址，取得有效图片 0 张。59 项取得 Wayback 未存档提示页，67 项在 TLS 握手阶段失败。后者没有源站 HTTP 响应，不能判为未存档。

| 类型 | 有效图片 | Wayback 404 | TLS 连接失败 | 未请求 |
|---|---:|---:|---:|---:|
| 原图 | 0 | 30 | 33 | 0 |
| 同目录缩略图 | 0 | 29 | 34 | 0 |

目标仍为 `http://www.worldofwarcraft.com/info/dungeons/images/karazhan/ssN.jpg` 和 `ssN-thumb.jpg`，N=1..63，回放时间提示为 `20080512210044id_`。没有混入 `thumbs/` 子目录预览图。批次在北京时间 11:13:04–11:15:39 运行，先检查上轮未请求的编号。所有保存响应体均完成独立长度、摘要及图片解码检查。镜像和浏览包没有修改。

## TLS 判断

- 本机系统 DNS 返回 `199.59.149.237`；通过现有代理取得的 Cloudflare HTTPS DNS 回答为 `207.241.237.3`。默认 direct 在 TCP 前超时。
- 对单次 direct 请求使用 HTTPS DNS 回答的地址后，TCP 可以建立，但 TLS 仍被重置。只修正解析结果不足以恢复当前直连。
- 本机代理为 `127.0.0.1:7890`，监听进程 `clash-win64`。同代理访问 Cloudflare 可以完成 TLS 并取得 HTTP 200。
- Wayback 已知 JPEG 对照在约 11:10:51 和 11:11:44 分别通过 Windows curl/Schannel、Python urllib/OpenSSL 成功取得，长度和摘要与原件一致。稍后的两个客户端对照均在 TLS 握手中失败：Schannel 报 `failed to receive handshake`，OpenSSL 报 `UNEXPECTED_EOF_WHILE_READING`。
- 强制 TLS 1.2，以及仅对当前代理请求指定 HTTPS DNS 回答的目标 IP，均未恢复握手。代理已返回 CONNECT 200，但 Wayback TLS 没有完成，没有出现源站 HTTP 状态或证书校验失败消息。
- 只读配置检查发现 `archive.org` 后缀规则指向代理选择组，并非显式 DIRECT；相关日志没有给出对应 EOF/reset/TLS 原因。未调用控制器，因此实际出口节点及失败位置仍未确认。

现有证据更支持 **Wayback 目标连接链路的间歇性中断**。系统 DNS 差异是一个实际问题线索，但指定地址后的失败表明它不能解释全部故障。跨 TLS 客户端复现也降低了单一 Schannel 实现问题的可能性。仅凭客户端记录，还不能定位连接由 Clash、上游代理、网络中间层还是远端关闭；也没有证据把 TLS 故障解释成 HTTP 429。

本轮保持证书验证，未修改系统 DNS、hosts、代理规则或进程。只刷新 DNS 缓存预计不足以解决已复现的 TLS 阶段中断。

## 证据与修正

- [逐项最终报告](../research/karazhan-recheck-20261015/batch-report.final.json)与[独立验收](../research/karazhan-recheck-20261015/root-acceptance.json)。
- [DNS 对照](../research/karazhan-recheck-20261015/dns-parent/summary.json)、[默认传输对照](../research/karazhan-recheck-20261015/control-parent/summary.json)、[跨客户端及进程内参数对照](../research/karazhan-recheck-20261015/tls-parent/summary.json)。
- [前次限时检查](karazhan-gallery-accessibility-20261014.md)。
- [Clash 本地配置与日志检查](../research/karazhan-recheck-20261015/proxy-local/clash-local-evidence.md)。

初始批次报告把 CONNECT 200 误记为源站响应，将 67 项 TLS 失败归入其他响应，连续传输失败停批也因此没有触发。父代理依据全部原始响应离线更正报告，并修正脚本的状态解析；没有为更正重发请求。初始报告与原始响应保留在本地，Git 保存最终报告。全部地址已尝试，不等于全部地址都取得了可用于判断存档内容的响应。
