"""Stage only the accepted final site/package proof and release tooling."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = 'research/continuous-recovery-20261021/'
PUB = ROOT / BASE / 'publication'
OUT = PUB / 'v51-release-stage-config.json'
assert not OUT.exists()
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for name in ('root-v51-final-acceptance.json', 'root-v51-portable-acceptance.json',
             'root-v51-portable-browser-acceptance.json'):
    assert read(PUB / name)['accepted'] is True
assert read(PUB / 'root-v51-portable-acceptance.json')['members_read'] == 10150
now = datetime.now(timezone.utc)
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
assert head == 'cdab4eed9c7055939c4a9bb707cc1fefcc3b7257'
assert subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT, text=True).strip() == head
assert shutil.disk_usage(ROOT).free >= 11005853696
producer = read(PUB / 'v51-portable-package-report.json')
summary = {key: producer[key] for key in (
    'archive', 'baseline_timestamp', 'processed_date', 'compression',
    'network_performed', 'package_member_count', 'site_member_count',
    'sidecar', 'sidecar_bytes', 'sidecar_sha256',
)}
summary.update({
    'producer_report_sha256': sha(PUB / 'v51-portable-package-report.json'),
    'archive_bytes': producer['verification']['archive_bytes'],
    'archive_sha256': producer['verification']['archive_sha256'],
    'independent_acceptance': BASE + 'publication/root-v51-portable-acceptance.json',
    'member_list_location': 'FILE_SHA256SUMS.txt inside the processed ZIP; the full producer member listing is retained locally.',
})
(PUB / 'root-v51-package-summary.json').write_bytes((json.dumps(summary, indent=2) + '\n').encode())
state_path = ROOT / BASE / 'status.json'
state = read(state_path)
state.update(
    phase='v51_online_and_portable_accepted_release_pending',
    current_local_version='v51', current_pages_version='v51',
    current_main_commit=head, current_code_commit=head,
    current_pages_commit='7494e7cc898b34f8f4c6a64922bde34b8dd2ee44',
    latest_pages_acceptance=BASE + 'publication/root-v51-pages-online-acceptance.json',
    latest_portable_acceptance=BASE + 'publication/root-v51-portable-acceptance.json',
    accepted_pages_this_run=7,
    accepted_pages_counter_semantics='New historical body pages; the one updated body page and five derived reading pages are counted separately.',
    image_counter_semantics='accepted_images_this_run and published_images_this_run count recovered original historical image entities; related-source supplements have separate counters.',
    network_worker_current_task='complete_processed_v51_package_no_network',
    local_worker_current_task='complete_exact_t_image_alias',
    source_downloads_closed=True, new_exports_closed=True,
    disk_free_latest_bytes=shutil.disk_usage(ROOT).free,
    updated_utc=now.isoformat(),
)
state_path.write_bytes((json.dumps(state, indent=2) + '\n').encode())
tasks_path = ROOT / BASE / 'tasks.json'
tasks = read(tasks_path)
for row in tasks['tasks']:
    if row['id'] == 'FINAL':
        row['state'] = 'v51_pages80_objects_and_portable145_paths_root_accepted_release_pending'
tasks_path.write_bytes((json.dumps(tasks, indent=2) + '\n').encode())
readme = ROOT / 'README.md'
text = readme.read_text(encoding='utf-8')
old = '启动后会打开本地浏览页面。在线版为 v49，离线包暂为 v39；新版离线包正在整理。'
assert old in text
text = text.replace(old, '启动后会打开本地浏览页面。在线版为 v51，离线包暂为 v39；新版离线包已完成本地验证，准备发布。')
needle = '- 补充百科与指南的四幅配图，页面注明 ArchiveCraft 来源。'
assert needle in text
text = text.replace(needle, needle + '\n- 恢复奥尔多／占星者说明弹窗与派系切换，修复四页 Wrath 字母图的显示。')
readme.write_bytes(text.encode())
changelog = ROOT / 'CHANGELOG.md'
text = changelog.read_text(encoding='utf-8')
old = '- 本地完成 v51：接通已有 Wrath 字母图片的精确地址，四页恢复显示；整理 177 个页面路径的分轮浏览记录与剩余素材清单，准备最终部署与离线包。'
assert old in text
text = text.replace(old, '- 发布 v51：恢复奥尔多／占星者说明弹窗与派系切换，接通四页 Wrath 字母图；80 个线上对象核对通过，离线包完成本地启动检查。整理 177 个页面路径的分轮浏览记录与剩余素材清单。')
old = '- 本地完成 v50：用已保存的原文恢复奥尔多／占星者介绍弹窗与派系切换，准备随最终版本发布。'
assert old in text
text = text.replace(old, '- 完成本地 v50：用已保存的原文恢复奥尔多／占星者介绍弹窗与派系切换，已合入 v51。')
changelog.write_bytes(text.encode())
with (ROOT / 'docs/continuous-recovery-20261021.md').open('ab') as f:
    f.write((f'\n### {now:%H:%M} UTC — v51线上与离线包验收\n\n'
        'main代码检查点cdab4eed已正常push；Pages提交7494e7cc构建完成，前后构建标识一致。80个指定线上对象均由direct取得，与本地长度和摘要一致。主代理绑定代码、完整导出、Chrome实际行为和线上对象，完成最终站点验收。\n\n'
        '处理后的浏览ZIP为546,302,950字节，10,150个成员，解压约634MB。独立检查全部成员，并从含空格路径解压，使用包内Python隔离服务实际请求145个对象的GET/HEAD，共290次本地请求；五页实际Chrome检查再次通过，包括两个派系弹窗和四页字母图。原制作报告的大型成员清单留在本地，包内提供FILE_SHA256SUMS.txt，公开整理后的包摘要和独立验收。\n\n'
        '[线上核对](../research/continuous-recovery-20261021/publication/root-v51-pages-online-acceptance.json) · [离线包核对](../research/continuous-recovery-20261021/publication/root-v51-portable-acceptance.json) · [包内实际浏览](../research/continuous-recovery-20261021/publication/root-v51-portable-browser-acceptance.json)\n\n'
        '资源下载与新导出已经结束，继续发布当前已验收的处理后离线包。Wayback最后一次控制429仍保留，不启动新来源批次。\n').encode())
p = ROOT / 'docs/non-gallery-restoration-20261021.md'
text = p.read_text(encoding='utf-8')
text = text.replace('两段文字来自已保存的2008-04-02同专题令牌脚本；仅补入缺失说明，按钮切换、原奖励数据和令牌页保持。实际Chrome完成两个弹窗及两次派系切换，正文与来源对应。准备与本轮最终版本一并发布。',
    '两段文字来自已保存的2008-04-02同专题令牌脚本；仅补入缺失说明，按钮切换、原奖励数据和令牌页保持。实际Chrome完成两个弹窗及两次派系切换，正文与来源对应，现已合入v51上线。')
text += ('\n## v51发布验收\n\n最终Pages版本为v51，80个线上对象与本地一致。浏览版ZIP约546MB，解压约634MB；独立成员检查与包内服务145个对象的GET/HEAD检查完成，实际Chrome再次验证派系说明和四页Wrath字母图。离线包发布结果单独记录，避免把本地完成等同于公开可下载。\n\n'
    '[线上核对](../research/continuous-recovery-20261021/publication/root-v51-pages-online-acceptance.json) · [离线包验收](../research/continuous-recovery-20261021/publication/root-v51-portable-acceptance.json)\n')
p.write_bytes(text.encode())
names = (
    'v51-main-commit.json', 'v51-main-push.json', 'push_v51_main.py',
    'v51-pages-publication.json', 'v51-pages-build-control.json',
    'v51-pages-build-control-r2.json', 'root-v51-pages-online-acceptance.json',
    'accept_v51_final_site.py', 'root-v51-final-acceptance.json',
    'v51-package-execution.json', 'root-v51-package-summary.json',
    'root-v51-portable-acceptance.json', 'prepare_v51_portable_browser.py',
    'root_v51_portable_browser.cjs', 'v51-portable-browser-preparation.json',
    'root-v51-portable-browser-acceptance.json', 'v51-release-notes.md',
    'prepare_v51_release_checkpoint.py',
)
paths = {BASE + 'publication/' + name for name in names}
paths.update({
    'README.md', 'CHANGELOG.md', 'docs/continuous-recovery-20261021.md',
    'docs/non-gallery-restoration-20261021.md', BASE + 'status.json', BASE + 'tasks.json',
})
folder = ROOT / BASE / 'integration/portable-release-tools-v51'
paths.update(p.relative_to(ROOT).as_posix() for p in folder.iterdir()
             if p.is_file() and p.suffix in {'.py', '.md', '.json'})
tracked = {}
for item in subprocess.check_output(['git', 'ls-tree', '-rz', 'HEAD'], cwd=ROOT).split(b'\0'):
    if item:
        meta, name = item.split(b'\t', 1)
        tracked[name.decode()] = meta.split()[2].decode()
changed = []
for name in sorted(paths):
    p = ROOT / name
    assert p.is_file() and not set(p.parts) & {'private', 'raw', '__pycache__'}
    data = p.read_bytes()
    assert len(data) < 2 * 1024 * 1024, (name, len(data))
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    if tracked.get(name) != blob:
        changed.append(name)
OUT.write_bytes((json.dumps({
    'paths': changed, 'receipt': BASE + 'publication/root-v51-release-staged-hygiene.json',
    'scope': 'Reviewed final Pages/portable proof, release adapters and current progress. No source HTTP/cookies, full producer member dump, site payload or archive staged.',
}, indent=2) + '\n').encode())
print(json.dumps({'paths': len(changed), 'bytes': sum((ROOT / name).stat().st_size for name in changed)}))
