# 2026-10-21 非图库内容恢复

从已发布的 v39 继续，按用户要求暂缓图库，推进新闻、百科、指南、非图库 Media/社区页面与共享资源。50个玩家图库及 Media 截图集合本轮不再查询。此前的[图库范围分析](player-gallery-accessibility-20261020.md)保留供后续参考。

授权窗口：**00:25:07–14:25:07 UTC（北京时间08:25:07–22:25:07）**，共14小时。12:45:07 UTC 后不启动新网络批次，13:05:07 后不启动新来源或导出版本；13:50:07前完成发布主体，14:10:07起仅收尾。

主代理负责设计、取舍、来源和浏览独立验收；最多两名 Luna Max 执行者分别负责本地审计/实现和唯一串行网络获取。工作期间自动接续用于恢复中断，不限制当前会话连续推进。验收通过的变更沿用已有授权正常 commit/push，可发布 Pages 与处理后的离线包；不 force push。

下载先 direct，失败后仅进程内代理 `127.0.0.1:7890`，TLS 验证开启。每批预先限定目标、请求数、时长与字节数；实际请求起点间隔至少5秒。429/503或五次连续传输失败立即停批，冷却至少120秒并尊重更长 Retry-After；下一窗口只接受最新失败之后的新成功控制。若持续429则转入本地页面修复和来源整理，减少无效控制，不更改系统网络、不绕限流、不用付费 Firecrawl。

D盘每批前后、每请求及大写入前余量须不少于11,005,853,696字节。原始站点、Source15、已验收版本、来源文件和历史ZIP冻结；新修复进入新的派生版本。原始HTTP/cookie资料私有，公开整理后的来源与验收，图片保留原始字节。历史登录、报名、支付等业务继续静态展示。

现有四十个新闻活动图片候选保留优先级；先核对当前页面与已执行回执，再查询新窗口。注释中的素材、目录索引行与实际取得的可用图片分别记录。文件改动需有实际可见效果或明确的兼容修复，不为增加恢复数重新启用历史注释或敏感业务。

总账：[status.json](../research/continuous-recovery-20261021/status.json)；[任务清单](../research/continuous-recovery-20261021/tasks.json)；[前轮记录](continuous-recovery-20261020.md)。

## 检查点

### 00:25 UTC — 启动

本地 main 为 `feddaef4`，工作树干净，未发现归档下载或本站预览服务器遗留进程。D盘余量约46.19GB。最新 Wayback 失败来自10月20日14:20 UTC的代理429；新控制绑定这条记录，避免退回更早的失败或成功状态。两名执行者分别准备非图库本地审计和小规模连接控制，控制尚未执行。

### 00:29 UTC — 当前发布基线已核对

GitHub main 为 `feddaef4`，Pages 构建与线上分支仍为已发布 v39，Release 的534MB离线包及附件仍公开。原始清单、Source15清单和v39来源表摘要均与上轮验收一致。自动接续标识为 `wow-14`，到本轮截止删除。

### 00:49 UTC — Wayback仍限流，继续本地修复

新的已知阳性资源控制实际执行两请求：direct连接超时，代理返回429，未取得新图片，按规则停止。本轮暂不重复Wayback控制，保留失败状态；转向本地可修交互、已有Flash内容的兼容展示验证，以及Common Crawl静态索引的独立来源方案。

静态盘点已读取974份非图库HTML（约53MB），定位704个不同的活动缺图目标；这是页面引用清单，不是存档缺失结论。下载页悬停按钮等候选进入实际浏览检查。百科三幅插图已有2026-10-11的旧查询结论，后续只查新来源或未覆盖年份。

### 01:01 UTC — Common Crawl静态目录可直连

固定2008–2009集合的次级目录HEAD与首尾各8KiB范围读取均由direct成功返回，目录63,881,470字节，范围与ETag一致。请求完成后，执行脚本因相对GO路径写报告出错；保留原始数据，以独立离线回执复核，未重跑请求。请求起点时间没有落盘，因此不补造间隔证据。下一批改为一次有上限地取得这份较小的次级目录，供本地定位；CDX块及原始文件仍分批审查。Wayback停批状态不变。

### 01:06 UTC — 非图库浏览与Flash原型

137个直接HTML兼容地址均返回200，资料片动态图标实测正常，均不作重复修复。下载页仅goblue6的鼠标移出事件确证报错；goblue5/name7的旧命名不一致在浏览中工作正常。菜单的重复隐藏文字列为辅助标签修复。

三份原有SWF经Ruffle手动播放器已实际显示：宝石插槽火花、男性矮人舞蹈、海象人模型。它们均为2008年4月捕获，原字节保持。首次只加载而未播放的状态不能算完成；主代理查看了后续真正显示内容的截图。下一步仅在对应三页启用兼容层，整站和历史业务Flash不启用；尚未进入已发布站点。

### 01:22–01:56 UTC — Common Crawl目录与五个索引块

直连取得63,881,470字节的完整次级目录，定位五个覆盖相关域名的CDXJ块。B01在取得后遇到本地字段错误；原始数据保留，未重发。修复并补完整执行路径的离线测试后，仅取得此前未请求的B02–B05。主代理独立解压、核对排序与精确来源行。四个后续块共有4,182条经筛选的元数据记录，没有图片类型记录；这只描述本集合所查块，不能推广为其他存档均无图片。

Wayback仍维持00:49的429停批；Common Crawl静态对象成功不作为恢复Wayback请求的依据。[四块来源验收](../research/continuous-recovery-20261021/publication/root-commoncrawl-blocks02-source-acceptance.json)

### 02:02 UTC — 取得BlizzCast正文

五个精确ARC成员均由direct取得：5月9日的第一、二期访谈，5月11日RSS，以及5月15日的首页、目录。原始XHTML完整，两期共50个对话块。主代理核对了实际实体、来源摘要、XML和正文结构；新增四份HTML来源与一份RSS，阅读页仍在制作。5月15日两页将作为晚于基准的补充，图片与音频尚未取得。[来源验收](../research/continuous-recovery-20261021/publication/root-blizzcast-source-acceptance.json)

### 02:17–02:29 UTC — SWF完整性调查

另外取得五个5月9日SWF的ARC实体。世界地图只存下130,744字节，而原响应声明495,861字节；Wrath featured也只存下130,744字节，原响应声明131,184字节，两者压缩流均未结束。navigation、subtitle和无声影片播放器结构完整；前两者与已有文件相同。新播放器文件只作素材来源，尚未启用。没有把五个取得的ARC算成五个可播放SWF。[来源及截断验收](../research/continuous-recovery-20261021/publication/root-main-swf-source-acceptance.json)

### 02:30 UTC — v41本地验收，准备部署

完成常规Source15派生导出，保留原有657个图片覆盖地址与全部既有对象。新站共9,126个文件、约625MB；主代理核对全部输出字节。三处Flash的实际浏览与四个未变化控制页覆盖相关行为；初版静音遮罩问题已修正，未发布v40候选。44项相关单元检查通过，修正遮罩后10项针对性检查通过。[兼容范围](flash-compatibility-20261021.md)

另一批34页非图库实际浏览发现天赋计算器两份共享脚本在导出时丢失转义，四个已测职业无法初始化；冻结Source15中这两份脚本完整，正在修复转换路径。Zangarmarsh奖励图标与若干动态图标仍缺精确资源。该批后续追踪超出原20分钟窗口，实际时间和偏离已记入[审计报告](../research/continuous-recovery-20261021/local-audit/phase2/phase2-audit-report.json)，服务器已停止。

### 02:44–02:49 UTC — v41部署生效

主树提交 `08282c45`，Pages 分支 `fa8784fd`。GitHub Pages已完成构建，13个线上对象均通过direct取得，与本地验收版本的长度、摘要和MIME一致，包括两份WASM、三处Flash页面及来源表。[线上核对](../research/continuous-recovery-20261021/publication/root-v41-pages-online-acceptance.json)。离线Release仍为v39，后续合并本轮修复再打包。

### 03:04 UTC — 准备v42：天赋计算器与BlizzCast

天赋计算器限定修复两份精确Source15脚本，保留转义和动态图片路径，跳过会破坏这些字符串的通用转换。九职业预览均可初始化；旧回执只对德鲁伊执行了加点、重置和全零模板保存，正式导出后将逐一测试九职业的非零模板。61个缺图目标经现有清单、编码别名和实际文件复核，均未找到本地实体：27张树背景、34张技能图标。[资源盘点](../research/continuous-recovery-20261021/integration/talents/resource-audit/README.md)

BlizzCast五份来源生成五个静态阅读页及一份样式，两期50个访谈块逐块核对了非空白文字。保留说话人、时间码与原文；5月15日首页和目录注明晚于基准。原站表单、脚本和播放器不进入阅读页，缺少的媒体列入后续来源调查。已保存的原站入口只接通到精确来源匹配的阅读页。新增模块测试使用可移植fixtures，相关63项检查通过。[接入设计](non-gallery-restoration-20261021.md)

### 03:22–03:36 UTC — v42正式导出验收与完整天赋缺图盘点

v42共9,132个文件、625,223,624字节。主代理逐项核对所有文件，新增仅为五个阅读页和一份样式；669个旧HTML只改变了678处已接受的BlizzCast链接，其余非HTML变化为两份天赋脚本和两份生成的路由文件。原有图片、SWF和WASM字节保持。[输出验收](../research/continuous-recovery-20261021/publication/root-v42-export-acceptance.json)

实际Chrome逐一完成九职业加点、重置、保存非零模板、重新打开和刷新恢复。五个阅读页正常，下载页和展开后的二月新闻均经可见链接跳转到访谈阅读页。[浏览验收](../research/continuous-recovery-20261021/publication/root-v42-browser-acceptance.json)

主代理查看截图后发现，先前61项只是动态404，遗漏了大量返回200的静态缺图占位。补做九职业DOM盘点，共1,259个独立缺失图片目标；其中1,232个在占位查询中，61个动态404与其部分重叠。主代理复核集合及实际文件、路由和来源表的本地缺省；这不是网络存档全局缺失结论。后续继续检查原始取证层是否有未进入派生站的素材。[完整缺图口径](non-gallery-restoration-20261021.md)

BlizzCast原站检查三批共28次请求。八个配图/样式目标最终均404；两个音频在direct和代理均为curl60 `SEC_E_WRONG_PRINCIPAL`，代理CONNECT 200不作音频原站200。没有关闭证书校验，未取得新图片和音频，停止这条原站跳转支线。Common Crawl静态索引另外提供九个基准日前主站正文线索，尚在准备获取，未算入新增正文。

### 03:42–03:49 UTC — v42上线与主站正文来源

main已推送`2577dcdc`，Pages构建`fdc976ed`完成。24个线上对象均经direct取得，长度、摘要、MIME与本地一致；离线Release仍为v39。[线上核对](../research/continuous-recovery-20261021/publication/root-v42-pages-online-acceptance.json)

九个精确Common Crawl ARC成员均由direct取得，主代理重新解析并核对URL、捕获时间、实体摘要和实际正文。七份可新增页面：旧战场截图比赛公告、Tinfoil Hat、双头食人魔、粉丝站计划、Molten Core宣传页、2004年9月补丁说明和吟游诗人介绍；内容目录更新一份，Wrath XML入口与已有原始正文相同，只补别名。所有捕获均早于基准。正在准备Source16派生输入，清除三个瞬态会话后缀，比赛与招募内容以历史展品呈现。[来源验收](../research/continuous-recovery-20261021/publication/root-main-pages-source-acceptance.json)

### 04:39–05:16 UTC — Source16与关联图标来源

固定公开仓库提交取得一个约5MB的WotLK计算器备份。主代理核对ZIP成员与Git树，并解码全部1,804个图片素材；其中986个36×36图标与缺口路径完全相同，作为后期关联素材单独接入。没有导入其天赋数据或脚本，也未把WotLK背景直接套用到2008页面。[来源与接入决定](../research/continuous-recovery-20261021/publication/root-related-talent-icon-integration-decision.json)

Source16全部8,364个输入文件与新正文来源核对通过，原Source15保留。v43完成本地字节与实际浏览验收：七个新增正文、一份目录更新及六个地址别名；暂未部署，准备与图标一并发布。[Source16验收](../research/continuous-recovery-20261021/publication/root-source16-local-acceptance.json)

### 05:42–06:15 UTC — v44浏览与新增页面缺口

九职业均完成加点、重置和非零模板保存、重开、刷新；986张关联图标正常显示，合并缺图集合剩273个目标。v44候选随后在主代理的差异审阅中发现比赛说明后遗留多余闭合锚点，因此未发布。修正代码后进入新版本，不覆盖候选。[候选审阅](../research/continuous-recovery-20261021/publication/root-v44-candidate-review.json)

新增正文59项图片、样式或Flash依赖经原始清单和历史ZIP核对，未取得精确原路径实体。Tinfoil Hat的九片提示框与Molten Core返回箭头可复用同站已保存布局，原型已实际查看；其他文章同名插图不自动替代。

### 06:16–06:27 UTC — DNS与TLS阶段分离诊断

本机解析为202.160.128.14，TCP超时，尚未进入TLS。两家DoH经进程内代理均返回207.241.237.3；刷新一次答案后，该地址直连TCP成功，随后TLS握手被重置（10054），没有证书或Wayback应用响应。未修改系统DNS、代理或证书，00:49的429停批仍保留。[独立核对](../research/continuous-recovery-20261021/publication/root-wayback-dns-tls-diagnosis.json)

### 06:41–07:02 UTC — v45本地验收

新版本保留Source16正文与986张关联图标，修复旧比赛措辞和锚点，加入10个到既有布局图片的路由映射，不产生重复布局图片。67项相关检查通过；全部10,130个文件、629,186,325字节核对通过。五页实际Chrome检查通过，主代理查看四张截图，确认提示框可读、返回箭头与历史比赛入口正常。首次探针过早离开首页跳转导致一个请求取消，修正探针的最终地址等待后通过，站点未因此改动。[本地验收](../research/continuous-recovery-20261021/publication/root-v45-local-acceptance.json)

线上仍为v42、离线Release为v39；v45进入提交和部署。Common Crawl另外三份RSS/指南来源已由direct取得，正文差异仍在审阅，尚未纳入本版。

### 07:37–08:07 UTC — v45部署与线上补验

main提交`335cb44f`、Pages提交`6b16f914`，GitHub构建完成。首轮45个对象有44个通过；约10.8MB的来源表两次HTTP200传输均在60秒超时。保留失败回执，只对这一对象放宽至180秒，direct一次完整取得并核对通过，共45个对象完成验收。[补验与合并回执](../research/continuous-recovery-20261021/publication/root-v45-pages-online-reconciliation.json)。离线Release仍为v39。

下一版准备六张带独立来源说明的后期天赋界面PNG，以及八个到已有2008年同站点数框GIF的兼容映射。九职业六图原型通过；点数框在德鲁伊、战士的初始、加点和重置状态均闭合，八个目标的原捕获日期仍留空。ArchiveCraft成为非图库缺图的新来源线索，先取四份精确百科HTML，再判断是否有可用图片。

### 08:44 UTC — v46本地验收与百科新图源

v46增加六张后期关联来源的天赋PNG界面图，并把八个点数框边框地址映射到已有2008年4月同站GIF。55项受影响检查通过；10,137个文件、629,321,494字节逐项核对通过，既有图片、脚本、天赋数据、SWF和WASM字节保持。九职业实际执行初始、加点、加满首项、单树重置和全部重置，另点击三个打印视图；剩余259个独立缺图目标。两次探针分别因预期措辞过短、把图片角片当作CSS背景而失败；修正探针后通过，站点未改。[本地验收](../research/continuous-recovery-20261021/publication/root-v46-local-acceptance.json)

只读脚本盘点：151个非图库外链JS有150个语法通过；奖励页旧Prototype脚本被通用转换损坏，但现有静态展品和全部HTML均不引用它，暂不接回。879份非图库HTML的12,051段内联脚本去重为2,322段，全部语法通过；语法检查未执行页面逻辑。

ArchiveCraft的四份百科HTML和四张引用图均由direct取得。高等精灵控制图与已有实体字节相同；Alleria、塞纳里奥议会、玛法里奥三张图经实际查看，准备以注明社区来源的当前关联素材接入。原目标捕获日期留空，Alleria保留WordPress缩放名说明；原百科正文保持。[图源决定](../research/continuous-recovery-20261021/publication/root-related-encyclopedia-image-decision.json)

Common Crawl补充三份来源复核完成：RSS九条标题已在五月新闻中，Cenarion指南截断于128KiB且末尾标记未结束，Implemented正文及文章图片与已有来源相同；保留来源，不覆盖现有页面。[复核](../research/continuous-recovery-20261021/publication/root-commoncrawl-pages02-content-acceptance.json)

### 11:12 UTC — 四幅关联配图与奖励按钮

v46已发布，60个线上对象由direct核对通过；保留首次main推送低速失败和随后代理正常推送的两份回执。

ArchiveCraft当前页面提供Alleria、塞纳里奥议会、玛法里奥三幅百科图，以及The Broken指南缩略图。四张JPEG共176,325字节，保留原字节，页面注明并链接来源。它们属于当前关联来源补充，原始2008年目标捕获日期留空。The Broken菜单使用的动态thumb-broken.jpg与静态thumb-thebroken.jpg经原页面及脚本核对，共用同一张缩略图。

v47候选的来源注记对比度不足，v48候选点击菜单后仍使用未映射的动态名称，两版均未发布。v49修正这两处，并只替换奖励表脚本中的两个图片路径。65项相关代码检查、10,143个实际输出对象及五页实际Chrome操作验收通过。第一版浏览探针还检查了既有派系说明文字缺口；失败记录保留，最终探针将其作为后续修复项记录。

[v49本地验收](../research/continuous-recovery-20261021/publication/root-v49-local-acceptance.json) · [实际浏览](../research/continuous-recovery-20261021/publication/root-v49-browser-acceptance.json)

百科扩展浏览审计完成49/52页，另三页因本地连接/加载超时未完成，不计作通过。已浏览页还观察到12个独立分类头像CSS目标缺失。离线服务器backlog对照没有证明增大队列有改善，未修改生产服务器。BC介绍Flash只显示封面；播放所需FLV和皮肤SWF在已缓存Common Crawl覆盖块中均无精确匹配，视频尚未恢复。

### 11:29 UTC — v49上线与百科补查

v49 Pages提交为`34916610`，74/74线上对象由direct取回并核对。另对先前未完成的Cenarius、Darnassian、Dejahna三页以60秒上限单独补查，全部正常加载、无页面错误；三份HTML与先前v48相同。合并两轮覆盖52页，分类头像仍为12个独立缺图目标，不把占位图计作恢复。

[v49线上核对](../research/continuous-recovery-20261021/publication/root-v49-pages-online-acceptance.json) · [三页补查](../research/continuous-recovery-20261021/publication/root-v49-encyclopedia-completion.json)

### 11:58 UTC — 派系说明文字恢复

v50本地验收恢复奥尔多／占星者说明。来源是Source16已保存的2008-04-02令牌脚本，提取两段原始文字，分别850和1,104字符；不导入其奖励数据。一个3,273字节defer helper只用于主介绍页，原脚本、令牌页和全部既有图片保持。

73项相关检查由10项本次检查及63项相同代码绑定的既有结果组成；不是本次重复执行73项。全部10,144个输出核对完成。实际Chrome打开两派说明弹窗并切换，主代理逐张查看两张截图。两轮失败探针分别涉及浏览器br标签序列化和未等待的宽泛文字定位，保留记录；最终探针使用原按钮锚点与可见状态检查，导出站点未改。

[v50本地验收](../research/continuous-recovery-20261021/publication/root-v50-local-acceptance.json) · [原文来源](../research/continuous-recovery-20261021/publication/root-aldor-scryers-lore-source-acceptance.json)

另发现Wrath字母T图片已存在，源路由为双斜线，而正文单斜线路由尚未接通；进行单独最小修复评审，不把已有素材计作新取得图片。

### 12:37 UTC — 最终本地版本v51与缺口清单

v51只新增T.gif的一个精确兼容地址。原GIF捕获于2008-04-23 09:51:02，48×48、1,419字节，已在本地；源逻辑地址含双斜线，输出地址为单斜线，浏览适配器此前未识别该输出地址。修复后Howling Fjord、Grizzly Hills、Borean Tundra和Bard四页实际显示原图，未新增图片实体或HTML跳转。

五页Chrome检查完成，包括两派说明弹窗与四页字母图；无外联、页面错误、失败请求或HTTP错误。全部10,144个实际文件核对；相对v50只改变路由表和嵌入路由表的浏览脚本，页面HTML及所有原图、脚本、奖励数据、SWF/WASM保持。v50作为本地检查点提交并正常push，最终以v51部署。

[v51本地验收](../research/continuous-recovery-20261021/publication/root-v51-local-acceptance.json)

合并分轮浏览记录得到177条独立页面路径，不表示在同一版本重新执行全站扫描。已观察状态中仍有411个本地缺资源目标，包含259个天赋图片目标；另单列已有但路由未接的T.gif（现由v51修复）及周年截图脚本拼接错误。后者保留为后续图库任务。两张名称含screenshot的新闻配图仍纳入新闻缺口，没有按文件名错误排除。原型排除只依据实际证据；未记录HTTP状态的已接受交互不补造200。

[整理后的缺口清单](../research/continuous-recovery-20261021/local-audit/non-gallery-closeout-v49-r3/README.md) · [主代理复核](../research/continuous-recovery-20261021/publication/root-non-gallery-closeout-acceptance.json)

12:11 UTC再次取一份已知正样本CDX控制：direct连接超时，代理返回429，2次请求后停止，无正CDX行，未开启后续Wayback批次。原始HTTP头和文本留本地，公开整理后的观察；没有重置历史失败记录。

[最新控制](../research/continuous-recovery-20261021/publication/root-control02-source-acceptance.json)
