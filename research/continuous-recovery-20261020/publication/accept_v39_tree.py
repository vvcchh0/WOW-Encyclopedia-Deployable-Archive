"""Verify the v39 output tree and isolate its delta from frozen v38."""
import hashlib
import json
import os
import re
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PUB = Path(__file__).resolve().parent
SITE = ROOT / '.scratch/pages-resources-20261020-v39'
OLD = ROOT / '.scratch/pages-resources-20261019-v38'
SHA = lambda data: hashlib.sha256(data).hexdigest()
READ = lambda path: json.loads(path.read_bytes())

def files_in(root):
    found = set()
    def visit(directory, prefix=''):
        for entry in os.scandir(directory):
            assert not entry.is_symlink(), entry.path
            relative = prefix + entry.name
            if entry.is_dir(follow_symlinks=False):
                visit(entry.path, relative + '/')
            elif entry.is_file(follow_symlinks=False):
                found.add(relative)
    visit(root)
    return found

def main():
    start = time.monotonic()
    out = PUB / 'root-v39-export-acceptance.json'
    assert not out.exists()
    before = shutil.disk_usage(ROOT).free
    assert before >= 11005853696
    gate_path = PUB / 'root-v39-export-go.json'
    gate = READ(gate_path)
    build_path = ROOT / 'research/continuous-recovery-20261020/integration/v39/v39-build-receipt.json'
    build = READ(build_path)
    assert build['export_completed'] and build['returncode'] == 0 and not build['timed_out']
    assert build['root_gate_sha256'] == SHA(gate_path.read_bytes())
    provenance_path = SITE / 'export-provenance.json'
    provenance_sha = SHA(provenance_path.read_bytes())
    assert provenance_sha == build['export_provenance_sha256']
    provenance = READ(provenance_path)
    files = {r['output_path']: r for r in provenance['files']}
    assert len(files) == len(provenance['files'])
    actual = files_in(SITE)
    assert actual == set(files) | {'export-provenance.json'}
    def check(pair):
        relative, row = pair
        assert relative and '..' not in relative.split('/') and '\\' not in relative and not relative.startswith('/')
        data = (SITE / relative).read_bytes()
        assert len(data) == row['derived_length'] and SHA(data) == row['derived_sha256'], relative
        return len(data)
    with ThreadPoolExecutor(max_workers=8) as pool:
        checked = sum(pool.map(check, files.items()))
    assert SHA((OLD / 'export-provenance.json').read_bytes()) == 'de6ee4348a688cf648a86bf2537fb7f8f60490721419e7f45aea6e881b590828'
    old = {r['output_path']: r for r in READ(OLD / 'export-provenance.json')['files']}
    assert not set(old) - set(files), 'lost an existing v38 object'
    expected_new = {'news/images/04-12/ordernow.jpg', 'news/images/05-10/trolldire.jpg'}
    added = set(files) - set(old)
    assert added == expected_new, sorted(added)
    changed = sorted(p for p in old if (old[p]['derived_sha256'],old[p]['derived_length']) != (files[p]['derived_sha256'],files[p]['derived_length']))
    allowed = {'__offline/pages_runtime.js', '__offline/route-map.json', 'news/wow-news2004.html', 'news/wow-news-10-2005.html', 'README.md'}
    assert set(changed) <= allowed and {'news/wow-news2004.html','news/wow-news-10-2005.html'} <= set(changed), changed
    old_news = (OLD / 'news/wow-news2004.html').read_text(encoding='utf-8')
    new_news = (SITE / 'news/wow-news2004.html').read_text(encoding='utf-8')
    def sale_body_span(text):
        heading = text.index('World of Warcraft Now On Sale from the Blizzard Store')
        start = text.index('<div class="postBody">', heading)
        end = text.index('</div>', start) + len('</div>')
        return start, end
    osale, oesale = sale_body_span(old_news)
    nsale, nesale = sale_body_span(new_news)
    assert old_news[:osale] == new_news[:nsale] and old_news[oesale:] == new_news[nesale:], 'changed sibling news content'
    old_trailer = (OLD / 'news/wow-news-10-2005.html').read_text(encoding='utf-8')
    new_trailer = (SITE / 'news/wow-news-10-2005.html').read_text(encoding='utf-8')
    old_srcs = re.findall(r'<img\b[^>]*\bsrc="([^"]*trolldire\.jpg[^"]*)"', old_trailer, re.I)
    assert len(old_srcs) == 1
    assert old_trailer.replace(old_srcs[0], '/WOW-Encyclopedia-Deployable-Archive/news/images/05-10/trolldire.jpg', 1) == new_trailer, 'unexpected trailer-news delta'
    reuse = READ(PUB / 'root-digest-reuse-source-acceptance.json')
    for target in reuse['routes']:
        key = target['target_route'].lstrip('/')
        record = files[key]
        assert record['recovery_method'] == 'payload_digest_reuse'
        assert record['actual_capture_timestamp'] is None
        assert record['indexed_capture_timestamp'] == target['target_indexed_capture_timestamp']
        assert record['cdx_digest'] == target['target_cdx_digest']
        assert record['source_sha256'] == record['derived_sha256'] == target['payload_source']['sha256']
        for field in ['original_url','actual_capture_timestamp','sha256','length']:
            assert record['payload_source'][field] == target['payload_source'][field]
    stats = provenance['stats']
    assert stats['image_overlay_records'] == 657 and stats['primary_image_overlay_records'] == 557 and stats['supplement_image_overlay_records'] == 100
    assert stats['guide_image_collection_images'] == 39 and stats['guide_preview_count'] == 22
    assert len(files) == 9115 and len(actual) == 9116
    after = shutil.disk_usage(ROOT).free
    assert after >= 11005853696
    receipt = {'accepted':True, 'checked_utc':datetime.now(timezone.utc).isoformat(), 'site':SITE.relative_to(ROOT).as_posix(),
        'elapsed_seconds':time.monotonic()-start, 'declared_files':len(files), 'actual_files':len(actual),
        'tree_bytes':checked+provenance_path.stat().st_size, 'export_provenance_sha256':provenance_sha,
        'image_overlays':657, 'new_image_bindings_since_v38':2, 'new_downloaded_images':0,
        'added_paths_compared_v38':sorted(added), 'changed_paths_compared_v38':changed,
        'unchanged_previous_objects':len(old)-len(changed), 'guide_collection_images':39,'guide_preview_images':22,
        'network_requests':0,'published':False,'browser_accepted':False,
        'disk_free_before_bytes':before,'disk_free_after_bytes':after,
        'bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':SHA(p.read_bytes())} for p in [gate_path,build_path,PUB/'root-digest-reuse-source-acceptance.json']],
        'scope':'Every declared v39 object checked from actual bytes. All prior v38 objects retained; unchanged objects match frozen v38 hashes. Two reused JPEG URL bindings retain separate target-index and payload-source dates.'}
    out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))

if __name__ == '__main__':
    main()
