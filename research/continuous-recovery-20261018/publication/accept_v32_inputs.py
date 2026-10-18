"""Root agreement of original sources, public copies, fixed maps and guarded v32 inputs."""
import datetime as dt
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT/'research/continuous-recovery-20261018'
PUB, LOCAL = RUN/'publication', RUN/'integration/v32'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
dest = PUB/'root-v32-input-acceptance.json'
assert not dest.exists()
pins = {
 'build_pages_v32.py':'b88a74633b488e07ac6570980733b1feab465523c7bf76da59cf304496dd2019',
 'execute_v32.py':'14a022cfd5750b0af00d8e87f6ae0af873dd81a137ab78b1597294c64316827a',
 'v32-primary-source-map.json':'939af6242b1e8cc9e62e09decd055b104cad7db4dcf17f42b9d002a4ed059318',
 'v32-supplement-source-map.json':'aeb391ba14f7debfbaf0a557a69bac693120ce2471da2d7162f5260602da6966',
 'v32-source-byte-audit.json':'8d37cfb59f80e4f64b6af00a2b220dcef61cc20d1e8448576d9b1cd2f794f768',
 'v32-impact-estimate.json':'f607bba28acee693ecaf6219e2ff233c436c457d270db37924145393f5f36fc5',
 'v32-input-preparation.json':'f83fa7053f2859ab87300f24f7438ced2db4aed2ef0b8689bd5b08148453c3bc',
 'v32-preflight.json':'d8b81b9bf571e999b376a07401e74299a5c9808b2011758ff3e4a21ff90507cd',
 'v32-input-proposal.md':'4b018fc1210fcfb3152da9f1c2ca8d5547a5bb2de92e29d7ce33d59eb02339c5',
 'v32-runner-preparation.md':'6f43a0223dc07f306954415957be7defbae0ba5b160c4fad80e8a26158d531bb'}
for name, wanted in pins.items():
    assert sha(LOCAL/name) == wanted, name
assert sha(ROOT/'tools/export_github_pages.py') == '8c50b1574f24a0bd2b03492ae8fe0cb7d3c48a50a247ba70d9e1859d58672afb'
assert sha(ROOT/'tools/historical_exhibits.py') == '35aa7e5928a6be4a07f2164708e32890aaa7257d89c6db923bf1311f950fd011'
assert sha(ROOT/'tools/publish_github_pages.py') == 'e7f4992dfdeae9f83f6771c538c8d55b084316fb2f2e73c92e874df319de9934'
assert sha(ROOT/'offline/build-manifest.json') == '397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459'

def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

builder=load('root_v32_preparation', LOCAL/'build_pages_v32.py')
runner=load('root_v32_guarded_runner', LOCAL/'execute_v32.py')
builder.verify_pinned_files()  # Read-only historical map/provenance pins; no old tool closure is rerun.
bindings=runner.required_bindings(builder)
sources,copies={},{}
receipts=[]
for family, count in [('news49',5),('next70',7)]:
    for n in range(1,count+1):
        for kind, target in [('source',sources),('public-copy',copies)]:
            path=PUB/f'root-{family}-batch{n}-{kind}-acceptance.json'
            data=read(path)
            assert data['accepted']
            receipts.append(path)
            for item in data['accepted_images']:
                assert item['original'] not in target
                target[item['original']]=item
entries=read(LOCAL/'v32-primary-source-map.json')['items']
assert not read(LOCAL/'v32-supplement-source-map.json')['items']
assert len(entries)==len(sources)==len(copies)==103
assert {x['original'] for x in entries}==set(sources)==set(copies)
checked=[]
for item in entries:
    source,copy=sources[item['original']],copies[item['original']]
    path=(ROOT/item['local_path']).resolve()
    path.relative_to((PUB/'accepted-images').resolve())
    assert item['local_path']==copy['local_path'] and not path.is_symlink()
    data=path.read_bytes()
    assert data==(ROOT/source['private_payload_path']).read_bytes()
    assert len(data)==item['length']==source['length']==copy['length']
    assert sha(path)==item['sha256']==source['sha256']==copy['sha256']
    assert item['actual_timestamp']==item['indexed_capture_timestamp']==source['actual_capture_timestamp']
    assert item['actual_timestamp']<='20080512210044'
    for key in ['mime','dimensions','decoded_frames','cdx_digest']:
        assert item[key]==source[key]==copy[key],(item['original'],key)
    assert item['original'].split('/')[2]=='www.worldofwarcraft.com'
    checked.append({'path':item['local_path'],'sha256':item['sha256'],'length':len(data)})
assert sum(x['length'] for x in checked)==1734198
preflight=read(LOCAL/'v32-preflight.json')
counts={'source_records':8357,'declared_files':8897,'actual_files':8898,
    'primary_overlays':350,'supplement_overlays':89,'total_overlays':439,'guide_previews':22,'guide_collection_images':39}
assert {key:preflight['expected_after_export'][key] for key in counts}==counts
runtime=preflight['expected_after_export']['runtime_allowed_changes']
assert runtime['historical_body_banner_pages']==5 and runtime['retired_armory_script']=='/new-hp/js/enhancedtip.js'
assert runtime['popup_runtime']=='__offline/pages_runtime.js' and runtime['attunement_mask_page']=='/bcattunement/index.html'
assert preflight['network_requests']==0 and preflight['export_executed'] is False
expectations=PUB/'v32-acceptance-expectations.json'
assert read(expectations)['expected_static_counts']['missing_occurrences']==1573
for p in receipts+[expectations,PUB/'prepare_v32_acceptance_expectations.py',Path(__file__)]:
    bindings[p.relative_to(ROOT).as_posix()]=sha(p)
site=ROOT/'.scratch/pages-resources-20261018-v32'
assert not site.exists() and not site.with_name(site.name+'.partial').exists()
assert not (LOCAL/'v32-build-receipt.json').exists()
free=shutil.disk_usage(ROOT).free
assert free>=11005853696
receipt={'accepted':True,'checked_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
    'map_bindings':[{'path':p,'sha256':s} for p,s in bindings.items()],
    'preflight_sha256':sha(LOCAL/'v32-preflight.json'),'public_image_copies':checked,
    'new_images':103,'image_bytes':1734198,'new_primary_images':103,'new_supplement_images':0,
    'network_requests':0,'export_executed':False,'disk_free_bytes':free,
    'scope':'103 exact source/private/public/map agreements. Preserve all336 prior overlays; include separately accepted runtime repairs and three derived mask references. Production browser acceptance remains required.'}
dest.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':True,'bindings':len(bindings),'images':len(checked),'receipt_sha256':sha(dest),'preflight_sha256':receipt['preflight_sha256']}))
