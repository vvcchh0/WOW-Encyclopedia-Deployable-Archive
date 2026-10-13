# 2026-10-13 资源补齐 Round002 计划

此轮只读检查当前 3,358 targets、coverage-audit 5,595 items，以及四个已指定的 JSON/JSONL 证据目录；不联网，不重复 Round001/首 50。

- 选出候选：50 项；原始 metadata 文件扫描：1740 个。
- 动作：{'exact_2008_cdx': 50}。
- 若少于 50，不把剩余目标称为已覆盖；下一轮仅在父代理放行后执行。

## 选择规则

优先 coverage 显示 prefix 未完成或仅 prefix 无 exact 证据的官方 HTTP 图片。已有 2008 status-200、已恢复实体、已知 HTML/error、外部/社交/账号页面和首 50 均排除。只有完整 exact 2008 全状态结果才能决定实体阶段；pre-2008 只能在 exact 2008 完整空证明后单列。

## 候选

|#|动作|优先|events|URL|覆盖类|
|---:|---|---:|---:|---|---|
|1|exact_2008_cdx|0|3|`https://www.worldofwarcraft.com/visa/reward/images/border-bot.gif`|uncovered_or_incomplete_prefix|
|2|exact_2008_cdx|0|3|`https://www.worldofwarcraft.com/visa/reward/images/frame-bot-bg.gif`|uncovered_or_incomplete_prefix|
|3|exact_2008_cdx|0|3|`https://www.worldofwarcraft.com/visa/reward/images/frame-bot-left.gif`|uncovered_or_incomplete_prefix|
|4|exact_2008_cdx|0|3|`https://www.worldofwarcraft.com/visa/reward/images/frame-bot-right.gif`|uncovered_or_incomplete_prefix|
|5|exact_2008_cdx|0|3|`https://www.worldofwarcraft.com/visa/reward/images/frame-left-bg.gif`|uncovered_or_incomplete_prefix|
|6|exact_2008_cdx|0|3|`https://www.worldofwarcraft.com/visa/reward/images/frame-left-bot.gif`|uncovered_or_incomplete_prefix|
|7|exact_2008_cdx|0|3|`https://www.worldofwarcraft.com/visa/reward/images/frame-left-top.gif`|uncovered_or_incomplete_prefix|
|8|exact_2008_cdx|0|3|`https://www.worldofwarcraft.com/visa/reward/images/frame-right-bg.gif`|uncovered_or_incomplete_prefix|
|9|exact_2008_cdx|0|3|`https://www.worldofwarcraft.com/visa/reward/images/frame-right-bot.gif`|uncovered_or_incomplete_prefix|
|10|exact_2008_cdx|0|3|`https://www.worldofwarcraft.com/visa/reward/images/frame-right-top.gif`|uncovered_or_incomplete_prefix|
|11|exact_2008_cdx|0|3|`https://www.worldofwarcraft.com/visa/reward/images/frame-top-bg.gif`|uncovered_or_incomplete_prefix|
|12|exact_2008_cdx|0|3|`https://www.worldofwarcraft.com/visa/reward/images/frame-top-left.gif`|uncovered_or_incomplete_prefix|
|13|exact_2008_cdx|0|3|`https://www.worldofwarcraft.com/visa/reward/images/frame-top-right.gif`|uncovered_or_incomplete_prefix|
|14|exact_2008_cdx|0|3|`https://www.worldofwarcraft.com/visa/reward/images/header-float.gif`|uncovered_or_incomplete_prefix|
|15|exact_2008_cdx|0|3|`https://www.worldofwarcraft.com/visa/reward/images/header.jpg`|uncovered_or_incomplete_prefix|
|16|exact_2008_cdx|0|3|`https://www.worldofwarcraft.com/visa/reward/images/navbar-bot.gif`|uncovered_or_incomplete_prefix|
|17|exact_2008_cdx|0|3|`https://www.worldofwarcraft.com/visa/reward/images/pixel.gif`|uncovered_or_incomplete_prefix|
|18|exact_2008_cdx|0|2|`http://www.worldofwarcraft.com/gadgetzan/gt001/images/ss3-thumb.jpg`|uncovered_or_incomplete_prefix|
|19|exact_2008_cdx|0|2|`https://www.worldofwarcraft.com/visa/reward/images/submit-button.jpg`|uncovered_or_incomplete_prefix|
|20|exact_2008_cdx|0|2|`http://www.worldofwarcraft.com/visa/images/pixel.gif`|uncovered_or_incomplete_prefix|
|21|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/burningcrusade/images/art/ss28-thumb.jpg`|uncovered_or_incomplete_prefix|
|22|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/burningcrusade/images/art/ss29-thumb.jpg`|uncovered_or_incomplete_prefix|
|23|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/burningcrusade/images/art/ss31-thumb.jpg`|uncovered_or_incomplete_prefix|
|24|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/burningcrusade/images/art/ss32-thumb.jpg`|uncovered_or_incomplete_prefix|
|25|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/burningcrusade/images/art/ss33-thumb.jpg`|uncovered_or_incomplete_prefix|
|26|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/burningcrusade/images/screenshots/ss233-thumb.jpg`|uncovered_or_incomplete_prefix|
|27|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/burningcrusade/images/screenshots/ss234-thumb.jpg`|uncovered_or_incomplete_prefix|
|28|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/burningcrusade/images/screenshots/ss235-thumb.jpg`|uncovered_or_incomplete_prefix|
|29|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/burningcrusade/images/screenshots/ss236-thumb.jpg`|uncovered_or_incomplete_prefix|
|30|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/burningcrusade/images/screenshots/ss237-thumb.jpg`|uncovered_or_incomplete_prefix|
|31|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/burningcrusade/images/screenshots/ss238-thumb.jpg`|uncovered_or_incomplete_prefix|
|32|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/burningcrusade/images/screenshots/ss239-thumb.jpg`|uncovered_or_incomplete_prefix|
|33|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/burningcrusade/images/screenshots/ss240-thumb.jpg`|uncovered_or_incomplete_prefix|
|34|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/burningcrusade/images/screenshots/ss241-thumb.jpg`|uncovered_or_incomplete_prefix|
|35|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/contests/05-02-valentines-screenshots/winners/images/ss02-thumb.jpg`|uncovered_or_incomplete_prefix|
|36|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/contests/05-03-7-wonders/images/winners/ss01-thumb.jpg`|uncovered_or_incomplete_prefix|
|37|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/contests/05-03-7-wonders/images/winners/ss02-thumb.jpg`|uncovered_or_incomplete_prefix|
|38|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/contests/05-03-7-wonders/images/winners/ss03-thumb.jpg`|uncovered_or_incomplete_prefix|
|39|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/contests/05-03-7-wonders/images/winners/ss04-thumb.jpg`|uncovered_or_incomplete_prefix|
|40|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/contests/05-03-7-wonders/images/winners/ss05-thumb.jpg`|uncovered_or_incomplete_prefix|
|41|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/contests/05-03-7-wonders/images/winners/ss06-thumb.jpg`|uncovered_or_incomplete_prefix|
|42|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/contests/05-10-pumpkin/images/winners/ss1-thumb.jpg`|uncovered_or_incomplete_prefix|
|43|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/contests/05-10-pumpkin/images/winners/ss2-thumb.jpg`|uncovered_or_incomplete_prefix|
|44|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/contests/05-10-pumpkin/images/winners/ss3-thumb.jpg`|uncovered_or_incomplete_prefix|
|45|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/contests/05-10-pumpkin/images/winners/ss4-thumb.jpg`|uncovered_or_incomplete_prefix|
|46|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/contests/05-10-pumpkin/images/winners/ss5-thumb.jpg`|uncovered_or_incomplete_prefix|
|47|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/contests/05-10-ss/images/winners/ss1-thumb.jpg`|uncovered_or_incomplete_prefix|
|48|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/contests/05-10-ss/images/winners/ss2-thumb.jpg`|uncovered_or_incomplete_prefix|
|49|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/contests/05-10-ss/images/winners/ss3-thumb.jpg`|uncovered_or_incomplete_prefix|
|50|exact_2008_cdx|0|1|`http://www.worldofwarcraft.com/contests/05-10-ss/images/winners/ss4-thumb.jpg`|uncovered_or_incomplete_prefix|

## 执行约束

最多 50 项、最多 4 条 Archive 流、每请求 60 秒、批次 1,200 秒、实体 16 MiB、响应累计 128 MiB、无自动重试；保留原始 CDX raw/meta/query URL。全局 workspace 预算 14,000,000,000 bytes，D 盘保留 11,000,000,000 bytes。图片必须通过实际 MIME、CDX SHA1、ZIP/CRC/SHA256 和 Pillow 完整解码；baseline、late-2008、pre-2008 分开。

Round002 runner 等待父代理 Pages/网络门禁；本文件本身没有执行任何请求。
