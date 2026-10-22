"""Curate the final v56 documentation and receipts; never include private payloads."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / 'research/continuous-recovery-20261022'
read = lambda p: json.loads(p.read_bytes())
write = lambda p, d: p.write_bytes((json.dumps(d, ensure_ascii=False, indent=2)+'\n').encode())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', action='store_true')
    args = parser.parse_args()
    assert not (HERE / 'publication-paths-v56-final.json').exists(), 'Final checkpoint already prepared'
    close = read(HERE / 'publication/final-local-closeout.json')
    online = read(HERE / 'root-v56-online-acceptance.json')
    release = read(HERE / 'publication/v56-public-release-publish.json')
    anonymous = read(HERE / 'publication/v56-public-assets-acceptance.json')
    package = read(HERE / 'publication/v56-portable-acceptance.json')
    assert all(x['accepted'] for x in [close, online, release, anonymous]) and package['status'] == 'accepted'
    assert online['objects_verified'] == 22 and anonymous['release_id'] == release['release_id'] == 420776997
    assert not release['draft'] and close['continuation_enabled'] is False
    assert not close['active_owned_preview_or_batch_processes']
    free = shutil.disk_usage(ROOT).free
    assert free >= 11005853696
    now = datetime.now(timezone.utc)
    assert now < datetime.fromisoformat('2026-10-22T14:51:33+00:00')
    status = read(HERE / 'status.json')
    status.update({
        'phase': 'closed_v56_published', 'updated_utc': now.isoformat(), 'closed_utc': now.isoformat(),
        'current_local_version': 'v56', 'current_pages_version': 'v56', 'offline_release_version': 'v56',
        'continuation_enabled': False, 'automation_status': 'deleted', 'in_flight_network_batch': None,
        'latest_main_commit': '7dff875e341d9d11cbfeb6417665b12059575c75',
        'main_commit_scope': 'Accepted source/export checkpoint; the containing closing-documentation commit identifies the final main revision.',
        'final_sync_receipt_scope': 'The closing commit push/readback is retained locally as push-main-<commit>.json, alongside previous normal push receipts.',
        'disk_free_latest_bytes': free, 'new_related_payload_bytes': 85003,
        'new_download_payload_bytes': 22433, 'new_related_browser_image_bytes': 85003,
        'new_related_source_images_accepted': 60, 'new_related_image_downloads': 4,
        'cached_related_images_newly_integrated': 56, 'new_original_capture_images_accepted': 0,
        'pages_build_version': 'v56', 'pages_build_commit': online['pages_commit'],
        'pages_build_status': 'completed_success', 'pages_actions_run': str(online['actions_run']),
        'pages_online_verification': '22_changed_objects_accepted',
        'v56_online_acceptance': 'root-v56-online-acceptance.json', 'v56_portable_package_accepted': True,
        'v56_package_members': 10211, 'v56_package_extracted_bytes': 635822442,
        'v56_package_smoke_http_checks': len(package['smoke_paths']),
        'v56_release_id': release['release_id'], 'v56_release_published': True,
        'v56_public_assets_accepted': True, 'v56_release_url': release['html_url'],
        'bounded_remaining_targets': 331, 'bounded_target_baseline_version': 'v53',
        'bounded_target_baseline_count': 390, 'bounded_targets_connected_this_run': 59,
        'player_gallery_groups_still_missing_originals_and_thumbnails': 50,
        'player_gallery_screenshot_count': 1684,
        'owned_preview_processes_active': 0, 'workers_state': 'both_completed',
        'final_local_closeout': 'publication/final-local-closeout.json',
        'completion_summary': 'docs/recovery-summary-20261022.md', 'completed_within_authorized_window': True,
    })
    write(HERE / 'status.json', status)
    tasks = read(HERE / 'tasks.json')
    for task in tasks['tasks']:
        if task['id'] == 'PUBLISH':
            task.update({'state': 'accepted_v56_pages_release_and_portable', 'evidence': 'root-v56-online-acceptance.json',
                         'additional_evidence': ['publication/v56-portable-acceptance.json', 'publication/v56-public-assets-acceptance.json']})
        elif task['id'] == 'CLOSE':
            task.update({'state': 'accepted_local_closeout_and_closing_checkpoint', 'evidence': 'publication/final-local-closeout.json'})
    write(HERE / 'tasks.json', tasks)
    doc = ROOT / 'docs/continuous-recovery-20261022.md'
    section = '\n## v56最终发布与收尾\n\n'
    section += ('main的7dff875e已正常推送，Pages的ada74291部署构建39789068533于13:43 UTC成功。'
                '唯一线上核验批次在13:55–13:57 UTC完成，22个对象全部direct 200、实际响应体与本地一致，'
                '实收15,959,895字节；最小实际请求间隔6.390554秒。主代理随后逐个重读私有响应体并独立验收，原始HTTP与cookie未公开。'
                '[线上验收](../research/continuous-recovery-20261022/root-v56-online-acceptance.json)\n\n')
    section += ('v56离线包从新的带空格目录启动，122个路径的GET／HEAD与根跳转共245项检查通过。'
                '包为546,446,950字节，解压635,822,442字节，10,211个成员。13:55 UTC已公开'
                '[Release](https://github.com/vvcchh0/WOW-Encyclopedia-Deployable-Archive/releases/tag/archive-20080512-browser-20261022-v56)，'
                '13:57 UTC完成三个公开附件的匿名读取／HEAD与GitHub摘要核对；未再下载整个ZIP。'
                '[包内验收](../research/continuous-recovery-20261022/publication/v56-portable-acceptance.json) · '
                '[公开附件验收](../research/continuous-recovery-20261022/publication/v56-public-assets-acceptance.json)\n\n')
    section += ('本轮来源获取和导出已结束。五个逐一核对命令行身份的预览服务已停止，两名执行者均完成，'
                '自动接续wow-7-5已由原生工具删除。再次核对四个冻结清单／来源摘要未变；未重复遍历历史ZIP。'
                f'收尾检查D盘余量为{close["disk_free_bytes"]:,}字节，高于11,005,853,696字节安全线。'
                '未启动新的Wayback批次或付费Firecrawl获取。'
                '[收尾验收](../research/continuous-recovery-20261022/publication/final-local-closeout.json)\n\n')
    section += ('README与本轮回顾同步为v56；本段及其验收作为独立文档检查点正常commit/push。'
                '后续从[剩余331个非图库目标](../research/continuous-recovery-20261022/v56-remaining-resource-targets.json)与'
                '[图库调查](player-gallery-accessibility-20261020.md)接续，有新来源证据后再开启相应获取窗口。'
                '[累计回顾](recovery-summary-20261022.md)\n')
    text = doc.read_text('utf-8')
    assert section.splitlines()[1] not in text
    doc.write_bytes((text.rstrip()+'\n'+section).encode())
    paths = [
        'accept_v56_online.py', 'root-v56-changes22-go.json', 'root-v56-online-acceptance.json',
        'push-main-7dff875e.json', 'push-gh-pages-ada74291.json', 'v56-pages-prepare.json',
        'network/github-pages-v56-changes22/plan.json',
        'network/github-pages-v56-changes22/object-manifest.json',
        'network/github-pages-v56-changes22/input-bindings.json',
        'network/github-pages-v56-changes22/runtime/object-match-summary.json',
        'publication/pages-build-v56-20261022T134554Z.json', 'publication/query_v56_pages_build.py',
        'publication/v56-portable-acceptance.json', 'publication/v56-release-config.json',
        'publication/v56-release-runtime/create-upload-intent.json',
        'publication/v56-release-runtime/create-upload-receipt.json',
        'publication/v56-release-runtime/draft-visible-adapter-receipt.json',
        'publication/v56-public-release-publish.json', 'publication/v56-public-assets-acceptance.json',
        'publication/publish_reviewed_release.py', 'publication/v56-release-notes.md',
        'publication/v56-release-notes.managed.md', 'publication/verify_v56_public_assets.py',
        'publication/final-local-closeout.json', 'publication/record_final_closeout.py',
        'publication/prepare_final_checkpoint.py',
    ]
    relative = [(HERE / p).relative_to(ROOT).as_posix() for p in paths]
    manifest = HERE / 'publication-paths-v56-final.json'
    write(manifest, relative)
    relative += [manifest.relative_to(ROOT).as_posix(), '.gitignore', 'README.md', 'CHANGELOG.md',
                 'docs/README.md', 'docs/recovery-summary-20261022.md', 'docs/continuous-recovery-20261022.md',
                 (HERE / 'status.json').relative_to(ROOT).as_posix(), (HERE / 'tasks.json').relative_to(ROOT).as_posix()]
    assert len(relative) == len(set(relative))
    ignore = ROOT / '.gitignore'
    contents = ignore.read_bytes().replace(b'\r\n', b'\n')
    for rel in relative:
        line = ('!/'+rel).encode()
        if line not in contents.splitlines():
            contents += line+b'\n'
    ignore.write_bytes(contents)
    credential = re.compile(rb'(?:gh[pousr]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{30,}|(?im:^set-cookie:)|(?im:^(?:proxy-)?authorization:\s*(?:basic|bearer)\s+\S+))')
    for rel in relative:
        path = ROOT / rel
        assert path.is_file() and not path.is_symlink()
        assert not {'private', 'raw', '__pycache__'}.intersection(path.parts) and path.suffix != '.zip'
        assert path.stat().st_size < 8*1024*1024 and not credential.search(path.read_bytes()), rel
    if args.stage:
        subprocess.run(['git', 'add', '--']+relative, cwd=ROOT, check=True, timeout=90)
        subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ROOT, check=True, timeout=90)
        staged = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z'], cwd=ROOT, timeout=90).decode().strip('\0').split('\0')
        assert set(staged) <= set(relative) and len(staged) >= 30
    print(json.dumps({'curated_paths': len(relative), 'staged': args.stage, 'disk_free_bytes': free,
                      'private_payloads_or_archives': 0, 'credential_scan_flags': 0,
                      'closing_manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
