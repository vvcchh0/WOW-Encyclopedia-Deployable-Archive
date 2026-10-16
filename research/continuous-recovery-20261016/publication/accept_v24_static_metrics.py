"""Root current static recount; reuse the accepted prior aggregate, not a duplicate old scan."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from accept_v23_static_metrics import scan
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;S=R/'.scratch/pages-resources-20261016-v24';P=R/'.scratch/pages-resources-20261016-v23'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=O/'root-v24-static-metrics-acceptance.json';assert not out.exists();prior_path=O/'root-v23-static-metrics-acceptance.json';prior=json.loads(prior_path.read_bytes());assert prior['accepted'] and prior['current_missing_occurrences']==1959 and prior['current_news_missing_occurrences']==574
    files,counter,news,allmarkers=scan(S);old=json.loads((P/'export-provenance.json').read_bytes());records={x['output_path']:x for x in old['files']};changed=[p for p in files if records[p]['derived_sha256']!=files[p]];assert len(files)==1104 and len(changed)==3 and all(p.startswith('news/') for p in changed),changed
    assert sum(news.values())==557 and len(counter)==1181 and sum(counter.values())==1942
    d={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'static_text_files':len(files),'prior_version':'v23','current_version':'v24','prior_unique_missing_images':prior['current_unique_missing_images'],'current_unique_missing_images':len(counter),'prior_missing_occurrences':1959,'current_missing_occurrences':sum(counter.values()),'removed_occurrences':1959-sum(counter.values()),'current_news_missing_occurrences':sum(news.values()),'current_news_unique_missing_images':len(news),'changed_static_text_files':changed,'all_placeholder_markers':allmarkers,'prior_acceptance_sha256':sha(prior_path),'export_provenance_sha256':sha(S/'export-provenance.json'),'scope':'Actual fixed1104 static files excluding _origins; original3368 dynamicgalleryentities remainseparate.'}
    out.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8');print(json.dumps(d))
if __name__=='__main__':main()
