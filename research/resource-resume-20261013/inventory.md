# 2026-10-13 本地资源补齐续跑清单

本报告是只读、无网络的候选整理；当前 3,358 条 `final-build/targets.json` 是唯一目标 SSOT。历史 `negative-coverage-review.json` 仍含 3,768 条，仅按原 URL 证据 join，不把历史多出的 410 条混入本计划。

## 状态与证据

- 当前状态：`cdx_row_evidence_no_local_entity`=14, `known_browser_gap_no_local_entity`=1727, `local_error_entity_evidence`=2, `local_plan_only_evidence`=2, `unmatched_local_evidence`=1613
- 旧 temporal review 可 join 14 对；join 模式：{'exact': 14}。历史 evidence 与当前 target 可能是 scheme/端口变体，已保留该差异。
- 本轮候选 50 项；没有执行 CDX、实体下载、批准 map 或站点重建。

## 建议顺序

1. `P1`：当前 3,358 条 SSOT 没有同时满足‘保存的 2008 status-200 image CDX 行且本地无实体’的项；14 条 CDX-only 中 3 条仅有更早图片，11 条没有有效图片 MIME，均未冒充 P1。
2. `P2`：只有更早 status-200 image 的候选；必须先有完整 exact 2008 全状态空证明，按 `pre2008_static_supplement` 单列，不得升级为 baseline。
3. `P3`：历史记录为完整前缀未索引、不完整或 unmatched；先做 exact 2008 全状态查询，prefix 空或触顶不等同于不存在。

## 候选（最多 50 项；详情见 inventory.json）

|#|优先级|类型|当前状态|events|URL|下一步|
|---:|---|---|---|---:|---|---|
|1|P2|pre2008_static_supplement_candidate|cdx_row_evidence_no_local_entity|9|`http://www.worldofwarcraft.com/info/classes/images/talents/icon-over-parchment.gif`|verify_full_exact_2008_empty_then_entity_get|
|2|P2|pre2008_static_supplement_candidate|cdx_row_evidence_no_local_entity|1|`http://www.worldofwarcraft.com/burningcrusade/townhall/images/bestiary/title-thebroken.png`|verify_full_exact_2008_empty_then_entity_get|
|3|P2|pre2008_static_supplement_candidate|cdx_row_evidence_no_local_entity|1|`https://www.worldofwarcraft.com/burningcrusade/townhall/images/bestiary/thumb-thebroken.jpg`|verify_full_exact_2008_empty_then_entity_get|
|4|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|295|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/dot.gif`|exact_cdx_2008_only|
|5|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|70|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_community.jpg`|exact_cdx_2008_only|
|6|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|39|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_player%20vs%20player.jpg`|exact_cdx_2008_only|
|7|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|37|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_the%20world.jpg`|exact_cdx_2008_only|
|8|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|31|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_reputations.jpg`|exact_cdx_2008_only|
|9|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|27|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_player%20interaction.jpg`|exact_cdx_2008_only|
|10|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|26|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_faq.jpg`|exact_cdx_2008_only|
|11|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|25|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_story.jpg`|exact_cdx_2008_only|
|12|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|22|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_getting%20started.jpg`|exact_cdx_2008_only|
|13|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|18|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_transportation.jpg`|exact_cdx_2008_only|
|14|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|14|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_items.jpg`|exact_cdx_2008_only|
|15|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|12|`http://www.worldofwarcraft.com/pvp/battlegrounds/images/warsonggulch/rewards/button-alliance-hilit.jpg`|exact_cdx_2008_only|
|16|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|12|`http://www.worldofwarcraft.com/pvp/battlegrounds/images/warsonggulch/rewards/button-horde.jpg`|exact_cdx_2008_only|
|17|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|11|`http://www.worldofwarcraft.com/shared/wow-com/images/basics/factions/alliance-honor.gif`|exact_cdx_2008_only|
|18|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|11|`http://www.worldofwarcraft.com/shared/wow-com/images/basics/factions/horde-honor.gif`|exact_cdx_2008_only|
|19|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|11|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_media.jpg`|exact_cdx_2008_only|
|20|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|10|`http://www.worldofwarcraft.com/info/encyclopedia/images/icons/508.jpg`|exact_cdx_2008_only|
|21|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/downloads/ssotd/images/screens/ss1340-thumb.jpg`|exact_cdx_2008_only|
|22|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|9|`http://www.worldofwarcraft.com/new-hp/images/countrymenu-bg.gif`|exact_cdx_2008_only|
|23|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/shared/global/talents/images/talents/arrows/down-2-green.gif`|exact_cdx_2008_only|
|24|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/shared/global/talents/images/talents/arrows/down-2-grey.gif`|exact_cdx_2008_only|
|25|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/shared/global/talents/images/talents/arrows/down-2-yellow.gif`|exact_cdx_2008_only|
|26|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/shared/global/talents/images/talents/icon-over-green.gif`|exact_cdx_2008_only|
|27|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/shared/global/talents/images/talents/icon-over-grey.gif`|exact_cdx_2008_only|
|28|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/shared/global/talents/images/talents/icon-over-yellow.gif`|exact_cdx_2008_only|
|29|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/bot-box/bot-left.gif`|exact_cdx_2008_only|
|30|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/bot-box/bot-right.gif`|exact_cdx_2008_only|
|31|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/bot-box/bot.gif`|exact_cdx_2008_only|
|32|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/bot-box/left.gif`|exact_cdx_2008_only|
|33|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/bot-box/right.gif`|exact_cdx_2008_only|
|34|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/bot-box/top-left.gif`|exact_cdx_2008_only|
|35|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/bot-box/top-right.gif`|exact_cdx_2008_only|
|36|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/bot-box/top.gif`|exact_cdx_2008_only|
|37|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/printableversion.gif`|exact_cdx_2008_only|
|38|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/reset.gif`|exact_cdx_2008_only|
|39|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/resetall.gif`|exact_cdx_2008_only|
|40|P3|needs_exact_2008_cdx|unmatched_local_evidence|9|`http://www.worldofwarcraft.com/shared/global/talents/includes/images/text-talents.gif`|exact_cdx_2008_only|
|41|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|9|`http://www.worldofwarcraft.com/shared/wow-com/images/subnav/icon_character_black.gif`|exact_cdx_2008_only|
|42|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|8|`http://www.worldofwarcraft.com/info/encyclopedia/images/icons/400.jpg`|exact_cdx_2008_only|
|43|P3|needs_exact_2008_cdx|unmatched_local_evidence|8|`http://www.worldofwarcraft.com/shared/global/talents/images/talents/arrows/down-1-green.gif`|exact_cdx_2008_only|
|44|P3|needs_exact_2008_cdx|unmatched_local_evidence|8|`http://www.worldofwarcraft.com/shared/global/talents/images/talents/arrows/down-1-grey.gif`|exact_cdx_2008_only|
|45|P3|needs_exact_2008_cdx|unmatched_local_evidence|8|`http://www.worldofwarcraft.com/shared/global/talents/images/talents/arrows/down-1-yellow.gif`|exact_cdx_2008_only|
|46|P3|needs_exact_2008_cdx|known_browser_gap_no_local_entity|8|`https://www.worldofwarcraft.com/gadgetzan/gt002/images/dalaran.jpg`|exact_cdx_2008_only|
|47|P3|needs_exact_2008_cdx|known_browser_gap_no_local_entity|8|`https://www.worldofwarcraft.com/gadgetzan/gt002/images/dalaranbg.jpg`|exact_cdx_2008_only|
|48|P3|needs_exact_2008_cdx|known_browser_gap_no_local_entity|8|`https://www.worldofwarcraft.com/gadgetzan/gt002/images/dalaranfloat.gif`|exact_cdx_2008_only|
|49|P3|needs_exact_2008_cdx|known_browser_gap_no_local_entity|7|`http://www.worldofwarcraft.com/images/parchment/plain/light.jpg`|exact_cdx_2008_only|
|50|P3|complete_prefix_needs_exact_index|known_browser_gap_no_local_entity|7|`http://www.worldofwarcraft.com/info/encyclopedia/images/icons/339.jpg`|exact_cdx_2008_only|

## 时间门禁

2008 baseline 要求 exact URL、2008 全年窗口、status 200、静态 MIME、实际正文摘要与 CDX 证据一致，并通过 ZIP/CRC/SHA 及格式校验。早于 2008 的图片只能在完整 exact 2008 空证明、明确证据路径和 opt-in validator 下作为独立补充；晚期 2008 也单独标注。HTTP 200 的 HTML soft404/Wayback 错误页不算图片。

## 可复跑接口与边界

- 查询契约：`from=20080101000000`、`to=20081231235959`、`matchType=exact`、`output=json`，不加 status/mime 过滤、collapse 或 showNumPages；保存原始 response/header/meta。
- 实体阶段使用既有 `tools/wayback_pooled_transport.py`/`tools/wayback_backup.py`，保留 TLS、Archive-only redirect、实际时间和限额；每个候选最多一次实体尝试。
- 验证命令接口：`bundled Python 3.12 tools/validate_recovery_sources.py --allow-pre2008-static-supplement <supplement-map>`。本报告不执行该命令，因为没有新增 map。
- 已知覆盖限制：当前 1,613 条 unmatched local evidence、14 条 CDX row without local entity；历史 prefix/incomplete 证据不构成物理不存在证明。

## 输入证据

- `final-build/targets.json` SHA256 `a4900bb989c3395e6ab10ef4442e4ddc591f361e8b14d29446e54a0344624345`。
- `negative-coverage-review.json` SHA256 `09ac05311b380a987aa868ef26e95a919199dc0ae428c15ea0676bf325fa72e8`（历史 3,768 条）。
- `cdx-only-temporal-review.json` SHA256 `ff64a73373c01cc23a97b8c29c5047e3c264e08b08a0be5591dca8f15c009823`（历史 422 条 temporal records）。

实际 CDX/实体网络批次需由父代理在 GitHub 部署阶段之后另行放行；本清单不会自动下载或把候选称为已恢复。
