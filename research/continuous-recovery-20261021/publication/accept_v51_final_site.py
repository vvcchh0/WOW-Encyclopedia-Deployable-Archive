"""Bind the independently accepted v51 site before portable ZIP validation."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
OUT = PUB / 'root-v51-final-acceptance.json'
assert not OUT.exists(), 'preserve the existing acceptance'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
names = (
    'root-v51-code-acceptance.json', 'root-v51-export-acceptance.json',
    'root-v51-browser-acceptance.json', 'root-v51-local-acceptance.json',
    'root-v51-pages-online-acceptance.json',
)
receipts = {name: read(PUB / name) for name in names}
assert all(row['accepted'] is True for row in receipts.values())
local = receipts['root-v51-local-acceptance.json']
site = ROOT / local['local_site']
provenance_sha = sha(site / 'export-provenance.json')
assert provenance_sha == 'd7fbb990abaf23d6931c28341d0e459c880093990f73effe3be1dfa28a6f599f'
for binding in local['bindings']:
    assert sha(ROOT / binding['path']) == binding['sha256'], binding['path']
for name in ('root-v51-export-acceptance.json', 'root-v51-browser-acceptance.json'):
    assert receipts[name]['export_provenance_sha256'] == provenance_sha
browser = receipts['root-v51-browser-acceptance.json']
assert browser['asset_fulfillments'] == 0
for key in ('external_requests', 'page_errors', 'request_failures'):
    assert browser[key] == []
assert len(browser['pages']) == 5
assert browser['pages'][0]['actual_popup_opens'] == 2
for page in browser['pages'][1:]:
    assert page['placeholder'] is False
    assert page['letter_image']['width'] == page['letter_image']['height'] == 48
online = receipts['root-v51-pages-online-acceptance.json']
assert online['local_gate_sha256'] == sha(PUB / 'root-v51-local-acceptance.json')
assert online['accepted_objects'] == len(online['objects']) == len(local['objects']) == 80
expected_pages = '7494e7cc898b34f8f4c6a64922bde34b8dd2ee44'
for key in ('build_before', 'build_after'):
    assert online[key]['status'] == 'built' and online[key]['commit'] == expected_pages
source_commit = read(PUB / 'v51-main-commit.json')['commit']
assert source_commit == 'cdab4eed9c7055939c4a9bb707cc1fefcc3b7257'
assert read(PUB / 'v51-main-push.json')['accepted'] is True
lore_paths = [
    'info/basics/factions/aldorscryers/aldor-scryers.xml.html',
    'info/basics/factions/aldorscryers/aldor-scryers-tokens.xml.html',
]
helper = '__offline/aldor-scryers-lore.js'
for path in [helper, *lore_paths]:
    assert (site / path).is_file()
assert sha(site / helper) == '253475779f9f0246639453efb691896c930cc2285e4ecb15c265e7ba81ca2785'
report = {
    'schema': 'wow-final-site-acceptance/v1',
    'accepted': True, 'version': 'v51',
    'checked_utc': datetime.now(timezone.utc).isoformat(),
    'scope': 'Final derived site, actual browser behavior and exact hosted objects. Portable ZIP and release are separately checked after this gate.',
    'local_site': local['local_site'],
    'source_main_commit': source_commit,
    'pages_commit': expected_pages,
    'export_provenance_sha256': provenance_sha,
    'actual_files': local['actual_files'],
    'tree_bytes': local['tree_bytes'],
    'online_objects': 80,
    'aldor_scryers_lore': {
        'accepted': True, 'version': 'v51',
        'generated_relative': helper, 'page_paths': lore_paths,
        'source_acceptance': 'research/continuous-recovery-20261021/publication/root-aldor-scryers-lore-source-acceptance.json',
    },
    'bindings': [
        {'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)}
        for p in [*[PUB / name for name in names], Path(__file__)]
    ],
}
OUT.write_bytes((json.dumps(report, indent=2) + '\n').encode())
print(json.dumps({'accepted': True, 'version': 'v51', 'online_objects': 80,
                  'portable_validation_pending': True}))
