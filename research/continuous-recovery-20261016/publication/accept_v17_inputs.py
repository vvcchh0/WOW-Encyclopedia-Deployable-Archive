"""Root gate for preview code, accepted news copies and the combined loaders."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
INTEGRATION=ROOT/'research/continuous-recovery-20261016/integration'
sys.path.insert(0,str(ROOT/'tools'))
import export_github_pages as exporter
import guide_previews

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    verification=json.loads((INTEGRATION/'guide-previews-verification.json').read_bytes())
    for path, expected in verification['implementation_sha256'].items():
        assert sha(ROOT/path)==expected,path
    for path, expected in verification['unchanged_adjacent_tools_sha256'].items():
        assert sha(ROOT/path)==expected,path
    source=ROOT/'.scratch/offline-navigation-20261015-v15'
    manifest_path=source/'build-manifest.json'
    assert sha(manifest_path)=='d89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002'
    manifest=json.loads(manifest_path.read_bytes())
    records=manifest['files']
    routes={x['route'] for x in records}|set(manifest.get('route_aliases',{}))
    static={x['route']:exporter.static_url(exporter.DEFAULT_BASE_PATH,exporter.static_rel_for_route(x['route'],x)) for x in records}
    bundle=guide_previews.load_guide_preview_map(INTEGRATION/'guide-previews-source-map.json',
        workspace_root=ROOT,source_site=source/'site',manifest_path=manifest_path,manifest=manifest,route_to_static=static)
    assert len(bundle.groups)==5 and bundle.preview_count==19
    for group in bundle.groups:
        section=guide_previews.render_gallery_section(group)
        assert section.count('<img ')==len(group.previews) and 'Full-size gallery images are still incomplete.' in section
        assert '<script' not in section and group.guide_static_url in section
        for preview in group.previews:
            assert preview.static_url in section
    news=json.loads((INTEGRATION/'v17-primary-news-image-source-map.json').read_bytes())
    accepted={}
    acceptance_paths=['root-news03-acceptance.json','root-news04-acceptance.json','root-allnews01-acceptance.json']
    for name in acceptance_paths:
        evidence=json.loads((OUT/name).read_bytes())
        assert evidence['accepted']
        for image in evidence['accepted_images']:
            assert image['original'] not in accepted
            accepted[image['original']]=image
    assert len(accepted)==len(news['items'])==20
    for image in news['items']:
        expected=accepted[image['logical_url']]
        data=(ROOT/image['local_path']).read_bytes()
        assert data==(ROOT/expected['raw_body_path']).read_bytes()
        assert len(data)==image['length']==expected['length']
        assert hashlib.sha256(data).hexdigest()==image['sha256']==expected['sha256']
        assert image['actual_timestamp']==expected['actual_timestamp']
    primary=[ROOT/'research/resource-resume-20261013/round002/entity-source-map.json',
        ROOT/'research/resource-resume-20261013/round003/entity-source-map.json',
        INTEGRATION/'v16-primary-news-image-source-map.json',INTEGRATION/'v17-primary-news-image-source-map.json']
    supplements=[ROOT/'research/related-sites-20261014/integration/regional-image-source-map.json',
        ROOT/'research/related-sites-20261014/integration/karazhan-late-source-map.json',
        ROOT/'research/media-screenshots-20261015/late-image-source-map.json',INTEGRATION/'v16-eu-image-source-map.json']
    loaded,primary_bytes=exporter.load_image_overlays(primary,workspace_root=ROOT,anchor_timestamp=manifest['anchor_timestamp'],
        frozen_routes=routes,frozen_static_paths={exporter.static_rel_for_route(x['route'],x) for x in records})
    retained, supplement_bytes=exporter.load_supplement_image_overlays(supplements,workspace_root=ROOT,
        anchor_timestamp=manifest['anchor_timestamp'],frozen_routes=routes|{x['route'] for x in loaded},
        frozen_static_paths={exporter.static_rel_for_route(x['route'],x) for x in records}|{x['relative'] for x in loaded},allow_later_image_supplements=True)
    assert len(loaded)==48 and len(retained)==21
    old=json.loads((ROOT/'.scratch/pages-resources-20261016-v16/export-provenance.json').read_bytes())
    old_overlays={x['route'] for x in old['files'] if x.get('kind')=='image_overlay'}
    assert len(old_overlays)==49
    assert old_overlays <= {x['route'] for x in loaded+retained}
    result={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'export_started':False,
        'production_sha256':{p:sha(ROOT/p) for p in verification['implementation_sha256']},
        'worker_test_receipt_sha256':sha(INTEGRATION/'guide-previews-verification.json'),
        'worker_tests_reported':{'focused':6,'existing_export_image':42},
        'root_actual_checks':'Real frozen-source preview loader/render, all20 news copy/raw byte equality, combined primary/supplement loaders and retained49 routes.',
        'guide_preview_count':19,'guide_gallery_pages':5,'new_news_images':20,'new_news_bytes':sum(x['length'] for x in news['items']),
        'primary_overlays':48,'supplement_overlays':21,'total_overlays':69,
        'source_records':len(records),'source_manifest_sha256':sha(manifest_path),
        'map_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in primary+supplements+[INTEGRATION/'guide-previews-source-map.json']}}
    (OUT/'root-v17-input-acceptance.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['accepted','guide_preview_count','new_news_images','total_overlays']}))

if __name__=='__main__': main()
