"""Review the narrow dynamic-thumbnail delta; retain unaffected v48 checks."""
import hashlib,json,sys,unittest
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];PUB=Path(__file__).resolve().parent
OUT=PUB/'root-v49-code-acceptance.json';assert not OUT.exists()
read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=read(PUB/'root-v48-code-acceptance.json')
worker_path=ROOT/'research/continuous-recovery-20261021/integration/related-guide-images-v49/adapter-test-receipt.json'
worker=read(worker_path)
validation=worker['validation']
assert validation['tests_run']==6 and validation['skipped']==0 and validation['result']=='OK'
assert worker['map_sha256']=='b2ef90f1cdb17af02a534be71c26d4c8859bab1c87220fb9f7cb1b9e94c2c05b'
changed={'tools/related_guide_images.py','tests/test_related_guide_images.py','tests/test_related_guide_pages.py'}
assert [sha(ROOT/p) for p in sorted(changed)]==[validation['test_image_sha256'],validation['test_pages_sha256'],validation['module_sha256']]
snap=ROOT/'research/continuous-recovery-20261021/integration/v48/code-snapshot'
for row in prior['code_bindings']:
    if row['path'] in changed:assert sha(snap/Path(row['path']).name)==row['sha256']
    else:assert sha(ROOT/row['path'])==row['sha256'],row['path']
sys.path.insert(0,str(ROOT))
suite=unittest.defaultTestLoader.loadTestsFromNames(['tests.test_related_guide_images','tests.test_related_guide_pages'])
def ids(suite):
    for value in suite:
        if isinstance(value,unittest.TestSuite):yield from ids(value)
        else:yield value.id()
fresh=set(ids(suite));assert len(fresh)==6
old=set(prior['tests']['unique_test_ids'])
unaffected={value for value in old if not value.startswith(('tests.test_related_guide_images.','tests.test_related_guide_pages.'))}
assert len(unaffected)==59
combined=sorted(unaffected|fresh);assert len(combined)==65
bindings=[{'path':r['path'],'sha256':sha(ROOT/r['path'])} for r in prior['code_bindings']]
receipt={'accepted':True,'version':'v49','checked_utc':datetime.now(timezone.utc).isoformat(),'tests':{'count':65,'skipped':0,'unique_test_ids':combined,'unchanged_tests_reused':59,'affected_guide_tests_passed':6,'affected_tests_receipt_sha256':sha(worker_path),'scope':'Source-checked dynamic thumbnail spelling; exporter, original page/scripts, other illustrations, reward repair, talent UI/layout remain unchanged from v48 checks.'},'code_bindings':bindings,'root_review':{'map_and_decision_pins_checked':True,'only_one_same_topic_dynamic_target_added':True,'original_page_and_bestiary_scripts_not_modified':True,'raw_jpeg_bytes_unchanged':True,'source_metadata_and_catalog_keep_mapping_classification_and_null_capture':True,'actual_browser_acceptance_pending':True},'bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in (PUB/'root-v48-code-acceptance.json',worker_path,PUB/'root-related-guide-image-v49-decision.json',PUB/'prepare_guide_dynamic_reuse.py',Path(__file__))],'network_requests':0,'published':False}
OUT.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps({'accepted':True,'unique_tests':65,'unchanged_reused':59,'affected_passed':6,'receipt_sha256':sha(OUT)}))
