# 三处历史 Flash 的兼容展示

本轮使用 Ruffle 0.7.1 显示已经保存的三个 SWF，覆盖宝石插槽火花、男性矮人舞蹈和海象人模型。它们分别来自2008年4月2日的捕获；新兼容层不改变这些文件。

| 页面 | 使用的文件 | 当前范围 |
| --- | --- | --- |
| `info/items/socketeditems.html` | `socket_anim.swf` | 五个原有插槽火花 |
| `info/races/dancing.html` | `dwarf_male.swf` | 男性矮人；其他选择显示尚未取得 |
| `wrath/features/factions/tuskarr.xml.html` | `tuskarr_idle.swf` | 页面首个模型位置 |

Ruffle由[官方0.7.1发布](https://github.com/ruffle-rs/ruffle/releases/tag/v0.7.1)取得，自托管运行文件约29.25MB，保留MIT与Apache许可证。运行时只在这三页建立手动播放器，没有启用全站Flash替换。原有业务Flash仍不加载。

播放器禁用脚本桥接、打开外部网址和套接字代理，读取固定路径的原始SWF并核对摘要。`allowNetworking: internal`用于本轮所选内容；不能把它描述为强隔离或把尚未实现的`none`选项当作保障。配置依据见[Ruffle API](https://ruffle.rs/js-docs/master/interfaces/Config.BaseLoadOptions.html)。原始源码、已验收版本和历史ZIP不变。

首次整站浏览发现Ruffle默认静音提示遮住模型，因此未发布v40候选。v41将这三个图形展品的`unmuteOverlay`设为`hidden`，在实际浏览中确认遮罩消失。五个火花和矮人舞蹈的两个时点截图保留；海象人按模型实际显示验收，没有把截图变化推断为所有原始动画都已复现。

男性矮人的三个原ZIP下载项仍未取得；其余十五种舞蹈选择也没有可用SWF。切换这些选项会显示缺失说明，不套用矮人的模型。下载页的`goblue6`鼠标移出错误同时修复；原本正常的其他按钮保持原逻辑。

验收：[文件与派生差异](../research/continuous-recovery-20261021/publication/root-v41-export-acceptance.json)；[实际浏览](../research/continuous-recovery-20261021/publication/root-v41-browser-acceptance.json)。本轮后续工作见[持续恢复记录](continuous-recovery-20261021.md)。
