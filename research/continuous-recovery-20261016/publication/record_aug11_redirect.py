"""Record a replay redirect and its pre-anchor digest without following it."""
import hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit
R=Path(__file__).resolve().parents[3];B=R/'research/continuous-recovery-20261016';D=B/'network/aug27-final3/output';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((D/'batch-report.json').read_bytes());state=json.loads((D/'state.json').read_bytes())
candidate=next(x for x in report['results'] if x['target_key']=='AUG27-11');selected=candidate['cdx']['selected'][0]
a=next(x for x in state['attempts'] if x.get('source_status')==302);headers_path=R/a['headers_path'];raw=headers_path.read_text(errors='replace');locations=re.findall(r'(?im)^location:\s*([^\r\n]*)',raw);assert len(locations)==1
target=locations[0];match=re.fullmatch(r'https://web\.archive\.org/web/(\d{14})id_/(http://www\.worldofwarcraft\.com/news/images/07-08/08-22-07-2\.jpg)',target);assert match and match[1]=='20080512231210' and match[2]==selected['original']
assert selected['timestamp']=='20080402080429' and selected['digest']=='MLUKMD2MO3CNVZGT2PCCNNXF7RDKJAA4'
receipt={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'network_requests':0,'automatic_redirects_followed':0,'original':selected['original'],'pre_anchor_indexed_capture':selected['timestamp'],'pre_anchor_cdx_digest':selected['digest'],'requested_replay':a['url'],'response_status':302,'observed_replay_location':target,'redirect_capture_timestamp':match[1],'after_anchor':True,'same_calendar_day':True,'source_header_sha256':sha(headers_path),'source_batch_report_sha256':sha(D/'batch-report.json'),'next_validation':'Query the exact original only within the same calendar-day later window, verify the later capture before replay, and compare its payload digest with the pre-anchor indexed digest. Preserve its actual date as an explicit supplement; do not silently follow redirects or label it a pre-anchor payload.'}
p=B/'publication/root-aug11-redirect-observation.json';assert not p.exists();p.write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt))
