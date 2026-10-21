"""Bind current Arathi behavior and hosted objects, retaining unchanged v51 behavior proof."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
OUT = PUB / 'root-v52-final-acceptance.json'
assert not OUT.exists()
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
names = ['root-v52-code-acceptance.json', 'root-v52-export-acceptance.json',
         'root-v52-browser-acceptance.json', 'root-v52-local-acceptance.json',
         'root-v52-pages-online-acceptance.json']
receipts = {name: read(PUB/name) for name in names}
assert all(row['accepted'] for row in receipts.values())
local=receipts['root-v52-local-acceptance.json'];site=ROOT/local['local_site']
for row in local['bindings']:
    assert sha(ROOT/row['path'])==row['sha256'], row['path']
assert sha(site/'export-provenance.json')==local['export_provenance_sha256']
browser=receipts['root-v52-browser-acceptance.json']
assert browser['pages'][0]['restored_previews']==20 and browser['pages'][0]['remaining_previews']==2
assert all(not browser[k] for k in ('page_errors','request_failures','external_requests','http_errors'))
online=receipts['root-v52-pages-online-acceptance.json']
assert online['local_gate_sha256']==sha(PUB/'root-v52-local-acceptance.json')
assert online['accepted_objects']==len(online['objects'])==25
pages=read(PUB/'v52-pages-publication.json')['new_commit_sha']
for key in ('build_before','build_after'):
    assert online[key]['status']=='built' and online[key]['commit']==pages
prior=read(PUB/'root-v51-browser-acceptance.json')
assert prior['accepted'] and prior['pages'][0]['actual_popup_opens']==2
assert receipts['root-v52-export-acceptance.json']['changed_existing_files']==['pvp/battlegrounds/info-arathi.html']
helper='__offline/aldor-scryers-lore.js'
assert sha(site/helper)=='253475779f9f0246639453efb691896c930cc2285e4ecb15c265e7ba81ca2785'
report={
    'accepted':True,'version':'v52','checked_utc':datetime.now(timezone.utc).isoformat(),
    'scope':'Final derived site, actual Arathi browser behavior and25 hosted objects. Unchanged v51 behavior is retained via complete byte comparison; ZIP/release are separately validated.',
    'local_site':local['local_site'],'source_main_commit':read(PUB/'v52-main-commit.json')['commit'],
    'pages_commit':pages,'export_provenance_sha256':local['export_provenance_sha256'],
    'actual_files':local['actual_files'],'tree_bytes':local['tree_bytes'],'online_objects':25,
    'aldor_scryers_lore':{'accepted':True,'version':'v52','generated_relative':helper,
        'page_paths':['info/basics/factions/aldorscryers/aldor-scryers.xml.html',
                      'info/basics/factions/aldorscryers/aldor-scryers-tokens.xml.html'],
        'prior_behavior_acceptance':'research/continuous-recovery-20261021/publication/root-v51-browser-acceptance.json',
        'reuse':'Both pages and helper remain byte-identical.'},
    'bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in
        [*[PUB/name for name in names],PUB/'root-v51-browser-acceptance.json',Path(__file__)]],
}
OUT.write_bytes((json.dumps(report,indent=2)+'\n').encode())
print(json.dumps({'accepted':True,'version':'v52','online_objects':25}))
