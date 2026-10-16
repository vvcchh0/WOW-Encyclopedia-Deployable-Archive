"""Root verification of current news illustration candidates and exclusions."""
import hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import quote,urlsplit
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016';D=B/'local-audit/v20-news-content20';S=R/'.scratch/pages-resources-20261016-v20';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=D/'v20-news-content20-public-candidates.json';d=json.loads(p.read_bytes());items=d['candidates'];assert len(items)==len({x['original'] for x in items})==20
prov=json.loads((S/'export-provenance.json').read_bytes());excluded={x['original_url'] for x in prov['files'] if x['kind']=='image_overlay'}
for n in ['root-aug-final3-source-acceptance.json','root-aug-cached19-source-acceptance.json','root-aug-late11-source-acceptance.json']:excluded.update(x['original'] for x in json.loads((B/'publication'/n).read_bytes())['accepted_images'])
refs=0;checks=0
for x in items:
    u=urlsplit(x['original']);assert u.hostname=='www.worldofwarcraft.com' and u.path.startswith('/news/images/') and Path(u.path).suffix.lower() in ('.jpg','.gif') and not u.query and x['original'] not in excluded
    assert x['cache']['positive_row_count']==0 and x['prior_evidence']['count']==0 and x['known_bad_capture'] is None
    refs+=x['occurrence_count_v20']
    for e in x['source_evidence']:
        q=S/e['path'];assert sha(q)==e['sha256'];line=q.read_text().splitlines()[e['line']-1]
        assert e['literal'] in line and e['requested']==x['original'] and (x['original'] in line or quote(x['original'],safe='') in line);checks+=1
result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'network_requests':0,'candidate_path':p.relative_to(R).as_posix(),'candidate_sha256':sha(p),'candidate_count':20,'image_references':refs,'literal_records_checked':checks,'existing_and_pending_originals_excluded':len(excluded),'scope':'Current original news body illustrations; no fresh archive queries or recovery inferred.'}
out=B/'publication/root-news-content20-candidates-acceptance.json';assert not out.exists();out.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result))
