"""Check every new v38 file and isolate its one-script delta from v37."""
import hashlib
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
SITE = ROOT / '.scratch/pages-resources-20261019-v38'
OLD = ROOT / '.scratch/pages-resources-20261019-v37'
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
READ = lambda p: json.loads(p.read_bytes())


def main():
    started = time.monotonic()
    out = PUB / 'root-v38-export-acceptance.json'
    assert not out.exists() and shutil.disk_usage(ROOT).free >= 11005853696
    gate_path = PUB / 'root-v38-export-go.json'
    gate = READ(gate_path)
    build_path = ROOT / 'research/continuous-recovery-20261019/integration/v38/v38-build-receipt.json'
    build = READ(build_path)
    assert build['export_completed'] and build['returncode'] == 0 and not build['timed_out']
    assert build['root_gate_sha256'] == SHA(gate_path) and build['elapsed_seconds'] < 600
    for row in gate['bindings']:
        assert SHA(ROOT / row['path']) == row['sha256'], row['path']
    provenance_path = SITE / 'export-provenance.json'
    assert SHA(provenance_path) == build['export_provenance_sha256'] == 'de6ee4348a688cf648a86bf2537fb7f8f60490721419e7f45aea6e881b590828'
    provenance = READ(provenance_path)
    files = {r['output_path']: r for r in provenance['files']}
    assert len(files) == len(provenance['files']) == 9113
    actual = {p.relative_to(SITE).as_posix() for p in SITE.rglob('*') if p.is_file()}
    assert actual == set(files) | {'export-provenance.json'}
    checked_bytes = 0
    for relative, row in files.items():
        path = (SITE / relative).resolve()
        path.relative_to(SITE)
        assert not path.is_symlink()
        data = path.read_bytes()
        assert len(data) == row['derived_length'] and hashlib.sha256(data).hexdigest() == row['derived_sha256'], relative
        checked_bytes += len(data)
    previous = {r['output_path']: r for r in READ(OLD / 'export-provenance.json')['files']}
    assert set(previous) == set(files)
    changes = [p for p in files if (files[p]['derived_sha256'], files[p]['derived_length']) != (previous[p]['derived_sha256'], previous[p]['derived_length'])]
    assert changes == ['toplist/includes-client/js/logic.js'], changes
    logic = (SITE / changes[0]).read_text('utf-8')
    assert 'var topListLocalDataRoutes = {};' in logic
    assert 'Historical ranking data for this date has not been recovered.' in logic
    assert 'xhr.open("GET", topListDataRoute, true);' in logic
    assert 'url(/toplist/images/table-left.jpg)' not in logic and 'url(/toplist/images/table-right.jpg)' not in logic
    assert (SITE / 'toplist/includes-client/js/prototype.js').read_bytes() == (ROOT / 'tests/fixtures/toplist-source15/prototype.js').read_bytes()
    assert not any(r['route'].startswith('/toplist/data/') for r in files.values())
    subprocess.run([r'C:\Users\17630\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe', '--check', str(SITE / changes[0])], check=True, timeout=30)
    stats = provenance['stats']
    assert stats['image_overlay_records'] == 655 and stats['primary_image_overlay_records'] == 555 and stats['supplement_image_overlay_records'] == 100
    assert stats['guide_image_collection_images'] == 39 and stats['guide_preview_count'] == 22
    result = {'accepted': True, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'site': SITE.relative_to(ROOT).as_posix(),
        'elapsed_seconds': time.monotonic()-started, 'hard_parent_timeout_seconds': 240,
        'declared_files': 9113, 'actual_files': 9114, 'tree_bytes': checked_bytes+provenance_path.stat().st_size,
        'export_provenance_sha256': SHA(provenance_path), 'image_overlays': 655, 'new_images_compared_v37': 0,
        'changed_paths_compared_v37': changes, 'source15_records': 8357, 'guide_collection_images': 39, 'guide_preview_images': 22,
        'network_requests': 0, 'published': False, 'browser_accepted': False,
        'bindings': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': SHA(p)} for p in (gate_path, build_path, PUB / 'root-toplist-datafix-tools-acceptance.json', PUB / 'root-v37-tree-acceptance-r2.json', PUB / 'root-v37-derived-delta-acceptance.json')],
        'scope': 'Every v38 file independently read and verified. Exactly one script changes from the frozen v37 tree; all96 accepted current-run image copies and prior content remain identical. Historical ranking data count0 is explicit, not a recovered dataset. Browser behavior is separate.'}
    assert shutil.disk_usage(ROOT).free >= 11005853696
    out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
