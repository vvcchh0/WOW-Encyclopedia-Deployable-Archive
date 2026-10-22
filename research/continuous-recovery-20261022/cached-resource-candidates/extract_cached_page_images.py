from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
import json, hashlib, csv, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

INVROOTS=[
 'research/continuous-recovery-20261022/network/archivecraft-dungeons01/runtime',
 'research/continuous-recovery-20261021/network/archivecraft-pages01/runtime',
 'research/continuous-recovery-20261021/network/archivecraft-guides01/runtime',
 'research/continuous-recovery-20261021/network/archivecraft-bc-guides01/runtime',
]
class Extract(HTMLParser):
 def __init__(self,base):
  super().__init__(convert_charrefs=True); self.base=base; self.records=[]; self.anchors=[]; self.heading=''; self.hdepth=0; self.hbuf=[]; self.pdepth=0; self.pbuf=[]; self.lastp=''; self.ignored=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs); t=tag.lower()
  if t in ('script','style'): self.ignored+=1; return
  if t=='a': self.anchors.append(a)
  if re.fullmatch(r'h[1-6]',t): self.hdepth+=1; self.hbuf=[]
  if t=='p': self.pdepth+=1; self.pbuf=[]
  if t=='img':
   src=a.get('src') or a.get('data-src') or a.get('data-lazy-src') or ''
   if src:
    rec={'line':self.getpos()[0],'src':src,'resolved_src':urljoin(self.base,src),'href':urljoin(self.base,self.anchors[-1].get('href','')) if self.anchors and self.anchors[-1].get('href') else '', 'alt':a.get('alt',''), 'title':a.get('title',''), 'heading':self.heading, 'paragraph':re.sub(r'\s+',' ',' '.join(self.pbuf)).strip() or self.lastp}
    self.records.append(rec)
 def handle_startendtag(self,tag,attrs): self.handle_starttag(tag,attrs); self.handle_endtag(tag)
 def handle_data(self,data):
  if self.ignored: return
  if self.hdepth: self.hbuf.append(data)
  if self.pdepth: self.pbuf.append(data)
 def handle_endtag(self,tag):
  t=tag.lower()
  if t in ('script','style') and self.ignored: self.ignored-=1; return
  if re.fullmatch(r'h[1-6]',t) and self.hdepth:
   h=re.sub(r'\s+',' ',' '.join(self.hbuf)).strip()
   if h: self.heading=h[:180]
   self.hdepth-=1
  if t=='p' and self.pdepth:
   p=re.sub(r'\s+',' ',' '.join(self.pbuf)).strip()
   if p: self.lastp=p[:320]
   self.pdepth-=1
  if t=='a' and self.anchors: self.anchors.pop()

pages=[]
for root in INVROOTS:
 invp=Path(root)/'public-inventory.json'; inv=json.loads(invp.read_text(encoding='utf-8'))
 for n,rec in enumerate(inv.get('records',[]),1):
  target=rec['target_id']; body=Path(root)/'private'/'raw'/f'attempt-{n:02d}-{target}-direct.body'
  # Historical names do not necessarily contain a numbered suffix; resolve by suffix match if needed.
  if not body.exists():
   hits=list((Path(root)/'private'/'raw').glob(f'*{target}*body'))
   if len(hits)!=1: raise RuntimeError(f'body not unique for {target}: {hits}')
   body=hits[0]
  data=body.read_bytes(); actual=hashlib.sha256(data).hexdigest()
  if len(data)!=rec['body_bytes'] or actual!=rec['body_sha256']:
   raise RuntimeError(f'hash/length mismatch {body}: {len(data)} {actual}')
  parser=Extract(rec['url']); parser.feed(data.decode('utf-8',errors='replace'))
  pages.append({'id':target,'url':rec['url'],'observed_utc':rec['current_observed_utc'],'body_path':str(body),'body_sha256':actual,'body_bytes':len(data),'title':rec.get('title',''),'images':parser.records})

for p in pages:
 if p['id'] not in ('archivecraft-bc-jewelcrafting','archivecraft-bc-professions',): continue
 print('\n###',p['id'],p['title'],'count',len(p['images']))
 for x in p['images']:
  if x['line'] < 1000: continue
  print(f"L{x['line']} | heading={x['heading'][:80]} | src={x['resolved_src']} | href={x['href']} | alt={x['alt'][:90]} | p={x['paragraph'][:130]}")
