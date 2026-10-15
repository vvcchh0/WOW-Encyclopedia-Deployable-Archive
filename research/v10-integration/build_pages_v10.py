"""Export the fresh v10 mirror using the accepted, unchanged image overlays."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import export_github_pages

def main():
    source=ROOT/'.scratch/offline-navigation-20261015-v10'
    output=ROOT/'.scratch/pages-resources-20261015-v10'
    implementation={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['tools/export_github_pages.py','tools/historical_exhibits.py']}
    primary=[ROOT/'research/resource-resume-20261013/round002/entity-source-map.json',ROOT/'research/resource-resume-20261013/round003/entity-source-map.json']
    supplements=[ROOT/'research/related-sites-20261014/integration/regional-image-source-map.json',ROOT/'research/related-sites-20261014/integration/karazhan-late-source-map.json',ROOT/'research/media-screenshots-20261015/late-image-source-map.json']
    result=export_github_pages.export_pages(source_site=source/'site',manifest_path=source/'build-manifest.json',output=output,image_source_maps=primary,supplement_image_source_maps=supplements,allow_later_image_supplements=True)
    receipt={'checked_utc':datetime.now(timezone.utc).isoformat(),'build':result,
        'source_stage':source.relative_to(ROOT).as_posix(),
        'primary_source_maps':[x.relative_to(ROOT).as_posix() for x in primary],
        'supplement_source_maps':[x.relative_to(ROOT).as_posix() for x in supplements],
        'allow_later_image_supplements':True,'published':False,
        'implementation_sha256':implementation,
        'implementation_unchanged_during_export':all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest for name,digest in implementation.items())}
    (ROOT/'research/v10-integration/root-build-v10.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))
if __name__=='__main__':
    main()
