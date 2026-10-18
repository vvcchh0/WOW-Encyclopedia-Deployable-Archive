"""Select actual unresolved image destinations, retaining all duplicate link sources."""
import hashlib
import html
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qs, quote, urlsplit

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
audit = PUB/'image-navigation-audit-v30.json'
assert sha(audit) == '31f5b0d00e4074beca5184c930fd762849a29be389dbcccaeefd60ecd664eed2'
provenance = ROOT/'.scratch/pages-resources-20261018-v30/export-provenance.json'
assert sha(provenance) == 'b04eb866bd7d21aa23ce8ad064eeb55b8b263e84147bb3755f4af7df84825d85'
records = {x['output_path']: x for x in read(provenance)['files']}
rows = read(audit)['candidates']
assert len(rows) == 73
groups = defaultdict(list)
for row in rows:
    url = urlsplit(row['original'])
    assert url.hostname in {'www.worldofwarcraft.com','worldofwarcraft.com','www.blizzard.com'}
    assert not url.query and not url.fragment and url.path.lower().endswith(('.jpg','.jpeg','.png','.gif'))
    assert row['recent_execution_record_count'] == 0
    for ref in row['references']:
        page = (ROOT/ref['output_file']).resolve()
        relative = page.relative_to(ROOT/'.scratch/pages-resources-20261018-v30').as_posix()
        assert sha(page) == ref['source_page_sha256'] == records[relative]['derived_sha256']
        line = html.unescape(page.read_text(encoding='utf-8').splitlines()[ref['line']-1])
        requested = [parse_qs(match.group(1), keep_blank_values=True).get('requested',[''])[0]
                     for match in re.finditer(r'missing\.html\?([^\"\'<>\s]*)',line)]
        assert row['original'] in requested, (row['original'], ref)
    host = 'www.worldofwarcraft.com' if url.hostname in {'www.worldofwarcraft.com','worldofwarcraft.com'} else url.hostname
    groups[(host,url.path)].append(row)
assert len(groups) == 70
needles = ROOT/'.scratch/navigation73-report-needles.txt'
needles.write_text('\n'.join(needle for row in rows for needle in (row['original'], quote(row['original'],safe='')))+'\n',encoding='utf-8')
command=['rg','--files-with-matches','--no-ignore','--fixed-strings','--file',str(needles),'research',
         '--glob','*batch-report*.json','--glob','*source-map*.json','--glob','*sanitized-summary.json','--glob','*request-record*.json']
search=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=60)
assert search.returncode == 1 and not search.stdout.strip() and not search.stderr.strip(), (search.returncode,search.stdout,search.stderr)

def priority(row):
    p=urlsplit(row['original']).path
    if '/news/images/07-' in p:
        return (0 if '/07-08/' in p else 1,p)
    if '/pvp/' in p or '/info/basics/' in p:
        return (2,p)
    if '/news/' in p:
        return (3,p)
    if '/wallpaper' in p or '/wallpaper' in row['original']:
        return (5,p)
    return (4,p)

selected=[]
for group in groups.values():
    group.sort(key=lambda row:(urlsplit(row['original']).hostname!='www.worldofwarcraft.com',urlsplit(row['original']).scheme!='http'))
    chosen=group[0]
    selected.append({'original':chosen['original'],'references':chosen['references'],
        'alternate_navigation_links':[{'original':x['original'],'references':x['references']} for x in group[1:]],
        'source_role':'literal_missing_html_image_destination','recent_execution_record_count':0})
selected.sort(key=priority)
for n,row in enumerate(selected,1):
    row['rank']=n
dest=PUB/'navigation-link-selected70.json'
assert not dest.exists()
dest.write_text(json.dumps({'accepted':True,'network_requests':0,'target_count':70,'input_navigation_urls':73,
    'source_audit':{'path':audit.relative_to(ROOT).as_posix(),'sha256':sha(audit)},
    'source_provenance':{'path':provenance.relative_to(ROOT).as_posix(),'sha256':sha(provenance)},
    'structured_report_search':{'exit_code':search.returncode,'matching_files':[], 'needle_sha256':sha(needles),
        'scope':'All research JSON batch reports, source maps, sanitized summaries and request records, using literal and percent-encoded URL needles. Other report formats and escaping conventions are outside this search.'},
    'duplicate_rule':'One output path per official origin/path; retain three alternate http/https or www navigation-link citations. No image is presumed identical across unrelated origins.',
    'scope':'Actual full-image, news-photo and wallpaper destinations already linked by archived pages. No paths inferred from thumbnail names. Download and navigation compatibility repair need separate review.',
    'rows':selected},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sha256':sha(dest),'targets':70,'first10':[x['original'] for x in selected[:10]]}))
