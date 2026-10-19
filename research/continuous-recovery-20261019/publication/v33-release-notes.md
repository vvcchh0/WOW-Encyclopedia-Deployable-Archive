以 2008-05-12 的官方百科存档为基准，保存百科与早期魔兽世界官网。本离线包为 2026-10-18 构建的 v33，在线版当前同为 v33。

- 相比此前离线包，补回更多旧新闻配图、文章大图、指南插画、壁纸和图标；上一轮共接入 376 个图片资源地址。
- 恢复文章图片放大、副本进度图和旧专业配方的查看，并接通已保存原图的页面链接。
- 历史账号、报名和付款内容作为静态展品展示。

下载 ZIP 并解压，安装 Python 3 后，Windows 用户双击 `START_BROWSE.cmd`。macOS / Linux 用户在解压目录运行：

```sh
python3 tools/serve_pages_preview.py --site site --port 0 --open-browser
```

50 个玩家截图图库的原编号图片仍有大量缺失，指南预览另行展示。部分旧页面交互尚在复核，已知比赛结果页存在旧菜单脚本问题。欢迎通过 Issues 提供缺图页面、可用存档和修复建议。

[在线浏览](https://vvcchh0.github.io/WOW-Encyclopedia-Deployable-Archive/) · [更新记录](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/blob/main/CHANGELOG.md) · [工作记录](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/blob/main/docs/continuous-recovery-20261019.md)

原站文字与美术素材归 Blizzard Entertainment 等权利人所有，详见随附 NOTICE。
