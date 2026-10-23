# 情人节指南截图显示修复

2026-10-23，本地 v57 修复了 Love is in the Air 指南页面的12处截图显示及原图链接。在线版和离线包的发布进度见[当天记录](continuous-recovery-20261023.md)。

旧脚本请求 `images/ssN-thumb.jpg`，点击后进入未保存的 `imageviewer.html`。对应的12张 `images/ssN.jpg` 原图此前已经取得，并且已用于页面的 Guide images 区域；缺口在旧截图位置的显示和点击路径。

派生脚本在该指南页面及已知别名上，使用已验收原图按最多200像素宽显示，保持比例，并将图片和说明文字链接到原图。已有缩略图的条目继续使用原交互。修复从现有图片清单生成，不产生缩略图别名文件。

本次计为12处显示修复、12张已有原图复用、0张新增原图。现有 Guide images 区域保留。另一个 `images/ss/` 目录下的34张玩家投稿原图和34张缩略图仍缺失；50个玩家图库的缺口也没有因此减少。

验收包括4项 Node／导出定点测试、既有44项回归检查，以及真实 Chrome 中的指南地址、路由别名和独立图库页面。两版本各10,205个文件完整回读对比，变化仅为共享截图脚本及导出来源记录，全部已有图片字节和路由表保持一致。主代理另检查了页面首处及最后一处截图的实际显示和原图链接。

整理后的来源、范围和验收摘要见[证据记录](evidence/love-guide-preview-repair-20261023.json)。实现位于 `tools/guide_image_collections.py` 与 `tools/export_github_pages.py`，测试位于 `tests/test_story_screenshot_previews.py`。
