"""Run the saved static audit and compactor against the frozen local v4 tree."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SITE = ROOT / '.scratch/pages-local-maintenance-20261014-v4'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    if (HERE / 'summary.json').exists() or (HERE / 'details-v4.json.gz').exists():
        raise SystemExit('refusing existing v4 evidence')
    audit = load('local_v4_audit_core', ROOT / 'research/local-maintenance-20261014/route-audit/audit_local_routes.py')
    audit.DERIVED = SITE
    audit.PROVENANCE_PATH = SITE / 'export-provenance.json'
    audit.ROUTEMAP_PATH = SITE / '__offline/route-map.json'
    audit.OUT = HERE
    if audit.main() != 0:
        raise SystemExit('source changed during static audit')
    compact = load('local_v4_compact_core', ROOT / 'research/local-maintenance-20261014/route-audit/compact_summary_v3.py')
    compact.AUDIT_DIR = HERE
    compact.SUMMARY_PATH = HERE / 'summary.json'
    compact.MARKDOWN_PATH = HERE / 'summary.md'
    compact.ARCHIVE_PATH = HERE / 'details-v4.json.gz'
    compact.main()
    text = compact.MARKDOWN_PATH.read_text(encoding='utf-8')
    text = text.replace('.scratch/pages-historical-exhibits-20261014-v3', '.scratch/pages-local-maintenance-20261014-v4')
    text = text.replace('The v3 source tree', 'The v4 source tree').replace('saved v3 JSON', 'saved v4 JSON')
    text = text.replace('Full v3 details:', 'Full v4 details:').replace('details-v3.json.gz', 'details-v4.json.gz')
    compact.MARKDOWN_PATH.write_text(text, encoding='utf-8', newline='\n')
    before = json.loads((ROOT / '.scratch/pages-historical-exhibits-20261014-v3/export-provenance.json').read_text(encoding='utf-8'))
    after = json.loads((SITE / 'export-provenance.json').read_text(encoding='utf-8'))
    old = {r['output_path']: (r['derived_sha256'], r['derived_length']) for r in before['files']}
    new = {r['output_path']: (r['derived_sha256'], r['derived_length']) for r in after['files']}
    changed = sorted(k for k in old.keys() & new.keys() if old[k] != new[k])
    comparison = {
        'baseline': '.scratch/pages-historical-exhibits-20261014-v3',
        'candidate': str(SITE.relative_to(ROOT)).replace('\\', '/'),
        'common_records': len(old.keys() & new.keys()),
        'unchanged_records': sum(old[k] == new[k] for k in old.keys() & new.keys()),
        'changed_paths': changed,
        'added_paths': sorted(new.keys() - old.keys()),
        'removed_paths': sorted(old.keys() - new.keys()),
        'flash_install_attributes_retired': sum(r.get('reference_counts', {}).get('flash_codebase_renamed', 0) for r in after['files']),
        'v4_provenance_sha256': hashlib.sha256((SITE / 'export-provenance.json').read_bytes()).hexdigest(),
    }
    (HERE / 'v3-v4-comparison.json').write_text(json.dumps(comparison, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(comparison, ensure_ascii=False))


if __name__ == '__main__':
    main()
