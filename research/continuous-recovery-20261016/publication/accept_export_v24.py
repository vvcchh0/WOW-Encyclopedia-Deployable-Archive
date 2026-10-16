"""Root actual full-byte acceptance of final v24."""
import hashlib,importlib.util,json,sys,shutil
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;B=R/'research/continuous-recovery-20261016';S=R/'.scratch/pages-resources-20261016-v24';P=R/'.scratch/pages-resources-20261016-v23'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=O/'root-v24-export-acceptance.json';assert not out.exists();h=O/'v24-qa-preparation/check_v24_offline.py';spec=importlib.util.spec_from_file_location('root_v24_byte_core',h);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);assert m.ROOT==R
    worker=json.loads(m.WORKER.read_bytes());gate=json.loads((O/'root-v24-final-input-acceptance.json').read_bytes());assert worker['export_completed'] and gate['accepted'] and gate['single_export_go'] and gate['fresh_images']==17
    for x in gate['bindings']:assert sha(R/x['path'])==x['sha256'],x['path']
    assert worker['input_hashes_before']==worker['input_hashes_after']
    for path,digest in worker['input_hashes_after'].items():assert sha(R/path)==digest,path
    assert sha(P/'export-provenance.json')==m.EXPECTED_PRIOR_V23_PROVENANCE_SHA and json.loads((O/'root-v23-export-acceptance.json').read_bytes())['accepted']
    assert sha(R/'offline/build-manifest.json')=='397f7dcdbc774d80c6f8c1f3dabf7933211ff182427bd2ef77c895752334f459'
    p=json.loads((S/'export-provenance.json').read_bytes());old=json.loads((P/'export-provenance.json').read_bytes());assert len(p['files'])==len({x['output_path'] for x in p['files']})==8637
    assert not S.with_name(S.name+'.partial').exists();errors=[];findings=[];tree=m.scan_tree(p,old,errors,findings);overlay=m.check_prior_overlays(p,old,errors);routing=m.check_routing(errors);images=m.check_new_images(p,errors);guides=m.check_collections_and_previews(p,errors)
    assert images['unique_routes']==17 and images['accepted_bytes']==172648
    assert all(p['stats'][k]==v for k,v in {'source_records':8357,'image_overlay_records':179,'primary_image_overlay_records':117,'supplement_image_overlay_records':62}.items())
    assert shutil.disk_usage(R).free>=11005853696
    d={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':not errors and not findings,'export_provenance_sha256':sha(S/'export-provenance.json'),'prior_provenance_sha256':sha(P/'export-provenance.json'),'root_checker_sha256':sha(Path(__file__)),'checker_sha256':sha(h),'worker_receipt_sha256':sha(m.WORKER),'checked_declared_files':tree['declared_files'],'actual_files':tree['actual_files'],'checked_tree_bytes':tree['tree_bytes'],'changed_paths':tree['changed_paths'],'changed_scanned_files':tree['changed_scanned_files'],'hygiene_reused_identical_files':tree['hygiene_reused_identical_files'],'prior_overlay_check':overlay,'routing_conservation':routing,'new_source_images':images,'guide_checks':guides,'stats':p['stats'],'errors':errors,'publication_findings':findings,'network_requests':0,'new_export_invocations':0,'published':False,'disk_free_bytes':shutil.disk_usage(R).free}
    out.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:d[k] for k in ['accepted','checked_declared_files','actual_files','checked_tree_bytes','changed_scanned_files','errors','publication_findings']}));assert d['accepted']
if __name__=='__main__':main()
