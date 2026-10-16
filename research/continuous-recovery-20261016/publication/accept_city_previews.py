"""Accept three existing guide previews, then bind the 22-preview union."""
import base64,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[3]
B=R/'research/continuous-recovery-20261016'
O=B/'publication'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())

def main():
    ap=B/'local-audit/nested-prefix01/nested-prefix01-audit-v1.json'
    audit=json.loads(ap.read_bytes())
    assert digest(ap)=='3b651a00c772e54d242124480b601a73e5144b48ed297fc9d951163887dcc989'
    items=[i for i in audit['items'] if i['gallery']=='City Attacks']
    assert len(items)==3
    checked=[]
    for i in items:
        payload=i['local_payload'];p=R/payload['path'];data=p.read_bytes();source=i['source_evidence']
        assert digest(p)==payload['sha256']==source['source_sha256']
        assert len(data)==payload['length']==source['source_length']
        assert (R/source['source_local_path']).read_bytes()==data
        assert source['actual_timestamp']<='20080512210044'
        assert source['source_base_url']=='http://www.worldofwarcraft.com'+i['route']
        d=base64.b32encode(hashlib.sha1(data).digest()).decode().rstrip('=')
        assert d==i['prefix_index']['rows'][0]['digest']
        parent=i['guide_evidence']['source_page'];page=R/parent['path']
        assert digest(page)==parent['sha256']
        assert parent['parent_a_literal'] in page.read_text(encoding='utf-8').splitlines()[parent['line']-1]
        assert parent['parent_href']=='/pvp/worldpvp/cityattacks-gallery.html'
        assert parent['gallery_link_fragment'] is None
        with Image.open(p) as im: im.load();assert list(im.size)==payload['dimensions']
        assert not i['already_in_v17_guide_preview']
        checked.append({'route':i['route'],'sha256':payload['sha256'],'length':len(data),
            'dimensions':payload['dimensions'],'capture_from_frozen_manifest':source['actual_timestamp'],
            'source_link':parent['parent_href'],'source_guide_route':'/info/basics/pvpcombat.html',
            'source_parent_line':parent['line'],'http_index_digest_match':True,'accepted':True})
    city={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'network_requests':0,
          'audit_sha256':digest(ap),'checked':checked,'errors':[],
          'scope':'Three existing City Attacks guide previews; group relationship only. No dynamic screenshot slot or full-image alias.',
          'visual_review':'Root viewed all three original JPEG files.'}
    save(O/'root-city-preview-acceptance.json',city)
    old=json.loads((O/'root-nested-preview-acceptance.json').read_bytes());assert old['accepted'] and len(old['checked'])==19
    oldmap=json.loads((B/'integration/guide-previews-source-map.json').read_bytes())
    merged_audit={'schema':'wow-recovery.guide-preview-union-audit.v1','counts':{'target_count':22,'groups':6,'new_city_previews':3,'previous_previews':19},
                  'items':[{'route':x['route'],'source_link':x.get('source_link'),'capture_from_frozen_manifest':x['capture_from_frozen_manifest']} for x in old['checked']+checked],
                  'inputs':[{'path':str((O/'root-nested-preview-acceptance.json').relative_to(R)).replace('\\','/'),'sha256':digest(O/'root-nested-preview-acceptance.json')},
                            oldmap['source_audit'],{'path':str(ap.relative_to(R)).replace('\\','/'),'sha256':digest(ap)},
                            {'path':str((O/'root-city-preview-acceptance.json').relative_to(R)).replace('\\','/'),'sha256':digest(O/'root-city-preview-acceptance.json')}],
                  'network_requests':0,'new_downloaded_images':0}
    save(O/'guide-preview-22-audit.json',merged_audit)
    union={'checked_utc':datetime.now(timezone.utc).isoformat(),'accepted':True,'scope':'Previously accepted nineteen previews plus three independently checked City Attacks previews.',
           'audit_sha256':digest(O/'guide-preview-22-audit.json'),'checked':old['checked']+checked,'errors':[],'network_requests':0}
    assert len({x['route'] for x in union['checked']})==22
    save(O/'root-guide-preview-22-acceptance.json',union)
    print(json.dumps({'accepted':True,'new_existing_previews':3,'total_previews':22,'groups':6,'downloaded_images':0}))

if __name__=='__main__':main()
