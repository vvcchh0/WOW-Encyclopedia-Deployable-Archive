"""Fetch the one exact PNG observed in the cached BC Professions article."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import shutil
import sys
import time
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
RUNNER=ROOT/'research/continuous-recovery-20261022/network/archivecraft-dungeons01/archivecraft_dungeons01.py'
SOURCE=ROOT/'research/continuous-recovery-20261021/network/archivecraft-bc-guides01/runtime/private/raw/attempt-03-archivecraft-bc-professions-direct.body'
URL='https://archivecraft.com/wp-content/uploads/images/index/townhall/burning-crusade/professions/page-title.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))

def main():
    plan=read(HERE/'plan.json');go=read(HERE/'root-go.json')
    assert go['accepted'] and go['root_go'] and go['plan_sha256']==sha(HERE/'plan.json')
    assert go['wrapper_sha256']==sha(Path(__file__))
    assert plan['target_url']==URL and URL in SOURCE.read_text(encoding='utf-8')
    assert sha(SOURCE)=='ec244462dce8cee50b4257829b8dd064ec41853be51d0be7d754385d91cfbae7'
    assert sha(RUNNER)=='7b95fa17bff6aa5245dc9fe45331652f02db5419c0e7ac14ff454af9d0fcad00'
    assert datetime.now(timezone.utc)<datetime.fromisoformat(go['valid_until'].replace('Z','+00:00'))
    assert shutil.disk_usage(ROOT).free>=11005853696 and not (HERE/'runtime').exists()
    spec=importlib.util.spec_from_file_location('bounded_professions_image_runner',RUNNER)
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    paths=m.make_paths(HERE/'runtime');paths.raw.mkdir(parents=True,exist_ok=False)
    attempts=[];last=None;start=time.monotonic();total=0;reason='not_attempted';cooldown=None
    image_info=None
    for index,proxy in enumerate((False,True),1):
        record,last=m.run_attempt({'target_id':'professions-page-title','url':URL},index,proxy,last,start,
            8*1024*1024-total,paths,cadence_seconds=6.2,batch_seconds=120)
        attempts.append(record);total+=record['body_bytes']
        status_stop,cooldown=m.handle_status(record)
        if status_stop:reason=status_stop;break
        if record['transport_failed']:
            reason='transport_failed'
            if not proxy and not record['response_cap_exceeded']:continue
            break
        if record['http_status']!=200:reason='http_status_not_200';break
        mime=(record['header_parse'].get('content_type') or '').split(';',1)[0].strip().lower()
        if mime!='image/png':reason='wrong_mime';break
        try:
            data=Path(record['_body_file']).read_bytes()
            with Image.open(io.BytesIO(data)) as im:
                assert im.format=='PNG'
                frames=getattr(im,'n_frames',1)
                for frame in range(frames):im.seek(frame);im.load()
                assert im.size==(324,72) and frames==1
                image_info={'format':'PNG','width':im.width,'height':im.height,'frames':frames}
        except Exception as exc:reason='image_decode_or_identity_mismatch';image_info={'error':type(exc).__name__};break
        reason='downloaded_valid_png_not_yet_independently_accepted';break
    m.require_disk('before private report')
    private={'attempts':attempts,'stop_reason':reason,'cooldown_not_before_utc':cooldown,'body_bytes':total,'image_info':image_info}
    paths.report.write_bytes((json.dumps(private,indent=2)+'\n').encode())
    a=attempts[-1]
    public={'schema':'wow-related-professions-banner-observation/v1','url':URL,
      'current_observed_utc':a['request_finished_utc'],'attempt_count':len(attempts),
      'http_status':a['http_status'],'transport':a['transport'],'body_bytes':a['body_bytes'],
      'body_sha256':a['body_sha256'],'image':image_info,'stop_reason':reason,
      'cooldown_not_before_utc':cooldown,'raw_http_private':True,
      'original_capture_timestamp':None,'historical_images_recovered':0,
      'disk_free_bytes':m.require_disk('before public observation')}
    (HERE/'observation.json').write_bytes((json.dumps(public,indent=2)+'\n').encode())
    print(json.dumps(public))

if __name__=='__main__':main()
