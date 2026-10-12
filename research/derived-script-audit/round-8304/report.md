# 派生 JavaScript 语法审计

本审计只读取 `offline/build-manifest.json` 指向的源文件和 `offline/site` 派生文件；不联网、不执行 JavaScript。源/派生字节先以 base64 写入 JSON，再由一个 Node `vm.Script` 进程分别编译，保留 CRLF，避免文本管道换行转换造成假失败。

- manifest 文件：`offline/build-manifest.json`（8304 entries）
- JS 实体（有源文件）：160；HTML 文档：917；inline classic 配对：11539
- Node 编译作业：11699；Node：v22.22.0；仅编译：`True`
- 源文件编译失败：0；派生文件编译失败：0；源通过而派生失败（新增损坏）：0
- 读取/HTML 提取错误：0；inline 数量不一致：0；声明 SHA 与实际 SHA 不一致：0

## 判定

只有 `source_compile_ok=true` 且 `derived_compile_ok=false` 才计入新增派生语法失败。历史源文件本身无法由 Node 编译的记录保留在 JSON 的 `source_compile_failures`，不会冒充镜像改写损坏。

## 证据

- 逐作业 JSON（含 source URL、source SHA、script index、两侧错误和短上下文）：`research/derived-script-audit/round-8304/audit.json`
- Node 输入（源/派生原始字节 base64）：`research/derived-script-audit/round-8304/compile-input.json`
- Node 输出：`research/derived-script-audit/round-8304/compile-results.json`
- 批处理器：`research/derived-script-audit/compile_batch.js`

## 复现

```powershell
python research/derived-script-audit/audit_scripts.py
```

本轮独立输出使用 import wrapper，未覆盖旧轮结果：

```powershell
python research/derived-script-audit/round-8304/run_audit_8304.py
```

运行前后 `offline/build-manifest.json` SHA256 均为
`397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459`。

## 新增失败摘要

未发现源编译通过而派生编译失败的作业。
