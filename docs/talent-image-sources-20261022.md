# 天赋图像补充的来源与匹配边界

这份记录区分三个来源层：2008 年页面原本请求的图像路径、后来 WotLK 天赋模拟器中同路径的图像、以及经人工核对后用于填补缺失目标的跨路径图像。补充的是图像文件；旧站的天赋数据、名称、等级、描述和加点逻辑继续使用 2008 年内容。

## 来源与历史边界

基础包有 986 张 36×36 图像，在缓存的 [CraftedRO WotLK 3.3.5a 仓库](https://github.com/CraftedRO/Offline-talent-calculator-for-WotLK-3.3.5a) 中逐路径找到相同文件名和目录。该组通过严格的同路径候选筛选；它们是后期相关素材，不是已证明的 2008 原图。[基础映射](../research/continuous-recovery-20261021/integration/related-talent-icons/input-map.json) 与 [基础来源验收](../research/continuous-recovery-20261021/publication/root-talent-related-source-acceptance.json) 固定了仓库 commit、ZIP 哈希和对象哈希。该 ZIP 于 2026-10-21 本地取得；原始捕获日期为 null。

后续映射只针对缺失目标显式登记后期来源路径。每行代表同一个目标图标的 `.jpg` 与 `-off.jpg` 两个状态；行中的来源路径也各自对应一对 JPEG。文件原字节被保留，没有重新编码。审计将它们标为 `later_related_source`，原图像是否与 2008 年像素相同仍为 `unknown`；两轮新增来源都没有把任何图像认定为恢复的 2008 原图。

## v55：10 个同职业天赋，20 张图

[v55 输入映射](../research/continuous-recovery-20261022/integration/related-talent-icons-v55/input-map.json) 在 986 项基础上加入 20 个 on/off 目标；[决定记录](../research/continuous-recovery-20261022/integration/related-talent-icons-v55/decision.json) 和 [v55 代码验收](../research/continuous-recovery-20261022/root-v55-code-acceptance.json) 固定了范围与理由。路径以下均相对于 `shared/global/talents/`；旧目标路径前加 `/shared/global/talents/` 即其请求 URL。v55 的十项都是同职业素材，因天赋移树、拼写变化或相关树位置变化而使用显式映射。

| 职业与天赋 | 缺失的 2008 目标 → 后期来源路径 | 匹配理由与已知差异 |
|---|---|---|
| Paladin · Divine Strength | `paladin/images/holy/divinestrength.jpg` → `paladin/images/protection/divinestrength.jpg` | 同职业、同名和力量效果；后期每级为 3%，旧数据为 2%。 |
| Paladin · Improved Concentration Aura | `paladin/images/protection/improvedconcentrationaura.jpg` → `paladin/images/holy/improvedconcentrationaura.jpg` | 同名及沉默/打断持续时间效果；后期多了任一光环激活条件。 |
| Paladin · Improved Judgement | `paladin/images/retribution/improvedjudgement.jpg` → `paladin/images/retribution/improvedjudgements.jpg` | 同职业、同树；后期文件名多一个 `s`，描述均为缩短审判冷却 1 或 2 秒。 |
| Hunter · Scatter Shot | `hunter/images/marksmanship/scattershot.jpg` → `hunter/images/survival/scattershot.jpg` | 同一主动技能与效果：50% 武器伤害、4 秒迷惑；从射击树移至生存树。 |
| Hunter · Readiness | `hunter/images/survival/readiness.jpg` → `hunter/images/marksmanship/readiness.jpg` | 同一冷却重置技能；后期不重置 Bestial Wrath，冷却为 3 分钟而旧版为 5 分钟。 |
| Rogue · Relentless Strikes | `rogue/images/assassination/relentlessstrikes.jpg` → `rogue/images/subtlety/relentlessstrikes.jpg` | 同职业；满级效果均为终结技按连击点数几率恢复能量，后期将相同最高几率拆成五级。 |
| Warrior · Improved Intercept | `warrior/images/arms/improvedintercept.jpg` → `warrior/images/fury/improvedintercept.jpg` | 同职业、两级冷却缩短效果相同；从武器树移至狂怒树。 |
| Warrior · Tactical Mastery | `warrior/images/protection/tacticalmastery.jpg` → `warrior/images/arms/tacticalmastery.jpg` | 同职业，保留怒气与防御姿态威胁效果对应；从防护树移至武器树。 |
| Warrior · Sweeping Strikes | `warrior/images/fury/sweepingstrikes.jpg` → `warrior/images/arms/sweepingstrikes.jpg` | 同职业、相邻目标追加攻击技能；后期为 5 次攻击，旧版为 10 次挥击。 |
| Warrior · Weapon Mastery | `warrior/images/fury/weaponmastery.jpg` → `warrior/images/arms/weaponmastery.jpg` | 同名、同职业；两级躲闪/缴械效果描述一致。 |

v55 的 [代码验收](../research/continuous-recovery-20261022/root-v55-code-acceptance.json)、[导出验收](../research/continuous-recovery-20261022/root-v55-export-acceptance.json) 与 [浏览器验收](../research/continuous-recovery-20261022/root-v55-browser-acceptance.json) 记录了既有 986 项保留、20 项补充和旧天赋数据保留。

## v56：9 个正式名称相同的天赋，18 张图

v56 叠加在 v55 的 1006 项之上，增加 18 个缺失图像状态，合计 1024 项。选择条件收紧为同职业且后期数据中的正式天赋名称相同；匹配理由及版本差异逐条记录在 [v56 决定](../research/continuous-recovery-20261022/integration/related-talent-icons-v56/decision.json)。[输入映射](../research/continuous-recovery-20261022/integration/related-talent-icons-v56/input-map.json) 与独立的 [v56 来源验收](../research/continuous-recovery-20261022/integration/related-talent-icons-v56/root-source-acceptance.json) 绑定 18 个原 JPEG 字节、旧新数据行与哈希；验收确认旧天赋数据行未改变，图像原始像素身份仍未知。

| 职业与正式名称 | 缺失的 2008 目标 → 后期来源路径 | 匹配理由与已知差异 |
|---|---|---|
| Mage · Molten Shields | `mage/images/fire/improvedfireward.jpg` → `mage/images/fire/moltenshields.jpg` | 同职业、同正式名称和 Fire Ward 效果；旧图像标签为 Improved Fire Ward，后期还包括 Frost Ward。 |
| Paladin · Guardian’s Favor | `paladin/images/protection/guardiansfavor.jpg` → `paladin/images/protection/guardian'sfavor.jpg` | 同职业、同正式名称；Blessing 后改称 Hand，防护/自由祝福效果对应。 |
| Rogue · Puncturing Wounds | `rogue/images/assassination/improvedbackstab.jpg` → `rogue/images/assassination/puncturingwounds.jpg` | 同职业、同正式名称及背刺效果；旧图像标签为 Improved Backstab。 |
| Rogue · Dirty Tricks | `rogue/images/subtlety/improvedsap.jpg` → `rogue/images/subtlety/dirtytricks.jpg` | 同职业、同正式名称；致盲/闷棍距离与能量消耗效果对应，机制细节以版本数据为准。 |
| Shaman · Earth’s Grasp | `shaman/images/elemental/earth'sgrasp.jpg` → `shaman/images/enhancement/earth'sgrasp.jpg` | 同职业、同正式名称；由元素树移至增强树，后期另增加冷却效果。 |
| Warrior · Death Wish | `warrior/images/arms/deathwish.jpg` → `warrior/images/fury/deathwish.jpg` | 同职业、同正式名称；由武器树移至狂怒树，后期版本不含恐惧免疫。 |
| Warrior · Improved Disciplines | `warrior/images/arms/improveddisciplines.jpg` → `warrior/images/protection/improveddisciplines.jpg` | 同职业、同正式名称；由武器树移至防护树，冷却缩减/持续时间数值有变化。 |
| Warrior · Improved Thunder Clap | `warrior/images/arms/improvedthunderclap.jpg` → `warrior/images/protection/improvedthunderclap.jpg` | 同职业、同正式名称；由武器树移至防护树，雷霆一击伤害修正有变化。 |
| Warrior · Improved Slam | `warrior/images/fury/improvedslam.jpg` → `warrior/images/arms/improvedslam.jpg` | 同职业、同正式名称；由狂怒树移至武器树，后期改为缩短挥击时间而非施法时间。 |

该清单没有把后期描述或天赋机制写回旧页面。不同版本的效果变化是选择“相关图像”而非等同版本数据的原因之一；不能据此推断两代图像像素相同。

## 未映射候选与其他素材

[缺口语义审计](../research/continuous-recovery-20261022/talent-icon-remaining-audit/audit.json) 按目标路由（on/off 各一条）与天赋组分别计数：v52 的 391 条资源行中有 172 条精确缺失的非背景天赋 JPG，合计 86 组；v55 映射 20 条/10 组后，审计检查了 69 个新增天赋组并找到 27 个同职业候选。v56 选入其中 9 组，另外 18 组机制、合并或改名候选仍未映射；另有 42 个新筛查天赋没有可靠候选。

同一审计还保留了 4 个跨职业歧义案例、涉及 5 个天赋（Paladin Precision、Paladin 与 Shaman Shield Specialization、Paladin Spell Warding、Rogue Sword Specialization），以及 Druid Nature’s Grasp 与 Improved Nature’s Grasp 两个未找到同职业来源的条目。这些项目没有因同名、部分机制或词语相似而自动补图。

天赋连线另有 [v54 箭头决定](../research/continuous-recovery-20261022/integration/related-talent-ui-v54/decision.json) 与 [v54 浏览器验收](../research/continuous-recovery-20261022/root-v54-browser-acceptance.json)：18 张箭头图通过，三张 `down-3` 因可见间隙未接入。阵营奖励物品的 3 张图则见 [独立映射决定](../research/continuous-recovery-20261022/integration/related-faction-icons-v54/decision.json) 和 [浏览器验收](../research/continuous-recovery-20261022/root-v54-faction-browser-acceptance.json)；这两组不是本页 27 个天赋映射候选的一部分。
