# 2008魔兽官网与百科离线恢复包

文件：`WOW_Encyclopedia_20080512_offline_recovery_20261012.zip`，2,251,344,514 B。

SHA-256：`66553fcd368ae5ee48dfb9f1b11897ac7fb3fd6a1983a0e303c2c088522c1c63`，也可使用相邻`.zip.sha256`文件核对。

请解压到短目录，例如 `D:\WoW2008`，不要直接使用ZIP完整文件名作为解压目录。研究证据里有较长文件名：首次在较深临时目录解压时触发了Windows 260字符路径限制，失败记录保留在`offline-20261012-recovery-portability-check.json`。ZIP本身已通过CRC及成员SHA-256校验。

安装Python 3后，在解压根目录双击`START_OFFLINE.cmd`并保持启动窗口打开，访问：

- 官网首页：<http://127.0.0.1:8765/>
- 百科：<http://127.0.0.1:8765/info/encyclopedia/index.xml>
- Game Guide：<http://127.0.0.1:8765/info/>
- Media：<http://127.0.0.1:8765/downloads/>

已有服务占用8765时，可使用 `powershell -File tools/launch_offline_mirror.ps1 -Port 8766`，访问相应端口。直接双击HTML/XML文件不能完整还原跳转和脚本。

此版本含8,304条路由、917个文档；917/917文档通过完整浏览验收。它是有明确缺口的恢复版，仍保留缺图、缺失脚本、Toplist数据等提示；旧Flash插件与在线账号功能不具备现代浏览器离线运行能力。实际捕获时间、跨时间补充及原始响应均有来源记录。

包内`FILE_SHA256SUMS.txt`校验逐文件内容；来源校验、浏览验收、打包校验及解压启动验证是不同检查，详见相邻报告及包内`offline/README.md`、`docs/resource-recovery-2008.md`。

短目录全新解压及独立本机服务验证已通过，见[成功验证报告](offline-20261012-recovery-portability-shortpath-check.json)与[root最终验收](offline-20261012-root-final-acceptance.json)。验证覆盖首页、百科词条、Game Guide、Media、新闻、JS MIME/摘要及本地缺失提示。测试用8877服务已停止，现有8765浏览服务保留；测试日志归档后，仅清除了可由ZIP恢复的临时解压副本。

最终检查时工作区约8.73 GB，D盘可用约21.57 GB，均符合14 GB工作区上限及10 GiB加256 MiB磁盘保留线。ZIP与历史备份摘要保持不变。
