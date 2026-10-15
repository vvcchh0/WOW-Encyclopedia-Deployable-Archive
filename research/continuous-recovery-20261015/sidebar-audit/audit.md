# Sidebar local audit (2026-10-15)

本审计只读取本地输入，未执行网络请求。逐条记录来自 `research/navigation-gaps-20261015/inventory.json`；原始纳入范围 588 条，原始排除 653 条，总账 1241 条。其中 `Legacy menu` 的 579 条被标记为 `parser_unclassified_legacy` 并重新纳入有效审计；真正范围外记录为 74 条。当前页面与资源判定按 `.scratch/pages-resources-20261015-v8` 及其 `__offline/route-map.json`、`export-provenance.json` 计算。

## Conservation and inputs

- Menu conservation: original in-scope 588/588; legacy reclassified 579/579; effective auditable 1167/1167; true excluded 74/74; total 1241/1241.
- Original section conservation: {'Community': 58, 'Game Guide': 470, 'Media': 33, 'News': 10, 'Workshop': 17} == {'Community': 58, 'Game Guide': 470, 'Media': 33, 'News': 10, 'Workshop': 17}.
- Effective auditable section counts: {'Community': 58, 'Game Guide': 470, 'Legacy menu': 579, 'Media': 33, 'News': 10, 'Workshop': 17}.
- True excluded section counts: {'Account': 26, 'Forums': 38, 'Support': 9, 'WoW Main': 1}.
- Frozen `offline/build-manifest.json`: `397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459`; acceptance expected `397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459`; unchanged=True.
- Latest v8 acceptance: accepted=True, output_files=8444, browser scenarios=7, passed=7, unit tests=55 with failures=0.

## Current effective audit status

- Page status: `{'business_or_sensitive': 6, 'external_or_dynamic': 54, 'missing_export_route': 40, 'resolved': 914, 'resolved_recovered': 3, 'resolved_via_alias': 150}`
- Asset status: `{'local_dependencies_resolved': 127, 'not_available': 100, 'partial_missing_assets': 940}`
- Interaction status: `{'legacy_plugin_static_indication': 902, 'localized_form_static_indication': 66, 'localized_script_static_indication': 89, 'not_available': 100, 'static_surface_static_indication': 10}`
- Inventory status retained for history: `{'content_route': 563, 'external_or_dynamic': 22, 'missing_export_route': 3, 'out_of_scope_business_or_external': 579}`
- Open gap records: 1120; historical records recovered by v8: 3.

`resolved_recovered` means the old inventory marked the entry external/dynamic or missing, while the current v8 route and page are present. It is retained in `historical_resolutions` and is not counted as an open gap. `scope_excluded` records are accounted for but are not treated as missing pages.

## Highest-value open proposals

- `sidebar-417` P0 `missing_page_or_route` legacy_news_rss_archives；菜单 26 条；placeholder 0；最新派生路由索引没有页面映射或文件，不能用假页面填充。
- `sidebar-423` P0 `missing_page_or_route` legacy_news_html_archives；菜单 9 条；placeholder 0；最新派生路由索引没有页面映射或文件，不能用假页面填充。
- `sidebar-449` P0 `missing_page_or_route` /ptr；菜单 2 条；placeholder 0；最新派生路由索引没有页面映射或文件，不能用假页面填充。
- `sidebar-436` P0 `missing_page_or_route` /pvp/battlegrounds/battlegroups.html；菜单 1 条；placeholder 0；最新派生路由索引没有页面映射或文件，不能用假页面填充。
- `sidebar-442` P0 `missing_page_or_route` /burningcrusade/townhall/professions.html；菜单 1 条；placeholder 0；最新派生路由索引没有页面映射或文件，不能用假页面填充。
- `sidebar-448` P0 `missing_page_or_route` /wrath/artwork.xml；菜单 1 条；placeholder 0；最新派生路由索引没有页面映射或文件，不能用假页面填充。
- `sidebar-192` P1 `missing_key_assets` .scratch/pages-resources-20261015-v8/info/basics/factions/zandalar/quests.html；菜单 2 条；placeholder 218；最新 v8 已有页面，但 provenance 标记 218 个 placeholder；这是可验证的本地资源缺口。
- `sidebar-050` P1 `missing_key_assets` .scratch/pages-resources-20261015-v8/community/tournaments/euregionals/index.html；菜单 1 条；placeholder 152；最新 v8 已有页面，但 provenance 标记 152 个 placeholder；这是可验证的本地资源缺口。
- `sidebar-308` P1 `missing_key_assets` .scratch/pages-resources-20261015-v8/insider/11/arena.xml.html；菜单 2 条；placeholder 22；最新 v8 已有页面，但 provenance 标记 22 个 placeholder；这是可验证的本地资源缺口。
- `sidebar-090` P1 `missing_key_assets` .scratch/pages-resources-20261015-v8/info/basics/highleveloptions.html；菜单 2 条；placeholder 19；最新 v8 已有页面，但 provenance 标记 19 个 placeholder；这是可验证的本地资源缺口。

## Group status by section

- `Community`: 58 records; page `{'external_or_dynamic': 3, 'resolved': 46, 'resolved_via_alias': 9}`; assets `{'local_dependencies_resolved': 10, 'not_available': 3, 'partial_missing_assets': 45}`.
- `Game Guide`: 470 records; page `{'external_or_dynamic': 13, 'resolved': 387, 'resolved_recovered': 1, 'resolved_via_alias': 69}`; assets `{'local_dependencies_resolved': 32, 'not_available': 13, 'partial_missing_assets': 425}`.
- `Legacy menu`: 579 records; page `{'business_or_sensitive': 6, 'external_or_dynamic': 32, 'missing_export_route': 40, 'resolved': 450, 'resolved_via_alias': 51}`; assets `{'local_dependencies_resolved': 65, 'not_available': 78, 'partial_missing_assets': 436}`.
- `Media`: 33 records; page `{'external_or_dynamic': 3, 'resolved': 21, 'resolved_recovered': 1, 'resolved_via_alias': 8}`; assets `{'local_dependencies_resolved': 9, 'not_available': 3, 'partial_missing_assets': 21}`.
- `News`: 10 records; page `{'external_or_dynamic': 2, 'resolved': 7, 'resolved_via_alias': 1}`; assets `{'local_dependencies_resolved': 5, 'not_available': 2, 'partial_missing_assets': 3}`.
- `Workshop`: 17 records; page `{'external_or_dynamic': 1, 'resolved': 3, 'resolved_recovered': 1, 'resolved_via_alias': 12}`; assets `{'local_dependencies_resolved': 6, 'not_available': 1, 'partial_missing_assets': 10}`.

## Evidence and use

Every record in `audit.json` carries the source menu path and line, the inventory index, current route-map result, resolved file hash when present, and provenance/dependency evidence when available. `repair-proposals.json` contains suggestions only; no production map, frozen source, build script, test, or deployment file was edited.

Known v8 acceptance gaps retained as context: ['Most US SSOTD images and all original SSOTD thumbnails remain missing.', 'Game Guide player screenshot original/thumbnail pairs remain unrecovered.', 'PvP intro.swf and Trial artwork remain unrecovered.'].
