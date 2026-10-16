"""Root recount of the fixed static scope and forty exact resource candidates."""
import hashlib,html,json,re
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import parse_qs,urlsplit,quote
from accept_static_resource_inventory import normalize
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016';D=B/'local-audit/v20-next-assets';S=R/'.scratch/pages-resources-20261016-v20';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((D/'v20-next-assets-private-audit-v2.json').read_bytes());public=json.loads((D/'v20-next-assets-public-summary-v2.json').read_bytes());counts=Counter();news=Counter();scanned=0
for p in S.rglob('*'):
    if not p.is_file() or p.suffix.lower() not in ('.html','.htm','.xml','.css') or p.relative_to(S).as_posix().startswith('_origins/'):continue
    scanned+=1
    for m in re.finditer(r'missing-image\.svg\?([^"\x27<>\s\)]*)',p.read_text(errors='replace'),re.I):
        u=parse_qs(html.unescape(m.group(1)),keep_blank_values=True).get('requested',[''])[0];q=urlsplit(u)
        if q.scheme not in ('http','https') or Path(q.path.lower()).suffix not in ('.gif','.jpg','.jpeg','.png','.webp','.svg','.bmp'):continue
        counts[normalize(u)]+=1
        if p.relative_to(S).as_posix().startswith('news/'):news[normalize(u)]+=1
assert scanned==1104 and len(counts)==1220 and sum(counts.values())==2018
assert dict(counts)=={x['canonical']:x['occurrence_count_v20'] for x in a['entities']}
assert sum(news.values())==590
queue=public['queues'];assert len(queue)==len({x['canonical'] for x in queue})==40
assert Counter(x['queue'][0] for x in queue)=={'A':20,'B':20}
for x in queue:
    assert counts[x['canonical']]==x['occurrence_count_v20'] and x['cache']['positive_row_count']==0
    u=urlsplit(x['original']);assert not u.query and not u.fragment
    if x['queue'][0]=='A':assert u.hostname in ('www.worldofwarcraft.com','worldofwarcraft.com')
    else:assert u.hostname in ('imgs.worldofwarcraft.co.kr','www.wowarmory.com','armory.wow-europe.com')
    for e in x['current_v20_evidence']:
        p=S/e['path'];assert sha(p)==e['sha256'];line=p.read_text().splitlines()[e['line']-1]
        assert e['literal'] in line and (e['requested'] in line or quote(e['requested'],safe='') in line)
receipt={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'network_requests':0,'static_text_files':scanned,'exact_image_entities':len(counts),'exact_image_marker_occurrences':sum(counts.values()),'news_marker_occurrences':sum(news.values()),'public_candidates':40,'main_candidates':20,'related_static_candidates':20,'all_candidate_literals_and_hashes_checked':True,'private_audit_sha256':sha(D/'v20-next-assets-private-audit-v2.json'),'public_summary_sha256':sha(D/'v20-next-assets-public-summary-v2.json'),'superseded_v1_scope_error':'v1 omitted XML/CSS: 55 files, 59 occurrences and 54 entities. v2 and this independent recount use the frozen v18 scope.','scope':'Static image placeholders excluding _origins; dynamic gallery targets counted separately.'}
p=B/'publication/root-v20-asset-queues-acceptance.json';assert not p.exists();p.write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt))
