from pathlib import Path
import hashlib,json,time,shutil,urllib.request,urllib.error,urllib.parse,ssl
from datetime import datetime,timezone
ROOT=Path.cwd();HERE=Path(__file__).parent
read=lambda p:json.loads(p.read_bytes())
publication=read(HERE/'v55-public-release-publish.json');assert publication['accepted'] and not publication['draft']
last=None;rows=[];events=[]
for asset in publication['assets']:
 method='HEAD' if asset['name'].endswith('.zip') else 'GET'
 for proxy in (False,True):
  assert shutil.disk_usage(ROOT).free>=11005853696
  assert datetime.now(timezone.utc)<datetime.fromisoformat('2026-10-22T14:36:33+00:00')
  if last is not None:
   while time.monotonic()-last<5.2:time.sleep(max(.01,5.21-(time.monotonic()-last)))
  proxies={'https':'http://127.0.0.1:7890'} if proxy else {}
  opener=urllib.request.build_opener(urllib.request.ProxyHandler(proxies),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
  req=urllib.request.Request(asset['browser_download_url'],method=method,headers={'Accept-Encoding':'identity','User-Agent':'WoW-historical-archive-check/1.0'})
  last=time.monotonic();start=datetime.now(timezone.utc).isoformat()
  try:
   with opener.open(req,timeout=30) as r:
    status=r.status;length=int(r.headers['Content-Length']);host=urllib.parse.urlsplit(r.url).hostname
    body=b'' if method=='HEAD' else r.read(131073)
    assert status==200 and length==asset['bytes'] and len(body)<=131072
    assert host in {'github.com','release-assets.githubusercontent.com','objects.githubusercontent.com'}
    if method=='GET':assert len(body)==asset['bytes'] and hashlib.sha256(body).hexdigest()==asset['digest'].removeprefix('sha256:')
    rows.append({'name':asset['name'],'method':method,'status':status,'declared_bytes':length,'read_bytes':len(body),'body_sha256':hashlib.sha256(body).hexdigest() if method=='GET' else None,'remote_api_digest':asset['digest'],'final_host':host,'process_proxy':proxy,'checked_utc':start,'anonymous':True})
    events.append({'name':asset['name'],'method':method,'start_utc':start,'proxy':proxy,'status':status})
    break
  except urllib.error.HTTPError as exc:
   events.append({'name':asset['name'],'start_utc':start,'proxy':proxy,'status':exc.code});raise
  except (urllib.error.URLError,TimeoutError,ConnectionError,OSError) as exc:
   events.append({'name':asset['name'],'start_utc':start,'proxy':proxy,'transport_error':type(exc).__name__})
   if proxy:raise
assert len(rows)==3
out={'schema':'wow-public-release-anonymous-assets/v1','accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'version':'v55','release_id':publication['release_id'],'tag':publication['tag'],'objects':rows,'events':events,'zip_scope':'Anonymous HEAD length plus GitHub uploaded-asset SHA-256; full anonymous ZIP not downloaded again. Full local archive and packaged server accepted separately.','disk_free_after_bytes':shutil.disk_usage(ROOT).free}
p=HERE/'v55-public-assets-acceptance.json';assert not p.exists();p.write_bytes((json.dumps(out,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps({'accepted':True,'objects':len(rows)}))
