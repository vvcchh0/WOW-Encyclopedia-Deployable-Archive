"""Derive v38 from the same accepted v37 source closure, once and offline."""
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PUB = ROOT / 'research/continuous-recovery-20261019/publication'
GATE = PUB / 'root-v38-export-go.json'
OUT = ROOT / '.scratch/pages-resources-20261019-v38'
RECEIPT = HERE / 'v38-build-receipt.json'
FLOOR = 11005853696
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
READ = lambda p: json.loads(p.read_bytes())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--go', action='store_true')
    parser.add_argument('--child', action='store_true')
    args = parser.parse_args()
    gate = READ(GATE)
    assert gate['accepted'] is True and gate['export_go'] is True
    assert gate['output'] == OUT.relative_to(ROOT).as_posix()
    assert datetime.now(timezone.utc) < datetime(2026, 10, 19, 13, 30, tzinfo=timezone.utc)
    for row in gate['bindings']:
        assert SHA(ROOT / row['path']) == row['sha256'], row['path']
    assert shutil.disk_usage(ROOT).free >= FLOOR
    if args.child:
        assert os.environ.get('WOW_V38_CHILD') == '1'
        assert not OUT.exists() and not OUT.with_name(OUT.name+'.partial').exists()
        sys.path.insert(0, str(ROOT / 'tools'))
        import export_github_pages as exporter
        result = exporter.export_pages(
            source_site=ROOT / '.scratch/offline-navigation-20261015-v15/site',
            manifest_path=ROOT / '.scratch/offline-navigation-20261015-v15/build-manifest.json',
            output=OUT, base_path='/WOW-Encyclopedia-Deployable-Archive/',
            workspace_root=ROOT, max_bytes=None, min_free_bytes=FLOOR,
            image_source_maps=tuple(ROOT / p for p in gate['primary_maps']),
            supplement_image_source_maps=tuple(ROOT / p for p in gate['supplement_maps']),
            allow_later_image_supplements=True,
            guide_preview_map=ROOT / gate['guide_preview_map'],
            guide_image_collection_map=ROOT / gate['guide_image_collection_map'])
        print(json.dumps(result, default=str))
        return
    assert args.go and not RECEIPT.exists()
    assert not OUT.exists() and not OUT.with_name(OUT.name+'.partial').exists()
    started = datetime.now(timezone.utc)
    before = shutil.disk_usage(ROOT).free
    env = dict(os.environ, WOW_V38_CHILD='1')
    stdout = HERE / 'export.stdout.log'
    stderr = HERE / 'export.stderr.log'
    timed_out = False
    with stdout.open('xb') as outlog, stderr.open('xb') as errlog:
        try:
            child = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(Path(__file__).resolve()), '--child'], cwd=ROOT, env=env, stdout=outlog, stderr=errlog, timeout=600, check=False)
            returncode = child.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            returncode = None
    finished = datetime.now(timezone.utc)
    receipt = {'executed': True, 'started_utc': started.isoformat(), 'finished_utc': finished.isoformat(),
        'elapsed_seconds': (finished-started).total_seconds(), 'timeout_seconds': 600,
        'timed_out': timed_out, 'returncode': returncode, 'published': False, 'network_requests': 0,
        'output': OUT.relative_to(ROOT).as_posix(), 'root_gate_sha256': SHA(GATE),
        'disk_free_before_bytes': before, 'disk_free_after_bytes': shutil.disk_usage(ROOT).free,
        'export_completed': False}
    if returncode == 0 and not timed_out:
        provenance = READ(OUT / 'export-provenance.json')
        receipt.update(export_completed=True, export_provenance_sha256=SHA(OUT / 'export-provenance.json'),
            declared_files=len(provenance['files']), actual_files=sum(p.is_file() for p in OUT.rglob('*')),
            stats=provenance['stats'])
    RECEIPT.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    assert receipt['export_completed'] and receipt['disk_free_after_bytes'] >= FLOOR, receipt
    assert receipt['declared_files'] == 9113 and receipt['actual_files'] == 9114
    assert receipt['stats']['image_overlay_records'] == 655
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
