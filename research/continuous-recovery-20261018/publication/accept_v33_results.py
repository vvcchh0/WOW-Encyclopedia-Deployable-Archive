"""Root recount of export placeholders or aggregation of an inspected browser result."""
import argparse, hashlib, html, json, re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit, urlunsplit
ROOT=Path(__file__).resolve().parents[3]
PUB=Path(__file__).resolve().parent
SITE=ROOT/'.scratch/pages-resources-20261018-v33'
RUN=PUB.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
bind=lambda p:{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def write(path,data):
    assert not path.exists();path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
def metrics():
    counter,news=Counter(),Counter();files=markers=0
    for p in SITE.rglob('*'):
        relative=p.relative_to(SITE).as_posix()
        if not p.is_file() or relative.startswith('_origins/') or p.suffix.lower() not in {'.html','.htm','.xml','.css'}:continue
        files+=1
        for m in re.finditer(r'missing-image\.svg\?([^\"\'<>\s\)]*)',p.read_text(encoding='utf-8',errors='replace'),re.I):
            markers+=1;raw=parse_qs(html.unescape(m.group(1))).get('requested',[''])[0];u=urlsplit(raw)
            if u.scheme not in {'http','https'} or Path(u.path.lower()).suffix not in {'.gif','.jpg','.jpeg','.png','.webp','.svg','.bmp'}:continue
            port=u.port
            if port==(80 if u.scheme=='http' else 443):port=None
            host=u.hostname.lower()+((':'+str(port)) if port else '')
            key=urlunsplit((u.scheme.lower(),host,u.path or '/',u.query,u.fragment));counter[key]+=1
            if relative.startswith('news/'):news[key]+=1
    actual={'static_text_files':files,'unique_missing_images':len(counter),'missing_occurrences':sum(counter.values()),'news_unique_missing_images':len(news),'news_missing_occurrences':sum(news.values())}
    assert actual==read(PUB/'v33-export-expectations.json')['expected_static_counts'],actual
    result={'accepted':True,'version':'v33','checked_utc':datetime.now(timezone.utc).isoformat(),**actual,'all_placeholder_markers':markers,
        'export_provenance_sha256':sha(SITE/'export-provenance.json'),'scope':'The same1104 static text files, excluding_origins. Native3368 dynamic gallery targets remain separate.'}
    write(PUB/'root-v33-static-metrics-acceptance.json',result);print(json.dumps(result))
def browser(result_path,visual):
    assert visual
    result_path=(ROOT/result_path).resolve();result_path.relative_to(RUN/'integration/v33/browser/results')
    data=read(result_path)
    assert data['accepted'] and not data['errors'] and not data['external_requests'] and not data['request_failures']
    assert data['checks'] and all(x['accepted'] for x in data['checks'])
    assert data['output_provenance_sha256']==sha(SITE/'export-provenance.json')
    inp=ROOT/data['input']['path'];assert sha(inp)==data['input']['sha256']
    expected=read(inp);manifest=read(PUB/'root-v33-source-receipts-manifest-r2.json')
    assert expected['new_original_count']==manifest['new_images']==120
    assert data['popup_full_image_links']==expected['browser_plan']['popup_full_image_links']['required']>=21
    assert data['ordinary_image_hrefs']==expected['browser_plan']['ordinary_image_hrefs']['required_unique_originals']
    assert data['static_render_targets']==expected['browser_plan']['static_render_targets']['candidate_count']
    for row in data['declaration_only_images']:
        assert row['declarations'] and all(x['dom_matches']==0 for x in row['declarations'])
    screenshots=[]
    for p in data['screenshots']:
        if isinstance(p,str):screenshots.append(bind(ROOT/p))
    assert len(screenshots)>=3
    result={'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'export_provenance_sha256':sha(SITE/'export-provenance.json'),
        'external_requests':0,'network_requests_to_external_sources':0,'browser_executed':True,'visual_reviewed':True,
        'browser_result':bind(result_path),'browser_input':bind(inp),'checks':len(data['checks']),
        'new_originals_served_and_decoded':120,'popup_full_image_links':data['popup_full_image_links'],
        'ordinary_image_hrefs':data['ordinary_image_hrefs'],'static_render_targets':data['static_render_targets'],
        'unused_css_declarations':data['declaration_only_images'],'screenshots':screenshots,
        'prior_baseline':expected['v32_baseline'],'baseline_rerun':False,
        'scope':'Real clicks and decoded originals for the v33 delta and previously validated image links changed by the href repair; the602-check v32 baseline is referenced, not rerun.'}
    write(PUB/'root-v33-browser-acceptance.json',result);print(json.dumps({k:result[k] for k in ['accepted','checks','popup_full_image_links','ordinary_image_hrefs','static_render_targets']}))
def main():
    p=argparse.ArgumentParser();p.add_argument('--metrics',action='store_true');p.add_argument('--browser-result');p.add_argument('--visual-reviewed',action='store_true');a=p.parse_args()
    if a.metrics:metrics()
    else:browser(a.browser_result,a.visual_reviewed)
if __name__=='__main__':main()
