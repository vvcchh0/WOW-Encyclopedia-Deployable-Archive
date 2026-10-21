"""Bind actual v41 Flash views plus unchanged v40 regression pages."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];PUB=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
site=ROOT/'.scratch/pages-resources-20261021-v41';old=ROOT/'.scratch/pages-resources-20261021-v40'
current_path=PUB/'v41-browser-r2-result.json';current=read(current_path)
assert current['accepted'] and current['version']=='v41' and len(current['rows'])==3 and not current['external_requests']
for row in current['rows']:
    assert row['status']==200 and not row['errors'] and not row['failed_without_success'] and not row['http_errors']
    assert all(not o or o['display']=='none' or o['visibility']=='hidden' for o in row['mute_overlays'])
    assert row['players']=={'socket':5,'dance':1,'tuskarr':1}[row['kind']]
old_core_path=PUB/'v40-browser-r2-progress.json';old_core=read(old_core_path)
old_regression_path=PUB/'v40-browser-r3-result.json';old_regression=read(old_regression_path)
assert old_regression['accepted'] and not old_regression['external_requests']
carry=[r for r in old_core['rows'] if r['kind']=='downloads']+old_regression['rows']
assert len(carry)==4
for row in carry:
    assert row['status']==200 and not row['errors'] and not row['failed_without_success'] and not row['http_errors']
    rel=row['route'].lstrip('/');assert sha(site/rel)==sha(old/rel)
for rel in ['__offline/pages_runtime.js','__offline/compat.js','__offline/route-map.json']:
    assert sha(site/rel)==sha(old/rel)
visual=[]
for name in ['dwarf-a.png','tuskarr-a.png','socket-0-a.png']:
    p=PUB/'v41-browser-r2-screenshots'/name
    visual.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)})
out=PUB/'root-v41-browser-acceptance.json';assert not out.exists()
receipt={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'version':'v41',
    'export_provenance_sha256':sha(site/'export-provenance.json'),
    'actual_v41_changed_pages':3,'unchanged_v40_regression_pages_carried':4,
    'carried_routes':[r['route'] for r in carry],
    'root_visual_review':{'dwarf':'Male dwarf visibly dancing; mute icon and dark overlay removed.',
        'tuskarr':'Tuskarr model visible over the preserved page background; no mute overlay. No claim that every original animation is reproduced.',
        'socket':'Five original gem-slot sparks visibly render; each two-time capture differs.'},
    'cancelled_requests_note':'Two Ruffle WASM requests were cancelled by the browser; the same URL returned200 and all actual players rendered. These are retained in the browser result.',
    'external_requests':0,'unresolved_resource_failures':0,'script_errors':0,
    'remaining':'Only male dwarf SWF is available for the dance selector; other choices explicitly unavailable. The source ZIP download links still lead to local missing-resource information.',
    'visual_bindings':visual,
    'bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in [current_path,old_core_path,old_regression_path,PUB/'check_v41_browser.cjs',PUB/'root-v41-export-acceptance.json']]}
out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt))
