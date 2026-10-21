"""Prepare or execute one new derived v45 export; never overwrite old versions."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PUB = ROOT / 'research/continuous-recovery-20261021/publication'
PREP = HERE / 'v45-input-preparation.json'
GATE = PUB / 'root-v45-export-go.json'
CODE_ACCEPTANCE = PUB / 'root-v45-code-acceptance.json'
SOURCE_ACCEPTANCE = PUB / 'root-source16-local-acceptance.json'
OLD_GATE = ROOT / 'research/continuous-recovery-20261020/publication/root-v39-export-go.json'
SOURCE_SITE = ROOT / '.scratch/offline-non-gallery-20261021-v16/site'
SOURCE_MANIFEST = SOURCE_SITE.parent / 'build-manifest.json'
OLD_PROVENANCE = ROOT / '.scratch/pages-resources-20261020-v39/export-provenance.json'
RUFFLE = ROOT / '.scratch/ruffle-0.7.1-probe-20261021/ruffle-0.7.1-web-selfhosted.zip'
OUTPUT = ROOT / '.scratch/pages-resources-20261021-v45'
FLOOR = 11005853696
CUTOFF = datetime(2026, 10, 21, 13, 5, 7, tzinfo=timezone.utc)

def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8-sig'))

def verify(rows: list[dict]) -> None:
    for row in rows:
        path = ROOT / row['path']
        assert path.resolve().is_relative_to(ROOT.resolve())
        assert path.is_file() and sha(path) == row['sha256'], row['path']

def prepare() -> dict:
    assert not PREP.exists() and not OUTPUT.exists() and not OUTPUT.with_suffix('.partial').exists()
    old = read(OLD_GATE)
    assert old['accepted'] and old['export_go']
    # The current reviewed exporter supersedes only its old code binding.
    # Prior maps, payload provenance, and all frozen versions remain checked.
    old['guide_preview_map'] = 'research/continuous-recovery-20261021/integration/v43/source16-guide-preview-map.json'
    old['guide_image_collection_map'] = 'research/continuous-recovery-20261021/integration/v43/source16-guide-image-collection-map.json'
    old_rows = [row for row in old['bindings'] if row['path'] not in {'tools/export_github_pages.py', 'tools/historical_exhibits.py'}]
    verify(old_rows)
    code = read(CODE_ACCEPTANCE)
    assert code['accepted'] and code['scope'] == 'related_icons_historical_contest_and_layout_reuse_reviewed_pending_export_browser'
    verify(code['code_bindings'])
    assert sha(OLD_PROVENANCE) == '02b1cd43766288f96c879ef464d7198bb09d1085008ae3e500773d594f6c7760'
    assert sha(RUFFLE) == 'ef12edbee135d581a9cd523837d746da30a07a64dbf1cf472d2e472c656f4b5e'
    source_acceptance = read(SOURCE_ACCEPTANCE)
    assert source_acceptance['accepted']
    assert source_acceptance['source_manifest_sha256'] == sha(SOURCE_MANIFEST)
    reader_map = ROOT / 'research/continuous-recovery-20261021/integration/blizzcast-reader/input-source-map.json'
    source_inputs = read(reader_map)
    icon_map = ROOT / 'research/continuous-recovery-20261021/integration/related-talent-icons/input-map.json'
    icon_input = read(icon_map)
    icon_extra = [icon_map, ROOT / icon_input['decision'], ROOT / icon_input['source_acceptance']] + [ROOT / row['payload_path'] for row in icon_input['entries']]
    layout_map = ROOT / 'research/continuous-recovery-20261021/integration/source16/layout-compatibility/input-map.json'
    layout_input = read(layout_map)
    layout_extra = [layout_map, ROOT / layout_input['decision']]
    extra = icon_extra + layout_extra + [PUB / 'root-source16-guide-rebinding-acceptance.json', ROOT / old['guide_preview_map'], ROOT / old['guide_image_collection_map'], SOURCE_ACCEPTANCE, SOURCE_MANIFEST, CODE_ACCEPTANCE, OLD_GATE, OLD_PROVENANCE, RUFFLE, reader_map, ROOT / source_inputs['source_acceptance'], Path(__file__)] + [ROOT / row['payload_path'] for row in source_inputs['records']]
    bindings = {row['path']: row['sha256'] for row in old_rows + code['code_bindings']}
    for path in extra:
        bindings[path.relative_to(ROOT).as_posix()] = sha(path)
    result = {
        'schema': 'wow-v45-input-preparation/v1', 'status': 'prepared_local_only',
        'prepared_utc': datetime.now(timezone.utc).isoformat(),
        'network_requests': 0, 'exported': False, 'published': False,
        'source_site': SOURCE_SITE.relative_to(ROOT).as_posix(),
        'source_manifest': SOURCE_MANIFEST.relative_to(ROOT).as_posix(),
        'source_manifest_sha256': sha(SOURCE_MANIFEST),
        'output': OUTPUT.relative_to(ROOT).as_posix(),
        'primary_maps': old['primary_maps'], 'supplement_maps': old['supplement_maps'],
        'guide_preview_map': old['guide_preview_map'],
        'guide_image_collection_map': old['guide_image_collection_map'],
        'flash_runtime_archive': RUFFLE.relative_to(ROOT).as_posix(),
        'blizzcast_source_map': reader_map.relative_to(ROOT).as_posix(),
        'related_talent_icon_map': icon_map.relative_to(ROOT).as_posix(),
        'expected_related_talent_icons': 986,
        'source16_layout_map': layout_map.relative_to(ROOT).as_posix(),
        'expected_layout_reused_target_paths': 10,
        'bindings': [{'path': path, 'sha256': digest} for path, digest in sorted(bindings.items())],
        'expected_image_overlays': 657, 'new_original_images': 0,
        'expected_reading_pages': 5, 'expected_reader_files': 6, 'expected_talent_scripts': 2, 'expected_source16_main_pages': 8,
        'expected_flash_pages': 3, 'expected_flash_runtime_files': 10,
        'scope': 'Preserve accepted Source16/v43 content; add 986 separately attributed later related icons clarify historical contest entry wording and reuse ten existing same-site layout objects',
        'deadline_utc': CUTOFF.isoformat(),
    }
    PREP.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return result

def execute() -> dict:
    prep = read(PREP)
    gate = read(GATE)
    assert gate['accepted'] and gate['export_go'] and gate['preparation_sha256'] == sha(PREP)
    assert gate['output'] == prep['output'] == OUTPUT.relative_to(ROOT).as_posix()
    assert datetime.now(timezone.utc) < CUTOFF
    assert not OUTPUT.exists() and not OUTPUT.with_name(OUTPUT.name + '.partial').exists()
    assert shutil.disk_usage(ROOT).free >= FLOOR
    verify(prep['bindings'])
    sys.path.insert(0, str(ROOT / 'tools'))
    import export_github_pages
    started = datetime.now(timezone.utc).isoformat()
    result = export_github_pages.export_pages(
        source_site=SOURCE_SITE, manifest_path=SOURCE_MANIFEST, output=OUTPUT,
        base_path='/WOW-Encyclopedia-Deployable-Archive/', workspace_root=ROOT,
        min_free_bytes=FLOOR,
        image_source_maps=tuple(ROOT / path for path in prep['primary_maps']),
        supplement_image_source_maps=tuple(ROOT / path for path in prep['supplement_maps']),
        allow_later_image_supplements=True,
        guide_preview_map=ROOT / prep['guide_preview_map'],
        guide_image_collection_map=ROOT / prep['guide_image_collection_map'],
        flash_runtime_archive=RUFFLE,
        blizzcast_source_map=ROOT / prep['blizzcast_source_map'],
        related_talent_icon_map=ROOT / prep['related_talent_icon_map'],
        source16_layout_map=ROOT / prep['source16_layout_map'],
    )
    receipt = {
        'status': 'export_executed_not_yet_accepted', 'started_utc': started,
        'finished_utc': datetime.now(timezone.utc).isoformat(),
        'preparation_sha256': sha(PREP), 'gate_sha256': sha(GATE), 'result': result,
        'provenance_sha256': sha(OUTPUT / 'export-provenance.json'),
        'network_requests': 0, 'published': False,
    }
    (HERE / 'v45-build-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    return receipt

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', action='store_true')
    mode.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    result = prepare() if args.prepare else execute()
    print(json.dumps({key: value for key, value in result.items() if key != 'bindings'}, ensure_ascii=False))
