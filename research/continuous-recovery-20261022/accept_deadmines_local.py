"""Verify existing Deadmines bytes across original, Source16 and v52 layers."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))

def main():
    manifest_path=ROOT/'.scratch/offline-non-gallery-20261021-v16/build-manifest.json'
    assert sha(manifest_path)=='e81eaefffbe994178e46fe02e2afd761d0747b1dad36455c1b4b1d2bfeec7b9a'
    manifest=read(manifest_path); records={r['route']:r for r in manifest['files']}
    browser_path=HERE/'dungeons-v52-browser-inspection.json'; browser=read(browser_path)
    assert not any(browser[k] for k in ('external_requests','page_errors','http_errors'))
    assert len(browser['images'])==10 and len(browser['originals'])==9
    prefix='/WOW-Encyclopedia-Deployable-Archive'
    requests=[(x['src'][len(prefix):],'preview') for x in browser['images']]
    requests += [(x['href'][len(prefix):],'original') for x in browser['originals']]
    items=[]
    for route,role in requests:
        record=records[route]; assert record['kind']=='image' and not record['transformed']
        paths=[ROOT/'offline/site'/route.lstrip('/'),ROOT/record['output_path'],
               ROOT/'.scratch/pages-resources-20261021-v52'/route.lstrip('/'), ROOT/record['source_local_path']]
        assert all(p.is_file() and sha(p)==record['source_sha256'] and p.stat().st_size==record['source_length'] for p in paths),route
        with Image.open(paths[0]) as im:
            assert im.format=='JPEG'
            for frame in range(getattr(im,'n_frames',1)): im.seek(frame); im.load()
            width,height=im.size; frames=getattr(im,'n_frames',1)
        items.append({'route':route,'role':role,'source_url':record['source_base_url'],
          'actual_capture_timestamp':record['actual_timestamp'],'sha256':record['source_sha256'],
          'bytes':record['source_length'],'width':width,'height':height,'frames':frames,
          'explicit_supplement':record.get('supplement',False),
          'layers_compared':['preserved_entity','original_site','source16','v52']})
    originals=[x for x in items if x['role']=='original']
    assert all(x['actual_capture_timestamp'].startswith('20080402') for x in originals)
    pairs=[(268,'ss0001.jpg','Moonbrook'),(274,'ss0005.jpg','dwarves entering the mine'),
      (275,'ss0007.jpg','Blood Ring trade'),(269,'ss0008.jpg','mine instance entrance'),
      (270,'ss0010.jpg','ogre and locked door'),(276,'ss0009.jpg','dwarven group portrait'),
      (271,'ss0012.jpg','goblin workshop'),(272,'ss0013.jpg','foundry'),(273,'ss0014.jpg','wizard and cannon')]
    result={'schema':'wow-root-deadmines-local-acceptance/v1','accepted':True,
      'checked_utc':datetime.now(timezone.utc).isoformat(),'originals':9,'previews':10,
      'new_images_recovered':0,'browser_inspection_sha256':sha(browser_path),
      'source_manifest_sha256':sha(manifest_path),'images':items,
      'visual_review':{'method':'Parent viewed every original image using view_image and checked the associated scenes against the preserved article captions.',
        'archivecraft_associations':[{'attachment_number':i,'local_filename':n,'scene':s,'basis':'caption and subject association; remote image bytes not downloaded'} for i,n,s in pairs]},
      'conclusion':'The nine early Deadmines images and all article previews already work in accepted local v52. No re-download or synthetic substitute is needed. Current hosted-byte checks are separate.',
      'date_boundary':'Capture times identify archive responses, not image creation dates or a precise Alpha/Beta build.'}
    (HERE/'root-deadmines-local-acceptance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'accepted':True,'originals':9,'previews':10,'layers':4,'new_images_recovered':0}))

if __name__=='__main__':main()
