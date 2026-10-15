# Clash 本机路由/DNS/TLS 只读证据（2026-10-15）

检查范围：本机运行中的 `clash-win64.exe`（PID 21732）及其已定位的配置、profile、日志；未访问网络、未调用控制器 API、未改配置/规则/进程、未 flush DNS、未重启。代理测试与客户端 TLS 批次由父代理完成，本记录不重复。

## 配置定位

- Clash 可执行文件：`D:\Clash\resources\static\files\win\x64\clash-win64.exe`。
- 父 GUI 进程的用户数据目录参数解析为 `C:\Users\17630\AppData\Roaming\clash_win`；其中 renderer 日志存在，但未发现 profile/config 文件。
- Core 配置目录：`C:\Users\17630\.config\clash`。
- 基础 `config.yaml`（15/10 11:01:40）仅有 `mixed-port: 7890`、`allow-lan: true`、`ipv6: false`、控制器字段和 secret；secret 未读取/记录。
- profile 目录中当前修改时间最新且唯一的大 profile 为 `profiles\1755624189306.yml`（506029 bytes，15/10 11:01:51）。订阅 URL、代理账号和节点原名均未记录。

## DNS 配置边界

在 `profiles\1755624189306.yml` 的 DNS block（第 11 行起）观察到：

- `enable: true`、`use-hosts: true`。
- `default-nameserver` 含 `119.29.29.29`、`223.5.5.5`、`223.6.6.6`、`114.114.114.114`、`8.8.8.8`、`1.12.12.12`、`120.53.53.53`，以及若干 `tls://` 上游；其协议路径未记录。
- `nameserver` 含 `119.29.29.29`、`223.5.5.5`、`223.6.6.6`、`dot.pub`、`1.12.12.12`、`120.53.53.53` 等；存在 `tls://` 上游。
- 未发现显式 `enhanced-mode`、`fake-ip-range` 或 `fake-ip-filter` 字段。因此本 profile 没有证据证明启用了 fake-ip；也不能仅凭缺省字段断言 Clash core 的实际默认模式。
- 未发现将 `web.archive.org` 或 `archive.org` 明确绑定到某个 DNS policy 的条目。`use-hosts: true` 表示本机 hosts 可能参与解析，但本次未修改/flush，也未把系统 DNS 与 Clash 上游差异解释为唯一根因。

## 域名规则

仅在该 profile 中找到两条与目标相关的匹配（第 1113、1861 行）：目标为 `archive.org`，均使用同一非内建动作/节点选择器；动作或节点原名以 `sha256` 前 12 位脱敏为 `a82f9b37b551`。没有 `web.archive.org` 的专门规则，也没有 `DIRECT` 字面动作证据；因而可支持的边界是：`archive.org` 后缀流量会进入一个代理/选择器动作，而非被显式 `DIRECT` 规则短路。选择器当时的具体出口节点未从配置静态内容确定。

## 近期日志

- 当前 core 日志 `C:\Users\17630\.config\clash\logs\2026-10-15-110142.log`（15/10 11:01:42，248413 bytes）含 131 行出现 `web.archive.org`/`archive.org`；这些行都只有连接/代理类信号，未出现 `EOF`、`reset`、`timeout`、`TLS`、`handshake`、`DNS` 或 `error` 关键词。行号与整行哈希已保留在本次只读扫描输出中，未把日志原文写入记录。
- 前一份 `2026-10-14-160501.log` 含 641 个目标行，其中仅 2 行同时命中 error、2 行 timeout；其余主要为 connect/代理类记录。没有从日志静态摘出可归因于目标 TLS 的 EOF/reset 证据。
- `AppData\Roaming\clash_win\logs\renderer.log` 与 `.old.log` 未命中目标域名；当前 core 空日志和 renderer 日志不能证明连接成功或失败。

## 因果边界

静态配置支持“目标后缀走代理选择器，DNS 由 Clash profile 的显式上游/hosts 逻辑处理，未显式 fake-ip”的判断；它不支持“目标必定 DIRECT”“目标必定使用系统 DNS”或“DNS 地址差异是唯一根因”。父代理的受控尝试显示同一时段存在成功与 TLS 失败并发，故本地日志中的 connect 记录也不能推出持续不可达或单一 TLS 客户端栈故障。当前最强结论是：目标连接在代理路径/出口或时段并发上呈间歇性异常，TLS EOF/reset 的具体发生点仍需依赖父代理的跨客户端结果与代理出口证据。
