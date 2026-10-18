"""Root input acceptance: actual loaders, public sources and frozen-site impact."""
import hashlib, html, importlib.util, json, re, shutil, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, quote, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'research/continuous-recovery-20261018'
PUB = RUN / 'publication'
I = RUN / 'integration/v33'
OLD = ROOT / '.scratch/pages-resources-20261018-v32'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
def load(name, p):
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m)
    return m
def key(raw):
    u = urlsplit(raw)
    if not u.hostname: return raw
    port = u.port
    if port == (80 if u.scheme == 'http' else 443): port = None
    host = u.hostname.lower() + ((':'+str(port)) if port else '')
    return urlunsplit((u.scheme.lower(), host, u.path or '/', u.query, u.fragment))
def write(path, data):
    assert not path.exists()
    path.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8', newline='\n')

def main():
    assert shutil.disk_usage(ROOT).free >= 11005853696
    b = load('root_v33_input_builder', I / 'build_pages_v33.py')
    runner = load('root_v33_input_runner', I / 'execute_v33.py')
    assert sha(I / 'build_pages_v33.py') == '444aa2ec0a8aee5c712ac0bbef59c9bde2bc6e6cb292e1213b113c7018d86304'
    assert sha(I / 'execute_v33.py') == '0011614bda8c9540e1266042630d12b4e3fe060582366d2db3edfd62a13179b0'
    source = read(PUB / 'root-v33-source-receipts-manifest-r2.json')
    assert source['accepted']
    expected = {}
    for batch in source['batches']:
        for binding in [batch['source_acceptance'], batch['public_copy_acceptance'], batch['visual_acceptance']]:
            assert sha(ROOT / binding['path']) == binding['sha256']
        for row in read(ROOT / batch['public_copy_acceptance']['path'])['accepted_images']:
            assert row['original'] not in expected
            expected[row['original']] = row
    new_items = read(I / 'v33-primary-source-map.json')['items'] + read(I / 'v33-supplement-source-map.json')['items']
    assert {x['original'] for x in new_items} == set(expected) and len(new_items) == source['new_images']
    for x in new_items:
        e = expected[x['original']]
        assert all(x[k] == e[k] for k in ['original','mime','dimensions','decoded_frames','length','sha256','cdx_digest','local_path'])
        assert x['actual_timestamp'] == x['indexed_capture_timestamp'] == e['actual_capture_timestamp']
        assert sha(ROOT / x['local_path']) == x['sha256']
    frozen, primary_maps, supplement_maps, pins = b.frozen_maps()
    e = b.import_exporter()
    manifest = read(b.SOURCE_MANIFEST)
    records = manifest['files']
    routes = {e.safe_route(str(x['route'])) for x in records} | set(manifest.get('route_aliases', {}))
    static = {e.static_rel_for_route(str(x['route']), x) for x in records}
    primary, _ = e.load_image_overlays(primary_maps + (I/'v33-primary-source-map.json',), workspace_root=ROOT,
        anchor_timestamp=manifest['anchor_timestamp'], frozen_routes=routes, frozen_static_paths=static)
    supplement, _ = e.load_supplement_image_overlays(supplement_maps + (I/'v33-supplement-source-map.json',), workspace_root=ROOT,
        anchor_timestamp=manifest['anchor_timestamp'], frozen_routes=routes | {x['route'] for x in primary},
        frozen_static_paths=static | {x['relative'] for x in primary}, allow_later_image_supplements=True)
    old_prov = read(OLD / 'export-provenance.json')
    assert sha(OLD / 'export-provenance.json') == 'a071d47b65232f723c2e74112adab521eb124d22b57aa430437646f06f50d356'
    old_files = {x['output_path']: x for x in old_prov['files']}
    old_overlays = {x['output_path']: x for x in old_prov['files'] if x.get('role') == 'image_overlay'}
    loaded = {x['relative']: x for x in primary+supplement}
    assert len(old_overlays) == 439 and set(old_overlays) <= set(loaded)
    for path, x in old_overlays.items():
        old = loaded[path]
        assert (old['source_sha256'],old['source_length'],old['original_url'],old['actual_timestamp'],old['mime']) == (x['derived_sha256'],x['derived_length'],x['original_url'],x['actual_capture_timestamp'],x['mime'])
    new_paths = {x['relative'] for x in primary+supplement} - set(old_overlays)
    assert len(new_paths) == len(new_items) and not new_paths & set(old_files)
    wanted = {key(x['original']): x for x in new_items}
    all_wanted = {key(x['original_url']): x for x in old_overlays.values()} | wanted
    allowed = {'__offline/route-map.json','__offline/pages_runtime.js','__offline/related-images/index.html'}
    before, removed, news, news_removed = Counter(), Counter(), Counter(), Counter()
    nav, text_files = [], 0
    for p in OLD.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in {'.html','.htm','.xml','.css'}: continue
        relative = p.relative_to(OLD).as_posix(); text = p.read_text(encoding='utf-8',errors='replace')
        if any(x['original'] in text or quote(x['original'],safe='') in text for x in new_items): allowed.add(relative)
        scoped = not relative.startswith('_origins/')
        if scoped: text_files += 1
        for marker in re.finditer(r'missing-image\.svg\?([^\"\'<>\s\)]*)',text,re.I):
            query = parse_qs(html.unescape(marker.group(1))); raw = query.get('requested',[''])[0]; u = urlsplit(raw)
            if u.scheme not in {'http','https'} or Path(u.path.lower()).suffix not in {'.gif','.jpg','.jpeg','.png','.webp','.svg','.bmp'}: continue
            k = key(raw)
            if scoped:
                before[k] += 1
                if relative.startswith('news/'): news[k] += 1
            if k in wanted:
                allowed.add(relative)
                if scoped:
                    removed[k] += 1
                    if relative.startswith('news/'): news_removed[k] += 1
        for marker in re.finditer(r'missing\.html\?([^\"\'<>\s\)]*)',text,re.I):
            query = parse_qs(html.unescape(marker.group(1)))
            raw = query.get('requested',[''])[0]
            if key(raw) in all_wanted and Path(urlsplit(raw).path.lower()).suffix in {'.gif','.jpg','.jpeg','.png'}:
                allowed.add(relative); nav.append({'page':relative,'original':raw,'new_overlay':key(raw) in wanted})
    metrics = read(PUB/'root-v32-static-metrics-acceptance.json')
    counts=(text_files,len(before),sum(before.values()),len(news),sum(news.values()))
    assert counts == (1104,930,1573,387,387), counts
    after, after_news = before-removed, news-news_removed
    stats = {'source_records':8357,'output_files':len(old_files)+len(new_paths),'image_overlay_records':len(loaded),
        'primary_image_overlay_records':len(primary),'supplement_image_overlay_records':len(supplement)}
    expectation = {'accepted':True,'network_requests':0,'export_executed':False,'new_output_paths':sorted(new_paths),
        'allowed_changed_output_paths':sorted(allowed),'stats':stats,'guide_collection_images':39,
        'navigation_href_recovery':nav,'removed_static_unique_addresses':len(removed),'removed_static_occurrences':sum(removed.values()),
        'expected_static_counts':{'static_text_files':text_files,'unique_missing_images':len(after),'missing_occurrences':sum(after.values()),
        'news_unique_missing_images':len(after_news),'news_missing_occurrences':sum(after_news.values())}}
    write(PUB/'v33-export-expectations.json',expectation)
    bindings = runner.required_bindings(b)
    gate = {'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),'network_requests':0,'export_executed':False,
        'preflight_sha256':sha(I/'v33-preflight.json'),
        **{k:source[k] for k in ['new_images','image_bytes','new_primary_images','new_supplement_images']},
        'map_bindings':[{'path':p,'sha256':s} for p,s in sorted(bindings.items())],
        'public_image_copies':[{'path':x['local_path'],'sha256':x['sha256'],'length':x['length']} for x in new_items],
        'actual_exporter_map_loaders_passed':True,'all_public_originals_rehashed':True,
        'expected_after_export':{'primary_overlays':len(primary),'supplement_overlays':len(supplement),'total_overlays':len(loaded),
        'declared_files':stats['output_files'],'actual_files':stats['output_files']+1},
        'export_expectations_sha256':sha(PUB/'v33-export-expectations.json')}
    write(PUB/'root-v33-input-acceptance.json',gate)
    print(json.dumps({'accepted':True,'new_images':len(new_items),'expected':gate['expected_after_export'],
        'navigation_href_references':len(nav),'static_counts':expectation['expected_static_counts'],'sha256':sha(PUB/'root-v33-input-acceptance.json')}))

if __name__ == '__main__': main()
