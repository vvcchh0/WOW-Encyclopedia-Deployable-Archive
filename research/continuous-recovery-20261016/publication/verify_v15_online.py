"""Reuse the accepted direct-first verifier for changed v15 and core objects."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
VERIFIER = ROOT / 'research/v14-integration/root_verify_pages_v14.py'

def main():
    binding = json.loads((OUT / 'v15-publication-binding.json').read_bytes())
    if not binding['accepted']:
        raise RuntimeError('Unaccepted local site')
    publication = json.loads((OUT / 'v15-pages-publication.json').read_bytes())
    if not publication.get('network_push_performed') or publication.get('push_returncode') != 0:
        raise RuntimeError('v15 was not pushed')
    spec = importlib.util.spec_from_file_location('v14_online_verifier', VERIFIER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = ROOT
    module.OUT = OUT
    module.SITE = ROOT / '.scratch/pages-resources-20261015-v15'
    module.EXPECTED_COMMIT = publication['new_commit_sha']
    module.PATHS = ['news/rss-08-2007.xml.html', 'news/rss-09-2007.xml.html',
        'news/newsarchive.css', '__offline/pages_runtime.js', '__offline/route-map.json',
        'new-hp/js/menu1_var.js', 'info/encyclopedia/index.xml.html', 'export-provenance.json']
    outcome = module.main()
    report_path = OUT / 'root-pages-online-acceptance.json'
    report = json.loads(report_path.read_bytes())
    report['verifier_source'] = str(VERIFIER.relative_to(ROOT)).replace('\\', '/')
    report['verifier_sha256'] = hashlib.sha256(VERIFIER.read_bytes()).hexdigest()
    report['prior_browser_acceptance'] = 'research/focused-recovery-20261015-2303/integration/root-browser-acceptance.json'
    report['prior_browser_acceptance_sha256'] = hashlib.sha256((ROOT / report['prior_browser_acceptance']).read_bytes()).hexdigest()
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return outcome

if __name__ == '__main__':
    raise SystemExit(main())
