# 资源下载连接诊断与修复尝试

2026-10-14，在 direct 优先、失败后代理的约定下，对上一批下载故障做了分阶段诊断。本轮尚未取得新的有效图片；原始下载及已接入的资源继续保留。

## 当前判断

- **默认直连在 TCP 连接前超时。** 三个独立控制请求完成了 DNS 查询，未建立 TCP 或 TLS，均以 curl 28 结束。
- **代理通道可以工作，回放请求另有问题。** 同一代理能取得 `archive.org/robots.txt`（200）及 `web.archive.org/robots.txt`（404）；已知 JPEG 回放返回 429、162 字节 nginx 错误页，与此前回放失败的响应模式一致。没有 `Retry-After`。现有证据不能确定产生限流响应的具体中间层。
- **单改解析结果不足以修复直连。** 正确的 Cloudflare HTTPS DNS A 查询取得 `207.241.237.3`；仅对一次请求使用 `--resolve` 后，TCP 在约 0.263 秒建立，但在 TLS 完成前连接被重置，curl 35，未收到 HTTP 或图片内容。不能把故障只归为 DNS，也不能据此确认某个具体过滤设备。

## 已做的修复尝试

本机两种解析方式返回不同地址，因此增加了进程内 HTTPS DNS 验证。Google direct 请求超时，代理路径的 Schannel 吊销检查离线失败；保留了验证，没有关闭它。Cloudflare direct 在 TCP 后重置，代理可以访问其 HTTPS DNS 服务。

第一次 DNS 探测误用了 `type=255`（ANY），返回不支持；该结果只能说明这次查询类型不受支持。随后更正为明确的 `type=A`，取得 HTTP 200、DNS Status 0、Question type 1 的回答。Cloudflare 的 JSON API 支持按类型查询，见[官方参数说明](https://developers.cloudflare.com/1.1.1.1/encryption/dns-over-https/make-api-requests/dns-json/)。

A 回答仅用于当次直连控制；其 TTL 为 120 秒，没有写入系统 DNS 或 hosts，也没有作为下载器的固定地址。`AD=false`，因此这次不是 DNSSEC 验证成功的证据。TLS 证书校验始终保留，代理、系统网络和浏览器保护没有修改。

## 结果与下一步

本轮共 12 次小型请求尝试，落盘响应正文共 927 字节，没有有效图片或新的来源映射。[诊断验收摘要](../research/network-recovery-20261014/acceptance.json)记录分阶段结果、时序指标和原始证据摘要。

在目前网络条件下，没有验证可用的回放下载路径。若提供另一条已经可用的代理路径，可先对一个已知图片做控制，再按当前路由过滤后获取小批缺项；否则保留已有材料并继续离线修复，避免重复请求同一 429。后续每批仍需检查实际日期、CDX SHA1、格式和完整解码，错误页不计为素材。

另对既有 3 张有效 JPEG、但 CDX 摘要不匹配的图片做了纯离线复核。它们的路径、时间和格式对应，但重新计算的 SHA1 均不在已保存的完整 87 行索引中，无法证明可归入另一条捕获；保留原文件，未计为新增。[离线复核](../research/network-recovery-20261014/offline-salvage/summary.md)
