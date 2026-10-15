import pathlib,json,hashlib,datetime,re,base64,html,urllib.parse,collections
P=pathlib.Path('research/continuous-recovery-20261015');D=P/'network-rss21'
def read(q):return json.loads(q.read_text(encoding='utf-8'))
def meta(q):return {'path':q.as_posix(),'bytes':q.stat().st_size,'sha256':hashlib.sha256(q.read_bytes()).hexdigest()}
def dt(x):return datetime.datetime.fromisoformat(x.replace('Z','+00:00'))
def norm(url):
 u=urllib.parse.urlsplit(url);return (u.scheme,u.hostname,u.port or (80 if u.scheme=='http' else 443),u.path,u.query)
def source_header(q):
 out=[]
 for block in re.split(r'\r?\n\r?\n',q.read_text(encoding='latin-1')):
  lines=block.splitlines()
  if not lines:continue
  m=re.match(r'HTTP/\S+\s+(\d+)(.*)',lines[0],re.I)
  if m and 'connection established' not in m.group(2).lower():out.append((int(m.group(1)),{k.lower():v.strip() for line in lines[1:] if ':' in line for k,v in [line.split(':',1)]}))
 return out[-1] if out else (None,{})
r=read(D/'batch-report.json');j=read(D/'dispatch-log.json');errors=[];attempts={};selected=[];summaries=[];traceclocks={};allcdx=0
counts={'/news/rss-08-2006.xml':35,'/news/rss-10-2006.xml':53}
for x in r['results']:
 for a in x['cdx'].get('attempts',[]):attempts[a['attempt']]=a
 for hop in x.get('replay_hops',[]):
  for a in hop['attempts']:attempts[a['attempt']]=a
 for a in x['cdx'].get('attempts',[]):
  if a['source_status']!=200:continue
  data=read(D/a['raw']['body']);fields=data[0];rows=[dict(zip(fields,y)) for y in data[1:] if isinstance(y,list)];allcdx+=len(rows)
  if len(rows)!=x['cdx']['capture_index_count']:errors.append('CDX count '+x['target'])
  for actual,declared in zip(rows,x['cdx']['capture_records']):
   if any(actual[k]!=declared[k] for k in fields):errors.append('CDX raw mismatch '+x['target'])
 if not x.get('entity_valid'):
  summaries.append({'target':x['target'],'classification':'transport_unknown_no_source_HTTP','prior_result':x['category'],'payload_accepted':False});continue
 c=x['selected_capture'];v=x['validation'];body=(D/v['raw_body_path']).read_bytes();status,h=source_header(D/v['raw_headers_path']);text=body.decode('utf-8');m=datetime.datetime.strptime(h['memento-datetime'],'%a, %d %b %Y %H:%M:%S GMT').replace(tzinfo=datetime.timezone.utc);actual=m.strftime('%Y%m%d%H%M%S');digest=base64.b32encode(hashlib.sha1(body).digest()).decode()
 eligible=[y for y in x['cdx']['capture_records'] if y['statuscode']=='200' and y['mimetype'] in ['text/html','application/xhtml+xml'] and '20040101'<=y['timestamp']<='20080512210044' and norm(y['original'])==norm(x['query_original'])]
 if not eligible or c['timestamp']!=max(y['timestamp'] for y in eligible) or norm(c['original'])!=norm(x['query_original']):errors.append('selection '+x['target'])
 if status!=200 or h['content-type'].split(';')[0]!='text/html' or actual!=c['timestamp'] or actual>'20080512210044' or digest!=c['digest'] or len(body)!=x['body_bytes'] or hashlib.sha256(body).hexdigest()!=x['body_sha256']:errors.append('payload '+x['target'])
 title=html.unescape(re.search(r'<title[^>]*>(.*?)</title>',text,re.I|re.S)[1]).strip();posts=re.findall(r'class=[\"\']posted-date[\"\'][^>]*>(.*?)</span>',text,re.I|re.S);entries=re.findall(r'class=[\"\']news-entry-date[\"\'][^>]*>(.*?)</li>',text,re.I|re.S)
 def dates(nodes):return [re.search(r'(?<!\d)(\d{1,2})-(\d{1,2})-(\d{2})(?!\d)',html.unescape(re.sub(r'<[^>]+>','',s))).group() for s in nodes]
 posted=dates(posts);entry=dates(entries);month,year=re.search(r'rss-(\d\d)-(\d{4})',x['target']).groups();expected_title=datetime.date(int(year),int(month),1).strftime('%B, %Y')
 if len(posted)!=counts[x['target']] or posted!=entry or any(int(z.split('-')[0])!=int(month) or int(z.split('-')[2])!=int(year)%100 for z in posted) or expected_title not in title or '<html' not in text.lower() or '<rss' in text.lower():errors.append('article identity '+x['target'])
 row={'target':x['target'],'query_original_url':x['query_original'],'captured_original_url':c['original'],'local_path':(D/v['raw_body_path']).as_posix(),'headers_local_path':(D/v['raw_headers_path']).as_posix(),'actual_timestamp':actual,'actual_memento':m.isoformat(),'body_bytes':len(body),'body_sha256':hashlib.sha256(body).hexdigest(),'cdx_digest':c['digest'],'mime':h['content-type'],'body_format':'expanded_html','title':title,'article_posted_date_count':len(posted),'article_posted_dates':dict(collections.Counter(posted)),'article_month_matches_url':True,'source_title_anomaly':None,'logical_url':x['query_original'],'proposed_route':x['target'],'role':'archived_news_html','source_group':'rss_path_expanded_html','source_event_dates_are_not_article_dates':True}
 selected.append(row);summaries.append({k:row[k] for k in ['target','body_bytes','body_sha256','actual_timestamp','title','article_posted_date_count']})
ordered=[attempts[k] for k in sorted(attempts)];sourcecount=0;bodytotal=0;maxfail=runfail=0
for a in ordered:
 status,h=source_header(D/a['raw']['headers']);body=(D/a['raw']['body']).read_bytes();bodytotal+=len(body);sourcecount+=status is not None
 if status!=a['source_status'] or len(body)!=a['body_bytes'] or (status and hashlib.sha256(body).hexdigest()!=a['body_sha256']):errors.append('attempt source/body '+str(a['attempt']))
 if status in [429,503] or a.get('automatic_redirects') or a.get('redirects_requested'):errors.append('rate/redirect '+str(a['attempt']))
 runfail=runfail+1 if status is None else 0;maxfail=max(maxfail,runfail)
 if runfail>=5 and a!=ordered[-1]:errors.append('continued after5fail')
 trace=(D/a['raw']['trace']).read_text(encoding='utf-8',errors='replace');clock=re.search(r'(?m)^(\d\d):(\d\d):(\d\d\.\d+)',trace)
 if clock:traceclocks[a['attempt']]=int(clock[1])*3600+int(clock[2])*60+float(clock[3])
 disp=j['dispatches'][a['attempt']-1]
 if disp['dispatch_monotonic']!=a['dispatch_monotonic'] or not disp['persisted_before_transport'] or dt(disp['dispatch_utc'])>dt(a['started_utc']):errors.append('journal '+str(a['attempt']))
monos=[b['dispatch_monotonic']-a['dispatch_monotonic'] for a,b in zip(ordered,ordered[1:])];utcs=[(dt(b['started_utc'])-dt(a['started_utc'])).total_seconds() for a,b in zip(ordered,ordered[1:])];traces=[traceclocks[b['attempt']]-traceclocks[a['attempt']] for a,b in zip(ordered,ordered[1:]) if a['attempt'] in traceclocks and b['attempt'] in traceclocks]
if min(monos)<5.1 or min(utcs)<5.0 or min(traces)<5.0:errors.append('cadence')
if len(ordered)!=6 or sourcecount!=4 or bodytotal!=326250 or len(selected)!=2 or allcdx!=r['capture_index_count'] or sum(x['body_bytes'] for x in selected)!=316313:errors.append('aggregate')
if len(ordered)>12 or (dt(r['finished_utc'])-dt(r['started_utc'])).total_seconds()>240 or dt(r['finished_utc'])>=dt('2026-10-15T14:05:00Z') or bodytotal>33554432 or max(a['body_bytes'] for a in ordered)>16777216:errors.append('caps')
if any(j[k]['disk_free_bytes']<11005853696 for k in ['disk_preflight','disk_postflight']) or not j['postflight_persisted_in_finally']:errors.append('disk')
accepted=not errors
out={'schema':'continuous-wow-rss21-independent-acceptance/v1','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'accepted':accepted,'network_requests_by_review':0,'report':meta(D/'batch-report.json'),'journal':meta(D/'dispatch-log.json'),'driver':meta(D/'rss21_driver.py'),'source_identity':'Exact scheme/host/path/query; default ports only normalize. All raw CDX rows read; selected latest eligible pre-anchor exact-origin capture; actual Memento checked from raw source headers independently. CDX length is WARC index length, not body bytes.','attempts':len(ordered),'source_HTTP_excluding_CONNECT':sourcecount,'CDX_rows':allcdx,'new_valid_expanded_HTML':len(selected),'new_raw_RSS_XML':0,'payload_bytes':sum(x['body_bytes'] for x in selected),'total_body_bytes':bodytotal,'entities':summaries,'minimum_monotonic_dispatch_seconds':min(monos),'minimum_actual_UTC_request_start_seconds':min(utcs),'minimum_trace_first_clock_seconds':min(traces),'max_consecutive_transport_failures':maxfail,'disk_free_before':j['disk_preflight']['disk_free_bytes'],'disk_free_after':j['disk_postflight']['disk_free_bytes'],'stop_reason':r['stop_reason'],'cadence_inference':'Lower cadence batch acquired2 pages with2 isolated transport failures. This is observed reliability evidence under this batch; causal root cause remains unproven.','integration':'Separate from frozen accepted v13. Root must explicitly approve any final source14 build.','errors':errors}
(P/'rss21-acceptance.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
sel={'schema':'continuous-wow-selected-rss21-expanded-html/v1','entry_count':len(selected),'entries':selected,'acceptance':(P/'rss21-acceptance.json').as_posix(),'accepted':accepted,'integration_held':True}
(P/'selected-rss21-source-map.json').write_text(json.dumps(sel,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':accepted,'acceptance':meta(P/'rss21-acceptance.json'),'selected_map':meta(P/'selected-rss21-source-map.json'),'errors':errors}))
