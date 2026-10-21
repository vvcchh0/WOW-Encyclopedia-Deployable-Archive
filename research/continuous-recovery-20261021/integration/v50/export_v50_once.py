"""Build v50 only after source and code acceptance of the faction lore repair."""
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
PREP = HERE / 'v50-input-preparation.json'
GO = PUB / 'root-v50-export-go.json'
OUTPUT = ROOT / '.scratch/pages-resources-20261021-v50'
FLOOR = 11005853696
CUTOFF = datetime(2026, 10, 21, 13, 5, 7, tzinfo=timezone.utc)
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def verify(rows):
    for row in rows:
        p = ROOT / row['path']
        assert p.resolve().is_relative_to(ROOT.resolve()) and p.is_file()
        assert sha(p) == row['sha256'], row['path']

def prepare():
    assert not PREP.exists() and not OUTPUT.exists()
    prior_path = ROOT / 'research/continuous-recovery-20261021/integration/v49/v49-input-preparation.json'
    prior = read(prior_path)
    code_path = PUB / 'root-v50-code-acceptance.json'
    code = read(code_path)
    assert code['accepted'] and code['tests']['skipped'] == 0
    assert read(PUB / 'root-v49-pages-online-acceptance.json')['accepted']
    assert read(PUB / 'root-aldor-scryers-lore-source-acceptance.json')['accepted']
    bindings = {r['path']: r['sha256'] for r in prior['bindings']}
    bindings.update({r['path']: r['sha256'] for r in code['code_bindings']})
    for p in (code_path, prior_path, PUB / 'root-v49-pages-online-acceptance.json',
              PUB / 'root-v49-local-acceptance.json',
              PUB / 'root-aldor-scryers-lore-source-acceptance.json', Path(__file__)):
        bindings[p.relative_to(ROOT).as_posix()] = sha(p)
    rows = [{'path': p, 'sha256': digest} for p, digest in sorted(bindings.items())]
    verify(rows)
    keys = ('source_site', 'source_manifest', 'primary_maps', 'supplement_maps',
            'guide_preview_map', 'guide_image_collection_map', 'flash_runtime_archive',
            'blizzcast_source_map', 'related_talent_icon_map', 'source16_layout_map',
            'related_talent_ui_map', 'talent_box_layout_map',
            'related_encyclopedia_image_map', 'related_guide_image_map')
    config = {k: prior[k] for k in keys}
    config.update(schema='wow-v50-input-preparation/v1',
                  prepared_utc=datetime.now(timezone.utc).isoformat(),
                  output=OUTPUT.relative_to(ROOT).as_posix(), bindings=rows,
                  restore_aldor_scryers_lore=True, prior_accepted_version='v49',
                  scope='One exact main faction page receives a generated helper containing two existing April 2 2008 lore literals; other pages, images, scripts and reward data are preserved.',
                  expected_helper_bytes=3273, expected_injected_pages=1,
                  new_original_2008_images=0, network_requests=0,
                  deadline_utc=CUTOFF.isoformat())
    PREP.write_bytes((json.dumps(config, indent=2) + '\n').encode())
    return {'prepared': True, 'bindings': len(rows), 'preparation_sha256': sha(PREP)}

def execute():
    config, gate = read(PREP), read(GO)
    assert gate['accepted'] and gate['export_go'] and gate['preparation_sha256'] == sha(PREP)
    assert datetime.now(timezone.utc) < CUTOFF and shutil.disk_usage(ROOT).free >= FLOOR
    assert not OUTPUT.exists() and not OUTPUT.with_name(OUTPUT.name + '.partial').exists()
    verify(config['bindings'])
    sys.path.insert(0, str(ROOT / 'tools'))
    import export_github_pages
    kwargs = {k: ROOT / config[k] for k in (
        'guide_preview_map', 'guide_image_collection_map', 'flash_runtime_archive',
        'blizzcast_source_map', 'related_talent_icon_map', 'related_talent_ui_map',
        'source16_layout_map', 'talent_box_layout_map',
        'related_encyclopedia_image_map', 'related_guide_image_map')}
    started = datetime.now(timezone.utc).isoformat()
    result = export_github_pages.export_pages(
        source_site=ROOT / config['source_site'], manifest_path=ROOT / config['source_manifest'],
        output=OUTPUT, base_path='/WOW-Encyclopedia-Deployable-Archive/', workspace_root=ROOT,
        min_free_bytes=FLOOR, image_source_maps=tuple(ROOT / p for p in config['primary_maps']),
        supplement_image_source_maps=tuple(ROOT / p for p in config['supplement_maps']),
        allow_later_image_supplements=True, restore_aldor_scryers_lore=True, **kwargs)
    receipt = {'status': 'export_executed_not_yet_accepted', 'started_utc': started,
               'finished_utc': datetime.now(timezone.utc).isoformat(),
               'preparation_sha256': sha(PREP), 'gate_sha256': sha(GO), 'result': result,
               'provenance_sha256': sha(OUTPUT / 'export-provenance.json'),
               'network_requests': 0, 'published': False}
    (HERE / 'v50-build-receipt.json').write_bytes((json.dumps(receipt, indent=2) + '\n').encode())
    return receipt

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--prepare', action='store_true')
    modes.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    print(json.dumps(prepare() if args.prepare else execute()))
