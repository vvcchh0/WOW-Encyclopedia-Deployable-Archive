import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;S=R/'.scratch/pages-resources-20261016-v25'
sys.path.insert(0,str(R/'research/continuous-recovery-20261016/publication'))
from accept_v23_static_metrics import scan
if __name__=='__main__':
 out=O/'root-v25-static-metrics-acceptance.json';assert not out.exists();files,counter,news,markers=scan(S);assert len(files)==1104 and sum(news.values())==557
 d={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'version':'v25','static_text_files':len(files),'unique_missing_images':len(counter),'missing_occurrences':sum(counter.values()),'news_unique_missing_images':len(news),'news_missing_occurrences':sum(news.values()),'all_placeholder_markers':markers,'export_provenance_sha256':hashlib.sha256((S/'export-provenance.json').read_bytes()).hexdigest(),'scope':'Same1104statictextfiles excluding_origins; native3368gallerytargetsremainseparate.'};out.write_bytes((json.dumps(d,indent=2)+'\n').encode());print(json.dumps(d))
