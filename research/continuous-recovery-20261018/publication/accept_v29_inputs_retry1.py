"""Independently approve forty additional original-image inputs for v29."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'research/continuous-recovery-20261018'
LOCAL = BASE / 'integration/v29'
OUT = BASE / 'publication/root-v29-input-retry1-acceptance.json'
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    pins = {
        'build_pages_v29.py': 'cd202bfa5eabd008d635ee81e424c8f8cc248e16cc6f6acadb225a530afa52e0',
        'v29-primary-source-map.json': 'fc1e9f4e5da090fd22c6f8eea6d333f6899b01dedfc2dec2b106be98411d58ed',
        'v29-preflight.json': 'b29e1e7f69cf17391084d8fb0770008e1b850c9e9b2f92ad5900c65e68ab0194',
        'v29-input-preparation.json': 'c54913a8ef64fa8c824af6290c493d44ebda73910ba526facd3fe37f775a29fe',
        'v29-impact-estimate.json': '454b2c2abb1f9823e1297c4ef48535df522f954c2bc1e18162b9067594550b48',
        'v29-input-proposal.md': '120a0ae5e66bf6da05a82b19f3a99f2bf2c8906a1eab9e39c636093d565dd44c',
    }
    for name, digest in pins.items():
        assert sha(LOCAL / name) == digest, name
    status = read(BASE / 'status.json')
    for relative, expected in status['frozen_bindings'].items():
        for change in status['tool_supersessions']:
            if change['path'] == relative and change['prior_sha256'] == expected:
                proof = read(BASE / change['acceptance'])
                assert proof['accepted'] and proof['accepted_tool_sha256'] == change['accepted_sha256']
                expected = change['accepted_sha256']
        assert sha(ROOT / relative) == expected, relative
    tool_receipt = BASE / 'publication/root-historical-news-tool-retry1-acceptance.json'
    assert read(tool_receipt)['accepted']
    assert sha(ROOT / 'tools/historical_exhibits.py') == read(tool_receipt)['accepted_tool_sha256'] == '35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011'
    previous = ROOT / '.scratch/pages-resources-20261018-v28/export-provenance.json'
    assert sha(previous) == '6f42a33a67480f95b229e05611659d7ae4a562df1a3092a71f287532c936f793'
    assert len([x for x in read(previous)['files'] if x.get('role') == 'image_overlay']) == 263
    bindings, accepted, copies = [], {}, {}
    for number in range(5, 9):
        for kind in ['source', 'public-copy']:
            path = BASE / f'publication/root-news-unplanned-batch{number}-{kind}-acceptance.json'
            receipt = read(path)
            assert receipt['accepted']
            bindings.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)})
            selected = accepted if kind == 'source' else copies
            for item in receipt['accepted_images']:
                assert item['original'] not in selected
                selected[item['original']] = item
    paths = [LOCAL / name for name in ['v29-primary-source-map.json', 'v29-impact-estimate.json', 'v29-preflight.json']]
    entries = read(paths[0])['items']
    assert len(entries) == len(accepted) == len(copies) == 40
    assert {item['original'] for item in entries} == set(accepted) == set(copies)
    checked = []
    for item in entries:
        source, copy = accepted[item['original']], copies[item['original']]
        assert item['local_path'] == copy['local_path']
        path = (ROOT / item['local_path']).resolve()
        path.relative_to((BASE / 'publication/accepted-images').resolve())
        assert not path.is_symlink()
        data = path.read_bytes()
        assert data == (ROOT / source['private_payload_path']).read_bytes()
        assert len(data) == item['length'] == source['length'] == copy['length']
        assert sha(path) == item['sha256'] == source['sha256'] == copy['sha256']
        assert item['logical_url'] == item['original'] == source['original']
        assert item['actual_timestamp'] == item['indexed_capture_timestamp'] == source['actual_capture_timestamp']
        assert item['actual_timestamp'] <= '20080512210044'
        for key in ['mime', 'dimensions', 'decoded_frames', 'cdx_digest']:
            assert item[key] == source[key] == copy[key], (item['original'], key)
        checked.append({'path': item['local_path'], 'sha256': item['sha256'], 'length': len(data)})
    assert sum(x['length'] for x in checked) == 318622
    preflight = read(paths[-1])
    assert preflight['expected_after_export'] == {'declared_files': 8761, 'actual_files': 8762, 'primary_overlays': 228, 'supplement_overlays': 75, 'total_overlays': 303, 'guide_previews': 22, 'guide_collection_images': 39}
    assert preflight['network_requests'] == 0 and preflight['export_executed'] is False
    expectations = BASE / 'publication/v29-export-expectations.json'
    assert set(read(expectations)['new_output_paths']) == {item['original'].split('.com/', 1)[1] for item in entries}
    assert read(expectations)['removed_static_unique_addresses'] == read(expectations)['removed_static_occurrences'] == 40
    site = ROOT / '.scratch/pages-resources-20261018-v29'
    assert not site.exists() and not site.with_name(site.name + '.partial').exists()
    assert shutil.disk_usage(ROOT).free >= 11005853696
    paths.extend(LOCAL / name for name in pins if LOCAL / name not in paths)
    paths.extend([BASE / 'integration/v28/build_pages_v28.py', BASE / 'integration/v28/v28-primary-source-map.json', previous])
    bindings.extend({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)} for path in paths + [ROOT / 'tools/export_github_pages.py', ROOT / 'tools/historical_exhibits.py', tool_receipt, expectations])
    result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
              'map_bindings': bindings, 'preflight_sha256': sha(LOCAL / 'v29-preflight.json'), 'public_image_copies': checked,
              'new_images': 40, 'image_bytes': 318622, 'new_images_relative_v28': 40, 'image_bytes_relative_v28': 318622,
              'new_images_relative_live_v28': 40, 'image_bytes_relative_live_v28': 318622,
              'guide_collection_images': 39, 'network_requests': 0, 'export_executed': False,
              'scope': 'Independent exact source/copy/metadata agreement. All old maps and v28 remain frozen. Actual static marker expectations come from the root scan; the corrected historical-news tool preserves the existing global account-link pass.',
              'disk_free_bytes': shutil.disk_usage(ROOT).free}
    OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key not in ['map_bindings', 'public_image_copies']}))


if __name__ == '__main__':
    main()
