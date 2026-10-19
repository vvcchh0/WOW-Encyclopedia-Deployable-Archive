"""Accept real scoped browser evidence and bind the87-object delta from livev35."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
RUN = PUB.parent
SITE = ROOT / '.scratch/pages-resources-20261019-v38'
LIVE = ROOT / '.scratch/pages-resources-20261019-v35'
BROWSER = RUN / 'integration/v38/browser'
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
READ = lambda p: json.loads(p.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': SHA(path), 'bytes': path.stat().st_size}


def main():
    out = PUB / 'root-v38-local-acceptance.json'
    browser_out = PUB / 'root-v38-browser-acceptance.json'
    assert not out.exists() and not browser_out.exists() and shutil.disk_usage(ROOT).free >= 11005853696
    tree_path = PUB / 'root-v38-export-acceptance.json'
    tree = READ(tree_path)
    assert tree['accepted'] and tree['actual_files'] == 9114 and tree['changed_paths_compared_v37'] == ['toplist/includes-client/js/logic.js']
    result_path = BROWSER / 'results/v38-browser-r1.json'
    receipt_path = BROWSER / 'v38-browser-run-receipt-r1.json'
    plan_path = BROWSER.parent / 'v38-browser-plan-r1.json'
    assert SHA(result_path) == '6fc0e40edf8bf644280217d90bee1d52979d9be5c4f1e6c4f50345554c9254a7'
    assert SHA(receipt_path) == 'ac19ccccad7af2e871334d11d7b5c350cf48f430d0d05f12da6459e92c20fb3a'
    result, run, plan = READ(result_path), READ(receipt_path), READ(plan_path)
    assert run['status'] == 'completed' and run['returncode'] == 0 and run['elapsed_seconds'] < 300
    assert result['status'] == 'completed_with_pending' and result['assertions']['mandatory_pass']
    assert all(result['assertions']['mandatory'].values())
    assert result['input']['sha256'] == run['input']['sha256'] == SHA(plan_path)
    assert result['output']['actual_files'] == 9114 and result['output']['provenance_sha256'] == tree['export_provenance_sha256']
    for key in ('page_errors', 'console_errors', 'server_errors', 'external_requests', 'toplist_data_requests', 'unrecorded_local_requests'):
        assert result[key] == [], key
    assert len(result['server_requests']) == 406 and all(r['status'] == 200 for r in result['server_requests'])
    assert len(result['news']['facts']) == 21
    for row in result['news']['facts']:
        assert row['status'] == 'passed' and row['dom_pass'] and row['http_assertion']['exact']
        assert row['asset_probe']['loaded'] and not row['asset_probe']['decode_error']
    top = result['toplist']
    assert top['script_runtime']['typeof_init'] == 'function' and top['script_runtime']['Prototype_Version'] == '1.5.0_rc1'
    for script in top['expected_scripts']:
        http = script['http_assertion']
        request = http['request']
        assert request['status'] == 200 and http['length_exact'] and http['sha256_exact']
        assert request['mime'].split(';')[0] in ('text/javascript', 'application/javascript')
        assert script['provenance']['mime'] == 'application/x-javascript' 
    assert top['initial']['data_state']['date_data_count'] == 0
    assert all(row['status'] == 'no_entry' and row['local_asset']['exact_target_url'] and row['http_assertion']['exact'] and row['local_probe']['loaded'] for row in top['css_candidates'])
    days = top['days_selector_observation']
    assert days['source_match'] and len(days['transitions']) == 3
    for row, expected in zip(days['transitions'], (1, 2, 1)):
        state = row['state']
        assert state['data_state']['num_of_tables'] == state['historical_missing_notice']['empty_table_count'] == expected
        assert state['data_state']['date_data_count'] == 0 and state['days_selector']['value'] == str(expected)
        assert len(state['historical_missing_notice']['visible_no_data']) == expected
        assert all(n['text'] == 'Historical ranking data for this date has not been recovered.' for n in state['historical_missing_notice']['visible_no_data'])
    assert result['assertions']['pending_count'] == 4
    screenshots = [ROOT / r['path'] for r in result['screenshots']]
    assert len(screenshots) == 2
    for row in result['screenshots']:
        assert SHA(ROOT / row['path']) == row['sha256']
    browser = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
        'export_provenance_sha256': tree['export_provenance_sha256'], 'external_requests': 0,
        'network_requests_to_external_sources': 0, 'actual_browser_requests': 406,
        'new_images_rendered': 21, 'reused_v36_rendered_targets': 48, 'reused_v35_rendered_targets': 24,
        'complete_historical_site_restored': False, 'javascript_mime_observation': 'Historical provenance records application/x-javascript; actual server supplies executable text/javascript. Both script response bytes/length/status are exact and runtime initializes. First local checker required legacy MIME equality and stopped before any receipt; corrected acceptance uses explicit modern JS MIME without changing the browser result.', 'pending': result['assertions']['pending'],
        'checks': [{'page': 'news/wow-news2004.html'}, {'page': 'toplist/index.html'}],
        'scope': 'Root reviewed both actual screenshots and all mandatory/local HTTP/DOM/script evidence. Real days1-to2-to1 changes empty tables with explicit unrecovered-data notices and no data requests. Ranking dataset0 and unavailable pagination controls remain declared limitations; they are not marked restored. Reuses unchanged v36/v35 image behavior through independently checked byte deltas.',
        'bindings': [bind(p) for p in (result_path, receipt_path, plan_path, PUB / 'root-v38-browser-execute-go.json', PUB / 'root-v37-derived-delta-acceptance.json', PUB / 'root-v36-image-layer-acceptance.json', PUB / 'root-v35-local-acceptance.json', *screenshots)]}
    browser_out.write_text(json.dumps(browser, indent=2)+'\n', encoding='utf-8')
    prov_path = SITE / 'export-provenance.json'
    provenance = READ(prov_path)
    assert SHA(prov_path) == tree['export_provenance_sha256']
    before = {r['output_path']: r for r in READ(LIVE / 'export-provenance.json')['files']}
    after = {r['output_path']: r for r in provenance['files']}
    new = set(after)-set(before)
    assert not (set(before)-set(after)) and len(new) == 72
    common = {p for p in before if (before[p]['derived_sha256'], before[p]['derived_length']) != (after[p]['derived_sha256'], after[p]['derived_length'])}
    assert len(common) == 14
    mime = {'.js': ['text/javascript', 'application/javascript'], '.json': ['application/json'], '.css': ['text/css'], '.html': ['text/html'], '.jpg': ['image/jpeg'], '.jpeg': ['image/jpeg'], '.gif': ['image/gif'], '.png': ['image/png']}
    objects = []
    for relative in sorted(new | common | {'export-provenance.json'}):
        path = SITE / relative
        row = {'path': relative, 'sha256': SHA(path), 'bytes': path.stat().st_size, 'mime': mime[path.suffix.lower()]}
        if relative in after:
            assert (row['sha256'], row['bytes']) == (after[relative]['derived_sha256'], after[relative]['derived_length'])
        objects.append(row)
    assert len(objects) == 87
    previous_pages = subprocess.check_output(['git', 'rev-parse', 'gh-pages'], cwd=ROOT, text=True, timeout=30).strip()
    assert previous_pages == '1eea9aae3cbb0c29a5097e409f32461e1aec39d5'
    paths = [tree_path, browser_out, PUB / 'root-v38-export-go.json', PUB / 'root-toplist-datafix-tools-acceptance.json', PUB / 'root-v37-tree-acceptance-r2.json', PUB / 'root-v37-derived-delta-acceptance.json', PUB / 'root-v36-image-layer-acceptance.json', BROWSER / 'check_v38_images_toplist_r1.cjs', BROWSER / 'execute_v38_browser_r1.py']
    local = {'accepted': True, 'published': False, 'checked_utc': datetime.now(timezone.utc).isoformat(),
        'version': 'v38', 'local_site': SITE.relative_to(ROOT).as_posix(), 'previous_pages_commit': previous_pages,
        'export_provenance_sha256': tree['export_provenance_sha256'], 'declared_files': 9113, 'actual_files': 9114,
        'tree_bytes': tree['tree_bytes'], 'image_overlays': 655, 'new_images_since_live_v35': 72,
        'current_run_new_image_files': 96, 'guide_collection_images': 39, 'guide_preview_images': 22,
        'external_requests': 0, 'historical_ranking_data_recovered': False, 'objects': objects,
        'bindings': [bind(p) for p in paths], 'scope': browser['scope']}
    out.write_text(json.dumps(local, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'accepted': True, 'version': 'v38', 'objects': 87, 'current_run_new_images': 96, 'published': False, 'ranking_dataset_recovered': False}))


if __name__ == '__main__':
    main()
