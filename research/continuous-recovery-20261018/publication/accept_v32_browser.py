"""Bind independent production-browser receipts after root screenshot inspection."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PUB=Path(__file__).resolve().parent
OUT=PUB/'root-v32-browser-acceptance.json'
assert not OUT.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
provenance=ROOT/'.scratch/pages-resources-20261018-v32/export-provenance.json'
assert sha(provenance)=='a071d47b65232f723c2e74112adab521eb124d22b57aa430437646f06f50d356'
receipts=['root-v32-controls-browser-acceptance.json',
    'root-v32-chart-browser-acceptance.json','root-v32-content-browser-retry4-acceptance.json']
bound=[];shots=[]
for name,expected in zip(receipts,[266,37,299]):
    p=PUB/name;a=read(p)
    assert a['accepted'] and len(a['checks'])==expected
    assert not a['errors'] and not a['external_requests']
    assert a['export_provenance_sha256']==sha(provenance)
    bound.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'checks':expected})
    for shot in a['screenshots']:
        s=PUB/shot;assert s.exists()
        shots.append({'path':s.relative_to(ROOT).as_posix(),'sha256':sha(s),'root_visual_inspection':True})
content=read(PUB/receipts[-1])
assert len(content['declaration_only_images'])==1
assert content['declaration_only_images'][0]['route']=='insider/12/images/12-magtheridon-design.jpg'
report={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),
    'export_provenance_sha256':sha(provenance),'checks':602,'browser_receipts':bound,
    'screenshots':shots,'root_visual_inspection':True,'external_requests':0,'errors':[],
    'new_originals_verified_over_local_http':103,'ordinary_originals_rendered':92,
    'source_css_declaration_only_images':content['declaration_only_images'],
    'coverage':['All49 newly recovered news images after original news expansion controls',
        'Ten equipment tabs and112 recovered icon occurrences; regional class icons',
        'Seven profession selectors and21 recipes; recovered material and socket images',
        'Static retired Armory tooltip and five real-body archive banners',
        'Persistent actual artwork popup and local missing-image popup',
        'Full attunement chart, eight path-image decodes, six hover controls and click locking'],
    'checker_findings':['Earlier image lookup could precede page normalization; retry waits on runtime and attached images.',
        'Collapsed news hides CSS artwork too; retry uses original expansion controls with frozen IDs.',
        'Magtheridon design.jpg is retained in a div.design CSS rule with zero matching source elements; served-byte acceptance is recorded without claiming visible display.'],
    'network_requests_to_external_sources':0}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':True,'checks':602,'screenshots':len(shots),'sha256':sha(OUT)}))
