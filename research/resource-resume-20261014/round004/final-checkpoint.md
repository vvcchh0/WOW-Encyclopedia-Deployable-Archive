# Round004 final checkpoint

范围：历史新闻及活动页缺图。候选 29 项；本次权威收尾结果为 **18 项成功、2 项 TLS 传输失败、9 项尚未请求**。完整 source map 见 `entity-source-map.json`。

整合复核显示，这 18 项虽然取得了有效历史回放，但全部已经存在于部署版 `build-manifest`，且 `derived_sha256` 逐字节一致。因此本批新增唯一资源为 **0**，与已有资源重复的实体为 **18**，不能把它们表述为部署缺口补齐。复核证据：`research/related-sites-20261014/integration/news-existing-route-check.json`。

## 请求记录

- 首轮实际尝试 29 次。由于 curl 启动前未创建 `entity/raw` 与 `entity/headers` 父目录，全部为本地 `curl exit 23`；原始 meta/stderr 保存在 `entity/attempt-001-local-write-error/`。
- 修正 `mkdir` 后第二轮实际尝试 20 次，18 项通过 HTTP 200、图片 MIME/magic、Pillow、SHA-256 与 CDX SHA1(base32)；2 项为 `curl exit 56` 的 Schannel `missing close_notify`。
- 初轮空 body 的 Pillow 错误含进程内存地址，未形成稳定的三次同错指纹；这一停批偏离已记录，后续按 curl exit code 分类。
- 额外只做了 1 次诊断 probe，结果保存在 `entity/probe/rank013-probe-result.json`，不自动并入 source map。之后已停止网络请求。

## TLS 失败

- rank 13: `http://www.worldofwarcraft.com/news/images/06-05/5-18-06-1.jpg` — curl 56, transport_tls_close_notify_curl_exit_56
- rank 19: `http://www.worldofwarcraft.com/news/images/06-05/5-4-06-1.jpg` — curl 56, transport_tls_close_notify_curl_exit_56

## 尚未请求

- rank 21: `http://www.worldofwarcraft.com/news/images/06-05/5-4-06-3.jpg`
- rank 22: `http://www.worldofwarcraft.com/news/images/06-05/eggs.jpg`
- rank 23: `http://www.worldofwarcraft.com/news/images/06-05/emusic-thumb.jpg`
- rank 24: `http://www.worldofwarcraft.com/news/images/06-05/murloc-egg-thumb.jpg`
- rank 25: `http://www.worldofwarcraft.com/news/images/06-05/thaddius.jpg`
- rank 26: `http://www.worldofwarcraft.com/news/images/06-05/wallpaper1-thumb.jpg`
- rank 27: `http://www.worldofwarcraft.com/news/images/06-05/wallpaper2-thumb.jpg`
- rank 28: `http://www.worldofwarcraft.com/news/images/06-05/wallpaper3-thumb.jpg`
- rank 29: `http://www.worldofwarcraft.com/news/images/06-05/zeppelin-thumb.jpg`

## Provenance

复用的选择证据来自 `research/resource-recovery-2008/full-page-static-cdx-selection.json`；source selection SHA-256 为 `978498a4b9ceaae4648273e9e9b47518e02da12f27a9c4781f0b505585ef2473`。该轮没有重新验证全年 CDX 完整性，冻结队列与原始选取证据保持引用关系。

本 checkpoint 只整理 Round004 已存在的本地素材，不构建、不部署，也不修改冻结源或 root 的 integration 目录。
