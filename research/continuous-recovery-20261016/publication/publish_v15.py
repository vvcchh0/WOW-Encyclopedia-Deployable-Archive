"""Publish the independently rebound v15 through the existing isolated-index tool."""
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

def main():
    binding = json.loads((OUT / 'v15-publication-binding.json').read_bytes())
    if not binding['accepted'] or binding['provenance_sha256'] != 'be0c336f831e19e63dedc4ada87ed672c620863061f9696e42048dfc1cea890a':
        raise RuntimeError('v15 binding not accepted')
    # Append process-only Git settings without replacing any inherited settings.
    count = int(os.environ.get('GIT_CONFIG_COUNT', '0'))
    settings = [('http.proxy', 'http://127.0.0.1:7890'), ('http.lowSpeedLimit', '1024'), ('http.lowSpeedTime', '60')]
    for offset, (key, value) in enumerate(settings):
        os.environ[f'GIT_CONFIG_KEY_{count + offset}'] = key
        os.environ[f'GIT_CONFIG_VALUE_{count + offset}'] = value
    os.environ['GIT_CONFIG_COUNT'] = str(count + len(settings))
    spec = importlib.util.spec_from_file_location('publish_pages', ROOT / 'tools/publish_github_pages.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.build_commit(root=ROOT, site=ROOT / '.scratch/pages-resources-20261015-v15',
        branch='gh-pages', message='Publish v15: recover August 2007 news',
        report_path=OUT / 'v15-pages-publication.json', push=True)
    print(json.dumps({k: result.get(k) for k in ['new_commit_sha', 'network_push_performed', 'push_returncode', 'status']}))

if __name__ == '__main__':
    main()
