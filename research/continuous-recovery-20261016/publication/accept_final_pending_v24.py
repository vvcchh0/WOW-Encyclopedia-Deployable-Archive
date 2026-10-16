"""Verify the final worker consolidation against frozen evidence without rescanning."""
import collections,gzip,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3]; B=R/'research/continuous-recovery-20261016'; P=B/'publication'; D=B/'local-audit/final-v24-pending'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
def main():
 out=P/'root-final-v24-pending-acceptance.json';assert not out.exists()
 summary=read(D/'public-summary.json');manifest=read(D/'artifacts.json');assert summary['network_requests']==0
 for a in manifest['artifacts']:
  p=D/a['path'];assert p.is_file() and sha(p)==a['sha256'] and p.stat().st_size==a['bytes']
 for b in summary['source_bindings']:
  p=(R if b['path'].startswith(('.scratch/','research/')) else B)/b['path'];assert p.is_file() and sha(p)==b['sha256'] and p.stat().st_size==b['bytes'],b['path']
 c=read(P/'root-v24-static-metrics-acceptance.json');q=json.loads(gzip.decompress((D/'private/static-missing-counter.json.gz').read_bytes()))
 assert len(q['counter'])==1181 and sum(q['counter'].values())==1942
 assert len(q['news_counter'])==551 and sum(q['news_counter'].values())==557
 for k in ['static_files','unique_missing_images','missing_occurrences','news_unique_missing_images','news_missing_occurrences']:
  ref={'static_files':c['static_text_files'],'unique_missing_images':c['current_unique_missing_images'],'missing_occurrences':c['current_missing_occurrences'],'news_unique_missing_images':c['current_news_unique_missing_images'],'news_missing_occurrences':c['current_news_missing_occurrences']}[k];assert q['counts'][k]==ref
 n=read(D/'native-gallery-statuses.json');a=read(B/n['source_binding']['path'])
 keys=['gallery','category','slot','kind','original_url','status']
 assert n['records']==[{k:x[k] for k in keys} for x in a['entities']]
 counts=dict(collections.Counter(x['status'] for x in n['records']));assert counts=={'archive_404':79,'transport_unknown':47,'never_requested':3242}
 candidates=[x for f in ['full-images20-candidates.json','remaining20-candidates.json','remaining9-candidates.json'] for x in read(B/'local-audit/gallery-neighbors'/f)['candidates']]
 accepted=[x for f in ['v23-neighbor-supplement-source-map-final40.json','v23-neighbor-supplement-catalog-map-final40.json'] for x in read(B/'integration'/f)['items']]
 expected={x['original'] for x in candidates}-{x['original'] for x in accepted};pri=summary['pending_priorities']
 assert len(expected)==9 and {x['original'] for x in pri['gallery_neighbors']['items']}==expected
 assert len(pri['news_content02_03']['items'])==3 and {x['rank'] for x in pri['news_content02_03']['items']}=={13,14,18}
 old=pri['news_content01'];assert old['count']==8 and old['candidate_queue_path']=='local-audit/v20-news-content20/v20-news-content20-public-candidates.json'
 assert sha(B/old['candidate_queue_path'])==old['candidate_queue_sha256']
 assert read(B/'local-audit/gallery-final-v7/gallery-prefix-registry-v7.json')['stats']['full_window_complete_groups']==50
 proof={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'network_requests':0,'new_static_scans':0,'bindings':[bind(D/x) for x in ['public-summary.json','public-summary.md','consolidate_v24_pending.py','artifacts.json','native-gallery-statuses.json','private/static-missing-counter.json.gz']],'static_missing_entities':1181,'static_missing_references':1942,'news_missing_entities':551,'news_missing_references':557,'native_entities':3368,'native_status_counts':counts,'positive_neighbor_pending':9,'fresh_news_unknown':3,'older_news_unknown':8,'metadata_repairs':['CONTENT01 queue pointer corrected to frozen v20 candidates','Private counter manifest path corrected; first attempt retained locally'],'scope':'Independent source binding, Counter arithmetic, complete native entity projection and pending-set checks; no new acquisition.'}
 out.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in proof.items() if k not in ('bindings','metadata_repairs')}))
if __name__=='__main__':main()
