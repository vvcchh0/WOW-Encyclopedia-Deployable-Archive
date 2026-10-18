"""Independently approve the exact 27-image v27 input set and exporter."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'research/continuous-recovery-20261018'
LOCAL = BASE / 'integration/v27'
OUT = BASE / 'publication/root-v27-input-acceptance.json'
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    status = read(BASE / 'status.json')
    approved_tool = read(BASE / 'publication/root-blizzard-origin-tool-acceptance.json')
    assert approved_tool['accepted']
    for relative, expected in status['frozen_bindings'].items():
        if relative == 'tools/export_github_pages.py':
            assert expected == approved_tool['baseline_tool_sha256']
            expected = approved_tool['accepted_tool_sha256']
        assert sha(ROOT / relative) == expected, relative
    assert sha(ROOT / '.scratch/pages-resources-20261018-v26/export-provenance.json') == 'f5580948c5df72a744577e15bf9165ee7ec477c5adf4b458e5db0241acd9c332'
    bindings, accepted = [], {}
    for name in ['root-news8-next-source-acceptance.json', 'root-news20-batch1-source-acceptance.json', 'root-news20-batch2-source-acceptance.json']:
        path = BASE / 'publication' / name
        receipt = read(path)
        assert receipt['accepted']
        bindings.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)})
        for item in receipt['accepted_images']:
            assert item['original'] not in accepted
            accepted[item['original']] = item
    paths = [LOCAL / name for name in ['v27-primary-source-map.json', 'v27-blizzard-supplement-source-map.json', 'v27-impact-estimate.json', 'v27-preflight.json']]
    entries = read(paths[0])['items'] + read(paths[1])['items']
    assert len(entries) == len(accepted) == 27
    assert len(read(paths[0])['items']) == 23 and len(read(paths[1])['items']) == 4
    assert {item['original'] for item in entries} == set(accepted)
    copies = []
    for item in entries:
        source = accepted[item['original']]
        path = (ROOT / item['local_path']).resolve()
        path.relative_to(LOCAL / 'accepted-images')
        assert not path.is_symlink()
        data = path.read_bytes()
        assert data == (ROOT / source['private_payload_path']).read_bytes()
        assert len(data) == item['length'] == source['length']
        assert sha(path) == item['sha256'] == source['sha256']
        assert item['logical_url'] == item['original'] == source['original']
        assert item['actual_timestamp'] == item['indexed_capture_timestamp'] == source['actual_capture_timestamp']
        assert item['actual_timestamp'] <= '20080512210044'
        for key in ['mime', 'dimensions', 'decoded_frames', 'cdx_digest']:
            assert item[key] == source[key], (item['original'], key)
        copies.append({'path': item['local_path'], 'sha256': item['sha256'], 'length': len(data)})
    preflight = read(paths[-1])
    assert preflight['expected_after_export'] == {'declared_files': 8681, 'actual_files': 8682, 'primary_overlays': 148, 'supplement_overlays': 75, 'total_overlays': 223, 'guide_previews': 22, 'guide_collection_images': 39}
    assert preflight['network_requests'] == 0 and preflight['export_executed'] is False
    site = ROOT / '.scratch/pages-resources-20261018-v27'
    assert not site.exists() and not site.with_name(site.name + '.partial').exists()
    assert shutil.disk_usage(ROOT).free >= 11005853696
    bindings.extend({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)} for path in paths + [LOCAL / 'build_pages_v27.py', BASE / 'publication/root-blizzard-origin-tool-acceptance.json'])
    result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
              'map_bindings': bindings, 'preflight_sha256': sha(paths[-1]), 'public_image_copies': copies,
              'new_images': 27, 'image_bytes': sum(x['length'] for x in copies),
              'guide_collection_images': 39, 'network_requests': 0, 'export_executed': False,
              'scope': 'Exact new input set matches independently accepted source bytes; map prepared flags remain historical, and this external root receipt approves their frozen bytes. Manifest-only impact estimate is not the expected browser reference count.',
              'disk_free_bytes': shutil.disk_usage(ROOT).free}
    OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key not in ['map_bindings', 'public_image_copies']}))


if __name__ == '__main__':
    main()
