"""Check the small v38 raster subset not covered by the metadata digest cache."""
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
from io import BytesIO
import base64
import hashlib
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'research/continuous-recovery-20261020'
SITE = ROOT / '.scratch/pages-resources-20261019-v38'
SHA = lambda data: hashlib.sha256(data).hexdigest()

def main():
    cache_path = BASE / 'local-audit/digest-reuse-all-captures/metadata-identity-cache.json'
    cache = json.loads(cache_path.read_bytes())['sha256_to_identities']
    audit_path = BASE / 'local-audit/digest-reuse-all-captures/audit.json'
    audit = json.loads(audit_path.read_bytes())
    targets = set(audit['cdx']['selected'])
    provenance = json.loads((SITE / 'export-provenance.json').read_bytes())
    raster = [r for r in provenance['files'] if r['mime'].split(';')[0] in {'image/jpeg','image/png','image/gif'}]
    missing = [r for r in raster if r['derived_sha256'] not in cache]
    assert len(missing) <= 64 and sum(r['derived_length'] for r in missing) <= 1024*1024
    digests = defaultdict(list)
    checked = []
    for row in missing:
        data = (SITE / row['output_path']).read_bytes()
        assert SHA(data) == row['derived_sha256'] and len(data) == row['derived_length']
        digest = base64.b32encode(hashlib.sha1(data).digest()).decode().rstrip('=')
        entry = {'path':row['output_path'],'sha256':SHA(data),'length':len(data),'cdx_digest':digest,'role':row['role']}
        checked.append(entry); digests[digest].append(entry)
    matches = []
    rows_checked = 0
    for report in audit['cdx']['reports']:
        data = (ROOT / report['path']).read_bytes()
        assert SHA(data) == report['sha256']
        rows = json.loads(data)
        if not isinstance(rows,list) or not rows or not isinstance(rows[0],list):
            continue
        header = rows[0]
        for values in rows[1:]:
            if not isinstance(values,list) or len(values)!=len(header):
                continue
            row = dict(zip(header,values))
            if row.get('original') not in targets or row.get('statuscode')!='200' or row.get('mimetype') not in {'image/jpeg','image/png','image/gif'} or not ('00000000000000'<row.get('timestamp','')<='20101207235959'):
                continue
            rows_checked += 1
            for payload in digests.get(row.get('digest'),[]):
                data = (SITE / payload['path']).read_bytes()
                with Image.open(BytesIO(data)) as image:
                    for frame in range(getattr(image,'n_frames',1)):
                        image.seek(frame); image.load()
                matches.append({'target_cdx':row,'source_cdx_file':report['path'],'payload':payload,'source_chain':'pending_if_new_match'})
    out = {'accepted':True,'checked_utc':datetime.now(timezone.utc).isoformat(),
        'audit_sha256':SHA(audit_path.read_bytes()),'metadata_cache_sha256':SHA(cache_path.read_bytes()),
        'raster_records':len(raster),'covered_by_existing_cache':len(raster)-len(missing),
        'additional_raster_files_checked':len(missing),'additional_payload_bytes_read':sum(r['length'] for r in checked),
        'eligible_target_rows_checked':rows_checked,'new_matches':matches,'checked_payloads':checked,
        'network_requests':0,'whole_image_rescan':False,'published':False,
        'scope':'Closes the raster subset absent from the accepted metadata cache using actual v38 bytes. CDX rows are restricted to locally indexed static targets; this is not a search of all archive holdings.'}
    path = BASE / 'publication/root-all-capture-cache-closure.json'
    assert not path.exists()
    path.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:out[k] for k in ['raster_records','covered_by_existing_cache','additional_raster_files_checked','additional_payload_bytes_read','eligible_target_rows_checked','new_matches']}))

if __name__ == '__main__':
    main()
