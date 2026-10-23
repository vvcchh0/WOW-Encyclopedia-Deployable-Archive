# 历史导出去重归档

历次 Pages 导出保留各阶段可浏览站点，但页面和图片有大量重复。2026-10-23 将 57 份历史导出整理为共享内容归档；每个唯一文件内容只保存一次，各版清单仍记录原路径、长度和 SHA-256。恢复会写出独立文件，不使用硬链接。

## 本轮结果

归档包含 57 个版本、513,856 个文件，共 33,445,408,630 字节逻辑内容。归档目录共 60 个文件、665,351,745 字节逻辑长度；其中 13,234 个共享对象全部实读核验，未压缩对象内容共 1,456,362,754 字节。三个代表版本均实际恢复并通过独立核验。随后删除 55 棵旧展开目录和三份临时恢复副本，保留 v55、v56、原始来源、Source15/16、`offline/site` 与完整历史 ZIP。

按原目录文件的 NTFS AllocationSize 实测，删除目录释放文件分配 32,714,919,104 字节，扣除新归档文件分配 665,473,576 字节后，净节省约 32.05 GB（32,049,445,528 字节）。该口径不计目录元数据和少量新审计文件，也不以 D 盘前后余量变化代替文件级节省；三份临时恢复副本的 1,784,109,860 字节不重复计入净节省。

整理后的[公开验收摘要](evidence/historical-export-deduplication-20261023.json)列出归档路径、长度、SHA-256 和验收结论，不包含私有 HTTP/Cookie 或个人会话清单。浏览站和 Release 仍为 v56；本次去重没有发布新网页或新离线浏览包。

## 核验与恢复

在仓库根目录运行共享归档核验：

```powershell
python -X utf8 tools/historical_export_store.py verify --store artifacts/historical-exports-20261023
```

恢复版本时须指定尚不存在的目标目录；例如恢复 v56：

```powershell
python -X utf8 tools/historical_export_store.py restore --store artifacts/historical-exports-20261023 --version pages-resources-20261022-v56 --dest .scratch/restore-v56
```

归档和各版原清单保留在维护者工作区。原始 HTTP、Cookie 和完整取证内容不随公开摘要发布。逐版原目录删除前的全量重读、对象回读及三个真实恢复副本均有独立验收记录；清理后验收确认上述来源和保留版本仍在。[2026-10-22 空间清理](storage-cleanup-20261022.md)与本轮分别核账。
