# Coolwow2 关联来源调查

2026-10-23，核对 `boom8866/coolwow2` 的固定提交，保存四份地下城指南 HTML，用来追查缺图的用途。当前没有取得新的图片文件，也没有修改网页中的图片映射。[整理后的来源记录](evidence/coolwow2-context-leads-20261023.json)

来源为[固定提交中的地下城目录](https://github.com/boom8866/coolwow2/tree/09c52b7673871b8048da92e5a13ed753fc08162f/instance)。该提交属于2015年的关联来源，内容包含法文魔兽官网片段。完整目录有3,006项；73个Git目录对象重构核对通过，四份HTML的原始字节、长度和Git blob标识均与目录一致。四页分别为Karazhan、Coilfang Reservoir、Hellfire Citadel及Caverns of Time，合计40,189字节。

## 时光之穴的八个缩略图线索

前三份页面没有图片引用；Caverns of Time页面含八处截图缩略图，并链接到法国欧服官网的三组图库。对应的英文图库已列入项目的[50组玩家图库清单](player-gallery-accessibility-20261020.md)，不是新增的112张缺图。

| 已有图库 | 已统计原图槽位 | 欧服链接中的片段编号 | 源页行号 |
|---|---:|---|---|
| Escape from Durnholde | 38 | 37、26 | 223、228 |
| Opening of the Dark Portal | 30 | 22、17、5 | 242、247、252 |
| Battle for Mount Hyjal | 44 | 42、25、7 | 266、271、276 |

源页和具体链接可从[Caverns of Time原始HTML](https://github.com/boom8866/coolwow2/blob/09c52b7673871b8048da92e5a13ed753fc08162f/instance/bc/caverns-of-time.htm#L223)追溯。目录中列有八个对应缩略图路径及blob标识，图片字节尚未获取或解码；欧服链接的编号也不能直接用作美服图库的编号。

后续可先获取这八个固定blob，检查图片内容，再决定是否作为注明欧服来源的关联素材展示。三组图库的112个原图槽位和112个缩略图槽位，已包含在既有的各1,684项总数中。本次不增加缺失目标，也不减少未恢复数量。

## 同名文件的用途核对

331项非图库静态缺失目标与完整目录比较，产生43个目标、72项同名关联，其中不少是`background.jpg`、`ss1-thumb.jpg`等通用名称。源页将`ss1-thumb.jpg`等放在时光之穴分区，不能据此补到Four Dragons、节日指南等其他页面。七个待补声望图标的精确名称在这份目录中没有命中。

这轮先保留源页、图注与链接关系，图片对应关系继续按具体内容核实。早期分析曾把上述三组图库误分为额外集合；主代理对照现有清单后更正，旧分析与修正版在本地研究记录中分别保留。

## 本轮连接结果

GitHub的四次blob请求均经直连、验证TLS后成功。12:30 UTC再做一次Wayback CDX控制：直连在GET发出前的连接阶段超时，代理完成TLS并收到429；没有读取429响应体或回放图片。该连接阶段没有细分DNS、TCP和TLS耗时，因此尚不能确定更具体的超时原因。本轮停止后续Wayback获取，保留失败记录与冷却时间。
