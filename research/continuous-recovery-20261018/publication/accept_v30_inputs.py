"""Root acceptance of the 33 static38 images and frozen v30 export inputs."""
import hashlib
import importlib.util
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261018'
LOCAL = RUN / 'integration/v30'
OUT = RUN / 'publication/root-v30-input-acceptance.json'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    pins = {
        'build_pages_v30.py': 'f9fbc95042d6f0e4894d280af6de5276db41746ccc6dc0fe5a8e8d3f6b027026',
        'execute_v30.py': '5e8524f73c58efeff117fba21ffa5e04233aa9afd81b6c5146b8bec7922fc2db',
        'v30-primary-source-map.json': '8f204f7ec9e07afa27f66a45ee5a0536f187aad141eac633e3a78d9b42a1274e',
        'v30-supplement-source-map.json': '53f84e21888dbc1ede9320ec9a177fde4bc73d993848f8a26d48da0531f02ce0',
        'v30-source-byte-audit.json': 'a43d06dc83ee795b574cd59cf186e1389cd410fbefbd8fd6d211ebc8bad2a8ba',
        'v30-impact-estimate.json': '0e3775503bb36318d47d82f0f7512216d569080000c404a9d78148ddcafe012a',
        'v30-input-preparation.json': '488170490743c5469f05088665dc9b60afc720af168626073f3ca18be3f2d803',
        'v30-preflight.json': 'ac821017c8b9a878db732f3d0cde8100b7677d5a0249d65f7dbf3b06f6a45e18',
        'v30-input-proposal.md': '8a01b5a95d634bd97544ded92e37682b2bbec031ad7a2d7e7bac03af40a4b67f',
        'v30-runner-preparation.md': 'd14172bec4dca63e10cc3ebc2de426299871f362ffcf753eff7aaf741610c658',
    }
    for name, expected in pins.items():
        assert sha(LOCAL / name) == expected, name
    status = read(RUN / 'status.json')
    for relative, expected in status['frozen_bindings'].items():
        for change in status['tool_supersessions']:
            if change['path'] == relative and change['prior_sha256'] == expected:
                proof = read(RUN / change['acceptance'])
                assert proof['accepted'] and proof['accepted_tool_sha256'] == change['accepted_sha256']
                expected = change['accepted_sha256']
        assert sha(ROOT / relative) == expected, relative
    previous = ROOT / '.scratch/pages-resources-20261018-v29/export-provenance.json'
    assert sha(previous) == '793e99ef3c55ef5d328f8f6773c15b86ca69a79e7504d1333a9c04364dca28f8'
    spec = importlib.util.spec_from_file_location('v30_preparation', LOCAL / 'build_pages_v30.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    frozen = builder.load_frozen_v28()
    closure = builder.validate_frozen_v29_closure(frozen)
    paths = [LOCAL / name for name in pins]
    paths += list(frozen.PRIMARY_MAPS) + list(frozen.SUPPLEMENT_MAPS)
    paths += [builder.V28_BUILDER, builder.V28_PRIMARY_MAP, builder.V28_PROVENANCE, builder.V28_RECEIPT,
              builder.V29_PRIMARY_MAP, builder.V29_PREPARATION, builder.V29_PREFLIGHT, builder.V29_RECEIPT,
              builder.V29_PROVENANCE, builder.SOURCE_MANIFEST, builder.ARMORY_TOOL_ACCEPTANCE,
              ROOT / 'tools/export_github_pages.py', ROOT / 'tools/historical_exhibits.py']
    sources, copies = {}, {}
    for number in range(1, 5):
        for kind, target in [('source', sources), ('public-copy', copies)]:
            path = RUN / f'publication/root-static38-batch{number}-{kind}-acceptance.json'
            receipt = read(path)
            assert receipt['accepted']
            paths.append(path)
            for item in receipt['accepted_images']:
                assert item['original'] not in target
                target[item['original']] = item
    entries = read(LOCAL / 'v30-primary-source-map.json')['items'] + read(LOCAL / 'v30-supplement-source-map.json')['items']
    assert len(entries) == len(sources) == len(copies) == 33
    assert {x['original'] for x in entries} == set(sources) == set(copies)
    checked = []
    for item in entries:
        source, copy = sources[item['original']], copies[item['original']]
        assert item['local_path'] == copy['local_path']
        path = (ROOT / item['local_path']).resolve()
        path.relative_to((RUN / 'publication/accepted-images').resolve())
        assert not path.is_symlink()
        data = path.read_bytes()
        assert data == (ROOT / source['private_payload_path']).read_bytes()
        assert len(data) == item['length'] == source['length'] == copy['length']
        assert sha(path) == item['sha256'] == source['sha256'] == copy['sha256']
        assert item['logical_url'] == item['original']
        assert item['actual_timestamp'] == item['indexed_capture_timestamp'] == source['actual_capture_timestamp']
        assert item['actual_timestamp'] <= '20080512210044'
        for key in ['mime', 'dimensions', 'decoded_frames', 'cdx_digest']:
            assert item[key] == source[key] == copy[key], (item['original'], key)
        checked.append({'path': item['local_path'], 'sha256': item['sha256'], 'length': len(data)})
    assert sum(x['length'] for x in checked) == 156857
    preflight = read(LOCAL / 'v30-preflight.json')
    assert preflight['expected_after_export'] == {'source_records': 8357, 'declared_files': 8794, 'actual_files': 8795,
        'primary_overlays': 247, 'supplement_overlays': 89, 'total_overlays': 336, 'guide_previews': 22, 'guide_collection_images': 39}
    assert preflight['network_requests'] == 0 and preflight['export_executed'] is False
    expectations = RUN / 'publication/v30-export-expectations.json'
    expected = read(expectations)
    assert expected['removed_static_unique_addresses'] == 33 and expected['removed_static_occurrences'] == 142
    assert expected['stats']['output_files'] == 8794
    paths += [expectations, RUN / 'publication/prepare_overlay_expectations.py', Path(__file__)]
    site = ROOT / '.scratch/pages-resources-20261018-v30'
    assert not site.exists() and not site.with_name(site.name + '.partial').exists()
    assert not (LOCAL / 'v30-build-receipt.json').exists()
    free = shutil.disk_usage(ROOT).free
    assert free >= 11005853696
    unique = dict.fromkeys(paths)
    result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
              'map_bindings': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)} for p in unique],
              'preflight_sha256': sha(LOCAL / 'v30-preflight.json'), 'public_image_copies': checked,
              'new_images': 33, 'image_bytes': 156857, 'new_primary_images': 19, 'new_supplement_images': 14,
              'network_requests': 0, 'export_executed': False, 'disk_free_bytes': free,
              'frozen_closure': closure,
              'scope': 'Root source/private/public/map metadata agreement; actual frozen-page scan predicts 142 restored static references on five pages. Old maps and original bytes stay frozen.'}
    OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['accepted', 'new_images', 'image_bytes', 'disk_free_bytes']}))


if __name__ == '__main__':
    main()
