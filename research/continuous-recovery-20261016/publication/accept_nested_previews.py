"""Verify the 19 existing preview bytes and dates in the frozen source chain."""
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
AUDIT = ROOT / 'research/continuous-recovery-20261016/local-audit/regional-discovery/nested-preview-audit-v4.json'
MANIFEST = ROOT / '.scratch/offline-navigation-20261015-v15/build-manifest.json'
PROVENANCE = ROOT / '.scratch/pages-resources-20261015-v15/export-provenance.json'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    manifest_bytes, provenance_bytes = MANIFEST.read_bytes(), PROVENANCE.read_bytes()
    if sha(manifest_bytes) != 'd89557a445ec5c81ef2652c49fd8ce9c102016f11411b7fa2aa795f5112ae002' or sha(provenance_bytes) != 'be0c336f831e19e63dedc4ada87ed672c620863061f9696e42048dfc1cea890a':
        raise RuntimeError('Frozen binding mismatch')
    source = {x['route']: x for x in json.loads(manifest_bytes)['files']}
    exported = {x['route']: x for x in json.loads(provenance_bytes)['files']}
    audit = json.loads(AUDIT.read_bytes())
    errors, checked = [], []
    for item in audit['items']:
        route = item['route']
        record, current = source[route], exported[route]
        payloads = [(ROOT / record['output_path']).read_bytes(), (ROOT / record['source_local_path']).read_bytes(),
            (PROVENANCE.parent / current['output_path']).read_bytes()]
        digest = sha(payloads[0])
        okay = all(data == payloads[0] for data in payloads) and digest == record['derived_sha256'] == current['derived_sha256'] and len(payloads[0]) == record['derived_length'] == current['derived_length']
        with Image.open(io.BytesIO(payloads[0])) as image:
            image.verify()
        with Image.open(io.BytesIO(payloads[0])) as image:
            image.load()
            dimensions = list(image.size)
        capture = record['actual_timestamp']
        okay = okay and capture == item['actual_capture_timestamp'] and '20080101000000' <= capture <= '20080512210044'
        parent = item['source_page']['parent_a']
        lines = (ROOT / item['source_page']['path']).read_text(encoding='utf-8').splitlines()
        okay = okay and parent['tag'] in lines[parent['source_line'] - 1]
        if not okay:
            errors.append(route)
        checked.append({'route': route, 'sha256': digest, 'length': len(payloads[0]), 'dimensions': dimensions,
            'capture_from_frozen_manifest': capture, 'source_link': parent['href'], 'accepted': okay})
    result = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'accepted': not errors and len(checked) == 19,
        'scope': 'Local original bytes and recorded capture dates verified across frozen source/export. Parent links establish preview navigation; this does not authenticate unavailable full images or create aliases.',
        'audit_sha256': sha(AUDIT.read_bytes()), 'checked': checked, 'errors': errors, 'network_requests': 0}
    (OUT / 'root-nested-preview-acceptance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'accepted': result['accepted'], 'count': len(checked), 'errors': errors}))
    if not result['accepted']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
