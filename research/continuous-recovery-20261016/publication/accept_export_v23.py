"""Root actual byte and source acceptance of the frozen v23 export."""
import hashlib,importlib.util,json,re,sys,shutil
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;B=R/'research/continuous-recovery-20261016';S=R/'.scratch/pages-resources-20261016-v23';P=R/'.scratch/pages-resources-20261016-v22'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=O/'root-v23-export-acceptance.json';assert not out.exists()
    h=O/'v23-qa-preparation/check_v23_offline.py';spec=importlib.util.spec_from_file_location('root_v23_check_core',h);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    assert sha(m.WORKER)==m.EXPECTED_WORKER_SHA and sha(m.ROOT_INPUT)==m.EXPECTED_ROOT_INPUT_SHA
    worker=json.loads(m.WORKER.read_bytes());gate=json.loads(m.ROOT_INPUT.read_bytes());assert worker['export_completed'] and gate['accepted'] and gate['single_export_go']
    for a in gate['bindings']:assert sha(R/a['path'])==a['sha256'],a['path']
    for stem in ['map_sha256','production_sha256']:
        assert worker[stem+'_before']==worker[stem+'_after']
        for path,digest in worker[stem+'_before'].items():assert sha(R/path)==digest,path
    assert sha(P/'export-provenance.json')==m.EXPECTED_V22_PROVENANCE_SHA
    assert json.loads((O/'root-v22-export-acceptance.json').read_bytes())['accepted']
    assert sha(R/'offline/build-manifest.json')=='397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459'
    assert sha(m.SOURCE_MANIFEST)==m.EXPECTED_MANIFEST_SHA and not S.with_name(S.name+'.partial').exists()
    p=json.loads((S/'export-provenance.json').read_bytes());old=json.loads((P/'export-provenance.json').read_bytes());assert len(p['files'])==len({x['output_path'] for x in p['files']})==8620
    errors=[];findings=[];tree=m.scan_tree(p,old,errors,findings);overlays=m.check_prior_overlays(p,old,errors);routing=m.check_routing(errors);sources=m.check_new_images(p,errors);guides=m.check_collections_and_previews(p,errors)
    assert all(p['stats'][k]==v for k,v in {'source_records':8357,'image_overlay_records':162,'primary_image_overlay_records':100,'supplement_image_overlay_records':62}.items())
    records={x['route']:x for x in p['files']};oldrecords={x['route']:x for x in old['files']};collection=p['guide_image_collections'];seen=set()
    for group in collection['groups']:
        for im in group['images']:
            assert im['route'] not in seen;seen.add(im['route']);rec=records[im['route']]
            assert (im['original'],im['sha256'],im['length'],im['actual_capture_timestamp'])==(rec['original_url'],rec['derived_sha256'],rec['derived_length'],rec['actual_capture_timestamp'])
        route=group['gallery_route'];before=(P/oldrecords[route]['output_path']).read_text(encoding='utf-8');after=(S/records[route]['output_path']).read_text(encoding='utf-8')
        for pattern in [r'addshots\([^;]+;',r'numShots\s*=\s*\d+\s*;']:
            assert re.findall(pattern,before)==re.findall(pattern,after),(route,pattern)
    assert len(seen)==32
    assert shutil.disk_usage(R).free>=11005853696
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':not errors and not findings,'export_provenance_sha256':sha(S/'export-provenance.json'),'prior_provenance_sha256':sha(P/'export-provenance.json'),'checker_sha256':sha(h),'root_checker_sha256':sha(Path(__file__)),'worker_receipt_sha256':sha(m.WORKER),'checked_declared_files':tree['declared_files'],'actual_files':tree['actual_files'],'checked_tree_bytes':tree['tree_bytes'],'changed_paths':tree['changed_paths'],'changed_scanned_files':tree['changed_scanned_files'],'hygiene_reused_identical_files':tree['hygiene_reused_identical_files'],'prior_overlay_check':overlays,'routing_conservation':routing,'new_source_images':sources,'guide_checks':guides,'collection_provenance_images_checked':32,'native_gallery_script_literals_unchanged':True,'stats':p['stats'],'errors':errors,'publication_findings':findings,'network_requests':0,'new_export_invocations':0,'published':False,'disk_free_bytes':shutil.disk_usage(R).free}
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:result[k] for k in ['accepted','checked_declared_files','actual_files','checked_tree_bytes','changed_scanned_files','errors','publication_findings']}));assert result['accepted']
if __name__=='__main__':main()
