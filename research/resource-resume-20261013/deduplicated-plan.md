# 2026-10-13 资源补齐去重计划

此文件只读扫描四个指定的本地证据目录，未联网、未解压 ZIP、未重试任何请求。原始 50 项初选保存在 `inventory.json`；本报告按 URL scheme/default-port 变体去重，但保留原 logical URL。

- 扫描文件：1740 个 JSON/JSONL。
- 动作分布：{'noimage': 3, 'reuseproof': 17, 'skipalreadyfailed': 30}。
- evidence kind：{'exact_2008_cdx_evidence': 3, 'failure_or_error': 98, 'url_mention_only': 55, 'exact_2008_empty_proof': 18, 'html_or_nonimage_row': 53, 'coverage_only': 110}。
- `reuseproof` 不重新下载；`skipalreadyfailed` 保留失败史且没有新依据；`noimage` 不满足 pre-2008 门禁；只有 `fetch_new` 可在父代理明确放行后进入新的 exact-CDX 阶段。

## 续跑顺序

1. 先处理 `fetch_new`：每项一次全年 exact 2008 CDX；只有完整空或有效 image 行才继续下一步。
2. `pre2008_static_supplement_candidate` 必须有完整 exact-2008 空证明；已有非空 HTML/error 证据的项目保持 `noimage`。
3. `reuseproof` 仅按已有 map/catalog 接入，不重新发 GET；`skipalreadyfailed` 不做同条件盲重试。

## 项目

|去重序|原排名|动作|角色|events|URL|
|---:|---:|---|---|---:|---|
|1|1|noimage|pre2008_static_supplement_candidate|9|`http://www.worldofwarcraft.com/info/classes/images/talents/icon-over-parchment.gif`|
|2|2|noimage|pre2008_static_supplement_candidate|1|`http://www.worldofwarcraft.com/burningcrusade/townhall/images/bestiary/title-thebroken.png`|
|3|3|noimage|pre2008_static_supplement_candidate|1|`https://www.worldofwarcraft.com/burningcrusade/townhall/images/bestiary/thumb-thebroken.jpg`|
|4|4|reuseproof|complete_prefix_needs_exact_index|295|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/dot.gif`|
|5|5|reuseproof|complete_prefix_needs_exact_index|70|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_community.jpg`|
|6|6|reuseproof|complete_prefix_needs_exact_index|39|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_player%20vs%20player.jpg`|
|7|7|reuseproof|complete_prefix_needs_exact_index|37|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_the%20world.jpg`|
|8|8|reuseproof|complete_prefix_needs_exact_index|31|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_reputations.jpg`|
|9|9|reuseproof|complete_prefix_needs_exact_index|27|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_player%20interaction.jpg`|
|10|10|reuseproof|complete_prefix_needs_exact_index|26|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_faq.jpg`|
|11|11|reuseproof|complete_prefix_needs_exact_index|25|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_story.jpg`|
|12|12|reuseproof|complete_prefix_needs_exact_index|22|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_getting%20started.jpg`|
|13|13|reuseproof|complete_prefix_needs_exact_index|18|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_transportation.jpg`|
|14|14|reuseproof|complete_prefix_needs_exact_index|14|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_items.jpg`|
|15|15|reuseproof|complete_prefix_needs_exact_index|12|`http://www.worldofwarcraft.com/pvp/battlegrounds/images/warsonggulch/rewards/button-alliance-hilit.jpg`|
|16|16|reuseproof|complete_prefix_needs_exact_index|12|`http://www.worldofwarcraft.com/pvp/battlegrounds/images/warsonggulch/rewards/button-horde.jpg`|
|17|17|skipalreadyfailed|complete_prefix_needs_exact_index|11|`http://www.worldofwarcraft.com/shared/wow-com/images/basics/factions/alliance-honor.gif`|
|18|18|reuseproof|complete_prefix_needs_exact_index|11|`http://www.worldofwarcraft.com/shared/wow-com/images/basics/factions/horde-honor.gif`|
|19|19|reuseproof|complete_prefix_needs_exact_index|11|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_media.jpg`|
|20|20|reuseproof|complete_prefix_needs_exact_index|10|`http://www.worldofwarcraft.com/info/encyclopedia/images/icons/508.jpg`|
|21|21|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/downloads/ssotd/images/screens/ss1340-thumb.jpg`|
|22|22|skipalreadyfailed|complete_prefix_needs_exact_index|9|`http://www.worldofwarcraft.com/new-hp/images/countrymenu-bg.gif`|
|23|23|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/shared/global/talents/images/talents/arrows/down-2-green.gif`|
|24|24|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/shared/global/talents/images/talents/arrows/down-2-grey.gif`|
|25|25|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/shared/global/talents/images/talents/arrows/down-2-yellow.gif`|
|26|26|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/shared/global/talents/images/talents/icon-over-green.gif`|
|27|27|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/shared/global/talents/images/talents/icon-over-grey.gif`|
|28|28|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/shared/global/talents/images/talents/icon-over-yellow.gif`|
|29|29|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/bot-box/bot-left.gif`|
|30|30|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/bot-box/bot-right.gif`|
|31|31|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/bot-box/bot.gif`|
|32|32|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/bot-box/left.gif`|
|33|33|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/bot-box/right.gif`|
|34|34|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/bot-box/top-left.gif`|
|35|35|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/bot-box/top-right.gif`|
|36|36|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/bot-box/top.gif`|
|37|37|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/printableversion.gif`|
|38|38|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/reset.gif`|
|39|39|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/resetall.gif`|
|40|40|skipalreadyfailed|needs_exact_2008_cdx|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/text-talents.gif`|
|41|41|reuseproof|complete_prefix_needs_exact_index|9|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_character_black.gif`|
|42|42|skipalreadyfailed|complete_prefix_needs_exact_index|8|`http://www.worldofwarcraft.com/info/encyclopedia/images/icons/400.jpg`|
|43|43|skipalreadyfailed|needs_exact_2008_cdx|8|`http://www.worldofwarcraft.com/shared/global/talents/images/talents/arrows/down-1-green.gif`|
|44|44|skipalreadyfailed|needs_exact_2008_cdx|8|`http://www.worldofwarcraft.com/shared/global/talents/images/talents/arrows/down-1-grey.gif`|
|45|45|skipalreadyfailed|needs_exact_2008_cdx|8|`http://www.worldofwarcraft.com/shared/global/talents/images/talents/arrows/down-1-yellow.gif`|
|46|46|skipalreadyfailed|needs_exact_2008_cdx|8|`https://www.worldofwarcraft.com/gadgetzan/gt002/images/dalaran.jpg`|
|47|47|skipalreadyfailed|needs_exact_2008_cdx|8|`https://www.worldofwarcraft.com/gadgetzan/gt002/images/dalaranbg.jpg`|
|48|48|skipalreadyfailed|needs_exact_2008_cdx|8|`https://www.worldofwarcraft.com/gadgetzan/gt002/images/dalaranfloat.gif`|
|49|49|skipalreadyfailed|needs_exact_2008_cdx|7|`http://www.worldofwarcraft.com/images/parchment/plain/light.jpg`|
|50|50|skipalreadyfailed|complete_prefix_needs_exact_index|7|`http://www.worldofwarcraft.com/info/encyclopedia/images/icons/339.jpg`|

## 证据与门禁

全年查询契约为 `from=20080101000000`、`to=20081231235959`、`matchType=exact`、`output=json`，不使用 status/MIME filter、collapse 或 showNumPages。实体获取需保留实际 Memento、响应 MIME、原始字节、CDX digest 和 ZIP/CRC/SHA 校验。

下一阶段需要父代理明确放行网络；本报告不改变批准 map、不把失败证据改写为缺失。
